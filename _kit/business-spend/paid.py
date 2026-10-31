"""Paid Social Strategy: the active Meta ads of the six brands in Canada (founder request, 2026-10-30).

paid_ads.json comes from paid_derive.py (private raw collection, never in the repository); paid_narrative.json is the editorial layer.
"""
import collections
import csv
import html
import io
import json
import os
import statistics

KIT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(KIT, 'paid_ads.json')
NARRATIVE = os.path.join(KIT, 'paid_narrative.json')
CSV_REL = 'assets/index/business-spend/business-spend-index-paid-ads-v1.csv'
NAMES = {'venn': 'Venn', 'float': 'Float', 'ramp': 'Ramp', 'loop': 'Loop', 'keep': 'Keep', 'airwallex': 'Airwallex'}
E = lambda s: html.escape(s, quote=True)
EXT = '<span class="sr-only"> (opens in a new tab)</span>'


def load():
    if not os.path.exists(DATA):
        return None
    with open(DATA, encoding='utf-8') as f:
        d = json.load(f)
    with open(NARRATIVE, encoding='utf-8') as f:
        d['narrative'] = json.load(f)
    errs = check(d)
    if errs:
        raise SystemExit('paid ads data fails its checks:\n  ' + '\n  '.join(errs))
    return d


def check(d):
    errs = []
    ids = [r['id'] for r in d['records']]
    if len(set(ids)) != len(ids):
        errs.append('paid: duplicate ad ids')
    for r in d['records']:
        if r['platform'] not in NAMES or r['days_running'] < 0:
            errs.append('paid: bad record %s' % r['id'])
    n = d['narrative']
    if [m['pid'] for m in n['messages']] != list(NAMES):
        errs.append('paid: one message row per brand, in order')
    if len(n['suggests']) > 3:
        errs.append('paid: at most three suggestions')
    return errs


def summary(d, pid):
    rs = [r for r in d['records'] if r['platform'] == pid]
    if not rs:
        return None
    fm = collections.Counter(r['format'] for r in rs)
    land = collections.Counter(r['landing'] for r in rs)
    return {'n': len(rs), 'library': d['library_counts'].get(pid), 'versions': sum(r['versions'] for r in rs),
            'oldest': min(r['start'] for r in rs), 'median_days': statistics.median(r['days_running'] for r in rs),
            'recent': sum(1 for r in rs if r['days_running'] <= 30), 'formats': fm, 'cta': collections.Counter(r['cta'] for r in rs),
            'landing': land, 'placements': collections.Counter(p for r in rs for p in r['placements'])}


def _long(day, long_date):
    return long_date(day + 'T12:00:00-04:00')


def _fmt(fm):
    lab = {'dynamic': 'dynamic (several versions)', 'video': 'video', 'image': 'image'}
    return ', '.join('%d %s' % (v, lab.get(k, k)) for k, v in fm.most_common())


