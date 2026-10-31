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
CREATIVES = os.path.join(KIT, 'paid_creatives.json')
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
    d['creatives'] = None
    if os.path.exists(CREATIVES):
        with open(CREATIVES, encoding='utf-8') as f:
            d['creatives'] = json.load(f)
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


def legacy_html(d, order, long_date):
    """The ad-text reading of 30 October (the tab before the 2026-10-31 creative review), kept in Sources & evidence."""
    n = d['narrative']
    out = ['<div class="bs-soc-cov" id="bs-paid-ref-scope"><p class="bs-obs">%s</p><p class="dek">%s</p></div>' % (E(n['view']['scope']), E(n['view']['limits']))]
    head = lambda i, t, q: '<h4 class="t">%s</h4><p class="dek">%s</p>' % (E(t), E(q))
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
    out.append('<div class="sub soc-sec" id="bs-paid-ref-activity">%s<div class="tw cards" tabindex="0" role="region" aria-label="Active Meta ads by brand"><table class="bs"><thead><tr>'
               '<th scope="col">Brand</th><th scope="col">Active ads</th><th scope="col">Running since</th><th scope="col">Formats</th><th scope="col">Button</th><th scope="col">Where the ads lead</th></tr></thead><tbody>%s</tbody></table></div>'
               '<p class="pnote">%s Every brand with ads placed them on Facebook and Instagram; most also ran on Threads, and some on Messenger, WhatsApp or Audience Network.</p></div>'
               % (head(1, 'Activity at a glance', 'How much each brand is running, and where the ads send people.'), ''.join(rows), E(n['counts_note'])))
    rows = ''.join('<tr><td class="brandcell">%s</td><td data-label="Main ad message">%s</td><td data-label="Offers and figures in the ads">%s</td><td data-label="Conditions in the ad text">%s</td></tr>' % (
        E(NAMES[m['pid']]), E(m['message']), E(m['offers']), E(m['conditions'])) for m in n['messages'])
    out.append('<div class="sub soc-sec" id="bs-paid-ref-messages">%s<p class="ktag">My reading of the ad text</p><div class="tw cards" tabindex="0" role="region" aria-label="Ad messages and offers"><table class="bs"><thead><tr>'
               '<th scope="col">Brand</th><th scope="col">Main ad message</th><th scope="col">Offers and figures in the ads</th><th scope="col">Conditions in the ad text</th></tr></thead><tbody>%s</tbody></table></div></div>'
               % (head(2, 'Messages and offers', 'What the ads promise, and whether the condition travels with the promise.'), rows))
    ex = []
    for e in n['examples']:
        ex.append('<article class="card ex soc-ex" id="bs-paid-ref-%s"><p class="kind">%s</p><h4 class="t">%s</h4><p class="dek">%s</p><p class="dek"><b>My reading:</b> %s</p><p class="pnote bs-soc-lim"><b>Limits:</b> %s</p></article>'
                  % ('ref-ex-' + e['id'].lower(), E(NAMES[e['pid']]), E(e['title']), E(e['observed']), E(e['reading']), E(e['limits'])))
    out.append('<div class="sub soc-sec" id="bs-paid-ref-examples">%s%s</div>' % (head(3, 'Ad-copy notes', 'Four ads read from their text on 30 October, chosen for how they present the offer, not for reach. Ad-copy review: the visuals were reviewed separately, below.'), ''.join(ex)))
    rows = ''.join('<tr><td class="brandcell">%s</td><td data-label="In the ads, 30 October">%s</td><td data-label="On the website, 23 October">%s</td></tr>' % (
        E(NAMES[w['pid']]), E(w['ads']), E(w['web'])) for w in n['website_check'])
    out.append('<div class="sub soc-sec" id="bs-paid-ref-vs-web">%s<div class="tw cards" tabindex="0" role="region" aria-label="Ads compared with the website evidence"><table class="bs"><thead><tr>'
               '<th scope="col">Brand</th><th scope="col">In the ads, 30 October</th><th scope="col">On the website, 23 October</th></tr></thead><tbody>%s</tbody></table></div><p class="pnote">%s</p><p class="pnote">%s</p></div>'
               % (head(4, 'Ads beside the website', 'Where the ads say something different from the website evidence.'), rows, E(n['website_check_note']), E(n['ramp_note'])))
    # The tests in paid_narrative.json "suggests" left the page on 2026-10-31; they are carried to the Lessons review.
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
            'Ad text was read in full on 30 October; the images and videos were reviewed on 31 October from the same collection (see above). Spend, impressions and reach are not shown by the library for these ads in Canada. A few records show an impressions label of &ldquo;&lt;100&rdquo;; it is not used.</p></div>'
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


