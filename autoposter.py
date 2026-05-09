#!/usr/bin/env python3
"""
dictate.app auto-poster — Bluesky + dev.to + Mastodon
2x/day (10 AM ET + 7 PM ET). Dev.to Tue + Thu mornings.
"""
import os, json, urllib.request, urllib.parse, datetime, re

SITE_URL = "https://dictate-app.pages.dev"

# ── Content bank (15 threads, ~7.5 days before any repeat at 2x/day) ──────────
# Each post has a "thread" array: post 1 = hook (<200 chars), posts 2-3 = value, post 4 = CTA
POSTS = [
    # 1
    {
        "text": f"Built a Windows dictation app. Ctrl+Space → speak → text appears at your cursor in ~200ms.\n\nNo Dragon. No $500 license. No Mac required.\n\n30-day free trial → {SITE_URL}\n\n#productivity #Windows #buildinpublic",
        "thread": [
            f"Built a Windows dictation app. Ctrl+Space → speak → text appears at your cursor in ~200ms. #productivity #windows",
            "The gap nobody filled:\n\n• Win+H — stops mid-sentence, no auto-paste\n• Dragon — $500+\n• Wispr Flow — Mac only\n• Local Whisper — 1-2s lag\n\nFast + Windows + auto-paste at cursor didn't exist. So I built it.",
            "Tech: Electron + Groq Whisper API. Audio goes to Groq only — they don't store it.\n\nHotkey is fully remappable. Works in any app. #groq #whisper #devtools",
            f"30-day free trial, no credit card → {SITE_URL}\n\n#productivity #windows #buildinpublic",
        ],
        "title": "I built a push-to-talk dictation app for Windows — 200ms, auto-paste at cursor",
        "body": f"""## The problem

Every Windows dictation option is either too slow, too expensive, or Mac-only:
- Win+H: stops mid-sentence, no auto-paste
- Dragon: $500+
- Wispr Flow / Superwhisper: Mac only
- Local Whisper on CPU: 1-2 second lag

## What I built

**dictate.app** — press Ctrl+Space, speak, text injects at your cursor. Powered by Groq Whisper so transcription is ~200ms.

## How it works

1. Press hotkey (Ctrl+Space by default, fully remappable)
2. Speak into your mic
3. Text auto-pastes wherever your cursor is — any app, any text field

## Tech stack

- Electron (Windows native)
- Groq Whisper API for transcription
- No HMW servers — audio goes to Groq only, they don't store it

## Free trial

7 days free, no credit card. {SITE_URL}

Would love feedback from anyone who types a lot for work.
""",
    },
    # 2
    {
        "text": f"Speaking is 2.5x faster than typing.\n\nAverage typing speed: 60 wpm.\nAverage speaking speed: 150 wpm.\n\nI switched to voice dictation and never looked back.\n\nWindows tool → {SITE_URL}\n\n#productivity #indiedev",
        "thread": [
            "Speaking is 2.5x faster than typing. This is not a hot take. It's math. #productivity",
            f"Average typing speed: 60 wpm.\nAverage speaking speed: 150 wpm.\n\nIf you write more than 500 words a day, that gap is costing you hours every week.\n\nI built a Windows voice typing app to close it → {SITE_URL}",
            "What actually made the habit stick:\n\n→ Remap to a mouse side button (one thumb, no chord)\n→ Don't correct mid-sentence (finish the thought first)\n→ Start with emails, not code",
            f"dictate.app — Windows dictation via Groq Whisper. ~200ms latency, auto-paste at cursor.\n\n{SITE_URL}\n\n#productivity #buildinpublic #windows",
        ],
        "title": "How I went from 60 wpm to 150 wpm — dictating instead of typing",
        "body": f"""The math is simple: average typing speed is 60 wpm, average speaking speed is 150 wpm. That's 2.5x more output for free.

I've been dictating emails, Slack messages, docs, and code comments for months. Here's what actually helped:

**1. Start with low-stakes output**
Emails and Slack first. Not code. The accuracy is good but not perfect.

**2. Don't correct mid-sentence**
Let the whole thought finish, then fix. Stopping to say "scratch that" breaks your flow more than a typo does.

**3. Remap to muscle memory**
I moved from Ctrl+Space to a side mouse button. Now it's zero friction.

**Tool I use:** dictate.app (Windows) — Ctrl+Space, speak, text appears at cursor. ~200ms via Groq Whisper.

Free trial: {SITE_URL}
""",
    },
    # 3
    {
        "text": f"Windows dictation in 2026 is still broken.\n\nWin+H stops mid-sentence. Dragon costs $500. Local Whisper takes 2 seconds. Wispr Flow is Mac only.\n\nSo I built the thing that fills the gap → {SITE_URL}\n\n#buildinpublic #indiedev",
        "thread": [
            f"Windows dictation in 2026 is still a mess. So I fixed it. #windows #productivity",
            "The gap nobody filled:\n\n| Tool | Speed | Auto-paste | Windows |\n|------|-------|-----------|--------|\n| Win+H | slow | ✗ | ✓ |\n| Dragon | ok | ✓ | ✓ |\n| Local Whisper | slow | ✗ | ✓ |\n| Wispr Flow | fast | ✓ | ✗ |\n\nFast + auto-paste + Windows = doesn't exist.",
            "dictate.app fills it:\n→ Groq Whisper = ~200ms\n→ Auto-paste at cursor (not clipboard)\n→ Custom hotkey\n→ Bring your own Groq key (free tier works)\n\n#groq #whisper #devtools",
            f"Brutal feedback welcome → {SITE_URL}\n\n#indiedev #buildinpublic #windows",
        ],
        "title": "Windows dictation in 2026 is still broken — so I fixed it",
        "body": f"""Voice dictation on Windows in 2026 is still a mess:

| Tool | Speed | Auto-paste | Price |
|------|-------|-----------|-------|
| Win+H | 2-3s | No | Free |
| Dragon | OK | Yes | $500+ |
| Local Whisper | 1-2s | No | Free (but slow) |
| Wispr Flow | Fast | Yes | Mac only |

The gap: **fast + Windows + auto-paste at cursor**. That combination doesn't exist anywhere.

So I built dictate.app:
- Groq Whisper = ~200ms transcription
- Auto-paste directly at cursor (not just clipboard)
- Custom hotkey (default Ctrl+Space)
- Bring your own Groq API key (free tier works)

{SITE_URL} — 30-day free trial
""",
    },
    # 4
    {
        "text": f"Hot take: the best productivity upgrade isn't a new app.\n\nIt's stopping typing altogether.\n\nI dictate everything now. 150 wpm vs 60 wpm.\n\nWindows tool I built → {SITE_URL}\n\n#productivity #indiedev",
        "thread": [
            "Hot take: the best productivity upgrade isn't a new app. It's stopping typing altogether. #productivity",
            f"I dictate everything now. Emails. Slack. Docs. Even these posts.\n\n150 wpm vs 60 wpm. Same mental effort.\n\nWindows voice typing tool → {SITE_URL}",
            "The trick that made it stick: remap the hotkey to a mouse side button.\n\nOne thumb click, speak, done. It becomes invisible.",
            f"dictate.app — Windows dictation via Groq Whisper, ~200ms latency.\n\n{SITE_URL}\n\n#productivity #buildinpublic #windows",
        ],
        "title": "Hot take: stop typing. Your output will double.",
        "body": f"""Everyone's optimizing their note apps, task managers, and keyboard shortcuts.

Nobody's talking about the 2.5x unlock: just talk instead of type.

Average typing speed: 60 wpm.
Average speaking speed: 150 wpm.

**Use a mouse button, not a keyboard hotkey.** A side button is always reachable. No chord to remember. One click, speak, done.

**Don't stop to correct mid-sentence.** Let the thought finish. Fix after. Interrupting yourself costs more than a typo.

**Start with emails.** Low stakes, fast feedback loop.

**Tool I use on Windows:** dictate.app — Ctrl+Space (or any hotkey), speak, text appears at cursor. ~200ms via Groq Whisper.

Free trial: {SITE_URL}
""",
    },
    # 5
    {
        "text": f"Dragon NaturallySpeaking costs $500.\n\nGroq Whisper API costs $0.02 per hour of audio.\n\nIf you dictate 30 min/day, that's $3/month.\n\nI built the Windows app that uses it → {SITE_URL}\n\n#buildinpublic #productivity",
        "thread": [
            "Dragon NaturallySpeaking costs $500. Here's the math on doing it for under $2/month instead. #productivity",
            "Groq Whisper API pricing: $0.02 per hour of audio.\n\nIf you dictate 30 minutes per day × 30 days = 15 hours/month = $0.30/month.\n\nEven at 2 hours/day of heavy use: $1.20/month. #groq #whisper",
            "I built a Windows app that uses Groq Whisper. You bring your own API key (free tier works for light use).\n\nYou own your data. You see the cost. No markup. No lock-in. #devtools",
            f"dictate.app → {SITE_URL}\n\n30-day free trial, no credit card\n\n#buildinpublic #indiedev #windows",
        ],
        "title": "Dragon costs $500. Here's the math on doing it for $3/month.",
        "body": f"""Dragon NaturallySpeaking: $500 upfront.

Groq Whisper API: $0.02 per hour of audio.

If you dictate 30 minutes per day × 30 days = 15 hours/month = **$0.30/month**.

At 2 hours/day heavy use: **$1.20/month**.

Worst case, 4 hours/day: **$2.40/month**.

You bring your own Groq API key (free tier works for light use — up to a certain quota). I built the Windows app that wraps it with hotkey + auto-paste.

{SITE_URL} — 30-day free trial.
""",
    },
    # 6
    {
        "text": f"The thing nobody tells you about dictation:\n\nThe learning curve isn't accuracy.\n\nIt's learning to think out loud without editing yourself mid-sentence.\n\nThat part takes 2 weeks.\n\n→ {SITE_URL}\n\n#productivity",
        "thread": [
            "The thing nobody tells you about dictation: the learning curve isn't accuracy. #productivity",
            "Accuracy is fine from day one. Groq Whisper is good.\n\nThe actual curve: learning to think out loud without interrupting yourself.\n\nEvery instinct says 'no wait' and then you stop and start over. That's the habit to break. #whisper #groq",
            "2 weeks in, it clicks. You stop editing mid-sentence. You finish thoughts. The words flow.\n\nVoice typing on Windows becomes invisible — just thought-to-text.",
            f"dictate.app — Ctrl+Space, speak, text at cursor in ~200ms\n\n{SITE_URL}\n\n#productivity #buildinpublic #windows",
        ],
        "title": "The real dictation learning curve nobody talks about",
        "body": f"""The accuracy is fine from day one. Modern Whisper models are good.

The actual hard part: learning to think out loud without editing yourself mid-sentence.

Every instinct says "no wait, I meant—" and then you stop and restart. That's what slows you down, not the tool.

The fix: let the whole thought finish. Every time. Fix it after.

In two weeks, the instinct changes. You stop editing in real-time. Words flow.

Windows tool: {SITE_URL} — 30-day free trial.
""",
    },
    # 7
    {
        "text": f"Auto-paste at cursor is the feature that changes everything.\n\nNot clipboard. Not a text box you then copy from. Directly at cursor.\n\nSounds obvious. Somehow most dictation tools don't do it.\n\n→ {SITE_URL}\n\n#productivity #Windows",
        "thread": [
            "Auto-paste at cursor is the feature that changes everything about voice typing. #productivity #windows",
            "Most dictation tools give you:\n1. A separate text box\n2. Or clipboard paste (Ctrl+V yourself)\n\nNeither is frictionless. You break your workflow to use the tool.",
            "dictate.app injects text directly at your cursor. Any app. Any text field.\n\nCtrl+Space → speak → text appears. Done.\n\nNo window switch. No paste step. #devtools #windows",
            f"30-day free trial → {SITE_URL}\n\n#productivity #indiedev #buildinpublic",
        ],
        "title": "Why auto-paste at cursor changes everything about dictation",
        "body": f"""Most dictation tools give you one of two workflows:

1. A separate text box you type into, then copy from
2. Clipboard paste — it transcribes, you hit Ctrl+V

Neither is frictionless. You break your workflow every time.

dictate.app injects text directly at your cursor. Any app. Any text field. No window switch. No paste step.

The difference sounds small. In practice it's the whole product.

Windows: {SITE_URL} — 30-day free trial.
""",
    },
    # 8
    {
        "text": f"What I use to build dictate.app:\n\n• Electron (Windows native)\n• Groq Whisper API (transcription)\n• uiohook-napi (global hotkeys)\n• robotjs (cursor injection)\n\nThe stack is boring. The product works.\n\n→ {SITE_URL}\n\n#buildinpublic #indiedev",
        "thread": [
            f"Tech stack behind dictate.app — Windows voice typing at ~200ms: #devtools #buildinpublic",
            "• Electron — Windows native, handles the app shell\n• Groq Whisper API — transcription in ~200ms, $0.02/hr\n• uiohook-napi — global hotkey listener (works even when app is in background)\n• robotjs — types text at cursor position (simulates keystrokes)\n\n#groq #whisper #windows",
            "The hard part wasn't transcription. It was injecting text into elevated Windows processes.\n\nwmic, uiautomation, 3 approaches before it worked. Some apps block everything.\n\nTesting across every major Windows app was most of the build time. #devtools",
            f"dictate.app → {SITE_URL}\n\n30-day free trial\n\n#indiedev #buildinpublic",
        ],
        "title": "Tech stack: how I built a 200ms Windows dictation app",
        "body": f"""**Stack:**
- Electron — Windows native app shell
- Groq Whisper API — transcription in ~200ms at $0.02/hr
- uiohook-napi — global hotkey listener (works while app is backgrounded)
- robotjs — types text at cursor position (simulates keystrokes)

**The hard part:** reliable cursor injection across different apps.

Some apps block clipboard paste. Some block simulated keystrokes. Some do both. Testing across every major Windows app took most of the build time.

**The easy part:** transcription. Groq Whisper just works.

{SITE_URL} — 30-day free trial.
""",
    },
    # 9
    {
        "text": f"Built a Windows dictation app because I couldn't find one that did all three:\n\n✓ Fast (200ms)\n✓ Auto-paste at cursor\n✓ Works on Windows\n\nAll three together didn't exist. So I built it.\n\n{SITE_URL}\n\n#buildinpublic #indiedev",
        "thread": [
            "Built a Windows dictation app because I couldn't find one that did all three things I needed. #buildinpublic #windows",
            "The three requirements:\n\n1/ Fast — under 300ms or it breaks flow\n2/ Auto-paste at cursor — not clipboard, not a separate window\n3/ Windows — not Mac, not browser extension\n\nEvery tool I found missed at least one.",
            "Wispr Flow: fast, auto-paste, Mac only. ✗\nWin+H: Windows, free, slow, no auto-paste. ✗\nDragon: Windows, auto-paste, $500. ✗\n\nGroq Whisper made the speed possible. Everything else is UX. #groq #whisper #devtools",
            f"dictate.app — now it exists.\n\n{SITE_URL} — 30-day free trial\n\n#buildinpublic #indiedev #productivity",
        ],
        "title": "I built it because the tool I wanted didn't exist",
        "body": f"""Three requirements. Every existing tool missed at least one.

**1. Fast** — under 300ms or it breaks flow. Win+H takes 2-3 seconds. Local Whisper on CPU takes 1-2 seconds.

**2. Auto-paste at cursor** — not clipboard, not a separate window. The text should appear exactly where I'm typing.

**3. Windows** — not Mac, not a browser extension, not Linux. Just Windows.

Wispr Flow: fast, auto-paste, Mac only. ✗
Win+H: Windows, free, slow, no auto-paste. ✗
Dragon: Windows, auto-paste, $500. ✗

So I built dictate.app.

{SITE_URL} — 30-day free trial.
""",
    },
    # 10
    {
        "text": f"Week 1 feedback on dictate.app:\n\n'This is the first Windows dictation tool that doesn't make me want to throw my computer'\n\nThat's the bar. We cleared it.\n\n→ {SITE_URL}\n\n#buildinpublic #indiedev",
        "thread": [
            "Week 1 feedback on dictate.app — Windows voice typing via Groq Whisper: #buildinpublic #productivity",
            "'This is the first Windows dictation tool that doesn't make me want to throw my computer.'\n\n'I remapped it to my mouse button and haven't touched the keyboard for emails since.'\n\n'200ms feels like zero. I didn't know dictation could feel like this.'",
            "Latency is the whole product.\n\nAt 2 seconds, you're aware of the tool. At 200ms, you're not.\n\nThat threshold is the difference between a tool you use daily and one you uninstall after a week. #devtools #windows",
            f"Free trial → {SITE_URL}\n\n#buildinpublic #indiedev #whisper",
        ],
        "title": "Week 1 user feedback on dictate.app",
        "body": f"""The feedback I needed to hear:

*"This is the first Windows dictation tool that doesn't make me want to throw my computer."*

*"I remapped it to my mouse button and haven't touched the keyboard for emails since."*

*"200ms feels like zero. I didn't know dictation could feel like this."*

That's the bar. Latency and friction are the whole product. Clear those and people keep using it.

{SITE_URL} — 30-day free trial.
""",
    },
    # 11 — build-in-public: launch numbers
    {
        "text": f"shipped dictate.app last week. 47 trial installs, 0 paid. still figuring out the funnel. #buildinpublic\n\n{SITE_URL}",
        "thread": [
            "shipped dictate.app last week. 47 trial installs, 0 paid. still figuring out the funnel. #buildinpublic #indiedev",
            "what I know so far:\n\n→ people download it when they see the latency demo\n→ nobody reads the pricing page\n→ the trial-to-paid conversion path is unclear\n\nnext: add an in-app prompt on day 6 of the trial",
            "the product itself seems to work. groq whisper at ~200ms genuinely surprises people.\n\nthe problem is distribution and conversion, not the dictation. #groq #whisper #windows",
            f"if you've tried it and have feedback → {SITE_URL}\n\n#buildinpublic #productivity #devtools",
        ],
        "title": "dictate.app week 1: 47 installs, 0 paid — what I learned",
        "body": f"""Shipped dictate.app and here's the honest update:

**Numbers:**
- Trial installs: 47
- Paid conversions: 0
- Refunds: 0 (nothing to refund yet)

**What I know:**
- People download when they see the latency demo
- Nobody reads the pricing page
- The trial-to-paid path is unclear

**Next action:** in-app prompt on day 6 of trial. Make the ask explicit.

The product itself works — Groq Whisper at ~200ms genuinely surprises people. The problem is conversion, not dictation.

{SITE_URL}
""",
    },
    # 12 — build-in-public: cost/tech breakdown
    {
        "text": f"dictate.app uses groq whisper. 200ms latency. that's 3x faster than openai whisper. cost: ~$0.02/hr of speech. #devtools\n\n{SITE_URL}",
        "thread": [
            "dictate.app uses groq whisper. 200ms latency. that's 3x faster than openai whisper. cost: ~$0.02/hr of speech. #devtools #groq",
            "why groq over openai for whisper:\n\n→ groq: ~200ms per request\n→ openai: ~600-800ms per request\n→ both use the same whisper model\n\nlatency wins. for voice typing, 600ms feels broken. 200ms feels instant. #whisper #productivity",
            "you bring your own groq key. free tier covers light use. heavy users pay pennies.\n\nno middleman markup. no audio stored on my servers. just you + groq. #windows #devtools",
            f"dictate.app → {SITE_URL}\n\n#buildinpublic #indiedev #productivity",
        ],
        "title": "Why I use Groq instead of OpenAI for Whisper — the latency difference",
        "body": f"""Both Groq and OpenAI offer Whisper transcription. Here's why I went with Groq for dictate.app:

**Groq:** ~200ms per request
**OpenAI:** ~600-800ms per request

Same underlying Whisper model. 3x speed difference.

For voice typing, that gap is the whole product. At 600ms you're waiting. At 200ms you're not.

Cost: ~$0.02/hr of audio. You bring your own key. Free tier works for most users.

{SITE_URL} — 30-day free trial.
""",
    },
    # 13 — build-in-public: hardest technical problem
    {
        "text": f"the hardest part of building dictate.app wasn't the ai. it was injecting text into elevated windows processes. wmic, uiautomation, 3 approaches before it worked. #devtools #buildinpublic",
        "thread": [
            "the hardest part of building dictate.app wasn't the ai. it was injecting text into elevated windows processes. #devtools #buildinpublic",
            "approach 1: clipboard + simulated ctrl+v\n→ fails in apps running as admin (UAC elevation blocks it)\n\napproach 2: SendInput via win32\n→ works most places, fails in some terminals and IDEs\n\napproach 3: UI Automation + accessibility APIs\n→ slower but covers the edge cases #windows",
            "ended up with a hybrid: try SendInput first, fall back to UI Automation, final fallback to clipboard.\n\n3 code paths for what looks like one feature. windows is something else.\n\n#indiedev #devtools #whisper",
            f"dictate.app — the result of that work → {SITE_URL}\n\n#buildinpublic #windows #productivity",
        ],
        "title": "The hardest Windows programming problem I solved — text injection across elevated processes",
        "body": f"""Building dictate.app, the AI part (Groq Whisper) was easy. The Windows part was not.

**The problem:** injecting typed text into any app, including ones running with admin elevation.

**Approach 1:** Clipboard + simulated Ctrl+V
→ Fails in elevated apps (UAC blocks cross-privilege input)

**Approach 2:** SendInput via Win32 API
→ Works in most apps, fails in some terminals and IDEs

**Approach 3:** UI Automation / Accessibility APIs
→ More universal but ~50ms slower

**Solution:** Hybrid. Try SendInput first, fall back to UI Automation, final fallback to clipboard paste. Three code paths for what looks like one feature.

Windows is something else. But it works now across every major app I've tested.

{SITE_URL} — 30-day free trial.
""",
    },
    # 14 — build-in-public: honest limitations
    {
        "text": f"honest review of my own app — dictate.app limitations:\n\n• doesn't work well for code\n• elevated apps needed a workaround\n• no offline mode\n\nbut for everything else: it's the best voice typing on windows. #buildinpublic",
        "thread": [
            "honest review of my own app — dictate.app limitations nobody talks about: #buildinpublic #indiedev",
            "• doesn't work well for code (groq whisper isn't trained on syntax)\n• elevated apps required a 3-approach workaround\n• no offline mode — requires groq api connection\n• hotkey conflicts with some apps (remappable but annoying)\n\n#windows #whisper",
            "what it does well:\n\n• 200ms latency — genuinely feels instant\n• any text field in any normal app\n• auto-paste at cursor, not clipboard\n• groq key stays yours, audio never hits my servers\n\n#groq #productivity #devtools",
            f"if you write lots of prose — emails, docs, slack — it's the best windows dictation option i know of.\n\n{SITE_URL}\n\n#buildinpublic #productivity #windows",
        ],
        "title": "Honest review of my own dictation app — what it's bad at",
        "body": f"""I built dictate.app so I should be honest about what it doesn't do well.

**Weaknesses:**
- Code dictation: Groq Whisper isn't trained on syntax. Variable names, brackets, operators — accuracy is poor.
- Elevated processes: took 3 different approaches to handle admin apps. It works, but it's a hack.
- No offline mode: requires a Groq API connection. No internet = no dictation.
- Hotkey conflicts: some apps grab global hotkeys before we can. Remappable, but annoying to discover.

**Where it's strong:**
- ~200ms latency — the fastest Windows dictation option I know of
- Any text field in any non-elevated app
- True auto-paste at cursor, not clipboard
- Your Groq key stays yours — audio never hits my servers

For prose — emails, docs, Slack, notes — I believe it's the best option on Windows right now.

{SITE_URL} — 30-day free trial.
""",
    },
    # 15 — build-in-public: what's next
    {
        "text": f"next features for dictate.app:\n\n→ custom vocabulary (for jargon + names)\n→ silence detection (auto-stop recording)\n→ windows 11 tray redesign\n\nbuilding in public. what would you add? #buildinpublic\n\n{SITE_URL}",
        "thread": [
            "next features for dictate.app — windows voice typing via groq whisper: #buildinpublic #indiedev",
            "→ custom vocabulary: teach it your jargon, names, brand terms\n→ silence detection: auto-stop after 1.5s of silence instead of releasing hotkey\n→ windows 11 tray redesign: current one is ugly and I know it\n\n#windows #devtools #whisper",
            "not building:\n\n✗ mac version (different beast)\n✗ browser extension (too limited)\n✗ self-hosted whisper (latency tradeoff isn't worth it for most users)\n\nfocused on making windows dictation the best it can be. #groq #productivity",
            f"what would you add? → {SITE_URL}\n\n#buildinpublic #windows #productivity #devtools",
        ],
        "title": "What's next for dictate.app — the roadmap, honest version",
        "body": f"""Building in public means sharing what's actually on the list.

**Building next:**
- Custom vocabulary: teach it your jargon, names, brand terms. Groq Whisper has a prompt parameter for this.
- Silence detection: auto-stop after 1.5s of silence instead of requiring hotkey release.
- Windows 11 tray redesign: current one is functional but ugly.

**Not building:**
- Mac version: different OS, different text injection APIs, different app entirely.
- Browser extension: too limited, can't access native app text fields.
- Self-hosted Whisper: local models have 1-2s latency. The cloud tradeoff is worth it.

**Why these and not others:** staying focused on Windows voice typing being the best it can be. Adding platforms dilutes that.

Feedback welcome: {SITE_URL}
""",
    },
]

