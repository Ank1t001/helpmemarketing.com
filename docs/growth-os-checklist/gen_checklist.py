# Generates docs/growth-os-checklist/seo-growth-os-checklist.html (capability guide, 2026-11-11).
import html
SCHED, DRAFT, MAN = ('Scheduled check','t-rep'), ('Automated draft + human review','t-evt'), ('Manual review','t-man')
AREAS = [
 ('1. Website health','Is the website reachable, working and easy for search engines to read?','Technical SEO, Sitemaps and Discovery, Page Performance, Structured Data', [
  ('Crawl and indexing checks', SCHED,
   'Broken URLs, redirect chains, robots directives, noindex tags, canonical URLs and sitemap inclusion.',
   'Repeat the configured URL checks and compare the results with the previous run.',
   'The affected URLs, the issue found on each and a recommended next action.',
   'Which fixes to make, and when.',
   'Your public website; Search Console for Google’s view of indexing.'),
  ('Page speed monitoring', SCHED,
   'Lab performance tests on key pages, plus real-visitor speed data where Google has enough of it.',
   'Retest the agreed pages and compare with earlier results.',
   'Pages that slowed down or improved, with the figures and the likely causes to look at.',
   'Whether a fix is worth the development time.',
   'Your public website; Google’s field data where available.'),
  ('Structured data checks', DRAFT,
   'Whether page markup is valid, free of errors and suited to the page.',
   'Validate markup on a schedule and draft new or corrected markup.',
   'The errors found and draft markup for the pages that need it.',
   'That the details are accurate; your developer adds and tests the markup.',
   'Your public website.'),
  ('Key journeys and forms', MAN,
   'Whether enquiry or booking journeys work on phones and desktops.',
   'Page availability can be rechecked; the journey itself is reviewed by a person.',
   'The steps that failed or caused confusion, with notes on each.',
   'Test submissions happen only with your permission.',
   'Your public website.'),
 ]),
 ('2. Search performance','Which pages and searches bring visibility and visits, and how is that changing?','Search Console Analysis, Local Search, Competitor Research', [
  ('Search performance monitoring', SCHED,
   'Page and query impressions, clicks, click-through rate and average position across comparable periods, with country filters.',
   'Collect connected search data, compare periods and flag changes for investigation.',
   'A shortlist of pages gaining or losing visibility, with the supporting figures.',
   'Which changes are worth investigating.',
   'Access to Google Search Console.'),
  ('Local visibility tracking', SCHED,
   'Business Profile details and categories, and where you appear for searches in specific locations.',
   'Repeat location-specific observations where a suitable tracking tool is set up.',
   'Dated observations by location, plus gaps in your profile.',
   'Profile changes before they are made.',
   'Your Google Business Profile; a location tracking tool where required, which may have its own cost.'),
  ('Competitor and opportunity research', MAN,
   'Which competitor pages appear for your topics, and where the gaps are.',
   'Collect search data for the agreed topics.',
   'A short list of opportunities, with the evidence behind each.',
   'Which opportunities fit your business.',
   'Third-party search data, which may have its own cost.'),
 ]),
 ('3. Content','Do your pages explain what you offer and answer the questions customers ask?','Content Review, Internal Linking, On-page SEO', [
  ('Content opportunity review', DRAFT,
   'Pages receiving impressions but few clicks, unanswered customer questions and possible overlap between pages.',
   'Identify candidates from the available data and prepare draft recommendations.',
   'A page-specific brief covering what to change and why.',
   'The brief, and any wording, before it is used.',
   'Your public website; Search Console for impressions and clicks.'),
  ('Internal linking review', DRAFT,
   'Links pointing to your priority pages, the wording of those links and relevant places to add new ones.',
   'Inspect crawlable links and prepare suggested additions.',
   'The source page, destination page and suggested link wording, for approval.',
   'Each suggested link before it is added.',
   'Your public website.'),
  ('Page basics', SCHED,
   'Missing, duplicated or unclear titles, descriptions and headings on important pages.',
   'Recheck the agreed pages and flag new problems.',
   'A list of pages with the issue and a suggested fix.',
   'The final wording.',
   'Your public website.'),
 ]),
 ('4. AI visibility','Can AI tools understand your pages, and does your business appear for the questions that matter?','AI Search Visibility, Answer Readiness', [
  ('AI visibility tracking', SCHED,
   'Whether selected AI answers mention your business, cite your pages or describe your services accurately.',
   'Repeat supported checks and keep dated observations; other platforms need browser or manual review.',
   'For each check: the question, platform, date, observed answer and any citation.',
   'Whether an answer is accurate, and what to do about it.',
   'An agreed question list and access to the selected AI tools; some tools may have their own cost.'),
  ('Answer readiness review', MAN,
   'Whether key pages give clear, direct answers that AI tools can understand and cite.',
   'Draft suggestions can be prepared; the judgement is made by a person.',
   'Page-by-page notes and suggested edits.',
   'Every edit before it is published.',
   'Your public website and your knowledge of the business.'),
 ]),
 ('5. Measurement','Can the figures be trusted before anyone draws conclusions from them?','Measurement Review', [
  ('Lead measurement review', DRAFT,
   'Whether recorded lead events correspond to real enquiries, whether test activity is included, and where evidence is missing.',
   'Collect the available figures and flag discrepancies for review.',
   'A clear explanation of which figures can support decisions and what needs checking.',
   'Which actions count as a result, and any change to tracking.',
   'Google Analytics and Tag Manager access; CRM or booking records with your permission.'),
 ]),
 ('6. Progress','What changed, what is still open, and what needs your approval?','Change Monitoring, Reporting', [
  ('Change verification', SCHED,
   'Whether an approved edit is live and meets its acceptance checks.',
   'Recheck observable page changes and update their status.',
   'A record showing each change as live, partly live, not yet live or unable to verify.',
   'Anything that could not be verified.',
   'Your public website and any connected data.'),
  ('Change record and summaries', DRAFT,
   'What was found, recommended, approved and changed, and what remains open.',
   'Keep a dated record and prepare a recurring summary.',
   'A short summary of what changed, what is unresolved and what needs your approval.',
   'The summary before it is shared with anyone else.',
   'Built from each run.'),
 ]),
]
e = lambda s: html.escape(s, quote=False).replace('’', '&rsquo;')
def card(c):
    name,(lab,cls),chk,auto,recv,rev,needs = c
    return f'''<div class="cap">
  <div class="cap-h"><h3>{e(name)}</h3><span class="tag {cls}">{lab}</span></div>
  <div class="cap-g">
    <div><p class="k">What it checks</p><p>{e(chk)}</p></div>
    <div><p class="k">What can run automatically</p><p>{e(auto)}</p></div>
    <div><p class="k">What you receive</p><p>{e(recv)}</p></div>
    <div><p class="k">What needs your review</p><p>{e(rev)}</p></div>
  </div>
  <p class="needs"><b>Needs:</b> {e(needs)}</p>
</div>'''
areas = ''.join(f'''<section class="area">
<h3 class="area-h">{t}</h3>
<p class="sec-sub">{s}</p>
{''.join(card(c) for c in caps)}
<p class="draws">Related specialist capabilities: {e(d)}.</p>
</section>
''' for t,s,d,caps in AREAS)
n = sum(len(a[3]) for a in AREAS)
doc = f'''<!doctype html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SEO Growth OS Checklist</title>
<!-- Source for the emailed checklist PDF (2026-11-11, capability guide). Generated by gen_checklist.py;
     render with docs/growth-os-checklist/build_pdf.mjs. Plain language, Canadian spelling, no em dashes. -->
<style>
  :root {{ --ink: #121212; --body: #3a3a3a; --muted: #6b6b6b; --line: #e4e1da; --tint: #f6f4ef; --orange: #c2410c; --mint: #007a62; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: Inter, "Helvetica Neue", Arial, sans-serif; font-size: 10.5pt; line-height: 1.5; color: var(--body); background: #fff; }}
  .page {{ max-width: 7.2in; margin: 0 auto; }}
  h1 {{ margin: 0; font-family: Georgia, "Times New Roman", serif; font-weight: 500; font-size: 26pt; line-height: 1.15; color: var(--ink); }}
  h1 em {{ color: var(--orange); }}
  h2 {{ margin: 28px 0 6px; font-family: Georgia, "Times New Roman", serif; font-weight: 500; font-size: 17pt; color: var(--ink); break-after: avoid; }}
  .kicker {{ margin: 0 0 10px; font-size: 8.5pt; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }}
  .lead {{ margin: 10px 0 0; font-size: 11.5pt; color: var(--ink); }}
  .note {{ margin: 12px 0 0; padding: 10px 14px; border-left: 3px solid var(--orange); background: var(--tint); }}
  .note2 {{ border-left-color: var(--muted); }}
  .sec-sub {{ margin: 0 0 8px; color: var(--muted); break-after: avoid; }}
  .tag {{ display: inline-block; padding: 1px 8px; border-radius: 99px; font-size: 8pt; font-weight: 600; white-space: nowrap; }}
  .t-rep {{ background: #e3f1ec; color: var(--mint); }}
  .t-man {{ background: #f3ece4; color: #8a4b12; }}
  .t-evt {{ background: #ecebf3; color: #43407a; }}
  .legend {{ margin: 14px 0 0; padding: 0; list-style: none; font-size: 9.5pt; }}
  .legend li {{ margin: 5px 0; }}
  .legend .tag {{ margin-right: 6px; }}
  ul.plain {{ margin: 6px 0 0; padding-left: 18px; }}
  ul.plain li {{ margin: 4px 0; }}
  .area {{ margin-top: 18px; }}
  .area-h {{ margin: 22px 0 2px; font-family: Georgia, "Times New Roman", serif; font-weight: 500; font-size: 14pt; color: var(--ink); break-after: avoid; }}
  .cap {{ margin-top: 10px; padding: 12px 14px; border: 1px solid var(--line); border-radius: 10px; break-inside: avoid; page-break-inside: avoid; }}
  .cap-h {{ display: flex; justify-content: space-between; align-items: baseline; gap: 10px; }}
  .cap-h h3 {{ margin: 0; font-size: 11pt; color: var(--ink); }}
  .cap-g {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px 18px; margin-top: 8px; }}
  .cap-g p {{ margin: 0; font-size: 9.5pt; }}
  .cap-g p.k {{ font-size: 7.5pt; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); font-weight: 600; margin-bottom: 1px; }}
  .needs {{ margin: 8px 0 0; padding-top: 6px; border-top: 1px solid var(--line); font-size: 9pt; color: var(--muted); }}
  .needs b {{ color: var(--body); }}
  .draws {{ margin: 8px 0 0; font-size: 8.5pt; color: var(--muted); }}
  .grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
  .box {{ padding: 12px 14px; background: var(--tint); border-radius: 10px; break-inside: avoid; }}
  .box h3 {{ margin: 0 0 4px; font-size: 11pt; color: var(--ink); }}
  .example {{ padding: 14px 16px; border: 1px solid var(--line); border-left: 3px solid var(--mint); border-radius: 0 10px 10px 0; break-inside: avoid; }}
  .example dl {{ margin: 8px 0 0; }}
  .example dt {{ font-size: 7.5pt; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); font-weight: 600; margin-top: 8px; }}
  .example dd {{ margin: 2px 0 0; }}
  .keep {{ break-inside: avoid; page-break-inside: avoid; }}
  .cta {{ margin-top: 16px; padding: 14px 16px; background: var(--tint); border-radius: 10px; }}
  .cta b {{ color: var(--ink); }}
  .foot {{ margin-top: 22px; padding-top: 10px; border-top: 1px solid var(--line); font-size: 9pt; color: var(--muted); }}
  a {{ color: var(--orange); }}
  .pb {{ break-before: page; page-break-before: always; }}
</style>
</head>
<body>
<div class="page">

<p class="kicker">HelpMeMarketing &middot; SEO Growth OS</p>
<h1>The SEO Growth OS <em>checklist</em></h1>
<p class="lead">The recurring SEO work I can help automate, the decisions it supports and the output you receive.</p>

<p class="note"><b>This is a guide, not an audit.</b> Requesting it does not run anything on your website. Website changes are always reviewed and approved by you before anything goes live.</p>
<p class="note note2">This checklist describes what SEO Growth OS is designed to cover. The capability names describe the work; they are not a claim that every workflow is already configured for your site. Available checks and automation are confirmed during setup.</p>

<h2>What it can take off your weekly task list</h2>
<ul class="plain">
  <li>Checking Search Console for pages gaining or losing visibility, and why.</li>
  <li>Rechecking broken links, redirects and indexing after changes to your site.</li>
  <li>Spotting pages that are seen in search but rarely clicked.</li>
  <li>Drafting page briefs and internal link suggestions for your approval.</li>
  <li>Checking whether selected AI answers mention or cite your business.</li>
  <li>Keeping a dated record of what changed, and whether it is live.</li>
</ul>

<p class="k-legend"><b>How each capability runs</b></p>
<ul class="legend">
  <li><span class="tag t-rep">Scheduled check</span> runs again on a schedule once the required tools, access and schedule are configured and tested.</li>
  <li><span class="tag t-evt">Automated draft + human review</span> the system prepares findings or drafts; a person reviews them before anything is used.</li>
  <li><span class="tag t-man">Manual review</span> needs a person to judge, with the system organising the evidence.</li>
</ul>

<h2>Specific checks and automations</h2>
<p class="sec-sub">{n} capabilities in six areas. Each shows what it checks, what can run automatically after setup, what you receive and what needs your review.</p>
{areas}

<section class="keep">
<h2>What a completed run gives you</h2>
<div class="grid2">
  <div class="box"><h3>Findings</h3><p>Issues grouped as broken, missing or underperforming, with shared causes combined into one finding.</p></div>
  <div class="box"><h3>Priorities</h3><p>Each recommendation weighed on severity, opportunity, strength of evidence, risk and effort, without one combined score.</p></div>
  <div class="box"><h3>Draft briefs and changes</h3><p>Page briefs, link suggestions and draft markup, ready for your approval, each with a way to check it was done.</p></div>
  <div class="box"><h3>A change record</h3><p>What was approved, what is live, and what could not be checked. Missing evidence is listed, never estimated.</p></div>
</div>
</section>

<section class="keep">
<h2>A real example from HelpMeMarketing</h2>
<div class="example">
  <p><b>From finding to a ready-to-use brief.</b> A run on my own website, November 2026.</p>
  <dl>
    <dt>What the run found</dt>
    <dd>SEO Growth OS identified a commercial page with limited search visibility, checked its indexing status and reviewed its internal links.</dd>
    <dt>What it prepared</dt>
    <dd>A brief identifying the pages to edit and the proposed link wording.</dd>
    <dt>What happened next</dt>
    <dd>The change required approval. Once approved, links were added from two related pages and went live on 10 November 2026. Implementation verification and search impact were tracked separately.</dd>
  </dl>
  <p class="draws">This shows the process on my own site. It is not a client result or proof of a ranking change.</p>
</div>
</section>

<section class="keep">
<h2>What setup requires</h2>
<ul class="plain">
  <li>Access to the data sources you want included, such as Search Console, Google Analytics, Tag Manager or your Business Profile.</li>
  <li>An agreed list of checks, pages and, for AI visibility, the questions to track.</li>
  <li>A schedule, and a test run to confirm each check works before it is relied on.</li>
  <li>Any third-party tools the chosen checks need; some have their own cost.</li>
  <li>Your approval before any website change goes live.</li>
</ul>
<div class="grid2">
  <div><h3 class="area-h">What it does not do</h3>
  <ul class="plain"><li>Promise rankings, traffic or AI citations.</li><li>Publish website changes without your approval.</li><li>Run without setup and the access each check needs.</li><li>Fill gaps with estimates when data is not available.</li></ul></div>
  <div class="cta"><b>Want this set up for your business?</b> I can help connect your data, configure the checks and set a schedule around your website and goals. Enquire at <a href="https://helpmemarketing.com/contact">helpmemarketing.com/contact</a>.</div>
</div>
</section>

<p class="foot">SEO Growth OS checklist &middot; HelpMeMarketing &middot; Ankit Kumar, Halton Hills, Ontario &middot; November 2026.</p>
</div>
</body>
</html>
'''
open('/home/user/helpmemarketing.com/docs/growth-os-checklist/seo-growth-os-checklist.html','w').write(doc)
print(n,'capabilities')
