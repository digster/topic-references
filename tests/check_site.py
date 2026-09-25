#!/usr/bin/env python3
"""Dev-only structural validator for the Topic References static site.

This is NOT part of the site and is never shipped — it just gives a quick
sanity check that the hand-maintained links stay consistent. It uses only the
Python standard library, so it runs anywhere:

    uv run tests/check_site.py            # offline checks (fast; what CI should run)
    uv run tests/check_site.py --online   # also fetch every external link (slow)

Offline checks (always run):
  1. Every topics/<slug>.html is linked from index.html (no orphan pages).
  2. Every topic link in index.html points to a file that exists (no dead links).
  3. Each topic page has the expected skeleton: links ../styles.css, has an
     <h1>, a "Last updated:" line holding a real YYYY-MM-DD date, and a back
     link to the index.
  4. Every external link — including links nested inside a resource note —
     opens in a new tab: target="_blank" rel="noopener".
  5. Every relative link is either ../index.html or a bare sibling filename
     that exists in topics/ (never ./slug.html or ../topics/slug.html).
  6. Cross-link rows follow the CLAUDE.md contract: bare sibling href, no
     target/rel, "— on this site" as the source, and no level pill.
  7. Cross-links are reciprocal: if page A links to sibling B, B links back.
  8. Level pills use data-level beginner|intermediate|advanced, and the label
     text matches the value.
  9. No resource URL is listed twice on the same page.

Online mode (--online) additionally fetches every unique external URL and
sorts the results into:
  FAIL   definitely broken — 404/410, a host that no longer resolves, a removed
         YouTube video, a missing GitHub repo. Makes the exit code 1.
  ERROR  could not connect or timed out; may be transient — recheck by hand.
  WARN   worth a human look — redirected to another site, or a 200 whose page
         title shares almost nothing with the listed title (how a recycled URL
         that now shows *different content* shows up; a status check alone
         passes it).
  SKIP   unverifiable from a script — bot walls (Cloudflare challenges,
         403/429 access blocks). Check these in a browser.
YouTube links are checked through the oEmbed endpoint and GitHub repos through
`git ls-remote`, because both hosts block scripted page requests.

Exit code is 0 when everything passes, 1 otherwise — handy for CI later.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html as html_lib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

# Resolve paths relative to the repo root (this file lives in tests/).
ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
TOPICS_DIR = ROOT / "topics"

# Matches HTML comment blocks so example markup inside <!-- ... --> (e.g. the
# `topics/<slug>.html` pattern documented in index.html) is not mistaken for a
# real link or element.
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)

# The source text that marks a row as an internal cross-link (CLAUDE.md).
ON_THIS_SITE = "— on this site"
LEVELS = {"beginner", "intermediate", "advanced"}
# A bare sibling filename, e.g. "machine-learning.html" — no directories.
SIBLING_RE = re.compile(r"^[a-z0-9-]+\.html$")


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


# --------------------------------------------------------------------------
# Page parsing
# --------------------------------------------------------------------------


@dataclass
class Anchor:
    """One <a> element on a topic page."""

    href: str
    target: str
    rel: str
    line: int


@dataclass
class Item:
    """One <li class="resource-item"> row."""

    line: int
    title: str = ""
    href: str = ""
    target: str = ""
    rel: str = ""
    source: str = ""
    level: str | None = None  # data-level value; None when the row has no pill
    level_label: str = ""


@dataclass
class Page:
    """What the checks need to know about a topic page."""

    anchors: list[Anchor] = field(default_factory=list)
    items: list[Item] = field(default_factory=list)
    updated: str = ""


class _PageParser(HTMLParser):
    """Collect every anchor and every resource row from a topic page.

    Resource rows never nest, so a flag plus the currently captured field is
    enough state; comments are ignored by HTMLParser itself.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.page = Page()
        self._item: Item | None = None
        self._capture: str | None = None  # "title" | "source" | "level" | "updated"

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: (v or "") for k, v in attrs}
        classes = a.get("class", "").split()
        line = self.getpos()[0]
        if tag == "a":
            self.page.anchors.append(Anchor(a.get("href", ""), a.get("target", ""), a.get("rel", ""), line))
        if tag == "p" and "last-updated" in classes:
            self._capture = "updated"
        elif tag == "li" and "resource-item" in classes:
            self._item = Item(line=line)
        elif self._item is not None:
            if tag == "a" and "res-title" in classes:
                self._item.href = a.get("href", "")
                self._item.target = a.get("target", "")
                self._item.rel = a.get("rel", "")
                self._capture = "title"
            elif tag == "span" and "res-source" in classes:
                self._capture = "source"
            elif tag == "span" and "level" in classes:
                self._item.level = a.get("data-level", "")
                self._capture = "level"

    def handle_endtag(self, tag: str) -> None:
        if tag == "li" and self._item is not None:
            self.page.items.append(self._item)
            self._item = None
            self._capture = None
        elif (tag == "a" and self._capture == "title") or (
            tag in ("span", "p") and self._capture in ("source", "level", "updated")
        ):
            self._capture = None

    def handle_data(self, data: str) -> None:
        if self._capture == "updated":
            self.page.updated += data
        elif self._item is not None and self._capture == "title":
            self._item.title += data
        elif self._item is not None and self._capture == "source":
            self._item.source += data
        elif self._item is not None and self._capture == "level":
            self._item.level_label += data


