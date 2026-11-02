#!/usr/bin/env python3
"""Generate the all-posts index pages for the blog.

Scans docs/posts/*/index.html and docs/en/posts/*/index.html, reads the
title / description / publish date / section out of each <head>, and writes
docs/posts/index.html plus docs/en/posts/index.html (newest first).

Re-run after adding or editing a post:

    python scripts/generate_posts_index.py
"""
from __future__ import annotations

import html
import re
import subprocess
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"


def clean(text: str) -> str:
    text = html.unescape(text).strip()
    text = re.sub(r"\s*·\s*EZ AI Ops.*$", "", text)
    return text


def grab(pattern: str, text: str, default: str = "") -> str:
    m = re.search(pattern, text, re.S)
    return clean(m.group(1)) if m else default


def git_date(path: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(path)],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
        return out
    except Exception:
        return ""


def parse_post(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    title = grab(r"<title>(.*?)</title>", text) or path.parent.name
    desc = grab(r'<meta name="description" content="(.*?)">', text)
    date = grab(r'<meta property="article:published_time" content="(.*?)"', text)
    if not date:
        date = git_date(path)
    section = grab(r'<meta property="article:section" content="(.*?)"', text)
    return {
        "slug": path.parent.name,
        "title": title,
        "desc": desc,
        "date": date,
        "section": section,
    }


def scan(dir_path: Path) -> list[dict]:
    posts = []
    for page in sorted(dir_path.glob("*/index.html")):
        posts.append(parse_post(page))
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def esc(text: str) -> str:
    return html.escape(text, quote=False)


STYLE = """
:root{--primary:#2c3e50;--accent:#4a90e2;--text:#24292f;--muted:#6b7280;--bg:#f6f8fa;--card-bg:#ffffff;--border:#e5e7eb}
*{box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",Helvetica,Arial,sans-serif;background:var(--bg);color:var(--text);margin:0;line-height:1.65;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
.site-header{background:#fff;border-bottom:1px solid var(--border)}
.site-header-inner{max-width:860px;margin:0 auto;padding:20px 24px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px}
.brand h1{margin:0;font-size:1.3rem;color:var(--primary);letter-spacing:-.01em}
.brand .brand-sub{display:block;font-size:.75rem;color:var(--muted);font-weight:400;margin-top:2px;letter-spacing:.02em}
nav.top-nav{display:flex;align-items:center;flex-wrap:wrap;gap:4px 6px}
nav.top-nav a{margin-left:6px;padding:5px 11px;border-radius:8px;color:var(--text);font-size:.92rem}
nav.top-nav a:first-child{margin-left:0}
nav.top-nav a:hover{background:#f0f4f9;color:var(--primary);text-decoration:none}
nav.top-nav a.active{background:var(--accent);color:#fff}
nav.top-nav a.nav-ext{color:var(--accent);font-weight:600}
.lang-switch{display:inline-flex;margin-left:14px;padding:2px;background:#f3f4f6;border-radius:12px;gap:2px}
.lang-switch a{margin:0;padding:3px 12px;font-size:.78rem;font-weight:600;letter-spacing:.02em;color:var(--muted);border-radius:10px;line-height:1.5}
.lang-switch a.active{background:var(--accent);color:#fff}
.lang-switch a:hover:not(.active){color:var(--primary);background:#e8eaed;text-decoration:none}
main{max-width:860px;margin:0 auto;padding:36px 24px 60px}
.page-title{font-size:1.6rem;color:var(--primary);margin:0 0 8px;letter-spacing:-.01em}
.page-hint{color:var(--muted);font-size:.88rem;margin:0 0 22px}
.post-list{list-style:none;margin:0;padding:4px 26px;background:var(--card-bg);border:1px solid var(--border);border-radius:10px}
.post-list li{border-bottom:1px dashed var(--border);padding:16px 0}
.post-list li:last-child{border-bottom:none}
.post-title{font-size:1rem;color:var(--text);font-weight:600}
.post-title:hover{color:var(--accent);text-decoration:none}
.post-desc{color:var(--muted);font-size:.86rem;margin:4px 0 8px}
.post-meta{display:flex;gap:10px;align-items:center;flex-wrap:wrap;font-size:.76rem;color:var(--muted)}
.post-meta .tag{background:#eef4fc;color:var(--accent);padding:2px 9px;border-radius:10px;font-weight:600;letter-spacing:.02em}
.also{margin:20px 0 0;color:var(--muted);font-size:.9rem}
footer{border-top:1px solid var(--border);background:#fff;color:var(--muted);font-size:.85rem}
footer .footer-inner{max-width:860px;margin:0 auto;padding:20px 24px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px}
@media(max-width:600px){.site-header-inner{flex-direction:column;align-items:flex-start}main{padding:26px 18px 44px}.post-list{padding:4px 18px}}
"""

FAVICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Crect width='32' height='32' rx='6' fill='%232c3e50'/%3E%3Ctext x='50%25' y='55%25' "
    "fill='white' font-size='14' font-family='Arial,sans-serif' text-anchor='middle' "
    "dominant-baseline='middle' font-weight='700'%3EEZ%3C/text%3E%3C/svg%3E"
)

