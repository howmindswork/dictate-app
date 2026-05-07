# dictate.app Full Audit — 2026-05-06

Auditor: Claude (senior engineer pass). Files read:
- `/mnt/c/Users/lukei/Desktop/dictate-app/src/main/{index,trial,transcribe,inject,hotkey}.js`
- `/mnt/c/Users/lukei/Desktop/dictate-app/src/renderer/{app,settings}.js`, `settings.html`
- `/mnt/c/Users/lukei/Desktop/dictate-app/electron-builder.yml`, `package.json`, `.env`
- `/home/luke/dictate-app-website/{index,privacy,thank-you,download}.html`, `sitemap.xml`, `robots.txt`
- `/home/luke/dictate-app-website/{autoposter,reddit_poster}.py`
- `/home/luke/dictate-app-website/scripts/auto_generate_post.py`
- `/home/luke/dictate-app-website/.github/workflows/{autoposter,blog-autopublish,reddit-poster}.yml`

---

## 1. SECURITY ISSUES

### [CRITICAL] Live Groq API key shipped inside installer

**File:** `electron-builder.yml` lines 24-26, `.env` line 1

`electron-builder.yml` explicitly copies `.env` into every compiled installer package:

```yaml
extraResources:
  - from: ".env"
    to: ".env"
```

`.env` contains a real, active Groq API key (`gsk_96RYhecmQMll6h7r0Ttg...`). Anyone who downloads the installer, extracts it with 7-Zip or innounp, and reads the `resources/.env` file has your Groq key. Groq keys have no per-user scoping — this key controls your entire Groq account.

**Fix:** Remove the `extraResources` block entirely. The app already prompts users to paste their own Groq key in Settings > AI Setup. Delete the `.env` from the build. Rotate the leaked key immediately.

---

### [CRITICAL] Owner/admin keys hardcoded in plaintext, shipped in app bundle

**File:** `src/main/trial.js` lines 1-2

```js
const OWNER_KEYS = ["DICTATE-OWNER-2026", "HMW-ADMIN-FOREVER"];
```

Electron apps ship as ASAR archives. ASAR is not encrypted. Anyone can run `npx asar extract app.asar app-extracted/` and read `trial.js` in plaintext in 10 seconds. These two strings bypass trial enforcement entirely. They are now public.

**Fix:** Rotate both keys. Never store bypass keys in source. If you need an owner unlock, derive it from a server-side check (HMAC of machine ID + secret, validated against your server) or at minimum obfuscate with a non-trivial transform.

---

### [CRITICAL] License key "validation" accepts any string over 8 characters

**File:** `src/main/index.js` lines 394-398

```js
ipcMain.on("validate-license-key", (event, key) => {
  const owner = isOwnerKey(key);
  const valid = owner || (typeof key === "string" && key.trim().length > 8);
  event.reply("license-key-validated", { valid, owner });
});
```

Any string longer than 8 characters is treated as a valid license key. There is no server check, no cryptographic signature, no Stripe webhook verification. Users can type `aaaaaaaaa` and get `valid: true`. Combined with the unencrypted electron-store, they can also directly edit the store JSON to set `licenseKey` to any value.

However: there is no UI in `settings.html` or `settings.js` that calls `validate-license-key` or saves `licenseKey` to preferences. The IPC handler exists in `index.js` but no renderer code calls it. So the "Buy" button opens Stripe in a browser — and after payment, there is no fulfillment path to actually unlock the app. Users who pay have no way to enter a key.

**Fix:** Implement actual license key delivery (Stripe webhook → email key → user enters it in-app → server validates). Until then, the product has no working paid tier.

---

### [HIGH] `nodeIntegration: true` + `contextIsolation: false` on both windows

**File:** `src/main/index.js` lines 134-137 (overlay) and 273-276 (settings)

Both windows run with the most dangerous Electron configuration possible. Any XSS in the renderer (e.g., from transcribed text being rendered without escaping, or from a future blog link) gives full Node.js access — filesystem read/write, shell execution, process spawning.

