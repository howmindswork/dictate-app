#!/usr/bin/env python3
"""
Post 5 selected Bluesky posts for @hmwofficial.bsky.social (dictate.app)
Spaces them 2 minutes apart.
"""

import sys
import time
from atproto import Client

HANDLE   = "hmwofficial.bsky.social"
PASSWORD = "i3gw-h7bn-zedb-tnz6"

POSTS = [
    # Post 3 — Stats + Groq speed + link
    "Groq's Whisper transcription runs in ~200ms. That's not a typo. You finish speaking and the text is already there. dictate.app runs it locally on Windows with no cloud roundtrip. https://dictate-app.pages.dev/download",

    # Post 19 — Vivid demo
    "Here's what using dictate.app feels like. You're in Gmail. You hold your hotkey. You say \"Hey Sarah, just following up on the proposal from Monday.\" You release. It's already there. Done.",

    # Post 7 — Build in public milestone
    "Build in public update: dictate.app just crossed its first 100 active installs. No ads. No launch post. Just word of mouth from people who stopped typing and never went back.",

    # Post 26 — Dragon comparison + link
    "Dragon NaturallySpeaking costs $150-$500 upfront plus annual support fees. It's powerful. It's also heavy, slow to start, and designed for an era before Whisper existed. dictate.app is $9/mo. https://dictate-app.pages.dev/download",

    # Post 13 — Writer use case
    "Writers: stop losing ideas because typing is too slow. dictate.app lets you speak a rough draft at 130 WPM. Edit later. The blank page is less scary when you can just talk at it.",
]

def main():
    client = Client()
    print(f"Logging in as {HANDLE}...")
    client.login(HANDLE, PASSWORD)
    print("Logged in.\n")

    posted_uris = []

    for i, text in enumerate(POSTS):
        print(f"[{i+1}/{len(POSTS)}] Posting ({len(text)} chars)...")
        print(f"  {text[:80]}...")
        resp = client.send_post(text=text)
        uri = resp.uri
        # Convert AT URI to web URL
        # Format: at://did:plc:xxx/app.bsky.feed.post/rkey
        parts = uri.split("/")
        rkey = parts[-1]
        did = parts[2]
        web_url = f"https://bsky.app/profile/{HANDLE}/post/{rkey}"
        print(f"  Posted: {web_url}\n")
        posted_uris.append(web_url)

        if i < len(POSTS) - 1:
            print("  Waiting 2 minutes before next post...")
            time.sleep(120)

    print("\nAll posts sent:")
    for url in posted_uris:
        print(f"  {url}")

if __name__ == "__main__":
    main()
