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

  python3 validate.py --social-package PKG_DIR [--social-zip PKG_ZIP]
                                      also confirm the Instagram records, quoted phrases and image
                                      sources against the private Instagram evidence package

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
from html import unescape as html_unescape
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
          r'\bconverts better\b', r'\bconfus', r'\blost (?:sales|customers|conversions|revenue)\b', r'\bdeliberate', r'\b(?:marketing|overall|numerical|platform) score\b', r'\bstar rating\b', r'\bwe\b', r'\bour\b', r'\bus\b']
# "US" (the country) is allowed: the "us" pattern is matched case-sensitively.
TAKE_LABEL = 'What this means for your marketing team'
QUESTION_ANSWERS = ('Answered', 'Answered on another page', 'Partly answered', 'Left unresolved')
TEST_FIELDS = ('id', 'title', 'finding', 'observation', 'evidence', 'question', 'reading', 'hypothesis', 'change', 'comparable',
               'measure', 'guardrail', 'limitation')
CHAIN = ['Observed evidence', 'Customer question', 'My interpretation', 'Testable hypothesis', 'Measurement']
LEGEND = ['What the sources say', 'My reading', TAKE_LABEL, 'Proposed test, not a result']


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


def check_followup(c, raw_dir=None):
    """The Airwallex follow-up of 30 October 2026 is kept apart from the 23 October research. With raw_dir (the private
    captures), every hash and quote is checked against the files."""
    import hashlib
    errs = []
    fu = getattr(c, 'followup', None)
    if not fu:
        return ['follow-up: record missing']
    if fu.get('checked_on') != '2026-10-30' or not fu.get('note') or not fu.get('method'):
        errs.append('follow-up: needs its own date (2026-10-30), a note and a method')
    srcs = {s['id']: s for s in fu.get('sources', [])}
    for s in srcs.values():
        for k in ('url', 'server_fetched_at', 'browser_rendered_at', 'html_sha256', 'text_sha256'):
            if not s.get(k):
                errs.append('follow-up: source %s missing %s' % (s.get('id'), k))
        if not str(s.get('server_fetched_at', '')).startswith('2026-10-30'):
            errs.append('follow-up: source %s not dated 30 October 2026' % s.get('id'))
    for f in fu.get('findings', []):
        if f.get('source') not in srcs or not f.get('quote') or not f.get('text'):
            errs.append('follow-up: finding %s needs a known source, text and an exact quote' % f.get('id'))
    if raw_dir:
        names = {'AWX-FU-PRICING': 'en-ca_pricing', 'AWX-FU-CARDS': 'en-ca_spend-management_cards', 'AWX-FU-TERMS': 'en-ca_terms_cash-rebate-promotion'}
        for sid, s in srcs.items():
            base = os.path.join(raw_dir, names.get(sid, sid))
            for ext, key in (('.html', 'html_sha256'), ('.rendered.txt', 'text_sha256')):
                if not os.path.exists(base + ext) or hashlib.sha256(open(base + ext, 'rb').read()).hexdigest() != s[key]:
                    errs.append('follow-up: %s%s does not match its recorded hash' % (sid, ext))
        for f in fu.get('findings', []):
            p = os.path.join(raw_dir, names.get(f['source'], f['source']) + '.rendered.txt')
            if os.path.exists(p) and f['quote'] not in open(p, encoding='utf-8').read():
                errs.append('follow-up: quote of %s not found in its capture' % f['id'])
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
        for k in ('audience', 'problem', 'benefit', 'offer', 'proof', 'question', 'observation', 'missing', 'ev'):
            if k not in p:
                errs.append('%s: narrative missing %s' % (pid, k))
        q = p.get('question') or {}
        if not q.get('text') or not q.get('detail') or q.get('answer') not in QUESTION_ANSWERS:
            errs.append('%s: the customer question needs text, detail and an answer from %s' % (pid, QUESTION_ANSWERS))
        for k in ('audience', 'problem', 'benefit', 'offer', 'proof'):
            ids = (p.get('ev') or {}).get(k) or []
            if not ids:
                errs.append('%s.%s: every messaging line needs its observation ids' % (pid, k))
            for i in ids:
                if i not in c.obs or c.obs[i]['platform'] != pid:
                    errs.append('%s.%s: bad evidence id %s' % (pid, k, i))
                elif c.obs[i]['status'] in ('not_checked',):
                    errs.append('%s.%s: %s was not checked' % (pid, k, i))
        if not p.get('main_message') or not p.get('stood_out'):
            errs.append('%s: the Messaging table needs a main message and what stood out' % pid)
        if re.search(r'capture request|\bR[12]\b', ' '.join(p.get('missing', []))):
            errs.append('%s: describe missing evidence in plain language, not internal capture codes' % pid)
        cp_ = c.n['compare']
        for k, _ in cp_['cost_columns'] + cp_['card_columns'] + cp_['fee_columns'] + cp_['acct_columns'] + cp_['spend_columns']:
            spec = c.n['compare']['rows'].get(pid, {}).get(k)
            if k == cp_['cost_columns'][0][0]:
                for lbl, txt, ids in c.n['compare']['rows'].get(pid, {}).get('restrictions', []):
                    if lbl not in ('Restriction', 'Credit') or not txt or not ids or any(i not in c.obs or c.obs[i]['platform'] != pid for i in ids):
                        errs.append('%s: restriction line %r needs a label and its own evidence' % (pid, txt))
            if spec is None:
                errs.append('%s: comparison cell %s missing' % (pid, k))
                continue
            sts = [c.obs[i]['status'] for i in spec.get('ids', []) if i in c.obs]
            # a cell whose statements could not be reconciled (class D) must say what could not be confirmed (2026-10-30)
            if any('D' in (c.obs[i].get('reconciliation') or {}).get('class', '') for i in spec.get('ids', []) if i in c.obs) and not spec.get('unclear'):
                errs.append('%s.%s: say what could not be confirmed (unclear)' % (pid, k))
            if spec.get('followup') and spec['followup'] != (getattr(c, 'followup', None) or {}).get('id'):
                errs.append('%s.%s: unknown follow-up %s' % (pid, k, spec['followup']))
            if spec.get('text') is not None and 'explicitly_unavailable' in sts and 'conflicting' not in sts and not spec.get('restriction'):
                errs.append('%s.%s: an explicitly unavailable entry needs its exact restriction for the table label' % (pid, k))
            for i in spec.get('ids', []):
                if i not in c.obs:
                    errs.append('%s.%s: unknown observation %s' % (pid, k, i))
                elif c.obs[i]['platform'] != pid:
                    errs.append('%s.%s: %s belongs to another platform' % (pid, k, i))
            if spec.get('text') is not None and not spec.get('ids'):
                errs.append('%s.%s: a filled cell needs evidence' % (pid, k))
            if spec.get('text') is not None and spec.get('ids') and all(c.obs[i]['status'] in ('not_found', 'not_checked') for i in spec['ids'] if i in c.obs):
                errs.append('%s.%s: text given but the evidence is not found or not checked' % (pid, k))
    jn = c.n.get('journeys', {})
    for pid in EXPECTED_ORDER:
        r = jn.get('rows', {}).get(pid)
        if not r:
            errs.append('journeys: no row for %s' % pid)
            continue
        for k in [k for k, _ in jn['columns']] + [k for k, _ in jn['table_columns']] + ['dest', 'stop']:
            if not r.get(k):
                errs.append('journeys.%s: %s is empty' % (pid, k))
        for i in r.get('ids', []):
            if i not in c.obs or c.obs[i]['platform'] != pid:
                errs.append('journeys.%s: bad evidence id %s' % (pid, i))
        for lbl, txt, ids in r.get('restrictions', []):
            if not lbl or not txt or not ids or any(i not in c.obs or c.obs[i]['platform'] != pid for i in ids):
                errs.append('journeys.%s: restriction line %r needs a label and its own evidence' % (pid, txt))
        if not any(c.obs.get(i, {}).get('category') in ('journey', 'availability') for i in r.get('ids', [])):
            errs.append('journeys.%s: needs a journey observation' % pid)
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
    places = [e.get('place') for e in c.n['examples']['items']]
    # Since the second 2026-10-31 brief, Website Messaging shows visual examples (narrative "web_examples") and the text examples sit in provider evidence.
    if places.count('messaging') or places.count('journeys') != 1 or any(not (x == 'journeys' or str(x).startswith('evidence:')) for x in places):
        errs.append('examples: one in the journey evidence, the rest in provider evidence expanders')
    web = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web_examples_2026-10-31.json'), encoding='utf-8'))
    caps = {w['id']: w for w in web['captures']}
    wx = c.n.get('web_examples', [])
    if [x['label'] for x in wx] != ['Value proposition', 'Proof', 'Call to action'] or len({caps[x['capture']]['pid'] for x in wx if x['capture'] in caps}) != len(wx):
        errs.append('examples: three website examples (value proposition, proof, call to action) from three different brands')
    for x in wx:
        w = caps.get(x['capture'])
        if not w or not w['captured_at'].startswith('2026-10-31') or not set(w['observations']) <= set(c.obs):
            errs.append('examples: website example %s needs a dated capture and linked observations' % x['capture'])
            continue
        pth = os.path.join(model.ROOT, w['src'].lstrip('/'))
        if not os.path.exists(pth) or hashlib.sha256(open(pth, 'rb').read()).hexdigest() != w['sha256']:
            errs.append('examples: the crop for %s is missing or differs from its recorded hash' % x['capture'])
    for pid in EXPECTED_ORDER:
        g = c.n['platforms'][pid].get('glance') or {}
        if set(g) != {'promise', 'audience', 'why', 'proof', 'ev'} or not g['ev'] or not set(g['ev']) <= set(c.obs) or any(t.count('. ') > 1 for k, t in g.items() if k != 'ev'):
            errs.append('messaging: %s needs one short sentence per column and linked observations' % pid)
    if not 2 <= len(c.n['patterns']['items']) <= 3:
        errs.append('patterns: two or three')
    tests = c.n['tests']['items']
    if len(tests) != 3:
        errs.append('tests: exactly three')
    fids = {x['id'] for x in f}
    tids = [t.get('id') for t in tests]
    if tids != ['T1', 'T2', 'T3']:
        errs.append('tests: ids T1, T2, T3 in order')
    for t in tests:
        for k in TEST_FIELDS + ('change_short', 'measure_short'):
            if not t.get(k):
                errs.append('test %s: missing %s' % (t.get('title'), k))
        if t.get('finding') not in fids:
            errs.append('test %s: tied to an unknown finding' % t.get('title'))
        for i in t.get('evidence', []):
            if i not in c.obs:
                errs.append('test %s: unknown observation %s' % (t.get('title'), i))
        if re.search(r'\d+\s*%|uplift|baseline of', ' '.join(str(t.get(k, '')) for k in ('measure', 'comparable', 'change', 'hypothesis')), re.I):
            errs.append('test %s: no invented baselines or uplift' % t.get('title'))
    for it in f:
        # The Overview figure ("X of N") must use the finding's own denominator and not exceed it.
        fig = re.fullmatch(r'(\d+) of (\d+)', it.get('figure', ''))
        if not fig or int(fig.group(1)) > int(fig.group(2)) or not re.match(r'(\d+ of )?%s\b' % fig.group(2), it.get('denominator', '')):
            errs.append('findings: %s figure %r does not match its denominator' % (it.get('id'), it.get('figure')))
        if not it.get('reading') or not it.get('analysis') or it.get('test') not in tids:
            errs.append('findings: %s needs my reading, links to its analysis and its test' % it.get('id'))
    if [s for s in c.n.get('chain', {}).get('steps', [])] != CHAIN:
        errs.append('narrative: the reasoning chain is %s' % ' > '.join(CHAIN))
    if [l for l, _ in c.n.get('legend', [])] != LEGEND:
        errs.append('narrative: the reading guide labels are %s' % LEGEND)
    for where, s in [('findings.take', c.n['findings']['take'])]:
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
    if getattr(c, 'social', None) and getattr(c, 'mode', 'draft') != 'draft':
        import social
        errs += social.release_gate(c.social)
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


