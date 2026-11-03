# Real Estate Index: editorial and layout rules (founder-approved 13 October 2026)

`report_body.html` is the live, approved body. Each refresh updates its figures and editorial text from the new cycle's evidence and keeps everything below. `build_v2.py` fails on most of these; the rest are review checks.

## Views (founder, 2026-11-02)
After the header and date bar, one tab bar over seven views since the same day's comparison (`nav.ri-tabs[data-ri-tabs]`, plain jump links in the HTML; the head script `data-ri-tabs-js` turns them into tabs) over six views, each a `div.ri-view`, in this order. Every view stays in the HTML, so search engines, readers without JavaScript and print see the whole report. `build_v2.py` checks the bar, the order and which sections sit in which view. No content is removed by the views; the numbered list below describes each block, and this list says where it sits.
- `#ri-view-overview` Overview: `#ri-overview` (item 2), `#ri-pulse` Category pulse (shown open), `#ri-guide` "Inside this edition" (one card per view).
- `#ri-view-rankings` Rankings: the metrics note (3), `#ri-rankings` (4), How to read the numbers (6), then expanders Compare the two firm groups, Firm summaries, Outside the category, for scale.
- `#ri-view-website` Website Messaging (added 2026-11-02): `#ri-website`, rendered by `strategy/render.py`.
- `#ri-view-organic` Organic Social: `#ri-creative` (5), `#ri-video` Video metrics comparison (shown open, never an expander), `#ri-insights` (7), formats (8), `#ri-series` Observed content series (the organic rows), then the Equiton expander.
- `#ri-view-paid` Paid Social: `#ri-activity` Company posts and advertising activity, `#ri-distribution` Video distribution and advertising context (both shown open), `#ri-ads` Active ads found in the Meta Ad Library (the rows whose Signal says paid, the ad count note and the closing line).
- `#ri-view-recs` Recommendations: `#ri-test` (9).
- `#ri-view-sources` Sources & evidence: `#ri-download` (10), `#ri-advanced` with its cards (11), the expanders How this research was produced, Coverage, `#ri-editions` Edition history, then `#ri-data` (12).
- FAQ and the report footer sit below the views (13).
- Five-firm strategy comparison (founder, 2026-11-02): `#ri-organic-compare` opens Organic Social, `#ri-paid-compare` opens Paid Social, `#ri-recs-firms` follows `#ri-test`, and a roster note sits on the Overview, all rendered by `strategy/render.py` between `<!-- STRATEGY:* -->` markers (see `strategy/README.md`). They compare the roster from edition 006: Equiton, Skyline, Lankin Investments, Greybrook Realty Partners, Centurion Asset Management. Which views are email-gated is still to be decided by the founder.
- Roster (founder, 2026-11-02, applied the same day as a revision of edition 005, every account re-collected for the same window): Equiton, Skyline, Lankin, Greybrook (@greybrook, cohort DEV) and Centurion; Pier 4 and McGillivray Capital left the board. The same five firms appear in every section. Hidden like counts are None in the data and left out of like-based figures, never counted as zero. The edition 005 snapshot keeps the first publication. Centurion had no corporate Instagram account that could be found on 2 November 2026, so it cannot be scored unless one is found; say so on the page, never invent an account.

