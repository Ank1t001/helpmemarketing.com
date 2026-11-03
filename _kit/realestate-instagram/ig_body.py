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

def render(csv_text, cycle, verified_date, next_date, as_of, modified_at=None, window=None, window_days=30):
    shell = (BASE / 'site_shell.html').read_text(encoding='utf-8')
    prefix, _, suffix = split_shell(shell)
    body = (BASE / 'report_body.html').read_text(encoding='utf-8')
    rows = list(csv.DictReader(io.StringIO(csv_text)))
    ranked = sum(r['cohort'] != 'REFERENCE' for r in rows)
    reference = len(rows) - ranked
    body = body.replace('{{WINDOW_DAYS}}', str(window_days))
    body = body.replace('{{WINDOW_END_LONG}}', long_date(window[1] if window else verified_date))
    body = body.replace('{{LAST_VERIFIED_LONG}}', long_date(verified_date))
    body = body.replace('{{NEXT_REFRESH_LONG}}', long_date(next_date))
    body = body.replace('{{LAST_VERIFIED_SHORT}}', short_date(verified_date))
    body = body.replace('{{NEXT_REFRESH_SHORT}}', short_date(next_date))
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

def short_date(iso):
    """Header date as on the Business index (2026-11-03): Nov 2, 2026."""
    y, m, d = iso.split('-')
    return f'{MONTHS[int(m) - 1][:3]} {int(d)}, {y}'

CANON = 'https://helpmemarketing.com/realestate-index'

def snapshot(page, cycle, verified_date):
    """Fixed copy of a published edition at /realestate-index/edition-NNN (noindex, self canonical)."""
    snap_url = f'{CANON}/edition-{cycle}'
    swaps = [
        (f'<link rel="canonical" href="{CANON}">', f'<link rel="canonical" href="{snap_url}">'),
        (f'<meta property="og:url" content="{CANON}">', f'<meta property="og:url" content="{snap_url}">'),
        (f'"url":"{CANON}","isAccessibleForFree"', f'"url":"{snap_url}","isAccessibleForFree"'),
        # Header meta line since 2026-11-03 (was the livebar); the archived note follows the header.
        ('</p></header>\n', f'</p></header>\n<div class="note warn"><span class="lbl">Archived edition {cycle}</span><p>Data collected {long_date(verified_date)}. This snapshot does not change. <a href="/realestate-index">See the current edition</a>.</p></div>\n'),
        (f'<a href="{CANON}">{CANON}</a></p>', f'<a href="{snap_url}">{snap_url}</a></p>'),
        (f'This address always shows the latest edition. For a fixed version, cite the <a href="/realestate-index/edition-{cycle}">edition {cycle} snapshot</a>.',
         f'This is the fixed snapshot of edition {cycle}. The <a href="/realestate-index">current edition</a> lives at /realestate-index.'),
    ]
    # A revised edition (2026-11-03 audit) names the snapshot as the original edition instead.
    rev = re.search(r'This address always shows the latest edition\. The <a href="/realestate-index/edition-%s">original [^<]*</a> is a fixed snapshot of the first publication, with a different set of firms, so it does not support the revised comparison\.' % cycle, page)
    if rev:
        swaps[-1] = (rev.group(0), f'This is the fixed snapshot of edition {cycle}. The <a href="/realestate-index">current edition</a> lives at /realestate-index.')
    # The email-code gate (2026-11-03) never applies to a fixed snapshot: drop the lock, dialog, cards, script and markup.
    page = re.sub(r'<script data-bsi-lock>.*?</script>', '', page, flags=re.S)
    page = re.sub(r'<script data-bsi-gate>.*?</script>', '', page, flags=re.S)
    page = re.sub(r'<!-- Email-code gate dialog.*?-->\n?<dialog class="bs-gate".*?</dialog>\n?', '', page, flags=re.S)
    page = re.sub(r'<div class="bs-gate-card" data-gate-card>.*?</button></div>\n?', '', page, flags=re.S)
    page = page.replace('<div class="bs-gated" data-gate="block"', '<div data-gate="none"')
    page = page.replace('"isAccessibleForFree":false,"hasPart":{"@type":"WebPageElement","isAccessibleForFree":false,"cssSelector":".bs-gated"}', '"isAccessibleForFree":true')
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
