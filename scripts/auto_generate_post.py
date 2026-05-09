#!/usr/bin/env python3
"""
auto_generate_post.py
Reads the first topic from blog/topics-queue.txt, calls the Anthropic API
to generate a complete HTML blog post, saves it to blog/, removes the used
topic from the queue, and regenerates blog/index.html.

Environment variables required:
  ANTHROPIC_API_KEY — Anthropic API key

Usage:
  python3 scripts/auto_generate_post.py
"""

import os
import re
import sys
import json
import glob
from datetime import date
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)

SITE_URL = "https://dictate-app.pages.dev"
BLOG_DIR = Path(__file__).parent.parent / "blog"
QUEUE_FILE = BLOG_DIR / "topics-queue.txt"
TODAY = date.today().strftime("%Y-%m-%d")

SYSTEM_PROMPT = f"""You are an SEO content writer for TechTips, an independent tech advice blog covering AI tools, productivity apps, Windows tips, and software comparisons.

TechTips is NOT affiliated with any single product. It covers broad tech topics. When a topic is relevant to voice dictation, you may recommend dictate.app (offline, private, $9/mo, Groq Whisper) as one option among others — naturally, not forced.

Key facts to use when relevant:
- dictate.app: offline voice-to-text for Windows, Groq Whisper, $9/mo, 7-day free trial, 30-day refund, 70+ languages, ~150 WPM, custom hotkey, no cloud
- Competitors: Wispr Flow (cloud, Mac-only), Dragon ($150+), Otter.ai (cloud), Windows built-in (limited)
- CTA URL for dictate.app: {SITE_URL}

Writing tone rules:
- Short sentences. Direct. No corporate fluff.
- Use facts and numbers wherever possible.
- Independent reviewer voice — not a company blog.
- Privacy and offline angle matters for voice/data topics.
- 2026 in all dates. Never 2025.
- No green anywhere in design. Purple (#c084fc) and rose (#f472b6) only.

Design system (CSS variables):
  --bg: #0d0a14
  --bg-accent: #1a1625
  --text-primary: #e8dff5
  --text-secondary: #c4b8d4
  --accent: #c084fc
  --accent-rose: #f472b6
"""