# ---------- Creative review (founder brief, 2026-10-31): percentage splits of distinct reviewed creatives ----------

FOCUS_L = [('product', 'Product-focused'), ('brand', 'Brand-focused'), ('brand_product', 'Brand + product'), ('not_assessed', 'Unclear / not assessed')]
FORMAT_L = [('video', 'Video'), ('image', 'Image'), ('carousel', 'Carousel'), ('other', 'Other'), ('not_assessed', 'Unclear / not assessed')]
STAGE_L = [('TOF', 'TOF · Awareness'), ('MOF', 'MOF · Consideration'), ('BOF', 'BOF · Action'), ('Mixed', 'Mixed'), ('not_assessed', 'Unclear / not assessed')]
APPROACH_L = {'product_demo': 'Product demonstration', 'product_shot': 'Product shot', 'customer_led': 'Customer-led', 'influencer_led': 'Influencer-led',
              'ugc_style': 'UGC-style', 'founder_led': 'Founder-led', 'brand_spokesperson': 'Brand spokesperson', 'scripted_skit': 'Scripted skit',
              'motion_graphics': 'Motion graphics', 'text_led_graphic': 'Text-led graphic', 'testimonial_quote': 'Testimonial quote',
              'competitor_comparison': 'Comparison with banks or rivals', 'lifestyle_photo': 'Lifestyle photo'}
THEME_L = {'fees_fx': 'Saving on fees or FX', 'rewards_cashback_interest': 'Rewards or interest', 'finance_admin_automation': 'Reducing finance admin',
           'spend_control': 'Spend control', 'international_payments': 'International payments', 'switching_from_bank': 'Switching providers',
           'account_opening_speed': 'Fast account opening', 'credit_financing': 'Credit or financing', 'accounting_integration': 'Accounting integration',
           'bill_pay': 'Bill pay', 'expense_management': 'Expense management', 'sector_specific': 'Industry-specific message', 'company_scale_trust': 'Company scale or trust'}
PERSONA_L = {'business_owner': 'Business owner', 'finance_leader': 'Finance leader', 'accountant_bookkeeper': 'Accountant or bookkeeper',
             'ecommerce_operator': 'Ecommerce operator', 'industry': 'Industry-specific audience', 'general_business': 'General business audience',
             'not_clear': 'Unclear / not assessed'}
UNCLEAR = 'Unclear / not assessed'
TOP_N = 8


def _other_label(k):
    t = (k.split(':', 1)[1] if ':' in k else k).strip().replace('_', ' ')
    t = ' '.join(w.upper() if w in ('tv', 'fx', 'qa', 'ui') else w for w in t.split())
    return t[:1].upper() + t[1:]


def approach_label(k):
    return 'Other observed approaches' if k == 'other' else (APPROACH_L.get(k) or _other_label(k))


def theme_label(k):
    return 'Other themes' if k == 'other' else (THEME_L.get(k) or _other_label(k))


def persona_key(p):
    return 'industry' if (p or '').startswith('industry') else (p if p in PERSONA_L else 'not_clear')


def sample(d, pid):
    """The brand's distinct creatives: every reviewed asset group, minus records a reviewer marked as the same execution."""
    cr = (d.get('creatives') or {}).get('creatives') or []
    return [c for c in cr if c['pid'] == pid and not c.get('same_as')]


def labels_of(c, dim):
    """Category keys for one creative. Exclusive dimensions return one key; overlapping ones return a set (unclear when empty)."""
    if dim == 'focus':
        return [c['focus']]
    if dim == 'format':
        return [c['format']]
    if dim == 'stage':
        return [c['stage']]
    if dim == 'approach':
        ks = sorted({'other' if k.startswith('other') else k for k in c['approaches'] if k != 'not_assessed'})
        return ks if (ks and c['inspection'] != 'not_assessed') else [UNCLEAR]
    if dim == 'theme':
        return sorted({'other' if k.startswith('other') else k for k in c['themes']}) or [UNCLEAR]
    if dim == 'persona':
        ks = sorted({persona_key(p['persona']) for p in c['personas']})
        return ks or ['not_clear']
    raise KeyError(dim)


def counts(cs, dim):
    out = collections.Counter()
    for c in cs:
        for k in set(labels_of(c, dim)):
            out[k] += 1
    return out


def pct(n, total):
    return int(round(100.0 * n / total)) if total else 0


