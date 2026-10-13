# Real Estate Index Instagram monthly build-kit migration

Version: cycle 005 (2026-10-13), built on the 2026-10-13 monthly migration draft. This is a separate Instagram kit. It does not replace or change other shared builders.

Canonical URL: https://helpmemarketing.com/realestate-index
Schedule: the 14th of each month, 09:00 America/New_York.

## What is implemented

- Portable Python standard-library builder; no absolute `/home/claude` paths.
- Current site shell from GitHub main `261bcbf`, including its comparison script and reading-level navigation.
- Current report structure: ri-overview, ri-rankings, ri-creative, ri-insights, ri-test, ri-advanced, ri-data. Advanced research remains in expandable sections.
- Current site gate endpoint, request payload and event handling preserved. No Apps Script changes or test submissions.
- Instagram-only CSV: 68 ranked-firm rows plus 10 REFERENCE rows recovered from the published cycle 003 CSV.
- Separate last verified data and next scheduled refresh. No public cadence promise.
- Five-firm IG_BRANDS roster and unchanged scoring, reproduced exactly against cycle 003: 65, 56, 44, 36, 31.
- Full research for the Instagram edition retained; other-platform creative cards and CSV rows excluded.
- Original shared build files remain intact in `../original/` in the package. They are not overwritten.

## Files and authority

- `build_v2.py`: input checks, scoring reproduction, CSV checks and local candidate output.
- `ig_body.py`: body-only render into the current shell.
- `site_shell.html`: current repository page used as persistent shell; update from GitHub before a later cycle if the production shell changes.
- `report_body.html`: reviewed editorial body for this dataset. It retains the approved cycle 003 research. It is NOT an evergreen narrative. Each new cycle must refresh its findings, cards, tables, source citations, experiments and historical comparisons using actual data.
- `ig_cycle.json`: Instagram-specific cycle metadata. Do not use legacy CYCLE/SCRAPED/WINDOW fields in the shared dataset for Instagram; they describe an older unrelated dataset.
- `body_review.json`: binds the reviewed body to the cycle and dataset fingerprint. A hash proves file identity, not the truth of editorial claims. Human/agent evidence review is still required.
- `reindex_data.py`, `ig_postlog.json`, `ig_caps.json`: recovered source inputs. Only the Instagram fields may be refreshed for this task.
- `reindex-cycle003-postlog.csv`: recovered exact public row-level Instagram data.
- `history/`: prior scoreboard evidence and verification status. Preserve original files.
- `SCHEDULED_TASK.txt`: replacement task instructions for this migration version.

## Run the recovered baseline

From this folder:

```bash
python3 build_v2.py --verify-baseline --as-of 2026-10-13
```

Output: `output/HISTORICAL_QA_cycle003.html` and `output/validation.json`.
This is historical local QA, not a fresh report and not a production-ready release.

The normal command deliberately rejects historical inputs:

```bash
python3 build_v2.py
```

Do not bypass this by changing dates or relabelling September metrics.

## Monthly fresh-cycle workflow

1. Read HMM Notion and the GitHub Index build brief, especially section 7. Preserve the current site head, nav, wrapper, footer and gate transport.
2. Obtain a fresh 90-day public Instagram scrape plus follower counts for the five firms and Wealthsimple. Filter ranked analysis to 30 days by timestamp, including pinned-post exclusion and permitted Equiton coauthorship. Reference data stays out of medians, percentiles and ranks.
3. Record raw artifacts, scrape timestamps, source handles, exclusions and caption coverage. Refresh IG, IG_BRANDS follower counts, IG_PEAK_90D, IG_REF, post log and full captions. Do not overwrite unrelated shared definitions.
4. Recover and reproduce the immediately prior cycle before trusting new scores. Cycle 004 remains BLOCKED in this package; its raw source inputs were not found. Do not silently treat cycle 003 as cycle 004.
5. Refresh every cycle-specific part of report_body.html from verified inputs. Preserve the seven section IDs and exact scoreboard headings. Keep the 45/30/25 scoring unchanged. Momentum and Consistency must not be introduced without separate approval.
6. Set ig_cycle.json to the actual new cycle, scraped_at, explicit 30-day window, status=fresh, CSV filename, prior_cycle and verified prior_verification record. Set next_scheduled_refresh to the next monthly 14th, November 14 for a successful October 14 scrape.
7. Record the reviewed body SHA-256 and the dataset fingerprint in body_review.json. Record publication_review=complete only after evidence, creative, advertising and editorial checks are actually complete.
   `python3 prepare_review.py` computes file identities and cycle metrics but deliberately leaves review pending. Use those metrics to refresh report_body.html; run it again after the body edits. It never grants publication approval.
8. Run python3 build_v2.py on the scrape date. It emits a local review candidate only. It does not deploy or claim a refreshed public page.
9. Before publishing, Claude Code swaps only between REPORT BODY markers in the latest actual repository file. Review the diff and get explicit approval to ship. Update sitemap lastmod truthfully after the page change. Browser QA must pass before approval; do not claim it from static checks.
10. After approved publication, verify the live cycle, dates, gate behaviour, CSV contents, comparison controls, log filters, frames and mobile/desktop layout. Only then claim last verified data has advanced on the public page.

## Blockers and evidence limits