def social_csv():
    import social
    return social.CSV_REL


def social_analysis_csv():
    import social
    return social.ANALYSIS_CSV_REL


def paid_csv():
    import paid
    return paid.CSV_REL


def view_html(body, vid):
    """One view's markup, from its section to the next section, whatever the tab order."""
    a = body.index('<section id="%s"' % vid)
    return body[a:body.index('<section id=', a + 1)]


PRIVATE_MARKERS = ('reposts-index', 'captions_exact', 'manifest-social', 'social-evidence-v1.zip', 'libfile_', 'drive.google', 'scratchpad', '_vercel_share', '/_kit/')


def check_social_outputs(c, body):
    """The Instagram view against social.json: order, counts, labels, CSV and private material."""
    import build
    import social
    s = c.social
    errs = []
    views = [v for _, v in build.view_order(c)]
    if [v for v in views if v != 'bs-paid'] != ['bs-overview', 'bs-social', 'bs-messaging', 'bs-compare', 'bs-journeys', 'bs-lessons'] or ('bs-paid' in views and views.index('bs-paid') != 2):
        errs.append('social: tab order is Overview, Social Media Strategy, Paid Social Strategy, Website Messaging, Product Comparison, Customer Journey, Lessons')
    if '<a href="#bs-social" id="bs-tab-social">Social Media Strategy</a>' not in body or html_escape(s['narrative']['view']['dek']) not in body:
        errs.append('social: the tab is labelled "Social Media Strategy" and opens with its one-line introduction')
    sec = view_html(body, 'bs-social')
    ref = view_html(body, 'bs-sources') if '<section id="bs-sources"' in body else ''
    tab = sec
    # Since 2026-10-31 (founder review) the tab is Positioning, Creative Strategy with examples and Engagement by Theme;
    # dates, coverage, calculation rules and the full readings sit in Sources & evidence.
    if s['narrative']['coverage_note'] not in html_unescape(ref) or s['narrative']['coverage_none'] not in html_unescape(ref):
        errs.append('social: Sources & evidence carries the coverage note and the no-posts sentence')
    st = s['narrative']['strategy']
    if re.findall(r'<h3><span class="soc-n">\d</span>([^<]+)</h3>', tab) != [st['positioning_title'], st['creative_title'], st['engagement_title']]:
        errs.append('social: the tab has three parts: Positioning, Creative Strategy, Engagement by Theme')
    for t in (st['positioning_limit'], st['creative_limit'], st['engagement_limit']):
        if html_escape(t) not in tab:
            errs.append('social: a comparison lost the limitation beside it (%s...)' % t[:40])
    if 'Not assessed' in tab or 'What this suggests' in tab or 'A possible test' in tab:
        errs.append('social: the tab carries no empty rows and no tests (tests live in Lessons)')
    if [r['pid'] for r in st['positioning_pair']] != ['venn', 'airwallex']:
        errs.append('social: Positioning compares Venn and Airwallex only')
    for i, cx in enumerate(st['creative_examples'], 1):
        p = next((x for x in s['posts'] if x['id'] == cx['post']), None)
        cl = next((x for x in s['analysis']['posts'] if x['post'] == cx['post']), None)
        art = re.search(r'<article class="soc-cex[^"]*" id="bs-sx%d">(.*?)</article>' % i, tab, re.S)
        if not p or not cl or p['attribution'] == 'unresolved' or not cl['approach_inspected']:
            errs.append('social: creative example %d must be an attributed post whose full creative was inspected' % i)
        elif not art or 'href="http' in art.group(1) or html_escape(cx['shows']) not in art.group(1):
            errs.append('social: creative example %d is missing from the tab, lacks its sentence, or links out' % i)
    if sum(1 for cx in st['creative_examples'] for p in s['posts'] if p['id'] == cx['post'] and p['platform'] == 'venn') > 2 or len(st['creative_examples']) > 4:
        errs.append('social: up to two creative examples per brand')
    sec = sec + ref
    review = 'For editorial review</span>' in tab
    if (s['status'] == 'review' and getattr(c, 'mode', 'draft') == 'draft') != review:
        errs.append('social: the editorial-review flag shows on the draft only, and only while approval is pending')
    for pid in EXPECTED_ORDER:
        a = next(x for x in s['accounts'] if x['platform'] == pid)
        row = re.search(r'<tr id="bs-sc-%s">(.*?)</tr>' % pid, sec, re.S)
        if not row:
            errs.append('social: coverage row for %s missing' % pid)
            continue
        cnt = re.search(r'data-label="Posts in the window"><span class="cell-main">(\d+)</span>', row.group(1))
        n = sum(1 for p in s['posts'] if p['platform'] == pid)
        if not cnt or int(cnt.group(1)) != n or n != a['posts_in_window']:
            errs.append('social: coverage count for %s does not match the %d records' % (pid, n))
        if n == 0 and 'No in-window posts found in the reviewed' not in row.group(1):
            errs.append('social: %s with no posts uses the agreed wording' % pid)
        if a['attribution']['status'] == 'unresolved' and 'Attribution unresolved' not in row.group(1):
            errs.append('social: %s attribution is labelled unresolved' % pid)
        if a['scope'] == 'global' and 'do not show what is offered in Canada' not in row.group(1):
            errs.append('social: %s is a global account and its row says so' % pid)
    venn = 'The captured Venn website footer linked to @tryvault, while this study uses owner-confirmed @venn.ca with supporting profile evidence.'
    if html_escape(venn) not in sec:
        errs.append('social: the Venn website-link sentence is missing or altered')
    if re.search(r'\binactive\b|\bdormant\b', sec, re.I):
        errs.append('social: an account with no posts is never called inactive')
    for ex in s['narrative']['examples']:
        p = next(x for x in s['posts'] if x['id'] == ex['post'])
        rec = re.search(r'<details class="bs-more" id="bs-s%s-src">(.*?)</details>' % ex['id'][1:].lower(), ref, re.S)
        if not rec:
            errs.append('social: the record for offer example %s is missing from Sources & evidence' % ex['id'])
            continue
        t = rec.group(1)
        if p['format'] == 'video' and social.VIDEO_LABEL not in t:
            errs.append('social: example %s is a reel and its record carries "%s"' % (ex['id'], social.VIDEO_LABEL))
        for need in ('What the evidence shows', 'Post record', html_escape(p['url'])):
            if need not in rec.group(1):
                errs.append('social: record for %s lacks %s' % (ex['id'], need))
        if p.get('paid_label') and html_escape(p['paid_label']['text']) not in t and p['paid_label']['text'] not in t:
            errs.append('social: example %s drops its paid-partnership label' % ex['id'])
    if 'Proposed test, not a result</span><h3 class="bs-ttitle">Test ' in sec:
        errs.append('social: the Instagram view adds no test of its own')
    for m in PRIVATE_MARKERS:
        if m in sec:
            errs.append('social: private material in the page (%s)' % m)
    if social.secret_findings(sec):
        errs.append('social: credential-like text in the page')
    rows = list(csv.reader(io.StringIO(social.render_csv(s))))
    head, data = rows[0], rows[1:]
    if head != social.CSV_HEAD or len(data) != len(s['posts']):
        errs.append('social csv: %d rows for %d posts' % (len(data), len(s['posts'])))
    if len({r[head.index('post_url')] for r in data}) != len(data):
        errs.append('social csv: duplicate post URLs')
    for pid in EXPECTED_ORDER:
        if sum(1 for r in data if r[0] == social.NAMES[pid]) != sum(1 for p in s['posts'] if p['platform'] == pid):
            errs.append('social csv: %s count differs from the page' % pid)
    att = social.attributed_count(s)
    unres = len(s['posts']) - att
    pa = head.index('provider_attribution')
    if sum(1 for r in data if r[pa] == 'attributed') != att or sum(1 for r in data if r[pa] == 'unresolved provider attribution') != unres:
        errs.append('social csv: provider_attribution must mark %d attributed posts and %d unresolved records' % (att, unres))
    unresolved_pl = {a['platform'] for a in s['accounts'] if a['attribution']['status'] == 'unresolved'}
    for r in data:
        if (r[pa] == 'attributed') == (next(k for k, v in social.NAMES.items() if v == r[0]) in unresolved_pl):
            errs.append('social csv: provider_attribution does not match the account for %s' % r[head.index('post_url')])
    if unres:
        for need in ('%d attributed posts' % att, '%d @tryramp records with unresolved provider attribution' % unres):
            if need not in sec:
                errs.append('social: totals must separate attributed posts from unresolved records (%r missing)' % need)
        for pid in unresolved_pl:
            row = re.search(r'<tr id="bs-sc-%s">(.*?)</tr>' % pid, sec, re.S)
            if row and (social.UNRESOLVED_LABEL not in row.group(1) or 'Attribution unresolved</span>' not in row.group(1)):
                errs.append('social: the %s row labels its records as unresolved' % pid)
    for r in data:
        for v in r:
            if v[:1] in ('=', '+', '-', '@', '\t', '\r'):
                errs.append('social csv: formula-like cell %r' % v[:20])
        if any(k in ','.join(r) for k in ('Caption as seen', 'reposts')):
            errs.append('social csv: captions and reposts stay out of the file')
    return errs


