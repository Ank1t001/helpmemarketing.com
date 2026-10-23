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
        self.assertEqual(rows['O-FLT-11'][5], 'Not found in reviewed sources')
        self.assertEqual(rows['O-LOP-15'][10], '')  # not checked: no capture time is invented
        self.assertIn('Not found in reviewed sources', self.page)

    def test_conditions_and_conflicts_render(self):
        self.assertIn('capped at $5,000 a month', self.page)
        self.assertIn('1% only above $25k monthly spend per card program', self.page)
        self.assertGreaterEqual(self.page.count('Unresolved difference:'), 10)

    def test_draft_head(self):
        self.assertIn('<meta name="robots" content="noindex, follow">', self.page)
        self.assertIn('<link rel="canonical" href="https://helpmemarketing.com/business-spend-index">', self.page)
        self.assertNotIn('datePublished', self.page)
        self.assertEqual(self.page.count('<h1>'), 1)

    def test_relationship_disclosure_is_confirmed_and_draft_stays(self):
        rel = self.c.edition['relationship_disclosure']
        self.assertEqual(rel['status'], 'complete')
        self.assertEqual(rel['text'], 'Neither I nor Help Me Marketing has a commercial relationship with Venn, Float, Ramp, Loop, Keep or Airwallex.')
        self.assertEqual(self.page.count(rel['text']), 1)
        self.assertNotIn('Relationship disclosure pending', self.page)
        self.assertEqual(self.c.edition['status'], 'draft')
        self.assertIsNone(self.c.edition['approvals']['editorial'])
        self.assertIsNone(self.c.edition['approvals']['publication'])
        self.assertIn('<meta name="robots" content="noindex, follow">', self.page)

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
        o = dict(self.c.obs['O-FLT-11'], amount=0, units='%')
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
