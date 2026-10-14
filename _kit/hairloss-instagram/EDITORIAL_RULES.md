# Hair Loss Index: editorial and layout rules (14 October 2026)

There is no build kit for this index yet. `/hair-loss-index` edition 001, as revised on 14 October 2026, is the approved body; edition 002 keeps its structure and wording and updates figures from the new collection. The Real Estate kit (`_kit/realestate-instagram`) is the model for building one: tokenised `report_body.html`, `site_shell.html`, a `build_v2.py` that validates these rules, and a snapshot per edition.

## Structure (in this order)
1. Header: kicker "The HMM Index · Instagram"; H1 "The Hair Loss Index"; lede; byline "Last 90 days ending {date}" · "For studio and clinic owners and marketing leads." · "Research and analysis by Ankit Kumar (link /about) · Founder, HMM (link /)". Date bar: "Last verified data" and "Next scheduled refresh" in long dates, ", not yet published" when overdue; no cycle number.
2. `#ri-overview` "What stood out in the last 90 days": three tiles, a "Brands included" line, one card with three titled findings that name the brands, the italic sample caveat.
3. Metrics note: "Tap or hover over underlined metrics for a definition. Open the linked posts to see the evidence."
4. `#ri-rankings` "The scoreboard": intro, "Which brand leads this edition?", the comparison card (head script), "View all metrics", "How the rankings work". Ranked brands first ("#N of M ranked"), then brands with fewer than five posts ("Not ranked"). Every row carries a `data-note`.
5. `#ri-journey` "From Instagram attention to a consultation": three tiles, then Stage 1, 2 and 3 in expanders. Stage 3 inspects the public path to booking; it never claims booking performance.
6. `#ri-creative` "The top post from each brand": cards ordered by likes, "Top post" badge, likes and times the brand's median likes, one observation, "View post"; frame reads under "Read the analysis".
7. "How to read the numbers": plays per follower (grey `bandbar neutral`), comments per post, comment to like ratio; reads under "Read this edition against the benchmarks".
8. `#ri-insights` "Which content themes stood out?" (Content theme, Posts analysed, Median likes, Key observation), then "How did post formats compare?".
9. `#ri-test` "What could be tested next" (Observation, Possible test).
10. `#ri-download` "Download the dataset" (label, `role="status"` message, privacy link, review invite; GATE_SOURCE `hair-loss-cycle-NNN`, which the forms script parses).
11. `#ri-advanced` "Research and methodology": About the researcher, Cite this research, then expanders: How this research was produced, Brand summaries, Coverage and corrections, `#ri-editions` Edition history, Category pulse, Plays comments and the booking ask, Large audience low local reach, the touring competitor, Plays and comments comparison, Video plays and advertising context, Observed content series and active ads, Compare the three brand groups.
12. `#ri-data` post log inside "Open the post log", FAQ, short footer.

Exact scoreboard headings (the head script reads them): Account, Score, Followers, Posts, Reels, Plays / foll, Avg likes, Avg comm, Flag, Top post.

## Wording
- This sample, edition (not cycle), %, 90-day. Recorded plays, never reach or views. Most liked, never best or winning. Above or below account median.
- Comments are a public signal, never bookings or intent. A DM ask "lines up with" comments; it is not shown to cause them.
- Flags neutral only: Above 1x, 0.25 to 1x, Below 0.25x, Fewer than 5 posts, No posts, N.NNx plays/followers, N ads found.
- Observation, Possible interpretation, Suggested test. Caption excerpts, never verbatim. No em or en dashes.
- State facts that the post log supports; when a claim cannot be checked against it, drop it or label it a possible interpretation.

## Metadata and snapshots
No `datePublished`. `dateModified` is the recorded production deployment time of the last content change (ISO 8601 with timezone). Article image `/assets/index/hair-loss/og.jpg`. Each edition gets `/hair-loss-index/edition-NNN` (self canonical, one `noindex, follow`, not in the sitemap); never rewrite a published snapshot's research content.
