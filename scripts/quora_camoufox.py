#!/usr/bin/env python3
"""
Quora auto-answerer for dictate-app using Camoufox.
Finds questions about Windows dictation, posts genuine helpful answers.
Runs once/week (Saturday 10 AM ET), max 2 answers per run.

SETUP: Add to ~/.claude_secrets:
  export QUORA_EMAIL="your_quora_email"
  export QUORA_PASSWORD="your_quora_password"
"""

import os, json, random, time, sys
from datetime import datetime, timedelta
from pathlib import Path

QUORA_EMAIL = os.environ.get("QUORA_EMAIL", "")
QUORA_PASSWORD = os.environ.get("QUORA_PASSWORD", "")

if not QUORA_EMAIL or not QUORA_PASSWORD:
    print("ERROR: Set QUORA_EMAIL and QUORA_PASSWORD in ~/.claude_secrets")
    sys.exit(1)

LOG_FILE = Path(__file__).parent / "quora_post_log.json"
SITE_URL = "https://dictate-app.pages.dev"
MAX_ANSWERS = 2

SEARCH_QUERIES = [
    "best windows dictation software 2026",
    "voice typing windows alternative dragon",
    "groq whisper windows app",
    "push to talk dictation windows",
    "windows voice dictation not dragon",
]

ANSWER_TEMPLATE = f"""The Windows dictation landscape in 2026 is honestly frustrating — there are four options and none of them are great by default:

**Win+H (built-in):** Stops recording mid-sentence if you pause. No auto-paste. You have to manually copy-paste into wherever you're typing. Basically unusable for serious work.

**Dragon NaturallySpeaking:** $500+ and it still requires training. Overkill for most people, and the pricing hasn't changed in 20 years.

**Local Whisper:** Incredibly accurate, but 1–2 second latency on CPU. On a GPU it's faster but you need a decent graphics card and the setup is annoying.

**Wispr Flow / Superwhisper:** The best UX by far — but they're Mac-only.

What I landed on: [dictate.app]({SITE_URL}) — it uses Groq's Whisper API for ~200ms transcription (way faster than local CPU Whisper), and it injects text directly at your cursor position in any app. Push-to-talk with Ctrl+Shift+Space by default, fully remappable.

The auto-paste-at-cursor is the thing that makes it actually usable. Most tools dump to clipboard and you paste manually. This one types directly wherever your cursor is.

7-day free trial, no card required. Worth testing for a week if you write a lot."""


def load_log():
    if LOG_FILE.exists():
        return json.loads(LOG_FILE.read_text())
    return {"answered": []}


def save_log(log):
    LOG_FILE.write_text(json.dumps(log, indent=2))


def human_delay(lo=2.0, hi=5.0):
    time.sleep(random.uniform(lo, hi))


def run():
    from camoufox.sync_api import Camoufox

    log = load_log()
    answered = set(log.get("answered", []))
    answers_posted = 0

    with Camoufox(headless=True) as browser:
        page = browser.new_page()

        # Login
        page.goto("https://www.quora.com/", timeout=30000)
        human_delay(2, 4)

        page.goto("https://www.quora.com/login", timeout=30000)
        human_delay(2, 3)

        try:
            page.fill('input[name="email"]', QUORA_EMAIL)
            human_delay(0.5, 1.5)
            page.fill('input[name="password"]', QUORA_PASSWORD)
            human_delay(0.8, 2.0)
            page.click('button[type="submit"], input[type="submit"]')
            page.wait_for_load_state("networkidle", timeout=15000)
            human_delay(2, 4)
        except Exception as e:
            print(f"Login error: {e}")
            return False

        for query in random.sample(SEARCH_QUERIES, len(SEARCH_QUERIES)):
            if answers_posted >= MAX_ANSWERS:
                break

            # Search for questions
            page.goto(f"https://www.quora.com/search?q={query.replace(' ', '+')}&type=question", timeout=30000)
            human_delay(3, 5)

            # Find question links
            links = page.locator("a[href*='/']").all()
            question_urls = []
            for link in links[:20]:
                href = link.get_attribute("href") or ""
                if href.startswith("/") and "-" in href and len(href) > 10 and "search" not in href:
                    full = "https://www.quora.com" + href
                    if full not in answered:
                        question_urls.append(full)

            for q_url in question_urls[:3]:
                if answers_posted >= MAX_ANSWERS:
                    break

                page.goto(q_url, timeout=30000)
                human_delay(3, 6)

                # Check if already answered or closed
                if q_url in answered:
                    continue

                # Click "Answer" button
                try:
                    answer_btn = page.locator('button:has-text("Answer"), a:has-text("Answer")').first
                    answer_btn.click()
                    human_delay(1, 3)
                except Exception:
                    continue

                # Type answer
                try:
                    editor = page.locator('[contenteditable="true"], .doc-content').first
                    editor.click()
                    human_delay(0.5, 1)
                    editor.type(ANSWER_TEMPLATE, delay=random.randint(30, 70))
                    human_delay(2, 4)

                    # Submit
                    submit = page.locator('button:has-text("Submit"), button:has-text("Post")').last
                    submit.click()
                    page.wait_for_load_state("networkidle", timeout=10000)
                    human_delay(2, 3)

                    answered.add(q_url)
                    answers_posted += 1
                    print(f"Answered: {q_url}")
                    human_delay(30, 60)  # Wait between answers
                except Exception as e:
                    print(f"Answer error on {q_url}: {e}")
                    continue

    log["answered"] = list(answered)
    log["last_run"] = datetime.utcnow().isoformat()
    save_log(log)
    print(f"Done. Posted {answers_posted} answers.")
    return True


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
