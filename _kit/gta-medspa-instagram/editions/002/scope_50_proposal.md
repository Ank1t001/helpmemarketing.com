# Edition 002 scope: 50-account GTA medspa Instagram benchmark (proposal, 2026-10-15)

Status: proposal only. No public page, report_body.html, schedule or other index was edited. No paid Apify run was launched; the only Apify calls were free dataset reads. Supporting files: `scope_decision.json`, `scope_50_accounts.json`, `scope_50_gaps.json`, `scope_50_profile_extract.json`.

## 1. The 50 accounts and the regional spread

The seeded pilot reproduces exactly. Over the 596-account cohort in `cohort_frozen.json` (region counts York 163, Peel 85, Toronto 162, Halton 85, Durham 67, Multi-region 34), largest-remainder allocation gives York 14, Peel 7, Toronto 13, Halton 7, Durham 6, Multi-region 3, and sorting handles then shuffling with `random.Random("pilot:20261015:{region}")` returns the saved 50 in every stratum (order and membership). Nothing was selected on followers, posts, engagement, expected rank or scrape success; the draw happened before any post collection.

Account types: 47 single-location, 2 multi-location groups, 1 chain. Origin: 46 from the original sample, 4 reserve substitutes (seeded reserve order, same stratum).

How the pool was defined, and the selection effects to disclose:
- Frame: Google Maps discovery from 60 capped searches (2,842 unique listings), reduced by clinic eligibility, geography and an Instagram link to 872 eligible accounts, then a region-proportional random sample of 600, then a profile check. The pool is the 596 that survived that check. So the 50 are a sample of a sample of the listings the searches returned, not of every GTA clinic.
- Public profile and official link were required at selection time (an official link means the clinic's website or Google listing carries the handle, or the profile's link has the clinic's domain; name similarity alone never counted). Clinics with no Instagram link on their listing (647 listings) or an unverified link (49) are outside the frame. Accounts whose profile was not found or private (38 originals) were replaced from the seeded reserve list (34 replaced, 4 slots left empty).
- Checked, not assumed: one rule gap. The profile check treated "Restricted profile" (age gate) as public, so 12 restricted accounts sit in the 596 pool. That keeps unscrapable accounts in the frame rather than filtering for success, and they are shown as restricted. One falls in the 50 (see below).

Eligibility re-check of the 50 (roster_build.py `eligibility` and `geography` on the discovery listings, listing-to-handle link, region):
- 49 of 50 pass every rule. Two flags to explain: reviveskinmedicalspa (Multi-region) has the handle on one listing (Milton, Halton) and its second listing (Mississauga, Peel) has no handle; it is grouped by the shared website domain, as the roster rule does, so it passes. skinvitality (Multi-region, 8 listings across Halton, Durham, Peel, Toronto, York) is eligible as a clinic and has an official listing link, but its profile is age-gated, so "public profile" is not established. It was admitted by the documented profile rule, so it is selected, but it is class C and cannot be analysed. It is not replaced.

## 2. How many have usable data

Classes are separate and never merged (evidence in `scope_50_accounts.json`):
- A genuine inactivity: 12. Collection succeeded and the newest posts predate 2026-07-17 (profile postsCount 0 for 1; for 11, the profile scraper's latest posts, read free from dataset 5vrqwBWwjGbgWWXto, are all before the window, newest non-pinned dates between 2023-07 and 2026-06-30; in 3 of them the post scraper returned only older pinned posts).
- B in-window posts collected: 36 (783 in-window rows, 824 rows total including 41 outside, no account near the 200 limit, largest 72 rows).
- C restricted or inaccessible: 1 (skinvitality).
- D failed collection: 0.
- E uncertain: 1 (mississauga.gracemed: public, no postsCount, no latest posts, post scraper returned nothing).

By region (A/B/C/E): York 3/11/0/0; Peel 0/6/0/1; Toronto 5/8/0/0; Halton 2/5/0/0; Durham 2/4/0/0; Multi-region 0/2/1/0.

Selected 50. Analysed for posting activity: 48 (36 with posts plus 12 with no in-window posts). Analysed for post-level measures: 36. Not analysed: 2 (1 restricted, 1 uncertain). Ranked or scored: unknown until the score step, because the three-reel threshold applies after collection and will reduce the ranked number below 36.

## 3. Remaining gaps and what would close them

- mississauga.gracemed (E): a profile re-check of that one account would settle whether it has posts. If postsCount is 0 it becomes A; if posts exist, one post-scraper run for that account with onlyPostsNewerThan 2026-07-17.
- skinvitality (C): nothing possible with the public scrapers; it stays "restricted".
- Limits that no extra run in this plan removes: class B rows under 200 show no cap was hit but not that the window was fully paged; class A relies on up to 12 latest posts per profile; 5 restricted_page errors came back without an account name across the 5 pilot runs and cannot be attributed (each of the 50 has its own outcome, but a partial restriction cannot be ruled out). The Apify account hit its billing-cycle usage limit during batch 16, so any paid run needs the founder to raise or reset it first.

## 4. Estimated incremental cost (estimates only; no billed figures exist)

Basis: BRONZE 0.0023 per result written; the pilot averaged 824 / 50 = 16.5 rows per account.
- Gap closure (recommended): about 0.0023 for the profile re-check, plus at most about 0.03 for one account's posts. Total under 0.05 USD.
- Optional confirmation re-run of the 12 class A accounts, limit 12 rows each: at most about 0.33 USD. Adds little, since the profile evidence already exists.
- Optional full re-run of all 50 in smaller batches to look for paging problems: about 1.9 USD (824 rows x 0.0023), the same as the pilot's estimated cost.
- Not needed: any collection for the other 546 accounts. The 6,019 batch rows already saved (estimated 13.8 USD, 6,019 x 0.0023) stay preserved and are excluded from the analysis.

## 5. Proposed publication wording and limitations

Positioning: "A 50-account GTA medspa Instagram benchmark." Never a GTA ranking, never a ranking of clinics. The score describes Instagram video activity.

Proposed lede (first person, edition not cycle, no dashes): "I looked at the Instagram video activity of 50 medspa accounts in the Greater Toronto Area over the 90 days from 17 July to 15 October 2026. The 50 are a region-proportional random sample of accounts I found through Google Maps searches, so this is a benchmark of a sample, not every GTA clinic and not a ranking of clinics."

Proposed coverage line: "Selected 50. Posting activity analysed for 48: 36 posted in the window and 12 had no posts in it. 1 account is restricted by Instagram and 1 could not be confirmed, so both are shown as such and are not counted as inactive."

Limitations to state in the page:
- Sampling frame: Google Maps discovery from 60 capped searches, so not every GTA clinic. Accounts needed a public profile and an official link from the clinic's website or Google listing at selection time. Clinics without a linked Instagram account are outside the frame.
- Region-proportional random sample drawn with a fixed seed before any posts were read; nothing chosen on followers, engagement or results. Multi-region accounts are their own group.
- Measures are recorded plays, not reach; comments are a public signal, never bookings or clinic performance. The three-reel ranking threshold applies after collection and will reduce the number of accounts that can be ordered; accounts under it are listed without a rank.
- Edition 001 used a different roster; differences from it are not clinic performance movement and are not compared.
- Restricted, failed or uncertain accounts are shown as such. A 200-post limit per account was never reached, but the scraper's date filter means complete paging of every window cannot be proven from the rows. No single account has more than 72 rows.

## Kit changes needed before a build (not made)

1. edition.json: edition 002, scraped_at 2026-10-15, window 2026-07-17 to 2026-10-15, status, sample size 50, selected and analysed counts.
2. Roster input: replace the cohort used by score.py, render.py, build.py and export_sheet.py with the 50 in `scope_50_accounts.json`; carry classes A to E into the scoreboard; keep the 6,019 batch rows out of every input.
3. report_body.html and EDITORIAL_RULES.md: title and H1 ("50-account GTA medspa Instagram benchmark" in place of "GTA Medspa Instagram Marketing Benchmarks"), lede, tile labels (Selected, Analysed, Ranked, Restricted or uncertain), the "Clinics included" line, methodology and sampling frame, a coverage section with the A to E counts, limitations, dataset description, and the edition 001 non-comparability note.
4. Article and FAQPage JSON-LD, meta description, OG text and breadcrumb wording to match; the FAQ must match the visible FAQ.
5. score.py and build.py: apply the three-reel threshold after collection and report ranked count separately; add class handling so restricted, failed and uncertain are never zero-post; `--check-live` must still PASS against the edition 001 snapshot.
6. Hub /medspa-marketing-research, /hmm-index card (refresh plan, latest published data, next collection) and the edition history: wording for a 50-account sample.
7. ROUTINE_PROMPT.md, ROUTINE_PLAN.md and the scheduled task prompt: the monthly refresh must say it re-collects the 50 only (or a new seeded 50, the founder's call), and carry the same disclosures.
8. Sheet export (Editions row, scoreboard, post log, roster): add selected, analysed and class columns.
9. Tests (tests/test_tools.py): cover the 50-account inputs and class rules.
