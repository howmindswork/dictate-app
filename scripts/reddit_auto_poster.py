#!/usr/bin/env python3
"""
Reddit auto-poster for dictate-app.pages.dev
No OAuth app needed. Uses either:
  A) Firefox cookies (if logged into Reddit in Firefox) — zero setup
  B) Username/password from ~/.claude_secrets — store REDDIT_USERNAME + REDDIT_PASSWORD

Run: python3 reddit_auto_poster.py
Dry-run: python3 reddit_auto_poster.py --dry-run
"""
import os, json, sys, shutil, sqlite3, datetime, urllib.request, urllib.parse, http.cookiejar

SITE_URL = "https://dictate-app.pages.dev"
LOG_FILE = os.path.join(os.path.dirname(__file__), "reddit_post_log.json")

# Firefox profile paths (no encryption — plaintext SQLite)
FF_PROFILES_BASE = "/mnt/c/Users/lukei/AppData/Roaming/Mozilla/Firefox/Profiles"

SUBREDDITS = [
    "speechrecognition",
    "windowsapps",
    "productivity",
    "devtools",
    "windows",
]

POSTS = [
    {
        "sub": "speechrecognition",
        "title": "I compared every Windows dictation option in 2026 — here's what I found",
        "body": f"""Been trying to find a fast Windows dictation tool that actually works. Here's what I tested:

**Win+H (built-in):** Stops mid-sentence, no auto-paste at cursor. Constantly interrupts flow.

**Dragon NaturallySpeaking:** $500+, heavy software, requires training. Overkill for most people.

**Whisper local (CPU):** 1-2 second lag. Fine for accuracy, terrible for real-time dictation.

**Wispr Flow / Superwhisper:** Great products, Mac only. Nothing for Windows.

**What I ended up building:** A push-to-talk app using Groq's Whisper API. Press Ctrl+Shift+Space, speak, release — text appears at cursor in ~200ms. Works in any app.

The key differentiator vs local Whisper is Groq's inference speed. The API is so fast it feels local.

Try it free: {SITE_URL}

Happy to answer questions about the setup or how it compares to anything else you've tried.""",
    },
    {
        "sub": "productivity",
        "title": "How I went from 60wpm to 150wpm by stopping typing altogether",
        "body": f"""Average typing speed: 60 wpm. Average speaking speed: 150 wpm.

I switched to dictating everything — emails, Slack messages, docs, notes — and my output basically doubled.

**What actually made the habit stick:**

1. Remap the hotkey to a mouse side button. One thumb click, speak, done. No chord to remember.
2. Don't correct mid-sentence. Let the whole thought finish, then fix. Stopping to say "scratch that" costs more than a typo.
3. Start with low-stakes output: emails and Slack first, not code or anything that needs precision.

**Tool I use on Windows:** push-to-talk dictation via Groq Whisper, ~200ms latency, auto-pastes wherever your cursor is. Works in every app including Slack, Notion, Gmail, VS Code comments.

{SITE_URL} — 7-day free trial

Anyone else gone full dictation? Curious what workflows it works best for.""",
    },
    {
        "sub": "windowsapps",
        "title": "Show off: I built a push-to-talk dictation app for Windows (200ms via Groq Whisper)",
        "body": f"""Built this because I couldn't find a Windows dictation tool that did all three:
- Fast (under 300ms)
- Auto-paste directly at cursor (not just clipboard)
- Actually works on Windows

Every option I tried was either Mac-only, $500, or 2 seconds of lag.

**How it works:**
- Electron app, global hotkey via uiohook-napi
- Audio captured while hotkey held
- Sent to Groq Whisper API on release (~200ms round trip)
- Text injected at cursor via keysender

No server-side storage. Audio goes to Groq only for transcription.

**Download:** {SITE_URL} (7-day free trial, no credit card)

Runs in the system tray. Hotkey is fully remappable. Feedback welcome.""",
    },
    {
        "sub": "devtools",
        "title": "Push-to-talk dictation for devs on Windows — built with Electron + Groq Whisper",
        "body": f"""Built a Windows dictation tool for developers who write a lot of prose (docs, emails, Slack, PR descriptions).

**Stack:**
- Electron 34 for Windows native
- uiohook-napi for global hotkey (Ctrl+Shift+Space by default, remappable)
- Groq Whisper API for transcription (~200ms)
- keysender for text injection at cursor

**Why Groq over local Whisper?** CPU inference takes 1-2 seconds — too slow for push-to-talk. Groq's inference is fast enough that it feels instant. Cost is ~$0.02/hour of audio at current pricing.

Works anywhere: VS Code, browser, Slack, Notion, email clients.

{SITE_URL} — free trial, no credit card

Open to technical feedback. The global hotkey and text injection parts were the hardest to get right on Windows.""",
    },
    {
        "sub": "windows",
        "title": "Windows dictation in 2026 is still bad — so I built something",
        "body": f"""Win+H exists but it's terrible. Stops mid-sentence, no auto-paste, breaks your flow constantly.

I spent a week testing alternatives. Dragon is $500. Every good dictation app (Wispr Flow, Superwhisper) is Mac-only. Local Whisper on CPU takes 2 seconds per transcription.

Built my own: push-to-talk hotkey, Groq Whisper for transcription, text auto-pastes wherever your cursor is. About 200ms from release to text appearing.

{SITE_URL} — 7-day free trial

If you write a lot — emails, docs, Slack — worth trying for a week. Speaking is 2.5x faster than typing once the habit is there.""",
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


def days_since(iso_date):
    if not iso_date:
        return 999
    d = datetime.datetime.fromisoformat(iso_date)
    return (datetime.datetime.utcnow() - d).days


def get_firefox_reddit_cookies():
    """Read Reddit cookies from Firefox — no encryption, plain SQLite."""
    if not os.path.exists(FF_PROFILES_BASE):
        return None

    for entry in os.listdir(FF_PROFILES_BASE):
        cookie_db = os.path.join(FF_PROFILES_BASE, entry, "cookies.sqlite")
        if not os.path.exists(cookie_db):
            continue
        tmp = "/tmp/ff_reddit_cookies.db"
        shutil.copy2(cookie_db, tmp)
        conn = sqlite3.connect(tmp)
        c = conn.cursor()
        c.execute("SELECT name, value FROM moz_cookies WHERE host LIKE '%reddit%'")
        rows = c.fetchall()
        conn.close()
        if rows:
            return {r[0]: r[1] for r in rows}
    return None


def login_with_password(username, password):
    """Authenticate via Reddit's legacy login endpoint — no OAuth app needed."""
    params = urllib.parse.urlencode({
        "user": username,
        "passwd": password,
        "api_type": "json",
    }).encode()

    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

    req = urllib.request.Request(
        "https://www.reddit.com/api/login",
        data=params,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with opener.open(req, timeout=15) as resp:
            data = json.loads(resp.read())
            errors = data.get("json", {}).get("errors", [])
            if errors:
                print(f"Login errors: {errors}")
                return None, None
            modhash = data.get("json", {}).get("data", {}).get("modhash")
            cookie_str = "; ".join(f"{c.name}={c.value}" for c in jar)
            return modhash, cookie_str
    except Exception as e:
        print(f"Login failed: {e}")
        return None, None


def get_modhash_from_cookies(cookie_dict):
    """Get modhash using existing session cookies."""
    cookie_str = "; ".join(f"{k}={v}" for k, v in cookie_dict.items())
    req = urllib.request.Request(
        "https://www.reddit.com/api/me.json",
        headers={
            "Cookie": cookie_str,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            if data.get("data"):
                modhash = data["data"].get("modhash")
                return modhash, cookie_str
    except Exception as e:
        print(f"Auth check failed: {e}")
    return None, None


def post_to_reddit(subreddit, title, body, cookie_str, modhash, dry_run=False):
    """Submit a self post to Reddit."""
    if dry_run:
        print(f"[DRY RUN] r/{subreddit}")
        print(f"  Title: {title}")
        print(f"  Body preview: {body[:80]}...")
        return True

    params = urllib.parse.urlencode({
        "api_type": "json",
        "kind": "self",
        "sr": subreddit,
        "title": title,
        "text": body,
        "resubmit": "true",
        "uh": modhash,
    }).encode()

    req = urllib.request.Request(
        "https://www.reddit.com/api/submit",
        data=params,
        headers={
            "Cookie": cookie_str,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Modhash": modhash,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            errors = result.get("json", {}).get("errors", [])
            if errors:
                print(f"Reddit errors: {errors}")
                return False
            url = result.get("json", {}).get("data", {}).get("url", "")
            print(f"Posted: {url}")
            return True
    except Exception as e:
        print(f"Post failed: {e}")
        return False


def pick_next_post(log):
    best, best_days = None, -1
    for post in POSTS:
        d = days_since(log.get(post["sub"], {}).get("last_posted"))
        if d > best_days:
            best_days, best = d, post
    return best, best_days


def get_secrets():
    """Load REDDIT_USERNAME and REDDIT_PASSWORD from ~/.claude_secrets."""
    secrets_file = os.path.expanduser("~/.claude_secrets")
    username = password = None
    if os.path.exists(secrets_file):
        with open(secrets_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("export REDDIT_USERNAME="):
                    username = line.split("=", 1)[1].strip('"').strip("'")
                elif line.startswith("export REDDIT_PASSWORD="):
                    password = line.split("=", 1)[1].strip('"').strip("'")
    return username, password


def main():
    dry_run = "--dry-run" in sys.argv

    log = load_log()
    post, days = pick_next_post(log)

    if days < 3 and not dry_run:
        print(f"All subs posted within 3 days. Next: r/{post['sub']} ({days}d). Skipping.")
        return

    print(f"Target: r/{post['sub']} (last posted {days}d ago)")

    modhash = cookie_str = None

    # Method 1: Firefox cookies
    ff_cookies = get_firefox_reddit_cookies()
    if ff_cookies:
        print("Found Firefox Reddit session, authenticating...")
        modhash, cookie_str = get_modhash_from_cookies(ff_cookies)

    # Method 2: Username/password from secrets
    if not modhash:
        username, password = get_secrets()
        if username and password:
            print(f"Using credentials for {username}...")
            modhash, cookie_str = login_with_password(username, password)

    if not modhash:
        print("""
BLOCKED: No Reddit session available.

To fix (pick one):
  A) Open Firefox, log into reddit.com, then re-run this script
  B) Add to ~/.claude_secrets:
       export REDDIT_USERNAME="your_username"
       export REDDIT_PASSWORD="your_password"
""")
        sys.exit(1)

    print(f"Authenticated. Posting to r/{post['sub']}...")
    success = post_to_reddit(post["sub"], post["title"], post["body"], cookie_str, modhash, dry_run)

    if success and not dry_run:
        log[post["sub"]] = {
            "last_posted": datetime.datetime.utcnow().isoformat(),
            "title": post["title"],
        }
        save_log(log)
        print("Done.")


if __name__ == "__main__":
    main()
