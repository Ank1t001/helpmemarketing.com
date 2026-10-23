"""Shared evidence model for the Business Cards & Spend Management Index kit.

Every record is checked here, so ingest.py, validate.py and build.py apply the same rules.
"""
import json
import os
import re
from datetime import datetime

KIT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(KIT, '..', '..'))

STATUSES = {
    'published': 'Published',
    'not_found': 'Not found in reviewed sources',
    'not_checked': 'Not checked',
    'conflicting': 'Conflicting',
    'explicitly_unavailable': 'Explicitly unavailable',
}
LAYERS = {'product', 'cross_border', 'marketing'}
CATEGORIES = {
    # product layer
    'card_model', 'network_issuer', 'card_format', 'rewards', 'plans', 'spend_controls', 'eligibility', 'availability',
    # cross-border layer (each checked on its own)
    'xb_card_spending', 'xb_fx', 'xb_accounts', 'xb_transfers',
    # regulatory statements as published (never a safety conclusion)
    'registration', 'funds_holding', 'registry_entry',
    # marketing execution
    # spend-management context
    'approvals', 'expense_workflow', 'accounting',
    'positioning', 'proof', 'case_study', 'journey', 'page_quality',
}
RECON_CLASSES = {'A', 'B', 'C', 'D', 'B and D'}
RECON_LABEL = {'A': 'Explained by different products or conditions', 'B': 'Rendered page and page code differ',
               'C': 'Unresolved difference in the same context', 'D': 'Insufficient evidence to decide'}
METHODS = {'server_fetch', 'browser', 'manual_document_review'}
ISO_OFFSET = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?[+-]\d{2}:\d{2}$')
SRC_ID = re.compile(r'^S-[A-Z]{3}-[A-Z0-9-]+$')
OBS_ID = re.compile(r'^O-[A-Z]{3}-\d{2,3}$')
SHA = re.compile(r'^[0-9a-f]{64}$')


def load(name):
    with open(os.path.join(KIT, name), encoding='utf-8') as f:
        return json.load(f)


def dump(name, data):
    path = os.path.join(KIT, name)
    text = json.dumps(data, ensure_ascii=False, indent=1, sort_keys=False) + '\n'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def parse_ts(value):
    if not isinstance(value, str) or not ISO_OFFSET.match(value):
        raise ValueError('timestamp without an ISO 8601 offset: %r' % (value,))
    return datetime.fromisoformat(value)


def platform_codes():
    p = load('platforms.json')
    return {k: v['code'] for k, v in p['platforms'].items()}, p['order']


def source_id(code, role):
    return 'S-%s-%s' % (code, re.sub(r'[^A-Z0-9]+', '-', role.upper()).strip('-'))


def check_source(s, codes):
    errs = []
    need = ['id', 'platform', 'role', 'requested_url', 'final_url', 'http_status', 'sha256', 'fetched_at', 'method', 'title']
    for k in need:
        if k not in s:
            errs.append('%s: missing %s' % (s.get('id', '?'), k))
    if errs:
        return errs
    if not SRC_ID.match(s['id']):
        errs.append('%s: bad source id' % s['id'])
    if s['platform'] not in codes:
        errs.append('%s: unknown platform %s' % (s['id'], s['platform']))
    elif s['id'] != source_id(codes[s['platform']], s['role']):
        errs.append('%s: id does not match platform and role' % s['id'])
    for k in ('requested_url', 'final_url'):
        if not str(s[k]).startswith('https://'):
            errs.append('%s: %s is not https' % (s['id'], k))
    if not isinstance(s['http_status'], int) and not (s['method'] == 'browser' and s['http_status'] is None):
        errs.append('%s: http_status must be an integer' % s['id'])
    if not SHA.match(str(s['sha256'])):
        errs.append('%s: sha256 is not 64 hex characters' % s['id'])
    if s['method'] not in METHODS:
        errs.append('%s: unknown method %s' % (s['id'], s['method']))
    try:
        parse_ts(s['fetched_at'])
    except ValueError as e:
        errs.append('%s: %s' % (s['id'], e))
    return errs


