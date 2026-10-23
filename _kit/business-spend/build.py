#!/usr/bin/env python3
"""Build the Business Cards & Spend Management Index page and its curated CSV.

  python3 build.py            render business-spend-index.html and the CSV
  python3 build.py --check    render in memory and fail if either output differs

The page and the CSV come from the same files (edition.json, platforms.json,
sources.json, observations.json, narrative.json) and the build reads no clock,
so the same inputs always give the same bytes. A rebuild never changes a date.
"""
import csv
import html
import io
import json
import os
import sys
from datetime import datetime

import model
import validate

PAGE = os.path.join(model.ROOT, 'business-spend-index.html')
CSV_REL = 'assets/index/business-spend/business-spend-index-edition-001-observations.csv'
CSV_PATH = os.path.join(model.ROOT, CSV_REL)
SITE = 'https://helpmemarketing.com'

CAT_LABEL = {
    'card_model': 'Card model and funding', 'network_issuer': 'Network and issuer', 'card_format': 'Card formats',
    'rewards': 'Rewards', 'plans': 'Plans', 'spend_controls': 'Spend controls', 'eligibility': 'Eligibility',
    'availability': 'Availability', 'xb_card_spending': 'Card spending in another currency', 'xb_fx': 'FX conversion',
    'xb_accounts': 'Multi-currency accounts', 'xb_transfers': 'Transfers', 'registration': 'Registration as stated',
    'funds_holding': 'Where funds are held, as stated', 'positioning': 'Positioning', 'proof': 'Proof',
    'case_study': 'Case study', 'journey': 'Application or demo journey', 'page_quality': 'Page rendering',
    'registry_entry': 'Registry entry (checked by me)', 'approvals': 'Approvals', 'expense_workflow': 'Receipts and expenses',
    'accounting': 'Accounting connections',
}
LAYER_LABEL = {'product': 'Product context', 'cross_border': 'Cross-border context', 'marketing': 'Marketing execution'}
METHOD_LABEL = {'server_fetch': 'server fetch, no JavaScript', 'browser': 'browser capture (Chrome)', 'manual_document_review': 'document review'}
E = lambda s: html.escape(s, quote=True)


def page_label(url):
    u = url.split('://', 1)[1].split('?')[0].rstrip('/')
    return u[4:] if u.startswith('www.') else u


def toronto_time(ts):
    d = datetime.fromisoformat(ts)
    h = d.hour % 12 or 12
    return '%d:%02d %s' % (h, d.minute, 'a.m.' if d.hour < 12 else 'p.m.')


def long_date(ts):
    d = datetime.fromisoformat(ts)
    return '%d %s %d' % (d.day, ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                                 'October', 'November', 'December'][d.month - 1], d.year)


class Ctx:
    def __init__(self):
        self.edition = model.load('edition.json')
        p = model.load('platforms.json')
        self.order = p['order']
        self.plats = p['platforms']
        self.sources = {s['id']: s for s in model.load('sources.json')['sources']}
        self.obs = {o['id']: o for o in model.load('observations.json')['observations']}
        self.n = model.load('narrative.json')
        # draft (staging), release (the live page) or snapshot (the fixed edition copy)
        self.mode = 'draft' if self.edition['status'] == 'draft' else 'release'
        self.release_date = (self.edition.get('published_at') or '')[:10] or None
        self.date_modified = self.edition.get('modified_at')

    def name(self, pid):
        return self.plats[pid]['name']

    def obs_for(self, pid):
        return [o for o in self.obs.values() if o['platform'] == pid]


def status_tag(status, always=False):
    if status == 'published' and not always:
        return ''
    return '<span class="st st-%s">%s</span>' % (status, E(model.STATUSES[status]))


def ev_links(c, ids):
    parts = []
    for i in ids:
        o = c.obs[i]
        parts.append('<a href="#ev-%s">%s, %s</a>' % (i, E(c.name(o['platform'])), E(CAT_LABEL[o['category']].lower())))
    return '<p class="evlinks"><b>Evidence:</b> %s</p>' % '; '.join(parts)


