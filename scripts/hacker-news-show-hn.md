# Show HN: Hacker News Draft

## Title (79 chars)
Show HN: dictate.app – push-to-talk voice dictation for Windows using Groq Whisper

---

## Maker Comment (post as first comment immediately after submission)

I built this because I was paying $599 for Dragon and it kept crashing on Windows 11. The free alternative (Win+H) works maybe 60% of the time and breaks completely inside Electron apps, VS Code, and anything that isn't a standard Win32 window.

The core technical problem with real-time dictation is latency. If there's more than ~400ms between when you stop speaking and when text appears, you lose the flow state that makes dictation faster than typing. OpenAI's Whisper API averages 2-3 seconds round-trip. Groq runs the same Whisper large-v3 model on their LPU hardware and returns in ~200ms. That gap is the entire product.

For app compatibility: instead of injecting keystrokes character-by-character (which breaks in rich text editors and anything with autocomplete), I transcribe to clipboard and fire Ctrl+V. Works everywhere Win32 supports paste — which is basically every app. The tradeoff is it clobbers whatever was in your clipboard, so I save and restore it. There's a race condition on some apps that I haven't fully solved.

What surprised me: users didn't want always-on voice activation. They wanted push-to-talk — hold a key, speak, release, text appears. That's now the primary mode. The "wake word" approach felt surveilled and triggered constantly in noisy environments.

What it doesn't do well yet: dictating code (variable names come out as prose), non-English languages (Whisper handles them but I haven't tested extensively), and anything requiring sub-100ms latency like live captions.

Current state: ~500 users, $8.99/month, 7-day free trial. 40% recurring affiliate program if anyone wants to write about it.

Stack: Electron, Node.js, Groq SDK, Windows native APIs for hotkey capture.

Happy to answer questions about the Groq integration, the clipboard approach, or why Electron was the wrong and then right choice.

---

## 3 Likely HN Questions + Honest Answers

**Q: Why Electron? It's bloated for a utility app.**
A: I tried a native Windows C# app first. The problem is distributing code-signing certs and getting past Windows Defender SmartScreen for unsigned binaries is brutal for a solo bootstrapped app. Electron ships with a trusted signing story via the app store or standard installers. The RAM overhead (~120MB) is real but most users don't care. I might revisit with Tauri eventually.

**Q: Groq could change their pricing or go down. What's your fallback?**
A: Fair risk. I have OpenAI Whisper as a fallback but it's slower. I'm keeping the API abstraction layer thin enough to swap. If Groq raises prices to unsustainable levels the product math breaks — I'd have to raise prices or find another inference provider. This is a known dependency risk I've accepted.

**Q: Why not just use Windows Speech Recognition built in to Windows?**
A: WSR uses Microsoft's older acoustic model, not Whisper. Accuracy is noticeably worse on technical vocabulary, accents, and anything outside standard American English. It also doesn't support push-to-talk with arbitrary hotkeys, and it breaks in the same Electron/non-standard window contexts as Win+H. I benchmarked both on the same hardware — Whisper wins on accuracy even accounting for the round-trip latency.

---

## Best Time to Post

**Target: Tuesday or Wednesday, 9-10 AM Eastern**

HN front page peaks 9 AM–2 PM ET on weekdays. Tuesday/Wednesday have less competition than Monday (people catching up) and Thursday/Friday (people checking out). Avoid weekends entirely — lower traffic, slower velocity means you fall off the front page before US West Coast wakes up.

Post, then immediately post your maker comment. Stay online for the first 2 hours to reply to every comment. Early comment velocity signals to HN's ranking that a post has engagement.

---

## What NOT to Say (phrases that get downvoted instantly)

- "disruptive" / "disrupting the X space"
- "10x better than Dragon" (make them conclude this, don't say it)
- "AI-powered" as a feature, not an explanation
- "seamless" / "frictionless" / "effortless"
- "we" when it's just you (HN respects honest solo builders)
- Fake user quotes in the submission text
- "I'm not a marketer so..." (then don't market)
- Mentioning the affiliate program in the submission (fine in comments if someone asks)
- "excited to share" / "thrilled to announce"
- Any mention of "journeys" or "spaces"
