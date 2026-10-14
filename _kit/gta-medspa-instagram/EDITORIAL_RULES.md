# GTA MedSpa Index: editorial and layout rules (14 October 2026)

The kit in this folder and ROUTINE_PROMPT.md run the monthly refresh (see README.md). `/gta-medspa-index` edition 001, as revised on 14 October 2026, is the approved body. A refresh keeps its structure and wording and replaces figures with the new collection's.

## Structure (in this order)
1. Header: kicker "The HMM Index · Instagram"; H1 "The GTA MedSpa Index"; lede; byline "Last 90 days ending {date}" · "For clinic owners and marketing leads." · "Research and analysis by Ankit Kumar (link /about) · Founder, HMM (link /)". Date bar: "Last verified data" and "Next scheduled refresh" in long dates, ", not yet published" when overdue; no cycle number.
2. `#ri-overview` "What stood out in the last 90 days": tiles (Clinics ranked, Posts analysed, Median plays per reel), the "Clinics included" line, one card with three titled findings, the italic sample caveat.
3. Metrics note.
4. `#ri-rankings` "The scoreboard": intro, "Which clinic leads this edition?", comparison card (head script, top 15 of the scoreboard for the chosen measure), "View all metrics" (top 25 table, every row with a `data-note`), "How the rankings work".
5. `#ri-creative` "The top reel from eight leading clinics": "Top reel" badges, plays and times followers, one observation, "View post"; frame reads under "Read the analysis".
6. "How to read the numbers" (histogram, four tiers), "How plays differ by region".
7. `#ri-insights` "Which content themes stood out?", "How did post formats compare?", "Did posting more line up with more plays?" (quadrant, analysis and caveat in an expander).
8. "Many clinics post content Canadian regulators could question" (aggregate shares only, never a named clinic; "could question", never "not permitted" as a verdict on a clinic; "not legal advice").
9. `#ri-test` (Observation, Possible test), `#ri-download`, `#ri-advanced` (researcher, citation, How this research was produced, What the top 25 have in common, Coverage and corrections, `#ri-editions`, Category pulse, Video share and comments comparison, Co-authored posts on clinic feeds), `#ri-data` post log in "Open the post log", FAQ (FAQPage JSON-LD built from the visible questions), footer with the clinic-name and regulatory disclaimers.

Exact scoreboard headings (the head script reads them): #, Clinic, Area, Score, Median plays, Posts, Pattern, Followers, Peak reel, Comments / 1k, Mix.

## Wording
- Recorded plays, never reach as a measured result ("Reach" survives only as the score pillar's name). Edition, not cycle. % not percent. This sample. Most played, never best.
- Comments are a public signal, never bookings. Regulatory text describes captions that match a pattern; it never says a clinic broke a rule.
- No dashes for missing values: "no video" or a blank cell. No em or en dashes anywhere.
- Name exceptions on the same board; when two collections disagree, say so beside the figure.

## Metadata and snapshots
Article (not Report) with author and publisher `@id`, image `/assets/index/gta-medspa/og.jpg`, no `datePublished`, `dateModified` from the recorded production deployment of the last content change. The Dataset block carries edition figures and is updated with each edition. Snapshots at `/gta-medspa-index/edition-NNN` (self canonical, one `noindex, follow`, not in the sitemap, never rewritten).
