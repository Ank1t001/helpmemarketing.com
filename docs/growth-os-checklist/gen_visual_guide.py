#!/usr/bin/env python3
"""Generates seo-growth-os-visual-guide.html: the SEO Growth OS Visual Guide, 5 fixed US Letter pages in HMM colours.

Page 1: where to start (problem table, six areas, label legend, scope note).
Pages 2 to 4: grouped cards, each with Checks, Automates (or Review for human work) and You receive.
Page 5: how a run works, the 10 November 2026 process example, what you receive, setup and the enquiry link.
Edit the lists below, never the HTML, then render:
  python3 docs/growth-os-checklist/gen_visual_guide.py
  NODE_PATH=$(npm root -g) node docs/growth-os-checklist/build_visual_guide.mjs
Brand tokens follow docs/HMM_Color_System.md. No em dashes; first person singular; no capability count.
"""
import html, os

HERE = os.path.dirname(os.path.abspath(__file__))
E = html.escape

# Tabler-style line icons (24px grid, stroke = currentColor)
ICON = {
    'health': '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 8h18"/><path d="M6 6h.01M8.5 6h.01M11 6h.01"/><path d="M8.5 14l2.5 2.5 4.5-5"/>',
    'search': '<circle cx="10" cy="10" r="7"/><path d="M21 21l-6-6"/><path d="M7 12l2-2.5 2 1.5 2.5-3"/>',
    'content': '<path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M9 9h1M9 13h6M9 17h6"/>',
    'ai': '<path d="M8 9h8M8 13h4"/><path d="M18 4a3 3 0 0 1 3 3v8a3 3 0 0 1-3 3h-5l-5 3v-3H6a3 3 0 0 1-3-3V7a3 3 0 0 1 3-3h12z"/><path d="M17 11.5l.6 1.4 1.4.6-1.4.6-.6 1.4-.6-1.4-1.4-.6 1.4-.6z" fill="currentColor"/>',
    'measure': '<path d="M3 21h18"/><rect x="5" y="12" width="3" height="6" rx="1"/><rect x="10.5" y="8" width="3" height="10" rx="1"/><rect x="16" y="4" width="3" height="14" rx="1"/>',
    'progress': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/>',
    'link': '<path d="M9 15l6-6"/><path d="M11 6l.5-.5a5 5 0 0 1 7 7L18 13"/><path d="M13 18l-.5.5a5 5 0 0 1-7-7L6 11"/>',
    'sitemap': '<rect x="9" y="3" width="6" height="5" rx="1"/><rect x="3" y="16" width="6" height="5" rx="1"/><rect x="15" y="16" width="6" height="5" rx="1"/><path d="M12 8v4M6 16v-2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v2"/>',
    'gauge': '<path d="M5 18a9 9 0 1 1 14 0"/><path d="M12 13l4-4"/><circle cx="12" cy="13" r="1"/>',
    'phone': '<rect x="7" y="3" width="10" height="18" rx="2"/><path d="M11 17h2"/>',
    'code': '<path d="M8 8l-4 4 4 4M16 8l4 4-4 4M14 5l-4 14"/>',
    'image': '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="9.5" r="1.5"/><path d="M21 16l-5-5-8 9"/>',
    'rocket': '<path d="M5 14c-1.5 1-2 4-2 7 3 0 6-.5 7-2"/><path d="M8 16l-3-3c1.5-6 6-10 14-10 0 8-4 12.5-10 14z"/><circle cx="14.5" cy="9.5" r="1.5"/>',
    'chart': '<path d="M4 19l5-6 4 3 7-9"/><path d="M15 7h5v5"/>',
    'target': '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    'users': '<circle cx="9" cy="8" r="3"/><path d="M3 20a6 6 0 0 1 12 0"/><circle cx="17" cy="9" r="2.5"/><path d="M16 14.5a5 5 0 0 1 5 5.5"/>',
    'pin': '<path d="M12 21s-7-6.5-7-12a7 7 0 0 1 14 0c0 5.5-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/>',
    'cart': '<circle cx="9" cy="20" r="1.5"/><circle cx="17" cy="20" r="1.5"/><path d="M3 4h2l2.5 11h11l2-8H6.5"/>',
    'globe': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    'heading': '<path d="M6 4v16M18 4v16M6 12h12"/>',
    'refresh': '<path d="M20 11a8 8 0 0 0-14.5-4.5L4 8"/><path d="M4 4v4h4"/><path d="M4 13a8 8 0 0 0 14.5 4.5L20 16"/><path d="M20 20v-4h-4"/>',
    'brief': '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V3h6v1"/><path d="M9 11l2 2 4-4M9 17h6"/>',
    'quote': '<path d="M5 4h14a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-6l-5 4v-4H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/><path d="M8 9h8M8 12h5"/>',
    'sparkle': '<path d="M12 3l2 5.5L19.5 10.5 14 12.5 12 18l-2-5.5-5.5-2L10 8.5z"/><path d="M19 17l.7 1.6 1.6.7-1.6.7L19 21.6l-.7-1.6-1.6-.7 1.6-.7z"/>',
    'flag': '<path d="M5 21V4"/><path d="M5 4h11l-2 4 2 4H5"/>',
    'click': '<path d="M9 9l11 4-5 2-2 5z"/><path d="M5 3v3M3 5h3M8.5 4.5l-1.5 1.5M4.5 8.5L6 7"/>',
    'shield': '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    'database': '<ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/><path d="M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>',
    'filter': '<path d="M4 5h16l-6 8v6l-4 2v-8z"/>',
    'history': '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/><path d="M12 8v4l3 2"/>',
    'checkc': '<circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/>',
    'bell': '<path d="M10 5a2 2 0 1 1 4 0 7 7 0 0 1 4 6v3l2 3H4l2-3v-3a7 7 0 0 1 4-6"/><path d="M9 17v1a3 3 0 0 0 6 0v-1"/>',
    'report': '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 17v-3M12 17v-6M16 17v-8"/>',
    'key': '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M17 6l3 3M14 9l2 2"/>',
    'eye': '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    'pen': '<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="M13.5 6.5l4 4"/>',
    'swap': '<path d="M4 8h14l-4-4M20 16H6l4 4"/>',
    'folder': '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
    'run': '<circle cx="6" cy="19" r="2"/><circle cx="18" cy="5" r="2"/><path d="M12 19h4.5a3.5 3.5 0 0 0 0-7h-8a3.5 3.5 0 0 1 0-7H12"/>',
}

