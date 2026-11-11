#!/usr/bin/env python3
"""Generates seo-growth-os-visual-guide.html (8 fixed Letter pages) in HMM brand colours.

Content is the founder's Visual Guide draft of 11 Nov 2026. Edit the lists below, then render:
  python3 docs/growth-os-checklist/gen_visual_guide.py
  NODE_PATH=$(npm root -g) node docs/growth-os-checklist/build_visual_guide.mjs
Brand tokens follow docs/HMM_Color_System.md: Obsidian #0E0E0E, Signal Orange #FF5C1A
(#B8400C for small text on light), Mint #007A62 on light, paper #F6F5F2, border #ECEAE4.
"""
import html, os

HERE = os.path.dirname(os.path.abspath(__file__))
E = html.escape

# Labels: key -> (text, css class)
L = {
    'R': ('Scheduled check', 'b-rep', 'refresh'),
    'D': ('Draft + review', 'b-draft', 'pen'),
    'H': ('Human review', 'b-human', 'eye'),
    'C': ('On change', 'b-change', 'swap'),
}

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

def badge(k):
    t, c, i = L[k]
    return f'<span class="badge {c}">{icon(i, "bi")}{E(t)}</span>'

AREAS = [
    dict(n='01', key='health', name='Website health', cover='Find access and technical issues.',
         sub='Spot problems before they become routine.', layout='grid3',
         items=[
            ('Crawl access & indexing', 'R', 'Robots rules, noindex, canonical URLs and status codes.', 'Flag affected URLs; Google indexing needs account evidence.'),
            ('Broken links & redirects', 'R', 'Links that fail, plus redirects that take multiple hops.', 'A source-to-destination list for review and repair.'),
            ('Sitemap discovery', 'R', 'Listed URLs, their reachability and sitemap consistency.', 'URLs to investigate or update in the sitemap.'),
            ('Page performance', 'R', 'Lab speed checks and real-user data when available.', 'Page-specific diagnostics, with lab and field data separated.'),
            ('Forms & mobile journeys', 'H', 'Navigation, enquiry paths and small-screen usability.', 'Observed barriers; submissions tested only with permission.'),
            ('Structured data validity', 'R', 'Whether page markup parses and passes supported validation.', 'Validation findings tied to the affected page.'),
            ('Structured data accuracy', 'H', 'Whether markup reflects the visible page and business.', 'Corrections or draft markup for developer review.'),
            ('Images & alt text', 'D', 'Missing descriptions and media affecting page performance.', 'Flagged images; a person checks description usefulness.'),
            ('Launch & redesign checks', 'C', 'Selected URLs and journeys before and after a release.', 'A comparison showing regressions and unresolved checks.'),
         ],
         needs='Public website; Search Console for Google indexing; lab and field performance sources where available.'),
    dict(n='02', key='search', name='Search performance', cover='See where visibility changes.',
         sub='Find the pages that deserve a closer look.', layout='grid2',
         items=[
            ('Page & query monitoring', 'R', 'Impressions, clicks, CTR and position over comparable periods.', 'Flag changes by page or query, with country filters agreed at setup.'),
            ('Search intent review', 'H', 'Whether a page answers the need behind its search queries.', 'A recommendation to clarify, expand or refocus the page.'),
            ('Competitor opportunities', 'H', 'Relevant competing pages and gaps in the topics covered.', 'Evidence-backed opportunities for your business to assess.'),
            ('Backlink review', 'H', 'Who links to you and competitors; unusual patterns worth investigating.', 'Findings with source limits, not automatic disavow advice.'),
            ('Local search & maps', 'R', 'Profile details and location-specific search observations where supported.', 'Dated observations for agreed services and locations.'),
            ('Online store listings', 'R', 'Product pages, product markup and available Merchant Center issues.', 'Product or account issues to review with your store team.'),
            ('Language & country versions', 'R', 'Hreflang relationships and consistency across relevant versions.', 'Affected URLs and configuration issues for review.'),
         ],
         needs='Search Console; relevant location, merchant, competitor or link data. Some sources have their own costs.'),
    dict(n='03', key='content', name='Content', cover='Identify pages needing attention.',
         sub='Turn a page-level finding into a useful brief.', layout='rows',
         items=[
            ('Page basics', 'R', 'Titles, descriptions, headings and links on selected pages.', 'A page-specific list of missing, conflicting or unclear elements.'),
            ('Content quality & freshness', 'H', 'Customer questions, factual accuracy, relevance and outdated information.', 'Sections to clarify or update, with the reason for each recommendation.'),
            ('Internal links & site structure', 'D', 'How priority pages connect and where relevant links could help visitors.', 'Suggested source page, destination and link wording for approval.'),
            ('Content briefs & recommendations', 'D', 'Evidence from the review, page purpose and the intended customer action.', 'A draft brief with proposed changes, supporting evidence and acceptance checks.'),
         ],
         optional=[
            ('Location & service pages at scale', 'H', 'Pages built from one template: useful differences between pages, factual consistency, internal links and indexing directives.', 'Pages to improve, merge, link or keep out of the index, with the reason for each.'),
            ('Conversion review', 'H', 'Offer clarity, calls to action and enquiry friction on key pages.', 'Recommendations or test ideas, each with the reason behind it.'),
         ],
         needs='Public pages, business knowledge and connected search data where relevant. All proposed changes require review.'),
    dict(n='04', key='ai', name='AI visibility', cover='Record mentions and citations.',
         sub='Keep a dated record of what AI answers show.', layout='rows',
         items=[
            ('Answer suitability', 'H', 'Whether pages clearly answer customer questions and support business claims.', 'Recommendations to improve clarity, completeness and supporting evidence.'),
            ('Google AI observations', 'R', 'Whether your business or pages appear in selected Google AI answers, where checks are supported.', 'The question, date, context and observed mentions or citations.'),
            ('Other AI mentions & citations', 'H', 'Selected assistant responses: business mentions, cited pages and factual accuracy.', 'Dated responses and citations, with inaccuracies or omissions flagged.'),
         ],
         needs='Agreed questions, target locations and access to selected AI tools or observation sources. Availability varies.',
         note='A repeated observation is not a fixed AI ranking or a promise of citation.'),
    dict(n='05', key='measure', name='Measurement', cover='Check what the figures mean.',
         sub='Understand whether recorded activity is useful.', layout='rows',
         items=[
            ('Define a meaningful result', 'H', 'Which actions count as enquiries, bookings, purchases or other business outcomes.', 'An agreed measurement definition before interpreting performance.'),
            ('Check actual event behaviour', 'H', 'Whether the intended action produces the expected tracking event.', 'A distinction between configured tags and observed events; tests need approval.'),
            ('Consent behaviour', 'H', 'What tracking does when a visitor accepts or declines consent.', 'Observed behaviour and gaps to review with the site owner.'),
            ('Match leads to real records', 'H', 'Whether recorded enquiries align with available CRM, booking or sales records.', 'Discrepancies and evidence gaps, without treating every event as a customer.'),
            ('Data quality', 'H', 'Test traffic, filters, time zones and date ranges that can distort comparisons.', 'Corrections to investigate before drawing conclusions from the numbers.'),
         ],
         needs='Analytics and tag access, agreed business outcomes, and enquiry or CRM records where permission is granted.'),
    dict(n='06', key='progress', name='Progress', cover='Keep findings and changes connected.',
         sub='Make the next run build on the last one.', layout='rows',
         items=[
            ('A dated change record', 'R', 'Findings, recommendations, decisions and changes from each run.', 'A persistent record showing what remains open and what changed.'),
            ('Implementation verification', 'C', 'Whether an approved edit is live and meets its acceptance checks.', 'Live, partly live, not yet live or unable to verify, supported by evidence.'),
            ('Monitoring & alerts', 'R', 'Agreed checks for regressions or notable changes against a suitable baseline.', 'Flagged changes with context; missing evidence is kept visible.'),
            ('Recurring summaries', 'D', 'New findings, unresolved issues, completed work and decisions still needed.', 'A concise update and a prioritised action list for review.'),
         ],
         needs='The previous run, change history, agreed checks and approval records. Scheduling depends on the configured environment.'),
]

