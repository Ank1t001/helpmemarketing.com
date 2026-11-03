#!/usr/bin/env python3
"""Derive public paid-ad records for the strategy comparison (founder, 2026-11-02) from private Meta Ad Library output.

Usage: python3 derive_ads.py PAGE_ADS.json SNAPSHOTS.json
PAGE_ADS.json: apify/facebook-ads-scraper page-level output (fields pageID, pageName, adArchiveID, startDateFormatted,
collationCount, publisherPlatform, snapshot.displayFormat, snapshot.ctaText, snapshot.linkUrl, snapshot.title,
snapshot.body.text); SNAPSHOTS.json: the same run with the full snapshot (cards, videos). Both stay private: they hold
full ad copy and signed media links. Only derived fields, the ad's short headline and its Ad Library link are kept.
"""
import collections, datetime, hashlib, json, os, re, sys
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
FIRMS = {'762651820485779': 'Equiton', '1136216849873517': 'Skyline', '256257607565454': 'Lankin'}
COLLECTED = '2026-11-02T19:46:18-05:00'

def text_of(x, s):
    body, title = s.get('body', {}).get('text') or '', s.get('title') or ''
    cards = s.get('cards') or []
    if ('{{' in body + title) and cards:
        title, body = cards[0].get('title') or '', cards[0].get('body') or ''
    return title.strip(), re.sub(r'\s+', ' ', title + ' ' + body)

def media(s):
    cards = s.get('cards') or []
    if s.get('videos') or any(k.get('videoHdUrl') or k.get('videoSdUrl') for k in cards): return 'video'
    return 'image'

def destination(url):
    host = urlparse(url or '').netloc.replace('www.', '')
    if not host: return 'none shown'
    if host == 'fb.me': return 'Meta link (fb.me)'
    if 'calendly' in host: return 'scheduling page'
    if 'instagram' in host: return 'Instagram'
    return 'firm website'

def focus(t):
    l = t[:400].lower()  # headline and opening lines; legal notes further down mention tax and accounts
    if re.search(r'open house|own a new home|homes remaining', l): return 'home sales'
    if re.search(r'\bevents?\b|webinar|\bregister\b|turning point', l): return 'investor event'
    if re.search(r'\b(rrsp|tfsa|rrif|lira)\b|year-end|\btax\b', l): return 'registered accounts and tax'
    if re.search(r'bridleview|develop', l): return 'development offering'
    if re.search(r'14\.9%|17,000|4,000|trusted by|chosen by|net return in 2025|track record', l): return 'track record'
    if re.search(r'questions investors|how it is built|fund structure|did you know|structure tells|five drivers|without directly owning', l): return 'investor education'
    return 'fund offer'

def stage(t, cta, dest):
    l = t[:400].lower()
    if re.search(r'act fast|limited access|last chance|still thinking|only thing left is the decision|what could waiting', l) or dest == 'scheduling page' or cta in ('Book now', 'Request time'): return 'decision'
    if re.search(r'questions investors|did you know|structure tells|fund structure|five drivers', l): return 'awareness'
    return 'consideration'

def derive(page_path, snap_path):
    raw1, raw2 = open(page_path, 'rb').read(), open(snap_path, 'rb').read()
    items = [x for x in json.loads(raw1)['items'] if x and x.get('pageID') in FIRMS]
    snaps = {x['adArchiveID']: x['snapshot'] for x in json.loads(raw2)['items'] if x}
    day = datetime.date.fromisoformat(COLLECTED[:10])
    recs = []
    for x in items:
        s = snaps[x['adArchiveID']]
        head, t = text_of(x, s)
        cta = x.get('snapshot.ctaText') or ((s.get('cards') or [{}])[0].get('ctaText') or '')
        url = x.get('snapshot.linkUrl') or ((s.get('cards') or [{}])[0].get('linkUrl') or '')
        dest = destination(url)
        start = x['startDateFormatted'][:10]
        recs.append({'id': x['adArchiveID'], 'firm': FIRMS[x['pageID']], 'page': x['pageName'].strip(),
            'library_url': 'https://www.facebook.com/ads/library/?id=%s' % x['adArchiveID'],
            'start': start, 'days_running': (day - datetime.date.fromisoformat(start)).days,
            'format': media(s), 'dynamic': x.get('snapshot.displayFormat') == 'DCO', 'versions': int(x.get('collationCount') or 1),
            'placements': sorted(p.title().replace('_', ' ') for p in (x.get('publisherPlatform') or [])),
            'cta': cta, 'destination': dest, 'headline': '' if '{{' in head else head[:90],
            'focus': focus(t), 'stage': stage(t, cta, dest),
            'return_figure': bool(re.search(r'\d+(\.\d+)?\s*%', t)), 'registered_accounts': bool(re.search(r'RRSP|TFSA|RRIF|LIRA', t)),
            'minimum': bool(re.search(r'\bminimum\b|with \$\d{1,3},\d{3}\b', t, re.I)), 'local': bool(re.search(r'\b(Oakville|Orangeville|St\. Catharines)\b', t)),
            'for_investors': True})
    for r in recs:
        if r['focus'] == 'home sales': r['for_investors'] = False
    recs.sort(key=lambda r: (['Equiton', 'Skyline', 'Lankin'].index(r['firm']), r['start'], r['id']))
    return raw1, raw2, recs

