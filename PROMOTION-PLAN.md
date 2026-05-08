# Dictate App — Promotion & Outreach Master Plan

Generated 2026-05-08. Synthesis of 6 parallel research bots.

## CRITICAL FINDING — FIXED TODAY

Site was functionally **invisible to Google**. Every canonical URL, OG tag, sitemap link, and JSON-LD `url` field pointed to `https://dictate.app` (HTTP 403, Luke does not own this domain). Search engines saw a site claiming to live at one URL while served from another → no indexing.

**Fixed:**
- All canonical/OG/JSON-LD/sitemap/robots URLs replaced with `https://dictate-app.pages.dev`
- Sitemap regenerated: 11 → 54 URLs (was missing 38 of 49 blog posts)
- `scripts/regenerate_sitemap.py` added — re-run before each deploy

## ACCOUNTS LUKE NEEDS TO CREATE (hand creds back, I automate from there)

### TIER 1 — Do these today (highest ROI)
1. **Product Hunt** maker account → producthunt.com (launch Tuesday 12:01 AM PT)
2. **Reddit** dedicated account → reddit.com (90+ days old preferred; if new, comment-build for 1 week)
3. **AlternativeTo** vendor → alternativeto.net
4. **G2** vendor → g2.com/products/new (auto-syndicates to Capterra/GetApp/SoftwareAdvice)
5. **IndieHackers** → indiehackers.com/products
6. **BetaList** submitter → betalist.com/submit
7. **SaaSHub** vendor → saashub.com/submit
8. **Rewardful** ($49/mo) → rewardful.com — wires to Stripe, handles affiliate tracking + tax forms

### TIER 2 — This week
9. **Hacker News** account → news.ycombinator.com (need 90+ days karma for Show HN to stick)
10. **Hashnode** + **Medium** + **Substack** → cross-post dev.to articles
11. **Mastodon** → fosstodon.org or indieweb.social
12. **Threads** → already wired to Bluesky cron, just need login
13. **AppSumo Partner** → appsumo.com/partners (apply, 2-4 wk review)
14. **Hunter.io** free → hunter.io (25 email lookups/mo)
15. **Apollo.io** free → apollo.io (50 credits/mo for finding emails)

### TIER 3 — This month
16. **Futurepedia / TAAFT / Future Tools / Toolify** — AI tool directories (free tier)
17. **MicroLaunch / Tiny Startups / FazierHQ / Pitchwall / Uneed / Peerlist Launchpad**
18. **Chocolatey** community packager → chocolatey.org

### Already have / running
- Bluesky (3x/day cron — confirmed live)
- dev.to (publishing live)
- GitHub (have PAT)
- Cloudflare (token expired, see below)

## BLOCKERS — TOKEN REFRESH NEEDED

- **Cloudflare API token in `~/.claude_secrets` returns "Authentication error"** — cannot pull traffic analytics or programmatically deploy. Refresh at dash.cloudflare.com → My Profile → API Tokens. Permissions needed: Pages:Edit, Analytics:Read, Account:Read.
- **No Microsoft Clarity API key** in secrets — Clarity is installed on site but I can't read traffic data. Add `CLARITY_API_KEY` to `~/.claude_secrets` from clarity.microsoft.com → Settings → Data Export.

## WHAT I CAN AUTOMATE WITH APIS RIGHT NOW (no manual work)

| Channel | Status | API |
|---|---|---|
| Bluesky | ✅ Running 3x/day | atproto |
| dev.to | ✅ Published 3 articles | REST |
| GitHub PRs (Winget, Chocolatey, awesome-windows) | Ready to script | gh CLI |
| Reddit | Ready to script (need account) | PRAW |
| Wikipedia comparison page | Ready to script | MediaWiki API |
| Mastodon | Ready to script (need account) | REST |
| Product Hunt launch | Ready to script (need account) | GraphQL |
| Hashnode/Medium cross-post | Ready to script | REST |

## TOP 30 OUTREACH TARGETS (cold email this week)

**Windows journalists:** Zac Bowden (Windows Central), Mark Hachman (PCWorld), Tim Brookes (How-To Geek), Joel Lee (MakeUseOf), Sean Endicott (Windows Central)

**Newsletters:** TLDR (sponsor@tldrnewsletter.com), Console.dev, Refind, IndieHackers Daily, Hacker Newsletter

**YouTubers:** ThioJoe, Britec09, Chris Titus Tech, Kevin Stratvert, ThePrimeagen, Theo, Fireship, Ali Abdaal, Thomas Frank, Christopher Lawley

**X/Twitter:** @levelsio, @dannypostmaa, @aliabdaal, @thomasjfrank, @SYSTMS

**Outlets:** Cybernews, Zapier blog, TechRadar, G2, Capterra

**Accessibility:** Steven Aquino (Forbes/TechCrunch), Christina Mallon (Microsoft Inclusive Design)

## POSTING CADENCE (avoid spam flags)

- **Mon:** Reddit comments + 1 dev.to post + cross-post Hashnode/Medium/Substack
- **Tue:** Hacker News Show HN OR Product Hunt launch (one big swing)
- **Wed:** IndieHackers milestone + Mastodon thread + Threads
- **Thu:** Reddit value post + Quora answers
- **Fri:** TikTok/Shorts demo + cross-post Bluesky/X
- **Sat:** Directory submissions (1/wk: AlternativeTo, SaaSHub, etc.)
- **Sun:** rest / inbound replies only

## 3 VIDEOS TO MAKE THIS WEEK

1. **"Wispr Flow vs SuperWhisper vs Dictate on Windows"** — comparison ranks for competitor searches
2. **"I dictated this 2,000-word post in 90 seconds"** — Shorts-native, viral
3. **"Setup in 60 seconds"** — converts cold traffic

Stack: OBS (free) + Capcut desktop (free) + Submagic ($16/mo) or Opus.pro ($19/mo) for clipping. Total ≤ $19/mo.

## REDDIT TARGETS (25 subs, ranked)

Top 10: r/SideProject, r/Windows11, r/productivity, r/SaaS, r/RSI, r/dictation, r/Accessibility, r/disability, r/transcription, r/copywriting

## AFFILIATE BLITZ — 40% LIFETIME

The hook is genuinely rare (most SaaS pays 25% one-time). Plan:
1. Sign up Rewardful ($49/mo), wire to Stripe, migrate /affiliates to their links
2. Submit to AffiliatePrograms.com, OfferVault, SaaSHub
3. Scrapling 200 X bios matching "AI tools" + "affiliate" → DM 50/day
4. Post in r/affiliatemarketing, r/juststart weekly threads
5. Email 30 micro-YouTubers with 40% LIFETIME hook
6. Pin viral X math tweet + $50 ad boost

## NEXT ACTIONS LUKE → ME

1. Tell me when accounts are created — paste creds into `~/.claude_secrets` with names like `REDDIT_CLIENT_ID`, `PRODUCTHUNT_TOKEN`, etc., I'll pull and use them.
2. Refresh Cloudflare API token so I can pull traffic + deploy.
3. Decide on Rewardful ($49/mo) — yes/no.
