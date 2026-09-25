#!/usr/bin/env python3
"""Self-tests for tests/check_site.py — prove each check catches what it claims.

Standard library only, like the validator itself:

    uv run tests/test_check_site.py        # or: python3 -m unittest discover -s tests

Every test builds a tiny topic page in memory, so nothing here touches the
real site or the network.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_site as cs  # noqa: E402  (import after the path tweak above)

SIBLINGS = {"a.html", "b.html", "c.html"}


def page(rows: str, *, updated: str = "2026-09-25", extra: str = "") -> str:
    """A minimal, valid topic page wrapping the given resource rows."""
    return f"""<!DOCTYPE html><html><head><link rel="stylesheet" href="../styles.css" /></head>
<body><a class="site-title" href="../index.html">Home</a>
<main><a class="back-link" href="../index.html">← All topics</a>
<h1>Topic</h1><p class="last-updated">Last updated: {updated}</p>
{extra}
<ul class="resource-list">{rows}</ul></main></body></html>"""


EXTERNAL_ROW = """<li class="resource-item">
  <a class="res-title" href="https://example.org/book" target="_blank" rel="noopener">A Book</a>
  <span class="res-source">— Someone (2024)</span>
  <span class="level" data-level="beginner">Beginner</span>
  <p class="resource-note">Good. Free copy <a href="https://example.org/free" target="_blank" rel="noopener">here</a>.</p>
</li>"""

CROSS_ROW = """<li class="resource-item">
  <a class="res-title" href="b.html">Topic B</a>
  <span class="res-source">— on this site</span>
  <p class="resource-note">Where B takes you next.</p>