TEMPLATE_CSS = """
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html { scroll-behavior: smooth; }
      :root {
        --bg: #0d0a14; --bg-accent: #1a1625;
        --text-primary: #e8dff5; --text-secondary: #c4b8d4;
        --accent: #c084fc; --accent-rose: #f472b6;
      }
      body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: var(--bg); color: var(--text-primary);
        line-height: 1.8; overflow-x: hidden;
      }
      canvas#starfield { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; pointer-events: none; }
      .wrap { position: relative; z-index: 1; }
      header {
        padding: 20px 32px; backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(192,132,252,0.1);
        position: sticky; top: 0; z-index: 100; background: rgba(13,10,20,0.85);
      }
      nav { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
      .nav-home { color: var(--text-secondary); text-decoration: none; font-size: 14px; transition: color 0.2s; display: flex; align-items: center; gap: 6px; }
      .nav-home:hover { color: var(--accent); }
      .logo-icon { width: 26px; height: 26px; border-radius: 6px; background: linear-gradient(135deg, #c084fc 0%, #f472b6 100%); display: inline-flex; align-items: center; justify-content: center; font-size: 14px; margin-right: 4px; }
      .cta-nav { display: inline-block; padding: 10px 24px; background: linear-gradient(135deg, var(--accent) 0%, var(--accent-rose) 100%); color: white; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600; transition: all 0.2s; box-shadow: 0 4px 14px rgba(192,132,252,0.3); }
      .cta-nav:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(192,132,252,0.5); }
      article { max-width: 760px; margin: 60px auto; padding: 0 24px 80px; }
      .post-label { display: inline-block; background: rgba(192,132,252,0.15); border: 1px solid rgba(192,132,252,0.3); color: var(--accent); font-size: 12px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 4px 12px; border-radius: 20px; margin-bottom: 20px; }
      h1 { font-size: clamp(28px, 5vw, 42px); font-weight: 700; line-height: 1.2; margin-bottom: 16px; }
      .post-meta { font-size: 13px; color: var(--text-secondary); margin-bottom: 40px; padding-bottom: 24px; border-bottom: 1px solid rgba(192,132,252,0.1); }
      h2 { font-size: 22px; font-weight: 700; color: var(--accent); margin: 36px 0 14px; }
      h3 { font-size: 18px; font-weight: 600; color: var(--text-primary); margin: 24px 0 10px; }
      p { margin-bottom: 18px; color: var(--text-secondary); font-size: 16px; }
      p strong { color: var(--text-primary); }
      ul, ol { padding-left: 24px; margin-bottom: 18px; }
      li { color: var(--text-secondary); font-size: 16px; margin-bottom: 6px; }
      li strong { color: var(--text-primary); }
      .table-wrap { overflow-x: auto; margin: 28px 0; }
      table { width: 100%; border-collapse: collapse; font-size: 14px; }
      th { background: rgba(192,132,252,0.15); color: var(--accent); font-weight: 700; text-align: left; padding: 12px 16px; border: 1px solid rgba(192,132,252,0.2); }
      td { padding: 10px 16px; border: 1px solid rgba(192,132,252,0.1); color: var(--text-secondary); }
      tr:nth-child(even) td { background: rgba(255,255,255,0.02); }
      .check { color: var(--accent); font-weight: 700; }
      .cross { color: var(--accent-rose); }
      .win { color: var(--accent); font-weight: 700; }
      .cta-block { background: linear-gradient(135deg, rgba(192,132,252,0.1) 0%, rgba(244,114,182,0.08) 100%); border: 1px solid rgba(192,132,252,0.25); border-radius: 12px; padding: 36px 32px; text-align: center; margin: 48px 0; }
      .cta-block h2 { margin: 0 0 10px; font-size: 22px; color: var(--text-primary); }
      .cta-block p { margin: 0 0 24px; }
      .cta-big { display: inline-block; padding: 14px 36px; background: linear-gradient(135deg, var(--accent) 0%, var(--accent-rose) 100%); color: white; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 700; transition: all 0.2s; box-shadow: 0 6px 20px rgba(192,132,252,0.35); }
      .cta-big:hover { transform: translateY(-2px); box-shadow: 0 10px 28px rgba(192,132,252,0.5); }
      .cta-sub { margin-top: 12px; font-size: 13px; color: var(--text-secondary); }
      footer { border-top: 1px solid rgba(192,132,252,0.1); padding: 32px; text-align: center; color: var(--text-secondary); font-size: 13px; }
      footer a { color: var(--accent); text-decoration: none; }
      @media (max-width: 600px) { article { padding: 0 16px 60px; } header { padding: 16px 20px; } .cta-block { padding: 24px 20px; } }
    </style>
"""

STARFIELD_JS = """
    <canvas id="starfield"></canvas>
    <script>
      const canvas = document.getElementById("starfield");
      const ctx = canvas.getContext("2d");
      function resizeCanvas() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
      resizeCanvas();
      window.addEventListener("resize", resizeCanvas);
      const stars = [];
      for (let i = 0; i < 50; i++) {
        stars.push({ x: Math.random()*canvas.width, y: Math.random()*canvas.height, radius: Math.random()*1.2, opacity: Math.random()*0.5+0.4, vx: (Math.random()-0.5)*0.08, vy: (Math.random()-0.5)*0.08 });
      }
      function drawStarfield() {
        ctx.fillStyle = "rgba(13,10,20,0.1)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        stars.forEach(s => {
          s.x += s.vx; s.y += s.vy;
          if (s.x < 0) s.x = canvas.width;
          if (s.x > canvas.width) s.x = 0;
          if (s.y < 0) s.y = canvas.height;
          if (s.y > canvas.height) s.y = 0;
          ctx.fillStyle = `rgba(192,132,252,${s.opacity})`;
          ctx.beginPath();
          ctx.arc(s.x, s.y, s.radius, 0, Math.PI * 2);
          ctx.fill();
        });
        requestAnimationFrame(drawStarfield);
      }
      drawStarfield();
    </script>
"""


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    text = re.sub(r"-+", "-", text)
    return text[:80]


