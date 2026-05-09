#!/usr/bin/env python3
"""
One-time Reddit login setup for Mr1v4.
Run this ONCE from Windows PowerShell:
  python scripts/reddit_login_setup.py

Camoufox opens a visible Firefox window.
Log in with Google. Close the browser when done.
Cookies are saved forever — bot runs headless after this.
"""
import os
from camoufox.sync_api import Camoufox

PROFILE_DIR = os.path.expanduser("~/.reddit_profiles/Mr1v4")
os.makedirs(PROFILE_DIR, exist_ok=True)

print("Opening Reddit login window...")
print("Log in with Google, then close the browser.")
print(f"Profile will be saved to: {PROFILE_DIR}")

with Camoufox(headless=False, user_data_dir=PROFILE_DIR) as browser:
    page = browser.new_page()
    page.goto("https://www.reddit.com/login")
    print("Browser open — log in now. Close the window when done.")
    try:
        page.wait_for_event("close", timeout=300000)
    except Exception:
        pass

print("Login saved. Bot will now run headless automatically.")
print("Test with: python3 scripts/reddit_camoufox.py --dry-run")