STEPS = [
    ('Find the signal', 'A commercial page had limited search visibility. The run flagged it for investigation.'),
    ('Check the evidence', 'Indexing status and internal links were reviewed. Weak linking was treated as a hypothesis, not a proven cause.'),
    ('Prepare the brief', 'The draft named the pages to edit and proposed clearer internal-link wording for approval.'),
    ('Verify, then measure', 'The workflow separates confirming the edit is live from assessing later search performance. This example does not claim a ranking lift.'),
]

CARD_ICON = {
    'Crawl access & indexing': 'search', 'Broken links & redirects': 'link', 'Sitemap discovery': 'sitemap',
    'Page performance': 'gauge', 'Forms & mobile journeys': 'phone', 'Structured data validity': 'code',
    'Structured data accuracy': 'checkc', 'Images & alt text': 'image', 'Launch & redesign checks': 'rocket',
    'Page & query monitoring': 'chart', 'Search intent review': 'target', 'Competitor opportunities': 'users',
    'Backlink review': 'link', 'Local search & maps': 'pin', 'Online store listings': 'cart',
    'Language & country versions': 'globe', 'Page basics': 'heading', 'Content quality & freshness': 'refresh',
    'Internal links & site structure': 'sitemap', 'Content briefs & recommendations': 'brief',
    'Answer suitability': 'quote', 'Google AI observations': 'sparkle', 'Other AI mentions & citations': 'ai',
    'Define a meaningful result': 'flag', 'Check actual event behaviour': 'click', 'Consent behaviour': 'shield',
    'Match leads to real records': 'database', 'Data quality': 'filter', 'A dated change record': 'history',
    'Implementation verification': 'checkc', 'Monitoring & alerts': 'bell', 'Recurring summaries': 'report',
    'Location & service pages at scale': 'pin', 'Conversion review': 'click',
}

