#!/usr/bin/env python3
"""
Reddit engagement bot for Mr1v4.
Runs from WSL2 (residential IP required — cloud IPs blocked by Reddit).

Modes (pass as arg):
  --scan       Search relevant threads, drop contextual comments
  --replies    Check own posts for new comments, reply to them
  --karma      Post a karma-farming post (non-promotional)
  --monitor    Check recent posts for virality, Telegram alert if blowing up

Cron schedule (set in crontab):
  Every 4h:   --replies
  10am UTC:   --scan
  2pm UTC:    --karma (non-promotional)
  After post: --monitor (run manually or chain after reddit_camoufox.py)
"""

import os, json, random, time, sys, base64, re
from datetime import datetime, timezone, timedelta
from pathlib import Path
import urllib.request, urllib.parse

# ── Config ────────────────────────────────────────────────────────────────────
COOKIES_FILE = Path(os.path.expanduser("~/.reddit_profiles/Mr1v4/cookies.json"))
LOG_FILE = Path(__file__).parent / "reddit_engage_log.json"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT = os.environ.get("TELEGRAM_CHAT_ID", "")

# Viral alert thresholds
ALERT_UPVOTES_30MIN = 50
ALERT_COMMENTS_1HR = 25

# Daily limits
MAX_COMMENTS_PER_DAY = 20
MAX_REPLIES_PER_DAY = 10

# ── Products ──────────────────────────────────────────────────────────────────
PRODUCTS = {
    "dictate": {
        "url": "https://dictate-app.pages.dev",
        "pitch": "voice dictation for Windows, Groq Whisper ~200ms, types at cursor",
        "subreddits": ["productivity", "windows", "indiedev", "windowsapps", "sideproject"],
        "keywords": [
            "voice dictation", "speech to text", "typing speed", "dictation software",
            "whisper", "transcription", "hands free typing", "talk to text",
            "faster than typing", "RSI", "wrist pain", "carpal tunnel"
        ],
    },
    "ecp": {
        "url": "https://howmindswork.org",
        "pitch": "emotional completion process for processing stuck feelings",
        "subreddits": ["spirituality", "selfimprovement", "mentalhealth", "meditation", "awakening"],
        "keywords": [
            "emotional release", "stuck emotions", "somatic", "inner child",
            "emotional healing", "trauma release", "emotional processing",
            "feel your feelings", "shadow work", "grief", "letting go"
        ],
    },
}

# ── Karma farming posts (non-promotional) ────────────────────────────────────
KARMA_POSTS = [
    {
        "subreddit": "Showerthoughts",
        "title": "the reason it's hard to apologize is that it requires you to briefly see yourself as the bad guy",
        "body": "",
    },
    {
        "subreddit": "LifeProTips",
        "title": "LPT: When you feel overwhelmed, write down every single thing in your head. The list is almost never as bad as the feeling.",
        "body": "Your brain treats unfinished thoughts like open browser tabs. Writing them down closes the tab. Even if you never look at the list again, the overwhelm usually drops significantly.",
    },
    {
        "subreddit": "Showerthoughts",
        "title": "the hardest part of learning something new isn't not knowing it, it's not knowing what you don't know",
        "body": "",
    },
    {
        "subreddit": "LifeProTips",
        "title": "LPT: If you're stuck on a decision, set a timer for 2 minutes and just decide. The quality of most small decisions doesn't matter nearly as much as the cost of staying stuck.",
        "body": "Indecision is its own choice. It just has worse odds.",
    },
    {
        "subreddit": "Showerthoughts",
        "title": "motivation gets you started but systems keep you going. most people have the motivation problem solved and the systems problem totally ignored",
        "body": "",
    },
    {
        "subreddit": "LifeProTips",
        "title": "LPT: Reply to emails and messages within 24 hours even if just to say you need more time. Silence reads as avoidance and creates more anxiety on both ends.",
        "body": "A 5 second \"got it, will get back to you by Thursday\" eliminates an entire category of social friction.",
    },
    {
        "subreddit": "Showerthoughts",
        "title": "people say they want honest feedback but what they usually want is enthusiastic validation with minor suggestions",
        "body": "",
    },
    {
        "subreddit": "selfimprovement",
        "title": "the thing nobody tells you about building habits: the streak doesn't matter. resuming after a break does.",
        "body": "I've reset my running streak 6 times in 2 years. I still run. The people who quit are the ones who decided breaking the streak meant the habit was over.\n\nMissing once is human. Deciding you've failed is optional.",
    },
    {
        "subreddit": "Showerthoughts",
        "title": "the version of you that doesn't want to do the hard thing and the version that's glad you did are both you, just at different times",
        "body": "",
    },
    {
        "subreddit": "productivity",
        "title": "what's one habit you built that made everything else easier?",
        "body": "Mine was writing down 3 things I need to do tomorrow before I close my laptop. Takes 2 minutes. My mornings stopped being chaotic.\n\ncurious what else people have found.",
    },
]

