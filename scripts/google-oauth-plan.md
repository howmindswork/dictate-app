# Google OAuth Implementation Plan — dictate.app

## Recommendation: Supabase (Option B)

**Why Supabase beats Cloudflare Worker auth and Firebase:**
- Built-in Google OAuth — 20 lines of code vs building from scratch
- Free tier: 50,000 MAU, 500MB DB, unlimited auth
- Postgres DB included — store users, subscriptions, trial dates in one place
- Supabase JS SDK works in Electron's renderer process without modification
- Row Level Security means no separate auth middleware to write
- Firebase is Google-locked and overkill; CF Worker auth requires building JWT issuance, session management, and DB from scratch

---

## Electron-Specific OAuth Flow

**Use localhost loopback redirect (not custom URL scheme)**

Reason: Custom URL schemes (`dictate://auth`) require OS registration and can be blocked by Windows security policies or antivirus. Localhost redirect is universally supported and is the approach Google officially recommends for native apps (RFC 8252).

Flow:
1. Electron app starts a temporary HTTP server on `localhost:PORT` (random port)
2. App calls `shell.openExternal('https://accounts.google.com/o/oauth2/auth?redirect_uri=http://localhost:PORT/callback&...')`
3. User logs in via system browser (Chrome, Edge, etc.) — not inside Electron
4. Google redirects to `localhost:PORT/callback?code=...`
5. Electron's local server catches the code, exchanges it for tokens via Supabase
6. Local server shuts down, Electron window comes forward
7. App receives session, stores it, never asks again

---

## What Google OAuth Returns

- `email` — primary identifier
- `name` — display name
- `picture` — avatar URL
- `sub` — Google's permanent user ID (use this as the stable identifier)

**Tying to Stripe:**
When user first signs in → create Supabase user row → create Stripe customer with `metadata.supabase_user_id = user.id` → store `stripe_customer_id` back in Supabase user row.

Stripe webhooks (`customer.subscription.created`, `customer.subscription.deleted`, `invoice.payment_failed`) update `subscription_status` in Supabase in real time.

---

## Database Schema (Supabase Postgres)

```sql
-- users table (Supabase auth.users handles credentials)
create table public.profiles (
  id uuid references auth.users primary key,
  email text not null,
  stripe_customer_id text unique,
  subscription_status text default 'trialing', -- trialing | active | past_due | canceled
  trial_start timestamptz default now(),
  trial_end timestamptz default (now() + interval '7 days'),
  created_at timestamptz default now()
);
```

Supabase auto-creates `auth.users` on Google sign-in. You only manage `public.profiles`.

---

## Website Login Page

**File:** `/home/luke/dictate-app-website/login.html`

Simple page on `dictate-app.pages.dev/login`:
- "Sign in with Google" button (Supabase JS handles the redirect)
- After login → redirect to `/dashboard`

**File:** `/home/luke/dictate-app-website/dashboard.html`

Shows:
- User's name + avatar
- Subscription status (Active / Trial ends in X days / Expired)
- Download button → links to GitHub release EXE
- Upgrade button (if on trial) → Stripe Checkout
- Affiliate link (if they joined the program)

---

## Step-by-Step Implementation Plan

### Phase 1: Supabase Setup (30 min, no code)
1. Create project at supabase.com (free)
2. Enable Google provider: Authentication → Providers → Google → paste Google OAuth client ID + secret
3. Create Google OAuth app at console.cloud.google.com → get client ID + secret
4. Add `dictate-app.pages.dev/auth/callback` as authorized redirect URI in Google Console
5. Create `public.profiles` table with schema above
6. Enable Row Level Security, add policy: users can only read/update their own row

### Phase 2: Website Auth Pages (2-3 hours)
7. Create `login.html` — purple theme, "Sign in with Google" button, Supabase JS CDN
8. Create `dashboard.html` — shows subscription status, download button, affiliate link
9. Create `auth/callback.html` — handles Supabase's OAuth redirect, stores session, redirects to dashboard
10. Add Supabase anon key to pages (safe to expose — RLS protects data)

### Phase 3: Stripe Webhook Worker (2 hours)
11. Add new route to affiliate-worker (or new worker): `POST /stripe-webhook`
12. On `checkout.session.completed`: create Supabase profile row, set `stripe_customer_id`
13. On `customer.subscription.*`: update `subscription_status` in Supabase
14. Register webhook in Stripe dashboard → point to worker URL

### Phase 4: Electron App Auth (3-4 hours)
15. In Electron main process: add `supabase-js` npm package
16. On app start: check if session token exists in `electron-store` (persisted local storage)
17. If no session: open login window → `shell.openExternal()` to `dictate-app.pages.dev/login`
18. Start localhost callback server, catch token, store in `electron-store`
19. On each API call to Groq: verify session is active (check `subscription_status` via Supabase)
20. If subscription expired: block dictation, show upgrade prompt

### Phase 5: Trial Enforcement (1 hour)
21. When user first authenticates: set `trial_start = now()`, `trial_end = now() + 7 days`
22. Groq API calls check: if `subscription_status = 'trialing'` AND `trial_end < now()` → block
23. Show "Your trial ended — upgrade for $8.99/month" with Stripe Checkout link

---

## Cost Estimate

| Service | Free Tier | Paid |
|---------|-----------|------|
| Supabase | 50,000 MAU, 500MB DB | $25/mo for 100k MAU |
| Google OAuth | Free forever | Free forever |
| Cloudflare Worker (webhook) | 100k req/day free | $5/mo for more |
| electron-store (local storage) | Free npm package | Free |

**At dictate.app's current scale: $0/month.**
At 10,000 paying users: still $0 (Supabase free tier covers it).
At 50,000+ users: $25/month Supabase Pro.

---

## Files to Create

- `login.html` — Google sign-in page
- `dashboard.html` — post-login user dashboard
- `auth/callback.html` — OAuth redirect handler
- New route in affiliate-worker: `POST /stripe-webhook`
- Electron: `src/auth.js` — session management module
- Electron: `src/trialCheck.js` — subscription enforcement

## Dependencies to Add (Electron)
- `@supabase/supabase-js` — auth + DB client
- `electron-store` — persistent local token storage  
- (no new website dependencies — use Supabase CDN)