The settings window does escape transcription text correctly (lines 82-91 of `settings.js`), but this is defense-in-depth that should not substitute for disabling `nodeIntegration`.

**Fix:** Switch to `nodeIntegration: false`, `contextIsolation: true`, add a `preload.js` that exposes only the specific IPC channels needed via `contextBridge.exposeInMainWorld`.

---

### [HIGH] CSP on settings.html only — overlay window (index.html) has no CSP

**File:** `src/renderer/settings.html` line 6-8 has a CSP. `src/renderer/index.html` (the overlay, which receives microphone data and renders it) has no CSP at all.

---

### [MEDIUM] `.env` in `.gitignore` but key is already in installer binaries

`.gitignore` correctly excludes `.env` from git. But `electron-builder.yml` packages it into the distributed binary. Git safety is irrelevant if every installer has the key embedded. See CRITICAL above.

---

## 2. TRIAL BYPASS RISKS

### [CRITICAL] Trial state in unencrypted electron-store — trivially bypassable

**File:** `src/main/index.js` line 25 — `const store = new Store();` (no encryption options)

electron-store stores data as plaintext JSON at `%APPDATA%\dictate-app\config.json` (or similar). Any user can open a terminal and run:

```
echo {"installDate":"2030-01-01T00:00:00.000Z"} > "%APPDATA%\dictate-app\config.json"
```

This resets the trial to 30 days. Alternatively they can delete the file and re-launch the app, which re-creates it with today's date — also resetting the trial.

**Fix options (in order of difficulty):**
1. Server-side trial validation tied to machine fingerprint (best)
2. electron-store with `encryptionKey` (delays crackers; key still in binary but harder)
3. Install-date written to Windows Registry with HKLM (requires admin; harder to edit)

None of these are perfect. Without a server check, determined users will always be able to bypass. The app is currently no more protected than shareware from 1998.

---

### [HIGH] Trial is 30 days in code, 7 days in all marketing

**File:** `src/main/trial.js` line 1 — `const TRIAL_DAYS = 30;`
**File:** `index.html` lines 10, 50, 112, 150 — all say "7-day free trial"
**File:** `settings.html` line 1057 — says "30-day free trial"

Pick one. Showing 30-day trial in the app and 7-day on the website is confusing. More importantly: if the website says 7-day, users who get 30 days think it's a bug. If it's 30-day, the website is misrepresenting the product.

---

## 3. BROKEN / STUB FEATURES

### [HIGH] License key entry UI does not exist

As noted above: `ipcMain.on("validate-license-key", ...)` is in `index.js` (line 394) but there is zero HTML input, zero JS call, zero form in `settings.html` or `settings.js` that uses it. After a user pays via Stripe, there is nowhere to enter their license key. The "Account" panel (`settings.html` line 1034) just shows "Free Trial" and an "Upgrade" button that opens the Stripe URL again.

---

### [HIGH] 5 settings toggles are UI-only stubs — they do nothing

The following preferences are saved to `electron-store` but **never read** in any functional code path:

| Toggle | Setting key | Status |
|---|---|---|
| Hands-free mode | `handsFreeModeEnabled` | No implementation anywhere |
| Remove filler words | `removeFiltersEnabled` | Not passed to Groq, not post-processed |
| Save recordings | `saveRecordingsEnabled` | No file write, no path |
| Auto-detect language | `autoDetectLanguageEnabled` | Groq called with no `language` param always |
| Dark theme | `darkThemeEnabled` | No theme switching logic |

The `autoPasteEnabled` setting is also ignored — `injectText()` is always called regardless of the toggle.

The `saveToLogEnabled` setting: transcriptions are always written to the store regardless of this being true or false (index.js lines 211-213 have no guard).

The `restoreClipboardEnabled` / "restore-clipboard" IPC handler at line 329 reads the current clipboard but never actually uses it to restore after paste — it just sends it back to renderer with no effect.