AUTO = {
    'Crawl access & indexing': 'Repeats the agreed URL checks and compares the results with the previous run.',
    'Broken links & redirects': 'Retests links and redirect chains on the agreed pages and lists what changed.',
    'Sitemap discovery': 'Fetches the sitemap, checks that each listed URL responds and flags mismatches.',
    'Page performance': 'Retests the agreed pages and compares them with earlier results.',
    'Structured data validity': 'Validates markup on the agreed pages and flags new errors.',
    'Images & alt text': 'Finds images without descriptions and drafts suggestions. You review whether each one is useful.',
    'Page & query monitoring': 'Collects connected search data, compares agreed periods and flags changes for review.',
    'Local search & maps': 'Repeats location-specific observations where a tracking source is set up, and dates each one.',
    'Online store listings': 'Rechecks product markup and available Merchant Center issues, and flags new ones.',
    'Language & country versions': 'Rechecks the links between language versions and flags breaks or mismatches.',
    'Page basics': 'Rechecks titles, descriptions and headings on the agreed pages and flags new problems.',
    'Internal links & site structure': 'Inspects crawlable links and prepares suggested linking opportunities. You review relevance and wording.',
    'Content briefs & recommendations': 'Drafts a brief from the review evidence. You approve the changes and the wording.',
    'Google AI observations': 'Repeats the agreed questions where checks are supported and records each dated answer.',
    'A dated change record': "Adds each run's findings, decisions and changes to the record.",
    'Monitoring & alerts': 'Reruns the agreed checks against the baseline and flags regressions.',
    'Recurring summaries': 'Drafts the summary from the record. You review it before it is shared.',
}

def auto(t):
    a = AUTO.get(t)
    return f'<p class="au"><b>{icon("refresh", "bi")}Automates:</b> {E(a)}</p>' if a else ''

TOTAL = 3 + len(AREAS)

def foot(i):
    return (f'<footer class="pf"><span>HelpMeMarketing / SEO Growth OS</span>'
            f'<span>{i:02d} / {TOTAL:02d}</span></footer>')

def head(kicker, title, sub, ico):
    return (f'<div class="kick-top">HelpMeMarketing</div>'
            f'<header class="ph"><div><div class="kick">{E(kicker)}</div><h1>{E(title)}</h1>'
            f'<p class="lede">{E(sub)}</p></div><div class="ph-ico">{icon(ico, "ico-lg")}</div></header>')

def grid_card(t, k, desc, out, inline=False):
    # Two-column cards are wide enough to carry the label beside the title.
    b = badge(k)
    return (f'<div class="gc"><div class="gc-h"><span class="ci">{icon(CARD_ICON[t])}</span><h3>{E(t)}</h3>{b if inline else ""}</div>{"" if inline else b}<p class="d">{E(desc)}</p>'
            f'{auto(t)}<p class="o"><b>Output:</b> {E(out)}</p></div>')

