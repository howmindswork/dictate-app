#!/usr/bin/env python3
"""
Reddit auto-poster for dictate-app.pages.dev
Posts to one subreddit per run, rotates formats, enforces 3-day cooldown per sub.

Required env vars:
  REDDIT_CLIENT_ID, REDDIT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD
"""
import os, json, sys, datetime

try:
    import praw
except ImportError:
    print("Installing praw...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "praw", "-q"])
    import praw

SITE_URL = "https://dictate-app.pages.dev"
LOG_FILE = os.path.join(os.path.dirname(__file__), "reddit_post_log.json")

SUBREDDITS = [
    "speechrecognition",
    "windowsapps",
    "productivity",
    "devtools",
    "windows",
]

POSTS = [
    {
        "title": "I compared every Windows dictation option in 2026 — here's what I found",
        "body": f"""After trying everything available, here's the honest breakdown:

**Win+H (built-in):** Free but stops mid-sentence and doesn't auto-paste. You have to manually copy the text. Kills the flow.

**Dragon NaturallySpeaking:** Still the gold standard for accuracy but $300-500+ upfront. Overkill for most people.

**Local Whisper (CPU):** 1-2 second lag. Usable but that pause breaks concentration.

**Wispr Flow / Superwhisper:** Fast and polished, but Mac only. Nothing equivalent existed for Windows.

**What I ended up building:** Push-to-talk via Groq Whisper. Hold hotkey, speak, text auto-pastes at your cursor in ~200ms. Works in any app. No clipboard step.

Been using it daily for a few months. The auto-paste-at-cursor is the piece everything else was missing.

If you're on Windows and looking for something: {SITE_URL} — 7-day trial, no credit card.

Happy to answer questions about the Whisper API setup or how the hotkey injection works."""
    },
    {
        "title": "How I went from 60wpm to 150wpm — stopped typing",
        "body": f"""Average typing speed: 60 wpm. Average speaking speed: 150 wpm. That gap used to bother me.

I switched to voice dictation for everything that isn't code — emails, Slack, docs, comments, notes. Here's what actually made the habit stick:

**Start with low-stakes output.** I began with emails and Slack, not important docs. Let yourself be okay with minor errors.

**Don't stop mid-sentence to correct.** Finish the thought, then fix. Stopping to say "scratch that" fragments your thinking more than a typo does.

**Remap to a mouse button.** I moved the hotkey to a side mouse button. One thumb press, speak, done. Now it's invisible friction.

**The tool matters.** I tried Win+H (stops mid-sentence) and local Whisper (1-2s lag). Neither felt natural. I ended up building something on Groq Whisper that pastes text directly at the cursor in ~200ms — that latency is what makes it feel like typing.

The app is at {SITE_URL} if you're on Windows and want to try the same setup. 7-day trial.

What's everyone else using for dictation on Windows?""",
    },
    {
        "title": "6 months of voice dictation as a developer — honest review",
        "body": f"""Started using voice dictation about 6 months ago after some wrist pain. Here's what I actually learned:

**What works well:**
- Emails and Slack messages — dictation is clearly faster
- Writing documentation — huge win, brain moves faster than fingers
- Code comments — surprisingly good once you get used to saying punctuation
- Notes and thinking out loud — the best use case honestly

**What doesn't work:**
- Actual code (variable names, syntax) — I still type code
- Short replies where typing is already instant
- Noisy environments obviously

**The tech I settled on:**
Groq Whisper via push-to-talk. I hold a hotkey, speak, text appears at my cursor. The ~200ms latency is what makes it usable — anything slower breaks the flow.

I was frustrated that every Windows option was either slow (local Whisper), expensive (Dragon), or Mac-only (Wispr Flow / Superwhisper). Ended up building my own: {SITE_URL}

Currently at 7-day free trial, $9/mo after. Not pushing it — just sharing what I use.

Curious what others in this community use for long-form writing.""",
    },
    {
        "title": "Push-to-talk vs always-listening dictation — which actually works better?",
        "body": f"""I've tried both approaches. Here's my honest take:

**Always-listening (wake word style):**
- Convenient in theory
- In practice: false triggers, privacy concerns, uncomfortable in shared spaces
- Works okay for single commands, breaks down for long-form writing

**Push-to-talk:**
- You control exactly when it's recording
- Works anywhere — office, coffee shop, doesn't matter
- Feels more like a tool, less like a surveillance device
- The physical gesture (press button, speak, release) creates a natural rhythm

I ended up going with push-to-talk. Built a Windows app that uses Groq Whisper — hold a hotkey, speak, text auto-pastes at cursor in ~200ms. Middle mouse button is my current remap.

The always-listening tools I tried (including some AI assistant integrations) had too many false triggers for actual productive use.

Anyone else have experience comparing the two? Curious if always-listening has gotten better — my testing was mainly 2025 tools.

If anyone wants to try the push-to-talk approach: {SITE_URL} — free trial.""",
    },
    {
        "title": "Groq Whisper vs Dragon NaturallySpeaking for Windows in 2026 — real comparison",
        "body": f"""I used Dragon for about 6 months before switching. Here's the actual comparison:

**Dragon NaturallySpeaking (Professional):**
- Accuracy: excellent after training, especially for technical vocab
- Latency: 0.3-0.8s typically
- Cost: $300-500 upfront
- Setup: heavy install, significant training required
- Works offline: yes

**Groq Whisper (via API):**
- Accuracy: very good, handles accents well, no training needed
- Latency: ~200ms (Groq's hardware is fast)
- Cost: ~$0.02/hr of audio (practically free for normal use)
- Setup: minimal
- Works offline: no (API call)

The main trade-off is offline vs online. If you're in a no-internet environment, Dragon wins. For everything else, Groq Whisper is faster, cheaper, and requires no training.

I wrapped it into a Windows push-to-talk app: {SITE_URL} — hold hotkey, speak, text at cursor. 7-day trial.

For most people who write a lot on Windows, the Groq approach is the better choice in 2026. Dragon's pricing model doesn't make sense anymore at these API costs.

Happy to go deeper on the technical side if anyone's curious.""",
    },
]

def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            return json.load(f)
    return {}

def save_log(log):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)

