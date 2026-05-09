#!/usr/bin/env python3
"""
Export Reddit session cookies for GitHub Actions.
Run this ONCE after reddit_login_setup.py:
  python3 scripts/reddit_export_cookies.py

Copy the printed base64 string → GitHub repo Settings → Secrets → REDDIT_COOKIES_MR1V4
"""
import os, json, base64
from camoufox.sync_api import Camoufox

PROFILE_DIR = os.path.expanduser("~/.reddit_profiles/Mr1v4")

if not os.path.exists(PROFILE_DIR):
    print("ERROR: No profile found. Run reddit_login_setup.py first.")
    raise SystemExit(1)

print("Opening saved session to export cookies...")
with Camoufox(headless=True, user_data_dir=PROFILE_DIR) as browser:
    page = browser.new_page()
    page.goto("https://www.reddit.com", timeout=30000)
    if "login" in page.url:
        print("ERROR: Session expired. Re-run reddit_login_setup.py first.")
        raise SystemExit(1)
    cookies = page.context.cookies()

encoded = base64.b64encode(json.dumps(cookies).encode()).decode()

print("\n" + "=" * 60)
print("Add this as GitHub secret: REDDIT_COOKIES_MR1V4")
print("=" * 60)
print(encoded)
print("=" * 60)
print(f"\n{len(cookies)} cookies exported.")
