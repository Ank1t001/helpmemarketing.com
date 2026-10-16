STEP 0, DATE GATE
Check today's date in America/Toronto. If it is not the 15th of the month, reply only "Not the 15th; nothing to do." and stop immediately: no tools, no git, no connectors. Exception: if a routine-fire-payload block contains exactly the words FORCE RUN, ignore the date and continue.
On a scheduled 15th run (not a FORCE RUN), read the edition records under _kit/gta-medspa-instagram/editions/ on origin/main: if the latest published edition's collected_on is fewer than 20 days before today, reply only "Previous edition is recent; nothing to do." and stop.

You are preparing the next monthly edition of the Med Spa Index (https://helpmemarketing.com/medspa-index) for Ankit Kumar (HMM). Since edition 003 it is a fixed comparison of five named Ontario med spa Instagram accounts, re-collected every month for the window from the 15th of the previous month to the 14th of this month. This run collects the data, writes the month's reading, builds the page, saves the data to Google Sheets and Drive, and publishes a PREVIEW on the staging-gta branch. It never touches main. Ankit approves in this session afterwards. Nobody is watching: do not ask questions; make the safest reasonable choice and state it in the report.

READ FIRST
Repository helpmemarketing.com (cloned). Read CLAUDE.md, then in _kit/gta-medspa-instagram/ read README.md (section "Five-account editions") and EDITORIAL_RULES.md (section "Five-account editions"); they override anything older. The kit is excluded from deploys by .vercelignore; if .vercelignore no longer lists /_kit/, stop and report.
Do not use ROUTINE_PROMPT.md, ROUTINE_PROMPT_50.md, build.py, build_50.py, score.py, render.py or roster files: they belong to editions 001 and 002.

HARD LIMITS
- The cohort is cohort_five.json: the same five accounts, in that order, every edition. Never rediscover, replace, add or drop an account. If an account's own website no longer links to its Instagram account, keep it, say so in the report, and let Ankit decide.
- Never log in to Instagram, never use session cookies or a personal account, and never try to get round an account's restriction. An account Instagram does not show to the logged-out tools is reported as not readable, never as zero.
- Use the existing Apify allowance only. Never change billing, plans or spending limits. Run caps: profiles 0.25 USD, posts 2.00 USD, at most one posts re-run (2.00 USD); the total of all caps must stay at or under 5 USD. If Apify refuses for budget or limits, stop collecting and report.
- Meta Ad Library: try once. If it cannot be read, record "not checked" with the reason. Never treat that as "no active ads".
- Do not write to Notion. Do not touch the Real Estate or Hair Loss kits, their branches or any page other than those named below. Do not change build_five.py, derive_five.py, frames_five.py, template_five.html or head_five.html; if one blocks a correct edition, stop and report.
- No em or en dashes anywhere. Canadian spelling. First person singular for HMM ("I", "my"), never "we", "our" or "us". No pricing.

STEP 1, PREPARE STAGING (before any file changes)
git fetch origin. If origin/staging-gta exists and is NOT an ancestor of origin/main, someone has unmerged work on it: stop and report, and do not touch it. Otherwise: git checkout -B staging-gta origin/main. All work happens on this branch.

STEP 2, PRIOR EDITION CHECK
In _kit/gta-medspa-instagram run python3 check_live.py. It must PASS (the kit reproduces the live page and every snapshot exists). If it fails, stop and report: someone changed the page without updating the kit.

STEP 3, NEW EDITION RECORD
NNN = latest published edition + 1, three digits. Collected = today (Toronto). Window = the 15th of last month to the 14th of this month (Toronto), both included, as window_five.py computes it (python3 -c "import window_five;print(window_five.window('<today>'))"); consecutive editions follow on without a gap. window_days = its length (28 to 31).
Create editions/NNN/ with:
- edition.json: {"edition": "NNN", "status": "draft", "collected_on": today, "window": [start, end], "window_days": <its length>, "timezone": "America/Toronto", "snapshot_path": "/medspa-index/edition-NNN"}.
- accounts.json: {"edition": "NNN", "accounts": [...]} with the five entries of cohort_five.json in order, without "alias", plus "verification_date". For each, open its official_website (WebFetch) and confirm it still links to the Instagram account: if confirmed, verification_date = today; if the site cannot be read, copy the previous edition's verification_date and say so in the report.
- services.json: re-check the six service categories on each official website with the rule in the previous edition's services.json (Confirmed only from the brand's own site; each entry keeps its source link and detail). If every entry was re-checked today, checked_on = today. If any site could not be read, copy the previous edition's services.json unchanged (its checked_on stays) and say so in the report. Never mix dates.

