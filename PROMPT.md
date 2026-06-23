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