# ── Thread comment templates (AI fills the context) ──────────────────────────
COMMENT_PROMPT = """You are a real Reddit user named Mr1v4. Write a natural, helpful comment for this Reddit thread.

Thread title: {title}
Subreddit: r/{subreddit}
Top comment so far: {top_comment}

Product context (only mention if it fits VERY naturally, otherwise just be helpful):
{product_context}

Rules:
- Write like a real person, casual tone, no em dashes (use commas or periods instead)
- No bullet points unless the thread uses them
- Max 150 words
- If recommending the product, make it feel like a personal recommendation not an ad
- Include the URL only if it would genuinely help them
- Sometimes just be helpful with no product mention at all (especially for karma farming)
- No phrases like "I hope this helps", "great question", "as someone who"

Write ONLY the comment text, nothing else."""

# ── Helpers ───────────────────────────────────────────────────────────────────
def load_log():
    if LOG_FILE.exists():
        return json.loads(LOG_FILE.read_text())
    return {"comments_today": 0, "replies_today": 0, "last_reset": "", "commented_threads": [], "own_posts": {}}

def save_log(log):
    LOG_FILE.write_text(json.dumps(log, indent=2))

def reset_daily_if_needed(log):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if log.get("last_reset") != today:
        log["comments_today"] = 0
        log["replies_today"] = 0
        log["last_reset"] = today
    return log

def telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = json.dumps({"chat_id": TELEGRAM_CHAT, "text": msg, "disable_web_page_preview": True}).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass

def human_delay(lo=2.0, hi=6.0):
    time.sleep(random.uniform(lo, hi))

def get_reddit_session():
    """Build a requests-like session using saved cookies for JSON API reads."""
    import http.cookiejar
    cookies = json.loads(COOKIES_FILE.read_text())
    cookie_header = "; ".join(
        f"{c['name']}={c['value']}"
        for c in cookies if "reddit" in c.get("domain", "")
    )
    return cookie_header

def reddit_get(path, params=None, cookie_header=None):
    """GET from Reddit JSON API."""
    base = "https://www.reddit.com"
    url = base + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Accept": "application/json",
    }
    if cookie_header:
        headers["Cookie"] = cookie_header
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())

def ai_comment(title, subreddit, top_comment, product_context):
    """Generate a contextual comment using Claude."""
    if not ANTHROPIC_API_KEY:
        return None
    prompt = COMMENT_PROMPT.format(
        title=title, subreddit=subreddit,
        top_comment=top_comment[:300] if top_comment else "none yet",
        product_context=product_context
    )
    payload = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 300,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
        return result["content"][0]["text"].strip()

def post_comment(comment_text, comment_url):
    """Post a comment to a Reddit thread URL using Camoufox."""
    from camoufox.sync_api import Camoufox
    cookies = json.loads(COOKIES_FILE.read_text())

    with Camoufox(headless=True) as browser:
        ctx = browser.new_context()
        ctx.add_cookies(cookies)
        page = ctx.new_page()

        if comment_url:
            page.goto(comment_url, timeout=30000)
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        human_delay(2, 4)

        # Find comment box
        comment_box = page.locator('[data-testid="comment-submission-form-richtext"] div[role="textbox"], div[id*="comment"] div[role="textbox"]').first
        comment_box.wait_for(timeout=10000)
        comment_box.click()
        human_delay(0.5, 1.0)
        page.keyboard.type(comment_text, delay=15)
        human_delay(1, 2)

        # Submit
        submit_btn = page.locator('button:has-text("Comment"), button:has-text("Reply")').last
        submit_btn.click()
        human_delay(3, 5)
        return page.url

