#!/usr/bin/env python3
"""Dev-only structural validator for the Topic References static site.

This is NOT part of the site and is never shipped — it just gives a quick
sanity check that the hand-maintained links stay consistent. It uses only the
Python standard library, so it runs anywhere:

    uv run tests/check_site.py        # or: python3 tests/check_site.py

Checks performed:
  1. Every topics/<slug>.html is linked from index.html (no orphan pages).
  2. Every topic link in index.html points to a file that exists (no dead links).
  3. Each topic page has the expected skeleton: links ../styles.css, has an
     <h1>, a "Last updated:" line, and a back link to the index.

Exit code is 0 when everything passes, 1 otherwise — handy for CI later.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Resolve paths relative to the repo root (this file lives in tests/).
ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
TOPICS_DIR = ROOT / "topics"

# Collected human-readable problems; the script fails if this is non-empty.
errors: list[str] = []

# Matches HTML comment blocks so example markup inside <!-- ... --> (e.g. the
# `topics/<slug>.html` pattern documented in index.html) is not mistaken for a
# real link or element.
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def strip_comments(html: str) -> str:
    """Remove HTML comments so they aren't scanned as real markup."""
    return COMMENT_RE.sub("", html)


def linked_topics(index_html: str) -> set[str]:
    """Return the set of topic filenames referenced from index.html.

    Matches href="topics/<name>.html" in the card anchors.
    """
    return set(re.findall(r'href="topics/([^"/]+\.html)"', index_html))


def existing_topics() -> set[str]:
    """Return the set of *.html filenames present in topics/."""
    if not TOPICS_DIR.is_dir():
        return set()
    return {p.name for p in TOPICS_DIR.glob("*.html")}


def check_topic_page(path: Path) -> None:
    """Validate that a single topic page has the required structure."""
    html = strip_comments(path.read_text(encoding="utf-8"))
    name = f"topics/{path.name}"

    if "../styles.css" not in html:
        errors.append(f"{name}: missing link to ../styles.css")
    if not re.search(r"<h1[^>]*>.*?\S.*?</h1>", html, re.S):
        errors.append(f"{name}: missing a non-empty <h1> title")
    if "Last updated:" not in html:
        errors.append(f"{name}: missing 'Last updated:' line")
    if "../index.html" not in html:
        errors.append(f"{name}: missing a back link to ../index.html")


def main() -> int:
    if not INDEX.is_file():
        print("ERROR: index.html not found at repo root.", file=sys.stderr)
        return 1

    index_html = strip_comments(INDEX.read_text(encoding="utf-8"))
    linked = linked_topics(index_html)
    present = existing_topics()

    # 1 & 2: cross-check links against files on disk.
    for missing in sorted(linked - present):
        errors.append(f"index.html links topics/{missing} but the file is missing")
    for orphan in sorted(present - linked):
        errors.append(f"topics/{orphan} exists but is not linked from index.html")

    # 3: per-page structural checks.
    for name in sorted(present):
        check_topic_page(TOPICS_DIR / name)

    if errors:
        print(f"✗ {len(errors)} problem(s) found:\n")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"✓ OK — {len(present)} topic page(s), all linked and well-formed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
