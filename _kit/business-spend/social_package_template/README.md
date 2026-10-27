# Social collection package (template)

Fill this folder in your own Chrome, following `CHROME_HANDOFF.md` steps S1 to S6 and `SOCIAL_MODULE_BRIEF.md`. Copy it outside the repository first: the filled package holds screenshots and must never be committed (this repository is public).

Window (fixed): 25 July through 22 October 2026, inclusive, America/Toronto. Channel: official company Instagram accounts only.

## Files

- `accounts.json`: six rows, one per provider, pre-filled with the Instagram accounts linked from each provider's website on 23 October 2026, plus the Ramp and Airwallex accounts supplied by the owner on 27 October 2026 (neither site links one). Nothing here is verified. For each row set `verified`, `verification` (what you checked), `scope` (canada, global or unclear), `logged_in` (true or false), `coverage` (complete, partial, blocked, no_account or unverified), `coverage_note`, `earliest_reached` (the oldest post date you reached) and `posts_in_window` (a number only when complete, otherwise null). Keep every row, even when there is no account.
- `posts.json`: one object per post in the window from a verified account. Fields: `id` (for example `LOP-IG-001`), `platform`, `channel` (`instagram`), `account` (the verified handle), `url`, `published_on` (YYYY-MM-DD, Toronto), `date_method` (visible_date, post_page_timestamp or relative_date_converted), `captured_at` (ISO time with offset), `scope`, `relation` (original, repost or collaboration), `format` (image, carousel, video, text, link or document), `topic` (offer, product feature, proof, eligibility or next step, company or culture, partnership or media, regulatory or trust statement, other), `question`, `product`, `geography`, `hook` (short quote), `proof` (or null), `cta` (or null), `inspected` (what you actually looked at), `inspection` (cover_and_caption, all_slides, watched_in_full or partial), `capture_ref` (the screenshot file name) and `metrics`.
- `metrics`: `{"likes": n|null, "comments": n|null, "views": n|null, "captured_at": "..."}`. Null when the count is not shown; never 0 for missing.
- `manifest-social.jsonl`: one line per screenshot: `platform`, `channel`, `role` (social-account for a profile header or feed-start capture, social-post, social-block for a login wall, challenge or block), `account`, `url`, `captured_at`, `logged_in`, `screenshot`, `sanitised` (true), `sanitisation_note`, and for posts `published_on`.
- `screenshots/`: the sanitised PNG or WebP files named in the manifest.

## Rules that the check enforces

Posts only from verified accounts and inside the window; every account row present; videos watched in full and carousels opened slide by slide before they are described (or `partial`); a complete count only when the feed was read past 25 July 2026; metrics with their own capture time and nulls for missing values; no cookies, tokens, session details or passwords anywhere; every post's screenshot in the manifest and in `screenshots/`.

## Check and send

From `_kit/business-spend`: `python3 social.py check /path/to/your-package`. It lists anything missing and writes nothing. When it passes, zip the folder as `business-spend-index-edition-001-social-evidence-v1.zip` and send the zip. `python3 social.py ingest` then writes `social.json` as a draft (screenshot hashes only), which adds nothing to the page until it is reviewed and you approve it by hand.
