#!/usr/bin/env python3
"""
One-time Reddit login setup for Mr1v4.
Run this ONCE:
  python3 scripts/reddit_login_setup.py

A Firefox window opens. Log in with Google. Close the browser when done.
Cookies are saved to ~/.reddit_profiles/Mr1v4/cookies.json
"""
import os, json, base64
from pathlib import Path
from camoufox.sync_api import Camoufox

COOKIES_FILE = Path(os.path.expanduser("~/.reddit_profiles/Mr1v4/cookies.json"))
COOKIES_FILE.parent.mkdir(parents=True, exist_ok=True)

print("Opening Reddit login window (Firefox via WSLg)...")
print("Log in with Google. Close the browser when done.")

with Camoufox(headless=False) as browser:
    page = browser.new_page()
    page.goto("https://www.reddit.com/login")
    print("Browser open — log in now. Close the window when done.")
    try:
        page.wait_for_event("close", timeout=300000)
    except Exception:
        pass

    try:
        cookies = page.context.cookies()
    except Exception:
        cookies = []

COOKIES_FILE.write_text(json.dumps(cookies, indent=2))
print(f"\nSaved {len(cookies)} cookies to {COOKIES_FILE}")

# Print base64 for GitHub secret
encoded = base64.b64encode(json.dumps(cookies).encode()).decode()
print("\n" + "=" * 60)
print("GitHub secret → REDDIT_COOKIES_MR1V4:")
print("=" * 60)
print(encoded)
print("=" * 60)
print("\nDone. Test with: python3 scripts/reddit_camoufox.py --dry-run")
