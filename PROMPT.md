# Prompt Log

A running record of the prompts that shaped this repo. Newest entries at the bottom.

---

## 2026-06-22 — Project bootstrap

> - I want to create a repo in which, given a topic you should give me all the
>   references, further readings, videos, blogs, books, etc. as resources which
>   I can go and study further
> - Before giving all the resources, add a small description about the topic and
>   then continue with the resources.
> - The repo should be a simple HTML site without any build steps. The landing
>   index.html should link the individual topic files.
> - It will be hosted as a static GitHub site.
> - Based on this description, create a local CLAUDE project file so that when I
>   give a topic in this repo the llm understands the requirement and adds the
>   necessary content.

Outcome: scaffolded a no-build static site (`index.html` + `styles.css` +
`topics/`), a copy-paste `templates/topic-template.html`, a `CLAUDE.md` workflow
contract, supporting docs, a dev-only `tests/check_site.py`, and a seeded sample
topic page (Transformers).

---

## 2026-06-23 — Add topic

> - Add a new topic - starting a new bank.
> - Don't focus too much on the regulatory part.

(When asked which lens to lead with, the user chose "all three" — fintech/neobank
builder playbook, bank-as-a-business economics, and a light regulatory pointer.)

Outcome: added `topics/starting-a-new-bank.html` (blended overview + curated,
web-verified resources across books, a single light regulatory primary reference,
articles, videos, courses, BaaS tools, and further reading) and a linked,
alphabetically-placed card in `index.html`.

---

## 2026-06-26 — Re-theme to "Brutalist Mono"

> Update the homepage to this theme. _(supplied a reference mockup: monospace UI,
> yellow header band, heavy black headings, thick black borders, hard offset
> shadows, warm-gray frame, cobalt-blue accent)_

(When asked: chose to apply the theme **site-wide** — not homepage-only — since
`styles.css` and the header/footer are shared; and chose a **fixed light** look
with no dark-mode variant.)

Outcome: rewrote `styles.css` only — remapped the `:root` design tokens to the
brutalist palette/fonts/shadows, removed the `prefers-color-scheme: dark` block,
and restyled the structural rules (body-as-frame, yellow header, square cards with
hard offset shadows + blue hover-fill, blue uppercase result count, squared
black-bordered level pills). No HTML and no JS changed; the search filter is
untouched. Verified homepage + topic page + hover/search/mobile in a browser.
