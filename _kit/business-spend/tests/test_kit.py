"""Run from the kit folder: python3 -m unittest tests.test_kit"""
import csv
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

KIT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, KIT)

import build  # noqa: E402
import model  # noqa: E402
import validate  # noqa: E402


class KitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page, cls.csv, cls.c = build.render()

    def test_inputs_and_outputs_pass(self):
        self.assertEqual(validate.check_inputs(self.c), [])
        self.assertEqual(validate.check_outputs(self.c, self.page, self.csv), [])

    def test_committed_outputs_match_a_fresh_build(self):
        with open(build.PAGE, encoding='utf-8') as f:
            self.assertEqual(f.read(), self.page)
        with open(build.CSV_PATH, encoding='utf-8') as f:
            self.assertEqual(f.read(), self.csv)

    def test_build_is_deterministic(self):
        page2, csv2, _ = build.render()
        self.assertEqual(page2, self.page)
        self.assertEqual(csv2, self.csv)

    def test_exactly_the_six_platforms_in_order(self):
        self.assertEqual(self.c.order, ['venn', 'float', 'ramp', 'loop', 'keep', 'airwallex'])
        for pid in self.c.order:
            self.assertIn('id="bs-p-%s"' % pid, self.page)

    def test_missing_values_stay_missing(self):
        for o in self.c.obs.values():
            if o['status'] in ('not_found', 'not_checked'):
                self.assertIsNone(o['amount'], o['id'])
        rows = {r[0]: r for r in csv.reader(io.StringIO(self.csv))}
        self.assertEqual(rows['O-RMP-08'][5], 'Not found in reviewed sources')
        for o in self.c.obs.values():
            if o['status'] == 'not_checked':
                self.assertIsNone(o['observed_at'], o['id'])  # no capture time is invented
        self.assertIn('Not found in reviewed sources', self.page)

    def test_conditions_and_conflicts_render(self):
        self.assertIn('earned on the first $5,000 (Essentials)', self.page)
        self.assertIn('1% only above $25k monthly spend per card program', self.page)
        self.assertEqual(self.page.count('Unresolved difference:'), sum(len(o['conflicts']) for o in self.c.obs.values()))
        for o in self.c.obs.values():
            if o['status'] == 'conflicting':
                self.assertTrue(o['conflicts'], o['id'])

    def test_draft_head(self):
        if self.c.mode != 'draft':
            self.skipTest('edition is published')
        self.assertIn('<meta name="robots" content="noindex, follow">', self.page)
        self.assertIn('<link rel="canonical" href="https://helpmemarketing.com/business-spend-index">', self.page)
        self.assertNotIn('datePublished', self.page)
        self.assertEqual(self.page.count('<h1>'), 1)

    def test_relationship_disclosure_is_confirmed_and_draft_stays(self):
        if self.c.mode != 'draft':
            self.skipTest('edition is published')
        rel = self.c.edition['relationship_disclosure']
        self.assertEqual(rel['status'], 'complete')
        self.assertEqual(rel['text'], 'Neither I nor Help Me Marketing has a commercial relationship with Venn, Float, Ramp, Loop, Keep or Airwallex.')
        self.assertEqual(self.page.count(rel['text']), 1)
        self.assertNotIn('Relationship disclosure pending', self.page)
        self.assertEqual(self.c.edition['status'], 'draft')
        self.assertIsNone(self.c.edition['approvals']['editorial'])
        self.assertIsNone(self.c.edition['approvals']['publication'])
        self.assertIn('<meta name="robots" content="noindex, follow">', self.page)

    def test_ten_differences_reconciled(self):
        rec = {o['id']: o['reconciliation']['class'] for o in self.c.obs.values() if o.get('reconciliation')}
        self.assertEqual(rec, {'O-VEN-04': 'C', 'O-VEN-11': 'C', 'O-VEN-15': 'B', 'O-FLT-03': 'A', 'O-LOP-04': 'C',
                               'O-KEP-08': 'A', 'O-AWX-01': 'D', 'O-AWX-04': 'B and D', 'O-AWX-07': 'A', 'O-AWX-12': 'A'})
        for oid, cls in rec.items():
            # evidence status and reconciliation are separate: only class C is Conflicting
            self.assertEqual(self.c.obs[oid]['status'] == 'conflicting', 'C' in cls, oid)
            self.assertIn('href="#ev-%s"' % oid, self.page[self.page.index('id="bs-recon"'):])
        self.assertNotEqual(self.c.obs['O-AWX-01']['status'], 'conflicting')
        self.assertIn('st-undetermined', self.page)

    def test_browser_sources_are_attested_not_invented(self):
        browser = [s for s in self.c.sources.values() if s['method'] == 'browser']
        self.assertEqual(len(browser), 34)
        for s in browser:
            self.assertIsNone(s['http_status'])
            self.assertTrue(s['screenshot'].endswith('.png'))
            self.assertTrue(s['fetched_at'].startswith('2026-10-23T12:'))
        for s in browser:
            self.assertNotIn(s['screenshot'], self.page)  # screenshots stay private
        self.assertIn('html[data-theme="dark"] .app :focus-visible{outline:2px solid var(--cta)', self.page)

    def test_spend_management_context_for_all_six(self):
        body = self.page[self.page.index('id="bs-spend-h"'):]
        body = body[:body.index('</table>')]
        self.assertEqual(body.count('<tr><td class="brandcell">'), 6)
        for label in ('Card limits and controls', 'Approvals', 'Receipts and expenses', 'Accounting connections'):
            self.assertIn(label, body)
        cats = {(o['platform'], o['category']) for o in self.c.obs.values()}
        for pid in self.c.order:
            for cat in ('spend_controls', 'approvals', 'expense_workflow', 'accounting'):
                self.assertIn((pid, cat), cats)

    def test_editorial_corrections(self):
        self.assertIn('earned on the first $5,000 (Essentials) or $25,000 (Plus) of card spend a month', self.page)
        self.assertNotIn('capped at $5,000', self.page)
        self.assertIsNone(self.c.obs['O-AWX-07']['amount'])
        self.assertIn('does not say whether that rate applies to card transactions', self.page)
        self.assertIn('No search result or link preview was observed', self.page)
        self.assertEqual(self.c.obs['O-FLT-11']['status'], 'published')
        self.assertTrue(self.c.obs['O-FLT-11']['observed_at'].startswith('2026-10-23T14:33'))
        self.assertIn('reCAPTCHA', self.c.obs['O-FLT-16']['statement'])
        self.assertEqual([f['id'] for f in self.c.n['findings']['items']][2], 'F3')
        self.assertIn('first screen', self.c.n['findings']['items'][2]['title'])
        self.assertNotIn('Registry', ' '.join(p['title'] for p in self.c.n['patterns']['items']))

    def test_release_dry_run_renders_without_touching_the_repo(self):
        import release
        before = {f: open(os.path.join(model.ROOT, f), encoding='utf-8').read() for f in ('hmm-index.html', 'sitemap.xml', 'business-spend-index.html')}
        c, gate, live, snap, csvtext, errs = release.render_all('2026-10-23', strict=False)
        self.assertEqual(errs, [])
        self.assertEqual(csvtext, self.csv)
        self.assertEqual(live[live.index('REPORT BODY START'):], snap[snap.index('REPORT BODY START'):])
        self.assertIn('content="index, follow', live)
        self.assertIn('<meta name="robots" content="noindex, follow">', snap)
        self.assertIn('href="https://helpmemarketing.com/business-spend-index/edition-001"', snap)
        self.assertNotIn('datePublished', live + snap)
        if self.c.edition['status'] == 'draft':
            self.assertTrue(any('approvals' in g for g in gate))  # the gate stays closed until the owner records it
        hub, hi = release.new_hub(before['hmm-index.html'], '2026-10-23')
        sm, si = release.new_sitemap(before['sitemap.xml'], '2026-10-23')
        self.assertEqual(hi + si, [])
        self.assertEqual(hub.count('href="/business-spend-index"'), 1)
        self.assertNotIn('edition-001', sm)  # snapshots stay out of the sitemap
        self.assertIn('Not scheduled', hub)
        after = {f: open(os.path.join(model.ROOT, f), encoding='utf-8').read() for f in before}
        self.assertEqual(before, after)

    def test_ramp_rewards_bounded(self):
        o = self.c.obs['O-RMP-05']
        self.assertTrue(o['statement'].startswith('A Canadian rewards rate was not found in the reviewed sources.'))
        self.assertNotIn('non-CAD', o['statement'] + (o['conditions'] or '') + (o['interpretation'] or ''))
        self.assertNotIn('non-CAD', self.page)

    def test_five_views_and_content_kinds(self):
        body = self.page[self.page.index('REPORT BODY START'):]
        pos = [body.index('<section id="%s" class="bs-view"' % v) for v in ('bs-overview', 'bs-compare', 'bs-messaging', 'bs-journeys', 'bs-lessons')]
        self.assertEqual(pos, sorted(pos))
        self.assertEqual(body.count('class="note reading"'), 6 + 4)  # six platforms, four examples
        self.assertEqual(body.count('Proposed test, not a result'), 3)
        self.assertEqual(body.count('What this means for your marketing team'), 8 + 1)  # takeaways retained, plus the legend entry
        self.assertIn('id="bs-journey-table"', body)
        self.assertNotIn('Next step observed', body)

    def test_ramp_uncaptured_terms_omitted(self):
        self.assertEqual(self.c.obs['O-RMP-02']['status'], 'not_checked')
        self.assertIsNone(self.c.obs['O-RMP-07']['amount'])
        for phrase in ('three percent', 'margin up to 3%', 'pre-authorised debit (Canadian'):
            self.assertNotIn(phrase, self.page)
        self.assertNotIn('S-RMP-BROWSER-CANADA-CARD-SUPPLEMENT', [r['source_id'] for r in self.c.obs['O-RMP-07']['sources']])

    def test_csv_formula_escaping(self):
        self.assertEqual(build.csv_safe('=SUM(A1)'), "'=SUM(A1)")
        self.assertEqual(build.csv_safe('+ Platform fee'), "'+ Platform fee")
        self.assertEqual(build.csv_safe('-1'), "'-1")
        self.assertEqual(build.csv_safe(None), '')
        for row in csv.reader(io.StringIO(self.csv)):
            for v in row:
                self.assertNotIn(v[:1], ('=', '+', '-', '@'))

    def test_model_rejects_zero_for_missing_and_uncited_facts(self):
        codes, _ = model.platform_codes()
        sources = self.c.sources
        o = dict(self.c.obs['O-RMP-08'], amount=0, units='%')
        self.assertTrue(any('not-found item cannot carry an amount' in e for e in model.check_observation(o, codes, sources)))
        o = dict(self.c.obs['O-VEN-02'], sources=[])
        self.assertTrue(any('needs at least one source' in e for e in model.check_observation(o, codes, sources)))
        o = dict(self.c.obs['O-VEN-02'], observed_at='2026-10-23T10:39:57')
        self.assertTrue(any('offset' in e for e in model.check_observation(o, codes, sources)))

    def test_ingest_is_idempotent_and_refuses_silent_changes(self):
        tmp = tempfile.mkdtemp()
        try:
            kit = os.path.join(tmp, 'k')
            shutil.copytree(KIT, kit, ignore=shutil.ignore_patterns('__pycache__', 'tests'))
            obs = os.path.join(tmp, 'obs.json')
            with open(os.path.join(KIT, 'observations.json'), encoding='utf-8') as f:
                data = json.load(f)['observations']
            with open(obs, 'w', encoding='utf-8') as f:
                json.dump(data, f)
            run = lambda *a: subprocess.run([sys.executable, 'ingest.py'] + list(a), cwd=kit, capture_output=True, text=True)
            r = run('observations', obs)
            self.assertEqual(r.returncode, 0, r.stdout)
            self.assertIn('0 added, %d unchanged' % len(data), r.stdout)
            data[0]['statement'] = 'changed'
            with open(obs, 'w', encoding='utf-8') as f:
                json.dump(data, f)
            r = run('observations', obs)
            self.assertEqual(r.returncode, 1)
            self.assertIn('use --replace', r.stdout)
            man = os.path.join(tmp, 'm.jsonl')
            with open(man, 'w') as f:
                f.write(json.dumps({'platform': 'keep', 'role': 'journey', 'url': 'https://www.trykeep.com/', 'final_url': 'https://www.trykeep.com/',
                                    'captured_at': '2026-10-24T09:12:05-04:00', 'country': 'Canada', 'plan_or_version': 'public', 'excerpt': 'x',
                                    'screenshot': 'missing.png', 'sanitised': True, 'sanitisation_note': 'none needed', 'title': 't'}) + '\n')
            r = run('browser', man, tmp)
            self.assertEqual(r.returncode, 1)
            self.assertIn('HANDOFF REQUEST', r.stdout)
        finally:
            shutil.rmtree(tmp)


if __name__ == '__main__':
    unittest.main()
