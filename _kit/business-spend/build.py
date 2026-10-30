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
        # Separately dated follow-up checks (not part of the 23 October 2026 research data or its CSV).
        self.followup = model.load('airwallex_followup_2026-10-30.json')
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
        restr = spec.get('restriction') if status == 'explicitly_unavailable' else None
        mark = lambda t: ' cell-restr' if restr and t == restr else ''
        body = '<span class="cell-main%s">%s</span>' % (mark(spec['text']), E(spec['text']))
        if spec.get('sub'):
            body += '<span class="cell-sub%s">%s</span>' % (mark(spec['sub']), E(spec['sub']))
        cls = ''
        # A restriction the cell already states is set in bold instead of repeated as a label.
        tag = '' if restr and restr in (spec['text'], spec.get('sub')) else table_tag(status, spec)
    if any('D' in (c.obs[i].get('reconciliation') or {}).get('class', '') for i in ids):
        tag += '<a class="st st-undetermined" href="#bs-unclear">%s</a>' % E(spec['unclear'])
    if spec.get('followup'):
        tag += '<a class="bs-fu" href="#bs-awx-followup">Checked 30 October 2026</a>'
    return '<td%s data-label="%s">%s%s</td>' % (cls, E(label), body, tag)


# Plain wording beside a claim in the comparison tables (founder, 2026-10-28). The formal status names stay in
# "What each status means", the evidence records and the CSV; "Explicitly unavailable" shows the exact restriction.
TABLE_LABEL = {'conflicting': 'Published pages disagree'}


def table_tag(status, spec):
    if status == 'explicitly_unavailable':
        return '<span class="st st-explicitly_unavailable">%s</span>' % E(spec['restriction'])
    if status in TABLE_LABEL:
        return '<span class="st st-%s">%s</span>' % (status, E(TABLE_LABEL[status]))
    return status_tag(status)


def compare_columns(cp):
    return cp['cost_columns'] + cp['card_columns'] + cp['fee_columns'] + cp['acct_columns'] + cp['spend_columns']


def restriction_lines(c, pid):
    return ''.join('<span class="bs-restr"><b>%s:</b> %s</span>' % (E(l), E(t)) for l, t, _ in c.n['compare']['rows'][pid].get('restrictions', []))


def table(c, title, cols, tid, head=True, note=None, restrictions=False):
    ths = ''.join('<th scope="col">%s</th>' % E(l) for _, l in cols)
    rows = []
    for pid in c.order:
        cells = ''.join(cell(c, pid, k, l) for k, l in cols)
        extra = restriction_lines(c, pid) if restrictions else ''
        rows.append('<tr id="%s-%s"><td class="brandcell"><a href="#bs-p-%s">%s</a>%s</td>%s</tr>' % (tid, pid, pid, E(c.name(pid)), extra, cells))
    label = ('<h3 id="%s-h">%s</h3>' % (tid, E(title))) if head else ''
    if note:
        label += '<p class="bs-tnote">%s</p>' % E(note)
    region = ('aria-labelledby="%s-h"' % tid) if head else ('aria-label="%s"' % E(title))
    return ('<div class="tblock" id="%s">%s'
            '<div class="tw cards" tabindex="0" role="region" %s><table class="bs">'
            '<caption class="sr-only">%s for six platforms, as published on 23 October 2026</caption>'
            '<thead><tr><th scope="col">Platform</th>%s</tr></thead><tbody>\n%s\n</tbody></table></div></div>'
            % (tid, label, region, E(title), ths, '\n'.join(rows)))


def compare_sources(c):
    items = []
    cols = compare_columns(c.n['compare'])
    for pid in c.order:
        parts = []
        for k, l in cols:
            ids = c.n['compare']['rows'][pid][k].get('ids', [])
            if ids:
                parts.append('%s: %s' % (E(l), ', '.join('<a href="#ev-%s">%s</a>' % (i, i) for i in ids)))
            else:
                parts.append('%s: not checked' % E(l))
        for l, t, ids in c.n['compare']['rows'][pid].get('restrictions', []):
            parts.append('%s line (%s): %s' % (E(l), E(t), ', '.join('<a href="#ev-%s">%s</a>' % (i, i) for i in ids)))
        if any(c.n['compare']['rows'][pid][k].get('followup') for k, _ in cols):
            parts.append('follow-up of 30 October 2026: <a href="#bs-awx-followup">record</a>')
        items.append('<li><b>%s.</b> %s</li>' % (E(c.name(pid)), '; '.join(parts)))
    return ('<h4 class="t">Where each entry comes from</h4>'
            '<p class="dek">Each entry links to the observation it summarises, with the exact wording, the page and the capture time.</p>'
            '<ul class="evlist">%s</ul>' % ''.join(items))


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


