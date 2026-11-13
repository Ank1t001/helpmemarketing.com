#!/usr/bin/env python3
"""Generates meta-growth-os-overview.html: the Meta Growth OS PDF overview, 5 fixed US Letter pages in HMM colours.

Same layout, brand and spacing as gen_visual_guide.py (the SEO Growth OS guide), with Meta ads content.
Page 1: where to start (problem table, six areas, label legend, scope note).
Pages 2 to 4: grouped cards, each with a description and You receive.
Page 5: how a run works, how the checks stay honest, what you receive, setup and the enquiry link.
No example from a real account (founder, 2026-11-12): nothing on these pages describes a client result.
Edit the lists below, never the HTML, then render:
  python3 docs/growth-os-checklist/gen_meta_overview.py
  NODE_PATH=$(npm root -g) node docs/growth-os-checklist/build_visual_guide.mjs meta
Brand tokens follow docs/HMM_Color_System.md. No em dashes; first person singular; no capability count or score.
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

CONTACT = 'https://helpmemarketing.com/contact?entry=meta_automation#contact-form'

# Each card: title, icon, remaining label keys (Draft + review or Human review only), description, you receive.
# Scheduled check and On change are legend-only no longer: removed from the tiles (founder, 2026-11-11).
def card(t, ic, labels, desc, receive, tag=None, note=None):
    return dict(t=t, ic=ic, labels=labels, desc=desc, receive=receive, tag=tag, note=note)

PAGES = [
    dict(kicker='Tracking & reporting', title='Can the numbers in Ads Manager be trusted?', cards=[
        card('Pixel & Conversions API', 'shield', '',
             'Checks which events the pixel and Conversions API send, and flags missing or duplicate events. Some checks need Events Manager access.',
             'Tracking findings and proposed corrections, with any untested events marked unverified.'),
        card('Event match quality', 'key', '',
             'Reviews how well events are matched to the people who took the action, and which details are missing.',
             'Match quality by event and what to add.'),
        card('Conversion goal', 'target', 'H',
             'Compares the action each campaign optimises toward with the result that matters to your business. A person confirms whether a difference is intended.',
             'Mismatches between campaign goals and your business goal.'),
        card('Columns & attribution windows', 'report', 'H',
             'Checks whether your reporting columns and attribution settings show the real picture, and flags comparisons across different windows.',
             'A recommended column and attribution setup.'),
        card('Results against your records', 'database', 'H',
             'Compares leads or purchases reported by Meta with your CRM or store records.',
             'Discrepancies and an explanation of which figures are reliable.',
             tag='Optional'),
        card('Limited mode', 'folder', '',
             'Runs from exported reports when the account cannot be connected, and marks every check that could not be verified.',
             'Findings with the unverified checks clearly labelled.',
             tag='Only where it applies'),
    ]),
    dict(kicker='Creative, structure & audience', title='Where is budget being lost?', cards=[
        card('Creative performance', 'image', '',
             'Reviews how each ad attracts attention and generates responses, comparing like with like before averaging.',
             'Ads to investigate, refresh or test.'),
        card('Possible creative fatigue', 'refresh', 'H',
             'Looks for ads whose results decline week by week while similar ads hold. Other causes, such as audience or delivery changes, are checked alongside it.',
             'Ads showing possible fatigue, with the evidence and when the change began.'),
        card('Creative briefs', 'brief', 'D',
             'Drafts briefs from the diagnosis: the hook, structure, timings and claims to verify. You approve each brief before production.',
             'A brief an editor can work from.'),
        card('Campaign structure & learning status', 'sitemap', '',
             'Reviews campaign organisation, delivery and learning status, and structures that may spread budget too thinly.',
             'Structure options, with any expected learning reset and its risks explained.'),
        card('Budget split', 'gauge', 'H',
             'Reviews how budget is spread across campaigns and audiences. Budgets are never changed without your approval.',
             'Where budget is concentrated or spread thin.'),
        card('Audiences & delivery', 'users', '',
             'Reviews audience settings, exclusions, saturation and potential overlap where the available data supports it.',
             'Audience findings and proposed tests.'),
    ]),
    dict(kicker='After the click & progress', title='Do the ads bring customers, and is the work moving forward?', cards=[
        card('Funnel & post-click', 'click', 'H',
             'Reviews what happens after the click, using your funnel stages described in your own words.',
             'Where people drop off between the click and becoming a customer.'),
        card('Lead quality & customer value', 'database', 'H',
             'Connects leads or orders to outcomes from your CRM or store to show which campaigns produce customers.',
             'Campaigns compared by customers and value, not just leads.',
             tag='Optional'),
        card('Priorities & draft actions', 'target', 'D',
             'Connects related findings by cause and ranks them by impact, effort and the strength of the evidence. You decide what proceeds.',
             'What to fix, test, investigate or leave unchanged.'),
        card('Change preparation', 'pen', 'D',
             'Drafts recommendations, briefs and tracking specifications. Where supported, new campaigns and ad sets are prepared paused until you approve them.',
             'Drafted changes ready for your approval.'),
        card('Baseline & monitoring', 'checkc', '',
             'Records a baseline once approved changes are live, with an indicator to watch for each, then compares later runs against it, accounting for learning status and sample size.',
             'What changed since the baseline and what needs attention.'),
        card('Change record & progress summary', 'history', 'D',
             'Records findings, decisions and completed work, then drafts an update for your review.',
             'A concise summary of progress, open issues and approvals needed.'),
    ]),
]

STAGES = [
    ('Establish the starting point', ['Understand your business', 'Check access and data', 'Verify tracking']),
    ('Find and plan improvements', ['Audit the account', 'Diagnose the problems', 'Prioritise the work']),
    ('Prepare, verify and monitor', ['Prepare changes', 'Baseline approved changes', 'Monitor and report']),
]

START = [
    ('Ads Manager and your sales do not match', 'Tracking, attribution and reporting', 'shield'),
    ('Your cost per result keeps rising', 'Creative, structure, audience and tracking', 'chart'),
    ('Ads seem to stop working after a few weeks', 'Creative and audience checks', 'refresh'),
    ('Plenty of leads, but few become customers', 'Customer journey and lead quality', 'click'),
    ('Account changes keep causing new problems', 'Change monitoring against a baseline', 'checkc'),
]

AREAS = [
    ('shield', 'Tracking & conversions', 'Events, duplicates, goals.'),
    ('image', 'Creative performance', 'Attention and responses.'),
    ('sitemap', 'Structure & budgets', 'Delivery and learning.'),
    ('users', 'Audiences & delivery', 'Exclusions and overlap.'),
    ('report', 'Reporting & attribution', 'Metrics and windows.'),
    ('click', 'Customer journey & value', 'Outcomes after the click.'),
]

TOTAL = 2 + len(PAGES)

def foot(i):
    return (f'<footer class="pf"><span>Meta Growth OS PDF overview &middot; HelpMeMarketing</span>'
            f'<span>{i} / {TOTAL}</span></footer>')

def para(key, cls, ic, text):
    i = icon(ic, 'bi') if ic else ''
    return f'<p class="{cls}"><b>{i}{key}</b> {E(text)}</p>'

def render_card(c):
    tag = f'<span class="tag">{E(c["tag"])}</span>' if c['tag'] else ''
    badges = ''.join(badge(k) for k in c['labels'])
    row = f'<div class="cd-b">{badges}{tag}</div>' if (badges or tag) else ''
    note = f'<p class="cn">{E(c["note"])}</p>' if c['note'] else ''
    return (f'<div class="cd"><div class="cd-h"><span class="ci">{icon(c["ic"])}</span><h3>{E(c["t"])}</h3></div>{row}'
            f'<p class="cd-d">{E(c["desc"])}</p>'
            f'<p class="k-rec"><b>You receive:</b> {E(c["receive"])}</p>{note}</div>')

pages = []

# Page 1: where should you start?
rows = ''.join(f'<tr><td>{E(a)}</td><td><span class="st-ic">{icon(ic)}</span>{E(b)}</td></tr>' for a, b, ic in START)
areas = ''.join(f'<div class="ar"><span class="ci">{icon(ic)}</span><div><h3>{E(t)}</h3><p>{E(d)}</p></div></div>' for ic, t, d in AREAS)
legend = ''.join(f'<tr><td>{badge(k)}</td><td>{E(L[k][3])}</td></tr>' for k in 'DH')
pages.append(f'''<section class="page">
  <div class="intro">
    <div class="intro-top"><img class="logo" src="../../assets/brand/hmm-logo-full.svg" width="150" height="69" alt="HelpMeMarketing"><span>Meta Growth OS PDF overview</span></div>
    <h1>Meta Growth OS</h1>
    <p class="intro-sub"><em>Find what is holding your Meta ads back.</em></p>
    <p class="intro-lede">Explore how Meta Growth OS identifies tracking issues, finds performance gaps and prioritises what needs attention.</p>
  </div>
  <div class="grp"><h2 class="sh">Where should you start?</h2>
  <table class="start"><thead><tr><th>What you are experiencing</th><th>Where to look first</th></tr></thead><tbody>{rows}</tbody></table></div>
  <div class="grp"><h2 class="sh">Six specialist areas</h2>
  <div class="areas">{areas}</div></div>
  <div class="grp"><h2 class="sh">How to read the labels</h2>
  <table class="legend">{legend}</table></div>
  <p class="scope">Checks depend on your ad account, connected tools and data. Automation is configured during setup, and you approve changes before anything goes live.</p>
  {foot(1)}</section>''')

for n, pg in enumerate(PAGES, start=2):
    cards = ''.join(render_card(c) for c in pg['cards'])
    pages.append(f'''<section class="page">
  <header class="ph"><div class="kick">{E(pg["kicker"])}</div><h1>{E(pg["title"])}</h1></header>
  <div class="cards">{cards}</div>
  {foot(n)}</section>''')

# Page 5: how it works and next step
flow = ''.join(f'<div class="frow"><div class="frow-h">{E(g)}</div>' +
               ''.join(f'<div class="fs"><span class="fn">{gi * 3 + si + 1}</span><h3>{E(t)}</h3></div>' for si, t in enumerate(steps)) + '</div>'
               for gi, (g, steps) in enumerate(STAGES))
pages.append(f'''<section class="page">
  <header class="ph"><div class="kick">How it works & next step</div><h1>From a finding to a clear next action</h1></header>
  <div class="grp"><div class="flow3">{flow}</div>
  <p class="flow-note">{icon("refresh", "bi")}Each stage builds on the evidence before it. Checks repeat on an agreed schedule, and proposed changes come to you for approval.</p></div>
  <div class="example"><div class="ex-h"><span class="nl">How the checks stay honest</span></div>
    <p>Tracking problems are identified before affected results are used to judge performance, and a data source that is not connected is marked as unchecked, never estimated.</p>
    <p>Performance recommendations account for learning status and sample size. Proposed changes need your approval, and each one is recorded with a baseline once it is live.</p></div>
  <div class="two">
    <div class="panel"><h2 class="ph2">{icon("report", "ico-s")}What you receive</h2><ul>
      <li>A clear report with findings and priorities.</li>
      <li>Draft briefs or recommendations for review.</li>
      <li>A dated record of decisions and changes.</li>
      <li>A baseline and an indicator to watch for each approved change.</li></ul></div>
    <div class="panel"><h2 class="ph2">{icon("key", "ico-s")}What setup needs</h2><ul>
      <li>Access to your Meta ad account, or exported reports.</li>
      <li>Your goals and what a result is worth to you.</li>
      <li>Your CRM or store, where results should be checked against customers.</li>
      <li>A Google Drive folder for the account record.</li></ul>
      <p class="pn">Requirements are confirmed during setup, before the first run.</p></div>
  </div>
  <div class="cta"><h2>Want these checks set up for your ad account?</h2>
    <p>Tell me about your ad account, the tools you use and what you want to automate.</p>
    <a href="{CONTACT}">Enquire about Meta ads automation &rarr;</a></div>
  {foot(TOTAL)}</section>''')

CSS = '''
@font-face{font-family:Fraunces;font-weight:400 500;font-style:normal;src:url(../../assets/fonts/fraunces-latin.woff2) format("woff2")}
@font-face{font-family:Fraunces;font-weight:400;font-style:italic;src:url(../../assets/fonts/fraunces-italic-latin.woff2) format("woff2")}
@font-face{font-family:Inter;font-weight:400 700;src:url(../../assets/fonts/inter-latin.woff2) format("woff2")}
:root{--s1:4px;--s2:8px;--s3:12px;--s4:16px;--s5:24px;--pad:16px 20px;--gap:16px;--r:12px;--obsidian:#0E0E0E;--elev:#1A1A1A;--paper:#F6F5F2;--card:#FFFFFF;--line:#ECEAE4;--line2:#D4D0C6;
 --text:#0E0E0E;--body:rgba(14,14,14,.82);--muted:#4A4A4A;--ter:#6B6B6B;--cta:#FF5C1A;--cta-ink:#B8400C;--mint:#007A62}
@page{size:Letter;margin:0}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{font-family:Inter,Arial,sans-serif;color:var(--text);font-size:10pt;line-height:1.38;-webkit-print-color-adjust:exact;print-color-adjust:exact}
/* Spacing scale 4/8/12/16/24: same page margins, 24px between blocks, 12px from a heading to its block, 16px grid gaps, 16px 20px box padding, 12px radius. */
.page{width:8.5in;height:11in;padding:.5in .55in .7in;position:relative;overflow:hidden;background:var(--paper);break-after:page;page-break-after:always;display:flex;flex-direction:column;gap:var(--s5)}
.grp{display:flex;flex-direction:column;gap:var(--s3)}
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
.pf{position:absolute;left:.55in;right:.55in;bottom:.35in;display:flex;justify-content:space-between;border-top:1px solid var(--line2);padding-top:var(--s2);font-size:8pt;color:var(--ter)}
/* page 1 */
.intro{background:var(--obsidian);color:#fff;border-radius:var(--r);padding:20px}
.intro-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--s2)}
.intro-top span{font-size:8pt;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--cta)}
.logo{width:84px;height:auto}
.intro h1{font-family:Fraunces,Georgia,serif;font-weight:500;font-size:28pt;line-height:1.05}
.intro-sub{font-family:Fraunces,Georgia,serif;font-size:17pt;margin-top:var(--s1)}
.intro-sub em{color:var(--cta)}
.intro-lede{font-size:10.5pt;color:#C7C7C7;margin-top:var(--s2);max-width:5.6in}
.sh{font-family:Fraunces,Georgia,serif;font-weight:500;font-size:14.5pt;line-height:1.2}
table{border-collapse:collapse;width:100%}
.start,.legend{background:var(--card);border:1px solid var(--line);border-radius:var(--r);border-collapse:separate;border-spacing:0;overflow:hidden}
.start th{text-align:left;font-size:8pt;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--ter);padding:var(--s2) 20px;border-bottom:1px solid var(--line);background:#FBFAF7}
.start td,.legend td{padding:var(--s2) 20px;border-bottom:1px solid var(--line);vertical-align:middle}
.start tr:last-child td,.legend tr:last-child td{border-bottom:0}
.start td:first-child{width:48%;color:var(--body)}
.start td:last-child{font-weight:600}
.st-ic{display:inline-flex;vertical-align:-4px;margin-right:var(--s2);color:var(--cta)}
.areas{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--gap)}
.ar{display:flex;gap:var(--s3);align-items:center;background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:var(--s3) var(--s4)}
.ar h3{font-size:10pt;font-weight:650}
.ar p{font-size:8.5pt;color:var(--muted);line-height:1.3}
.legend td{color:var(--body)}
.legend td:first-child{width:180px}
.scope{padding:var(--pad);border-left:3px solid var(--cta);background:#EFEDE7;border-radius:0 var(--r) var(--r) 0;color:var(--body)}
/* card pages */
.ph{display:flex;flex-direction:column;gap:var(--s1)}
.ph h1{font-family:Fraunces,Georgia,serif;font-weight:500;font-size:21pt;line-height:1.15}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:var(--gap)}
.cd{background:var(--card);border:1px solid var(--line);border-top:3px solid var(--cta);border-radius:var(--r);padding:var(--pad);break-inside:avoid;display:flex;flex-direction:column}
.cd-h{display:flex;gap:var(--s3);align-items:center}
.cd-h h3{font-size:11.5pt;font-weight:650;line-height:1.25}
.cd-b{display:flex;flex-wrap:wrap;gap:var(--s2);margin-top:var(--s3)}
.cd p{color:var(--body)}
.cd-d{margin-top:var(--s3);font-size:11pt;line-height:1.5}
.cd p b{font-weight:650;color:var(--text);margin-right:2px}
.k-auto b{color:var(--mint)!important}
.k-rev b{color:var(--muted)!important}
.k-rec{padding-top:var(--s3);margin-top:var(--s3);border-top:1px solid var(--line);font-size:11pt;line-height:1.5}
.k-rec b{color:var(--cta-ink)!important}
.cn{margin-top:var(--s2);font-size:8.5pt;color:var(--ter)!important;font-style:italic}
/* page 5 */
.flow3{display:flex;flex-direction:column;gap:var(--s2)}
.frow{display:grid;grid-template-columns:1.25fr 1fr 1fr 1fr;gap:var(--s2);align-items:stretch}
.frow-h{display:flex;align-items:center;padding:0 var(--s3);border-radius:var(--r);background:var(--obsidian);color:#fff;font-weight:650;font-size:9.5pt;line-height:1.25}
.frow:last-child .frow-h{background:var(--cta);color:var(--obsidian)}
.fs{display:flex;align-items:center;gap:var(--s2);background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:10px var(--s3)}
.fs .fn{flex:none;width:22px;height:22px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;margin:0;background:rgba(255,92,26,.12);color:var(--cta-ink);font-size:8.5pt}
.fs h3{font-size:9.5pt;font-weight:650;line-height:1.25}
.fl{position:relative;background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:16px 8px;text-align:center}
.fl:not(:last-child)::after{content:"";position:absolute;right:-9px;top:28px;width:7px;height:7px;border-top:2px solid var(--cta);border-right:2px solid var(--cta);transform:rotate(45deg);background:var(--paper);z-index:1}
.fi{display:inline-flex;width:32px;height:32px;border-radius:50%;background:var(--obsidian);color:#fff;align-items:center;justify-content:center}
.fl:last-child .fi{background:var(--cta)}
.fn{display:block;font-size:7.5pt;font-weight:700;color:var(--ter);margin-top:var(--s2)}
.fl h3{font-size:9.5pt;font-weight:650;line-height:1.2;margin-top:2px}
.flow-note{font-size:9.5pt;color:var(--cta-ink);text-align:center}
.example{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--mint);border-radius:0 var(--r) var(--r) 0;padding:var(--pad)}
.ex-h{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:var(--s2)}
.nl{font-size:8.5pt;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--mint)}
.ex-date{font-size:8.5pt;color:var(--ter)}
.example p{color:var(--body)}
.example p+p{margin-top:var(--s2)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:var(--gap)}
.panel{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:var(--pad)}
.ph2{font-family:Fraunces,Georgia,serif;font-weight:500;font-size:13.5pt;margin-bottom:var(--s3)}
.panel ul{padding-left:17px;color:var(--body)}
.panel li+li{margin-top:var(--s2)}
.panel li::marker{color:var(--cta)}
.nw{white-space:nowrap}
.pn{margin-top:var(--s3);font-size:9pt;color:var(--ter)}
.cta{background:var(--obsidian);color:#fff;border-radius:var(--r);padding:20px}
.cta h2{font-family:Fraunces,Georgia,serif;font-weight:500;font-size:16pt;margin-bottom:var(--s1)}
.cta p{color:#C7C7C7;margin-bottom:var(--s3)}
.cta a{color:var(--cta);font-weight:700;font-size:11pt;text-decoration:none}
'''

doc = f'''<!doctype html><html lang="en-CA"><head><meta charset="utf-8">
<title>Meta Growth OS PDF Overview | HelpMeMarketing</title><style>{CSS}</style></head>
<body>{"".join(pages)}</body></html>'''
open(os.path.join(HERE, 'meta-growth-os-overview.html'), 'w').write(doc)
assert '—' not in doc
print(f'{TOTAL} pages')