def check_social_package(c, pkg, zpath=None):
    """Against the private Instagram package: quotes, image sources, record hashes and the package hash."""
    import social
    import social_derive
    errs = []
    s = c.social or json.load(open(social.PATH, encoding='utf-8'))
    if zpath:
        h = social_derive.sha(zpath)
        if h != s['package']['sha256']:
            errs.append('social package: zip sha256 %s is not the recorded %s' % (h, s['package']['sha256']))
    with open(os.path.join(pkg, 'posts.json'), encoding='utf-8') as f:
        caps = {p['id']: social_derive.caption_as_seen(p) for p in json.load(f)}
    for p in s['posts']:
        f = os.path.join(pkg, 'screenshots', p['capture_ref'])
        if not os.path.exists(f) or social_derive.sha(f) != p['capture_sha256']:
            errs.append('social package: capture for %s missing or changed' % p['id'])
        if p['hook'] and p['hook'] not in caps.get(p['id'], ''):
            errs.append('social package: hook for %s is not exact caption text' % p['id'])
    n = social.load_narrative()
    for ex in n['examples']:
        cap = caps.get(ex['post'], '')
        for x in ex['shows']:
            if isinstance(x, dict) and 'q' in x and x['q'] not in cap:
                errs.append('social package: example %s quote %r is not exact caption text' % (ex['id'], x['q'][:40]))
        img = ex.get('image')
        if img:
            f = os.path.join(pkg, 'screenshots', img['from'])
            if not os.path.exists(f) or social_derive.sha(f) != img['from_sha256']:
                errs.append('social package: image source for %s missing or changed' % ex['id'])
    return errs



