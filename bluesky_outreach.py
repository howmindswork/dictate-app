#!/usr/bin/env python3
"""
Bluesky affiliate outreach for dictate.app
Finds relevant accounts and sends DMs about the affiliate program.
"""

import requests
import time
import json
from datetime import datetime, timezone

# Credentials
HANDLE = "hmwofficial.bsky.social"
APP_PASSWORD = "i3gw-h7bn-zedb-tnz6"
BASE_URL = "https://bsky.social/xrpc"
CHAT_URL = "https://api.bsky.chat/xrpc"
PUBLIC_URL = "https://public.api.bsky.app/xrpc"

# Search terms targeting the right audience
SEARCH_TERMS = [
    "obsidian notes",
    "notion productivity",
    "voice typing",
    "dictation workflow",
    "ADHD productivity",
    "writing workflow",
    "PKM tools",
    "second brain",
]

LOG_FILE = "/home/luke/dictate-app-website/outreach-log.md"

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
        print(f"  Search failed for '{query}': {resp.status_code} {resp.text[:200]}")
        return []
    return resp.json().get("posts", [])

def get_profile(token, actor):
    resp = requests.get(f"{BASE_URL}/app.bsky.actor.getProfile", params={
        "actor": actor
    }, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code != 200:
        return None
    return resp.json()

def get_or_create_convo(token, my_did, member_did):
    # members must be repeated query params, not a list
    url = f"{CHAT_URL}/chat.bsky.convo.getConvoForMembers?members={my_did}&members={member_did}"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code != 200:
        print(f"  getConvoForMembers failed: {resp.status_code} {resp.text[:300]}")
        return None
    return resp.json().get("convo", {}).get("id")

def send_dm(token, convo_id, message):
    resp = requests.post(f"{CHAT_URL}/chat.bsky.convo.sendMessage", json={
        "convoId": convo_id,
        "message": {"text": message}
    }, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    if resp.status_code != 200:
        print(f"  sendMessage failed: {resp.status_code} {resp.text[:300]}")
        return False
    return True

def build_message(display_name, recent_topic):
    name = display_name.split()[0] if display_name else "there"
    msg = (
        f"Hey {name} — loved your post on {recent_topic}.\n\n"
        f"I built dictate.app — voice dictation for Windows using Groq Whisper. "
        f"200ms latency, works in every app.\n\n"
        f"We pay 40% recurring commission. So if you mention it once and someone subscribes, "
        f"you get $3.60/month from them forever.\n\n"
        f"No review required, just an affiliate link. Want the details?"
    )
    return msg

def append_log(entries):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    with open(LOG_FILE, "a") as f:
        f.write(f"\n## Outreach run — {timestamp}\n\n")
        f.write("| Handle | Display Name | Followers | Topic | Status | Time |\n")
        f.write("|--------|-------------|-----------|-------|--------|------|\n")
        for e in entries:
            f.write(f"| @{e['handle']} | {e['display_name']} | {e['followers']} | {e['topic']} | {e['status']} | {e['time']} |\n")

def main():
    print("Authenticating...")
    token, my_did = auth()
    print(f"Authenticated as {HANDLE} (DID: {my_did})")

    # Collect candidate accounts: handle -> {profile, topic, post_text}
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
            if handle in candidates:
                continue

            # Get full profile for follower count (searchPosts doesn't include it)
            profile = get_profile(token, handle)
            if not profile:
                continue

            followers_full = profile.get("followersCount", 0)
            if followers_full < 200:
                continue

            # Check account isn't too big (>10k)
            if followers_full > 10000:
                continue

            # Grab post text for topic context
            record = post.get("record", {})
            post_text = record.get("text", "")[:80].replace("\n", " ")

            candidates[handle] = {
                "did": author.get("did", ""),
                "display_name": profile.get("displayName", handle),
                "followers": followers_full,
                "topic": term,
                "post_text": post_text,
            }
            print(f"    Found: @{handle} ({followers_full} followers)")

        if len(candidates) >= 40:
            break
        time.sleep(1)

    print(f"\nFound {len(candidates)} candidate accounts.")

    # Sort by followers descending, take top 20 to have buffer
    sorted_candidates = sorted(candidates.values(), key=lambda x: x["followers"], reverse=True)[:20]

    print("\nSending DMs (30s gap between each)...")
    log_entries = []
    dm_count = 0
    target = 15

    for c in sorted_candidates:
        if dm_count >= target:
            break

        handle_val = [h for h, v in candidates.items() if v["did"] == c["did"]][0]
        print(f"\n  [{dm_count+1}/{target}] @{handle_val} ({c['followers']} followers)")

        # Build message
        topic_label = c["topic"]
        message = build_message(c["display_name"], topic_label)

        # Get/create conversation
        convo_id = get_or_create_convo(token, my_did, c["did"])
        if not convo_id:
            print(f"    Could not get convo for @{handle_val}, skipping.")
            log_entries.append({
                "handle": handle_val,
                "display_name": c["display_name"],
                "followers": c["followers"],
                "topic": topic_label,
                "status": "FAILED - no convo",
                "time": datetime.now(timezone.utc).strftime("%H:%M UTC")
            })
            continue

        # Send DM
        success = send_dm(token, convo_id, message)
        status = "SENT" if success else "FAILED - send error"
        print(f"    {status}")

        log_entries.append({
            "handle": handle_val,
            "display_name": c["display_name"],
            "followers": c["followers"],
            "topic": topic_label,
            "status": status,
            "time": datetime.now(timezone.utc).strftime("%H:%M UTC")
        })

        if success:
            dm_count += 1
            if dm_count < target:
                print(f"    Waiting 30s before next DM...")
                time.sleep(30)
        else:
            time.sleep(5)

    print(f"\nDone. Sent {dm_count} DMs.")

    # Initialize log file if needed
    import os
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write("# dictate.app Bluesky Outreach Log\n\n")

    append_log(log_entries)
    print(f"Log written to {LOG_FILE}")

    # Summary
    print("\n=== SUMMARY ===")
    for e in log_entries:
        print(f"  @{e['handle']} ({e['followers']} followers) — {e['status']}")

if __name__ == "__main__":
    main()
