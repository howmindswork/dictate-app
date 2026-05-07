#!/usr/bin/env python3
"""
Bluesky growth infrastructure for dictate.app.
- Task 1: Create "Windows Productivity Tools" starter pack
- Task 2: Post build-in-public thread (3 parts)
- Task 3: Pin post 1 to profile
"""

import requests
import json
import time
from datetime import datetime, timezone

HANDLE = "hmwofficial.bsky.social"
APP_PASSWORD = "i3gw-h7bn-zedb-tnz6"
BASE_URL = "https://bsky.social/xrpc"

# Accounts to include in starter pack (handle -> DID)
STARTER_PACK_ACCOUNTS = {
    "hmwofficial.bsky.social":      "did:plc:6v4i3nht5phcagfqarnyvvd7",  # dictate.app / HMW
    "howtogeek.bsky.social":        "did:plc:qfirfugnq6mit2dsbjn6uixc",  # How-To Geek
    "scrivenerapp.bsky.social":     "did:plc:uud4em4oqfhfs3ifrcsuvd4n",  # Scrivener (Windows writing app)
    "beeskieapp.bsky.social":       "did:plc:ceed6upnlvcikxqb32xpgamj",  # Beeskie (Windows Bluesky app)
    "windowsupdate.bsky.social":    "did:plc:mxxvc3yuqob3nno65jmc6d5a",  # Windows Update
    "windowsground.bsky.social":    "did:plc:6b4xkr6wq4zg4d7uj2ftgd4t",  # Windows Ground
    "dfly.app":                     "did:plc:hljzyofcq4twihud6nfsnl3m",  # Dragonfly (drafts/bookmarks)
    "reintivity.bsky.social":       "did:plc:xpkutblweipuwfctehqecjmf",  # Reintivity (Windows productivity)
    "codewithtyler.com":            "did:plc:sed5tcnrzo7skznjuxbgynav",  # Tyler Hughes (SaaS builder)
    "jimraptis.com":                "did:plc:mkoxdrzc2uajaotzb5zhekcd",  # Jim Raptis (indie SaaS)
    "tsanlis.bsky.social":          "did:plc:w7n4kcfcvwrfayugdp4fhfdq",  # Thomas Sanlis (uneed.best)
    "bndkt.com":                    "did:plc:22n24um7rv6eptuqkqx7yine",  # Benedikt (React/RN indie hacker)
}

# Thread posts
POST_1 = "shipped dictate.app last week. windows voice dictation powered by groq whisper. 200ms avg latency. here's what i've learned so far 🧵 #buildinpublic #groq"
POST_2 = "the hardest part wasn't the AI. it was injecting text into elevated windows processes (admin apps, UAC dialogs). tried 3 approaches before finding what works. groq whisper itself was 50 lines of code."
POST_3 = "if you write a lot on windows and want to try voice dictation — 7-day free trial, no account required: https://dictate-app.pages.dev #productivity #windows #devtools"


def auth():
    resp = requests.post(f"{BASE_URL}/com.atproto.server.createSession", json={
        "identifier": HANDLE,
        "password": APP_PASSWORD
    })
    resp.raise_for_status()
    data = resp.json()
    print(f"Authenticated as: {data['handle']} ({data['did']})")
    return data["accessJwt"], data["did"]


def create_record(token, repo, collection, record):
    resp = requests.post(f"{BASE_URL}/com.atproto.repo.createRecord",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"repo": repo, "collection": collection, "record": record}
    )
    if not resp.ok:
        print(f"  ERROR {resp.status_code}: {resp.text[:300]}")
        resp.raise_for_status()
    return resp.json()


def put_record(token, repo, collection, rkey, record):
    resp = requests.post(f"{BASE_URL}/com.atproto.repo.putRecord",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"repo": repo, "collection": collection, "rkey": rkey, "record": record}
    )
    if not resp.ok:
        print(f"  ERROR {resp.status_code}: {resp.text[:300]}")
        resp.raise_for_status()
    return resp.json()


def delete_record(token, repo, collection, rkey):
    resp = requests.post(f"{BASE_URL}/com.atproto.repo.deleteRecord",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"repo": repo, "collection": collection, "rkey": rkey}
    )
    return resp


# ─── TASK 1: Create Starter Pack ───────────────────────────────────────────────

