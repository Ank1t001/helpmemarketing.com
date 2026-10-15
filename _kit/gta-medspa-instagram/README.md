# Med Spa Index (GTA) build kit (from edition 002; formerly the GTA MedSpa Index)

Canonical URL: https://helpmemarketing.com/medspa-index (since 2026-10-15; `/gta-medspa-index` permanently redirects to it, and the edition 001 and 002 snapshots stay at `/gta-medspa-index/edition-00N`; new snapshots go to `/medspa-index/edition-NNN`)
Schedule: the 15th of each month, 09:15 America/Toronto, scheduled task "HMM - GTA MedSpa Index (Monthly)" (paused since 15 October 2026). From edition 004 its stored prompt must be `ROUTINE_PROMPT_FIVE.md` (see "Five-account editions"); `ROUTINE_PROMPT.md` and `ROUTINE_PROMPT_50.md` describe editions 001 and 002 only. Update the stored prompt and this file together.
Window: from edition 003, the 30 complete days before the collection date (editions 001 and 002 used 90 days).
Data store: Google Sheet "HMM GTA MedSpa Index data" (`1_Qi7e54I4WG9M7Uie8lzrBwtbOreykvtqn0qku59QG8`: Editions, Roster, and per edition "ENNN scoreboard", "ENNN ranking" and "ENNN post log") and the Drive folder "GTA MedSpa Index" (`15xJ1lYPJM4W-8O2b9gXU-I_V2lvZfAjt`, inside "HMM Indexes") for each edition's post log CSV.

## Files
- `report_body.html`: the live, approved body with `{{TOKENS}}` (dates, edition, scoreboard rows, log tabs, post log, gated CSV). Editorial text is edited in place each edition.
- `site_shell.html`: a copy of the live page; `build.py` swaps the body and regenerates the Article `dateModified`, the FAQPage (from the visible FAQ) and the Dataset (from `edition.json`).
- `edition.json`: edition, collection date, window, next refresh, `modified_at` (the recorded production deployment of the last content change), roster status and the Dataset block.
- `roster.json`: the clinic list (handle, name, area, region, include, exclude_reason). Missing until the first run rebuilds it: the edition 001 list of 341 accounts was not saved. Rebuilt when older than 92 days.
- `municipalities.json`, `themes.json`, `compliance_patterns.json`: discovery searches, theme keywords and caption patterns.
- `score.py`: scores one collection (`work/posts.jsonl`, `work/profiles.json`) into `editions/NNN/metrics.json` and lists caption matches for review.
- `render.py`: scoreboard rows, post log, log tabs and CSV into `editions/NNN/blocks.json`, using `editions/NNN/notes.json` (one data-note per top-25 clinic).
- `build.py`: assembles `output/gta-medspa-index.html` and `output/edition-NNN.html` and validates them; `--check-live` also requires the page to equal the repo page byte for byte.
- `export_sheet.py`: writes the edition's Sheet rows as tab-separated files in `work/sheet/` (top 25, the full ranking, post log in parts of 300 rows, the Editions row, the roster) for the routine to paste; `--postlog-only` backfills the edition 001 post log.
- `editions/001/blocks.json`: the edition 001 generated blocks, extracted from the live page so the prior-edition check can run.
- `work/`, `output/`: run files, never committed.

## Check the kit against the live page
```
python3 build.py --edition 001 --as-of 2026-10-14 --check-live
```
Must print PASS. Any edit to the page made outside the routine must be mirrored here in the same commit (body into `report_body.html` with its tokens, head or style into `site_shell.html`), or the next run stops at its prior-edition check.

## Edition 001 caveats
Edition 001 used two collections and its scoring code was not kept; some ranking-collection post counts look capped at 10. Edition 002 is the first single-pass, coded edition, so it shows no movement column; movement starts at edition 003.

## Run helpers (added 2026-10-15)
- `roster_build.py`: validates a Google Maps discovery crawl into the roster (`--root` for tests, compact output, `--full` for the whole summary). Eligibility, geography, account and sampling logic are unchanged from edition 002 and covered by tests that reproduce the committed roster from the saved discovery data.
- `tools/apify_tool.py`: compact Apify helper. `watch` (needs `APIFY_TOKEN` in the environment, never printed) polls with backoff and prints one line per state change; `status --raw FILE` summarises a saved connector reply; `fetch` downloads a dataset in resumable pages and verifies the count; `build-input` writes actor inputs from the saved handle list so the list never passes through the model; `start` reads its input from a file and sends `maxTotalChargeUsd`. Sessions with only the Apify connector have no token and cannot poll from a shell: use `status` and long waits, not one model call per minute.
- `tools/checkpoint.py`: `editions/NNN/checkpoint.json` records each stage with file hashes. `check` prints done, stale or pending per stage and the next stage; a resumed run skips done stages.
- `tools/verify_profiles.py`: checks collected profiles against the clinic listings and proposes replacements from the reserve order.
- `tools/usage_report.py`: reconciles token usage by stage from a session transcript.
- `tests/test_tools.py`: `python3 -m unittest tests.test_tools` (offline, mock server, no paid calls).
- `INSTRUCTION_LOADING_PROPOSAL.md`: a proposal only; nothing in it is applied.