def icon(name, cls='ico'):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON[name]}</svg>')

# Labels: key -> (text, css class, symbol, legend meaning)
L = {
    'S': ('Scheduled check', 'b-rep', 'refresh', 'Can run on an agreed schedule after setup and testing.'),
    'D': ('Draft + review', 'b-draft', 'pen', 'Prepares suggestions for a person to assess.'),
    'H': ('Human review', 'b-human', 'eye', 'Needs judgment or validation.'),
    'C': ('On change', 'b-change', 'swap', 'Runs around an update, fix or redesign.'),
}

def badge(k):
    t, c, i, _ = L[k]
    return f'<span class="badge {c}">{icon(i, "bi")}{E(t)}</span>'

CONTACT = 'https://helpmemarketing.com/contact?entry=seo_automation#contact-form'

# Each card: title, icon, label keys, optional tag, checks, automates, review, you receive, note
def card(t, ic, labels, checks, receive, auto=None, review=None, tag=None, note=None):
    return dict(t=t, ic=ic, labels=labels, checks=checks, receive=receive, auto=auto, review=review, tag=tag, note=note)

PAGES = [
    dict(kicker='Website health & search performance', title='Can people and search engines reach the right pages?', cards=[
        card('Access, indexing & sitemaps', 'search', 'S',
             'Status codes, robots directives, noindex, canonical URLs and sitemap inclusion.',
             'Affected URLs, the issue on each and the next step.',
             auto='Reruns the agreed URL checks and compares them with the last run. Public website signals are kept apart from Google’s recorded indexing status, which needs Search Console.'),
        card('Links, redirects & website updates', 'link', 'SC',
             'Broken links, redirect chains, and selected pages and journeys before and after a release.',
             'Affected source and destination URLs, plus regressions found after a release.',
             auto='Retests links and redirects on the agreed pages. Around a release, compares before and after.'),
        card('Performance & media', 'gauge', 'SD',
             'Lab speed on key pages, real-user data where Google has enough, missing image descriptions and media that slows pages.',
             'Page-specific diagnostics, with lab and real-user data kept apart, and flagged images.',
             auto='Retests the agreed pages against earlier results. Flags images without descriptions and drafts them.',
             review='A person checks that each description is useful.'),
        card('Structured data', 'code', 'SH',
             'Whether markup is valid, and whether it matches the visible page and your business.',
             'Page-specific findings and draft corrections for your developer.',
             auto='Validates markup on the agreed pages and flags new errors.',
             review='Accuracy against the page and business is checked by a person.'),
        card('Search performance & opportunities', 'chart', 'SH',
             'Page and query impressions, clicks, CTR and position across comparable periods. Search intent, competitor pages and backlinks.',
             'Pages or opportunities to investigate, with the evidence behind each.',
             auto='Collects connected search data, compares agreed periods and flags changes.',
             review='Intent, competitor and backlink findings need interpretation. Backlinks are investigated, never auto-disavowed.'),
        card('Local, store & international', 'globe', 'S',
             'Local: Business Profile details and location searches. Store: product pages, product markup and Merchant Center issues. International: language and country versions.',
             'Dated location observations, product or account issues, and affected URLs between versions.',
             auto='Repeats supported observations and rechecks product markup and version links.',
             tag='Only where it applies'),
    ]),
    dict(kicker='Content & AI visibility', title='Do your pages answer the questions customers ask?', cards=[
        card('Page basics & content freshness', 'heading', 'SH',
             'Titles, descriptions and headings. Customer questions, accuracy and outdated information.',
             'Page-specific issues and sections to update, with the reason for each.',
             auto='Rechecks titles, descriptions and headings on the agreed pages and flags new problems.',
             review='Accuracy, freshness and wording are an editorial judgment.'),
        card('Internal linking', 'sitemap', 'D',
             'How priority pages connect, and where a relevant link would help visitors.',
             'Source page, destination and suggested link wording.',
             auto='Inspects crawlable links and prepares suggested additions.',
             review='You review relevance and wording.'),
        card('Content briefs', 'brief', 'D',
             'The page’s purpose, the intended customer action and the evidence from the review.',
             'A brief saying what to change, why, and how to verify it was done.',
             auto='Drafts the brief from the available evidence.',
             review='You approve the changes and wording.'),
        card('Location & service pages at scale', 'pin', 'H',
             'Pages built from one template: useful differences, factual consistency, internal links and indexing directives.',
             'Pages to improve, merge, link or keep out of the index, with the reason for each.',
             review='Similarity is a starting point for review, not a pass mark. Nothing is published in bulk.',
             tag='Optional'),
        card('Answer suitability', 'quote', 'H',
             'Clear answers to customer questions, accurate business information and evidence for claims.',
             'Specific sections to clarify or strengthen.',
             review='Suggestions can be drafted; clarity and accuracy are judged by a person.'),
        card('AI mentions & citations', 'sparkle', 'SH',
             'Selected Google AI answers and other assistant responses to agreed questions.',
             'Question, platform, date, observed mention, citation and accuracy concerns.',
             auto='Repeats supported Google AI observations on a schedule.',
             review='Other assistants are checked in a browser or by hand. Accuracy is judged by a person.',
             note='AI answers vary; observations are recorded with their date and context.'),
    ]),
    dict(kicker='Measurement & progress', title='Are enquiries being measured, and is the work moving forward?', cards=[
        card('Conversion & enquiry journey', 'click', 'H',
             'Offer clarity, calls to action, form usability and friction on phones and desktops.',
             'Observed barriers, with recommendations or test ideas.',
             review='A person walks the journey. Forms are submitted only with your permission.'),
        card('Events & consent', 'shield', 'H',
             'Whether intended actions produce the expected events, and how tracking responds to consent choices.',
             'What fires, what does not, and the gaps to fix.',
             review='Configured tags are kept apart from behaviour observed in a test. Tests need your approval.'),
        card('Real enquiries & data quality', 'database', 'H',
             'Which actions count as a result, whether recorded leads match your business records, and test traffic, filters, time zones and reporting dates.',
             'Discrepancies, and which figures can be relied on.',
             review='Records are compared only with your permission.'),
        card('Priorities & draft actions', 'target', 'D',
             'Recommendations consider the seriousness of the issue, the opportunity, strength of evidence, implementation risk, effort and dependencies.',
             'What to address now, investigate, test or leave unchanged.',
             auto='Combines related findings and drafts a prioritised plan.',
             review='You decide what goes ahead.'),
        card('Change verification & monitoring', 'checkc', 'CS',
             'Whether approved changes are live, whether their acceptance checks pass and whether problems recur.',
             'A confirmed status with evidence: live, partly live, not yet live or unable to verify. Business impact is assessed separately.',
             auto='Rechecks observable changes and reruns the agreed checks against a baseline.'),
        card('Change record & recurring summary', 'history', 'SD',
             'New findings, decisions, completed work, unresolved items and approvals needed.',
             'A concise update backed by a dated working record.',
             auto='Adds each run to the record and drafts the summary.',
             review='You review the summary before it is shared.'),
    ]),
]

