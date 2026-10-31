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
import re
import io
import json
import os
import sys
from datetime import datetime

import model
import paid
import social
import validate

PAGE = os.path.join(model.ROOT, 'business-spend-index.html')
KIT_DIR = os.path.dirname(os.path.abspath(__file__))
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
        self.paid = paid.load()
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


def cell_status(c, pid, key):
    spec = c.n['compare']['rows'][pid][key]
    ids = spec.get('ids', [])
    statuses = [c.obs[i]['status'] for i in ids]
    if not ids:
        return 'not_checked'
    if 'conflicting' in statuses:
        return 'conflicting'
    if spec.get('text') is None:
        return statuses[0]
    if 'explicitly_unavailable' in statuses:
        return 'explicitly_unavailable'
    return 'published'


def unclear_tag(c, spec):
    if any('D' in (c.obs[i].get('reconciliation') or {}).get('class', '') for i in spec.get('ids', [])):
        return '<a class="st st-undetermined" href="#bs-unclear">%s</a>' % E(spec['unclear'])
    return ''


def cell(c, pid, key, label):
    spec = c.n['compare']['rows'][pid][key]
    ids = spec.get('ids', [])
    status = cell_status(c, pid, key)
    if spec.get('text') is None:
        # A missing entry shows its status in the same label style as every other status (2026-10-31).
        why = re.sub(r'^Not checked:\s*', '', re.split(r'(?<=\.)\s', c.obs[ids[0]]['statement'])[0]) if ids else ''
        body = '<span class="st st-%s">%s</span>%s' % (status, E(model.STATUSES[status]), ('<span class="cell-sub">%s</span>' % E(why[0].upper() + why[1:])) if why else '')
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
    tag += unclear_tag(c, spec)
    # The 30 October follow-up is one note under the table, not a link inside each cell (2026-10-31).
    return '<td%s data-label="%s">%s%s</td>' % (cls, E(label), body, tag)


def glance_cell(c, pid, key, label):
    """Short form of a detail cell for the at-a-glance table; the status and evidence are the detail cell's."""
    spec = c.n['compare']['rows'][pid][key]
    text = c.n['compare']['glance'][pid][key]
    status = cell_status(c, pid, key)
    if text is None:
        return '<td class="miss" data-label="%s"><span class="st st-%s">%s</span></td>' % (E(label), status, E(model.STATUSES[status]))
    tag = '' if status == 'explicitly_unavailable' else table_tag(status, spec)
    return '<td data-label="%s"><span class="cell-main">%s</span>%s%s</td>' % (E(label), E(text), tag, unclear_tag(c, spec))


def glance_table(c, num):
    cp = c.n['compare']
    cols = cp['glance_columns']
    ths = ''.join('<th scope="col">%s</th>' % E(l) for _, l in cols)
    rows = '\n'.join('<tr id="bs-glance-%s"><td class="brandcell">%s</td>%s</tr>' % (pid, E(c.name(pid)), ''.join(glance_cell(c, pid, k, l) for k, l in cols)) for pid in c.order)
    return ('<div class="tblock" id="bs-cmp-glance"><h3 id="bs-cmp-glance-h"><span class="soc-n">%d</span>%s</h3><p class="bs-tnote">%s</p>'
            '<div class="tw cards" tabindex="0" role="region" aria-labelledby="bs-cmp-glance-h"><table class="bs bs-glance">'
            '<caption class="sr-only">Rewards, plan fees, card spending in another currency and accounting connections for six platforms, as published on 23 October 2026</caption>'
            '<thead><tr><th scope="col">Platform</th>%s</tr></thead><tbody>\n%s\n</tbody></table></div></div>'
            % (num, E(cp['glance_title']), E(cp['glance_note']), ths, rows))


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


def table(c, title, cols, tid, head=True, note=None, restrictions=False, link=False, num=None, after=''):
    ths = ''.join('<th scope="col">%s</th>' % E(l) for _, l in cols)
    rows = []
    for pid in c.order:
        cells = ''.join(cell(c, pid, k, l) for k, l in cols)
        extra = restriction_lines(c, pid) if restrictions else ''
        name = ('<a href="#bs-p-%s">%s</a>' % (pid, E(c.name(pid)))) if link else E(c.name(pid))   # plain in the tabs (2026-10-30, final)
        rows.append('<tr id="%s-%s"><td class="brandcell">%s%s</td>%s</tr>' % (tid, pid, name, extra, cells))
    label = ('<h3 id="%s-h">%s%s</h3>' % (tid, ('<span class="soc-n">%d</span>' % num) if num else '', E(title))) if head else ''
    if note:
        label += '<p class="bs-tnote">%s</p>' % E(note)
    region = ('aria-labelledby="%s-h"' % tid) if head else ('aria-label="%s"' % E(title))
    return ('<div class="tblock" id="%s">%s'
            '<div class="tw cards" tabindex="0" role="region" %s><table class="bs">'
            '<caption class="sr-only">%s for six platforms, as published on 23 October 2026</caption>'
            '<thead><tr><th scope="col">Platform</th>%s</tr></thead><tbody>\n%s\n</tbody></table></div>%s</div>'
            % (tid, label, region, E(title), ths, '\n'.join(rows), after))


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
             '<a href="#bs-spend-%s">spending controls</a> rows in Product Comparison, and its <a href="#bs-jt-%s">first screen</a> in Customer Journey.</p>'
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
            '<p class="dek">Ankit Kumar, Help Me Marketing. <em>How Six Business Finance Brands Market Their Products</em>, a marketing case study in The HMM Index. Edition %s, first published as the Business Cards &amp; Spend Management Index. Public pages captured %s%s. <a href="%s">%s</a></p>'
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


VIEW_ORDER = [('overview', 'bs-overview'), ('social', 'bs-social'), ('paid', 'bs-paid'), ('messaging', 'bs-messaging'), ('compare', 'bs-compare'), ('journeys', 'bs-journeys'), ('lessons', 'bs-lessons')]


def view_order(c):
    # Tab order and labels (founder, 2026-10-30): Overview, Social Media Content, Messaging & Offers, Compare Products,
    # Application Journey, Lessons. The Social view shows only with a derived module in review or reviewed.
    return [v for v in VIEW_ORDER if (v[0] != 'social' or c.social) and (v[0] != 'paid' or getattr(c, 'paid', None))]


TEST_ROWS = [('observation', 'Observed evidence'), ('question', 'Customer question'), ('reading', 'My interpretation'),
             ('hypothesis', 'Testable hypothesis'), ('change', 'One change'), ('comparable', 'What stays comparable'),
             ('measure', 'Primary measurement'), ('guardrail', 'Guardrail'), ('limitation', 'When the result would be inconclusive')]




