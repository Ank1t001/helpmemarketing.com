# Ordinary-browser handoff, Dental Implant Marketing Index edition 001

Updated 16 October 2026 after the browser-20261016 evidence pass. That pass ran in a logged-out headless Chromium in the Claude Code cloud container, not in the founder's Chrome. What it completed is in `editions/001/raw/browser-20261016/` and in `ads.json` and `social.json`. The checks below are still outstanding and need an ordinary browser on an ordinary connection. Keep the window fixed at 16 September to 15 October 2026 (America/Toronto). Record each check's date and time (Toronto), the exact URL and a screenshot. Do not submit forms, book, upload photos, message clinics, use logins for clinic accounts or bypass any restriction.

## 1. Websites still unread [observations.json, comparison.json, narrative.json]

- **Dundas East Dental**, https://dundaseastdental.com/. The cloud browser saw only a "VPN or Proxy Detected" panel. In an ordinary browser, record:
  - practice name, street address and city, and phone;
  - implant and full-arch page URLs, and the clinician presented for implants;
  - consultation offer and fee;
  - cost and financing: single, per arch or full mouth; starting price or package; materials; temporary versus final restoration; inclusions, exclusions and conditions;
  - enquiry route and required fields (read only), and what the site says happens next;
  - the Instagram link and any agency credit;
  - whether the reviews shown refer to other clinics (an unverified cached copy names Norton Dental Centre and Northland Dental Vaughan).
- **Bond Street Dental**, https://www.dentalimplantsclinic.ca/. The cloud browser saw a Cloudflare security check. Pass it only as a normal visitor would. Record:
  - whether the site itself identifies Bond Street Dental, with its address (Google ad records show "Bond Street Dental" listings and "113 Bond St", but that is ad evidence only);
  - whether the site names Passion Dental Group, or another brand such as "Bentway", which appears in one ad;
  - the same fields as for Dundas East Dental above;
  - the conditions behind any implant price: Google ads show "Dental Implant At $1,599", and an unverified cached copy mentioned a surgical-phase price.

## 2. Instagram [social.json]

- **@gajjardentistry**: the logged-out profile request was refused (HTTP 429). Read the profile and every post dated 16 September to 15 October 2026. Record for each post: URL, date from the post page, owner, collaborators, format, caption first line, visible likes and comments, plays where shown, pinned status and whether it concerns implants.
- **@studiobdental** and **@northyork.smilecentre**: confirm that the posts already recorded are every post in the window (4 and 5 observed). Look for posts the logged-out grid may have missed, collaborator posts, and posts dated 1 to 15 October. Then set coverage to `confirmed_complete` or record the gap. Plays were not shown logged out; record them where they are shown.
- **Dundas East Dental and Bond Street Dental**: only after the website gives the handle, read the posts as above.

## 3. Advertising [ads.json]

- **Meta Ad Library**, Bond: searches for "Dental Implants Clinic" and "Passion Dental Group" were not run. Match the advertiser page before attributing anything.
- **Meta Ad Library**, Dundas East Dental: if the website names a dentist or another page name, search it as well.
- **Google Ads Transparency**, Gajjar: 11 of 15 any-time creatives were not opened. None was shown in the window, so this is optional.
- Never record spend, reach, targeting or performance.

## 4. Preview

Open the preview link from the build report on a real phone and in desktop Chrome, in both themes:
- the hero buttons, and Tab focus on "See the five clinics";
- the comparison, examples and advertising tables as cards on the phone;
- the price note in the Studio B Dental card;
- every summary opened with Enter;
- "Review my implant enquiry journey", which must open `/contact?intent=review&entry=research_dental` without submitting.

## Not for this handoff

- No production verification and no indexing request until the edition is released.
- The forms script must be redeployed with `research_dental` (set `forms_script_research_dental_deployed` in `edition.json` once confirmed).
