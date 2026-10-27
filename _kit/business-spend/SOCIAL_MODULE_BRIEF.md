# Collection brief: social content module (planned, not collected)

Status, 27 October 2026: collected on 26 October 2026 (package `business-spend-index-edition-001-social-evidence-v1.zip`) and ingested on 27 October 2026 (`SOCIAL_INGEST_NOTE.md`). The "Instagram content" view (`#bs-social`, after Messaging & offers) is shown on the staging draft for editorial review only; release waits for the owner's approval, recorded by hand in `social.json`. Ramp's account attribution is unresolved. This brief stays the rulebook for the module; where the owner's ingestion brief of 27 October 2026 differs (examples may use reels read from cover and caption only, labelled "Cover and caption reviewed; video not watched."; the view is titled "Instagram content"), the later instruction applies.

## Question

How do the same six providers (Venn, Float, Ramp, Loop, Keep, Airwallex) present their cards, spend tools and cross-border offers in their own Instagram posts, and do those posts carry the conditions and proof that their web pages carry? The module follows the page's chain: observed evidence, customer question, my interpretation, testable hypothesis, measurement. It does not rank accounts, compare reach, claim paid promotion, or say anything about leads, revenue or business results.

## Observation window (fixed)

**25 July through 22 October 2026, inclusive, America/Toronto. This is 90 complete calendar days. Do not silently move this window.**

