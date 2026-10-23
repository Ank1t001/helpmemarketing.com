# Collection brief: social content module (planned, not collected)

Status, 24 October 2026: planned additional research module for the Business Cards & Spend Management Index. Nothing has been collected. The page has no social tab and must not get one until this module is collected, ingested, reviewed and approved by the owner. No examples are to be written before the evidence exists.

## Question

How do the same six providers (Venn, Float, Ramp, Loop, Keep, Airwallex) present their cards, spend tools and cross-border offers in their own social posts, and do those posts carry the conditions and proof that their web pages carry? The module extends the page's existing lessons (conditions beside the offer, the basis behind a figure, what happens next). It does not rank accounts, compare reach or claim anything about business performance.

## Accounts

Candidate accounts are those each provider links from its own website. They come from the server captures of 23 October 2026 (homepage and other captured pages; IDs are in `sources.json`). A candidate becomes a verified account only when the collector confirms, logged out, that the handle resolves, the profile names the provider, and the profile links back to the provider's site.

| Provider | Instagram | LinkedIn | X | YouTube | Facebook | Linked from | Notes to resolve |
|---|---|---|---|---|---|---|---|
| Venn | instagram.com/tryvault | linkedin.com/company/vennca | twitter.com/venncanada | youtube.com/@venncanada | none linked | S-VEN-HOME and 7 other Venn pages | The Instagram handle does not contain "venn". Confirm the profile is Venn's before including it; if it is not, record Instagram as "no account linked from the site". |
| Float | instagram.com/floatfinancialofficial | linkedin.com/company/floatfinancial | x.com/float_financial | youtube.com/@floatfinancial | facebook.com/floatfinancial | S-FLT-HOME (raw HTML; the links sit in markup my text extraction missed) | Confirm each in a browser. |
| Ramp | none linked | linkedin.com/company/ramp | x.com/tryramp | none linked | facebook.com/rampcard | S-RMP-HOME and 5 other Canadian pages | These are Ramp's global accounts, linked from the Canadian site. Record posts as global; mark a post Canada-specific only if the post itself says so. |
| Loop | instagram.com/bankonloop | linkedin.com/company/loop-financial | none (the only X link is a third-party post in a testimonial) | none linked | none linked | S-LOP-HOME and 11 other Loop pages | |
| Keep | instagram.com/keep_hq | ca.linkedin.com/company/trykeep | none linked | none linked | facebook.com/p/Keep-100080028222444 | S-KEP-HOME and 7 other Keep pages | Keep's self-serve sign-up was closed when checked; posting may also have changed. Record what is there. |
| Airwallex | none linked | linkedin.com/company/airwallex | twitter.com/airwallex | none linked | facebook.com/airwallex | S-AWX-HOME and 11 other Airwallex pages | Global accounts linked from the Canadian site; same rule as Ramp. |

Do not add accounts found by searching (employee profiles, regional accounts not linked from the site, fan or partner accounts). If the owner wants a Canadian regional account that is not linked from the site, that is a separate decision recorded here before collection.

## Channels

Instagram, LinkedIn, X, YouTube and Facebook, only where the provider links an account (table above). No TikTok or Threads account is linked by any of the six. Paid ads (Meta Ad Library, LinkedIn ads, Google Ads Transparency) are out of scope for this module.

## Observation window (fixed)

Proposed: posts published from 24 July 2026, 00:00, to 23 October 2026, 23:59:59, Toronto time (92 days, ending on the day the edition 001 pages were captured). The owner confirms or changes the window before collection; once collection starts it does not move.

- Collect once, within 14 days after the window closes, and record the actual capture time of every post. Posts deleted before collection cannot be seen; say so in the method.
- A post belongs to the window by its published date in Toronto time. Where a platform shows only a relative date ("3w"), record the absolute date from the post's own page or its ID, and the method used.

## Coverage rules

- Logged out only, in a clean browser profile, from Canada. No accounts, logins, cookies, follow requests, likes, comments, messages, form submissions or ad clicks.
- If a channel shows posts only after login (often LinkedIn and X), record that channel as "Not checked: login required" with a capture of the prompt, and do not work around it.
- Every post in the window on each checked account is recorded, including reposts and pinned posts dated inside the window. Pinned posts dated outside it are excluded and noted. Stories, live streams and archived posts are excluded (they cannot be read completely when logged out).
- Record the coverage per account: the earliest post date reached, whether the feed reached past the window start, and how many posts were in the window. A count is complete only if the feed reached past the window start.
- Rate limits, blocks or challenges are recorded once and not retried.

## What to record for each post

`platform`, `account`, `post_url`, `published_at` (with offset), `captured_at` (with offset), `format` (image, carousel, video, text, link, document), `caption_excerpt` (up to 300 characters, quoted exactly), `topic` (codebook below), `offer_conditions_present` (yes, no, not applicable), `proof_basis_present` (yes, no, not applicable), `cta_destination` (URL or none), `canada_specific` (yes, no, unclear) and, only where publicly displayed, the visible like, comment, view or repost counts with the capture time. Counts are recorded as displayed, never compared as performance or used to rank accounts.

Topic codebook (one primary topic per post): offer (rewards, FX, pricing, credit or limits), product feature, proof (customer story or figure), eligibility or next step, company or culture (hiring, team, events), partnership or media, regulatory or trust statement, other. Two people should be able to code the same post the same way; record any post that does not fit.

## Evidence requirements

- One screenshot per post showing the post, its date and its caption (sanitised: no logged-in UI, no personal data of commenters), plus one screenshot per account of the profile header and the grid or feed at the window start.
- A capture manifest in the existing `ingest.py browser` format, one line per screenshot, with real capture times. Missing or unsanitised files stop the ingest with a handoff request.
- Raw captures go into a private archive with a sha256 recorded in `edition.json`, like the edition 001 evidence archive. Nothing raw is committed: the repository is public.
- Observations use the existing statuses: Published, Not found in reviewed sources, Not checked, Conflicting, Explicitly unavailable. "No posts in the window" is a finding only when coverage is complete.

## Publication rule

The module appears on the page only after it is collected, ingested, validated and reviewed, and the owner approves it. Until then, the page does not mention social findings and shows no empty tab. Any finding must name its denominator (accounts and posts covered) and its window.
