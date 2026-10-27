"""Run from the kit folder: python3 -m unittest tests.test_kit"""
import csv
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

KIT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, KIT)

import build  # noqa: E402
import model  # noqa: E402
import social  # noqa: E402
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
        self.assertEqual(body.count('<tr id="bs-spend-'), 6)
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
        self.assertEqual(hub.count('href="/business-spend-index"'), 2)  # artwork link and read link, as on the other cards
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
        pos = [body.index('<section id="%s" class="bs-view"' % v) for v in ('bs-overview', 'bs-compare', 'bs-messaging', 'bs-social', 'bs-journeys', 'bs-lessons')]
        self.assertEqual(pos, sorted(pos))
        self.assertEqual(body.count('class="note reading"'), 6 + 4 + 1 + 4)  # six platforms, four examples, the journey reading, four Instagram examples
        self.assertEqual(body.count('Proposed test, not a result</span><b>Test '), 3)   # still exactly three tests
        self.assertEqual(body.count('What this means for your marketing team'), 8 + 1 + 4)  # takeaways retained, the legend entry, four Instagram examples
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


    # ----- 2026-10-23 update: true tabs, panel content, reasoning chain, social module, archive status -----

    def test_tabs_markup_script_and_print(self):
        body = self.page[self.page.index('REPORT BODY START'):]
        nav = body[body.index('class="ri-nav bs-views"'):]
        nav = nav[:nav.index('</nav>')]
        self.assertIn('<div class="bs-tablist">', nav)
        for k in ('overview', 'compare', 'messaging', 'social', 'journeys', 'lessons'):
            self.assertIn('<a href="#bs-%s" id="bs-tab-%s">' % (k, k), nav)
        self.assertEqual(re.findall(r'id="bs-tab-([a-z]+)"', nav), ['overview', 'compare', 'messaging', 'social', 'journeys', 'lessons'])
        self.assertNotIn('role="tab', body)                  # roles come from the script: without it the page is a plain reading order
        self.assertNotRegex(body, r'<section id="bs-[a-z]+" class="bs-view"[^>]* hidden')
        self.assertEqual(body.count('<p class="bs-next">'), 6)
        script = self.page[self.page.index('<script data-bsi-tabs>'):]
        script = script[:script.index('</script>')]
        for needle in ("'tablist'", "'tab'", "'tabpanel'", 'aria-selected', 'aria-controls', 'aria-labelledby', 'ArrowRight', 'ArrowLeft',
                       "'Home'", "'End'", 'pushState', 'replaceState', 'popstate', 'hashchange', 'scrollRestoration', "p.tagName === 'DETAILS'", 'av.hidden'):
            self.assertIn(needle, script)
        self.assertIn('@media print{\n.msi.msi .bs-view[hidden]{display:block!important}', self.page)
        self.assertNotIn('data-bsi-views', self.page)
        self.assertNotIn('onclick', self.page)

    def test_reasoning_chain_and_reading_guide(self):
        body = self.page[self.page.index('REPORT BODY START'):]
        self.assertIn('<ol class="chain-steps"><li>Observed evidence</li><li>Customer question</li><li>My interpretation</li><li>Testable hypothesis</li><li>Measurement</li></ol>', body)
        for label in ('What the sources say', 'My reading', 'What this means for your marketing team', 'Proposed test, not a result'):
            self.assertIn('<dt>%s</dt>' % label, body)
        for t in self.c.n['tests']['items']:
            li = body[body.index('<li id="bs-%s">' % t['id'].lower()):]
            li = li[:li.index('</li>')]
            dts = [x for x in __import__('re').findall(r'<dt>([^<]+)</dt>', li)]
            self.assertEqual(dts, ['Observed evidence', 'Customer question', 'My interpretation', 'Testable hypothesis', 'One change',
                                   'What stays comparable', 'Primary measurement', 'Guardrail', 'When the result would be inconclusive'])
            self.assertTrue(t['evidence'])
        for f in self.c.n['findings']['items']:
            blk = body[body.index('<div class="find" id="bs-%s">' % f['id'].lower()):]
            blk = blk[:blk.index('</dl>')]
            self.assertIn('href="#bs-%s"' % f['test'].lower(), blk)
            for _, anchor in f['analysis']:
                self.assertIn('href="#%s"' % anchor, blk)
                self.assertIn('id="%s"' % anchor, body)

    def test_messaging_fields_trace_to_evidence(self):
        body = self.page[self.page.index('REPORT BODY START'):]
        for pid in self.c.order:
            blk = body[body.index('id="bs-p-%s"' % pid):]
            blk = blk[:blk.index('<details')]
            for label in ('Audience named', 'Problem emphasised', 'Promised benefit', 'Offer and its conditions', 'Proof supplied'):
                self.assertIn('<dt>%s</dt>' % label, blk)
            self.assertIn('<b>Customer question:</b>', blk)
            for anchor in ('bs-prod-%s', 'bs-xb-%s', 'bs-spend-%s', 'bs-jt-%s'):
                self.assertIn('href="#%s"' % (anchor % pid), blk)
            for ids in self.c.n['platforms'][pid]['ev'].values():
                for i in ids:
                    self.assertEqual(self.c.obs[i]['platform'], pid)
        new = ['O-VEN-23', 'O-FLT-23', 'O-RMP-21', 'O-LOP-21', 'O-KEP-20', 'O-AWX-20']
        for i in new:
            o = self.c.obs[i]
            self.assertEqual(o['category'], 'positioning')
            self.assertTrue(all(r['source_id'].endswith('-HOME') for r in o['sources']))
            self.assertEqual(o['observed_at'], self.c.sources[o['sources'][0]['source_id']]['fetched_at'])

    def test_eligibility_kept_apart_from_wider_availability(self):
        body = self.page[self.page.index('id="bs-prod-h"'):]
        body = body[:body.index('</table>')]
        self.assertIn('Who can apply from Canada', body)
        self.assertIn('Self-serve sign-up route closed to new applicants when checked', body)
        self.assertIn('availability in other countries is not assessed', self.page)

    def test_hub_wording_and_card_artwork(self):
        import release
        hub = open(os.path.join(model.ROOT, 'hmm-index.html'), encoding='utf-8').read()
        new, issues = release.new_hub(hub, '2026-10-23')
        self.assertEqual(issues, [])
        self.assertIn('<title>The HMM Index: Marketing Research | HelpMeMarketing</title>', new)
        self.assertNotIn('Instagram Benchmarks', new)
        self.assertIn('Sources accompany the observations, with my interpretation labelled separately.', new)
        # owner's wording, 27 October 2026
        self.assertIn('<li><h3>Public data only</h3><p>I review publicly available business content. The Instagram studies examine posts; the business card study examines websites, application and demo entry screens, and Instagram content. Each study explains its sources and access limitations.</p></li>', new)
        self.assertIn('<li><h3>Consistent within each study</h3><p>Each study applies a shared checklist and records differences in coverage. The business card study separates product information, messaging, entry screens and Instagram observations. Missing evidence and unresolved account attribution are labelled. Figures from different studies are not compared.</p></li>', new)
        self.assertIn('How six selected platforms explain business cards, spend management and cross-border payments to Canadian businesses, alongside a review of selected Canadian and global Instagram accounts. An independent case study from dated public sources, not a ranking or recommendation.', new)
        self.assertEqual(new.count('Monthly</p>'), hub.count('Monthly</p>'))   # the Instagram studies keep their cadence
        self.assertIn('Not scheduled', new)
        self.assertIn('/assets/index/business-spend/hero.webp', new)
        for f in ('hero.webp', 'hero-704.webp'):
            self.assertTrue(os.path.exists(os.path.join(model.ROOT, 'assets/index/business-spend', f)))
        desc = __import__('re').search(r'<meta name="description" content="([^"]+)"', new).group(1)
        self.assertTrue(70 <= len(desc) <= 158, len(desc))

    def test_archive_storage_status_is_not_overstated(self):
        a = self.c.edition['evidence_archive']
        self.assertEqual(a['sha256'], '735b0ac51676bd02c253ee1a29b0e0b460c75497ef4430247cb0070c2cd781ab')
        st = a['storage']
        self.assertTrue(st['reference_supplied'])
        self.assertFalse(st['stored_copy_retrieved'])
        self.assertFalse(st['stored_copy_hash_verified'])
        self.assertNotIn('temporary storage', json.dumps(a))
        for root, _, files in os.walk(KIT):
            for f in files:
                if f.endswith(('.json', '.md', '.py', '.html')):
                    with open(os.path.join(root, f), encoding='utf-8', errors='replace') as fh:
                        self.assertNotIn('libfile_' + '8a18', fh.read(), f)   # the private storage reference never enters the repo
        self.assertNotIn('libfile', self.page)


    def test_loop_correction_is_logged_and_propagated(self):
        body = self.page[self.page.index('REPORT BODY START'):]
        log = body[body.index('id="bs-corrections"'):]
        log = log[:log.index('</details>')]
        self.assertIn('<b>26 October 2026.</b>', log)   # Toronto date of commit 9e020f1 (21:08 EDT)
        self.assertIn('12 hours weekly', log)
        self.assertIn('O-LOP-12', log)
        outside = self.page.replace(log, '')
        self.assertNotIn('12 hours a year', outside + self.csv)        # only the correction history may quote the old wording
        self.assertNotIn('12 hours saved a year', outside + self.csv)
        self.assertIn('Before this correction', log)
        self.assertIn('Businesses save an average of $40,000 annually and 12 hours weekly', [s['excerpt'] for s in self.c.obs['O-LOP-12']['sources']])

