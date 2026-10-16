"""Tests for the Dental Implant Marketing Index kit. Run from the kit folder: python3 -m unittest tests.test_build"""
import copy, json, re, sys, unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build as B

ED = "001"
KIT = Path(__file__).resolve().parent.parent
REPO = KIT.parent.parent

def rec(K, rid):
    for a, x in K["ads"]["checks"].items():
        for plat in ("meta", "google"):
            for r in x[plat]["records"]:
                if r["id"] == rid: return r
    raise KeyError(rid)

def post(K, sc):
    return next(p for p in K["social"]["posts"] if p["shortcode"] == sc)

class Window(unittest.TestCase):
    def test_last_30_complete_days(self):
        w = B.window_last_30(datetime(2026, 10, 16, 14, 14, tzinfo=B.TZ))
        self.assertEqual((str(w[0]), str(w[1])), ("2026-09-16", "2026-10-15"))
        self.assertEqual((w[1] - w[0]).days + 1, 30)

    def test_window_uses_toronto_date_not_utc(self):
        # 03:30 UTC on 1 November is still 31 October in Toronto
        w = B.window_last_30(B.toronto("2026-11-01T03:30:00Z"))
        self.assertEqual(str(w[1]), "2026-10-30")

    def test_after_daylight_time_ends(self):
        w = B.window_last_30(datetime(2026, 11, 2, 0, 30, tzinfo=B.TZ))
        self.assertEqual((str(w[0]), str(w[1])), ("2026-10-03", "2026-11-01"))

    def test_post_timestamps_compared_in_toronto(self):
        w = B.window_last_30(datetime(2026, 10, 16, 12, 0, tzinfo=B.TZ))
        self.assertTrue(B.in_window("2026-10-16T03:59:00Z", w))   # 15 October, 11:59 p.m. Toronto
        self.assertFalse(B.in_window("2026-10-16T04:01:00Z", w))  # 16 October, collection day
        self.assertFalse(B.in_window("2026-09-16T03:59:00Z", w))  # 15 September in Toronto

class Posts(unittest.TestCase):
    W = B.window_last_30(datetime(2026, 10, 16, 12, 0, tzinfo=B.TZ))
    H = {"studiobdental"}

    def test_cleaning(self):
        posts = [
            {"shortcode": "a1", "timestamp": "2026-10-01T15:00:00Z", "owner": "studiobdental", "likes": 10, "comments": 1},
            {"shortcode": "a1", "timestamp": "2026-10-01T15:00:00Z", "owner": "studiobdental", "likes": 10},
            {"error": "not_found", "shortcode": "zz", "timestamp": "2026-10-02T15:00:00Z"},
            {"shortcode": "old", "timestamp": "2026-06-01T15:00:00Z", "owner": "studiobdental", "pinned": True},
            {"shortcode": "c1", "timestamp": "2026-10-03T15:00:00Z", "owner": "partner_account", "requested_handle": "studiobdental", "likes": 5},
            {"shortcode": "h1", "timestamp": "2026-10-04T15:00:00Z", "owner": "studiobdental", "likes": -1, "comments": None},
        ]
        own, collab, rep = B.clean_posts(copy.deepcopy(posts), self.H, self.W)
        self.assertEqual([p["shortcode"] for p in own], ["a1", "h1"])
        self.assertEqual([p["shortcode"] for p in collab], ["c1"])
        self.assertEqual((rep["duplicates"], rep["errors"], rep["outside_window"], rep["pinned_outside"]), (1, 1, 1, 1))
        hidden = next(p for p in own if p["shortcode"] == "h1")
        self.assertIsNone(hidden["likes"])      # hidden likes stay missing, never zero
        self.assertIsNone(hidden["comments"])

class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.K0 = B.load(ED)

    def setUp(self):
        self.K = copy.deepcopy(self.K0)

    def fails(self, K, target="draft"):
        with self.assertRaises(B.BuildError):
            B.validate(K, target)

    def page(self, K=None):
        K = K or self.K; O = B.validate(K, "draft"); page, used = B.render(K, O, "draft")
        B.check_page(page, True, used, O, ED, K)
        return page

