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
        h = (KIT / "editions/002/draft/gta-medspa-index-50-draft.html").read_text()
        self.assertNotRegex(h, "[\u2014\u2013]")
        self.assertIn("<h1>50-account GTA medspa Instagram benchmark</h1>", h)
        self.assertIn('content="noindex, nofollow"', h)
        self.assertNotIn("FAQPage", h)
        self.assertNotRegex(h[h.index('<div class="msi">'):], r'\sstyle=')


class ReleaseFiles(unittest.TestCase):
    def test_live_page_snapshot_and_links(self):
        root = KIT.parent.parent
        live = (root / "gta-medspa-index.html").read_text()
        snap = (root / "gta-medspa-index/edition-002.html").read_text()
        for h, canon, robots in ((live, "https://helpmemarketing.com/gta-medspa-index", "index, follow"),
                                 (snap, "https://helpmemarketing.com/gta-medspa-index/edition-002", "noindex, follow")):
            self.assertNotRegex(h, "[\\u2014\\u2013]")
            self.assertEqual(h.count('name="robots"'), 1)
            self.assertIn(f'name="robots" content="{robots}', h)
            self.assertIn(f'rel="canonical" href="{canon}"', h)
            self.assertNotIn("FAQPage", h)
            head = h[: h.index('<div class="msi">')]
            for stale in ("176", "ranked", "data-ri-reading", "benchmark-50-og.jpg\"" if False else "gta-medspa/og.jpg"):
                self.assertNotIn(stale, head)
            for m in re.finditer(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', h, flags=re.S):
                j = json.loads(m.group(1))
                self.assertNotIn("dateModified", j)  # recorded from the production deployment at publication
            self.assertIn("benchmark-50-og.jpg", h)
        for f in ("benchmark-50-og.jpg", "benchmark-50-hero.webp", "benchmark-50-hero-704.webp"):
            self.assertTrue((root / "assets/index/gta-medspa" / f).exists(), f)
        sm = (root / "sitemap.xml").read_text()
        self.assertIn("/gta-medspa-index</loc>", sm)
        self.assertNotIn("edition-002", sm)
        self.assertTrue((root / "gta-medspa-index/edition-001.html").exists())
        ed = json.loads((KIT / "edition.json").read_text())
        self.assertEqual((ed["edition"], ed["scoring"], ed["status"]), ("002", "not applicable", "release_candidate"))


class BuildGuards(unittest.TestCase):
    """build_50.py in a temporary copy of the repo: stale-value guards and publication dates. Real files are never touched."""
    def setUp(self):
        self.t = Path(tempfile.mkdtemp())
        root = KIT.parent.parent
        for rel in ("_kit/gta-medspa-instagram", "gta-medspa-index", "gta-medspa-index.html", "medspa-marketing-research.html"):
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
        p = self.build("--edition", "002")
        self.assertEqual(p.returncode, 0, p.stderr)
        for rel in ("gta-medspa-index.html", "gta-medspa-index/edition-002.html"):
            self.assertEqual((self.t / rel).read_text(), (KIT.parent.parent / rel).read_text(), rel)

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
        for rel in ("gta-medspa-index.html", "gta-medspa-index/edition-002.html"):
            h = (self.t / rel).read_text()
            self.assertIn('"dateModified":"' + iso + '"', h)
            self.assertIn("<span>Updated <b>16 October 2026</b></span>", h)
            self.assertIn("<b>15 October 2026</b>", h)  # the collection date stays separate
        hub = (self.t / "medspa-marketing-research.html").read_text()
        self.assertIn('"dateModified":"' + iso + '"', hub)
        self.assertIn("Published 14 October 2026 &middot; Updated 16 October 2026", hub)
        self.assertIn('"datePublished":"2026-10-14T23:46:05+00:00"', hub)
        ed = json.loads((self.k / "edition.json").read_text())
        self.assertEqual(ed["modified_at"], iso)
        self.assertIsNone(json.loads((KIT / "edition.json").read_text())["modified_at"])  # real file untouched


if __name__ == "__main__":
    unittest.main(verbosity=2)