def take(text):
    return ('<div class="note take"><span class="lbl">What this means for your marketing team</span><p>%s</p></div>' % E(text))


def gap_note(what):
    return ('<div class="note take gap"><span class="lbl">What this means for your marketing team</span>'
            '<p><b>Evidence placeholder.</b> %s</p></div>' % E(what))


def cell(c, pid, key, label):
    spec = c.n['compare']['rows'][pid][key]
    ids = spec.get('ids', [])
    statuses = [c.obs[i]['status'] for i in ids]
    if not ids:
        status = 'not_checked'
    elif 'conflicting' in statuses:
        status = 'conflicting'
    elif spec.get('text') is None:
        status = statuses[0]
    elif 'explicitly_unavailable' in statuses:
        status = 'explicitly_unavailable'
    else:
        status = 'published'
    if spec.get('text') is None:
        body = '<span class="cell-main">%s</span>' % E(model.STATUSES[status])
        cls = ' class="miss"'
        tag = ''
    else:
        body = '<span class="cell-main">%s</span>' % E(spec['text'])
        if spec.get('sub'):
            body += '<span class="cell-sub">%s</span>' % E(spec['sub'])
        cls = ''
        tag = status_tag(status)
    if any('D' in (c.obs[i].get('reconciliation') or {}).get('class', '') for i in ids):
        tag += '<span class="st st-undetermined">Not determined</span>'
    return '<td%s data-label="%s">%s%s</td>' % (cls, E(label), body, tag)


def table(c, title, cols, tid):
    head = ''.join('<th scope="col">%s</th>' % E(l) for _, l in cols)
    rows = []
    for pid in c.order:
        cells = ''.join(cell(c, pid, k, l) for k, l in cols)
        rows.append('<tr><td class="brandcell"><a href="#bs-p-%s">%s</a></td>%s</tr>' % (pid, E(c.name(pid)), cells))
    return ('<div class="tblock"><h3 id="%s-h">%s</h3>'
            '<div class="tw cards" tabindex="0" role="region" aria-labelledby="%s-h"><table class="bs">'
            '<caption class="sr-only">%s for six platforms, as published on 23 October 2026</caption>'
            '<thead><tr><th scope="col">Platform</th>%s</tr></thead><tbody>\n%s\n</tbody></table></div></div>'
            % (tid, E(title), tid, E(title), head, '\n'.join(rows)))


def compare_sources(c):
    items = []
    cols = c.n['compare']['product_columns'] + c.n['compare']['xb_columns'] + c.n['compare']['spend_columns']
    for pid in c.order:
        parts = []
        for k, l in cols:
            ids = c.n['compare']['rows'][pid][k].get('ids', [])
            if ids:
                parts.append('%s: %s' % (E(l), ', '.join('<a href="#ev-%s">%s</a>' % (i, i) for i in ids)))
            else:
                parts.append('%s: not checked' % E(l))
        items.append('<li><b>%s.</b> %s</li>' % (E(c.name(pid)), '; '.join(parts)))
    return ('<details class="ri-adv srcs"><summary>Where each entry comes from</summary>'
            '<p class="dek">Each entry links to the observation it summarises, with the exact wording, the page and the capture time.</p>'
            '<ul class="evlist">%s</ul></details>' % ''.join(items))


