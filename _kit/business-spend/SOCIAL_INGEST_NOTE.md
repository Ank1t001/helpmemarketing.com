# Ingestion note: Instagram evidence v1 (edition 001)

Ingested 27 October 2026 (Toronto). Status: **shown on the staging draft for editorial review; editorial approval not granted.** `social.json` has status `review` and `approved: null`. The release build stays blocked until the owner records approval in `social.json` by hand (`validate.check_inputs`, listed by `release.py --dry-run`).

## Package

| Item | Value |
|---|---|
| File | `business-spend-index-edition-001-social-evidence-v1.zip` |
| SHA-256 | `680d0e77756b67b8b7e619528de648ae6c405a09a136f39e1e01eb9ae5338231` (matches the owner's stated hash) |
| Size | 34,159,536 bytes |
| Retrieved | 27 October 2026, 1:53 p.m. Toronto, over HTTPS from a private cloud-storage link the owner shared. The link reference is kept out of this repository. |
| SHA256SUMS.txt | 100 entries, all match |
| Existing checker | `python3 -I social.py check PACKAGE`: PASS (6 accounts, 51 posts, 95 screenshots), run before any change to the kit |
| Stored | Private, outside the repository. The original zip is unchanged; nothing in it was edited. |

Raw screenshots, exact caption text, the repost list (`reposts-index.json`) and the collector's handoff stay private. The repository holds hashes, derived records and two curated image derivatives only.

## How the derived files were made

```
python3 -I social_derive.py PACKAGE_DIR PACKAGE_ZIP [PRIVATE_CAPTIONS_OUT]   # writes social.json (status review)
python3 -I social_images.py PACKAGE_DIR/screenshots                         # writes the two WebP derivatives, prints provenance
python3 build.py                                                            # page, observations CSV, Instagram posts CSV
python3 validate.py --social-package PACKAGE_DIR --social-zip PACKAGE_ZIP   # quotes, captures and zip hash against the package
```

`social_derive.py` refuses to write if the zip hash, any SHA256SUMS line, the existing checker, the targeted secret check or the expected per-account counts fail. `PRIVATE_CAPTIONS_OUT` (exact captions, with the one restoration applied separately) must be outside the repository; the script refuses a path inside it.

## Corrections to the collector's handoff (made in derived files; timestamps never rewritten)

1. **Formats and inspection.** The handoff says "All 34 videos are inspection: partial". The records hold 33 videos, 10 carousels and 8 images. Inspection: 33 videos partial (cover, caption, header and counts; not played), 1 carousel partial (the Kumar Method carousel on @tryramp), 9 carousels all slides, 8 images cover and caption. 34 posts were partially inspected: 33 videos and 1 carousel.
2. **Collection times.** The handoff says collection ran 21:49 to 22:16. The post records start at 21:45:38 and end at 22:15:28; the last manifest capture is 22:15:56. The first pass (Float, Loop and Keep, the @tryvault profile and the website footers) ran 21:01:57 to 21:09:43. The page states 9:01 p.m. to 10:15 p.m. Toronto time, with post records from 9:45 p.m.
3. **Venn website link.** The handoff says the venn.ca footer "still links" @tryvault and, elsewhere, that Ramp, Airwallex and Venn "still have no Instagram link". The capture shows the venn.ca footer linking instagram.com/tryvault; "no Instagram link" applies to Ramp and Airwallex only. The page says: "The captured Venn website footer linked to @tryvault, while this study uses owner-confirmed @venn.ca with supporting profile evidence." No reason for the difference is asserted.
4. **Omitted caption word.** In `ramp-ig-DeLBKE-hlOg` the collector marked one word as omitted because the old filter rejected it. The retained screenshot shows "stayed way past the last session"; the word is restored in the private caption file only. The old filter rejected ordinary words (session, cookie, token); `social.secret_findings` now checks for credential patterns (cookie headers, named session cookies with values, authorization headers, bearer tokens, JWTs, key or password assignments, the private storage reference format, private cloud-storage links, share tokens, cloud keys).
5. **Caption completions.** `[balance...]` (Venn `Db8eeMHEV9v`) and `[Store]` (Venn `DcOdMd8oMR-`) are the collector's completions of captions cut off in the capture, not source text. Neither is quoted; the page says the capture cuts the sentence off.
6. **Airwallex repost count.** The tab title says 15 reposts; `reposts-index.json` lists 12 (5 of in-window originals); the screenshot shows the first 8. Reposts are excluded from every count either way.
7. **Duplicate sections.** None in the handoff; no change needed.

## Clean derived summary

| Provider | Account | Scope | Attribution | Posts in window | Collaborations | Notes |
|---|---|---|---|---|---|---|
| Venn | @venn.ca | Canadian | Owner-confirmed; profile links venn.ca | 9 (7 reels, 1 carousel, 1 image) | 0 | Website footer captured linking @tryvault (excluded, not collected) |
| Float | @floatfinancialofficial | Canadian | Linked from floatfinancial.com structured data | 0 | n/a | No in-window posts found in the reviewed grid and Reels surfaces; newest 5 June 2026 |
| Ramp | @tryramp | Global | **Unresolved** | 19 records with unresolved provider attribution (12 reels, 2 carousels, 5 images) | 15: 13 published by other accounts (billpaythemusical 5, tonyhawk 4, thekumarmethod 3, playbill 1), 2 by @tryramp with a co-author; 4 "Paid partnership with tryramp" labels | Reposts: 118 listed, excluded |
| Loop | @bankonloop | Canadian | Linked from the bankonloop.com footer | 0 | n/a | No in-window posts found in the reviewed grid and Reels surfaces; newest 11 June 2026 |
| Keep | @keep_hq | Canadian | Linked from the trykeep.com footer | 0 | n/a | No in-window posts found in the reviewed grid (no Reels tab); newest 17 July 2024 |
| Airwallex | @airwallex | Global | Owner-supplied; profile names Airwallex and links airwallex.com | 23 (14 reels, 7 carousels, 2 images) | 5: 4 published by other accounts (dysonheppell 2, thejoshvfx 1, crystallimlange 1), 1 by @airwallex with co-authors; 4 paid-partnership labels (3 header, 1 caption only) | Reposts: 12 listed (tab says 15), excluded |

Totals: 51 records = 32 attributed posts (Venn 9, Airwallex 23) + 19 @tryramp records with unresolved provider attribution. The page, the CSV (`provider_attribution` column) and `social.json` (`totals.attributed_posts`, `totals.unresolved_records`) keep the two apart; findings about providers use the 32.

Window 25 July to 22 October 2026, Toronto dates, by each post page's timestamp. Grid and Reels duplicates removed by shortcode (51 unique URLs). `earliest_reached` comes from post IDs, not opened pages. Four reposts duplicate coded collaboration posts (3 Ramp, 1 Airwallex); reposts are not counted, so nothing is double counted.

**Metrics.** Kept as displayed: whole numbers as integers, abbreviations as text ("11.1K"), "No comments yet" as 0, a missing count as null (comments on `airwallex-ig-DeR-myVkbUa`). Each post carries `likes_comments_captured_at` (the post-page read time), `views_captured_at` (minute precision, from the Reels-tab read time recorded in the collector's notes: Ramp 21:58, Venn and Airwallex 22:15; no seconds invented) and `views_source`. Two Airwallex tiles (SHIFT, Money20/20) are blurred in the screenshot; their counts come from the page text. Metrics are not shown on the page, in the CSV, or compared.

## Ramp attribution: unresolved

Sought: an official Ramp source naming or linking @tryramp, or claiming the campaigns the account posts. Retained evidence first, then server fetches on 27 October 2026 (Toronto), hashes in `social.json` (`accounts[ramp].attribution.corroboration`).

- Retained 23 October captures of ten ramp.com pages: links to x.com/tryramp and linkedin.com/company/ramp; no Instagram link.
- ramp.com (1:58 p.m.) and ramp.com/blog (1:58 p.m.): no Instagram link; footer lists LinkedIn, X and Facebook. ramp.com/newsroom: 404.
- ramp.com/blog/ramp-at-60-billion (1:59 p.m.): Ramp's own post of 15 October 2026 carries the figures in @tryramp's carousel of the same day. Matching content, not an account link.
- tonystockprotrader.com (the profile link) and billpaythemusical.com: campaign sites naming Ramp as operator or presenter; their own description, not conclusive. The musical's site links its own Instagram account, not @tryramp.
- Web search restricted to ramp.com found nothing about the account or the campaign; trade press attributes the campaigns to Ramp but is not an official Ramp source.

Result: **unresolved**. The 19 records are kept, counted and listed, labelled unresolved, and excluded from examples and from conclusions about Ramp. Owner action that would resolve it: confirmation from Ramp, or an official Ramp page that links the account.

## Images

Two derivatives under `/assets/index/business-spend/social/`, made by `social_images.py` from sanitised post screenshots (sources' hashes checked against `social.json`): a minimal crop of the post (media, header with its paid-partnership label, caption), with the counts row covered in the panel's background colour so the image does not invite a comparison of counts. Crop box, covered area, source file and hash, output hash, alt text and credit are recorded in `social_narrative.json` and shown in each example's provenance. The two Venn examples use caption excerpts: their cover frames do not show the point (one shows a person from behind; one is a small dashboard image with a blurred account name).

## Editorial pass (27 October 2026, owner's instruction)

- Venn example of 30 July: Venn's plan limits were captured on 23 October; whether any applied on 30 July was not established. The example says so beside the analysis and no longer presents the October limits as missing from the July caption.
- Ramp: still unresolved; Ramp was not contacted and nothing was recollected. The 19 records are labelled "records with unresolved provider attribution" in the table, the download and every total, apart from the 32 attributed posts.
- Airwallex creator example: statements about a missing market or condition are limited to the caption and cover; the video was not watched. `social.check_narrative` now refuses whole-post claims on reels that were not watched.
- Relationship disclosure: confirmed by the owner on 23 October 2026 and kept on the page; no longer listed as open.

## Three tests

Unchanged. No social observation gives stronger evidence than the website observations behind tests 1 to 3: the posts are a different surface, captured on a different date, and reels were read from cover and caption only. The view links two Venn posts to test 1 and one Airwallex post to test 3.

## Still needed before release

- The owner's editorial review of the Instagram view, then approval recorded by hand in `social.json` (`status: reviewed`, `approved`).
- A decision on Ramp attribution (or leave it unresolved, as the page states).
- The existing release requirements in `RELEASE_STEPS.md`: the edition approvals and the owner's approval of the hub wording.
