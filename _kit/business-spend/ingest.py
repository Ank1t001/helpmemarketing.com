#!/usr/bin/env python3
"""Idempotent ingestion into the kit.

  python3 ingest.py sources FETCH_LOG.jsonl [--method server_fetch|browser]
      Adds each capture in a fetch log (one JSON object per line, as written by the
      collection fetcher or a Chrome capture manifest) to sources.json. The id is
      derived from platform and role, so running the same log twice changes nothing.
      A capture whose id exists with a different sha256 or time is refused unless
      --replace is given (a re-capture must be a deliberate decision).

  python3 ingest.py observations FILE.json [--replace]
      Merges observation records (a JSON list) into observations.json by id, with
      the same schema, timestamp and traceability checks as validate.py. Identical
      records are skipped; changed records need --replace.

  python3 ingest.py browser MANIFEST.jsonl FILES_DIR [--replace]
      Adds sanitised Chrome captures (see CHROME_HANDOFF.md for the manifest fields).
      Every file the manifest names must exist in FILES_DIR and be readable; each is
      hashed. If anything is missing or unsanitised, nothing is written and a specific
      handoff request is printed instead (exit status 1).

Raw pages are never stored in the kit: only URL, final URL, status, hash, capture
time, method and title are recorded here. The raw captures stay in private storage.
"""
import hashlib
import json
import os
import re
import sys

import model

KEEP = ['platform', 'role', 'requested_url', 'final_url', 'http_status', 'content_type', 'bytes', 'sha256', 'fetched_at', 'title']


def ingest_sources(path, method, replace):
    codes, _ = model.platform_codes()
    data = model.load('sources.json')
    have = {s['id']: s for s in data['sources']}
    added = skipped = replaced = 0
    errs = []
    with open(path, encoding='utf-8') as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            raw = json.loads(line)
            if raw.get('error'):
                errs.append('line %d: capture recorded an error (%s); not ingested' % (n, raw['error']))
                continue
            rec = {k: raw.get(k) for k in KEEP}
            rec['method'] = method
            rec['method_detail'] = raw.get('method')
            rec = dict([('id', model.source_id(codes.get(rec['platform'], 'XXX'), rec['role'] or ''))] + list(rec.items()))
            e = model.check_source(rec, codes)
            if e:
                errs += ['line %d: %s' % (n, x) for x in e]
                continue
            old = have.get(rec['id'])
            if old == rec:
                skipped += 1
            elif old is None:
                have[rec['id']] = rec
                added += 1
            elif replace:
                have[rec['id']] = rec
                replaced += 1
            else:
                errs.append('line %d: %s already exists with different content; use --replace' % (n, rec['id']))
    if errs:
        print('\n'.join(errs))
        print('Nothing written.')
        return 1
    order = {k: i for i, k in enumerate(model.platform_codes()[1])}
    data['sources'] = sorted(have.values(), key=lambda s: (order[s['platform']], model.parse_ts(s['fetched_at']), s['id']))
    model.dump('sources.json', data)
    print('sources: %d added, %d unchanged, %d replaced, %d total' % (added, skipped, replaced, len(data['sources'])))
    return 0


def ingest_observations(path, replace):
    obs = model.load('observations.json')
    src = model.load('sources.json')
    with open(path, encoding='utf-8') as f:
        incoming = json.load(f)
    have = {o['id']: o for o in obs['observations']}
    added = skipped = replaced = 0
    for o in incoming:
        old = have.get(o.get('id'))
        if old == o:
            skipped += 1
        elif old is None:
            have[o['id']] = o
            added += 1
        elif replace:
            have[o['id']] = o
            replaced += 1
        else:
            print('%s already exists with different content; use --replace. Nothing written.' % o.get('id'))
            return 1
    trial = dict(obs, observations=list(have.values()))
    errs, _ = model.check_all(trial, src)
    if errs:
        print('\n'.join(errs))
        print('Nothing written.')
        return 1
    order = {k: i for i, k in enumerate(model.platform_codes()[1])}
    trial['observations'].sort(key=lambda o: (order[o['platform']], o['id']))
    model.dump('observations.json', trial)
    print('observations: %d added, %d unchanged, %d replaced, %d total' % (added, skipped, replaced, len(trial['observations'])))
    return 0


