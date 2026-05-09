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

# ── Session: local cookie file (WSL2) or env var (GitHub Actions) ────────────
COOKIES_B64 = os.environ.get("REDDIT_COOKIES_MR1V4", "")
COOKIES_FILE = Path(os.path.expanduser("~/.reddit_profiles/Mr1v4/cookies.json"))

if COOKIES_B64:
    COOKIES = json.loads(base64.b64decode(COOKIES_B64))
elif COOKIES_FILE.exists():
    COOKIES = json.loads(COOKIES_FILE.read_text())
else:
    print("ERROR: No Reddit session available.")
    print("  Run: python3 scripts/reddit_login_setup.py")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────
LOG_FILE = Path(__file__).parent / "reddit_post_log.json"
SITE_URL = "https://dictate-app.pages.dev"
COOLDOWN_DAYS = 3

SUBREDDITS = [
    "productivity",
    "windows",
    "indiedev",
    "windowsapps",
    "sideproject",
]

POSTS = [
    {
        "title": "compared every Windows dictation tool I could find, here's where I landed",
        "body": f"""spent way too long on this but figured I'd share

Win+H - built in, free, but you have to paste manually and it takes 2-3 seconds. annoying.

Dragon - actually works great but $500+ is insane for most people

local Whisper - surprisingly good if you have a decent GPU. CPU is too slow for daily use imo. still have to paste manually though.

Wispr Flow - probably the best UX I've tried but it's Mac only which is a dealbreaker

what I'm using now: [dictate.app]({SITE_URL}) - it's basically Whisper via Groq (so like 200ms latency) and it types directly at your cursor instead of clipboard. makes a bigger difference than you'd think.

has a free trial if anyone wants to test it before paying. lmk if you have questions"""
    },
    {
        "title": "voice dictation finally clicked for me after I stopped trying to correct myself mid-sentence",
        "body": f"""been meaning to post this for a while

I tried dictation like 3 times over the years and gave up every time. kept stopping to say "no scratch that" or trying to edit while talking. made me slower than just typing.

what actually worked: just let the whole sentence out, then go back. sounds obvious but it took me a while to actually do it consistently.

also moved it to a side mouse button instead of a keyboard shortcut. way less disruptive.

using [dictate.app]({SITE_URL}) on Windows right now, it's Groq Whisper under the hood so the latency is fast enough that it doesn't break flow. tried a few others first but the cursor injection vs clipboard thing matters a lot in practice.

anyway. if you've tried dictation before and quit, might be worth another shot with the right setup"""
    },
    {
        "title": "voice dictation on Windows - what's actually working in 2026",
        "body": f"""been doing this for about 6 months so figured I'd do a writeup

the accuracy problem is basically solved at this point. Whisper gets 95%+ most of the time. that's not why people quit.

what trips people up is the mental shift. typing is editing as you go. dictation works better if you just say the whole thing and clean it up after. took me a couple weeks to stop fighting that.

setup I'm on: [dictate.app]({SITE_URL}) - it's an Electron app, uses Groq Whisper API, round trip is around 200ms. the main thing that makes it work for me vs other tools is that it types at the cursor directly - other stuff pastes from clipboard which means you have to ctrl+v every time.

the BYOK model (bring your own Groq key) is a nice touch too, audio goes from your machine to Groq, no middleman

anyone else on Windows doing this? curious what people are running"""
    },
    {
        "title": "push to talk is way better than always-on for actual daily use",
        "body": f"""tried both, push to talk wins for me

always-on sounds appealing in theory but background noise is a constant issue. also you end up doing this weird thing where you're thinking mid-sentence and it's transcribing your ums and pauses.

push to talk: you hold the button when you're ready to talk, let go when done. takes a day to get used to and then you stop thinking about it.

I have it mapped to a mouse side button now. works in any app, no context switching.

using [dictate.app]({SITE_URL}) for this on Windows, it's remappable so you can put it wherever. Groq Whisper backend so it's fast.

curious if others have tried both - I could see always-on working better for certain use cases but I haven't figured out when"""
    },
    {
        "title": "ran actual latency tests on different Whisper options, Groq is faster than I expected",
        "body": f"""did this because I couldn't find any recent benchmarks, so ran my own

CPU Whisper (i7-12700): 800ms to 1.4s depending on length
GPU Whisper (RTX 3070): 200-400ms, usable but not instant
OpenAI API: 400-900ms, varies a lot with network
Groq API: 150-250ms consistently

Groq was the surprise. didn't expect the cloud option to beat local GPU but here we are

I'm using this via [dictate.app]({SITE_URL}) - it handles the mic capture, hotkey, and pastes at cursor. you bring your own Groq key which is free for light use and means your audio goes direct to Groq, not through some middleman server

if anyone has GPU Whisper numbers from a 4090 or something I'd be curious how much faster it gets"""
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

    with Camoufox(headless=True) as browser:
        ctx = browser.new_context()
        ctx.add_cookies(COOKIES)
        page = ctx.new_page()

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
        title_input = page.locator('textarea[name="title"]').first
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

        body_area = page.locator('div[name="body"][role="textbox"]').first
        body_area.click()
        human_delay(0.3, 0.8)
        body_area.type(post["body"], delay=random.randint(20, 60))
        human_delay(1, 3)

        # Submit (button text varies: "Post" or "Request to Post" on restricted subs)
        page.locator('button:has-text("Post"), button:has-text("Request to Post")').last.click()
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
    if "--dry-run" in sys.argv:
        log = load_log()
        sub = pick_subreddit(log)
        post = random.choice(POSTS)
        print(f"DRY RUN — would post to r/{sub}:")
        print(f"  Title: {post['title']}")
        print(f"  Cookies loaded: {len(COOKIES)}")
        sys.exit(0)
    success = run()
    sys.exit(0 if success else 1)