def _fixture():
    """Synthetic data for the social checks only. Nothing here is an observation."""
    acct = {'platform': 'loop', 'channel': 'instagram', 'handle': 'example_handle', 'url': 'https://example.invalid/example_handle',
            'verified': True, 'verification': 'fixture', 'scope': 'canada', 'logged_in': False, 'checked_at': '2026-11-01T09:55:00-04:00', 'coverage': 'complete',
            'coverage_note': 'fixture', 'earliest_reached': '2026-07-01', 'posts_in_window': 1}
    post = {'id': 'P-1', 'platform': 'loop', 'channel': 'instagram', 'account': 'example_handle', 'url': 'https://example.invalid/p/1',
            'published_on': '2026-08-01', 'date_method': 'post_page_timestamp', 'captured_at': '2026-11-01T10:00:00-04:00', 'scope': 'canada',
            'relation': 'original', 'format': 'image', 'topic': 'offer', 'question': 'q', 'product': 'card', 'geography': 'Canada',
            'hook': 'h', 'proof': None, 'cta': None, 'inspected': 'image and caption', 'inspection': 'cover_and_caption', 'capture_ref': 'C-1',
            'metrics': {'likes': None, 'comments': 3, 'views': None, 'captured_at': '2026-11-01T10:00:00-04:00'}}
    return {'status': 'draft', 'approved': None, 'window': dict(social.WINDOW), 'accounts': [acct], 'posts': [post], 'gallery': [], 'summary': []}