def check_observation(o, codes, sources):
    """Schema, ID, timestamp and traceability rules for one observation."""
    errs = []
    oid = o.get('id', '?')
    need = ['id', 'platform', 'product', 'layer', 'category', 'market', 'eligibility', 'plan', 'statement', 'amount',
            'units', 'currency', 'conditions', 'sources', 'status', 'method', 'observed_at', 'conflicts', 'interpretation', 'public']
    for k in need:
        if k not in o:
            errs.append('%s: missing field %s' % (oid, k))
    if errs:
        return errs
    if not OBS_ID.match(oid):
        errs.append('%s: bad observation id' % oid)
    if o['platform'] not in codes:
        errs.append('%s: unknown platform' % oid)
    elif not oid.startswith('O-%s-' % codes[o['platform']]):
        errs.append('%s: id prefix does not match platform' % oid)
    if o['layer'] not in LAYERS:
        errs.append('%s: unknown layer %s' % (oid, o['layer']))
    if o['category'] not in CATEGORIES:
        errs.append('%s: unknown category %s' % (oid, o['category']))
    if o['status'] not in STATUSES:
        errs.append('%s: unknown status %s' % (oid, o['status']))
    if o['method'] not in METHODS:
        errs.append('%s: unknown method %s' % (oid, o['method']))
    if not str(o['statement']).strip():
        errs.append('%s: empty statement' % oid)
    # Missing values are null, never zero or an empty string standing in for "unknown".
    for k in ('amount', 'units', 'currency', 'conditions', 'eligibility', 'plan', 'product', 'interpretation'):
        if o[k] == '':
            errs.append('%s: %s is an empty string; use null' % (oid, k))
    if o['amount'] is not None and not isinstance(o['amount'], (int, float)):
        errs.append('%s: amount must be a number or null' % oid)
    if o['amount'] is not None and o['units'] is None:
        errs.append('%s: amount without units' % oid)
    if o['status'] in ('not_checked',) and o['sources']:
        errs.append('%s: a not-checked item cannot cite sources' % oid)
    if o['status'] in ('published', 'conflicting', 'explicitly_unavailable') and not o['sources']:
        errs.append('%s: status %s needs at least one source' % (oid, o['status']))
    if o['status'] == 'not_found':
        if not o.get('reviewed_sources'):
            errs.append('%s: not-found needs the list of reviewed_sources' % oid)
        for sid in o.get('reviewed_sources', []):
            if sid not in sources:
                errs.append('%s: reviewed source %s not in sources.json' % (oid, sid))
    if o['conflicts'] and o['status'] != 'conflicting':
        errs.append('%s: conflict records belong only on Conflicting items; put open questions in conditions' % oid)
    if o['status'] == 'conflicting' and not o['conflicts']:
        errs.append('%s: conflicting status without a conflict record' % oid)
    if o['status'] == 'not_found' and o['amount'] is not None:
        errs.append('%s: a not-found item cannot carry an amount' % oid)
    times = []
    for ref in o['sources']:
        sid = ref.get('source_id')
        if sid not in sources:
            errs.append('%s: source %s not in sources.json' % (oid, sid))
            continue
        if not str(ref.get('excerpt', '')).strip():
            errs.append('%s: source %s without an excerpt' % (oid, sid))
        if len(ref.get('excerpt', '')) > 400:
            errs.append('%s: excerpt from %s is over 400 characters' % (oid, sid))
        times.append(sources[sid]['fetched_at'])
        if sources[sid]['platform'] != o['platform'] and '*' not in sources[sid].get('covers', []) and o['platform'] not in sources[sid].get('covers', []):
            errs.append('%s: cites a source from another platform (%s)' % (oid, sid))
    times += [sources[sid]['fetched_at'] for sid in o.get('reviewed_sources', []) if sid in sources]
    if o['observed_at'] is not None:
        try:
            parse_ts(o['observed_at'])
        except ValueError as e:
            errs.append('%s: %s' % (oid, e))
        if times and o['observed_at'] != max(times, key=parse_ts):
            errs.append('%s: observed_at must equal the latest capture time of its cited and reviewed sources (%s)' % (oid, max(times, key=parse_ts)))
    elif o['status'] != 'not_checked':
        errs.append('%s: observed_at is null for a checked item' % oid)
    for c in o['conflicts']:
        if not c.get('note'):
            errs.append('%s: conflict without a note' % oid)
    rec = o.get('reconciliation')
    if rec is not None:
        if rec.get('class') not in RECON_CLASSES:
            errs.append('%s: reconciliation class must be one of %s' % (oid, sorted(RECON_CLASSES)))
        elif not rec.get('note') or not rec.get('topic'):
            errs.append('%s: reconciliation needs a topic and a note' % oid)
        else:
            # Evidence status and reconciliation are separate: only a class C difference (unresolved in the
            # same context) is Conflicting. Class D (insufficient evidence) never sets the status by itself.
            if 'C' in rec['class'] and o['status'] != 'conflicting':
                errs.append('%s: class %s is an unresolved difference, so the status is Conflicting' % (oid, rec['class']))
            if 'C' not in rec['class'] and o['status'] == 'conflicting':
                errs.append('%s: class %s does not establish a conflict; use the evidence status of the statements' % (oid, rec['class']))
    return errs


def check_all(obs_data, src_data):
    codes, _ = platform_codes()
    errs = []
    sources = {}
    for s in src_data['sources']:
        errs += check_source(s, codes)
        if s['id'] in sources:
            errs.append('%s: duplicate source id' % s['id'])
        sources[s['id']] = s
    ids = set()
    for o in obs_data['observations']:
        errs += check_observation(o, codes, sources)
        if o.get('id') in ids:
            errs.append('%s: duplicate observation id' % o.get('id'))
        ids.add(o.get('id'))
    for o in obs_data['observations']:
        for c in o.get('conflicts', []):
            w = c.get('with')
            if w is not None and w not in ids:
                errs.append('%s: conflict points to unknown %s' % (o['id'], w))
    return errs, sources
