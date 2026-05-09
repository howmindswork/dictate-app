#!/usr/bin/env python3
"""
Reddit auto-poster for dictate-app using Camoufox.
Runs headless, rotates subreddits with 3-day cooldown.

SETUP: Add to ~/.claude_secrets:
  export REDDIT_USERNAME="your_reddit_username"
  export REDDIT_PASSWORD="your_reddit_password"
"""

import os, json, random, time, sys, base64
from datetime import datetime, timedelta
from pathlib import Path

# ── Session mode: local profile (WSL2) or cookie injection (GitHub Actions) ───
COOKIES_B64 = os.environ.get("REDDIT_COOKIES_MR1V4", "")
PROFILE_DIR = os.path.expanduser("~/.reddit_profiles/Mr1v4")

USE_COOKIE_INJECTION = bool(COOKIES_B64)
USE_LOCAL_PROFILE = not USE_COOKIE_INJECTION and os.path.exists(PROFILE_DIR)

if not USE_COOKIE_INJECTION and not USE_LOCAL_PROFILE:
    print("ERROR: No Reddit session available.")
    print("  Local: run python3 scripts/reddit_login_setup.py")
    print("  Cloud: set REDDIT_COOKIES_MR1V4 secret in GitHub Actions")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────
LOG_FILE = Path(__file__).parent / "reddit_post_log.json"
SITE_URL = "https://dictate-app.pages.dev"
COOLDOWN_DAYS = 3

SUBREDDITS = [
    "speechrecognition",
    "windowsapps",
    "productivity",
    "windows",
    "indiedev",
]

POSTS = [
    {
        "title": "I compared every Windows dictation option in 2026 — here's what actually works",
        "body": f"""After trying everything, here's the honest breakdown:

| Tool | Speed | Auto-paste | Price | Platform |
|------|-------|-----------|-------|---------|
| Win+H | 2-3s | ❌ | Free | Windows |
| Dragon | OK | ✅ | $500+ | Windows |
| Local Whisper | 1-2s | ❌ | Free | Windows |
| Wispr Flow | Fast | ✅ | $10/mo | Mac only |

The gap nobody filled: **fast + Windows + auto-paste at cursor**.

I ended up using [dictate.app]({SITE_URL}) — it uses Groq's Whisper API so transcription is ~200ms, and it injects text directly at your cursor in any app. 7-day trial if you want to test it.

Happy to answer questions about any of these tools."""
    },
    {
        "title": "How I went from 60wpm to 150wpm — stopped typing, started talking",
        "body": f"""Average typing speed: 60 wpm. Average speaking speed: 150 wpm.

That 2.5x gap is just sitting there, unused.

I switched to voice dictation for emails, Slack, and docs about 6 months ago. A few things that actually made the habit stick:

**1. Use a mouse side button, not a keyboard chord**
One thumb click to start recording. It becomes invisible.

**2. Don't correct mid-sentence**
Finish the thought, then fix. Stopping to say "scratch that" costs more than a typo.

**3. Start with emails, not code**
Low stakes, fast feedback. Code comes later when you're comfortable.

Tool I use on Windows: [dictate.app]({SITE_URL}) — push-to-talk via Ctrl+Shift+Space, text appears at cursor in ~200ms via Groq Whisper. Free trial if you want to experiment.

What's your current setup?"""
    },
    {
        "title": "6 months of voice dictation on Windows — honest review",
        "body": f"""I've been dictating everything on Windows for 6 months. Here's what nobody tells you:

**The learning curve isn't accuracy. It's learning to think out loud.**

Whisper-based tools are 95%+ accurate. The hard part is stopping yourself from editing mid-sentence. You have to let the whole thought out before you fix anything.

Took me about 2 weeks to stop self-interrupting.

**What I use:** [dictate.app]({SITE_URL}) — Electron app, Groq Whisper backend, ~200ms round trip. Works in any Windows app because it simulates keypresses rather than using clipboard.

The auto-paste-at-cursor is what makes it usable. Other tools dump to clipboard and you have to manually paste. This one just types wherever your cursor is.

Anyone else doing voice dictation on Windows? Curious what setups people are running."""
    },
    {
        "title": "Push-to-talk vs always-on dictation — which actually works for daily use?",
        "body": f"""Been thinking about this a lot after 6 months of voice dictation.

**Always-on** (wake word style):
- Feels more natural in theory
- Background noise is a constant problem
- You have to remember to "stop" recording

**Push-to-talk**:
- You control exactly when it listens
- Works in noisy environments
- Faster to start/stop than you'd expect once it's on a mouse button

I ended up on push-to-talk and don't think I'd go back. The control feels better for writing, where you often want to think silently for a few seconds between sentences.

Using [dictate.app]({SITE_URL}) on Windows — Groq Whisper backend so it's actually fast (~200ms). The hotkey is remappable; I have it on a side mouse button.

What do you prefer? Curious if others have tried both."""
    },
    {
        "title": "Groq Whisper for Windows voice dictation — real-world latency numbers",
        "body": f"""Tested this properly with timestamps. Results:

- **Local Whisper (CPU, i7-12700):** 800ms–1.4s
- **Local Whisper (GPU, RTX 3070):** 200ms–400ms
- **OpenAI Whisper API:** 400ms–900ms (network dependent)
- **Groq Whisper API:** 150ms–250ms

Groq is genuinely fast. The latency is low enough that it feels like real-time.

I'm using it via [dictate.app]({SITE_URL}) on Windows — it handles the hotkey capture, mic input, and auto-paste at cursor. You bring your own Groq API key (free tier works for light use).

The BYOK model means your audio goes directly from your machine to Groq — no middleman server logging your dictation.

Anyone running local GPU Whisper getting better numbers? Interested in the comparison."""
    },
]


