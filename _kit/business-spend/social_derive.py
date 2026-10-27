#!/usr/bin/env python3
"""Derive social.json from the Instagram evidence package (edition 001, v1) without changing the package.

  python3 -I social_derive.py PACKAGE_DIR PACKAGE_ZIP [PRIVATE_CAPTIONS_OUT]

PACKAGE_DIR is the extracted package (accounts.json, posts.json, manifest-social.jsonl, reposts-index.json,
screenshots/); PACKAGE_ZIP is the original zip, hashed here and never modified. The script:

- verifies the zip's sha256 and every line of SHA256SUMS.txt;
- runs social.check on the package as delivered (the existing checker, not bypassed);
- runs the targeted secret check over every text file in the package, captions included;
- writes social.json: the package's account and post records plus derived fields (publisher, collaboration
  detail, paid-partnership label, split metric times, inspection label, attribution status), the corrections
  to the collector's handoff, and the excluded material as counts only.

Exact caption text stays in the private package: social.json keeps the short opening line already coded as
`hook` (checked to be an exact substring of the caption as seen) and the editorial fields, never the caption.
The repost list (reposts-index.json) stays private; only its counts are recorded. The editorial layer (the
panel's wording, examples and patterns) is in social_narrative.json and is never written by this script.
"""
import hashlib
import json
import os
import re
import sys
from collections import Counter

KIT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KIT)
import social  # noqa: E402

EXPECTED_ZIP_SHA = '680d0e77756b67b8b7e619528de648ae6c405a09a136f39e1e01eb9ae5338231'
EXPECTED_COUNTS = {'venn': 9, 'float': 0, 'ramp': 19, 'loop': 0, 'keep': 0, 'airwallex': 23}
OUT = os.path.join(KIT, 'social.json')