def days_since(iso_str):
    dt = datetime.datetime.fromisoformat(iso_str)
    return (datetime.datetime.utcnow() - dt).days

def pick_subreddit(log):
    for sub in SUBREDDITS:
        last = log.get(sub, {}).get("last_posted")
        if last is None or days_since(last) >= 3:
            return sub
    # All on cooldown — pick the one posted longest ago
    return min(SUBREDDITS, key=lambda s: log.get(s, {}).get("last_posted", "2000-01-01"))

def pick_post(log, sub):
    used = log.get(sub, {}).get("used_post_indices", [])
    available = [i for i in range(len(POSTS)) if i not in used]
    if not available:
        available = list(range(len(POSTS)))  # reset
    import random
    return random.choice(available)

def main():
    for var in ["REDDIT_CLIENT_ID", "REDDIT_SECRET", "REDDIT_USERNAME", "REDDIT_PASSWORD"]:
        if not os.environ.get(var):
            print(f"Missing env var: {var}")
            sys.exit(1)

    reddit = praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_SECRET"],
        username=os.environ["REDDIT_USERNAME"],
        password=os.environ["REDDIT_PASSWORD"],
        user_agent="dictate-app-poster/1.0",
    )

    log = load_log()
    sub_name = pick_subreddit(log)
    post_idx = pick_post(log, sub_name)
    post = POSTS[post_idx]

    print(f"Posting to r/{sub_name}: {post['title']}")

    subreddit = reddit.subreddit(sub_name)
    submission = subreddit.submit(title=post["title"], selftext=post["body"])

    print(f"Posted: https://reddit.com{submission.permalink}")

    if sub_name not in log:
        log[sub_name] = {}
    log[sub_name]["last_posted"] = datetime.datetime.utcnow().isoformat()
    used = log[sub_name].get("used_post_indices", [])
    used.append(post_idx)
    log[sub_name]["used_post_indices"] = used
    log[sub_name]["last_url"] = f"https://reddit.com{submission.permalink}"
    save_log(log)
    print("Log updated.")

if __name__ == "__main__":
    main()
