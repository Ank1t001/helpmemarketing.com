# Medspa research measurement: browser handoff (15 October 2026)

For Claude in Chrome, working with Ankit. Three jobs: redeploy the forms script so research entry points reach the Leads Source column, add one GTM event, and run the Rich Results checks. Nothing on the website changes. Production commit at the time of writing: `2690982`.

## 1. Where things stand

| Item | State |
| --- | --- |
| Research review links carry `entry=research_hub`, `research_gta_medspa`, `research_gta_medspa_help` | Deployed (live pages match the repo byte for byte, checked 15 October) |
| `/contact` accepts those values and sends them as `entry_point`; anything unknown becomes `direct` | Deployed |
| `research_service_click` pushes on the hub and the GTA page | Deployed |
| Forms script `leadSource_` allows the research values | Repo only (commit `7ccd0a6`). Production runs whatever was last deployed by hand; until it is redeployed, research enquiries still save as leads but their Source has no `entry ...` part |
| `testLeadSources` (log-only check) in the forms script | Repo only (this commit) |
| GTM trigger and GA4 tag for `research_service_click` | Not configured. Browser work |
| GA4 custom dimensions `research_page`, `service` | Not configured. Browser work |
| Google Rich Results Test on the hub and GTA page | Not run. Browser work |
| Tested so far | Locally only: the repo's `leadSource_` and the `/contact` entry whitelist were run against the values in the matrix below and gave the expected Source text. No production submission and no GTM preview has been run |

## 2. Forms script

**Source:** `docs/HMM_Forms_AppsScript.gs` in this repo.

**Find the production script.** Open the Google Sheet "HMM | Contact Us", then Extensions, then Apps Script (file `Code.gs`). In Deploy, Manage deployments, the active web app deployment is the one whose URL is exactly the `SHEET_URL` in `contact.html` (line 308):
`https://script.google.com/macros/s/AKfycbzeefYKM_xZuJHIg9pjl0hTLo57v87Qfpb5DzwvikeyVY3_QdYHFd18zpzlfBsbALSp/exec`
Note its current version number and its "Execute as" and "Who has access" values before changing anything.

**Check before patching.** Search `Code.gs` for `research_(hub`.
- Found, and the deployment's version is the latest saved version: nothing to do in the script. Skip to the checks.
- Found in the editor but the deployment points at an older version: deploy a new version (step 4 below) without editing code.
- Not found: apply the patch.

**Patch (minimal).** In `leadSource_`, replace this one line:

```
  if (/^(home_hero|home_final|home_journey|work_final|industry_(healthcare|finance|dtc|saas)_(hero|final)|direct)$/.test(entry)) parts.push('entry ' + entry);
```

with:

```
  if (/^(home_hero|home_final|home_journey|work_final|industry_(healthcare|finance|dtc|saas)_(hero|final)|research_(hub|gta_medspa|gta_medspa_help)|direct)$/.test(entry)) parts.push('entry ' + entry);
```

Then paste the `testLeadSources` function from the repo file directly above `testEmails` (optional, but it is the safe check). If the production `Code.gs` differs from the repo in more places than this line, apply only the patch: do not paste the whole repo file over an unknown production version.

**Steps.**
1. Apply the patch (or confirm it is there). Save.
2. Run `testLeadSources`. It writes no row, sends no email and makes no network call. Expected log:
   ```
   research_hub -> contact form | free review | entry research_hub
   research_gta_medspa -> contact form | free review | entry research_gta_medspa
   research_gta_medspa_help -> contact form | free review | entry research_gta_medspa_help
   home_hero -> contact form | free review | entry home_hero
   direct -> contact form | free review | entry direct
   not_a_real_entry -> contact form | free review
   ```
3. Do not run `testRouting` for this check. It writes TEST rows, and when the `TURNSTILE_SECRET` property is set its contact cases land on Spam ("No Turnstile token"), so it cannot show the Source text.
4. Deploy, Manage deployments, the pencil on the EXISTING deployment, Version: New version, description "Research entry points", Deploy. Never "New deployment": that makes a new URL and every form on the site would keep posting to the old one.
5. Open the `/exec` URL. It must reply `{"result":"ok","message":"HMM forms endpoint is live."}` and the URL must be unchanged.

