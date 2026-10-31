#!/usr/bin/env python3
"""Make sure every page under docs/ carries the Cloudflare Web Analytics beacon.

The article pages are Astro output built on another machine; this repository
holds the result, not the source. Copying a fresh build in would silently drop
the beacon and the analytics would go quiet without anyone noticing. Run this
after importing new output.

Idempotent: pages that already have the beacon are left untouched, so it is safe
to run on every import.

    python scripts/add_analytics.py          # apply
    python scripts/add_analytics.py --check  # exit 1 if any page is missing it
"""
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")

# One token covers both ezaiops.com and tools.ezaiops.com; Cloudflare reports
# them separately by request host.
BEACON = ('<script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
          'data-cf-beacon=\'{"token": "4bbeee48cff340fe9ae88884f763f334"}\'></script>\n')


def main():
    check_only = "--check" in sys.argv
    pages = sorted(glob.glob(os.path.join(DOCS, "**", "*.html"), recursive=True))

    added, already, broken = [], [], []
    for path in pages:
        name = os.path.relpath(path, ROOT).replace("\\", "/")
        html = open(path, encoding="utf-8").read()

        if "cloudflareinsights" in html:
            already.append(name)
            continue
        if "</body>" not in html:
            broken.append(name)
            continue

        added.append(name)
        if not check_only:
            open(path, "w", encoding="utf-8", newline="\n").write(
                html.replace("</body>", BEACON + "</body>", 1))

    print("pages: %d | missing beacon: %d | already had it: %d"
          % (len(pages), len(added), len(already)))
    for name in added:
        print("  + " + name)
    for name in broken:
        print("  ! no </body>: " + name)

    if check_only and added:
        print("\nRun `python scripts/add_analytics.py` to fix.")
        return 1
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