**Risk:** If a user turns off "auto-paste" expecting dictation to stop pasting, it still pastes. If they turn off "save to log" for privacy reasons, their transcriptions are still saved.

---

### [MEDIUM] Pause functionality broken on overlay close

When `stop-recording` IPC fires while recording is paused (`mediaRecorder.state === 'paused'`), the code in `app.js` line 173 calls `mediaRecorder.stop()` but does not call `mediaRecorder.resume()` first. Some browsers/Chromium versions throw an error stopping a paused MediaRecorder — behavior is undefined. The audio may or may not be transcribed.

---

### [MEDIUM] Stats polling every 3 seconds is wasteful

`settings.js` line 333: `setInterval(() => ipcRenderer.send("get-stats"), 3000)`. Stats don't change that fast. This runs IPC and JSON parsing in an infinite loop the entire time settings is open. On slow systems this will be noticeable. Should be event-driven (send stats after each transcription).

---

### [MEDIUM] `tray.displayBalloon` called without checking Windows-only availability

`index.js` lines 171-177 and 457-462 call `tray.displayBalloon()` — this is only available on Windows. There's a guard (`tray.displayBalloon &&`) which is correct, but the try/catch scope around hotkey conflicts doesn't cover the balloon call.

---

## 4. AUTO-POSTER BUGS

### [HIGH] `build_facets()` uses `str.find()` which always returns the first occurrence

**File:** `autoposter.py` lines 508-527

```python
start = text_bytes.find(url_bytes)    # WRONG for duplicates
start = text_bytes.find(tag_bytes)    # WRONG for duplicates
```

`bytes.find()` always returns the index of the **first** occurrence. If a hashtag (e.g., `#indiedev`) appears twice, or if two different URLs share a prefix, the second facet's `byteStart` will point at the first occurrence. Bluesky will render hyperlinks at wrong positions.

**Fix:** Use `re.finditer()` and use `m.start()` for the byte index (after accounting for multi-byte chars):
```python
for m in re.finditer(rb'#\w+', text_bytes):
    facets.append({"index": {"byteStart": m.start(), "byteEnd": m.end()}, ...})
```

---

### [MEDIUM] All social posts and blog posts link to `dictate-app.pages.dev` (staging URL)

**File:** `autoposter.py` line 8, `reddit_poster.py` lines 28/54/68/82/95, `scripts/auto_generate_post.py` line 29

```python
SITE_URL = "https://dictate-app.pages.dev"
```

Every Bluesky post, dev.to article, Mastodon toot, Reddit post, and auto-generated blog post sends users to the Cloudflare Pages preview URL, not `https://dictate.app`. If you ever lose the Pages project or rename it, all traffic in every piece of distributed content evaporates. More immediately: the branding says "dictate.app" but links go to a `pages.dev` subdomain which looks unprofessional and suspicious.

---

### [MEDIUM] Reddit poster will eventually get banned for spam

**File:** `reddit_poster.py` lines 119-123

`resubmit: True` is set, which bypasses Reddit's duplicate detection. More critically, all posts are from the same account, to the same subreddits, on a fixed weekly schedule, with the developer's link in every one. Reddit's spam detection will catch this pattern. Many of the target subreddits (r/productivity, r/windows) have strict self-promotion rules.

The posts do include disclosures like "[I built it]" which helps, but the fully automated weekly cadence will get the account shadowbanned. There's no error handling — if Reddit returns a 429 or ban response, the script prints the JSON and exits with no alert.

---

### [LOW] No error alerting on autoposter failures

**File:** `autoposter.py` lines 657-680, `reddit_poster.py` passim

All posting failures print to stdout and silently continue. In GitHub Actions this means a failure appears as a "passing" run with error lines buried in logs. No email, no Slack, no GitHub issue is created on failure. You will not know if posting stops working.

---

## 5. WEBSITE ISSUES

### [HIGH] OG image, Twitter image, and screenshot don't exist

**File:** `index.html` lines 33, 54, 82