STEP 4, COLLECT (Apify connector), one pass
1. apify/instagram-profile-scraper with usernames = the five handles, maxTotalChargeUsd 0.25. Save the reply as editions/NNN/raw/source_profiles.json.gz: gzip JSON {"run_id", "dataset_id", "actor", "started_at", "finished_at", "items": [every dataset item, verbatim]} (started_at and finished_at from the run).
2. apify/instagram-scraper with directUrls = the five https://www.instagram.com/<handle>/ URLs, resultsType "posts", resultsLimit 80, no date filter, maxTotalChargeUsd 2.00. Save every dataset item verbatim, one JSON object per line, as editions/NNN/raw/source_posts.jsonl.gz.
Read datasets with get-dataset-items (or the Apify resource reader) and page with limit and offset until every item is saved; large replies are saved to disk, so parse them from there and never retype values.
3. editions/NNN/run_ledger.json: {"edition": "NNN", "runs": [...]} with, per run: stage ("profiles" or "posts"), actor, run_id, dataset_id, started_at, finished_at, cap_usd, input (posts: {"resultsType": "posts", "resultsLimit": 80, "date_filter": null}), accounts (the five handles), items (number of saved items), hit_cap (true if the run stopped at its cap), saved (path). If a run hit its cap, stop and report.
4. Meta Ad Library: try https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=CA&q=<brand>&search_type=keyword_unordered once for one brand with WebFetch. If the page needs JavaScript or the fetch fails, write editions/NNN/adlibrary.json in the previous edition's shape with "result": "not checked", "reason" (what happened), and each check's status "not checked: page requires JavaScript" (or the real reason). Do not try other workarounds.

STEP 5, DERIVE
python3 derive_five.py --edition NNN. It must finish without an assertion. If it reports an account whose coverage is "incomplete" (the oldest unpinned post returned is inside the window), re-run the posts stage ONCE for all five with resultsLimit 200 (cap 2.00), replace raw/source_posts.jsonl.gz, rename the first posts entry in the ledger to stage "posts_superseded", add the new run as "posts", and derive again. If coverage is still incomplete, stop and report.

STEP 6, CODE THE POSTS AND THE STANDOUT COVERS
1. editions/NNN/coding.json: {"edition": "NNN", "method": copy from the previous edition, "types": copy, "posts": {shortcode: {"type", "topic"}}, ...}. Code every in-window post in observations.json (own and collaboration) with one type from cohort_five.json content_types and one short lowercase topic, from its caption and what it shows. Code what the post is, not how well it did.
2. python3 frames_five.py --edition NNN --fetch work/covers. The first run saves each standout post's cover as work/covers/<shortcode>.jpg and stops. Open and look at every cover image. Then add to coding.json, for exactly the standout posts in metrics.json:
   - standout_visuals {shortcode: one or two sentences on what the cover shows; quote overlay text exactly; describe only the cover, never the video or later slides}
   - standout_frames {shortcode: alt text, what is visible, no figures}
   - standout_titles {shortcode: a short factual card heading, for example "A pelvic floor reel that opened with a humorous line"}
   - frame_crop {shortcode: 0 to 1, the share of the extra height cut from the top when cropping to 4:5; 0.5 centres it, lower keeps more of the top so overlay text stays in frame}
   - standout_collab {shortcode: text} only where the caption tags a partner and that matters; otherwise leave it out
   - literal_numbers {"21": "age limit in Instagram's restriction reply", ...}: every number you quote from a cover or caption, with its source. Never use it for a figure the data computes.
   Run python3 frames_five.py --edition NNN --from work/covers. It writes the 640x800 WebP frames to /assets/index/medspa/frames/<handle>-cycleNNN.webp and editions/NNN/frames.json.

