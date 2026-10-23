# Chrome handoff: Business Cards & Spend Management Index, edition 001

Edition 001 was collected by server fetch only (23 October 2026, 10:39 a.m. to 10:48 a.m. Toronto time; no JavaScript, no cookies). The items below need a real browser. None of them may be described as checked until the files listed here arrive and `ingest.py browser` accepts them.

## Status (updated 23 October 2026, after the browser pass)

The browser pass of 23 October 2026, 12:00 p.m. to 12:14 p.m. Toronto time (package `business-spend-browser-pass-2026-10-23`, 34 captures) covered items 1 to 15 below. Its captures are in `sources.json` (`S-<CODE>-BROWSER-...`, method `browser`, screenshot hashes only), and the observations it changed carry the browser sources. The ten differences it reconciled carry a `reconciliation` class (A to D) and are listed on the page under "How the reported differences were reconciled". Screenshots are held privately outside the repository; check them with `validate.py --raw RAW_DIR --browser SHOTS_DIR`.

Still open after the pass:

- Venn: what the homepage line "200+ countries in 30+ currencies" shows to visitors (in the page code; visibility not established).
- Float: the network of Float Charge (not stated separately); what happens after a demo is booked.
- Ramp: no Canadian rewards rate is published (a finding, not a gap to close); the Rewards Terms page was read in the browser without a capture file; a server fetch of Ramp legal pages returns only a script shell (13 characters), so any future text evidence for them needs a browser capture.
- Airwallex: the terms for the "Credit line for corporate cards" (class D); the rebate terms and what "eligible" covers (class D); the demo booking form (not opened).
- Loop: the product tour beyond its first screen.
- Not possible without an account or a submission: any step after the first screen of the six journeys.
- The browser pass used a normal Chrome profile (not signed in to the providers) and checked mobile in a 390px frame; my own checks cover real keyboard focus and real mobile viewports.

## Rules for every capture

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
- Five open differences after reconciliation: Venn cashback caps (C), Venn send currencies (C), Loop rewards on Basic (C), Airwallex cashback (B and D), Airwallex credit line (D). Each stays shown as an unresolved difference unless the owner decides otherwise or the provider clarifies.
- Owner's editorial review and explicit release instruction. Approvals in `edition.json` are entered by hand from the owner's instruction; nothing in the kit sets them.
- Forms script: `research_business_spend` is added to the source in `docs/HMM_Forms_AppsScript.gs` but not deployed. Until the owner pastes the updated script into the Apps Script editor and deploys a new version (Deploy, Manage deployments, edit, New version), leads from this page are saved normally but the Source column omits the entry. Check with `testLeadSources` in the editor after deploying; it writes no row.
