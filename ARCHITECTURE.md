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
│   ├── check_site.py         # dev-only structure + link checker (stdlib, `uv run`; `--online`)
│   └── test_check_site.py    # self-tests for the checker
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

### Cross-links reuse the resource row, not a new component
Topic pages link to each other from the **end of their 🔗 Further Reading section**, as ordinary
`.resource-item` rows with `— on this site` as the source. There is deliberately no
`.related-topics` block and no dedicated CSS: a sibling page *is* a further-reading resource, so it
gets the same visual weight as an external one and the stylesheet stays unchanged.

Two properties follow from that and are easy to break:

- Internal links use a **bare sibling filename** (`href="transformers.html"`) and carry **no**
  `target="_blank" rel="noopener"` — they open in the same tab, which is the one attribute-level
  difference from every other link on the site. They also carry no level pill.
- Within a family of closely related topics, cross-links are kept **symmetric** — if A links to B,
  B links back to A. Unrelated pages stay isolated; symmetry is a rule *inside* a family, not a
  requirement that every page link to every other.

There are currently two families, and they are shaped differently on purpose:

- The six **AI** pages (`artificial-intelligence`, `deep-learning`, `machine-learning`,
  `transformers`, `large-language-models`, `generative-ai-beyond-llms`) form a **complete graph** —
  five links each. Every pair really is a next step for the other, so nothing had to be left out.
- The seven **crypto** pages (`blockchain-and-cryptocurrency`, `ethereum-and-smart-contracts`,
  `decentralized-finance`, `nfts-and-digital-ownership`, `layer-2-and-scaling`,
  `zero-knowledge-proofs`, `crypto-economics-and-daos`) are **deliberately not complete** — 17 of
  the 21 possible pairs. `blockchain-and-cryptocurrency` is the hub and links to all six others;
  the rest are wired only where one page is genuinely the next step from the other. ZK↔DeFi,
  ZK↔NFTs, ZK↔DAOs and L2↔DAOs are omitted for that reason.

**Symmetry is not the same as completeness.** A family being cross-linked never means every page in
it links to every other — forcing the missing edges would put rows on the page that no reader
actually wants, which is the same failure as padding a resource section. Add an edge only when
`CLAUDE.md`'s test is met ("actually a next step for each other — a shared field is not enough"),
then make it reciprocal.

Families are also not sealed off from each other: `decentralized-finance` ↔ `starting-a-new-bank`
is a single edge between the crypto family and an otherwise isolated page, because each really is
the next step from the other. `data-structures-and-algorithms` and
`structuralism-and-post-structuralism` remain fully isolated.

`structuralism-and-post-structuralism` is worth calling out because it is the site's first
**humanities** topic, and it shows the taxonomy is domain-agnostic rather than tech-only: the same
seven sections, level pills and prose conventions carry a philosophy page without modification.
It is isolated on purpose. There is a tempting line from Saussure's "language is a system of
differences" to the distributional semantics behind word embeddings, but a reader studying
structuralism is not thereby ready for `large-language-models`, and vice versa — an intellectual
resemblance is not a next step, so no edge was added in either direction.

`tests/check_site.py` enforces both properties. It parses every topic page, checks each
cross-link row's four differences from an external row, and derives reciprocity from the actual
link graph rather than a hardcoded family list — so a new family, or a new bridge like
DeFi ↔ bank, is checked without editing the validator. It reports the pair count on success
(33 as of 2026-09-25: 15 AI, 17 crypto, 1 bridge).

### Link health is checked by title, not just by status code
`tests/check_site.py --online` fetches every external URL, but a `200` is treated as necessary,
not sufficient. The 2026-09-25 review found two links that returned a healthy `200` while
showing unrelated content — a Christie's lot URL recycled for a wine lot, and a Penguin URL whose
ISBN pointed at a different book. The checker therefore compares each live page `<title>` with
the listed resource title and flags low overlap as `WARN`, alongside cross-site redirects.