def row_card(t, k, desc, out):
    return (f'<div class="rc"><div class="rc-h"><span class="ci">{icon(CARD_ICON[t])}</span><h3>{E(t)}</h3>{badge(k)}</div><div class="rc-g">'
            f'<div><div class="lab">Checks</div><p class="d">{E(desc)}</p></div>'
            f'<div><div class="lab">You receive</div><p class="o">{E(out)}</p></div></div>{auto(t)}</div>')

def needs(a):
    note = f'<p class="nn">{E(a["note"])}</p>' if a.get('note') else ''
    return f'<div class="needs"><div class="nl">What this needs</div><p>{E(a["needs"])}</p>{note}</div>'

pages = []

# Cover
tiles = ''.join(
    f'<div class="ct">{icon(a["key"])}<div><h3>{E(a["name"])}</h3><p>{E(a["cover"])}</p></div></div>' for a in AREAS)
legend = ''.join(f'<li>{badge(k)}<span>{E(t)}</span></li>' for k, t in [
    ('R', 'can run on an agreed schedule after setup and testing.'),
    ('D', 'prepare suggestions for a person to assess.'),
    ('H', 'judgment or validation is required.'),
    ('C', 'a check around a release, fix or redesign.'),
])
pages.append(f'''<section class="page cover">
  <div class="cv-top"><img class="logo" src="../../assets/brand/hmm-logo-full.svg" width="150" height="69" alt="HelpMeMarketing"><span class="kick">Visual guide</span></div>
  <h1 class="cv-h">SEO Growth OS</h1>
  <p class="cv-sub">Know what is checked.<br><em>See what can be automated.</em></p>
  <p class="cv-lede">A practical guide to recurring checks, draft recommendations and progress tracking for your website.</p>
  <div class="ctiles">{tiles}</div>
  <div class="kick or">How to read this guide</div>
  <ul class="legend">{legend}</ul>
  <p class="cv-fine">Available checks and automation are confirmed during setup. Tools, access and schedules must be configured and tested. This guide is not an audit of your website.</p>
</section>''')

FLOW = [
    ('key', 'Brief & access', 'Your goals, priority pages and the tools you connect.'),
    ('search', 'Collect evidence', 'Website, search and analytics data, each dated.'),
    ('health', 'Run the checks', 'Selected checks across the six areas.'),
    ('target', 'Diagnose & prioritise', 'Shared causes combined; each fix weighed.'),
    ('pen', 'Draft & approve', 'Briefs, links and markup prepared for your approval.'),
    ('checkc', 'Verify & monitor', 'Confirm it is live, then watch for change.'),
]
DIMS = [('flag', 'Severity'), ('chart', 'Opportunity'), ('eye', 'Evidence'), ('shield', 'Risk'), ('gauge', 'Effort & readiness')]
GROUPS = ['Urgent verified issues', 'Low-risk evidenced improvements', 'Larger planned improvements',
          'Experiments with a decision rule', 'Investigations blocked by data', 'Defer or leave unchanged']
RECEIVE = [
    ('report', 'A plain-language report', 'Status and coverage for each area, findings and next actions.'),
    ('folder', 'A working record', 'Evidence, findings, decisions and changes, kept between runs.'),
    ('checkc', 'An acceptance check', 'Every recommendation says how to confirm it was done.'),
]
flow = ''.join(f'<div class="fl"><span class="fn">{n}</span><span class="fi">{icon(ic)}</span><h3>{E(t)}</h3><p>{E(d)}</p></div>'
               for n, (ic, t, d) in enumerate(FLOW, start=1))
dims = ''.join(f'<div class="dm">{icon(ic)}<span>{E(t)}</span></div>' for ic, t in DIMS)
groups = ''.join(f'<li><span class="gn">{n}</span>{E(g)}</li>' for n, g in enumerate(GROUPS, start=1))
recv = ''.join(f'<div class="rv"><span class="ci">{icon(ic)}</span><div><h3>{E(t)}</h3><p>{E(d)}</p></div></div>' for ic, t, d in RECEIVE)
pages.append(f'''<section class="page">{head("How it works", "How a run works", "Six stages, from your brief to a verified change. The next run starts from the last.", "refresh")}
  <div class="flow">{flow}</div>
  <div class="loop">{icon("refresh", "bi")}Repeat on an agreed schedule, or around a release</div>
  <div class="two">
    <div class="panel"><div class="nl">How each fix is weighed</div>
      <div class="dims">{dims}</div>
      <p class="pn">Each dimension is judged on its own. There is no single combined score.</p></div>
    <div class="panel"><div class="nl">Then grouped by what to do next</div><ol class="groups">{groups}</ol></div>
  </div>
  <div class="nl gap">What you receive</div>
  <div class="recv">{recv}</div>
  {foot(2)}</section>''')

