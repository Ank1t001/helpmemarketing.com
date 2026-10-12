# HMM Phase 2 report: SEO, AEO and GEO implementation (October 2026)

Prepared 12 October 2026 against the founder instructions "HMM Phase 2: SEO, AEO & GEO Implementation Instructions". Planning documents stay in `/docs` (excluded from the deployment by `.vercelignore`). Companion files: `/docs/HMM_Phase2_Intent_Links_Authority_2026-10.md` (intent map) and `/docs/HMM_Phase2_Outreach_Shortlist_2026-10.md` (outreach shortlist).

## 1. Internal-link implementation log (Phase 2B)

Links were placed on existing words where the text already discussed the destination. Where no natural phrase existed, one short related line (`pm-related`, the class already used on these pages) was added. No headings, copy or layout were rewritten.

| Source page | Destination | Anchor text | Status | Verification |
|---|---|---|---|---|
| `/industries/healthcare` | `/services/seo` | local search | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px |
| `/industries/healthcare` | `/services/ai-automation` | Fast replies, confirmations and reminders | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px |
| `/industries/finance` | `/services/performance-marketing` | Paid search, social | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px |
| `/industries/finance` | `/services/analytics-attribution` | Reporting past the lead | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px |
| `/industries/dtc` | `/services/website-development` | Product pages, landing pages and checkout | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px |
| `/industries/dtc` | `/services/performance-marketing` | Paid ads | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px |
| `/industries/dtc` | `/services/analytics-attribution` | tracking | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px |
| `/industries/saas` | `/services/performance-marketing` | paid campaigns | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px |
| `/industries/saas` | `/services/ai-automation` | CRM follow-up and nurture | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px |
| `/industries/saas` | `/services/analytics-attribution` | every touch that helped a deal | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px |
| `/services/performance-marketing` | `/ad-calculator` | estimate your ad budget | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px (new related line) |
| `/services/performance-marketing` | `/ad-set-calculator` | check how many Meta ad sets your budget can support | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px (new related line) |
| `/services/performance-marketing` | `/meta-growth-os` | the Meta Growth OS audit system | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px (new related line) |
| `/services/analytics-attribution` | `/industries/finance` | marketing for finance firms | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px (new related line) |
| `/services/analytics-attribution` | `/industries/saas` | SaaS demand generation | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px (new related line) |
| `/services/branding-social` | `/hmm-index` | my Instagram benchmark research | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px (appended to existing related line) |
| `/blog/marketing-mistakes` | `/services/analytics-attribution` | Fix attribution first | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px |
| `/blog/marketing-mistakes` | `/services/website-development` | one landing page per campaign | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px |
| `/blog/marketing-strategy-from-zero` | `/services/website-development` | a website that converts | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px |
| `/blog/marketing-strategy-from-zero` | `/services/analytics-attribution` | conversion tracking | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px |
| `/blog/marketing-strategy-from-zero` | `/ad-calculator` | spending enough on one channel | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px |
| `/about` | `/work` | DTC, SaaS, healthcare and finance brands | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px |
| `/about` | `/services` | the services I offer | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px (new related line) |
| `/about` | `/hmm-index` | my original Instagram benchmark research | Done | Destination file exists; no broken or redirected links site-wide; page regression passed at 1440 and 390 px (new related line) |
| `/blog/healthcare-marketing-channels` | `/services/branding-social` | Reviews and reputation management | Done (fix) | Was linking to `/reviews-reputation`, a redirect |
| `/services/seo` | `/ai-seo-agency` | More on AI search visibility | Already present | Verified in source |
| `/services/seo` | `/seo-growth-os` | See the SEO Growth OS | Already present | Verified in source |
| `/services/ai-automation` | `/ai-marketing-agency` | How I use AI in marketing | Already present | Verified in source |
| `/industries/healthcare` | `/services/performance-marketing` | (none) | Skipped | No text on the page discusses ads; not forced |
| `/blog/choose-marketing-agency` | `/gta-marketing-agency`, `/services` | (none) | Skipped | The post has no local or service passage to link from |
| `/blog/seo-ppc-or-social`, `/blog/paid-ads-vs-organic` | `/ai-seo-agency` | (none) | Skipped | Neither post mentions AI search; both already link to the SEO and Performance Marketing services |

## 2. URL migration verification: `/realestate-index` (Phase 2A)

Checked against the live site on 12 October 2026 with HTTP requests:

| Check | Result |
|---|---|
| `https://helpmemarketing.com/realestate-index` | HTTP 200 |
| `/instagram-reindex` | HTTP 308, `location: /realestate-index` (one hop, permanent) |
| Old URL serving its own 200 page | No |
| Canonical on the new page | Self-referencing `https://helpmemarketing.com/realestate-index` |
| Robots meta | `index, follow` |
| Sitemap | Lists `/realestate-index`; old URL absent |
| Internal links, AI Tools, HMM Index, Work, tool finder, JSON-LD, og:url | All point to `/realestate-index` (changed in commit `1bf1184`) |
| Assets | Frames under `/assets/index/real-estate/frames/` unchanged and loading |
| Research dates | Unchanged (cycle 003, 24 Sep 2026) |
| Redirect chains | None on the canonical path. **Opportunity:** the legacy form `/instagram-reindex.html` takes two hops (308 to `/instagram-reindex`, then 308 to `/realestate-index`) because Vercel's clean-URL redirect runs first. Rarely requested; no action unless it appears in Search Console. |

