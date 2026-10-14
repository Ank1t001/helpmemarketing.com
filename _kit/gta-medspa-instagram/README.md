# GTA MedSpa Index build kit (from edition 002)

Canonical URL: https://helpmemarketing.com/gta-medspa-index
Schedule: the 15th of each month, 09:15 America/Toronto (first run 15 October 2026), scheduled task "HMM - GTA MedSpa Index (Monthly)". Its stored prompt is versioned in `ROUTINE_PROMPT.md`; update both together.
Window: the 90 days ending the collection date, refreshed monthly (editions overlap by design).

## Files
- `report_body.html`: the live, approved body with `{{TOKENS}}` (dates, edition, scoreboard rows, log tabs, post log, gated CSV). Editorial text is edited in place each edition.
- `site_shell.html`: a copy of the live page; `build.py` swaps the body and regenerates the Article `dateModified`, the FAQPage (from the visible FAQ) and the Dataset (from `edition.json`).
- `edition.json`: edition, collection date, window, next refresh, `modified_at` (the recorded production deployment of the last content change), roster status and the Dataset block.
- `roster.json`: the clinic list (handle, name, area, region, include, exclude_reason). Missing until the first run rebuilds it: the edition 001 list of 341 accounts was not saved. Rebuilt when older than 92 days.
- `municipalities.json`, `themes.json`, `compliance_patterns.json`: discovery searches, theme keywords and caption patterns.
- `score.py`: scores one collection (`work/posts.jsonl`, `work/profiles.json`) into `editions/NNN/metrics.json` and lists caption matches for review.
- `render.py`: scoreboard rows, post log, log tabs and CSV into `editions/NNN/blocks.json`, using `editions/NNN/notes.json` (one data-note per top-25 clinic).
- `build.py`: assembles `output/gta-medspa-index.html` and `output/edition-NNN.html` and validates them; `--check-live` also requires the page to equal the repo page byte for byte.
- `editions/001/blocks.json`: the edition 001 generated blocks, extracted from the live page so the prior-edition check can run.
- `work/`, `output/`: run files, never committed.

## Check the kit against the live page
```
python3 build.py --edition 001 --as-of 2026-10-14 --check-live
```
Must print PASS. Any edit to /gta-medspa-index made outside the routine must be mirrored here in the same commit (body into `report_body.html` with its tokens, head or style into `site_shell.html`), or the next run stops at its prior-edition check.

## Edition 001 caveats
Edition 001 used two collections and its scoring code was not kept; some ranking-collection post counts look capped at 10. Edition 002 is the first single-pass, coded edition, so it shows no movement column; movement starts at edition 003.
