#!/usr/bin/env python3
"""Build paid_creatives.json: one record per distinct reviewed Meta ad creative (founder brief, 2026-10-31).

Usage: python3 paid_creatives_derive.py QUEUE.json CLASS_DIR REVIEWED_ON

QUEUE.json is the private inspection queue made from the 30 October 2026 collection (the same Apify run as
paid_ads.json, re-read from its dataset on 31 October with the media fields). CLASS_DIR holds the reviewers'
classification files. The output keeps no media links and no full ad copy: only ids, asset hashes, labels,
short on-screen hooks and the reasons for each label.

Unit of analysis: a distinct creative execution within a brand. Assets that are byte-identical are one creative;
assets whose middle frame (video) or image is a near match by perceptual hash, with the same brand, kind and
length within 1.5 seconds, are one creative; a reviewer's same_as link (a resize, crop or re-cut with the same
hook, message and visual story) merges the later record into the earlier one.
"""
import hashlib
import json
import os
import re
import sys

KIT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(KIT, 'paid_creatives.json')
BRANDS = {'Venn Canada': 'venn', 'Float': 'float', 'Ramp': 'ramp', 'Loop Financial': 'loop', 'Airwallex': 'airwallex'}
FOCUS = ['product', 'brand', 'brand_product', 'not_assessed']
FORMAT = ['video', 'image', 'carousel', 'other', 'not_assessed']
STAGE = ['TOF', 'MOF', 'BOF', 'Mixed', 'not_assessed']


HANDLE = re.compile(r'@(?!(?:airwallex|venn\.ca|tryramp|ramp|floatcard|loop)\b)[A-Za-z0-9_.]+')


def scrub(t):
    """Private people's handles (commenters, for example) never reach the repository; brand handles stay."""
    return HANDLE.sub('@[handle removed]', t or '')


def main(queue_path, class_dir, reviewed_on):
    queue = {q['id']: q for q in json.load(open(queue_path))}
    recs = {}
    for f in sorted(os.listdir(class_dir)):
        if f.endswith('.json'):
            for r in json.load(open(os.path.join(class_dir, f))):
                if r['id'] in recs:
                    raise SystemExit('duplicate classification for %s' % r['id'])
                recs[r['id']] = r
    missing = sorted(set(queue) - set(recs))
    if missing:
        raise SystemExit('no classification for %s' % ', '.join(missing))
    out = []
    for cid in sorted(queue):
        q, r = queue[cid], recs[cid]
        st = r.get('stage')
        if isinstance(st, list):
            st = st[0] if len(st) == 1 else ('Mixed' if st else 'not_assessed')
        fmt = r.get('format') or 'not_assessed'
        if fmt == 'carousel_card':
            fmt = 'image'
        rec = {
            'id': cid, 'pid': BRANDS[q['brand']], 'snapshot': '2026-10-30', 'reviewed_on': reviewed_on,
            'ads': q['ads'], 'ad_slots': q['ad_slots'], 'asset_sha256': q['rep_sha256'], 'exact_variants': q['variants_exact'],
            'kind': q['kind'], 'duration_s': q['duration_s'], 'frames_reviewed': q['frames_in_sheet'] if q['kind'] == 'video' else None,
            'meta_format_labels': q['display_formats'], 'paid_partnership_label': bool(q.get('paid_partnership')),
            'inspection': r.get('inspected', 'not_assessed'), 'inspection_note': scrub(r.get('inspection_note', '')),
            'same_as': (r.get('same_as') or '').strip() or None,
            'focus': r.get('focus') if r.get('focus') in FOCUS else 'not_assessed', 'focus_note': scrub(r.get('focus_note', '')),
            'format': fmt if fmt in FORMAT else 'other',
            'approaches': sorted(set(r.get('approaches') or [])), 'approach_evidence': scrub(r.get('approach_evidence', '')),
            'people': r.get('people', ''),
            'themes': sorted(set(r.get('themes') or [])),
            'personas': [{'persona': p.get('persona'), 'clue': scrub(p.get('clue', ''))} for p in (r.get('personas') or []) if p.get('persona')],
            'stage': st if st in STAGE else 'not_assessed', 'stage_reason': scrub(r.get('stage_reason', '')),
            'hook': scrub(r.get('hook'))[:140], 'competitor_comparison': bool(r.get('competitor_comparison')),
            'example_value': scrub(r.get('example_value', '')), 'notes': scrub(r.get('notes', '')),
        }
        out.append(rec)
    doc = {
        'source': 'Meta Ad Library, Canada, active ads, collected 30 October 2026 at 5:28 p.m. Toronto time (the snapshot behind paid_ads.json)',
        'media_read': 'The same Apify dataset re-read on %s for its image and video files; the files are kept privately with their hashes' % reviewed_on,
        'queue_sha256': hashlib.sha256(open(queue_path, 'rb').read()).hexdigest(),
        'unit': 'A distinct creative execution within a brand (see the docstring of paid_creatives_derive.py).',
        'creatives': out,
    }
    json.dump(doc, open(OUT, 'w'), indent=1, ensure_ascii=False)
    open(OUT, 'a').write('\n')
    print('wrote %d creatives to %s' % (len(out), OUT))


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
