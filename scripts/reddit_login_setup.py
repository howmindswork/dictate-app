#!/usr/bin/env python3
"""
One-time Reddit login setup for Mr1v4.
Run this ONCE:
  python3 scripts/reddit_login_setup.py

Firefox opens. Log in with Google. Script auto-detects login and saves cookies.
"""
import os, json, base64, time
from pathlib import Path
from camoufox.sync_api import Camoufox

COOKIES_FILE = Path(os.path.expanduser("~/.reddit_profiles/Mr1v4/cookies.json"))
COOKIES_FILE.parent.mkdir(parents=True, exist_ok=True)

print("Opening Reddit in Firefox...")
print("Click 'Log In', use Google OAuth, complete login.")
print("Script will auto-save cookies once you're logged in.\n")

with Camoufox(headless=False) as browser:
    ctx = browser.new_context()
    page = ctx.new_page()
    page.goto("https://www.reddit.com", timeout=30000)

    print("Browser is open. Log in via Google OAuth as Mr1v4.")
    print("Waiting for login button to appear...")

    # Step 1: wait for login button to become visible (page loaded)
    try:
        page.locator('[data-testid="login-button"]').wait_for(timeout=30000)
        print("Login button detected. Please click it and log in as Mr1v4.")
    except Exception:
        print("(Login button not found — already logged in?)")

    # Step 2: wait for login button to disappear (login complete)
    print("Waiting for you to complete login...")
    for i in range(120):  # up to 10 minutes
        time.sleep(5)
        try:
            btn_count = page.locator('[data-testid="login-button"]').count()
            current_url = page.url
            if btn_count == 0 and "login" not in current_url and "reddit.com" in current_url:
                # Extra confirm: check for logged-in indicator
                time.sleep(3)
                if page.locator('[data-testid="login-button"]').count() == 0:
                    print("Login confirmed!")
                    break
        except Exception:
            pass
        if i % 6 == 5:
            print(f"  Still waiting... ({(i+1)*5}s)")

    time.sleep(2)
    cookies = ctx.cookies()

reddit_cookies = [c for c in cookies if "reddit" in c.get("domain", "")]
if len(reddit_cookies) < 3:
    print(f"WARNING: Only {len(reddit_cookies)} Reddit cookies found. Login may not be complete.")

COOKIES_FILE.write_text(json.dumps(cookies, indent=2))
print(f"Saved {len(cookies)} cookies ({len(reddit_cookies)} Reddit) to {COOKIES_FILE}")

# Auto-set GitHub secret if gh CLI available
encoded = base64.b64encode(json.dumps(cookies).encode()).decode()
try:
    import subprocess
    result = subprocess.run(
        ["gh", "secret", "set", "REDDIT_COOKIES_MR1V4",
         "--body", encoded, "--repo", "howmindswork/dictate-app"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("GitHub secret REDDIT_COOKIES_MR1V4 updated automatically!")
    else:
        print("Could not auto-set GitHub secret. Run manually:")
        print(f"  python3 scripts/reddit_export_cookies.py")
except FileNotFoundError:
    print("gh CLI not found. Set secret manually.")

print("\nDone. Test with: python3 scripts/reddit_camoufox.py --dry-run")