STEP 7, WRITE THE READING (editions/NNN/narrative.json)
Run python3 build_five.py --edition NNN --tokens to list every figure available, with its value. Then write narrative.json fresh for this edition. Read the previous edition's narrative.json (or, for edition 004, the edition 003 page) for structure and tone only: never carry a sentence that describes last month's posts.
Shape:
{"edition": "NNN",
 "comparability": "what makes the accounts' numbers not like-for-like this month (subjects, audiences, post counts), ending with: read each account against its own median, not as a league table",
 "findings": [three of {"title": "...", "text": "... <b>Denominator:</b> ..."}],
 "findings_takeaway": "...",
 "accounts": {alias: {"blocks": [["What it published", "..."], ["Interpretation", "..."], ["Limitation", "..."], ["One test", "..."]], "takeaway": "..."}} for exactly the readable accounts (aliases in cohort_five.json; "Observed gap" may replace "Interpretation" when the observation is a posting gap),
 "patterns": [two to five of {"title": "...", "text": "..."}], "patterns_takeaway": "...",
 "tests": [three of {"title": "... (finding N)", "compare": "...", "measure": "..."}]}
Rules (the build enforces the first four):
- Every figure is a token: {{a.vit.posts_in_window}}, {{s.sig.likes}}, {{p.posts_all}}, {{r.sig.vit.median_plays}} (ratio), {{prev.vit.posts_in_window}} (previous edition), {{a.las.gap_days}}, {{a.spa.before1}} (date of the last post before the window). Small counts in words: {{w.p.readable}} gives "four", {{W.p.readable}} "Four". Never type a figure; quoted numbers only via literal_numbers.
- No "we", "our" or "us"; no em or en dash; none of: viral, winning, the best, top-performing, leverage, unlock, supercharge.
- Each finding states its denominator. Each test title ends with "(finding N)" and its measure names what to read and when (for example saves seven days after posting).
- Separate observation from interpretation. Never claim a cause, a reason the clinic did something, bookings or enquiries. A posting gap is reported with its dates and "the reason is not known from public data". Comments are not bookings; a play is a view, not a person; boosting cannot be seen.
- A comparison with the previous edition uses prev.* tokens, says "compared with edition PPP", and is an observation, not a trend.
- An account that could not be read gets no narrative entry: build_five.py writes its card from the saved restriction reply.
- Takeaways: two or three short sentences, practical, each with one specific team question or one test with a named measure.

STEP 8, BUILD AND CHECK
1. python3 build_five.py --edition NNN must PASS. Fix narrative.json or coding.json until it does; never edit the scripts or templates.
2. python3 -m unittest tests.test_tools must pass.
3. Read the built page (medspa-index.html, between the REPORT BODY markers) end to end as a reader: every sentence true for this edition's data, no claim from last month, the restricted account (if any) described only by its saved reply.
4. Browser QA with Playwright (python3 -m http.server from the repo root, page /medspa-index.html): at 1280 px and 375 px the document does not scroll sideways; every standout image decodes at 640 px wide; sorting the comparison table works; no page errors. If Chromium is unavailable, report browser QA as NOT RUN.