def ev_item(c, o):
    src_html = []
    for ref in o['sources']:
        s = c.sources[ref['source_id']]
        src_html.append('<blockquote>%s</blockquote><span class="src"><a href="%s" rel="noopener nofollow" target="_blank">%s</a> &middot; captured %s, %s Toronto time &middot; %s</span>'
                        % (E(ref['excerpt']), E(s['final_url']), E(page_label(s['final_url'])), long_date(s['fetched_at']),
                           toronto_time(s['fetched_at']), METHOD_LABEL[s['method']]))
    if o['status'] == 'not_found':
        rev = [c.sources[s] for s in o['reviewed_sources']]
        src_html.append('<span class="src">Pages reviewed: %s</span>' % ', '.join(
            '<a href="%s" rel="noopener nofollow" target="_blank">%s</a>' % (E(s['final_url']), E(page_label(s['final_url']))) for s in rev))
    extra = ''
    if o['conditions']:
        extra += '<span class="interp"><b>Conditions:</b> %s</span>' % E(o['conditions'])
    for cf in o['conflicts']:
        extra += '<span class="interp"><b>Unresolved difference:</b> %s</span>' % E(cf['note'])
    if o.get('reconciliation'):
        extra += '<span class="interp"><b>Reconciliation:</b> %s</span>' % E(recon_text(o['reconciliation']))
    if o['interpretation']:
        extra += '<span class="interp"><b>My reading:</b> %s</span>' % E(o['interpretation'])
    return ('<li id="ev-%s"><span class="cat">%s</span> %s<br>%s%s%s</li>'
            % (o['id'], E(CAT_LABEL[o['category']]), status_tag(o['status'], True), E(o['statement']), extra, ''.join(src_html)))


def recon_text(r):
    labels = ' and '.join('%s (%s)' % (k, model.RECON_LABEL[k].lower()) for k in r['class'].split(' and '))
    return 'class %s. %s' % (labels, r['note'])


def recon_details(c):
    rows = []
    order = {p: i for i, p in enumerate(c.order)}
    for o in sorted((o for o in c.obs.values() if o.get('reconciliation')), key=lambda o: (order[o['platform']], o['id'])):
        r = o['reconciliation']
        rows.append('<tr><td data-label="Platform">%s</td><td data-label="Difference"><a href="#ev-%s">%s</a></td><td data-label="Class">%s</td><td data-label="Why" class="wrap-cell">%s</td></tr>'
                    % (E(c.name(o['platform'])), o['id'], E(r['topic']), E(r['class']), E(r['note'])))
    legend = '; '.join('%s: %s' % (k, v) for k, v in sorted(model.RECON_LABEL.items()))
    return ('<details class="ri-adv srcs" id="bs-recon"><summary>How the %d reported differences were reconciled</summary>'
            '<p class="dek">After the first reading, a browser pass compared each pair of statements by product, transaction, country and customer, plan, currency, dates and conditions. Classes: %s. Both statements stay in the evidence for every item.</p>'
            '<div class="tw cards" tabindex="0" role="region" aria-label="Reconciliation of the reported differences"><table class="bs"><thead><tr><th scope="col">Platform</th><th scope="col">Difference</th><th scope="col">Class</th><th scope="col">Why</th></tr></thead><tbody>%s</tbody></table></div></details>'
            % (len(rows), E(legend), ''.join(rows)))


def platform_block(c, pid):
    p = c.n['platforms'][pid]
    obs = sorted(c.obs_for(pid), key=lambda o: o['id'])
    times = sorted({o['observed_at'] for o in obs if o['observed_at']}, key=model.parse_ts)
    pages = sorted({s for o in obs for s in [r['source_id'] for r in o['sources']] + o.get('reviewed_sources', [])})
    rows = [('Who it is for and the main promise', p['positioning']), ('Offer and its conditions', p['offer']),
            ('Funding, rewards and FX explained', p['explanation']), ('Published proof', p['proof']),
            ('Next step observed', p['journey'])]
    dl = ''.join('<dt>%s</dt><dd>%s</dd>' % (E(a), E(b)) for a, b in rows)
    missing = p['missing']
    miss = ('<p class="dek"><b>Missing evidence.</b> %s.</p>' % E('; '.join(missing))) if missing else '<p class="dek"><b>Missing evidence.</b> None identified in this edition.</p>'
    tk = take(p['take']) if p.get('take') else gap_note('This takeaway is waiting for evidence: %s.' % '; '.join(missing))
    nb = sum(1 for x in pages if c.sources[x]['method'] == 'browser')
    when = 'Observed %s, %s to %s Toronto time, from %d server captures and %d browser captures.' % (
        long_date(times[0]), toronto_time(times[0]), toronto_time(times[-1]), len(pages) - nb, nb)
    return ('<div class="card plat" id="bs-p-%s"><h3>%s</h3><dl>%s</dl>'
            '<p class="dek"><b>Editorial observation.</b> %s</p>%s%s'
            '<details class="ri-adv srcs"><summary>Sources and exact wording for %s (%d observations)</summary><ul class="evlist">%s</ul></details>'
            '<p class="pnote">%s</p></div>'
            % (pid, E(c.name(pid)), dl, E(p['observation']), miss, tk, E(c.name(pid)), len(obs),
               ''.join(ev_item(c, o) for o in obs), E(when)))


