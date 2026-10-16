"""Tests for the Dental Implant Marketing Index kit. Run from the kit folder: python3 -m unittest tests.test_build"""
import copy, sys, unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build as B

ED = "001"

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

class Edition(unittest.TestCase):
    def setUp(self):
        self.K = B.load(ED)

    def fails(self, K, target="draft"):
        with self.assertRaises(B.BuildError):
            B.validate(K, target)

    def test_committed_edition_validates(self):
        O = B.validate(copy.deepcopy(self.K), "draft")
        self.assertEqual(len({o["clinic"] for o in O.values()}), 3)

    def test_five_clinic_identities(self):
        K = copy.deepcopy(self.K); K["cohort"]["clinics"] = K["cohort"]["clinics"][:4]; self.fails(K)
        K = copy.deepcopy(self.K); K["cohort"]["clinics"][1]["name"] = "Smile By Design"; self.fails(K)

    def test_excerpt_must_be_in_saved_page(self):
        K = copy.deepcopy(self.K); K["obs"][0]["excerpt"] = "an address that is not on the page"; self.fails(K)

    def test_source_must_be_official_domain(self):
        K = copy.deepcopy(self.K)
        o = next(x for x in K["obs"] if x["clinic"] == "nysc"); o["clinic"] = "studiob"; self.fails(K)

    def test_figures_must_come_from_cited_sources(self):
        K = copy.deepcopy(self.K); K["nar"]["findings"][0]["text"] += " One clinic charges $9,999."; self.fails(K)

    def test_exactly_three_tests(self):
        K = copy.deepcopy(self.K); K["nar"]["tests"].append(copy.deepcopy(K["nar"]["tests"][0])); self.fails(K)
        K = copy.deepcopy(self.K); K["nar"]["tests"].pop(); self.fails(K)

    def test_tests_carry_no_invented_numbers(self):
        K = copy.deepcopy(self.K); K["nar"]["tests"][0]["measure"] += " Target a 20% lift."; self.fails(K)

    def test_takeaways_required(self):
        K = copy.deepcopy(self.K); K["nar"]["accounts"]["studiob"]["takeaway"] = ""; self.fails(K)
        K = copy.deepcopy(self.K); K["nar"]["patterns"][0]["takeaway"] = "Generic advice."; self.fails(K)

    def test_unverified_handle_stays_missing(self):
        K = copy.deepcopy(self.K); K["social"]["handles"]["dundas"]["handle"] = "dundaseastdental"; self.fails(K)

    def test_no_posts_while_not_collected(self):
        K = copy.deepcopy(self.K); K["social"]["posts"] = [{"shortcode": "x"}]; self.fails(K)

    def test_voice_rules(self):
        K = copy.deepcopy(self.K); K["nar"]["summary"] += " We reviewed every clinic."; self.fails(K)
        K = copy.deepcopy(self.K); K["nar"]["summary"] += " A clear — dash."; self.fails(K)

    def test_release_refused_while_evidence_missing(self):
        self.fails(copy.deepcopy(self.K), "release")

    def test_draft_page(self):
        K = copy.deepcopy(self.K); O = B.validate(K, "draft")
        page, used = B.render(K, O, "draft")
        B.check_page(page, True, used, O, ED)
        self.assertIn('<meta name="robots" content="noindex, nofollow">', page)
        self.assertNotIn('"datePublished"', page)
        self.assertNotIn('href="/dental-index/edition-001"', page)
        self.assertIn('<link rel="canonical" href="https://helpmemarketing.com/dental-index">', page)
        self.assertEqual(page.count("What this means for your clinic"), 3 + 5 + 4)
        self.assertIn("16 September 2026 to 15 October 2026", page)
        self.assertIn(f"the {len(used)} website observations", page)

    def test_inline_style_rejected(self):
        K = copy.deepcopy(self.K); O = B.validate(K, "draft")
        page, used = B.render(K, O, "draft")
        with self.assertRaises(B.BuildError):
            B.check_page(page.replace('<h3>1. ', '<h3 style="color:red">1. ', 1), True, used, O, ED)

if __name__ == "__main__":
    unittest.main()
