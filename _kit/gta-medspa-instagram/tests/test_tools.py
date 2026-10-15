"""Offline tests for the roster builder and the Apify helpers. No network beyond a local mock server; no paid calls."""
import gzip, json, os, re, shutil, subprocess, sys, tempfile, threading, unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
PY = sys.executable


def run(args, env=None, cwd=None):
    e = dict(os.environ)
    e.pop("APIFY_TOKEN", None)
    e.update(env or {})
    return subprocess.run([PY] + args, capture_output=True, text=True, env=e, cwd=cwd, timeout=120)


def listing(pid, title, cat, city, ig=None, site=None, cats=None, lat=43.7, lng=-79.4, street=None, pc=None):
    return {"placeId": pid, "title": title, "categoryName": cat, "categories": cats or [cat], "city": city,
            "state": "Ontario", "street": street or f"{pid} Main St", "postalCode": pc or "L4C 1T9",
            "address": f"{street or pid + ' Main St'}, {city}, ON {pc or 'L4C 1T9'}, Canada",
            "location": {"lat": lat, "lng": lng}, "website": site, "instagrams": ig or [],
            "permanentlyClosed": False, "temporarilyClosed": False, "searchString": "medspa X, Ontario"}


def ig(h):
    return [f"https://www.instagram.com/{h}/"]


def synthetic():
    L = [
        listing("a1", "Glow Medspa", "Medical spa", "Toronto", ig("glowmedspa"), "https://glowmedspa.ca", pc="M5V 1A1"),
        listing("a2", "Oak Aesthetics", "Medical spa", "Oakville", ig("oakaesthetics"), "https://oakaesthetics.ca", pc="L6H 1A1"),
        listing("a3", "Pure Skin Clinic", "Skin care clinic", "Markham", ig("pureskinclinic"), "https://pureskin.ca"),
        listing("a4", "Luxe Hair Salon", "Hair salon", "Toronto", ig("luxehair"), pc="M5V 2A2"),
        listing("a5", "Barrie Med Spa", "Medical spa", "Barrie", ig("barriemedspa")),
        listing("a6", "Chain Laser Clinic Toronto", "Laser hair removal service", "Toronto", ig("chainlaser"), "https://chainlaser.ca", pc="M4W 1A1"),
        listing("a7", "Chain Laser Clinic Oakville", "Laser hair removal service", "Oakville", ig("chainlaser"), "https://chainlaser.ca", pc="L6H 2B2"),
        listing("a8", "Chain Laser Clinic Brampton", "Laser hair removal service", "Brampton", [], "https://chainlaser.ca", pc="L6W 1A1"),
        listing("a9", "Dermalyn Skin Clinic", "Medical spa", "Vaughan", ig("vagaropro"), "https://dermalyn.ca"),
        listing("b1", "Closed Medspa", "Medical spa", "Toronto", ig("closedmedspa"), pc="M5V 3A3"),
        listing("b2", "No Link Medspa", "Medical spa", "Ajax", [], "https://nolinkmedspa.ca"),
        listing("b3", "Fake Handle Clinic", "Medical spa", "Whitby", ig("appstore"), "https://fakehandle.ca"),
        listing("b4", "Massage Place", "Massage therapist", "Pickering", ig("massageplace")),
        listing("b5", "Halton Skin Lab", "Medical spa", None, ig("haltonskinlab"), "https://haltonskinlab.ca", lat=43.52, lng=-79.88),
    ]
    L[9]["permanentlyClosed"] = True
    L[13].update({"address": None, "street": None, "postalCode": None, "city": None})
    return L