class Edition(Base):
    def test_committed_edition_validates(self):
        O = B.validate(self.K, "draft")
        self.assertEqual(len({o["clinic"] for o in O.values()}), 3)

    def test_five_clinic_identities(self):
        K = copy.deepcopy(self.K); K["cohort"]["clinics"] = K["cohort"]["clinics"][:4]; self.fails(K)
        K = copy.deepcopy(self.K); K["cohort"]["clinics"][1]["name"] = "Smile By Design"; self.fails(K)

    def test_excerpt_must_be_in_saved_page(self):
        self.K["obs"][0]["excerpt"] = "an address that is not on the page"; self.fails(self.K)

    def test_source_must_be_official_domain(self):
        o = next(x for x in self.K["obs"] if x["clinic"] == "nysc"); o["clinic"] = "studiob"; self.fails(self.K)

    def test_figures_must_come_from_cited_sources(self):
        self.K["nar"]["findings"][0]["text"] += " One clinic charges $9,999."; self.fails(self.K)

    def test_ad_figure_must_be_in_the_cited_ad(self):
        K = copy.deepcopy(self.K); K["nar"]["accounts"]["studiob"]["price_note"]["rows"][1]["wording"] += " Also $18,990."; self.fails(K)
        K = copy.deepcopy(self.K)  # the website row cannot borrow the ad's figure
        K["nar"]["accounts"]["studiob"]["price_note"]["rows"][0]["wording"] += " $17,990."; self.fails(K)

    def test_exactly_three_tests(self):
        K = copy.deepcopy(self.K); K["nar"]["tests"].append(copy.deepcopy(K["nar"]["tests"][0])); self.fails(K)
        K = copy.deepcopy(self.K); K["nar"]["tests"].pop(); self.fails(K)

    def test_tests_carry_no_invented_numbers(self):
        self.K["nar"]["tests"][0]["measure"] += " Target a 20% lift."; self.fails(self.K)

    def test_takeaways_required(self):
        K = copy.deepcopy(self.K); K["nar"]["accounts"]["studiob"]["takeaway"] = ""; self.fails(K)
        K = copy.deepcopy(self.K); K["nar"]["patterns"][0]["takeaway"] = "Generic advice."; self.fails(K)

    def test_unverified_handle_stays_missing(self):
        self.K["social"]["handles"]["dundas"]["handle"] = "dundaseastdental"; self.fails(self.K)

    def test_voice_rules(self):
        K = copy.deepcopy(self.K); K["nar"]["summary"] += " We reviewed every clinic."; self.fails(K)
        K = copy.deepcopy(self.K); K["nar"]["summary"] += " A clear — dash."; self.fails(K)

    def test_draft_page(self):
        page = self.page()
        self.assertIn('<meta name="robots" content="noindex, nofollow">', page)
        self.assertNotIn('"datePublished"', page)
        self.assertNotIn('href="/dental-index/edition-001"', page)
        self.assertIn('<link rel="canonical" href="https://helpmemarketing.com/dental-index">', page)
        N = self.K["nar"]
        self.assertEqual(page.count("What this means for your clinic"), len(N["findings"]) + 5 + len(N["patterns"]))
        self.assertIn("16 September 2026 to 15 October 2026", page)
        self.assertIn('dental-index-edition-001-ads.csv">the 45 ad library records', page)
        self.assertIn('dental-index-edition-001-instagram.csv">the 9 observed Instagram posts', page)
        for blk in re.findall(r'<script type="application/ld\+json">\n(.*?)\n</script>', page, re.S):
            self.assertIn(json.loads(blk)["@type"], ("BreadcrumbList", "Article"))
        self.assertEqual(page.count('data-review-cta="research_dental"'), 2)

    def test_inline_style_rejected(self):
        O = B.validate(self.K, "draft"); page, used = B.render(self.K, O, "draft")
        with self.assertRaises(B.BuildError):
            B.check_page(page.replace('<h3>1. ', '<h3 style="color:red">1. ', 1), True, used, O, ED, self.K)