def recon_details(c, inline=False):
    rows = []
    order = {p: i for i, p in enumerate(c.order)}
    for o in sorted((o for o in c.obs.values() if o.get('reconciliation')), key=lambda o: (order[o['platform']], o['id'])):
        r = o['reconciliation']
        rows.append('<tr><td data-label="Platform">%s</td><td data-label="Difference"><a href="#ev-%s">%s</a></td><td data-label="Class">%s</td><td data-label="Why" class="wrap-cell">%s</td></tr>'
                    % (E(c.name(o['platform'])), o['id'], E(r['topic']), E(r['class']), E(r['note'])))
    legend = '; '.join('%s: %s' % (k, v) for k, v in sorted(model.RECON_LABEL.items()))
    if inline:
        head = '<h4 class="t" id="bs-recon">How the %d reported differences were reconciled</h4>' % len(rows)
        body = ('<p class="dek">After the first reading, a browser pass compared each pair of statements by product, transaction, country and customer, plan, currency, dates and conditions. Classes: %s. Both statements stay in the evidence for every item.</p>'
                '<div class="tw cards" tabindex="0" role="region" aria-label="Reconciliation of the reported differences"><table class="bs"><thead><tr><th scope="col">Platform</th><th scope="col">Difference</th><th scope="col">Class</th><th scope="col">Why</th></tr></thead><tbody>%s</tbody></table></div>'
                % (E(legend), ''.join(rows)))
        return head + body
    return ('<details class="ri-adv srcs" id="bs-recon"><summary>How the %d reported differences were reconciled</summary>'
            '<p class="dek">After the first reading, a browser pass compared each pair of statements by product, transaction, country and customer, plan, currency, dates and conditions. Classes: %s. Both statements stay in the evidence for every item.</p>'
            '<div class="tw cards" tabindex="0" role="region" aria-label="Reconciliation of the reported differences"><table class="bs"><thead><tr><th scope="col">Platform</th><th scope="col">Difference</th><th scope="col">Class</th><th scope="col">Why</th></tr></thead><tbody>%s</tbody></table></div></details>'
            % (len(rows), E(legend), ''.join(rows)))


def id_links(ids):
    return ', '.join('<a href="#ev-%s">%s</a>' % (i, i) for i in ids)


PLAT_ROWS = [('audience', 'Audience named'), ('problem', 'Problem emphasised'), ('benefit', 'Promised benefit'),
             ('offer', 'Offer and its conditions'), ('proof', 'Proof supplied')]