Status: **verified complete.**

## 3. Search-intent map (Phase 2C)

Unchanged from `/docs/HMM_Phase2_Intent_Links_Authority_2026-10.md` section 1. **Validation pending**: needs the Search Console export (Canada, web, last three months, queries by landing page with clicks, impressions, CTR and position). No titles were changed, nothing was merged or redirected. Roles: `/services/seo` commercial SEO; `/ai-seo-agency` AI search visibility; `/ai-marketing-agency` the broader AI-supported approach.

## 4. Business identity (Phase 2D)

Founder decision on 12 October 2026: HMM is based in **Halton Hills, Ontario, Canada**. Implemented in commit `d30b9be`:

| Element | Before | After |
|---|---|---|
| Footer NAP line (every page, desktop and phone menu share the footer) | Burlington, Ontario, Canada | Halton Hills, Ontario, Canada |
| JSON-LD `addressLocality` (/, /about, /gta-marketing-agency, /ai-marketing-agency, /ai-agents-halton) | Burlington | Halton Hills |
| "I'm based in…" FAQ answers and FAQPage text (/services, /gta-marketing-agency) | Burlington | Halton Hills |
| GTA page title, og/twitter titles, descriptions, H2 | Burlington | Halton Hills |
| /ai-agents-halton business line | Burlington-based; Burlington, ON | Halton Hills-based; Halton Hills, ON |
| Forms script `SENDER_POSTAL` | Burlington | Halton Hills (takes effect after the founder redeploys the Apps Script) |
| Google Maps link (schema sameAs) | Pin at 43.637, −79.871 | Kept: the pin is in Halton Hills, matching the base |

Kept on purpose: Burlington as a served city (GTA area list, /ai-agents-halton service area), the fictional ABC Clinic on the homepage, MedSpa Index clinic areas, the audit's "Busy parents in Burlington" example. Not added: street address, postal code, phone or office. Social profiles (Instagram, LinkedIn, Facebook) are identical everywhere.

**Open:** confirm the Google Business Profile's public name and service-area settings in the profile itself; the site cannot verify those.

## 5. Outreach shortlist (Phase 2E)

`/docs/HMM_Phase2_Outreach_Shortlist_2026-10.md`: 16 verified outlets across the six categories, each with website, audience, asset, angle, published contact (only where published), guidelines, dated recent activity and restrictions; a separate "considered but not verified" list. Status: **research only, nothing sent.** Paid-placement routes (RENX sponsored content, CBAM sponsorship, Canadian Aesthetics Expo) are flagged as excluded.

## 6. AI visibility monitoring framework (Phase 2F)

Purpose: record whether HMM is mentioned or cited in AI-generated answers, with a repeatable process. No score is calculated; single answers are never treated as rankings.

### Method

- **Platforms:** Google AI Overviews / AI Mode (google.ca), ChatGPT (search on), Perplexity, Microsoft Copilot. Record the exact product and model shown.
- **Settings:** logged-out or a fresh profile, location Canada (Ontario where the platform allows), English, no personalisation, no follow-up prompts. Note any setting that could not be controlled.
- **Cadence:** monthly, same questions, same order, same week of the month. Run each question once per platform per cycle; if answers vary obviously between two runs, record both.
- **Storage:** one row per question per platform per date in a sheet (columns below). Keep screenshots or exported answers as evidence.
- **Reporting:** counts of mentions and citations per area over time, with the caveat that answers change between runs.

### Record fields

| Field | Notes |
|---|---|
| Question | Exact wording from the set below |
| Platform and model | e.g. ChatGPT, model name shown |
| Test date | YYYY-MM-DD |
| Location / settings | Country, logged-out, search on/off |
| HMM mentioned | Yes / No |
| HMM cited with a link | Yes / No |
| Cited URL | When present |
| Other cited sources | Domains listed |
| Notes and limitations | Variation, refusals, settings not controllable |

### Starting query set (candidates, not verified demand; validate against buyer language and Search Console)

| Area | Questions |
|---|---|
| Marketing agency | Which marketing agencies serve small businesses in Ontario? · Who offers paid ads, analytics and marketing automation for Ontario businesses? · Marketing consultant in Halton Hills |
| SEO and AI search | Who are SEO consultants in Ontario for service businesses? · How can a Canadian business show up in AI search answers? · AI search visibility services in Canada |
| Performance marketing | Who manages Google and Meta ads for Canadian small businesses? · How much should a small business spend on Google Ads in Canada? |
| Marketing automation | Who sets up lead follow-up automation for small businesses in Ontario? |
| Marketing tools | Free marketing audit tool for small businesses · Ad spend calculator by customer goal · How many Meta ad sets can my budget support? |
| Original research | Instagram benchmarks for GTA medical spas · How do Canadian private real estate firms use Instagram? · Instagram benchmarks for hair loss clinics in Ontario |

