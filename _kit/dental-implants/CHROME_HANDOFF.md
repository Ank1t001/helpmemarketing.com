# Chrome handoff, Dental Implant Marketing Index edition 001

Prepared 16 October 2026. Nothing below has been done yet. Record every result with the date and time (Toronto), the exact URL and a screenshot, then add it to the kit files named in brackets. Do not submit forms, book, upload photos, message clinics, use logins for clinic accounts or bypass any restriction.

## 1. Websites that refused automated access [observations.json, comparison.json, narrative.json]

- **Dundas East Dental**, https://dundaseastdental.com/ (HTTP 403 to automated requests).
  - Confirm: practice name, street address and city, phone, the clinician presented for implants (a cached copy names Dr. Ammar Taimish) and whether reviews shown refer to other clinics (a cached copy shows Norton Dental Centre and Northland Dental Vaughan).
  - Open the main implant or full-arch page: positioning and patient situation, any published price (a cached copy shows several all-inclusive full-arch prices), financing, consultation offer, proof, the enquiry form's fields (read only), and any explanation of what happens after an enquiry.
  - Note the Instagram link in the header or footer, and any agency credit.
- **Bond Street Dental**, https://www.dentalimplantsclinic.ca/ (Cloudflare challenge). Pass the challenge only as a normal visitor in a normal browser.
  - Confirm that the site identifies Bond Street Dental (a cached copy says so) and its address.
  - Same implant page review as above, including the advertised surgical-phase price and its stated conditions.
  - Note the Instagram link and any agency credit.

## 2. Advertising [ads.json]

For each clinic, both platforms. Statuses: relevant ads observed, no matching ads found in the documented search, advertiser identity uncertain, access blocked.

- **Meta Ad Library**: country Canada, all ads, active status all. Search terms are in `ads.json` (`prepared_urls`). Match the advertiser page to the clinic before attributing anything; record the advertiser page URL, each relevant ad's library URL, creative or offer text, start date and destination URL where shown.
- **Google Ads Transparency Center**: region Canada, search by the clinic's domain (prepared links in `ads.json`). Record the advertiser name and verification, each relevant ad's URL, format, creative or offer, and dates shown.
- Never record spend, reach, targeting or performance.

## 3. Instagram [social.json]

Not collected: paid collection is not authorised for this study, and a logged-out request was refused (HTTP 429). Founder decision needed: either authorise a collection route with a spending limit, or approve a manual read in the browser. If manual, for each verified handle (@studiobdental, @northyork.smilecentre, @gajjardentistry, plus the two handles found in step 1): list every post published 16 September to 15 October 2026 (Toronto time) with its URL, date, format, owner (clinic or collaborator), caption first line, visible likes and comments, plays where shown, pinned status, and whether it concerns implants. Keep hidden values blank. If the window is re-dated at collection, use the window `build.py` computes for that collection date.

## 4. Preview verification

Open the preview link from the build report on a phone and a desktop browser: hero, comparison (cards on a phone), content placeholders, a clinic card and its takeaway, the three tests, the method sections with the keyboard (Tab and Enter on each summary), and the "Review my implant enquiry journey" button, which should open `/contact?intent=review&entry=research_dental`.

## Not for this handoff

No production verification or indexing request until the edition is released.
