"""Social content module for the Business Cards & Spend Management Index (planned; nothing collected).

The page gets a "Social content" view only when _kit/business-spend/social.json exists, its status
is "reviewed", the owner's approval is recorded in it by hand, and check() passes. Until then
load_reviewed() returns None and the page shows no social tab, summary or example.

Fixed rules (SOCIAL_MODULE_BRIEF.md): official company Instagram accounts only (LinkedIn dropped by the owner, 26 October 2026);
posts published 25 July through 22 October 2026 inclusive, America/Toronto (90 complete days);
the window never moves. Website observation dates are separate and unchanged.
"""
import html
import json
import os
import re
from datetime import date, datetime

KIT = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(KIT, 'social.json')
E = lambda s: html.escape(s, quote=True)

WINDOW = {'start': '2026-07-25', 'end': '2026-10-22', 'tz': 'America/Toronto', 'days': 90}
CHANNELS = {'instagram': 'Instagram'}
PLATFORMS = ('venn', 'float', 'ramp', 'loop', 'keep', 'airwallex')
SCOPES = ('canada', 'global', 'unclear')
COVERAGE = {'complete': 'Complete inventory', 'partial': 'Partial sample', 'blocked': 'Blocked (not the same as inactive)',
            'no_account': 'No verified official account', 'unverified': 'Account identity not verified'}
RELATIONS = ('original', 'repost', 'collaboration')
FORMATS = ('image', 'carousel', 'video', 'text', 'link', 'document')
INSPECTION = ('cover_and_caption', 'all_slides', 'watched_in_full', 'partial')
DATE_METHODS = ('visible_date', 'post_page_timestamp', 'relative_date_converted')
POST_FIELDS = ('id', 'platform', 'channel', 'account', 'url', 'published_on', 'date_method', 'captured_at', 'scope', 'relation',
               'format', 'topic', 'question', 'product', 'geography', 'hook', 'proof', 'cta', 'inspected', 'inspection',
               'capture_ref', 'metrics')
METRICS = {'instagram': ('likes', 'comments', 'views')}
ACCOUNT_FIELDS = ('platform', 'channel', 'handle', 'url', 'verified', 'verification', 'scope', 'logged_in', 'checked_at', 'coverage',
                  'coverage_note', 'earliest_reached', 'posts_in_window')
# Never in this public repository or the page (the brief, section "Collection").
PRIVATE = re.compile(r'(cookie|session|token|bearer|sessionid|csrftoken|libfile_|authorization|password)', re.I)
BANNED = re.compile(r'(best[- ]performing|top[- ]performing|viral|went viral|engagement rate|paid promotion|boosted|sponsored by|lead generation|revenue)', re.I)


def window_text(s=None):
    a = date.fromisoformat(WINDOW['start'])
    b = date.fromisoformat(WINDOW['end'])
    m = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    return '%d %s to %d %s %d, Toronto time (%d days)' % (a.day, m[a.month - 1], b.day, m[b.month - 1], b.year, WINDOW['days'])


def _in_window(d):
    return WINDOW['start'] <= d <= WINDOW['end']