# ── Mode: scan threads and comment ───────────────────────────────────────────
def mode_scan():
    log = reset_daily_if_needed(load_log())

    if log["comments_today"] >= MAX_COMMENTS_PER_DAY:
        print(f"Comment limit reached ({MAX_COMMENTS_PER_DAY}/day). Skipping.")
        return

    cookie_header = get_reddit_session()
    commented = 0

    for product_key, product in PRODUCTS.items():
        if log["comments_today"] + commented >= MAX_COMMENTS_PER_DAY:
            break

        # Pick a random keyword and subreddit combo
        keyword = random.choice(product["keywords"])
        subreddit = random.choice(product["subreddits"])

        print(f"Scanning r/{subreddit} for '{keyword}'...")
        try:
            results = reddit_get(f"/r/{subreddit}/search.json", params={
                "q": keyword, "sort": "new", "t": "day", "restrict_sr": 1, "limit": 10
            }, cookie_header=cookie_header)
        except Exception as e:
            print(f"Search failed: {e}")
            continue

        posts = results.get("data", {}).get("children", [])
        random.shuffle(posts)

        for post_data in posts:
            p = post_data["data"]
            post_id = p["id"]
            post_url = f"https://www.reddit.com{p['permalink']}"

            # Skip already commented, stickied, locked, or very new
            if post_id in log["commented_threads"]:
                continue
            if p.get("stickied") or p.get("locked"):
                continue
            if p.get("num_comments", 0) > 500:
                continue  # too crowded, comment gets buried

            # Get top comment for context
            try:
                thread = reddit_get(f"{p['permalink']}.json", cookie_header=cookie_header)
                comments = thread[1]["data"]["children"]
                top_comment = ""
                for c in comments[:3]:
                    if c["kind"] == "t1":
                        top_comment = c["data"].get("body", "")
                        break
            except Exception:
                top_comment = ""

            # Generate comment
            product_context = f"Product: {product['url']} — {product['pitch']}"
            # 40% chance to not mention product at all (karma farming)
            if random.random() < 0.4:
                product_context = "No product mention — just be genuinely helpful"

            comment_text = ai_comment(p["title"], subreddit, top_comment, product_context)
            if not comment_text or len(comment_text) < 20:
                continue

            print(f"Commenting on: {p['title'][:60]}")
            print(f"Comment: {comment_text[:100]}...")

            try:
                post_comment(comment_text, post_url)
                log["commented_threads"].append(post_id)
                log["commented_threads"] = log["commented_threads"][-500:]  # keep last 500
                commented += 1
                save_log(log)
                print(f"Done. ({commented} comments this run)")
                human_delay(120, 300)  # 2-5 min between comments
                break
            except Exception as e:
                print(f"Comment failed: {e}")
            break  # one comment per product per scan run

    log["comments_today"] += commented
    save_log(log)
    print(f"Scan done. {commented} new comments. Daily total: {log['comments_today']}")

# ── Mode: reply to comments on own posts ─────────────────────────────────────
def mode_replies():
    log = reset_daily_if_needed(load_log())

    if log["replies_today"] >= MAX_REPLIES_PER_DAY:
        print("Reply limit reached. Skipping.")
        return

    cookie_header = get_reddit_session()

    try:
        # Get recent posts by Mr1v4
        submitted = reddit_get("/user/Mr1v4/submitted.json", params={"limit": 10}, cookie_header=cookie_header)
        posts = submitted["data"]["children"]
    except Exception as e:
        print(f"Could not fetch own posts: {e}")
        return

    replied = 0
    for post_data in posts:
        p = post_data["data"]
        post_id = p["id"]
        num_comments = p.get("num_comments", 0)

        if num_comments == 0:
            continue

        # Check which comments we've already replied to
        replied_to = log.get("own_posts", {}).get(post_id, [])

        try:
            thread = reddit_get(f"{p['permalink']}.json", params={"limit": 25}, cookie_header=cookie_header)
            comments = thread[1]["data"]["children"]
        except Exception:
            continue

        for c in comments:
            if c["kind"] != "t1":
                continue
            comment = c["data"]
            comment_id = comment["id"]
            author = comment.get("author", "")

            # Skip our own comments, already replied, deleted, AutoModerator
            if author in ("Mr1v4", "[deleted]", "AutoModerator"):
                continue
            if comment_id in replied_to:
                continue

            # Generate a reply
            reply_prompt = f"""A Reddit user replied to my post. Write a natural, brief reply.

My post title: {p['title']}
Their comment: {comment['body'][:400]}

Rules: casual, friendly, 1-3 sentences max, no em dashes, no "great question", no product pitching in replies (just be human)"""

            reply_text = ai_comment(p["title"], p["subreddit"], comment["body"], "No product pitch — just reply naturally as a person")

            if not reply_text:
                continue

            reply_url = f"https://www.reddit.com{p['permalink']}"
            print(f"Replying to u/{author}: {reply_text[:80]}...")

            try:
                post_comment(reply_text, reply_url)
                if post_id not in log["own_posts"]:
                    log["own_posts"][post_id] = []
                log["own_posts"][post_id].append(comment_id)
                replied += 1
                save_log(log)
                human_delay(60, 180)
                if replied + log["replies_today"] >= MAX_REPLIES_PER_DAY:
                    break
            except Exception as e:
                print(f"Reply failed: {e}")

        if replied + log["replies_today"] >= MAX_REPLIES_PER_DAY:
            break

    log["replies_today"] += replied
    save_log(log)
    print(f"Replies done. {replied} new. Daily total: {log['replies_today']}")