def msg_glance_reference(c, n):
    """Sources & evidence: the observations behind each row of "Messaging at a glance" (founder brief, 2026-10-31)."""
    rows = ''.join('<li><b>%s.</b> %s %s</li>' % (E(c.name(pid)), E(n['platforms'][pid]['glance']['promise']),
                   ev_links(c, n['platforms'][pid]['glance']['ev']).replace('<p class="evlinks">', '<span class="evlinks">').replace('</p>', '</span>')) for pid in c.order)
    return '<div id="bs-msg-glance-ev"><h4 class="t">Messaging at a glance: evidence</h4><p class="dek">Each row reads the homepage, a relevant product page and the proof linked from them, observed 23 October 2026; audience lines quote the site where it names one.</p><ul class="dek">%s</ul></div>' % rows


def web_capture_reference(c):
    """Sources & evidence: the 31 October 2026 captures behind the Website Messaging examples."""
    web = json.load(open(os.path.join(KIT_DIR, 'web_examples_2026-10-31.json'), encoding='utf-8'))
    items = ''.join('<li><b>%s, %s.</b> <a href="%s" rel="noopener nofollow" target="_blank">%s%s</a>, captured %s, %s Toronto time (HTTP %d). Wording: %s %s Crop box %s of the private full screenshot (sha256 %s&hellip;); published crop sha256 %s&hellip;. %s</li>' % (
        E(c.name(w['pid'])), E({'value': 'value proposition', 'proof': 'proof', 'cta': 'call to action'}[w['kind']]), E(w['url']), E(w['url']), EXT,
        E(iso_long(w['captured_at'][:10])), E(toronto_time(w['captured_at'])), w['http_status'], E(w['quote']), E(w['matches_23_october']),
        E(', '.join(str(v) for v in w['crop'])), E(w['capture_sha256'][:16]), E(w['sha256'][:16]),
        ev_links(c, w['observations']).replace('<p class="evlinks">', '<span class="evlinks">').replace('</p>', '</span>')) for w in web['captures'])
    return '<div id="bs-msg-captures"><h4 class="t">Website examples: captures of 31 October 2026</h4><p class="dek">%s %s</p><ul class="dek">%s</ul></div>' % (E(web['note']), E(web['method']), items)

# Line icons for the Customer Journey stages (Tabler outline shapes, 24px grid, currentColor).
_SV = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" focusable="false">%s</svg>'
JOURNEY_ICONS = {
    'route': _SV % '<circle cx="6" cy="19" r="2"/><circle cx="18" cy="5" r="2"/><path d="M12 19h4.5a3.5 3.5 0 0 0 0-7h-8a3.5 3.5 0 0 1 0-7H12"/>',
    'doc': _SV % '<path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M9 13h6M9 17h4"/>',
    'shield': _SV % '<path d="M12 3a12 12 0 0 0 8.5 3A12 12 0 0 1 12 21 12 12 0 0 1 3.5 6 12 12 0 0 0 12 3"/><path d="m9 12 2 2 4-4"/>',
    'card': _SV % '<rect x="3" y="5" width="18" height="14" rx="3"/><path d="M3 10h18M7 15h.01M11 15h2"/>',
}


def journey_followup_reference(c, n):
    """Sources & evidence: the 31 October 2026 follow-up records and where each Customer Journey comparison cell comes from."""
    jf = json.load(open(os.path.join(KIT_DIR, 'journey_followup_2026-10-31.json'), encoding='utf-8'))
    kinds = {'help_centre': 'Help centre (provider description)', 'website_faq': 'Website FAQ (provider description)', 'entry_route': 'Entry route (observed)', 'blocked': 'Not readable from this review'}
    stg = {'entry': 'Start', 'prepare': 'Provide details', 'review': 'Verification and decision', 'first_use': 'First use'}
    recs = []
    for r in jf['records']:
        recs.append('<li id="jf-%s"><b>%s, %s.</b> <a href="%s" rel="noopener nofollow" target="_blank">%s%s</a>. %s, %s, %s Toronto time (HTTP %s). %s. Stage: %s.%s %s%s%s</li>' % (
            E(r['id']), E(c.name(r['pid'])), E(r['route']), E(r['url']), E(r['title']), EXT, E(kinds[r['kind']]), E(iso_long(r['captured_at'][:10])), E(toronto_time(r['captured_at'])), r['http_status'],
            E('Scope: ' + r['scope']), E(', '.join(stg[s] for s in r['stages'])),
            (' Wording: &ldquo;%s&rdquo;' % E(r['wording'])) if r['wording'] else '', E(r['summary']),
            (' <i>%s</i>' % E(r['uncertainty'])) if r['uncertainty'] else '', '' if r['used'] else ' Not used in the comparison.'))
    jl = n['journey']['labels']
    def refs(ids):
        return ', '.join(('<a href="#jf-%s">%s</a>' % (i, i)) if i.startswith('J-') else id_links([i]) for i in ids)
    cells = []
    for pid in c.order:
        g = n['journeys']['rows'][pid]['guide']
        cells.append('<li><b>%s.</b> %s</li>' % (E(c.name(pid)), '; '.join('%s: %s (%s)' % (E(l), ', '.join(E(jl[k]) for k, _, _ in g[col]), '; '.join(refs(ids) for _, _, ids in g[col])) for col, l in n['journey']['compare_columns'])))
    return ('<div id="bs-journey-followup"><h4 class="t">Follow-up of 31 October 2026: help centres and entry routes</h4><p class="dek">%s %s</p>'
            '<p class="dek">Qualifications kept with every finding: provider time estimates are not guarantees; account approval and credit card approval may be separate; published guidance does not confirm that an application route is open; a step not reviewed is not evidence that the provider lacks it.</p>'
            '<ul class="dek">%s</ul></div><div id="bs-journey-coverage"><h4 class="t">Where each comparison cell comes from</h4><ul class="dek">%s</ul></div>') % (E(jf['note']), E(jf['method']), ''.join(recs), ''.join(cells))