for i, a in enumerate(AREAS, start=3):
    if a['layout'] == 'rows':
        body = f'<div class="rows">{"".join(row_card(*it) for it in a["items"])}</div>'
        if a.get('optional'):
            body += ('<div class="opt-h">Optional, when relevant to your business</div>'
                     f'<div class="grid2 opt">{"".join(grid_card(*it, inline=True) for it in a["optional"])}</div>')
    else:
        body = f'<div class="{a["layout"]}">{"".join(grid_card(*it, inline=a["layout"] == "grid2") for it in a["items"])}</div>'
    pages.append(f'<section class="page">{head(a["n"] + " / Six areas", a["name"], a["sub"], a["key"])}'
                 f'{body}{needs(a)}{foot(i)}</section>')

steps = ''.join(f'<div class="st"><span class="sn">{n:02d}</span><div><h3>{E(t)}</h3><p>{E(d)}</p></div></div>'
                for n, (t, d) in enumerate(STEPS, start=1))
pages.append(f'''<section class="page">{head("From check to action", "What a run gives you", "A real example from my own website, recorded on 10 November 2026.", "run")}
  <div class="steps">{steps}</div>
  <div class="needs"><div class="nl">Setup around your business</div>
    <p>Choose priority pages and outcomes. Connect the required data. Test the checks and handoffs. Agree a schedule and review process.</p>
    <p class="nn">Some checks need a signed-in browser and an available device. The workflow was tested on my own website. Some checks remained partial or unavailable, and the first scheduled weekly run was still pending.</p></div>
  <div class="cta"><h2>Want these checks set up for your business?</h2>
    <p>Tell me your website, the tools you use and what you want to automate.</p>
    <a href="https://helpmemarketing.com/contact?entry=seo_automation#contact-form">Enquire about SEO automation &rarr;</a></div>
  <p class="fine">Scope: designed capabilities, selected and validated during setup. No automatic publishing, guaranteed rankings or overall score. This guide does not include the underlying skill files.</p>
  <p class="fine">Basis: approved SEO Growth OS documentation and my own run record, 10 November 2026. Guide prepared 11 November 2026.</p>
  {foot(TOTAL)}</section>''')