## 7. SEO Growth OS and Meta Growth OS accuracy (Phase 2G)

Headlines unchanged in this phase.

| Item | SEO Growth OS page | Meta Growth OS page |
|---|---|---|
| Version | Release 2.2.1 (founder-confirmed 12 Oct 2026) | No version in the package README; page shows none |
| Skills | 39 (founder-confirmed); component list documents 32 of them | 13, verified against `/meta-growth-os.zip` |
| Files | "39 skills, a README and a setup guide" | 13 skills and a README with setup and requirements (verified; no separate setup guide) |
| Prerequisites | Stated generally (supported AI tool, data sources); exact list **not verified** (package not in the repo) | Verified from README: Google Drive and a Meta Ads connection required; CSV Limited Mode; CRM or commerce data optional |
| Download | Emailed from Drive via the forms script | Direct download from the page after email |
| Recurring monitoring | Described as a schedule you set up (not automatic) | Opt-in; a run stops at the report (verified) |
| Prompt | Behind "Advanced setup"; README declared authoritative; known conflict ("do not stop" vs approval gates) left for the founder's current prompt | Same treatment |

**Discrepancies documented, not changed:** (1) the SEO page's "a setup guide" and the prerequisite list are unverified until the 2.2.1 package or README is available; (2) the 7 skills beyond the 32 listed are unnamed on the page; (3) the Meta README ends with the old "Growth Architects" audience line (inside the zip).

## 8. Technical QA (Phase 2H)

| Type | Finding | Status |
|---|---|---|
| Broken | Two links to `/services/...` inside JSON-LD on `/industries/saas` and `/blog/marketing-strategy-from-zero` introduced during linking (FAQ text appears in schema first) | Fixed before commit; all JSON-LD parses sitewide |
| Broken | `/blog/healthcare-marketing-channels` linked to `/reviews-reputation` (a redirect) | Fixed: links to `/services/branding-social` |
| Broken | Redirects `/reputation` and `/reviews-reputation` pointed to `/services/branding-social#reviews`, an anchor that no longer exists | Fixed in `vercel.json`: destination `/services/branding-social` |
| Pass | Internal links on every served page resolve; no links to redirected URLs remain | Verified |
| Pass | Every served page has a canonical; none is noindex | Verified |
| Pass | Sitemap includes `/realestate-index`, excludes the old URL | Verified live |
| Pass | 15 changed pages: no script errors, no horizontal scroll, no broken links at 1440 px (light) and 390 px (dark) | Verified locally |
| Pass | Contact form, consent and analytics files untouched | Verified (no changes to `contact.html` beyond the footer NAP line, `consent.js`, `site.js`) |
| Opportunity | `/instagram-reindex.html` two-hop redirect | Low priority |
| Opportunity | `/about` says "price on outcomes, not billable hours" and "I bill for the work… platforms bill you directly with zero markup", which describes a pricing model | **Needs founder decision** (content not rewritten per the instructions) |
| Opportunity | Growth OS page titles still read "One System, Any Site / Any Account" | Left unchanged per instructions |
| Missing | Search Console export for intent validation | Founder |

## 9. Changed files

- Commit `d30b9be` (location): 53 files: every served page's footer line, JSON-LD on `/`, `/about`, `/gta-marketing-agency`, `/ai-marketing-agency`, `/ai-agents-halton`, FAQ text on `/services` and `/gta-marketing-agency`, `docs/HMM_Forms_AppsScript.gs`, `CLAUDE.md`, `docs/HMM_Design_System.md`, the Phase 2 planning doc.
- This commit (links and QA): `industries/healthcare.html`, `industries/finance.html`, `industries/dtc.html`, `industries/saas.html`, `services/performance-marketing.html`, `services/analytics-attribution.html`, `services/branding-social.html`, `blog/marketing-mistakes.html`, `blog/marketing-strategy-from-zero.html`, `blog/healthcare-marketing-channels.html`, `about.html`, `vercel.json`, `docs/HMM_Phase2_Report_2026-10.md`, `docs/HMM_Phase2_Outreach_Shortlist_2026-10.md`, `docs/HMM_Design_System.md`.

## 10. Outstanding dependencies and decisions

1. Search Console export (intent validation).
2. Google Business Profile settings check (name, service area).
3. Redeploy the forms Apps Script so emails carry Halton Hills.
4. Approve the outreach shortlist before any pitch.
5. Decide on the About page's pricing-model wording.
6. SEO Growth OS 2.2.1 README (prerequisites, files, 7 skill names, current prompt).
7. AI-page direction for `/ai-agents-halton`.
8. Run the first AI visibility cycle (manual; needs platform access).