class FixedWindow(Base):
    def test_window_comes_from_edition_json(self):
        self.assertEqual(B.edition_window(self.K["edition"]), (B.date(2026, 9, 16), B.date(2026, 10, 15)))

    def test_later_collection_does_not_move_the_window(self):
        self.K["social"]["collection_started_utc"] = "2026-11-20T15:00:00Z"
        self.assertIn("Observation window</b> 16 September 2026 to 15 October 2026", self.page())

    def test_window_must_be_thirty_days(self):
        self.K["edition"]["window"]["end"] = "2026-10-16"; self.fails(self.K)

    def test_window_cannot_be_moved_past_the_evidence(self):
        # moving the window forward puts every collection inside it, which the build refuses
        self.K["edition"]["window"].update(start="2026-09-17", end="2026-10-16"); self.fails(self.K)

    def test_post_outside_the_window_rejected(self):
        post(self.K, "DdbhpOgIMJE")["published_utc"] = "2026-09-16T03:00:00Z"; self.fails(self.K)  # 15 September in Toronto

class Advertising(Base):
    def test_historical_ad_cannot_be_shown_as_in_window(self):
        rec(self.K, "google-CR06173431441167220737")["window_relation"] = "shown_in_window"; self.fails(self.K)

    def test_historical_ads_are_labelled_historical(self):
        page = self.page()
        table = page.split('id="dx-ads"')[1].split('id="dx-accounts"')[0]
        rows = [r for r in table.split("<tr>") if "CR06173431441167220737" in r]
        self.assertEqual(len(rows), 1); row = rows[0].split("</tr>")[0]
        self.assertIn("Historical", row); self.assertNotIn("Active when observed", row)

    def test_meta_window_relation_follows_dates(self):
        rec(self.K, "meta-26002231369395543")["window_relation"] = "active_at_observation_started_in_window"; self.fails(self.K)

    def test_group_ads_not_attributed_to_the_clinic(self):
        K = copy.deepcopy(self.K); rec(K, "google-CR03812698612471693313")["attribution"]["confidence"] = "supported"; self.fails(K)  # domain-only creative
        K = copy.deepcopy(self.K); rec(K, "google-CR07943027236351770625")["attribution"]["confidence"] = "confirmed"; self.fails(K)  # identity unresolved
        K = copy.deepcopy(self.K); K["ads"]["checks"]["bond"]["google"]["status"] = "relevant_ads_observed"; self.fails(K)

    def test_bond_counts_split_by_creative_evidence(self):
        recs = self.K["ads"]["checks"]["bond"]["google"]["records"]
        self.assertEqual(len(recs), 26)
        self.assertEqual(sum(r["attribution"]["confidence"] == "supported" for r in recs), 12)
        self.assertEqual(sum(r["treatment"]["implant_related"] == "yes" for r in recs), 3)

    def test_implant_relevance_follows_treatment(self):
        rec(self.K, "meta-2023758354972864")["treatment"]["implant_related"] = "yes"; self.fails(self.K)  # Invisalign ad

    def test_unrelated_ads_not_counted_as_implant(self):
        page = self.page()
        self.assertIn("7 ad cards, 0 about implants; 7 active or shown in the window; 1 not attributable to the clinic", page)  # NYSC Meta: Invisalign, plus My Smile Centre
        self.assertIn("2 ad cards, 0 about implants", page)       # Gajjar Meta: general dentistry (election notice excluded)

    def test_no_match_needs_an_empty_search(self):
        self.K["ads"]["checks"]["studiob"]["google"]["status"] = "no_matching_ads_found"
        self.K["ads"]["checks"]["nysc"]["google"]["status"] = "no_matching_ads_found"; self.fails(self.K)

    def test_tampered_evidence_rejected(self):
        b = self.K["batches"]["browser-20261016"]; m = b["manifest"]["shots/meta-studiob-2.png"]; m["sha256_stored"] = "0" * 64
        self.fails(self.K)