def read_queue() -> list[str]:
    if not QUEUE_FILE.exists():
        return []
    lines = QUEUE_FILE.read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in lines if l.strip()]


def pop_topic() -> str | None:
    topics = read_queue()
    if not topics:
        return None
    topic = topics[0]
    remaining = topics[1:]
    QUEUE_FILE.write_text("\n".join(remaining) + ("\n" if remaining else ""), encoding="utf-8")
    return topic


def wrap_in_shell(slug: str, title: str, description: str, keywords: str, body_html: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} | TechTips</title>
  <meta name="description" content="{description}" />
  <meta name="keywords" content="{keywords}" />
  <meta name="author" content="TechTips" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{SITE_URL}/blog/{slug}.html" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{description}" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="{SITE_URL}/blog/{slug}.html" />
  <meta property="og:site_name" content="TechTips" />
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "{title}",
    "description": "{description}",
    "author": {{"@type": "Organization", "name": "TechTips"}},
    "publisher": {{"@type": "Organization", "name": "TechTips"}},
    "datePublished": "{TODAY}",
    "dateModified": "{TODAY}",
    "url": "{SITE_URL}/blog/{slug}.html"
  }}
  </script>
{TEMPLATE_CSS}
</head>
<body>
  <div class="wrap">
    <header>
      <nav>
        <a class="nav-home" href="{SITE_URL}/blog/">
          <span class="logo-icon">💡</span> TechTips
        </a>
        <a class="cta-nav" href="{SITE_URL}">Try dictate.app →</a>
      </nav>
    </header>
    <article>
{body_html}
      <div class="cta-block">
        <h2>Ready to dictate?</h2>
        <p>7-day free trial. Works in any text field. No credit card required.</p>
        <a class="cta-big" href="{SITE_URL}">Start Free Trial →</a>
        <p class="cta-sub">30-day refund guarantee. $9/mo after trial.</p>
      </div>
    </article>
    <footer>
      <p>© 2026 TechTips &nbsp;·&nbsp; Independent tech advice &nbsp;·&nbsp; <a href="{SITE_URL}/blog/">More articles</a></p>
    </footer>
  </div>
{STARFIELD_JS}
</body>
</html>"""


def generate_body(topic: str) -> dict:
    """Call Claude API and get back JSON with title, description, keywords, slug, body_html."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = f"""Write a complete SEO blog post for dictate.app on this topic: "{topic}"

Return a JSON object with these exact keys:
- title: SEO-optimized H1 title (under 65 chars)
- description: Meta description (150–160 chars)
- keywords: comma-separated target keywords (3–5)
- slug: URL slug, lowercase hyphenated (no .html)
- body_html: the full article HTML body

For body_html, use only these HTML elements:
- <span class="post-label">Category</span> at the very top
- <h1>{{title}}</h1>
- <p class="post-meta">TechTips &nbsp;·&nbsp; {TODAY[:7].replace('-', ' ')} 2026 &nbsp;·&nbsp; X min read</p>
- <h2>, <h3>, <p>, <ul>, <li>, <ol>, <strong>
- <div class="table-wrap"><table><tr><th>/<td> with class="check", "cross", or "win" as needed
- No inline styles. No other HTML elements.

Article requirements:
- 600–900 words
- Target keyword in H1, first paragraph, at least one H2
- Privacy/offline angle included
- At least one concrete number (price, WPM, time, etc.)
- Short sentences. No filler phrases.
- All dates say 2026
- CTA link must be: {SITE_URL}
- No green colors referenced anywhere

