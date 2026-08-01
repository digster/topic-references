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
dropped — then added back on a follow-up instruction:

> You can add the most probable Wolfram's link now(based on search) and if it
> does not work, we can update it later.

Search corroborates the URL and its title, so it reads as a container
reachability problem, not link rot; it is the only row on the page not opened
end-to-end, and the page now carries 50 resources. `aiengineeringbook.com`
turned out to be
a **parked domain for sale** ("A Brand New Domain!"), so *AI Engineering* is
linked via Chip Huyen's own book page instead — a 200 that would have shipped a
dead link. Stochastic Parrots 403s behind Cloudflare on the ACM DOI from here, so
a content-verified free PDF is linked (confirmed 14 pages with the correct four
authors via `pypdf`) with the ACM proceedings noted in the note.

---

## 2026-07-29 — Add topic: Generative AI (Beyond LLMs)

> Add a topic on non llm parts of generative ai. Think image, video, audio,
> diffusion models, GANs etc(haven't listed everything).

Three clarifying questions were asked and answered by the user. **Title:** the
user supplied their own wording, *Generative AI (Beyond LLMs)*, rather than any
of the three offered — it names the boundary with the existing LLM page instead
of just listing modalities, so the page's first paragraph opens on that contrast.
**Scope:** audio/music, video *and* 3D/neural rendering each get full resource
rows; ethics/copyright was not selected, so it stays a single pointer row in
Further Reading. **Emphasis:** balanced — intuition, then papers, then hands-on,
with a Tools & Interactive section.

The user also pushed back on an artificial cap: an earlier draft of the plan said
to trim the papers section to ~14 to match the LLM page's 12. That was invented,
not required — `CLAUDE.md` rule 5 forbids *padding*, which is not a ceiling on
genuine quality. The section ships all 23 verified papers, grouped into six
labelled runs (foundations, diffusion lineage, text-to-image, audio, video, 3D),
because the topic spans more model families *and* more modalities than any other
page on the site.

Outcome: `topics/generative-ai-beyond-llms.html` with **55 resources** across all
seven sections, a card added second in the landing-page grid, and one new Further
Reading row on `topics/large-language-models.html` so its "image, audio and video
generation are a separate topic" sentence finally resolves. Every link opened
before shipping: 25 arXiv pages content-checked via `citation_title`, 20 other
URLs by page title, 5 YouTube IDs via `oembed`, 4 GitHub repos via `WebFetch`.

---

## 2026-07-30 — Add topic: Artificial Intelligence

> Add a topic on AI(think Artificial Intelligence: A modern approach by Peter
> Norvig)

Four clarifying questions were asked; the user took the recommended option on all
four. **Scope: umbrella + carve-out.** Four of the six existing pages were already
AI-adjacent, so the new page sits *above* them rather than beside them: full
resource coverage for what nothing else covers — agents, search, adversarial
search, CSPs, logic and knowledge representation, planning, reasoning under
uncertainty, reinforcement learning, the history of the field, and safety at the
field level — with depth on statistical learning, deep nets, transformers, LLMs
and diffusion routed to the sibling pages instead of restated. **Title:** plain
*Artificial Intelligence*, the canonical umbrella name, which also sorts the card
first. **Cross-links:** reciprocal, on all four existing AI pages. **Emphasis:**
balanced and learning-path ordered.

The AIMA framing in the prompt drove the page's structure: the description opens
on Russell & Norvig's agent definition, then derives the classical toolkit in the
order the textbook does, and closes by naming explicitly that learning is one
technique inside that picture rather than the whole of it — the carve-out
sentence that makes the four cross-links at the bottom read as a map instead of
an afterthought.

Outcome: `topics/artificial-intelligence.html` with **41 resources** across all
seven sections, a card added first in the landing-page grid, and one Further
Reading row added to each of `machine-learning`, `transformers`,
`large-language-models` and `generative-ai-beyond-llms` (dates bumped to
2026-07-30), which closes the cross-link web — `transformers.html` had no
internal cross-links at all before this. All 39 external URLs opened before
shipping.

---

## 2026-07-30 — Add topic: Deep Learning

> * add a topic on deep learning
> * decide on updating cross links for viable existing posts

Three clarifying questions were asked. **Scope: comprehensive standalone**, against
the recommendation — the alternative was a foundations-only page that deferred
attention, LLMs and diffusion to the siblings, but the user chose a page that reads
end to end on its own and accepts the resulting overlap. In practice that means the
page runs backprop → CNNs → RNNs → attention → diffusion, with the last two carried
at survey depth (one paper each, framed as pointers) so the overlap stays a map
rather than a restatement. **Cross-links: full symmetry.** **Title collision:**
`Transformers (Deep Learning)` renamed to plain `Transformers`.

The second bullet turned out to be the more interesting half. The site's existing
cross-links were lopsided: `artificial-intelligence`, `large-language-models` and
`generative-ai-beyond-llms` each linked to all their siblings, but `machine-learning`
linked to only two and `transformers` to exactly one — an artefact of pages being
added one at a time and only ever gaining reciprocal rows. Adding an eighth page on
top of that would have made the web more ragged, so the gaps were filled in the same
pass: the six AI pages now form a complete graph, five links each. The two
non-AI pages (`data-structures-and-algorithms`, `starting-a-new-bank`) were
deliberately left isolated — "both are computer science" is a topical neighbour, not
a next step, and wiring them in would dilute what a cross-link means here.

The rename had a tail the plan caught but the obvious edit would have missed: four
sibling pages used `Transformers (Deep Learning)` as the *link text* on their
cross-link rows, so the old title survived in four places beyond the page's own
`<h1>` and `<title>`, plus once in `README.md`.

Outcome: `topics/deep-learning.html` with **49 resources** across all seven sections,
a card added third in the grid, and nine new cross-link rows spread across five
existing pages (AI +1, gen-AI +1, LLM +1, ML +3, transformers +4). The cross-link
convention was only ever convention — visible in the shipped pages, absent from
`CLAUDE.md`, `ARCHITECTURE.md` and the template — so it is now written down in the
first two. All 47 external URLs opened before shipping; 70 Playwright checks passed.

---

## 2026-08-01 — Add topic family: Crypto, Blockchain, DeFi & NFTs

> Add a topic on crypto, blockchain, DeFi, NFT, etc. and related topics from the ecosystem.

The prompt names four topics and then gestures at a fifth category ("related topics from
the ecosystem"), so the first question was how many pages that should become. Asked, and
the answers set the shape of the work:

- **Scope: seven pages**, not one omnibus page — matching how this repo already grows a
  subject area (one page per topic, reciprocally cross-linked).
- **The economics/governance page is `crypto-economics-and-daos`.** The seven-page option
  had previewed a `daos-and-token-governance` slug, but the more specific follow-up answer
  picked "Crypto Economics & DAOs", so that one won.
- **Stance: neutral, include critique.** Lead with how the technology works, and carry the
  genuinely good critical material — Diehl, Molly White, Chainalysis crime data, rekt.news
  post-mortems, the BIS and Fed papers — alongside the builder material rather than in a
  ghetto section. This follows from the house style ("accuracy first", "neutral tone")
  rather than being a departure from it.

The interesting design question was the cross-link graph. The AI family is a complete
graph, and the obvious move was to do the same here — 21 pairs, 42 rows. That would have
broken `CLAUDE.md`'s actual rule, which is not "link everything in the family" but "only
link pages that are actually a next step for each other". NFTs↔ZK and Layer 2↔DAOs fail
that test. So the crypto family is deliberately incomplete: 17 of 21 pairs, with
`blockchain-and-cryptocurrency` as a hub linking to all six siblings and the remaining
edges wired only where they earn it. `ARCHITECTURE.md` now says this explicitly, because
"the AI family is a complete graph" was previously the only worked example and read as a
requirement.

One edge crosses out of the family: `decentralized-finance` ↔ `starting-a-new-bank`. DeFi
reimplements deposits, lending and payment rails without a licence, so each page is a real
next step from the other; the bank page's date was bumped for its new row.

Outcome: seven new pages carrying **170 unique external resources**, seven cards added to
the grid in alphabetical order (the site goes 8 → 15 topics), 34 cross-link rows inside the
family plus 2 for the bank edge. Every URL was opened before shipping — which caught a
guessed arXiv ID that turned out to be a paper on epidemic forecasting, another on
fractional harmonic functions, and several plausible-looking YouTube IDs that did not
exist. `ARCHITECTURE.md` updated for the second family; `README.md` left alone, as in
previous topic-add sessions, since it enumerates neither topics nor a count.
