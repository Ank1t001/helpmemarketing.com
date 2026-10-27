# Business Cards & Spend Management Index kit

Builds `/business-spend-index` (the page at `business-spend-index.html`) and its curated CSV (`/assets/index/business-spend/business-spend-index-edition-001-observations.csv`) from one set of evidence files. Edition 001 is a **draft**: `noindex`, not in the sitemap, the nav or the HMM Index hub.

The whole `_kit/` folder is excluded from deployment by `.vercelignore`, so none of these files are served.

## What the Index is

How six platforms (Venn, Float, Ramp, Loop, Keep, Airwallex, in that order) explain business cards, spend management and cross-border payments to Canadian businesses, read from dated public pages. It is a point-in-time reading of communication and enquiry journeys. It is not a product test, a compliance assessment, a ranking or a recommendation. Lending, investment, personal banking, crypto, payroll, SEO rankings, social posting and ad libraries are out of scope.

## Files

| File | What it holds |
|---|---|
| `edition.json` | Edition number, status (draft or published), readiness, collection start and end (America/Toronto, with offsets), publication and modification dates (null for a draft), relationship disclosure (status and the confirmed wording, the one place it is stored), approvals (entered by hand from the owner; never generated). |
| `platforms.json` | The six platforms, their order, code and Canadian starting URL. |
| `sources.json` | One record per capture: stable ID `S-<CODE>-<ROLE>`, URL, final URL, HTTP status, sha256 of the captured bytes, capture time, method. No page content. |
| `observations.json` | One record per claim: stable ID `O-<CODE>-NN`, platform, product, layer (product, cross_border, marketing), category, market, eligibility, plan, statement, amount, units, currency, conditions, cited sources with short excerpts, status, method, observed_at, conflicts, interpretation (my reading, kept apart from the statement), public flag. |
| `narrative.json` | The five views (Overview, Compare products, Messaging & offers, Application journeys, Lessons & tests), the content-type legend, the journey table, findings, comparison cells, examples, the five-question reading per platform with its takeaway, patterns, the three tests, method text and the help section. Every finding, example, pattern and table cell names the observation IDs it rests on. |
| `site_shell.html` | The site head, nav and footer, copied from `/medspa-index` (the shared `.msi` styles), with four tokens. |
| `page_head.html` | Page-scoped CSS and two scripts: `data-bsi-tabs` (the five views as accessible tabs: hash and history, deep links that open the view and the details around their target, keyboard pattern, focus kept out of hidden views; without JavaScript every view shows in order) and the `review_cta_click` push. Print shows every view. |
| `build.py` | Renders the page and CSV. Reads no clock. `--check` fails if the committed outputs differ from a fresh build. |
| `validate.py` | Input and output checks; `--raw DIR` also checks every excerpt against the private capture and every capture hash. |
| `model.py` | The shared evidence rules (statuses, categories, IDs, timestamps, traceability). |
| `ingest.py` | Idempotent ingestion: `sources` (fetch log), `observations` (records by ID), `browser` (Chrome captures with a manifest). Changed records need `--replace`; missing files produce a handoff request and no write. |
| `release.py` | Release preparation. `--dry-run OUTDIR --release-date YYYY-MM-DD` renders the live page, the edition snapshot, the hub and the sitemap outside the repository and reports open gates; `--apply` writes them only after `edition.json` records the owner's release instruction. Steps in `RELEASE_STEPS.md`. |
| `collect.py` | The bounded server fetcher used for edition 001. Its output directory is private storage. |
| `SOCIAL_MODULE_BRIEF.md` | Collection brief for the planned social content module (official Instagram accounts only, the fixed window 25 July to 22 October 2026, verification, coverage, per-post fields, inspection and metrics rules). Not collected; nothing on the page. |
| `social.py` | Schema and checks for a future `social.json` (window, channels, verification, coverage labels, required fields, explicit nulls for missing metrics, no session material) and the renderer for the Social content view. `load_reviewed()` returns nothing until `social.json` is reviewed and approved by hand, so the page has no social tab today. |
| `social_package_template/` | Starting point for the social collection: six account rows (website-linked Instagram candidates, none verified), empty posts and manifest, and a field guide. Copied outside the repository and filled in Chrome; `python3 social.py check DIR` and `python3 social.py ingest DIR` (writes a draft `social.json`, screenshot hashes only). |
| `artwork.html` | Source of the hub card artwork (`/assets/index/business-spend/hero.webp` and `hero-704.webp`), rendered by Playwright at 1056x591. Text and outline shapes only. |
| `CHROME_HANDOFF.md` | Browser checks still needed, the manifest format and the publication blockers. |
| `tests/test_kit.py` | Unit tests. |

