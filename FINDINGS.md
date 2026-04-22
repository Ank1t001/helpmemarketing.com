# FINDINGS.md — Off-scope observations

Anything noticed during the repositioning work that is NOT part of the migration plan lands here. Do not fix inline. The user triages separately.

Format: one bullet per finding, newest at top. Include file path + line number where applicable.

---

## Client-roster pass — real clients mapped

- Per-client metric attribution is tight but uses industry aggregates (from the user-provided "Premium Metrics" list) as each client's headline number. Example: Luxe & Charme shows "+312% revenue growth" — the DTC industry aggregate, not a client-specific verified measurement. If any client's real number differs significantly, the value on that card needs to change.
- Duration (timeframe pill on each case card, e.g. "12 months", "9 months", "6 months") is chosen for visual rhythm across the grid, not sourced from client-specific data. Swap per client when real engagement lengths are known.
- Homepage testimonial still has `[PLACEHOLDER]` on both the quote and author name. Suggested featured client is Equiton but the user should supply the exact quote + signer (CEO, Founder, Head of Marketing, etc). Currently fallback text is the mockup's "acted like a partner instead of a vendor" line — that's kept as a visual placeholder, not intended to ship as-is.
- Homepage `<title>` + meta description still `[PLACEHOLDER]`-flagged. Current value ("HelpMeMarketing — Growth Partner for Premium Brands") is a reasonable default but the user should lock positioning copy before indexing.
- Travel is NOT one of the four industry pages but IS a case-card vertical (TravelUp on homepage + work). Work page gained a "Travel" filter button. If Travel grows into a primary vertical, a new `/industries/travel` page is the next step; until then it lives only on `/work` + homepage hero.
- Industry page hero metric cards now attribute the industry aggregate to one representative client (DTC→Luxe & Charme, SaaS→Fieldline Ops, Healthcare→Vanguard Pharmacy, Finance→Equiton). If those attributions are wrong (e.g. Fieldline Ops didn't actually produce the 3.2× aggregate on their own), the label needs a tweak.
- Service page hero metric cards now each attribute to one representative client across the roster: SEO→Vanguard Pharmacy, Ads→TravelUp, Websites→Luxe & Charme, Social→Shakti Warrior, Brand→Sterling Wealth, Lifecycle→Wax and Wane, Analytics→Fieldline Ops, Reviews→Med Aesticics. User can reshuffle if a different client is a better proof point for a given service.
- Case-card quotes were ALL removed from homepage + industry pages + work page because the roster didn't include quotes. Only the final-CTA and testimonial retain quote text. When real quotes arrive, the `.case-quote` div can be re-added to any card.

## Phase 6 — final pages + archive

- Blog posts (8 items in `blog.html`) are still 100% healthcare-themed (Google Ads for healthcare 2026, HIPAA-aware GTM, PHIPA vs PIPEDA, Vanguard Pharmacy, etc). Per plan these stay until the user refreshes with new posts. Hero + newsletter copy are now generalized but the post cards themselves surface healthcare-specific topics — acceptable for a historical archive.
- `/work.html` shows 6 placeholder cases (1 Healthcare, 2 DTC, 2 SaaS, 1 Finance). The `Vanguard Pharmacy & Clinic` card is kept as a real case that straddles verticals — user may want to promote it off the main case grid once real cases arrive, in which case it lives verbatim in `/_healthcare/case-studies.html` already.
- Ad-calculator BENCH values are aggregated industry approximations (CPL, conversion, LTV per DTC/SaaS/Healthcare/Finance segment). Flagged with a `[PLACEHOLDER]` comment in the file header. User should confirm or replace with owned benchmarks before shipping.
- `/_healthcare/` folder now contains four pages: healthcare-seo, hipaa-checklist, ad-calculator, case-studies. All asset paths have been rewritten to `../styles.css` and `../{page}.html` for subfolder hosting. `robots.txt` has `Disallow: /_healthcare/`; `sitemap.xml` omits the archive. The healthcare industry page (`/industries/healthcare`) links to `/_healthcare/hipaa-checklist` as a resource bridge.
- About.html founding story is a placeholder-friendly generic narrative ("We spent years inside agencies…"). If the user has a real origin story they want on the page, it swaps in cleanly — the structure and principles stay.
- Privacy.html and Terms.html were generalized: "healthcare-only" → "premium brands across DTC, SaaS, healthcare, and finance"; "patient" → contextualized to "client, patient, or prospective buyer"; "practice" → "business"; PHI references expanded to cover regulated data broadly. Compliance bona fides preserved for healthcare engagements via BAA/DPA references.
- Pricing FAQ replaced the healthcare-specific HIPAA/PHIPA entry with a regulated-industries FAQ that covers both healthcare (HIPAA-aware tracking) and finance (consent-first creative) — keeps the signal value without locking positioning back to healthcare.

## Phase 5 — industry pages

- Industry pages deliberately omit the dark-navy Process section (per user's option B choice: hero + pain + services + case + CTA). If UX review wants process added for consistency with service pages, a single line in each industry file inserts it.
- The same three placeholder gradient classes (`case-1/2/3`) are reused across homepage + all 4 industry case grids. That means DTC's "Arden & Oak" card, Healthcare's "Vanguard Pharmacy" card, etc. all share visual backgrounds. When real photography ships, each case gets its own image — no conflict, but today the repetition is visible when you scroll across pages.
- Every industry page has a reordered services grid showing all 6 homepage services. I chose to reorder rather than filter (showing 4 instead of 6) to keep cross-sell potential open. If the user wants literal filtering per industry, it's a small edit per page.
- The healthcare industry page surfaces a link to `/_healthcare/hipaa-checklist` in its hero secondary CTA. That's the only main-site page that references the archive; intentional for conversion-asset surfacing.
- Industry case studies are all PLACEHOLDER invented clients (Arden & Oak, Fieldline Ops, Maison Noord, Meridian Wealth, etc). Each industry page has one `[PLACEHOLDER]` comment wrapping all three cards. User replaces when real client assignments come in.
- `data-screen-label="industry"` is new — used on all 4 pages for analytics and any future industry-specific overrides.

## Phase 4 — service pages

- All 8 service pages share the same 4-step Process section verbatim. When a service needs a truly service-specific process (e.g. Websites might warrant design-review / launch-rehearsal phases), that's worth revisiting. Out of scope for repositioning.
- Hero metric values on every service page are invented benchmarks (+42%, ↓32%, 2.3×, 3.8×, +124%, +48%, 4.9★, 95%). Each page has a single `[PLACEHOLDER]` comment at the metric card wiring point; user replaces with real client numbers pre-ship.
- Icon color mapping reuses 6 classes across 8 services: Analytics + Brand both use `ic-navy`; Ads + Reviews both use `ic-gold`. Not a conflict per se (only 6 appear on the homepage), but worth noting if a 7th/8th distinct accent color is ever wanted.
- `services.html` splits into two sections: "Core services" (6 cards, 3-col) and "Supporting services" (2 cards, 2-col). The 2-col override uses an inline style on the grid; if a third supporting service is ever added, the override should turn into a dedicated class.
- The old service slugs (`/clinic-websites`, `/retention`, `/reputation`, `/brand`, `/healthcare-seo`, `/hipaa-checklist`) now return 301s via `vercel.json`. Both the `.html` and clean-URL variants are covered. Verify on Vercel preview with `curl -I` before any go-live.

## Phase 0 — seed

- `contact.html:204` — Google Apps Script endpoint is hardcoded in an inline `<script>`. Not a problem to fix now, but worth noting for future infrastructure hardening (env var / config file / CSP).
- `sitemap.xml` is hand-maintained; no validation step. After Phase 4/5 URL changes, recommend a one-time XML lint pass.
- `.nav-link.active` state is set manually per page in both the desktop and mobile nav blocks. Some pages (contact, blog, pricing, privacy, terms, hipaa-checklist, ad-calculator) correctly leave no link active; others (service detail pages) mark Services active. Consistency is OK today — flag if it drifts.
- `ad-calculator.html:258-270` — the `BENCH` table is 11 healthcare specialties with specific CPL/convRate/LTV values. Replacing it with a generalist BENCH (Phase 6) requires either user-supplied benchmarks or research. Current values should be archived to `/_healthcare/ad-calculator.html` verbatim for reuse.
- `work.html:250-265` — case-study filter JS toggles cards by `data-tag`. After Phase 6 migration, the filter values change (Pharmacy/Physio/Derm/Dental → DTC/SaaS/Healthcare/Finance) but the logic is unchanged.
- `styles.css` is ~1,026 lines of hand-authored CSS. No CSS linter, no stylelint config. If the repo ever grows, introducing one would catch drift — out of scope for repositioning.
- `vercel.json` has security headers and `cleanUrls` but no redirect rules. Phase 4 will be the first time the `redirects` array is introduced.
- Mobile menu toggle is an inline `onclick="..."` on the hamburger button, duplicated on every page (see `CLAUDE.md`). Not broken, just the cost of not having templating.
- No analytics script currently in the codebase. When/if analytics is added, it should be a Phase 7+ effort — not part of repositioning.
- Fonts currently load with `display=swap`. Good. Keep this when switching to Fraunces.
