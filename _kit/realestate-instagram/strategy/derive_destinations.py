#!/usr/bin/env python3
"""Ad destinations (founder brief, 2026-11-03), a separately dated update to the 2 November paid review.

Usage: python3 derive_destinations.py RAW.json PAGES.json
RAW.json: apify/facebook-ads-scraper output for the three investor advertiser pages, collected 3 November 2026 (private:
it holds full ad copy and signed media links). PAGES.json: the listed website and booking links opened in Chromium on
3 November 2026 (private: page text). Writes ad_destinations.json with derived fields only: ad ID, firm, check date,
destination type, the listed link for website and booking destinations, how it was verified, the specific offer the ad
names and whether the destination presents it, and whether the ad ID was in the 2 November review.

Rules: Meta form only when the library record itself shows the instant form questions; a record that shows a form and
also lists a website link stays Unverified (the record does not show which the reader reaches); a page that shows a bot
check stays Unverified (never bypassed). "Presents the offer" compares the specific fund, development or event named in
the ad with the visible destination text (form disclaimers excluded). Unverified destinations stay in the denominator.
"""
import collections, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIRMS = {'762651820485779': 'Equiton', '1136216849873517': 'Skyline', '256257607565454': 'Lankin'}
RUN = {'actor': 'apify/facebook-ads-scraper', 'run': '6s1UgcJOJjd3fGoRf', 'started': '2026-11-03T11:10:51-05:00', 'finished': '2026-11-03T11:11:54-05:00'}
OFFERS = [('Bridleview Residences', r'bridleview'), ('Wilson Station Condos', r'wilson station'), ('US Apartment Fund', r'us apartment fund|us residential income fund'),
          ('Apartment Fund', r'(?<!us )apartment fund|equiton residential income fund'), ('Lankin Apartment REIT', r'lankin apartment reit'),
          ('At the Turning Point event', r'turning point'), ('Skyline Apartment REIT', r'skyline apartment reit'), ('Skyline Industrial REIT', r'skyline industrial reit'),
          ('Skyline Retail REIT', r'skyline retail reit'), ('Skyline Clean Energy Fund', r'skyline clean energy fund')]
DISCLAIMER = re.compile(r'By submitting|Important Information|Past performance|Offering Memorandum|^[\*¹²]|Targeted returns are|Privacy Policy|calls may be recorded', re.I)


def offers(t):
    t = t.lower()
    return [n for n, p in OFFERS if re.search(p, t)]


def derive(raw_path, pages_path):
    raw = open(raw_path, 'rb').read()
    pages = json.load(open(pages_path))
    orig = {x['id'] for x in json.load(open(os.path.join(HERE, 'ads.json')))['records']}
    checks = {i: c for c in json.load(open(os.path.join(HERE, 'ad_destination_checks.json')))['checks'] for i in c['ids']}
    recs = []
    for x in json.loads(raw):
        s = x['snapshot']; firm = FIRMS[x['pageID']]; cards = s.get('cards') or []
        adtext = ' '.join([s.get('title') or '', (s.get('body') or {}).get('text') or ''] + [(k.get('title') or '') + ' ' + (k.get('body') or '') for k in cards])
        ets = [e.get('text', '') for e in (s.get('extraTexts') or [])]
        visible = ' '.join(t for t in ets if not DISCLAIMER.search(t.strip()))
        link = (s.get('linkUrl') or '').split('?')[0]
        form = bool(re.search(r'\b(First name|Email|Phone number|Full name)\b', ' '.join(ets)))
        if 'marquis' in link:
            continue  # a home-sales ad on Equiton's page, not investor-facing (as in the 2 November review)
        named = offers(adtext); listed = None
        if form and link.startswith('http://fb.me'):
            typ, basis, dest = 'Meta form', 'The library record shows the instant form and its questions.', visible
        elif form:
            typ, basis, dest, listed = 'Unverified', 'The library record shows an instant form and also lists a website link; the record does not show which the reader reaches.', None, link
        elif 'calendly' in link:
            typ, basis, dest, listed = 'Booking page', 'Calendly booking page opened on 3 November 2026.', pages[link]['text'], link
        elif pages.get(link, {}).get('status') == 200:
            typ = 'Campaign landing page' if 'turning-point' in link else 'Fund or product page'
            basis, dest, listed = 'Page opened on 3 November 2026.', pages[link]['text'], link
        else:
            typ, basis, dest, listed = 'Unverified', 'The listed link showed a bot check when opened on 3 November 2026; it was not bypassed.', None, link
        if not named:
            pres = 'No specific offer named'
        elif dest is None:
            pres = 'Unverified'
        else:
            got = [n for n in named if n in offers(dest)]
            pres = 'Yes' if len(got) == len(named) else ('Partly' if got else 'No')
        c = checks.get(x['adArchiveID'])
        if c and typ == 'Unverified' and c.get('resolve_by_url_label'):  # founder decision 2026-11-03: Meta's URL-link label decides
            pg = pages.get(link, {})
            typ = ('Page not found' if pg.get('status') == 404 else 'Campaign landing page' if 'private-reit' in link
                   else 'Homepage or other general page')
            dest = pg.get('text') if pg.get('status') == 200 else ''
            pres = 'No specific offer named' if not named else ('Yes' if all(n in offers(dest) for n in named) else 'No')
            basis = ('The Ad Library labels the ad &quot;This ad is from a URL link&quot; and all its versions point to this address (checked in the author\'s own browser on 3 November 2026); '
                     'a Meta form is attached as an extra asset, and the live ad cannot be seen.').replace('&quot;', '"')
            if pg.get('final') and pg['final'].split('?')[0] != link:
                basis += ' The address redirects to ' + pg['final'].split('?')[0] + '.'
        elif c and typ == 'Unverified':  # resolved by a read-only check in the author's own browser (ad_destination_checks.json)
            typ, pres, listed = c['destination'], c['presents_offer'], c['final_url']
            basis = 'Read in the author\'s own browser with Claude in Chrome on 3 November 2026 at 11:25 a.m. Toronto time, after the page showed a bot check to the collector.'
        recs.append({'id': x['adArchiveID'], 'firm': firm, 'check_date': '2026-11-03', 'destination': typ, 'listed_link': listed, 'basis': basis,
                     'offer_named': '; '.join(named) or None, 'presents_offer': pres, 'differences': c.get('differences') if c else None, 'in_2_november_review': x['adArchiveID'] in orig,
                     'library_url': 'https://www.facebook.com/ads/library/?id=' + x['adArchiveID']})
    links = {}
    for u, v in pages.items():
        if 'error' in v: continue
        links[u] = {'final_url': v['final'].split('?')[0], 'status': v['status'], 'title': v['title'], 'text_sha256': hashlib.sha256(v['text'].encode()).hexdigest()}
    out = {'source': 'Meta Ad Library, country Canada, active ads, the three investor advertiser pages of the 2 November review',
           'collected': RUN, 'raw_sha256': hashlib.sha256(raw).hexdigest(), 'raw_kept': 'Private; not in this repository',
           'check_date': '2026-11-03', 'listed_links_opened': links,
           'counts': dict(collections.Counter(r['firm'] for r in recs)), 'records': recs}
    with open(os.path.join(HERE, 'ad_destinations.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1, ensure_ascii=False); f.write('\n')
    return out


if __name__ == '__main__':
    o = derive(sys.argv[1], sys.argv[2])
    print(o['counts'], len(o['records']))
