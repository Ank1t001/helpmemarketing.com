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

def render(csv_text, cycle, verified_date, next_date, as_of):
    shell = (BASE / 'site_shell.html').read_text(encoding='utf-8')
    prefix, _, suffix = split_shell(shell)
    body = (BASE / 'report_body.html').read_text(encoding='utf-8')
    rows = list(csv.DictReader(io.StringIO(csv_text)))
    ranked = sum(r['cohort'] != 'REFERENCE' for r in rows)
    reference = len(rows) - ranked
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
    return prefix + '\n' + body + '\n' + suffix