def parse_page(html: str) -> Page:
    """Parse a topic page into anchors, resource rows and its date line."""
    parser = _PageParser()
    parser.feed(strip_comments(html))
    page = parser.page
    for it in page.items:
        it.title = " ".join(it.title.split())
        it.source = " ".join(it.source.split())
        it.level_label = " ".join(it.level_label.split())
    page.updated = " ".join(page.updated.split())
    return page


def is_external(href: str) -> bool:
    return href.startswith(("http://", "https://"))


def is_cross_link(item: Item) -> bool:
    """A row is an internal cross-link if it links a sibling or says so."""
    return bool(SIBLING_RE.match(item.href)) or item.source == ON_THIS_SITE


# --------------------------------------------------------------------------
# Offline checks — pure functions returning lists of problems
# --------------------------------------------------------------------------


def check_skeleton(name: str, html: str) -> list[str]:
    """Check 3: the page skeleton every topic page shares."""
    problems: list[str] = []
    body = strip_comments(html)
    if "../styles.css" not in body:
        problems.append(f"{name}: missing link to ../styles.css")
    if not re.search(r"<h1[^>]*>.*?\S.*?</h1>", body, re.S):
        problems.append(f"{name}: missing a non-empty <h1> title")
    if "Last updated:" not in body:
        problems.append(f"{name}: missing 'Last updated:' line")
    if "../index.html" not in body:
        problems.append(f"{name}: missing a back link to ../index.html")
    return problems