def iso_long(day):
    return long_date(day + 'T12:00:00-04:00')


def snapshot_url(c):
    return '%s/edition-%s' % (c.edition['canonical'], c.edition['edition'])


def cite_and_editions(c):
    ed = c.edition
    start, end = ed['collection_started_at'], ed['collection_ended_at']
    snap = '/' + snapshot_url(c).split('.com/', 1)[1]
    return ('<div class="card" id="bs-cite"><h4>Cite this research</h4>'
            '<p class="dek">Ankit Kumar, Help Me Marketing. <em>Business Cards &amp; Spend Management Index</em> (The HMM Index). Edition %s. Public pages captured %s. <a href="%s">%s</a></p>'
            '<p class="dek m0">For a fixed version, cite the <a href="%s">edition %s snapshot</a>. <a href="#bs-editions">Edition history</a></p></div>'
            '<section id="bs-editions"><details class="ri-adv"><summary>Edition history</summary>'
            '<div class="tw" tabindex="0" role="region" aria-label="Edition history, scrolls sideways"><table><thead><tr><th scope="col">Edition</th><th scope="col">Dates</th><th scope="col">What it covered</th></tr></thead><tbody>'
            '<tr><td><b>%s</b> (this page)</td><td class="wrap-cell">Published %s. Public pages captured %s, %s to %s Toronto time. <a href="%s">Snapshot</a></td>'
            '<td class="wrap-cell">First edition: how six selected platforms explain business cards, spend management and cross-border payments, read from public pages and enquiry journeys. No refresh is scheduled.</td></tr>'
            '</tbody></table></div><p class="pnote">This address shows the latest edition. Each published edition keeps a snapshot at a fixed address.</p></details></section>'
            % (E(ed['edition']), long_date(start), E(ed['canonical']), E(ed['canonical']), snap, E(ed['edition']),
               E(ed['edition']), E(iso_long(c.release_date)), long_date(start), toronto_time(start), toronto_time(end), snap))


