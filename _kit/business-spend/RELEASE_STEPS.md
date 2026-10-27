# Release steps: Business Cards & Spend Management Index, edition 001

Status on 27 October 2026: **released.** The owner approved edition 001, the Instagram content and the final hub wording on 27 October 2026 (recorded in `edition.json` `approvals` and `social.json` `approved`), and instructed the ship of the reviewed staging commit `6e643b3` plus the release-generated changes. Steps 6 to 13 were followed; the record of the production deployment and `modified_at` is in `edition.json`. Steps 1 (stored archive copy) and 5 (forms script) remain open and are not release blockers. The text below is kept as the procedure for any later edition.

Original status (24 October 2026): draft on `staging-business-spend`, `noindex`, not merged.

## Before release (owner decisions and inputs)

1. **Evidence archive** (`business-spend-index-edition-001-evidence.zip`, sha256 `735b0ac51676bd02c253ee1a29b0e0b460c75497ef4430247cb0070c2cd781ab`): the owner has supplied a private storage reference (status `reference_supplied`). Still to do: retrieve the stored copy and run `validate.py --archive` on it. Only then set `storage.stored_copy_retrieved`, `storage.stored_copy_hash_verified` and `location_status: stored`. The reference itself never goes in this repository.
2. **Editorial review** of the staging page, including the three Conflicting items and two Not determined items, which stay shown as they are unless you decide otherwise.
3. **Hub wording**: approve or edit the seven wording changes in `release.py` `HUB_EDITS` (listed in the dry-run report). They broaden only wording that implied every Index studies Instagram or refreshes monthly; the three Instagram studies keep their methods, monthly schedule, card labels and dates. Also choose a text-only hub card or supply a 1056x591 hero image pair.
4. **Optional captures** R1 and R2 in `CHROME_HANDOFF.md`. Without R1 the page keeps the bounded Ramp rewards wording; without R2 the Ramp card model and conversion margin stay omitted with the limitation stated (decision of 24 October 2026).
5. **Forms script**: deploy `research_business_spend` using the steps in `CHROME_HANDOFF.md` and send the version number. Not a hard blocker (leads are saved either way), but attribution needs it.

## Release (after the owner's explicit instruction)

6. Record the instruction in `edition.json` by hand: `status: published`, `approvals.editorial` and `approvals.publication` with the date and the instruction's wording, `published_at` = the Toronto release date (YYYY-MM-DD). Nothing generates these.
7. `python3 release.py --apply` writes: `business-spend-index.html` (index, follow; citation card; edition history; draft label gone), `business-spend-index/edition-001.html` (snapshot: self canonical, one `noindex, follow`, edition 001 breadcrumb item, header comment, same body), `hmm-index.html` (card, `CollectionPage` entry, approved wording) and `sitemap.xml` (the live page with the release date; `hmm-index` lastmod). The snapshot is never in the sitemap.
8. Checks: `python3 build.py --check`, `python3 validate.py --raw RAW --browser SHOTS --archive ZIP`, `python3 -m unittest tests.test_kit`, the JSON-LD audit in the Design System, and browser checks at 1280/390 in both themes.
9. Update `CLAUDE.md` (the Business Spend bullet: published, snapshot path, hub and sitemap) and the Design System note in the same commit.
10. Commit on `staging-business-spend`, deploy a preview, verify: page 200 and indexable, snapshot 200 and `noindex`, hub card, sitemap, `/_kit/` 404.

## Ship (only on "ship it")

11. Merge `staging-business-spend` into `main` and push. The merge also carries `contact.html` (entry allow-list) and the kit; nothing else on main changes.
12. After the production deployment is READY: a metadata commit sets `edition.json` `modified_at` to the deployment's ready time (full ISO time with timezone), rebuilds the page so the Article carries `dateModified`, records the same fix in the snapshot's header comment, and sets the hub card's "Last updated" to the Toronto date of the deployment. No `datePublished`.
13. Verify production: `/business-spend-index` (200, index), `/business-spend-index/edition-001` (200, noindex), `/business-spend-index.html` (308), `/hmm-index`, `/sitemap.xml`, `/_kit/business-spend/README.md` (404), and the review button reaching `/contact?intent=review&entry=research_business_spend`.

Not part of this release unless asked: requesting indexing, submitting the sitemap, IndexNow, any scheduled refresh.

The Instagram content module (`SOCIAL_MODULE_BRIEF.md`, `SOCIAL_INGEST_NOTE.md`) was collected, ingested and approved with this release (27 October 2026). For a later edition it releases only when `social.json` is `reviewed` with the owner's approval recorded by hand; `validate.check_inputs` blocks the release otherwise.
