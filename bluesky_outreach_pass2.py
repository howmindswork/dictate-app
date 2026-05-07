#!/usr/bin/env python3
"""
Bluesky affiliate outreach pass 2 — reaches remaining candidates.
Already sent to: eliostruyf.com, knowtheory.net, heartpunk.bsky.social,
permaverm.in, mikebrady.bsky.social, thepixelcrush.com
Need 9 more to reach 15 total.
"""

import requests
import time
from datetime import datetime, timezone

HANDLE = "hmwofficial.bsky.social"
APP_PASSWORD = "i3gw-h7bn-zedb-tnz6"
BASE_URL = "https://bsky.social/xrpc"
CHAT_URL = "https://api.bsky.chat/xrpc"

LOG_FILE = "/home/luke/dictate-app-website/outreach-log.md"

ALREADY_SENT = {
    "eliostruyf.com",
    "knowtheory.net",
    "heartpunk.bsky.social",
    "permaverm.in",
    "mikebrady.bsky.social",
    "thepixelcrush.com",
}

SEARCH_TERMS = [
    "obsidian notes",
    "notion productivity",
    "voice typing",
    "dictation workflow",
    "ADHD productivity",
    "writing workflow",
    "PKM tools",
    "second brain",
    "productivity tools",
    "note taking",
    "windows productivity",
    "developer tools",
]

def auth():
    resp = requests.post(f"{BASE_URL}/com.atproto.server.createSession", json={
        "identifier": HANDLE,
        "password": APP_PASSWORD
    })
    resp.raise_for_status()
    data = resp.json()
    return data["accessJwt"], data["did"]

def search_posts(token, query, limit=25):
    resp = requests.get(f"{BASE_URL}/app.bsky.feed.searchPosts", params={
        "q": query,
        "limit": limit
    }, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code != 200:
        print(f"  Search failed for '{query}': {resp.status_code}")
        return []
    return resp.json().get("posts", [])

def get_profile(token, actor):
    resp = requests.get(f"{BASE_URL}/app.bsky.actor.getProfile", params={
        "actor": actor
    }, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code != 200:
        return None
    return resp.json()

def get_convo(token, my_did, member_did):
    url = f"{CHAT_URL}/chat.bsky.convo.getConvoForMembers?members={my_did}&members={member_did}"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code != 200:
        err = resp.json().get("error", "")
        return None, err
    return resp.json().get("convo", {}).get("id"), None

def send_dm(token, convo_id, message):
    resp = requests.post(f"{CHAT_URL}/chat.bsky.convo.sendMessage", json={
        "convoId": convo_id,
        "message": {"text": message}
    }, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    if resp.status_code != 200:
        print(f"  sendMessage failed: {resp.status_code} {resp.text[:200]}")
        return False
    return True

def build_message(display_name, topic):
    name = display_name.split()[0] if display_name else "there"
    # Sanitize name — remove emoji/special chars that might break
    name = ''.join(c for c in name if c.isalpha() or c in " '-").strip() or "there"

    topic_phrases = {
        "obsidian notes": "Obsidian / note-taking",
        "notion productivity": "Notion + productivity",
        "voice typing": "voice typing",
        "dictation workflow": "dictation workflow",
        "ADHD productivity": "ADHD productivity",
        "writing workflow": "writing workflow",
        "PKM tools": "PKM / knowledge tools",
        "second brain": "building a second brain",
        "productivity tools": "productivity tools",
        "note taking": "note-taking",
        "windows productivity": "Windows productivity",
        "developer tools": "dev tools",
    }
    topic_label = topic_phrases.get(topic, topic)

    msg = (
        f"Hey {name} — loved your posts on {topic_label}.\n\n"
        f"I built dictate.app — voice dictation for Windows using Groq Whisper. "
        f"200ms latency, works in every app.\n\n"
        f"We pay 40% recurring commission. Mention it once, someone subscribes — "
        f"you get $3.60/month from them forever.\n\n"
        f"No review required, just an affiliate link. Want the details?"
    )
    return msg

def append_log(entries):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    with open(LOG_FILE, "a") as f:
        f.write(f"\n## Outreach run pass 2 — {timestamp}\n\n")
        f.write("| Handle | Display Name | Followers | Topic | Status | Time |\n")
        f.write("|--------|-------------|-----------|-------|--------|------|\n")
        for e in entries:
            f.write(f"| @{e['handle']} | {e['display_name']} | {e['followers']} | {e['topic']} | {e['status']} | {e['time']} |\n")

def main():
    print("Authenticating...")
    token, my_did = auth()
    print(f"Authenticated as {HANDLE}")

    candidates = {}

    print("\nSearching for relevant accounts...")
    for term in SEARCH_TERMS:
        print(f"  Searching: '{term}'")
        posts = search_posts(token, term, limit=25)
        for post in posts:
            author = post.get("author", {})
            handle = author.get("handle", "")
            if not handle or handle == HANDLE:
                continue
            if handle in candidates or handle in ALREADY_SENT:
                continue

            profile = get_profile(token, handle)
            if not profile:
                continue

            followers = profile.get("followersCount", 0)
            if followers < 200 or followers > 10000:
                continue

            record = post.get("record", {})
            post_text = record.get("text", "")[:80].replace("\n", " ")

            candidates[handle] = {
                "did": author.get("did", ""),
                "display_name": profile.get("displayName", handle),
                "followers": followers,
                "topic": term,
                "post_text": post_text,
            }
            print(f"    Found: @{handle} ({followers} followers)")

        if len(candidates) >= 60:
            break
        time.sleep(0.5)

    print(f"\nFound {len(candidates)} new candidates.")

    sorted_candidates = sorted(candidates.items(), key=lambda x: x[1]["followers"], reverse=True)

    TARGET = 9  # need 9 more to reach 15 total
    log_entries = []
    dm_count = 0

    print(f"\nSending up to {TARGET} more DMs...")
    for handle, c in sorted_candidates:
        if dm_count >= TARGET:
            break

        print(f"\n  [{dm_count+1}/{TARGET}] @{handle} ({c['followers']} followers)")

        message = build_message(c["display_name"], c["topic"])

        convo_id, err = get_convo(token, my_did, c["did"])
        if not convo_id:
            print(f"    Skipping: {err}")
            continue  # Don't log skipped ones, just move on

        success = send_dm(token, convo_id, message)
        status = "SENT" if success else "FAILED - send error"
        t = datetime.now(timezone.utc).strftime("%H:%M UTC")
        print(f"    {status}")

        log_entries.append({
            "handle": handle,
            "display_name": c["display_name"],
            "followers": c["followers"],
            "topic": c["topic"],
            "status": status,
            "time": t,
        })

        if success:
            dm_count += 1
            if dm_count < TARGET:
                print(f"    Waiting 30s...")
                time.sleep(30)
        else:
            time.sleep(5)

    print(f"\nDone. Sent {dm_count} additional DMs (total now ~{dm_count + 6}/15).")
    append_log(log_entries)
    print(f"Log written to {LOG_FILE}")

    print("\n=== SUMMARY ===")
    for e in log_entries:
        print(f"  @{e['handle']} ({e['followers']} followers) — {e['status']}")

if __name__ == "__main__":
    main()