# ── Bluesky helpers ────────────────────────────────────────────────────────────
def build_facets(text):
    """Build AT Protocol facets using regex match positions (handles duplicates correctly)."""
    facets = []
    text_bytes = text.encode("utf-8")

    def char_to_byte(char_pos):
        return len(text[:char_pos].encode("utf-8"))

    for m in re.finditer(r'https?://[^\s\)]+', text):
        byte_start = char_to_byte(m.start())
        byte_end = char_to_byte(m.end())
        facets.append({
            "index": {"byteStart": byte_start, "byteEnd": byte_end},
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": m.group(0)}]
        })

    for m in re.finditer(r'#(\w+)', text):
        byte_start = char_to_byte(m.start())
        byte_end = char_to_byte(m.end())
        facets.append({
            "index": {"byteStart": byte_start, "byteEnd": byte_end},
            "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": m.group(1)}]
        })

    return facets


def bsky_session(handle, password):
    data = json.dumps({"identifier": handle, "password": password}).encode()
    req = urllib.request.Request(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def bsky_create_post(session, text):
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    text = text[:300]
    record = {"$type": "app.bsky.feed.post", "text": text, "createdAt": now}
    facets = build_facets(text)
    if facets:
        record["facets"] = facets
    data = json.dumps({
        "repo": session["did"],
        "collection": "app.bsky.feed.post",
        "record": record
    }).encode()
    req = urllib.request.Request(
        "https://bsky.social/xrpc/com.atproto.repo.createRecord",
        data=data,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + session["accessJwt"]},
        method="POST"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def bsky_create_reply(session, text, root_uri, root_cid, parent_uri, parent_cid):
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    text = text[:300]
    record = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": now,
        "reply": {
            "root": {"uri": root_uri, "cid": root_cid},
            "parent": {"uri": parent_uri, "cid": parent_cid}
        }
    }
    facets = build_facets(text)
    if facets:
        record["facets"] = facets
    data = json.dumps({
        "repo": session["did"],
        "collection": "app.bsky.feed.post",
        "record": record
    }).encode()
    req = urllib.request.Request(
        "https://bsky.social/xrpc/com.atproto.repo.createRecord",
        data=data,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + session["accessJwt"]},
        method="POST"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def post_bluesky_thread(handle, password, post):
    session = bsky_session(handle, password)
    thread = post.get("thread", [post["text"]])

    root = bsky_create_post(session, thread[0])
    root_uri, root_cid = root["uri"], root["cid"]
    parent_uri, parent_cid = root_uri, root_cid

    for reply_text in thread[1:]:
        reply = bsky_create_reply(session, reply_text, root_uri, root_cid, parent_uri, parent_cid)
        parent_uri, parent_cid = reply["uri"], reply["cid"]

    return root