def check(s, asset_root=None):
    """Return a list of errors. An empty list means the module may be rendered."""
    errs = []
    if s.get('window') != WINDOW:
        errs.append('social: window must be exactly %s (it never moves)' % json.dumps(WINDOW))
    if (date.fromisoformat(WINDOW['end']) - date.fromisoformat(WINDOW['start'])).days + 1 != WINDOW['days']:
        errs.append('social: window length is not %d days' % WINDOW['days'])
    if s.get('status') not in ('draft', 'reviewed'):
        errs.append('social: status must be draft or reviewed')
    if s.get('status') == 'reviewed' and not (s.get('approved') or '').strip():
        errs.append('social: reviewed without the owner approval recorded by hand')
    text = json.dumps(s, ensure_ascii=False)
    if PRIVATE.search(text):
        errs.append('social: private or session material found (%s); remove it before anything is stored here' % PRIVATE.search(text).group(0))
    accts = {}
    for a in s.get('accounts', []):
        for k in ACCOUNT_FIELDS:
            if k not in a:
                errs.append('social account %s/%s: missing %s' % (a.get('platform'), a.get('channel'), k))
        if a.get('platform') not in PLATFORMS:
            errs.append('social account: unknown platform %r' % a.get('platform'))
        if a.get('channel') not in CHANNELS:
            errs.append('social account %s: channel %r is out of scope (Instagram only)' % (a.get('platform'), a.get('channel')))
        if a.get('scope') not in SCOPES:
            errs.append('social account %s/%s: scope must be one of %s' % (a.get('platform'), a.get('channel'), SCOPES))
        if a.get('coverage') not in COVERAGE:
            errs.append('social account %s/%s: coverage must be one of %s' % (a.get('platform'), a.get('channel'), tuple(COVERAGE)))
        if a.get('coverage') == 'complete' and a.get('posts_in_window') is None:
            errs.append('social account %s/%s: a complete inventory needs its post count' % (a.get('platform'), a.get('channel')))
        if a.get('coverage') in ('blocked', 'no_account', 'unverified') and a.get('posts_in_window') is not None:
            errs.append('social account %s/%s: no post count for %s coverage' % (a.get('platform'), a.get('channel'), a.get('coverage')))
        if a.get('coverage') == 'complete' and a.get('earliest_reached', '9999') >= WINDOW['start']:
            errs.append('social account %s/%s: complete only if the feed was read past the window start' % (a.get('platform'), a.get('channel')))
        if a.get('verified') is not True and a.get('coverage') in ('complete', 'partial'):
            errs.append('social account %s/%s: posts from an unverified account cannot be used' % (a.get('platform'), a.get('channel')))
        try:
            datetime.fromisoformat(a.get('checked_at') or '')
        except ValueError:
            errs.append('social account %s/%s: record when the account was checked (checked_at, ISO time with offset)' % (a.get('platform'), a.get('channel')))
        if not isinstance(a.get('logged_in'), bool):
            errs.append('social account %s/%s: record whether the browser was logged in (true or false)' % (a.get('platform'), a.get('channel')))
        accts[(a.get('platform'), a.get('channel'))] = a
    ids = set()
    for p in s.get('posts', []):
        pid = p.get('id', '?')
        for k in POST_FIELDS:
            if k not in p:
                errs.append('social post %s: missing %s (record a missing value as null, never leave it out)' % (pid, k))
        if pid in ids:
            errs.append('social post %s: duplicate id' % pid)
        ids.add(pid)
        a = accts.get((p.get('platform'), p.get('channel')))
        if not a or not a.get('verified'):
            errs.append('social post %s: not from a verified official account in the accounts list' % pid)
        elif a.get('handle') != p.get('account'):
            errs.append('social post %s: account %r does not match the verified handle' % (pid, p.get('account')))
        d = p.get('published_on') or ''
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', d) or not _in_window(d):
            errs.append('social post %s: published_on %r is outside %s to %s' % (pid, d, WINDOW['start'], WINDOW['end']))
        if p.get('date_method') not in DATE_METHODS:
            errs.append('social post %s: date_method must be one of %s' % (pid, DATE_METHODS))
        try:
            datetime.fromisoformat(p.get('captured_at') or '')
        except ValueError:
            errs.append('social post %s: captured_at must be an ISO time with offset' % pid)
        if p.get('relation') not in RELATIONS:
            errs.append('social post %s: relation must be one of %s' % (pid, RELATIONS))
        if p.get('format') not in FORMATS:
            errs.append('social post %s: format must be one of %s' % (pid, FORMATS))
        if p.get('inspection') not in INSPECTION:
            errs.append('social post %s: inspection must be one of %s' % (pid, INSPECTION))
        if p.get('format') == 'video' and p.get('inspection') not in ('watched_in_full', 'partial'):
            errs.append('social post %s: a video is analysed only after it is watched (or labelled partial)' % pid)
        if p.get('format') == 'carousel' and p.get('inspection') not in ('all_slides', 'partial'):
            errs.append('social post %s: a carousel is analysed only after every slide is inspected (or labelled partial)' % pid)
        if p.get('scope') not in SCOPES:
            errs.append('social post %s: scope must be one of %s' % (pid, SCOPES))
        mt = p.get('metrics') or {}
        want = METRICS.get(p.get('channel'), ())
        for k in want:
            if k not in mt:
                errs.append('social post %s: metric %s missing; record null when it is not shown' % (pid, k))
        if any(mt.get(k) is not None for k in want) and not mt.get('captured_at'):
            errs.append('social post %s: metrics need their own capture time' % pid)
        for k in mt:
            if k not in want and k != 'captured_at':
                errs.append('social post %s: metric %s is not recorded for %s' % (pid, k, p.get('channel')))
    for g in s.get('gallery', []):
        post = next((p for p in s.get('posts', []) if p.get('id') == g.get('post')), None)
        if not post:
            errs.append('social gallery: unknown post %r' % g.get('post'))
            continue
        if post.get('inspection') == 'cover_and_caption' and post.get('format') in ('video', 'carousel'):
            errs.append('social gallery %s: only the cover and caption were inspected' % g.get('post'))
        for k in ('image', 'alt', 'credit', 'observed', 'reading', 'take'):
            if not (g.get(k) or '').strip():
                errs.append('social gallery %s: missing %s' % (g.get('post'), k))
        img = g.get('image') or ''
        if not img.startswith('/assets/index/business-spend/social/'):
            errs.append('social gallery %s: images live under /assets/index/business-spend/social/ (sanitised, curated)' % g.get('post'))
        elif asset_root and not os.path.exists(os.path.join(asset_root, img.lstrip('/'))):
            errs.append('social gallery %s: image file missing' % g.get('post'))
    per = {}
    for g in s.get('gallery', []):
        post = next((p for p in s.get('posts', []) if p.get('id') == g.get('post')), {})
        per[post.get('platform')] = per.get(post.get('platform'), 0) + 1
    for pl, k in per.items():
        if k > 2:
            errs.append('social gallery: %s has %d examples (at most two, the second only for a distinct lesson)' % (pl, k))
    partial = any(a.get('coverage') in ('partial', 'blocked', 'unverified') for a in s.get('accounts', []))
    for row in s.get('summary', []):
        if partial and any(k in row for k in ('frequency', 'share', 'proportion', 'posts_per_week')):
            errs.append('social summary: frequency or topic proportions need a complete inventory for every account in the row')
    for g in s.get('gallery', []):
        for k in ('observed', 'reading', 'take'):
            m = BANNED.search(g.get(k) or '')
            if m:
                errs.append('social gallery %s: %r is not a claim this module can make' % (g.get('post'), m.group(0)))
    return errs


