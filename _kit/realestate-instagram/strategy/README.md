# Five-firm strategy comparison (founder, 2 November 2026)

The roster is **Equiton, Skyline, Lankin Investments, Greybrook Realty Partners and Centurion Asset Management** (founder, 2026-11-02; applied the same day to the whole page as a revision of edition 005; Pier 4 and McGillivray Capital left the board). This folder holds the website, organic and paid comparison of those five, shown on `/realestate-index` in the Website Messaging view, at the top of Organic Social and Paid Social, and as "Recommendations for the five firms".

| File | What it is |
|---|---|
| `derive_ads.py` | Meta Ad Library records from private apify/facebook-ads-scraper output: focus, likely stage, format, destination, flags. Writes `ads.json`. |
| `derive_organic.py` | Organic records: edition posts for the firms on the board, Greybrook's posts for the same window. Writes `organic.json`. |
| `websites.json` | Website reads (homepage and main investor page), short quotes, page-text hashes. Written by hand from a Chromium read. |
| `render.py` | Renders the five blocks between the `<!-- STRATEGY:* -->` markers in `../report_body.html`. Every figure is counted from the records. |

## Accounts and advertiser pages (2 November 2026)

- Instagram: @equitoninc, @skylinegroupofcompanies, @lankin_investments, @greybrook (linked from greybrook.com). Centurion: no corporate Instagram account found (centurion.ca links none; four likely handles do not exist; a name search found only an unrelated account). Check again each refresh; never invent one.
- Meta advertiser pages: Equiton Inc. 762651820485779 (also shown as Equiton Canada), Skyline Wealth Management Inc. 1136216849873517, Skyline Living 230167614033735 (resident leasing, counted separately), Lankin 256257607565454, Centurion Asset Management Inc. 133679347320566. No active ads matched "Greybrook".
- Websites: equiton.com (bot check on 2 November; not bypassed; needs a manual read), skylinewealthmanagement.ca (with skylinegroupofcompanies.ca), lankin.com, greybrook.com, centurion.ca.

## Refresh
1. Ad Library, Canada, active: exact-phrase searches for each firm name, then each page id above in full (`view_all_page_id`), plus a count-only run (`onlyTotal`). Keep raw output private; pass it to `derive_ads.py` (update `COLLECTED`, the run ids and `library_totals`).
2. Read each website (homepage and main investor page) and update `websites.json`, with hashes of the page text. Never bypass a bot check: record the site as not read.
3. Update `derive_organic.py` for the edition's posts and run it.
4. `python3 render.py`, record the new body hash in `../body_review.json`, then build. The body's wording rules (`../EDITORIAL_RULES.md`) apply here too: active ads found, never spend; a stage is a reading of wording, not a result.

## Website Messaging (2026-11-03, founder)

`website_view` renders one glance table from each firm's `glance` (offer, evidence, next) and the two `examples` (captioned crops in `/assets/index/real-estate/website/`, SHA-256 recorded). `website_sources` renders the nine per-firm fields, collection notes, `corrections` and the unresolved Lankin comparison into Sources & evidence between the `STRATEGY:websrc` markers. Equiton's site shows a bot check to Chromium; on 2 November 2026 it was read in the founder's own browser with Claude in Chrome (`read_by`), with no page text or hash kept. The Centurion minimum was corrected on 3 November 2026 after the Apartment REIT page was read again.

`paid_section` (Paid Social, 2026-11-03) also reads `ad_destinations.json`: the running-time, button and destination table and the longest-running ad per firm are counted there; `ads.json` `examples` is kept as a record but no longer rendered.
