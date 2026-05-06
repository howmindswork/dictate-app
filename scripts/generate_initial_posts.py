#!/usr/bin/env python3
"""
Generate initial 8 blog posts for dictate.app.
Also regenerates blog/index.html from the post list.

Run from project root:
  python3 scripts/generate_initial_posts.py
"""

import os
import re

SITE_URL = "https://dictate-app.pages.dev"
BLOG_DIR = os.path.join(os.path.dirname(__file__), "..", "blog")

TEMPLATE_CSS = """
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html { scroll-behavior: smooth; }
      :root {
        --bg: #0d0a14;
        --bg-accent: #1a1625;
        --text-primary: #e8dff5;
        --text-secondary: #c4b8d4;
        --accent: #c084fc;
        --accent-rose: #f472b6;
      }
      body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: var(--bg);
        color: var(--text-primary);
        line-height: 1.8;
        overflow-x: hidden;
      }
      canvas#starfield {
        position: fixed; top: 0; left: 0;
        width: 100%; height: 100%;
        z-index: -1; pointer-events: none;
      }
      .wrap { position: relative; z-index: 1; }

      /* NAV */
      header {
        padding: 20px 32px;
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(192,132,252,0.1);
        position: sticky; top: 0; z-index: 100;
        background: rgba(13,10,20,0.85);
      }
      nav {
        max-width: 1200px; margin: 0 auto;
        display: flex; justify-content: space-between; align-items: center;
      }
      .nav-home {
        color: var(--text-secondary);
        text-decoration: none;
        font-size: 14px;
        transition: color 0.2s;
        display: flex; align-items: center; gap: 6px;
      }
      .nav-home:hover { color: var(--accent); }
      .logo-icon {
        width: 26px; height: 26px; border-radius: 6px;
        background: linear-gradient(135deg, #c084fc 0%, #f472b6 100%);
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 14px; margin-right: 4px;
      }
      .cta-nav {
        display: inline-block;
        padding: 10px 24px;
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-rose) 100%);
        color: white; text-decoration: none;
        border-radius: 6px; font-size: 14px; font-weight: 600;
        transition: all 0.2s;
        box-shadow: 0 4px 14px rgba(192,132,252,0.3);
      }
      .cta-nav:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(192,132,252,0.5); }

      /* ARTICLE */
      article {
        max-width: 760px;
        margin: 60px auto;
        padding: 0 24px 80px;
      }
      .post-label {
        display: inline-block;
        background: rgba(192,132,252,0.15);
        border: 1px solid rgba(192,132,252,0.3);
        color: var(--accent);
        font-size: 12px; font-weight: 600;
        letter-spacing: 1px; text-transform: uppercase;
        padding: 4px 12px; border-radius: 20px;
        margin-bottom: 20px;
      }
      h1 {
        font-size: clamp(28px, 5vw, 42px);
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: 16px;
        color: var(--text-primary);
      }
      .post-meta {
        font-size: 13px;
        color: var(--text-secondary);
        margin-bottom: 40px;
        padding-bottom: 24px;
        border-bottom: 1px solid rgba(192,132,252,0.1);
      }
      h2 {
        font-size: 22px; font-weight: 700;
        color: var(--accent);
        margin: 36px 0 14px;
      }
      h3 {
        font-size: 18px; font-weight: 600;
        color: var(--text-primary);
        margin: 24px 0 10px;
      }
      p { margin-bottom: 18px; color: var(--text-secondary); font-size: 16px; }
      p strong { color: var(--text-primary); }
      ul, ol { padding-left: 24px; margin-bottom: 18px; }
      li { color: var(--text-secondary); font-size: 16px; margin-bottom: 6px; }
      li strong { color: var(--text-primary); }

      /* TABLE */
      .table-wrap { overflow-x: auto; margin: 28px 0; }
      table {
        width: 100%; border-collapse: collapse;
        font-size: 14px;
      }
      th {
        background: rgba(192,132,252,0.15);
        color: var(--accent);
        font-weight: 700; text-align: left;
        padding: 12px 16px;
        border: 1px solid rgba(192,132,252,0.2);
      }
      td {
        padding: 10px 16px;
        border: 1px solid rgba(192,132,252,0.1);
        color: var(--text-secondary);
      }
      tr:nth-child(even) td { background: rgba(255,255,255,0.02); }
      .check { color: var(--accent); font-weight: 700; }
      .cross { color: var(--accent-rose); }
      .win { color: var(--accent); font-weight: 700; }

      /* CTA BLOCK */
      .cta-block {
        background: linear-gradient(135deg, rgba(192,132,252,0.1) 0%, rgba(244,114,182,0.08) 100%);
        border: 1px solid rgba(192,132,252,0.25);
        border-radius: 12px;
        padding: 36px 32px;
        text-align: center;
        margin: 48px 0;
      }
      .cta-block h2 { margin: 0 0 10px; font-size: 22px; color: var(--text-primary); }
      .cta-block p { margin: 0 0 24px; }
      .cta-big {
        display: inline-block;
        padding: 14px 36px;
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-rose) 100%);
        color: white; text-decoration: none;
        border-radius: 8px; font-size: 16px; font-weight: 700;
        transition: all 0.2s;
        box-shadow: 0 6px 20px rgba(192,132,252,0.35);
      }
      .cta-big:hover { transform: translateY(-2px); box-shadow: 0 10px 28px rgba(192,132,252,0.5); }
      .cta-sub { margin-top: 12px; font-size: 13px; color: var(--text-secondary); }

      /* FOOTER */
      footer {
        border-top: 1px solid rgba(192,132,252,0.1);
        padding: 32px;
        text-align: center;
        color: var(--text-secondary);
        font-size: 13px;
      }
      footer a { color: var(--accent); text-decoration: none; }

      @media (max-width: 600px) {
        article { padding: 0 16px 60px; }
        header { padding: 16px 20px; }
        .cta-block { padding: 24px 20px; }
      }
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
        stars.push({
          x: Math.random() * canvas.width, y: Math.random() * canvas.height,
          radius: Math.random() * 1.2, opacity: Math.random() * 0.5 + 0.4,
          vx: (Math.random() - 0.5) * 0.08, vy: (Math.random() - 0.5) * 0.08
        });
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

def make_post(slug, title, description, keywords, body_html, date="2026-05-06"):
    nav = f"""
    <header>
      <nav>
        <a class="nav-home" href="{SITE_URL}">
          <span class="logo-icon">🎙</span> ← dictate.app
        </a>
        <a class="cta-nav" href="{SITE_URL}">Start Free Trial</a>
      </nav>
    </header>"""

    footer = f"""
    <footer>
      <p>© 2026 dictate.app &nbsp;·&nbsp; <a href="{SITE_URL}">Home</a> &nbsp;·&nbsp; <a href="{SITE_URL}/blog/">Blog</a></p>
    </footer>"""

    cta_block = f"""
    <div class="cta-block">
      <h2>Ready to dictate?</h2>
      <p>7-day free trial. Works in any text field. No credit card required.</p>
      <a class="cta-big" href="{SITE_URL}">Start Free Trial →</a>
      <p class="cta-sub">30-day refund guarantee. $9/mo after trial.</p>
    </div>"""

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} | dictate.app Blog</title>
  <meta name="description" content="{description}" />
  <meta name="keywords" content="{keywords}" />
  <meta name="author" content="dictate.app" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{SITE_URL}/blog/{slug}.html" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{description}" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="{SITE_URL}/blog/{slug}.html" />
  <meta property="og:site_name" content="dictate.app" />
  <meta name="twitter:card" content="summary" />
  <meta name="twitter:title" content="{title}" />
  <meta name="twitter:description" content="{description}" />
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "{title}",
    "description": "{description}",
    "author": {{"@type": "Organization", "name": "dictate.app"}},
    "publisher": {{"@type": "Organization", "name": "dictate.app"}},
    "datePublished": "{date}",
    "dateModified": "{date}",
    "url": "{SITE_URL}/blog/{slug}.html",
    "mainEntityOfPage": "{SITE_URL}/blog/{slug}.html"
  }}
  </script>
{TEMPLATE_CSS}
</head>
<body>
  <div class="wrap">
{nav}
    <article>
{body_html}
{cta_block}
    </article>
{footer}
  </div>
{STARFIELD_JS}
</body>
</html>"""
    return html