BROWSER_FIELDS = ['platform', 'role', 'url', 'final_url', 'captured_at', 'country', 'plan_or_version', 'excerpt', 'screenshot', 'sanitised', 'sanitisation_note', 'title']
SECRETS = re.compile(r'(?i)(set-cookie|cookie:|authorization:|bearer\s+[a-z0-9._-]{10,}|session[_-]?id=|_vercel_jwt|access_token|refresh_token)')


def ingest_browser(path, files_dir, replace):
    codes, _ = model.platform_codes()
    need, recs = [], []
    with open(path, encoding='utf-8') as f:
        lines = [l for l in f if l.strip()]
    if not lines:
        need.append('the manifest is empty; send one line per capture')
    for n, line in enumerate(lines, 1):
        try:
            m = json.loads(line)
        except ValueError:
            need.append('line %d: not valid JSON' % n)
            continue
        miss = [k for k in BROWSER_FIELDS if m.get(k) in (None, '')]
        if miss:
            need.append('line %d: fill %s' % (n, ', '.join(miss)))
            continue
        if SECRETS.search(line):
            need.append('line %d: contains cookie, token or session material; send a sanitised manifest' % n)
            continue
        if m['sanitised'] is not True:
            need.append('line %d: screenshot %s is not marked sanitised; blur account names, emails, cookies and session details, then resend' % (n, m['screenshot']))
            continue
        try:
            model.parse_ts(m['captured_at'])
        except ValueError:
            need.append('line %d: captured_at must be the genuine capture time with an offset, e.g. 2026-10-24T09:12:05-04:00' % n)
            continue
        fp = os.path.join(files_dir, os.path.basename(m['screenshot']))
        if not os.path.isfile(fp):
            need.append('line %d: file %s is not in %s; upload the sanitised file itself, not a path on another machine' % (n, m['screenshot'], files_dir))
            continue
        with open(fp, 'rb') as f:
            data = f.read()
        if not data:
            need.append('line %d: file %s is empty' % (n, m['screenshot']))
            continue
        rec = {'id': model.source_id(codes.get(m['platform'], 'XXX'), 'browser-' + m['role']), 'platform': m['platform'], 'role': 'browser-' + m['role'],
               'requested_url': m['url'], 'final_url': m['final_url'], 'http_status': None, 'content_type': None, 'bytes': len(data),
               'sha256': hashlib.sha256(data).hexdigest(), 'fetched_at': m['captured_at'], 'title': m['title'], 'method': 'browser',
               'method_detail': 'Chrome, logged out, %s, %s; %s' % (m['country'], m['plan_or_version'], m['sanitisation_note']),
               'screenshot': os.path.basename(m['screenshot'])}
        e = model.check_source(rec, codes)
        if e:
            need += ['line %d: %s' % (n, x) for x in e]
            continue
        recs.append(rec)
    if need:
        print('HANDOFF REQUEST (nothing was written):')
        print('\n'.join('- ' + x for x in need))
        return 1
    data = model.load('sources.json')
    have = {s['id']: s for s in data['sources']}
    for r in recs:
        if r['id'] in have and have[r['id']] != r and not replace:
            print('%s already exists with different content; use --replace. Nothing written.' % r['id'])
            return 1
    added = sum(1 for r in recs if r['id'] not in have)
    for r in recs:
        have[r['id']] = r
    order = {k: i for i, k in enumerate(model.platform_codes()[1])}
    data['sources'] = sorted(have.values(), key=lambda s: (order[s['platform']], model.parse_ts(s['fetched_at']), s['id']))
    model.dump('sources.json', data)
    print('browser sources: %d added, %d total. Add or update observations that cite them, then run build.py.' % (added, len(data['sources'])))
    return 0


def main(argv):
    if len(argv) < 3 or argv[1] not in ('sources', 'observations', 'browser'):
        print(__doc__)
        return 2
    replace = '--replace' in argv
    if argv[1] == 'browser':
        if len(argv) < 4:
            print(__doc__)
            return 2
        return ingest_browser(argv[2], argv[3], replace)
    if argv[1] == 'sources':
        method = 'server_fetch'
        if '--method' in argv:
            method = argv[argv.index('--method') + 1]
        return ingest_sources(argv[2], method, replace)
    return ingest_observations(argv[2], replace)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