- A post belongs to the window by its publication date in Toronto time. Record how the date was established: `visible_date`, `post_page_timestamp` (the date in the post page's own time element) or `relative_date_converted` (a "3w"-style date converted on the collection day; say so).
- The website observation dates (23 October 2026, 10:39 a.m. to 2:33 p.m.) stay unchanged. The page shows the social collection dates separately ("Social posts 25 July to 22 October 2026"), and the method states both.
- Record the actual capture time of every post and of every set of visible metrics.

## Channels and accounts

Official company Instagram accounts only (owner decision, 26 October 2026: LinkedIn is out of scope). Not LinkedIn, X, YouTube, Facebook, TikTok or Threads; not founder, executive or employee accounts; not partner, regional fan or reseller accounts.

Verification, in this order:

1. Prefer the account the provider links from its own website (the candidates below come from the server captures of 23 October 2026). The owner supplied the Ramp and Airwallex accounts on 26 October 2026; neither site links an Instagram account, so those two are owner-supplied candidates and need the same identity check.
2. Cross-check identity: the profile names the provider, and the profile's link points to the provider's domain.
3. Label scope: `canada` when the account presents itself as the provider's Canadian account, `global` when it is the company's worldwide account, `unclear` otherwise. A post is Canada-specific only if the post itself says so.
4. If identity stays uncertain, record the account as `unverified` and collect nothing from it.
5. Website links and owner-supplied handles are discovery leads, not proof: every account is verified on its own profile before any post is used. A missing Instagram link on a Canadian website does not show that the provider has no Instagram account; record `no_account` only when no official account can be identified.
6. Do not attribute a global account's product terms or offers to Canada without supporting evidence, and never substitute a founder's or employee's profile for the company account.

| Provider | Instagram candidate | Linked from | To resolve |
|---|---|---|---|
| Venn | instagram.com/venn.ca (owner-supplied, 26 Oct 2026) | Not linked from venn.ca: the site links instagram.com/tryvault instead (S-VEN-HOME and 7 other Venn pages, 23 Oct captures; still so in a server fetch 26 Oct, 9:34 p.m.). The homepage also links to www.tryvault.com and help.tryvault.com. | Verify @venn.ca's profile name and its link to venn.ca, and collect from it once verified. Check what @tryvault shows (name, link, whether it points to @venn.ca or looks inactive) and record it; do not collect from @tryvault unless the owner decides it is also in scope. |
| Float | instagram.com/floatfinancialofficial | S-FLT-HOME (raw HTML) | Verify. |
| Ramp | instagram.com/tryramp (owner-supplied, 26 Oct 2026) | Not linked from ramp.com or ramp.com/en-ca (23 Oct captures; server fetch 26 Oct, 9:03 p.m.) | Verify the profile name and that it links to ramp.com. Probably the company's worldwide account: label `global` unless it presents itself as Canadian. |
| Loop | instagram.com/bankonloop | S-LOP-HOME and 11 other Loop pages | Verify. |
| Keep | instagram.com/keep_hq | S-KEP-HOME and 7 other Keep pages | Keep's self-serve sign-up route was closed when checked; record what is posted, without inferring why. |
| Airwallex | instagram.com/airwallex (owner-supplied, 26 Oct 2026) | Not linked from airwallex.com or airwallex.com/en-ca (23 Oct captures; server fetch 26 Oct, 9:03 p.m.) | Verify the profile name and that it links to airwallex.com. Probably the company's worldwide account: label `global` unless it presents itself as Canadian. |

## Collection

- Public posts may be viewed in the owner's normal signed-in Chrome. Record for each account whether the browser was signed in to Instagram (`logged_in` true or false).
- **Never export cookies, share login tokens, automate private account access or bypass restrictions. Do not start paid collection without an approved budget.** No scrapers, no follow requests, likes, comments, messages, form submissions or ad clicks.
- A rate limit, block or challenge is recorded once (`blocked`) and not retried. Blocked is not inactive: it means "not seen", never "no posts".
- If collection cannot proceed, the code work stands on its own and the page shows no social content.

## Coverage

- Preferred: a complete inventory of the window for each verified account, reading the feed past 25 July 2026 (record `earliest_reached`). A count is complete only if the feed reached past the window start.
- Owned posts, reposts and collaborator posts are recorded separately (`relation`: original, repost, collaboration).
- Otherwise: a labelled partial sample (`partial`), with no posting frequency and no topic proportions for that account.
- Excluded: Stories, live streams, deleted posts, private content and ad libraries (Meta Ad Library). Pinned posts dated outside the window are excluded and noted.
- No claims about paid promotion, boosting or distribution.

## What to record for each post

`id`, `platform` (provider), `channel`, `account` (the verified handle), `url` (permanent URL or post ID), `published_on` and `date_method`, `captured_at` (with offset), `scope` (account geographic scope), `relation`, `format` (image, carousel, video, text, link, document), `topic`, `question` (the customer question the post addresses), `product` and `geography`, `hook` (the opening line or frame, quoted short), `proof` (what supports the claim, or null), `cta` (destination or null), `inspected` (what was actually looked at), `inspection` (`cover_and_caption`, `all_slides`, `watched_in_full` or `partial`), `capture_ref` (the screenshot file in the private archive) and `metrics`.

Topic codebook (one primary topic): offer (rewards, FX, pricing, credit or limits), product feature, proof (customer story or figure), eligibility or next step, company or culture, partnership or media, regulatory or trust statement, other.

## Inspection rules

- A cover and caption support analysis of the cover and caption only.
- A video is analysed only after it is watched; a carousel only after every slide is inspected. Anything less is labelled `partial` and cannot carry a gallery example.
- Full captions are not reproduced on the page; short quoted phrases only.

## Metrics

- Recorded as displayed (likes, comments, views), with their own capture time and the post's age at capture. A metric that is not shown is recorded as `null`, never left out or set to zero.
- No ranking by likes, no "best performing", no engagement rates with inconsistent denominators, no leads or revenue. The method discloses that older posts have had longer to collect responses.

## Evidence and storage

- One sanitised screenshot per post (post, date and caption; no signed-in UI, account names of the viewer, notifications, commenter names or faces of private individuals), plus one per account of the profile header and the feed at the window start.
- A capture manifest in the existing `ingest.py browser` format, with real capture times; missing or unsanitised files stop the ingest with a handoff request.
- Raw captures go into a separate, versioned private archive (`business-spend-index-edition-001-social-evidence-v1.zip`) with its own manifest and sha256, recorded in `social.json`. The edition 001 evidence archive is not modified. Raw captures, private storage references, session material and personal information never enter this public repository, the page or the CSV.

## Validation and publication

`social.py` enforces the window, the Instagram-only channel, verification, coverage labels, required fields, the inspection rules, explicit nulls for missing metrics, per-platform metric names and the absence of session material. The page gets a "Social content" view (`#bs-social`) only when `social.json` has status `reviewed`, the owner's approval is recorded in it by hand, and the checks pass. The view then shows: a scope and coverage note, a compact cross-brand summary, and a curated gallery with stated selection criteria (one strong example per provider where supported, a second only for a distinct lesson). Each example carries the image, credit and link, date and platform, the observed message, my reading and a takeaway. Images are self-hosted under `/assets/index/business-spend/social/` after sanitising; they are never hotlinked.

If the module gives stronger evidence than one of the three current tests, at most one test is replaced, with the reason recorded.
