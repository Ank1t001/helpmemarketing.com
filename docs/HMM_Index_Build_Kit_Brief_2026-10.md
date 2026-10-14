# HMM Index: Build Kit brief for the report body (October 2026)

Status: **handoff only.** This brief describes what the external Build Kit (`build_v2.py`) should emit from cycle 004 onward. Writing it does not update the kit. Until the kit is changed, each cycle's generated body will overwrite the manual patch made to `/realestate-index` on 12 October 2026.

Applies to all three Index instances (`/realestate-index`, `/hair-loss-index`, `/gta-medspa-index`). The example figures below are cycle 003 Real Estate numbers and are for illustration only; the kit must always fill them from that cycle's verified data.

Source of the brief: founder review "HMM Real Estate Instagram Index: UX & Content Review" (12 October 2026).

## 1. Ground rules (non-negotiable)

1. **Never invent or estimate figures.** Every number on the page comes from the cycle's scraped dataset or is calculated from it by the kit's existing formulas. If a number cannot be computed, show "not available this cycle", never a guess.
2. **Keep everything.** Research, rankings, scores, pillar calculations, methodology, the full post log, source links on every claim, the CSV download and the cycle history all stay. Advanced sections may move lower or into expandable blocks; nothing is deleted.
3. **Body-only publish** stays as in CLAUDE.md: paste only between the REPORT BODY markers; the site owns the head, nav, `.msi` wrapper and footer. The head stays cycle-agnostic (no cycle number, dates, cadence words such as "fortnightly", firm counts or coverage claims).
4. **House rules**: first person singular for the publisher (I = Ankit Kumar), no em dashes, Canadian spelling, no inline `style` attributes (use the utility classes listed in CLAUDE.md, "Index generator contract"), frames self-hosted under `/assets/index/<instance>/frames/`.

## 2. Data freshness rules

The page must always show two different things, never merged into one claim:

| Field | Meaning | Source |
|---|---|---|
| **Last verified data** | The date the dataset on this page was scraped and checked | The cycle's `scraped_at` (Instagram rows) |
| **Next scheduled refresh** | The date the next cycle is planned | The kit's schedule |

Rules:

- The "last verified" date changes only when a new refresh has completed and been published. Never move it forward by hand.
- If today's date is past the scheduled refresh and no new cycle is published, the status bar shows the scheduled date followed by "not yet published". Do not call the page a "live index" in that state.
- Do not print a cadence ("twice monthly, 5th and 19th", "fortnightly") anywhere the kit cannot guarantee it. Show the next scheduled date instead.
- The download confirmation must not promise a delivery date ("lands on 5 Oct"); use "I'll email you when cycle NNN is published."
- The bottom "Last updated" line repeats the same two fields with the same wording.

Status bar markup (current patch):

```html
<div class="livebar"><span>Last verified data <b>24 Sep 2026</b></span>
<span>Next scheduled refresh <b>5 Oct 2026</b>, not yet published</span>
<span>Cycle <b>003</b></span></div>
```

When the cycle is on schedule, the second span reads `Next scheduled refresh <b>DATE</b>` without the suffix, and the first span may be preceded by the live dot.

## 3. Revised page structure (top to bottom)