def check_page(name: str, html: str, siblings: set[str]) -> list[str]:
    """Checks 3–6, 8 and 9 for one topic page.

    `siblings` is the set of topic filenames that exist, so cross-links to a
    page that doesn't exist are caught here rather than 404ing in a browser.
    """
    problems = check_skeleton(name, html)
    page = parse_page(html)
    own = name.rsplit("/", 1)[-1]

    # 3 (date): "Last updated:" must hold a real calendar date.
    m = re.fullmatch(r"Last updated:\s*(\d{4}-\d{2}-\d{2})", page.updated)
    if page.updated and not m:
        problems.append(f"{name}: 'Last updated' is not YYYY-MM-DD: {page.updated!r}")
    elif m:
        try:
            dt.date.fromisoformat(m.group(1))
        except ValueError:
            problems.append(f"{name}: 'Last updated' is not a real date: {m.group(1)}")

    # 4 & 5: every anchor, wherever it sits on the page.
    for a in page.anchors:
        where = f"{name}:{a.line}"
        if is_external(a.href):
            if a.target != "_blank" or "noopener" not in a.rel.split():
                problems.append(f'{where}: external link needs target="_blank" rel="noopener": {a.href}')
        elif a.href == "../index.html":
            continue
        elif SIBLING_RE.match(a.href):
            if a.href not in siblings:
                problems.append(f"{where}: links sibling {a.href}, which does not exist")
            elif a.href == own:
                problems.append(f"{where}: page links to itself")
        else:
            problems.append(f"{where}: relative link must be ../index.html or a bare sibling filename: {a.href!r}")

    seen: dict[str, int] = {}
    for it in page.items:
        where = f"{name}:{it.line}"
        # 6: the four ways a cross-link row differs from an external row.
        if is_cross_link(it):
            if not SIBLING_RE.match(it.href):
                problems.append(f"{where}: '{ON_THIS_SITE}' row must link a bare sibling filename, not {it.href!r}")
            if it.source != ON_THIS_SITE:
                problems.append(f"{where}: cross-link to {it.href} must use the source '{ON_THIS_SITE}'")
            if it.target or it.rel:
                problems.append(f"{where}: cross-link to {it.href} must not set target/rel (opens in the same tab)")
            if it.level is not None:
                problems.append(f"{where}: cross-link to {it.href} must not carry a level pill")
        # 8: pills drive the colour, so the value must be one CSS knows.
        if it.level is not None:
            if it.level not in LEVELS:
                problems.append(f"{where}: unknown data-level {it.level!r} on {it.title!r}")
            elif it.level_label != it.level.capitalize():
                problems.append(
                    f"{where}: level label {it.level_label!r} does not match data-level {it.level!r} on {it.title!r}"
                )
        # 9: the same resource listed twice on one page.
        if it.href:
            if it.href in seen:
                problems.append(f"{where}: {it.href} is already listed on line {seen[it.href]}")
            else:
                seen[it.href] = it.line
    return problems


def cross_link_targets(page: Page) -> set[str]:
    """The sibling filenames a page links to from its resource rows."""
    return {it.href for it in page.items if SIBLING_RE.match(it.href)}


def check_reciprocity(graph: dict[str, set[str]]) -> list[str]:
    """Check 7: every cross-link A → B needs a matching B → A.

    Derived from the actual link graph rather than a hardcoded family list, so
    it keeps working as topics are added (ARCHITECTURE.md: symmetry, not
    completeness, is the rule).
    """
    problems: list[str] = []
    for src in sorted(graph):
        for dst in sorted(graph[src]):
            if dst in graph and src not in graph[dst]:
                problems.append(f"topics/{src} links {dst}, but topics/{dst} does not link back")
    return problems


# --------------------------------------------------------------------------
# Online mode
# --------------------------------------------------------------------------

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
# Phrases that identify a bot challenge rather than the real page.
CHALLENGE_RE = re.compile(
    r"just a moment|attention required|access denied|client challenge|checking your browser"
    r"|captcha|cf-chl|verify you are human|establishing a secure connection",
    re.I,
)
STOPWORDS = set(
    "the a an of and to in on for with by from at is are how what why your you it its as or be this that".split()
)
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)


@dataclass
class Result:
    url: str
    status: str  # OK | WARN | SKIP | ERROR | FAIL
    detail: str
    pages: list[str] = field(default_factory=list)


def title_words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS and len(w) > 2}


def title_overlap(listed: str, live: str) -> float:
    """Share of words the listed text and the live <title> have in common."""
    a, b = title_words(listed), title_words(live)
    if not a or not b:
        return 1.0  # nothing to compare — don't flag
    return len(a & b) / min(len(a), len(b))


def titles_match(title: str, source: str, live: str, threshold: float = 0.25) -> bool:
    """Does a live page <title> plausibly belong to the listed resource?

    Takes the better of title-only and title+source overlap — source text such as
    "— Loom Network" would otherwise dilute a short brand-name title — and also
    accepts a squashed-substring match ("ApplyingML" contains "Applying ML").
    Real wrong-content cases score near zero (the recycled Christie's lot: 0.2).
    """
    squash = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())  # noqa: E731
    if title and live and (squash(title) in squash(live) or squash(live) in squash(title)):
        return True
    return max(title_overlap(title, live), title_overlap(f"{title} {source}", live)) >= threshold