FLOW = [
    ('key', 'Brief & access'), ('search', 'Collect evidence'), ('health', 'Run the checks'),
    ('target', 'Diagnose & prioritise'), ('pen', 'Draft & approve'), ('checkc', 'Verify & monitor'),
]

START = [
    ('Important pages rarely appear in search', 'Search performance and indexing checks', 'search'),
    ('People visit but few enquire', 'Conversion and measurement review', 'click'),
    ('Unsure whether AI tools mention your business', 'AI visibility checks', 'sparkle'),
    ('Problems return after website updates', 'Change verification and monitoring', 'checkc'),
    ('SEO findings pile up without action', 'Prioritised briefs and progress tracking', 'brief'),
]

AREAS = [
    ('health', 'Website health', 'Access, links, speed and markup.'),
    ('search', 'Search performance', 'Visibility, intent and opportunities.'),
    ('content', 'Content', 'Page basics, links and briefs.'),
    ('ai', 'AI visibility', 'Answers, mentions and citations.'),
    ('measure', 'Measurement', 'Enquiries, events and data quality.'),
    ('progress', 'Progress', 'Priorities, verification and records.'),
]

TOTAL = 2 + len(PAGES)

def foot(i):
    return (f'<footer class="pf"><span>SEO Growth OS Visual Guide &middot; HelpMeMarketing</span>'
            f'<span>{i} / {TOTAL}</span></footer>')