## Statuses

- **Published**: an applicable official source states it. It was not tested.
- **Not found in reviewed sources**: the pages reviewed (listed in `reviewed_sources`) did not establish it.
- **Not checked**: no valid check was completed (for example a page that returned only a JavaScript shell). No sources, no capture time.
- **Conflicting**: relevant sources differ and the difference is unresolved. Needs a conflict note.

A reconciled difference carries `reconciliation` (`class` A, B, C, D or "B and D", `topic`, `note`): A different products or conditions, B rendered page and page code differ, C unresolved in the same context, D insufficient evidence. Evidence status and reconciliation class are separate: only a class C difference (unresolved in the same context) has the status Conflicting; A, B and D never set it. A class D item keeps the evidence status of its statements and shows a separate "Not determined" tag. Conflict records sit only on Conflicting items; open questions go in conditions. `model.py` enforces this.

Browser captures (method `browser`) cite a sanitised screenshot by hash; their excerpts come from the page text in Chrome and are attested by the capture manifest. Registry captures carry `covers: ["*"]` so any platform's registry entry can cite them.
- **Explicitly unavailable**: an applicable source says it is not available.

Missing values are `null`, never `0` or an empty string.

## Commands (run in this folder)

```
python3 build.py                     # write the page and the CSV
python3 build.py --check             # PASS only if both match a fresh build
python3 validate.py --raw RAW_DIR    # also check excerpts and hashes against private captures
python3 validate.py --raw RAW_DIR --browser SHOTS_DIR   # and the browser screenshots' hashes
python3 -m unittest tests.test_kit
```

## Editing rules

- Edit the JSON files, then build. Never hand-edit `business-spend-index.html` or the CSV.
- A rebuild never changes a date. Collection times come from `sources.json`; `edition.json` start and end must equal the first and last capture. A draft carries no publication or modification date and no `datePublished` or `dateModified` in its JSON-LD.
- Write in first person singular, Canadian spelling, no em dashes, none of the banned phrases in `/docs/HMM_Content_Rules.md`. `validate.py` also refuses "hides", "misleading", "non-compliant", "safest", "winner", "cheapest" and score language in my own text.
- Keep registration, supervision, licensing, card issuing, deposit holding and insurance separate, as each provider states them. Registration is never endorsement.
- Interpretations go in `interpretation` (shown as "My reading" on the page) and never in the CSV.
- Raw captures (HTML, text, screenshots) stay outside the repository. Only short excerpts, hashes and metadata are committed.

## Release (not done for edition 001)

Before release: the Chrome items, a decision on each conflict, the owner's review and explicit instruction, the deployed forms script with `research_business_spend`. Then set `status` to published and the approvals from the owner's instruction, add the page to `sitemap.xml` and the hub, and add `datePublished` and `dateModified` from the recorded production deployment (the Real Estate and Hair Loss Index rules in `CLAUDE.md`). Keep a fixed snapshot for each published edition.

## Evidence storage

The kit holds hashes, not the evidence. The underlying captures (64 server captures and 34 sanitised browser screenshots, with the browser-pass manifest) are in one private archive, `business-spend-index-edition-001-evidence.zip`, recorded in `edition.json` under `evidence_archive` with its sha256. `ARCHIVE_MANIFEST.json` inside it maps every source ID to its files. The archive must never be committed here: this repository is public. Storage is recorded in three separate steps in `edition.json` `evidence_archive`: a storage reference supplied (done: the owner supplied a private reference, which is kept out of this public repository), the stored copy retrieved, and the stored copy's hash verified with `validate.py --archive` (neither done). `location_status` is `reference_supplied`; it becomes `stored` only after both later steps. The archive itself is never modified: social evidence goes in a separate, versioned archive with its own manifest and hash (see `SOCIAL_MODULE_BRIEF.md`). Check a stored copy with `python3 validate.py --raw RAW_DIR --browser SHOTS_DIR --archive EVIDENCE_ZIP` (or extract the archive and point `--raw` and `--browser` at its folders).
