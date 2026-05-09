#!/usr/bin/env python3
"""
Daily AI/voice/dictation news alert → Telegram.
Scans Reddit + HN for relevant trending content.
Sends only if something worth noting is found.
"""
import os, json, urllib.request, urllib.parse, time, datetime

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

KEYWORDS = ["whisper", "dictation", "voice typing", "speech recognition",
            "groq", "transcription", "dragon naturally", "wispr", "voice dictation",
            "push to talk", "openai whisper", "voice to text", "speech to text"]

COMPETITOR_KEYWORDS = ["omnidictate", "voquill", "heynds", "speechpulse",
                       "wispr flow", "superwhisper", "voicetypr"]

SUBREDDITS = ["productivity", "windows", "speechrecognition", "indiedev", "windowsapps"]

def fetch(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "dictate-alert-bot/1.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def scan_reddit():
    hits = []
    for sub in SUBREDDITS:
        try:
            data = fetch(f"https://www.reddit.com/r/{sub}/top.json?t=day&limit=10")
            for post in data["data"]["children"]:
                p = post["data"]
                title = p.get("title", "").lower()
                if any(k in title for k in KEYWORDS):
                    is_competitor = any(c in title for c in COMPETITOR_KEYWORDS)
                    hits.append({
                        "sub": sub,
                        "title": p["title"],
                        "score": p.get("score", 0),
                        "url": "https://reddit.com" + p.get("permalink", ""),
                        "competitor": is_competitor,
                    })
            time.sleep(1)
        except Exception as e:
            print(f"Reddit {sub} error: {e}")
    return sorted(hits, key=lambda x: x["score"], reverse=True)[:5]

def scan_hn():
    hits = []
    yesterday = int(time.time()) - 86400
    for q in ["voice dictation windows", "whisper speech", "groq whisper"]:
        try:
            url = (f"https://hn.algolia.com/api/v1/search?query={urllib.parse.quote(q)}"
                   f"&tags=story&hitsPerPage=3&numericFilters=created_at_i>{yesterday}")
            data = fetch(url)
            for h in data.get("hits", []):
                title = h.get("title", "").lower()
                if any(k in title for k in KEYWORDS + COMPETITOR_KEYWORDS):
                    is_competitor = any(c in title for c in COMPETITOR_KEYWORDS)
                    hits.append({
                        "title": h["title"],
                        "points": h.get("points", 0),
                        "url": f"https://news.ycombinator.com/item?id={h['objectID']}",
                        "competitor": is_competitor,
                    })
        except Exception as e:
            print(f"HN error: {e}")
    seen = set()
    deduped = []
    for h in hits:
        if h["url"] not in seen:
            seen.add(h["url"])
            deduped.append(h)
    return deduped[:3]

def build_message(reddit_hits, hn_hits):
    today = datetime.date.today().strftime("%b %d")
    lines = [f"🔍 *Dictate App Intel — {today}*\n"]

    if reddit_hits:
        lines.append("📱 *Reddit Today:*")
        for h in reddit_hits:
            tag = "🔴 THREAT" if h["competitor"] else "✅ OPPORTUNITY"
            lines.append(f"• [r/{h['sub']}] {h['title']} — {h['score']} upvotes")
            lines.append(f"  → {tag}")
        lines.append("")

    if hn_hits:
        lines.append("🟠 *Hacker News:*")
        for h in hn_hits:
            tag = "🔴 THREAT" if h["competitor"] else "✅ OPPORTUNITY"
            lines.append(f"• {h['title']} — {h['points']} pts")
            lines.append(f"  → {tag}: {h['url']}")
        lines.append("")

    # Recommendation
    has_threat = any(h.get("competitor") for h in reddit_hits + hn_hits)
    top_sub = reddit_hits[0]["sub"] if reddit_hits else None

    if has_threat:
        lines.append("💡 *Action:* Competitor activity detected — consider posting your angle today.")
    elif top_sub:
        lines.append(f"💡 *Action:* Voice/dictation trending on r/{top_sub} — good time to post.")

    return "\n".join(lines)

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }).encode()
    req = urllib.request.Request(url, data=payload,
                                  headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        resp = json.loads(r.read())
    return resp.get("ok")

def main():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        return

    print("Scanning Reddit...")
    reddit_hits = scan_reddit()
    print(f"  Found {len(reddit_hits)} relevant posts")

    print("Scanning HN...")
    hn_hits = scan_hn()
    print(f"  Found {len(hn_hits)} relevant stories")

    if not reddit_hits and not hn_hits:
        print("Nothing relevant today — skipping Telegram.")
        return

    msg = build_message(reddit_hits, hn_hits)
    print("Sending Telegram...")
    ok = send_telegram(msg)
    print("Sent!" if ok else "Failed to send")

if __name__ == "__main__":
    main()