def same_site(url_a: str, url_b: str) -> bool:
    """True when two URLs share a host (ignoring a leading www.)."""
    host = lambda u: urllib.parse.urlparse(u).netloc.lower().removeprefix("www.")  # noqa: E731
    return host(url_a) == host(url_b)


def youtube_oembed_url(url: str) -> str | None:
    """oEmbed endpoint for a YouTube video/playlist URL, else None."""
    p = urllib.parse.urlparse(url)
    if p.netloc.lower().removeprefix("www.") in ("youtube.com", "youtu.be") and (
        p.path in ("/watch", "/playlist") or p.netloc.endswith("youtu.be")
    ):
        return "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(url, safe="")
    return None


def github_repo(url: str) -> str | None:
    """'owner/repo' for a GitHub repository root URL, else None."""
    p = urllib.parse.urlparse(url)
    parts = [s for s in p.path.split("/") if s]
    if p.netloc.lower() == "github.com" and len(parts) == 2:
        return f"{parts[0]}/{parts[1]}"
    return None


def classify_http_error(code: int, body: str) -> tuple[str, str]:
    """Map an HTTP error status (plus its body) to a result status."""
    if CHALLENGE_RE.search(body):
        return "SKIP", f"HTTP {code} bot challenge — check in a browser"
    if code in (404, 410):
        return "FAIL", f"HTTP {code}"
    if code in (401, 403, 429, 451):
        return "SKIP", f"HTTP {code} access blocked for scripts — check in a browser"
    return ("ERROR" if code >= 500 else "FAIL"), f"HTTP {code}"


def host_resolves(url: str) -> bool:
    try:
        socket.getaddrinfo(urllib.parse.urlparse(url).hostname or "", 443)
        return True
    except socket.gaierror as exc:
        return exc.errno not in (socket.EAI_NONAME, getattr(socket, "EAI_NODATA", socket.EAI_NONAME))


def _fetch(url: str, timeout: int = 30) -> tuple[int, str, str, str]:
    """GET a URL (following redirects) → (status, final_url, content_type, body_prefix)."""
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read(400_000).decode("utf-8", "replace")
        return resp.status, resp.geturl(), resp.headers.get("Content-Type", ""), body


def check_url(url: str, listed: tuple[str, str]) -> Result:
    """Fetch one external URL and classify it (see the module docstring)."""
    oembed = youtube_oembed_url(url)
    if oembed:
        try:
            _, _, _, body = _fetch(oembed, timeout=20)
            data = json.loads(body)
            return Result(url, "OK", f"YouTube: {data.get('title', '')!r} by {data.get('author_name', '')}")
        except urllib.error.HTTPError as exc:
            if exc.code in (400, 404):
                return Result(url, "FAIL", f"YouTube oEmbed HTTP {exc.code} — video removed or private")
            if exc.code in (401, 403, 429):  # 401 = owner disabled embedding; the video may still exist
                return Result(url, "SKIP", f"YouTube oEmbed HTTP {exc.code} — check in a browser")
            return Result(url, "ERROR", f"YouTube oEmbed HTTP {exc.code}")
        except (OSError, ValueError) as exc:
            return Result(url, "ERROR", f"YouTube oEmbed: {exc}")

    repo = github_repo(url)
    if repo and shutil.which("git"):
        try:
            proc = subprocess.run(
                ["git", "ls-remote", "--exit-code", f"https://github.com/{repo}", "HEAD"],
                capture_output=True, text=True, timeout=45,
                env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},  # never block on a credential prompt
            )
        except subprocess.TimeoutExpired:
            return Result(url, "ERROR", "git ls-remote timed out")
        if proc.returncode == 0:
            return Result(url, "OK", "GitHub repo exists (git ls-remote)")
        if "not found" in proc.stderr.lower():
            return Result(url, "FAIL", "GitHub repo not found")
        return Result(url, "ERROR", f"git ls-remote: {proc.stderr.strip()[:120]}")

    try:
        status, final, ctype, body = _fetch(url)
    except urllib.error.HTTPError as exc:
        try:
            err_body = exc.read(200_000).decode("utf-8", "replace")
        except OSError:
            err_body = ""
        st, detail = classify_http_error(exc.code, err_body)
        return Result(url, st, detail)
    except (urllib.error.URLError, OSError) as exc:
        if not host_resolves(url):
            return Result(url, "FAIL", "host no longer resolves (DNS)")
        reason = getattr(exc, "reason", exc)
        return Result(url, "ERROR", f"could not connect: {reason}")

    m = TITLE_RE.search(body)
    live_title = " ".join(html_lib.unescape(m.group(1)).split()) if m else ""
    if status == 202 or CHALLENGE_RE.search(live_title):
        return Result(url, "SKIP", f"HTTP {status} bot challenge — check in a browser")
    if not same_site(url, final):
        return Result(url, "WARN", f"redirected to another site: {final}")
    title, source = listed
    if "html" in ctype and title and live_title and not titles_match(title, source, live_title):
        return Result(url, "WARN", f"page title {live_title[:90]!r} shares little with the listed {title[:60]!r}")
    return Result(url, "OK", live_title[:90] or ctype)