def create_starter_pack(token, did):
    print("\n=== TASK 1: Creating Starter Pack ===")
    now = datetime.now(timezone.utc).isoformat()

    # Step 1: Create a reference list
    print("Step 1: Creating reference list...")
    list_rec = create_record(token, did, "app.bsky.graph.list", {
        "$type": "app.bsky.graph.list",
        "name": "Windows Productivity Tools",
        "purpose": "app.bsky.graph.defs#referencelist",
        "description": "Top accounts for Windows productivity, developer tools, and indie SaaS — curated by dictate.app",
        "createdAt": now
    })
    list_uri = list_rec["uri"]
    list_cid = list_rec["cid"]
    print(f"  List created: {list_uri}")

    # Step 2: Add accounts to list
    print("Step 2: Adding accounts to list...")
    for handle, account_did in STARTER_PACK_ACCOUNTS.items():
        print(f"  Adding {handle}...")
        try:
            create_record(token, did, "app.bsky.graph.listitem", {
                "$type": "app.bsky.graph.listitem",
                "subject": account_did,
                "list": list_uri,
                "createdAt": datetime.now(timezone.utc).isoformat()
            })
            time.sleep(0.3)
        except Exception as e:
            print(f"  Warning: failed to add {handle}: {e}")

    # Step 3: Create the starter pack
    print("Step 3: Creating starter pack record...")
    sp_rec = create_record(token, did, "app.bsky.graph.starterpack", {
        "$type": "app.bsky.graph.starterpack",
        "name": "Windows Productivity Tools",
        "description": "Apps, tools, and builders focused on Windows productivity. Includes dictate.app — voice dictation powered by Groq Whisper.",
        "list": list_uri,
        "createdAt": now
    })
    sp_uri = sp_rec["uri"]
    sp_cid = sp_rec.get("cid", "")
    print(f"  Starter pack created: {sp_uri}")

    # Derive a share URL
    # AT-URI format: at://did.../app.bsky.graph.starterpack/<rkey>
    rkey = sp_uri.split("/")[-1]
    share_url = f"https://bsky.app/starter-pack/{HANDLE}/{rkey}"
    print(f"  Share URL: {share_url}")

    return sp_uri, share_url


# ─── TASK 2 + 3: Post thread and pin ──────────────────────────────────────────

def post_thread_and_pin(token, did):
    print("\n=== TASK 2+3: Posting build-in-public thread ===")
    now = datetime.now(timezone.utc).isoformat()

    # Post 1 (root)
    print("Posting part 1...")
    p1 = create_record(token, did, "app.bsky.feed.post", {
        "$type": "app.bsky.feed.post",
        "text": POST_1,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "langs": ["en"]
    })
    p1_uri = p1["uri"]
    p1_cid = p1["cid"]
    print(f"  Post 1: {p1_uri}")
    time.sleep(1)

    # Post 2 (reply to p1)
    print("Posting part 2...")
    p2 = create_record(token, did, "app.bsky.feed.post", {
        "$type": "app.bsky.feed.post",
        "text": POST_2,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "langs": ["en"],
        "reply": {
            "root": {"uri": p1_uri, "cid": p1_cid},
            "parent": {"uri": p1_uri, "cid": p1_cid}
        }
    })
    p2_uri = p2["uri"]
    p2_cid = p2["cid"]
    print(f"  Post 2: {p2_uri}")
    time.sleep(1)

    # Post 3 (reply to p2)
    print("Posting part 3...")
    p3 = create_record(token, did, "app.bsky.feed.post", {
        "$type": "app.bsky.feed.post",
        "text": POST_3,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "langs": ["en"],
        "reply": {
            "root": {"uri": p1_uri, "cid": p1_cid},
            "parent": {"uri": p2_uri, "cid": p2_cid}
        }
    })
    p3_uri = p3["uri"]
    print(f"  Post 3: {p3_uri}")

    # Pin post 1
    print("\nPinning post 1 to profile...")
    pin_result = put_record(token, did, "app.bsky.actor.profile", "self", {
        "$type": "app.bsky.actor.profile",
        "pinnedPost": {"uri": p1_uri, "cid": p1_cid}
    })
    print(f"  Profile updated with pinned post.")

    rkey = p1_uri.split("/")[-1]
    post_url = f"https://bsky.app/profile/{HANDLE}/post/{rkey}"
    print(f"  Thread URL: {post_url}")

    return p1_uri, post_url


def main():
    token, did = auth()
    sp_uri, share_url = create_starter_pack(token, did)
    p1_uri, post_url = post_thread_and_pin(token, did)

    print("\n=== DONE ===")
    print(f"Starter pack: {share_url}")
    print(f"Thread post 1: {post_url}")
    print(f"Starter pack AT-URI: {sp_uri}")
    print(f"Post 1 AT-URI: {p1_uri}")


if __name__ == "__main__":
    main()