**Leave unchanged:** the deployment's "Execute as" and "Who has access"; Script Properties (including `TURNSTILE_SECRET`, never copied anywhere); the Leads tab's 13 columns and their order; the other tabs; any project triggers; `setup`, `importGrowthOsHistory` and `importIndexHistory` (do not run them). No new permissions are needed: the patch adds no new service.

**What the patch does and does not touch.** Only the Source text of `contact` leads. Fields, tabs, spam filing, Turnstile, the review confirmation email and the JSON reply (`saved: 'lead'`) are unchanged. An unknown entry adds no `entry` part and the lead still saves.

## 3. `research_service_click`

**Emitters (one listener per page, no other code pushes this event):**

| Page | `research_page` | `service` values (link target) |
| --- | --- | --- |
| /medspa-marketing-research | `medspa-marketing-research` | `performance-marketing`, `branding-social`, `website-development`, `analytics-attribution` (two links), `ai-automation` in the decisions table; `industries-healthcare` in the author section. 7 links |
| /gta-medspa-index | `gta-medspa-index` | `performance-marketing`, `website-development`, `analytics-attribution`, `ai-automation`, `industries-healthcare` in "#ri-help". 5 links |

Each link carries `data-research-service`; the slug matches `/services/<slug>`, and `industries-healthcare` is `/industries/healthcare`. The edition 001 snapshot does not emit it.

**Push:** `{event: 'research_service_click', research_page: 'gta-medspa-index', service: 'website-development'}`. No personal data.

**Related event, already live:** the research review links push `review_cta_click` with `entry_point` = `research_hub`, `research_gta_medspa` or `research_gta_medspa_help`, and `/contact` then carries the same `entry_point` on `contact_view`, `contact_form_start`, `contact_submit` and `contact_submit_error`. Check in GTM that `review_cta_click` and `contact_submit` already have tags; if either has none, report it rather than adding it in this pass.

**Consent.** The push always happens. GTM (`GTM-NSQPX93X`) loads only after the consent answer is in (`hmmConsentGo`, 2.4 second fallback) and the visitor's first scroll, mouse move, touch, key or click. Defaults are `analytics_storage` denied with `wait_for_update: 800`; `consent.js` grants analytics by default outside Quebec, the EU and EEA, the UK and Switzerland, and a Global Privacy Control signal or an opt-out keeps it denied. With consent granted the GA4 event is sent normally. With it denied, the GA4 tag's built-in consent check applies: cookieless pings if the container uses advanced consent mode, nothing if it uses basic mode. Do not change the container's consent mode. Known gap, not fixed here: on a phone where the very first touch is the tap on a service link, the page can leave before GTM loads, so that click may not be recorded (the same applies to `review_cta_click`).

**GTM configuration (container GTM-NSQPX93X, Default Workspace):**
1. Variables, New, Data Layer Variable: name `DLV - research_page`, Data Layer Variable Name `research_page`, version 2. Again for `DLV - service` with `service`. If the container already names its data layer variables another way (look at the one used for `entry_point`), follow that pattern.
2. Triggers, New, Custom Event: name `CE - research_service_click`, Event name `research_service_click`, regex off, fires on All Custom Events.
3. Tags, New, Google Analytics: GA4 Event: name `GA4 - research_service_click`. Measurement ID: the same value or variable the existing GA4 event tags use (copy it from the `contact_submit` tag); do not create a second Google tag. Event Name `research_service_click`. Event Parameters: `research_page` = `{{DLV - research_page}}`, `service` = `{{DLV - service}}`. Consent settings: leave "Not set" or "No additional consent required" (built-in checks cover `analytics_storage`). Trigger: `CE - research_service_click`.
4. Preview (see the matrix), then Submit with version name "research_service_click GA4 event" and Publish only after the preview passes.
5. GA4 Admin, Custom definitions, Create custom dimension, scope Event: `research_page` (parameter `research_page`) and `service` (parameter `service`). If a dimension named `service` already exists, reuse it.
6. Do not mark `research_service_click` as a key event.

## 4. Test matrix

