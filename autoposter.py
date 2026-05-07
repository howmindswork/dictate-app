#!/usr/bin/env python3
"""
dictate.app auto-poster — Bluesky + dev.to + Mastodon
No API approval needed. Runs free on GitHub Actions.
"""
import os, json, urllib.request, urllib.parse, datetime, re

SITE_URL = "https://dictate-app.pages.dev"

# ── Content bank ──────────────────────────────────────────────────────────────
# Each entry: text (Bluesky/Mastodon), title + body (dev.to), thread (Bluesky thread format)
POSTS = [
    {
        "text": f"Built a Windows dictation app that pastes text at your cursor in ~200ms.\n\nCtrl+Space → speak → text appears. No Dragon. No $500 license. No Mac required.\n\n7-day free trial → {SITE_URL}\n\n#productivity #Windows #buildinpublic",
        "thread": [
            f"Built a Windows dictation app. Ctrl+Space → speak → text appears at your cursor in ~200ms.\n\nFree trial → {SITE_URL}",
            "The gap in the market:\n\n• Win+H — stops mid-sentence, no auto-paste\n• Dragon — $500+\n• Wispr Flow / Superwhisper — Mac only\n• Local Whisper — 1-2s lag\n\nFast + Windows + auto-paste didn't exist. So I built it.",
            "Tech: Electron + Groq Whisper API. Audio goes to Groq only — they don't store it. No HMW servers in the loop.\n\nHotkey is fully remappable. Works in any app, any text field.\n\n#indiedev #buildinpublic",
        ],
        "title": "I built a push-to-talk dictation app for Windows — 200ms transcription, auto-paste at cursor",
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
    {
        "text": f"Went from 60 wpm typing to 150+ wpm by just talking.\n\nThe habit shift is harder than the tool. Tips:\n• Start with emails, not code\n• Don't correct mid-sentence\n• Remap to a mouse button\n\nTool I use → {SITE_URL}\n\n#productivity #Windows",
        "thread": [
            f"Speaking is 2.5x faster than typing. I switched to voice dictation 3 months ago and never looked back.\n\nTool → {SITE_URL}",
            "What actually helped:\n\n1/ Start with low-stakes output — emails and Slack first. Accuracy isn't perfect for code.\n\n2/ Don't correct mid-sentence. Let the thought finish, then fix. Interrupting yourself kills flow.\n\n3/ Remap to muscle memory. I use a side mouse button. Zero friction.",
            "The tool: dictate.app for Windows. Ctrl+Space, speak, text appears at your cursor. ~200ms via Groq Whisper.\n\nAnyone else dictating instead of typing? What clicked for you?\n\n#productivity #buildinpublic",
        ],
        "title": "How I went from 60 wpm to 150 wpm — dictating instead of typing",
        "body": f"""The math is simple: average typing speed is 60 wpm, average speaking speed is 150 wpm. That's 2.5x more output for free.

I've been dictating emails, Slack messages, docs, and code comments for months. Here's what actually helped:

**1. Start with low-stakes output**
Emails and Slack first. Not code. The accuracy is good but not perfect — you'll want to proofread code.

**2. Don't correct mid-sentence**
Let the whole thought finish, then fix. Stopping to say "scratch that" breaks your flow more than a typo does.

**3. Remap to muscle memory**
I moved from Ctrl+Space to a side mouse button. Now it's zero friction.

**Tool I use:** dictate.app (Windows) — Ctrl+Space, speak, text appears at cursor. ~200ms via Groq Whisper.

Free trial: {SITE_URL}

Anyone else doing this? What workflow changes helped you?
""",
    },
    {
        "text": f"Windows dictation in 2026: Win+H is still broken. Local Whisper is slow. Dragon costs $500.\n\nThe sweet spot: Groq Whisper = 200ms, auto-paste at cursor, custom hotkey.\n\nBuilt it and shipping it → {SITE_URL}\n\n#buildinpublic #indiedev",
        "thread": [
            f"Windows dictation in 2026 is still a mess. So I fixed it.\n\n{SITE_URL}",
            "The comparison nobody talks about:\n\n• Win+H — 2-3s, no auto-paste, free\n• Dragon — OK speed, $500+\n• Local Whisper — 1-2s, no auto-paste, free\n• Wispr Flow — fast, Mac only\n\nFast + Windows + auto-paste at cursor = gap in market.",
            "dictate.app fills that gap:\n→ Groq Whisper = ~200ms\n→ Auto-paste at cursor (not clipboard)\n→ Custom hotkey\n→ Bring your own Groq API key (free tier works)\n\nBuilding in public. Brutal feedback welcome.\n\n#indiedev #buildinpublic",
        ],
        "title": "Windows dictation in 2026 is still broken — so I fixed it",
        "body": f"""Voice dictation on Windows in 2026 is still a mess:

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

{SITE_URL} — 7-day free trial
""",
    },
    {
        "text": f"Hot take: the best productivity upgrade isn't a new app. It's stopping typing altogether.\n\nI dictate everything now. Emails, docs, Slack messages. 150 wpm vs 60 wpm.\n\nWindows-native tool I built → {SITE_URL}\n\n#productivity #indiedev",
        "thread": [
            "Hot take: the best productivity upgrade isn't a new app. It's stopping typing altogether.",
            f"I dictate everything now.\n\nEmails. Slack. Docs. Even these posts.\n\nSpeaking is 150 wpm. Typing is 60. That's 2.5x output for the same mental effort.\n\nTool (Windows) → {SITE_URL}",
            "The trick that made it stick: remap the hotkey to a mouse side button.\n\nNo keyboard chord to remember. One thumb click, speak, done. It becomes invisible.\n\n#productivity #buildinpublic",
        ],
        "title": "Hot take: stop typing. Your output will double.",
        "body": f"""Everyone's optimizing their note apps, task managers, and keyboard shortcuts.

Nobody's talking about the 2.5x unlock hiding in plain sight: just talk instead of type.

Average typing speed: 60 wpm.
Average speaking speed: 150 wpm.

I've been dictating for months. Emails, Slack, docs, code comments. Here's how to make it stick:

**Use a mouse button, not a keyboard hotkey.** A side button is always reachable. No chord to remember. One click, speak, done.

**Don't stop to correct mid-sentence.** Let the thought finish. Fix after. Interrupting yourself costs more than a typo.

**Start with emails.** Low stakes, fast feedback loop. Code comes later once you trust the accuracy.

**Tool I use on Windows:** dictate.app — Ctrl+Space (or any hotkey), speak, text appears at cursor. ~200ms via Groq Whisper.

Free trial: {SITE_URL}
""",
    },
]

# ── Bluesky helpers ────────────────────────────────────────────────────────────
def build_facets(text, urls=None):
    """Build AT Protocol facets for URLs found in text."""
    facets = []
    text_bytes = text.encode("utf-8")

    # Auto-detect URLs if not provided
    if urls is None:
        urls = re.findall(r'https?://[^\s]+', text)

    for url in urls:
        url_bytes = url.encode("utf-8")
        start = text_bytes.find(url_bytes)
        if start == -1:
            continue
        facets.append({
            "index": {"byteStart": start, "byteEnd": start + len(url_bytes)},
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": url}]
        })

    # Also detect #hashtags as tag facets
    for m in re.finditer(r'#(\w+)', text):
        tag = m.group(1)
        start = text_bytes.find(m.group(0).encode("utf-8"))
        if start == -1:
            continue
        facets.append({
            "index": {"byteStart": start, "byteEnd": start + len(m.group(0).encode("utf-8"))},
            "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": tag}]
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


def bsky_post(session, text):
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    text = text[:300]
    facets = build_facets(text)
    record = {"$type": "app.bsky.feed.post", "text": text, "createdAt": now}
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
        result = json.loads(r.read())
    return result


def bsky_reply(session, text, root_uri, root_cid, parent_uri, parent_cid):
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    text = text[:300]
    facets = build_facets(text)
    record = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": now,
        "reply": {
            "root": {"uri": root_uri, "cid": root_cid},
            "parent": {"uri": parent_uri, "cid": parent_cid}
        }
    }
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
    thread = post.get("thread")

    if thread and len(thread) > 1:
        # Post thread: root + replies
        root = bsky_post(session, thread[0])
        root_uri = root["uri"]
        root_cid = root["cid"]
        parent_uri, parent_cid = root_uri, root_cid

        for reply_text in thread[1:]:
            reply = bsky_reply(session, reply_text, root_uri, root_cid, parent_uri, parent_cid)
            parent_uri = reply["uri"]
            parent_cid = reply["cid"]

        return root
    else:
        return bsky_post(session, post["text"])


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
    week = datetime.datetime.utcnow().isocalendar()[1]
    post = POSTS[week % len(POSTS)]

    results = {}

    bsky_handle   = os.getenv("BLUESKY_HANDLE")
    bsky_password = os.getenv("BLUESKY_PASSWORD")
    if bsky_handle and bsky_password:
        try:
            results["bluesky"] = post_bluesky_thread(bsky_handle, bsky_password, post)
            thread_len = len(post.get("thread", [post["text"]]))
            print(f"✓ Bluesky posted ({thread_len}-post thread)")
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
