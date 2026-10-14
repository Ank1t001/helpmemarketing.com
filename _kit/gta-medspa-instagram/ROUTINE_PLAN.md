# GTA MedSpa Index: what a monthly routine needs (14 October 2026)

The Real Estate routine (`_kit/realestate-instagram/ROUTINE_PROMPT.md`) works because the kit holds the roster, the scoring code, the tokenised body, a validator and the previous edition's data. For the GTA MedSpa Index none of these exist in the repo or in Drive. What exists: the published page (top 25 table, 488-post log of the top 25, aggregate figures) and the frames.

## Gaps to close, in order
1. **Clinic roster.** The 341 accounts (handle, clinic name, municipality, region, exclusions) are not saved. Rebuild once: Google Maps listings for the 37 municipality searches, filter out day spas, salons, massage and physio, resolve handles, then a founder review. Save as `roster.json`. Re-run discovery quarterly, not monthly; monthly runs reuse the roster.
2. **One collection pass.** Edition 001 used two collections and the ranking collection appears to have capped some clinics at 10 posts. The routine must collect every roster account once, by date (`onlyPostsNewerThan` the window start, filtered by timestamp in code), with no small per-account cap.
3. **Scoring code.** Not kept for edition 001. Write `score.py`: median plays per reel, comments per 1,000 plays capped at the 95th percentile, percentile ranks, 70/30 weights, three-reel qualifying rule, tiers, pattern groups, correlation, regional medians. Edition 001 cannot be reproduced, so edition 002 is the first coded edition; show no movement column until edition 003 (or show it with a caveat).
4. **Theme and compliance rules in code.** The keyword lists for the seven themes and the caption patterns (prescription drug plus condition, before-and-after, missing disclaimer, superlative or guarantee, testimonial) must be written down, plus a review step: AI-assisted reading of every matched caption, with the founder approving before publication. The page reports aggregate shares only.
5. **Kit and validator.** `report_body.html` (tokenised from today's page), `site_shell.html`, a `build.py` that checks section order, wording, flags, data-notes, metadata and the snapshot, as the Real Estate `build_v2.py` does.
6. **Routine prompt.** Same shape as the Real Estate one: date gate and recency gate, staging preview, report, "ship it" in the session, `dateModified` from the deployment.

## Decisions for the founder
- Window: keep a rolling 90 days (stable pool, editions overlap) or move to 30 days (fewer clinics reach three reels).
- Run day (the Real Estate routine runs on the 14th).
- Monthly spend ceiling for Apify (roughly 341 accounts of posts each run, plus frames; check the current per-result price in the Apify console).
- Whether the cadence finding stays on the page until a single-pass collection confirms it.
