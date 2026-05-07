#!/usr/bin/env python3
"""
dictate.app auto-poster — Bluesky + dev.to + Mastodon
No API approval needed. Runs free on GitHub Actions.
"""
import os, json, urllib.request, urllib.parse, datetime, random

# ── Content bank ──────────────────────────────────────────────────────────────
POSTS = [
    {
        "text": "Built a Windows dictation app that pastes text at your cursor in ~200ms. Press Ctrl+Space, speak, done. No Dragon, no cloud storage, no $500 license. 7-day free trial. https://dictate-app.pages.dev #productivity #Windows",
        "title": "I built a push-to-talk dictation app for Windows — 200ms transcription, auto-paste at cursor",
        "body": """## The problem

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

7 days free, no credit card. https://dictate-app.pages.dev

Would love feedback from anyone who types a lot for work.
""",
    },
    {
        "text": "Went from 60 wpm typing to 150+ wpm by just talking. The habit shift is harder than the tool. Tips: start with emails not code, don't correct mid-sentence, use a side mouse button. Tool: https://dictate-app.pages.dev #productivity",
        "title": "How I went from 60 wpm to 150 wpm — dictating instead of typing",
        "body": """The math is simple: average typing speed is 60 wpm, average speaking speed is 150 wpm. That's 2.5x more output for free.

I've been dictating emails, Slack messages, docs, and code comments for months. Here's what actually helped:

**1. Start with low-stakes output**
Emails and Slack first. Not code. The accuracy is good but not perfect — you'll want to proofread code.

**2. Don't correct mid-sentence**
Let the whole thought finish, then fix. Stopping to say "scratch that" breaks your flow more than a typo does.

**3. Remap to muscle memory**
I moved from Ctrl+Space to a side mouse button. Now it's zero friction.

**Tool I use:** dictate.app (Windows) — Ctrl+Space, speak, text appears at cursor. ~200ms via Groq Whisper.

Free trial: https://dictate-app.pages.dev

Anyone else doing this? What workflow changes helped you?
""",
    },
    {
        "text": "Windows dictation in 2026: Win+H is still bad. Local Whisper is slow. The sweet spot is Groq Whisper — 200ms, auto-paste, custom hotkey. Built it, shipping it. https://dictate-app.pages.dev #buildinpublic #indiedev",
        "title": "Windows dictation in 2026 is still broken — so I fixed it",
        "body": """Voice dictation on Windows in 2026 is still a mess:

| Tool | Speed | Auto-paste | Price |
|------|-------|-----------|-------|
| Win+H | 2-3s | No | Free |
| Dragon | OK | Yes | $500+ |
| Local Whisper | 1-2s | No | Free (but slow) |
| Wispr Flow | Fast | Yes | Mac only |

The gap I found: **fast + Windows + auto-paste at cursor**. That's the feature combination that doesn't exist anywhere.

So I built dictate.app:
- Groq Whisper = ~200ms transcription
- Auto-paste directly at cursor (not just clipboard)
- Custom hotkey (default Ctrl+Space)
- Bring your own Groq API key (free tier works)

Building in public. First week of shipping. Would love brutal feedback.

https://dictate-app.pages.dev — 7-day free trial
""",
    },
]

# ── Bluesky ───────────────────────────────────────────────────────────────────
def post_bluesky(handle, password, text):
    # Get session
    data = json.dumps({"identifier": handle, "password": password}).encode()
    req = urllib.request.Request(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req) as r:
        session = json.loads(r.read())

    # Post
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    record = {"$type": "app.bsky.feed.post", "text": text[:300], "createdAt": now}
    data = json.dumps({"repo": session["did"], "collection": "app.bsky.feed.post", "record": record}).encode()
    req = urllib.request.Request(
        "https://bsky.social/xrpc/com.atproto.repo.createRecord",
        data=data,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + session["accessJwt"]},
        method="POST"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

# ── dev.to ────────────────────────────────────────────────────────────────────
def post_devto(api_key, title, body):
    data = json.dumps({"article": {"title": title, "body_markdown": body, "published": True, "tags": ["productivity", "windows", "buildinpublic"]}}).encode()
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
    week = datetime.datetime.utcnow().isocalendar()[1]
    post = POSTS[week % len(POSTS)]

    results = {}

    bsky_handle   = os.getenv("BLUESKY_HANDLE")
    bsky_password = os.getenv("BLUESKY_PASSWORD")
    if bsky_handle and bsky_password:
        try:
            results["bluesky"] = post_bluesky(bsky_handle, bsky_password, post["text"])
            print("✓ Bluesky posted")
        except Exception as e:
            print(f"✗ Bluesky: {e}")

    devto_key = os.getenv("DEVTO_API_KEY")
    if devto_key:
        try:
            results["devto"] = post_devto(devto_key, post["title"], post["body"])
            print("✓ dev.to posted")
        except Exception as e:
            print(f"✗ dev.to: {e}")

    masto_token    = os.getenv("MASTODON_TOKEN")
    masto_instance = os.getenv("MASTODON_INSTANCE", "mastodon.social")
    if masto_token:
        try:
            results["mastodon"] = post_mastodon(masto_instance, masto_token, post["text"])
            print("✓ Mastodon posted")
        except Exception as e:
            print(f"✗ Mastodon: {e}")

    print(json.dumps(results, indent=2))
