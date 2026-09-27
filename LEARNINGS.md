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
- **Lapsed domains redirect somewhere unrelated.** The companion site of a standard textbook
  (`evolutionarycomputation.org`) now lands on a restaurant; `ti.arc.nasa.gov` paper links
  soft-redirect to NASA's home page; `picbreeder.org` now opens a different project. The
  checker's cross-site `WARN` catches these — never wave one through.
- **Check who uploaded a video.** oEmbed's `author_name` separates the creator's channel from a
  re-upload. For 1990s SIGGRAPH work the Internet Archive's `siggraph` collection is the official
  copy (used for Karl Sims's *Evolved Virtual Creatures*).
- **A URL printed in a paper can die.** The Segment Anything abstract still points at
  `segment-anything.com`, which no longer resolves; Meta's demo moved to
  `aidemos.meta.com/segment-anything/`. Don't copy project links from a paper without fetching them.
- **Playlist titles can be wrong, and search hits can be copies.** Google DeepMind's own playlist
  for the *RL Lecture Series 2021* is titled "Deep Learning Lecture Series 2021" on YouTube, while
  the top search results for the course were playlists re-uploaded by individuals. List the
  playlist's `videoId`s from its page and oEmbed each one: the video titles and `author_name`
  settle both questions.
- **Official hubs die quietly too.** `deepmind.com/learning-resources/…` pages and `dpmd.ai`
  short links now redirect to deepmind.google's home page — the site-root rule above applies.
- **No `<title>` means the title check can't help.** `fpcv.cs.columbia.edu` has no title element,
  so the checker passes it on content type alone. Confirm such pages by their body text.
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
- **Some publishers block every client here** — MIT Press, Packt, IEEE Xplore (a `202`
  challenge), `science.org`, `direct.mit.edu` and Springer book pages refuse curl, `urllib` *and*
  `WebFetch`. For a paper, confirm the DOI through Crossref and link where `https://doi.org/<doi>`
  redirects (`curl -o /dev/null -w '%{redirect_url}'`). For a book, confirm the ISBN at
  `https://openlibrary.org/isbn/<isbn>.json` (follow redirects) *and* find the exact URL in a
  search index or an official source such as the publisher's repo for the book.
- **Springer articles sit behind a cookie redirect.** `link.springer.com/article/…` and its PDFs
  bounce through `idp.springer.com`, which curl, `urllib` and `WebFetch` can't complete, so an
  OpenAlex "bronze" (free-to-read) label can't be confirmed from here. For the classic
  *Machine Learning* papers, the authors' own copies verify cleanly (Sutton's and Dayan's pages);
  a garbled text layer can be checked by rendering page 1 with `uv run --with pymupdf`.
- **OpenAlex finds the legitimate free copy.** `https://api.openalex.org/works/doi:<doi>` reports
  whether a paper is open access and where (e.g. a university repository), with no key or email.
  Check it before calling a paper paywalled or hunting for a copy by hand. (`api.github.com`
  403s here; use `git ls-remote` and `raw.githubusercontent.com` instead.)
- **Dead domain or bad connection?** Resolve the host (`socket.getaddrinfo`, or DNS-over-HTTPS
  via `https://dns.google/resolve?name=<host>&type=A`). NXDOMAIN (`Status: 3`) means dead, as
  with `docs.circom.io`. A reset or timeout means retry, and several transient resets
  (rekt.news, zkhack.dev, stephendiehl.com) passed on the second try.
- **A 406 can just be user-agent filtering.** `szeliski.org` and `export.arxiv.org` answer curl's
  default agent with 406; the checker's browser-like headers get a 200 from szeliski.org. For
  arXiv metadata in bulk, read the `citation_title` / `citation_author` / `citation_date` meta tags
  on `arxiv.org/abs/<id>` instead of the export API. `ai.meta.com/research/…` returns 400 to scripts.
- **Certificate failures aren't dead links, but keep them out of the sweep.** `web.eecs.umich.edu`
  (incomplete chain) and `vision.stanford.edu` (certificate for another host) fail verification from
  scripts. Link an equivalent that verifies — the course's YouTube playlist, another university's
  copy of the same PDF — rather than adding a known `ERROR`.
- **Headless Chromium here doesn't trust the session proxy's CA.** Don't work around it by
  ignoring certificate errors. Use curl, `urllib` (which honours `SSL_CERT_FILE`) or `WebFetch`
  instead. Localhost needs no proxy (`--no-proxy-server`) for browser checks of the site itself.

## PDFs

- `pdftotext`/`pdftoppm` aren't installed; use `uv run --with pypdf --with cryptography`
  (the extra `cryptography` avoids a clash with the system package).
- **Scans have no text layer.** Extract the page-1 image (`page.images`), view it, then delete
  it. Never trust PDF metadata: titles often just echo the filename.
- **An official host can serve an incomplete PDF.** IJCAI's own file for Koza's 1989 paper is
  one page of a seven-page paper; the author's copy is complete. Check the page count, not just
  that the response is a PDF.
- **`WebFetch` can't read PDFs** (it only saves the binary), and 1990s Ghostscript PDFs can use
  font encodings that garble text extraction. If the text won't come out, confirm the file
  through the host's own page that links it — a group's publication list, a proceedings contents
  page.
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
  The public videos are often from a different term than the page (CS234 is Winter 2026 on its
  site, but its public lectures are Spring 2024), so date the videos separately in the note.
- **The landing search is a substring match.** Short queries hit inside words: `ppo` already
  matches "support" (ML) and "opposition" (Structuralism). Pick distinctive queries such as
  `grpo` when checking that a new card's tags work.
- **Fast-moving fields need a date check on every refresh**: Ethereum upgrades (Pectra, Fusaka),
  regulation (MiCA, the GENIUS Act), rebrands (MakerDAO → Sky, LM Arena → Arena AI) and retired
  courses (Coursera's MLOps specialization) all changed after the pages were written.
