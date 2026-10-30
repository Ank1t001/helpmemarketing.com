#!/usr/bin/env python3
"""Derive the public paid-ads records from a private Meta Ad Library collection (Apify apify/facebook-ads-scraper output).

Usage: python3 paid_derive.py RAW.json
Writes paid_ads.json (records and counts). The raw file stays private: it holds full ad copy and media URLs.
Only derived fields, the ad's own headline and its Ad Library link are kept here.
"""
import collections
import datetime
import hashlib
import json
import os
import sys
from urllib.parse import urlparse

KIT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(KIT, 'paid_ads.json')
PAGES = {'110570531583802': 'venn', '112248814446225': 'float', '103437121012366': 'ramp',
         '100272378031127': 'loop', '110390671388330': 'keep', '946272522105063': 'airwallex'}
PLATFORM = {'FACEBOOK': 'Facebook', 'INSTAGRAM': 'Instagram', 'MESSENGER': 'Messenger', 'THREADS': 'Threads',
            'WHATSAPP': 'WhatsApp', 'AUDIENCE_NETWORK': 'Audience Network'}
FORMAT = {'DCO': 'dynamic', 'VIDEO': 'video', 'IMAGE': 'image'}


def landing(url):
    if not url:
        return ''
    u = urlparse(url)
    return (u.netloc.replace('www.', '') + u.path).rstrip('/') or u.netloc


def derive(raw_path, collected_at, counts):
    raw = open(raw_path, 'rb').read()
    items = [x for x in json.loads(raw)['items'] if x]
    day = datetime.date.fromisoformat(collected_at[:10])
    recs = []
    for x in items:
        body = (x.get('snapshot.body.text') or '') + ' ' + (x.get('snapshot.title') or '')
        start = x['startDateFormatted'][:10]
        recs.append({
            'id': x['adArchiveID'], 'platform': PAGES[x['pageID']], 'page_name': x['pageName'],
            'library_url': 'https://www.facebook.com/ads/library/?id=%s' % x['adArchiveID'],
            'start': start, 'days_running': (day - datetime.date.fromisoformat(start)).days,
            'format': FORMAT.get(x.get('snapshot.displayFormat'), 'other'), 'versions': x.get('collationCount') or 1,
            'placements': [PLATFORM.get(p, p.title()) for p in x.get('publisherPlatform') or []],
            'cta': x.get('snapshot.ctaText') or '', 'landing': landing(x.get('snapshot.linkUrl')),
            'headline': (x.get('snapshot.title') or '').strip(),
            'template_unrendered': '{{product' in body,
            'us_card_disclosure': 'Member FDIC' in body, 'canadian_card_disclosure': 'Peoples Trust' in body,
            'mentions_tryramp': '@tryramp' in body.lower(),
        })
    recs.sort(key=lambda r: (list(PAGES.values()).index(r['platform']), r['start'], r['id']))
    return {'source': 'Meta Ad Library, country Canada, active ads only, sorted by impressions (the library order, not a figure)',
            'collected_at': collected_at, 'tool': 'Apify actor apify/facebook-ads-scraper (official), run by the author',
            'raw_sha256': hashlib.sha256(raw).hexdigest(), 'raw_kept': 'Private; not in this repository',
            'library_counts': counts, 'records': recs}


if __name__ == '__main__':
    # Library totals read the same day by a count-only run (onlyTotal); see paid_narrative.json for how they differ from records.
    counts = {'venn': 34, 'float': 11, 'ramp': 47, 'loop': 17, 'keep': 0, 'airwallex': 24}
    out = derive(sys.argv[1], '2026-10-30T17:28:03-04:00', counts)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(json.dumps(out, indent=1, ensure_ascii=False) + '\n')
    c = collections.Counter(r['platform'] for r in out['records'])
    print('Wrote %s: %d records %s' % (os.path.relpath(OUT), len(out['records']), dict(c)))
