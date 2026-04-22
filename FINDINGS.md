# FINDINGS.md — Off-scope observations

Anything noticed during the repositioning work that is NOT part of the migration plan lands here. Do not fix inline. The user triages separately.

Format: one bullet per finding, newest at top. Include file path + line number where applicable.

---

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