class Social(Base):
    def test_partial_sample_is_labelled_and_never_complete(self):
        self.assertIn("incomplete sample", self.page())
        K = copy.deepcopy(self.K); K["social"]["status"] = "collected"; self.fails(K)

    def test_no_frequency_claims_from_a_partial_sample(self):
        K = copy.deepcopy(self.K); K["nar"]["accounts"]["nysc"]["observed"] += " It posts about implants three times a week."; self.fails(K)
        K = copy.deepcopy(self.K); K["nar"]["findings"][3]["text"] += " These were all of its posts in the window."; self.fails(K)

    def test_owner_must_be_the_verified_handle(self):
        post(self.K, "DdsKsuVM8b4")["owner"] = "drcharlesbotbol"; self.fails(self.K)

    def test_metrics_match_the_saved_post(self):
        post(self.K, "Dd9BwhfFG0x")["metrics"]["likes"] = 70; self.fails(self.K)

    def test_missing_metrics_stay_missing(self):
        K = copy.deepcopy(self.K); post(K, "Dd9BwhfFG0x")["metrics"]["plays"] = -1; self.fails(K)
        page = self.page()
        self.assertNotIn('data-label="Plays">0<', page)
        self.assertEqual(page.count('data-label="Plays">Not shown<'), 9)

    def test_missing_plays_are_not_a_release_blocker(self):
        rep = B.release_report(self.K)
        self.assertTrue(any("plays not shown" in x for x in rep["missing_optional_metrics"]))
        blockers = rep["core_evidence_gaps"] + rep["unreviewed_coverage_gaps"] + rep["checks_awaiting_execution"]
        self.assertFalse(any("plays" in x for x in blockers))

class Release(Base):
    def test_release_refused_while_evidence_missing(self):
        self.fails(self.K, "release")

    def test_release_report_categories(self):
        rep = B.release_report(self.K)
        self.assertIn("Dundas East Dental: official website not reviewed", rep["core_evidence_gaps"])
        self.assertIn("Bond Street Dental: Instagram handle not verified", rep["core_evidence_gaps"])
        self.assertTrue(any("Bond Street Dental: clinic identity" in x for x in rep["core_evidence_gaps"]))
        self.assertIn("Studio B Dental: Instagram coverage probable_not_confirmed", rep["unreviewed_coverage_gaps"])
        self.assertIn("Dr. Neil J. Gajjar Associates & Specialists: Instagram coverage blocked", rep["unreviewed_coverage_gaps"])
        self.assertIn("Dundas East Dental: meta documented search found no matching ads", rep["completed_searches_no_match"])
        self.assertTrue(any("forms script" in x for x in rep["checks_awaiting_execution"]))

    def test_reviewed_limitation_clears_only_its_gap(self):
        self.K["edition"]["reviewed_limitations"] = [{"clinic": "studiob", "gap": "instagram_coverage"}]
        rep = B.release_report(self.K)
        self.assertNotIn("Studio B Dental: Instagram coverage probable_not_confirmed", rep["unreviewed_coverage_gaps"])
        self.assertIn("North York Smile Centre: Instagram coverage probable_not_confirmed", rep["unreviewed_coverage_gaps"])

class DarkModeButton(unittest.TestCase):
    """The Index head rule .msi.msi a{color:var(--text-muted)} once turned the dark-theme hero button grey on orange."""
    head = (KIT / "head_dental.html").read_text()
    css = (REPO / "styles.css").read_text()

    @staticmethod
    def spec(sel):
        ids = len(re.findall(r"#[\w-]+", sel)); cls = len(re.findall(r"\.[\w-]+|\[[^\]]+\]|:(?!not)[\w-]+", sel))
        els = len(re.findall(r"(?:^|[\s>+~])([a-z][\w-]*)", sel)); return (ids, cls, els)

    def test_button_rule_present_and_outranks_the_link_rule(self):
        self.assertIn(".msi.msi a.btn-primary{color:var(--bg)}", self.head)
        self.assertGreater(self.spec(".msi.msi a.btn-primary"), self.spec(".msi.msi a"))
        # the light theme rule must still win over the fix
        self.assertGreater(self.spec('html:not([data-theme="dark"]) body.redesign-prototype .btn-primary'), self.spec(".msi.msi a.btn-primary"))

    def test_dark_button_colours_meet_aa(self):
        def hexval(name, scope):
            m = re.search(re.escape(scope) + r"\s*\{[^}]*?" + re.escape(name) + r":\s*(#[0-9A-Fa-f]{6})", self.css, re.S); return m[1]
        def lum(h):
            c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
            c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
            return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
        bg, cta = hexval("--bg", "body.redesign-prototype"), hexval("--cta", "body.redesign-prototype")
        a, b = sorted((lum(bg), lum(cta)), reverse=True)
        self.assertGreaterEqual((a + 0.05) / (b + 0.05), 4.5)

    def test_page_carries_the_fix(self):
        self.assertIn(".msi.msi a.btn-primary{color:var(--bg)}", (REPO / "dental-index.html").read_text())

if __name__ == "__main__":
    unittest.main()