# ── Mode: karma farming post ──────────────────────────────────────────────────
def mode_karma():
    from camoufox.sync_api import Camoufox

    log = reset_daily_if_needed(load_log())
    cookies = json.loads(COOKIES_FILE.read_text())

    post = random.choice(KARMA_POSTS)
    print(f"Karma post → r/{post['subreddit']}: {post['title'][:60]}")

    with Camoufox(headless=True) as browser:
        ctx = browser.new_context()
        ctx.add_cookies(cookies)
        page = ctx.new_page()

        page.goto(f"https://www.reddit.com/r/{post['subreddit']}/submit", timeout=30000)
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        human_delay(3, 5)

        title_el = page.locator('textarea[name="title"]').first
        title_el.wait_for(timeout=10000)
        title_el.click()
        human_delay(0.3, 0.8)
        title_el.fill(post["title"])
        human_delay(1, 2)

        if post["body"]:
            body_el = page.locator('div[name="body"][role="textbox"]').first
            body_el.wait_for(timeout=10000)
            body_el.click()
            human_delay(0.5, 1.0)
            page.keyboard.type(post["body"], delay=12)
            human_delay(1, 2)

        page.locator('button:has-text("Post"), button:has-text("Request to Post")').last.click()
        try:
            page.wait_for_url("**created=**", timeout=20000)
        except Exception:
            human_delay(4, 6)

        post_url = page.url
        print(f"Karma post submitted: {post_url}")

        # Track this post for virality monitoring
        post_id_match = re.search(r'created=t3_([a-z0-9]+)', post_url)
        if post_id_match:
            post_id = post_id_match.group(1)
            log["own_posts"][post_id] = []
            log["own_posts"][f"{post_id}_sub"] = post["subreddit"]
            log["own_posts"][f"{post_id}_time"] = datetime.now(timezone.utc).isoformat()
            save_log(log)

# ── Mode: virality monitor ────────────────────────────────────────────────────
def mode_monitor():
    cookie_header = get_reddit_session()
    log = load_log()

    try:
        submitted = reddit_get("/user/Mr1v4/submitted.json", params={"limit": 5}, cookie_header=cookie_header)
        posts = submitted["data"]["children"]
    except Exception as e:
        print(f"Could not fetch posts: {e}")
        return

    for post_data in posts:
        p = post_data["data"]
        created = datetime.fromtimestamp(p["created_utc"], tz=timezone.utc)
        age_minutes = (datetime.now(timezone.utc) - created).total_seconds() / 60

        # Only monitor posts less than 6 hours old
        if age_minutes > 360:
            continue

        score = p.get("score", 0)
        num_comments = p.get("num_comments", 0)
        upvote_ratio = p.get("upvote_ratio", 0)
        title = p["title"]
        post_url = f"https://www.reddit.com{p['permalink']}"

        alert_key = f"alerted_{p['id']}"
        already_alerted = log.get(alert_key, False)

        # Blowing up thresholds
        blowing_up = (
            (age_minutes <= 30 and score >= ALERT_UPVOTES_30MIN) or
            (age_minutes <= 60 and num_comments >= ALERT_COMMENTS_1HR) or
            (score >= 200)
        )

        if blowing_up and not already_alerted:
            msg = (
                f"Reddit post blowing up! 🔥\n"
                f"r/{p['subreddit']} | {age_minutes:.0f} min old\n"
                f"↑{score} ({upvote_ratio*100:.0f}%) | {num_comments} comments\n"
                f'"{title[:80]}"\n'
                f"{post_url}"
            )
            telegram(msg)
            print(msg)
            log[alert_key] = True
            save_log(log)
        else:
            print(f"r/{p['subreddit']} | ↑{score} | {num_comments} comments | {age_minutes:.0f} min old")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not COOKIES_FILE.exists():
        print("ERROR: No session found. Run reddit_login_setup.py first.")
        sys.exit(1)

    mode = sys.argv[1] if len(sys.argv) > 1 else "--scan"

    if mode == "--scan":
        mode_scan()
    elif mode == "--replies":
        mode_replies()
    elif mode == "--karma":
        mode_karma()
    elif mode == "--monitor":
        mode_monitor()
    else:
        print(f"Unknown mode: {mode}")
        print("Usage: python3 reddit_engage.py [--scan|--replies|--karma|--monitor]")
        sys.exit(1)
