#!/usr/bin/env python3
"""
dictate.app Bluesky engagement bot.
Replies to relevant posts in #buildinpublic / #indiedev / Windows productivity niche.
Runs via GitHub Actions 2x/day.
"""

import os, sys, json, datetime, time, random
from pathlib import Path

HANDLE = "hmwofficial.bsky.social"
SITE_URL = "https://dictate-app.pages.dev"

REPLIED_FILE = Path(__file__).parent / "engage-replied.json"
MAX_REPLIES = 5

SEARCH_TERMS = [
    "buildinpublic windows",
    "indiedev productivity",
    "voice dictation windows",
    "whisper transcription",
    "dictation software",
    "typing too slow",
    "side mouse button productivity",
    "faster than typing",
    "launched my app",
    "shipped today",
    "indie saas",
    "solopreneur tools",
    "keyboard shortcuts productivity",
]

REPLY_PROMPTS = [
    "indie dev building dictate.app (Windows voice typing). write a 1-sentence reply that adds a specific insight or asks a genuine question. no self-promotion. max 200 chars.",
    "you're a windows productivity indie hacker. write a brief reply that's specific to the post, adds value, and feels like a real person replied. no marketing. under 200 chars.",
    "you build dictate.app. write a reply that shares a concrete finding or asks what they'd add. skip intros. be direct. under 180 chars.",
]


def load_replied():
    if REPLIED_FILE.exists():
        try:
            data = json.loads(REPLIED_FILE.read_text())
            cutoff = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=7)).isoformat()
            return {k: v for k, v in data.items() if v > cutoff}
        except Exception:
            return {}
    return {}


def save_replied(data):
    REPLIED_FILE.write_text(json.dumps(data, indent=2))


def ai_reply(post_text: str) -> str:
    bluesky_path = str(Path(__file__).parent.parent.parent / "bluesky")
    if bluesky_path not in sys.path:
        sys.path.insert(0, bluesky_path)
    try:
        from agents.token_manager import call
        prompt = random.choice(REPLY_PROMPTS)
        return call([
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Post: {post_text[:300]}\n\nWrite the reply:"},
        ], max_tokens=80, budget="fast", temperature=0.85)
    except Exception as e:
        print(f"  [engage] AI failed: {e}")
        return ""


def run():
    bluesky_path = str(Path(__file__).parent.parent.parent / "bluesky")
    if bluesky_path not in sys.path:
        sys.path.insert(0, bluesky_path)

    secrets = {}
    secrets_path = Path.home() / ".claude_secrets"
    if secrets_path.exists():
        for line in secrets_path.read_text().splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                k = k.replace("export ", "").strip()
                v = v.strip().strip('"').strip("'")
                secrets[k] = v

    password = secrets.get("BLUESKY_HMWOFFICIAL_PASSWORD") or os.environ.get("BLUESKY_APP_PASSWORD", "")
    if not password:
        print("[engage] No password found")
        return

    from atproto import Client
    bsky = Client()
    bsky.login(HANDLE, password)
    print(f"[engage] Logged in as {HANDLE}")

    replied = load_replied()
    reply_count = 0
    term = random.choice(SEARCH_TERMS)

    print(f"[engage] Searching: {term}")
    try:
        results = bsky.app.bsky.feed.search_posts({"q": term, "limit": 20, "sort": "latest"})
        posts = results.posts if hasattr(results, "posts") else []
    except Exception as e:
        print(f"  [engage] Search failed: {e}")
        return

    for post in posts:
        if reply_count >= MAX_REPLIES:
            break

        uri = post.uri
        if uri in replied:
            continue
        if post.author.handle == HANDLE:
            continue

        text = getattr(post.record, "text", "") if hasattr(post, "record") else ""
        if len(text) < 25:
            continue

        # Skip posts already many hours old (engage while fresh)
        try:
            age_hours = (datetime.datetime.now(datetime.UTC) - datetime.datetime.fromisoformat(
                post.indexed_at.replace("Z", "+00:00")
            )).total_seconds() / 3600
            if age_hours > 18:
                continue
        except Exception:
            pass

        reply_text = ai_reply(text)
        if not reply_text or len(reply_text) < 10:
            continue

        reply_text = reply_text.strip().strip('"')

        try:
            parent_ref = {"uri": post.uri, "cid": post.cid}
            root_ref = parent_ref
            if hasattr(post.record, "reply") and post.record.reply:
                root_ref = {"uri": post.record.reply.root.uri, "cid": post.record.reply.root.cid}

            bsky.send_post(
                text=reply_text[:300],
                reply_to={"root": root_ref, "parent": parent_ref},
            )
            replied[uri] = datetime.datetime.now(datetime.UTC).isoformat()
            save_replied(replied)
            reply_count += 1
            print(f"  [engage] Replied to @{post.author.handle}: {reply_text[:80]}")
            time.sleep(random.uniform(8, 20))
        except Exception as e:
            print(f"  [engage] Reply failed: {e}")

    print(f"[engage] Done. {reply_count} replies sent.")


if __name__ == "__main__":
    run()