CSS = '''
@font-face{font-family:Fraunces;font-weight:400 500;font-style:normal;src:url(../../assets/fonts/fraunces-latin.woff2) format("woff2")}
@font-face{font-family:Fraunces;font-weight:400;font-style:italic;src:url(../../assets/fonts/fraunces-italic-latin.woff2) format("woff2")}
@font-face{font-family:Inter;font-weight:400 700;src:url(../../assets/fonts/inter-latin.woff2) format("woff2")}
:root{--obsidian:#0E0E0E;--elev:#1A1A1A;--paper:#F6F5F2;--card:#FFFFFF;--line:#ECEAE4;--line2:#D4D0C6;
 --text:#0E0E0E;--body:rgba(14,14,14,.8);--muted:#4A4A4A;--ter:#6B6B6B;--cta:#FF5C1A;--cta-ink:#B8400C;--mint:#007A62;--mint-b:#00D4AA}
@page{size:Letter;margin:0}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{font-family:Inter,Arial,sans-serif;color:var(--text);-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:8.5in;height:11in;padding:.42in .6in .75in;position:relative;overflow:hidden;background:var(--paper);break-after:page;page-break-after:always}
.page:last-child{break-after:auto}
h1,h2,h3,p{margin:0}
.kick{font-size:8.5pt;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--ter)}
.kick.or{color:var(--cta)}
.kick-top{font-size:8pt;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--cta-ink);margin-bottom:12px}
.ph{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px}
.ph h1{font-family:Fraunces,Georgia,serif;font-weight:500;font-size:31pt;line-height:1.05;margin:4px 0 6px;letter-spacing:-.01em}
.lede{font-size:11pt;color:var(--muted)}
.ph-ico{width:58px;height:58px;border-radius:14px;background:rgba(255,92,26,.10);color:var(--cta);display:flex;align-items:center;justify-content:center;flex:none}
.ico-lg{width:32px;height:32px}
.badge{display:inline-block;font-size:7pt;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:3px 8px;border-radius:999px;white-space:nowrap}
.b-rep{background:rgba(0,122,98,.11);color:var(--mint)}
.b-draft{background:rgba(255,92,26,.12);color:var(--cta-ink)}
.b-human{background:#fff;color:var(--text);box-shadow:inset 0 0 0 1px var(--line2)}
.b-change{background:var(--obsidian);color:#fff}
.grid3,.grid2{display:grid;gap:8px}
.grid3{grid-template-columns:repeat(3,1fr)}
.grid2{grid-template-columns:repeat(2,1fr)}
.gc{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:11px 13px 12px;border-top:3px solid var(--cta)}
.gc h3{font-size:10.5pt;font-weight:650;margin-bottom:7px;line-height:1.25}
.gc .badge{margin-bottom:8px}
.d{font-size:8.6pt;line-height:1.45;color:var(--muted)}
.o{font-size:8.6pt;line-height:1.45;color:var(--text);margin-top:4px}
.gc .o b{font-weight:650}
.rows{display:flex;flex-direction:column;gap:8px}
.rc{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--cta);border-radius:0 12px 12px 0;padding:11px 16px 12px}
.rc-h{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:7px}
.rc-h h3{font-size:11pt;font-weight:650}
.rc-g{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.lab{font-size:7.5pt;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--ter);margin-bottom:3px}
.rc .o{margin-top:0}
.au{font-size:8.4pt;line-height:1.42;color:var(--body);margin-top:5px}
.au b{color:var(--mint)}
.au b{font-weight:650}
.rc .au{margin-top:6px;padding-top:6px;border-top:1px dashed var(--line)}
.opt-h{margin:10px 0 6px;font-size:7.5pt;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--ter)}
.opt .gc{border-top-color:var(--line2);border-style:dashed;border-top-style:solid}
.needs{margin-top:10px;background:#EFEDE7;border-radius:12px;padding:13px 16px}
.nl{font-size:7.5pt;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--cta-ink);margin-bottom:5px}
.needs p{font-size:9.2pt;line-height:1.5;color:var(--body)}
.needs .nn{font-size:8pt;color:var(--ter);margin-top:6px}
.pf{position:absolute;left:.6in;right:.6in;bottom:.4in;display:flex;justify-content:space-between;border-top:1px solid var(--line2);padding-top:8px;font-size:7.5pt;color:var(--ter);letter-spacing:.04em}
.bi{width:10px;height:10px;vertical-align:-1.5px;margin-right:4px;stroke-width:2.2}
.ci{flex:none;width:26px;height:26px;border-radius:8px;background:rgba(255,92,26,.10);color:var(--cta);display:inline-flex;align-items:center;justify-content:center}
.ci .ico{width:15px;height:15px}
.gc-h{display:flex;gap:9px;align-items:center;margin-bottom:8px}
.gc-h h3{margin:0;flex:1}
.rc-h h3{flex:1}
/* how it works */
.flow{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;counter-reset:f}
.fl{position:relative;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:13px 14px}
.fl:not(:nth-child(3n))::after{content:"";position:absolute;right:-9px;top:30px;width:8px;height:8px;border-top:2px solid var(--cta);border-right:2px solid var(--cta);transform:rotate(45deg);background:var(--paper)}
.fn{position:absolute;top:10px;right:12px;font-size:8pt;font-weight:700;color:var(--ter)}
.fi{display:inline-flex;width:34px;height:34px;border-radius:50%;background:var(--obsidian);color:#fff;align-items:center;justify-content:center;margin-bottom:8px}
.fi .ico{width:18px;height:18px}
.fl:last-child .fi{background:var(--cta)}
.fl h3{font-size:10.5pt;font-weight:650;margin-bottom:3px}
.fl p{font-size:8.6pt;line-height:1.4;color:var(--muted)}
.loop{margin:9px 0 14px;font-size:8.5pt;font-weight:600;color:var(--cta-ink);text-align:center;border:1px dashed var(--line2);border-radius:999px;padding:6px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.panel{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:13px 14px}
.dims{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin:4px 0 8px}
.dm{display:flex;align-items:center;gap:7px;font-size:8.8pt;font-weight:600;background:var(--paper);border-radius:8px;padding:6px 8px}
.dm .ico{width:15px;height:15px;color:var(--cta)}
.pn{font-size:8pt;color:var(--ter);line-height:1.4}
.groups{list-style:none;margin:4px 0 0;padding:0;display:grid;gap:5px}
.groups li{display:flex;align-items:center;gap:8px;font-size:8.8pt}
.gn{flex:none;width:18px;height:18px;border-radius:50%;background:var(--obsidian);color:#fff;font-size:7.5pt;font-weight:700;display:inline-flex;align-items:center;justify-content:center}
.groups li:first-child .gn{background:var(--cta)}
.groups li:last-child .gn{background:var(--line2);color:var(--text)}
.gap{margin-top:14px}
.recv{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.rv{display:flex;gap:10px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 13px}
.rv h3{font-size:10pt;font-weight:650;margin-bottom:3px}
.rv p{font-size:8.4pt;line-height:1.4;color:var(--muted)}
/* cover */
.cover{background:var(--obsidian);color:#fff}
.cv-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:46px}
.cv-top .kick{color:var(--cta)}
.logo{width:120px;height:auto}
.cv-h{font-family:Fraunces,Georgia,serif;font-weight:500;font-size:46pt;line-height:1;letter-spacing:-.01em}
.cv-sub{font-family:Fraunces,Georgia,serif;font-size:22pt;line-height:1.25;margin-top:14px}
.cv-sub em{font-style:italic;color:var(--cta)}
.cv-lede{font-size:11pt;line-height:1.55;color:#B3B3B3;margin:18px 0 34px;max-width:5.2in}
.ctiles{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:34px}
.ct{display:flex;gap:12px;align-items:flex-start;background:var(--elev);border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:16px}
.ct .ico{width:26px;height:26px;color:var(--cta);flex:none;margin-top:1px}
.ct h3{font-size:11pt;font-weight:650;margin-bottom:3px}
.ct p{font-size:8.8pt;color:#A3A3A3}
.legend{list-style:none;padding:0;margin:10px 0 0;display:grid;gap:8px}
.legend li{display:flex;align-items:center;gap:10px;font-size:9.2pt;color:#D9D9D9}
.legend .badge{min-width:150px;text-align:center}
.cover .b-human{background:transparent;color:#fff;box-shadow:inset 0 0 0 1px rgba(255,255,255,.35)}
.cover .b-change{background:#fff;color:var(--obsidian)}
.cover .b-rep{background:rgba(0,212,170,.14);color:var(--mint-b)}
.cover .b-draft{background:rgba(255,92,26,.18);color:#FF8A5C}
.cv-fine{position:absolute;left:.6in;right:.6in;bottom:.5in;font-size:8pt;line-height:1.5;color:#8A8A8A;border-top:1px solid rgba(255,255,255,.12);padding-top:10px}
/* run page */
.steps{display:flex;flex-direction:column;gap:9px}
.st{display:flex;gap:16px;align-items:flex-start;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.sn{flex:none;width:34px;height:34px;border-radius:50%;background:var(--obsidian);color:#fff;font-weight:700;font-size:10pt;display:flex;align-items:center;justify-content:center}
.st:last-child .sn{background:var(--cta)}
.st h3{font-size:11pt;font-weight:650;margin-bottom:3px}
.st p{font-size:9pt;line-height:1.45;color:var(--muted)}
.cta{margin-top:14px;background:var(--obsidian);color:#fff;border-radius:12px;padding:18px 20px}
.cta h2{font-family:Fraunces,Georgia,serif;font-weight:500;font-size:16pt;margin-bottom:5px}
.cta p{font-size:9.2pt;color:#B3B3B3;margin-bottom:9px}
.cta a{color:var(--cta);font-weight:700;font-size:10pt;text-decoration:none}
.fine{font-size:7.8pt;line-height:1.5;color:var(--ter);margin-top:9px}
'''

doc = f'''<!doctype html><html lang="en-CA"><head><meta charset="utf-8">
<title>SEO Growth OS visual guide | HelpMeMarketing</title><style>{CSS}</style></head>
<body>{"".join(pages)}</body></html>'''
open(os.path.join(HERE, 'seo-growth-os-visual-guide.html'), 'w').write(doc)
assert '—' not in doc
print(f"{TOTAL} pages, {sum(len(a['items']) + len(a.get('optional', [])) for a in AREAS)} capabilities")
