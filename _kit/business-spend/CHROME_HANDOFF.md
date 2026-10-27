# Chrome handoff: Business Cards & Spend Management Index, edition 001

Edition 001 was collected by server fetch only (23 October 2026, 10:39 a.m. to 10:48 a.m. Toronto time; no JavaScript, no cookies). The items below need a real browser. None of them may be described as checked until the files listed here arrive and `ingest.py browser` accepts them.

## Status (updated 23 October 2026, after the browser pass)

The browser pass of 23 October 2026, 12:00 p.m. to 12:14 p.m. Toronto time (package `business-spend-browser-pass-2026-10-23`, 34 captures) covered items 1 to 15 below. Its captures are in `sources.json` (`S-<CODE>-BROWSER-...`, method `browser`, screenshot hashes only), and the observations it changed carry the browser sources. The ten differences it reconciled carry a `reconciliation` class (A to D) and are listed on the page under "How the reported differences were reconciled". Screenshots are held privately outside the repository; check them with `validate.py --raw RAW_DIR --browser SHOTS_DIR`.

Still open after the pass:

- Venn: what the homepage line "200+ countries in 30+ currencies" shows to visitors (in the page code; visibility not established).
- Float: the network of Float Charge (not stated separately); what happens after a demo is booked; whether the demo form's "How did you hear about us" question is required. Transfer pricing is now from the Payments page (server fetch, 23 October 2026, 2:33 p.m.; not seen in a browser).
- Ramp: a Canadian rewards rate was not found in the reviewed sources (R1 would capture the Rewards Terms). Decision of 24 October 2026 on R2: no retained capture or other authoritative source supports the card supplement's payment terms or conversion margin (the screenshot shows only the opening section; the server copy is a script shell), so both details were removed from the page and the limitation is stated. R2 would allow them to be restored. A server fetch of Ramp legal pages returns only a script shell (13 characters).
- Airwallex: the terms for the "Credit line for corporate cards" (class D); the rebate terms and what "eligible" covers (class D); whether the fee schedule's 1.00% Auto Conversion Fee applies to card purchases; the demo booking form (not opened).
- Loop: whether the Basic plan earns points on card spend in currencies other than CAD, USD, EUR and GBP (the earn-rate table does not list them).
- Loop: the product tour beyond its first screen.
- Not possible without an account or a submission: any step after the first screen of the six journeys.
- The browser pass used a normal Chrome profile (not signed in to the providers) and checked mobile in a 390px frame; my own checks cover real keyboard focus and real mobile viewports.
- Social module (Instagram only, 25 July to 22 October 2026; LinkedIn dropped by the owner on 27 October 2026): not started. Steps S1 to S6 below.

## Open capture requests (release review, 24 October 2026)

| # | What to capture | Start from | Observation |
|---|---|---|---|
| R1 | Ramp Rewards Terms, logged out, from Canada: full-page screenshots that show "Last Updated", Section 1.3 (Qualified Purchases) and the Canada Regional Schedule in full, plus any stated earn rate for Canada. Copy the visible text of the Canada schedule into a `.txt` file beside the screenshots. If no Canadian rate or schedule is visible, capture the page anyway and say so. | https://ramp.com/legal/customer-terms/services-terms/rewards-terms | O-RMP-05 |
| R2 | Ramp Canada Card Supplement (details currently omitted; capture needed to restore them): full-page screenshots covering "Last Updated", Section 1 (Canadian Card Program), the statement and payment sections (payment in full, pre-authorised debit) and the currency conversion clause ("will not exceed three percent (3%)"). Copy the visible text into a `.txt` file. | https://ramp.com/legal/customer-terms/services-terms/canada-payment-card-supplement | O-RMP-02, O-RMP-07 |

Manifest lines use the format below with `platform` `ramp` and `role` `legal-rewards` (R1) or `legal-canada-card` (R2); list the observation IDs in `observations`. Until R1 arrives, the page says only: "A Canadian rewards rate was not found in the reviewed sources."

## Social module: Instagram, 25 July to 22 October 2026 (planned; owner in Chrome)

Brief and rules: `SOCIAL_MODULE_BRIEF.md`. Window: **25 July through 22 October 2026, inclusive, America/Toronto (90 complete calendar days); do not move it.** Channel: official company Instagram accounts only (LinkedIn dropped by the owner, 27 October 2026). Nothing from this module appears on the page until it is ingested, validated by `social.py`, reviewed and approved.

These steps differ from the website rules below in one way: public posts may be viewed in your normal signed-in Chrome. Record for each account whether you were signed in to that platform. **Never export cookies, share login tokens, automate private account access or bypass restrictions. Do not start paid collection without an approved budget.**

