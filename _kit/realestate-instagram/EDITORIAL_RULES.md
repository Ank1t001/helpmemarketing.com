# Real Estate Index: editorial and layout rules (founder-approved 13 October 2026)

`report_body.html` is the live, approved body. Each refresh updates its figures and editorial text from the new cycle's evidence and keeps everything below. `build_v2.py` fails on most of these; the rest are review checks.

## Structure (in this order)
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
Every expander is a bordered card, 24px inset (16px at 720), content 20px below the summary, 12px between stacked cards. Boxes use a 24px inset (16px sides at 720). 48px between sections (32px at 720). Grids use `minmax(min(…, 100%), 1fr)` so nothing overflows an expander on phones.

## Metadata and snapshots
`dateModified` = `ig_cycle.json` `modified_at`, the recorded production deployment time of the last content change (ISO 8601 with timezone). No `datePublished`. Article image `/assets/index/real-estate/og.jpg`. Publish `output/edition-NNN.html` as `realestate-index/edition-NNN.html` (self canonical, one `noindex, follow`); never regenerate an earlier snapshot; record any later fix to one in its head comment and add a visible dated note when visible text is corrected.
