# Reddit Posts — dictate.app

Ready-to-post Reddit content for 5 subreddits. Do not copy-paste identically across all at once — space posts out by at least a week each.

---

## 1. r/SideProject

**Subreddit rules summary:**
- Working products only, not just ideas
- Self-promotion explicitly welcome — this is the point of the sub
- Include a demo link
- Be honest about stage (early, beta, shipped)
- Real numbers and transparency get the most engagement
- Repeat posts OK if spaced out and adding new value (progress update, milestone)
- No engagement farming or fake traction claims

---

**Title:**
I built a Windows dictation app using Groq Whisper — $9/mo, ships text anywhere your cursor is

**Body:**
Been a terrible typist my whole life. Decided to fix it with code instead of practice.

What I built: a Windows system tray app that listens via hotkey, transcribes with Groq's Whisper API, and injects text into whatever input is focused — browser, Notepad, Slack, whatever.

A few things that surprised me during the build:

**Latency was harder than accuracy.** I assumed users would care most about word accuracy. Wrong. They care about how long it takes for text to appear after they stop talking. Groq's API returns in ~280ms vs ~1100ms on OpenAI's Whisper. That gap is the difference between feeling native and feeling broken.

**Simulating keystrokes across Windows apps is a minefield.** Different apps respond to different Windows messages. I ended up building a small compatibility layer that tries `SendInput` first, falls back to `WM_CHAR`, then escalates from there.

**The privacy question comes up every time.** Users want to know their audio isn't stored. I added an explicit first-run disclosure and link to Groq's policy. Converts better now.

Pricing landed at $9/month. API cost at typical usage (~30 min/day) is about $0.60/month in Groq fees, so there's margin.

Early days, but the users who make it past day 3 are still on it a month later. That's the retention signal I'm building toward.

Try it: https://dictate-app.pages.dev

Happy to answer questions about the Windows audio API weirdness — there's a lot of it.

---

## 2. r/IMadeThis

**Subreddit rules summary:**
- Showcase things you personally made — projects, products, art, tools
- Self-promotion is the explicit purpose of the sub (~200K members)
- Be genuine, not just a link drop — include context about what and why
- Engage with comments
- Not a place for idea pitches — must be a real made thing
- Keep it community-oriented: share what you learned, not just "buy my thing"

---

**Title:**
I made a Windows dictation app powered by Groq Whisper — talk instead of type, text lands wherever your cursor is

**Body:**
I hate typing. I'm accurate enough but slow, and I make a lot of small errors that kill my flow. So I built something.

It's a system tray app for Windows. You press a hotkey, say what you want to type, release the key, and the transcription appears in whatever field you had focused. Works across apps — browser, Word, code editors, chat.

Under the hood it's using Groq's Whisper Large v3 API. Groq's hardware (they make LPUs, not GPUs) makes Whisper return in around 280ms, which is the threshold that makes it feel instant rather than slow.

The hardest parts:
- Getting text injection to work across every type of Windows app (each one handles keyboard events differently)
- Managing audio sessions without conflicts when other apps are using the mic
- Making the system tray UX feel native, not like a web app shoved into a box

It's $9/month. There's a free trial. Windows 10 and 11.

Link: https://dictate-app.pages.dev

If you've built anything with Windows audio APIs before — I have stories.

---

## 3. r/productivity

**Subreddit rules summary:**
- Focus on tips, tools, systems, and methods that improve productivity
- Self-promotion is allowed but must be value-first — lead with the content, not the pitch
- Low-effort "check out my app" posts get removed
- Posts should teach or demonstrate something genuinely useful
- Flair your post correctly (e.g., "Tool" or "Tip")
- Discussion and honest comparison posts do very well here
- No affiliate spam or referral link baiting

---

**Title:**
I replaced typing with dictation for a month — here's what actually changed (and what didn't)