```html
<meta property="og:image" content="https://dictate.app/og-image.png" />
<meta name="twitter:image" content="https://dictate.app/twitter-image.png" />
"screenshotUrl": "https://dictate.app/screenshot.png"
```

None of these files exist in the website directory. Social shares of the dictate.app URL show a broken image. The JSON-LD structured data references a missing screenshot. This is the first thing social crawlers see.

---

### [HIGH] Fake aggregated reviews in structured data

**File:** `index.html` lines 91-96

```json
"aggregateRating": {
  "ratingValue": "4.8",
  "ratingCount": "42"
}
```

This is fabricated social proof. Google can penalize or manual-action sites for fake structured data, particularly fake reviews. If this product has zero real reviews yet, this is both dishonest and a legal risk (FTC). Remove or replace with real data.

---

### [HIGH] Sitemap contains 4 pages that don't exist

**File:** `sitemap.xml` — references `/download`, `/faq`, `/features`, `/pricing` as standalone pages.
**Reality:** `terms.html`, `faq.html`, `features.html`, `pricing.html` do not exist. Only `download.html` exists. These are all section anchors within `index.html` (`#features`, `#pricing`, `#faq`).

Google will crawl these URLs, get 404s, and the sitemap will be flagged as invalid. Remove the non-existent pages from the sitemap or create the pages.

---

### [HIGH] Pricing on website contradicts the app and the Stripe link

- Website pricing section shows: Starter (free), Pro ($9/mo), Team ($24/mo) — **subscription model**
- JSON-LD structured data says: `"price": "29.00"` — **one-time purchase**
- FAQ says: "purchase a lifetime license ($29)" — **one-time**
- The app's Account panel says: "Upgrade to Pro for $9/mo"
- The Stripe checkout URL is the same link for all three pricing tiers (monthly, annual, team) — three plans pointing to one URL

The product doesn't know whether it's a subscription or a lifetime purchase. These need to reconcile before money changes hands or you'll have chargebacks.

---

### [MEDIUM] Blog auto-publisher uses `claude-haiku-4-5-20251001` — model may be deprecated

**File:** `scripts/auto_generate_post.py` line 270

The model ID `claude-haiku-4-5-20251001` may not be current. Check Anthropic's model list to ensure the blog pipeline won't fail on a monday morning due to a retired model.

---

### [MEDIUM] Blog posts branded as "TechTips" — a separate entity from dictate.app

**File:** `scripts/auto_generate_post.py` lines 34-37, 185, 228

The system prompt and templates present the blog as "TechTips, an independent tech advice blog ... NOT affiliated with any single product." But the blog lives at `dictate-app.pages.dev/blog/` and the nav has "Try dictate.app →" in the header of every post. This astroturfing is transparent to any reader. If discovered by a journalist or competitor, it's reputational damage.

---

### [MEDIUM] No `terms.html` exists, but it's linked from sitemap

Terms of service do not exist as a page. Privacy policy exists (`privacy.html`) but Terms does not. Many app stores, payment processors, and affiliate networks require a ToS URL.

---

### [LOW] Blog index card links use absolute `SITE_URL` (pages.dev) not relative paths

**File:** `scripts/auto_generate_post.py` lines 308-313

Blog index cards link to `https://dictate-app.pages.dev/blog/{slug}.html`. If the domain changes or you add a custom domain to CF Pages, all internal blog links will still go to `pages.dev`.

---

### [LOW] `robots.txt` disallows `/*.json$` but `Disallow` regex syntax is not supported

**File:** `robots.txt` line 8 — `Disallow: /*.json$`

Robots.txt does not support regex. The `$` at the end and `*` wildcard behavior varies by crawler. Googlebot honors `*` as a wildcard (matching any path containing `.json`) but ignores `$`. This is probably harmless but misleading.

---

## 6. GITHUB ACTIONS ISSUES

### [MEDIUM] `autoposter.yml` env var name mismatch for Bluesky password

**File:** `.github/workflows/autoposter.yml` line 17 vs `autoposter.py` line 654