- Cycle 004 raw inputs and fresh captions are not recovered. Its scoreboard repeats cycle 003's listed metrics, but that alone does not prove how it was produced.
- The stored ig_caps.json is older than the September dataset. Do not claim its captions were refreshed. Normal fresh-cycle builds require current caption coverage.
- Historical source frame descriptions are carried from the published report; no new vision review was performed.
- Browser QA was attempted but the execution environment has no installed Chromium binary. Desktop table overflow, mobile layout and interactive behaviour remain pending browser verification.
- Raw Drive upload is supported by the currently exposed upload_file/update_file actions. The older fixed 45 KB connector ceiling should not be assumed for these actions. Verify actual upload success and bytes rather than truncating files.

## Validation performed

- Cycle 003 scores and ranks match all five published rows exactly.
- Recovered CSV rows match the ranked dataset's brands, likes, comments and shortcodes.
- CSV contains Instagram only, with reference rows separate.
- Section IDs, scoreboard headings, no-video cells, frame paths, gate endpoint and payload checked.
- Em/en dash normalisation checked.
- Stale-input normal build correctly fails.

No website deployment, fresh scraping, form submission, Notion write or Claude schedule modification was performed.


## Cycle 005 (collected 13 October 2026)

- Window 2026-09-13 to 2026-10-13 (30 days); 90-day lookback from 2026-07-15. Next scheduled refresh 2026-11-14.
- Roster unchanged: Skyline, Equiton, Lankin, Pier 4, McGillivray Capital. Wealthsimple is REFERENCE only.
- @parvisinvest was considered on 13 Oct and left off at Ankit's direction: like counts hidden on 13 of 16 in-window posts, no own video, multi-issuer platform.
- Prior-cycle check: cycle 004 raw inputs were never recovered. Ankit approved a baseline exception on 13 Oct (history/cycle004-verification.json, status exception_approved). Scoring reproduced cycle 003 exactly (65, 56, 44, 36, 31) from history/reindex_data_cycle003.py before cycle 005 numbers were used. Rank movement reads the published cycle 004 scoreboard CSV.
- Results: Pier 4 72 (#1, up 1), McGillivray Capital 67 (#2, down 1, BOOST 67x from a reel co-authored with @scott_mcgillivray), Skyline 39, Lankin 38, Equiton 30.
- Ad library (active, Canada, exact phrase): all five firms had live investor ads. Counts are minimums; Equiton hit the 25-result cap.
- Correction published on the page: the cycle 003 claim that McGillivray's ads were the only documented paid social was incomplete.

## Body generation (new at cycle 005)

`report_body.html` is now generated by `gen_body.py` from `reindex_data.py`, `ig_postlog.json`, `ig_cycle.json` and
`cycle_inputs.json` (the cycle's editorial strings, frame reads, ad counts, campaign rows and FAQ). Every count, median,
badge, no-video cell and CSV count is computed, so consistency rules 1 to 3 hold by construction. Rewrite
`cycle_inputs.json` from the new evidence each cycle, then:

```bash
python3 gen_body.py && python3 prepare_review.py   # review pending
# review the evidence, then set publication_review=complete in body_review.json
python3 build_v2.py --as-of YYYY-MM-DD             # on the scrape date
```

To repeat the baseline check, temporarily point the kit at `history/reindex_data_cycle003.py` and
`history/ig_postlog_cycle003.json` and run `python3 build_v2.py --verify-baseline` with `ig_cycle.json` set to cycle 003.

## Authorship, citation and editions (2026-10-13)

- `report_body.html` is now the reviewed live page body (founder-approved 13 October 2026), with tokens `{{CYCLE}}`, `{{LAST_VERIFIED_LONG}}`, `{{NEXT_REFRESH_LONG}}`, `{{OVERDUE}}`, `{{RANKED_ROWS}}`, `{{REFERENCE_ROWS}}` and `{{GATED_CSV}}`. Each cycle, update its figures and editorial text from the new evidence; keep its structure, wording rules and the authorship blocks.
- `gen_body.py` is retired and exits on run: it emits the pre-13-October structure (old header, BOOST/ORGANIC flags, "Advanced research").
- `ig_cycle.json` carries `modified_at`: the recorded ISO 8601 time with timezone of the production deployment that made the last content change (Vercel deployment ready time), plus `modified_at_source`. `ig_body.render` writes it into the head's Article `dateModified`; the build rejects a date alone, a missing timezone or a midnight placeholder. Snapshots take the same value when first generated and are never regenerated, so archive dates never refresh. There is no `datePublished`: the earliest evidence is the 2026-08-14 commit that added the page, which records the code change, not verified first publication, and Vercel keeps no deployment record that old.
- `build_v2.py` also writes `output/edition-NNN.html`, a fixed snapshot (self canonical, exactly one robots tag `noindex, follow`, archived-edition note, extra breadcrumb). The build fails if `datePublished` appears, if `dateModified` differs from `modified_at`, or if the Article image (the index artwork `/assets/index/real-estate/og.jpg`, 1200x630) is missing. On publication copy it to `realestate-index/edition-NNN.html` in the site repo and add a row to the Edition history table in `report_body.html`. Never edit or regenerate an earlier snapshot.
- Validation now fails if the linked byline, researcher profile, cite block (matching the cycle and date), snapshot link, edition history, methodology section or the Article author/publisher `@id` links are missing.