## Edition 002 scope (2026-10-15)
Edition 002 is a fixed 50-account observational study: `cohort_50.json` is the cohort, `build_50.py` builds the page, snapshot and local Sheet export files (`--target release`) or a local draft, and no score, rank or leaderboard applies (`score.py`, `render.py` and `build.py` do not apply to it). `site_shell.html` is kept as the edition 001 shell for reference; the cleaned shell is generated by `build_50.py`. `roster.json` and `editions/002/roster_eligible.json` are background research from the discovery crawl. Routine instructions for the fixed cohort are prepared in `ROUTINE_PROMPT_50.md` and are not yet in the stored task.

## Edition 003 scope (2026-10-15, founder brief)
Edition 003 is a fixed five-account comparison (VitalityMD, Signature Cosmetic Clinic, Laserbody MD, Skin Vitality, SpaMedica), window the last 30 complete days in Toronto time (15 September to 14 October 2026), collected 15 October 2026. It is not comparable with editions 001 and 002.
- Inputs, all under `editions/003/`: `raw/source_profiles.json.gz` and `raw/source_posts.jsonl.gz` (Apify replies, saved as returned), `accounts.json` (identity verification), `services.json` (official-site service checks), `adlibrary.json` (Meta Ad Library: not checked, page needs JavaScript), `run_ledger.json`, `coding.json` (content type and topic per post; standout visual notes), `edition_003.json`.
- `python3 derive_003.py` writes `observations.json` (raw observed values; hidden likes null, never 0) and `metrics.json` (derived, with denominators). `python3 build_003.py` writes the draft page (`noindex, nofollow`, no snapshot) and the dataset CSVs in `/assets/index/medspa/`. At publication: `python3 build_003.py --target release --published-at <ISO> --modified-at <ISO from the production deployment> --modified-source "<deployment id, commit>"` makes the page indexable, records dateModified, updates the research hub dates and creates `/medspa-index/edition-003` once. A later page-only change (such as a dated clarification) is rebuilt with `--target release`, the recorded `published_at` and a new `--modified-at` from its production deployment; the hub keeps its recorded `hub_modified_at` unless its own content changes (`--hub-modified-at`). A draft build is refused once the edition is published.
- `build_50.py` still reproduces edition 002 but, while `editions/003/edition_003.json` exists, writes its page to `editions/002/release/medspa-index-002.html` and never touches the live page or the hub.
- **Superseded (2026-10-15):** the conflict below is resolved by the five-account pipeline (next section).
- **Conflict for the founder:** `ROUTINE_PROMPT_50.md` and the stored scheduled task "HMM - GTA MedSpa Index (Monthly)" describe a 50-account (or older 596-account) monthly refresh. Neither matches the five-account edition; the routine must not run against the live page until the founder decides how edition 004 is refreshed. The task was not changed.

## Five-account editions (004 onward, prepared 2026-10-15)
Every edition from 004 re-collects the five accounts of `cohort_five.json` (fixed, in order; never replaced or added to) over the 30 complete days before the 15th, with the method of edition 003, and is built by generic scripts so the monthly run produces the same page as edition 003. The routine prompt is `ROUTINE_PROMPT_FIVE.md`.
- `derive_five.py --edition NNN`: raw replies to `observations.json` and `metrics.json` (reproduces edition 003's files byte for byte).
- `frames_five.py --edition NNN --fetch DIR`: saves each standout cover and stops; after the covers are looked at and `coding.json` has `standout_visuals`, `standout_frames` (alt), `standout_titles`, `frame_crop` (and optional `standout_collab`), `--from DIR` writes the 640x800 WebP frames and `frames.json`.
- `build_five.py --edition NNN [--tokens | --target release ... | --check-live]`: page structure from `template_five.html` and `head_five.html`; every figure is a token computed from the data (`--tokens` lists them); the month's reading is `editions/NNN/narrative.json` (three findings with denominators, one card per readable account, two to five patterns, three tests). Generated from the data: the comparison, services and account tables, standout cards, unreadable account cards (from the saved restriction reply), collaborations, missing data, Ad Library, edition history (five-account editions plus `cohort_five.json` legacy rows), corrections (`editions/*/corrections.json`, earlier editions labelled) and the citation. The build refuses a figure typed by hand (unless declared in `coding.json` `literal_numbers` with its source), "we", "our" or "us", dashes, banned words, unknown tokens, a missing or extra account reading and standout notes that do not match the current standout posts.
- Release: `--target release` with a provisional time makes the page indexable, creates `/medspa-index/edition-NNN` once, regenerates the hub and `/hmm-index` text (elements tagged `data-msi`, from the edition records and `cohort_five.json` `hub_legacy` and `schedule`) and sets the sitemap lastmod; a second release with the production ready time records `dateModified` on the page, hub and snapshot (with a metadata note in the snapshot head). After publication a draft build is refused and `--check-live` proves the page still reproduces.
- `check_live.py`: the routine's prior-edition check (edition 003 through the kit test, later editions through `build_five.py --check-live`).
- `export_five.py --edition NNN --status Preview|Published --commit SHA`: TSVs for the Sheet tabs "ENNN posts" and "ENNN accounts" and the Editions row (same columns as before; no leader or score).
- `cohort_five.json` `schedule.active` is false while the stored task is paused; set it to true when the founder re-enables the task, so the next release writes the monthly refresh plan on `/hmm-index`.
- Tests: `tests.test_tools.Five` builds a sample edition 004 from edition 003's records through draft, release, recorded time, check-live and export, and checks each guard.