# Owner and research decisions recorded with the derivation (see SOCIAL_INGEST_NOTE.md).
ATTRIBUTION = {
    'venn': {'status': 'owner_confirmed', 'label': 'Owner-confirmed; profile links venn.ca',
             'website_link': 'The captured Venn website footer linked to @tryvault, while this study uses owner-confirmed @venn.ca with supporting profile evidence.',
             'evidence': ['venn-ig-profile-venn-ca.png', 'venn-site-footer-links-tryvault.png', 'venn-ig-tryvault-profile-not-used.png'],
             'excluded_accounts': ['tryvault']},
    'float': {'status': 'website_linked', 'label': 'Linked from floatfinancial.com structured data; profile links floatfinancial.com',
              'website_link': 'Linked from the floatfinancial.com homepage Organization structured data (sameAs); no visible footer link.',
              'evidence': ['float-ig-profile.png', 'float-site-footer-no-visible-instagram-link.png']},
    'ramp': {'status': 'unresolved', 'label': 'Attribution unresolved: no official Ramp source links @tryramp',
             'website_link': 'ramp.com links no Instagram account (its footer lists LinkedIn, X and Facebook). The profile links tonystockprotrader.com, a campaign site that names Ramp as its operator.',
             'evidence': ['ramp-ig-profile-tryramp.png', 'ramp-site-tonystockprotrader-com.png'],
             'corroboration': {
                 'sought': 'An official Ramp source (ramp.com, its blog or newsroom) that names or links @tryramp, or that claims the campaigns the account posts. Retained evidence first, then server fetches.',
                 'retained': 'The 23 October 2026 server captures of ten ramp.com pages link x.com/tryramp and linkedin.com/company/ramp and no Instagram account. The handle tryramp matches Ramp\'s X account; a matching handle on another network is consistent with, not proof of, the same owner.',
                 'fetched': [
                     {'url': 'https://ramp.com/', 'at': '2026-10-27T13:58:38-04:00', 'http': 200, 'method': 'server fetch (curl), no JavaScript, no cookies', 'sha256': 'd3b80409dcc190e57cc9faf0b3562336c5408f2f39fcf53f5182f0b9b304f44c', 'finding': 'No Instagram link; footer social links are LinkedIn, X and Facebook.'},
                     {'url': 'https://ramp.com/blog', 'at': '2026-10-27T13:58:40-04:00', 'http': 200, 'method': 'server fetch (curl), no JavaScript, no cookies', 'sha256': '0e7a455467e8c1605169bc9f90b1cb4d408239707899b6f2e4162e57d096b8e0', 'finding': 'No Instagram link; no mention of Tony Stock Pro Trader or Bill Pay The Musical in the served listing.'},
                     {'url': 'https://ramp.com/newsroom', 'at': '2026-10-27T13:58:40-04:00', 'http': 404, 'method': 'server fetch (curl), no JavaScript, no cookies', 'sha256': 'deea79d81207183883ae1e94bf4f04856893c6cb75c33cc88690903f39044a52', 'finding': 'Not found.'},
                     {'url': 'https://ramp.com/blog/ramp-at-60-billion', 'at': '2026-10-27T13:59:03-04:00', 'http': 200, 'method': 'server fetch (curl), no JavaScript, no cookies', 'sha256': '1c8288d4e1d0d387de2dda3894b579a0b739babb81abe5668991e6104ed15457', 'finding': 'Ramp\'s own post of 15 October 2026 gives the figures in @tryramp\'s carousel of the same day ($60B, 85,000 businesses, over $1 billion a month, Router, Glass). It does not name or link an Instagram account: matching content, not an account link.'},
                     {'url': 'https://tonystockprotrader.com/', 'at': '2026-10-27T13:58:41-04:00', 'http': 200, 'method': 'server fetch (curl), no JavaScript, no cookies', 'sha256': 'afbf90fdcb67f70b2612ae9733bee19ecc1e16648201d93c178cca753c9893b2', 'finding': 'Campaign site (the profile link): links ramp.com and its privacy policy and carries a Ramp Business Corporation notice. Its own description; not an official Ramp source for the account.'},
                     {'url': 'https://billpaythemusical.com/', 'at': '2026-10-27T13:58:41-04:00', 'http': 200, 'method': 'server fetch (curl), no JavaScript, no cookies', 'sha256': 'd333568e4a489e41b86133433cf69bfd0fb3d00ab37c8d506552e3bd36829ee1', 'finding': 'Campaign site: says Ramp presents the musical and links instagram.com/billpaythemusical, not @tryramp.'},
                 ],
                 'web_search': '27 October 2026: searches restricted to ramp.com found no page about the campaign or the Instagram account; trade press (WERSM, Shredder, theinspiration.com, TheaterMania) attributes both campaigns to Ramp but is not an official Ramp source.',
                 'result': 'unresolved',
                 'reasoning': 'No official Ramp source names or links @tryramp. The account\'s profile links a campaign site, and that site\'s self-description is not conclusive. The matching funding post and the X handle are consistent with Ramp but do not establish who runs the account. The 19 records are kept and counted, labelled unresolved, and no conclusion about Ramp rests on them.',
             }},
    'loop': {'status': 'website_linked', 'label': 'Linked from the bankonloop.com footer; profile links bankonloop.com',
             'website_link': 'Linked from the bankonloop.com/en-ca footer.', 'evidence': ['loop-ig-profile.png', 'loop-site-footer-instagram-link.png']},
    'keep': {'status': 'website_linked', 'label': 'Linked from the trykeep.com footer; profile links trykeep.com',
             'website_link': 'Linked from the trykeep.com footer.', 'evidence': ['keep-ig-profile.png', 'keep-site-footer-instagram-link.png']},
    'airwallex': {'status': 'profile_verified', 'label': 'Owner-supplied; profile names Airwallex and links airwallex.com',
                  'website_link': 'Not linked from airwallex.com as served in Canada; the profile carries a verified badge and links www.airwallex.com.',
                  'evidence': ['airwallex-ig-profile.png', 'airwallex-ig-profile-links.png', 'airwallex-site-footer-no-instagram.png']},
}

# Coverage wording for accounts with no in-window post (the owner's brief: never "inactive").
NO_POSTS = {
    'float': 'No in-window posts found in the reviewed grid and Reels surfaces.',
    'loop': 'No in-window posts found in the reviewed grid and Reels surfaces.',
    'keep': 'No in-window posts found in the reviewed grid (the profile shows no Reels tab).',
}
REELS_SHOTS = {'venn': ['venn-ig-reels-tab-views.png'], 'ramp': ['ramp-ig-reels-tab-views-1.png', 'ramp-ig-reels-tab-views-2.png'],
               'airwallex': ['airwallex-ig-reels-tab-views-1.png', 'airwallex-ig-reels-tab-views-2.png', 'airwallex-ig-reels-tab-views-3.png']}
