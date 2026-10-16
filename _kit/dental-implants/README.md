# Dental Implant Marketing Index kit

Builds `/dental-index` (repo root `dental-index.html`): a comparison of how five selected Ontario dental clinics, focused on the Greater Toronto Area, present and promote implant consultations. A study of published marketing, not a ranking of clinics or a judgement of clinical care. Founder brief of 16 October 2026. This folder is excluded from deploys by `.vercelignore`.

Status: edition 001 is a **draft** (noindex, not in the sitemap, not linked from any hub or menu). Release requirements are listed in `editions/001/edition.json`; `build.py --target release` refuses until they are met.

## Files

- `cohort.json`: the five clinics (fixed order and names; never substituted silently), identity notes and the five reserve candidates (never shown on the page).
- `site_shell.html`: head, nav, `.msi` wrapper and footer copied from `medspa-index.html` by `tools/make_shell.py` (source commit recorded in the file). Re-run it only when the shared Index head changes.
- `head_dental.html`: dental-only styles (scoped to `.msi`) and the research CTA tracking (`review_cta_click`, `research_service_click`).
- `build.py`: validates every input, renders the page and the observations CSV. Never edit the page body by hand.
- `tests/test_build.py`: `python3 -m unittest tests.test_build` (window boundaries, post cleaning, identities, excerpt and figure tracing, three tests, takeaways, voice, draft and release gates).
- `tools/fetch.py`: saves public pages as evidence (`editions/NNN/raw/pages/<sha12>.html.gz`, one line per fetch in `raw/fetch_log.jsonl`). Never submits forms, sends cookies or logs in.
- `tools/extract.py`: plain text (`raw/text/`) and visible form fields (`raw/forms.json`) from the saved pages. `tools/view.py` prints a page's text without its site navigation.
- `CHROME_HANDOFF.md`: the browser work still to do for edition 001.

Per edition (`editions/NNN/`):

| File | Holds |
|---|---|
| `raw/` | Source records: saved pages, fetch log (URL, final URL, status, UTC time, bytes, sha256), extracted text and form fields |
| `observations.json` | Dated, sourced observations: clinic, dimension, kind (`observed`, `claim`, `absence`), excerpt, statement, limitation |
| `leads.json` | Unverified leads (for example cached copies of blocked sites). Never shown or counted |
| `comparison.json` | The five-clinic comparison cells, each resting on observations |
| `social.json` | Instagram handles (verified from the official site, or empty with a reason) and collected posts |
| `ads.json` | Meta Ad Library and Google Ads Transparency Center status per clinic, with prepared searches |
| `narrative.json` | The reading: summary, findings, clinic analyses, cross-clinic patterns, exactly three tests |
| `edition.json` | Status (`draft` or `ready`), window rule, snapshot path, release requirements |

Outputs: `dental-index.html` and `assets/index/dental/dental-index-edition-NNN-observations.csv` (only the observations used on the page; no personal data).

## Build

```
python3 build.py --edition 001 --check   # validate only
python3 build.py --edition 001           # draft page and CSV
python3 -m unittest tests.test_build
```

`build.py` checks, among others: the five clinic identities; every observation's source is in the fetch log with HTTP 200 and on the clinic's official domain; every excerpt appears word for word in the saved page; every digit in the reading appears in a cited source page; one to four findings, one analysis per clinic, exactly three tests with every field and no figures; a two- or three-sentence "What this means for your clinic" takeaway after each finding, clinic analysis and pattern (pending clinics get a labelled placeholder); no em or en dashes, no "we/our/us", no banned wording; unverified handles stay empty; no posts while social status is `not_collected`; one H1; no inline styles; one robots tag; draft pages noindex with no dates and no snapshot link; JSON-LD parses; the CSV row count matches the page.

## Windows and social posts

Observation window: the last 30 complete calendar days in America/Toronto before the collection date (`window_last_30`). Collected Instagram posts go through `clean_posts`: window filter by Toronto date, error rows dropped, duplicates removed, old pinned posts outside the window excluded, clinic-owned and collaborator-owned posts kept apart, negative or hidden metrics kept missing (never zero). Classify implant relevance per post (implant, general dentistry, hygiene, Invisalign, other); compare implant posts only, and say so if there are too few. No engagement ranking.

## Release (not run for edition 001)

When every requirement in `edition.json` is met and Ankit approves, set `status` to `ready`, then `python3 build.py --edition 001 --target release --published-at <production ready time> --modified-at <same>`. Release adds the snapshot, the sitemap entry and the hub links in a separate, reviewed change; none of these exist for the draft.