def platform_block(c, pid):
    """One provider's supporting evidence in Messaging & offers, as a labelled expander (founder brief, 2026-10-30, third)."""
    p = c.n['platforms'][pid]
    obs = sorted(c.obs_for(pid), key=lambda o: o['id'])
    times = sorted({o['observed_at'] for o in obs if o['observed_at']}, key=model.parse_ts)
    pages = sorted({s for o in obs for s in [r['source_id'] for r in o['sources']] + o.get('reviewed_sources', [])})
    dl = ''.join('<dt>%s</dt><dd>%s <span class="evlinks">(%s)</span></dd>' % (E(l), E(p[k]), id_links(p['ev'][k])) for k, l in PLAT_ROWS)
    links = ('<p class="pnote dlinks"><b>Product details:</b> %s&rsquo;s <a href="#bs-prod-%s">cards, rewards and costs</a>, <a href="#bs-xb-%s">currency fees</a> and '
             '<a href="#bs-spend-%s">spending controls</a> rows in Compare products, and its <a href="#bs-jt-%s">first screen</a> in Application journeys.</p>'
             % (E(c.name(pid)), pid, pid, pid, pid))
    q = p['question']
    reading = ('<div class="note reading"><span class="lbl">My reading</span><p><b>Customer question:</b> &ldquo;%s&rdquo; <b class="ans">%s.</b> %s</p><p>%s</p></div>'
               % (E(q['text']), E(q['answer']), E(q['detail']), E(p['observation'])))
    missing = p['missing']
    miss = ('<p class="dek"><b>Missing evidence.</b> %s.</p>' % E('; '.join(missing))) if missing else '<p class="dek"><b>Missing evidence.</b> None identified in this edition.</p>'
    extra = ''.join('<p class="dek"><b>%s.</b> %s <b>My reading:</b> %s %s</p>' % (
        E(e['title']), E(e['body']), E(e['lesson']), ev_links(c, e['evidence']).replace('<p class="evlinks">', '<span class="evlinks">').replace('</p>', '</span>'))
        for e in c.n['examples']['items'] if e.get('place') == 'evidence:' + pid)
    fu = ''
    if c.followup and c.followup.get('platform', 'airwallex') == pid:
        fu = ('<p class="dek bs-fu-note"><b>Separately dated follow-up, checked 30 October 2026.</b> A week after these observations I rechecked Airwallex&rsquo;s pricing, card page and cash rebate promotion terms. '
              'That check is not part of the 23 October observations, statuses or downloads: <a href="#bs-awx-followup">read the follow-up record</a>.</p>')
    nb = sum(1 for x in pages if c.sources[x]['method'] == 'browser')
    when = 'Observed %s, %s to %s Toronto time, from %d server captures and %d browser captures.' % (
        long_date(times[0]), toronto_time(times[0]), toronto_time(times[-1]), len(pages) - nb, nb)
    return ('<details class="bs-more plat" id="bs-p-%s"><summary>%s: sources, exact wording and missing evidence (%d observations)</summary>'
            '<p class="ktag fact">What the sources say</p><dl>%s</dl>%s%s%s%s%s'
            '<h4 class="t">Observations and exact wording</h4><ul class="evlist">%s</ul><p class="pnote">%s</p></details>'
            % (pid, E(c.name(pid)), len(obs), dl, links, reading, miss, extra, fu, ''.join(ev_item(c, o) for o in obs), E(when)))


def short_date(value):
    """Founder's byline format (2026-10-28): 'Oct 27, 2026', from an ISO date or time (the Toronto date of the recorded deployment)."""
    from datetime import date
    d = date.fromisoformat(value[:10])
    return '%s %d, %d' % (d.strftime('%b'), d.day, d.year)


def iso_long(day):
    return long_date(day + 'T12:00:00-04:00')


def snapshot_url(c):
    return '%s/edition-%s' % (c.edition['canonical'], c.edition['edition'])