## Blocks (descriptions; positions are set by the views above)
1. Header: kicker "The HMM Index · Instagram"; H1 "The Real Estate Index"; the lede; byline row "Last {N} days ending {window end}" (tokens `{{WINDOW_DAYS}}` and `{{WINDOW_END_LONG}}`) · "For business owners and marketing leads." · "Research and analysis by Ankit Kumar (link /about) · Founder, HMM (link /)". Date bar: "Last verified data" and "Next scheduled refresh" in long dates ("13 October 2026"); no cycle number.
2. `#ri-overview` "What stood out in the last {N} days": three tiles (Posts analysed, Comments recorded, Firms running Meta ads), a "Firms included" line, one card with three titled findings that name the firms, and the italic sample caveat.
3. One-line metrics note: "Tap or hover over underlined metrics for a definition. Open the linked posts to see the evidence."
4. `#ri-rankings` "The scoreboard": intro, "Which firm leads this edition?" answer with its limitation, the comparison card (built by the head script from the table), then expanders "View all metrics" (the table, exact headings below) and "How the rankings work" (firm summaries live in Research, not here). Every scoreboard `<tr>` carries a plain-sentence `data-note`.
5. `#ri-creative` "The top post from each firm": cards ordered by likes, "Top post" badge, likes and "times the firm's median likes", one observation, "View post"; frame reads and tests under "Read the analysis".
6. "How to read the numbers": three band cards (engagement rate, comment to like ratio, peak plays ÷ followers with the grey `bandbar neutral`), reads under "Read this edition against the benchmarks".
7. `#ri-insights` "Which content themes stood out?": four-column table, one caveat line, "Explore the theme analysis".
8. "How did post formats compare?": three format cards, one sentence, "Read the format analysis".
9. `#ri-test` "What could be tested next".
10. `#ri-download` "Download the dataset": visible "Email address" label, `role="status" aria-live="polite"` message, privacy link, the review invite.
11. `#ri-advanced` "Research and methodology": "About the researcher" and "Cite this research" cards, then expanders: How this research was produced, Firm summaries (all five firms), Coverage, previous-edition comparison and correction, `#ri-editions` Edition history (add this edition's row as "(this page)"), and the evidence sections.
12. `#ri-data` "The full post log" inside "Open the post log" (caption excerpts, "View post" links, filters).
13. FAQ, then the report footer with the short "About this index" and the methodology link.

Exact scoreboard headings (the head script reads them): Account, Score, Followers, Posts, Mix, Median likes, Med comm, Like/play, Peak, Flag, Top post.

## Wording
- This sample, never the whole category. Edition, not cycle, in visitor text. % not "percent". "{N}-day", "90-day", "{N} days", where N is the window length (`{{WINDOW_DAYS}}` in report_body.html, never typed; edition 005 printed 30). Window rule from edition 006 (founder, 2026-10-16): the 14th of the previous month to the 13th of the collection month, both included, Toronto time, so editions follow on without gaps or overlaps (28 to 31 days).
- Post with the most likes, never best-performing or winning. Above or below account median, never working, landed or not landing.
- Recorded plays, never reach. Peak plays ÷ followers bands are numeric (below 10x, 10 to 50x, above 50x); plays can include repeats and do not show unique viewers or paid distribution.
- Active ads found, never spend. Public post metrics do not separate paid and organic engagement.
- Median of firm-level rates, never pooled median. Comments are not investor intent.
- Flags use the neutral style only: Below 10x, N.Nx plays/followers, No video, Fewer than 5 posts, N ads found. No BOOST, PUSH or ORGANIC.
- Distribution (formerly "Distribution honesty"); no "honest end". Benchmark labels: lower band, middle band, upper band, lower comment ratio, index target band, review the comment pattern.
- Observation, Possible interpretation, Suggested test. Caption excerpts, never verbatim. No em or en dashes.
- Edition 004 is "the scoreboard dated 5 October 2026"; its publication on this website has not been verified.

## Layout (head styles in `site_shell.html`; keep them)
Every expander is a bordered card, 24px inset (16px at 720), content 20px below the summary, 12px between stacked cards. Boxes use a 24px inset (16px sides at 720). 48px between sections (32px at 720). Grids use `minmax(min(…, 100%), 1fr)` so nothing overflows an expander on phones. Polish pass (founder, 2026-11-02): the section menu sticks at 92px, below the 83px site header; the top posts sit three to a row (two at 1000px, one at 560px) with a short last row centred, and the firm name and post label below the image, not over it; 12px between the Research cards and the first expander, 48px above the post log; the dataset email field uses the page background; links in `.pnote` are orange and underlined.

## Metadata and snapshots
`dateModified` = `ig_cycle.json` `modified_at`, the recorded production deployment time of the last content change (ISO 8601 with timezone). No `datePublished`. Article image `/assets/index/real-estate/og.jpg`. Publish `output/edition-NNN.html` as `realestate-index/edition-NNN.html` (self canonical, one `noindex, follow`); never regenerate an earlier snapshot; record any later fix to one in its head comment and add a visible dated note when visible text is corrected.
