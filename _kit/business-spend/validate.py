#!/usr/bin/env python3
"""Checks for the Business Cards & Spend Management Index kit.

  python3 validate.py                 input and output checks (build.py runs these too)
  python3 validate.py --raw DIR       also confirm every server-fetch excerpt is in its private
                                      capture and every capture hash matches (DIR holds the raw
                                      captures and their fetch_log.jsonl; it is never in the repo)
  python3 validate.py --raw DIR --browser SHOTS_DIR --archive EVIDENCE_ZIP
                                      also confirm the private archive is the one recorded in
                                      edition.json and holds every source's files with matching hashes
  python3 validate.py --raw DIR --browser SHOTS_DIR
                                      also confirm every browser capture's screenshot hash
                                      (browser excerpts come from the page text in Chrome and
                                      are attested by the capture manifest, not by a text file)

Exit status is 0 only when every check passes.
"""
import csv
import gzip
from html import escape as html_escape
import hashlib
import io
import json
import os
import re
import sys
import unicodedata
from html.parser import HTMLParser

import model

EXPECTED_ORDER = ['venn', 'float', 'ramp', 'loop', 'keep', 'airwallex']
BANNED = [r'\bleverag', r'\butili[sz]e', r'\bempower', r'\bunlock', r'\bsupercharg', r'\bcrucial\b', r'\bpivotal\b', r'\bparamount\b',
          r'\bmyriad\b', r'\bplethora\b', r'\bseamless', r'\beffortless', r'\bholistic\b', r'\bdelve', r'\bgame-changing\b', r'\brevolution',
          r'\bcutting-edge\b', r'\btransform', r'\bsynerg', r'\becosystem\b', r'\bparadigm\b', r'\bdisrupt', r'\breimagin', r'\breinvent',
          r'\bpremium\b', r'\bjust\b',
          # editorial boundaries for this Index
          r'\bhides?\b', r'\bhidden\b', r'\bmislead', r'\bnon-compliant\b', r'\bsafest\b', r'\bwinner\b', r'\bbest card\b', r'\bcheapest\b',
          r'\bconverts better\b', r'\b(?:marketing|overall|numerical|platform) score\b', r'\bstar rating\b', r'\bwe\b', r'\bour\b', r'\bus\b']
# "US" (the country) is allowed: the "us" pattern is matched case-sensitively.
TAKE_LABEL = 'What this means for your marketing team'


def norm(s):
    s = unicodedata.normalize('NFKC', s)
    for a, b in (('’', "'"), ('‘', "'"), ('“', '"'), ('”', '"'), (' ', ' '), ('‑', '-')):
        s = s.replace(a, b)
    return re.sub(r'\s+', ' ', s).strip().lower()


def own_text(c):
    """Every string I wrote (narrative, statements, conditions, interpretations), never the quoted excerpts."""
    out = []

    def walk(x, where):
        if isinstance(x, str):
            out.append((where, x))
        elif isinstance(x, list):
            for i, y in enumerate(x):
                walk(y, '%s[%d]' % (where, i))
        elif isinstance(x, dict):
            for k, y in x.items():
                if k in ('ids', 'evidence', 'href', 'entry', 'id', 'finding', 'platform', 'status'):
                    continue
                walk(y, '%s.%s' % (where, k))
    walk(c.n, 'narrative')
    for o in c.obs.values():
        for k in ('statement', 'conditions', 'interpretation'):
            if o[k]:
                out.append(('%s.%s' % (o['id'], k), o[k]))
        for cf in o['conflicts']:
            out.append(('%s.conflict' % o['id'], cf['note']))
    return out


def check_text(c):
    errs = []
    for where, s in own_text(c):
        if '—' in s:
            errs.append('%s: em dash' % where)
        for pat in BANNED:
            flags = 0 if pat.startswith(r'\bus\b') else re.I
            # quoted provider wording inside my sentences is allowed (text between straight double quotes)
            unq = re.sub(r'"[^"]*"', '', s)
            if re.search(pat, unq, flags):
                errs.append('%s: banned or out-of-bounds wording %r' % (where, pat))
    for o in c.obs.values():
        for r in o['sources']:
            if '—' in r['excerpt']:
                errs.append('%s: excerpt contains an em dash; shorten the excerpt' % o['id'])
    return errs