# The collector blurred faces in this screenshot, which also covered two tiles' view counts; those counts were read from the page text.
BLURRED_VIEW_TILES = {'airwallex-ig-DeR-myVkbUa', 'airwallex-ig-DezQZwBiY6q'}


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def caption_as_seen(p):
    m = re.search(r'Caption as seen: (.*)$', p['inspected'], re.S)
    return m.group(1) if m else ''


def inspected_summary(p):
    return p['inspected'].split(' Caption as seen:')[0].strip()


def publisher_of(url):
    m = re.match(r'https://www\.instagram\.com/([^/]+)/(p|reel)/([^/]+)/$', url)
    return (m.group(1), m.group(3)) if m else (None, None)


def derive(pkg, zpath):
    errs, notes = [], []
    zsha = sha(zpath)
    if zsha != EXPECTED_ZIP_SHA:
        errs.append('zip sha256 %s does not match the expected %s' % (zsha, EXPECTED_ZIP_SHA))
    sums = [l.split() for l in open(os.path.join(pkg, 'SHA256SUMS.txt'), encoding='utf-8') if l.strip()]
    bad = [f for h, f in sums if sha(os.path.join(pkg, f)) != h]
    if bad:
        errs.append('SHA256SUMS mismatch: %s' % bad)
    s0, cerrs = social.package_to_module(pkg)
    errs += ['package check: ' + e for e in cerrs]
    # Targeted secret check over every text file as delivered.
    for name in ('accounts.json', 'posts.json', 'manifest-social.jsonl', 'reposts-index.json', 'HANDOFF.md'):
        with open(os.path.join(pkg, name), encoding='utf-8') as f:
            hit = social.secret_findings(f.read())
        if hit:
            errs.append('secret check: %s: %s' % (name, hit))
    with open(os.path.join(pkg, 'manifest-social.jsonl'), encoding='utf-8') as f:
        man = [json.loads(l) for l in f if l.strip()]
    with open(os.path.join(pkg, 'reposts-index.json'), encoding='utf-8') as f:
        rep = json.load(f)
    accounts, posts = s0['accounts'], s0['posts']
    shots = {x['file']: x['sha256'] for x in s0['screenshots']}
    mtime = {m['screenshot']: m['captured_at'] for m in man}

    # ---------- posts ----------
    out_posts, seen_codes = [], set()
    for p in posts:
        cap = caption_as_seen(p)
        pub, code = publisher_of(p['url'])
        if not pub:
            errs.append('post %s: URL is not a permanent post URL' % p['id'])
        if code in seen_codes:
            errs.append('post %s: duplicate shortcode %s (grid and Reels counted twice)' % (p['id'], code))
        seen_codes.add(code)
        header = re.search(r'Header reads "([^"]+)"', p['inspected'])
        label = re.search(r'"(Paid partnership[^"]*)"', p['inspected'])
        cap_label = re.search(r'#Paid partnership with @(\w+)', cap)
        paid = None
        if label:
            paid = {'where': 'header', 'text': label.group(1).replace(' (Instagram label)', '')}
        elif cap_label:
            paid = {'where': 'caption', 'text': '#Paid partnership with @%s' % cap_label.group(1)}
        if p['relation'] == 'original' and pub != p['account']:
            errs.append('post %s: original but published by @%s' % (p['id'], pub))
        if p['relation'] == 'collaboration':
            collab = 'published_by_collaborator' if pub != p['account'] else 'published_with_coauthor'
        else:
            collab = None
        hook = p['hook']
        if hook and hook not in cap:
            errs.append('post %s: hook is not an exact substring of the caption as seen' % p['id'])
        mt = p['metrics']
        vt = re.search(r'Views read from the @[\w.]+ Reels tab at (\d\d):(\d\d)', p['inspected'])
        views_at = '2026-10-26T%s:%s-04:00' % vt.groups() if vt else None
        if mt['views'] is not None and not vt:
            errs.append('post %s: views recorded without the time they were read' % p['id'])
        if vt:
            tabs = REELS_SHOTS[p['platform']]
            src = '@%s Reels tab, read at %s:%s Toronto time (screenshots %s)' % (p['account'], vt.group(1), vt.group(2), ', '.join(tabs))
            if p['id'] in BLURRED_VIEW_TILES:
                src += '; this tile is blurred in the screenshot, so the count comes from the page text read at that time'
        else:
            src = None
        restored = None
        if '[one word omitted' in cap:
            restored = {'marker': '[one word omitted: the kit text filter rejects it]', 'restored': 'session',
                        'from': p['capture_ref'], 'from_sha256': shots.get(p['capture_ref']),
                        'reason': 'The retained post screenshot shows the caption ending "stayed way past the last session". The kit\'s old filter rejected the ordinary word "session"; it now checks for credential patterns only.'}
        completions = re.findall(r'\[([A-Za-z]+(?:\.\.\.)?)\]', cap)
        q = {k: p[k] for k in ('id', 'platform', 'channel', 'account', 'url', 'published_on', 'date_method', 'captured_at', 'scope', 'relation',
                               'format', 'topic', 'question', 'product', 'geography', 'hook', 'proof', 'cta', 'inspection', 'capture_ref')}
        q.update({
            'shortcode': code, 'publisher': pub, 'collaboration': collab, 'header': header.group(1) if header else None, 'paid_label': paid,
            'inspected': inspected_summary(p),
            'inspection_label': social.inspection_label(p['format'], p['inspection']),
            'capture_sha256': shots.get(p['capture_ref']),
            'attribution': ATTRIBUTION[p['platform']]['status'],
            'metrics': {'likes': mt['likes'], 'comments': mt['comments'], 'views': mt['views'],
                        'likes_comments_captured_at': mt['captured_at'], 'views_captured_at': views_at,
                        'views_time_precision': 'minute' if views_at else None, 'views_source': src},
            'caption_restoration': restored,
            'caption_completions': ['[%s] is the collector\'s completion of a caption cut off in the capture, not source text' % x for x in completions] or None,
        })
        if mt['captured_at'] != p['captured_at']:
            notes.append('post %s: metric time differs from the record time' % p['id'])
        out_posts.append(q)

    # ---------- accounts ----------
    counts = Counter(p['platform'] for p in out_posts)
    out_acc = []
    for a in accounts:
        pl = a['platform']
        if counts.get(pl, 0) != EXPECTED_COUNTS[pl] or a['posts_in_window'] != EXPECTED_COUNTS[pl]:
            errs.append('account %s: %s posts recorded, %s coded, %s expected' % (pl, a['posts_in_window'], counts.get(pl, 0), EXPECTED_COUNTS[pl]))
        mine = [p for p in out_posts if p['platform'] == pl]
        b = dict(a)
        b.update({
            'attribution': ATTRIBUTION[pl],
            'earliest_reached_method': 'post ID of the oldest post read (not an opened page)',
            'relations': dict(Counter(p['relation'] for p in mine)),
            'collaborations': {'published_by_collaborator': sum(1 for p in mine if p['collaboration'] == 'published_by_collaborator'),
                               'published_with_coauthor': sum(1 for p in mine if p['collaboration'] == 'published_with_coauthor'),
                               'publishers': dict(Counter(p['publisher'] for p in mine if p['collaboration'] == 'published_by_collaborator'))},
            'paid_labels': sum(1 for p in mine if p['paid_label']),
            'formats': dict(Counter(p['format'] for p in mine)),
            'no_posts_text': NO_POSTS.get(pl),
            'pass': 'first' if a['checked_at'] < '2026-10-26T21:30' else 'second',
        })
        out_acc.append(b)

    # ---------- excluded material (counts only; the list stays private) ----------
    rp = rep['reposts']
    rc = {}
    for pl in ('ramp', 'airwallex'):
        mine = [r for r in rp if r['platform'] == pl]
        dup = [r['url'] for r in mine if r['url'] in {p['url'] for p in out_posts}]
        rc[pl] = {'listed_in_index': len(mine), 'originals_in_window_estimated': sum(1 for r in mine if r['original_in_window']),
                  'also_coded_as_posts': len(dup), 'listed_at': rep['listed_at'][pl]}
    rc['airwallex']['tab_title_count'] = 15
    rc['ramp']['tab_title_count'] = 118

    post_times = sorted(p['captured_at'] for p in out_posts)
    man_times = sorted(mtime.values())
    first = sorted(t for t in man_times if t < '2026-10-26T21:30')
    second = sorted(t for t in man_times if t >= '2026-10-26T21:30')
    fmt = Counter(p['format'] for p in out_posts)
    insp = Counter((p['format'], p['inspection']) for p in out_posts)
    s = {
        'status': 'review', 'approved': None,
        'review_note': 'Shown on the staging draft for editorial review only. Editorial approval is not granted; the release build is blocked until the owner records it here by hand.',
        'window': dict(social.WINDOW),
        'package': {'file': os.path.basename(zpath), 'sha256': zsha, 'bytes': os.path.getsize(zpath), 'sums_entries': len(sums), 'sums_verified': not bad,
                    'retrieved_at': '2026-10-27T13:53:29-04:00', 'retrieval': 'Shared by the owner as a private cloud-storage link (reference kept out of this repository); downloaded over HTTPS; the original is unchanged.',
                    'checker': 'social.py check: PASS (6 accounts, 51 posts, 95 screenshots)', 'screenshots': len(shots)},
        'collection': {
            'date': '2026-10-26', 'tz': 'America/Toronto',
            'first_pass': {'from': first[0], 'to': first[-1], 'covers': 'Float, Loop and Keep accounts, the @tryvault profile and the website footers'},
            'second_pass': {'from': post_times[0], 'to': second[-1], 'covers': 'Venn, Ramp and Airwallex accounts and all 51 post records'},
            'post_records': {'from': post_times[0], 'to': post_times[-1]},
            'text': '26 October 2026, 9:01 p.m. to 10:15 p.m. Toronto time',
            'note': ('Posts were collected after the window closed: a first pass at 9:01 to 9:09 p.m. read Float, Loop and Keep, and a second pass read Venn, Ramp and Airwallex, '
                     'with post records from 9:45 p.m. to 10:15 p.m. Publication dates come from each post page\'s timestamp, converted to Toronto time. '
                     'Displayed likes, comments and views were recorded with their own read times but are not shown or compared here: posts had different ages at collection, '
                     'and a collaboration\'s counts include the other account\'s audience.'),
        },
        'totals': {'posts': len(out_posts),
                   'attributed_posts': sum(1 for p in out_posts if ATTRIBUTION[p['platform']]['status'] != 'unresolved'),
                   'unresolved_records': sum(1 for p in out_posts if ATTRIBUTION[p['platform']]['status'] == 'unresolved'), 'formats': dict(fmt), 'inspection': {'%s/%s' % k: v for k, v in sorted(insp.items())},
                   'partially_inspected': sum(1 for p in out_posts if p['inspection'] == 'partial'),
                   'by_platform': dict(counts), 'topics': dict(Counter(p['topic'] for p in out_posts))},
        'accounts': out_acc,
        'posts': out_posts,
        'excluded': {
            'reposts': rc,
            'reposts_note': 'Instagram does not show when a repost was made, so no repost can be dated to the window. Reposts are left out of every count, frequency, topic share and comparison; the list stays in the private package.',
            'boundary_posts': [{'platform': 'venn', 'shortcode': 'DbLaePCDan-', 'published_on': '2026-07-24'}, {'platform': 'airwallex', 'shortcode': 'DbK-bZ_jI3G', 'published_on': '2026-07-24'}],
            'not_collected': 'Stories, highlights, live videos, the Tagged tab, ads, private content and the @tryvault account.',
        },
        'derived_corrections': [
            {'topic': 'Format and inspection counts', 'handoff': 'All 34 videos are inspection: partial.',
             'records': 'The records hold 33 videos, 10 carousels and 8 images. Inspection: 33 videos partial (cover, caption, header and counts; not played), 1 carousel partial (the Kumar Method carousel), 9 carousels all slides, 8 images cover and caption.',
             'derived': '34 posts were partially inspected: 33 videos and 1 carousel.'},
            {'topic': 'Collection times', 'handoff': 'Collected between 21:49 and 22:16 Toronto time; Float, Loop and Keep from a first pass at 21:01 to 21:10.',
             'records': 'Manifest captures run from %s to %s; post records from %s to %s.' % (man_times[0][11:19], man_times[-1][11:19], post_times[0][11:19], post_times[-1][11:19]),
             'derived': 'Second pass from %s (the first post record), not 21:49; first pass %s to %s. No timestamp was changed.' % (post_times[0][11:19], first[0][11:19], first[-1][11:19])},
            {'topic': 'Venn website link', 'handoff': 'The venn.ca footer still links @tryvault; elsewhere, Ramp, Airwallex and Venn "still have no Instagram link in their site footers".',
             'records': 'venn-site-footer-links-tryvault.png shows the venn.ca footer Instagram icon linking to instagram.com/tryvault.',
             'derived': ATTRIBUTION['venn']['website_link'] + ' The handoff\'s "no Instagram link" applies to Ramp and Airwallex only. No reason for the difference is asserted.'},
            {'topic': 'Omitted caption word', 'handoff': 'One word omitted in DeLBKE-hlOg because the kit\'s text filter rejects it.',
             'records': 'The retained screenshot ramp-post-2026-10-06-DeLBKE-hlOg.png shows the word.', 'derived': 'Restored as "session" in the private derived record; the filter now checks for credential patterns, not ordinary words.'},
            {'topic': 'Caption completions', 'handoff': 'Captions are as seen, sometimes shortened with "...".',
             'records': 'Two Venn captions carry bracketed completions, [balance...] in Db8eeMHEV9v and [Store] in DcOdMd8oMR-, where the visible caption was cut off.',
             'derived': 'Marked as the collector\'s completions, not source text; neither is quoted on the page.'},
            {'topic': 'Airwallex repost count', 'handoff': 'The Reposts tab lists 15 reposts.',
             'records': 'reposts-index.json lists %d Airwallex reposts (%d of in-window originals); the screenshot shows the first 8.' % (rc['airwallex']['listed_in_index'], rc['airwallex']['originals_in_window_estimated']),
             'derived': 'Recorded as "15 on the tab title, 12 listed"; reposts are excluded from every count either way.'},
            {'topic': 'Duplicate sections', 'handoff': 'Checked for repeated sections.', 'records': 'None found.', 'derived': 'No change needed.'},
        ],
        'notes': notes,
    }
    errs += ['derived module: ' + e for e in social.check(s)]
    return s, errs


