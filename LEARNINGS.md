# Learnings

Things this codebase has taught us the hard way. Read before adding or refreshing resources.
Most of it is about one problem: **proving a link is right, not just alive.**

## A 200 is not proof

- **URLs get recycled.** A Christie's lot URL for Beeple's *Everydays* later served a 1990
  Château Lafite-Rothschild wine lot, and a Penguin URL for *Banking On It* served Sinclair
  McKay's *Dresden*. Both returned a healthy 200. Always compare the live page title with the
  resource you think you're linking; `tests/check_site.py --online` does this automatically.
- **Penguin UK routes by ISBN and reuses its numeric book IDs.** Verify the ISBN in the URL,
  not just the ID. Christie's online sales use the stable
  `onlineonly.christies.com/s/<sale>/<lot>/<id>` form.
- **Soft redirects to a home page.** Some hosts (occ.gov) bounce deep links to their home page
  for scripted clients. The status is 200 and a menu item can even contain your keyword. If the
  final URL is the site root, you have not verified anything.
- **Soft-404s.** Several unrelated paths returning byte-identical pages means an error page.
- **Wrong identifiers look plausible.** A guessed JSTOR stable ID and a guessed ISBN each
  resolved to a real but unrelated work. For DOIs and JSTOR IDs, confirm the metadata through
  Crossref (`https://api.crossref.org/works/<doi>`), which returns title, journal, volume and
  pages without touching the bot-walled publisher.

## Verifying through bot walls, without disabling TLS

- **YouTube** rate-limits page loads; use `https://www.youtube.com/oembed?format=json&url=…`,
  which returns the real title and channel. A 401 can just mean embedding is disabled.
- **GitHub** returns 403 to scripted page loads; use `git ls-remote https://github.com/o/r HEAD`
  for existence and `raw.githubusercontent.com` for file contents.
- **Cloudflare, Akamai and similar** block curl and Python differently: a host can pass curl and
  fail `urllib` (otexts.com, nature.com), or the reverse. When both fail, `WebFetch` sometimes
  gets through (it verified the SEC and OCC pages). If nothing verifies a host, leave the
  resource out and record it for a browser retry. Never ship on a guess.
- **Dead domain or bad connection?** Resolve the host (`socket.getaddrinfo`, or DNS-over-HTTPS
  via `https://dns.google/resolve?name=<host>&type=A`). NXDOMAIN (`Status: 3`) means dead, as
  with `docs.circom.io`. A reset or timeout means retry, and several transient resets
  (rekt.news, zkhack.dev, stephendiehl.com) passed on the second try.
- **Headless Chromium here doesn't trust the session proxy's CA.** Don't work around it by
  ignoring certificate errors. Use curl, `urllib` (which honours `SSL_CERT_FILE`) or `WebFetch`
  instead. Localhost needs no proxy (`--no-proxy-server`) for browser checks of the site itself.

## PDFs

- `pdftotext`/`pdftoppm` aren't installed; use `uv run --with pypdf --with cryptography`
  (the extra `cryptography` avoids a clash with the system package).
- **Scans have no text layer.** Extract the page-1 image (`page.images`), view it, then delete
  it. Never trust PDF metadata: titles often just echo the filename.
- **Free-copy rule.** Link single canonical papers and essays hosted by their author, a
  university or a legitimate public archive. Don't link scans of whole in-print books or
  chapters, or copies stamped with JSTOR's "personal use only" terms on a course page. Link the
  publisher or JSTOR record instead and flag the cost.

## Content pitfalls

- **Descriptions go stale when they count things.** "The four sibling pages" stayed in two
  descriptions after a fifth page was added. Don't hard-code counts of other pages.
- **Markdown habits leak into HTML.** `*word*` renders as literal asterisks; use `<em>`.
- **Long unbroken tokens overflow on phones.** A repo path in a note widened a page by 58px
  at 375px. `styles.css` now sets `overflow-wrap: anywhere` on `.resource-item`, but check new
  pages at phone width anyway.
- **Semester-scoped course URLs rot** (`/sp26/`, `/autumn2025/`). Prefer the current edition
  and date it in the source line; keep an older recording in the note if it's still the classic.
- **Fast-moving fields need a date check on every refresh**: Ethereum upgrades (Pectra, Fusaka),
  regulation (MiCA, the GENIUS Act), rebrands (MakerDAO → Sky, LM Arena → Arena AI) and retired
  courses (Coursera's MLOps specialization) all changed after the pages were written.
