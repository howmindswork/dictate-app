# dev.to Articles for dictate.app

Publish with: `python3 scripts/publish-devto.py`

---
ARTICLE_SEPARATOR
---

```
---
title: I replaced typing with voice dictation for 30 days. Here's what happened.
published: false
description: I typed everything for 20 years. Then I tried talking instead. Here's an honest look at 30 days of voice dictation as a developer.
tags: productivity, windows, tools, career
cover_image: null
---
```

I type fast. Around 130 words per minute on a good day. I assumed voice dictation was for people who couldn't type.

Then I got tendinitis in my right wrist and had to rethink that assumption.

## The experiment

I committed to using voice dictation for everything non-code for 30 days. Emails, Slack messages, documentation, meeting notes, this post.

The tool I landed on was [dictate.app](https://dictate.app). It runs on Windows, uses Groq's Whisper model under the hood, and works in every app via push-to-talk. Hold a key, speak, release. The text appears wherever your cursor is.

No cloud subscription lock-in. No browser tab required. $8.99 a month.

## Week 1: frustrating

The first week was rough. I kept stopping mid-sentence to think, which tanked my speed. Voice dictation rewards people who can think in complete sentences. I couldn't.

My accuracy was around 92%. That sounds good until you're editing "public static void" into "public static Lloyd" for the fifth time.

I also felt weird talking at my desk. Self-conscious. I work in a home office so nobody heard me, but it still felt strange.

## Week 2: it clicked

Something shifted around day 10. I stopped trying to speak like I type. I started speaking like I talk.

Shorter sentences. More natural phrasing. Trusting the edit pass.

My speed jumped. I was hitting 180 to 200 words per minute on long-form content. That's 40 to 50 percent faster than my typing.

The push-to-talk mode helped a lot. I could pause, think, then speak. No awkward silences captured. No "um" and "uh" in my text.

## Week 3: real productivity gains

By week three I was writing better emails. Faster, yes, but also more human. When you speak, you don't write like a robot.

Documentation improved too. I stopped abbreviating. I stopped leaving out context. Speaking a full explanation is easier than typing a full explanation.

Meeting notes went from 20 minutes of typing to 5 minutes of speaking. That time adds up.

## Week 4: the honest verdict

**What voice dictation is great for:**
- Emails and Slack messages
- Documentation and wikis
- Meeting notes and summaries
- Blog posts and long-form content
- Any creative writing

**What it's bad for:**
- Code (variable names are a disaster)
- Terminal commands
- Anything requiring exact syntax
- Situations where you can't speak out loud

## The numbers

After 30 days, I tracked my output:

- Average words per minute typing: 130
- Average words per minute speaking: 190
- Reduction in wrist strain: noticeable
- Time saved per day on non-code writing: about 45 minutes

The 45-minute daily savings was the biggest surprise. I write more than I thought.

## Would I keep using it?

Yes. I kept using it. I'm still using it.

Not for code. Not for the terminal. But for everything else, speaking is faster and less physically demanding than typing.

If you're curious, [dictate.app](https://dictate.app) has a 7-day free trial. Try it for a week and pay attention to how much non-code writing you actually do. You might be surprised.

---
ARTICLE_SEPARATOR
---

```
---
title: Voice dictation for developers: a practical guide
published: false
description: When does voice dictation actually help developers? When does it fail? A practical breakdown of what to dictate and what to keep typing.
tags: webdev, productivity, windows, beginners
cover_image: null
---
```

Voice dictation sounds like a gimmick until you realize how much of a developer's day isn't code.

Emails. Slack. Documentation. Code reviews. Meeting notes. Pull request descriptions. A lot of what you type every day is prose, not syntax.

That's where voice dictation earns its keep.

## What works well

**Prose writing** is where dictation shines. Emails, Slack messages, documentation, blog posts, README files. If you're writing in a natural language, speaking is almost always faster than typing.

**Code reviews** are a good fit. You're describing problems, suggesting approaches, explaining trade-offs. That's all natural language. Dictate your review comments instead of typing them.

**PR descriptions** take forever to type and most developers write terrible ones because of it. Speaking a detailed PR description takes two minutes. Typing one feels like work. The result is better descriptions and better code review.

**Meeting notes** are obvious. You can't type and listen at the same time. You can speak a summary into a push-to-talk app right after the meeting ends.

## What doesn't work

**Code itself** is where voice dictation fails. Variable names, function signatures, brackets, semicolons. These don't translate from speech to text reliably.

There are voice coding tools like Talon and Cursorless that are designed specifically for this. They're impressive but have a steep learning curve. Worth researching if RSI is a serious concern.

**Terminal commands** have the same problem. `git rebase -i HEAD~3` doesn't dictate cleanly.

**Anything requiring precision** is safer to type. Configuration files, SQL queries, regex patterns.

## The push-to-talk workflow

The best dictation apps use push-to-talk mode. Hold a key, speak, release. Text appears at your cursor.

This is important because it solves the pacing problem. You can pause and think without capturing silence or filler words. You can stop speaking, move your cursor, and start again.

[dictate.app](https://dictate.app) does this well on Windows. It works in any app because it types the text using simulated keystrokes. No browser tab required. No switching windows.

## Tips for dictating technical content

**Spell out the unusual stuff.** For a variable name like `getUserById`, say "get user by ID" and then manually type the camelCase version. Dictate the surrounding prose, type the precise bits.

**Use short sentences.** Voice dictation accuracy improves when you speak in clear, complete sentences. Long run-on sentences with lots of clauses create more errors.

**Trust the edit pass.** Don't stop and correct every mistake as you go. Speak the whole thing, then do one editing pass at the end. You'll move faster.

**Speak punctuation when needed.** Most modern dictation tools handle punctuation automatically based on context. When they don't, you can say "comma", "period", "new paragraph" explicitly.

## Getting started

Pick a week where you have a lot of email and documentation work. Try dictating everything non-code for five days. Pay attention to where it saves time and where it slows you down.

The first two days will feel awkward. That's normal. By day five you'll have a clear picture of whether it fits your workflow.

[dictate.app](https://dictate.app) has a 7-day free trial if you want to experiment on Windows without committing.

---
ARTICLE_SEPARATOR
---

```
---
title: The hidden cost of typing all day (and what I switched to)
published: false
description: Repetitive strain injuries are common in developers. Most of us don't think about prevention until something hurts. Here's what the research says and what I changed.
tags: healthydev, productivity, windows, career
cover_image: null
---
```

I started getting pain in my right wrist at 28. Not sharp pain. A dull ache that showed up after long days and took a while to go away.

I ignored it for six months because I was busy.

That was a mistake.

## The numbers on typing injuries

Repetitive strain injuries affect roughly 1 in 3 computer workers at some point in their career. Among developers, the rate is higher because typing is literally the job.

Carpal tunnel syndrome, tendinitis, cubital tunnel syndrome. These conditions develop slowly. They don't announce themselves. By the time you notice consistent pain, there's already damage.

Recovery is slow. Weeks to months. Some people never fully recover without surgery.

The cost isn't just physical. Time away from work, reduced output, career disruption. One serious RSI can set a developer back a year.

## What makes typing risky

The risk isn't a single session. It's cumulative load over months and years.

Typing on a standard flat keyboard keeps your wrists in a slightly awkward position for hours at a time. You're making the same small movements thousands of times per day. The tendons and nerves in your wrists and forearms weren't designed for that volume.

The things that increase risk: typing fast, typing for long unbroken stretches, poor ergonomics, and no recovery time.

Most developers hit all four.

## What actually helps

Ergonomic keyboards help. Split keyboards, mechanical switches, proper wrist positioning. These reduce the strain per keystroke. They don't eliminate the volume problem.

Regular breaks help. The 20-20-20 rule (every 20 minutes, look 20 feet away for 20 seconds) is for eyes, but the same principle applies to wrists. Frequent short breaks beat rare long ones.

Strength and flexibility exercises help. Many physical therapists have specific protocols for keyboard workers.

Reducing keystroke volume helps most. Less typing means less cumulative strain.

## Where voice dictation fits

Voice dictation doesn't replace typing. It reduces it.

I started using [dictate.app](https://dictate.app) after my wrist pain became hard to ignore. It's a Windows app with push-to-talk voice dictation. Hold a key, speak, the text appears. Works in any app.

I kept typing code. That still requires precision that dictation can't match reliably.

Everything else went to voice. Emails. Slack. Documentation. Long explanations. That shift reduced my daily typing volume significantly. On a heavy writing day, I might type 8,000 to 10,000 words. Now a good chunk of that is spoken instead.

The wrist situation improved. Not immediately. But over a few weeks, the daily ache got less frequent.

## The honest reality

Voice dictation has a learning curve. The first week feels slow and awkward. You have to learn to think in spoken sentences, not typed ones.

It also won't save you if you're already injured. If you're in pain now, see a doctor. Dictation is prevention and maintenance, not treatment.

But if you're a developer who types a lot and hasn't thought seriously about RSI yet, it's worth thinking about now. Prevention is dramatically easier than recovery.

The best time to reduce your typing volume was five years ago. The second best time is this week.

[dictate.app](https://dictate.app) has a 7-day free trial. Experiment with it for a week on your prose writing and see if it changes how your hands feel by Friday.