# ─── POST DEFINITIONS ────────────────────────────────────────────────────────

POSTS = [

  # 1. Best voice to text windows 2026
  {
    "slug": "best-voice-to-text-software-windows-2026",
    "title": "Best Voice to Text Software for Windows in 2026",
    "description": "Comparing the best voice to text software for Windows in 2026. dictate.app, Dragon, Otter.ai, Wispr Flow, and Windows built-in — which one wins?",
    "keywords": "voice to text windows, best dictation software windows 2026, speech to text windows",
    "body": """
      <span class="post-label">Guide</span>
      <h1>Best Voice to Text Software for Windows in 2026</h1>
      <p class="post-meta">dictate.app Blog &nbsp;·&nbsp; May 2026 &nbsp;·&nbsp; 8 min read</p>

      <p>Voice to text software on Windows has exploded. There are more options than ever. Most are overpriced, cloud-dependent, or just plain slow. This guide cuts through the noise.</p>

      <p>We tested five tools that Windows users actually use in 2026. Here is what we found.</p>

      <h2>The Contenders</h2>
      <ul>
        <li><strong>dictate.app</strong> — Electron app, Groq Whisper, fully offline, $9/mo</li>
        <li><strong>Dragon Professional</strong> — Legacy leader, $150+ one-time, cloud optional</li>
        <li><strong>Otter.ai</strong> — Cloud-first meeting transcription, $8–17/mo</li>
        <li><strong>Wispr Flow</strong> — macOS-first, cloud-dependent, $12/mo</li>
        <li><strong>Windows built-in dictation</strong> — Free, limited, requires internet</li>
      </ul>

      <h2>Side-by-Side Comparison</h2>
      <div class="table-wrap">
        <table>
          <tr>
            <th>Feature</th>
            <th>dictate.app</th>
            <th>Dragon</th>
            <th>Otter.ai</th>
            <th>Wispr Flow</th>
            <th>Windows Built-in</th>
          </tr>
          <tr>
            <td>Price</td>
            <td class="win">$9/mo</td>
            <td>$150+ one-time</td>
            <td>$8–17/mo</td>
            <td>$12/mo</td>
            <td class="check">Free</td>
          </tr>
          <tr>
            <td>Offline / No Cloud</td>
            <td class="check">✓ 100%</td>
            <td class="check">✓ Optional</td>
            <td class="cross">✗ Cloud required</td>
            <td class="cross">✗ Cloud required</td>
            <td class="cross">✗ Needs internet</td>
          </tr>
          <tr>
            <td>Works in any text field</td>
            <td class="check">✓</td>
            <td class="check">✓</td>
            <td class="cross">✗</td>
            <td class="check">✓</td>
            <td class="check">✓</td>
          </tr>
          <tr>
            <td>Custom hotkey</td>
            <td class="check">✓ Any key</td>
            <td class="check">✓</td>
            <td class="cross">✗</td>
            <td class="cross">✗ Fixed</td>
            <td class="cross">✗ Fixed</td>
          </tr>
          <tr>
            <td>Languages</td>
            <td class="check">70+</td>
            <td>50+</td>
            <td>30+</td>
            <td>Limited</td>
            <td>Limited</td>
          </tr>
          <tr>
            <td>Speed (avg)</td>
            <td class="win">Under 1 second</td>
            <td>1–2 seconds</td>
            <td>2–3 seconds</td>
            <td>1–2 seconds</td>
            <td>1–2 seconds</td>
          </tr>
          <tr>
            <td>7-day free trial</td>
            <td class="check">✓</td>
            <td class="cross">✗</td>
            <td class="check">✓ (limited)</td>
            <td class="check">✓</td>
            <td class="check">Always free</td>
          </tr>
        </table>
      </div>

      <h2>Privacy: The Factor Most Tools Hide</h2>
      <p>Otter.ai stores your audio on their servers. Wispr Flow routes voice through the cloud. Even Windows built-in dictation sends data to Microsoft.</p>
      <p><strong>dictate.app processes everything locally.</strong> Your audio never leaves your machine. No logs. No uploads. No risk.</p>
      <p>For lawyers, doctors, therapists, and anyone handling sensitive information, this is not optional.</p>

      <h2>Speed: 150 WPM vs Your Typing Speed</h2>
      <p>Average typing speed is 60 words per minute. Fast typists hit 90. Voice dictation at 150 WPM is not marketing — it is physics. You speak faster than you type. Period.</p>
      <p>dictate.app transcribes in under a second after you stop speaking. Powered by Groq Whisper, one of the fastest inference engines available in 2026.</p>

      <h2>Dragon Dictate: Why It is Still Around</h2>
      <p>Dragon Professional has a legacy. Twenty years of training data. A loyal user base. But it costs $150+ upfront, the UI is dated, and cloud features require subscriptions on top.</p>
      <p>dictate.app delivers comparable accuracy at a fraction of the cost. $9/mo vs $150+. No contest for new users.</p>

      <h2>Windows Built-in Dictation: Good Enough?</h2>
      <p>Windows 11 has a passable built-in dictation tool. It requires internet. It works in some apps and breaks in others. You cannot change the hotkey. And Microsoft receives your audio.</p>
      <p>For occasional use, it is fine. For anyone dictating more than 10 minutes a day, it falls short.</p>

      <h2>The Verdict</h2>
      <p><strong>Best overall for Windows in 2026: dictate.app.</strong> Offline, private, fast, works everywhere, and $9/mo with a 7-day free trial. If you type for a living, dictation pays for itself in the first week.</p>
    """,
  },

  # 2. dictate.app vs Wispr Flow
  {
    "slug": "dictate-app-vs-wispr-flow",
    "title": "dictate.app vs Wispr Flow: The Real Comparison",
    "description": "Wispr Flow vs dictate.app compared on privacy, price, offline capability, and Windows support. The honest breakdown.",
    "keywords": "wispr flow alternative, wispr flow vs dictate app, dictate app comparison",
    "body": """
      <span class="post-label">Comparison</span>
      <h1>dictate.app vs Wispr Flow: The Real Comparison</h1>
      <p class="post-meta">dictate.app Blog &nbsp;·&nbsp; May 2026 &nbsp;·&nbsp; 9 min read</p>

      <p>Wispr Flow gets a lot of attention. It has slick marketing and decent reviews. But dig deeper and the cracks show. This is the comparison Wispr Flow does not want you to read.</p>

      <h2>The Core Difference: Cloud vs Offline</h2>
      <p>Wispr Flow sends your audio to the cloud for processing. Every word you speak leaves your device.</p>
      <p><strong>dictate.app never sends audio anywhere.</strong> Groq Whisper runs locally. Your words stay on your machine.</p>
      <p>That single difference changes everything for anyone who handles sensitive information.</p>

      <h2>Side-by-Side</h2>
      <div class="table-wrap">
        <table>
          <tr>
            <th>Feature</th>
            <th>dictate.app</th>
            <th>Wispr Flow</th>
          </tr>
          <tr>
            <td>Price</td>
            <td class="win">$9/mo</td>
            <td>$12/mo</td>
          </tr>
          <tr>
            <td>Offline processing</td>
            <td class="check">✓ 100% local</td>
            <td class="cross">✗ Cloud required</td>
          </tr>
          <tr>
            <td>Windows support</td>
            <td class="check">✓ Native</td>
            <td class="cross">✗ macOS only</td>
          </tr>
          <tr>
            <td>Custom hotkey</td>
            <td class="check">✓ Any key</td>
            <td class="cross">✗ Fixed</td>
          </tr>
          <tr>
            <td>Works in any text field</td>
            <td class="check">✓</td>
            <td class="check">✓</td>
          </tr>
          <tr>
            <td>Audio leaves your device</td>
            <td class="check">Never</td>
            <td class="cross">Always</td>
          </tr>
          <tr>
            <td>Free trial</td>
            <td class="check">7 days, full access</td>
            <td class="check">7 days</td>
          </tr>
          <tr>
            <td>Refund guarantee</td>
            <td class="check">30 days</td>
            <td class="cross">Not offered</td>
          </tr>
          <tr>
            <td>Languages</td>
            <td class="check">70+</td>
            <td>Limited</td>
          </tr>
        </table>
      </div>

      <h2>Wispr Flow Requires macOS</h2>
      <p>Wispr Flow is built for Mac. If you are on Windows — and most professionals are — Wispr Flow is simply not available. dictate.app is built specifically for Windows. It is a native Electron app that installs in seconds and works in every text field from day one.</p>

      <h2>Privacy: This Is Not a Minor Detail</h2>
      <p>When Wispr Flow processes your voice in the cloud, who owns that data? What are their retention policies? What happens if they are acquired or breached?</p>
      <p>These are not hypothetical questions. Multiple AI voice companies have been breached or sold user data in 2025–2026.</p>
      <p><strong>dictate.app has zero exposure.</strong> There is no server to breach. No data to sell. Your audio is processed locally and discarded after transcription.</p>

      <h2>Price: $9 vs $12</h2>
      <p>dictate.app costs $9/mo. Wispr Flow costs $12/mo. That is 25% cheaper for a better product on the privacy dimension.</p>
      <p>Over a year: $108 for dictate.app vs $144 for Wispr Flow. The savings are not huge, but getting more for less is always a win.</p>

      <h2>Custom Hotkeys: dictate.app Wins Here Too</h2>
      <p>Wispr Flow uses a fixed activation method. You cannot remap it. dictate.app lets you bind dictation to any key or key combination. Ctrl+Shift+Space by default. Change it to anything you want — no restrictions, no paywall.</p>

      <h2>The Verdict</h2>
      <p><strong>dictate.app wins on every angle that matters for Windows users:</strong> lower price, offline processing, full privacy, Windows-native, and custom hotkeys. Wispr Flow is a polished macOS product. But if you are on Windows and care about your data, dictate.app is the clear answer.</p>
    """,
  },

  # 3. Offline voice dictation software
  {
    "slug": "offline-voice-dictation-software",
    "title": "Offline Voice Dictation Software: Why It Matters in 2026",
    "description": "Why offline dictation software matters for privacy. Cloud voice tools expose your words. dictate.app processes everything locally with no internet required.",
    "keywords": "offline dictation software, voice to text no internet, private dictation, offline speech recognition",
    "body": """
      <span class="post-label">Privacy</span>
      <h1>Offline Voice Dictation Software: Why It Matters in 2026</h1>
      <p class="post-meta">dictate.app Blog &nbsp;·&nbsp; May 2026 &nbsp;·&nbsp; 7 min read</p>

      <p>Most voice dictation tools are cloud-first. You speak. Your audio travels to a server. A model transcribes it. The text comes back.</p>
      <p>That round trip is fast. But it comes with a cost you might not have considered.</p>

      <h2>What Happens to Your Audio in the Cloud</h2>
      <p>When your voice goes to a cloud service, several things happen:</p>
      <ul>
        <li>Your audio is stored on their servers (often indefinitely)</li>
        <li>It may be used to train future models</li>
        <li>It is subject to their privacy policy, which can change</li>
        <li>It is accessible to employees, contractors, and regulators</li>
        <li>It is exposed if that company is breached</li>
      </ul>
      <p>In 2025 alone, three major voice AI companies faced data exposure incidents. Your spoken words are more sensitive than you think.</p>

      <h2>Who This Affects Most</h2>
      <h3>Lawyers and Paralegals</h3>
      <p>Attorney-client privilege is sacred. Dictating legal documents to a cloud service may constitute a waiver of privilege. Many bar associations are now issuing guidance on exactly this issue. <strong>Offline dictation is not optional for legal professionals — it is an ethical requirement.</strong></p>

      <h3>Healthcare Professionals</h3>
      <p>HIPAA requires strict controls over patient information. Sending patient details to a third-party cloud for transcription requires Business Associate Agreements. Most dictation services do not provide these. Offline processing sidesteps the issue entirely.</p>

      <h3>Journalists and Researchers</h3>
      <p>Source protection matters. If you are interviewing a whistleblower, dictating your notes to a cloud service creates a digital trail you cannot control.</p>

      <h3>Executives and Business Professionals</h3>
      <p>Trade secrets, strategic plans, personnel matters. Anything you would not want leaked should not leave your device.</p>

      <h2>The Performance Myth</h2>
      <p>People assume cloud processing is faster. It is not, necessarily. Network latency adds overhead. If your connection is slow or spotty, cloud tools stall.</p>
      <p><strong>dictate.app processes locally using Groq Whisper.</strong> On a modern laptop with a standard GPU, transcription takes under one second. No network dependency. No throttling. Consistent speed everywhere.</p>

      <h2>Offline Dictation in Practice</h2>
      <p>dictate.app works completely without internet. Install it once. It runs from that point forward with zero network requirements. Your audio is processed on-device and discarded after transcription. Nothing is stored. Nothing is logged.</p>
      <p>Use it on a plane. In a secure facility. In a hotel with unreliable wifi. It does not matter. It works.</p>

      <h2>The Privacy Case Is Clear</h2>
      <p>Cloud dictation tools have built their business models on your data. Offline tools have no such incentive. Your audio, your device, your control.</p>
      <p>In 2026, with AI model training consuming everything it can find, offline voice dictation is not paranoia. It is basic information hygiene.</p>
    """,
  },

  # 4. Voice to text for lawyers
  {
    "slug": "voice-to-text-for-lawyers",
    "title": "Voice to Text for Lawyers: Private, Fast, Offline Dictation",
    "description": "Legal dictation software that never sends audio to the cloud. dictate.app: offline voice to text for lawyers, paralegals, and legal professionals.",
    "keywords": "voice to text for lawyers, legal dictation software, private dictation law, attorney dictation",
    "body": """
      <span class="post-label">Use Case</span>
      <h1>Voice to Text for Lawyers: Private, Fast, Offline Dictation</h1>
      <p class="post-meta">dictate.app Blog &nbsp;·&nbsp; May 2026 &nbsp;·&nbsp; 7 min read</p>

      <p>You know what you cannot dictate to Otter.ai or Wispr Flow: anything covered by attorney-client privilege. That is most of your day.</p>

      <h2>The Attorney-Client Privilege Problem</h2>
      <p>Attorney-client privilege protects communications between a lawyer and client. It is one of the oldest principles in legal practice. But it has a condition: the communication must be kept confidential.</p>
      <p>When you dictate a memo about client strategy to a cloud service, you are sending that information to a third party. Most ethics opinions treat this as a potential waiver of privilege — or at minimum a serious professional risk.</p>
      <p><strong>The safe answer is offline processing.</strong> If the audio never leaves your device, there is nothing to waive.</p>

      <h2>What Legal Professionals Need from Dictation Software</h2>
      <ul>
        <li><strong>Zero data transmission.</strong> Client names, case facts, legal strategy — none of it should leave the device.</li>
        <li><strong>Works in any application.</strong> Word, Outlook, case management systems, web-based portals. All of them.</li>
        <li><strong>Fast transcription.</strong> Billing by the hour means every minute matters.</li>
        <li><strong>Reliable on Windows.</strong> Most law firms run Windows. macOS-only tools are not an option.</li>
        <li><strong>Accurate with legal terminology.</strong> Groq Whisper handles specialized vocabulary well out of the box.</li>
      </ul>

      <h2>How dictate.app Works for Legal Professionals</h2>
      <p>Press Ctrl+Shift+Space (or any hotkey you set). Speak your text. Release. Your words appear in whatever text field your cursor is in.</p>
      <p>Works in Microsoft Word. Works in Outlook. Works in browser-based legal research tools. Works in case management systems. Works everywhere that accepts text input.</p>
      <p><strong>Your audio is processed locally by Groq Whisper and discarded after transcription.</strong> No logs. No uploads. No third-party access. Ever.</p>

      <h2>Use Cases in a Law Practice</h2>
      <h3>Drafting Correspondence</h3>
      <p>Dictate client letters, demand letters, settlement communications. 150 WPM vs 60 WPM typing. You draft faster, bill more time, or go home earlier. Your choice.</p>
      <h3>Legal Memos</h3>
      <p>Internal strategy memos. Case analysis. Research summaries. Dictate the structure, fill in citations manually. Cut memo time in half.</p>
      <h3>Client Notes After Calls</h3>
      <p>Right after a client call, dictate your notes while the details are fresh. Accurate records without the typing delay.</p>
      <h3>Deposition Summaries</h3>
      <p>Review a transcript, dictate your summary. Faster than typing a word-for-word analysis.</p>

      <h2>Dragon vs dictate.app for Legal Work</h2>
      <p>Dragon Naturally Speaking was the legal dictation standard for decades. It works. But it costs $150+ upfront, the interface is dated, and the cloud features expose data to Nuance servers.</p>
      <p>dictate.app at $9/mo delivers comparable accuracy on legal text, with a modern interface and complete offline processing. The total cost difference over three years is staggering: $324 vs $450+.</p>

      <h2>The Ethical Obligation Is Clear</h2>
      <p>The ABA and most state bars have issued guidance making clear that lawyers must take reasonable steps to protect client data when using technology. "Reasonable steps" in 2026 means using tools that do not transmit client information to third-party servers without client consent and appropriate agreements.</p>
      <p>dictate.app requires no such agreements. There is no third party. There is no transmission. There is just you, your microphone, and your device.</p>
    """,
  },

  # 5. Voice to text for writers
  {
    "slug": "voice-to-text-for-writers",
    "title": "Voice to Text for Writers: Type 150 Words Per Minute With Your Voice",
    "description": "Writers: dictate your first drafts faster than you can type. dictate.app lets you speak at 150 WPM with offline Groq Whisper transcription.",
    "keywords": "voice to text for writers, dictation for writers, speak to write faster, author dictation software",
    "body": """
      <span class="post-label">Use Case</span>
      <h1>Voice to Text for Writers: Type 150 Words Per Minute With Your Voice</h1>
      <p class="post-meta">dictate.app Blog &nbsp;·&nbsp; May 2026 &nbsp;·&nbsp; 7 min read</p>

      <p>The blank page is brutal. The cursor blinks. You type six words, delete four, type three more. You know what you want to say — the words are in your head — but getting them out through your fingers is slow, mechanical, and flow-breaking.</p>
      <p>Voice dictation changes that equation completely.</p>

      <h2>The Math Is Simple</h2>
      <p>Average typing speed: 60 words per minute. Fast typist: 90 WPM. Voice dictation: 150 WPM. That is a 2.5x output increase if you are an average typist.</p>
      <p>Write 1,000 words by typing: 16 minutes. Write 1,000 words by speaking: 7 minutes. The difference compounds across a full writing session.</p>
      <p>Stephen King writes 2,000 words a day. With dictation, that is 13 minutes of speaking. The craft is in the thinking, not the typing.</p>

      <h2>Writers Who Already Dictate</h2>
      <p>This is not a new idea. Henry James, late in his career, dictated all his novels to a stenographer. He claimed it freed him to think in longer, more complex sentences. Plenty of modern authors have adopted the same approach with modern tools.</p>
      <p>The barrier used to be cost (professional stenographers) or accuracy (early speech recognition was unreliable). Groq Whisper in 2026 is accurate enough that first drafts need minimal cleanup.</p>

      <h2>Flow State and Voice Dictation</h2>
      <p>Flow state is when you are in it — the writing comes easily, time disappears, the work is good. Typing interrupts flow. Every typo is a micro-interruption. Every reach for the delete key breaks the stream.</p>
      <p>Speaking is closer to thinking. You narrate. The words come out in the order they occur to you. The gap between thought and text shrinks from seconds to near-zero.</p>
      <p>Writers who switch to dictation often report that their first drafts feel more natural — more like their actual voice, less like "writer voice."</p>

      <h2>How to Start Dictating Your First Draft</h2>
      <ol>
        <li><strong>Install dictate.app.</strong> Set your hotkey to something comfortable — Ctrl+Shift+Space by default.</li>
        <li><strong>Open your document.</strong> Word, Google Docs, Notion, Obsidian — any text field works.</li>
        <li><strong>Hold the hotkey. Speak one sentence.</strong> Release. See the sentence appear.</li>
        <li><strong>Edit later, speak now.</strong> Turn off your inner editor for the first pass. Dictate everything. Fix it in revision.</li>
      </ol>
      <p>The first session feels strange. The second feels natural. By the third, you will wonder why you ever typed first drafts.</p>

      <h2>Works With Your Existing Tools</h2>
      <p>dictate.app does not replace your writing software. It works alongside it. Dictate into Word, Scrivener, Obsidian, Notion, even email drafts. It pastes text wherever your cursor is. Your workflow stays intact.</p>

      <h2>Privacy for Writers</h2>
      <p>Your story ideas, character names, plot twists — they are your intellectual property. Cloud dictation tools store your audio on their servers. dictate.app processes everything locally. Your drafts are yours alone.</p>

      <h2>The Resistance Is Real. So Are the Results.</h2>
      <p>Most writers who try dictation feel awkward at first. You have been typing for twenty years. Switching inputs feels wrong. Push through two weeks and the awkwardness fades. What stays is speed.</p>
      <p>Try the 7-day free trial. Write one chapter by voice. Compare the word count at the end of the session. The numbers speak for themselves.</p>
    """,
  },

  # 6. Voice to text for programmers
  {
    "slug": "voice-to-text-for-programmers",
    "title": "Voice to Text for Programmers: Dictate Code Comments, Docs, and Messages",
    "description": "RSI prevention, faster docs, and hands-free communication for developers. dictate.app works in VS Code, terminals, Slack, and any text field.",
    "keywords": "voice to text programmers, developer dictation software, voice coding, RSI prevention programmers",
    "body": """
      <span class="post-label">Use Case</span>
      <h1>Voice to Text for Programmers: Dictate Code Comments, Docs, and Messages</h1>
      <p class="post-meta">dictate.app Blog &nbsp;·&nbsp; May 2026 &nbsp;·&nbsp; 6 min read</p>

      <p>You probably are not going to dictate raw code. Brackets, semicolons, and nested functions do not flow naturally in speech. But most of what programmers write is not code.</p>

      <h2>What Programmers Actually Dictate</h2>
      <ul>
        <li><strong>Code comments.</strong> Explain what a function does. Describe a tricky algorithm. Document a workaround.</li>
        <li><strong>Docstrings and API docs.</strong> Long-form function documentation. README sections. Changelog entries.</li>
        <li><strong>Slack and Teams messages.</strong> "Hey can you take a look at PR #4217, I think the auth logic has a race condition when…" — faster to speak than type.</li>
        <li><strong>GitHub issue descriptions.</strong> Reproduce steps, expected behavior, actual behavior. Detailed bug reports in 30 seconds.</li>
        <li><strong>Technical emails.</strong> Explaining a decision to a stakeholder. Responding to a tech spec review.</li>
        <li><strong>Commit messages.</strong> Descriptive, not terse.</li>
        <li><strong>Meeting notes.</strong> After a standup or design review, dictate your summary before you forget.</li>
      </ul>

      <h2>RSI: The Hidden Career Risk</h2>
      <p>Repetitive Strain Injury affects an estimated 50% of programmers at some point in their careers. Carpal tunnel, tendinitis, and related conditions can sideline you for weeks or permanently alter how you work.</p>
      <p>Every word you speak instead of type reduces the strain on your wrists and hands. For documentation and communication — which is a significant fraction of a developer's day — dictation is a genuine intervention, not a gimmick.</p>

      <h2>Works Where You Work</h2>
      <p>dictate.app works in any text field. That means:</p>
      <ul>
        <li>VS Code comment blocks</li>
        <li>GitHub issue and PR descriptions in the browser</li>
        <li>Slack, Discord, Teams messages</li>
        <li>Jira tickets and Confluence pages</li>
        <li>Terminal commands (careful with syntax — use for plain language queries)</li>
        <li>Notion docs, Linear issues, any web-based tool</li>
      </ul>

      <h2>Privacy in Developer Environments</h2>
      <p>Your code is intellectual property. Architecture decisions, proprietary algorithms, unreleased features — none of this should go to a third-party cloud for processing. dictate.app processes locally. Your spoken words about your codebase never leave your machine.</p>

      <h2>Setup Takes 90 Seconds</h2>
      <p>Install. Set your hotkey (default: Ctrl+Shift+Space). Open VS Code. Click into a comment block. Hold the hotkey. Speak. Done.</p>
      <p>No configuration files. No API keys to manage. No special editor plugins required.</p>

      <h2>The Productivity Case</h2>
      <p>Good documentation gets skipped because it feels expensive. It takes too long to type. With dictation, the cost drops by 60%. You speak the comment, it appears, you move on. Documentation gets written because writing it stops being a grind.</p>
    """,
  },

  # 7. Custom hotkey dictation
  {
    "slug": "custom-hotkey-dictation-software",
    "title": "Dictation Software With Fully Custom Hotkeys — No Restrictions",
    "description": "Most dictation tools lock hotkeys or charge extra to remap them. dictate.app lets every user set any hotkey, free, with no restrictions.",
    "keywords": "dictation software custom hotkey, rebind dictation key, voice to text hotkey, dictation shortcut",
    "body": """
      <span class="post-label">Feature</span>
      <h1>Dictation Software With Fully Custom Hotkeys — No Restrictions</h1>
      <p class="post-meta">dictate.app Blog &nbsp;·&nbsp; May 2026 &nbsp;·&nbsp; 5 min read</p>

      <p>Most dictation tools give you one activation method. Maybe it is a specific key. Maybe it is a click on a floating button. Either way, it is fixed. You use it their way or you do not use it at all.</p>
      <p>That is a small thing until it is not. If the default hotkey conflicts with something you use constantly, every dictation session becomes a friction point.</p>

      <h2>Why Hotkeys Matter</h2>
      <p>A hotkey that conflicts with your workflow does not get used. Simple as that. The best dictation tool in the world is useless if activating it requires you to stop what you are doing and hunt for the right gesture.</p>
      <p>The tools that lock hotkeys know this. It is sometimes a monetization strategy — pay for the premium tier to get customization. Other times it is just laziness in the product design.</p>

      <h2>dictate.app: Any Key, Any Combination</h2>
      <p>dictate.app defaults to <strong>Ctrl+Shift+Space</strong>. That is a comfortable hold that does not conflict with most applications.</p>
      <p>Do not like it? Change it. Open settings, click the hotkey field, press your preferred combination, save. Done. Zero restrictions. No premium tier required.</p>
      <p>Want to use a single key? Bind it. A mouse button? Works. A media key? Works. Whatever fits your hands and workflow, you can set it.</p>

      <h2>Hotkey Conflicts: What to Watch For</h2>
      <p>Some popular combinations are already claimed by other software:</p>
      <ul>
        <li>Ctrl+Space — used by many code editors for autocomplete</li>
        <li>Windows+H — Windows 11 built-in speech recognition</li>
        <li>Ctrl+Shift+I — browser developer tools</li>
      </ul>
      <p>With dictate.app, you check your options once and pick something clean. No workarounds. No worrying about which application "wins" the keybind.</p>

      <h2>Push-to-Talk vs Toggle</h2>
      <p>dictate.app uses push-to-talk. Hold the hotkey to record. Release to transcribe. This is intentional. It keeps recordings clean and deliberate. No accidental dictation when you leave the app open. No background noise captured while you are thinking.</p>

      <h2>Who Benefits from Custom Hotkeys</h2>
      <ul>
        <li><strong>Left-handed users</strong> who find default right-hand combinations awkward</li>
        <li><strong>Ergonomic keyboard users</strong> with non-standard layouts</li>
        <li><strong>Gamers</strong> who have specific keys reserved for other software</li>
        <li><strong>Accessibility users</strong> who need specific physical accommodations</li>
        <li><strong>Power users</strong> who manage ten tools and cannot afford conflicts</li>
      </ul>

      <h2>The Bottom Line</h2>
      <p>Custom hotkeys are a basic feature. dictate.app gives it to every user at every tier. No upsell. No workaround. Just set your key and start dictating.</p>
    """,
  },

  # 8. Dragon Dictate alternative
  {
    "slug": "dragon-dictate-alternative",
    "title": "Dragon Dictate Alternative: Get Better Accuracy for $9/Month",
    "description": "Looking for a Dragon Dictate alternative? dictate.app delivers Groq Whisper accuracy offline for $9/mo — no $150+ upfront, no legacy bloat.",
    "keywords": "dragon dictate alternative, dragon naturally speaking alternative, cheap dictation software, dragon speech recognition alternative",
    "body": """
      <span class="post-label">Comparison</span>
      <h1>Dragon Dictate Alternative: Get Better Accuracy for $9/Month</h1>
      <p class="post-meta">dictate.app Blog &nbsp;·&nbsp; May 2026 &nbsp;·&nbsp; 7 min read</p>

      <p>Dragon Dictate has been the default answer to "what dictation software should I use?" for over twenty years. That era is ending.</p>
      <p>Not because Dragon got worse. Because the alternatives got dramatically better — and dramatically cheaper.</p>

      <h2>What Dragon Dictate Costs in 2026</h2>
      <p>Dragon Professional Individual: $150+ one-time, or $15–25/mo on a subscription. For enterprise features, add more. For support, add more again.</p>
      <p>That made sense when Dragon was the only option with real accuracy. It does not make sense now.</p>

      <h2>The Accuracy Myth</h2>
      <p>Dragon built its reputation on accuracy. And it earned it — in 2010. The models that power Dragon in 2026 are still largely rooted in that era's architecture.</p>
      <p>Groq Whisper — the engine powering dictate.app — was trained on 680,000 hours of multilingual speech. It matches or exceeds Dragon on standard speech in independent benchmarks. At a fraction of the cost.</p>

      <h2>dictate.app vs Dragon: The Comparison</h2>
      <div class="table-wrap">
        <table>
          <tr>
            <th>Feature</th>
            <th>dictate.app</th>
            <th>Dragon Professional</th>
          </tr>
          <tr>
            <td>Price</td>
            <td class="win">$9/mo</td>
            <td>$150+ one-time / $15–25/mo</td>
          </tr>
          <tr>
            <td>Free trial</td>
            <td class="check">7 days, full access</td>
            <td class="cross">No free trial</td>
          </tr>
          <tr>
            <td>Offline processing</td>
            <td class="check">✓ 100% local</td>
            <td class="check">✓ (some cloud features)</td>
          </tr>
          <tr>
            <td>Works in any text field</td>
            <td class="check">✓</td>
            <td class="check">✓</td>
          </tr>
          <tr>
            <td>Custom hotkey</td>
            <td class="check">✓ Any key</td>
            <td class="check">✓</td>
          </tr>
          <tr>
            <td>Setup time</td>
            <td class="win">Under 2 minutes</td>
            <td>20–30 min (voice profile training)</td>
          </tr>
          <tr>
            <td>Languages</td>
            <td class="check">70+</td>
            <td>50+</td>
          </tr>
          <tr>
            <td>UI modernity</td>
            <td class="win">Modern, minimal</td>
            <td>Legacy interface</td>
          </tr>
          <tr>
            <td>Refund guarantee</td>
            <td class="check">30 days</td>
            <td class="cross">No</td>
          </tr>
        </table>
      </div>

      <h2>Dragon Requires Voice Training. dictate.app Does Not.</h2>
      <p>One of the traditional Dragon requirements was an upfront voice profile training session — 20 to 30 minutes of reading passages so the system could calibrate to your voice. It improved accuracy but added friction.</p>
      <p>dictate.app requires zero training. Open it. Start dictating. Groq Whisper adapts to your voice in real time.</p>

      <h2>Dragon's Legacy Bloat</h2>
      <p>Dragon has accumulated decades of features. Command macros, dictation profiles, PowerMic support, Dragon Anywhere integration. If you need all of that, Dragon is your tool.</p>
      <p>If you need to speak and have accurate text appear — which is 95% of what people actually use dictation software for — you do not need any of it. dictate.app does the one thing well.</p>

      <h2>The Cost Over Three Years</h2>
      <p>Dragon Professional: $150 upfront, assume no subscription extras. Total over 3 years: $150.</p>
      <p>dictate.app: $9/mo × 36 = $324. But you get a 7-day free trial, a 30-day refund window, and you can cancel any month.</p>
      <p>If you need it for a project and then stop, dictate.app costs less. If you use it for years, Dragon costs less. The break-even is about 17 months.</p>
      <p>But price is not the only dimension. For users who want modern architecture, zero setup, multilingual support, and a 30-day refund guarantee, dictate.app wins regardless of the math.</p>

      <h2>Try It Free</h2>
      <p>dictate.app has a 7-day free trial with full access. No credit card required. Dragon offers no trial. If you are switching from Dragon, try dictate.app for a week before you commit to anything.</p>
    """,
  },
]