def load_reviewed():
    if not os.path.exists(PATH):
        return None
    with open(PATH, encoding='utf-8') as f:
        s = json.load(f)
    if s.get('status') != 'reviewed':
        return None
    errs = check(s, os.path.dirname(os.path.dirname(KIT)))
    if errs:
        raise SystemExit('social.json is marked reviewed but fails its checks:\n  ' + '\n  '.join(errs))
    return s


def method_html(s):
    return ('<h4 class="t">Social posts</h4><p class="dek">Official company Instagram accounts only, posts published %s, collected %s. '
            'These dates are separate from the website observation dates above. %s</p>' % (E(window_text()), E(s['collection']['text']), E(s['collection']['note'])))


def panel_html(c):
    s = c.social
    rows = []
    for pid in c.order:
        cells = []
        for ch in CHANNELS:
            a = next((x for x in s['accounts'] if x['platform'] == pid and x['channel'] == ch), None)
            if not a:
                cells.append('<td data-label="%s">Not checked</td>' % CHANNELS[ch])
                continue
            n = '' if a['posts_in_window'] is None else ', %d posts in the window' % a['posts_in_window']
            cells.append('<td data-label="%s"><span class="cell-main">%s%s</span><span class="cell-sub">%s account &middot; %s</span></td>' % (
                CHANNELS[ch], E(COVERAGE[a['coverage']]), E(n), E(a['scope'].capitalize()), E(a['coverage_note'])))
        rows.append('<tr><td class="brandcell">%s</td>%s</tr>' % (E(c.name(pid)), ''.join(cells)))
    cov = ('<div class="tblock" id="bs-social-coverage"><p class="ktag fact">What the sources say</p><h3 id="bs-sc-h">Scope and coverage</h3><p class="dek">%s</p>'
           '<div class="tw cards" tabindex="0" role="region" aria-labelledby="bs-sc-h"><table class="bs"><thead><tr><th scope="col">Platform</th><th scope="col">Instagram</th></tr></thead>'
           '<tbody>%s</tbody></table></div></div>' % (E(s['scope_note']), ''.join(rows)))
    summ = ''.join('<li>%s</li>' % E(x['text']) for x in s.get('summary', []))
    summary = '<div class="sub" id="bs-social-summary"><h3>Across the six</h3><div class="card reading-card"><span class="ktag">My reading across the six</span><ul class="dek">%s</ul></div></div>' % summ
    posts = {p['id']: p for p in s['posts']}
    gal = []
    for g in s.get('gallery', []):
        p = posts[g['post']]
        gal.append('<figure class="card soc" id="bs-s-%s"><img src="%s" alt="%s" width="640" height="800" loading="lazy" decoding="async">'
                   '<figcaption><span class="kind">%s &middot; %s &middot; %s</span><p class="pnote m0">%s &middot; <a href="%s" rel="noopener nofollow" target="_blank">View the post</a></p>'
                   '<p class="ktag fact">What the post says</p><p class="dek">%s</p><div class="note reading"><span class="lbl">My reading</span><p>%s</p></div>%s</figcaption></figure>' % (
                       E(g['post'].lower()), E(g['image']), E(g['alt']), E(c.name(p['platform'])), E(CHANNELS[p['channel']]), E(p['published_on']),
                       E(g['credit']), E(p['url']), E(g['observed']), E(g['reading']),
                       '<div class="note take"><span class="lbl">What this means for your marketing team</span><p>%s</p></div>' % E(g['take'])))
    gallery = '<div class="sub" id="bs-social-gallery"><h3>Selected posts</h3><p class="dek">%s</p>%s</div>' % (E(s['selection']), ''.join(gal))
    return cov + summary + gallery