class RosterBuild(unittest.TestCase):
    def setUp(self):
        self.t = Path(tempfile.mkdtemp())
        (self.t / "work").mkdir()
        (self.t / "work" / "listings.json").write_text(json.dumps(synthetic()))

    def tearDown(self):
        shutil.rmtree(self.t)

    def build(self, cap=600, seed=7):
        p = run([str(KIT / "roster_build.py"), "--edition", "009", "--root", str(self.t), "--cap", str(cap),
                 "--seed", str(seed), "--built-at", "2026-01-01", "--run-id", "mock"])
        self.assertEqual(p.returncode, 0, p.stderr)
        return p.stdout, json.loads((self.t / "editions/009/roster_eligible.json").read_text())["clinics"]

    def test_eligibility_geography_and_accounts(self):
        out, r = self.build()
        h = {c["handle"]: c for c in r}
        self.assertEqual(set(h), {"glowmedspa", "oakaesthetics", "pureskinclinic", "chainlaser", "haltonskinlab"})
        self.assertEqual(h["chainlaser"]["branches"], 3)  # shared account counted once; unlinked branch resolved by domain
        self.assertEqual(h["chainlaser"]["region"], "Multi-region")
        self.assertEqual(h["chainlaser"]["account_type"], "multi-location group")
        self.assertEqual(h["haltonskinlab"]["region"], "Halton")  # no address: coordinates, labelled approximate
        self.assertIn("coordinates (approximate)", h["haltonskinlab"]["geo_methods"])
        ex = json.loads((self.t / "editions/009/exclusions.json").read_text())
        why = " ".join(e["reason"] for e in ex)
        for needle in ("hair salon", "massage", "permanently closed", "outside the five"):
            self.assertIn(needle, why)
        unres = json.loads((self.t / "editions/009/roster_unresolved.json").read_text())
        self.assertEqual(sorted(u["title"] for u in unres), ["Fake Handle Clinic", "No Link Medspa"])  # a platform handle is not a clinic account
        self.assertEqual(unres[0]["status"], "account unresolved")
        unv = json.loads((self.t / "editions/009/roster_unverified.json").read_text())
        self.assertIn("vagaropro", {u["linked_handle"] for u in unv})
        self.assertNotIn("appstore", " ".join(json.dumps(c) for c in r))

    def test_compact_output(self):
        out, _ = self.build()
        self.assertLessEqual(len(out.splitlines()), 4)
        self.assertLess(len(out), 1200)

    def test_sampling_is_reproducible_and_proportional(self):
        extra = [listing(f"x{i}", f"Clinic {i} Medspa", "Medical spa", c, ig(f"clinicmedspa{i}x"), f"https://clinic{i}x.ca")
                 for i, c in enumerate(["Toronto"] * 12 + ["Mississauga"] * 8 + ["Markham"] * 8 + ["Oshawa"] * 4 + ["Oakville"] * 4)]
        (self.t / "work" / "listings.json").write_text(json.dumps(synthetic() + extra))
        _, r1 = self.build(cap=20, seed=11)
        s1 = json.loads((self.t / "editions/009/sampling.json").read_text())
        _, r2 = self.build(cap=20, seed=11)
        s2 = json.loads((self.t / "editions/009/sampling.json").read_text())
        self.assertTrue(s1["required"])
        self.assertEqual(s1["selected"], s2["selected"])
        self.assertEqual(s1["selected_count"], 20)
        self.assertEqual(sum(v["selected"] for v in s1["allocation"].values()), 20)
        self.assertIn("Multi-region", s1["allocation"])
        _, r3 = self.build(cap=20, seed=12)
        s3 = json.loads((self.t / "editions/009/sampling.json").read_text())
        self.assertNotEqual(s1["selected"], s3["selected"])  # the seed, nothing else, decides

    def test_saved_discovery_reproduces_committed_roster(self):
        src = KIT / "editions/002/discovery_listings.json.gz"
        if not src.exists():
            self.skipTest("no saved discovery data")
        (self.t / "work" / "listings.json").write_bytes(gzip.open(src).read())
        p = run([str(KIT / "roster_build.py"), "--edition", "002", "--root", str(self.t), "--seed", "20261015",
                 "--built-at", "2026-10-15", "--run-id", "9eUmdtGUOD6YBu17u"])
        self.assertEqual(p.returncode, 0, p.stderr)
        for f in ("sampling.json", "roster_eligible.json", "exclusions.json", "roster_unresolved.json"):
            self.assertEqual((self.t / "editions/002" / f).read_text(), (KIT / "editions/002" / f).read_text(), f)
        self.assertEqual((self.t / "roster.json").read_text(), (KIT / "roster.json").read_text())


class Mock(BaseHTTPRequestHandler):
    calls = []
    runs = {}
    def log_message(self, *a): pass
    def _send(self, code, obj, raw=None):
        b = raw if raw is not None else json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        Mock.calls.append(("GET", self.path, self.headers.get("Authorization")))
        if self.headers.get("Authorization") != "Bearer SECRET-TOKEN":
            return self._send(401, {"error": "bad token SECRET-TOKEN"})
        if self.path.startswith("/v2/actor-runs/"):
            rid = self.path.split("/")[3].split("?")[0]
            seq = Mock.runs[rid]
            st = seq.pop(0) if len(seq) > 1 else seq[0]
            return self._send(200, {"data": st})
        if self.path.startswith("/v2/datasets/"):
            q = dict(p.split("=") for p in self.path.split("?")[1].split("&"))
            off, lim = int(q["offset"]), int(q["limit"])
            return self._send(200, [{"i": i} for i in range(off, min(off + lim, 25))])
        self._send(404, {})
    def do_POST(self):
        Mock.calls.append(("POST", self.path, self.headers.get("Authorization")))
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        Mock.runs["newrun"] = [{"id": "newrun", "status": "READY", "defaultDatasetId": "d1"}]
        self._send(201, {"data": {"id": "newrun", "status": "READY", "defaultDatasetId": "d1", "echo": len(body.get("usernames", []))}})