**Test workflow that notifies no client.** Use only Ankit's own mailbox as the email (a plus alias is fine). The forms script sends no owner alert; the only email a contact submission triggers is the review confirmation, and it goes to the address typed in the form. Name every test "TEST research 15 Oct", website `https://example.com`, phone blank. Type into the fields (do not rely on autofill alone) and wait more than three seconds before sending, so the bot guard does not file the test on Spam. Start each case in a new tab. Delete the TEST rows from Leads afterwards. If a sheet notification rule or another automation watches the Leads tab, pause it or expect it to fire.

**A. Source preservation (after the script redeploy)**

| # | Start | Click | `/contact` URL | Expected Source (Leads, last column) |
| --- | --- | --- | --- | --- |
| A1 | /medspa-marketing-research | "Request a marketing review" | `?intent=review&entry=research_hub` | `contact form \| free review \| entry research_hub \| landing /medspa-marketing-research` |
| A2 | /gta-medspa-index | "Get my free marketing review" in the download section (`#ri-download`) | `entry=research_gta_medspa` | `... \| entry research_gta_medspa \| landing /gta-medspa-index` |
| A3 | /gta-medspa-index | "Request a marketing review" in `#ri-help` | `entry=research_gta_medspa_help` | `... \| entry research_gta_medspa_help \| landing /gta-medspa-index` |
| A4 | / (home) | hero "Get my free marketing review" | `entry=home_hero` (plus UTM tags) | `... \| entry home_hero \| source ... \| landing /` (regression) |
| A5 | type `/contact?intent=review&entry=research_bogus` | none | as typed | `... \| entry direct \| landing /contact...` (unknown falls back to direct) |

For every A case: the page shows the review thank-you (not "check it by hand"), the row has all 13 columns in their usual places, and the confirmation email "Your free marketing review request is in" reaches the test mailbox. A1 to A3 only show the `entry` part after the redeploy; before it, the row still saves without that part.

**B. Service clicks (GTM Preview, before publishing).** Open Tag Assistant on the page, scroll once so GTM loads, then Ctrl or Cmd click each service link (a new tab keeps the page and its event history).

| # | Page | Link | Expected |
| --- | --- | --- | --- |
| B1 | hub | each of the 7 links | one `research_service_click` per click, `research_page` = `medspa-marketing-research`, `service` = the slug in section 3; `GA4 - research_service_click` fired once |
| B2 | GTA | each of the 5 links | same, `research_page` = `gta-medspa-index` |
| B3 | hub | the review CTA | `review_cta_click` with `entry_point` `research_hub`; the research tag does not fire |
| B4 | either | consent granted (Ontario default) | hit visible in GA4 DebugView with both parameters |
| B5 | either | Privacy choices, turn analytics off, reload | the push still shows in Tag Assistant; the GA4 hit is blocked or cookieless per the container's mode; no personal data in any parameter |

**C. Completed enquiry, end to end.** Run A1 inside the same Tag Assistant session: expect `contact_view` and `contact_form_start` with `entry_point` `research_hub`, then `contact_submit` with `contact_intent` `review` and `entry_point` `research_hub` once the thank-you shows, and the Leads row from A1.

## 5. Rich Results Test

At https://search.google.com/test/rich-results, test the live URLs (not code):
- `https://helpmemarketing.com/medspa-marketing-research`: expect Breadcrumbs valid. `CollectionPage` is not a rich result type, so the tool will not list it.
- `https://helpmemarketing.com/gta-medspa-index`: expect Breadcrumbs and Article valid; FAQ may be listed as detected but not eligible (Google limits FAQ results to some sites). `Dataset` is checked by the Dataset Search tools, not this test.

Record errors and warnings for each URL. Errors need a fix through the GTA kit (`_kit/gta-medspa-instagram`) or the hub page; warnings for optional fields are acceptable. schema.org's validator already showed 0 errors on both pages (14 October).

## 6. Report back

Script: version number before and after, the `testLeadSources` log, and the `/exec` reply. GTM: the published version number. Rows A1 to A5 and B1 to B5 as pass or fail with what was seen. Rich Results: detected items, errors and warnings per URL.
