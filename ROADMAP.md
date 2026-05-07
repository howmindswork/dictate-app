# dictate.app Roadmap

_Last updated: 2026-05-06_

---

## ✅ Done This Session

- [x] Reviews: real photo avatars (randomuser.me)
- [x] Reviews: fade edge mask so cards don't look cut off
- [x] Background starfield: trails slowly shorten after 20s (less distracting)
- [x] 7-day trial everywhere (app + landing page)
- [x] Stripe Pro monthly ($9/mo) + annual ($79/yr) — live with 7-day trial
- [x] Stripe Team monthly ($24/mo) + annual ($240/yr) — live with 7-day trial
- [x] Team plan button → correct Stripe link
- [x] Holiday emoji: auto-changes hero 🌙 to holiday icon within 7 days of event
- [x] Holiday sale banner: appears automatically near holidays with deal copy
- [x] UX audit + all CRITICAL/HIGH fixes (trial wall, error feedback, hotkey conflict, API key validation, trial countdown)
- [x] Tray icon: clean white mic on transparent bg
- [x] Overlay animation: symmetric slide-up + slide-down

---

## 🔥 Next Up (Priority Order)

### 1. Upload the .exe installer
- Build the Electron app: `cd /mnt/c/Users/lukei/Desktop/dictate-app && npm run build`
- Upload .exe to Cloudflare R2 or Pages `/download/dictate-app-setup.exe`
- Update `thank-you.html` download href

### 2. Team Plan — License Key Sharing (app-side)
- When user buys Team plan, they receive a "team license key" via Stripe webhook
- Key format: `TEAM-XXXX-XXXX-XXXX` (signals multi-seat)
- App validates key locally (offline-first) — no server needed for v1
- Team members each enter the same key; app stores it in electron-store
- For cancellation detection: phone home to a lightweight CF Worker once/day to verify key still active
- **Files to edit:** `src/main/index.js` (license check), add `src/main/license.js`

### 3. Cancellation Save Deal
- When Stripe sends `customer.subscription.deleted` webhook:
  - Send cancellation save email via Resend: "Before you go — here's 40% off for 3 months"
  - Coupon: `SAVE40` (3-month duration)
- **Files:** New CF Worker for Stripe webhooks

### 4. First-Run Onboarding
- On first launch (no installDate yet), show a welcome modal or overlay
- Steps: "1. Press Ctrl+Space to start" → "2. Speak clearly" → "3. Text appears at your cursor"
- **Files:** `src/renderer/settings.html` (add onboarding modal)

### 5. Microsoft Clarity Analytics
- Replace `CLARITY_PROJECT_ID` in index.html with real project ID
- Sign up at clarity.microsoft.com

---

## 📣 Marketing / Advertising

### Autonomous Forum Posting (in progress this session)
Forums to post on:
- r/productivity — 5.8M members, high traffic, allows tool recommendations
- r/windows — 2.2M members
- r/software — 600K members  
- r/workhacks
- r/transcription
- r/speechrecognition
- Hacker News "Show HN"
- ProductHunt launch
- Indie Hackers
- dev.to / Hashnode blog posts
- Twitter/X threads (how-it-works demo)
- YouTube Shorts demo

### Reddit Rules to Follow
- Must be genuine, not spam
- Share as a user who found/built something useful
- Don't post same content to multiple subs on same day
- Wait 24h between same link posts
- Include value in post (not just "here's my app")
- Engage with comments

### Proven Ad Copy Angles
1. "I was typing 60 wpm. Now I dictate 150 wpm. Here's how."
2. "Built a dictation app that works offline — no Dragon, no cloud, just speed"
3. "Show HN: dictate.app — push-to-talk transcription for Windows, free 7-day trial"

---

## 💡 Future Ideas

- Holiday deals on all HMW Cloudflare sites (goodaura, come-down) — same banner pattern
- Logo emoji in nav that changes with holidays (same logic as hero emoji)
- Auto-detect trial expiry → show upgrade modal in app (vs current tray balloon only)
- Affiliate program: share link, earn 30% recurring
- Windows Store listing
- Chrome extension companion (dictate in browser fields directly)
- Team admin dashboard (web portal to manage seats)

---

## 🔑 Key Links

| Resource | URL |
|----------|-----|
| Landing page (prod) | https://dictate-app.pages.dev |
| Thank-you page | https://dictate-app.pages.dev/thank-you.html |
| Pro monthly Stripe | https://buy.stripe.com/bJeeVdbHu8OJ57ocYrdwc0m |
| Pro annual Stripe | https://buy.stripe.com/4gM9ATfXK7KFdDU7E7dwc0n |
| Team monthly Stripe | https://buy.stripe.com/dRmdR9aDq8OJ6bs7E7dwc0o |
| Team annual Stripe | https://buy.stripe.com/3cI7sLfXK8OJ0R8e2vdwc0p |
| App source | /mnt/c/Users/lukei/Desktop/dictate-app |