def check_inputs(c):
    errs, _ = model.check_all({'observations': list(c.obs.values())}, {'sources': list(c.sources.values())})
    ed = c.edition
    if c.order != EXPECTED_ORDER or sorted(c.plats) != sorted(EXPECTED_ORDER):
        errs.append('platforms: exactly Venn, Float, Ramp, Loop, Keep, Airwallex in that order')
    try:
        start, end = model.parse_ts(ed['collection_started_at']), model.parse_ts(ed['collection_ended_at'])
        for s in c.sources.values():
            t = model.parse_ts(s['fetched_at'])
            if not (start <= t <= end):
                errs.append('%s: captured outside the edition collection window' % s['id'])
        times = sorted((model.parse_ts(s['fetched_at']) for s in c.sources.values()))
        if times and (times[0] != start or times[-1] != end):
            errs.append('edition: collection start and end must equal the first and last capture')
    except ValueError as e:
        errs.append('edition: %s' % e)
    rel = ed.get('relationship_disclosure') or {}
    if rel.get('status') not in ('complete', 'not_established'):
        errs.append('edition: relationship_disclosure.status must be complete or not_established')
    if rel.get('status') == 'complete':
        if not rel.get('text') or not rel.get('confirmed_on') or not ed['approvals'].get('relationship_disclosure'):
            errs.append('edition: a complete relationship disclosure needs its text, confirmed_on and the recorded approval')
        if '\u2014' in rel.get('text', ''):
            errs.append('edition: em dash in the relationship disclosure')
    if 'relationship' in c.n.get('method', {}):
        errs.append('narrative: the relationship disclosure lives in edition.json only')
    if ed['timezone'] != 'America/Toronto':
        errs.append('edition: timezone must be America/Toronto')
    if ed['status'] not in ('draft', 'published'):
        errs.append('edition: status must be draft or published')
    if ed['status'] == 'published':
        if not all(ed['approvals'].get(k) for k in ('editorial', 'relationship_disclosure', 'publication')):
            errs.append('edition: published needs recorded approvals (they are entered by hand from the owner, never generated)')
        if ed['relationship_disclosure']['status'] != 'complete':
            errs.append('edition: published needs a completed relationship disclosure')
        if not ed.get('published_at'):
            errs.append('edition: published needs published_at from the recorded deployment')
    elif ed.get('published_at') or ed.get('modified_at'):
        errs.append('edition: a draft carries no publication or modification date')
    for pid in EXPECTED_ORDER:
        if not c.obs_for(pid):
            errs.append('%s: no observations' % pid)
        p = c.n['platforms'].get(pid)
        if not p:
            errs.append('%s: no platform narrative' % pid)
            continue
        for k in ('positioning', 'offer', 'explanation', 'proof', 'journey', 'observation', 'missing'):
            if k not in p:
                errs.append('%s: narrative missing %s' % (pid, k))
        if not p.get('take') and not p.get('missing'):
            errs.append('%s: needs a takeaway or a labelled evidence placeholder' % pid)
        for k, _ in c.n['compare']['product_columns'] + c.n['compare']['xb_columns'] + c.n['compare']['spend_columns']:
            spec = c.n['compare']['rows'].get(pid, {}).get(k)
            if spec is None:
                errs.append('%s: comparison cell %s missing' % (pid, k))
                continue
            for i in spec.get('ids', []):
                if i not in c.obs:
                    errs.append('%s.%s: unknown observation %s' % (pid, k, i))
                elif c.obs[i]['platform'] != pid:
                    errs.append('%s.%s: %s belongs to another platform' % (pid, k, i))
            if spec.get('text') is not None and not spec.get('ids'):
                errs.append('%s.%s: a filled cell needs evidence' % (pid, k))
            if spec.get('text') is not None and spec.get('ids') and all(c.obs[i]['status'] in ('not_found', 'not_checked') for i in spec['ids'] if i in c.obs):
                errs.append('%s.%s: text given but the evidence is not found or not checked' % (pid, k))
    f = c.n['findings']['items']
    if not 1 <= len(f) <= 3:
        errs.append('findings: one to three')
    for block, items in (('findings', f), ('examples', c.n['examples']['items']), ('patterns', c.n['patterns']['items'])):
        for it in items:
            if not it.get('evidence'):
                errs.append('%s: %s has no evidence' % (block, it.get('id', it.get('title'))))
            for i in it.get('evidence', []):
                if i not in c.obs:
                    errs.append('%s: unknown observation %s' % (block, i))
            if block in ('findings', 'patterns') and not it.get('denominator'):
                errs.append('%s: %s has no denominator' % (block, it.get('id', it.get('title'))))
    if len(c.n['examples']['items']) > 4:
        errs.append('examples: at most four')
    if not 2 <= len(c.n['patterns']['items']) <= 3:
        errs.append('patterns: two or three')
    tests = c.n['tests']['items']
    if len(tests) != 3:
        errs.append('tests: exactly three')
    fids = {x['id'] for x in f}
    for t in tests:
        for k in ('title', 'finding', 'example', 'uncertainty', 'change', 'measure', 'guardrail', 'comparison', 'limitation'):
            if not t.get(k):
                errs.append('test %s: missing %s' % (t.get('title'), k))
        if t.get('finding') not in fids:
            errs.append('test %s: tied to an unknown finding' % t.get('title'))
        if re.search(r'\d+\s*%|uplift|baseline of', ' '.join(str(t.get(k, '')) for k in ('measure', 'comparison', 'change')), re.I):
            errs.append('test %s: no invented baselines or uplift' % t.get('title'))
    for where, s in [('findings.take', c.n['findings']['take']), ('patterns.take', c.n['patterns']['take'])] + [('%s.take' % k, v.get('take') or '') for k, v in c.n['platforms'].items()]:
        if s:
            n = len([x for x in re.split(r'(?<=[.?!])\s+', s.strip()) if x])
            if not 2 <= n <= 3:
                errs.append('%s: a takeaway is two or three sentences (has %d)' % (where, n))
    m = c.n['method']['dates']
    import build  # late import: build imports this module
    st, en = ed['collection_started_at'], ed['collection_ended_at']
    for piece in (build.long_date(st), build.toronto_time(st), build.toronto_time(en)):
        if piece not in m:
            errs.append('method.dates: does not match the edition collection times (%s)' % piece)
    errs += check_text(c)
    return errs