def journey_capture_reference(c):
    """Sources & evidence: the 31 October 2026 captures behind the Customer Journey examples."""
    doc = json.load(open(os.path.join(KIT_DIR, 'journey_examples_2026-10-31.json'), encoding='utf-8'))
    items = ''.join('<li><b>%s.</b> <a href="%s" rel="noopener nofollow" target="_blank">%s%s</a>, captured %s, %s Toronto time (HTTP %d). Wording: %s %s Crop box %s of the private full screenshot (sha256 %s&hellip;); published crop sha256 %s&hellip;. %s</li>' % (
        E(c.name(w['pid'])), E(w['url']), E(w['url']), EXT, E(iso_long(w['captured_at'][:10])), E(toronto_time(w['captured_at'])), w['http_status'],
        E(w['quote']), E(w['matches_23_october']), E(', '.join(str(v) for v in w['crop'])), E(w['capture_sha256'][:16]), E(w['sha256'][:16]),
        ev_links(c, w['observations']).replace('<p class="evlinks">', '<span class="evlinks">').replace('</p>', '</span>')) for w in doc['captures'])
    return '<div id="bs-journey-captures"><h4 class="t">Earlier first-screen examples: captures of 31 October 2026</h4><p class="dek">%s %s</p><ul class="dek">%s</ul></div>' % (E(doc['note']), E(doc['method']), items)


def msg_support_reference(c, n):
    """Sources & evidence: every "How the promise is supported" check with the observations behind it (founder review, 2026-10-31)."""
    ms = n['messaging_support']
    rows = []
    for pid in c.order:
        for k, lab in ms['checks']:
            cell = ms[pid][k]
            rows.append('<li><b>%s, %s: %s.</b> %s %s</li>' % (E(c.name(pid)), E(lab.lower()), E(ms['labels'][cell['s']]), E(cell['t']),
                        ev_links(c, cell['ev']).replace('<p class="evlinks">', '<span class="evlinks">').replace('</p>', '</span>')))
    return '<div id="bs-msg-support-ev"><h4 class="t">How each promise is supported: evidence</h4><ul class="dek">%s</ul></div>' % ''.join(rows)

def example_card(c, e, eid=None, evidence=True):
    # Short form (2026-10-30): heading, the observed fact, one sentence of my reading, the evidence link.
    return ('<div class="card ex"%s><h4 class="t">%s</h4><p class="dek">%s</p>'
            '<p class="dek"><b>My reading:</b> %s</p>%s</div>' % (
                (' id="%s"' % eid) if eid else '', E(e['title']), E(e['body']), E(e['lesson']), ev_links(c, e['evidence']) if evidence else ''))


# Line icons for the Overview guide (founder brief, 2026-10-30, final): restrained, decorative only (the text carries the meaning).
_SVG = '<svg class="bs-gi" viewBox="0 0 48 48" width="40" height="40" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">%s</svg>'
ICONS = {
    'post': _SVG % '<rect x="9" y="7" width="30" height="34" rx="4"/><rect x="14" y="12" width="20" height="14" rx="2"/><circle cx="20" cy="17" r="2"/><path d="M14 24l6-5 5 4 3-2 6 5"/><path d="M14 31h20M14 36h12"/>',
    'bubble': _SVG % '<path d="M8 12a5 5 0 0 1 5-5h22a5 5 0 0 1 5 5v14a5 5 0 0 1-5 5H21l-8 7v-7a5 5 0 0 1-5-5z"/><path d="M15 15h18M15 22h12"/>',
    'grid': _SVG % '<rect x="7" y="9" width="34" height="30" rx="3"/><path d="M7 19h34M7 29h34M19 9v30M30 9v30"/>',
    'steps': _SVG % '<circle cx="10" cy="24" r="4"/><circle cx="24" cy="24" r="4"/><circle cx="38" cy="24" r="4"/><path d="M14 24h6M28 24h6"/>',
    'ads': _SVG % '<path d="M8 20v8a2 2 0 0 0 2 2h4l10 7V11L14 18h-4a2 2 0 0 0-2 2z"/><path d="M31 18a8 8 0 0 1 0 12M35 13a14 14 0 0 1 0 22"/>',
    'check': _SVG % '<path d="M9 13l3 3 5-6M9 25l3 3 5-6M9 37l3 3 5-6"/><path d="M22 13h17M22 25h17M22 37h17"/>',
}

EXT = ' <span class="sr-only">(opens in a new tab)</span>'


