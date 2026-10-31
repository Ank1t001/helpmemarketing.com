# Section-by-section review, /business-spend-index

Started 31 October 2026 at the founder's request: one section at a time, decisions recorded here, then one final brief once every section has been reviewed. Nothing in this file is applied to the page until the final brief is approved. Each decision says what changes, what stays and why.

Sections in review order: Overview, Social Media Strategy, Paid Social Strategy, Website Messaging, Product Comparison, Customer Journey, Lessons, Sources & evidence, then sitewide spacing.

## 1. Overview (decided 31 October 2026)

Keep:
- The heading "Inside this case study".
- Six cards with simple line icons, each a link to its tab, in a 3 x 2 grid (2 columns at tablet, 1 on mobile).
- Social Media Strategy and Paid Social Strategy as separate cards and tabs.
- One small "Sources & evidence" link below the tab bar.

Change:

| Element | Now | Final brief |
|---|---|---|
| Social Media Strategy card description | How brands position themselves, what they post and the response they receive. | How brands position themselves, vary their creatives and engage their audience. |
| Customer Journey card description | What happens after clicking and which steps are explained. | How brands guide customers from their website to getting started. |
| Note below the cards (`div.bs-ov-scope`: "Independent marketing research from dated public sources. Not a product recommendation." and the dates line) | Shown | Removed (founder, 31 October 2026, reversing the earlier "keep research dates and independence statement" in the same review) |

Open, to settle in the final brief:
- **"Not a product recommendation" has no other place on the page.** Every date in the removed note is still shown in its own section (Instagram window in Social Media Strategy, 23 October in Website Messaging and Compare, the Airwallex follow-up in Compare, all of them in Sources & evidence), and the relationship disclosure is in Sources & evidence. The "not a product recommendation" line appears only in the note being removed. Options: (a) add it to the hero byline line; (b) put it at the top of Sources & evidence beside the relationship disclosure; (c) drop it. Recommendation: (a), a few words in the hero keep it visible to readers comparing providers.
- The paid social review period (Meta Ad Library, active ads collected 30 October 2026) is not in any Overview note; decide when reviewing Paid Social Strategy whether it needs a place outside that tab.
- The Social Media Strategy description now promises "vary their creatives". The section can show format mix (reels, carousels, images) for Venn and Airwallex, but creative approach is established only for posts whose full creative was inspected (2 of 9 Venn, 9 of 23 Airwallex: the reels were not watched). Settle in the Social Media Strategy review whether the section supports the new wording as it stands.

Findings, rankings and detailed comparisons stay in their own sections; the Overview stays a short visual guide.

## 2. Social Media Strategy (in review)

Audit of the current view, 31 October 2026 (local build of `f13a8cf`):

- Length: about 6,500px at 1280px wide and 12,100px at 390px, the longest view on the page.
- Brand positioning and Product positioning list all six brands. Four rows in each say "No in-window posts" or "Not assessed" (Float, Ramp, Loop, Keep). On phones each becomes its own card, so eight of the twelve cards carry no reading.
- The scope note is three paragraphs at body size above the first subsection.
- Creative strategy: two columns (Venn, Airwallex); the shorter Venn column leaves an empty area beside Airwallex's longer list.
- "Selected posts" sits inside Creative strategy as an unnumbered heading, about 2,000px long. The two text-only Venn cards span the full width with text limited to about 680px, leaving the right half empty.
- Engagement by theme: the tables touch the paragraph after them (0px gap) and sit 8px under the brand name; the theme column is 11.5px bold while every other table's first column is 13.5px regular. Five caveat bullets follow.
- What this suggests uses "What I observed"; Lessons uses "What I noticed".

## Sitewide spacing and padding (collected across sections)

Measured on the local build at 1280px and 390px, 31 October 2026:

- Consistent: section top padding (24px), H2 size and gap to the first block (24px), gaps between top-level blocks (32px desktop, 24px mobile) in Social, Paid, Journeys.
- Inconsistent:
  - H3 bottom margin 8px (Social, Paid, Messaging) vs 12px (Compare, Journeys); H3 top margin 8px in Messaging and Lessons, 0 elsewhere.
  - Product Comparison keeps 32px gaps on phones (others drop to 24px) and uses 12px and 16px gaps between its intro lines.
  - Lessons' block starts 16px after the heading; other views use 24px.
  - Card padding: Overview cards 20px all round; example cards 24px (24/16 on phones).
  - Tables sit flush against the text after them in Engagement by theme.
- Proposed scale for the final brief: block gap 32px desktop / 24px phone; subsection heading to content 12px; table or card to following text 16px; card padding 24px desktop / 20px phone for every card type; one first-column style for all tables.
