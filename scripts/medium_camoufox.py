#!/usr/bin/env python3
"""
Medium cross-poster for dictate-app articles.
Fetches from dev.to, posts to Medium via Camoufox browser automation.
Rate limit: 1 article per run, 1 run per week max.

CREDENTIALS NEEDED — add to ~/.claude_secrets:
  export MEDIUM_EMAIL="your@email.com"
  export MEDIUM_PASSWORD="yourpassword"
"""
import os, json, time, random, sys, urllib.request
from pathlib import Path
from datetime import datetime, timedelta

DEVTO_KEY  = os.environ.get("DEVTO_API_KEY", "")
MED_EMAIL  = os.environ.get("MEDIUM_EMAIL", "")
MED_PASS   = os.environ.get("MEDIUM_PASSWORD", "")
LOG_FILE   = Path(__file__).parent / "medium_post_log.json"
RATE_DAYS  = 7  # minimum days between runs


def load_log():
    if LOG_FILE.exists():
        return json.loads(LOG_FILE.read_text())
    return {"posted": [], "last_run": None}


def save_log(log):
    LOG_FILE.write_text(json.dumps(log, indent=2))


def rate_limited(log):
    if not log["last_run"]:
        return False
    last = datetime.fromisoformat(log["last_run"])
    return datetime.utcnow() - last < timedelta(days=RATE_DAYS)


def fetch_devto_articles():
    req = urllib.request.Request(
        "https://dev.to/api/articles/me/published?per_page=30",
        headers={"api-key": DEVTO_KEY}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def fetch_article_body(article_id):
    req = urllib.request.Request(
        f"https://dev.to/api/articles/{article_id}",
        headers={"api-key": DEVTO_KEY}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def post_to_medium(title, body_markdown, tags):
    from camoufox.sync_api import Camoufox

    with Camoufox(headless=True) as browser:
        page = browser.new_page()

        # Login
        page.goto("https://medium.com/m/signin", wait_until="networkidle")
        time.sleep(random.uniform(2, 4))

        # Click "Sign in with email"
        try:
            page.get_by_text("Sign in with email").click()
            time.sleep(random.uniform(1, 2))
        except Exception:
            page.get_by_text("Continue with email").click()
            time.sleep(random.uniform(1, 2))

        page.fill('input[type="email"]', MED_EMAIL)
        page.keyboard.press("Enter")
        time.sleep(random.uniform(1, 2))
        page.fill('input[type="password"]', MED_PASS)
        page.keyboard.press("Enter")
        time.sleep(random.uniform(3, 5))

        # Navigate to new story
        page.goto("https://medium.com/new-story", wait_until="networkidle")
        time.sleep(random.uniform(2, 3))

        # Fill title
        title_el = page.locator("h3[data-placeholder='Title']").first
        title_el.click()
        title_el.fill(title)
        time.sleep(random.uniform(0.5, 1))
        page.keyboard.press("Tab")

        # Fill body — type in chunks to avoid paste detection
        body_el = page.locator("p[data-placeholder='Tell your story...']").first
        body_el.click()
        # Split into chunks and type with small delays
        chunks = [body_markdown[i:i+500] for i in range(0, len(body_markdown), 500)]
        for chunk in chunks:
            page.keyboard.type(chunk, delay=random.randint(5, 20))
            time.sleep(random.uniform(0.2, 0.8))

        time.sleep(random.uniform(2, 3))

        # Click Publish button
        page.get_by_role("button", name="Publish").click()
        time.sleep(random.uniform(2, 3))

        # Add tags in the publish dialog
        tag_input = page.locator("input[placeholder*='tag']").first
        for tag in tags[:5]:
            tag_input.fill(tag)
            page.keyboard.press("Enter")
            time.sleep(random.uniform(0.3, 0.7))

        # Confirm publish
        page.get_by_role("button", name="Publish now").click()
        time.sleep(random.uniform(3, 5))

        return page.url


def main():
    if not DEVTO_KEY:
        print("ERROR: DEVTO_API_KEY not set in environment")
        sys.exit(1)
    if not MED_EMAIL or not MED_PASS:
        print("ERROR: MEDIUM_EMAIL or MEDIUM_PASSWORD not set in ~/.claude_secrets")
        print("Add: export MEDIUM_EMAIL='your@email.com'")
        print("Add: export MEDIUM_PASSWORD='yourpassword'")
        sys.exit(1)

    log = load_log()

    if rate_limited(log):
        print(f"Rate limited — last run {log['last_run']}. Min {RATE_DAYS} days between runs.")
        sys.exit(0)

    articles = fetch_devto_articles()
    already_posted = set(log["posted"])

    # Find first article not yet posted
    to_post = None
    for a in articles:
        if str(a["id"]) not in already_posted:
            to_post = a
            break

    if not to_post:
        print("All articles already posted to Medium.")
        sys.exit(0)

    print(f"Posting: {to_post['title']}")
    full = fetch_article_body(to_post["id"])
    body = full.get("body_markdown", full.get("body_html", ""))

    tags = ["productivity", "windows", "voice-dictation", "developer-tools", "dictation"]

    try:
        medium_url = post_to_medium(to_post["title"], body, tags)
        log["posted"].append(str(to_post["id"]))
        log["last_run"] = datetime.utcnow().isoformat()
        save_log(log)
        print(f"Posted: {medium_url}")
    except Exception as e:
        print(f"ERROR posting to Medium: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