BEACON = (
    '<script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
    'data-cf-beacon=\'{"token": "4bbeee48cff340fe9ae88884f763f334"}\'></script>'
)

TEMPLATE = Template("""<!DOCTYPE html>
<html lang="$lang">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>$page_title</title>
  <meta name="description" content="$page_desc">
  <meta property="og:title" content="$page_title">
  <meta property="og:description" content="$page_desc">
  <meta property="og:type" content="website">
  <meta property="og:url" content="$canonical">
  <link rel="canonical" href="$canonical">
  <link rel="alternate" hreflang="zh-CN" href="https://ezaiops.com/posts/">
  <link rel="alternate" hreflang="en" href="https://ezaiops.com/en/posts/">
  <link rel="alternate" hreflang="x-default" href="https://ezaiops.com/posts/">
  <link rel="icon" href="$favicon">
  <style>$style</style>
</head>
<body>

  <header class="site-header">
    <div class="site-header-inner">
      <div class="brand">
        <h1>$brand_name</h1>
        <span class="brand-sub">$brand_sub</span>
      </div>
      <nav class="top-nav">
        $nav
      </nav>
    </div>
  </header>

  <main>
    <h2 class="page-title">$heading</h2>
    <p class="page-hint">$hint</p>
    <ul class="post-list">
$items
    </ul>
    <p class="also">$also</p>
  </main>

  <footer>
    <div class="footer-inner">
      <span>$copyright</span>
      <span>$footer_links</span>
      <span><a href="https://tools.ezaiops.com/?lang=$tool_lang">$footer_tools</a></span>
    </div>
  </footer>

$beacon
</body>
</html>
""")


def render_items(posts: list[dict], base: str, tag_fallback: str) -> str:
    rows = []
    for p in posts:
        tag = p["section"] or tag_fallback
        desc = esc(p["desc"])
        desc_html = f'\n        <p class="post-desc">{desc}</p>' if desc else ""
        rows.append(
            f'      <li>\n'
            f'        <a class="post-title" href="{base}{p["slug"]}/">{esc(p["title"])}</a>'
            f'{desc_html}\n'
            f'        <div class="post-meta"><span>{esc(p["date"])}</span>'
            f'<span class="tag">{esc(tag)}</span></div>\n'
            f'      </li>'
        )
    return "\n".join(rows)