Return ONLY valid JSON, no markdown fences."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt, "cache_control": {"type": "ephemeral"}}]}],
        extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"},
    )

    raw = message.content[0].text.strip()
    # Strip markdown code fences if present
    raw = re.sub(r"^```(?:json)?\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)

    return json.loads(raw)


def scan_existing_posts() -> list[dict]:
    """Scan blog/ for HTML files and extract title+description from meta tags."""
    posts = []
    pattern = str(BLOG_DIR / "*.html")
    for path in sorted(glob.glob(pattern)):
        fname = os.path.basename(path)
        if fname == "index.html":
            continue
        content = open(path, encoding="utf-8").read()
        title_m = re.search(r"<title>(.*?)\s*\|", content)
        desc_m = re.search(r'<meta name="description" content="(.*?)"', content)
        slug = fname.replace(".html", "")
        if title_m and desc_m:
            posts.append({
                "slug": slug,
                "title": title_m.group(1).strip(),
                "desc": desc_m.group(1).strip(),
            })
    return posts


def rebuild_index(posts: list[dict]):
    card_html = ""
    for c in posts:
        card_html += f"""
        <a class="card" href="{SITE_URL}/blog/{c['slug']}.html">
          <h2>{c['title']}</h2>
          <p>{c['desc']}</p>
          <span class="read-more">Read →</span>
        </a>"""

    index_html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>TechTips — AI Tools, Software Picks &amp; Tech Advice</title>
  <meta name="description" content="AI tools, software comparisons, Windows tips, and tech advice for getting more done. Independent reviews and guides." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{SITE_URL}/blog/" />
  <style>
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    :root {{ --bg:#0d0a14; --text-primary:#e8dff5; --text-secondary:#c4b8d4; --accent:#c084fc; --accent-rose:#f472b6; }}
    body {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:var(--bg); color:var(--text-primary); line-height:1.7; overflow-x:hidden; }}
    canvas#starfield {{ position:fixed; top:0; left:0; width:100%; height:100%; z-index:-1; pointer-events:none; }}
    .wrap {{ position:relative; z-index:1; }}
    header {{ padding:20px 32px; backdrop-filter:blur(10px); border-bottom:1px solid rgba(192,132,252,0.1); position:sticky; top:0; z-index:100; background:rgba(13,10,20,0.85); }}
    nav {{ max-width:1200px; margin:0 auto; display:flex; justify-content:space-between; align-items:center; }}
    .nav-home {{ color:var(--text-secondary); text-decoration:none; font-size:14px; display:flex; align-items:center; gap:6px; }}
    .nav-home:hover {{ color:var(--accent); }}
    .logo-icon {{ width:26px; height:26px; border-radius:6px; background:linear-gradient(135deg,#c084fc 0%,#f472b6 100%); display:inline-flex; align-items:center; justify-content:center; font-size:14px; margin-right:4px; }}
    .cta-nav {{ display:inline-block; padding:10px 24px; background:linear-gradient(135deg,var(--accent) 0%,var(--accent-rose) 100%); color:white; text-decoration:none; border-radius:6px; font-size:14px; font-weight:600; }}
    .hero {{ text-align:center; padding:80px 24px 40px; }}
    .hero h1 {{ font-size:clamp(28px,5vw,44px); font-weight:700; margin-bottom:12px; }}
    .hero p {{ color:var(--text-secondary); font-size:16px; }}
    .grid {{ max-width:1100px; margin:0 auto; padding:0 24px 80px; display:grid; grid-template-columns:repeat(3,1fr); gap:24px; }}
    .card {{ background:rgba(255,255,255,0.03); border:1px solid rgba(192,132,252,0.15); border-radius:12px; padding:28px 24px; text-decoration:none; display:block; transition:all 0.2s; color:var(--text-primary); }}
    .card:hover {{ border-color:rgba(192,132,252,0.4); background:rgba(192,132,252,0.05); transform:translateY(-3px); box-shadow:0 8px 24px rgba(192,132,252,0.15); }}
    .card h2 {{ font-size:17px; font-weight:700; color:var(--text-primary); margin-bottom:10px; line-height:1.3; }}
    .card p {{ font-size:14px; color:var(--text-secondary); margin-bottom:16px; line-height:1.6; }}
    .read-more {{ font-size:14px; color:var(--accent); font-weight:600; }}
    footer {{ border-top:1px solid rgba(192,132,252,0.1); padding:32px; text-align:center; color:var(--text-secondary); font-size:13px; }}
    footer a {{ color:var(--accent); text-decoration:none; }}
    @media (max-width:900px) {{ .grid {{ grid-template-columns:repeat(2,1fr); }} }}
    @media (max-width:580px) {{ .grid {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <nav>
        <a class="nav-home" href="{SITE_URL}/blog/"><span class="logo-icon">💡</span> TechTips</a>
        <a class="cta-nav" href="{SITE_URL}">Try dictate.app →</a>
      </nav>
    </header>
    <div class="hero">
      <h1>Tech Tips &amp; Guides</h1>
      <p>AI tools, software picks, and tech advice for getting more done.</p>
    </div>
    <div class="grid">
{card_html}
    </div>
    <footer>
      <p>© 2026 TechTips &nbsp;·&nbsp; Independent tech advice &nbsp;·&nbsp; <a href="{SITE_URL}/blog/">More articles</a></p>
    </footer>
  </div>
  <canvas id="starfield"></canvas>
  <script>
    const canvas=document.getElementById("starfield"),ctx=canvas.getContext("2d");
    function resizeCanvas(){{canvas.width=window.innerWidth;canvas.height=window.innerHeight;}}
    resizeCanvas();window.addEventListener("resize",resizeCanvas);
    const stars=[];
    for(let i=0;i<50;i++)stars.push({{x:Math.random()*canvas.width,y:Math.random()*canvas.height,radius:Math.random()*1.2,opacity:Math.random()*0.5+0.4,vx:(Math.random()-0.5)*0.08,vy:(Math.random()-0.5)*0.08}});
    function draw(){{
      ctx.fillStyle="rgba(13,10,20,0.1)";ctx.fillRect(0,0,canvas.width,canvas.height);
      stars.forEach(s=>{{s.x+=s.vx;s.y+=s.vy;if(s.x<0)s.x=canvas.width;if(s.x>canvas.width)s.x=0;if(s.y<0)s.y=canvas.height;if(s.y>canvas.height)s.y=0;ctx.fillStyle=`rgba(192,132,252,${{s.opacity}})`;ctx.beginPath();ctx.arc(s.x,s.y,s.radius,0,Math.PI*2);ctx.fill();}});
      requestAnimationFrame(draw);
    }}
    draw();
  </script>
</body>
</html>"""

    out_path = BLOG_DIR / "index.html"
    out_path.write_text(index_html, encoding="utf-8")
    print(f"  Rebuilt: blog/index.html ({len(posts)} posts)")


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set.")
        sys.exit(1)

    topic = pop_topic()
    if not topic:
        print("Queue is empty. Add more topics to blog/topics-queue.txt")
        sys.exit(0)

    print(f"Topic: {topic}")

    try:
        data = generate_body(topic)
    except json.JSONDecodeError as e:
        print(f"ERROR: API returned invalid JSON: {e}")
        sys.exit(1)

    slug = data.get("slug") or slugify(topic)
    title = data["title"]
    description = data["description"]
    keywords = data.get("keywords", "")
    body_html = data["body_html"]

    # Ensure CTA link is correct
    body_html = body_html.replace("https://dictate.app", SITE_URL)

    out_path = BLOG_DIR / f"{slug}.html"
    full_html = wrap_in_shell(slug, title, description, keywords, body_html)
    out_path.write_text(full_html, encoding="utf-8")
    print(f"  Wrote: blog/{slug}.html")

    # Rebuild index
    posts = scan_existing_posts()
    rebuild_index(posts)

    print(f"Done. Slug: {slug}")
    # Output slug for use in CI (commit message etc.)
    print(f"GENERATED_SLUG={slug}")


if __name__ == "__main__":
    main()
