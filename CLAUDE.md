# CLAUDE.md — Topic References

This repo is a **personal study-resources site**. The user gives a *topic*; you produce a page
that opens with a short description of that topic and then lists curated, real resources (books,
papers, articles, videos, courses, further reading) to study it further.

This file is the **contract** for how to add content. Follow it exactly so every topic page comes
out consistent and trustworthy.

---

## Golden rules

1. **No build step, ever.** Plain HTML + one shared `styles.css` + a tiny inline `<script>` on the
   landing page. No frameworks, bundlers, npm, or JSON-fetch rendering. The site must work by
   double-clicking `index.html` (`file://`) and on GitHub Pages alike.
2. **Description first.** Every topic page starts with a 2–4 sentence plain-language overview
   (what it is + why it matters) before any resources.
3. **Real, verified links only.** Use live web search to find and confirm URLs, combined with your
   own knowledge of canonical resources (the classic book, the official docs, the seminal paper).
   **Open/verify every URL before including it.** Drop anything dead, paywalled-with-no-value, or
   uncertain. A short list of real links beats a long list of guesses.
4. **Never pad.** Omit any resource section you can't fill with genuinely good links. Quality and
   accuracy over volume.

---

## Workflow: when the user gives a topic

### 1. Derive the slug
- Slug = kebab-case of the topic, e.g. `Graph Neural Networks` → `graph-neural-networks`.
- The page lives at `topics/<slug>.html`.
- If a page for that slug already exists, **update it** (refresh links, add new resources, bump the
  date) rather than creating a duplicate.

### 2. Research and verify
- Use `WebSearch` / `WebFetch` to gather candidate resources and **confirm each link resolves**.
- Combine with your knowledge of canonical/standard resources for the topic (famous books,
  official documentation, foundational papers, well-known explainers).
- Prefer primary and authoritative sources; prefer free/accessible versions when they exist
  (e.g. an author's free draft over a paywall).
- Aim for a useful spread across levels (Beginner → Advanced) and formats.

### 3. Write the page from the template
- Copy `templates/topic-template.html` to `topics/<slug>.html` and fill every `{{PLACEHOLDER}}`.
- **Description block:** 2–4 sentences, plain language, no marketing fluff. Add the optional
  `Good to know first` prerequisites box only if there are real prerequisites.
- **Order resources by learning path where sensible** (gentle intro → hands-on → primary source →
  deep dives), not just alphabetically.
- Set `Last updated:` to **today's date** (`YYYY-MM-DD`).
- Confirm the page links `../styles.css`, has the back-to-home link, and keeps the favicon `<link>`.
- Every external link must be `target="_blank" rel="noopener"`.
- Remove the template's instructional HTML comments from the finished page.

#### Resource section taxonomy (keep this order; delete empty sections)
| Section | Use for |
|---|---|
| 📚 Books | textbooks, definitive references |
| 📄 Papers & Primary References | seminal/standard papers, specs, RFCs |
| ✍️ Articles & Blog Posts | explainers, deep-dive posts |
| 🎥 Videos & Talks | lectures, conference talks, YouTube |
| 🎓 Courses & Tutorials | structured courses, interactive books, guided tutorials |
| 🔧 Tools & Interactive *(optional)* | playgrounds, visualizers, notebooks, repos |
| 🔗 Further Reading / Going Deeper | next steps, surveys, related topics |

Each resource row uses this exact shape:
```html
<li class="resource-item">
  <a class="res-title" href="URL" target="_blank" rel="noopener">Title</a>
  <span class="res-source">— Author / Publisher / Year</span>
  <span class="level" data-level="beginner|intermediate|advanced">Level</span>
  <p class="resource-note">One line on why it's worth your time.</p>
</li>
```
The `level` pill is optional per row but encouraged. Use exactly one of
`beginner` / `intermediate` / `advanced` in `data-level` (the value styles the pill color).

### 4. Link it from the landing page
Add **one card** to the `#topic-grid` in `index.html`, kept in **alphabetical order by title**:
```html
<a class="topic-card" href="topics/<slug>.html" data-tags="lowercase synonyms keywords">
  <h3>Topic Title</h3>
  <p>One-line description.</p>
</a>
```
- `data-tags` feeds the client-side search filter — include lowercase synonyms, acronyms, and
  related terms a user might type (e.g. for transformers: `attention nlp llm gpt bert`).
- Do **not** touch the `<script>` filter logic; it reads cards generically.

### 5. Housekeeping (per the user's global conventions)
- Append the user's prompt to `PROMPT.md`.
- Add or update today's work summary at `memory/YYYY-MM-DD.md`.
- If the change is structural (new section type, new file, layout change), update `ARCHITECTURE.md`.
- Update `README.md` if the topic list or usage instructions meaningfully change.
- **Generate a git commit message for the user, but do not commit** (unless running in a remote
  cloud session). Never list Claude as author or co-author.

---

## House style
- Tone: concise, neutral, helpful. Notes are one line each — say *why* a resource is worth it.
- Accuracy first: if you're unsure a claim or link is correct, verify it or leave it out.
- Accessibility: semantic headings, meaningful link text (not "click here").
- Don't introduce external CSS/JS/CDNs. Keep everything self-contained.

## Verifying your work
- Open `index.html` in a browser: cards render, search filters live, the count updates, and a
  nonsense query shows the "no matches" message.
- Open the new `topics/<slug>.html`: description appears first, sections render, dark mode works
  (it follows the OS setting), and the back link returns home.
- Optional structural check: `uv run tests/check_site.py` (verifies every topic page is linked from
  `index.html` and vice-versa).

## File map
```
index.html                 landing page (cards + search filter)
styles.css                 shared styles for all pages
topics/<slug>.html         one page per topic
templates/topic-template.html   skeleton to copy for new topics
tests/check_site.py        optional dev-only structure check (uv run)
```