def body(c):
    n, ed = c.n, c.edition
    h = n['hero']
    start, end = ed['collection_started_at'], ed['collection_ended_at']
    when = '%s, %s to %s Toronto time' % (long_date(start), toronto_time(start), toronto_time(end))
    draft = c.mode == 'draft'
    out = ['<!-- ===== BUSINESS SPEND INDEX REPORT BODY START ===== generated by _kit/business-spend/build.py; edit the kit, not this page ===== -->', '<div class="wrap">']
    out.append('<header><p class="kicker">%s</p><h1>%s</h1><p class="lede">%s</p><p class="scope">%s</p>' % (E(h['kicker']), E(h['title']), E(h['subtitle']), E(h['scope'])))
    out.append('<div class="byline"><span><b>Observed</b> %s</span><span>Research and analysis by <b><a href="/about">Ankit Kumar</a></b> &middot; Founder, <a href="/">HMM</a></span></div>' % E(when))
    out.append('<div class="livebar">%s<span>Edition <b>%s</b></span><span>%s</span></div>' % (
        '<span class="draft-flag">Draft</span>' if draft else '', E(ed['edition']), 'Not yet published' if draft else 'Published <b>%s</b>' % E(iso_long(c.release_date))))
    out.append('<p class="hero-act"><a class="btn btn-outline" href="%s">%s</a></p>' % (E(h['action']['href']), E(h['action']['label'])))
    if draft:
        out.append('<p class="pnote">%s</p>' % E(h['draft_note']))
    out.append('</header>')
    out.append('<nav class="ri-nav" aria-label="On this page"><a href="#bs-findings">What stood out</a><a href="#bs-compare">Comparison</a><a href="#bs-examples">Examples</a><a href="#bs-platforms">Each platform</a><a href="#bs-patterns">Patterns</a><a href="#bs-tests">Tests to run</a><a href="#bs-method">Method</a></nav>')

    f = n['findings']
    items = []
    for it in f['items']:
        items.append('<div class="find"><span class="q">%s</span><h3>%s</h3><p class="dek">%s <b>Denominator:</b> %s</p>%s</div>' % (
            E(it['question']), E(it['title']), E(it['body']), E(it['denominator']), ev_links(c, it['evidence'])))
    out.append('<section id="bs-findings"><div class="sec-head"><h2>What stood out</h2><p class="dek">%s</p></div><div class="card">%s%s</div></section>' % (
        E(f['dek']), ''.join(items), take(f['take'])))

    cp = n['compare']
    out.append('<section id="bs-compare"><div class="sec-head"><h2>The six platforms at a glance</h2><p class="dek">%s</p></div>' % E(cp['dek']))
    out.append(table(c, 'Product context', cp['product_columns'], 'bs-prod'))
    out.append(table(c, 'Cross-border context', cp['xb_columns'], 'bs-xb'))
    out.append(table(c, 'Spend-management context', cp['spend_columns'], 'bs-spend'))
    out.append('<p class="pnote"><b>Reading the table.</b> %s An entry with a status label is not a plain published fact; <a href="#bs-statuses">what each status means</a>. &ldquo;Not determined&rdquo; is not a status: it marks two published statements whose relationship the evidence cannot settle (<a href="#bs-recon">reconciliation</a> class D).</p>' % E(cp['note']))
    out.append(compare_sources(c))
    out.append('<p class="pnote dlinks"><b>Download the data:</b> <a href="/%s" download>every observation with its source (CSV)</a>.</p></section>' % CSV_REL)

    ex = n['examples']
    exs = ''.join('<div class="card ex"><span class="kind">%s &middot; %s</span><h3>%s</h3><p class="dek">%s</p><p class="dek m0"><b>Why it is useful:</b> %s</p>%s</div>' % (
        E(e['kind']), E(c.name(e['platform'])), E(e['title']), E(e['body']), E(e['lesson']), ev_links(c, e['evidence'])) for e in ex['items'])
    out.append('<section id="bs-examples"><div class="sec-head"><h2>Selected communication examples</h2><p class="dek">%s</p></div>%s</section>' % (E(ex['dek']), exs))

    out.append('<section id="bs-platforms"><div class="sec-head"><h2>Platform by platform</h2><p class="dek">The same five questions for each platform, in the order Venn, Float, Ramp, Loop, Keep, Airwallex. The summary is first; the exact wording and sources are in each expander.</p></div>')
    out += [platform_block(c, pid) for pid in c.order]
    out.append('</section>')

    pt = n['patterns']
    pts = ''.join('<p class="dek"><b>%s.</b> %s%s <b>Denominator:</b> %s</p>%s' % (
        E(x['title']), E(x['body']), (' <b>Exceptions:</b> %s' % E(x['exceptions'])) if x['exceptions'] else '', E(x['denominator']), ev_links(c, x['evidence'])) for x in pt['items'])
    out.append('<section id="bs-patterns"><div class="sec-head"><h2>Patterns across the six</h2><p class="dek">%s</p></div><div class="card">%s%s</div></section>' % (E(pt['dek']), pts, take(pt['take'])))

    ts = n['tests']
    labels = [('example', 'Observed example'), ('uncertainty', 'Customer uncertainty'), ('change', 'Change, and what stays the same'),
              ('measure', 'Primary measure'), ('guardrail', 'Quality guardrail'), ('comparison', 'Comparison method'), ('limitation', 'When the result would be inconclusive')]
    lis = ''.join('<li><b>%s</b> <span class="evlinks">(from finding %s)</span><dl>%s</dl></li>' % (
        E(t['title']), E(t['finding'][1:]), ''.join('<dt>%s</dt><dd>%s</dd>' % (E(l), E(t[k])) for k, l in labels)) for t in ts['items'])
    out.append('<section id="bs-tests"><div class="sec-head"><h2>Three tests for a marketing team</h2><p class="dek">%s</p></div><div class="card"><ol class="tests">%s</ol>'
               '<p class="pnote m0">There are no baselines, uplift figures or sample sizes here on purpose: they depend on your own traffic and data.</p></div></section>' % (E(ts['dek']), lis))

    m = n['method']
    st = ''.join('<dt>%s</dt><dd>%s</dd>' % (E(a), E(b)) for a, b in m['statuses'])
    lim = ''.join('<li>%s</li>' % E(x) for x in m['limitations'])
    rel = ed['relationship_disclosure']
    if rel['status'] == 'complete':
        rel_html = '<p class="dek m0">%s</p>' % E(rel['text'])
    else:
        rel_html = ('<div class="note gap"><span class="lbl">Placeholder</span><p>Relationship disclosure pending. Before publication I will state here whether '
                    'I or Help Me Marketing have any commercial connection with any of the six providers.</p></div>')
    nobs = len(c.obs)
    nsrc = len(c.sources)
    nbr = sum(1 for x in c.sources.values() if x['method'] == 'browser')
    out.append('<section id="bs-method"><div class="sec-head"><h2>How this research was done</h2></div>'
               '<div class="card"><h3>Selection</h3><p class="dek">%s</p><h3>Dates</h3><p class="dek">%s</p><h3>Public sources only</h3><p class="dek">%s</p>'
               '<h3 id="bs-statuses">What each status means</h3><dl class="statdefs">%s</dl><h3>Limitations</h3><ul class="dek">%s</ul>'
               '<p class="pnote">%d observations from %d captures of public pages (%d by server fetch, %d in a browser), six platforms, edition %s. Interpretations are marked &ldquo;My reading&rdquo; and kept apart from what each source states.</p></div>'
               % (E(m['selection']), E(m['dates']), E(m['public_only']), st, lim, nobs, nsrc, nsrc - nbr, nbr, E(ed['edition'])))
    out.append('<div class="grid2"><div class="card"><h4>About the researcher</h4><p class="dek m0">Research and analysis by <a href="/about">Ankit Kumar</a>, founder of Help Me Marketing, a marketing practice in Halton Hills, Ontario. This Index reads marketing pages; it is not financial, legal or regulatory advice.</p></div>'
               '<div class="card"><h4>Relationship disclosure</h4>%s</div></div>' % rel_html)
    if not draft:
        out.append(cite_and_editions(c))
    out.append(recon_details(c))
    out.append('<details class="ri-adv"><summary>Corrections</summary><p class="m0">%s</p></details>' % E(m['corrections']).replace('Hello@helpmemarketing.com', '<a href="mailto:Hello@helpmemarketing.com">Hello@helpmemarketing.com</a>'))
    out.append('<p class="pnote dlinks"><b>Download the data:</b> <a href="/%s" download>the curated observations (CSV)</a>: platform, category, observation, status, market and plan, conditions, source URL and capture time. My interpretations are not in the file.</p></section>' % CSV_REL)

    hp = n['help']
    href = '/contact?intent=review&amp;entry=%s#contact-form' % hp['entry']
    out.append('<section id="bs-help"><div class="sec-head"><h2>%s</h2></div><div class="card"><p class="dek m0">%s</p>'
               '<a class="btn btn-primary" href="%s" data-review-cta="%s">%s</a></div></section>' % (E(hp['heading']), E(hp['body']), href, hp['entry'], E(hp['button'])))
    out.append('<footer><div class="about"><p><b>About this index.</b> The Business Cards &amp; Spend Management Index is part of <b>The HMM Index</b> by Help Me Marketing. Edition %s reads how six selected platforms explain business cards, spend management and cross-border payments to Canadian businesses, from public pages captured on %s. It is not a ranking, a product test or a recommendation.</p></div>'
               '<div class="byline-block"><p>Company names are used to report their public pages and imply no relationship with Help Me Marketing.</p></div></footer>' % (E(ed['edition']), long_date(start)))
    out.append('</div>')
    out.append('<!-- ===== BUSINESS SPEND INDEX REPORT BODY END ===== -->')
    return '\n'.join(out)