</li>"""


def problems(html: str, name: str = "topics/a.html") -> list[str]:
    return cs.check_page(name, html, SIBLINGS)


class OfflineChecks(unittest.TestCase):
    def test_valid_page_has_no_problems(self) -> None:
        self.assertEqual(problems(page(EXTERNAL_ROW + CROSS_ROW)), [])

    def test_external_title_link_needs_target_and_rel(self) -> None:
        row = EXTERNAL_ROW.replace(' target="_blank" rel="noopener">A Book', ">A Book")
        self.assertTrue(any("target=\"_blank\"" in p and "example.org/book" in p for p in problems(page(row))))

    def test_link_nested_in_note_is_checked_too(self) -> None:
        row = EXTERNAL_ROW.replace('free" target="_blank" rel="noopener"', 'free" target="_blank"')
        self.assertTrue(any('rel="noopener"' in p and "example.org/free" in p for p in problems(page(row))))

    def test_cross_link_must_not_open_new_tab(self) -> None:
        row = CROSS_ROW.replace('href="b.html"', 'href="b.html" target="_blank" rel="noopener"')
        self.assertTrue(any("must not set target/rel" in p for p in problems(page(row))))

    def test_cross_link_must_not_carry_level_pill(self) -> None:
        row = CROSS_ROW.replace("</span>\n", '</span>\n  <span class="level" data-level="beginner">Beginner</span>\n', 1)
        self.assertTrue(any("must not carry a level pill" in p for p in problems(page(row))))

    def test_cross_link_needs_on_this_site_source(self) -> None:
        row = CROSS_ROW.replace("— on this site", "— this site")
        self.assertTrue(any("must use the source" in p for p in problems(page(row))))

    def test_on_this_site_row_must_link_a_bare_sibling(self) -> None:
        row = CROSS_ROW.replace('href="b.html"', 'href="../topics/b.html"')
        found = problems(page(row))
        self.assertTrue(any("must link a bare sibling filename" in p for p in found))
        self.assertTrue(any("relative link must be" in p for p in found))

    def test_dot_slash_and_missing_sibling_are_rejected(self) -> None:
        self.assertTrue(any("relative link must be" in p for p in problems(page(CROSS_ROW.replace("b.html", "./b.html")))))
        self.assertTrue(any("does not exist" in p for p in problems(page(CROSS_ROW.replace("b.html", "zzz.html")))))

    def test_self_link_is_rejected(self) -> None:
        self.assertTrue(any("links to itself" in p for p in problems(page(CROSS_ROW.replace("b.html", "a.html")))))

    def test_unknown_level_value_and_mismatched_label(self) -> None:
        bad_value = EXTERNAL_ROW.replace('data-level="beginner">Beginner', 'data-level="expert">Expert')
        self.assertTrue(any("unknown data-level" in p for p in problems(page(bad_value))))
        bad_label = EXTERNAL_ROW.replace('data-level="beginner">Beginner', 'data-level="beginner">Advanced')
        self.assertTrue(any("does not match data-level" in p for p in problems(page(bad_label))))

    def test_duplicate_resource_on_one_page(self) -> None:
        self.assertTrue(any("already listed" in p for p in problems(page(EXTERNAL_ROW + EXTERNAL_ROW))))

    def test_last_updated_must_be_a_real_date(self) -> None:
        self.assertTrue(any("not a real date" in p for p in problems(page(EXTERNAL_ROW, updated="2026-13-40"))))
        self.assertTrue(any("not YYYY-MM-DD" in p for p in problems(page(EXTERNAL_ROW, updated="Sept 2026"))))

    def test_example_markup_inside_comments_is_ignored(self) -> None:
        commented = '<!-- <a class="res-title" href="./nope.html">x</a> <a href="http://x.org">y</a> -->'
        self.assertEqual(problems(page(EXTERNAL_ROW, extra=commented)), [])

    def test_missing_skeleton_pieces_are_reported(self) -> None:
        found = problems("<html><body><p>no skeleton</p></body></html>")
        for piece in ("styles.css", "<h1>", "Last updated", "back link"):
            self.assertTrue(any(piece in p for p in found), piece)


class Reciprocity(unittest.TestCase):
    def test_one_way_link_is_reported(self) -> None:
        found = cs.check_reciprocity({"a.html": {"b.html"}, "b.html": set()})
        self.assertEqual(found, ["topics/a.html links b.html, but topics/b.html does not link back"])

    def test_symmetric_but_incomplete_family_is_fine(self) -> None:
        # a–b and b–c linked both ways, a–c not linked at all: symmetry, not completeness.
        graph = {"a.html": {"b.html"}, "b.html": {"a.html", "c.html"}, "c.html": {"b.html"}}
        self.assertEqual(cs.check_reciprocity(graph), [])

    def test_cross_link_targets_reads_only_sibling_rows(self) -> None:
        self.assertEqual(cs.cross_link_targets(cs.parse_page(page(EXTERNAL_ROW + CROSS_ROW))), {"b.html"})


class OnlineHelpers(unittest.TestCase):
    """The pure decision helpers behind --online; no network involved."""

    def test_recycled_url_with_unrelated_title_is_flagged(self) -> None:
        # The two real cases from the 2026-09-25 review: recycled URLs showing other content.
        beeple = ("Beeple, Everydays: The First 5000 Days", "— Christie's (2021)")
        self.assertFalse(cs.titles_match(*beeple, "Château Lafite-Rothschild 1990 | Christie's"))
        self.assertTrue(cs.titles_match(*beeple, "Beeple (b. 1981), EVERYDAYS: THE FIRST 5000 DAYS | Christie's"))
        boden = ("Banking On It: How I Disrupted an Industry", "— Anne Boden, Penguin (2020)")
        self.assertFalse(cs.titles_match(*boden, "Dresden"))
        self.assertTrue(cs.titles_match(*boden, "Banking On It"))

    def test_short_brand_titles_are_not_false_alarms(self) -> None:
        # Seen as noise in the first --online run: brand names diluted by the source text.
        self.assertTrue(cs.titles_match("CryptoZombies", "— Loom Network", "#1 Solidity Tutorial | CryptoZombies"))
        self.assertTrue(cs.titles_match("Applying ML", "— Eugene Yan", "ApplyingML - Papers, Guides, and Interviews"))
        self.assertTrue(cs.titles_match("CS231n Course Notes", "— Stanford", "CS231n Deep Learning for Computer Vision"))

    def test_same_site_ignores_www_and_path_changes(self) -> None:
        self.assertTrue(cs.same_site("https://ethereum.org/en/dao/", "https://ethereum.org/dao/"))
        self.assertTrue(cs.same_site("http://www.example.org/a", "https://example.org/b"))
        self.assertFalse(cs.same_site("https://docs.makerdao.com/", "https://developers.skyeco.com/"))

    def test_http_error_classification(self) -> None:
        self.assertEqual(cs.classify_http_error(404, "")[0], "FAIL")
        self.assertEqual(cs.classify_http_error(410, "")[0], "FAIL")
        self.assertEqual(cs.classify_http_error(403, "<title>Just a moment...</title>")[0], "SKIP")
        self.assertEqual(cs.classify_http_error(429, "")[0], "SKIP")
        self.assertEqual(cs.classify_http_error(503, "")[0], "ERROR")
        # A redirect loop (urllib reports it as the 3xx) is a bot/cookie symptom, not a dead page.
        self.assertEqual(cs.classify_http_error(302, "")[0], "SKIP")

    def test_youtube_and_github_routing(self) -> None:
        self.assertIsNotNone(cs.youtube_oembed_url("https://www.youtube.com/watch?v=bBC-nXj3Ng4"))
        self.assertIsNotNone(cs.youtube_oembed_url("https://www.youtube.com/playlist?list=PL123"))
        self.assertIsNone(cs.youtube_oembed_url("https://www.youtube.com/@berkeley-cs188"))
        self.assertEqual(cs.github_repo("https://github.com/karpathy/nanoGPT"), "karpathy/nanoGPT")
        self.assertIsNone(cs.github_repo("https://github.com/karpathy/nanoGPT/tree/master/data"))
        self.assertIsNone(cs.github_repo("https://gist.github.com/x/y"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