| Step | What to do | What to send |
|---|---|---|
| S1 Verify accounts (six providers) | From each provider's own homepage, follow its footer Instagram link. On the profile, check that the name is the provider's and the profile link points to the provider's domain. Venn's Instagram link goes to `@tryvault`: do not assume it is Venn; verify the name and the link to venn.ca, or record it as unverified. Ramp and Airwallex link no Instagram from their sites; the owner supplied `@tryramp` and `@airwallex` (27 October 2026): verify each profile's name and its link to ramp.com or airwallex.com, and label it `global` unless it presents itself as Canadian. | One sanitised screenshot of the footer link and one of the profile header per provider; one line per provider in `accounts.json` (fields below). |
| S2 Inventory each verified account | Scroll the feed back past 25 July 2026 and screenshot the feed where the window starts. Open every post published 25 July to 22 October 2026 (Toronto date) on its own page: record the fields below. Watch each video in full and open every carousel slide before describing it; otherwise mark `partial`. Record owned posts, reposts and collaborator posts separately. Skip Stories, lives, ads and private content. | One sanitised screenshot per post showing the post, its date and the opening of the caption; one row per post in `posts.json`. |
| S3 Metrics | Copy only the counts the post shows (likes, comments, views) with the time you read them. Write `null` for a count that is not shown. | In each post row. |
| S4 Stop conditions | A login wall you are not already past, a challenge, a rate limit or a block: screenshot it once, record `blocked`, move to the next account. Do not retry or work around it. If you cannot read the whole window, record `partial` with how far back you reached. | The screenshot and the coverage note. |
| S5 Sanitise | Blur your own name, avatar, notifications, messages and any "people you may know" panels; blur commenter names and faces of private individuals. Keep the provider's name, the post, its date and the visible counts. | Sanitised files only. |
| S6 Package | Put the screenshots, `manifest-social.jsonl`, `accounts.json` and `posts.json` in a new zip, `business-spend-index-edition-001-social-evidence-v1.zip`, separate from the edition 001 evidence archive (which stays unchanged). Send it in the chat; I record its hash. | The zip. |

`accounts.json`, one object per provider: `platform`, `channel` (instagram), `handle`, `url`, `verified` (true or false), `verification` (how: name, link domain, linked from which page), `scope` (canada, global or unclear), `logged_in` (true or false), `coverage` (complete, partial, blocked, no_account or unverified), `coverage_note`, `earliest_reached` (date), `posts_in_window` (a number only when complete, else null).

`posts.json`, one object per post: `id`, `platform`, `channel` (instagram), `account`, `url`, `published_on` (YYYY-MM-DD, Toronto), `date_method` (visible_date, post_page_timestamp or relative_date_converted), `captured_at` (with offset), `scope`, `relation` (original, repost or collaboration), `format` (image, carousel, video, text, link or document), `topic` (codebook in the brief), `question` (the customer question the post addresses, in your words), `product`, `geography`, `hook` (opening line, short quote), `proof` (or null), `cta` (destination or null), `inspected` (what you looked at), `inspection` (cover_and_caption, all_slides, watched_in_full or partial), `capture_ref` (the screenshot file name), `metrics` (`{"likes": 12, "comments": null, "views": null, "captured_at": "..."}`).

`manifest-social.jsonl` uses the manifest format below with `role` `social-account`, `social-post` or `social-block`, plus `channel`, `account`, `logged_in` and, for posts, `published_on`.

**Start from `social_package_template/`** (copy it outside the repository): it holds the six account rows pre-filled with the website-linked Instagram candidates (none verified), empty `posts.json` and manifest, and a README with every field. Before sending, run `python3 social.py check /path/to/package`: it prints a handoff request and writes nothing until the package is complete. Status 23 October 2026: not started; this session had no access to the owner's Chrome.

## Forms script: deploy `research_business_spend` (founder, in Chrome; nothing on the website changes)

The website half is already in the branch (`contact.html` accepts `entry=research_business_spend` and sends it as `entry_point`). The forms script must also allow it, or leads from this page are saved without the entry in the Source column (they are still saved). Do this before or at release; order does not matter for safety.