def _val(n, total):
    return '%d%% &middot; %d of %d creative%s' % (pct(n, total), n, total, '' if total == 1 else 's')


def _cats(dim, cs_all):
    """Category order for a dimension, the same for every brand."""
    if dim == 'focus':
        return FOCUS_L
    if dim == 'format':
        return FORMAT_L
    if dim == 'stage':
        return STAGE_L
    tot = counts(cs_all, dim)
    lab = {'approach': approach_label, 'theme': theme_label, 'persona': lambda k: PERSONA_L.get(k, k)}[dim]
    keys = sorted((k for k in tot if k not in (UNCLEAR, 'not_clear', 'other')), key=lambda k: (-tot[k], lab(k)))
    tail = [k for k in ('other', UNCLEAR, 'not_clear') if k in tot]
    return [(k, UNCLEAR if k in (UNCLEAR, 'not_clear') else lab(k)) for k in keys + tail]


def _stack(cs, cats, label):
    total = len(cs)
    c = counts(cs, cats is STAGE_L and 'stage' or cats is FORMAT_L and 'format' or 'focus')
    x, rects, key = 0.0, [], []
    for i, (k, lab) in enumerate(cats):
        n = c.get(k, 0)
        if not n:
            continue
        w = 1000.0 * n / total
        cls = 'pd-c-un' if k == 'not_assessed' else 'pd-c%d' % (i + 1)
        rects.append('<rect class="%s" x="%.2f" y="0" width="%.2f" height="18"/>' % (cls, x, w))
        key.append('<li><span class="pd-sw %s" aria-hidden="true"></span>%s <b>%s</b></li>' % (cls, E(lab), _val(n, total)))
        x += w
    return ('<svg class="pd-stack" viewBox="0 0 1000 18" preserveAspectRatio="none" role="img" aria-label="%s"><title>%s</title>%s</svg><ul class="pd-key">%s</ul>'
            % (E(label), E(label), ''.join(rects), ''.join(key)))


def _bars(cs, cats, dim):
    total = len(cs)
    c = counts(cs, dim)
    rows = []
    for i, (k, lab) in enumerate(cats):
        n = c.get(k, 0)
        w = 0 if not total else 200.0 * n / total
        rows.append('<li class="%s"><span class="pd-bl">%s</span><svg class="pd-bar" viewBox="0 0 200 10" preserveAspectRatio="none" aria-hidden="true" focusable="false">'
                    '<rect class="pd-track" width="200" height="10" rx="2"/><rect class="%s" width="%.2f" height="10" rx="2"/></svg><span class="pd-bv">%s</span></li>'
                    % ('pd-extra' if i >= TOP_N else '', E(lab), 'pd-c-un' if lab == UNCLEAR else 'pd-fill', w, _val(n, total) if n else '0 of %d' % total))
    return '<ul class="pd-bars">%s</ul>' % ''.join(rows)


def _brand_head(pid, cs, d):
    found = len(sample(d, pid))
    reviewed = sum(1 for c in cs if c['inspection'] != 'not_assessed')
    cov = 'all %d reviewed' % found if reviewed == found else 'partial sample: %d of %d reviewed' % (reviewed, found)
    return '<p class="pd-brand"><b>%s</b> <span class="pd-n">%d distinct creative%s, %s</span></p>' % (E(NAMES[pid]), found, '' if found == 1 else 's', cov)


def coverage(d, order):
    have, none = [], []
    for pid in order:
        cs = sample(d, pid)
        (have if cs else none).append(pid)
    return have, none


def _dim_panel(d, have, dim, title, overlap, cs_all):
    cats = _cats(dim, cs_all)
    if overlap:
        cards = ''.join('<div class="pd-card">%s%s</div>' % (_brand_head(pid, sample(d, pid), d), _bars(sample(d, pid), cats, dim)) for pid in have)
        more = ('<button type="button" class="pd-showall" aria-expanded="false" hidden>Show all categories (%d)</button>' % len(cats)) if len(cats) > TOP_N else ''
        body = '<p class="pd-note">A creative can appear in more than one category.</p><div class="pd-cards">%s</div>%s' % (cards, more)
    else:
        body = '<div class="pd-stacks">%s</div>' % ''.join('<div class="pd-srow">%s%s</div>' % (
            _brand_head(pid, sample(d, pid), d), _stack(sample(d, pid), cats, '%s, %s' % (NAMES[pid], title.lower()))) for pid in have)
    return '<div class="pd-dim" data-dim="%s" id="bs-paid-dim-%s"><h4 class="t pd-dimh">%s</h4>%s</div>' % (dim, dim, E(title), body)