def sources_view(c, views, start, end, draft):
    """The one reference view: the full research trail behind every tab (founder brief, 2026-10-30, final). Not a tab; the
    "Sources & evidence" link beside the tabs opens it and its return control goes back to the tab the reader came from."""
    n, ed = c.n, c.edition
    m = n['method']
    when = '%s, %s to %s Toronto time' % (long_date(start), toronto_time(start), toronto_time(end))
    parts = []
    toc = [('bs-ref-scope', 'Scope, dates and coverage'), ('bs-ref-web', 'Website evidence by provider'), ('bs-ref-social', 'Social accounts, posts, classifications and engagement'), ('bs-ref-paid', 'Paid ads: collection and records'),
           ('bs-ref-journey', 'Customer-journey evidence'), ('bs-ref-tests', 'Findings and full test specifications'), ('bs-ref-status', 'Status definitions and reconciliation'),
           ('bs-ref-images', 'Image provenance'), ('bs-ref-author', 'Author and relationship disclosure'), ('bs-cite', 'Citation'),
           ('bs-editions', 'Edition history and corrections'), ('bs-ref-downloads', 'Downloads')]
    if not c.social:
        toc = [t for t in toc if t[0] not in ('bs-ref-social', 'bs-ref-images')]
    if not c.paid:
        toc = [t for t in toc if t[0] != 'bs-ref-paid']
    if draft:
        toc = [t for t in toc if t[0] != 'bs-cite']
    back = '<p class="bs-ref-back"><a href="#bs-overview" data-bs-back>&larr; <span>Back to the index</span></a></p>'
    v = views['sources']
    parts.append('<section id="bs-sources" class="bs-view bs-ref" aria-labelledby="bs-sources-h">%s<div class="sec-head"><h2 id="bs-sources-h">%s</h2><p class="dek">%s</p></div>'
                 '<nav class="bs-reftoc" aria-label="Sources and evidence contents"><ol>%s</ol></nav>' % (
                     back, E(v['title']), E(v['dek']), ''.join('<li><a href="#%s">%s</a></li>' % (i, E(t)) for i, t in toc)))

    def sec(sid, title, html_):
        parts.append('<div class="bs-refsec" id="%s"><h3>%s</h3>%s</div>' % (sid, E(title), html_))

    # 1. Scope, dates and coverage
    about = ''.join('<div class="kind"><dt>%s</dt><dd>%s</dd></div>' % (E(a), E(b)) for a, b in n['about'])
    leg = ''.join('<div class="kind kind-%d"><dt>%s</dt><dd>%s</dd></div>' % (i, E(a), E(b)) for i, (a, b) in enumerate(n['legend']))
    ch = n['chain']
    lim = ''.join('<li>%s</li>' % E(x) for x in m['limitations'])
    nobs, nsrc = len(c.obs), len(c.sources)
    nbr = sum(1 for x in c.sources.values() if x['method'] == 'browser')
    fu = c.followup
    sec('bs-ref-scope', 'Scope, dates and coverage',
        '<div id="bs-about"><p class="dek">%s</p><dl class="legend">%s</dl></div>'
        '<div id="bs-method"><div id="bs-scope"><h4 class="t">Scope</h4><p class="dek">%s</p><h4 class="t">Selection</h4><p class="dek">%s</p>'
        '<h4 class="t">Dates</h4><p class="dek">Websites observed %s. %s%s</p><h4 class="t">Public sources only</h4><p class="dek">%s</p>%s'
        '<h4 class="t">Limitations</h4><ul class="dek">%s</ul>'
        '<p class="pnote">%d observations from %d captures of public pages (%d by server fetch, %d in a browser), six platforms, edition %s.</p></div></div>'
        '<div id="bs-guide"><h4 class="t">How to read the analysis</h4><dl class="legend">%s</dl><h4 class="t chain-h">How each conclusion is reached</h4>'
        '<ol class="chain-steps">%s</ol><p class="pnote m0">%s</p></div>' % (
            E(views['overview']['about_intro']), about, E(m['scope']), E(m['selection']), E(when), E(m['dates']),
            (' A separately dated follow-up on Airwallex only was checked on %s; it is not part of the 23 October observations.' % iso_long(fu['checked_on'])) if fu else '',
            E(m['public_only']), social.method_html(c.social) if c.social else '', lim, nobs, nsrc, nsrc - nbr, nbr, E(ed['edition']),
            leg, ''.join('<li>%s</li>' % E(s_) for s_ in ch['steps']), E(ch['note'])))
    # 2. Website evidence by provider
    cp = n['compare']
    sec('bs-ref-web', 'Website evidence by provider',
        '<p class="dek">%s</p>%s%s<h4 class="t">Each provider&rsquo;s pages</h4><p class="dek">%s</p><div id="bs-platforms">%s</div>%s' % (
            E(cp['note']), table(c, 'More product details', cp['card_columns'], 'bs-cards', link=True), table(c, 'Account and transfer details', cp['acct_columns'], 'bs-xt', link=True),
            E(views['messaging']['evidence_dek']), ''.join(platform_block(c, pid) for pid in c.order),
            compare_sources(c) + '<h4 class="t">Messaging examples: evidence</h4><ul class="dek">%s</ul>' % ''.join(
                '<li><b>%s.</b> %s</li>' % (E(e['title']), ev_links(c, e['evidence']).replace('<p class="evlinks">', '<span class="evlinks">').replace('</p>', '</span>'))
                for e in n['examples']['items'] if e.get('place') == 'messaging'))
            + msg_glance_reference(c, n) + msg_support_reference(c, n) + web_capture_reference(c))
    # 3. Social accounts, posts and attribution
    if c.social:
        sec('bs-ref-social', 'Social accounts, posts, classifications and engagement', social.strategy_reference_html(c) + social.reference_html(c) + (social.analysis_reference_html(c.social) if c.social.get('analysis') else ''))
    if c.paid:
        sec('bs-ref-paid', 'Paid ads: collection, creative review and records', paid.creative_reference_html(c.paid, c.order) + paid.reference_html(c.paid, c.order, long_date, toronto_time) + '<div id="bs-paid-adtext"><h4 class="t">Ad-text reading, 30 October 2026</h4>' + paid.legacy_html(c.paid, c.order, long_date) + '</div>')
    # 4. Customer-journey evidence
    jn = n['journeys']
    jlabels = [('start', 'Starting page and button'), ('dest', 'Destination'), ('asks', 'Fields asked for'), ('elig', 'Eligibility shown'),
               ('next', 'Next step and consent wording'), ('limit', 'Availability note'), ('stop', 'Where inspection stopped')]
    jev = []
    for pid in c.order:
        r = jn['rows'][pid]
        t0 = c.obs[r['ids'][0]]['observed_at']
        dd = ''.join('<dt>%s</dt><dd>%s</dd>' % (E(l), E(r[k])) for k, l in jlabels)
        dd += ''.join('<dt>%s</dt><dd>%s</dd>' % (E(l), E(t)) for l, t, _ in r.get('restrictions', []))
        dd += '<dt>Observed</dt><dd>%s, %s Toronto time <span class="evlinks">(%s)</span></dd>' % (long_date(t0), toronto_time(t0), id_links(r['ids']))
        jev.append('<div id="bs-jt-%s"><h4 class="t" id="bs-jev-%s">%s</h4><dl class="chain">%s</dl></div>' % (pid, pid, E(c.name(pid)), dd))
    jy = n['journey']
    stage_ev = journey_followup_reference(c, n)
    e3 = [e for e in n['examples']['items'] if e.get('place') == 'journeys']
    sec('bs-ref-journey', 'Customer-journey evidence',
        '<div id="bs-jt-evidence"><h4 class="t">First screens</h4><p class="dek">%s</p>%s%s</div>'
        '%s'
        '%s'
        '<h4 class="t" id="bs-journey-gaps">Gaps for a later edition</h4><p class="dek">Targeted checks that would make the later stages fuller. None is a broad new collection.</p><ul class="dek">%s</ul>' % (
            E(jn['note']), ''.join(jev), ''.join(example_card(c, e, 'bs-e3') for e in e3), stage_ev, journey_capture_reference(c), ''.join('<li>%s</li>' % E(g) for g in jy['gaps'])))
    # 5. Findings and full test specifications
    fl = []
    for it in n['findings']['items']:
        an = ', '.join('<a href="#%s">%s</a>' % (a[1], E(a[0])) for a in it['analysis'])
        fl.append('<div class="bs-fdetail" id="bs-%s-detail"><h4 class="t">Finding %s. %s</h4><dl class="chain"><dt>What the sources say</dt><dd>%s <b>Denominator:</b> %s %s</dd>'
                  '<dt>Customer question</dt><dd>&ldquo;%s&rdquo;</dd><dt>My reading</dt><dd>%s</dd><dt>Where it shows</dt><dd class="dlinks">%s. Proposed test: <a href="#bs-%s">test %s</a>.</dd></dl></div>' % (
                      it['id'].lower(), it['id'][1:], E(it['title']), E(it['body']), E(it['denominator']),
                      ev_links(c, it['evidence']).replace('<p class="evlinks">', '<span class="evlinks">').replace('</p>', '</span>'),
                      E(it['question']), E(it['reading']), an, it['test'].lower(), it['test'][1:]))
    tl = []
    for t in n['tests']['items']:
        dd = []
        for k, l in TEST_ROWS:
            val = E(t[k])
            if k == 'observation':
                val += ' <span class="evlinks">(%s)</span>' % id_links(t['evidence'])
            dd.append('<dt>%s</dt><dd>%s</dd>' % (E(l), val))
        tl.append('<div class="bs-tspec" id="bs-%s-spec"><h4 class="t">Test %s. %s <span class="ktag test">Proposed test, not a result</span></h4><dl class="chain">%s</dl></div>' % (
            t['id'].lower(), t['id'][1:], E(t['title']), ''.join(dd)))
    pt = n['patterns']
    pts = ''.join('<p class="dek"><b>%s.</b> %s%s <b>Denominator:</b> %s</p>%s' % (
        E(x['title']), E(x['body']), (' <b>Exceptions:</b> %s' % E(x['exceptions'])) if x['exceptions'] else '', E(x['denominator']), ev_links(c, x['evidence'])) for x in pt['items'])
    sec('bs-ref-tests', 'Findings and full test specifications',
        '%s<p class="dek"><b>A question to start with:</b> %s</p>%s<p class="dek">%s</p><div id="bs-patterns"><h4 class="t">Other observations across the six</h4><p class="dek">%s</p>%s</div>' % (
            ''.join(fl), E(n['findings']['take']), ''.join(tl), E(n['tests']['data_note']), E(pt['dek']), pts))
    # 6. Status definitions and reconciliation
    st = ''.join('<dt>%s</dt><dd>%s</dd>' % (E(a), E(b)) for a, b in m['statuses'])
    fu_html = ''
    if fu:
        fu_src = {x['id']: x for x in fu['sources']}
        rc = fu.get('recheck')
        fu_html = ('<h4 class="t" id="bs-awx-followup">Airwallex follow-up, checked %s</h4><p class="dek">%s %s%s</p><ul class="dek">%s</ul>'
                   '<p class="dek"><b>Not established:</b> %s</p><p class="pnote">Pages checked: %s.</p>' % (
                       iso_long(fu['checked_on']), E(fu['note']), E(fu['method']), (' ' + E(rc['note'])) if rc else '',
                       ''.join('<li>%s <span class="src">&ldquo;%s&rdquo;, <a href="%s" rel="noopener nofollow" target="_blank">%s%s</a></span></li>' % (
                           E(f['text']), E(f['quote']), E(fu_src[f['source']]['url']), E(fu_src[f['source']]['title']), EXT) for f in fu['findings']),
                       E(' '.join(fu['not_established'])),
                       '; '.join('<a href="%s" rel="noopener nofollow" target="_blank">%s%s</a> (server fetch %s, browser %s Toronto time; capture SHA-256 %s&hellip;)' % (
                           E(x['url']), E(x['title']), EXT, toronto_time(x['server_fetched_at']), toronto_time(x['browser_rendered_at']), E(x['html_sha256'][:16])) for x in fu['sources'])))
    sec('bs-ref-status', 'Status definitions and reconciliation',
        '<h4 class="t" id="bs-statuses">What each status means</h4><dl class="statdefs">%s</dl>'
        '<div id="bs-cmp-read"><p class="dek">A label beside an entry means it is not a plain published fact. &ldquo;Published pages disagree&rdquo; is the status Conflicting. A restriction set in bold (such as &ldquo;Not offered to businesses in Quebec&rdquo;) is the status Explicitly unavailable. &ldquo;Not checked&rdquo; means no valid check was completed, and &ldquo;Not found in reviewed sources&rdquo; means the reviewed pages did not establish it; neither means a feature is unavailable. Restriction lines beside a provider repeat what its pages state and are not a complete eligibility assessment.</p>'
        '<p class="dek" id="bs-unclear">%s</p></div>%s%s' % (st, E(cp['unclear']), recon_details(c, inline=True), fu_html))
    # 7. Image provenance
    if c.social:
        sec('bs-ref-images', 'Image provenance', social.images_html(c.social))
    # 8. Author and relationship disclosure
    rel = ed['relationship_disclosure']
    if rel['status'] == 'complete':
        rel_html = '<p class="dek"><b>Relationship disclosure.</b> %s</p>' % E(rel['text'])
    else:
        rel_html = ('<div class="note gap"><span class="lbl">Placeholder</span><p>Relationship disclosure pending. Before publication I will state here whether '
                    'I or Help Me Marketing have any commercial connection with any of the six providers.</p></div>')
    sec('bs-ref-author', 'Author and relationship disclosure',
        '<div id="bs-research"><p class="dek">Research and analysis by <a href="/about">Ankit Kumar</a>, founder of Help Me Marketing, a marketing practice in Halton Hills, Ontario. This Index reads marketing pages; it is not financial, legal or regulatory advice.</p>%s</div>' % rel_html)
    # 9 and 10. Citation, edition history and corrections
    log = ''.join('<li><b>%s.</b> %s</li>' % (E(d), E(x)) for d, x in m.get('corrections_log', []))
    corr = ('<h4 class="t" id="bs-corrections">Corrections</h4><p class="dek">%s</p>%s' % (
        E(m['corrections']).replace('Hello@helpmemarketing.com', '<a href="mailto:Hello@helpmemarketing.com">Hello@helpmemarketing.com</a>'),
        ('<ul class="dek corrections-log">%s</ul>' % log) if log else '<p class="pnote m0">No corrections recorded.</p>'))
    if not draft:
        cite, ed_table = cite_and_editions(c)
        sec('bs-cite', 'Citation', cite)
        sec('bs-editions', 'Edition history and corrections', ed_table + corr)
    else:
        sec('bs-editions', 'Edition history and corrections', corr)
    # 11. Downloads
    dl = ['<li><a href="/%s" download>Website observations from 23 October 2026 (CSV)</a>: platform, category, observation, status, market and plan, conditions, source URL and capture time. My interpretations and the Airwallex follow-up of 30 October 2026 are not in the file.</li>' % CSV_REL]
    if c.social:
        dl.append('<li><a href="/%s" download>Instagram records (CSV)</a>: all %d records, %d attributed posts and %d @tryramp records with unresolved provider attribution, marked in the provider_attribution column. Captions, displayed counts and reposts are not in the file.</li>' % (
            social.CSV_REL, len(c.social['posts']), social.attributed_count(c.social), len(c.social['posts']) - social.attributed_count(c.social)))
        if c.social.get('analysis'):
            dl.append('<li><a href="/%s" download>Social analysis, version 1 (CSV)</a>: one row per attributed post (%d), with the primary theme, secondary tags, format, creative approach and whether it was inspected, audience, product and benefit, the basis for each classification, likes and comments as displayed with their state (exact, approximate or missing) and read time, and views where recorded. Captions, comment text and commenter names are not in the file. The two files above keep their meaning and columns.</li>' % (
                social.ANALYSIS_CSV_REL, len(c.social['analysis']['posts'])))
    if c.paid:
        dl.append('<li><a href="/%s" download>Paid ads, version 1 (CSV)</a>: one row per active Meta ad collected on 30 October 2026 (%d), with the Ad Library link, start date, days running, format, versions, placements, button, destination page and headline, and flags for unfilled template text and card disclosures. Full ad copy and media are not in the file.</li>' % (
            paid.CSV_REL, len(c.paid['records'])))
    sec('bs-ref-downloads', 'Downloads', '<ul class="dek dlinks">%s</ul>' % ''.join(dl))
    parts.append(back.replace('bs-ref-back', 'bs-ref-back bs-ref-back-end') + '</section>')
    return '\n'.join(parts)


