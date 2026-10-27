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
import social
import validate

PAGE = os.path.join(model.ROOT, 'business-spend-index.html')
CSV_REL = 'assets/index/business-spend/business-spend-index-edition-001-observations.csv'
CSV_PATH = os.path.join(model.ROOT, CSV_REL)
SOCIAL_CSV_PATH = os.path.join(model.ROOT, social.CSV_REL)
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
        # Instagram module: status review shows the view for editorial review (release stays blocked by
        # validate.check_inputs); status reviewed, with the owner's approval recorded by hand, releases it.
        self.social = social.load_module()

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
        rows.append('<tr id="%s-%s"><td class="brandcell"><a href="#bs-p-%s">%s</a></td>%s</tr>' % (tid, pid, pid, E(c.name(pid)), cells))
    return ('<div class="tblock" id="%s"><h3 id="%s-h">%s</h3>'
            '<div class="tw cards" tabindex="0" role="region" aria-labelledby="%s-h"><table class="bs">'
            '<caption class="sr-only">%s for six platforms, as published on 23 October 2026</caption>'
            '<thead><tr><th scope="col">Platform</th>%s</tr></thead><tbody>\n%s\n</tbody></table></div></div>'
            % (tid, tid, E(title), tid, E(title), head, '\n'.join(rows)))


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


def id_links(ids):
    return ', '.join('<a href="#ev-%s">%s</a>' % (i, i) for i in ids)


PLAT_ROWS = [('audience', 'Audience named'), ('problem', 'Problem emphasised'), ('benefit', 'Promised benefit'),
             ('offer', 'Offer and its conditions'), ('proof', 'Proof supplied')]