It also refuses to call a link dead on weak evidence. Hosts that block scripts are `SKIP`, not
failures: YouTube is verified through its oEmbed endpoint and GitHub repositories through
`git ls-remote`, because both reject scripted page loads; Cloudflare-style challenges (and
`global.oup.com`'s empty `202`) are listed for a browser check. A connection error only becomes
`FAIL` when the host genuinely no longer resolves in DNS, which is how `docs.circom.io` went.
Online mode is opt-in because it is slow and needs the network; the offline checks are what
every change should pass.

### Landing page card order: clusters, not alphabetical
Cards in `#topic-grid` are ordered so that **related topics sit next to each other**. The grid was
alphabetical until 2026-09-15; alphabetical order scattered the families (`Deep Learning` sat
between `Decentralized Finance` and `Ethereum`, and the six AI pages were split across the whole
grid), which made a browsable index read as an arbitrary list.

The clustering is **read off the cross-link graph above rather than invented** — a page belongs
beside the pages it links to. Current order:

| # | Cluster | Pages |
|---|---|---|
| 1 | AI & machine learning | `artificial-intelligence` → `machine-learning` → `deep-learning` → `transformers` → `large-language-models` → `generative-ai-beyond-llms` |
| 2 | Crypto & blockchain | `blockchain-and-cryptocurrency` → `ethereum-and-smart-contracts` → `layer-2-and-scaling` → `zero-knowledge-proofs` → `nfts-and-digital-ownership` → `crypto-economics-and-daos` → `decentralized-finance` |
| 3 | Traditional finance | `starting-a-new-bank` |
| 4 | Standalone | `data-structures-and-algorithms`, `structuralism-and-post-structuralism` |

Within a cluster the order is a **learning path** — the parent field first, then what builds on it
— mirroring how resources are ordered inside a topic page. Two adjacencies are load-bearing and
should survive future edits: `layer-2-and-scaling` next to `zero-knowledge-proofs` (the strongest
edge in the crypto family), and `decentralized-finance` immediately before `starting-a-new-bank`,
which puts the site's only cross-family edge side by side on the page.

Three constraints shaped the implementation:

- **Grouping is source order only — there are no per-cluster containers.** The grid is
  `repeat(auto-fill, minmax(250px, 1fr))` over an 832px content column, so it renders 3 columns on
  desktop, 2 when narrower and 1 below 540px, with cards flowing in document order. Source
  adjacency is the only thing that holds a cluster together at every width; cluster boundaries are
  marked by HTML comments, which create no boxes and so cannot disturb the layout.
- **No headings inside the grid.** A `<h2>` in `#topic-grid` would become a grid item, and the
  search filter only toggles `.topic-card` — so filtering would strand headings above hidden
  cards. Fixing that would mean editing the inline `<script>`, which `CLAUDE.md` forbids. A flat,
  reordered grid gets the grouping for free and keeps the filter generic.
- **The filter is order-independent**, indexing cards positionally (`cards[i]` ↔ `haystacks[i]`),
  so reordering the DOM reorders both together. A side benefit: filtered results now come back in
  cluster order too — searching `attention` lists Deep Learning, Transformers, LLMs in that order.

The group sizes happen to land well on the grid: at 3 columns the AI cluster fills rows 1–2
exactly, and at 2 columns **every** cluster boundary falls on a row boundary. That is a bonus, not
a constraint to preserve — adding a topic will shift it, and linear adjacency is what matters.

## Data flow

There is none at runtime beyond the search filter:

1. Browser loads `index.html` + `styles.css`.
2. The inline script indexes the static cards (text + `data-tags`) once on load.
3. Typing in the search box hides/shows cards and updates the count — pure DOM manipulation.
4. Clicking a card navigates to a static `topics/<slug>.html` page.

## Conventions
- **Slugs** are kebab-case; topic file = `topics/<slug>.html`.
- **Topic cards** are **grouped by cluster** in `index.html`, not alphabetical — see
  *Landing page card order* below.
- **External links** use `target="_blank" rel="noopener"`.
- **Internal cross-links** use a bare sibling filename and *no* `target`/`rel` — same tab.
- **Level pills** use `data-level="beginner|intermediate|advanced"` (drives pill color).
- Favicon is an inline SVG emoji data-URI in each page's `<head>` — no asset files.

## Adding/changing things
- New topic → follow `CLAUDE.md` (research & verify links, fill the template, add a card).
- New resource section type or layout change → update `templates/topic-template.html`,
  `styles.css`, and this file together so they stay in sync.
- Keep `tests/check_site.py` passing (`uv run tests/check_site.py`); run `--online` when adding or
  refreshing resources, and `uv run tests/test_check_site.py` after changing the checker itself.