1. Open the "HMM | Contact Us" Google Sheet, then Extensions → Apps Script, signed in as the script owner.
2. Deploy → Manage deployments. Note the active web app deployment's version number and confirm its URL is the `/exec` URL that `/contact` uses (`AKfycbzeefYK.../exec`). Close the dialog without changes.
3. In `Code.gs`, find function `leadSource_`. On the line that starts `if (/^(home_hero|home_final|home_journey|work_final|`, change `research_(hub|gta_medspa|gta_medspa_help)|direct)` to `research_(hub|gta_medspa|gta_medspa_help|business_spend)|direct)`. The whole line must then read:
   `  if (/^(home_hero|home_final|home_journey|work_final|industry_(healthcare|finance|dtc|saas)_(hero|final)|research_(hub|gta_medspa|gta_medspa_help|business_spend)|direct)$/.test(entry)) parts.push('entry ' + entry);`
   If that line in the editor differs from the repository version (`docs/HMM_Forms_AppsScript.gs`, line 219) in any other way, stop and send me the editor's line; do not paste the whole file, which would overwrite any change made only in the editor.
4. In function `testLeadSources`, add `'research_business_spend', ` after `'research_gta_medspa_help', ` in the list.
5. Save (Ctrl+S).
6. Choose `testLeadSources` in the function menu and press Run. It writes no row, sends no email and skips Turnstile. In the Execution log, confirm these lines:
   - `research_business_spend -> contact form | free review | entry research_business_spend`
   - `not_a_real_entry -> contact form | free review` (no entry part)
   - the other entries unchanged.
7. Deploy → Manage deployments → the pencil on the existing web app deployment → Version: New version → description `research_business_spend entry` → Deploy. Do not choose New deployment (that makes a new URL). Confirm the URL is unchanged and the version number went up by one.
8. Send me: the execution log lines from step 6 (a screenshot with no personal data), the new version number and the deploy time (Toronto). I record them; I do not submit a lead.

What stays unverified until a real enquiry: the stored Source value in the Leads tab. The first review request sent from the published page should read `contact form | free review | entry research_business_spend | ...` in the Source column. Do not create a test lead to check it.

## Rules for every capture (website pages; the social module above has its own sign-in rule)

- Logged out, in a clean Chrome profile, from Canada. Note the province you appear to be in if a page asks.
- No accounts, logins, cookies from earlier sessions, invented business details, credit checks, form submissions or transactions. Stop at the first screen that asks for personal or business information, or at a submit button. Do not press it.
- If a page shows a challenge, a block or a refusal, capture it once and stop. Do not retry or work around it.
- Before saving, blur any account name, email address, phone number, cookie banner ID or session detail. Never send unsanitised originals.
- Record the genuine capture time from the clock when the screenshot is taken, with the offset (for example `2026-10-24T09:12:05-04:00`). Never use the upload time.
- Send the files themselves (PNG or WebP) plus one manifest. A path on another machine is not evidence.

## Manifest format (one JSON object per line, `manifest.jsonl`)

```json
{"platform": "keep", "role": "journey", "url": "https://www.trykeep.com/", "final_url": "https://app.trykeep.com/applications-closed", "captured_at": "2026-10-24T09:12:05-04:00", "country": "Canada (Ontario)", "plan_or_version": "public, logged out", "excerpt": "We're not accepting new applications at this time", "screenshot": "keep-journey-01.png", "sanitised": true, "sanitisation_note": "no personal data on screen", "title": "Keep", "observations": ["O-KEP-05"]}
```

`platform` is one of venn, float, ramp, loop, keep, airwallex. `role` is a short name for the page (for example `journey`, `cards`, `pricing`). `observations` lists the observation IDs the capture confirms, corrects or replaces.

Ingest with `python3 ingest.py browser manifest.jsonl FILES_DIR`. If anything is missing, unsanitised or undated, it prints a handoff request and writes nothing. Screenshots stay in private storage; only hashes and metadata enter `sources.json`. Publish a screenshot only after a separate decision on rights and context, with a caption giving provider, page, capture date and what it shows.

## Items captured in the browser pass (kept for the next edition)