# ── dev.to ────────────────────────────────────────────────────────────────────
def post_devto(api_key, title, body):
    data = json.dumps({
        "article": {
            "title": title,
            "body_markdown": body,
            "published": True,
            "tags": ["productivity", "windows", "ai", "devtools"],
            "canonical_url": None
        }
    }).encode()
    req = urllib.request.Request(
        "https://dev.to/api/articles",
        data=data,
        headers={"Content-Type": "application/json", "api-key": api_key},
        method="POST"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


# ── Mastodon ──────────────────────────────────────────────────────────────────
def post_mastodon(instance, token, text):
    data = urllib.parse.urlencode({"status": text[:500], "visibility": "public"}).encode()
    req = urllib.request.Request(
        f"https://{instance}/api/v1/statuses",
        data=data,
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/x-www-form-urlencoded"},
        method="POST"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    now_utc = datetime.datetime.utcnow()
    day_of_year = now_utc.timetuple().tm_yday
    # slot 0 = morning run (~10 AM ET = 15 UTC), slot 1 = evening run (~7 PM ET = 23 UTC)
    slot = 0 if now_utc.hour < 20 else 1
    idx = (day_of_year * 2 + slot) % len(POSTS)
    post = POSTS[idx]

    print(f"Day {day_of_year}, slot {slot} → post #{idx + 1}: {post['title']}")
    results = {}

    bsky_handle   = os.getenv("BLUESKY_HANDLE")
    bsky_password = os.getenv("BLUESKY_PASSWORD")
    if bsky_handle and bsky_password:
        try:
            results["bluesky"] = post_bluesky_thread(bsky_handle, bsky_password, post)
            print(f"✓ Bluesky thread posted ({len(post.get('thread', [post['text']]))} parts)")
        except Exception as e:
            print(f"✗ Bluesky: {e}")

    # dev.to: Tue + Thu mornings (weekdays 1 and 3), morning slot only
    devto_key = os.getenv("DEVTO_API_KEY")
    if devto_key and now_utc.weekday() in (1, 3) and slot == 0:
        try:
            results["devto"] = post_devto(devto_key, post["title"], post["body"])
            print("✓ dev.to posted")
        except Exception as e:
            print(f"✗ dev.to: {e}")
    elif devto_key:
        print(f"· dev.to skipped (posts Tue/Thu mornings, today={now_utc.strftime('%A')})")

    masto_token    = os.getenv("MASTODON_TOKEN")
    masto_instance = os.getenv("MASTODON_INSTANCE", "mastodon.social")
    if masto_token:
        try:
            results["mastodon"] = post_mastodon(masto_instance, masto_token, post["text"])
            print("✓ Mastodon posted")
        except Exception as e:
            print(f"✗ Mastodon: {e}")

    print(json.dumps(results, indent=2))