def head_meta(c):
    ed, h = c.edition, c.n['hero']
    title = 'Business Cards & Spend Management Index | HelpMeMarketing'
    og = 'Business Cards & Spend Management Index'
    desc = 'How six platforms explain spending controls, rewards and cross-border payments to Canadian businesses, read from dated public pages. By Ankit Kumar.'
    robots = {'draft': 'noindex, follow', 'snapshot': 'noindex, follow',
              'release': 'index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1'}[c.mode]
    url = snapshot_url(c) if c.mode == 'snapshot' else ed['canonical']
    lines = [
        '<title>%s</title>' % E(title),
        '<meta name="description" content="%s">' % E(desc),
        '<link rel="preload" href="/assets/fonts/fraunces-latin.woff2" as="font" type="font/woff2" crossorigin>',
        '<link rel="preload" href="/assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>',
        '<link rel="stylesheet" href="/styles.css">',
        '<link rel="canonical" href="%s">' % url,
        '<meta name="robots" content="%s">' % robots,
        '<meta property="og:type" content="article">',
        '<meta property="og:site_name" content="HelpMeMarketing">',
        '<meta property="og:title" content="%s">' % E(og),
        '<meta property="og:description" content="%s">' % E(h['subtitle']),
        '<meta property="og:url" content="%s">' % url,
        '<meta property="og:image" content="%s/og-image.jpg">' % SITE,
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta property="og:locale" content="en_CA">',
        '<meta property="article:author" content="Ankit Kumar">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:title" content="%s">' % E(og),
        '<meta name="twitter:description" content="%s">' % E(h['subtitle']),
        '<meta name="twitter:image" content="%s/og-image.jpg">' % SITE,
    ]
    return '\n'.join(lines), title, desc


