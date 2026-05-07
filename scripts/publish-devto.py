#!/usr/bin/env python3
"""Publish dev.to articles from devto-articles.md"""

import re
import time
import requests

def load_api_key():
    import os
    with open(os.path.expanduser("~/.claude_secrets")) as f:
        for line in f:
            line = line.strip()
            if line.startswith("DEVTO_API_KEY"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise ValueError("DEVTO_API_KEY not found in ~/.claude_secrets")

def parse_articles(path="scripts/devto-articles.md"):
    with open(path) as f:
        content = f.read()

    raw_blocks = re.split(r"---\nARTICLE_SEPARATOR\n---", content)
    articles = []

    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue

        # Extract frontmatter from code fence
        fm_match = re.search(r"```\n(---\n.*?---)\n```", block, re.DOTALL)
        if not fm_match:
            continue

        frontmatter = fm_match.group(1)
        body = block[fm_match.end():].strip()

        title_m = re.search(r"^title:\s*(.+)$", frontmatter, re.MULTILINE)
        desc_m = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
        tags_m = re.search(r"^tags:\s*(.+)$", frontmatter, re.MULTILINE)

        if not title_m:
            continue

        tags = [t.strip() for t in tags_m.group(1).split(",")] if tags_m else []

        articles.append({
            "title": title_m.group(1).strip(),
            "description": desc_m.group(1).strip() if desc_m else "",
            "tags": tags,
            "body_markdown": body,
            "published": True,
        })

    return articles

def publish_article(api_key, article):
    resp = requests.post(
        "https://dev.to/api/articles",
        headers={
            "api-key": api_key,
            "Content-Type": "application/json",
        },
        json={"article": article},
    )
    resp.raise_for_status()
    return resp.json()

def main():
    api_key = load_api_key()
    articles = parse_articles()
    print(f"Found {len(articles)} articles to publish\n")

    for i, article in enumerate(articles, 1):
        print(f"[{i}/{len(articles)}] Publishing: {article['title']}")
        try:
            result = publish_article(api_key, article)
            print(f"  Published: {result.get('url', 'no URL returned')}")
        except requests.HTTPError as e:
            print(f"  Error: {e.response.status_code} {e.response.text[:200]}")

        if i < len(articles):
            print("  Waiting 10 seconds...")
            time.sleep(10)

    print("\nDone.")

if __name__ == "__main__":
    main()
