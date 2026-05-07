#!/usr/bin/env python3
"""
dictate.app auto-poster — Bluesky + dev.to + Mastodon
2x/day (10 AM ET + 7 PM ET). Dev.to Tuesdays only.
"""
import os, json, urllib.request, urllib.parse, datetime, re

SITE_URL = "https://dictate-app.pages.dev"

# ── Content bank (20 posts, ~10 days before any repeat at 2x/day) ─────────────
POSTS = [
    # 1
    {
        "text": f"Built a Windows dictation app. Ctrl+Space → speak → text appears at your cursor in ~200ms.\n\nNo Dragon. No $500 license. No Mac required.\n\n30-day free trial → {SITE_URL}\n\n#productivity #Windows #buildinpublic",
        "thread": [
            f"Built a Windows dictation app. Ctrl+Space → speak → text appears at your cursor in ~200ms.\n\nFree trial → {SITE_URL}",
            "The gap:\n\n• Win+H — stops mid-sentence, no auto-paste\n• Dragon — $500+\n• Wispr Flow — Mac only\n• Local Whisper — 1-2s lag\n\nFast + Windows + auto-paste at cursor didn't exist. So I built it.",
            "Tech: Electron + Groq Whisper. Audio goes to Groq only — they don't store it.\n\nHotkey is fully remappable. Works in any app.\n\n#indiedev #buildinpublic",
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
            "Speaking is 2.5x faster than typing. This is not a hot take. It's math.",
            f"Average typing speed: 60 wpm.\nAverage speaking speed: 150 wpm.\n\nIf you write more than 500 words a day, that gap is costing you hours every week.\n\nI built a Windows app to close it → {SITE_URL}",
            "What actually made the habit stick:\n\n→ Remap to a mouse side button (one thumb, no chord)\n→ Don't correct mid-sentence (finish the thought first)\n→ Start with emails, not code\n\n#productivity #buildinpublic",
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
            f"Windows dictation in 2026 is still a mess. So I fixed it.\n\n{SITE_URL}",
            "The gap nobody filled:\n\n| Tool | Speed | Auto-paste | Windows |\n|------|-------|-----------|--------|\n| Win+H | slow | ✗ | ✓ |\n| Dragon | ok | ✓ | ✓ |\n| Local Whisper | slow | ✗ | ✓ |\n| Wispr Flow | fast | ✓ | ✗ |\n\nFast + auto-paste + Windows = doesn't exist.",
            "dictate.app fills it:\n→ Groq Whisper = ~200ms\n→ Auto-paste at cursor (not clipboard)\n→ Custom hotkey\n→ Bring your own Groq key (free tier works)\n\nBrutal feedback welcome.\n\n#indiedev #buildinpublic",
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
            "Hot take: the best productivity upgrade isn't a new app. It's stopping typing altogether.",
            f"I dictate everything now. Emails. Slack. Docs. Even these posts.\n\n150 wpm vs 60 wpm. Same mental effort.\n\nWindows tool → {SITE_URL}",
            "The trick that made it stick: remap the hotkey to a mouse side button.\n\nOne thumb click, speak, done. It becomes invisible.\n\n#productivity #buildinpublic",
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
        "text": f"I was skeptical about voice dictation.\n\nSeemed gimmicky. Seemed slow. Seemed like I'd spend more time correcting than typing.\n\nThen I tried it for a week.\n\n→ {SITE_URL}\n\n#productivity #Windows",
        "thread": [
            "I was skeptical about voice dictation. Seemed gimmicky. Seemed slow.",
            "Then I tried it for a week.\n\nWeek 1: slower than typing (expected)\nWeek 2: about the same speed\nWeek 3: noticeably faster\nMonth 2: I genuinely don't want to type long things anymore",
            f"The tool that got me there: dictate.app — Ctrl+Space, speak, text appears at cursor in ~200ms on Windows.\n\nFree trial → {SITE_URL}\n\n#productivity #buildinpublic",
        ],
        "title": "I was skeptical about voice dictation. Then I tried it.",
        "body": f"""I thought dictation was for people who couldn't type. I was wrong.

**Week 1:** Slower than typing. Expected.
**Week 2:** About the same speed. Accuracy improving.
**Week 3:** Noticeably faster. The corrections are getting rarer.
**Month 2:** I genuinely don't want to type long things anymore.

The thing that changed it: a tool that actually works. Low latency (~200ms), auto-paste at cursor, no friction.

If the tool is slow, you blame yourself. If the tool is fast, you blame nothing.

Windows: {SITE_URL} — 30-day free trial.
""",
    },
    # 6
    {
        "text": f"If you write more than 1,000 words a day, you should try dictation.\n\nNot because typing is slow. Because speaking is faster.\n\nThe math: 60 wpm typing vs 150 wpm speaking. You're leaving hours on the table.\n\n→ {SITE_URL}\n\n#productivity",
        "thread": [
            "If you write more than 1,000 words a day, you should try dictation.",
            "Not because typing is slow.\n\nBecause speaking is faster.\n\n60 wpm vs 150 wpm. If you write 2,000 words/day that's 33 minutes typing vs 13 minutes speaking.\n\n20 minutes/day = 120 hours/year.",
            f"The Windows tool that makes this actually work: dictate.app\n\nCtrl+Space → speak → text at cursor in ~200ms\n\n{SITE_URL} — 30-day free trial\n\n#productivity #indiedev",
        ],
        "title": "If you write 1,000+ words a day, you're leaving time on the table",
        "body": f"""60 wpm typing. 150 wpm speaking. That's not an opinion, it's an average.

If you write 2,000 words per day:
- Typing: ~33 minutes
- Speaking: ~13 minutes
- Difference: 20 minutes

Over a year, that's 120 hours.

The bottleneck isn't tool quality anymore. It's habits and latency. If dictation feels slow, the tool is the problem — not you.

Windows: {SITE_URL} — 30-day free trial.
""",
    },
    # 7
    {
        "text": f"Sent 40 emails today.\n\nTyped maybe 150 words total.\n\nThe rest was dictated. Each email: hold button, speak, done.\n\nWindows app → {SITE_URL}\n\n#productivity #buildinpublic",
        "thread": [
            "Sent 40 emails today. Typed maybe 150 words total.",
            "The rest was dictated.\n\nEach email: hold button, speak, release. Text appears where my cursor is.\n\nThe whole thing takes as long as thinking of what to say — not longer.",
            f"Tool: dictate.app for Windows\nHotkey: Ctrl+Space (remappable)\nLatency: ~200ms via Groq Whisper\n\n{SITE_URL} — 30-day free trial\n\n#productivity #indiedev",
        ],
        "title": "I sent 40 emails today and typed almost nothing",
        "body": f"""Dictated all of them. Each one: hold hotkey, speak, release. Text appears at cursor.

The whole thing takes as long as thinking — not longer.

Email is the perfect starting point for dictation:
- Low stakes (you'll proofread anyway)
- Short bursts (not 10-minute monologues)
- High volume (you write dozens a day)

After a week of email dictation, everything else follows.

Windows: {SITE_URL} — 30-day free trial.
""",
    },
    # 8
    {
        "text": f"The thing nobody tells you about dictation:\n\nThe learning curve isn't accuracy.\n\nIt's learning to think out loud without editing yourself mid-sentence.\n\nThat part takes 2 weeks.\n\n→ {SITE_URL}\n\n#productivity",
        "thread": [
            "The thing nobody tells you about dictation: the learning curve isn't accuracy.",
            "Accuracy is fine from day one. Groq Whisper is good.\n\nThe actual curve: learning to think out loud without interrupting yourself.\n\nEvery instinct says 'no wait' and then you stop and start over. That's the habit to break.",
            f"2 weeks in, it clicks. You stop editing mid-sentence. You finish thoughts. The words flow.\n\ndictate.app — Ctrl+Space, speak, text at cursor in ~200ms\n\n{SITE_URL}\n\n#productivity #buildinpublic",
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
    # 9
    {
        "text": f"Remap your dictation hotkey to a mouse side button.\n\nIt sounds trivial. It's not.\n\nOne thumb click, speak, text appears. Zero friction. Becomes muscle memory in 3 days.\n\n→ {SITE_URL}\n\n#productivity #Windows",
        "thread": [
            "One change that made dictation actually stick: remap the hotkey to a mouse side button.",
            "Keyboard chords have a problem: you have to stop what you're doing to reach them.\n\nA mouse side button is always there. Your thumb never leaves it. One click, speak, done.\n\nZero interruption to hand position.",
            f"Dictation tool I use: dictate.app — fully remappable hotkey, ~200ms latency, auto-paste at cursor.\n\nWindows only → {SITE_URL}\n\n#productivity #indiedev",
        ],
        "title": "The one remapping that makes dictation actually stick",
        "body": f"""Keyboard hotkeys for dictation have a problem: you have to stop what you're doing to reach them.

A mouse side button solves this. Your thumb is already there. One click, speak, done. Hand position doesn't change.

It sounds trivial. It's not. This one change is why dictation went from "interesting experiment" to "I can't work without it."

dictate.app has fully remappable hotkeys. Set it once, forget it exists.

Windows: {SITE_URL} — 30-day free trial.
""",
    },
    # 10
    {
        "text": f"Built a Windows dictation app because I couldn't find one that did all three:\n\n✓ Fast (200ms)\n✓ Auto-paste at cursor\n✓ Works on Windows\n\nAll three together didn't exist. So I built it.\n\n{SITE_URL}\n\n#buildinpublic #indiedev",
        "thread": [
            "Built a Windows dictation app because I couldn't find one that did all three things I needed.",
            "The three requirements:\n\n1/ Fast — under 300ms or it breaks flow\n2/ Auto-paste at cursor — not clipboard, not a separate window\n3/ Windows — not Mac, not browser extension\n\nEvery tool I found missed at least one.",
            f"So I built dictate.app.\n\nGroq Whisper = ~200ms\nAuto-paste at cursor = ✓\nWindows native = ✓\n\n{SITE_URL} — 30-day free trial\n\n#buildinpublic #indiedev",
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
    # 11
    {
        "text": f"My writing output in one month of dictating everything:\n\n• Emails: 3x faster\n• Slack: barely notice I'm writing\n• Docs: still adjusting\n• Code comments: actually writing them now\n\nWindows tool → {SITE_URL}\n\n#productivity",
        "thread": [
            "One month of dictating everything. Here's what actually changed.",
            "Emails: 3x faster. I don't dread the inbox anymore.\n\nSlack: I barely notice I'm writing. Messages come out in full sentences instead of fragments.\n\nDocs: still adjusting. Longer-form thinking out loud is a different skill.\n\nCode comments: I'm actually writing them now because there's no friction.",
            f"Tool: dictate.app — Ctrl+Space, speak, 200ms, auto-paste.\n\nWindows only → {SITE_URL}\n\n#productivity #buildinpublic",
        ],
        "title": "One month of dictating everything — what actually changed",
        "body": f"""**Emails:** 3x faster. I don't dread the inbox anymore.

**Slack:** I barely notice I'm writing. Messages come out in full sentences instead of fragments.

**Docs:** Still adjusting. Longer-form thinking out loud is a different skill than typing.

**Code comments:** I'm actually writing them now. Zero friction means zero excuse not to.

**The surprise:** My writing got worse before it got better. You think slower than you speak. But then it evens out.

Tool: {SITE_URL} — 30-day free trial.
""",
    },
    # 12
    {
        "text": f"Dragon NaturallySpeaking costs $500.\n\nGroq Whisper API costs $0.02 per hour of audio.\n\nIf you dictate 30 min/day, that's $3/month.\n\nI built the Windows app that uses it → {SITE_URL}\n\n#buildinpublic #productivity",
        "thread": [
            "Dragon NaturallySpeaking costs $500. Here's the math on doing it for $3/month instead.",
            "Groq Whisper API pricing: $0.02 per hour of audio.\n\nIf you dictate 30 minutes per day × 30 days = 15 hours/month = $0.30/month.\n\nEven at 2 hours/day of heavy use: $1.20/month.",
            f"I built a Windows app that uses Groq Whisper. You bring your own API key (free tier works for light use).\n\ndictate.app → {SITE_URL}\n\n30-day free trial, no credit card\n\n#buildinpublic #indiedev",
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
    # 13
    {
        "text": f"The best writing tool is your voice.\n\nYou already have it. You've had it your whole life.\n\nYou're just not using it to write.\n\n→ {SITE_URL}\n\n#productivity #writing",
        "thread": [
            "The best writing tool is your voice. You already have it.",
            "Speaking is how humans have communicated for 200,000 years.\n\nTyping is how we've communicated for 170.\n\nYour brain is optimized for speech. Lean into that.",
            f"dictate.app — Ctrl+Space, speak, text appears at cursor in ~200ms.\n\nWindows native → {SITE_URL}\n\n#productivity #buildinpublic",
        ],
        "title": "The best writing tool is already built into you",
        "body": f"""Speaking is how humans have communicated for 200,000 years.

Typing is how we've communicated for 170.

Your brain is optimized for speech. Sentences flow naturally. Thoughts connect. You don't get "writer's block" when you're talking — you get conversational block, which is different and rarer.

The friction is the tool, not the skill. Low-latency auto-paste dictation removes that friction.

Windows: {SITE_URL} — 30-day free trial.
""",
    },
    # 14
    {
        "text": f"Building in public update:\n\nShipped dictate.app — Windows dictation, 200ms, auto-paste.\n\nBiggest fear: it would just be Win+H with extra steps.\nResult: it's not. The latency and auto-paste make it a different category.\n\n→ {SITE_URL}\n\n#buildinpublic",
        "thread": [
            f"Building in public update: shipped dictate.app for Windows.\n\n{SITE_URL}",
            "Biggest fear going in: I was just rebuilding Win+H with extra steps.\n\nResult: the 200ms latency and true auto-paste (at cursor, not clipboard) make it feel like a different category of tool.",
            "What I learned: latency is the product.\n\nAt 2 seconds, you notice the gap. At 200ms, you don't. That threshold is the entire difference between a tool you use and a tool you forget.\n\n#buildinpublic #indiedev",
        ],
        "title": "Building in public: what I learned shipping a Windows dictation app",
        "body": f"""Biggest fear: I was just rebuilding Win+H with extra steps.

Result: the 200ms latency and true auto-paste at cursor (not clipboard) make it feel like a different category.

**What I learned: latency is the product.**

At 2 seconds, you're aware of the tool. At 200ms, you're not. That threshold is the entire difference between a tool you use daily and a tool you uninstall after a week.

Groq Whisper makes the 200ms number possible. Everything else is UX.

30-day free trial: {SITE_URL}
""",
    },
    # 15
    {
        "text": f"Ctrl+Space is my most-used keyboard shortcut.\n\nMore than Ctrl+C. More than Ctrl+Z. More than Alt+Tab.\n\nEvery time I need to write something, I press it.\n\n→ {SITE_URL}\n\n#productivity #Windows",
        "thread": [
            "Ctrl+Space is now my most-used keyboard shortcut. More than Ctrl+C.",
            "Every time I need to write something: Ctrl+Space, speak, done.\n\nEmails, Slack, search bars, doc titles, commit messages, everything.\n\nThe hotkey is fully remappable but I haven't changed it. It's muscle memory now.",
            f"dictate.app — Windows dictation that actually works.\n\nCtrl+Space → speak → 200ms → text at cursor.\n\n{SITE_URL} — 30-day free trial\n\n#productivity #buildinpublic",
        ],
        "title": "Ctrl+Space became my most-used shortcut",
        "body": f"""More than Ctrl+C. More than Ctrl+Z. More than Alt+Tab.

Every time I need to write anything — email, Slack, search bar, doc title, commit message — I press it.

The process: Ctrl+Space, speak, text appears at cursor.

That's the whole thing. No window switches. No clipboard paste. No mode changes. Just text where I need it.

Windows: {SITE_URL} — 30-day free trial.
""",
    },
    # 16
    {
        "text": f"Auto-paste at cursor is the feature that changes everything.\n\nNot clipboard. Not a text box you then copy from. Directly at cursor.\n\nSounds obvious. Somehow most dictation tools don't do it.\n\n→ {SITE_URL}\n\n#productivity #Windows",
        "thread": [
            "Auto-paste at cursor is the feature that changes everything about dictation.",
            "Most dictation tools give you:\n1. A separate text box\n2. Or clipboard paste (Ctrl+V yourself)\n\nNeither is frictionless. You break your workflow to use the tool.",
            f"dictate.app injects text directly at your cursor. Any app. Any text field.\n\nCtrl+Space → speak → text appears. Done.\n\n{SITE_URL} — 30-day free trial\n\n#productivity #indiedev",
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
    # 17
    {
        "text": f"Bring your own API key — it's the right model.\n\nYou control your data. You see the cost. No markup. No lock-in.\n\nMy Windows dictation app uses Groq Whisper. You bring the key.\n\n→ {SITE_URL}\n\n#buildinpublic #indiedev",
        "thread": [
            "\"Bring your own API key\" is the right model for AI tools. Here's why.",
            "When the tool controls the API:\n• You don't know where your data goes\n• You pay a markup on compute\n• You're locked in\n\nWhen you bring your own key:\n• Groq's privacy policy is what matters (they don't store audio)\n• You pay actual cost (~$0.02/hr)\n• You can switch tools tomorrow",
            f"dictate.app uses this model. Bring your own Groq API key (free tier works for light use).\n\nWindows → {SITE_URL}\n\n#buildinpublic #indiedev",
        ],
        "title": "Why bring-your-own-API-key is the right model for AI tools",
        "body": f"""When the tool controls the API:
- You don't know where your data goes
- You pay a markup on compute
- You're locked in to their pricing and existence

When you bring your own key:
- The AI provider's privacy policy is what matters — not a middle layer
- You pay actual cost (Groq Whisper: ~$0.02/hr of audio)
- You can switch tools tomorrow without losing anything

dictate.app uses this model. Bring your own Groq API key. Free tier covers light use.

{SITE_URL} — 30-day free trial.
""",
    },
    # 18
    {
        "text": f"Things I no longer type:\n\n• Emails (dictated)\n• Slack messages (dictated)\n• Search queries (dictated)\n• Meeting notes (dictated)\n\nThings I still type:\n\n• Code\n• Passwords\n\n→ {SITE_URL}\n\n#productivity",
        "thread": [
            "Things I no longer type:\n\n• Emails\n• Slack messages\n• Search queries\n• Meeting notes\n• Jira tickets\n• Doc titles",
            "Things I still type:\n\n• Code (accuracy isn't there yet for syntax)\n• Passwords (you don't want to say those out loud)\n\nEverything else: dictated.",
            f"Tool: dictate.app — Ctrl+Space, speak, text at cursor in ~200ms.\n\nWindows only → {SITE_URL}\n\n#productivity #buildinpublic",
        ],
        "title": "Everything I stopped typing (and what I still type)",
        "body": f"""**No longer typed:**
- Emails
- Slack messages
- Search queries
- Meeting notes
- Jira tickets
- Doc titles and headings

**Still typed:**
- Code (accuracy isn't reliable enough for syntax)
- Passwords (don't say those out loud)

Everything else: dictated. The division happened naturally over about 3 weeks.

Tool: {SITE_URL} — 30-day free trial.
""",
    },
    # 19
    {
        "text": f"What I use to build dictate.app:\n\n• Electron (Windows native)\n• Groq Whisper API (transcription)\n• uiohook-napi (global hotkeys)\n• robotjs (cursor injection)\n\nThe stack is boring. The product works.\n\n→ {SITE_URL}\n\n#buildinpublic #indiedev",
        "thread": [
            f"Tech stack behind dictate.app (Windows dictation, ~200ms):\n\n{SITE_URL}",
            "• Electron — Windows native, handles the app shell\n• Groq Whisper API — transcription in ~200ms, $0.02/hr\n• uiohook-napi — global hotkey listener (works even when app is in background)\n• robotjs — types text at cursor position (simulates keystrokes)",
            "The hard part wasn't transcription. It was reliable cursor injection across different apps.\n\nSome apps block clipboard paste. Some block simulated keystrokes. Testing across every major Windows app was most of the work.\n\n#buildinpublic #indiedev",
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
    # 20
    {
        "text": f"Week 1 feedback on dictate.app:\n\n'This is the first Windows dictation tool that doesn't make me want to throw my computer'\n\nThat's the bar. We cleared it.\n\n→ {SITE_URL}\n\n#buildinpublic #indiedev",
        "thread": [
            "Week 1 feedback on dictate.app:",
            "'This is the first Windows dictation tool that doesn't make me want to throw my computer.'\n\n'I remapped it to my mouse button and haven't touched the keyboard for emails since.'\n\n'200ms feels like zero. I didn't know dictation could feel like this.'",
            f"That's the bar. Clear it and people keep using it.\n\nFree trial → {SITE_URL}\n\n#buildinpublic #indiedev",
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
            "tags": ["productivity", "windows", "buildinpublic", "indiedev"]
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

    # dev.to: Tuesdays only (weekday 1), morning slot only
    devto_key = os.getenv("DEVTO_API_KEY")
    if devto_key and now_utc.weekday() == 1 and slot == 0:
        try:
            results["devto"] = post_devto(devto_key, post["title"], post["body"])
            print("✓ dev.to posted")
        except Exception as e:
            print(f"✗ dev.to: {e}")
    elif devto_key:
        print("· dev.to skipped (only posts Tuesday mornings)")

    masto_token    = os.getenv("MASTODON_TOKEN")
    masto_instance = os.getenv("MASTODON_INSTANCE", "mastodon.social")
    if masto_token:
        try:
            results["mastodon"] = post_mastodon(masto_instance, masto_token, post["text"])
            print("✓ Mastodon posted")
        except Exception as e:
            print(f"✗ Mastodon: {e}")

    print(json.dumps(results, indent=2))