def jsonld(c, desc):
    url = c.edition['canonical']
    crumbs = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': 'The HMM Index', 'item': SITE + '/hmm-index'},
        {'@type': 'ListItem', 'position': 3, 'name': c.n['hero']['title'], 'item': url}]}
    if c.mode == 'snapshot':
        crumbs['itemListElement'].append({'@type': 'ListItem', 'position': 4, 'name': 'Edition %s' % c.edition['edition'], 'item': snapshot_url(c)})
    # Draft: no datePublished or dateModified. They are added at release from the recorded deployment, never from a build.
    article = {'@context': 'https://schema.org', '@type': 'Article', 'headline': c.n['hero']['title'], 'description': desc,
               'image': {'@type': 'ImageObject', 'url': SITE + '/og-image.jpg', 'width': 1200, 'height': 630},
               'author': {'@type': 'Person', '@id': SITE + '/about#ankit-kumar', 'name': 'Ankit Kumar', 'url': SITE + '/about'},
               'publisher': {'@id': SITE + '/#organization'}, 'mainEntityOfPage': url, 'inLanguage': 'en-CA'}
    if c.mode != 'draft' and c.date_modified:
        # From the recorded production deployment of the last content change, never from a build.
        article['dateModified'] = c.date_modified
    return '\n'.join('<script type="application/ld+json">\n%s\n</script>' % json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in (crumbs, article))