def build_zh(posts: list[dict]) -> str:
    nav = (
        '<a href="/">首页</a>\n'
        '        <a class="active" href="/posts/" aria-current="page">文章</a>\n'
        '        <a href="/#topics">话题</a>\n'
        '        <a href="/about/">关于</a>\n'
        '        <a class="nav-ext" href="https://tools.ezaiops.com/?lang=zh">工具 <span aria-hidden="true">↗</span></a>\n'
        '        <div class="lang-switch">\n'
        '          <a href="/posts/" class="active" aria-current="page">中文</a>\n'
        '          <a href="/en/posts/" hreflang="en">EN</a>\n'
        '        </div>'
    )
    return TEMPLATE.substitute(
        lang="zh-CN",
        page_title="全部文章 · EZ AI Ops Tips",
        page_desc="EZ AI Ops Tips 全部文章索引：Agent 可观测性系列、AI 技术栈地图等，按发布时间倒序。",
        canonical="https://ezaiops.com/posts/",
        favicon=FAVICON,
        style=STYLE,
        brand_name="轻松自动化笔记",
        brand_sub="Notes · Tools · Pricing",
        nav=nav,
        heading="全部文章",
        hint=f"共 {len(posts)} 篇 · 按发布时间倒序 · Agent 可观测性系列为主线",
        items=render_items(posts, "/posts/", "文章"),
        also='另见：<a href="/graph/ai-2026/">AI 技术全景图谱 2026（可交互，93 个节点）</a>',
        copyright="© 2026 EZ AI Ops Tips · 轻松自动化笔记",
        footer_links='<a href="/about/">关于</a> · <a href="/contact/">联系</a> · <a href="/privacy/">隐私</a>',
        footer_tools="免费工具站 →",
        tool_lang="zh",
        beacon=BEACON,
    )


def build_en(posts: list[dict]) -> str:
    nav = (
        '<a href="/en/">Home</a>\n'
        '        <a class="active" href="/en/posts/" aria-current="page">Articles</a>\n'
        '        <a href="/en/#topics">Topics</a>\n'
        '        <a href="/en/about/">About</a>\n'
        '        <a class="nav-ext" href="https://tools.ezaiops.com/?lang=en">Tools <span aria-hidden="true">↗</span></a>\n'
        '        <div class="lang-switch">\n'
        '          <a href="/posts/" hreflang="zh-CN">中文</a>\n'
        '          <a href="/en/posts/" class="active" aria-current="page">EN</a>\n'
        '        </div>'
    )
    return TEMPLATE.substitute(
        lang="en",
        page_title="All articles · EZ AI Ops Tips",
        page_desc="Every article on EZ AI Ops Tips: the agent observability series, the AI stack map and more, newest first.",
        canonical="https://ezaiops.com/en/posts/",
        favicon=FAVICON,
        style=STYLE,
        brand_name="EZ AI Ops Tips",
        brand_sub="轻松自动化笔记",
        nav=nav,
        heading="All articles",
        hint=f"{len(posts)} posts, newest first — the agent observability series is the main pillar",
        items=render_items(posts, "/en/posts/", "Article"),
        also='See also: <a href="/en/graph/ai-2026/">AI Technology Landscape 2026 (interactive, 93 nodes)</a>',
        copyright="© 2026 EZ AI Ops Tips · 轻松自动化笔记",
        footer_links='<a href="/en/about/">About</a> · <a href="/en/contact/">Contact</a> · <a href="/en/privacy/">Privacy</a>',
        footer_tools="Free tools →",
        tool_lang="en",
        beacon=BEACON,
    )


def main() -> None:
    zh_posts = scan(DOCS / "posts")
    en_posts = scan(DOCS / "en" / "posts")
    if not zh_posts and not en_posts:
        raise SystemExit("no posts found — check the docs/posts layout")

    zh_out = DOCS / "posts" / "index.html"
    en_out = DOCS / "en" / "posts" / "index.html"
    zh_out.write_text(build_zh(zh_posts), encoding="utf-8")
    en_out.write_text(build_en(en_posts), encoding="utf-8")
    print(f"zh index: {len(zh_posts)} posts -> {zh_out.relative_to(ROOT)}")
    print(f"en index: {len(en_posts)} posts -> {en_out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
