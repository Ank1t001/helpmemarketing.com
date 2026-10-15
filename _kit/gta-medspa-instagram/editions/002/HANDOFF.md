# Edition 002 handoff (written 2026-10-15; read this, not the old conversation)

Repo `Ank1t001/helpmemarketing.com`, branch `staging-gta` (kit work only; never touch main, public pages, sitemap, schedules, other indexes or the treatment study). Kit folder: `_kit/gta-medspa-instagram/`. Routine rules: CLAUDE.md "Index generator contract" and `EDITORIAL_RULES.md`. Commit 8a9323a is kept as is; do no more optimisation development (use existing tools, ad hoc one-off Python is fine for data steps, no new tool files).

## State (all verified, files hashed in `editions/002/checkpoint.json`)
- Discovery: run 9eUmdtGUOD6YBu17u, dataset hM1gda12hTum3eC8N, 2,842 unique listings, saved as `editions/002/discovery_listings.json.gz`.
- Roster: 872 eligible unique accounts (`roster_eligible.json`), 647 listings with no Instagram link ("account unresolved", kept apart), 49 listings with an unverified link (`roster_unverified.json`), exclusion log in `exclusions.json`. 600 is a MAXIMUM cohort. Sample: seed 20261015, region-proportional, Multi-region its own stratum (`sampling.json`, `roster.json`). Reserve order: `sample_rank_in_stratum` in `roster_eligible.json`.
- Profiles: run Zoi0DpoQSneBRv56E, dataset 5vrqwBWwjGbgWWXto, 600/600 items, saved as `source_profiles.json.gz`. `profiles_verified.json`: 562 "verified", 38 "failed" (not found or private), 38 reserve replacements proposed (`replacements_pending_profile_check`).
- Window is FROZEN: 90 days ending 2026-10-15, start 2026-07-17, both inclusive. Do not move it because execution was delayed. `edition.json` has not been updated yet for edition 002 (still edition 001 values); set edition, scraped_at 2026-10-15, window, status when you next write it.

## Environment facts
- Connector-only: no APIFY_TOKEN, shell cannot reach Apify. So `tools/apify_tool.py watch`, `start` and `fetch` cannot be used (they are only tested against a mock). Usable: `status --raw FILE` is not useful either (no way to save a connector reply to a file except large replies the harness persists). Be honest in the report: connector calls were used, with infrequent checks (`get-actor-run`, waitSecs 45 at most, then wait several minutes between checks using a background Bash timer or a single longer check; never one poll per minute).
- Actor inputs must be passed inline in the `call-actor` input. Never print handle lists or raw records beforehand; produce the JSON with a one-off Python snippet and pass it once. Read datasets with `ReadMcpResourceTool` on `http://api.apify.internal:3333/v2/datasets/{id}/items?...&limit=250&fields=...`; large replies are saved to disk automatically (parse the saved file with Python, do not display it).
- Prices (BRONZE, per result): instagram-scraper 0.0023, instagram-profile-scraper 0.0023. `call-actor` has `callOptions.maxTotalChargeUsd` (pay-per-event actors).
- `python3 -m unittest tests.test_tools` must still pass (run before committing).

## Task 1: correct the checkpoint
The `profiles_verified` stage was marked done while replacements were unresolved. Remove that stage record from `checkpoint.json` (it must read pending) and keep a record in the stage `profiles_collected` meta. Classify every selected account, from `profiles_verified.json` and the roster, into four separate states and store them in `editions/002/profile_status.json` (do not weaken the existing eligibility or replacement rules, and do not treat name similarity as official evidence):
1. profile found and public;
2. official evidence connecting the account to the clinic: the profile's external link has the clinic's website domain, OR the clinic's own website or Google listing links to the handle (`handle_source` contains "listing contact data"). Username or profile-name similarity and a city in the biography are weaker signals and are labelled "weak evidence only", not official;
3. private, not found or otherwise unresolved;
4. replacement pending (failed account whose seeded reserve has not yet been checked).
Report the four counts.

