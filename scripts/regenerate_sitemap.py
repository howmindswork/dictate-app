#!/usr/bin/env python3
"""Regenerate sitemap.xml from current site files."""
import os, glob, datetime
from pathlib import Path

BASE = "https://dictate-app.pages.dev"
ROOT = Path(__file__).resolve().parent.parent

static = [
    ("/", "1.0", "weekly"),
    ("/download.html", "0.9", "weekly"),
    ("/affiliates.html", "0.8", "monthly"),
    ("/privacy.html", "0.3", "yearly"),
    ("/thank-you.html", "0.2", "yearly"),
]

blog_files = sorted(glob.glob(str(ROOT / "blog" / "*.html")))

def mtime(p):
    return datetime.date.fromtimestamp(os.path.getmtime(p)).isoformat()

xml = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for path, prio, freq in static:
    full = ROOT / path.lstrip("/") if path != "/" else ROOT / "index.html"
    lm = mtime(full) if full.exists() else datetime.date.today().isoformat()
    xml.append(f"  <url><loc>{BASE}{path}</loc><lastmod>{lm}</lastmod><changefreq>{freq}</changefreq><priority>{prio}</priority></url>")
for f in blog_files:
    slug = Path(f).stem
    lm = mtime(f)
    xml.append(f"  <url><loc>{BASE}/blog/{slug}.html</loc><lastmod>{lm}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>")
xml.append("</urlset>")

(ROOT / "sitemap.xml").write_text("\n".join(xml))
print(f"Wrote sitemap with {len(static) + len(blog_files)} URLs")
