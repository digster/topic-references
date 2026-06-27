# Architecture

A deliberately tiny static site. This document explains the structure and the **why** behind the
few decisions that matter, so future changes stay consistent.

## Big picture

```
topic-references/
├── index.html                # landing: hero + search box + card grid + inline filter JS
├── styles.css                # single shared stylesheet for ALL pages
├── topics/
│   └── <slug>.html           # one self-contained page per topic
├── templates/
│   └── topic-template.html   # skeleton copied to create each new topic page
├── tests/
│   └── check_site.py         # dev-only structural validator (stdlib, run via `uv run`)
├── CLAUDE.md                 # the workflow contract for adding topics
├── README.md / PROMPT.md / LICENSE
├── .nojekyll                 # serve files as-is on GitHub Pages
└── memory/                   # dated work summaries
```

There is **no application layer** — no server, no build, no JS framework. Pages are authored HTML
served statically. The only runtime code is one inline `<script>` in `index.html`.

## Key decisions (the "why")

### No build step
The site must be viewable by double-clicking `index.html` (`file://`) and identically when served
by GitHub Pages. That rules out anything requiring compilation, a dev server, or module bundling.
This is a hard constraint, not a preference — see `CLAUDE.md`.

### Static links, not a data manifest
The landing page lists topics as **hardcoded `<a class="topic-card">` anchors**, not by fetching a
`topics.json` at runtime. Reason: `fetch()` is blocked on the `file://` protocol, so a manifest
approach would silently break local preview. Hardcoded links work everywhere. The cost is that
adding a topic means editing `index.html` — an acceptable, explicit trade.

### Client-side search over static DOM
Search filters the cards already present in the DOM (matching the query against each card's text +
its `data-tags` attribute). Because it never fetches anything, it works offline and on Pages with
zero configuration. The filter logic is generic — it reads all `.topic-card` elements — so adding a
card requires **no JS changes**.

### One shared stylesheet + CSS custom properties
All pages link the same `styles.css`. Theming uses CSS variables defined in `:root` (colors,
hard-offset shadows, fonts, border weight), so restyling the whole site is mostly a token remap and
visual consistency is guaranteed across every topic page.

The active theme is **"Brutalist Mono"**: a monospace UI font and heavy system-sans display
headings (system stacks only — **no web fonts/CDNs**, per the no-build constraint), thick black
borders, hard offset drop shadows (solid color, zero blur), a warm-gray page framing a white
content panel (the `<body>` itself is the frame), a yellow header band, and a cobalt-blue accent
used for links, the result count, and the card-hover fill. It is a deliberate **fixed light**
statement: there is intentionally **no** `prefers-color-scheme: dark` variant, so the look is
identical in light and dark OS modes.

### Consistent topic-page anatomy
Every topic page follows the same structure (description block first, then a fixed taxonomy of
resource sections). The shape is defined once in `templates/topic-template.html` and enforced by
`CLAUDE.md`. Consistency is what makes the site feel like a trustworthy reference rather than a pile
of pages.

## Data flow

There is none at runtime beyond the search filter:

1. Browser loads `index.html` + `styles.css`.
2. The inline script indexes the static cards (text + `data-tags`) once on load.
3. Typing in the search box hides/shows cards and updates the count — pure DOM manipulation.
4. Clicking a card navigates to a static `topics/<slug>.html` page.

## Conventions
- **Slugs** are kebab-case; topic file = `topics/<slug>.html`.
- **Topic cards** are kept alphabetical in `index.html`.
- **External links** use `target="_blank" rel="noopener"`.
- **Level pills** use `data-level="beginner|intermediate|advanced"` (drives pill color).
- Favicon is an inline SVG emoji data-URI in each page's `<head>` — no asset files.

## Adding/changing things
- New topic → follow `CLAUDE.md` (research & verify links, fill the template, add a card).
- New resource section type or layout change → update `templates/topic-template.html`,
  `styles.css`, and this file together so they stay in sync.
- Keep `tests/check_site.py` passing (`uv run tests/check_site.py`).