class _Scan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.ids = []
        self.hrefs = []
        self.h1 = 0
        self.jsonld = []
        self._ld = None
        self.styles = 0
        self.robots = []
        self.canonical = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.append(a['id'])
        if 'style' in a:
            self.styles += 1
        if tag == 'h1':
            self.h1 += 1
        if tag == 'a' and 'href' in a:
            self.hrefs.append(a['href'])
        if tag == 'meta' and a.get('name') == 'robots':
            self.robots.append(a.get('content'))
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonical.append(a.get('href'))
        if tag == 'script' and a.get('type') == 'application/ld+json':
            self._ld = []

    def handle_endtag(self, tag):
        if tag == 'script' and self._ld is not None:
            self.jsonld.append(''.join(self._ld))
            self._ld = None

    def handle_data(self, d):
        if self._ld is not None:
            self._ld.append(d)
        else:
            self.text.append(d)


def build_csv():
    import build
    return build.CSV_REL


def check_outputs(c, page, csvtext, extra_paths=()):
    errs = []
    mode = getattr(c, 'mode', 'draft')
    s = _Scan()
    s.feed(page)
    body = page[page.index('REPORT BODY START'):page.index('REPORT BODY END')]
    if s.h1 != 1:
        errs.append('page: %d h1 elements' % s.h1)
    dup = sorted({i for i in s.ids if s.ids.count(i) > 1})
    if dup:
        errs.append('page: duplicate ids %s' % dup)
    if s.styles:
        errs.append('page: %d inline style attributes' % s.styles)
    want = c.edition['canonical'] + ('/edition-%s' % c.edition['edition'] if mode == 'snapshot' else '')
    if s.canonical != [want]:
        errs.append('page: canonical must be %s' % want)
    if len(s.robots) != 1:
        errs.append('page: exactly one robots tag')
    elif mode in ('draft', 'snapshot') and s.robots[0] != 'noindex, follow':
        errs.append('page: a %s carries noindex, follow' % mode)
    elif mode == 'release' and ('noindex' in s.robots[0] or not s.robots[0].startswith('index, follow')):
        errs.append('page: the release page is index, follow')
    if mode == 'draft' and ('id="bs-cite"' in page or 'class="draft-flag"' not in page):
        errs.append('page: a draft shows the Draft label and no citation card')
    if mode in ('release', 'snapshot'):
        snap = '/business-spend-index/edition-%s' % c.edition['edition']
        if 'class="draft-flag"' in page or 'Not yet published' in page:
            errs.append('page: a published page carries no draft label')
        if 'id="bs-cite"' not in page or 'id="bs-editions"' not in page or 'href="%s"' % snap not in page:
            errs.append('page: a published page carries the citation card, edition history and the snapshot link')
    if mode == 'snapshot' and '<!-- Snapshot of edition %s as first published.' % c.edition['edition'] not in page:
        errs.append('page: the snapshot carries its header comment')
    types = []
    for raw in s.jsonld:
        try:
            types.append(json.loads(raw)['@type'])
        except Exception as e:
            errs.append('page: JSON-LD does not parse (%s)' % e)
    if sorted(types) != ['Article', 'BreadcrumbList']:
        errs.append('page: JSON-LD types %s (expected Article and BreadcrumbList only)' % types)
    banned = ('Product', 'Offer', 'Review', 'AggregateRating', 'FAQPage', 'datePublished') + (('dateModified',) if mode == 'draft' else ())
    for bad in banned:
        if any(bad in raw for raw in s.jsonld):
            errs.append('page: JSON-LD contains %s' % bad)
    art = [json.loads(r) for r in s.jsonld if '"Article"' in r]
    if art and art[0]['headline'] != c.n['hero']['title']:
        errs.append('page: Article headline must equal the H1')
    if '—' in body:
        errs.append('page: em dash in the report body')
    for h in s.hrefs:
        if '/_kit/' in h or h.startswith('/docs/') or 'scratchpad' in h or '.jsonl' in h:
            errs.append('page: links to a private path %s' % h)
        if h.startswith('#') and len(h) > 1 and h[1:] not in s.ids:
            errs.append('page: in-page link to a missing id %s' % h)
        if h.startswith('/') and not h.startswith('//'):
            path = h.split('#')[0].split('?')[0]
            if path.endswith('.html'):
                errs.append('page: link with .html suffix %s' % h)
            target = os.path.join(model.ROOT, path.lstrip('/'))
            if path not in ('/', '', '/' + build_csv()) and path not in extra_paths and not (os.path.exists(target) or os.path.exists(target + '.html')):
                errs.append('page: internal link target missing %s' % h)
    for pid in EXPECTED_ORDER:
        block = body[body.index('id="bs-p-%s"' % pid):]
        block = block[:block.index('</details>')]
        if TAKE_LABEL not in block:
            errs.append('page: %s has no takeaway or placeholder' % pid)
    if body.count('What this means for your marketing team') < 8:
        errs.append('page: expected a takeaway after each platform, after the findings and after the patterns')
    if body.count('<ol class="tests"><li>') != 1 or body.count('<dt>Observed example</dt>') != 3:
        errs.append('page: exactly three tests')
    for o in c.obs.values():
        if 'id="ev-%s"' % o['id'] not in body:
            errs.append('page: observation %s not rendered' % o['id'])
        if o['conflicts'] and o['status'] == 'conflicting':
            if 'Unresolved difference:' not in body[body.index('id="ev-%s"' % o['id']):][:4000]:
                errs.append('page: conflict for %s not rendered' % o['id'])
    rel = c.edition['relationship_disclosure']
    if rel['status'] == 'complete':
        if body.count(html_escape(rel['text'])) != 1 or 'Relationship disclosure pending' in body:
            errs.append('page: the confirmed relationship disclosure must appear once, with no pending placeholder')
    elif 'Relationship disclosure pending' not in body:
        errs.append('page: a pending relationship disclosure must show its placeholder')
    if 'data-review-cta="research_business_spend"' not in body or 'entry=research_business_spend#contact-form' not in body:
        errs.append('page: review CTA must carry entry research_business_spend')
    rows = list(csv.reader(io.StringIO(csvtext)))
    head, data = rows[0], rows[1:]
    want = [o for o in c.obs.values() if o['public']]
    if len(data) != len(want):
        errs.append('csv: %d rows for %d public observations' % (len(data), len(want)))
    ids = [r[0] for r in data]
    if len(set(ids)) != len(ids):
        errs.append('csv: duplicate observation ids')
    for r in data:
        o = c.obs.get(r[0])
        if not o:
            errs.append('csv: unknown id %s' % r[0])
            continue
        if r[head.index('status')] != model.STATUSES[o['status']]:
            errs.append('csv: status mismatch for %s' % r[0])
        if r[head.index('observed_at')] != (o['observed_at'] or ''):
            errs.append('csv: observed_at mismatch for %s' % r[0])
        if o['amount'] is None and r[head.index('observation')] == '0':
            errs.append('csv: a missing value written as zero for %s' % r[0])
        for v in r:
            if v[:1] in ('=', '+', '-', '@', '\t', '\r'):
                errs.append('csv: unescaped formula-like cell in %s' % r[0])
        if 'interpretation' in ','.join(head) or (o['interpretation'] and o['interpretation'] in ','.join(r)):
            errs.append('csv: interpretations must stay out of the file (%s)' % r[0])
    return errs


