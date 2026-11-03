#!/usr/bin/env python3
"""Organic strategy records for the five-firm comparison (founder, 2026-11-02).

All four scored accounts: the kit post log (ig_postlog.json, ig_caps.json), re-collected 2 November 2026 for the edition
window with apify/instagram-scraper (run dfN9H7QBCXbpjMbnu; collector output with comments stays private). GREYBROOK below
holds the author's fund reading of Greybrook's captions; themes are in the post log.
Centurion: no corporate Instagram account found (centurion.ca links none; four likely handles do not exist; a name search
returned only an unrelated account; run thCyg7lmfVVuUAqgT and xI9l37BBtL4ekfSd6).
"""
import json, os, re, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__)); KIT = os.path.dirname(HERE)
WINDOW = ['2026-09-13', '2026-10-13']
FUND = re.compile(r'\b(fund|REIT|invest with|invest in (our|the)|offering|RRSP|TFSA|minimum investment|accredited)\b', re.I)
RET = re.compile(r'\d+(\.\d+)?\s*%[^.]{0,40}(return|distribution|yield)', re.I)
# Greybrook, 13 posts 13 September to 13 October 2026: shortcode, date, format, theme, likes (None = hidden), comments, plays, names a fund
GREYBROOK = [
 ('DdRxt_TFDCc', '2026-09-14', 'Carousel', 'Brand / other', None, 0, None, False),
 ('DdUToJwh0R5', '2026-09-15', 'Reel', 'Development / asset', None, 0, 427, False),
 ('DdZOvK7Eehx', '2026-09-17', 'Carousel', 'Investor education', None, 0, None, False),
 ('DdjqT1yo9qs', '2026-09-21', 'Reel', 'Brand / other', 5, 0, 497, False),
 ('DdpEtOBlFF-', '2026-09-23', 'Carousel', 'Investor education', 3, 0, None, False),
 ('DdrOcccDBfT', '2026-09-24', 'Static', 'Market / macro', None, 0, None, False),
 ('DduJjOolANz', '2026-09-25', 'Carousel', 'Investor education', 1, 1, None, True),
 ('DdwB4nvIqg6', '2026-09-26', 'Reel', 'CSR / community', 24, 0, 1104, False),
 ('Dd6rKEaI8Hr', '2026-09-30', 'Reel', 'Development / asset', 8, 0, 416, False),
 ('Dd_rxuxI19r', '2026-10-02', 'Reel', 'CSR / community', 19, 1, 792, False),
 ('DeJ9DvgkbLy', '2026-10-06', 'Carousel', 'CSR / community', 116, 6, None, False),
 ('DeMoUy3kYoH', '2026-10-07', 'Carousel', 'Brand / other', 26, 3, None, False),
 ('DePUKGskWWC', '2026-10-08', 'Static', 'Brand / other', 31, 0, None, False)]

def build():
    """All four accounts from the kit's post log, re-collected 2 November 2026 for the edition window."""
    pl = json.load(open(os.path.join(KIT, 'ig_postlog.json'))); caps = json.load(open(os.path.join(KIT, 'ig_caps.json')))
    import sys; sys.path.insert(0, KIT); import reindex_data as d
    plays = {p[7]: p[5] for p in d.IG}
    fund = {g[0]: g[7] for g in GREYBROOK}
    posts = []
    for b, date, fmt, theme, hook, likes, comments, _, code in pl:
        cap = (caps.get(code) or {}).get('cap') or hook
        named = fund[code] if code in fund else bool(FUND.search(cap))
        posts.append({'firm': b, 'code': code, 'date': date, 'format': fmt, 'theme': theme, 'likes': likes, 'comments': comments,
                      'plays': plays.get(code), 'names_fund': named, 'return_figure': bool(RET.search(cap))})
    followers = {b: d.IG_BRANDS[b]['ig_foll'] for b in d.IG_BRANDS}
    out = {'window': WINDOW, 'accounts': {'Equiton': '@equitoninc', 'Skyline': '@skylinegroupofcompanies', 'Lankin': '@lankin_investments', 'Greybrook': '@greybrook', 'Centurion': None},
           'followers': followers, 'followers_note': 'All four read on 2 November 2026.',
           'centurion': 'No corporate Instagram account found on 2 November 2026: centurion.ca links none, four likely handles do not exist and a name search returned only an unrelated account.',
           'sources': {'posts_run': 'dfN9H7QBCXbpjMbnu', 'profiles_run': 'a47HIlg0Lva9uQ76o', 'centurion_runs': ['thCyg7lmfVVuUAqgT', 'xI9l37BBtL4ekfSd6']},
           'posts': posts}
    with open(os.path.join(HERE, 'organic.json'), 'w', encoding='utf-8') as f: f.write(json.dumps(out, indent=1, ensure_ascii=False) + chr(10))
    return out

if __name__ == '__main__':
    o = build()
    for f in ['Equiton', 'Skyline', 'Lankin', 'Greybrook']:
        p = [x for x in o['posts'] if x['firm'] == f]; lk = [x['likes'] for x in p if x['likes'] is not None]
        print(f, len(p), {k: sum(x['format'] == k for x in p) for k in ('Reel', 'Carousel', 'Static')}, 'fund', sum(x['names_fund'] for x in p), 'ret', sum(x['return_figure'] for x in p), 'med', st.median(lk), 'hidden', len(p) - len(lk))