def para(key, cls, ic, text):
    i = icon(ic, 'bi') if ic else ''
    return f'<p class="{cls}"><b>{i}{key}</b> {E(text)}</p>'

def render_card(c):
    tag = f'<span class="tag">{E(c["tag"])}</span>' if c['tag'] else ''
    badges = ''.join(badge(k) for k in c['labels'])
    out = [f'<div class="cd"><div class="cd-h"><span class="ci">{icon(c["ic"])}</span><h3>{E(c["t"])}</h3></div>'
           f'<div class="cd-b">{badges}{tag}</div>',
           para('Checks', 'k-chk', None, c['checks'])]
    if c['auto']:
        out.append(para('Automates', 'k-auto', 'refresh', c['auto']))
    if c['review']:
        out.append(para('Review', 'k-rev', 'eye', c['review']))
    out.append(para('You receive', 'k-rec', None, c['receive']))
    if c['note']:
        out.append(f'<p class="cn">{E(c["note"])}</p>')
    out.append('</div>')
    return ''.join(out)

pages = []

# Page 1: where should you start?
rows = ''.join(f'<tr><td>{E(a)}</td><td><span class="st-ic">{icon(ic)}</span>{E(b)}</td></tr>' for a, b, ic in START)
areas = ''.join(f'<div class="ar"><span class="ci">{icon(ic)}</span><div><h3>{E(t)}</h3><p>{E(d)}</p></div></div>' for ic, t, d in AREAS)
legend = ''.join(f'<tr><td>{badge(k)}</td><td>{E(L[k][3])}</td></tr>' for k in 'SDHC')
pages.append(f'''<section class="page">
  <div class="intro">
    <div class="intro-top"><img class="logo" src="../../assets/brand/hmm-logo-full.svg" width="150" height="69" alt="HelpMeMarketing"><span>SEO Growth OS Visual Guide</span></div>
    <h1>SEO Growth OS</h1>
    <p class="intro-sub"><em>Find the checks your business needs.</em></p>
    <p class="intro-lede">Explore the website and search checks I can help automate, the recommendations they produce and where your review is needed.</p>
  </div>
  <h2 class="sh">Where should you start?</h2>
  <table class="start"><thead><tr><th>What you are experiencing</th><th>Start here</th></tr></thead><tbody>{rows}</tbody></table>
  <h2 class="sh">Six areas</h2>
  <div class="areas">{areas}</div>
  <h2 class="sh">How to read the labels</h2>
  <table class="legend">{legend}</table>
  <p class="scope">Checks depend on your website, connected tools and data. Automation is configured during setup, and you approve changes before anything is published.</p>
  {foot(1)}</section>''')