def csv_safe(v):
    v = '' if v is None else str(v)
    if v[:1] in ('=', '+', '-', '@', '\t', '\r'):
        v = "'" + v
    return v


def render_csv(c):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['observation_id', 'platform', 'layer', 'category', 'observation', 'status', 'market_plan', 'conditions', 'source_url', 'excerpt', 'observed_at'])
    order = {p: i for i, p in enumerate(c.order)}
    for o in sorted((o for o in c.obs.values() if o['public']), key=lambda o: (order[o['platform']], o['id'])):
        mp = '; '.join(x for x in [o['market'], o['eligibility'], o['plan']] if x)
        conds = ' '.join(x for x in [o['conditions']] + [cf['note'] for cf in o['conflicts']] if x)
        if o.get('reconciliation'):
            conds += ' Reconciliation: ' + recon_text(o['reconciliation'])
        if o['status'] == 'not_found':
            urls = [c.sources[s]['final_url'] for s in o['reviewed_sources']]
        else:
            urls = [c.sources[r['source_id']]['final_url'] for r in o['sources']]
        urls = list(dict.fromkeys(urls))
        exc = ' | '.join(r['excerpt'] for r in o['sources'])
        w.writerow([csv_safe(x) for x in [o['id'], c.name(o['platform']), LAYER_LABEL[o['layer']], CAT_LABEL[o['category']], o['statement'],
                                          model.STATUSES[o['status']], mp, conds, ' | '.join(urls), exc, o['observed_at']]])
    return buf.getvalue()


def render(c=None, mode=None, strict=True):
    c = c or Ctx()
    if mode:
        c.mode = mode
    errs = validate.check_inputs(c)
    if errs and strict:
        raise SystemExit('Build stopped:\n' + '\n'.join(errs))
    meta, title, desc = head_meta(c)
    with open(os.path.join(model.KIT, 'site_shell.html'), encoding='utf-8') as f:
        shell = f.read()
    with open(os.path.join(model.KIT, 'page_head.html'), encoding='utf-8') as f:
        page_head = f.read().rstrip('\n')
    if c.mode == 'snapshot':
        page_head += ('\n<!-- Snapshot of edition %s as first published. Research content in this snapshot is never rewritten; '
                      'record any later metadata fix in this comment. -->' % c.edition['edition'])
    page = (shell.replace('{{HEAD_META}}', meta).replace('{{JSONLD}}', jsonld(c, desc))
            .replace('{{PAGE_HEAD}}', page_head).replace('{{BODY}}', body(c)))
    assert not any(t in page for t in ('{{HEAD_META}}', '{{JSONLD}}', '{{PAGE_HEAD}}', '{{BODY}}'))
    return page, render_csv(c), c


def main(argv):
    page, csvtext, c = render()
    errs = validate.check_outputs(c, page, csvtext)
    if errs:
        raise SystemExit('Output checks failed:\n' + '\n'.join(errs))
    if '--check' in argv:
        bad = []
        for path, text in ((PAGE, page), (CSV_PATH, csvtext)):
            try:
                with open(path, encoding='utf-8') as f:
                    if f.read() != text:
                        bad.append(path)
            except FileNotFoundError:
                bad.append(path)
        if bad:
            print('Out of date: ' + ', '.join(os.path.relpath(b, model.ROOT) for b in bad))
            return 1
        print('PASS: page and CSV match a fresh build')
        return 0
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(PAGE, 'w', encoding='utf-8') as f:
        f.write(page)
    with open(CSV_PATH, 'w', encoding='utf-8') as f:
        f.write(csvtext)
    print('Wrote %s (%d bytes) and %s (%d rows)' % (os.path.relpath(PAGE, model.ROOT), len(page.encode()), CSV_REL, csvtext.count('\n') - 1))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