def tab_html(d, order, long_date):
    n = d['narrative']
    cr = d.get('creatives')
    if not cr:
        return '<p class="dek">%s</p>' % E(n['creative']['pending'])
    cv = n['creative']
    have, none = coverage(d, order)
    cs_all = [c for pid in have for c in sample(d, pid)]
    out = ['<p class="soc-lim pd-lead">%s</p>' % E(cv['share_note'])]
    nocov = '; '.join('%s: %s' % (NAMES[p], E(cv['coverage_status'].get(p, 'no active ads in Canada found in the snapshot'))) for p in none)
    head = lambda i, t: '<h3><span class="soc-n">%d</span>%s</h3>' % (i, E(t))
    # 1. Creative mix by brand
    sel = ''.join('<button type="button" class="pd-opt" data-dim="%s" aria-pressed="%s">%s</button>' % (k, 'true' if i == 0 else 'false', E(t))
                  for i, (k, t) in enumerate((('focus', 'Focus'), ('format', 'Format'), ('approach', 'Creative approach'), ('theme', 'Theme'))))
    panels = (_dim_panel(d, have, 'focus', 'Focus', False, cs_all) + _dim_panel(d, have, 'format', 'Format', False, cs_all)
              + _dim_panel(d, have, 'approach', 'Creative approach', True, cs_all) + _dim_panel(d, have, 'theme', 'Theme', True, cs_all))
    stood = ''.join('<li>%s</li>' % E(x['text']) for x in cv.get('mix_stood_out', []))
    out.append('<div class="sub soc-sec pd-sec" id="bs-paid-mix">%s<div class="pd-sel" role="group" aria-label="Compare the creative mix by" hidden>%s</div>'
               '<div class="pd-dims" data-pd-dims>%s</div>%s%s</div>'
               % (head(1, cv['mix_title']), sel, panels,
                  ('<div class="pd-stood"><p><b>What stood out</b></p><ul>%s</ul></div>' % stood) if stood else '',
                  ('<p class="soc-lim">Not compared: %s.</p>' % nocov) if nocov else ''))
    # 2. Audience and buying stage
    out.append('<div class="sub soc-sec pd-sec" id="bs-paid-audience">%s<p class="soc-lim pd-lead">%s</p>%s%s%s</div>'
               % (head(2, cv['audience_title']), E(cv['audience_note']),
                  _dim_panel(d, have, 'persona', 'Customer personas', True, cs_all),
                  _dim_panel(d, have, 'stage', 'Likely buying stage', False, cs_all),
                  _not_observed(d, have)))
    # 3. Selected creative examples
    out.append('<div class="sub soc-sec pd-sec" id="bs-paid-examples">%s%s</div>' % (head(3, cv['examples_title']), examples_html(d, cv)))
    return '\n'.join(out)


def _not_observed(d, have):
    lines = []
    for pid in have:
        c = counts(sample(d, pid), 'stage')
        miss = [lab for k, lab in STAGE_L[:3] if not c.get(k)]
        if miss:
            lines.append('%s: %s' % (NAMES[pid], ', '.join(miss)))
    return ('<p class="soc-lim">Not observed in the reviewed sample: %s.</p>' % E('; '.join(lines))) if lines else ''


def _chips(c):
    lab = dict(FOCUS_L)
    chips = [lab[c['focus']], dict(FORMAT_L)[c['format']]] + [approach_label(a) for a in c['approaches']]
    return ''.join('<span class="pd-chip">%s</span>' % E(x) for x in chips)


def examples_html(d, cv):
    byid = {c['id']: c for c in d['creatives']['creatives']}
    cards = []
    for i, ex in enumerate(cv['examples']):
        c = byid[ex['creative']]
        img = ex.get('image')
        fig = ('<figure class="pd-shot"><img src="%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async"><figcaption>%s</figcaption></figure>'
               % (E(img['src']), E(img['alt']), img['width'], img['height'], E(img['caption']))) if img else ''
        kind = '' if img else '<p class="pd-adcopy">Ad-copy review: the visual was not reviewed.</p>'
        personas = ', '.join(sorted({PERSONA_L[persona_key(p['persona'])] for p in c['personas']})) or UNCLEAR
        card = ('<article class="pd-ex%s" id="bs-paid-x%d">%s<div class="pd-ex-text"><p class="soc-tags">%s</p><p class="pd-hook">%s</p><p class="pd-chips">%s</p>'
                '<p class="pd-meta"><b>Appears to address:</b> %s &middot; <b>Likely stage:</b> %s</p>%s<p class="soc-stood"><b>What stood out:</b> %s</p></div></article>'
                % (' has-img' if img else '', i + 1, fig, E(NAMES[c['pid']]), E(ex.get('hook') or c['hook']), _chips(c), E(personas), E(dict(STAGE_L)[c['stage']]),
                   kind, E(ex['stood_out'])))
        cards.append(card)
    first, rest = cards[:4], cards[4:]
    more = ('<details class="pd-more"><summary>More examples (%d)</summary><div class="pd-exs">%s</div></details>' % (len(rest), ''.join(rest))) if rest else ''
    return '<div class="pd-exs">%s</div>%s' % (''.join(first), more)


