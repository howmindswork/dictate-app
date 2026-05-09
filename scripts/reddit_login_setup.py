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

    logged_in = False
    for _ in range(60):  # poll up to 5 minutes
        time.sleep(5)
        try:
            # Logged in = user avatar/menu visible, no login button
            has_login_btn = page.locator('[data-testid="login-button"], button:has-text("Log In")').count()
            has_user_menu = page.locator('[data-testid="user-drawer-content"], #USER_DROPDOWN_ID, [aria-label="user actions"]').count()
            url = page.url

            if has_login_btn == 0 and "login" not in url:
                logged_in = True
                print("Login detected! Saving cookies...")
                break
            print(f"  Waiting for login... ({_*5}s)")
        except Exception:
            pass

    cookies = ctx.cookies()

if not logged_in:
    print("Timed out waiting for login. Try again.")
    raise SystemExit(1)

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
