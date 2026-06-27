# 📚 Topic References

A personal, ever-growing index of topics. For each topic you get a **short description** followed
by a curated set of **resources to study it further** — books, papers, articles, videos, courses,
and tools.

It's a plain static site: **no build step, no frameworks, no dependencies.** Just HTML, one CSS
file, and a tiny bit of vanilla JavaScript for search.

🔗 **Live site:** _enable GitHub Pages (see below) and drop your URL here._

---

## How it works

- [`index.html`](index.html) is the landing page: a searchable grid of topic cards.
- Each topic is its own page under [`topics/`](topics/), e.g. `topics/transformers.html`.
- [`styles.css`](styles.css) styles everything with a single shared **"Brutalist Mono"** theme —
  monospace type, thick black borders, hard offset shadows, a yellow header, and a cobalt-blue
  accent. It's a fixed light look (no OS dark-mode variant), built entirely from system fonts.
- The search box on the landing page filters cards instantly, entirely client-side — so it works
  whether you open the file locally or visit the hosted site.

A sample topic, **[Transformers (Deep Learning)](topics/transformers.html)**, ships as a reference
example. Feel free to delete it once you've added your own.

## Adding a topic

This repo is designed to be filled in with help from an AI assistant (Claude Code). Just ask:

> "Add a topic: **Kalman Filters**"

The assistant follows the workflow in [`CLAUDE.md`](CLAUDE.md): it researches and verifies real
resources, writes `topics/<slug>.html` from the template, and links it from `index.html`.

**Prefer to do it by hand?**
1. Copy [`templates/topic-template.html`](templates/topic-template.html) to `topics/<slug>.html`.
2. Fill in the description and resource sections (delete sections you can't fill well).
3. Add a card for it in `index.html` (keep cards alphabetical).

## Local preview

No server needed — just open `index.html` in your browser:

```sh
open index.html        # macOS
```

(Optional) serve it over HTTP if you prefer:

```sh
python3 -m http.server 8000   # then visit http://localhost:8000
```

## Optional: validate the site

A small, dependency-free Python script checks that every topic page is linked from `index.html`
and vice-versa. It is **dev-only** and not required to view the site:

```sh
uv run tests/check_site.py
```

## Deploy to GitHub Pages

1. Push this repo to GitHub.
2. Repo **Settings → Pages**.
3. Under **Build and deployment**, set **Source: Deploy from a branch**, branch **`main`**,
   folder **`/ (root)`**, and save.
4. Your site goes live at `https://<username>.github.io/<repo>/` within a minute or two.

The included [`.nojekyll`](.nojekyll) file tells GitHub Pages to serve files as-is (no Jekyll
processing).

## License

[MIT](LICENSE) © digster
