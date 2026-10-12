# HMM Phase 1 indexing follow-up, 12 Oct 2026

Production baseline: main `261bcbf` (Phase 2 release, live 12 Oct 2026 14:50 UTC). No site changes in this follow-up.

## 1. Search Console actions (founder, in the GSC interface)

This environment has no Search Console access, so nothing below has been submitted yet. Record each line when done. An indexing request is not proof of indexing.

| Action | Date and time | Status shown by GSC | URLs detected / result |
|---|---|---|---|
| Resubmit `https://helpmemarketing.com/sitemap.xml` | pending | pending | live file holds 49 `<loc>` entries (checked 12 Oct) |
| URL Inspection + request indexing `/realestate-index` | pending | pending | live: 200, self-canonical, no noindex, in sitemap |
| URL Inspection + request indexing `/hmm-index` | pending | pending | live: 200, self-canonical, no noindex, in sitemap |
| URL Inspection + request indexing `/services` | pending | pending | live: 200, self-canonical, no noindex, in sitemap |
| URL Inspection + request indexing `/about` | pending | pending | live: 200, self-canonical, no noindex, in sitemap |

## 2. Last crawl vs recent page updates

Crawl dates from the Phase 1 workbook; change times from git (main).

| Page | Last Google crawl | Updates since 8 Oct | Reading |
|---|---|---|---|
| `/about` | 8 Oct | 8 Oct 14:05 to 14:21 UTC (voice, team claims); 10 Oct light mode; 11 Oct header, footer, full rebuild (20:37 UTC); 12 Oct location, links, pricing removal | Crawl predates the rebuild and every later change. If the 8 Oct crawl was before 14:05 UTC, it predates all of them. Google has not seen the current page. |
| `/services` | 11 Oct (time not recorded) | 11 Oct header/footer (15:41 UTC) and full rebuild (20:30 UTC); 12 Oct location FAQ | Crawl most likely predates the 20:30 UTC rebuild, but the crawl time is needed to confirm. Google has almost certainly not seen the 12 Oct version. |

Content length is a hypothesis, not a cause: both "Crawled, currently not indexed" verdicts were made on versions that no longer exist. Recheck after a fresh crawl before judging the current pages.

## 3. Issue Register reconciliation (against production, 12 Oct)

The register lives in the founder's workbook; only items checkable here are listed.

| Issue | Production check | Proposed status |
|---|---|---|
| T-08 healthcare blog links via `/reviews-reputation` | Live `/blog/healthcare-marketing-channels` has 0 references; links go to `/services/branding-social`. `/reviews-reputation` and `/reputation` 308 to `/services/branding-social` (no dead anchor) | Close: fixed in `a46f4d3`, live in `261bcbf` |
| `/instagram-reindex` migration | 308 to `/realestate-index`; new URL 200, self-canonical, in sitemap; old URL not in sitemap | Close (Google indexing of new URL tracked separately) |
| Sitemap `lastmod` all one date | Still true: all 49 entries read 2026-10-11, but `/about` and `/services` changed 12 Oct | Keep open. Fix is the CLAUDE.md git-date refresh script; it is a site file change, so needs approval |
| HIPAA checklist orphan | Still true: no served page links to `/industries/healthcare/hipaa-checklist` (only the unserved `docs/_healthcare` archive) | Keep open, needs a decision (link from a relevant page, keep as resource, or noindex) |
| `/realestate-index`, `/hmm-index` unknown to Google | Pages healthy live | Keep open until URL Inspection shows them known |
| `/services`, `/about` crawled, not indexed | See section 2 | Keep open; recheck after recrawl |

## 4. When to recheck

- Sitemap processing: 2 to 3 days after resubmission (around 15 Oct).
- URL Inspection for the four URLs: about 7 days after the requests (around 19 Oct), then 26 Oct if unchanged.
- Page indexing report and matched-period clicks: with the 27 Oct SEO Growth OS run.