def tab_html(d, order, long_date):
    n = d['narrative']
    out = ['<div class="bs-soc-cov" id="bs-paid-scope"><p class="bs-obs">%s</p><p class="dek">%s</p></div>' % (E(n['view']['scope']), E(n['view']['limits']))]
    head = lambda i, t, q: '<h3><span class="soc-n">%d</span>%s</h3><p class="dek soc-q">%s</p>' % (i, E(t), E(q))
    rows = []
    for pid in order:
        s = summary(d, pid)
        if not s:
            rows.append('<tr><td class="brandcell">%s</td><td data-label="Active ads">0</td><td data-label="Running since" colspan="4">No active ads in Canada when collected.</td></tr>' % E(NAMES[pid]))
            continue
        top = '; '.join('%s (%d)' % (E(k), v) for k, v in s['landing'].most_common(3))
        rows.append('<tr><td class="brandcell">%s</td><td data-label="Active ads">%d<span class="cell-sub">%d versions; library count %s</span></td>'
                    '<td data-label="Running since">%s<span class="cell-sub">%d of %d started in the last 30 days</span></td><td data-label="Formats">%s</td>'
                    '<td data-label="Button">%s</td><td data-label="Where the ads lead">%s</td></tr>' % (
                        E(NAMES[pid]), s['n'], s['versions'], s['library'], _long(s['oldest'], long_date), s['recent'], s['n'], E(_fmt(s['formats'])),
                        E(', '.join('%s (%d)' % kv for kv in s['cta'].most_common())), top))
    out.append('<div class="sub soc-sec" id="bs-paid-activity">%s<div class="tw cards" tabindex="0" role="region" aria-label="Active Meta ads by brand"><table class="bs"><thead><tr>'
               '<th scope="col">Brand</th><th scope="col">Active ads</th><th scope="col">Running since</th><th scope="col">Formats</th><th scope="col">Button</th><th scope="col">Where the ads lead</th></tr></thead><tbody>%s</tbody></table></div>'
               '<p class="pnote">%s Every brand with ads placed them on Facebook and Instagram; most also ran on Threads, and some on Messenger, WhatsApp or Audience Network.</p></div>'
               % (head(1, 'Activity at a glance', 'How much each brand is running, and where the ads send people.'), ''.join(rows), E(n['counts_note'])))
    rows = ''.join('<tr><td class="brandcell">%s</td><td data-label="Main ad message">%s</td><td data-label="Offers and figures in the ads">%s</td><td data-label="Conditions in the ad text">%s</td></tr>' % (
        E(NAMES[m['pid']]), E(m['message']), E(m['offers']), E(m['conditions'])) for m in n['messages'])
    out.append('<div class="sub soc-sec" id="bs-paid-messages">%s<p class="ktag">My reading of the ad text</p><div class="tw cards" tabindex="0" role="region" aria-label="Ad messages and offers"><table class="bs"><thead><tr>'
               '<th scope="col">Brand</th><th scope="col">Main ad message</th><th scope="col">Offers and figures in the ads</th><th scope="col">Conditions in the ad text</th></tr></thead><tbody>%s</tbody></table></div></div>'
               % (head(2, 'Messages and offers', 'What the ads promise, and whether the condition travels with the promise.'), rows))
    ex = []
    for e in n['examples']:
        ex.append('<article class="card ex soc-ex" id="bs-paid-%s"><p class="kind">%s</p><h4 class="t">%s</h4><p class="dek">%s</p><p class="dek"><b>My reading:</b> %s</p><p class="pnote bs-soc-lim"><b>Limits:</b> %s</p></article>'
                  % (e['id'].lower(), E(NAMES[e['pid']]), E(e['title']), E(e['observed']), E(e['reading']), E(e['limits'])))
    out.append('<div class="sub soc-sec" id="bs-paid-examples">%s%s</div>' % (head(3, 'Selected ads', 'Four approaches worth noticing, chosen for how they present the offer, not for reach.'), ''.join(ex)))
    rows = ''.join('<tr><td class="brandcell">%s</td><td data-label="In the ads, 30 October">%s</td><td data-label="On the website, 23 October">%s</td></tr>' % (
        E(NAMES[w['pid']]), E(w['ads']), E(w['web'])) for w in n['website_check'])
    out.append('<div class="sub soc-sec" id="bs-paid-vs-web">%s<div class="tw cards" tabindex="0" role="region" aria-label="Ads compared with the website evidence"><table class="bs"><thead><tr>'
               '<th scope="col">Brand</th><th scope="col">In the ads, 30 October</th><th scope="col">On the website, 23 October</th></tr></thead><tbody>%s</tbody></table></div><p class="pnote">%s</p><p class="pnote">%s</p></div>'
               % (head(4, 'Ads beside the website', 'Where the ads say something different from the website evidence.'), rows, E(n['website_check_note']), E(n['ramp_note'])))
    items = ''.join('<li><dl class="bs-tmain"><dt>What I observed</dt><dd>%s</dd><dt>My reading</dt><dd>%s</dd><dt>A possible test</dt><dd>%s</dd></dl></li>' % (
        E(x['observed']), E(x['reading']), E(x['test'])) for x in n['suggests'])
    out.append('<div class="sub soc-sec" id="bs-paid-suggests">%s<ol class="soc-sug">%s</ol></div>' % (head(5, 'What this suggests', 'What the ads suggest, with a test for each.'), items))
    return '\n'.join(out)