def write_private(pkg, out):
    """Exact caption text as captured, with the one restoration applied separately. Private: never in the repository."""
    if os.path.abspath(out).startswith(os.path.dirname(os.path.dirname(KIT))):
        raise SystemExit('Refused: the private caption file must be written outside the repository')
    with open(os.path.join(pkg, 'posts.json'), encoding='utf-8') as f:
        posts = json.load(f)
    rows = {}
    for p in posts:
        cap = caption_as_seen(p)
        rows[p['id']] = {'caption_as_captured': cap,
                         'caption_restored': cap.replace('[one word omitted: the kit text filter rejects it]', 'session') if '[one word omitted' in cap else None}
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=1, ensure_ascii=False)


def main(argv):
    if len(argv) == 4:
        write_private(argv[1], argv[3])
        argv = argv[:3]
    if len(argv) != 3:
        print(__doc__)
        return 2
    s, errs = derive(argv[1], argv[2])
    if errs:
        print('Refused (nothing written):\n  ' + '\n  '.join(errs))
        return 1
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(s, f, indent=1, ensure_ascii=False)
        f.write('\n')
    t = s['totals']
    print('Wrote social.json (status review, approval not recorded): %d records (%d attributed posts, %d with unresolved provider attribution) %s; formats %s; partially inspected %d.' % (
        t['posts'], t['attributed_posts'], t['unresolved_records'], t['by_platform'], t['formats'], t['partially_inspected']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