# ---------- Collection package: check and ingest (CHROME_HANDOFF.md, steps S1 to S6) ----------
# A package folder holds accounts.json, posts.json, manifest-social.jsonl and screenshots/. Nothing in it is
# committed: the check reads it where it lies, and ingest writes only social.json (status draft, screenshot
# hashes, no images). A draft never adds a tab to the page.

MANIFEST_FIELDS = ('platform', 'channel', 'role', 'account', 'url', 'captured_at', 'logged_in', 'screenshot', 'sanitised', 'sanitisation_note')


def _read_package(d):
    import hashlib
    errs, out = [], {}
    for name in ('accounts.json', 'posts.json'):
        p = os.path.join(d, name)
        if not os.path.exists(p):
            errs.append('package: %s missing' % name)
            out[name] = []
            continue
        with open(p, encoding='utf-8') as f:
            out[name] = json.load(f)
    man = []
    p = os.path.join(d, 'manifest-social.jsonl')
    if not os.path.exists(p):
        errs.append('package: manifest-social.jsonl missing')
    else:
        with open(p, encoding='utf-8') as f:
            for n, line in enumerate(f, 1):
                if line.strip():
                    try:
                        man.append(json.loads(line))
                    except ValueError:
                        errs.append('manifest line %d: not JSON' % n)
    shots = {}
    for m in man:
        for k in MANIFEST_FIELDS:
            if k not in m:
                errs.append('manifest %s: missing %s' % (m.get('screenshot', '?'), k))
        if m.get('role') not in ('social-account', 'social-post', 'social-block'):
            errs.append('manifest %s: role must be social-account, social-post or social-block' % m.get('screenshot'))
        if m.get('sanitised') is not True:
            errs.append('manifest %s: not marked sanitised; send sanitised files only' % m.get('screenshot'))
        if not isinstance(m.get('logged_in'), bool):
            errs.append('manifest %s: logged_in must be true or false' % m.get('screenshot'))
        try:
            datetime.fromisoformat(m.get('captured_at') or '')
        except ValueError:
            errs.append('manifest %s: captured_at must be an ISO time with offset' % m.get('screenshot'))
        f = os.path.join(d, 'screenshots', m.get('screenshot') or '')
        if not m.get('screenshot') or not os.path.isfile(f):
            errs.append('manifest %s: file not in screenshots/' % m.get('screenshot'))
        else:
            with open(f, 'rb') as fh:
                shots[m['screenshot']] = hashlib.sha256(fh.read()).hexdigest()
    for p in out['posts.json']:
        ref = p.get('capture_ref')
        if ref not in shots:
            errs.append('post %s: capture_ref %r is not a manifest screenshot' % (p.get('id'), ref))
    for a in out['accounts.json']:
        if a.get('coverage') in ('complete', 'partial', 'blocked') and not any(
                m.get('role') in ('social-account', 'social-block') and m.get('platform') == a.get('platform') and m.get('channel') == a.get('channel') for m in man):
            errs.append('account %s/%s: needs a profile (or block) screenshot in the manifest' % (a.get('platform'), a.get('channel')))
    have = {(a.get('platform'), a.get('channel')) for a in out['accounts.json']}
    for pl in PLATFORMS:
        for ch in CHANNELS:
            if (pl, ch) not in have:
                errs.append('accounts.json: no row for %s/%s (record no_account, unverified or blocked rather than leaving it out)' % (pl, ch))
    return out, man, shots, errs


