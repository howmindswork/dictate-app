#!/usr/bin/env python3
"""
Bluesky auto-poster for @hmwbsky.bsky.social (HMW)
Posts the next queued post from bluesky-post-queue.md.
Tracks position in bluesky-post-index.txt. Wraps around when done.
"""

import os
import re
import sys

HANDLE = "hmwbsky.bsky.social"
QUEUE_FILE = os.path.join(os.path.dirname(__file__), "bluesky-post-queue.md")
INDEX_FILE = os.path.join(os.path.dirname(__file__), "bluesky-post-index.txt")

def get_password():
    pw = os.environ.get("BLUESKY_PASSWORD") or os.environ.get("BLUESKY_APP_PASSWORD")
    if pw:
        return pw
    secrets = os.path.expanduser("~/.claude_secrets")
    if os.path.exists(secrets):
        with open(secrets) as f:
            for line in f:
                line = line.strip()
                if line.startswith("BLUESKY_APP_PASSWORD") or line.startswith("BLUESKY_HMWOFFICIAL_PASSWORD"):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise ValueError("No Bluesky password found")

def parse_queue(path):
    with open(path) as f:
        content = f.read()
    posts = []
    for block in re.split(r"---", content):
        lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
        text_lines = []
        for line in lines:
            if line.startswith("#") or line.startswith("**") or line.startswith("Category") or line.startswith("Format") or line.startswith("Generated") or line.startswith("Half"):
                continue
            text_lines.append(line)
        text = " ".join(text_lines).strip()
        if len(text) > 50:
            posts.append(text)
    return posts

def get_index(path):
    if os.path.exists(path):
        with open(path) as f:
            try:
                return int(f.read().strip())
            except:
                return 0
    return 0

def save_index(path, idx):
    with open(path, "w") as f:
        f.write(str(idx))

def post_to_bluesky(handle, password, text):
    try:
        from atproto import Client
    except ImportError:
        os.system("pip install atproto -q")
        from atproto import Client
    try:
        client = Client()
        client.login(handle, password)
        client.send_post(text=text[:300])
        print(f"Posted ({len(text)} chars): {text[:80]}...")
    except Exception as e:
        if "AccountTakedown" in str(e) or "account_taken_down" in str(e):
            print(f"[autopost] Account {handle} is banned. Exiting gracefully.")
            sys.exit(0)
        raise

def main():
    posts = parse_queue(QUEUE_FILE)
    if not posts:
        print("No posts in queue")
        sys.exit(1)

    idx = get_index(INDEX_FILE)
    if idx >= len(posts):
        idx = 0
        print("Queue complete — wrapping around")

    post = posts[idx]
    password = get_password()

    print(f"Posting #{idx + 1} of {len(posts)}")
    post_to_bluesky(HANDLE, password, post)
    save_index(INDEX_FILE, idx + 1)

if __name__ == "__main__":
    main()