def check_raw(c, raw):
    errs = []
    log = {}
    with open(os.path.join(raw, 'fetch_log.jsonl'), encoding='utf-8') as f:
        for line in f:
            x = json.loads(line)
            log[(x['platform'], x['role'])] = x
    texts = {}
    for sid, s in c.sources.items():
        if s['method'] == 'browser':
            continue
        x = log.get((s['platform'], s['role']))
        if not x:
            errs.append('%s: no private capture in %s; request it in the handoff' % (sid, raw))
            continue
        gz = os.path.join(raw, x['file'] + '.html.gz')
        txt = os.path.join(raw, x['file'] + '.txt')
        if not os.path.exists(gz) or not os.path.exists(txt):
            errs.append('%s: capture files missing; request them in the handoff' % sid)
            continue
        with gzip.open(gz, 'rb') as f:
            if hashlib.sha256(f.read()).hexdigest() != s['sha256']:
                errs.append('%s: capture hash does not match sources.json' % sid)
        with open(txt, encoding='utf-8', errors='replace') as f:
            texts[sid] = norm(f.read())
    for o in c.obs.values():
        for r in o['sources']:
            t = texts.get(r['source_id'])
            if t is not None and norm(r['excerpt']) not in t:
                errs.append('%s: excerpt not found in %s: %r' % (o['id'], r['source_id'], r['excerpt'][:80]))
    return errs


