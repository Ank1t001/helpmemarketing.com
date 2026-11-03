"""Run from the kit folder: python3 -m unittest tests.test_kit"""
import csv
import html
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


PRE_RELEASE = '6e643b3'   # the reviewed staging commit the owner approved on 27 October 2026 (before release.py --apply)


def pre_release(rel):
    """A repository file as it was before the release was applied (the input of release.new_hub and new_sitemap)."""
    out = subprocess.run(['git', 'show', '%s:%s' % (PRE_RELEASE, rel)], cwd=model.ROOT, capture_output=True, text=True)
    if out.returncode:
        raise unittest.SkipTest('pre-release commit %s not available in this clone' % PRE_RELEASE)
    return out.stdout


def released(c):
    return c.edition['status'] == 'published'


# Hub edits made after the edition 001 release by hand, outside this kit (founder, 2026-11-02: the cards go two by two
# and the deck no longer says "Each is free to read, with no sign-up", since the case study gates some tabs; the Real
# Estate and Hair Loss cards use their own card artwork in the Med Spa pattern).
HUB_LATER_EDITS = [
    ('<dl class="ix-dates"><div><dt>Last updated</dt><dd>October 13, 2026</dd></div>',
     '<dl class="ix-dates"><div><dt>Last updated</dt><dd>November 3, 2026</dd></div>'),
    ('<p class="wk-tool-who">Five Canadian private real estate investment firms, ranked on public Instagram likes, comments and recorded plays.</p>',
     '<p class="wk-tool-who">Five Canadian private real estate investment firms compared on Instagram, Meta ads and their websites, with four ranked on public Instagram engagement.</p>'),
    ('<p class="section-deck">Pick the one closest to your business. Each is free to read, with no sign-up.</p>\n    <div class="wk-tools-grid">',
     '<p class="section-deck">Pick the one closest to your business.</p>\n    <div class="wk-tools-grid ix-grid">'),
    ('<img src="/assets/index/real-estate/hero.webp" alt="" width="1056" height="591" loading="lazy" decoding="async">',
     '<img src="/assets/index/real-estate/card.webp" srcset="/assets/index/real-estate/card-704.webp 704w, /assets/index/real-estate/card.webp 1056w" sizes="(max-width: 900px) calc(100vw - 40px), 576px" alt="" width="1056" height="591" loading="lazy" decoding="async">'),
    ('<img src="/assets/index/hair-loss/hero.webp" alt="" width="1056" height="591" loading="lazy" decoding="async">',
     '<img src="/assets/index/hair-loss/card.webp" srcset="/assets/index/hair-loss/card-704.webp 704w, /assets/index/hair-loss/card.webp 1056w" sizes="(max-width: 900px) calc(100vw - 40px), 576px" alt="" width="1056" height="591" loading="lazy" decoding="async">'),
    ('{"@type":"WebPage","name":"The Real Estate Index: Instagram","description":"Five Canadian private real estate investment firms, ranked on public Instagram likes, comments and recorded plays."',
     '{"@type":"WebPage","name":"How Canadian Real Estate Investment Firms Market to Investors","description":"Five Canadian private real estate investment firms compared on Instagram, Meta ads and their websites, with four ranked on public Instagram engagement."'),
]


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
        for label in ('Limits and approvals', 'Receipts and expenses', 'Accounting connections'):
            self.assertIn(label, body)
        # limits and approvals share one column (2026-10-30); each cell still cites both kinds of evidence
        for pid in self.c.order:
            cats_in_cell = {self.c.obs[i]['category'] for i in self.c.n['compare']['rows'][pid]['controls']['ids']}
            self.assertEqual(cats_in_cell, {'spend_controls', 'approvals'}, pid)
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

    def test_gate_checks_catch_a_missing_part(self):
        body = self.page[self.page.index('REPORT BODY START'):]
        self.assertEqual(validate.check_gate(self.c, self.page, body), [])
        broken = self.page.replace('"cssSelector":".bs-gated"', '"cssSelector":".x"')
        self.assertTrue(any('JSON-LD' in e for e in validate.check_gate(self.c, broken, body)))
        nocard = re.sub(r'</div><div class="bs-gate-card[^"]*" data-gate-card>.*?</div>', '</div>', body, count=1)
        self.assertTrue(any('unlock card' in e for e in validate.check_gate(self.c, self.page, nocard)))

    def test_release_dry_run_renders_without_touching_the_repo(self):
        import release
        before = {f: open(os.path.join(model.ROOT, f), encoding='utf-8').read() for f in ('hmm-index.html', 'sitemap.xml', 'business-spend-index.html')}
        c, gate, live, snap, csvtext, errs = release.render_all('2026-10-23', strict=False)
        self.assertEqual(errs, [])
        self.assertEqual(csvtext, self.csv)
        # The live page carries the email-code gate (2026-11-02); the fixed snapshot never does. Without the gate markup they match.
        self.assertNotIn('class="bs-gated"', snap)
        self.assertIn('class="bs-gated"', live)
        ungated = re.sub(r'<div class="bs-gated"[^>]*>', '', re.sub(r'</div><div class="bs-gate-card[^"]*" data-gate-card>.*?</div>', '', live))
        ungated = re.sub(r'<dialog class="bs-gate".*?</dialog>\n?', '', ungated, flags=re.S)
        self.assertEqual(ungated[ungated.index('REPORT BODY START'):], snap[snap.index('REPORT BODY START'):])
        self.assertIn('content="index, follow', live)
        self.assertIn('<meta name="robots" content="noindex, follow">', snap)
        self.assertIn('href="https://helpmemarketing.com/business-spend-index/edition-001"', snap)
        self.assertNotIn('datePublished', live + snap)
        if self.c.edition['status'] == 'draft':
            self.assertTrue(any('approvals' in g for g in gate))  # the gate stays closed until the owner records it
        src = {f: (pre_release(f) if released(self.c) else before[f]) for f in ('hmm-index.html', 'sitemap.xml')}
        hub, hi = release.new_hub(src['hmm-index.html'], '2026-10-23')
        sm, si = release.new_sitemap(src['sitemap.xml'], '2026-10-23')
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
        pos = [body.index('<section id="%s" class="bs-view"' % v) for v in ('bs-overview', 'bs-messaging', 'bs-compare', 'bs-social', 'bs-paid', 'bs-journeys', 'bs-lessons')]
        self.assertEqual(pos, sorted(pos))
        self.assertEqual(body.count('class="note reading"'), 6)  # six provider evidence expanders (the journey reading went with the 2026-10-31 rebuild)
        self.assertEqual(body.count('<article class="bs-lesson"'), 6)   # one card per brand since 2026-11-01; the three test designs stay in Sources
        self.assertEqual(body.count('<dt>Testable hypothesis</dt>'), 3)
        self.assertEqual(body.count('What this means for your marketing team'), 1)  # the reading-guide entry only (2026-10-30, final: no takeaway boxes)
        self.assertIn('id="bs-journey-table"', body)
        self.assertNotIn('Next step observed', body)

    def test_paid_ads_tab(self):
        # Founder request (2026-10-30): Meta Ad Library, Canada, active ads, collected 30 October 2026.
        import paid
        body = self.page[self.page.index('REPORT BODY START'):]
        tab = validate.view_html(body, 'bs-paid')
        d = self.c.paid
        self.assertIn('<a href="#bs-paid" id="bs-tab-paid">Paid Social</a>', body)
        self.assertEqual(len(d['records']), 119)
        self.assertEqual({p: sum(1 for r in d['records'] if r['platform'] == p) for p in self.c.order}, {'venn': 20, 'float': 11, 'ramp': 47, 'loop': 17, 'keep': 0, 'airwallex': 24})
        ref = validate.view_html(body, 'bs-sources')
        self.assertIn('No active ads in Canada when collected', ref)       # the ad-text reading moved to Sources & evidence (2026-10-31)
        self.assertIn('no spend, impressions or reach', ref)
        # Creative review (founder brief, 2026-10-31): distinct reviewed creatives, percentages from counts, three subsections.
        cr = d['creatives']['creatives']
        heads = [x for x in cr if not x['same_as']]
        self.assertEqual(len(cr), 175)
        self.assertEqual({p: len(paid.sample(d, p)) for p in self.c.order}, {'venn': 12, 'float': 5, 'ramp': 35, 'loop': 14, 'keep': 0, 'airwallex': 21})
        self.assertEqual(len(heads), 87)
        self.assertEqual(re.findall(r'<h3><span class="soc-n">\d</span>([^<]+)</h3>', tab), ['Creative mix by brand', 'Audience and buying stage', 'Selected creative examples'])
        self.assertIn('Personas and buying stages are inferred from the creative, not confirmed campaign targeting.', tab)
        self.assertIn('Product-focused <b>79% &middot; 11 of 14 creatives</b>', tab)    # Loop focus, computed from counts
        self.assertIn('Not compared: Keep had no active ads in Canada when the library was checked.', tab)
        self.assertNotIn('Percentages show the share', tab)
        self.assertEqual(re.findall(r'<div class="bs-stat"><dt>([^<]+)</dt><dd>([^<]+)</dd>', tab), [('Meta ads', '119'), ('Distinct creatives', '87'), ('Brands advertising', '5 of 6'), ('Started within 30 days', '102')])
        self.assertEqual(len(re.findall(r'<article class="pd-ex', tab)), 8)
        self.assertEqual(tab.count('<details class="pd-more">'), 1)
        self.assertNotIn('Keep</b>', tab)                                       # no percentages for a brand with no creatives
        for dim in ('focus', 'format', 'stage'):
            for p in ('venn', 'float', 'ramp', 'loop', 'airwallex'):
                self.assertEqual(sum(paid.counts(paid.sample(d, p), dim).values()), len(paid.sample(d, p)))
        self.assertEqual(validate.check_paid_creatives(self.c, body), [])
        self.assertNotRegex(tab, r'(?i)\bperform(s|ed)? (best|better)|winning ad|engagement rate')
        self.assertEqual(sum(1 for r in d['records'] if r['days_running'] <= 30), 102)
        self.assertEqual(sum(1 for r in d['records'] if r['platform'] == 'ramp' and 'lp2/industry/nonprofits' in r['landing']), 12)
        rows = list(csv.reader(io.StringIO(paid.render_csv(d))))
        self.assertEqual(len(rows) - 1, 119)
        self.assertNotIn('snapshot', open(paid.DATA, encoding='utf-8').read())   # derived records only, no raw fields

    def test_case_study_title_and_social_analysis(self):
        # Founder brief (2026-10-30, case study): title, metadata, Social Media Strategy computed from the recorded counts.
        body = self.page[self.page.index('REPORT BODY START'):]
        t = 'How Six Business Finance Brands Market Their Products'
        self.assertIn('<h1>%s</h1><p class="bs-subtitle">A marketing case study</p>' % t, body)
        self.assertIn('<title>%s</title>' % t, self.page)
        self.assertIn('<meta property="og:title" content="%s">' % t, self.page)
        self.assertIn('"headline":"%s"' % t, self.page)
        self.assertIn('<p class="kicker">The HMM Index</p>', body)
        s = self.c.social
        self.assertEqual(social.metric('1.5K'), (None, 'approximate'))
        self.assertEqual(social.metric(None), (None, 'missing'))
        self.assertEqual(social.metric(0), (0, 'exact'))
        a = {r['theme']: r for r in social.engagement(s, 'airwallex')}
        self.assertEqual((a['partnership']['posts'], a['partnership']['usable'], a['partnership']['median'], a['partnership']['median_solo']), (7, 6, 237, 75))
        self.assertEqual((a['company_events']['usable'], a['company_events']['median']), (6, 50))
        v = {r['theme']: r for r in social.engagement(s, 'venn')}
        self.assertEqual((v['customer_story']['posts'], v['customer_story']['median']), (6, 4))
        self.assertEqual(sum(r['posts'] for r in social.engagement(s, 'airwallex')), 23)
        self.assertEqual(sum(r['posts'] for r in social.engagement(s, 'venn')), 9)
        rows = list(csv.reader(io.StringIO(social.render_analysis_csv(s))))
        self.assertEqual(len(rows) - 1, 51)                        # Ramp counts on the owner's confirmation (1 November 2026)
        self.assertEqual(sum(1 for r in rows[1:] if r[1] == 'Ramp'), 19)
        self.assertEqual(sum(r['posts'] for r in social.engagement(s, 'ramp')), 19)
        for col in ('focus', 'creative_approaches', 'personas', 'likely_stage', 'account_attribution'):
            self.assertTrue(all(r[rows[0].index(col)] for r in rows[1:]), col)
        approx = [r for r in rows[1:] if r[rows[0].index('interactions_state')] == 'approximate']
        self.assertEqual(len(approx), 15)                          # 2 Airwallex, 13 Ramp (abbreviated counts such as 244.9K)
        self.assertTrue(all(r[rows[0].index('likes_plus_comments')] == '' for r in approx))
        for r in rows[1:]:
            if r[rows[0].index('format')] == 'video':
                # every attributed reel carries its 1 November 2026 frame review
                self.assertEqual(r[rows[0].index('approach_inspected')], 'yes')
                self.assertEqual(r[rows[0].index('video_reviewed_on')], '2026-11-01')
                self.assertGreaterEqual(int(r[rows[0].index('video_frames_reviewed')]), 12)
            else:
                self.assertEqual(r[rows[0].index('video_reviewed_on')], '')

    def test_reel_execution_needs_a_frame_review(self):
        import copy
        m = social.load_module()
        self.assertEqual(social.check_analysis(m), [])
        reels = [c for c in m['analysis']['posts'] if c.get('video_review')]
        self.assertEqual(len(reels), 33)                          # 21 Venn and Airwallex reels, 12 Ramp reels
        self.assertTrue(all(c['approach_inspected'] and ':' in c['approach'] for c in reels))
        bad = copy.deepcopy(m)
        bad['analysis']['posts'][[c['post'] for c in bad['analysis']['posts']].index(reels[0]['post'])].pop('video_review')
        self.assertIn('no recorded frame review', ' '.join(social.check_analysis(bad)))
        bad = copy.deepcopy(m)
        bad['analysis']['posts'][[c['post'] for c in bad['analysis']['posts']].index(reels[0]['post'])]['video_review']['frames_reviewed'] = 3
        self.assertIn('no recorded frame review', ' '.join(social.check_analysis(bad)))
        raw = json.dumps(m['analysis'])
        self.assertNotIn('cdninstagram', raw)
        self.assertNotIn('fbcdn', raw)

    def test_analysis_rules_on_synthetic_posts(self):
        # Synthetic fixture only, never published: medians ignore missing and abbreviated counts.
        s = {'analysis': {'guide': {'themes': [['t', 'T', ''], ['u', 'U', '']]}, 'posts': [
            {'post': 'a', 'theme': 't'}, {'post': 'b', 'theme': 't'}, {'post': 'c', 'theme': 't'}, {'post': 'd', 'theme': 'u'}]},
             'posts': [{'id': 'a', 'platform': 'x', 'relation': 'original', 'metrics': {'likes': 10, 'comments': 0}},
                       {'id': 'b', 'platform': 'x', 'relation': 'collaboration', 'metrics': {'likes': '2.1K', 'comments': 5}},
                       {'id': 'c', 'platform': 'x', 'relation': 'original', 'metrics': {'likes': 4, 'comments': None}},
                       {'id': 'd', 'platform': 'x', 'relation': 'original', 'metrics': {'likes': 1, 'comments': 1}}]}
        r = {x['theme']: x for x in social.engagement(s, 'x')}
        self.assertEqual((r['t']['posts'], r['t']['usable'], r['t']['median'], r['t']['collab']), (3, 1, 10, 1))
        self.assertEqual(r['u']['median'], 2)

    def test_final_layout_tabs_and_sources(self):
        # Founder brief (2026-10-30, final): plain tabs, one Sources & evidence view holding the research trail.
        body = self.page[self.page.index('REPORT BODY START'):]
        ov, so, pa, msg, cmp_, jr, ls = (validate.view_html(body, v) for v in ('bs-overview', 'bs-social', 'bs-paid', 'bs-messaging', 'bs-compare', 'bs-journeys', 'bs-lessons'))
        ref = validate.view_html(body, 'bs-sources')
        self.assertIn('<h2 id="bs-overview-h">Inside this case study</h2>', ov)
        self.assertEqual(re.findall(r'<a class="bs-gcard" href="#(bs-[a-z]+)"', ov), ['bs-messaging', 'bs-compare', 'bs-social', 'bs-paid', 'bs-journeys', 'bs-lessons'])
        self.assertNotIn('class="find"', ov)
        # Overview, second look (founder, 2026-11-02): signature panel, open and gated groups, Recommendations featured last.
        self.assertIn('<div class="bs-ovhero"><div class="sec-head"><h2 id="bs-overview-h">', ov)
        self.assertIn('<em>side by side</em>', ov)
        self.assertIn('<p class="bs-ovlabel">Open to everyone</p>', ov)
        self.assertIn('Full case study<span class="bs-ovlock">', ov)
        self.assertEqual(re.findall(r'href="#(bs-[a-z]+)" data-feature', ov), ['bs-lessons'])
        # Overview refinement (founder brief, 2026-10-31): no intro paragraph or provider list, the six blocks with the agreed copy.
        self.assertNotIn('bs-provs', ov)
        self.assertNotIn(self.c.n['views']['overview']['dek'], ov)
        self.assertEqual(re.findall(r'<span class="bs-gt">([^<]+)</span>', ov), ['Website Messaging', 'Product Comparison', 'Organic Social', 'Paid Social', 'Sign-up Journey', 'Recommendations'])
        self.assertEqual(re.findall(r'<span class="bs-gd">([^<]+)</span>', ov), [
            'How brands explain their value and support their claims.',
            'Cards, rewards, fees and key conditions.',
            'The content brands post on Instagram, who it speaks to and the response it receives.',
            'The creative approaches brands use, who they speak to and their likely buying stages.',
            'How brands guide customers from their first click to getting started.',
            'One or two ideas for each brand to test.'])
        self.assertIn('<h2 id="bs-paid-h">Paid Social</h2>', pa)
        self.assertNotIn('Social Media Paid Ads Strategy', body)
        self.assertNotIn('</div></nav><p class="bs-srcrow">', body)
        self.assertLess(body.index('id="bs-srclink"'), body.index('<section id="bs-sources"'))
        self.assertGreater(body.index('id="bs-srclink"'), body.index('<section id="bs-lessons"'))
        self.assertEqual(body.count('id="bs-srclink"'), 1)
        self.assertNotIn('bs-ov-scope', ov)                    # the note under the cards was removed (founder, 2026-10-31)
        self.assertNotIn('Independent marketing research', body)            # byline line removed (founder, 2026-11-01)
        self.assertRegex(body.split('</header>')[0], r'<span class="bs-meta-date">Last Updated [A-Z][a-z]{2} \d{1,2}, \d{4}</span>')  # the date never wraps
        with open(os.path.join(KIT, 'page_head.html'), encoding='utf-8') as f:
            self.assertIn('.msi.msi .ri-nav.bs-views{margin-top:0;top:92px}', f.read())   # sticky tabs clear the site header
        self.assertNotIn('About this case study.', body)                    # footer box removed (founder, 2026-11-01)
        src = body.split('id="bs-ref-author"')[1]
        self.assertIn('it is not a ranking, a product test or a recommendation', src)
        self.assertIn('Company names are used to report their public pages and posts and imply no relationship with Help Me Marketing.', src)
        # Founder brief (2026-10-31, second): one five-column comparison for all six brands, then three visual examples.
        self.assertNotIn('Website observations: 23 October 2026', msg)
        self.assertIn('A look at how brands explain their value, build trust and encourage customers to take the next step.', msg)
        # Brand message cards since 2026-11-02 (founder): the same four criteria for every brand.
        self.assertEqual(re.findall(r'<dt>([^<]+)</dt>', msg[msg.index('class="bs-msgcards"'):])[:4], ['Main promise', 'Who it speaks to', 'Why choose them?', 'Proof used'])
        self.assertEqual(msg.count('<dt>Proof used</dt>'), 6)
        self.assertEqual(re.findall(r'<article class="bs-msgc" id="bs-msg-([a-z]+)">', msg), list(self.c.order))
        self.assertEqual(msg.count('<p class="bs-msgc-flag">'), 4)   # Venn, Float, Loop and Keep name the figure without a stated basis
        self.assertEqual(re.findall(r'<h3[^>]*><span class="soc-n">\d</span>([^<]+)</h3>', msg), ['Messaging at a glance', 'Messaging in practice'])
        self.assertEqual(re.findall(r'<p class="soc-tags">([^&]+?) &middot;', msg), ['Value proposition', 'Proof', 'Call to action'])
        self.assertEqual(len(re.findall(r'<figure class="bs-wex-shot"><a class="bs-zoom"[^>]*><img src="/assets/index/business-spend/web/', msg)), 3)
        self.assertEqual(msg.count('captured 31 October 2026'), 3)
        self.assertEqual(msg.count('<a class="bs-zoom" href="/assets/index/business-spend/web/'), 3)    # click to enlarge (2026-10-31)
        self.assertIn('The outcomes in the case study are provider-reported, not independently verified.', msg)
        self.assertNotIn('described, not measured', msg)
        self.assertNotIn('<div class="card ex">', msg)
        self.assertNotRegex(msg.replace('credit score', ''), r'(?i)best website|\b(?:scored?|ranked|rating)\b|\d+ ?/ ?10|winning')   # "credit score" is quoted site wording
        ref = validate.view_html(body, 'bs-sources')
        for need in ('id="bs-msg-glance-ev"', 'id="bs-msg-captures"', 'id="bs-msg-support-ev"'):
            self.assertIn(need, ref)
        self.assertNotRegex(body, r'(?i)capture request|\bR[12]\b|after booking|is booked')
        fu = ref[ref.index('id="bs-p-airwallex"'):]
        self.assertIn('checked 30 October 2026', fu[:fu.index('</details>')])
        # Product Comparison (founder, 2026-10-31, refinement brief): one comparison, three categories behind a switch, no at-a-glance table.
        self.assertEqual(re.findall(r'<h3[^>]*><span class="soc-n">\d</span>([^<]+)</h3>', cmp_), ['Compare by category'])
        self.assertEqual(re.findall(r'<button type="button" class="pd-opt bs-copt" data-cat="([a-z]+)" aria-pressed="(true|false)"', cmp_), [('cards', 'true'), ('fees', 'false'), ('tools', 'false')])
        self.assertEqual(re.findall(r'class="bs-cpanel" id="bs-cpanel-([a-z]+)"', cmp_), ['cards', 'fees', 'tools'])
        heads = lambda tid: re.findall(r'<th scope="col">([^<]+)</th>', cmp_[cmp_.index('id="%s"' % tid):cmp_.index('</thead>', cmp_.index('id="%s"' % tid))])
        self.assertEqual(heads('bs-prod'), ['Brand', 'Card funding / repayment', 'Rewards and key condition', 'Plan costs'])
        self.assertEqual(heads('bs-xb'), ['Brand', 'Card spending', 'Currency conversion'])
        self.assertEqual(heads('bs-spend'), ['Brand', 'Limits and approvals', 'Receipts and expenses', 'Accounting connections'])
        for tid in ('bs-prod', 'bs-xb', 'bs-spend'):
            self.assertEqual(len(re.findall(r'<tr id="%s-[a-z]+">' % tid, cmp_)), 6)
        for gone in ('bs-cmp-glance', 'bs-glance-', 'data-brand=', 'bs-cmp-sel', 'At a glance', 'Current eligibility needs confirmation'):
            self.assertNotIn(gone, cmp_)
        self.assertIn('Fees apply to different transactions and conditions; these are not like-for-like total costs.', cmp_)
        self.assertIn('Observed 23 October 2026. Later rechecks are noted in the row they change.', cmp_)
        self.assertEqual(cmp_.count('<b>Follow-up, 30 October 2026:</b>'), 1)          # named once, on Airwallex's note line
        # Since 2026-11-02 (founder) each brand is its own tbody, its notes on a full-width line under the row; the brand cell holds only the name.
        self.assertEqual(cmp_.count('<tbody class="bs-cgroup">'), 3 * len(self.c.order))
        self.assertNotRegex(cmp_, r'<td class="brandcell">[^<]+<span')
        for tid in ('bs-prod', 'bs-xb', 'bs-spend'):                                    # no links inside the comparison cells
            seg = cmp_[cmp_.index('id="%s"' % tid):]
            self.assertNotIn('<a ', seg[seg.index('<tbody'):seg.index('</table>')])
        self.assertIn('Rechecked 31 October 2026: the Canadian pricing page lists a corporate liability charge card with credit limits; repayment terms are not published there.', cmp_)
        self.assertIn('Eligibility not confirmed at the follow-up', cmp_)
        self.assertIn('Rechecked 31 October 2026: the Canadian pages mention rewards but publish no rate.', cmp_)
        self.assertIn('and again on 31 October 2026', cmp_)
        self.assertNotRegex(cmp_, r'<td class="miss"[^>]*><span class="cell-main">')
        self.assertEqual(cmp_.count('<span class="st st-not_checked">Not checked</span>'), 1)              # Ramp funding
        self.assertEqual(cmp_.count('<span class="st st-not_found">Not found in reviewed sources</span>'), 2)   # Ramp rewards and FX conversion
        self.assertIn('id="bs-recheck-RMP-RECHECK-2026-10-31"', ref)
        self.assertIn('<h2 id="bs-journeys-h">Sign-up Journey</h2>', jr)
        # Founder brief (2026-10-31, second): four stages, one labelled comparison, two help-page examples.
        self.assertIn('A look at how brands guide customers from their first click to getting started.', jr)
        self.assertEqual(re.findall(r'<h3[^>]*><span class="soc-n">\d</span>([^<]+)</h3>', jr), ['Journey overview', 'How the brands compare', 'Journey examples'])
        self.assertEqual(re.findall(r'<span class="bs-st">([^<]+)</span>', jr), ['Start', 'Provide details', 'Verification and decision', 'First use'])
        self.assertIn('aria-label="Four journey stages"', jr)
        self.assertNotRegex(jr, r'(?i)six stages|five stages|keeps using')
        self.assertIn('Routes vary by product. Account approval and card approval may be separate.', jr)
        self.assertEqual(re.findall(r'<th scope="col">([^<]+)</th>', jr), ['Brand', 'Entry routes', 'What to prepare', 'Review and waiting', 'Getting started'])
        self.assertEqual(len(re.findall(r'<tr id="bs-jt-row-[a-z]+">', jr)), 6)
        self.assertIn('<p class="soc-lim">First screens were observed directly. Later steps come from public guidance; timing estimates are not guarantees.</p>', jr)
        self.assertNotIn('Website FAQ', jr)
        row = lambda pid: jr[jr.index('<tr id="bs-jt-row-%s">' % pid):jr.index('</tr>', jr.index('<tr id="bs-jt-row-%s">' % pid))]
        self.assertIn('separate card application', row('loop'))
        self.assertNotIn('demo-only', row('float'))
        self.assertIn('direct application', row('float'))
        self.assertIn('Interac e-Transfer', row('float'))
        self.assertEqual(row('float').count('bs-src-none'), 1)        # only the verification documents stay unconfirmed
        self.assertEqual(row('airwallex').count('Canadian applicability not confirmed'), 2)
        self.assertIn('closed-applications page on 23 October and again on 31 October', row('keep'))
        self.assertIn('Not confirmed', row('airwallex'))
        self.assertIn('under 10 minutes to sign up, then asks applicants to allow up to 24 hours', row('venn'))
        self.assertEqual(re.findall(r'<p class="soc-tags">([^&]+?) &middot; ([^<]+?) <span', jr), [('Venn', 'Guidance while waiting'), ('Loop', 'Account approval versus card approval')])
        self.assertEqual(jr.count('<a class="bs-zoom" href="/assets/index/business-spend/web/'), 2)
        self.assertEqual(jr.count('help centre, captured 31 October 2026.'), 2)
        for gone in ('bs-js-', 'bs-jpick', 'bs-jlegend', 'cashback', 'QuickBooks', 'NetSuite', 'interest', 'fastest', 'easiest', 'best onboarding', 'lowest friction', 'O-VEN', 'J-VEN'):
            self.assertNotIn(gone, jr)
        self.assertEqual(body.count('<dialog class="bs-lightbox"'), 1)
        self.assertNotIn('<dialog', msg + jr)          # one shared dialog outside the tab panels
        for need in ('id="bs-journey-followup"', 'id="bs-journey-coverage"', 'id="bs-journey-captures"', 'id="jf-J-FLT-3"', 'Not readable from this review', 'id="bs-float-access"', 'id="bs-journey-dates"', 'id="jf-J-FLT-7"'):
            self.assertIn(need, ref)
        self.assertIn('href="#bs-t3">See the recommendations for each brand', jr)
        for pid in self.c.order:
            self.assertIn('id="bs-jt-%s"' % pid, ref)
        self.assertIn('id="bs-e3"', ref)
        self.assertEqual(re.findall(r'<h3 class="bs-ttitle">([^<]+)<span class="bs-lcount">', ls), ['Venn', 'Float', 'Ramp', 'Loop', 'Keep', 'Airwallex'])
        self.assertEqual(re.findall(r'<dt>([^<]+)</dt>', ls[ls.index('class="bs-lessons"'):]), ['What I saw', 'Recommendation'] * 12)
        self.assertEqual(ls.count('<li class="bs-opp">'), 12)
        self.assertIn('<a href="#bs-lessons" id="bs-tab-lessons">Recommendations</a>', body)
        self.assertEqual(re.findall(r'<div class="bs-stat"><dt>([^<]+)</dt><dd>([^<]+)</dd>', ls), [('Recommendations', '12'), ('Claims and conditions', '6'), ('Sign-up journeys', '3'), ('Social and ad content', '3')])
        self.assertIn('One or two recommendations for each brand, drawn from the evidence in this case study.', ls)
        self.assertEqual(ls.count('not proven improvements'), 1)
        for card, anchors in (('venn', ('bs-t1', 'bs-f1')), ('ramp', ('bs-t3', 'bs-f3')), ('keep', ('bs-t2', 'bs-f2'))):
            seg = ls[ls.index('id="bs-lesson-%s"' % card):]
            seg = seg[:seg.index('</article>')]
            for a in anchors:
                self.assertIn('id="%s"' % a, seg)
        for f in ('bs-f1', 'bs-f2', 'bs-f3', 'bs-t1', 'bs-t2', 'bs-t3'):
            self.assertIn('id="%s"' % f, ls)
        self.assertIn('id="bs-f1-detail"', ref)
        self.assertIn('directional reading only', ref)
        self.assertIn('<a class="bs-srclink" href="#bs-sources" id="bs-srclink">Sources &amp; evidence</a>', body)
        self.assertIn('data-bs-back', ref)
        for v in (ov, so, pa, msg, cmp_, jr, ls):
            self.assertNotRegex(v, r'\bO-[A-Z]{3}-\d\d\b|id="ev-|What the sources say|<details(?! class="(?:pd-more|bs-more soc-detail)")')

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
        for k in ('overview', 'social', 'paid', 'messaging', 'compare', 'journeys', 'lessons'):
            self.assertIn('<a href="#bs-%s" id="bs-tab-%s">' % (k, k), nav)
        self.assertEqual(re.findall(r'id="bs-tab-([a-z]+)"', nav), ['overview', 'messaging', 'compare', 'social', 'paid', 'journeys', 'lessons'])
        self.assertNotIn('role="tab', body)                  # roles come from the script: without it the page is a plain reading order
        self.assertNotRegex(body, r'<section id="bs-[a-z]+" class="bs-view"[^>]* hidden')
        self.assertEqual(body.count('<p class="bs-next">'), 7)
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
            li = body[body.index('<div class="bs-tspec" id="bs-%s-spec">' % t['id'].lower()):]
            li = li[:li.index('</dl>')]
            dts = [x for x in __import__('re').findall(r'<dt>([^<]+)</dt>', li)]
            self.assertEqual(dts, ['Observed evidence', 'Customer question', 'My interpretation', 'Testable hypothesis', 'One change',
                                   'What stays comparable', 'Primary measurement', 'Guardrail', 'When the result would be inconclusive'])
            self.assertTrue(t['evidence'])
        for f in self.c.n['findings']['items']:
            blk = body[body.index('<div class="bs-fdetail" id="bs-%s-detail">' % f['id'].lower()):]
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
        # restrictions stay visible beside the provider; the full eligibility details sit in the expander (2026-10-30)
        body = self.page[self.page.index('id="bs-prod-h"'):]
        body = body[:body.index('</table>')]
        self.assertIn('<b>Restriction:</b> Self-serve sign-up closed to new applicants when checked', body)
        self.assertIn('<b>Restriction:</b> Not offered to businesses in Quebec', body)
        self.assertIn('<b>Credit:</b> Float Charge credit is subject to eligibility criteria', body)
        det = self.page[self.page.index('id="bs-cards"'):]
        det = det[:det.index('</table>')]
        self.assertIn('Eligibility details', det)
        self.assertIn('Self-serve sign-up route closed to new applicants when checked', det)
        self.assertIn('availability in other countries is not assessed', self.page)

    def test_hub_wording_and_card_artwork(self):
        import release
        current = open(os.path.join(model.ROOT, 'hmm-index.html'), encoding='utf-8').read()
        hub = pre_release('hmm-index.html') if released(self.c) else current
        new, issues = release.new_hub(hub, '2026-10-23')
        self.assertEqual(issues, [])
        if released(self.c):
            # The card's Last updated follows the latest recorded production deployment (RELEASE_STEPS step 12), in Toronto time.
            expected = release.new_hub(hub, (self.c.edition.get('modified_at') or self.c.edition['published_at'])[:10])[0]
            for was, now in HUB_LATER_EDITS:  # hub edits made after the release, outside this kit
                self.assertEqual(expected.count(was), 1, was)
                expected = expected.replace(was, now)
            self.assertEqual(current, expected)
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
        log = log[:log.index('<details class="bs-refsec"')]
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
        m = social.load_module()
        if m['status'] == 'review':
            self.assertIsNone(social.load_reviewed())   # in review: approval not recorded
            self.assertIsNone(m['approved'])
        else:
            self.assertEqual(social.load_reviewed()['status'], 'reviewed')   # approved by hand on 27 October 2026

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

    def test_tab_order_and_labels(self):
        c = build.Ctx()
        body = build.body(c)
        self.assertEqual([v for _, v in build.view_order(c)], ['bs-overview', 'bs-messaging', 'bs-compare', 'bs-social', 'bs-paid', 'bs-journeys', 'bs-lessons'])
        self.assertIn('<a href="#bs-social" id="bs-tab-social">Organic Social</a>', body)
        self.assertIn('A look at how brands present themselves on Instagram, the content they create and the engagement it receives.', body)
        self.assertIn('Official company Instagram accounts only, posts published 25 July to 22 October 2026', body)
        self.assertNotIn('<b>Instagram posts</b>', body.split('</header>')[0])  # dates live in Scope & sources, not the hero (2026-10-28)
        self.assertIn('Websites observed 23 October 2026, 10:39 a.m. to 2:33 p.m. Toronto time.', body)
        tab = validate.view_html(body, 'bs-social')
        sec = tab + validate.view_html(body, 'bs-sources')
        self.assertEqual('For editorial review' in tab, c.social['status'] == 'review')   # the flag shows only while approval is pending
        self.assertIn('The captured Venn website footer linked to @tryvault, while this study uses owner-confirmed @venn.ca with supporting profile evidence.', sec)
        self.assertEqual(sec.count('No in-window posts found in the reviewed'), 3 + 3 + 3 + 3)   # in Sources & evidence: accounts table, positioning, product positioning, coverage assessment
        self.assertNotRegex(sec, r'(?i)\binactive\b')
        self.assertGreaterEqual(sec.count('Cover and caption reviewed 26 October 2026. Video reviewed 1 November 2026 as'), 3)   # the offer examples' reel records carry both reviews
        # Founder (2026-11-01): the format of Paid Social Strategy, Ramp included on the owner's confirmation.
        self.assertEqual(re.findall(r'<h3><span class="soc-n">\d</span>([^<]+)</h3>', tab), ['Creative mix by brand', 'Audience and buying stage', 'Selected examples', 'Engagement by theme'])
        self.assertNotIn('Not assessed', tab)
        self.assertNotIn('What this suggests', tab)
        self.assertEqual(len(re.findall(r'<article class="pd-ex has-img" id="bs-sx', tab)), 6)
        self.assertEqual(tab.count('<details class="bs-more soc-detail"><summary>More detail</summary><p>'), 4)
        self.assertNotIn('soc-detail" open', tab)
        for dim in ('focus', 'format', 'approach', 'theme', 'persona', 'stage'):
            self.assertIn('id="bs-social-dim-%s"' % dim, tab)
        self.assertEqual([m for m in re.findall(r'<p class="pd-brand"><b>(\w+)</b>', tab)][:3], ['Venn', 'Ramp', 'Airwallex'])
        self.assertIn('Not compared: no posts found on the reviewed Float, Loop and Keep accounts during the research window (latest posts 5 June 2026, 11 June 2026 and 17 July 2024).', html.unescape(tab))
        self.assertNotIn('on the study owner', html.unescape(tab))
        self.assertNotIn('Percentages show the share', tab)
        self.assertEqual(re.findall(r'<div class="bs-stat"><dt>([^<]+)</dt><dd>([^<]+)</dd>', tab), [('Posts reviewed', '51'), ('Brands with posts found', '3 of 6'), ('Reels', '33'), ('Collaborations', '20')])
        self.assertIn('Based on visible likes and comments. Small samples are directional and do not establish sales performance.', tab)
        self.assertIn('Window and coverage', sec)
        self.assertIn('Owner-confirmed, 1 November 2026', sec)
        self.assertNotIn('Attribution unresolved', sec)

    def test_release_is_blocked_until_approval(self):
        c = build.Ctx()
        c.social = dict(c.social, status='review', approved=None)   # as it stood before the owner's approval
        c.mode = 'release'
        self.assertTrue(any('editorial review only' in e for e in validate.check_inputs(c)))
        c.mode = 'draft'
        self.assertFalse(any('editorial review only' in e for e in validate.check_inputs(c)))
        c2 = build.Ctx()
        if c2.social['status'] == 'reviewed':
            self.assertTrue(c2.social['approved'].startswith('2026-10-27: owner instruction'))   # recorded by hand, never generated
            self.assertEqual(social.release_gate(c2.social), [])
        self.assertTrue(social.release_gate({'status': 'review'}))
        self.assertEqual(social.release_gate({'status': 'reviewed', 'approved': 'by hand'}), [])

    def test_derived_records(self):
        s = json.load(open(social.PATH, encoding='utf-8'))
        self.assertIn(s['status'], ('review', 'reviewed'))
        self.assertEqual(bool(s['approved']), s['status'] == 'reviewed')
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
        self.assertIn('Organic Social', errs(lambda m: m['view'].update(title='Social content')))
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
        self.assertIn('Frames reviewed on 1 November 2026', social._editorial_text(ex['S3']['shows']))
        self.assertIn('audio not heard', ex['S3']['reading'])
        self.assertIn('caption, the cover or the on-screen text', ex['S3']['reading'])
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