class ApifyTool(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = HTTPServer(("127.0.0.1", 0), Mock)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.env = {"APIFY_API_BASE": f"http://127.0.0.1:{cls.srv.server_port}", "APIFY_TOKEN": "SECRET-TOKEN"}

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def setUp(self):
        self.t = Path(tempfile.mkdtemp())
        Mock.calls.clear()

    def tearDown(self):
        shutil.rmtree(self.t)

    def tool(self, *a, env=None):
        return run([str(KIT / "tools/apify_tool.py"), "--root", str(self.t)] + list(a), env=env if env is not None else self.env)

    def test_watch_success_compact_and_status_file(self):
        Mock.runs["r1"] = [{"id": "r1", "status": "RUNNING", "statusMessage": "x" * 400, "stats": {"runTimeSecs": 5},
                            "storages": {"datasets": {"default": {"id": "d1", "itemCount": 10, "fields": ["f"] * 500}}}},
                           {"id": "r1", "status": "RUNNING", "stats": {"runTimeSecs": 9}, "storages": {"datasets": {"default": {"id": "d1", "itemCount": 10}}}},
                           {"id": "r1", "status": "SUCCEEDED", "usageTotalUsd": 0.5, "stats": {"runTimeSecs": 12},
                            "storages": {"datasets": {"default": {"id": "d1", "itemCount": 30}}}}]
        p = self.tool("watch", "--run-id", "r1", "--interval", "0.05", "--max-interval", "0.1", "--timeout", "20")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(len(p.stdout.splitlines()), 2)  # unchanged state is not reprinted
        self.assertIn("SUCCEEDED | 30 items", p.stdout)
        self.assertNotIn("SECRET-TOKEN", p.stdout + p.stderr)
        st = json.loads((self.t / "work/status/r1.json").read_text())
        self.assertEqual(st["items"], 30)
        self.assertNotIn("SECRET-TOKEN", json.dumps(st))

    def test_watch_failure_is_actionable_and_timeout_bounded(self):
        Mock.runs["r2"] = [{"id": "r2", "status": "FAILED", "statusMessage": "out of memory", "storages": {"datasets": {"default": {"id": "d2", "itemCount": 7}}}}]
        p = self.tool("watch", "--run-id", "r2", "--interval", "0.05")
        self.assertEqual(p.returncode, 2)
        self.assertIn("ACTION", p.stdout); self.assertIn("d2", p.stdout)
        Mock.runs["r3"] = [{"id": "r3", "status": "RUNNING", "storages": {"datasets": {"default": {"id": "d3", "itemCount": 1}}}}]
        p = self.tool("watch", "--run-id", "r3", "--interval", "0.05", "--max-interval", "0.05", "--timeout", "0.3", "--stall-polls", "2")
        self.assertEqual(p.returncode, 2)
        self.assertIn("still RUNNING", p.stdout); self.assertIn("NOTE: no new items", p.stdout)

    def test_auth_errors_do_not_leak_token(self):
        p = self.tool("watch", "--run-id", "r1", env={**self.env, "APIFY_TOKEN": "WRONG"})
        self.assertNotEqual(p.returncode, 0)
        self.assertNotIn("WRONG", p.stdout + p.stderr); self.assertNotIn("SECRET-TOKEN", p.stdout + p.stderr)
        p = self.tool("watch", "--run-id", "r1", env={"APIFY_API_BASE": self.env["APIFY_API_BASE"]})
        self.assertIn("APIFY_TOKEN is not set", p.stderr)

    def test_status_from_saved_connector_reply(self):
        raw = self.t / "run.json"
        raw.write_text(json.dumps({"runId": "r9", "status": "SUCCEEDED", "statusMessage": "Finished", "startedAt": "a", "finishedAt": "b",
                                   "stats": {"runTimeSecs": 85.4, "computeUnits": 0.09},
                                   "storages": {"datasets": {"default": {"id": "d9", "itemCount": 600, "fields": ["f%d" % i for i in range(2000)]}}}}))
        p = self.tool("status", "--raw", str(raw), env={})
        self.assertEqual(p.returncode, 0)
        self.assertEqual(p.stdout.strip(), "r9 | SUCCEEDED | 600 items | 85s")
        raw.write_text(json.dumps({"runId": "r9", "status": "RUNNING", "storages": {"datasets": {"default": {"id": "d9", "itemCount": 5}}}}))
        p = self.tool("status", "--raw", str(raw), env={})
        self.assertEqual(p.returncode, 3); self.assertIn("NEXT: check again in 300s", p.stdout)

    def test_fetch_paged_resumable_and_verified(self):
        out = self.t / "d.json"
        p = self.tool("fetch", "--dataset", "d1", "--out", str(out), "--page", "10", "--total", "25")
        self.assertEqual(p.returncode, 0, p.stderr); self.assertIn("OK 25/25", p.stdout)
        self.assertEqual(len(json.loads(out.read_text())), 25)
        n = len(Mock.calls)
        p = self.tool("fetch", "--dataset", "d1", "--out", str(out), "--page", "10", "--total", "25")
        self.assertEqual(len(Mock.calls), n)  # resumed entirely from saved pages: no downloads repeated
        p = self.tool("fetch", "--dataset", "d1", "--out", str(self.t / "e.json"), "--page", "10", "--total", "30")
        self.assertEqual(p.returncode, 2); self.assertIn("INCOMPLETE 25/30", p.stdout)

    def test_start_reads_input_from_file_with_charge_cap(self):
        h = self.t / "h.json"; h.write_text(json.dumps({"selected": [f"h{i}" for i in range(600)]}))
        p = self.tool("build-input", "--kind", "profiles", "--handles", str(h), "--outdir", str(self.t / "in"))
        self.assertEqual(p.stdout.strip(), f"600 handles -> 1 input file(s) in {self.t / 'in'}")
        self.assertNotIn("h599", p.stdout)
        p = self.tool("build-input", "--kind", "posts", "--handles", str(h), "--outdir", str(self.t / "in"), "--since", "2026-07-17")
        self.assertIn("12 input file(s)", p.stdout)
        first = json.loads((self.t / "in/posts-01.input.json").read_text())
        self.assertEqual((len(first["directUrls"]), first["resultsLimit"], first["onlyPostsNewerThan"]), (50, 200, "2026-07-17"))
        p = self.tool("start", "--actor", "apify/instagram-profile-scraper", "--input", str(self.t / "in/profiles.input.json"), "--max-charge", "3")
        self.assertEqual(p.returncode, 0, p.stderr)
        post = [c for c in Mock.calls if c[0] == "POST"][0]
        self.assertIn("apify~instagram-profile-scraper/runs?maxTotalChargeUsd=3", post[1])
        self.assertNotIn("SECRET-TOKEN", p.stdout)


class Checkpoint(unittest.TestCase):
    def test_done_stale_pending_and_next(self):
        t = Path(tempfile.mkdtemp())
        try:
            (t / "editions/005").mkdir(parents=True)
            f = t / "editions/005/x.json"; f.write_text("1")
            c = lambda *a: run([str(KIT / "tools/checkpoint.py"), "--root", str(t)] + list(a))
            c("set", "--edition", "005", "--stage", "discovery_export", "--files", str(f), "--meta", "items=5")
            out = c("check", "--edition", "005").stdout
            self.assertRegex(out, r"discovery_export\s+done\s+items=5"); self.assertIn("NEXT: roster_validated", out)
            f.write_text("2")
            self.assertRegex(c("check", "--edition", "005").stdout, r"discovery_export\s+stale")
        finally:
            shutil.rmtree(t)


class UsageReport(unittest.TestCase):
    def test_stage_sums_equal_totals_and_dedupe(self):
        t = Path(tempfile.mkdtemp())
        try:
            u = lambda cr, cc, o: {"input_tokens": 1, "cache_read_input_tokens": cr, "cache_creation_input_tokens": cc, "output_tokens": o}
            rows = [{"type": "assistant", "timestamp": "2026-01-01T00:00:01Z", "message": {"id": "m1", "usage": u(10, 5, 1)}},
                    {"type": "assistant", "timestamp": "2026-01-01T00:00:01Z", "message": {"id": "m1", "usage": u(10, 5, 9)}},
                    {"type": "assistant", "timestamp": "2026-01-01T00:05:00Z", "message": {"id": "m2", "usage": u(20, 0, 4)}}]
            (t / "t.jsonl").write_text("\n".join(map(json.dumps, rows)))
            (t / "s.json").write_text(json.dumps({"stages": [{"label": "A", "from": "2026-01-01T00:00:00Z"}, {"label": "B", "from": "2026-01-01T00:02:00Z"}]}))
            p = run([str(KIT / "tools/usage_report.py"), str(t / "t.jsonl"), "--stages", str(t / "s.json"), "--out", str(t / "o.json")])
            self.assertEqual(p.returncode, 0, p.stderr)
            o = json.loads((t / "o.json").read_text())
            self.assertEqual(o["totals"]["calls"], 2); self.assertEqual(o["totals"]["output"], 13)
            self.assertEqual(o["stages"]["B"]["cache_read"], 20)
        finally:
            shutil.rmtree(t)


class Draft50(unittest.TestCase):
    def test_draft_reconciles_and_has_no_ranking(self):
        if not (KIT / "editions/002/source_posts_pilot.jsonl.gz").exists():
            self.skipTest("no saved pilot records")
        p = run([str(KIT / "build_50.py")])
        self.assertEqual(p.returncode, 0, p.stderr)
        f = json.loads((KIT / "editions/002/draft/draft_figures.json").read_text())
        self.assertEqual((f["selected"], f["classes"], f["rows_returned"], f["rows_in_window"], f["rows_outside_window"]),
                         (50, {"A": 12, "B": 36, "C": 1, "E": 1}, 824, 783, 41))
        h = (KIT / "editions/002/draft/medspa-index-draft.html").read_text()
        self.assertNotRegex(h, "[\u2014\u2013]")
        self.assertIn("<h1>Med Spa Index</h1>", h)
        self.assertIn('content="noindex, nofollow"', h)
        self.assertNotIn("FAQPage", h)
        self.assertNotRegex(h[h.index('<div class="msi">'):], r'\sstyle=')


class ReleaseFiles(unittest.TestCase):
    def test_live_page_snapshot_and_links(self):
        root = KIT.parent.parent
        live = (root / "medspa-index.html").read_text()
        self.assertFalse((root / "gta-medspa-index.html").exists())  # the old page file is gone; the redirect serves the old URL
        snap = (root / "gta-medspa-index/edition-002.html").read_text()
        e3 = json.loads((KIT / "editions/003/edition_003.json").read_text())
        live_robots = "index, follow" if e3["status"] == "published" else "noindex, nofollow"  # edition 003 stays noindex until its release build
        for h, canon, robots in ((live, "https://helpmemarketing.com/medspa-index", live_robots),
                                 (snap, "https://helpmemarketing.com/gta-medspa-index/edition-002", "noindex, follow")):
            self.assertNotRegex(h, "[\\u2014\\u2013]")
            self.assertEqual(h.count('name="robots"'), 1)
            self.assertIn(f'name="robots" content="{robots}', h)
            self.assertIn(f'rel="canonical" href="{canon}"', h)
            self.assertEqual("FAQPage" in h, h is live)  # edition 003 carries a visible FAQ; the 002 snapshot has none
            head = h[: h.index('<div class="msi">')]
            for stale in ("176", "ranked", "data-ri-reading", "benchmark-50-og.jpg\"" if False else "gta-medspa/og.jpg"):
                self.assertNotIn(stale, head)
            for m in re.finditer(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', h, flags=re.S):
                j = json.loads(m.group(1))
                if j.get("@type") == "Article" and h is live:  # recorded from the production deployment at publication, never guessed
                    want = e3.get("modified_at")
                    self.assertEqual(j.get("dateModified"), want)
            self.assertIn("medspa-index-og.jpg" if h is live else "benchmark-50-og.jpg", h)  # the published snapshot keeps its own artwork
        for f in ("medspa-index-og.jpg", "medspa-index-hero.webp", "medspa-index-hero-704.webp", "benchmark-50-og.jpg", "benchmark-50-hero.webp"):
            self.assertTrue((root / "assets/index/gta-medspa" / f).exists(), f)
        sm = (root / "sitemap.xml").read_text()
        self.assertIn("/medspa-index</loc>", sm)
        self.assertNotIn("/gta-medspa-index", sm)
        self.assertNotIn("edition-00", sm)
        self.assertIn("<h1>Med Spa Index</h1>", live)
        self.assertIn("<title>Med Spa Index: Ontario Med Spa Instagram | HelpMeMarketing</title>", live)
        self.assertIn("Edition <b>003</b>", live)
        self.assertTrue((root / "gta-medspa-index/edition-001.html").exists())
        ed = json.loads((KIT / "edition.json").read_text())
        self.assertEqual((ed["edition"], ed["scoring"]), ("002", "not applicable"))
        self.assertIn(ed["status"], ("release_candidate", "published"))


class BuildGuards(unittest.TestCase):
    """build_50.py in a temporary copy of the repo: stale-value guards and publication dates. Real files are never touched."""
    def setUp(self):
        self.t = Path(tempfile.mkdtemp())
        root = KIT.parent.parent
        for rel in ("_kit/gta-medspa-instagram", "gta-medspa-index", "medspa-index.html", "medspa-marketing-research.html"):
            src, dst = root / rel, self.t / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns("work", "output", "__pycache__", "renders"))
            else:
                shutil.copy(src, dst)
        self.k = self.t / "_kit/gta-medspa-instagram"

    def tearDown(self):
        shutil.rmtree(self.t)

    def build(self, *a):
        return run([str(self.k / "build_50.py"), "--target", "release", *a])

    def edit(self, rel, fn):
        f = self.k / rel
        d = json.loads(f.read_text())
        fn(d)
        f.write_text(json.dumps(d))

    def test_reproduces_committed_pages(self):
        ed = json.loads((self.k / "edition.json").read_text())
        extra = ["--modified-at", ed["modified_at"], "--modified-source", ed["modified_at_source"]] if ed.get("modified_at") else []
        p = self.build("--edition", "002", *extra)
        self.assertEqual(p.returncode, 0, p.stderr)
        for rel in ("medspa-index.html", "gta-medspa-index/edition-002.html"):  # edition 003 owns the live page; the 002 snapshot is never rewritten
            self.assertEqual((self.t / rel).read_text(), (KIT.parent.parent / rel).read_text(), rel)
        # the edition 002 page build_50 now writes to its release folder equals the 002 page as last committed before edition 003
        prev = subprocess.run(["git", "show", "932acb2:medspa-index.html"], capture_output=True, text=True, cwd=KIT).stdout
        if prev:
            self.assertEqual((self.k / "editions/002/release/medspa-index-002.html").read_text(), prev)

    def test_stale_values_are_refused(self):
        self.assertIn("stale edition", self.build("--edition", "003").stderr)
        self.edit("edition.json", lambda d: d["counts"].update(posts_observed=35))
        self.assertIn("do not match the data", self.build().stderr)
        self.edit("edition.json", lambda d: d["counts"].update(posts_observed=36))
        self.edit("edition.json", lambda d: d.update(window=["2026-07-18", "2026-10-15"]))
        self.assertIn("window must be", self.build().stderr)
        self.edit("edition.json", lambda d: d.update(window=["2026-07-17", "2026-10-15"]))
        self.edit("editions/002/run_ledger.json", lambda d: d["runs"][0].update(cap_usd=1.5))
        self.assertIn("exceeds the 5.0 guard", self.build().stderr)
        self.edit("editions/002/run_ledger.json", lambda d: d["runs"][0].update(cap_usd=1.0, hit_cap=True))
        self.assertIn("reached its cap", self.build().stderr)
        self.edit("editions/002/run_ledger.json", lambda d: d["runs"][0].update(hit_cap=False))
        self.edit("edition.json", lambda d: d["inputs"].update(posts="editions/001/x.jsonl.gz"))
        self.assertIn("not under editions/002/", self.build().stderr)

    def test_edition_without_approved_text_is_refused(self):
        self.edit("edition.json", lambda d: d.update(edition="003"))
        self.assertNotEqual(self.build().returncode, 0)

    def test_dates_are_recorded_only_when_given(self):
        iso = "2026-10-16T14:30:00+00:00"
        self.assertNotEqual(self.build("--modified-at", iso).returncode, 0)  # needs a source
        self.assertNotEqual(self.build("--modified-at", "2026-10-16T14:30:00", "--modified-source", "x").returncode, 0)  # needs an offset
        self.assertNotEqual(self.build("--modified-at", "2026-10-14T14:30:00+00:00", "--modified-source", "x").returncode, 0)  # before collection
        p = self.build("--modified-at", iso, "--modified-source", "deployment dpl_x (commit abc)")
        self.assertEqual(p.returncode, 0, p.stderr)
        h = (self.k / "editions/002/release/medspa-index-002.html").read_text()
        self.assertIn('"dateModified":"' + iso + '"', h)
        self.assertNotIn(iso, (self.t / "medspa-index.html").read_text())  # edition 003 owns the live page
        self.assertIn("<span>Updated <b>16 October 2026</b></span>", h)
        self.assertIn("<b>15 October 2026</b>", h)  # the collection date stays separate
        self.assertNotIn("Updated <b>16 October", (self.t / "gta-medspa-index/edition-002.html").read_text())  # snapshot untouched
        hub = (self.t / "medspa-marketing-research.html").read_text()
        self.assertNotIn(iso, hub)  # the hub now follows edition 003's release, not build_50
        self.assertIn('"datePublished":"2026-10-14T23:46:05+00:00"', hub)
        ed = json.loads((self.k / "edition.json").read_text())
        self.assertNotEqual(ed.get("modified_at"), iso)  # edition 002 no longer owns the live page, so its record is not changed
        self.assertNotEqual(json.loads((KIT / "edition.json").read_text()).get("modified_at"), iso)  # real file untouched


class UrlMigration(unittest.TestCase):
    def test_redirect_is_exact_and_links_follow(self):
        root = KIT.parent.parent
        v = json.loads((root / "vercel.json").read_text())
        old = [r for r in v["redirects"] if "gta-medspa" in r["source"]]
        self.assertEqual(old, [{"source": "/gta-medspa-index", "destination": "/medspa-index", "permanent": True}])  # exact path only
        self.assertFalse([r for r in v["redirects"] + v["rewrites"] if r["source"].startswith("/(") and "gta-medspa" in r.get("destination", "")])
        self.assertTrue((root / "gta-medspa-index/edition-001.html").exists() and (root / "gta-medspa-index/edition-002.html").exists())
        for rel in ("medspa-marketing-research.html", "hmm-index.html", "work.html", "ai-tools.html", "medspa-index.html"):
            h = (root / rel).read_text()
            bad = [u for u in re.findall(r'href="(/gta-medspa-index[^"]*)"', h) if not re.match(r"/gta-medspa-index/edition-00[12]$", u)]
            self.assertEqual(bad, [], rel)  # only the preserved snapshot URLs may keep the old path
        hub = (root / "medspa-marketing-research.html").read_text()
        self.assertIn('href="/medspa-index"', hub)
        self.assertIn("/gta-medspa-index/edition-001", hub)
        self.assertIn("research_gta_medspa", (root / "medspa-index.html").read_text())  # entry value and review CTA id keep their names
        self.assertIn("research_(hub|gta_medspa", (root / "contact.html").read_text())  # contact.html allowlist regex


class Edition003(unittest.TestCase):
    """build_003.py (five-account edition) in a temporary copy of the repo. Real files are never touched."""
    def setUp(self):
        self.t = Path(tempfile.mkdtemp())
        root = KIT.parent.parent
        for rel in ("_kit/gta-medspa-instagram", "gta-medspa-index", "medspa-index", "medspa-index.html", "medspa-marketing-research.html", "assets/index/medspa"):
            src, dst = root / rel, self.t / rel
            if not src.exists():
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            (shutil.copytree(src, dst, ignore=shutil.ignore_patterns("work", "output", "__pycache__", "renders", "screens")) if src.is_dir() else shutil.copy(src, dst))
        self.k = self.t / "_kit/gta-medspa-instagram"
        self.root = root
        self.cfg = json.loads((KIT / "editions/003/edition_003.json").read_text())
        self.published = self.cfg["status"] == "published"

    def tearDown(self):
        shutil.rmtree(self.t)

    def b(self, *a):
        return run([str(self.k / "build_003.py"), *a])

    def test_derive_and_draft_reproduce_committed_files(self):
        p = run([str(self.k / "derive_003.py")])
        self.assertEqual(p.returncode, 0, p.stderr)
        for rel in ("editions/003/metrics.json", "editions/003/observations.json"):
            self.assertEqual((self.k / rel).read_text(), (KIT / rel).read_text(), rel)
        c = self.cfg  # once published, the page is reproduced from the recorded release values
        p = self.b("--target", "release", "--published-at", c["published_at"], "--modified-at", c["modified_at"], "--modified-source", c["modified_at_source"]) if self.published else self.b()
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("PASS release" if self.published else "PASS draft", p.stdout)
        for rel in ("medspa-index.html", "medspa-marketing-research.html", "assets/index/medspa/medspa-index-edition-003-posts.csv", "assets/index/medspa/medspa-index-edition-003-accounts.csv"):
            self.assertEqual((self.t / rel).read_text(), (self.root / rel).read_text(), rel)
        snap = self.t / "medspa-index/edition-003.html"
        if self.published:  # the snapshot is kept as published, never rewritten
            self.assertIn("snapshot kept as published", p.stdout)
            self.assertEqual(snap.read_text(), (self.root / "medspa-index/edition-003.html").read_text())
        else:
            self.assertFalse(snap.exists())  # no snapshot before publication

    def test_page_rules(self):
        h = (self.root / "medspa-index.html").read_text()
        body = h[h.index('<div class="msi">'):]
        self.assertNotRegex(h, "[\u2014\u2013]")
        self.assertEqual(h.count("<h1"), 1)
        self.assertNotRegex(body, r"\sstyle=")
        self.assertNotRegex(h, r'"@type":\s*"(Review|Rating|AggregateRating)"')
        self.assertIn('href="/contact?intent=review&amp;entry=research_gta_medspa#contact-form" data-review-cta="research_gta_medspa"', h)
        self.assertEqual(body.count("What this means for your clinic"), 7)  # findings, five accounts, patterns
        for link in ("/realestate-index", "/about", "/work", "/services/branding-social", "/services/analytics-attribution"):
            self.assertIn(f'href="{link}"', body)
        hist = re.search(r"<td><b>003</b>.*?</tr>", body, re.S).group(0)
        if self.published:
            self.assertIn('<meta name="robots" content="index, follow', h)
            self.assertIn('Published 15 October 2026. ', hist)
            self.assertIn('href="/medspa-index/edition-003"', hist)
        else:
            self.assertIn('<meta name="robots" content="noindex, nofollow">', h)
            self.assertNotIn("Published 1", hist)  # no publication date while unpublished
        lds = [json.loads(m) for m in re.findall(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', h, re.S)]
        types = [j["@type"] for j in lds]
        self.assertEqual(types, ["BreadcrumbList", "Article", "Dataset", "FAQPage"])
        art = lds[1]
        self.assertEqual(art["headline"], "Med Spa Index")
        self.assertEqual((art["author"]["@id"], art["publisher"]["@id"]), ("https://helpmemarketing.com/about#ankit-kumar", "https://helpmemarketing.com/#organization"))
        self.assertNotIn("datePublished", art)
        self.assertEqual(art.get("dateModified"), self.cfg["modified_at"] if self.published else None)
        if self.published:
            s = (self.root / "medspa-index/edition-003.html").read_text()
            self.assertEqual(s.count('<meta name="robots"'), 1)
            self.assertIn('<meta name="robots" content="noindex, follow">', s)
            self.assertIn('<link rel="canonical" href="https://helpmemarketing.com/medspa-index/edition-003">', s)
            crumb = json.loads(re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', s, re.S).group(1))
            self.assertEqual(crumb["itemListElement"][-1]["item"], "https://helpmemarketing.com/medspa-index/edition-003")
        faq_vis = [re.sub(r"<[^>]+>", "", q) for q in re.findall(r'<details class="ri-adv faq"><summary>(.*?)</summary>', body)]
        self.assertEqual([q["name"] for q in lds[3]["mainEntity"]], faq_vis)
        for d in lds[2]["distribution"]:
            self.assertTrue((self.root / d["contentUrl"].split(".com/")[1]).exists(), d["contentUrl"])

    def test_figures_reconcile_with_metrics(self):
        m = json.loads((KIT / "editions/003/metrics.json").read_text())["accounts"]
        h = (self.root / "medspa-index.html").read_text()
        rows = list(__import__("csv").DictReader(open(self.root / "assets/index/medspa/medspa-index-edition-003-posts.csv")))
        for hd, a in m.items():
            if not a["accessible"]:
                self.assertEqual(sum(r["account"] == hd for r in rows), 0)
                continue
            self.assertEqual(sum(r["account"] == hd for r in rows), a["posts_in_window"])
            self.assertIn(f'data-v="{a["followers"]}"', h)
            self.assertIn(a["standout"]["url"], h)
        readable = [a for a in m.values() if a["accessible"]]
        lo, hi = min(a["posts_in_window"] for a in readable), max(a["posts_in_window"] for a in readable)
        for rel in ("medspa-marketing-research.html", "hmm-index.html"):  # hand-written summaries elsewhere must match the data
            self.assertIn(f"{lo} to {hi}", (self.root / rel).read_text(), rel)

    def test_wrong_data_is_refused(self):
        c = self.k / "editions/003/coding.json"
        d = json.loads(c.read_text())
        d["standout_visuals"]["Xnotreal"] = d["standout_visuals"].pop(next(iter(d["standout_visuals"])))
        c.write_text(json.dumps(d))
        self.assertIn("standout visuals", self.b().stderr)  # a changed standout needs a fresh visual inspection
        shutil.copy(KIT / "editions/003/coding.json", c)
        t = self.k / "editions/003/body_template.html"
        t.write_text(t.read_text().replace("{{a.vit.followers}}", "{{a.vit.folowers}}", 1) + "{{a.vit.nope}}")
        self.assertIn("has no value", self.b().stderr)
        shutil.copy(KIT / "editions/003/body_template.html", t)
        t.write_text(t.read_text().replace("What stood out</h2>", "What stood out \u2014</h2>", 1))
        self.assertIn("dash", self.b().stderr)
        shutil.copy(KIT / "editions/003/body_template.html", t)
        e = self.k / "editions/003/edition_003.json"
        d = json.loads(e.read_text()); d["window"] = ["2026-09-14", "2026-10-14"]; e.write_text(json.dumps(d))
        self.assertNotEqual(self.b().returncode, 0)

    def test_release_creates_snapshot_once(self):
        self.assertNotEqual(self.b("--target", "release").returncode, 0)  # needs recorded dates
        (self.t / "medspa-index/edition-003.html").unlink(missing_ok=True)  # simulate the first release in the copy
        e = self.k / "editions/003/edition_003.json"
        d = json.loads(e.read_text()); d.pop("hub_modified_at", None); e.write_text(json.dumps(d))
        iso = "2026-10-20T15:00:00+00:00"
        p = self.b("--target", "release", "--published-at", iso, "--modified-at", iso, "--modified-source", "deployment dpl_x (commit abc)")
        self.assertEqual(p.returncode, 0, p.stderr)
        live, snap = (self.t / "medspa-index.html").read_text(), (self.t / "medspa-index/edition-003.html").read_text()
        self.assertIn('content="index, follow', live)
        self.assertIn('"dateModified":"' + iso + '"', live)
        self.assertIn("Published 20 October 2026", live)
        self.assertEqual(snap.count('name="robots"'), 1)
        self.assertIn('<meta name="robots" content="noindex, follow">', snap)
        self.assertIn('rel="canonical" href="https://helpmemarketing.com/medspa-index/edition-003"', snap)
        self.assertIn("Published 14 October 2026 &middot; Updated 20 October 2026", (self.t / "medspa-marketing-research.html").read_text())
        first = snap
        p = self.b("--target", "release", "--published-at", iso, "--modified-at", "2026-10-25T15:00:00+00:00", "--modified-source", "y")
        self.assertIn("snapshot kept as published", p.stdout)
        self.assertEqual((self.t / "medspa-index/edition-003.html").read_text(), first)
        self.assertIn('"dateModified":"2026-10-25T15:00:00+00:00"', (self.t / "medspa-index.html").read_text())
        hub = (self.t / "medspa-marketing-research.html").read_text()  # a page-only change leaves the hub's dates alone
        self.assertIn("Updated 20 October 2026", hub)
        self.assertIn('"dateModified":"' + iso + '"', hub)


class Five(unittest.TestCase):
    """Generic five-account pipeline (derive_five, build_five, check_live, export_five) on a sample edition 004 made from
    edition 003's saved records, in a temporary copy of the repo. Real files are never touched."""
    def setUp(self):
        self.t = Path(tempfile.mkdtemp())
        root = KIT.parent.parent
        for rel in ("_kit/gta-medspa-instagram", "medspa-index", "gta-medspa-index", "medspa-index.html", "medspa-marketing-research.html",
                    "hmm-index.html", "sitemap.xml", "assets/index/medspa"):
            src, dst = root / rel, self.t / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            (shutil.copytree(src, dst, ignore=shutil.ignore_patterns("work", "output", "__pycache__", "renders", "screens")) if src.is_dir() else shutil.copy(src, dst))
        self.k = self.t / "_kit/gta-medspa-instagram"
        e3, e4 = self.k / "editions/003", self.k / "editions/004"
        e4.mkdir()
        shutil.copytree(e3 / "raw", e4 / "raw")
        for f in ("run_ledger.json", "services.json", "adlibrary.json"):
            shutil.copy(e3 / f, e4 / f)
        coh = json.loads((self.k / "cohort_five.json").read_text())
        acc = {"edition": "004", "accounts": [dict(a, verification_date="2026-10-15") for a in coh["accounts"]]}
        for a in acc["accounts"]:
            a.pop("alias")
        (e4 / "accounts.json").write_text(json.dumps(acc))
        (e4 / "edition.json").write_text(json.dumps({"edition": "004", "status": "draft", "collected_on": "2026-10-15",
                                                      "window": ["2026-09-15", "2026-10-14"], "window_days": 30, "timezone": "America/Toronto"}))
        c = json.loads((e3 / "coding.json").read_text())
        c.update(edition="004", standout_titles={k: "A sample title" for k in c["standout_visuals"]}, frame_crop={k: 0.5 for k in c["standout_visuals"]},
                 literal_numbers={"21": "age limit", "2025": "award year quoted from a cover"})
        (e4 / "coding.json").write_text(json.dumps(c))
        f = json.loads((e3 / "frames.json").read_text())
        f["edition"] = "004"
        (e4 / "frames.json").write_text(json.dumps(f))
        shutil.copy(KIT / "tests/fixtures/narrative_sample.json", e4 / "narrative.json")
        self.e4 = e4

    def tearDown(self):
        shutil.rmtree(self.t)

    def k_run(self, *a):
        return run([str(self.k / a[0]), *a[1:]], cwd=self.k)

    def test_derive_five_reproduces_edition_003(self):
        p = self.k_run("derive_five.py", "--edition", "003")
        self.assertEqual(p.returncode, 0, p.stderr)
        for rel in ("metrics.json", "observations.json"):
            self.assertEqual((self.k / "editions/003" / rel).read_text(), (KIT / "editions/003" / rel).read_text(), rel)

    def test_sample_edition_draft_release_record_and_check(self):
        self.assertEqual(self.k_run("derive_five.py", "--edition", "004").returncode, 0)
        p = self.k_run("build_five.py", "--edition", "004")
        self.assertEqual(p.returncode, 0, p.stderr)
        page = (self.t / "medspa-index.html").read_text()
        self.assertIn('<meta name="robots" content="noindex, nofollow">', page)
        self.assertIn("Edition <b>004</b>", page)
        self.assertIn('<td><b>003</b></td><td class="wrap-cell">Published 15 October 2026.', page)
        self.assertIn('href="/medspa-index/edition-003">Snapshot</a>', page)
        self.assertIn("Clarification, 15 October 2026.</b> Edition 003.", page)
        self.assertNotIn("{{", page)
        self.assertNotRegex(page, "[\u2014\u2013]")
        self.assertGreaterEqual(page.count("21+ viewing restriction"), 8)  # page, FAQ data, table, notes and method
        t0 = "2026-11-15T15:00:00-05:00"
        p = self.k_run("build_five.py", "--edition", "004", "--target", "release", "--published-at", t0, "--modified-at", t0, "--modified-source", "provisional: release commit time")
        self.assertEqual(p.returncode, 0, p.stderr)
        snap = (self.t / "medspa-index/edition-004.html").read_text()
        self.assertIn('<meta name="robots" content="noindex, follow">', snap)
        self.assertEqual(json.loads(re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', snap, re.S).group(1))["itemListElement"][-1]["item"],
                         "https://helpmemarketing.com/medspa-index/edition-004")
        hub = (self.t / "medspa-marketing-research.html").read_text()
        self.assertIn("Edition 004 covers 15 September to 14 October 2026 and re-collects", hub)
        self.assertIn('href="/medspa-index/edition-003">Edition 003 snapshot</a>', hub)
        self.assertIn("Edition 004, collected 15 October 2026", (self.t / "hmm-index.html").read_text())
        self.assertIn("<lastmod>2026-11-15", (self.t / "sitemap.xml").read_text())
        t1 = "2026-11-15T20:10:00.000+00:00"
        p = self.k_run("build_five.py", "--edition", "004", "--target", "release", "--published-at", t1, "--modified-at", t1, "--modified-source", "deployment dpl_x (commit abc)")
        self.assertEqual(p.returncode, 0, p.stderr)
        for f in ("medspa-index.html", "medspa-index/edition-004.html", "medspa-marketing-research.html"):
            self.assertIn(f'"dateModified":"{t1}"', (self.t / f).read_text(), f)
        self.assertIn("Metadata fix", (self.t / "medspa-index/edition-004.html").read_text())
        self.assertEqual(self.k_run("build_five.py", "--edition", "004", "--check-live").returncode, 0)
        self.assertNotEqual(self.k_run("build_five.py", "--edition", "004").returncode, 0)  # no draft over a published edition
        p = self.k_run("check_live.py")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("edition 004", p.stdout)
        (self.t / "medspa-index.html").write_text((self.t / "medspa-index.html").read_text().replace("Patterns across the five", "Patterns"))
        self.assertNotEqual(self.k_run("check_live.py").returncode, 0)  # a hand edit to the live page is caught
        self.assertEqual(self.k_run("export_five.py", "--edition", "004", "--status", "Published", "--commit", "abc").returncode, 0)

    def bad(self, change, expect):
        self.assertEqual(self.k_run("derive_five.py", "--edition", "004").returncode, 0)
        change()
        p = self.k_run("build_five.py", "--edition", "004")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn(expect, p.stderr)

    def narr(self, f):
        n = json.loads((self.e4 / "narrative.json").read_text())
        f(n)
        (self.e4 / "narrative.json").write_text(json.dumps(n))

    def test_typed_figure_is_refused(self):
        self.bad(lambda: self.narr(lambda n: n["findings"][0].update(text=n["findings"][0]["text"] + " It posted 17 times.")), "typed by hand")

    def test_we_is_refused(self):
        self.bad(lambda: self.narr(lambda n: n.update(patterns_takeaway="We think this matters.")), "first person singular")

    def test_missing_account_reading_is_refused(self):
        self.bad(lambda: self.narr(lambda n: n["accounts"].pop("spa")), "readable accounts")

    def test_unknown_token_is_refused(self):
        self.bad(lambda: self.narr(lambda n: n.update(findings_takeaway="{{a.skv.median_likes}} likes.")), "has no value")

    def test_stale_standout_note_is_refused(self):
        def f():
            c = json.loads((self.e4 / "coding.json").read_text())
            c["standout_titles"].popitem()
            (self.e4 / "coding.json").write_text(json.dumps(c))
        self.bad(f, "standout_titles")

    def test_cohort_cannot_change(self):
        a = json.loads((self.e4 / "accounts.json").read_text())
        a["accounts"][4]["handle"] = "someotherclinic"
        (self.e4 / "accounts.json").write_text(json.dumps(a))
        p = self.k_run("derive_five.py", "--edition", "004")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("never replace or add accounts", p.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
