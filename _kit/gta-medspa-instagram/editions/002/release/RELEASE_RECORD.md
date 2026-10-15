# Edition 002 release record (preflight on fa280ae, updated for the next commit)

## Dates policy
- Observation window 17 July to 15 October 2026 and collection date 15 October 2026 come from edition.json and never change.
- The pages carry no dateModified and no visible Updated date until publication. After the production deployment is READY, run `python3 build_50.py --target release --edition 002 --modified-at <ready time ISO 8601 with offset> --modified-source "Vercel production deployment <id> (commit <sha>) ready time"`. It sets dateModified on the live page and the snapshot, the visible "Updated" date (America/Toronto) on both, the research hub's dateModified and visible Updated date, and edition.json modified_at. datePublished on the hub and every historical edition date (edition 001 row and snapshot) are untouched. Then set the sitemap lastmod for /gta-medspa-index, /medspa-marketing-research and /hmm-index to the publication date (the existing refresh command in CLAUDE.md does this from git).
- /hmm-index has no date fields; only its GTA card text changed.

## Hidden likes: 70 versus 66
Both numbers are correct and measure different sets (saved records `source_posts_pilot.jsonl.gz`, window 17 July to 15 October 2026, likes recorded as -1 by the scraper, never null):
- 783 feed posts in the window: 70 hidden (713 visible).
- 725 own posts: 66 hidden (659 visible). The page's headline figure and the denominator for likes.
- 58 collaboration posts: 4 hidden (54 visible).
- All 824 rows returned, including the 41 older pinned posts outside the window: 77 hidden.
The earlier draft's 70 was the all-feed count; the candidate's 66 is the own-post count. The page now states both ("66 of the 725 own posts (70 of all 783 feed posts, which adds 4 of the 58 collaboration posts)"). No like-based comparison exists.

## GTA scheduled task (outstanding, needs a browser session)
Task "HMM - GTA MedSpa Index (Monthly)" still holds the superseded prompt (rediscovery, 596-account collection, scoring). It cannot be changed from this session. Replace its stored prompt with the entire contents of `_kit/gta-medspa-instagram/ROUTINE_PROMPT_50.md`, leave its schedule (the 15th, 09:15 America/Toronto) and every other task unchanged, then save. Until then do not let it fire (next fire 15 November 2026); if it cannot be updated in time, pause that one task.

## Validation
See `preflight_pages.json` for the page checks (links, images, titles, descriptions, canonicals, robots, sitemap, contact entries, edition 001 preservation). Structured data was parsed as JSON and checked against the visible text; it was not run through Google's Rich Results Test or any external validator.