## Task 2: bounded profile check of the 38 reserves (once)
One `apify/instagram-profile-scraper` run for the 38 reserve handles in `profiles_verified.json` -> `replacements_pending_profile_check`, `maxTotalChargeUsd` 0.5 (expected about 0.09). Reuse the 600 existing profiles; do not rescrape them. Save the 38 results next to the others (add to `source_profiles` as a new file, e.g. `source_profiles_reserves.json.gz`), apply the same four-state classification, substitute a reserve only if it is public and has official evidence, otherwise leave the slot unresolved. DO NOT launch a second replacement round; list remaining unresolved slots in the report. Update `sources.json` with the run.

## Task 3: prepare the pilot (before launching anything)
Pilot = 50 accounts chosen reproducibly across the geographic strata: use only accounts in state 1+2 (public, official evidence); allocate 50 across Toronto, Peel, York, Durham, Halton and Multi-region proportionally to their selected counts (largest remainder), then within each stratum sort handles alphabetically and shuffle with `random.Random(f"pilot:20261015:{region}")`, take the first n. Never select by followers, posts, engagement or expected rank. Save `editions/002/pilot_selection.json` with seed and allocation.
Confirm and write down in `editions/002/pilot_plan.json` BEFORE launching (use `fetch-actor-details` with pricing, inputSchema and readme for `apify/instagram-scraper`, plus `search-apify-docs` if needed):
- actual pricing and billing basis (per result written?);
- whether `onlyPostsNewerThan` reduces collection and billing or only filters output afterwards (do not guess; find the actor's documentation, and say "unconfirmed" if the docs do not say);
- whether `maxTotalChargeUsd` is supported and enforced for this actor (pay-per-event);
- how partial results and completed accounts are preserved (dataset items written before a cap stay; no way to resume mid-account).
Budget: maximum $5 additional Apify charges for the pilot. If the cap cannot be enforced for this actor, DO NOT launch and report. Note: 50 accounts x resultsLimit 200 x 0.0023 = 23 USD worst case, above the cap, so use several smaller runs (suggested: 5 runs of 10 accounts, each `maxTotalChargeUsd` 1.0, run one after another so total is at most 5) so per-account completeness can be judged. Keep `resultsLimit` 200 (the existing per-account limit), `resultsType` posts, `onlyPostsNewerThan` 2026-07-17, inputs as profile URLs. If a run hits its cap, mark its accounts incomplete; do not extrapolate their low counts.

## Task 4: run the pilot only
Run the pilot runs, with infrequent compact status checks. Write `work/posts.jsonl` rows in the format `score.py` expects (see the header of `score.py`: handle from `inputUrl`, owner, shortcode, timestamp, type, plays, likes, comments, caption, coauthors, pinned) but keep pilot rows clearly separated (e.g. `work/posts_pilot.jsonl`) because the pilot is not a full collection. Read dataset items with the fields listed in the routine prompt (shortCode,type,caption,commentsCount,likesCount,timestamp,ownerUsername,inputUrl,videoPlayCount,coauthorProducers,isPinned), page with limit 250 and parse from disk. Per account decide complete / incomplete (complete = oldest post returned is before the window start, or the account's posts ran out, and result count below 200; incomplete otherwise). STOP after the pilot: do not launch the remaining accounts. Do not build, publish or save to Sheets in this stage.
Record each run in `sources.json` (run id, dataset id, started, finished, status, items, usd or estimate with the basis) and set a checkpoint note (do not mark `posts_collected` done: only the pilot ran).

## Task 5: report (final message, compact)
Accounts attempted and completed; posts inside the window; actual cost where available (and what is estimated); whether any run hit a cap or returned incomplete histories; estimated remaining cost for the other accounts WITH assumptions (do not extrapolate from capped or incomplete accounts); model calls and token usage for this stage (count your own calls; give measured token figures only if available); the exact resume checkpoint (`python3 tools/checkpoint.py check --edition 002` output plus what is pending). Commit the new saved files to `staging-gta` as one commit (kit only, trailer lines as instructed by the session) and push with `git push -u origin staging-gta`. Never push to main.

Keep outputs compact: counts, paths, failures, short evidence excerpts. No handle lists, raw records or repeated schemas in context.