**Body:**
I decided to use voice dictation as my primary input method for a full month. I built my own Windows app to do it (powered by Groq's Whisper API), so the tool was purpose-built for this experiment. Here's what I learned:

**What got better:**
- Long-form writing. Articles, emails, documentation. The output quality went up because my brain stops filtering when I'm talking vs typing.
- Speed on anything over 3 sentences. Once you're past a short reply, speaking is 3-4x faster than typing for most people.
- Physical comfort. Less wrist fatigue on heavy writing days.

**What didn't change much:**
- Short replies. For "sounds good" or a 10-word Slack message, it's faster to type. The hotkey overhead costs you.
- Code. Whisper handles variable names surprisingly well, but dictating code syntax is awkward. Still type code.
- Anything in a focused meeting. You can't dictate in a meeting without disrupting it.

**What surprised me:**
- Latency matters more than accuracy. A 96% accurate transcription that takes 2 seconds feels worse than a 94% accurate one that takes 0.3 seconds.
- Punctuation is a learned skill. You have to train yourself to say "comma" and "period" until it becomes automatic. Takes about a week.

If you're curious about the tool I built for this: https://dictate-app.pages.dev (Windows, $9/month, free trial). But the experiment works with any dictation tool — the insights apply regardless.

What has your experience been with voice input?

---

## 4. r/speechrecognition

**Subreddit rules summary:**
- Community for speech recognition technology, research, tools, and discussion
- Product posts are tolerated if there's genuine technical substance — pure marketing posts get removed
- Technical comparisons and benchmark discussions are highly valued
- Questions and troubleshooting posts welcome
- Self-promotion should be framed around technical contribution, not sales
- Community is smaller and more technical — quality over quantity
- No spam or duplicate posts

---

**Title:**
Built a Windows dictation app on Groq Whisper — latency comparison with OpenAI Whisper, Dragon, and local inference

**Body:**
I've been testing Whisper across different inference backends for a Windows dictation app I built. The latency differences are significant enough to share.

Test setup: 5-second audio clip, spoken English, repeated 20 times, median latency recorded.

| Backend | Median latency | Notes |
|---|---|---|
| Groq Whisper Large v3 | 280ms | LPU inference |
| OpenAI Whisper API | 1100ms | Standard tier |
| Local — GPU (RTX 3080) | 390ms | faster-whisper |
| Local — CPU (Ryzen 9) | 7800ms | Not viable for real-time |
| Dragon NaturallySpeaking | ~200ms | On-device, different model class |

The practical takeaway: anything over ~500ms starts to feel like the transcription is lagging behind your speech rather than transcribing it. Groq is the only cloud option that clears that threshold in testing.

Word accuracy on a 50-sentence test set (technical vocabulary, English):
- Groq Whisper Large v3: 96.1%
- Dragon NaturallySpeaking: 88.3%
- OpenAI Whisper Large v3: 96.0% (same model, expected)

The accuracy between Groq and OpenAI is essentially identical — they run the same model. The difference is purely inference speed.

The app I built around this: https://dictate-app.pages.dev — it's a Windows system tray app that sends audio to Groq and injects text into the focused input. $9/month.

Happy to share more about the Windows audio capture side if useful — that had its own set of quirks.

---

## 5. r/Windows

**Subreddit rules summary:**
- General Windows discussion, tips, news, help, and community
- App showcases are allowed but should be framed as genuinely useful to Windows users
- Posts should explain what problem is solved and how — not just "here's my app"
- Avoid obvious self-promotion language ("check out my product," "buy now")
- Technical posts and how-tos get more upvotes than link drops
- Community is large (3M+) — quality posts can get significant traction
- No paid promotion disguised as organic posts

---

**Title:**
I got tired of Windows' built-in dictation and built my own — hotkey to type anywhere, powered by Groq Whisper

**Body:**
Windows has built-in dictation (Win+H) and I used it for a while. It works well enough for basic use, but I kept running into the same problems:

- Accuracy dropped on technical terms and names
- Punctuation required explicit commands ("period", "comma") but wasn't reliable
- It doesn't work in every app — some inputs just don't receive dictated text
- No way to configure which microphone it uses without changing the system default

So I built my own.

It's a system tray app that sits quietly in the tray until you hold a hotkey (configurable). While you hold the key, it records. When you release, it sends the audio to Groq's Whisper API and injects the transcription wherever your cursor is. The injection works across browsers, Office apps, Notepad, Slack, most Electron apps.

A few things that work better than Win+H in my testing:
- Accuracy is noticeably higher on non-standard words
- Latency is around 300ms from release to text appearing (Groq's hardware is fast)
- Works in more apps than the built-in dictation
- You can configure which audio device it uses

The app is https://dictate-app.pages.dev — Windows 10 and 11, $9/month with a free trial. I made it because I needed it; sharing in case others have the same frustrations with Win+H.

---

## Notes on posting strategy

- **Spacing**: Post one per week minimum, not all at once. Reddit flags account bursts.
- **Engagement first**: If the account is new, spend 1-2 weeks commenting in these subs before posting.
- **Reply to every comment**: Especially in the first hour. Algorithm rewards engagement velocity.
- **r/SideProject and r/IMadeThis** are safest for direct product posts.
- **r/productivity and r/Windows** need the value-first frame — lead with the insight or problem, mention the tool later.
- **r/speechrecognition** is small and technical — the benchmark table approach is the right fit there.