STEP 9, PUBLISH TO STAGING
1. git diff origin/main --stat may show only: medspa-index.html, assets/index/medspa/ (this edition's two CSVs and frame files) and _kit/gta-medspa-instagram/editions/NNN/. Nothing else (the release step, not this one, changes the hub, /hmm-index and the sitemap).
2. One commit on staging-gta, message "Med Spa Index edition NNN (draft)". git push --force-with-lease origin staging-gta.
3. Vercel builds staging-gta automatically (project prj_FgAYUbd4Z46yAM5GfuYfdIZQalaJ, team team_b23KCbTsM0q2YjkanFnAsZKm). Find the deployment for the commit with the Vercel connector, wait until READY, then get a share link with get_access_to_vercel_url for <deployment url>/medspa-index. Open the complete link once without cookies (curl -L) and confirm it returns 200 and the Med Spa Index with "Edition <b>NNN</b>". Report that exact link; never retype a deployment URL.

STEP 10, SAVE THE DATA (Google Sheets and Google Drive connectors)
Sheet "HMM GTA MedSpa Index data", id 1_Qi7e54I4WG9M7Uie8lzrBwtbOreykvtqn0qku59QG8; Drive folder "GTA MedSpa Index", id 15xJ1lYPJM4W-8O2b9gXU-I_V2lvZfAjt. Never create a second Sheet or folder, never trash a file, never change another edition's tabs. Send Sheets writes without writeControl.
1. python3 export_five.py --edition NNN --status Preview --commit <short sha of the staging commit>. If the Sheet has no "E003 posts" tab, also run python3 export_five.py --edition 003 --status Published --commit <short sha of origin/main> and add E003 first.
2. Add tabs "ENNN posts" and "ENNN accounts" (clear them instead if they exist from an earlier attempt) and paste each TSV with update_spreadsheet pasteData (coordinate row 0, column 0; delimiter "\t"; PASTE_NORMAL); freeze and bold row 1. In "Editions", overwrite this edition's row if column A has it, otherwise paste editions_row.tsv on the first empty row.
3. Drive: upload this edition's two CSVs (plain, not converted) and run_ledger.json, named medspa-index-edition-NNN-<name>. Do not upload the raw files in editions/NNN/raw/: they are compressed and too large to pass through the Drive connector intact, and the repo commit keeps them. On a re-run, update files of the same name instead of adding new ones.
4. Read back: tab row counts equal file line counts; the Editions row reads as written; the files are listed in the folder. If a connector is missing or fails, finish everything else and report exactly what was not saved; never claim a save that did not happen.

STEP 11, REPORT (final message)
Lead with the share link and the commit. Then: window and collected date; for each account, posts in window, readable or not and why, and the change from the previous edition; the three findings in one line each; anything the data could not support that you left out; coverage and any re-run; Apify runs, caps and cost; Ad Library result; website and services checks (re-checked or carried); Sheet tabs and Drive files saved (links https://docs.google.com/spreadsheets/d/1_Qi7e54I4WG9M7Uie8lzrBwtbOreykvtqn0qku59QG8 and https://drive.google.com/drive/folders/15xJ1lYPJM4W-8O2b9gXU-I_V2lvZfAjt); every check with PASS, FAIL or NOT RUN. End with: "Reply 'ship it' to put this live."

DO NOT push to main, merge, ping IndexNow, delete branches or touch any other page in this run. A scheduled prompt is not approval.

WHEN ANKIT REPLIES "ship it" IN THIS SESSION
1. git fetch origin. Confirm origin/staging-gta is still the reported commit and origin/main is its ancestor; if not, stop and ask.
2. Release build on staging-gta: in the kit, run python3 build_five.py --edition NNN --target release --published-at <now, ISO with offset> --modified-at <same> --modified-source "provisional: release commit time, replaced by the production deployment ready time". It makes the page indexable, creates the snapshot /medspa-index/edition-NNN, updates the hub and /hmm-index text and the sitemap. python3 -m unittest tests.test_tools must pass. Commit "Med Spa Index edition NNN: release".
3. Fast-forward only: git push origin staging-gta:main (never force-push main; if main moved, stop and ask). Also push staging-gta.
4. Find the production deployment for that commit (target production) and wait until READY; if none appears within 2 minutes, create one with create_deployment (gitSource github Ank1t001/helpmemarketing.com, ref main, sha = the commit, target production). Take its "ready" time as ISO 8601 UTC with +00:00.
5. python3 build_five.py --edition NNN --target release --published-at <ready> --modified-at <ready> --modified-source "production deployment <id> (commit <short sha>) ready <ready>". This records the time on the page, the hub and the snapshot (with a metadata note in the snapshot head). python3 check_live.py must PASS. Commit "Med Spa Index edition NNN: recorded dateModified" and push to main (fast-forward) and staging-gta.
6. Update the Sheet: python3 export_five.py --edition NNN --status Published --commit <short sha of the shipped main commit>; overwrite this edition's Editions row; read it back.
7. Verify production (https://helpmemarketing.com, add a cache-busting query): /medspa-index returns 200 with one indexable robots tag, canonical /medspa-index, dateModified equal to the recorded time, no datePublished, "Edition <b>NNN</b>", the FAQ data matching the visible FAQ; /medspa-index/edition-NNN returns 200 with one "noindex, follow" and its own canonical; every earlier snapshot is byte-identical to before the release; the frames and both CSVs return 200; /gta-medspa-index and /medspa-index.html 308 to /medspa-index; /medspa-marketing-research and /hmm-index show edition NNN; /_kit/gta-medspa-instagram/README.md returns 404. Report each result, with failures listed separately.
8. Remind Ankit that "Request indexing" in Search Console and the Rich Results Test are manual Google checks.

IF BLOCKED
If Apify, Vercel, Google Sheets, Google Drive or a GitHub push is unavailable, do every step you can, then report exactly what was blocked and what to reconnect. Never claim an unperformed collection, save, check or deploy.