class SocialModuleTests(unittest.TestCase):
    def test_window_is_fixed_at_ninety_days(self):
        self.assertEqual(social.WINDOW, {'start': '2026-07-25', 'end': '2026-10-22', 'tz': 'America/Toronto', 'days': 90})
        self.assertEqual(social.window_text(), '25 July to 22 October 2026, Toronto time (90 days)')
        self.assertIsNone(social.load_reviewed())   # in review: approval not recorded
        m = social.load_module()
        self.assertEqual((m['status'], m['approved']), ('review', None))

    def test_good_fixture_passes(self):
        self.assertEqual(social.check(_fixture()), [])

    def test_rules(self):
        def errs(mut):
            s = _fixture(); mut(s); return ' | '.join(social.check(s))
        self.assertIn('window must be exactly', errs(lambda s: s['window'].update(start='2026-07-24')))
        self.assertIn('out of scope', errs(lambda s: s['accounts'][0].update(channel='x')))
        self.assertIn('Instagram only', errs(lambda s: s['accounts'][0].update(channel='linkedin')))
        self.assertIn('outside 2026-07-25 to 2026-10-22', errs(lambda s: s['posts'][0].update(published_on='2026-10-23')))
        self.assertIn('watched', errs(lambda s: s['posts'][0].update(format='video')))
        self.assertIn('every slide', errs(lambda s: s['posts'][0].update(format='carousel')))
        self.assertIn('metric views missing', errs(lambda s: s['posts'][0]['metrics'].pop('views')))
        self.assertIn('credential-like', errs(lambda s: s['posts'][0].update(capture_ref='sessionid=abc123def456')))
        self.assertIn('credential-like', errs(lambda s: s['posts'][0].update(hook='Authorization: Bearer abcdefghijklmnopqrstuvwxyz0123')))
        self.assertIn('credential-like', errs(lambda s: s['posts'][0].update(hook='libfile_' + '0123456789abcdef01')))
        self.assertIn('reposts cannot be dated', errs(lambda s: s['posts'][0].update(relation='repost')))
        self.assertIn('displayed abbreviation', errs(lambda s: s['posts'][0]['metrics'].update(likes='about 11k')))
        self.assertIn('unverified', errs(lambda s: s['accounts'][0].update(verified=False)))
        self.assertIn('logged in', errs(lambda s: s['accounts'][0].update(logged_in=None)))
        self.assertIn('checked_at', errs(lambda s: s['accounts'][0].update(checked_at=None)))
        self.assertIn('past the window start', errs(lambda s: s['accounts'][0].update(earliest_reached='2026-08-01')))
        self.assertIn('no post count', errs(lambda s: s['accounts'][0].update(coverage='blocked')))
        self.assertIn('owner approval', errs(lambda s: s.update(status='reviewed')))
        self.assertIn('complete inventory', errs(lambda s: (s['accounts'][0].update(coverage='partial'), s['summary'].append({'text': 't', 'frequency': 2}))))

    def test_ordinary_words_are_not_credentials(self):
        for text in ('stayed way past the last session', 'cookie jar', 'a token of thanks', 'password reset help article', 'Bearer of good news'):
            self.assertEqual(social.secret_findings(text), [], text)
        for text in ('sessionid=8a7f6e5d4c3b', 'Cookie: csrftoken=abc', 'eyJhbGciOiJIUzI1.eyJzdWIiOiIxMjM0NTY.SflKxwRJSMeKKF2QT4fw', 'https://drive.google.com/file/d/abc/view',
                     'api_key=abcdef123456', 'x?_vercel_share=abcdefgh1234'):
            self.assertTrue(social.secret_findings(text), text)

    def test_instagram_view_sits_after_messaging_for_review(self):
        c = build.Ctx()
        body = build.body(c)
        self.assertEqual([v for _, v in build.view_order(c)], ['bs-overview', 'bs-compare', 'bs-messaging', 'bs-social', 'bs-journeys', 'bs-lessons'])
        self.assertIn('<a href="#bs-social" id="bs-tab-social">Instagram content</a>', body)
        self.assertIn('<b>Instagram posts</b> published 25 July to 22 October 2026; collected 26 October 2026', body)
        self.assertIn('<b>Websites observed</b> 23 October 2026', body)
        sec = body[body.index('<section id="bs-social"'):body.index('<section id="bs-journeys"')]
        self.assertIn('For editorial review', sec)
        self.assertIn('The captured Venn website footer linked to @tryvault, while this study uses owner-confirmed @venn.ca with supporting profile evidence.', sec)
        self.assertEqual(sec.count('No in-window posts found in the reviewed'), 3)
        self.assertNotRegex(sec, r'(?i)\binactive\b')
        self.assertEqual(sec.count(social.VIDEO_LABEL), 3)   # S1, S2 and S3 are reels (S4 is a carousel)
        self.assertIn('Attribution unresolved', sec)
        self.assertNotIn('ramp-ig-', sec)                       # no Ramp example while attribution is unresolved

    def test_release_is_blocked_until_approval(self):
        c = build.Ctx()
        c.mode = 'release'
        self.assertTrue(any('editorial review only' in e for e in validate.check_inputs(c)))
        c.mode = 'draft'
        self.assertFalse(any('editorial review only' in e for e in validate.check_inputs(c)))
        self.assertTrue(social.release_gate({'status': 'review'}))
        self.assertEqual(social.release_gate({'status': 'reviewed', 'approved': 'by hand'}), [])

    def test_derived_records(self):
        s = json.load(open(social.PATH, encoding='utf-8'))
        self.assertEqual(s['status'], 'review')
        self.assertIsNone(s['approved'])
        self.assertEqual({a['platform']: a['posts_in_window'] for a in s['accounts']}, {'venn': 9, 'float': 0, 'ramp': 19, 'loop': 0, 'keep': 0, 'airwallex': 23})
        self.assertEqual(s['totals']['formats'], {'video': 33, 'carousel': 10, 'image': 8})
        self.assertEqual(s['totals']['inspection'], {'carousel/all_slides': 9, 'carousel/partial': 1, 'image/cover_and_caption': 8, 'video/partial': 33})
        self.assertEqual(s['totals']['partially_inspected'], 34)
        ramp = next(a for a in s['accounts'] if a['platform'] == 'ramp')
        awx = next(a for a in s['accounts'] if a['platform'] == 'airwallex')
        self.assertEqual((ramp['relations'], ramp['collaborations']['published_by_collaborator'], ramp['collaborations']['published_with_coauthor']), ({'original': 4, 'collaboration': 15}, 13, 2))
        self.assertEqual(awx['relations'], {'original': 18, 'collaboration': 5})
        self.assertEqual(ramp['attribution']['status'], 'unresolved')
        self.assertEqual(s['collection']['post_records']['from'], '2026-10-26T21:45:38-04:00')
        self.assertEqual(len({p['url'] for p in s['posts']}), 51)
        for p in s['posts']:
            self.assertNotIn('Caption as seen', p['inspected'])     # exact captions stay private
            if p['metrics']['views'] is not None:
                self.assertTrue(p['metrics']['views_captured_at'] and p['metrics']['views_source'])
        self.assertEqual(next(p for p in s['posts'] if p['id'] == 'ramp-ig-DeLBKE-hlOg')['caption_restoration']['restored'], 'session')
        self.assertEqual(next(p for p in s['posts'] if p['id'] == 'airwallex-ig-DeR-myVkbUa')['metrics']['comments'], None)
        self.assertEqual(next(p for p in s['posts'] if p['id'] == 'ramp-ig-DexOf5RysxI')['metrics']['likes'], '11.1K')

    def test_narrative_rules(self):
        s = json.load(open(social.PATH, encoding='utf-8'))
        n = social.load_narrative()
        self.assertEqual(social.check_narrative(s, n, model.ROOT), [])
        import copy

        def errs(mut):
            m = copy.deepcopy(n); mut(m); return ' | '.join(social.check_narrative(s, m, model.ROOT))
        self.assertIn('attribution is unresolved', errs(lambda m: m['examples'][0].update(post='ramp-ig-DehBhI9G1w1')))
        self.assertIn('partly inspected carousel', errs(lambda m: m['examples'][0].update(post='ramp-ig-DcRk2HjEpvT')))
        self.assertIn('two or three sentences', errs(lambda m: m['examples'][0].update(take='One sentence only?')))
        self.assertIn('text excerpt', errs(lambda m: m['examples'][0].pop('no_image_reason')))
        self.assertIn('not a claim', errs(lambda m: m['examples'][0].update(reading='This was the best performing post.')))
        self.assertIn('recorded hash', errs(lambda m: m['examples'][2]['image'].update(sha256='0' * 64)))
        self.assertIn('Instagram content', errs(lambda m: m['view'].update(title='Social content')))
        # a reel read from cover and caption cannot carry a claim about the whole post
        self.assertIn('overstates', errs(lambda m: m['examples'][2].update(reading='A reader cannot tell from the post where the card is offered.')))
        self.assertIn('overstates', errs(lambda m: m['examples'][2].update(reading='The post names no market. Second sentence.')))

    def test_editorial_pass_2026_10_27(self):
        n = social.load_narrative()
        ex = {e['id']: e for e in n['examples']}
        web = social._editorial_text(ex['S1']['website'])
        self.assertIn('Those are October terms', web)
        self.assertIn('Whether any plan limit applied on 30 July 2026', web)
        self.assertIn('was not established', ex['S1']['reading'])          # the date limit sits beside the analysis
        self.assertNotIn('the plan limit the pricing page sets', ex['S1']['reading'])
        self.assertIn('The video was not watched', social._editorial_text(ex['S3']['shows']))
        self.assertIn('caption or cover', ex['S3']['reading'])
        s = social.load_module()
        self.assertEqual((s['totals']['attributed_posts'], s['totals']['unresolved_records']), (32, 19))
        self.assertEqual(social.attributed_count(s), 32)
        rows = list(csv.reader(io.StringIO(social.render_csv(s))))
        pa = rows[0].index('provider_attribution')
        self.assertEqual(sum(1 for r in rows[1:] if r[pa] == 'unresolved provider attribution'), 19)
        self.assertTrue(all(r[pa] == 'unresolved provider attribution' for r in rows[1:] if r[0] == 'Ramp'))
        ed = json.load(open(os.path.join(KIT, 'edition.json'), encoding='utf-8'))
        self.assertEqual(ed['relationship_disclosure']['status'], 'complete')   # confirmed by the owner, not an open question
        self.assertNotIn('relationship disclosure', open(os.path.join(KIT, 'SOCIAL_INGEST_NOTE.md'), encoding='utf-8').read().split('## Still needed before release')[1].lower())

    def test_instagram_csv(self):
        s = social.load_module()
        rows = list(csv.reader(io.StringIO(social.render_csv(s))))
        self.assertEqual(rows[0], social.CSV_HEAD)
        self.assertEqual(len(rows) - 1, 51)
        self.assertFalse(any(v[:1] in '=+-@' for r in rows[1:] for v in r if v))
        with open(os.path.join(model.ROOT, social.CSV_REL), encoding='utf-8') as f:
            self.assertEqual(f.read(), social.render_csv(s))

    def test_template_package_is_refused_until_filled(self):
        tpl = os.path.join(KIT, 'social_package_template')
        s, errs = social.package_to_module(tpl)
        self.assertTrue(any('logged in' in e for e in errs))
        self.assertEqual(len(s['accounts']), 6)
        self.assertEqual({x['channel'] for x in s['accounts']}, {'instagram'})   # LinkedIn out of scope (owner, 26 October 2026)
        self.assertTrue(all(a['verified'] is False for a in s['accounts']))   # nothing pre-verified
        self.assertEqual(s['posts'], [])

    def test_filled_package_checks_and_ingests_as_draft(self):
        d = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(d, 'screenshots'))
            accts = []
            for pl in social.PLATFORMS:
                for ch in social.CHANNELS:
                    accts.append({'platform': pl, 'channel': ch, 'handle': None, 'url': None, 'verified': False, 'verification': 'fixture',
                                  'scope': 'unclear', 'logged_in': False, 'checked_at': '2026-11-01T09:50:00-04:00', 'coverage': 'no_account', 'coverage_note': 'fixture',
                                  'earliest_reached': None, 'posts_in_window': None})
            a = _fixture()['accounts'][0]
            accts = [x for x in accts if (x['platform'], x['channel']) != ('loop', 'instagram')] + [a]
            post = _fixture()['posts'][0]
            post['capture_ref'] = 'loop-ig-1.png'
            man = [{'platform': 'loop', 'channel': 'instagram', 'role': 'social-account', 'account': 'example_handle', 'url': 'https://example.invalid/x',
                    'captured_at': '2026-11-01T10:00:00-04:00', 'logged_in': False, 'screenshot': 'loop-ig-profile.png', 'sanitised': True, 'sanitisation_note': 'fixture'},
                   {'platform': 'loop', 'channel': 'instagram', 'role': 'social-post', 'account': 'example_handle', 'url': post['url'],
                    'captured_at': '2026-11-01T10:01:00-04:00', 'logged_in': False, 'screenshot': 'loop-ig-1.png', 'sanitised': True, 'sanitisation_note': 'fixture',
                    'published_on': post['published_on']}]
            for m in man:
                with open(os.path.join(d, 'screenshots', m['screenshot']), 'wb') as f:
                    f.write(b'fixture')
            with open(os.path.join(d, 'accounts.json'), 'w') as f:
                json.dump(accts, f)
            with open(os.path.join(d, 'posts.json'), 'w') as f:
                json.dump([post], f)
            with open(os.path.join(d, 'manifest-social.jsonl'), 'w') as f:
                f.write('\n'.join(json.dumps(m) for m in man))
            s, errs = social.package_to_module(d)
            self.assertEqual(errs, [])
            self.assertEqual(s['status'], 'draft')
            self.assertEqual(len(s['screenshots']), 2)
            out = os.path.join(d, 'social.json')
            old, social.PATH = social.PATH, out
            try:
                self.assertEqual(social.main(['social.py', 'ingest', d]), 0)
                social.PATH = out
                self.assertIsNone(social.load_reviewed())        # a draft adds no view
            finally:
                social.PATH = old
            os.remove(os.path.join(d, 'screenshots', 'loop-ig-1.png'))
            self.assertTrue(any('capture_ref' in e or 'not in screenshots' in e for e in social.package_to_module(d)[1]))
        finally:
            shutil.rmtree(d)


if __name__ == '__main__':
    unittest.main()

