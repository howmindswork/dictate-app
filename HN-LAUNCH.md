# Hacker News Launch — dictate-app.pages.dev

**Post on:** Tuesday or Wednesday, 9–11 AM ET
**Be online for:** 2–3 hours after posting to reply to comments
**HN account:** howmindswork (confirm this is your account before posting)

---

## STEP 1: Warm-Up Comments (post these BEFORE the Show HN)

Post at least 3–5 of these comments on existing threads in the days before your Show HN.
This signals an active, genuine account. Do NOT post them all on the same day.

---

### Warm-Up Comment A
**Thread to find:** Search HN for "Whisper" or "transcription" — any recent thread about speech-to-text

> The latency gap between local Whisper on CPU and a hosted API is wider than most people realize. On a mid-range laptop, local whisper-large takes 2–4 seconds. Groq's hosted inference gets it under 200ms. For push-to-talk workflows that feels like a different product category entirely — local feels like you're waiting, API feels like it just works. Tradeoff is obviously the privacy model, but for most prose dictation (emails, docs, Slack) that's acceptable.

---

### Warm-Up Comment B
**Thread to find:** Any thread about Electron, cross-platform desktop apps, or "native vs web"

> The thing Electron gets wrong for Windows productivity tools isn't performance — it's global hotkeys. Electron's `globalShortcut` only fires when the Electron process is in the foreground unless you specifically handle it. For a dictation app that needs to capture keystrokes while you're in Word or Notepad, you end up doing something ugly with `uiohook-napi` or similar to get truly global keyboard capture. The web platform abstraction breaks down exactly where system-level tools need it most.

---

### Warm-Up Comment C
**Thread to find:** Search HN for "Windows" + "productivity" or "indie" + "Windows app"

> The Windows developer tool market is genuinely underserved compared to Mac. Most productivity/dev tools launch Mac-first (or Mac-only) and add Windows support 18 months later if at all. Wispr Flow, Superwhisper — both Mac-only. There's a real gap for tools that assume Windows as the primary platform rather than an afterthought.

---

### Warm-Up Comment D
**Thread to find:** Any thread about "text injection" or "clipboard" automation on Windows

> The reliable way to inject text at cursor position on Windows without accessibility APIs is clipboard + Ctrl+V simulation. Write to clipboard, wait ~100ms for the clipboard to settle, then SendKeys Ctrl+V via PowerShell. It's inelegant but works universally across apps — Notepad, VS Code, browsers, Teams, everything. The alternative is UI Automation COM interfaces which are app-specific and fragile.

---

### Warm-Up Comment E
**Thread to find:** Any thread about "indie" SaaS, small software products, or developer tools pricing

> The BYOK (bring your own API key) model for AI-powered tools is interesting because it inverts the cost structure. Instead of absorbing inference costs as a subscription business, you pass them to users who probably already have API credits sitting unused. Groq's free tier is generous enough that light dictation use costs users effectively nothing. The downside is onboarding friction — "go get an API key" is a real drop-off point.

---

## STEP 2: Show HN Post

**Title (copy exactly):**
```
Show HN: Push-to-talk dictation for Windows – 200ms via Groq Whisper, auto-pastes at cursor
```

**Body text (copy exactly):**
```
I built this because I couldn't find a Windows dictation tool that did all three things I needed: fast transcription, auto-paste directly at cursor (not just clipboard), and works on Windows.

The options I tried:

- Win+H (built-in): 2-3 second lag, doesn't auto-paste, stops mid-sentence on long pauses
- Dragon NaturallySpeaking: $500 upfront, heavy, designed for an era before Whisper
- Whisper locally (CPU): 1-2 seconds on a mid-range laptop, no paste integration  
- Wispr Flow / Superwhisper: fast and polished, Mac only

The combination "fast + Windows + auto-paste at cursor" didn't exist, so I built it.

**How it works:**

1. Press Ctrl+Space (remappable)
2. Speak
3. Release — text appears at your cursor in whatever app you're in

Technically: Electron + Groq's Whisper API for transcription (~200ms round-trip). For global hotkeys I'm using Electron's built-in `globalShortcut`. Text injection is clipboard write + PowerShell SendKeys Ctrl+V simulation — inelegant, but works universally across every Windows app I've tested.

The hardest part wasn't the transcription. Groq's API is fast and reliable enough that it mostly just works. The hard part was text injection: getting text to appear at cursor position in any arbitrary Windows app without accessibility APIs. The clipboard approach is the only thing I found that works in VS Code, Word, Notepad, browsers, Teams, Slack, and chat apps simultaneously.

It's an Electron app, so the installer is ~80MB and Windows will show a SmartScreen warning (I'm working on code signing). The "More Info → Run Anyway" flow is required for now.

What it doesn't do yet: custom vocabulary for proper nouns/jargon, silence detection for hands-free mode, Mac/Linux support.

7-day trial, no credit card: https://dictate-app.pages.dev
```

---

## STEP 3: First Author Comment (post within 2 minutes of submitting)

```
Happy to answer questions. A few I expect to come up:

**Why Electron and not a native app?**
Speed to ship. I can do everything in JS/Node I'd need for this: global hotkeys, audio capture, tray icon, auto-updater. A native C++ or C# app would probably be ~30MB smaller and start 200ms faster, but it's a 3-6x longer build. If this gets traction I'd consider a native rewrite.

**Privacy — does audio leave the machine?**
Yes, it goes to Groq's API for transcription. Groq's terms say they don't train on API requests and don't store audio. For sensitive environments (legal, medical, classified), don't use this. For writing emails and Slack messages, I'm comfortable with it personally.

**Is Groq reliable enough?**
In ~3 weeks of daily use I've had maybe 3-4 transcription failures, all during obvious API incidents that affected everything on Groq. Uptime is good. The free tier handles light use comfortably; heavy users will hit rate limits and need a paid key.
```

---

## Notes

- Do NOT post the Show HN from the same IP as bulk automated posting (use your regular home IP)
- Reply to EVERY comment in the first 2 hours — HN algorithm rewards early engagement
- If someone asks a technical question you can't answer honestly, say so — HN audience spots evasion immediately
- Don't upvote-brigade your own post — it gets flagged
- If it doesn't hit front page, wait 3 months and try again with a different angle
