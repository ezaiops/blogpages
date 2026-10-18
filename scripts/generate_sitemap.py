#!/usr/bin/env python3
"""Generate docs/sitemap.xml for ezaiops.com.

The blog is a static tree of docs/**/index.html with Chinese pages at the root and
English pages under /en/. Every page already declares hreflang alternates in its
own <head>; this sitemap repeats them as xhtml:link entries so crawlers get the
same pairing from the sitemap itself.

Run from the repo root:  python scripts/generate_sitemap.py
"""
import datetime
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
BASE = "https://ezaiops.com"


def page_url(rel_dir):
    """docs/posts/x -> /posts/x/ ; docs/en/index.html -> /en/ ; docs/index.html -> /"""
    rel = rel_dir.replace(os.sep, "/").strip("/")
    if rel in ("", "en"):
        return BASE + "/" + (rel + "/" if rel else "")
    return "%s/%s/" % (BASE, rel)


def last_modified(path):
    """Prefer the last git commit date; fall back to file mtime."""
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", rel],
            cwd=ROOT, capture_output=True, text=True, timeout=10)
        stamp = out.stdout.strip()
        if stamp:
            return stamp
    except Exception:
        pass
    return datetime.date.fromtimestamp(os.path.getmtime(path)).isoformat()


def collect():
    pages = []
    for dirpath, dirnames, filenames in os.walk(DOCS):
        if "index.html" not in filenames:
            continue
        rel = os.path.relpath(dirpath, DOCS)
        if rel == ".":
            rel = ""
        pages.append((rel.replace(os.sep, "/"), os.path.join(dirpath, "index.html")))
    return sorted(pages)


def counterpart(rel):
    """Return the (zh, en) path pair for a given relative directory."""
    if rel == "":
        return "", "en"
    if rel == "en":
        return "", "en"
    if rel.startswith("en/"):
        return rel[3:], rel
    return rel, "en/" + rel


def build(pages):
    by_rel = {rel: path for rel, path in pages}
    entries = []
    for rel, path in pages:
        zh, en = counterpart(rel)
        url = page_url(rel)
        lines = ["  <url>", "    <loc>%s</loc>" % url]
        for lang, other in (("zh-CN", zh), ("en", en)):
            if other in by_rel:
                lines.append('    <xhtml:link rel="alternate" hreflang="%s" href="%s"/>'
                             % (lang, page_url(other)))
        if zh in by_rel:
            lines.append('    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>'
                         % page_url(zh))
        priority = "1.0" if rel in ("", "en") else "0.8"
        changefreq = "weekly" if rel in ("", "en") else "monthly"
        lines.append("    <lastmod>%s</lastmod>" % last_modified(path))
        lines.append("    <changefreq>%s</changefreq>" % changefreq)
        lines.append("    <priority>%s</priority>" % priority)
        lines.append("  </url>")
        entries.append("\n".join(lines))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(entries) + "\n</urlset>\n")


def main():
    pages = collect()
    out = build(pages)
    with open(os.path.join(DOCS, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(out)
    print("sitemap written: %d urls" % len(pages))
    for rel, _ in pages:
        print("  " + page_url(rel))


if __name__ == "__main__":
    main()