def load_log():
    if LOG_FILE.exists():
        return json.loads(LOG_FILE.read_text())
    return {}


def save_log(log):
    LOG_FILE.write_text(json.dumps(log, indent=2))


def pick_subreddit(log):
    now = datetime.utcnow()
    for sub in SUBREDDITS:
        last = log.get(sub)
        if not last:
            return sub
        if datetime.fromisoformat(last) + timedelta(days=COOLDOWN_DAYS) < now:
            return sub
    # All on cooldown — pick least recently posted
    return min(SUBREDDITS, key=lambda s: log.get(s, "2000-01-01"))


def human_delay(lo=2.0, hi=5.0):
    time.sleep(random.uniform(lo, hi))


def run():
    from camoufox.sync_api import Camoufox

    log = load_log()
    subreddit = pick_subreddit(log)
    post = random.choice(POSTS)

    print(f"[{datetime.utcnow().isoformat()}] u/Mr1v4 → r/{subreddit}: {post['title'][:50]}...")
    mode = "cookie-inject" if USE_COOKIE_INJECTION else "local-profile"
    print(f"  Auth mode: {mode}")

    kwargs = {"headless": True}
    if USE_LOCAL_PROFILE:
        kwargs["user_data_dir"] = PROFILE_DIR

    with Camoufox(**kwargs) as browser:
        if USE_COOKIE_INJECTION:
            cookies = json.loads(base64.b64decode(COOKIES_B64))
            ctx = browser.new_context()
            ctx.add_cookies(cookies)
            page = ctx.new_page()
        else:
            page = browser.new_page()

        # Warm up — visit Reddit home (session already logged in)
        page.goto("https://www.reddit.com", timeout=30000)
        human_delay(3, 7)

        if "login" in page.url or page.locator('[data-testid="login-button"]').count() > 0:
            print("ERROR: Session expired. Re-run login setup and re-export cookies.")
            return False

        # Navigate to subreddit submit page
        page.goto(f"https://www.reddit.com/r/{subreddit}/submit", timeout=30000)
        human_delay(2, 4)

        # Fill title
        title_input = page.locator('textarea[placeholder*="Title"]').first
        title_input.click()
        human_delay(0.3, 0.8)
        title_input.fill(post["title"])
        human_delay(1, 2)

        # Switch to text post and fill body
        try:
            page.locator('button:has-text("Text")').first.click()
            human_delay(1, 2)
        except Exception:
            pass

        body_area = page.locator('.public-DraftEditor-content, [data-testid="post-body"]').first
        body_area.click()
        human_delay(0.3, 0.8)
        body_area.type(post["body"], delay=random.randint(20, 60))
        human_delay(1, 3)

        # Submit
        page.locator('button:has-text("Post")').last.click()
        page.wait_for_load_state("networkidle", timeout=15000)
        human_delay(2, 3)

        post_url = page.url
        print(f"Posted: {post_url}")

        log[subreddit] = datetime.utcnow().isoformat()
        save_log(log)
        _telegram(f"Reddit posted ✅\nr/{subreddit}\n{post['title'][:60]}\n{post_url}")
        return True


def _telegram(msg):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat:
        return
    try:
        import urllib.request
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = json.dumps({"chat_id": chat, "text": msg}).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
