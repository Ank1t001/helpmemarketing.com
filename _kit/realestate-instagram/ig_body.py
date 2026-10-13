"""Render a reviewed Instagram report body into the current site shell.

Editorial HTML is a cycle-specific input, not an indefinitely reusable narrative.
The caller verifies its dataset fingerprint before using it.
"""
import csv
import io
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
START = re.compile(r'<!-- ===== REINDEX REPORT BODY START =====.*?-->', re.S)
END = '<!-- ===== REINDEX REPORT BODY END ===== -->'

def split_shell(source):
    match = START.search(source)
    if not match or source.count(END) != 1:
        raise ValueError('Expected one pair of REPORT BODY markers')
    finish = source.index(END, match.end())
    return source[:match.end()], source[match.end():finish], source[finish:]

def render(csv_text, cycle, verified_date, next_date, as_of, modified_at=None):
    shell = (BASE / 'site_shell.html').read_text(encoding='utf-8')
    prefix, _, suffix = split_shell(shell)
    body = (BASE / 'report_body.html').read_text(encoding='utf-8')
    rows = list(csv.DictReader(io.StringIO(csv_text)))
    ranked = sum(r['cohort'] != 'REFERENCE' for r in rows)
    reference = len(rows) - ranked
    body = body.replace('{{LAST_VERIFIED_LONG}}', long_date(verified_date))
    body = body.replace('{{NEXT_REFRESH_LONG}}', long_date(next_date))
    body = body.replace('{{LAST_VERIFIED}}', verified_date)
    body = body.replace('{{NEXT_REFRESH}}', next_date)
    body = body.replace('{{OVERDUE}}', ', not yet published' if as_of > next_date else '')
    body = body.replace('{{CYCLE}}', cycle)
    body = body.replace('{{CSV_ROWS}}', str(len(rows)))
    body = body.replace('{{RANKED_ROWS}}', str(ranked))
    body = body.replace('{{REFERENCE_ROWS}}', str(reference))
    body = body.replace('{{GATED_CSV}}', json.dumps(csv_text, ensure_ascii=True).replace('</', '<\\/'))
    if re.search(r'\{\{[A-Z_]+\}\}', body):
        raise ValueError('Unresolved report token')
    if modified_at:
        check_timestamp(modified_at)
        prefix, count = re.subn(r'"dateModified":"[^"]*"', '"dateModified":"' + modified_at + '"', prefix)
        if count != 1:
            raise ValueError('Expected one dateModified in the shell head')
    return prefix + '\n' + body + '\n' + suffix

TIMESTAMP = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$')

def check_timestamp(value):
    """dateModified must be a recorded ISO 8601 time with a zone, never a date alone or a midnight placeholder."""
    if not TIMESTAMP.match(value) or 'T00:00:00' in value:
        raise ValueError('modified_at must be a recorded ISO 8601 timestamp with a timezone: ' + value)

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
          'September', 'October', 'November', 'December']

def long_date(iso):
    y, m, d = iso.split('-')
    return f'{int(d)} {MONTHS[int(m) - 1]} {y}'

CANON = 'https://helpmemarketing.com/realestate-index'

def snapshot(page, cycle, verified_date):
    """Fixed copy of a published edition at /realestate-index/edition-NNN (noindex, self canonical)."""
    snap_url = f'{CANON}/edition-{cycle}'
    swaps = [
        (f'<link rel="canonical" href="{CANON}">', f'<link rel="canonical" href="{snap_url}">'),
        (f'<meta property="og:url" content="{CANON}">', f'<meta property="og:url" content="{snap_url}">'),
        (f'"url":"{CANON}","isAccessibleForFree"', f'"url":"{snap_url}","isAccessibleForFree"'),
        ('<div class="livebar">', f'<div class="note warn"><span class="lbl">Archived edition {cycle}</span><p>Data collected {long_date(verified_date)}. This snapshot does not change. <a href="/realestate-index">See the current edition</a>.</p></div>\n<div class="livebar">'),
        (f'<a href="{CANON}">{CANON}</a></p>', f'<a href="{snap_url}">{snap_url}</a></p>'),
        (f'This address always shows the latest edition. For a fixed version, cite the <a href="/realestate-index/edition-{cycle}">edition {cycle} snapshot</a>.',
         f'This is the fixed snapshot of edition {cycle}. The <a href="/realestate-index">current edition</a> lives at /realestate-index.'),
    ]
    page, robots = re.subn(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="noindex, follow">', page)
    if robots != 1:
        raise ValueError('Expected one robots meta tag in the page')
    for old, new in swaps:
        if page.count(old) != 1:
            raise ValueError('Snapshot anchor not found: ' + old[:60])
        page = page.replace(old, new)
    crumb = None
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
        if '"BreadcrumbList"' in block:
            crumb = block
    if crumb:
        j = json.loads(crumb)
        items = j['itemListElement']
        items.append({'@type': 'ListItem', 'position': len(items) + 1, 'name': f'Edition {cycle}', 'item': snap_url})
        page = page.replace(crumb, json.dumps(j, ensure_ascii=False, separators=(',', ':')))
    return page