for n, pg in enumerate(PAGES, start=2):
    cards = ''.join(render_card(c) for c in pg['cards'])
    pages.append(f'''<section class="page">
  <header class="ph"><div class="kick">{E(pg["kicker"])}</div><h1>{E(pg["title"])}</h1></header>
  <div class="cards">{cards}</div>
  {foot(n)}</section>''')

# Page 5: how it works and next step
flow = ''.join(f'<div class="fl"><span class="fi">{icon(ic)}</span><span class="fn">{i}</span><h3>{E(t)}</h3></div>'
               for i, (ic, t) in enumerate(FLOW, start=1))
pages.append(f'''<section class="page">
  <header class="ph"><div class="kick">How it works & next step</div><h1>From a finding to a clear next action</h1></header>
  <div class="flow">{flow}</div>
  <p class="flow-note">{icon("refresh", "bi")}The stages can span more than one run. Each run builds on the previous record, and not every finding leads to a change in the same run.</p>
  <div class="example"><div class="ex-h"><span class="nl">An example from my own website</span><span class="ex-date">Process example, recorded 10 November 2026</span></div>
    <p>A run flagged a commercial page with limited search visibility. It checked indexing and internal links, then prepared a brief naming the pages to edit and the proposed link wording.</p>
    <p>The proposed change required approval. Confirming implementation and assessing later search performance are separate steps.</p></div>
  <div class="two">
    <div class="panel"><h2 class="ph2">{icon("report", "ico-s")}What you receive</h2><ul>
      <li>A clear report with findings and priorities.</li>
      <li>Draft briefs or recommendations for review.</li>
      <li>A dated record of decisions and changes.</li>
      <li>A way to verify each recommended change.</li></ul></div>
    <div class="panel"><h2 class="ph2">{icon("key", "ico-s")}What setup needs</h2><ul>
      <li>Your website and priority outcomes.</li>
      <li>Access to the agreed data sources.</li>
      <li>Selected checks, a tested schedule and a review process.</li></ul>
      <p class="pn">Some checks need paid tools or an available signed-in browser; requirements are confirmed during setup.</p></div>
  </div>
  <div class="cta"><h2>Want these checks set up for your business?</h2>
    <p>Tell me your website, the tools you use and what you want to automate.</p>
    <a href="{CONTACT}">Enquire about SEO automation &rarr;</a></div>
  {foot(TOTAL)}</section>''')