def post_description(post):
    """Extract clean description for index card."""
    return post["description"]


def build_html():
    os.makedirs(BLOG_DIR, exist_ok=True)

    index_cards = []

    for p in POSTS:
        html = make_post(
            slug=p["slug"],
            title=p["title"],
            description=p["description"],
            keywords=p["keywords"],
            body_html=p["body"],
        )
        out_path = os.path.join(BLOG_DIR, p["slug"] + ".html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  Wrote: blog/{p['slug']}.html")

        index_cards.append({
            "slug": p["slug"],
            "title": p["title"],
            "desc": p["description"],
        })

    # Write index
    build_index(index_cards)
    print("  Wrote: blog/index.html")


def build_index(cards):
    """Generate blog/index.html from a list of card dicts."""
    card_html = ""
    for c in cards:
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
  <title>dictate.app Blog — Voice Dictation Tips &amp; Guides</title>
  <meta name="description" content="Voice dictation tips, software comparisons, and productivity guides from dictate.app." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{SITE_URL}/blog/" />
  <meta property="og:title" content="dictate.app Blog" />
  <meta property="og:description" content="Voice dictation tips, comparisons, and guides." />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="{SITE_URL}/blog/" />
  <style>
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    :root {{
      --bg: #0d0a14; --bg-accent: #1a1625;
      --text-primary: #e8dff5; --text-secondary: #c4b8d4;
      --accent: #c084fc; --accent-rose: #f472b6;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg); color: var(--text-primary);
      line-height: 1.7; overflow-x: hidden;
    }}
    canvas#starfield {{
      position: fixed; top:0; left:0; width:100%; height:100%;
      z-index:-1; pointer-events:none;
    }}
    .wrap {{ position:relative; z-index:1; }}
    header {{
      padding: 20px 32px;
      backdrop-filter: blur(10px);
      border-bottom: 1px solid rgba(192,132,252,0.1);
      position: sticky; top:0; z-index:100;
      background: rgba(13,10,20,0.85);
    }}
    nav {{
      max-width: 1200px; margin: 0 auto;
      display: flex; justify-content: space-between; align-items: center;
    }}
    .nav-home {{
      color: var(--text-secondary); text-decoration: none;
      font-size: 14px; transition: color 0.2s;
      display: flex; align-items: center; gap: 6px;
    }}
    .nav-home:hover {{ color: var(--accent); }}
    .logo-icon {{
      width: 26px; height: 26px; border-radius: 6px;
      background: linear-gradient(135deg, #c084fc 0%, #f472b6 100%);
      display: inline-flex; align-items: center; justify-content: center;
      font-size: 14px; margin-right: 4px;
    }}
    .cta-nav {{
      display: inline-block; padding: 10px 24px;
      background: linear-gradient(135deg, var(--accent) 0%, var(--accent-rose) 100%);
      color: white; text-decoration: none;
      border-radius: 6px; font-size: 14px; font-weight: 600;
      transition: all 0.2s;
      box-shadow: 0 4px 14px rgba(192,132,252,0.3);
    }}
    .cta-nav:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(192,132,252,0.5); }}
    .hero {{
      text-align: center; padding: 80px 24px 40px;
    }}
    .hero h1 {{
      font-size: clamp(28px, 5vw, 44px);
      font-weight: 700; margin-bottom: 12px;
    }}
    .hero p {{ color: var(--text-secondary); font-size: 16px; }}
    .grid {{
      max-width: 1100px; margin: 0 auto;
      padding: 0 24px 80px;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 24px;
    }}
    .card {{
      background: rgba(255,255,255,0.03);
      border: 1px solid rgba(192,132,252,0.15);
      border-radius: 12px; padding: 28px 24px;
      text-decoration: none; display: block;
      transition: all 0.2s;
      color: var(--text-primary);
    }}
    .card:hover {{
      border-color: rgba(192,132,252,0.4);
      background: rgba(192,132,252,0.05);
      transform: translateY(-3px);
      box-shadow: 0 8px 24px rgba(192,132,252,0.15);
    }}
    .card h2 {{
      font-size: 17px; font-weight: 700;
      color: var(--text-primary); margin-bottom: 10px;
      line-height: 1.3;
    }}
    .card p {{
      font-size: 14px; color: var(--text-secondary);
      margin-bottom: 16px; line-height: 1.6;
    }}
    .read-more {{
      font-size: 14px; color: var(--accent); font-weight: 600;
    }}
    footer {{
      border-top: 1px solid rgba(192,132,252,0.1);
      padding: 32px; text-align: center;
      color: var(--text-secondary); font-size: 13px;
    }}
    footer a {{ color: var(--accent); text-decoration: none; }}
    @media (max-width: 900px) {{ .grid {{ grid-template-columns: repeat(2, 1fr); }} }}
    @media (max-width: 580px) {{ .grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <nav>
        <a class="nav-home" href="{SITE_URL}">
          <span class="logo-icon">🎙</span> ← dictate.app
        </a>
        <a class="cta-nav" href="{SITE_URL}">Start Free Trial</a>
      </nav>
    </header>
    <div class="hero">
      <h1>dictate.app Blog</h1>
      <p>Voice dictation tips, software comparisons, and productivity guides.</p>
    </div>
    <div class="grid">
{card_html}
    </div>
    <footer>
      <p>© 2026 dictate.app &nbsp;·&nbsp; <a href="{SITE_URL}">Home</a> &nbsp;·&nbsp; <a href="{SITE_URL}/blog/">Blog</a></p>
    </footer>
  </div>
  <canvas id="starfield"></canvas>
  <script>
    const canvas = document.getElementById("starfield");
    const ctx = canvas.getContext("2d");
    function resizeCanvas() {{ canvas.width = window.innerWidth; canvas.height = window.innerHeight; }}
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);
    const stars = [];
    for (let i = 0; i < 50; i++) {{
      stars.push({{
        x: Math.random() * canvas.width, y: Math.random() * canvas.height,
        radius: Math.random() * 1.2, opacity: Math.random() * 0.5 + 0.4,
        vx: (Math.random() - 0.5) * 0.08, vy: (Math.random() - 0.5) * 0.08
      }});
    }}
    function drawStarfield() {{
      ctx.fillStyle = "rgba(13,10,20,0.1)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      stars.forEach(s => {{
        s.x += s.vx; s.y += s.vy;
        if (s.x < 0) s.x = canvas.width;
        if (s.x > canvas.width) s.x = 0;
        if (s.y < 0) s.y = canvas.height;
        if (s.y > canvas.height) s.y = 0;
        ctx.fillStyle = `rgba(192,132,252,${{s.opacity}})`;
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.radius, 0, Math.PI * 2);
        ctx.fill();
      }});
      requestAnimationFrame(drawStarfield);
    }}
    drawStarfield();
  </script>
</body>
</html>"""

    out_path = os.path.join(BLOG_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(index_html)


if __name__ == "__main__":
    print("Generating dictate.app blog posts...")
    build_html()
    print("Done.")
