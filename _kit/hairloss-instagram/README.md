# Hair Loss Index build kit (from edition 002)

Canonical URL: https://helpmemarketing.com/hair-loss-index
Schedule: the 16th of each month, 09:15 America/Toronto (first run 16 October 2026), scheduled task "HMM - Hair Loss Index (Monthly)". Its stored prompt is versioned in `ROUTINE_PROMPT.md`; update both together.
Window: the 90 days ending the collection date, refreshed monthly (editions overlap by design).
Data store: Google Sheet "HMM Hair Loss Index data" (`1wVrhuPpavUQ9-D9B4BPiWJbAeg0MZ-1-V2Xv5NpsWpU`: Editions, Roster, and per edition "ENNN scoreboard" and "ENNN post log") and the Drive folder "Hair Loss Index" (`1k9ch41mq2ghVJPMTMqVDf5MfBvBNiggD`, inside "HMM Indexes") for each edition's post log CSV. The older "HMM Hair Loss Index" folder is left as it was.

## Files
- `report_body.html`: the live, approved body with `{{TOKENS}}` (dates, edition, scoreboard rows, the Stage 1 and Stage 2 tables, log tabs, post log, gated CSV). Editorial text is edited in place each edition.
- `site_shell.html`: a copy of the live page; `build.py` swaps the body and sets the Article `dateModified` from `edition.json`. The page carries no FAQPage or Dataset block.
- `edition.json`: edition, collection dates, window, next refresh, `modified_at` (the recorded production deployment of the last content change), the date ads were checked, and the Sheet and folder IDs.
- `roster.json`: the roster from edition 002 (founder decisions, 16 October 2026): the seven Ontario hair loss clinics with the largest Instagram accounts that published at least five posts in the 90 days ending 16 October 2026 (the ten largest were selected first; the three with fewer than five posts were removed the same day), one handle each, in two groups (TRANSPLANT, NON-SURGICAL), with each clinic's frame file slug and city. Changed only with Ankit's approval. Edition 001's nine-brand roster and studio themes are kept in `editions/001/roster.json` and `editions/001/themes.json`; `build.py` validates an edition against its own `editions/NNN/roster.json` when one exists.
- `themes.json`: the nine clinic content themes and their caption keywords (first match wins), from edition 002; `asks.json`: caption patterns for the booking and general asks.
- `score.py`: scores one collection (`work/posts.jsonl`, `work/profiles.json`) into `editions/NNN/metrics.json`. Its first run writes `work/conversion_proposed.json` and `work/theme_review.json` and stops until `editions/NNN/conversion.json` (reviewed caption ask and steps to enquire) and `editions/NNN/ads.json` (Meta Ad Library check) exist; corrections to themes go in `editions/NNN/theme_overrides.json`.
- `render.py`: scoreboard rows, stage tables, log tabs, post log and CSV into `editions/NNN/blocks.json`, using `editions/NNN/notes.json` (one data-note per brand).
- `build.py`: assembles `output/hair-loss-index.html` and `output/edition-NNN.html` and validates them; `--check-live` also requires the page to equal the repo page byte for byte.
- `export_sheet.py`: writes the edition's Sheet rows as tab-separated files in `work/sheet/` (scoreboard, post log in parts of 300 rows, the Editions row) for the routine to paste; `--postlog-only` backfills the edition 001 post log.
- `editions/001/blocks.json`: the edition 001 generated blocks, extracted from the live page so the prior-edition check can run.
- `work/`, `output/`: run files, never committed.

## Score (from edition 002)
30% Discovery (percentile of average recorded reel plays per follower) + 20% Interest (percentile of engagement rate) + 30% Consideration (percentile of average comments per post) + 20% Conversion path (caption ask: booking 50, general 25, none 0; plus steps to enquire: one 50, two 35, three 20, none 0). Percentiles within the ranked brands (five or more posts), half credit for ties; unranked brands are placed against the ranked brands' values. Rounded to a whole number.

## Check the kit against the live page
```
python3 build.py --edition 001 --as-of 2026-10-14 --check-live
```
Must print PASS. Any edit to /hair-loss-index made outside the routine must be mirrored here in the same commit (body into `report_body.html` with its tokens, head or style into `site_shell.html`), or the next run stops at its prior-edition check. The edition 001 snapshot is never changed.

## Edition 001 caveats
Edition 001 used two collections (8 September for the scoreboard, 9 September for the rest) and its pillar scaling was not kept, so its scores cannot be reproduced. Edition 002 is the first single-collection, coded edition and the first on the seven-clinic roster; its scores are not comparable with edition 001's, so movement starts at edition 003, compared with edition 002 only. The edition 001 snapshot keeps a placeholder dash in its comparison card ("Brands marked –"); the live page and kit use "NR" since 14 October 2026.
