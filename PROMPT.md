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

---

## 2026-06-26 — Remove homepage footer text

> Remove this text from the footer. _(the "Built as a static site… see CLAUDE.md"
> line in the landing-page footer)_

Outcome: removed the entire `<footer class="site-footer">` block from `index.html`
(rather than leaving an empty bordered band, which would look like a glitch in the
framed layout). The card grid's `padding-bottom` keeps breathing room before the
frame's bottom border. Topic-page footers (the "← Back to all topics" link) and the
shared `.site-footer` CSS are untouched. Verified in a browser.

---

## 2026-07-28 — Add topic

> Add a new topic on data structures and algorithms.

(Asked which lens to lead with — CS fundamentals, interview prep, or competitive
programming. The question went unanswered, so the page uses the **balanced**
framing, matching the "all three" choice made for the bank topic.)

Outcome: added `topics/data-structures-and-algorithms.html` (25 web-verified
resources across all seven sections, ordered as a learning path) and an
alphabetically-first card in `index.html`. Core sections lead with CS
fundamentals; practice platforms sit in Tools, and contest/advanced material in
Further Reading. Dropped Hoare's *Quicksort* (paywalled), the Stanford Coursera
specialization (not free — linked Roughgarden's own free video site instead), and
two unverifiable single-page apps. Verified with `check_site.py` and 21 Playwright
browser checks.

---

## 2026-07-28 — Paid resources are allowed

> Regarding Stanford's Coursera Algorithms Specialization, If a resource is good
> enough, it should be mentioned even though it's paid. So add it as a resource
> and also update this directive in the project's claude file.

Outcome: rewrote the rule in `CLAUDE.md` — golden rule 3 no longer drops
"paywalled-with-no-value" links, and a new golden rule 4 says paid resources
belong on the page when they're genuinely among the best, with the cost
disclosed in the note and a free equivalent linked alongside where one exists.
The research step in the workflow was reworded to match: prefer a free version
of the *same* resource, but never exclude a resource for being paid. Applied to
`topics/data-structures-and-algorithms.html`: added the Stanford/Roughgarden
Coursera specialization (Courses) and Hoare's *Quicksort* (Papers) — the two
resources previously dropped on paywall grounds — each flagged as paid in its
note. Page now carries 27 resources.

---

## 2026-07-29 — Redo the first two topic pages

> The first two topics in the repo were done in a non opus 5 model. I want to
> redo them. It's also fine if resources from the previous version get repeated.

(Asked three scoping questions. Answers: Transformers → **foundations + modern
stack**; Starting a New Bank → **options 1 and 4 blended**, i.e. a
jurisdiction-agnostic business core with the US as the worked example plus UK/EU
and India pointers; depth → **match the DSA page**.)

Outcome: full rewrites of `topics/transformers.html` (32 resources) and
`topics/starting-a-new-bank.html` (32 resources) from the template, every URL
re-verified live. The Transformers page now carries the post-2017 architecture
(RoPE, FlashAttention, MoE, scaling laws, interpretability, Mamba) alongside the
fundamentals; the bank page leads with economics that hold in any jurisdiction
and adds UK (PRA/FCA New Bank Start-up Unit) and India (RBI) primary sources next
to the US ones. Both landing-page cards refreshed with new descriptions and
`data-tags`. Fixed two rotten links inherited from the old pages (a 404 Coursera
specialization, a plain-`http://` Annotated Transformer URL).

---

## 2026-07-29 — Add topic: Machine Learning

> Add a topic on ml(machine learning).  Don't focus too much on ai, we are going
> to add it separately.

(Asked three scoping questions. Answers: deep-learning scope → **classical ML +
production/MLOps**, no DL block; theory depth → **balanced ladder** from gentle
intros to genuinely rigorous texts; card title → plain **"Machine Learning"**.)

Outcome: new `topics/machine-learning.html` with **33 resources** across all
seven sections, plus one card added to `index.html` in alphabetical position 2.
The page deliberately stays on classical, largely tabular ML and the practice of
running it in production — ISL/ESL, trees and ensembles, honest evaluation, then
Rules of ML, the hidden-technical-debt paper, Made With ML and MLOps courses.
Deep learning appears once, as a cross-link to the existing Transformers page, to
leave room for the AI topic coming separately. Three link problems found and
handled: R2D3's *A Visual Introduction to Machine Learning* was down (HTTP 522
throughout the session) and was dropped rather than shipped broken; Breiman's
*Two Cultures* turned out to be paywalled on Project Euclid, so a content-verified
free university copy is linked instead; Papers with Code is sunset (302s to
Hugging Face) and was excluded.

---

## 2026-07-29 — No dark mode

> we are not going to have dark mode for now for this site.

Outcome: settled the stale verification step that had been flagged in the two
previous sessions. `CLAUDE.md`'s "Verifying your work" section no longer tells
you to check that dark mode works — it now checks the level pills are colored
and states that the theme is deliberately fixed light, with a pointer to
`ARCHITECTURE.md`. Nothing else needed changing: `ARCHITECTURE.md` already
documented the fixed-light decision, `styles.css` has had no
`prefers-color-scheme: dark` block since the Brutalist Mono re-theme, and the
earlier `PROMPT.md` mention is a historical record that stays as written.

---

## 2026-07-29 — Add topic: Large Language Models

> Add a topic on llms in generative ai. don't focus on the non llm parts of
> generative ai, it will be added in a future topic.

(Asked three scoping questions. The picker returned empty twice — the answers
never arrived — so they were re-sent as plain text and answered `1b / 2c / 3a`:
card title → plain **"Large Language Models"**, no parenthetical; overlap with
the existing Transformers page → **self-contained, overlap freely**; emphasis →
**balanced ladder** across internals, training and application practice.)

Outcome: new `topics/large-language-models.html` with **49 resources** across all
seven sections, plus one card added to `index.html` in alphabetical position 2.
The page runs the full arc — next-token prediction, scaling laws, RLHF/DPO
alignment, prompting, chain-of-thought, RAG, agents, evals, local inference — and
states in its description that image, audio and video generation are a separate
topic still to come. Per answer 2c it deliberately repeats ~11 rows that also
appear on the Transformers page (Attention Is All You Need, GPT-3, Chinchilla,
the Illustrated Transformer, Karpathy's videos, the HF LLM Course, nanochat,
Jurafsky & Martin) so a reader landing here is never sent elsewhere for the
fundamentals; the two pages stay differently shaped, and both cross-link.

Two link problems found and handled. Stephen Wolfram's *What Is ChatGPT Doing …
and Why Does It Work?* was unreachable from this container on three attempts
(HTTP 503 via WebFetch, connection failure via curl with a browser UA) and was
dropped rather than shipped unverified. `aiengineeringbook.com` turned out to be
a **parked domain for sale** ("A Brand New Domain!"), so *AI Engineering* is
linked via Chip Huyen's own book page instead — a 200 that would have shipped a
dead link. Stochastic Parrots 403s behind Cloudflare on the ACM DOI from here, so
a content-verified free PDF is linked (confirmed 14 pages with the correct four
authors via `pypdf`) with the ACM proceedings noted in the note.