Workflow sets: `BLUESKY_PASSWORD: ${{ secrets.BLUESKY_APP_PASSWORD }}`
Script reads: `os.getenv("BLUESKY_PASSWORD")`

The secret name is `BLUESKY_APP_PASSWORD` (correct for an app password, not account password). The env var name passed to the script is `BLUESKY_PASSWORD`. This is consistent — but if the secret is not set in the repo, Bluesky posting silently does nothing. There's no validation that required secrets exist before running.

---

### [MEDIUM] `blog-autopublish.yml` auto-commits to `github.ref_name` — dangerous on main

**File:** `.github/workflows/blog-autopublish.yml` line 76

```yaml
git push origin ${{ github.ref_name }}
```

This bot pushes directly to whatever branch is checked out — including `main`. A CI failure, malformed HTML, or LLM hallucination in the post content gets pushed straight to production with no review. There's no PR, no diff check, no staging step.

---

### [LOW] `blog-autopublish.yml` topic is passed unsanitized into a git commit message

**File:** `.github/workflows/blog-autopublish.yml` line 75

```yaml
git commit -m "blog: auto-publish — ${TOPIC:0:60}"
```

If `topics-queue.txt` ever contains a topic with shell metacharacters (backticks, `$`, quotes), this could break the commit command. Low risk in practice but worth quoting: `git commit -m "blog: auto-publish — $(echo "$TOPIC" | head -c 60)"`.

---

## 7. AFFILIATE SYSTEM

### [HIGH] No affiliate system exists — just placeholder Stripe URLs

There is no affiliate system. No `/affiliates` page, no affiliate tracking code, no referral parameter in Stripe links, no cookie-based attribution. The sitemap doesn't even list an affiliates page.

Stripe's built-in affiliate/referral features are limited. If you want affiliates, you need either:
- Rewardful / PartnerStack / Lemon Squeezy (redirect-based)
- Custom: append `?ref=CODE` to Stripe URLs and capture in metadata via Stripe JS

Currently there is zero infrastructure for this.

---

### [HIGH] After Stripe payment there is no license fulfillment