def package_to_module(d):
    out, man, shots, errs = _read_package(d)
    s = {'status': 'draft', 'approved': None, 'window': dict(WINDOW), 'accounts': out['accounts.json'], 'posts': out['posts.json'],
         'gallery': [], 'summary': [], 'screenshots': [{'file': k, 'sha256': v} for k, v in sorted(shots.items())],
         'collection': {'started_at': min((m['captured_at'] for m in man if m.get('captured_at')), default=None),
                        'ended_at': max((m['captured_at'] for m in man if m.get('captured_at')), default=None)}}
    errs += check(s)
    return s, errs


def main(argv):
    if len(argv) != 3 or argv[1] not in ('check', 'ingest'):
        print('usage: python3 social.py check|ingest PACKAGE_DIR')
        return 2
    s, errs = package_to_module(argv[2])
    if errs:
        print('HANDOFF REQUEST (nothing was written):\n  ' + '\n  '.join(errs))
        return 1
    n = len(s['posts'])
    if argv[1] == 'check':
        print('PASS: %d accounts, %d posts, %d screenshots; window %s' % (len(s['accounts']), n, len(s['screenshots']), window_text()))
        return 0
    if os.path.exists(PATH):
        with open(PATH, encoding='utf-8') as f:
            if json.load(f).get('status') == 'reviewed':
                print('Refused: social.json is already reviewed; a new collection goes in a new, versioned module.')
                return 1
    with open(PATH, 'w', encoding='utf-8') as f:
        json.dump(s, f, indent=1, ensure_ascii=False)
        f.write('\n')
    print('Wrote social.json (status draft: no tab on the page). %d posts. Review, add the gallery and summary, then record approval by hand.' % n)
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