| # | Section | Purpose | Notes |
|---|---|---|---|
| 1 | Header | Title, one-sentence scope, publisher | Byline audience: "For business owners and marketing leads who want to see what their category is doing on Instagram." Never "Growth Architects" or "performance marketers" as the audience. |
| 2 | Status bar | Freshness (section 2) | |
| 3 | **Three findings from this cycle** | A 30-second takeaway | Three tiles (posts reviewed, comments recorded, accounts compared) plus three numbered findings in a `card`. Followed by: "These describe this cycle's sample only; they don't show cause and effect or predict future results." Each finding must be traceable to a table lower on the page. |
| 4 | Scoreboard | Compare the firms | Caveat **directly under the dek**, as a `pnote`: HMM-built index of public engagement, not an official Instagram ranking, not a measure of leads, customers or revenue; plus a sentence on comment volume or roster changes when either affects ranks. Future: let readers switch between overall score and single measures (engagement rate, posting frequency, comments), each with a one-line definition. |
| 5 | Creative examples | Make the analysis memorable | Compact gallery: self-hosted frame, account, theme, **Observation** (how it did against that account's own typical post in the window) and **What to test** (one experiment). No claim that one post proves a repeatable formula. |
| 6 | Content themes | Ideas to test | Heading "Which content themes received more engagement in this sample". Dek states likes are not adjusted for follower count or posting frequency and some themes have few posts. Keep the table and its "read" column. |
| 7 | Category story and account notes | Narrative | Keep, in the buyer-friendly tone (section 4). |
| 8 | Methodology and advanced sections | Full transparency | Roster changes, pillar definitions and weights, the creative positioning map, the boost ledger, the cohort read, campaign watch, outside-the-category reference. May sit lower or inside `<details>`; must stay complete and linked. |
| 9 | Full post log | Evidence | Filterable, every row linked to its source post. |
| 10 | Take the dataset with you | Primary CTA | The email-gated CSV stays the primary action. |
| 11 | Secondary CTA | Soft review offer | `pnote` under the gate: "Want a second opinion on your own marketing? Send your website and I'll review the publicly visible parts and share what I'd improve first. Get my free marketing review (link to `/contact?intent=review#contact-form`). It isn't a full competitor study." |
| 12 | FAQ, about, byline, last updated | | |

Visual hierarchy: one H1; each section an H2 in sentence case; tiles only for headline counts; one `card` per narrative block; caveats as `pnote` or `note`, placed next to the thing they qualify, not paragraphs later.

## 4. Buyer-friendly language

Describe what the public data shows; do not judge firms or claim business outcomes that likes, comments and plays cannot establish.

| Avoid | Use instead |
|---|---|
| "Which content themes actually work" | "Which content themes received more engagement in this sample" |
| "The cautionary tale" | "High posting, low visible engagement" |
| "publishes constantly and is met with silence" | "posts often, with low visible engagement relative to its follower count" |
| "punished for silence" | "posted rarely" |
| "The one thing that works is the thing they do least" | "The format that drew the most likes is the one they used least" |
| "the mirrors are dying" | "cross-posted accounts are slipping" |
| "cannot be bought, cannot be conjured ... got nothing" | "In this sample, cross-posting and question-led captions did not bring replies" |
| "A question mark is not an engagement strategy" | "A question at the end of a caption did not start conversations in this sample" |
| "Any agency reporting you an average is hiding the median" | drop the sentence; keep the definition of a median |
| "the most work for the least return", "doing nothing" | "Highest posting frequency, but low visible engagement relative to follower count" |

Also: never present the Index Score as a measure of customers, leads or revenue; use "in this sample" or "this cycle" on every comparative claim; firm wording rule from CLAUDE.md stands ("has no corporate Instagram account").

## 5. Methodology disclosures (must appear every cycle)

- How the score is built: pillars, weights, which pillars are percentile-based, and which enter later.
- Sample size: posts, accounts, comments, the window length and the scrape date.
- Roster changes since the last cycle and their effect on percentile scores.
- What the data cannot show: causation, sales, leads, paid reach that is not visible publicly.
- Data source: public Instagram data via the scheduled pipeline; nothing estimated.

## 6. What changed on the live page on 12 October 2026 (manual patch, cycle 003 body)

Made directly in `realestate-index.html`, figures unchanged:

- Lede "Living competitive intelligence" became "Competitive intelligence"; byline audience rewritten.
- Status bar: "Live index" and the cadence removed; last verified date (24 Sep 2026) and next scheduled refresh (5 Oct 2026, not yet published) shown separately; same in the bottom "Last updated" line.
- New "Three findings from this cycle" section (figures 68, 17 and 5 and the three findings are taken from the existing tiles and theme table).
- Scoreboard caveat added under its dek.
- Theme heading and dek reworded.
- "The cautionary tale" and "The category story" reworded per section 4; the median tooltip's agency sentence removed.
- "fortnightly" removed from the About line, the head descriptions and the JSON-LD description (head and JSON-LD persist across cycles; the About line is in the body).
- Download confirmation no longer promises 5 Oct delivery.
- Secondary review CTA added under the CSV gate.

Not done on the live page (needs the kit, or real data the repo does not have):

- Moving advanced sections lower or into `<details>`, and the scoreboard metric switcher.
- The creative-examples gallery with observation and test per post (needs per-post baselines from the dataset).
- Applying the same changes to `/hair-loss-index` and `/gta-medspa-index` (not touched in this patch).
- Any cycle 004 data.

## 7. Reading levels pass (12 October 2026, second founder review)

Goal: 30 seconds to understand, 2 minutes to compare, then everything else available to verify.

### Persistent (in the page head, survives every cycle, nothing for the kit to emit)

`<style>` and `<script data-ri-reading>` in the head of `/realestate-index`:

- **Section navigator** (`.ri-nav`, sticky): Overview, Rankings, Creative, Insights, Research, Data. Built from section ids; a link appears only when its id exists, and the nav needs at least three.
- **Interactive comparison** (`.ri-cmp`) inserted above the scoreboard table: measure buttons (overall score, followers, posts, median likes, median comments, likes per play, peak plays ÷ followers with "lower is better"), one bar per firm, and a detail panel with that firm's full table row and Instagram link. It reads the scoreboard `<table>` the kit already emits, so **keep the scoreboard column headings exactly**: Account, Score, Followers, Posts, Mix, Median likes, Med comm, Like/play, Peak, Flag, Top post; first cell holds the account link. Renaming a heading drops that measure from the switcher.
- **Larger creative frames**: two columns on desktop, 14px body text.
- **Advanced toggles** style for `details.ri-adv`.

### The kit must emit (body; done by hand for cycle 003)

Section order and ids:

1. Header, status bar (section 2 rules), metrics note.
2. `<section id="ri-overview">` Three findings from this cycle.
3. `<section id="ri-rankings">` The scoreboard (caveat under the dek), then the leader analysis wrapped as `<details class="ri-adv"><summary>What the top of the board is doing</summary>…</details>`.
4. `<section id="ri-creative">` The vision pass, then What good looks like.
5. `<section id="ri-insights">` Content themes, then Format.
6. `<section id="ri-test">` What could be tested next: a two-column table (Observation, Possible test) with the dek "Proposed experiments based on this cycle's observations, not promises of better results." Rows must follow from that cycle's findings.
7. `<section id="ri-advanced">` Advanced research and methodology (heading and dek), followed by each advanced section as its own `<section>` whose content is wrapped in `<details class="ri-adv"><summary>Title</summary>…</details>`: roster change, category pulse, category story, the high-posting account note, creative positioning map, boost ledger, campaign watch, cohort read, outside the category.
8. `<section id="ri-data">` The full post log, then Take the dataset with you (gate and secondary review line), then FAQ, then the footer.

All content stays in the HTML (details are closed, not removed), so search engines and readers who open them get the full research.

### Live now vs still needed

| Item | Status |
|---|---|
| Navigator, interactive comparison, larger frames, toggle style | Live, persistent (head) |
| Section order, ids, details wrappers, "What could be tested next" | Live for cycle 003 only; kit must emit from cycle 004 |
| Carousel or per-post "why it stood out / what to test" creative cards | Not built; needs per-post baselines from the kit's data |
| Same treatment on /hair-loss-index and /gta-medspa-index | Hair Loss done 2026-10-14 (by hand, see Design System note); GTA MedSpa not done |

## 8. Hair Loss Index (12 October 2026, founder review "HMM Hair Loss Index: UX & Content Review")

Same rules and reading levels as sections 1 to 7, applied to `/hair-loss-index` cycle 001 by hand. Data unchanged.

### Persistent (head)

The same `.ri-*` CSS and `data-ri-reading` script as the Real Estate Index, with this page's scoreboard measures: Score, Followers, Posts, Reels, Views / foll, Avg likes, Avg comm. **Keep those column headings exactly.** The navigator adds a Journey link for `#ri-journey`.

### The kit must emit (body)

1. Header (audience line: "For studio and clinic owners who want to see how their category uses Instagram, from first view to a booking enquiry."), status bar per section 2, metrics note.
2. `#ri-overview` Three findings from this cycle (tiles: posts reviewed, brands compared, nearly dormant; three findings each traceable to a stage table).
3. `#ri-rankings` scoreboard with the caveat `pnote` (public activity, not consultations, bookings or revenue; Stories and paid reach can be missed), then the account profiles in `details.ri-adv` with neutral headlines (e.g. "Strong reach, few calls to action", never "The reach engine that forgot to ask").
4. `#ri-journey` "From Instagram attention to a consultation": three tiles (Discover / Build trust / Take action) with the dek that it organises the research and is not a measured booking funnel; then Stage 1, Stage 2 and Stage 3 tables. Stage 3 is an inspection of the public path to booking, not booking performance.
5. `#ri-creative` vision pass (two-column frames), What good looks like.
6. `#ri-insights` themes ("received more engagement in this sample", with the follower-count caveat), Format.
7. `#ri-test` "What could be tested next" (was "What the index says to do"); dek "Proposed experiments … not promises of more bookings"; no claims such as "the entire distance between number two and number one".
8. `#ri-advanced` heading, then in `details.ri-adv`: coverage note, category pulse, category story, large-audience note, the touring competitor, positioning map, boost ledger, campaign watch, cohort read.
9. Method and limits (visible), `#ri-data` post log, dataset gate (no delivery date: "when it is published"), FAQ.

Freshness on cycle 001: last verified data 8 Sep 2026; next scheduled refresh 8 Oct 2026, not yet published. "Living", "Live index" and "every 30 days" removed.

### Wording applied (add to the section 4 table)

| Avoid | Use instead |
|---|---|
| "the metric that predicts a booking" | "comments, the public measure closest to a booking enquiry" |
| "The cause is not the content, it is the last line" | "One likely factor is the last line of the caption" |
| "not luck and not audience love. It is a mechanic" | "line up with a clear mechanic" |
| "books consultations in the comments" | "draws booking requests in public comments" |
| "Buyers in an embarrassing category do not respond to proof…" | "In this sample, frames opening on a person drew more engagement than result reveals" |
| "worth nothing until a caption tells the viewer what to do next" | "reach without a clear next step drew few public replies in this sample" |
| "The cautionary tale / The largest idle audience" | "Large audience, low local reach" |
| "It is an audience problem … The fix is not more posts" | "A likely factor is who the audience is … Something to test" |

### Still needed

Selectable per-competitor profiles driven from the scoreboard (currently the profiles sit in one toggle), a creative carousel with per-post "why it stood out / what to test", and the kit change itself. /gta-medspa-index not yet reviewed.

## 9. GTA MedSpa Index (12 October 2026, founder request, no separate review)

Same rules and reading levels applied to `/gta-medspa-index` cycle 001 by hand. Data unchanged.

### Persistent (head)

Same `.ri-*` CSS and `data-ri-reading` script, adapted: the clinic name is read from the column headed **Clinic** (column 0 is the rank `#`); measures are Score, Median reach, Posts, Followers, Peak reel, Comments / 1k; the box shows the **top 15** of the scoreboard rows for the chosen measure (the scoreboard lists the top 25 of 176 ranked clinics) and says so. Keep those headings exactly.

### The kit must emit (body)

1. Header ("I measured…"), status bar per section 2 (on schedule: last verified data 10 Sep 2026, next scheduled refresh 10 Dec 2026; no cadence line, no "Live index" label), metrics note.
2. `#ri-overview` the existing "What the data says" takeaways card.
3. `#ri-rankings` scoreboard with the caveat `pnote` (public reach and response, not bookings, patients or revenue; paid reach and Stories invisible), then "What the top of the board is doing" in `details.ri-adv`.
4. `#ri-creative` vision pass (two-column frames).
5. `#ri-insights` themes ("received more reach in this sample"), Format, Posting more does almost nothing, The gap, Where your clinic sits, the compliance ledger (heading "Many clinics post content Canadian regulators could question"; keep "could question", never "do not allow" as a blanket claim about the market).
6. `#ri-test` What the index says to do.
7. `#ri-advanced` heading, then in `details.ri-adv`: coverage note, category pulse, creative positioning map, collaborator ledger.
8. Method and limits, `#ri-data` post log (FAQ sits in the same block), dataset gate ("when it is published"), and a closing card: "Want a second opinion?" with the free marketing review (`/contact?intent=review#contact-form`), stating it is not a full competitor study or a compliance review. The old card offered a personal ranking report via "Need Help? Let's Talk"; that offer is retired.

### Wording applied

"We measured / We expected / We tested / We read / We are not claiming" in first person singular; "paying for an account nobody is watching" became "has an account with little or no recent video" and "posted little or no video in the window". Quoted clinic captions in the post log are verbatim and stay as they are.