Stripe has no webhook configured (no server, no API endpoint in the codebase). When a user pays:
1. Stripe collects payment
2. Stripe redirects to `thank-you.html` (presumably — there's no `success_url` visible in the code)
3. User receives no license key
4. User has no way to enter a license key in the app (UI doesn't exist)
5. The app remains in trial/expired state

This is the most business-critical broken flow. Users who pay get nothing.

---

## 8. BUSINESS RISKS

### [CRITICAL] The paid tier is completely non-functional

Stripe takes the money. No license key is generated, emailed, or deliverable. No UI exists to enter one. No server validates one. This is a product that can take payment but cannot fulfill it.

**What kills this fastest:** the first paying customer who can't figure out how to "unlock" the app after paying files a chargeback. Stripe notices the pattern and restricts the account.

---

### [CRITICAL] Groq API key leaked in every installer

Every copy of the app distributed is shipping your Groq API key. Anyone can extract it and rack up transcription charges against your account. Groq Whisper is cheap but not free at scale.

---

### [HIGH] No update mechanism

`check-for-updates` in `index.js` line 368 just opens `https://dictate-app.pages.dev` in a browser. There is no auto-updater (no `electron-updater`, no Squirrel, no NSIS update check). When you ship a fix, users with old versions get nothing. You'd have to rely on them noticing the website.

---

### [HIGH] No crash reporting or telemetry

You have zero visibility into how the app behaves in production. No Sentry, no error reporting, no usage analytics. Transcription errors are printed to `console.error` which goes to `app-err.log` on the user's disk, which you never see.

---

### [HIGH] Social posts all promote a staging URL, not the real domain

All distributed content (20 Bluesky posts, 6 Reddit posts, all blog posts) links to `dictate-app.pages.dev`. This will never rank for the domain `dictate.app` and looks unprofessional.

---

### [MEDIUM] Product claims "offline" / "local" in some places — it's not

`auto_generate_post.py` system prompt line 38: "dictate.app: offline voice-to-text for Windows"

The app is not offline. It requires an internet connection to Groq for every transcription. `index.html` line 142 correctly states this. But the blog post generator instructs Claude to call it "offline" — every auto-generated blog post will lie about this.

---

## 9. MISSING FEATURES (vs. Wispr Flow, Dragon)

| Feature | Wispr Flow | Dragon | dictate.app |
|---|---|---|---|
| Offline mode / local model | No | Yes | No (and falsely claimed) |
| Custom vocabulary / word substitutions | Yes | Yes | No |
| Auto-punctuation | Yes | Yes | No (Groq returns punctuated text but no post-processing) |
| Filler word removal ("um", "uh") | Yes | Yes | Setting exists but not implemented |
| Formatting commands ("new paragraph", "period") | Yes | Yes | No |
| Voice commands beyond dictation | Limited | Yes | No |
| Auto-update mechanism | Yes | Yes | No — manual only |
| Cloud backup of transcription history | — | No | Advertised on pricing page but not built |
| Multi-language per-session switching | Yes | Limited | Setting exists, not implemented |
| Mobile companion | Yes (iPhone) | Limited | No |
| App-specific profiles | Dragon | Yes | No |
| License key entry UI | N/A | N/A | Missing |
| GDPR data deletion | Yes | Yes | No mechanism |

---

## TOP 10 PRIORITIZED ACTION LIST

1. **[Do today] Rotate the leaked Groq API key.** It's in `electron-builder.yml`'s `extraResources` and bundled into every installer. Remove the extraResources block, delete `.env`. Rotate the key at console.groq.com immediately.

2. **[Do today] Build license fulfillment.** Add a license key input field in settings.html. Add a Stripe webhook to a Cloudflare Worker that generates a signed key (HMAC-SHA256) and emails it to the buyer. Implement server-side validation in the app's IPC handler (replace the "any 8-char string is valid" logic). Without this, paid users get nothing and chargebacks will follow.

3. **[This week] Replace hardcoded owner keys with a server check.** `trial.js` owner keys are extractable from the ASAR in under a minute. Rotate them. If you need a dev bypass, use an env var that's not shipped in the build.

4. **[This week] Point all content at `dictate.app` not `pages.dev`.** Update `SITE_URL` in `autoposter.py`, `reddit_poster.py`, and `scripts/auto_generate_post.py`. Update the Stripe checkout URL in `index.js` to match the website's Stripe links. All links in distributed content must go to your real domain.

5. **[This week] Fix the trial days mismatch.** Pick 7 or 30. Update the code (`trial.js`) and all marketing copy (`index.html`, `settings.html`, all post templates) to match.

6. **[This week] Add OG images.** `og-image.png` and `twitter-image.png` don't exist. Every social share of dictate.app shows a broken image. Create a 1200×630 image and a 1200×600 Twitter image and commit them.

7. **[This week] Remove fake structured data ratings.** `index.html` claims 42 reviews at 4.8 stars. This is fabricated. Remove the `aggregateRating` block from the JSON-LD until you have real reviews. Google can penalize for this.

8. **[Next two weeks] Implement the top 3 stub settings.** Remove filler words (`removeFiltersEnabled` — post-process Groq output with a regex), honor auto-paste toggle (guard `injectText()` call), make save-to-log actually conditional (guard the store write at index.js line 211). These settings show in the UI and do nothing — users will file bugs.

9. **[Next two weeks] Switch Electron security model.** Set `nodeIntegration: false`, `contextIsolation: true` on both windows. Write a `preload.js` with `contextBridge` for the needed IPC channels. This is a breaking change that requires rewriting all `ipcRenderer` calls in renderer code, but the current setup is a security liability.

10. **[Next month] Add an update mechanism.** Integrate `electron-updater` with a GitHub Releases workflow. Right now every shipped user is permanently stuck on their installed version with no way to receive bug fixes. Also add Sentry or similar for crash telemetry — you're flying blind on production errors.