def check_paid_creatives(c, body):
    """Paid Social Strategy creative review (founder brief, 2026-10-31): counts, denominators, labels and examples."""
    import hashlib
    import paid
    errs = []
    d = c.paid
    cr = d['creatives']['creatives']
    ids = {x['id']: x for x in cr}
    if len(ids) != len(cr):
        errs.append('paid creatives: duplicate creative ids')
    rec_ids = {r['id'] for r in d['records']}
    for x in cr:
        if not set(x['ads']) <= rec_ids:
            errs.append('paid creatives: %s links an ad that is not in the 30 October records' % x['id'])
        if x.get('same_as') and (x['same_as'] not in ids or ids[x['same_as']].get('same_as') or ids[x['same_as']]['pid'] != x['pid']):
            errs.append('paid creatives: %s merges into a creative that is not a distinct creative of the same brand' % x['id'])
        if x['inspection'] == 'not_assessed' and (x['focus'] != 'not_assessed' or x['approaches']):
            errs.append('paid creatives: %s was not inspected but carries visual labels' % x['id'])
    covered = {a for x in cr for a in x['ads']}
    if covered != rec_ids - {r['id'] for r in d['records'] if r['platform'] == 'keep'}:
        errs.append('paid creatives: every ad record with media maps to a creative (%d of %d)' % (len(covered), len(rec_ids)))
    tab = view_html(body, 'bs-paid')
    for pid in paid.NAMES:
        cs = paid.sample(d, pid)
        if not cs:
            if '%s:' % paid.NAMES[pid] not in tab:
                errs.append('paid creatives: %s has no reviewed creatives and needs a coverage line, not percentages' % pid)
            continue
        n = len(cs)
        for dim in ('focus', 'format', 'stage'):
            cnt = paid.counts(cs, dim)
            if sum(cnt.values()) != n:
                errs.append('paid creatives: %s %s counts add to %d, not %d' % (pid, dim, sum(cnt.values()), n))
        for dim in ('approach', 'theme', 'persona'):
            cnt = paid.counts(cs, dim)
            if any(v > n for v in cnt.values()):
                errs.append('paid creatives: %s %s has a category above the sample size' % (pid, dim))
            for k, v in cnt.items():
                if v and ('%d of %d creative' % (v, n)) not in tab:
                    errs.append('paid creatives: %s %s %s (%d of %d) is not shown with its count' % (pid, dim, k, v, n))
    cv = d['narrative']['creative']
    for so in cv['mix_stood_out']:
        cs = paid.sample(d, so['pid'])
        v = paid.counts(cs, so['dim']).get(so['key'], 0)
        if ('%d of %d' % (v, len(cs))) not in so['text']:
            errs.append('paid creatives: "What stood out" for %s says something other than %d of %d' % (so['pid'], v, len(cs)))
    for i, ex in enumerate(cv['examples'], 1):
        x = ids.get(ex['creative'])
        if not x or x.get('same_as') or x['inspection'] == 'not_assessed':
            errs.append('paid creatives: example %d must be a distinct, inspected creative' % i)
            continue
        img = ex.get('image')
        if img:
            pth = os.path.join(model.ROOT, img['src'].lstrip('/'))
            if not os.path.exists(pth) or hashlib.sha256(open(pth, 'rb').read()).hexdigest() != img['sha256']:
                errs.append('paid creatives: example %d image is missing or differs from its recorded hash' % i)
        elif 'Ad-copy review' not in tab:
            errs.append('paid creatives: example %d has no visual and must be labelled as an ad-copy review' % i)
    for need in (cv['share_note'], cv['audience_note'], 'A creative can appear in more than one category.'):
        if html_escape(need) not in tab:
            errs.append('paid creatives: the tab lacks "%s"' % need[:50])
    if re.search(r'(?i)\b(best[- ]performing|top[- ]performing|winning|winner|dominant|outperform\w*|most effective|highest[- ]converting)\b', html_unescape(re.sub(r'<[^>]+>', ' ', tab))):
        errs.append('paid creatives: the tab makes a performance claim')
    for old in ('bs-paid-activity', 'bs-paid-messages', 'bs-paid-vs-web', 'bs-paid-suggests', 'bs-paid-scope'):
        if 'id="%s"' % old in tab:
            errs.append('paid creatives: the old block %s is still in the tab' % old)
    return errs

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
        # a schema type or key, not a word in a title ("Products" is fine; "@type":"Product" is not)
        if any(re.search(r'"%s"' % re.escape(bad), raw) for raw in s.jsonld):
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
            if path not in ('/', '', '/' + build_csv(), '/' + social_csv(), '/' + social_analysis_csv(), '/' + paid_csv()) and path not in extra_paths and not (os.path.exists(target) or os.path.exists(target + '.html')):
                errs.append('page: internal link target missing %s' % h)
    msg = view_html(body, 'bs-messaging')
    refv = view_html(body, 'bs-sources') if '<section id="bs-sources"' in body else ''
    for pid in EXPECTED_ORDER:
        if 'id="bs-msg-%s"' % pid not in msg or '<details class="bs-more plat" id="bs-p-%s">' % pid not in refv:
            errs.append('page: %s needs a Messaging table row and an evidence expander in Sources & evidence' % pid)
    # The tabs stay plain (founder brief, 2026-10-30, final): no observation IDs, evidence lists or "What the sources say" labels.
    import build as _b
    for _, vid in _b.view_order(c):
        tv = view_html(body, vid)
        if re.search(r'\bO-[A-Z]{3}-\d\d\b|id="ev-|What the sources say|capture request|<details(?! class="pd-more")', tv):   # the one "More examples" control in Paid Social Strategy is allowed (founder, 2026-10-31)
            errs.append('page: %s carries evidence detail that belongs in Sources & evidence' % vid)
    if not refv or 'data-bs-back' not in refv or refv.count('id="ev-') != len(c.obs):
        errs.append('page: Sources & evidence holds every observation and a return control')
    if TAKE_LABEL in msg or re.search(r'capture request|\bR[12]\b', body, re.I) or html_escape(c.n['views']['messaging']['table_note']) not in msg:   # the date sits in the limitation beside the table since 2026-10-31
        errs.append('page: Messaging carries no takeaway boxes or capture codes, and keeps its dated limitation beside the table')
    if 'booked' in body or 'after booking' in body:
        errs.append('page: a demo request is not a booked meeting')
    if body.count('<ol class="tests"><li') != 1 or body.count('<dt>Testable hypothesis</dt>') != 3 or body.count('Proposed test, not a result</span><h3 class="bs-ttitle">Test ') != 3:
        errs.append('page: exactly three tests, each with its hypothesis')
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
    import build  # late import: build imports this module
    views = [v for _, v in build.view_order(c)]
    nav = body[body.index('class="ri-nav bs-views"'):]
    nav = nav[:nav.index('</nav>')]
    tl = nav[:nav.index('</div>')] if '</div>' in nav else nav
    if [h[1:] for h in re.findall(r'href="(#[^"]+)"', tl)] != views or 'bs-srclink' in nav:
        errs.append('page: the section nav lists the views in order (%s)' % ', '.join(views))
    # One Sources & evidence link, outside the tab bar, directly after it (founder brief, 2026-10-31).
    after = body[body.index('class="ri-nav bs-views"'):]
    after = after[after.index('</nav>') + 6:]
    if body.count('id="bs-srclink"') != 1 or not after.startswith('<p class="bs-srcrow"><a class="bs-srclink" href="#bs-sources" id="bs-srclink">Sources &amp; evidence</a></p>'):
        errs.append('page: one Sources & evidence link sits directly below the tab bar, outside it')
    if '<a href="#bs-paid" id="bs-tab-paid">' in body and '<a href="#bs-paid" id="bs-tab-paid">Paid Social Strategy</a>' not in body:
        errs.append('page: the paid ads tab is labelled "Paid Social Strategy"')
    if ('bs-social' in views) != bool(getattr(c, 'social', None)) or ('id="bs-social"' in body) != bool(getattr(c, 'social', None)):
        errs.append('page: the Instagram view appears only with a derived module in review or reviewed')
    if getattr(c, 'social', None):
        errs += check_social_outputs(c, body)
    if getattr(c, 'paid', None) and c.paid.get('creatives'):
        errs += check_paid_creatives(c, body)
    if 'class="bs-tablist"' not in nav or len(re.findall(r'<a href="#bs-[a-z]+" id="bs-tab-[a-z]+">', nav)) != len(views):
        errs.append('page: the nav holds one tab link per view inside .bs-tablist')
    if '<script data-bsi-tabs>' not in page or 'data-bsi-views' in page:
        errs.append('page: the tab script is present and the old scroll spy is gone')
    for v in views:
        if '<section id="%s" class="bs-view"' % v not in body:
            errs.append('page: view %s missing' % v)
        sec = body[body.index('<section id="%s"' % v):]
        nxt = re.search(r'<section id="[^"]+" class="bs-view"', sec[1:])
        ends = [i for i in ((nxt.start() + 1) if nxt else -1, sec.find('<section id="bs-help"')) if i > 0]
        sec = sec[:min(ends)] if ends else sec
        if '<p class="bs-next">' not in sec:
            errs.append('page: view %s has no next-view link' % v)
        if ' hidden' in sec[:sec.index('>')]:
            errs.append('page: view %s is hidden in the HTML (only the script hides views)' % v)
    for label in LEGEND:
        if html_escape(label) not in body:
            errs.append('page: reading guide label missing: %s' % label)
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
    errs += check_followup(c, argv[argv.index('--followup') + 1] if '--followup' in argv else None)
    if '--raw' in argv:
        errs += check_raw(c, argv[argv.index('--raw') + 1])
    if '--browser' in argv:
        errs += check_browser(c, argv[argv.index('--browser') + 1])
    if '--archive' in argv:
        errs += check_archive(c, argv[argv.index('--archive') + 1])
    if '--social-package' in argv:
        errs += check_social_package(c, argv[argv.index('--social-package') + 1],
                                     argv[argv.index('--social-zip') + 1] if '--social-zip' in argv else None)
    if errs:
        print('\n'.join(errs))
        print('FAIL: %d problems' % len(errs))
        return 1
    n_conf = sum(1 for o in c.obs.values() if o['status'] == 'conflicting')
    by = {k: sum(1 for o in c.obs.values() if o['status'] == k) for k in model.STATUSES}
    print('PASS: %d sources, %d observations (%s), %d unresolved conflicts%s' % (
        len(c.sources), len(c.obs), ', '.join('%s %d' % (model.STATUSES[k], v) for k, v in by.items()), n_conf,
        ('; excerpts and hashes checked against private captures' + ('; browser screenshot hashes checked' if '--browser' in argv else '') + ('; evidence archive checked' if '--archive' in argv else '')) if '--raw' in argv else '; private captures not checked (pass --raw DIR)')
        + (('; Instagram view: %d posts, status %s' % (len(c.social['posts']), c.social['status'])) if getattr(c, 'social', None) else '')
        + (('; Instagram package checked (quotes, captures%s)' % (', zip hash' if '--social-zip' in argv else '')) if '--social-package' in argv else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