def run_online(pages: dict[str, Page], workers: int = 8) -> int:
    """Check every unique external URL; print a grouped report; return #FAIL."""
    listed: dict[str, tuple[str, str]] = {}  # url -> (listed title, source)
    where: dict[str, set[str]] = {}
    for name, page in pages.items():
        for it in page.items:
            if is_external(it.href):
                listed.setdefault(it.href, (it.title, it.source))
        for a in page.anchors:
            if is_external(a.href):
                listed.setdefault(a.href, ("", ""))  # note links have no listed title to compare
                where.setdefault(a.href, set()).add(name)

    print(f"\nChecking {len(listed)} external URLs (this takes a few minutes)…")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda u: check_url(u, listed[u]), sorted(listed)))
    for r in results:
        r.pages = sorted(where.get(r.url, ()))

    counts = {s: 0 for s in ("OK", "WARN", "SKIP", "ERROR", "FAIL")}
    for r in results:
        counts[r.status] += 1
    for status in ("FAIL", "ERROR", "WARN", "SKIP"):
        group = [r for r in results if r.status == status]
        if group:
            print(f"\n{status} ({len(group)}):")
            for r in group:
                print(f"  - {r.url}\n      {r.detail}  [{', '.join(r.pages)}]")
    print("\n" + "  ".join(f"{k}: {v}" for k, v in counts.items()))
    return counts["FAIL"]


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--online", action="store_true", help="also fetch every external link (slow)")
    args = ap.parse_args(argv)

    if not INDEX.is_file():
        print("ERROR: index.html not found at repo root.", file=sys.stderr)
        return 1

    errors: list[str] = []
    index_html = strip_comments(INDEX.read_text(encoding="utf-8"))
    linked = linked_topics(index_html)
    present = existing_topics()

    # 1 & 2: cross-check index links against files on disk.
    for missing in sorted(linked - present):
        errors.append(f"index.html links topics/{missing} but the file is missing")
    for orphan in sorted(present - linked):
        errors.append(f"topics/{orphan} exists but is not linked from index.html")

    # 3–6, 8, 9 per page; 7 across pages.
    pages: dict[str, Page] = {}
    graph: dict[str, set[str]] = {}
    for fname in sorted(present):
        html = (TOPICS_DIR / fname).read_text(encoding="utf-8")
        errors += check_page(f"topics/{fname}", html, present)
        page = pages[f"topics/{fname}"] = parse_page(html)
        graph[fname] = cross_link_targets(page)
    errors += check_reciprocity(graph)

    if errors:
        print(f"✗ {len(errors)} problem(s) found:\n")
        for e in errors:
            print(f"  - {e}")
    else:
        edges = sum(len(v) for v in graph.values()) // 2
        print(f"✓ OK — {len(present)} topic page(s), all linked and well-formed; {edges} reciprocal cross-link pair(s).")

    failed = run_online(pages) if args.online else 0
    return 1 if errors or failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