if __name__ == '__main__':
    raw1, raw2, recs = derive(sys.argv[1], sys.argv[2])
    centurion = [{'id': i, 'firm': 'Centurion', 'page': 'Centurion Asset Management Inc.', 'library_url': 'https://www.facebook.com/ads/library/?id=%s' % i,
                  'start': s, 'days_running': (datetime.date(2026, 11, 2) - datetime.date.fromisoformat(s)).days, 'format': 'image', 'dynamic': False,
                  'versions': 1, 'placements': ['Audience Network', 'Facebook', 'Instagram', 'Threads'], 'cta': c, 'destination': 'firm website',
                  'headline': "Join One of Canada's Best Workplaces", 'focus': 'recruitment', 'stage': 'not investor-facing',
                  'return_figure': False, 'registered_accounts': False, 'minimum': False, 'local': False, 'for_investors': False}
                 for i, s, c in [('1098663923129636', '2026-07-13', 'Learn more'), ('1576266057510044', '2026-07-15', 'See details'),
                                 ('1757263535428694', '2026-07-15', 'See details'), ('1028958226729065', '2026-07-16', 'See details')]]
    out = {'source': 'Meta Ad Library, country Canada, active ads only', 'collected_at': COLLECTED,
           'tool': 'Apify actor apify/facebook-ads-scraper (official), run by the author',
           'method': 'Exact-phrase keyword searches for each firm name found the advertiser pages; each investor-facing page was then read in full by page id. Unrelated advertisers that matched a name were excluded.',
           'runs': {'keyword_search': ['hOYiJNytTODyh34ej', 'KnCD4k6pSjelNxonj'], 'pages': ['IoWOR4yVVOgrIQuFm', 'p3UKHx9XoCgN60Bnk'], 'library_totals': ['WM8F3Fp9YtUvKZO0H']},
           'raw_sha256': {'page_ads': hashlib.sha256(raw1).hexdigest(), 'snapshots': hashlib.sha256(raw2).hexdigest()}, 'raw_kept': 'Private; not in this repository',
           'library_totals': {'Equiton': {'page': 'Equiton Inc.', 'active': 56, 'complete': False},
                              'Skyline': {'page': 'Skyline Wealth Management Inc.', 'active': 16, 'complete': True},
                              'Skyline Living (resident leasing)': {'page': 'Skyline Living', 'active': 6, 'complete': True},
                              'Lankin': {'page': 'Lankin', 'active': 36, 'complete': False},
                              'Greybrook': {'page': None, 'active': 0, 'note': 'No active ads in Canada matched "Greybrook".'},
                              'Centurion': {'page': 'Centurion Asset Management Inc.', 'active': 4, 'complete': True}},
           'records': recs + centurion}
    with open(os.path.join(HERE, 'ads.json'), 'w', encoding='utf-8') as f: f.write(json.dumps(out, indent=1, ensure_ascii=False) + '\n')
    c = collections.Counter((r['firm'], r['focus']) for r in out['records'])
    print(len(out['records']), sorted(c.items()))
    print(collections.Counter((r['firm'], r['stage']) for r in out['records']))