def reference_html(d, order, long_date, toronto_time):
    rows = ''.join('<tr><td class="brandcell">%s<span class="cell-sub">%s</span></td><td data-label="Ad"><a href="%s" rel="noopener nofollow" target="_blank">%s%s</a><span class="cell-sub">%s</span></td>'
                   '<td data-label="Format">%s, %d version%s</td><td data-label="Placements">%s</td><td data-label="Button and destination">%s<span class="cell-sub">%s</span></td><td data-label="Flags">%s</td></tr>' % (
                       E(NAMES[r['platform']]), E(_long(r['start'], long_date)), E(r['library_url']), E(r['id']), EXT, E(r['headline'] or '(no headline)'),
                       E(r['format']), r['versions'], '' if r['versions'] == 1 else 's', E(', '.join(r['placements'])), E(r['cta']), E(r['landing']),
                       E('; '.join(x for x, f in (('template text not filled in', r['template_unrendered']), ('US card disclosure', r['us_card_disclosure']),
                                                  ('Canadian card disclosure', r['canadian_card_disclosure']), ('mentions @tryramp', r['mentions_tryramp'])) if f) or 'None'))
                   for r in d['records'])
    lc = ', '.join('%s %d' % (NAMES[p], d['library_counts'][p]) for p in order)
    return ('<div id="bs-paid-method"><h4 class="t">How the ads were collected</h4><p class="dek">%s, collected %s at %s Toronto time with the %s. Library counts that day: %s. '
            'The raw collection, with full ad copy and media links, is kept privately (SHA-256 %s&hellip;); this page and its download keep the ad ID, start date, format, versions, placements, button, destination page and headline. '
            'Ad text was read in full; videos and images were not reviewed. Spend, impressions and reach are not shown by the library for these ads in Canada. A few records show an impressions label of &ldquo;&lt;100&rdquo;; it is not used.</p></div>'
            '<div id="bs-paid-records"><h4 class="t">Ad records (%d)</h4><div class="tw" tabindex="0" role="region" aria-label="Ad records, scrolls sideways"><table class="bs soc-cl"><thead><tr><th scope="col">Brand and start</th><th scope="col">Ad and headline</th><th scope="col">Format</th><th scope="col">Placements</th><th scope="col">Button and destination</th><th scope="col">Flags</th></tr></thead><tbody>%s</tbody></table></div></div>'
            % (E(d['source']), long_date(d['collected_at']), toronto_time(d['collected_at']), E(d['tool']), lc, E(d['raw_sha256'][:16]), len(d['records']), rows))


HEAD = ['ad_id', 'brand', 'facebook_page', 'ad_library_url', 'start_date', 'days_running_at_collection', 'format', 'versions', 'placements', 'button', 'destination', 'headline',
        'template_text_not_filled_in', 'us_card_disclosure', 'canadian_card_disclosure', 'mentions_tryramp', 'collected_at']


def render_csv(d):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(HEAD)
    safe = lambda v: ("'" + v) if isinstance(v, str) and v[:1] in ('=', '+', '-', '@') else v
    for r in d['records']:
        w.writerow([r['id'], NAMES[r['platform']], r['page_name'], r['library_url'], r['start'], r['days_running'], r['format'], r['versions'], '; '.join(r['placements']),
                    r['cta'], r['landing'], safe(r['headline']), *('yes' if r[k] else 'no' for k in ('template_unrendered', 'us_card_disclosure', 'canadian_card_disclosure', 'mentions_tryramp')),
                    d['collected_at']])
    return buf.getvalue()