def check_browser(c, shots):
    errs = []
    for sid, s in c.sources.items():
        if s['method'] != 'browser':
            continue
        fp = os.path.join(shots, s.get('screenshot') or '')
        if not os.path.isfile(fp):
            errs.append('%s: screenshot %s not in %s' % (sid, s.get('screenshot'), shots))
            continue
        with open(fp, 'rb') as f:
            if hashlib.sha256(f.read()).hexdigest() != s['sha256']:
                errs.append('%s: screenshot hash does not match sources.json' % sid)
    return errs


def check_archive(c, path):
    """The private archive must be the one recorded in edition.json and hold every source's files."""
    import zipfile
    errs = []
    rec = c.edition.get('evidence_archive') or {}
    with open(path, 'rb') as f:
        if hashlib.sha256(f.read()).hexdigest() != rec.get('sha256'):
            errs.append('archive: sha256 differs from edition.json evidence_archive')
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        top = names[0].split('/')[0]
        man = json.loads(z.read(top + '/ARCHIVE_MANIFEST.json'))
        mapped = {m['source_id']: m for m in man['sources']}
        for sid, s in c.sources.items():
            m = mapped.get(sid)
            if not m:
                errs.append('archive: %s has no files in the archive' % sid)
                continue
            for f in m['files']:
                if top + '/' + f not in names:
                    errs.append('archive: %s missing %s' % (sid, f))
            data = z.read(top + '/' + m['files'][0])
            if s['method'] != 'browser':
                data = gzip.decompress(data)
            if hashlib.sha256(data).hexdigest() != s['sha256']:
                errs.append('archive: %s hash does not match sources.json' % sid)
    return errs


def main(argv):
    import build
    page, csvtext, c = build.render()
    errs = check_outputs(c, page, csvtext)
    if '--raw' in argv:
        errs += check_raw(c, argv[argv.index('--raw') + 1])
    if '--browser' in argv:
        errs += check_browser(c, argv[argv.index('--browser') + 1])
    if '--archive' in argv:
        errs += check_archive(c, argv[argv.index('--archive') + 1])
    if errs:
        print('\n'.join(errs))
        print('FAIL: %d problems' % len(errs))
        return 1
    n_conf = sum(1 for o in c.obs.values() if o['status'] == 'conflicting')
    by = {k: sum(1 for o in c.obs.values() if o['status'] == k) for k in model.STATUSES}
    print('PASS: %d sources, %d observations (%s), %d unresolved conflicts%s' % (
        len(c.sources), len(c.obs), ', '.join('%s %d' % (model.STATUSES[k], v) for k, v in by.items()), n_conf,
        ('; excerpts and hashes checked against private captures' + ('; browser screenshot hashes checked' if '--browser' in argv else '') + ('; evidence archive checked' if '--archive' in argv else '')) if '--raw' in argv else '; private captures not checked (pass --raw DIR)'))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