def creative_reference_html(d, order):
    """Sources & evidence: how the creatives were reviewed, deduplicated and counted, and one row per creative."""
    cr = d.get('creatives')
    if not cr:
        return ''
    cv = d['narrative']['creative']
    rows = []
    kids = collections.defaultdict(list)
    for c in cr['creatives']:
        if c.get('same_as'):
            kids[c['same_as']].append(c)
    for c in cr['creatives']:
        if c.get('same_as'):
            continue
        group = [c] + kids[c['id']]
        c = dict(c, ads=sorted({a for g in group for a in g['ads']}), exact_variants=sum(g['exact_variants'] for g in group),
                 id=c['id'] + ((' with ' + ', '.join(g['id'] for g in kids[c['id']])) if kids[c['id']] else ''))
        rows.append('<tr><td class="brandcell">%s<span class="cell-sub">%s</span></td><td data-label="Ads">%s<span class="cell-sub">%d asset%s</span></td>'
                    '<td data-label="Reviewed">%s<span class="cell-sub">%s</span></td><td data-label="Focus and format">%s, %s</td><td data-label="Approach">%s</td>'
                    '<td data-label="Themes">%s</td><td data-label="Personas">%s</td><td data-label="Stage">%s<span class="cell-sub">%s</span></td><td data-label="Hook">%s</td></tr>' % (
                        E(NAMES[c['pid']]), E(c['id']),
                        ', '.join('<a href="https://www.facebook.com/ads/library/?id=%s" rel="noopener nofollow" target="_blank">%s%s</a>' % (E(a), E(a), EXT) for a in c['ads'][:3]) + (' and %d more' % (len(c['ads']) - 3) if len(c['ads']) > 3 else ''),
                        c['exact_variants'], '' if c['exact_variants'] == 1 else 's',
                        E(c['inspection']), E(c['inspection_note']), E(dict(FOCUS_L)[c['focus']]), E(dict(FORMAT_L)[c['format']]),
                        E(', '.join(approach_label(a) for a in c['approaches']) or UNCLEAR), E(', '.join(theme_label(t) for t in c['themes']) or UNCLEAR),
                        E('; '.join('%s (%s)' % (PERSONA_L[persona_key(p['persona'])], p['clue']) for p in c['personas']) or UNCLEAR),
                        E(dict(STAGE_L)[c['stage']]), E(c['stage_reason']), E(c['hook'])))
    have, none = coverage(d, order)
    tally = '; '.join('%s %d' % (NAMES[p], len(sample(d, p))) for p in have)
    rules = ''.join('<li>%s</li>' % E(x) for x in cv['method'])
    return ('<div id="bs-paid-creative-method"><h4 class="t">How the creatives were reviewed and counted</h4><ul class="dek">%s</ul>'
            '<p class="dek">Distinct creatives by brand: %s. Classification data: <code>_kit/business-spend/paid_creatives.json</code> in the site repository (no media links or full ad copy).</p></div>'
            '<div id="bs-paid-creatives"><h4 class="t">Distinct reviewed creatives (%d)</h4><p class="dek">One row per distinct creative; the ids after &ldquo;with&rdquo; are resized or re-cut copies merged into it.</p><div class="tw" tabindex="0" role="region" aria-label="Reviewed creatives, scrolls sideways"><table class="bs soc-cl"><thead><tr>'
            '<th scope="col">Brand and creative</th><th scope="col">Ads</th><th scope="col">Review</th><th scope="col">Focus and format</th><th scope="col">Approach</th><th scope="col">Themes</th><th scope="col">Personas and clue</th><th scope="col">Stage</th><th scope="col">Hook</th></tr></thead><tbody>%s</tbody></table></div></div>'
            % (rules, tally, len(rows), ''.join(rows)))