def cite_and_editions(c):
    ed = c.edition
    start, end = ed['collection_started_at'], ed['collection_ended_at']
    snap = '/' + snapshot_url(c).split('.com/', 1)[1]
    html = ('<div class="card" id="bs-cite"><h4>Cite this research</h4>'
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
    # Overview layout (2026-10-28): the citation and the edition table are rendered by the Overview as two expanders.
    cite = html[html.index('<p class="dek">'):html.index('</div><section id="bs-editions">')]
    table = html[html.index('<div class="tw"'):html.index('</details></section>')]
    return cite, table


VIEW_ORDER = [('overview', 'bs-overview'), ('compare', 'bs-compare'), ('messaging', 'bs-messaging'), ('journeys', 'bs-journeys'), ('lessons', 'bs-lessons')]


def view_order(c):
    order = list(VIEW_ORDER)
    if c.social:
        order.append(('social', 'bs-social'))   # last (founder, 2026-10-30): Messaging, Application journeys and Lessons read in sequence
    return order


TEST_ROWS = [('observation', 'Observed evidence'), ('question', 'Customer question'), ('reading', 'My interpretation'),
             ('hypothesis', 'Testable hypothesis'), ('change', 'One change'), ('comparable', 'What stays comparable'),
             ('measure', 'Primary measurement'), ('guardrail', 'Guardrail'), ('limitation', 'When the result would be inconclusive')]


def example_card(c, e, eid=None):
    # Short form (2026-10-30): heading, the observed fact, one sentence of my reading, the evidence link.
    return ('<div class="card ex"%s><h4 class="t">%s</h4><p class="dek">%s</p>'
            '<p class="dek"><b>My reading:</b> %s</p>%s</div>' % (
                (' id="%s"' % eid) if eid else '', E(e['title']), E(e['body']), E(e['lesson']), ev_links(c, e['evidence'])))


def body(c):
    n, ed = c.n, c.edition
    h = n['hero']
    start, end = ed['collection_started_at'], ed['collection_ended_at']
    when = '%s, %s to %s Toronto time' % (long_date(start), toronto_time(start), toronto_time(end))
    draft = c.mode == 'draft'
    out = ['<!-- ===== BUSINESS SPEND INDEX REPORT BODY START ===== generated by _kit/business-spend/build.py; edit the kit, not this page ===== -->', '<div class="wrap">']
    # Hero (founder brief, 2026-10-28): kicker, title, one line on what to compare, the six providers, one metadata line and one note.
    # Capture times and the scope paragraph live in "Scope & sources" (the methodology), not here.
    out.append('<header><p class="kicker">%s</p><h1>%s</h1><p class="lede">%s</p>' % (E(h['kicker']), E(h['title']), E(h['lede'])))
    out.append('<p class="bs-provs">%s</p>' % ' &middot; '.join(E(c.name(pid)) for pid in c.order))
    out.append('<p class="bs-meta">%sBy <a href="/about">Ankit Kumar</a> &middot; Edition %s &middot; %s</p>' % (
        '<span class="draft-flag">Draft</span> ' if draft else '', E(ed['edition']), 'Not yet published' if draft else 'Last Updated %s' % E(short_date(c.date_modified or c.release_date))))
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
                % (vid, vid, vid, E(v.get('heading', v['title'])), E(v['dek'])))

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
    # Founder brief (2026-10-28): findings first, my reading beside each, one takeaway, then the research details in expanders.
    out.append(view_open('overview', 'bs-overview'))
    out.append('<p class="bs-obs">%s</p>' % E(views['overview']['observed']))
    f = n['findings']
    tests = {t['id']: t for t in n['tests']['items']}
    items = []
    for k, it in enumerate(f['items'], 1):
        t = tests[it['test']]
        an = ', '.join('<a href="#%s">%s</a>' % (a[1], E(a[0])) for a in it['analysis'])
        detail = ('<details class="bs-fdetail"><summary>Evidence for this finding</summary><p class="dek fdetail-t">%s</p><dl class="chain">'
                  '<dt>What the sources say</dt><dd>%s <b>Denominator:</b> %s %s</dd>'
                  '<dt>Customer question</dt><dd>&ldquo;%s&rdquo;</dd>'
                  '<dt>My reading</dt><dd>%s</dd>'
                  '<dt>Analysis and test</dt><dd class="dlinks">%s. Proposed test, not a result: <a href="#bs-%s">test %s, %s</a>.</dd></dl></details>' % (
                      E(it['title']), E(it['body']), E(it['denominator']), ev_links(c, it['evidence']).replace('<p class="evlinks">', '<span class="evlinks">').replace('</p>', '</span>'),
                      E(it['question']), E(it['reading']), an, t['id'].lower(), t['id'][1:], E(t['title'])))
        # Key figure first (2026-10-28): the count comes from the finding's denominator; validate.py checks they agree.
        # Headline first, then the count as a supporting line with its own denominator (founder, 2026-10-28).
        items.append('<div class="find" id="bs-%s"><h3 class="bs-ftitle">%s</h3><p class="bs-fig"><b>%s</b> %s</p><p class="dek">%s</p>'
                     '<p class="bs-fgo"><a href="#%s">%s<span aria-hidden="true"> &rarr;</span></a></p>%s</div>' % (
                         it['id'].lower(), E(it['short_title']), E(it['figure']), E(it['figure_label']), E(it['summary']), it['explore'][1], E(it['explore'][0]), detail))
    out.append('<div id="bs-findings" class="bs-finds">%s</div>' % ''.join(items))
    out.append(take(f['take']))
    m = n['method']
    st = ''.join('<dt>%s</dt><dd>%s</dd>' % (E(a), E(b)) for a, b in m['statuses'])
    lim = ''.join('<li>%s</li>' % E(x) for x in m['limitations'])
    rel = ed['relationship_disclosure']
    if rel['status'] == 'complete':
        rel_line = 'No commercial relationship with the six providers.'
        rel_full = '<p class="dek"><b>Relationship disclosure.</b> %s</p>' % E(rel['text'])
    else:
        rel_line = 'Relationship disclosure pending.'
        rel_full = ('<div class="note gap"><span class="lbl">Placeholder</span><p>Relationship disclosure pending. Before publication I will state here whether '
                    'I or Help Me Marketing have any commercial connection with any of the six providers.</p></div>')
    nobs = len(c.obs)
    nsrc = len(c.sources)
    nbr = sum(1 for x in c.sources.values() if x['method'] == 'browser')
    out.append('<div class="bs-research" id="bs-research"><p class="bs-author">Research and analysis by <a href="/about">Ankit Kumar</a>, founder of Help Me Marketing. %s</p>' % E(rel_line))
    about = ''.join('<div class="kind"><dt>%s</dt><dd>%s</dd></div>' % (E(a), E(b)) for a, b in n['about'])
    out.append('<details class="bs-rd" id="bs-about"><summary>About this study</summary><p class="dek">%s</p><dl class="legend">%s</dl>'
               '<p class="dek">Research and analysis by <a href="/about">Ankit Kumar</a>, founder of Help Me Marketing, a marketing practice in Halton Hills, Ontario. This Index reads marketing pages; it is not financial, legal or regulatory advice.</p>%s</details>'
               % (E(views['overview']['about_intro']), about, rel_full))
    leg = ''.join('<div class="kind kind-%d"><dt>%s</dt><dd>%s</dd></div>' % (i, E(a), E(b)) for i, (a, b) in enumerate(n['legend']))
    ch = n['chain']
    chain = '<ol class="chain-steps">%s</ol>' % ''.join('<li>%s</li>' % E(s) for s in ch['steps'])
    out.append('<details class="bs-rd" id="bs-guide"><summary>How to read the analysis</summary><dl class="legend">%s</dl>'
               '<h4 class="t chain-h">How each conclusion is reached</h4>%s<p class="pnote m0">%s</p></details>' % (leg, chain, E(ch['note'])))
    social_method = social.method_html(c.social) if c.social else ''
    out.append('<div id="bs-method"><details class="bs-rd" id="bs-scope"><summary>Sources and methodology</summary>'
               '<h4 class="t">Scope</h4><p class="dek">%s</p><h4 class="t">Selection</h4><p class="dek">%s</p><h4 class="t">Dates</h4><p class="dek">Websites observed %s. %s</p><h4 class="t">Public sources only</h4><p class="dek">%s</p>%s'
               '<h4 class="t" id="bs-statuses">What each status means</h4><dl class="statdefs">%s</dl><h4 class="t">Limitations</h4><ul class="dek">%s</ul>'
               '<p class="pnote">%d observations from %d captures of public pages (%d by server fetch, %d in a browser), six platforms, edition %s. Interpretations are marked &ldquo;My reading&rdquo; and kept apart from what each source states.</p>%s</details></div>'
               % (E(m['scope']), E(m['selection']), E(when), E(m['dates']), E(m['public_only']), social_method, st, lim, nobs, nsrc, nsrc - nbr, nbr, E(ed['edition']), recon_details(c, inline=True)))
    log = ''.join('<li><b>%s.</b> %s</li>' % (E(d), E(x)) for d, x in m.get('corrections_log', []))
    corr = ('<h4 class="t" id="bs-corrections">Corrections</h4><p class="dek">%s</p>%s' % (
        E(m['corrections']).replace('Hello@helpmemarketing.com', '<a href="mailto:Hello@helpmemarketing.com">Hello@helpmemarketing.com</a>'),
        ('<ul class="dek corrections-log">%s</ul>' % log) if log else '<p class="pnote m0">No corrections recorded.</p>'))
    if not draft:
        cite, ed_table = cite_and_editions(c)
        out.append('<details class="bs-rd" id="bs-cite"><summary>Cite this research</summary>%s</details>' % cite)
        out.append('<details class="bs-rd" id="bs-editions"><summary>Edition history and corrections</summary><h4 class="t">Edition history</h4>%s%s</details>' % (ed_table, corr))
    else:
        out.append('<details class="bs-rd" id="bs-editions"><summary>Corrections</summary>%s</details>' % corr)
    out.append('<p class="pnote dlinks"><b>Download the data:</b> <a href="/%s" download>the curated observations (CSV)</a>: platform, category, observation, status, market and plan, conditions, source URL and capture time. My interpretations are not in the file.</p></div>' % CSV_REL)
    out.append(view_close('overview'))

    # ---------- 2. Compare products ----------
    cp = n['compare']
    out.append(view_open('compare', 'bs-compare'))
    # Founder brief (2026-10-30, second): short, direct and plain. Three compact tables, each with an optional details expander;
    # restrictions beside the provider; supporting information grouped at the bottom.
    out.append('<p class="bs-cmp-when"><b>Website observations: %s.</b> %s</p>' % (long_date(start), E(cp['observed_line'])))
    out.append('<p class="bs-cmp-jump"><a href="#bs-prod">Cards, rewards &amp; costs</a> &middot; <a href="#bs-xb">Currency fees</a> &middot; <a href="#bs-spend">Spending controls</a></p>')
    out.append('<div class="bs-cmp-sec">%s<details class="bs-more"><summary>More product details: network, issuer, card formats and eligibility</summary>%s</details></div>'
               % (table(c, 'Cards, rewards & costs', cp['cost_columns'], 'bs-prod', note=cp['pricing_note'], restrictions=True),
                  table(c, 'More product details', cp['card_columns'], 'bs-cards', head=False)))
    out.append('<div class="bs-cmp-sec">%s<details class="bs-more"><summary>Account and transfer details: currencies, banking partners, interest offers and transfers</summary>%s</details></div>'
               % (table(c, 'Currency fees', cp['fee_columns'], 'bs-xb', note=cp['currency_note']), table(c, 'Account and transfer details', cp['acct_columns'], 'bs-xt', head=False)))
    out.append('<div class="bs-cmp-sec">%s</div>' % table(c, 'Spending controls', cp['spend_columns'], 'bs-spend'))
    fu = c.followup
    fu_src = {x['id']: x for x in fu['sources']}
    fu_html = ('<h4 class="t" id="bs-awx-followup">Airwallex follow-up, 30 October 2026</h4><p class="dek">%s %s</p><ul class="dek">%s</ul>'
               '<p class="dek"><b>Not established:</b> %s</p><p class="pnote">Pages checked: %s.</p>' % (
                   E(fu['note']), E(fu['method']),
                   ''.join('<li>%s <span class="src">&ldquo;%s&rdquo;, <a href="%s" rel="noopener nofollow" target="_blank">%s</a></span></li>' % (
                       E(f['text']), E(f['quote']), E(fu_src[f['source']]['url']), E(fu_src[f['source']]['title'])) for f in fu['findings']),
                   E(' '.join(fu['not_established'])),
                   '; '.join('<a href="%s" rel="noopener nofollow" target="_blank">%s</a> (server fetch %s, browser %s Toronto time; capture SHA-256 %s&hellip;)' % (
                       E(x['url']), E(x['title']), toronto_time(x['server_fetched_at']), toronto_time(x['browser_rendered_at']), E(x['html_sha256'][:16])) for x in fu['sources'])))
    out.append('<details class="bs-more bs-cmp-read" id="bs-cmp-read"><summary>Sources and how to read the comparison</summary>'
               '<p class="dek">%s</p>'
               '<p class="dek">A label beside an entry means it is not a plain published fact. &ldquo;Published pages disagree&rdquo; is the status Conflicting. A restriction set in bold (such as &ldquo;Not offered to businesses in Quebec&rdquo;) is the status Explicitly unavailable. &ldquo;Not checked&rdquo; means no valid check was completed, and &ldquo;Not found in reviewed sources&rdquo; means the reviewed pages did not establish it; neither means a feature is unavailable. Restriction lines beside a provider repeat what its pages state and are not a complete eligibility assessment. <a href="#bs-statuses">What each status means</a>.</p>'
               '<p class="dek" id="bs-unclear">%s</p></details>' % (E(cp['note']), E(cp['unclear'])))
    out.append('<details class="bs-more bs-cmp-read" id="bs-cmp-evidence"><summary>Detailed evidence and reconciliation notes</summary>%s'
               '<p class="dek">How the reported differences were classified: <a href="#bs-recon">reconciliation of the ten differences</a>.</p>%s</details>'
               % (compare_sources(c), fu_html))
    out.append('<p class="pnote dlinks"><b>Download the data:</b> <a href="/%s" download>every observation from 23 October 2026 with its source (CSV)</a>. The Airwallex follow-up of 30 October 2026 is recorded above and is not in the file.</p>' % CSV_REL)
    out.append(view_close('compare'))

    # ---------- 3. Messaging & offers ----------
    # Founder brief (2026-10-30, third): one reading table, two examples, the evidence per provider in expanders.
    ex = n['examples']
    vm = views['messaging']
    out.append(view_open('messaging', 'bs-messaging'))
    out.append('<p class="bs-obs">%s</p>' % E(vm['observed']))
    mrows = ''.join('<tr id="bs-msg-%s"><td class="brandcell"><a href="#bs-p-%s">%s</a></td><td data-label="Main message">%s</td><td data-label="What stood out">%s</td></tr>\n' % (
        pid, pid, E(c.name(pid)), E(n['platforms'][pid]['main_message']), E(n['platforms'][pid]['stood_out'])) for pid in c.order)
    out.append('<div class="tblock" id="bs-msg-table"><p class="ktag">My reading</p><h3 id="bs-msg-h">%s</h3><p class="bs-tnote">%s</p>'
               '<div class="tw cards" tabindex="0" role="region" aria-labelledby="bs-msg-h"><table class="bs"><caption class="sr-only">My reading of each platform&rsquo;s main message, from pages observed on 23 October 2026</caption>'
               '<thead><tr><th scope="col">Platform</th><th scope="col">Main message</th><th scope="col">What stood out</th></tr></thead><tbody>\n%s</tbody></table></div></div>'
               % (E(vm['table_title']), E(vm['table_note']), mrows))
    exs = ''.join(example_card(c, e) for e in ex['items'] if e.get('place') == 'messaging')
    out.append('<div id="bs-examples" class="sub"><h3>Selected examples</h3><p class="dek">%s</p>%s</div>' % (E(ex['dek']), exs))
    out.append('<div id="bs-platforms" class="sub"><h3>%s</h3><p class="dek">%s</p>%s</div>' % (
        E(vm['evidence_title']), E(vm['evidence_dek']), ''.join(platform_block(c, pid) for pid in c.order)))
    out.append(view_close('messaging'))

    # ---------- 4. Application journeys ----------
    jn = n['journeys']
    out.append(view_open('journeys', 'bs-journeys'))
    head = ''.join('<th scope="col">%s</th>' % E(l) for _, l in jn['table_columns'])
    rows = []
    for pid in c.order:
        r = jn['rows'][pid]
        cells = ''.join('<td data-label="%s">%s</td>' % (E(l), E(r[k])) for k, l in jn['table_columns'])
        status = ''.join(status_tag(c.obs[i]['status']) for i in r['ids'][:1])
        rl = ''.join('<span class="bs-restr"><b>%s:</b> %s</span>' % (E(l), E(t)) for l, t, _ in r.get('restrictions', []))
        rows.append('<tr id="bs-jt-%s"><td class="brandcell"><a href="#bs-jev-%s">%s</a>%s%s</td>%s</tr>' % (pid, pid, E(c.name(pid)), status, rl, cells))
    out.append('<div class="tblock" id="bs-journey-table">'
               '<div class="tw cards" tabindex="0" role="region" aria-label="First screen after each main start button, scrolls sideways"><table class="bs"><caption class="sr-only">First screen after each provider&rsquo;s main start button, 23 October 2026</caption>'
               '<thead><tr><th scope="col">Platform</th>%s</tr></thead><tbody>\n%s\n</tbody></table></div></div>' % (head, '\n'.join(rows)))
    out.append('<div class="sub" id="bs-journey-reading"><div class="note reading"><span class="lbl">My reading</span><p>%s</p></div>'
               '<p class="dlinks bs-tlink"><a href="#bs-t3">%s<span aria-hidden="true"> &rarr;</span></a></p></div>' % (E(jn['reading']), E(jn['test_link'])))
    jlabels = [('start', 'Starting page and button'), ('dest', 'Destination'), ('asks', 'Fields asked for'), ('elig', 'Eligibility shown'),
               ('next', 'Next step and consent wording'), ('limit', 'Availability note'), ('stop', 'Where inspection stopped')]
    jev = []
    for pid in c.order:
        r = jn['rows'][pid]
        t0 = c.obs[r['ids'][0]]['observed_at']
        dd = ''.join('<dt>%s</dt><dd>%s</dd>' % (E(l), E(r[k])) for k, l in jlabels)
        dd += '<dt>Observed</dt><dd>%s, %s Toronto time <span class="evlinks">(%s)</span></dd>' % (long_date(t0), toronto_time(t0), id_links(r['ids']))
        jev.append('<h4 class="t" id="bs-jev-%s">%s</h4><dl class="chain">%s</dl>' % (pid, E(c.name(pid)), dd))
    e3 = [e for e in ex['items'] if e.get('place') == 'journeys']
    out.append('<details class="bs-more" id="bs-jt-evidence"><summary>First-screen evidence</summary><p class="dek">%s</p>%s%s</details>' % (
        E(jn['note']), ''.join(jev), ''.join(example_card(c, e, 'bs-e3') for e in e3)))
    out.append(view_close('journeys'))

    # ---------- 5. Lessons & tests ----------
    # Tests first, each with the change and the measure, the full chain in an expander; the patterns under "Other observations".
    pt = n['patterns']
    ts = n['tests']
    out.append(view_open('lessons', 'bs-lessons'))
    lis = []
    for t in ts['items']:
        dd = []
        for k, l in TEST_ROWS:
            v = E(t[k])
            if k == 'observation':
                v += ' <span class="evlinks">(%s)</span>' % id_links(t['evidence'])
            dd.append('<dt>%s</dt><dd>%s</dd>' % (E(l), v))
        lis.append('<li id="bs-%s"><span class="ktag test">Proposed test, not a result</span><h3 class="bs-ttitle">Test %s. %s</h3>'
                   '<dl class="bs-tmain"><dt>The change</dt><dd>%s</dd><dt>What to measure</dt><dd>%s</dd></dl>'
                   '<details class="bs-more"><summary>Evidence and test setup</summary><p class="dek dlinks">From <a href="#bs-%s">finding %s</a>.</p><dl>%s</dl></details></li>' % (
                       t['id'].lower(), t['id'][1:], E(t['title']), E(t['change_short']), E(t['measure_short']), t['finding'].lower(), t['finding'][1:], ''.join(dd)))
    out.append('<div id="bs-tests" class="sub"><ol class="tests">%s</ol><p class="dek bs-datanote">%s</p></div>' % (''.join(lis), E(ts['data_note'])))
    pts = ''.join('<p class="dek"><b>%s.</b> %s%s <b>Denominator:</b> %s</p>%s' % (
        E(x['title']), E(x['body']), (' <b>Exceptions:</b> %s' % E(x['exceptions'])) if x['exceptions'] else '', E(x['denominator']), ev_links(c, x['evidence'])) for x in pt['items'])
    out.append('<details class="bs-more" id="bs-patterns"><summary>%s</summary><p class="dek">%s</p>%s</details>' % (E(pt['title']), E(pt['dek']), pts))
    out.append(view_close('lessons'))

    # ---------- 6. Social Media Content (only with a derived module in review or reviewed) ----------
    if c.social:
        out.append(view_open('social', 'bs-social'))
        out.append(social.panel_html(c))
        out.append(view_close('social'))

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
        fixes = ''.join(' Metadata fix, %s' % f for f in c.edition.get('snapshot_metadata_fixes', []))
        page_head += ('\n<!-- Snapshot of edition %s as first published. Research content in this snapshot is never rewritten; '
                      'record any later metadata fix in this comment.%s -->' % (c.edition['edition'], fixes))
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