CSS = '''
@font-face{font-family:Fraunces;font-weight:400 500;font-style:normal;src:url(../../assets/fonts/fraunces-latin.woff2) format("woff2")}
@font-face{font-family:Fraunces;font-weight:400;font-style:italic;src:url(../../assets/fonts/fraunces-italic-latin.woff2) format("woff2")}
@font-face{font-family:Inter;font-weight:400 700;src:url(../../assets/fonts/inter-latin.woff2) format("woff2")}
:root{--obsidian:#0E0E0E;--elev:#1A1A1A;--paper:#F6F5F2;--card:#FFFFFF;--line:#ECEAE4;--line2:#D4D0C6;
 --text:#0E0E0E;--body:rgba(14,14,14,.82);--muted:#4A4A4A;--ter:#6B6B6B;--cta:#FF5C1A;--cta-ink:#B8400C;--mint:#007A62}
@page{size:Letter;margin:0}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{font-family:Inter,Arial,sans-serif;color:var(--text);font-size:10pt;line-height:1.38;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:8.5in;height:11in;padding:.42in .55in .62in;position:relative;overflow:hidden;background:var(--paper);break-after:page;page-break-after:always}
.page:last-child{break-after:auto}
h1,h2,h3,p,ul{margin:0}
.ico{width:18px;height:18px}
.ico-s{width:17px;height:17px;color:var(--cta);vertical-align:-3px;margin-right:6px}
.bi{width:10px;height:10px;vertical-align:-1px;margin-right:4px;stroke-width:2.2}
.ci{flex:none;width:30px;height:30px;border-radius:8px;background:rgba(255,92,26,.11);color:var(--cta);display:inline-flex;align-items:center;justify-content:center}
.kick{font-size:8.5pt;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--cta-ink)}
.badge{display:inline-block;font-size:7.5pt;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:3px 8px;border-radius:999px;white-space:nowrap}
.b-rep{background:rgba(0,122,98,.11);color:var(--mint)}
.b-draft{background:rgba(255,92,26,.12);color:var(--cta-ink)}
.b-human{background:#fff;color:var(--text);box-shadow:inset 0 0 0 1px var(--line2)}
.b-change{background:var(--obsidian);color:#fff}
.tag{display:inline-block;font-size:7.5pt;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:2px 8px;border-radius:999px;border:1px dashed var(--ter);color:var(--muted)}
.pf{position:absolute;left:.55in;right:.55in;bottom:.3in;display:flex;justify-content:space-between;border-top:1px solid var(--line2);padding-top:7px;font-size:8pt;color:var(--ter)}
/* page 1 */
.intro{background:var(--obsidian);color:#fff;border-radius:14px;padding:18px 22px 18px;margin-bottom:14px}
.intro-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.intro-top span{font-size:8pt;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--cta)}
.logo{width:92px;height:auto}
.intro h1{font-family:Fraunces,Georgia,serif;font-weight:500;font-size:30pt;line-height:1.05}
.intro-sub{font-family:Fraunces,Georgia,serif;font-size:17pt;margin-top:4px}
.intro-sub em{color:var(--cta)}
.intro-lede{font-size:10.5pt;color:#C7C7C7;margin-top:8px;max-width:5.6in}
.sh{font-family:Fraunces,Georgia,serif;font-weight:500;font-size:14.5pt;margin:12px 0 7px}
table{border-collapse:collapse;width:100%}
.start{background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden}
.start th{text-align:left;font-size:8pt;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--ter);padding:8px 14px;border-bottom:1px solid var(--line);background:#FBFAF7}
.start td{padding:7px 14px;border-bottom:1px solid var(--line);vertical-align:middle}
.start tr:last-child td{border-bottom:0}
.start td:first-child{width:48%;color:var(--body)}
.start td:last-child{font-weight:600}
.st-ic{display:inline-flex;vertical-align:-4px;margin-right:8px;color:var(--cta)}
.areas{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.ar{display:flex;gap:10px;align-items:center;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:9px 11px}
.ar h3{font-size:10pt;font-weight:650}
.ar p{font-size:8.5pt;color:var(--muted);line-height:1.3}
.legend{background:var(--card);border:1px solid var(--line);border-radius:12px}
.legend td{padding:5px 14px;border-bottom:1px solid var(--line);color:var(--body)}
.legend tr:last-child td{border-bottom:0}
.legend td:first-child{width:180px}
.scope{margin-top:10px;padding:10px 14px;border-left:3px solid var(--cta);background:#EFEDE7;border-radius:0 10px 10px 0;color:var(--body)}
/* card pages */
.ph{margin-bottom:12px}
.ph h1{font-family:Fraunces,Georgia,serif;font-weight:500;font-size:21pt;line-height:1.15;margin-top:4px}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:9px}
.cd{background:var(--card);border:1px solid var(--line);border-top:3px solid var(--cta);border-radius:12px;padding:10px 13px 11px;break-inside:avoid}
.cd-h{display:flex;gap:9px;align-items:center}
.cd-h h3{font-size:11pt;font-weight:650;line-height:1.2}
.cd-b{display:flex;flex-wrap:wrap;gap:5px;margin:7px 0 6px}
.cd p{margin-top:4px;color:var(--body)}
.cd p b{font-weight:650;color:var(--text);margin-right:2px}
.k-auto b{color:var(--mint)!important}
.k-rev b{color:var(--muted)!important}
.k-rec{padding-top:5px;margin-top:6px!important;border-top:1px dashed var(--line)}
.k-rec b{color:var(--cta-ink)!important}
.cn{font-size:8.5pt;color:var(--ter)!important;font-style:italic}
/* page 5 */
.flow{display:grid;grid-template-columns:repeat(6,1fr);gap:6px}
.fl{position:relative;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 8px 14px;text-align:center}
.fl:not(:last-child)::after{content:"";position:absolute;right:-6px;top:30px;width:7px;height:7px;border-top:2px solid var(--cta);border-right:2px solid var(--cta);transform:rotate(45deg);background:var(--paper);z-index:1}
.fi{display:inline-flex;width:32px;height:32px;border-radius:50%;background:var(--obsidian);color:#fff;align-items:center;justify-content:center}
.fl:last-child .fi{background:var(--cta)}
.fn{display:block;font-size:7.5pt;font-weight:700;color:var(--ter);margin-top:4px}
.fl h3{font-size:9.5pt;font-weight:650;line-height:1.2;margin-top:1px}
.flow-note{margin:12px 0 26px;font-size:9.5pt;color:var(--cta-ink);text-align:center}
.example{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--mint);border-radius:0 12px 12px 0;padding:16px 18px}
.ex-h{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:5px}
.nl{font-size:8.5pt;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--mint)}
.ex-date{font-size:8.5pt;color:var(--ter)}
.example p{color:var(--body);margin-top:4px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-top:26px}
.panel{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.ph2{font-family:Fraunces,Georgia,serif;font-weight:500;font-size:13.5pt;margin-bottom:6px}
.panel ul{padding-left:17px;color:var(--body)}
.panel li{margin-top:6px}
.panel li::marker{color:var(--cta)}
.pn{margin-top:8px;font-size:9pt;color:var(--ter)}
.cta{margin-top:26px;background:var(--obsidian);color:#fff;border-radius:12px;padding:22px 24px}
.cta h2{font-family:Fraunces,Georgia,serif;font-weight:500;font-size:16pt;margin-bottom:4px}
.cta p{color:#C7C7C7;margin-bottom:8px}
.cta a{color:var(--cta);font-weight:700;font-size:11pt;text-decoration:none}
'''

doc = f'''<!doctype html><html lang="en-CA"><head><meta charset="utf-8">
<title>SEO Growth OS Visual Guide | HelpMeMarketing</title><style>{CSS}</style></head>
<body>{"".join(pages)}</body></html>'''
open(os.path.join(HERE, 'seo-growth-os-visual-guide.html'), 'w').write(doc)
assert '—' not in doc
print(f'{TOTAL} pages')