def body(c):
    n, ed = c.n, c.edition
    h = n['hero']
    start, end = ed['collection_started_at'], ed['collection_ended_at']
    when = '%s, %s to %s Toronto time' % (long_date(start), toronto_time(start), toronto_time(end))
    draft = c.mode == 'draft'
    out = ['<!-- ===== BUSINESS SPEND INDEX REPORT BODY START ===== generated by _kit/business-spend/build.py; edit the kit, not this page ===== -->', '<div class="wrap">']
    # Hero (founder brief, 2026-10-28): kicker, title, one line on what to compare, the six providers, one metadata line and one note.
    # Capture times and the scope paragraph live in "Scope & sources" (the methodology), not here.
    out.append('<header><p class="kicker">%s</p><h1>%s</h1><p class="bs-subtitle">%s</p><p class="lede">%s</p>' % (E(h['kicker']), E(h['title']), E(h['subtitle']), E(h['lede'])))
    out.append('<p class="bs-provs">%s</p>' % ' &middot; '.join(E(c.name(pid)) for pid in c.order))
    # The independence line sits in the byline since 2026-10-31 (founder; it was the note under the Overview cards).
    out.append('<p class="bs-meta">%sBy <a href="/about">Ankit Kumar</a> &middot; Edition %s &middot; %s<span class="bs-meta-ind">%s</span></p>' % (
        '<span class="draft-flag">Draft</span> ' if draft else '', E(ed['edition']), 'Not yet published' if draft else 'Last Updated %s' % E(short_date(c.date_modified or c.release_date)),
        E(h['independence'])))
    if draft:
        out.append('<p class="pnote">%s</p>' % E(h['draft_note']))
    out.append('</header>')
    views = dict(n['views'])
    if c.social:
        views['social'] = {'title': c.social['view']['title'], 'dek': c.social['view']['dek']}
    if getattr(c, 'paid', None):
        views['paid'] = {'title': c.paid['narrative']['view']['title'], 'dek': c.paid['narrative']['view']['dek']}
    order = view_order(c)
    # Tabs plus one small "Sources & evidence" link for the whole index (founder brief, 2026-10-30, final).
    # The Sources link sits outside the rounded tab bar, right-aligned below it (founder brief, 2026-10-31).
    out.append('<nav class="ri-nav bs-views" aria-label="Sections of this page"><div class="bs-tablist">%s</div></nav>'
               '<p class="bs-srcrow"><a class="bs-srclink" href="#bs-sources" id="bs-srclink">Sources &amp; evidence</a></p>' % ''.join(
                   '<a href="#%s" id="bs-tab-%s">%s</a>' % (vid, k, E(views[k]['title'])) for k, vid in order))

    def view_open(key, vid, cls='bs-view', dek=True):
        v = views[key]
        return ('<section id="%s" class="%s" aria-labelledby="%s-h"><div class="sec-head"><h2 id="%s-h">%s</h2>%s</div>'
                % (vid, cls, vid, vid, E(v.get('heading', v['title'])), ('<p class="dek">%s</p>' % E(v['dek'])) if dek else ''))

    def view_close(key):
        keys = [k for k, _ in order]
        i = keys.index(key)
        prev = ('<a href="#%s">&larr; Back: %s</a>' % (order[i - 1][1], E(views[order[i - 1][0]]['title']))) if i else ''
        if i + 1 < len(order):
            k2, v2 = order[i + 1]
            nxt = '<a href="#%s">Next: %s &rarr;</a>' % (v2, E(views[k2]['title']))
        else:
            nxt = '<a href="#%s">Back to %s</a>' % (order[0][1], E(views[order[0][0]]['title']))
        return '<p class="bs-next">%s%s</p></section>' % (prev, nxt)

    V = {}
    plain = lambda pid: E(c.name(pid))
    fu = c.followup

    # ---------- Overview: a visual guide to the index (founder brief, 2026-10-30, final) ----------
    vo = views['overview']
    guide = ''.join('<a class="bs-gcard" href="#bs-%s">%s<span class="bs-gt">%s</span><span class="bs-gd">%s</span></a>' % (
        k, ICONS[icon], E(views[k]['title'] if k in views else t), E(desc)) for k, t, desc, icon in vo['guide'] if k in views)
    # No intro paragraph, provider list or note below the cards: the hero carries the providers and the independence line,
    # and each section carries its own dates (founder review, 2026-10-31).
    V['overview'] = (view_open('overview', 'bs-overview', dek=False)
                     + '<nav class="bs-guide" aria-label="Sections of this case study">%s</nav>' % guide
                     + view_close('overview'))

    # ---------- Social Media Content ----------
    if c.social:
        V['social'] = view_open('social', 'bs-social') + social.strategy_html(c) + view_close('social')
    if c.paid:
        V['paid'] = view_open('paid', 'bs-paid') + paid.tab_html(c.paid, c.order, long_date) + view_close('paid')

    # ---------- Messaging & Offers ----------
    ex = n['examples']
    vm = views['messaging']
    # Founder brief (2026-10-31, second): one comparison with the same criteria for all six brands, then three visual examples.
    web = json.load(open(os.path.join(KIT_DIR, 'web_examples_2026-10-31.json'), encoding='utf-8'))
    caps = {w['id']: w for w in web['captures']}
    gl = lambda pid: n['platforms'][pid]['glance']
    mrows = ''.join('<tr id="bs-msg-%s"><td class="brandcell">%s</td><td data-label="Main promise">%s</td><td data-label="Who it speaks to">%s</td><td data-label="Why choose them?">%s</td><td data-label="Proof used">%s</td></tr>\n' % (
        pid, plain(pid), E(gl(pid)['promise']), E(gl(pid)['audience']), E(gl(pid)['why']), E(gl(pid)['proof'])) for pid in c.order)
    cards = []
    for i, x in enumerate(n['web_examples'], 1):
        w = caps[x['capture']]
        # Click to enlarge (founder, 2026-10-31): the link opens the full-resolution crop in an in-page dialog; without JavaScript it opens the image.
        cards.append('<article class="bs-wex" id="bs-wex-%d"><figure class="bs-wex-shot"><a class="bs-zoom" href="%s" data-zoom-w="%d" data-zoom-h="%d" aria-label="Enlarge screenshot: %s">'
                     '<img src="%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async"><span class="bs-zoom-hint" aria-hidden="true">Click to enlarge</span></a>'
                     '<figcaption>%s, captured %s.</figcaption></figure><div class="bs-wex-text"><p class="soc-tags">%s &middot; %s</p><p class="bs-wex-quote">%s</p>'
                     '<p class="soc-stood"><b>What stood out:</b> %s</p></div></article>' % (
                         i, E(w['zoom_src']), w['zoom_width'], w['zoom_height'], E('%s, %s' % (c.name(w['pid']), x['label'].lower())),
                         E(w['src']), E(x['alt']), w['width'], w['height'], E(c.name(w['pid'])), E(iso_long(w['captured_at'][:10])), E(x['label']), E(c.name(w['pid'])), E(x['wording']), E(x['stood_out'])))
    V['messaging'] = (view_open('messaging', 'bs-messaging')
                      + '<div class="sub soc-sec" id="bs-msg-table"><h3 id="bs-msg-h"><span class="soc-n">1</span>%s</h3><p class="soc-lim">%s</p>'
                        '<div class="tw cards" tabindex="0" role="region" aria-labelledby="bs-msg-h"><table class="bs bs-msgt"><caption class="sr-only">Main promise, audience, claimed difference and proof for six brands, from pages observed on 23 October 2026</caption>'
                        '<thead><tr><th scope="col">Brand</th><th scope="col">Main promise</th><th scope="col">Who it speaks to</th><th scope="col">Why choose them?</th><th scope="col">Proof used</th></tr></thead><tbody>\n%s</tbody></table></div></div>'
                        % (E(vm['table_title']), E(vm['table_note']), mrows)
                      + '<div id="bs-examples" class="sub soc-sec"><h3><span class="soc-n">2</span>%s</h3><p class="soc-lim">%s</p><div class="bs-wexs">%s</div>'
                        '</div>' % (E(vm['examples_title']), E(vm['examples_note']), ''.join(cards))
                      + view_close('messaging'))

    # ---------- Compare Products ----------
    cp = n['compare']
    # Product Comparison (founder, 2026-10-31): one intro line, a numbered at-a-glance table, a phone brand selector
    # for the three numbered detail parts, the Airwallex follow-up as one note, no footer note.
    fu = ('<p class="pnote bs-fu-note">%s <a href="#bs-awx-followup">See the follow-up in Sources &amp; evidence</a>.</p>' % E(cp['followup_note'])) if any(cp['rows'][p_][k].get('followup') for p_ in c.order for k, _ in cp['cost_columns']) else ''
    brand_sel = ('<div class="bs-cmp-sel" role="group" aria-label="Brands shown in parts 2 to 4" hidden><span class="bs-cmp-sel-l">Show</span>%s</div>'
                 % ''.join('<button type="button" class="bs-bopt" data-brand="%s" aria-pressed="%s">%s</button>' % (k, 'true' if k == 'all' else 'false', E(l))
                           for k, l in [('all', 'All brands')] + [(p_, c.name(p_)) for p_ in c.order]))
    V['compare'] = (view_open('compare', 'bs-compare')
                    + '<div class="bs-cmp-sec">%s</div>' % glance_table(c, 1)
                    + brand_sel
                    + '<div class="bs-cmp-sec">%s</div>' % table(c, 'Cards, rewards & costs', cp['cost_columns'], 'bs-prod', note=cp['pricing_note'], restrictions=True, num=2, after=fu)
                    + '<div class="bs-cmp-sec">%s</div>' % table(c, 'Currency fees', cp['fee_columns'], 'bs-xb', note=cp['currency_note'], num=3)
                    + '<div class="bs-cmp-sec">%s</div>' % table(c, 'Spending controls', cp['spend_columns'], 'bs-spend', num=4)
                    + view_close('compare'))

    # ---------- Customer Journey (founder brief, 2026-10-31, second): four stages, one labelled comparison, two help-page examples ----------
    jy = n['journey']
    jn = n['journeys']
    jl = jy['labels']
    stages = ''.join('<li class="bs-jst" id="bs-jst-%s"><span class="bs-jst-top"><span class="bs-sn" aria-hidden="true">%d</span><span class="bs-jst-ic" aria-hidden="true">%s</span></span>'
                     '<span class="bs-st">%s</span><span class="bs-sd">%s</span></li>' % (s['key'], i, JOURNEY_ICONS[s['icon']], E(s['name']), E(s['text'])) for i, s in enumerate(jy['stages'], 1))
    cols = jy['compare_columns']
    def gcell(items):
        return ''.join('<p class="bs-jg"><span class="bs-src bs-src-%s">%s</span> %s</p>' % (k, E(jl[k]), E(txt)) for k, txt, _ in items)
    jrows = ''.join('<tr id="bs-jt-row-%s"><td class="brandcell">%s</td>%s</tr>\n' % (pid, plain(pid), ''.join(
        '<td data-label="%s">%s</td>' % (E(l), gcell(jn['rows'][pid]['guide'][k])) for k, l in cols)) for pid in c.order)
    jf = json.load(open(os.path.join(KIT_DIR, 'journey_followup_2026-10-31.json'), encoding='utf-8'))
    jcaps = {w['id']: w for w in jf['examples']}
    jcards = []
    for i, x in enumerate(jy['examples'], 1):
        w = jcaps[x['capture']]
        jcards.append('<article class="bs-wex bs-jex" id="bs-jex-%d"><figure class="bs-wex-shot"><a class="bs-zoom" href="%s" data-zoom-w="%d" data-zoom-h="%d" aria-label="Enlarge screenshot: %s">'
                      '<img src="%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async"><span class="bs-zoom-hint" aria-hidden="true">Click to enlarge</span></a>'
                      '<figcaption>%s help centre, captured %s.</figcaption></figure><div class="bs-wex-text"><p class="soc-tags">%s &middot; %s <span class="bs-src bs-src-help">%s</span></p>'
                      '<p class="soc-stood"><b>What stood out:</b> %s</p></div></article>' % (
                          i, E(w['zoom_src']), w['zoom_width'], w['zoom_height'], E('%s, %s' % (c.name(w['pid']), x['label'].lower())),
                          E(w['src']), E(x['alt']), w['width'], w['height'], E(c.name(w['pid'])), E(iso_long(w['captured_at'][:10])), E(c.name(w['pid'])), E(x['label']), E(jl['help']), E(x['stood_out'])))
    V['journeys'] = (view_open('journeys', 'bs-journeys')
                     + '<div class="sub soc-sec" id="bs-journey-map"><h3 id="bs-jmap-h"><span class="soc-n">1</span>%s</h3>'
                       '<ol class="bs-jstages" aria-label="Four journey stages">%s</ol><p class="soc-lim bs-jnote">%s</p></div>' % (E(jy['overview_title']), stages, E(jy['overview_note']))
                     + '<div class="sub soc-sec" id="bs-journey-table"><h3 id="bs-jm-h"><span class="soc-n">2</span>%s</h3><p class="soc-lim">%s</p>'
                       '<div class="tw cards" tabindex="0" role="region" aria-labelledby="bs-jm-h"><table class="bs bs-jfirst"><caption class="sr-only">Entry routes, what to prepare, review and waiting, and getting started for six brands, from first screens observed on 23 October 2026 and help pages read on 31 October 2026</caption>'
                       '<thead><tr><th scope="col">Brand</th>%s</tr></thead><tbody>\n%s</tbody></table></div></div>' % (
                           E(jy['compare_title']), E(jy['compare_note']), ''.join('<th scope="col">%s</th>' % E(l) for _, l in cols), jrows)
                     + '<div class="sub soc-sec" id="bs-journey-examples"><h3><span class="soc-n">3</span>%s</h3><p class="soc-lim">%s</p><div class="bs-wexs bs-jexs">%s</div>'
                       '<p class="dlinks bs-tlink"><a href="#bs-t3">%s<span aria-hidden="true"> &rarr;</span></a></p></div>' % (
                           E(jy['examples_title']), E(jy['examples_note']), ''.join(jcards), E(jn['test_link']))
                     + view_close('journeys'))

    # ---------- Lessons: three tests, each with what I noticed ----------
    ts = n['tests']
    F = {f['id']: f for f in n['findings']['items']}
    lis = []
    for t in ts['items']:
        f = F[t['finding']]
        lis.append('<li id="bs-%s"><span class="ktag test">Proposed test, not a result</span><h3 class="bs-ttitle">Test %s. %s</h3><dl class="bs-tmain">'
                   '<dt>What I noticed</dt><dd id="bs-%s"><span class="bs-fig"><b>%s</b> %s.</span> %s</dd>'
                   '<dt>Change to try</dt><dd>%s</dd><dt>What to measure</dt><dd>%s</dd></dl></li>' % (
                       t['id'].lower(), t['id'][1:], E(t['title']), f['id'].lower(), E(f['figure']), E(f['figure_label']), E(f['noticed']),
                       E(t['change_short']), E(t['measure_short'])))
    V['lessons'] = (view_open('lessons', 'bs-lessons')
                    + '<div id="bs-tests" class="sub"><div id="bs-findings"></div><ol class="tests">%s</ol><p class="dek bs-datanote">%s</p>'
                      '<p class="pnote dlinks">Full test specifications, guardrails and the evidence behind each finding are in <a href="#bs-ref-tests">Sources &amp; evidence</a>.</p></div>'
                      % (''.join(lis), E(ts['data_note']))
                    + view_close('lessons'))

    out += [V[k] for k, _ in order]
    # One shared screenshot dialog outside the tab panels, so it opens from any tab (2026-10-31).
    out.append('<dialog class="bs-lightbox" id="bs-lightbox" aria-label="Enlarged screenshot"><figure><img src="" alt=""><figcaption></figcaption></figure><button type="button" class="bs-lightbox-close">Close</button></dialog>')
    out.append(sources_view(c, views, start, end, draft))

    hp = n['help']
    href = '/contact?intent=review&amp;entry=%s#contact-form' % hp['entry']
    out.append('<section id="bs-help"><div class="sec-head"><h2>%s</h2></div><div class="card"><p class="dek m0">%s</p>'
               '<a class="btn btn-primary" href="%s" data-review-cta="%s">%s</a></div></section>' % (E(hp['heading']), E(hp['body']), href, hp['entry'], E(hp['button'])))
    out.append('<footer><div class="about"><p><b>About this case study.</b> It is part of <b>The HMM Index</b> by Help Me Marketing. Edition %s, first published as the Business Cards &amp; Spend Management Index, is an independent comparative marketing case study of how six selected platforms explain business cards, spend management and cross-border payments to Canadian businesses, from public pages captured on %s%s. It is not a ranking, a product test or a recommendation.</p></div>'
               '<div class="byline-block"><p>Company names are used to report their public pages and posts and imply no relationship with Help Me Marketing.</p></div></footer>' % (
                   E(ed['edition']), long_date(start), ' and official Instagram posts published 25 July to 22 October 2026' if c.social else ''))
    out.append('</div>')
    out.append('<!-- ===== BUSINESS SPEND INDEX REPORT BODY END ===== -->')
    return '\n'.join(out)


def head_meta(c):
    ed, h = c.edition, c.n['hero']
    # Title from 2026-10-30 (founder): the case-study title. 53 characters, so no brand suffix (the budget is 60).
    title = h['title']
    og = h['title']
    desc = 'A marketing case study of how Venn, Float, Ramp, Loop, Keep and Airwallex explain their offers, publish social content and guide customers.'
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
        '<meta property="og:description" content="%s">' % E(h['lede']),
        '<meta property="og:url" content="%s">' % url,
        '<meta property="og:image" content="%s/og-image.jpg">' % SITE,
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta property="og:locale" content="en_CA">',
        '<meta property="article:author" content="Ankit Kumar">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:title" content="%s">' % E(og),
        '<meta name="twitter:description" content="%s">' % E(h['lede']),
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
    if c.paid:
        files.append((os.path.join(model.ROOT, paid.CSV_REL), paid.render_csv(c.paid)))
        if c.social.get('analysis'):
            files.append((os.path.join(model.ROOT, social.ANALYSIS_CSV_REL), social.render_analysis_csv(c.social)))
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
