#!/usr/bin/env python3
"""
dictate.app Reddit auto-poster
Posts one entry from the content bank to a subreddit.
Runs via GitHub Actions cron — picks the next unposted entry.
"""
import os, json, random, urllib.request, urllib.parse, datetime

CLIENT_ID     = os.environ["REDDIT_CLIENT_ID"]
CLIENT_SECRET = os.environ["REDDIT_CLIENT_SECRET"]
USERNAME      = os.environ["REDDIT_USERNAME"]
PASSWORD      = os.environ["REDDIT_PASSWORD"]

# ── Content bank ─────────────────────────────────────────────────────────────
POSTS = [
    {
        "subreddit": "SideProject",
        "title": "I built a Windows dictation app because Wispr Flow is Mac-only and Dragon costs $500",
        "text": (
            "Tired of the options on Windows:\n"
            "- Built-in Win+H: stops mid-sentence, no auto-paste\n"
            "- Dragon: $500+, feels like 2008\n"
            "- Wispr Flow / Superwhisper: Mac only\n"
            "- Local Whisper on CPU: 1-2 second lag = breaks flow\n\n"
            "Built dictate.app. Press Ctrl+Space, speak, text injects at your cursor. "
            "Powered by Groq Whisper so transcription is ~200ms. 7-day free trial, no credit card.\n\n"
            "Would love brutal feedback — Windows users are genuinely underserved here.\n\n"
            "https://dictate-app.pages.dev"
        ),
    },
    {
        "subreddit": "productivity",
        "title": "Went from 60 wpm typing to 150+ wpm dictating — here's what actually helped",
        "text": (
            "Started using push-to-talk dictation for emails, Slack, docs. "
            "The habit shift was harder than the tool.\n\n"
            "Tips that actually worked:\n"
            "1. Start with low-stakes stuff (emails, notes) not code\n"
            "2. Don't correct mistakes mid-sentence — let it finish, then fix\n"
            "3. Remap hotkey to something muscle-memory (I use a side mouse button)\n\n"
            "Tool I use: dictate.app (Windows, free trial) — Ctrl+Space, speak, text pastes wherever your cursor is.\n\n"
            "Anyone else doing this? What do you use?\n\n"
            "[I built it — disclosing upfront]"
        ),
    },
    {
        "subreddit": "windows",
        "title": "PSA: Windows built-in voice typing (Win+H) is way worse than it needs to be",
        "text": (
            "Win+H randomly stops mid-sentence, doesn't auto-paste at cursor, "
            "no custom hotkey, and the accuracy isn't great.\n\n"
            "I switched to dictate.app — custom hotkey (Ctrl+Space), auto-paste at cursor, "
            "near-instant transcription via Groq Whisper. Free 7-day trial.\n\n"
            "https://dictate-app.pages.dev\n\n"
            "[I'm the developer]"
        ),
    },
    {
        "subreddit": "speechrecognition",
        "title": "Speed comparison: Win+H vs local Whisper vs Groq Whisper for Windows dictation",
        "text": (
            "Tested all three on the same hardware:\n\n"
            "- Win+H: 2-3s lag, decent accuracy, no auto-paste\n"
            "- Local Whisper (CPU): 1-2s, good accuracy, setup painful\n"
            "- Groq Whisper (dictate.app): ~200ms, best accuracy, auto-paste at cursor\n\n"
            "The lag difference is the one that kills flow state the most. "
            "Once you drop below 300ms it feels instantaneous.\n\n"
            "https://dictate-app.pages.dev for the Groq-powered one — free trial, Windows only.\n\n"
            "[I built the last one]"
        ),
    },
    {
        "subreddit": "workhacks",
        "title": "Stop typing. Start dictating. 2.5x output for free.",
        "text": (
            "Average typing speed: 60 wpm.\n"
            "Average speaking speed: 150 wpm.\n\n"
            "That's 2.5x more output using your voice. "
            "I've been dictating emails, Slack messages, docs, and even code comments for months.\n\n"
            "Setup: install dictate.app (Windows), press Ctrl+Space, speak, text appears at cursor. "
            "Uses Groq Whisper so it's ~200ms — fast enough to not break your flow.\n\n"
            "Free 7-day trial: https://dictate-app.pages.dev"
        ),
    },
    {
        "subreddit": "software",
        "title": "dictate.app — push-to-talk Windows dictation powered by Groq Whisper",
        "text": (
            "Just launched a Windows dictation app. Main differentiators:\n\n"
            "- ~200ms transcription (Groq Whisper, not local CPU)\n"
            "- Auto-pastes at cursor position, not just clipboard\n"
            "- Custom hotkey (default Ctrl+Space)\n"
            "- Bring your own Groq API key (free tier works)\n"
            "- No HMW servers — audio goes to Groq only, they don't store it\n\n"
            "7-day free trial: https://dictate-app.pages.dev\n\n"
            "Windows only for now. Happy to answer questions."
        ),
    },
]

def get_token():
    data = urllib.parse.urlencode({"grant_type": "password", "username": USERNAME, "password": PASSWORD}).encode()
    req = urllib.request.Request(
        "https://www.reddit.com/api/v1/access_token",
        data=data,
        headers={
            "User-Agent": "dictate-app-poster/1.0 by " + USERNAME,
            "Authorization": "Basic " + __import__("base64").b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode(),
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["access_token"]

def submit_post(token, subreddit, title, text):
    data = urllib.parse.urlencode({
        "sr": subreddit,
        "kind": "self",
        "title": title,
        "text": text,
        "nsfw": False,
        "spoiler": False,
        "resubmit": True,
    }).encode()
    req = urllib.request.Request(
        "https://oauth.reddit.com/api/submit",
        data=data,
        headers={
            "User-Agent": "dictate-app-poster/1.0 by " + USERNAME,
            "Authorization": "Bearer " + token,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        result = json.loads(r.read())
    return result

if __name__ == "__main__":
    # Pick post based on week number so it cycles through all posts
    week = datetime.datetime.utcnow().isocalendar()[1]
    post = POSTS[week % len(POSTS)]

    print(f"Posting to r/{post['subreddit']}: {post['title']}")
    token = get_token()
    result = submit_post(token, post["subreddit"], post["title"], post["text"])
    print(json.dumps(result, indent=2))