| # | Platform | What to check | Page to start from | Observation(s) |
|---|---|---|---|---|
| 1 | Venn | Sign-up journey up to the first screen that asks for business details: which fields are shown, any eligibility or Quebec note, what happens after the email and password step. Stop before submitting. | https://app.venn.ca/signup | O-VEN-18 |
| 2 | Float | Do `{{interest-rate}}` and `{{customer-count}}` fill in a browser? Capture the rendered values on the homepage and business accounts page. | https://floatfinancial.com/ and https://floatfinancial.com/business-accounts | O-FLT-10, O-FLT-14 |
| 3 | Float | Network: card artwork and agreement list for the pre-funded card and Float Charge (Visa only, or Visa and Mastercard?). | https://floatfinancial.com/corporate-cards and https://floatfinancial.com/legal | O-FLT-02, O-FLT-03 |
| 4 | Float | Demo journey: fields shown after the work email, up to submit. | https://floatfinancial.com/demo | O-FLT-16 |
| 5 | Ramp | Canadian card agreement: locate the Canadian cardholder or platform terms (card model: charge, credit or pre-funded; repayment). The legal index returned an empty page to the server. | https://ramp.com/legal | O-RMP-02 |
| 6 | Ramp | Canadian rewards: is a cashback or rewards rate stated for Canada on any Canadian page or in the Canadian terms? | https://ramp.com/en-ca/corporate-cards, https://ramp.com/en-ca/pricing | O-RMP-05 |
| 7 | Ramp | Sign-up journey for a Canadian business up to the first form screen, and the main navigation links on the Canadian homepage (Canadian or US pages?). | https://ramp.com/en-ca and https://ramp.com/en-ca/signup | O-RMP-14, O-RMP-15 |
| 8 | Loop | Product tour and application journey up to the first form screen. | https://www.bankonloop.com/en-ca/explore-product | O-LOP-15 |
| 9 | Loop | Is the "Lorem ipsum" text visible on the homepage or the Bells of Steel case study? Capture the section if so. | https://www.bankonloop.com/en-ca and the case study URL in sources.json (S-LOP-CASE) | O-LOP-14 |
| 10 | Keep | Confirm that "Get started" leads to the closed-applications page in a browser, and capture the homepage button and the closed page. | https://www.trykeep.com/ | O-KEP-05 |
| 11 | Keep | The card comparison table on the card page: what the "Foreign exchange (FX) Fees" row shows for Keep, and whether the 3% card conversion fee appears anywhere on the public pages. | https://www.trykeep.com/products/business-card and https://www.trykeep.com/resources/faq | O-KEP-07, O-KEP-08 |
| 12 | Airwallex | Sign-up journey up to the first form screen. | https://www.airwallex.com/en-ca/signup | O-AWX-14 |
| 13 | Airwallex | Cashback: which figure the rendered cards page shows (title 2%, body 1%), and the linked rebate terms. Also the automatic card conversion fee level in the fee schedule. | https://www.airwallex.com/en-ca/spend-management/cards and the "Fee Schedule" link on the terms pages | O-AWX-04, O-AWX-07 |
| 14 | Airwallex | Credit line for corporate cards: terms or eligibility page, if public. | https://www.airwallex.com/en-ca/pricing | O-AWX-01 |
| 15 | All six | Registry lookups, recorded as the registry shows them (name, number, status, date of lookup): FINTRAC MSB registry for Venn (M22941967), Float (M23497654), Loop Payments and Airwallex (Canada) (M19395067); Bank of Canada PSP registry for Ramp Business Corporation, Float, Loop Payments, Keep and Airwallex (Canada). This records what the registries say; it is not an endorsement or a safety rating. | https://fintrac-canafe.canada.ca/msb-esm/reg-eng and https://www.bankofcanada.ca/regulatory-oversight/retail-payments/psp-registry/ | O-VEN-13, O-FLT-12, O-RMP-11, O-LOP-11, O-KEP-11, O-AWX-11 |

## After the files arrive

1. `python3 ingest.py browser manifest.jsonl FILES_DIR`
2. Update the affected observations (cite the new `S-...-BROWSER-...` sources, change status, keep the server observation history in the conditions) and ingest them with `python3 ingest.py observations FILE.json --replace`.
3. If a capture changes the edition collection end, update `collection_ended_at` in `edition.json` to the last genuine capture time.
4. `python3 build.py`, `python3 validate.py --raw RAW_DIR`, `python3 -m unittest tests.test_kit`.

## Publication blockers (not browser items)

- Relationship disclosure: resolved 2026-10-23. The founder confirmed: "Neither I nor Help Me Marketing has a commercial relationship with Venn, Float, Ramp, Loop, Keep or Airwallex." Recorded in `edition.json` and shown in the method section.
- Three unresolved differences (class C, status Conflicting): Venn cashback spend limits, Venn send currencies, Loop rewards on Basic. Two items not determined (class D): Airwallex cashback eligibility and the Airwallex credit line. Each stays shown as it is unless the owner decides otherwise or the provider clarifies.
- Owner's editorial review and explicit release instruction. Approvals in `edition.json` are entered by hand from the owner's instruction; nothing in the kit sets them.
- Forms script: `research_business_spend` is added to the source in `docs/HMM_Forms_AppsScript.gs` but not deployed. Until the owner pastes the updated script into the Apps Script editor and deploys a new version (Deploy, Manage deployments, edit, New version), leads from this page are saved normally but the Source column omits the entry. Check with `testLeadSources` in the editor after deploying; it writes no row.