def platform_block(c, pid):
    p = c.n['platforms'][pid]
    obs = sorted(c.obs_for(pid), key=lambda o: o['id'])
    times = sorted({o['observed_at'] for o in obs if o['observed_at']}, key=model.parse_ts)
    pages = sorted({s for o in obs for s in [r['source_id'] for r in o['sources']] + o.get('reviewed_sources', [])})
    dl = ''.join('<dt>%s</dt><dd>%s <span class="evlinks">(%s)</span></dd>' % (E(l), E(p[k]), id_links(p['ev'][k])) for k, l in PLAT_ROWS)
    links = ('<p class="pnote dlinks"><b>Product details:</b> %s&rsquo;s <a href="#bs-prod-%s">product</a>, <a href="#bs-xb-%s">cross-border</a> and '
             '<a href="#bs-spend-%s">spend-management</a> rows in Compare products, and its <a href="#bs-jt-%s">first screen</a> in Application journeys.</p>'
             % (E(c.name(pid)), pid, pid, pid, pid))
    q = p['question']
    reading = ('<div class="note reading"><span class="lbl">My reading</span><p><b>Customer question:</b> &ldquo;%s&rdquo; <b class="ans">%s.</b> %s</p><p>%s</p></div>'
               % (E(q['text']), E(q['answer']), E(q['detail']), E(p['observation'])))
    missing = p['missing']
    miss = ('<p class="dek"><b>Missing evidence.</b> %s.</p>' % E('; '.join(missing))) if missing else '<p class="dek"><b>Missing evidence.</b> None identified in this edition.</p>'
    tk = take(p['take']) if p.get('take') else gap_note('This takeaway is waiting for evidence: %s.' % '; '.join(missing))
    nb = sum(1 for x in pages if c.sources[x]['method'] == 'browser')
    when = 'Observed %s, %s to %s Toronto time, from %d server captures and %d browser captures.' % (
        long_date(times[0]), toronto_time(times[0]), toronto_time(times[-1]), len(pages) - nb, nb)
    return ('<div class="card plat" id="bs-p-%s"><h4 class="t">%s</h4><p class="ktag fact">What the sources say</p><dl>%s</dl>%s'
            '%s%s%s'
            '<details class="ri-adv srcs"><summary>Sources and exact wording for %s (%d observations)</summary><ul class="evlist">%s</ul></details>'
            '<p class="pnote">%s</p></div>'
            % (pid, E(c.name(pid)), dl, links, reading, miss, tk, E(c.name(pid)), len(obs),
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
            '<p class="dek">Ankit Kumar, Help Me Marketing. <em>Business Cards &amp; Spend Management Index</em> (The HMM Index). Edition %s. Public pages captured %s%s. <a href="%s">%s</a></p>'
            '<p class="dek m0">For a fixed version, cite the <a href="%s">edition %s snapshot</a>. <a href="#bs-editions">Edition history</a></p></div>'
            '<section id="bs-editions"><details class="ri-adv"><summary>Edition history</summary>'
            '<div class="tw" tabindex="0" role="region" aria-label="Edition history, scrolls sideways"><table><thead><tr><th scope="col">Edition</th><th scope="col">Dates</th><th scope="col">What it covered</th></tr></thead><tbody>'
            '<tr><td><b>%s</b> (this page)</td><td class="wrap-cell">Published %s. Public pages captured %s, %s to %s Toronto time. <a href="%s">Snapshot</a></td>'
            '<td class="wrap-cell">First edition: how six selected platforms explain business cards, spend management and cross-border payments, read from public pages and enquiry journeys%s. No refresh is scheduled.</td></tr>'
            '</tbody></table></div><p class="pnote">This address shows the latest edition. Each published edition keeps a snapshot at a fixed address.</p></details></section>'
            % (E(ed['edition']), long_date(start), '; Instagram posts published 25 July to 22 October 2026, collected 26 October 2026' if c.social else '',
               E(ed['canonical']), E(ed['canonical']), snap, E(ed['edition']),
               E(ed['edition']), E(iso_long(c.release_date)), long_date(start), toronto_time(start), toronto_time(end), snap,
               ', with official Instagram posts' if c.social else ''))


VIEW_ORDER = [('overview', 'bs-overview'), ('compare', 'bs-compare'), ('messaging', 'bs-messaging'), ('journeys', 'bs-journeys'), ('lessons', 'bs-lessons')]


def view_order(c):
    order = list(VIEW_ORDER)
    if c.social:
        order.insert(3, ('social', 'bs-social'))   # after Messaging & offers, before Application journeys
    return order


TEST_ROWS = [('observation', 'Observed evidence'), ('question', 'Customer question'), ('reading', 'My interpretation'),
             ('hypothesis', 'Testable hypothesis'), ('change', 'One change'), ('comparable', 'What stays comparable'),
             ('measure', 'Primary measurement'), ('guardrail', 'Guardrail'), ('limitation', 'When the result would be inconclusive')]


def example_card(c, e, eid=None):
    return ('<div class="card ex"%s><span class="kind">%s &middot; %s</span><h4 class="t">%s</h4><p class="ktag fact">What the sources say</p><p class="dek">%s</p>'
            '<div class="note reading"><span class="lbl">My reading</span><p>%s</p></div>%s</div>' % (
                (' id="%s"' % eid) if eid else '', E(e['kind']), E(c.name(e['platform'])), E(e['title']), E(e['body']), E(e['lesson']), ev_links(c, e['evidence'])))


def body(c):
    n, ed = c.n, c.edition
    h = n['hero']
    start, end = ed['collection_started_at'], ed['collection_ended_at']
    when = '%s, %s to %s Toronto time' % (long_date(start), toronto_time(start), toronto_time(end))
    draft = c.mode == 'draft'
    out = ['<!-- ===== BUSINESS SPEND INDEX REPORT BODY START ===== generated by _kit/business-spend/build.py; edit the kit, not this page ===== -->', '<div class="wrap">']
    out.append('<header><p class="kicker">%s</p><h1>%s</h1><p class="lede">%s</p><p class="scope">%s</p>' % (E(h['kicker']), E(h['title']), E(h['subtitle']), E(h['scope'])))
    social_when = ''
    if c.social:
        social_when = social.byline_html(c.social)
    out.append('<div class="byline"><span><b>Websites observed</b> %s</span>%s<span>Research and analysis by <b><a href="/about">Ankit Kumar</a></b> &middot; Founder, <a href="/">HMM</a></span></div>' % (E(when), social_when))
    out.append('<div class="livebar">%s<span>Edition <b>%s</b></span><span>%s</span></div>' % (
        '<span class="draft-flag">Draft</span>' if draft else '', E(ed['edition']), 'Not yet published' if draft else 'Published <b>%s</b>' % E(iso_long(c.release_date))))
    out.append('<p class="hero-act"><a class="btn btn-outline" href="%s">%s</a></p>' % (E(h['action']['href']), E(h['action']['label'])))
    if draft:
        out.append('<p class="pnote">%s</p>' % E(h['draft_note']))
    out.append('</header>')
    views = dict(n['views'])
    if c.social:
        views['social'] = {'title': c.social['view']['title'], 'dek': c.social['view']['dek']}
    order = view_order(c)
    out.append('<nav class="ri-nav bs-views" aria-label="Sections of this page"><div class="bs-tablist">%s</div></nav>' % ''.join(
        '<a href="#%s" id="bs-tab-%s">%s</a>' % (vid, k, E(views[k]['title'])) for k, vid in order))

    def view_open(key, vid):
        v = views[key]
        return ('<section id="%s" class="bs-view" aria-labelledby="%s-h"><div class="sec-head"><h2 id="%s-h">%s</h2><p class="dek">%s</p></div>'
                % (vid, vid, vid, E(v['title']), E(v['dek'])))

    def view_close(key):
        keys = [k for k, _ in order]
        i = keys.index(key)
        if i + 1 < len(order):
            k2, v2 = order[i + 1]
            link = '<a href="#%s">Next: %s &rarr;</a>' % (v2, E(views[k2]['title']))
        else:
            link = '<a href="#%s">Back to %s</a>' % (order[0][1], E(views[order[0][0]]['title']))
        return '<p class="bs-next">%s</p></section>' % link

    # ---------- 1. Overview ----------
    out.append(view_open('overview', 'bs-overview'))
    about = ''.join('<div class="kind"><dt>%s</dt><dd>%s</dd></div>' % (E(a), E(b)) for a, b in n['about'])
    out.append('<div class="card bs-about" id="bs-about"><h3>About this study</h3><dl class="legend">%s</dl></div>' % about)
    leg = ''.join('<div class="kind kind-%d"><dt>%s</dt><dd>%s</dd></div>' % (i, E(a), E(b)) for i, (a, b) in enumerate(n['legend']))
    ch = n['chain']
    chain = '<ol class="chain-steps">%s</ol>' % ''.join('<li>%s</li>' % E(s) for s in ch['steps'])
    out.append('<div class="card bs-legend" id="bs-guide"><h3>How to read this page</h3><dl class="legend">%s</dl>'
               '<h4 class="t chain-h">How each conclusion is reached</h4>%s<p class="pnote m0">%s</p></div>' % (leg, chain, E(ch['note'])))
    f = n['findings']
    tests = {t['id']: t for t in n['tests']['items']}
    items = []
    for it in f['items']:
        t = tests[it['test']]
        an = ', '.join('<a href="#%s">%s</a>' % (a[1], E(a[0])) for a in it['analysis'])
        items.append('<div class="find" id="bs-%s"><h4 class="t">%s</h4><dl class="chain">'
                     '<dt>What the sources say</dt><dd>%s <b>Denominator:</b> %s %s</dd>'
                     '<dt>Customer question</dt><dd>&ldquo;%s&rdquo;</dd>'
                     '<dt>My reading</dt><dd>%s</dd>'
                     '<dt>Analysis and test</dt><dd class="dlinks">%s. Proposed test, not a result: <a href="#bs-%s">test %s, %s</a>.</dd></dl></div>' % (
                         it['id'].lower(), E(it['title']), E(it['body']), E(it['denominator']), ev_links(c, it['evidence']).replace('<p class="evlinks">', '<span class="evlinks">').replace('</p>', '</span>'),
                         E(it['question']), E(it['reading']), an, t['id'].lower(), t['id'][1:], E(t['title'])))
    out.append('<div id="bs-findings" class="sub"><h3>Three findings</h3><p class="dek">%s</p><div class="card">%s%s</div></div>' % (
        E(f['dek']), ''.join(items), take(f['take'])))
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
    out.append('<div class="grid2"><div class="card"><h4>About the researcher</h4><p class="dek m0">Research and analysis by <a href="/about">Ankit Kumar</a>, founder of Help Me Marketing, a marketing practice in Halton Hills, Ontario. This Index reads marketing pages; it is not financial, legal or regulatory advice.</p></div>'
               '<div class="card"><h4>Relationship disclosure</h4>%s</div></div>' % rel_html)
    if not draft:
        out.append(cite_and_editions(c))
    social_method = social.method_html(c.social) if c.social else ''
    out.append('<div id="bs-method" class="sub"><details class="ri-adv srcs"><summary>How this research was done</summary>'
               '<h4 class="t">Selection</h4><p class="dek">%s</p><h4 class="t">Dates</h4><p class="dek">%s</p><h4 class="t">Public sources only</h4><p class="dek">%s</p>%s'
               '<h4 class="t" id="bs-statuses">What each status means</h4><dl class="statdefs">%s</dl><h4 class="t">Limitations</h4><ul class="dek">%s</ul>'
               '<p class="pnote">%d observations from %d captures of public pages (%d by server fetch, %d in a browser), six platforms, edition %s. Interpretations are marked &ldquo;My reading&rdquo; and kept apart from what each source states.</p></details>'
               % (E(m['selection']), E(m['dates']), E(m['public_only']), social_method, st, lim, nobs, nsrc, nsrc - nbr, nbr, E(ed['edition'])))
    out.append(recon_details(c))
    log = ''.join('<li><b>%s.</b> %s</li>' % (E(d), E(x)) for d, x in m.get('corrections_log', []))
    out.append('<details class="ri-adv" id="bs-corrections"><summary>Corrections</summary><p class="m0">%s</p>%s</details>' % (
        E(m['corrections']).replace('Hello@helpmemarketing.com', '<a href="mailto:Hello@helpmemarketing.com">Hello@helpmemarketing.com</a>'),
        ('<ul class="dek corrections-log">%s</ul>' % log) if log else '<p class="pnote m0">No corrections recorded.</p>'))
    out.append('<p class="pnote dlinks"><b>Download the data:</b> <a href="/%s" download>the curated observations (CSV)</a>: platform, category, observation, status, market and plan, conditions, source URL and capture time. My interpretations are not in the file.</p></div>' % CSV_REL)
    out.append(view_close('overview'))

    # ---------- 2. Compare products ----------
    cp = n['compare']
    out.append(view_open('compare', 'bs-compare'))
    out.append('<p class="ktag fact">What the sources say</p>')
    out.append(table(c, 'Product context', cp['product_columns'], 'bs-prod'))
    out.append(table(c, 'Cross-border context', cp['xb_columns'], 'bs-xb'))
    out.append(table(c, 'Spend-management context', cp['spend_columns'], 'bs-spend'))
    out.append('<p class="pnote"><b>Reading the tables.</b> %s An entry with a status label is not a plain published fact; <a href="#bs-statuses">what each status means</a>. &ldquo;Not determined&rdquo; is not a status: it marks two published statements whose relationship the evidence cannot settle (<a href="#bs-recon">reconciliation</a> class D).</p>' % E(cp['note']))
    out.append(compare_sources(c))
    out.append('<p class="pnote dlinks"><b>Download the data:</b> <a href="/%s" download>every observation with its source (CSV)</a>.</p>' % CSV_REL)
    out.append(view_close('compare'))

    # ---------- 3. Messaging & offers ----------
    ex = n['examples']
    out.append(view_open('messaging', 'bs-messaging'))
    exs = ''.join(example_card(c, e) for e in ex['items'] if e['kind'] != 'Enquiry design')
    out.append('<div id="bs-platforms" class="sub"><h3>Platform by platform</h3><p class="dek">The same questions for each platform, in the order Venn, Float, Ramp, Loop, Keep, Airwallex. What the sources say comes first, with the observation IDs behind each line; then one customer question and my reading. Product facts stay in <a href="#bs-compare">Compare products</a>; each block links to its rows there.</p>')
    out += [platform_block(c, pid) for pid in c.order]
    out.append('</div>')
    out.append('<div id="bs-examples" class="sub"><h3>Selected communication examples</h3><p class="dek">%s</p>%s</div>' % (E(ex['dek']), exs))
    out.append(view_close('messaging'))

    # ---------- 4. Instagram content (only with a derived module in review or reviewed) ----------
    if c.social:
        out.append(view_open('social', 'bs-social'))
        out.append(social.panel_html(c))
        out.append(view_close('social'))

    # ---------- 5. Application journeys ----------
    jn = n['journeys']
    out.append(view_open('journeys', 'bs-journeys'))
    head = ''.join('<th scope="col">%s</th>' % E(l) for _, l in jn['columns'])
    rows = []
    for pid in c.order:
        r = jn['rows'][pid]
        cells = ''.join('<td data-label="%s">%s%s</td>' % (E(l), E(r[k]), ('<span class="cell-sub">Destination: %s</span>' % E(r['dest'])) if k == 'start' else '') for k, l in jn['columns'])
        status = ''.join(status_tag(c.obs[i]['status']) for i in r['ids'][:1])
        rows.append('<tr id="bs-jt-%s"><td class="brandcell"><a href="#bs-p-%s">%s</a>%s<span class="cell-sub">Observation stopped: %s</span><span class="cell-sub">Evidence: %s</span></td>%s</tr>' % (pid, pid, E(c.name(pid)), status, E(r['stop']), id_links(r['ids']), cells))
    out.append('<div class="tblock" id="bs-journey-table"><p class="ktag fact">What the sources say</p><h3 id="bs-jt-h">What each first screen showed</h3>'
               '<div class="tw cards" tabindex="0" role="region" aria-labelledby="bs-jt-h"><table class="bs"><caption class="sr-only">First screen of each provider&rsquo;s application or demo journey, 23 October 2026</caption>'
               '<thead><tr><th scope="col">Platform</th>%s</tr></thead><tbody>\n%s\n</tbody></table></div><p class="pnote">%s</p></div>' % (head, '\n'.join(rows), E(jn['note'])))
    out.append('<div class="sub" id="bs-journey-reading"><h3>My reading of the first screens</h3><div class="note reading"><span class="lbl">My reading</span><p>%s</p></div></div>' % E(jn['reading']))
    e3 = [e for e in ex['items'] if e['kind'] == 'Enquiry design']
    out.append(''.join(example_card(c, e, 'bs-e3') for e in e3))
    out.append('<div class="card test-ptr"><span class="ktag test">Proposed test, not a result</span><p class="dek m0">%s <a href="#bs-t3">Read test 3</a>.</p></div>' % E(jn['test']))
    out.append(view_close('journeys'))

    # ---------- 6. Lessons & tests ----------
    pt = n['patterns']
    out.append(view_open('lessons', 'bs-lessons'))
    pts = ''.join('<p class="dek"><b>%s.</b> %s%s <b>Denominator:</b> %s</p>%s' % (
        E(x['title']), E(x['body']), (' <b>Exceptions:</b> %s' % E(x['exceptions'])) if x['exceptions'] else '', E(x['denominator']), ev_links(c, x['evidence'])) for x in pt['items'])
    out.append('<div id="bs-patterns" class="sub"><h3>Patterns across the six</h3><p class="dek">%s</p><div class="card reading-card"><span class="ktag">My reading across the six</span>%s%s</div></div>' % (E(pt['dek']), pts, take(pt['take'])))
    ts = n['tests']
    lis = []
    for t in ts['items']:
        dd = []
        for k, l in TEST_ROWS:
            v = E(t[k])
            if k == 'observation':
                v += ' <span class="evlinks">(%s)</span>' % id_links(t['evidence'])
            dd.append('<dt>%s</dt><dd>%s</dd>' % (E(l), v))
        lis.append('<li id="bs-%s"><span class="ktag test">Proposed test, not a result</span><b>Test %s. %s</b> <span class="evlinks">(from <a href="#bs-%s">finding %s</a>)</span><dl>%s</dl></li>' % (
            t['id'].lower(), t['id'][1:], E(t['title']), t['finding'].lower(), t['finding'][1:], ''.join(dd)))
    out.append('<div id="bs-tests" class="sub"><h3>Three tests for a marketing team</h3><p class="dek">%s</p><div class="card"><ol class="tests">%s</ol>'
               '<p class="pnote m0">There are no baselines, uplift figures or sample sizes here on purpose: they depend on your own traffic and data.</p></div></div>' % (E(ts['dek']), ''.join(lis)))
    out.append(view_close('lessons'))

    hp = n['help']
    href = '/contact?intent=review&amp;entry=%s#contact-form' % hp['entry']
    out.append('<section id="bs-help"><div class="sec-head"><h2>%s</h2></div><div class="card"><p class="dek m0">%s</p>'
               '<a class="btn btn-primary" href="%s" data-review-cta="%s">%s</a></div></section>' % (E(hp['heading']), E(hp['body']), href, hp['entry'], E(hp['button'])))
    out.append('<footer><div class="about"><p><b>About this index.</b> The Business Cards &amp; Spend Management Index is part of <b>The HMM Index</b> by Help Me Marketing. Edition %s is an independent comparative marketing case study of how six selected platforms explain business cards, spend management and cross-border payments to Canadian businesses, from public pages captured on %s%s. It is not a ranking, a product test or a recommendation.</p></div>'
               '<div class="byline-block"><p>Company names are used to report their public pages and posts and imply no relationship with Help Me Marketing.</p></div></footer>' % (
                   E(ed['edition']), long_date(start), ' and official Instagram posts published 25 July to 22 October 2026' if c.social else ''))
    out.append('</div>')
    out.append('<!-- ===== BUSINESS SPEND INDEX REPORT BODY END ===== -->')
    return '\n'.join(out)


def head_meta(c):
    ed, h = c.edition, c.n['hero']
    title = 'Business Cards & Spend Management Index | HelpMeMarketing'
    og = 'Business Cards & Spend Management Index'
    desc = 'An independent comparative marketing case study of how six platforms explain spend controls, rewards and cross-border payments to Canadian businesses.'
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
    files = [(PAGE, page), (CSV_PATH, csvtext)]
    if c.social:
        files.append((SOCIAL_CSV_PATH, social.render_csv(c.social)))
    if '--check' in argv:
        bad = []
        for path, text in files:
            try:
                with open(path, encoding='utf-8') as f:
                    if f.read() != text:
                        bad.append(path)
            except FileNotFoundError:
                bad.append(path)
        if bad:
            print('Out of date: ' + ', '.join(os.path.relpath(b, model.ROOT) for b in bad))
            return 1
        print('PASS: page and CSV files match a fresh build')
        return 0
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    for path, text in files:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
    print('Wrote %s (%d bytes) and %s (%d rows)%s' % (os.path.relpath(PAGE, model.ROOT), len(page.encode()), CSV_REL, csvtext.count('\n') - 1,
          (' and %s (%d rows)' % (social.CSV_REL, files[2][1].count('\n') - 1)) if c.social else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
