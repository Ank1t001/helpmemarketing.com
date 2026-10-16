#!/usr/bin/env python3
"""Build the Dental Implant Marketing Index page (/dental-index) from the kit. Standard library only.

    python3 build.py --edition 001                 draft: noindex, no dates, no snapshot, not in the sitemap
    python3 build.py --edition 001 --check         validate only, write nothing
    python3 build.py --edition 001 --report        print the release report (blockers by category) and exit
    python3 build.py --edition 001 --target release --published-at ISO --modified-at ISO
                                                   release: refused until every release requirement is met

Sources of truth (editions/NNN/): edition.json (status, the fixed observation window, evidence batches, reviewed limitations),
raw/ (website fetch log and pages; raw/<batch>/ for browser evidence with manifest.json), observations.json (dated, sourced
website observations), comparison.json, social.json, ads.json, narrative.json; cohort.json at the kit root.
Outputs: dental-index.html (repo root) and three CSVs in assets/index/dental/ (website observations, ad records, Instagram posts).
The page body is never edited by hand.
"""
import argparse, csv, gzip, hashlib, html, io, json, re, sys
from datetime import datetime, date, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
TZ = ZoneInfo("America/Toronto")
SITE = "https://helpmemarketing.com"
ROUTE = "/dental-index"
CANON = SITE + ROUTE
PAGE = REPO / "dental-index.html"
CSV_DIR = REPO / "assets" / "index" / "dental"
E = lambda s: html.escape(str(s), quote=True)
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
ALIASES = ["studiob", "nysc", "gajjar", "dundas", "bond"]
NAMES = {"studiob": "Studio B Dental", "nysc": "North York Smile Centre", "gajjar": "Dr. Neil J. Gajjar Associates & Specialists",
         "dundas": "Dundas East Dental", "bond": "Bond Street Dental"}
KINDS = {"observed", "claim", "absence"}
AD_STATUS = {"relevant_ads_observed": "Relevant ads observed", "no_matching_ads_found": "No matching ads found in the documented search",
             "advertiser_uncertain": "Advertiser identity uncertain", "not_checked": "Not checked", "access_blocked": "Access blocked"}
CONFIDENCE = {"confirmed": "Confirmed", "supported": "Supported", "uncertain": "Uncertain"}
TREATMENTS = {"implant": "Implants", "implant_full_arch": "Full-arch implants", "veneers": "Veneers", "invisalign": "Invisalign", "general_dentistry": "General dentistry",
              "emergency": "Emergency dentistry", "root_canal": "Root canal", "whitening": "Whitening", "cosmetic": "Cosmetic dentistry", "sedation": "Sedation dentistry",
              "clinic_culture": "Clinic culture", "not_treatment_marketing": "Not treatment marketing", "unclear": "Unclear"}
RELATIONS = {"active_at_observation_started_before_window": "Active when observed; library start date before the window",
             "active_at_observation_started_in_window": "Active when observed; started inside the window",
             "started_after_window": "Started after the window",
             "ended_in_or_after_window": "Inactive when observed; ran into the window",
             "historical_before_window": "Historical: ended or last shown before the window",
             "shown_in_window": "Shown in the window (Google date filter, Pacific Time)"}
COVERAGE = {"confirmed_complete", "probable_not_confirmed", "blocked", "handle_not_verified", "not_collected"}
BANNED = ["viral", "winning", "best-performing", "best performing", "top-performing", "leverage", "unlock", "supercharge", "game-changer",
          "guarantee", "in today's fast-paced world"]
# Claims that need complete coverage: posting frequency, totals for the window, "only" statements about what an account published.
FREQUENCY = re.compile(r"\b(per (day|week|month)|a (day|week|month)\b|times a\b|posting frequency|every post|all (of )?(its|their) posts|only (posted|published)|published only|posted only|(total|all) posts in the window|posts in total)", re.I)
TAKE = "What this means for your clinic"

class BuildError(Exception):
    pass

def need(cond, msg):
    if not cond: raise BuildError(msg)

def long_date(d):
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"

def date_forms(iso):
    d = date.fromisoformat(iso)
    return f"{long_date(d)} {MONTHS[d.month-1]} {d.day}, {d.year} {MONTHS[d.month-1][:3]} {d.day}, {d.year}"

def toronto(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(TZ)

def clock(dt):
    h = dt.hour % 12 or 12
    return f"{h}:{dt.minute:02d} {'a.m.' if dt.hour < 12 else 'p.m.'}"

def window_last_30(collected_local):
    """The last 30 complete calendar days in America/Toronto before a collection date. Used once, when an edition's window is
    first written into edition.json; a build never recomputes the window."""
    end = collected_local.date() - timedelta(days=1)
    return end - timedelta(days=29), end

def edition_window(ed):
    w = ed.get("window"); need(isinstance(w, dict), "edition.json needs a fixed window {start, end, timezone, days}")
    s, e = date.fromisoformat(w["start"]), date.fromisoformat(w["end"])
    need(w["timezone"] == "America/Toronto", "window timezone must be America/Toronto")
    need((e - s).days + 1 == w["days"] == 30, "the window must be 30 days, start and end included")
    return s, e

def in_window(ts, w):
    d = toronto(ts).date()
    return w[0] <= d <= w[1]

def after_window(ts, w):
    return toronto(ts).date() > w[1]

def clean_posts(posts, handles, w):
    """Window filter, error-row exclusion, de-duplication and owner/collaboration split for collected Instagram posts.
    Returns (own, collab, report). Missing metrics stay None; nothing is converted to zero."""
    seen, own, collab = set(), [], []
    report = {"rows": len(posts), "errors": 0, "duplicates": 0, "outside_window": 0, "pinned_outside": 0, "not_cohort": 0}
    for p in posts:
        if p.get("error") or not p.get("shortcode") or not p.get("timestamp"):
            report["errors"] += 1; continue
        if p["shortcode"] in seen:
            report["duplicates"] += 1; continue
        seen.add(p["shortcode"])
        if not in_window(p["timestamp"], w):
            report["outside_window"] += 1
            if p.get("pinned"): report["pinned_outside"] += 1
            continue
        owner = p.get("owner")
        if owner in handles: own.append(p)
        elif p.get("requested_handle") in handles: collab.append(p)
        else: report["not_cohort"] += 1
    for p in own + collab:
        for k in ("likes", "comments", "plays"):
            if k in p and p[k] is not None and p[k] < 0: p[k] = None
    return own, collab, report

def window_relation(platform, pd, w, in_window_list):
    s, e = w[0].isoformat(), w[1].isoformat()
    if platform == "meta":
        if pd["status_at_observation"] == "inactive":
            return "historical_before_window" if pd["ended"] and pd["ended"] < s else "ended_in_or_after_window"
        if pd["started"] < s: return "active_at_observation_started_before_window"
        return "active_at_observation_started_in_window" if pd["started"] <= e else "started_after_window"
    if in_window_list: return "shown_in_window"
    return "historical_before_window" if pd["last_shown"] < s else "unknown"

def norm(t):
    return re.sub(r"\s+", " ", t.replace("​", "")).strip()

def load(ed):
    D = HERE / "editions" / ed
    need(D.exists(), f"edition {ed} not found")
    j = lambda p: json.loads((D / p).read_text(encoding="utf-8"))
    log = [json.loads(l) for l in (D / "raw" / "fetch_log.jsonl").read_text().splitlines() if l.strip()]
    K = {"D": D, "cohort": json.loads((HERE / "cohort.json").read_text()), "edition": j("edition.json"), "obs": j("observations.json")["observations"],
         "cmp": j("comparison.json"), "nar": j("narrative.json"), "social": j("social.json"), "ads": j("ads.json"), "log": log, "batches": {}}
    for b in K["edition"].get("evidence_batches", []):
        R = D / "raw" / b["batch"]
        if (R / "manifest.json").exists():
            jl = lambda p: [json.loads(l) for l in (R / p).read_text().splitlines() if l.strip()]
            K["batches"][b["batch"]] = {"R": R, "manifest": {m["repo_path"]: m for m in json.loads((R / "manifest.json").read_text()) if m["repo_path"]},
                "load": {r["tag"]: r for r in jl("logs/load_log.jsonl")}, "meta": json.loads((R / "logs/meta_parsed.json").read_text()),
                "gcr": {r["url"].split("/creative/")[1].split("?")[0]: r for r in jl("logs/google_creatives.jsonl")},
                "bond": {c["url"].split("/creative/")[1].split("?")[0]: c for c in json.loads((R / "logs/bond_google_creatives.json").read_text())},
                "window_links": {u.split("/creative/")[1].split("?")[0] for u in json.loads((R / "logs/bond_google_links.json").read_text())["links"]},
                "gwin": {r["alias"]: r for r in jl("logs/google_window.jsonl")}, "ig": {r["shortcode"]: r for r in jl("logs/ig_posts.jsonl")}}
    return K

def page_text(D, rec):
    return re.sub(r"\s+", " ", (D / "raw" / "text" / f"{rec['sha256'][:12]}.txt").read_text(encoding="utf-8"))

def stored_file(K, rel, where):
    """A screenshot or log referenced by a record must be in its batch manifest, unchanged."""
    m = re.match(r"raw/([^/]+)/(.+)$", rel or ""); need(m, f"{where}: evidence path {rel!r} is not under raw/<batch>/")
    b = K["batches"].get(m[1]); need(b, f"{where}: unknown evidence batch {m[1]}")
    man = b["manifest"].get(m[2]); need(man, f"{where}: {m[2]} is not in the {m[1]} manifest")
    p = b["R"] / m[2]; need(p.exists(), f"{where}: {rel} missing")
    need(hashlib.sha256(p.read_bytes()).hexdigest() == man["sha256_stored"], f"{where}: {rel} changed since ingestion")
    return b

def ad_records(K):
    out = {}
    for a, x in K["ads"]["checks"].items():
        for plat in ("meta", "google"):
            for r in x[plat].get("records", []): out[r["id"]] = (a, plat, r)
    return out

def validate_ads(K, w):
    A = K["ads"]; need(A.get("schema") == 2, "ads.json schema 2 expected")
    need(set(A["checks"]) == set(ALIASES), "ads.json needs a check per clinic")
    for a, x in A["checks"].items():
        for plat in ("meta", "google"):
            c = x[plat]; st = c["status"]; where = f"ads {a} {plat}"
            need(st in AD_STATUS, where + ": unknown status")
            recs = c.get("records", [])
            if st == "not_checked":
                need(not c.get("searches") and not recs, where + ": a check that has not run has no searches or records"); continue
            need(c.get("searched_at") and c.get("searches") and c.get("evidence"), where + ": a check needs a time, its searches and evidence")
            need(c.get("summary") and c.get("limits"), where + ": a check needs a public summary and its limits")
            for s in c["searches"]:
                need(after_window(s["searched_utc"], w), where + ": searches must follow the window")
                stored_file(K, s["screenshot"], where)
            if st == "no_matching_ads_found":
                need(not recs, where + ": no-match status with records")
                for s in c["searches"]:
                    need(s.get("result") == "No ads match your search criteria" or s.get("result_count") == 0, where + ": a search returned results")
            if st == "relevant_ads_observed":
                need(any(r["attribution"]["confidence"] in ("confirmed", "supported") for r in recs), where + ": relevant ads need at least one attributed record")
            if st == "advertiser_uncertain":
                need(recs and any(r["attribution"]["confidence"] == "uncertain" for r in recs), where + ": uncertain status needs uncertain records")
            ident = c.get("identity", {})
            if "uncertain" in json.dumps(ident): need(st == "advertiser_uncertain", where + ": while the clinic identity behind the domain is uncertain the status stays advertiser_uncertain")
            for r in recs:
                validate_ad(K, a, plat, r, w, ident)
    return ad_records(K)

def validate_ad(K, a, plat, r, w, ident):
    where = f"ad {r.get('id')}"
    for k in ("id", "platform", "url", "advertiser", "attribution", "treatment", "observed_utc", "platform_dates", "window_relation", "text_basis", "screenshot"):
        need(k in r, f"{where}: missing {k}")
    need(r["platform"] == plat and r["attribution"]["clinic"] == a, where + ": platform or clinic mismatch")
    need(r["attribution"]["confidence"] in CONFIDENCE and r["attribution"].get("basis"), where + ": attribution needs a confidence and a basis")
    if "uncertain" in json.dumps(ident):
        need(r["attribution"]["confidence"] != "confirmed", where + ": nothing is confirmed while the clinic identity behind the domain is uncertain")
    if r["attribution"].get("creative_evidence") == "domain":
        need(r["attribution"]["confidence"] == "uncertain", where + ": a creative showing only the domain cannot be attributed to the clinic")
    cat, impl = r["treatment"]["category"], r["treatment"]["implant_related"]
    need(cat in TREATMENTS, where + ": unknown treatment")
    need(impl == ("yes" if cat.startswith("implant") else "unclear" if cat == "unclear" else "no"), where + ": implant relevance must follow the treatment category")
    need(after_window(r["observed_utc"], w), where + ": observed before the window ended")
    pd = r["platform_dates"]
    b = stored_file(K, r["screenshot"], where)
    if plat == "meta":
        lid = r["id"].removeprefix("meta-")
        cards = [x for v in b["meta"].values() for x in v["ads"] if x["library_id"] == lid]
        need(cards, where + ": library id not in the saved results")
        need(r["url"] == f"https://www.facebook.com/ads/library/?id={lid}", where + ": library URL")
        need(pd["status_at_observation"] == cards[0]["status"].lower(), where + ": status differs from the saved results")
        if r["text"]:
            hay = norm((b["R"] / r["text_basis"]).read_text())
            need(norm(r["text"]) in hay, where + ": ad text not found in the saved results page")
        rel = window_relation("meta", pd, w, False)
    else:
        cid = r["id"].removeprefix("google-")
        src = b["bond"].get(cid) or b["gcr"].get(cid); need(src, where + ": creative not in the saved logs")
        ls = src.get("last_shown") or re.search(r"Last shown: ([^|]+)", src["main"])[1].strip()
        need(pd["last_shown"] == datetime.strptime(ls, "%b %d, %Y").date().isoformat(), where + ": last shown date differs from the log")
        need(pd["status_at_observation"] is None and pd["started"] is None, where + ": Google records carry only the last shown date")
        rel = window_relation("google", pd, w, cid in b["window_links"])
    need(r["window_relation"] == rel, f"{where}: window relation {r['window_relation']} should be {rel}")
    if rel == "historical_before_window": need(pd["status_at_observation"] != "active", where + ": a historical ad cannot be active")

def validate_social(K, w):
    S = K["social"]; need(set(S["handles"]) == set(ALIASES), "social.json needs a handle record per clinic")
    need(S["status"] in ("not_collected", "partial_sample", "collected"), "social status")
    need(S.get("reason") and S.get("public_reason"), "social: a reason and a public reason are required")
    if S["status"] == "not_collected":
        need(not S["posts"], "social: not collected needs no posts"); return
    cov = S["coverage"]; need(set(cov) == set(ALIASES), "social: coverage per clinic")
    for a, h in S["handles"].items():
        need(cov[a]["status"] in COVERAGE, f"social {a}: coverage status")
        if h["status"] != "verified_link": need(h["handle"] is None and h.get("reason") and cov[a]["status"] == "handle_not_verified", f"social {a}: unverified handle must stay empty")
        else: need(cov[a]["status"] != "handle_not_verified", f"social {a}: verified handle with an unverified coverage status")
    complete = all(cov[a]["status"] == "confirmed_complete" for a in ALIASES if S["handles"][a]["status"] == "verified_link")
    need((S["status"] == "collected") == complete, "social: 'collected' only when every verified account's coverage is confirmed complete; otherwise 'partial_sample'")
    need(after_window(S["collection_started_utc"], w), "social: collection must start after the window")
    seen = set()
    for p in S["posts"]:
        where = "post " + p.get("shortcode", "?"); need(p["shortcode"] not in seen, where + ": duplicate"); seen.add(p["shortcode"])
        h = S["handles"][p["clinic"]]
        need(h["status"] == "verified_link" and p["owner"] == h["handle"], where + ": owner is not the clinic's verified handle")
        need(re.fullmatch(rf"https://www\.instagram\.com/{re.escape(p['owner'])}/(p|reel)/{re.escape(p['shortcode'])}/", p["url"]), where + ": URL")
        need(in_window(p["published_utc"], w), where + ": published outside the fixed window")
        need(after_window(p["observed_utc"], w), where + ": observed before the window ended")
        need(p["collaboration"] in ("none_shown", "collaboration") and (p["collaboration"] == "none_shown" or p.get("collaborators")), where + ": collaboration")
        need(p["implant_relevance"] == ("yes" if p["treatment"].startswith("implant") else "unclear" if p["treatment"] == "unclear" else "no"), where + ": implant relevance must follow the treatment")
        need(p["treatment"] in TREATMENTS, where + ": treatment")
        need(p["video_watched"] is False or p["format"] != "reel", where + ": a watched video needs its own review record")
        need("videos not watched" in p["analysis_basis"] or p["video_watched"], where + ": analysis basis")
        m = p["metrics"]
        for k in ("likes", "comments", "plays"):
            need(m[k] is None or (isinstance(m[k], int) and m[k] >= 0), f"{where}: {k} must be a count or missing")
        need(m["plays"] is not None or m.get("plays_status", "").startswith("missing"), where + ": missing plays need a status")
        b = stored_file(K, p["screenshot"], where); raw = b["ig"].get(p["shortcode"]); need(raw, where + ": not in the saved post log")
        need(raw["times"][0]["dt"] == p["published_utc"], where + ": date differs from the post page")
        mm = re.match(r"([\d,]+) likes, ([\d,]+) comments", raw["og_desc"] or "")
        need(mm and (int(mm[1].replace(",", "")), int(mm[2].replace(",", ""))) == (m["likes"], m["comments"]), where + ": counts differ from the post page")
    for a in ALIASES:
        n = sum(1 for p in S["posts"] if p["clinic"] == a)
        need(n == (cov[a]["posts_read"] or 0), f"social {a}: posts_read does not match the posts recorded")

def facts(K):
    """Counts the page may state, computed from the records (accepted by the figure check)."""
    S, AD = K["social"], ad_records(K)
    f = {len(S["posts"]), sum(p["implant_relevance"] == "yes" for p in S["posts"])}
    for a in ALIASES:
        ps = [p for p in S["posts"] if p["clinic"] == a]; f |= {len(ps), sum(p["implant_relevance"] == "yes" for p in ps)}
        for plat in ("meta", "google"):
            c = K["ads"]["checks"][a][plat]; rs = c.get("records", [])
            f |= {len(rs), sum(r["treatment"]["implant_related"] == "yes" for r in rs), sum(r["attribution"]["confidence"] == "uncertain" for r in rs),
                  sum(r["attribution"]["confidence"] != "uncertain" for r in rs), sum(r.get("grouped_ads", 1) for r in rs)}
            f |= {s.get("result_count") for s in c.get("searches", []) if s.get("result_count") is not None}
    return {str(x) for x in f if x is not None}

def validate(K, target):
    D, ed = K["D"], K["edition"]
    w = edition_window(ed)
    clinics = K["cohort"]["clinics"]
    need([c["alias"] for c in clinics] == ALIASES, "cohort must be the five selected clinics in order: " + ", ".join(ALIASES))
    need({c["alias"]: c["name"] for c in clinics} == NAMES, "cohort clinic names changed")
    ok = {}
    for r in K["log"]:
        if r.get("status") == 200 and r.get("saved"): ok[r["final_url"]] = r
    O = {}
    for o in K["obs"]:
        need(o["id"] not in O, "duplicate observation id " + o["id"])
        need(o["clinic"] in ALIASES and o["kind"] in KINDS, "bad clinic or kind in " + o["id"])
        r = ok.get(o["source_url"]); need(r is not None, f"{o['id']}: source not in the fetch log with HTTP 200")
        need(after_window(r["fetched_utc"], w), f"{o['id']}: fetched before the window ended")
        if o["evidence"] == "text":
            need(re.sub(r"\s+", " ", o["excerpt"]) in page_text(D, r), f"{o['id']}: excerpt not found in the saved page text")
        elif o["evidence"] == "html":
            need(o["excerpt"] in gzip.open(HERE / r["saved"]).read().decode("utf8", "replace"), f"{o['id']}: excerpt not in the saved page source")
        else:
            need(o["kind"] == "absence" and not o["excerpt"], f"{o['id']}: only an absence may have no excerpt")
        need(urlparse(o["source_url"]).netloc.replace("www.", "") == next(c["domain"] for c in clinics if c["alias"] == o["clinic"]),
             f"{o['id']}: source is not on the clinic's official domain")
        o["_rec"] = r; O[o["id"]] = o
    ADR = validate_ads(K, w)
    validate_social(K, w)
    POSTS = {p["shortcode"]: p for p in K["social"]["posts"]}
    F = facts(K)
    partial = K["social"]["status"] != "collected"

    def ref(i):
        if i.startswith("ad:"):
            need(i[3:] in ADR, f"unknown ad record {i}"); a, plat, r = ADR[i[3:]]
            b = K["batches"][r["screenshot"].split("/")[1]]
            hay = " ".join([r["text"], " ".join(date_forms(v) for v in (r["platform_dates"][k] for k in ("started", "ended", "last_shown")) if v)]
                           + ([norm((b["R"] / r["text_basis"]).read_text())] if r["text_basis"].startswith("pages/") else []))
            return a, hay
        if i.startswith("ig:"):
            need(i[3:] in POSTS, f"unknown post {i}"); p = POSTS[i[3:]]
            raw = K["batches"][p["screenshot"].split("/")[1]]["ig"][p["shortcode"]]
            return p["clinic"], (raw["og_title"] or "") + " " + date_forms(toronto(p["published_utc"]).date().isoformat())
        need(i in O, f"unknown observation {i}"); return O[i]["clinic"], page_text(D, O[i]["_rec"])

    def cites(ids, clinic=None, where=""):
        need(ids, where + ": cites no evidence")
        for i in ids:
            c, _ = ref(i)
            if clinic: need(c == clinic, f"{where}: {i} belongs to another clinic")
        return ids

    def digits_ok(text, ids, where):
        hay = " ".join(ref(i)[1] for i in ids)
        for num in re.findall(r"\$?\d[\d,]*(?:\.\d+)?%?", text):
            need(num in hay or num in F, f"{where}: the figure {num} does not appear in a cited source or a computed count")

    def voice(text, where):
        need("—" not in text and "–" not in text, where + ": em or en dash")
        need(not re.search(r"\b(we|our|ours|us)\b", text, re.I), where + ": HMM voice is first person singular, never we/our/us")
        low = text.lower()
        for b in BANNED: need(b not in low, f"{where}: banned wording '{b}'")
        if partial: need(not FREQUENCY.search(text), f"{where}: frequency or complete-window claim while Instagram coverage is not confirmed")

    def takeaway(t, where):
        need(isinstance(t, str) and t.strip(), where + ": missing 'What this means for your clinic' takeaway")
        n = len([s for s in re.split(r"(?<=[.!?])\s+", t.strip()) if s])
        need(2 <= n <= 3, f"{where}: takeaway must be two or three sentences ({n})")
        need(re.search(r"\b(ask|test|measure|check)\b", t, re.I), where + ": takeaway needs one question for the team or one test")

    N = K["nar"]
    all_ids = [o for o in O] + ["ad:" + k for k in ADR] + ["ig:" + k for k in POSTS]
    voice(N["summary"], "summary"); digits_ok(N["summary"], all_ids, "summary")
    Fd = N["findings"]; need(1 <= len(Fd) <= 4, "What stood out: one to four findings")
    for i, f in enumerate(Fd, 1):
        w_ = f"finding {i}"; cites(f["obs"], where=w_)
        for k in ("title", "text", "limitation", "takeaway"):
            voice(f[k], w_); digits_ok(f[k], f["obs"], w_)
        takeaway(f["takeaway"], w_)
    A = N["accounts"]; need(set(A) == set(ALIASES), "one account analysis per clinic")
    for a in ALIASES:
        x = A[a]; w_ = "account " + a
        if x.get("ad_note"):
            cites(x["ad_note"]["obs"], a, w_ + " ad note"); voice(x["ad_note"]["text"], w_); digits_ok(x["ad_note"]["text"], x["ad_note"]["obs"], w_ + " ad note")
        if x.get("pending"):
            need(x.get("reason"), w_ + ": pending account needs a reason"); voice(x["reason"], w_); continue
        cites(x["obs"], a, w_)
        for k in ("positioning", "observed", "supports", "unknown", "takeaway"):
            need(x.get(k), f"{w_}: missing {k}"); voice(x[k], w_); digits_ok(x[k], x["obs"], w_)
        takeaway(x["takeaway"], w_)
        pn = x.get("price_note")
        if pn:
            for row in pn["rows"]:
                cites(row["obs"], a, w_ + " price note")
                for k in ("label", "wording", "scope"): voice(row[k], w_ + " price note"); digits_ok(row[k], row["obs"], w_ + " price note")
            for k in ("title", "reading"): voice(pn[k], w_ + " price note"); digits_ok(pn[k], [i for r in pn["rows"] for i in r["obs"]], w_ + " price note")
    for i, p in enumerate(N["patterns"], 1):
        w_ = f"pattern {i}"; cites(p["obs"], where=w_)
        for k in ("title", "text", "takeaway"):
            voice(p[k], w_); digits_ok(p[k], p["obs"], w_)
        takeaway(p["takeaway"], w_)
    T = N["tests"]; need(len(T) == 3, "exactly three practical tests")
    for i, t in enumerate(T, 1):
        for k in ("title", "evidence", "hypothesis", "change", "constant", "measure", "guardrails", "compare", "insufficient"):
            need(t.get(k), f"test {i}: missing {k}"); voice(t[k], f"test {i}")
            need(not re.search(r"\d", t[k]) or k == "title", f"test {i} {k}: no invented baselines, targets or lifts (no figures)")
        need(re.search(r"\(finding [1-4]\)$", t["title"]), f"test {i}: title must end with (finding N)")
    for p in K["social"]["posts"]:
        if p["implant_relevance"] == "yes":
            need(p.get("why"), f"post {p['shortcode']}: an implant example needs a reason it was chosen")
            voice(p["why"], "post " + p["shortcode"]); digits_ok(p["why"], ["ig:" + p["shortcode"]], "post " + p["shortcode"])
    for k, (a, plat, r) in ADR.items():
        if r["treatment"]["implant_related"] == "yes":
            need(r.get("summary"), f"ad {k}: an implant record shown on the page needs a summary")
            voice(r["summary"], "ad " + k); digits_ok(r["summary"], ["ad:" + k], "ad " + k)
    for a in ("dundas", "bond"):
        if A[a].get("pending"): need(A[a].get("method_note"), f"account {a}: pending account needs a method note"); voice(A[a]["method_note"], "account " + a)
    for a, x in K["ads"]["checks"].items():
        for plat in ("meta", "google"):
            c = x[plat]
            if c["status"] != "not_checked":
                ids = ["ad:" + r["id"] for r in c["records"]] or []
                voice(c["summary"], f"ads {a} {plat}")
                hay_ids = ids
                for num in re.findall(r"\$?\d[\d,]*(?:\.\d+)?%?", c["summary"]):
                    need(num in F or any(num in ref(i)[1] for i in hay_ids) or any(num in str(s.get("result", "")) for s in c["searches"]), f"ads {a} {plat} summary: figure {num} not traceable")
    C = K["cmp"]["rows"]; need(set(C) == set(ALIASES), "comparison needs one row per clinic")
    for a in ALIASES:
        row = C[a]
        if row.get("status") == "not_confirmed":
            need(N["accounts"][a].get("pending"), f"comparison {a}: not confirmed while the account analysis is written"); continue
        for col in K["cmp"]["columns"]:
            cell = row[col["key"]]; voice(cell["text"], f"comparison {a}"); cites(cell["obs"], a, f"comparison {a} {col['key']}")
            digits_ok(cell["text"], cell["obs"], f"comparison {a}")
    for a, h in K["social"]["handles"].items():
        if h["status"] == "verified_link":
            o = O[h["source_obs"]]; need(o["clinic"] == a and f"instagram.com/{h['handle']}/" in o["excerpt"], f"social {a}: handle not backed by its source")
    voice(K["social"]["public_reason"], "social public reason")
    if target == "release":
        rep = release_report(K)
        blockers = rep["core_evidence_gaps"] + rep["unreviewed_coverage_gaps"] + rep["checks_awaiting_execution"]
        need(not blockers, "release refused: " + "; ".join(blockers))
    return O

def release_report(K):
    """Release status by category. Only the first three categories block a release; missing optional metrics and completed
    searches with no matching ads are reported, never treated as errors."""
    N, S, A, ed = K["nar"], K["social"], K["ads"]["checks"], K["edition"]
    reviewed = {(r["clinic"], r["gap"]) for r in ed.get("reviewed_limitations", [])}
    core, cov, opt, nomatch, awaiting = [], [], [], [], []
    for a in ALIASES:
        if N["accounts"][a].get("pending"): core.append(f"{NAMES[a]}: official website not reviewed")
        if S["handles"][a]["status"] != "verified_link": core.append(f"{NAMES[a]}: Instagram handle not verified")
        for plat in ("meta", "google"):
            c = A[a][plat]
            if c.get("identity") and "uncertain" in json.dumps(c["identity"]): core.append(f"{NAMES[a]}: clinic identity behind the advertised domain is uncertain ({plat})")
            if c["status"] == "not_checked": awaiting.append(f"{NAMES[a]}: {plat} advertising check not run")
            if c["status"] == "access_blocked": awaiting.append(f"{NAMES[a]}: {plat} advertising check blocked")
            if c["status"] == "no_matching_ads_found": nomatch.append(f"{NAMES[a]}: {plat} documented search found no matching ads")
        st = S.get("coverage", {}).get(a, {}).get("status", "not_collected" if S["status"] == "not_collected" else None)
        if S["handles"][a]["status"] == "verified_link" and st != "confirmed_complete" and (a, "instagram_coverage") not in reviewed:
            cov.append(f"{NAMES[a]}: Instagram coverage {st}")
    missing_plays = sum(1 for p in S.get("posts", []) if p["metrics"]["plays"] is None)
    if missing_plays: opt.append(f"plays not shown for {missing_plays} of {len(S['posts'])} posts (logged-out view); not a data error")
    if ed.get("status") != "ready": awaiting.append("founder review: edition.json status is not 'ready'")
    if not ed.get("forms_script_research_dental_deployed"): awaiting.append("forms script with research_dental not confirmed deployed")
    return {"core_evidence_gaps": core, "unreviewed_coverage_gaps": cov, "missing_optional_metrics": opt,
            "completed_searches_no_match": nomatch, "checks_awaiting_execution": awaiting}

def link_label(u):
    p = urlparse(u); path = p.path.strip("/")
    if p.netloc.endswith("facebook.com"): return "Meta Ad Library record " + re.search(r"id=(\d+)", u)[1]
    if p.netloc == "adstransparency.google.com": return "Google Ads Transparency creative " + path.split("/")[-1][-6:]
    if p.netloc.endswith("instagram.com"): return "instagram.com/" + path
    return p.netloc.replace("www.", "") + ("/" + path if path else " home page")

def render(K, O, target, published=None, modified=None):
    D, N, C, S, AD = K["D"], K["nar"], K["cmp"], K["social"], K["ads"]["checks"]
    ed = K["edition"]["edition"]; draft = target != "release"
    clin = {c["alias"]: c for c in K["cohort"]["clinics"]}
    ADR = ad_records(K); POSTS = {p["shortcode"]: p for p in S["posts"]}
    web_times = sorted(o["_rec"]["fetched_utc"] for o in O.values())
    w_first, w_last = toronto(web_times[0]), toronto(web_times[-1])
    win = edition_window(K["edition"])
    W = f"{long_date(win[0])} to {long_date(win[1])}"
    web_when = f"{long_date(w_first)}, {clock(w_first)} to {clock(w_last)} Toronto time"
    browser = next((b for b in K["edition"].get("evidence_batches", []) if b["batch"].startswith("browser")), None)
    bl = sorted(r["started_utc"] for b in K["batches"].values() for r in b["load"].values())
    b_first, b_last = (toronto(bl[0]), toronto(max(bl[-1], max(p["observed_utc"] for p in S["posts"])))) if bl else (None, None)
    br_when = f"{long_date(b_first)}, {clock(b_first)} to {clock(b_last)} Toronto time" if b_first else None
    handles = S["handles"]; partial = S["status"] != "collected"

    def url_of(i):
        if i.startswith("ad:"): return ADR[i[3:]][2]["url"]
        if i.startswith("ig:"): return POSTS[i[3:]]["url"]
        return O[i]["source_url"]

    def source_links(ids):
        seen, out = [], []
        for i in ids:
            u = url_of(i)
            if u in seen: continue
            seen.append(u); out.append(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(link_label(u))}</a>')
        return ", ".join(out)

    def sources_html(ids):
        return '<p class="pnote dx-src"><b>Sources:</b> ' + source_links(ids) + "</p>"

    def take_html(t):
        return f'<div class="note take"><span class="lbl">{TAKE}</span><p>{E(t)}</p></div>'

    def ig(a):
        h = handles[a]
        return (f'<a href="https://www.instagram.com/{E(h["handle"])}/" target="_blank" rel="noopener">@{E(h["handle"])}</a>' if h["handle"] else "Not verified")

    def when(ts):
        t = toronto(ts); return f"{long_date(t)}, {clock(t)} Toronto time"

    def pdate(r):
        pd = r["platform_dates"]
        if r["platform"] == "meta":
            s = f'{pd["status_at_observation"].capitalize()} when observed; library start date {long_date(date.fromisoformat(pd["started"]))}'
            return s + (f'; ended {long_date(date.fromisoformat(pd["ended"]))}' if pd["ended"] else "")
        return f'Last shown {long_date(date.fromisoformat(pd["last_shown"]))} (Pacific Time)'

    used = sorted({i for f in N["findings"] for i in f["obs"]} | {i for a in N["accounts"].values() for i in a.get("obs", [])} |
                  {i for p in N["patterns"] for i in p["obs"]} | {i for r in C["rows"].values() for k, c in r.items() if isinstance(c, dict) for i in c.get("obs", [])} |
                  {i for a in N["accounts"].values() if a.get("price_note") for r in a["price_note"]["rows"] for i in r["obs"]})
    used = [i for i in used if i in O]
    n_posts, n_ads = len(S["posts"]), len(ADR)
    sample_line = (f"{n_posts} posts observed on {sum(1 for a in ALIASES if any(p['clinic'] == a for p in S['posts']))} accounts, incomplete sample" if partial else f"{n_posts} posts")
    b = []
    status_line = "Draft for review" if draft else f"Published {long_date(datetime.fromisoformat(published).astimezone(TZ))}"
    b.append('<div class="wrap">')
    b.append('<header class="dx-head"><p class="kicker">The HMM Index &middot; Dental implants</p><h1>Dental Implant Marketing Index</h1>')
    b.append('<p class="lede">How five selected Ontario dental clinics in the Greater Toronto Area present and promote implant consultations, '
             'what an owner can compare against their own clinic, and three tests to discuss with a marketing team. A study of published marketing, '
             'not a ranking of clinics or a judgement of clinical care.</p>')
    b.append(f'<div class="byline"><span><b>Observation window</b> {W}</span><span>For dental practice owners reviewing their implant marketing.</span>'
             '<span>Research and analysis by <b><a href="/about">Ankit Kumar</a></b> &middot; Founder, <a href="/">HMM</a></span></div>')
    b.append(f'<div class="livebar"><span>Websites checked <b>{E(web_when)}</b></span><span>Instagram <b>{E(sample_line if n_posts else "not collected yet")}</b></span>'
             f'<span>Ad libraries checked <b>{E(long_date(b_first)) if b_first else "not yet"}</b></span><span>Edition <b>{ed}</b></span><span><b>{status_line}</b></span></div>')
    b.append('<div class="dx-actions"><a class="btn btn-primary" href="#dx-compare">See the five clinics</a><a class="btn btn-outline" href="#dx-tests">Explore the three tests</a></div></header>')
    if draft:
        b.append('<div class="note warn"><span class="lbl">Draft, not published</span><p>This page is a draft for review and is hidden from search engines. '
                 'Two of the five clinic websites could not be read, so findings about websites rest on three clinics. Instagram evidence is an incomplete sample from two accounts, '
                 'and advertising evidence comes from public ad libraries, which show what ran, not how it performed. Missing evidence is shown as missing, never as zero.</p></div>')
    b.append('<nav class="ri-nav" aria-label="On this page"><a href="#dx-findings">What stood out</a><a href="#dx-compare">Comparison</a>'
             '<a href="#dx-examples">Content examples</a><a href="#dx-ads">Advertising</a><a href="#dx-accounts">Each clinic</a><a href="#dx-patterns">Patterns</a>'
             '<a href="#dx-tests">Tests to run</a><a href="#dx-method">Method</a></nav>')
    b.append(f'<section id="dx-answer"><div class="card"><h2 class="dx-h">The short answer</h2><p class="dek m0">{E(N["summary"])}</p></div></section>')

    b.append('<section id="dx-findings"><div class="sec-head"><h2>What stood out</h2>'
             '<p class="dek">Findings from the published implant pages, consultation offers and enquiry forms of the three clinics whose websites I could read, '
             'with the Instagram posts and ad library records observed for the same clinics. Each names its examples and the limitation needed to read it; none claims that a feature caused better results.</p></div>')
    for i, f in enumerate(N["findings"], 1):
        b.append(f'<div class="card"><h3>{i}. {E(f["title"])}</h3><p class="dek">{E(f["text"])}</p>'
                 f'<p class="dek dx-lim"><b>Limitation.</b> {E(f["limitation"])}</p>{sources_html(f["obs"])}{take_html(f["takeaway"])}</div>')
    b.append("</section>")

    def ig_cell(a):
        h = handles[a]; cov = S.get("coverage", {}).get(a, {})
        if not h["handle"]: return 'Not verified<span class="cell-sub">Handle not confirmed; no account assumed</span>'
        if cov.get("status") == "blocked": return f'{ig(a)}<span class="cell-sub">Not read: request refused</span>'
        ps = [p for p in S["posts"] if p["clinic"] == a]
        if not ps: return f'{ig(a)}<span class="cell-sub">Posts not collected</span>'
        k = sum(p["implant_relevance"] == "yes" for p in ps); u = sum(p["implant_relevance"] == "unclear" for p in ps)
        return (f'{ig(a)}<span class="cell-sub">{len(ps)} posts observed in the window, {k} about implants' + (f", {u} unclear" if u else "") +
                ('; incomplete sample' if cov.get("status") != "confirmed_complete" else "") + '</span>')

    def ad_cell(a, plat):
        c = AD[a][plat]; rs = [r for r in c.get("records", []) if r["treatment"]["category"] != "not_treatment_marketing"]
        st = E(AD_STATUS[c["status"]])
        if not rs: return st
        att = [r for r in rs if r["attribution"]["confidence"] != "uncertain"]; unc = len(rs) - len(att)
        impl = sum(r["treatment"]["implant_related"] == "yes" for r in rs)
        inwin = sum(r["window_relation"] in ("active_at_observation_started_before_window", "active_at_observation_started_in_window", "shown_in_window") for r in rs)
        hist = sum(r["window_relation"] == "historical_before_window" for r in rs)
        kind = "ad cards" if plat == "meta" else "creatives"
        parts = [f"{len(rs)} {kind}, {impl} about implants"]
        if inwin: parts.append(f"{inwin} active or shown in the window")
        if hist: parts.append(f"{hist} historical only")
        if unc: parts.append(f"{unc} not attributable to the clinic")
        return f'{st}<span class="cell-sub">{E("; ".join(parts))}</span>'

    cols = C["columns"]
    b.append('<section id="dx-compare"><div class="sec-head"><h2>Five-clinic comparison</h2>'
             '<p class="dek">The same definitions for every clinic. &ldquo;Not confirmed&rdquo; means the evidence could not be collected yet; '
             '&ldquo;Not checked&rdquo; means the check has not run; &ldquo;No matching ads found&rdquo; describes one documented search, not a clinic&rsquo;s whole advertising. '
             'Listed on a website is not the same as tested and working. Counts describe what was observed, not performance. On a phone, each clinic is shown as a card.</p></div>')
    b.append('<div class="tw cards" tabindex="0" role="region" aria-label="Five-clinic comparison table"><table class="cmp dx-cmp">'
             f'<caption class="sr-only">Implant marketing of five selected Ontario dental clinics, websites checked {E(long_date(w_first))}</caption><thead><tr><th scope="col">Clinic</th>')
    for c in cols: b.append(f'<th scope="col">{E(c["label"])}</th>')
    b.append('<th scope="col">Instagram, observed posts</th><th scope="col">Meta Ad Library</th><th scope="col">Google Ads Transparency</th></tr></thead><tbody>')
    for a in ALIASES:
        row = C["rows"][a]
        b.append(f'<tr><th scope="row" class="brandcell"><a href="{E(clin[a]["official_url"])}" target="_blank" rel="noopener">{E(NAMES[a])}</a><span class="handle">{E(clin[a]["city"])}</span></th>')
        for c in cols:
            if row.get("status") == "not_confirmed":
                b.append(f'<td class="wrap-cell dx-miss" data-label="{E(c["label"])}">Not confirmed<span class="cell-sub">{E(row["reason"])}</span></td>')
            else:
                cell = row[c["key"]]; src = O[cell["obs"][0]]["source_url"]
                b.append(f'<td class="wrap-cell" data-label="{E(c["label"])}">{E(cell["text"])}<span class="cell-sub"><a href="{E(src)}" target="_blank" rel="noopener" aria-label="Source for {E(NAMES[a])}, {E(c["label"])} (opens the clinic page)">Source</a></span></td>')
        b.append(f'<td class="wrap-cell" data-label="Instagram, observed posts">{ig_cell(a)}</td>')
        for plat, lab in (("meta", "Meta Ad Library"), ("google", "Google Ads Transparency")):
            b.append(f'<td class="wrap-cell" data-label="{lab}">{ad_cell(a, plat)}</td>')
        b.append("</tr>")
    b.append("</tbody></table></div>")
    b.append(f'<p class="pnote"><b>Definitions.</b> Positioning, cost, consultation, proof and enquiry entries come from the official clinic pages checked on {E(web_when)}; '
             'they describe the pages at that time, not throughout the window. '
             '&ldquo;Published cost information&rdquo; means a price or range printed by the clinic; it is not a quote and inclusions differ, so figures are not comparable between clinics. '
             'Clinic statements about outcomes or experience are reported as the clinic&rsquo;s claims. Forms were read, never submitted. '
             f'Instagram counts are posts observed in an incomplete sample, never totals. Ad counts are the records shown by each library for the documented search on {E(long_date(b_first)) if b_first else "the check date"}.</p>')
    b.append(f'<p class="pnote dlinks"><b>Download the data:</b> <a href="/assets/index/dental/dental-index-edition-{ed}-observations.csv">the {len(used)} website observations used on this page (CSV)</a> &middot; '
             f'<a href="/assets/index/dental/dental-index-edition-{ed}-ads.csv">the {n_ads} ad library records (CSV)</a> &middot; '
             f'<a href="/assets/index/dental/dental-index-edition-{ed}-instagram.csv">the {n_posts} observed Instagram posts (CSV)</a>.</p></section>')

    # Instagram examples
    order = lambda p: (ALIASES.index(p["clinic"]), p["published_utc"])
    imp = sorted([p for p in S["posts"] if p["implant_relevance"] == "yes"], key=order)
    b.append('<section id="dx-examples"><div class="sec-head"><h2>Observed content examples</h2>'
             f'<p class="dek">Implant posts from the observation window, {W}, chosen because they are the implant posts in the sample. '
             'They come from an incomplete sample read in a logged-out browser, so they are examples, not every post an account published. '
             'Videos were not watched: each reading uses the caption and whatever part of the cover was visible. Likes and comments are public counts when observed, at different post ages; plays were not shown.</p></div>')
    b.append('<div class="dx-phs">')
    for p in imp:
        pub = toronto(p["published_utc"]); age = (toronto(p["observed_utc"]).date() - pub.date()).days
        m = p["metrics"]
        b.append(f'<div class="card dx-ex"><p class="kicker">{E(NAMES[p["clinic"]])} &middot; {E(long_date(pub))} &middot; {"Reel" if p["format"] == "reel" else "Image post"}</p>'
                 f'<p class="dek"><b>{E(p["topic"])}.</b> {E(p.get("why", ""))}</p>'
                 f'<p class="pnote m0"><b>Call to action:</b> {E(p["cta"])}. <b>Cover:</b> {E(p["cover"])}.</p>'
                 f'<p class="pnote m0"><b>When observed ({age} days after posting):</b> {m["likes"]} likes, {m["comments"]} comments, plays not shown.</p>'
                 f'<p class="pnote dx-src"><a href="{E(p["url"])}" target="_blank" rel="noopener">View the post on Instagram</a></p></div>')
    for a in ALIASES:
        if any(p["clinic"] == a for p in imp): continue
        h = handles[a]; cov = S.get("coverage", {}).get(a, {})
        why = ("no implant post appeared among the posts observed from " + ig(a) + "." if any(p["clinic"] == a for p in S["posts"]) else
               "posts from " + ig(a) + " could not be read (request refused)." if cov.get("status") == "blocked" else
               "the Instagram account has not been verified yet." if not h["handle"] else "posts from " + ig(a) + " have not been collected.")
        b.append(f'<div class="card dx-ph"><p class="kicker">{E(NAMES[a])}</p><p class="dek m0">Example pending: {why}</p></div>')
    b.append('</div>')
    if S["posts"]:
        b.append('<h3 class="dx-h3">The observed sample</h3><div class="tw cards" tabindex="0" role="region" aria-label="Observed Instagram posts"><table class="cmp dx-cmp">'
                 '<caption class="sr-only">Instagram posts observed in the window, by clinic</caption><thead><tr><th scope="col">Clinic</th><th scope="col">Date</th><th scope="col">Format</th>'
                 '<th scope="col">Topic</th><th scope="col">About implants</th><th scope="col">Likes</th><th scope="col">Comments</th><th scope="col">Plays</th><th scope="col">Post</th></tr></thead><tbody>')
        for p in sorted(S["posts"], key=order):
            m = p["metrics"]
            b.append(f'<tr><th scope="row" class="brandcell">{E(NAMES[p["clinic"]])}</th><td data-label="Date">{E(long_date(toronto(p["published_utc"])))}</td>'
                     f'<td data-label="Format">{"Reel" if p["format"] == "reel" else "Image post"}</td><td class="wrap-cell" data-label="Topic">{E(p["topic"])}</td>'
                     f'<td data-label="About implants">{E(p["implant_relevance"].capitalize())}</td><td data-label="Likes">{m["likes"] if m["likes"] is not None else "Not shown"}</td>'
                     f'<td data-label="Comments">{m["comments"] if m["comments"] is not None else "Not shown"}</td><td class="dx-miss" data-label="Plays">{m["plays"] if m["plays"] is not None else "Not shown"}</td>'
                     f'<td data-label="Post"><a href="{E(p["url"])}" target="_blank" rel="noopener" aria-label="Open the {E(NAMES[p["clinic"]])} post of {E(long_date(toronto(p["published_utc"])))} on Instagram">Open</a></td></tr>')
        b.append('</tbody></table></div>')
    b.append(f'<div class="note warn"><span class="lbl">How complete this is</span><p>{E(S["public_reason"])}</p></div></section>')

    # Advertising
    b.append('<section id="dx-ads"><div class="sec-head"><h2>Advertising in public ad libraries</h2>'
             f'<p class="dek">What Meta Ad Library and Google Ads Transparency Center showed for each clinic when checked on {E(br_when) if br_when else "the check date"}. '
             'Each record keeps apart who paid for the ad, how confidently it can be tied to the clinic, the treatment it promotes and when the platform says it ran. '
             'Public libraries show that an ad ran, not its budget, audience or results, and nothing here estimates them.</p></div>')
    b.append('<div class="card"><h3>Per clinic</h3><ul class="dx-adlist">')
    for a in ALIASES:
        for plat, lab in (("meta", "Meta Ad Library"), ("google", "Google Ads Transparency")):
            c = AD[a][plat]
            b.append(f'<li><b>{E(NAMES[a])}, {lab}: {E(AD_STATUS[c["status"]])}.</b> {E(c.get("summary") or c.get("reason", ""))}</li>')
    b.append('</ul></div>')
    impl_recs = [ADR[k][2] for k in ADR if ADR[k][2]["treatment"]["implant_related"] == "yes"]
    b.append('<h3 class="dx-h3">Every implant ad record found</h3><div class="tw cards" tabindex="0" role="region" aria-label="Implant ad records"><table class="cmp dx-cmp">'
             '<caption class="sr-only">Implant-related ad records, with attribution and dates</caption><thead><tr><th scope="col">Clinic searched</th><th scope="col">Platform</th>'
             '<th scope="col">Advertiser</th><th scope="col">Tied to the clinic</th><th scope="col">What it shows</th><th scope="col">Platform dates</th><th scope="col">Relation to the window</th></tr></thead><tbody>')
    for r in sorted(impl_recs, key=lambda r: (ALIASES.index(r["attribution"]["clinic"]), r["platform"], r["id"])):
        a = r["attribution"]["clinic"]
        b.append(f'<tr><th scope="row" class="brandcell">{E(NAMES[a])}</th><td data-label="Platform">{"Meta" if r["platform"] == "meta" else "Google"}</td>'
                 f'<td class="wrap-cell" data-label="Advertiser">{E(r["advertiser"]["name"])}</td>'
                 f'<td class="wrap-cell" data-label="Tied to the clinic">{E(CONFIDENCE[r["attribution"]["confidence"]])}<span class="cell-sub">{E(r["attribution"]["basis"])}</span></td>'
                 f'<td class="wrap-cell" data-label="What it shows">{E(r["summary"])}'
                 f'<span class="cell-sub"><a href="{E(r["url"])}" target="_blank" rel="noopener">{E(link_label(r["url"]))}</a></span></td>'
                 f'<td class="wrap-cell" data-label="Platform dates">{E(pdate(r))}</td><td class="wrap-cell" data-label="Relation to the window">{E(RELATIONS[r["window_relation"]])}</td></tr>')
    b.append('</tbody></table></div>')
    b.append('<p class="pnote"><b>How to read this.</b> Confirmed: the advertiser or destination is the clinic&rsquo;s own. Supported: the ad names the clinic, its dentist or its location, '
             'but the link was not confirmed on the clinic&rsquo;s site. Uncertain: the ad cannot be tied to the clinic from what it shows. Meta shows a start date and whether an ad was running when checked; '
             'Google shows the last date an ad was shown. Neither shows delivery day by day, so &ldquo;active when observed&rdquo; does not mean the ad ran throughout the window, '
             'and historical ads are examples of past activity only. The full list of records, including ads for other treatments, is in the ad records download.</p></section>')

    b.append('<section id="dx-accounts"><div class="sec-head"><h2>Clinic by clinic</h2>'
             '<p class="dek">For each clinic: its implant positioning, what its website, observed posts and ad records show, what that evidence supports, what remains unknown, and what it means for your clinic. '
             'Observations come from the pages and records; interpretations are mine and are labelled as such. None of these clinics is an HMM client.</p></div>')
    for a in ALIASES:
        x = N["accounts"][a]
        b.append(f'<div class="card acct" id="dx-{a}"><h3>{E(NAMES[a])} <span class="handle">({ig(a) if handles[a]["handle"] else "Instagram not verified"})</span></h3>')
        if x.get("pending"):
            b.append(f'<div class="note warn"><span class="lbl">Website evidence pending</span><p>{E(x["reason"])}</p></div>')
            if x.get("ad_note"):
                b.append(f'<div class="note"><span class="lbl">Ad library records only</span><p>{E(x["ad_note"]["text"])}</p></div>{sources_html(x["ad_note"]["obs"])}')
            b.append(f'<div class="note take dx-pending"><span class="lbl">{TAKE}</span><p>Not written yet. A takeaway will be added only after this clinic&rsquo;s website has been reviewed.</p></div></div>')
            continue
        for lab, k in (("Positioning", "positioning"), ("Observed marketing", "observed"), ("What the evidence supports", "supports"), ("What remains unknown", "unknown")):
            b.append(f'<p class="dek"><b>{lab}.</b> {E(x[k])}</p>')
        pn = x.get("price_note")
        if pn:
            b.append(f'<div class="note dx-price"><span class="lbl">{E(pn["title"])}</span><dl class="dx-dl">')
            for row in pn["rows"]:
                ids = row["obs"]; ts = [O[i]["_rec"]["fetched_utc"] if i in O else ADR[i[3:]][2]["observed_utc"] for i in ids]
                b.append(f'<dt>{E(row["label"])}</dt><dd>{E(row["wording"])} {E(row["scope"])} <span class="cell-sub">Observed {E(when(min(ts)))}. Source: {source_links(ids)}</span></dd>')
            b.append(f'</dl><p class="m0">{E(pn["reading"])}</p></div>')
        b.append(sources_html(x["obs"]) + take_html(x["takeaway"]) + "</div>")
    b.append("</section>")

    b.append('<section id="dx-patterns"><div class="sec-head"><h2>Across the clinics</h2>'
             '<p class="dek">The same dimensions compared across the clinics I could read. These are observations from selected clinics, not patterns in Ontario dentistry.</p></div>')
    for p in N["patterns"]:
        b.append(f'<div class="card"><h3>{E(p["title"])}</h3><p class="dek">{E(p["text"])}</p>{sources_html(p["obs"])}{take_html(p["takeaway"])}</div>')
    b.append("</section>")

    b.append('<section id="dx-tests"><div class="sec-head"><h2>Three practical tests</h2>'
             '<p class="dek">Each test comes from a finding above and is measured with your own records. There are no baselines, targets or expected lifts here: '
             'what counts as a change depends on your own numbers. A before-and-after comparison is not a controlled split test, and lead outcomes need equal follow-up time.</p></div>')
    labels = [("evidence", "Evidence that prompted it"), ("hypothesis", "Hypothesis"), ("change", "The one change"), ("constant", "What stays the same"),
              ("measure", "Primary measure"), ("guardrails", "Guardrails"), ("compare", "How and when to compare"), ("insufficient", "Not enough evidence if")]
    for i, t in enumerate(N["tests"], 1):
        b.append(f'<div class="card dx-test" id="dx-test-{i}"><h3>Test {i}. {E(t["title"])}</h3><dl class="dx-dl">')
        for k, lab in labels: b.append(f"<dt>{lab}</dt><dd>{E(t[k])}</dd>")
        b.append("</dl></div>")
    b.append("</section>")

    def ad_li(a, plat, name):
        x = AD[a][plat]
        if x["status"] == "not_checked":
            links = " &middot; ".join(f'<a href="{E(u)}" target="_blank" rel="noopener">prepared search</a>' for u in x.get("prepared_urls", []))
            return f'<li>{E(NAMES[a])}, {name}: Not checked. {links}</li>'
        ss = "; ".join(f'<a href="{E(s["url"])}" target="_blank" rel="noopener">{E(s["terms"])}</a> ({E(s["filters"])}; {E(s.get("result") or str(s.get("result_count")) + " ads")})' for s in x["searches"])
        return f'<li>{E(NAMES[a])}, {name}: {E(AD_STATUS[x["status"]])}. Searched {E(when(x["searched_at"]))}: {ss}. Limits: {E(" ".join(x["limits"]))}</li>'
    b.append('<section id="dx-method"><div class="sec-head"><h2>Method, sources and limitations</h2>'
             '<p class="dek">How the evidence was collected, what was left out and why. This research assesses published marketing, not clinical quality, treatment outcomes or patient suitability.</p></div>')
    b.append('<section><details class="ri-adv"><summary>Why these five clinics</summary><p>Five Ontario clinics in or near the Greater Toronto Area that market dental implants, '
             'chosen by the founder for comparison. It is a selected group, not a sample of the market and not a ranking. North York Smile Centre and Smile By Design are the same practice and are counted once. '
             'Five further clinics are held in reserve for possible later editions and do not appear here.</p></details></section>')
    b.append(f'<section><details class="ri-adv"><summary>Dates, identity and pages reviewed</summary><p>Observation window: {W}, fixed for this edition: the 30 complete days in Toronto time before the first collection, '
             'recorded once and never moved by a later rebuild. '
             f'Websites were checked on {E(web_when)}; website evidence describes each page at that moment, not throughout the window. '
             + (f'Instagram, the ad libraries and the two blocked websites were checked on {E(br_when)} in a logged-out headless browser in a cloud workspace, with no login, saved cookies or paid collection. ' if br_when else "")
             + 'A clinic&rsquo;s identity, location and Instagram account come only from its official website; a dentist&rsquo;s personal account is never treated as the clinic&rsquo;s. '
             'Each page reviewed is saved with its fetch time and a fingerprint, and every quoted excerpt is checked against the saved page.</p><ul>')
    for a in ALIASES[:3]:
        urls = sorted({o["source_url"] for o in O.values() if o["clinic"] == a})
        b.append(f'<li>{E(NAMES[a])}: ' + ", ".join(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(urlparse(u).path.strip("/") or "home page")}</a>' for u in urls) + "</li>")
    for a in ("dundas", "bond"):
        b.append(f'<li>{E(NAMES[a])}: {E(N["accounts"][a]["method_note"])}</li>')
    b.append('</ul></details></section>')
    b.append('<section><details class="ri-adv"><summary>Instagram collection and implant content</summary><p>Each verified profile was opened once without logging in, and each grid item that appeared to fall inside the window was opened once. '
             'A post&rsquo;s date comes from the post page, and only posts published inside the window in Toronto time are kept. Clinic-owned and collaborator-owned posts are kept apart; '
             'hidden or restricted values stay missing rather than becoming zero. Posts are classified as implant, other treatments or unclear from the caption and the visible part of the cover; '
             'videos were not watched, so nothing is said about their spoken content or editing. Public likes and comments are cumulative when observed, at different post ages, '
             'and no engagement ranking is shown. Because completeness was not confirmed, no posting frequency or window total is given.</p>'
             f'<p class="m0"><b>Status in this draft.</b> {E(S["reason"])}</p></details></section>')
    b.append('<section><details class="ri-adv"><summary>Advertising checks</summary><p>Meta Ad Library (exact-phrase keyword searches, Canada, all ads, active and inactive) and Google Ads Transparency Center '
             '(domain searches, Canada, any time and the window) were checked separately for each clinic. An advertiser is tied to a clinic only where the ad itself, its page or its destination supports it; '
             'a group advertiser&rsquo;s ads are not credited to a clinic as a group. A documented search with no results does not mean a clinic never advertises, and nothing here estimates spend, reach, targeting or results.</p><ul>')
    for a in ALIASES:
        b.append(ad_li(a, "meta", "Meta Ad Library") + ad_li(a, "google", "Google Ads Transparency Center"))
    b.append("</ul></details></section>")
    b.append('<section><details class="ri-adv"><summary>What is not measured, and how to read the evidence</summary><p>Nothing on this page estimates advertising budgets, revenue, return on ad spend, cost per lead, '
             'consultation conversion, treatment acceptance, agency fees or appointment capacity; public pages cannot show them. A website credit to a marketing provider shows a published association, '
             'not a current contract, its value or its scope. A tracking script, pixel or separate phone number does not show that automation, retargeting or attribution works, and a stated response promise '
             'is not a measured response time. No form was submitted, no appointment booked, no photo uploaded and no clinic contacted.</p>'
             '<p class="m0">Each statement is labelled as an observation (what a page or record shows), a clinic claim (what a clinic says about itself, reported, not endorsed) or my interpretation.</p></details></section>')
    b.append('<section><details class="ri-adv"><summary>Corrections</summary><p class="m0">If a clinic detail, figure or source is wrong, email '
             '<a href="mailto:Hello@helpmemarketing.com">Hello@helpmemarketing.com</a> with the link and the correction. Confirmed corrections are made with a dated note.</p></details></section>')
    b.append('<div class="grid2"><div class="card"><h4>About the researcher</h4><p class="dek">Ankit Kumar is the founder of Help Me Marketing and works on performance marketing, conversion tracking '
             'and competitive research. He is a marketing researcher and practitioner, not a clinician, and none of these clinics is an HMM client. Through The HMM Index he analyses public marketing activity '
             'and explains its patterns and limits.</p><p class="dek m0"><a href="/about">About Ankit</a> &middot; <a href="/work">Explore HMM&rsquo;s work</a></p></div>')
    cite_tail = ("A fixed snapshot will be created when this edition is published." if draft else
                 f'For a fixed version, cite the <a href="{ROUTE}/edition-{ed}">edition {ed} snapshot</a>.')
    b.append(f'<div class="card" id="dx-cite"><h4>Cite this research</h4><p class="dek">Ankit Kumar, Help Me Marketing. <i>Dental Implant Marketing Index</i> (The HMM Index). Edition {ed}'
             f'{" (draft)" if draft else ""}. Observation window {W}; websites checked {E(long_date(w_first))}. <a href="{CANON}">{CANON}</a></p><p class="dek m0">{cite_tail}</p></div></div>')
    b.append('<section><div class="card"><h4>Related research</h4><p class="dek m0">Other editions of The HMM Index: <a href="/realestate-index">Real Estate Index</a> &middot; '
             '<a href="/medspa-index">Med Spa Index</a> &middot; <a href="/hair-loss-index">Hair Loss Index</a> &middot; <a href="/hmm-index">All Index research</a></p></div></section>')
    b.append("</section>")
    b.append('<section id="dx-help"><div class="sec-head"><h2>Review your implant enquiry journey</h2></div><div class="card"><p class="dek">This research shows what other clinics publish; '
             'it does not show how your own journey performs. If you would like a review of your implant enquiry journey, from the implant page and consultation offer to how enquiries are '
             'measured and followed up, <a href="/contact?intent=review&amp;entry=research_dental#contact-form" data-review-cta="research_dental">ask for a free marketing review</a>. '
             'Related services: <a href="/services/website-development" data-research-service="website-development">implant and landing pages</a>, '
             '<a href="/services/analytics-attribution" data-research-service="analytics-attribution">tracking from enquiry to consultation</a> and '
             '<a href="/services/ai-automation" data-research-service="ai-automation">enquiry follow-up</a>.</p>'
             '<a class="btn btn-primary" href="/contact?intent=review&amp;entry=research_dental#contact-form" data-review-cta="research_dental">Review my implant enquiry journey</a></div></section>')
    b.append(f'<footer><div class="about"><p><b>About this index.</b> The Dental Implant Marketing Index is part of <b>The HMM Index</b> by Help Me Marketing. Edition {ed} compares how five selected '
             'Ontario dental clinics present and promote implant consultations. It is not a ranking and does not measure clinical quality, bookings or revenue.</p></div><div class="byline-block">'
             '<p><b>Dental Implant Marketing Index</b> &middot; an instance of <b>The HMM Index</b> by HMM &middot; built and reviewed by <b>Ankit Kumar</b>, Founder, HMM</p>'
             f'<p>Websites checked <b>{E(long_date(w_first))}</b> &middot; edition <b>{ed}</b>{" &middot; draft" if draft else ""}</p>'
             '<p>Clinic names are used to report publicly available information and imply no relationship with Help Me Marketing.</p></div></footer></div>')
    body = "\n".join(b)

    title = "Dental Implant Marketing Index | HelpMeMarketing"
    desc = "How five selected Ontario dental clinics present implant consultations: pricing, consultation offers, proof and enquiry routes, with three tests to run."
    robots = "noindex, nofollow" if draft else "index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"
    og_t = "Dental Implant Marketing Index"
    meta = "\n".join([f"<title>{E(title)}</title>", f'<meta name="description" content="{E(desc)}">',
        '<link rel="preload" href="/assets/fonts/fraunces-latin.woff2" as="font" type="font/woff2" crossorigin>',
        '<link rel="preload" href="/assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>', '<link rel="stylesheet" href="/styles.css">',
        f'<link rel="canonical" href="{CANON}">', f'<meta name="robots" content="{robots}">', '<meta property="og:type" content="article">',
        '<meta property="og:site_name" content="HelpMeMarketing">', f'<meta property="og:title" content="{og_t}">', f'<meta property="og:description" content="{E(desc)}">',
        f'<meta property="og:url" content="{CANON}">', f'<meta property="og:image" content="{SITE}/og-image.jpg">', '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">', '<meta property="og:locale" content="en_CA">', '<meta property="article:author" content="Ankit Kumar">',
        '<meta name="twitter:card" content="summary_large_image">', f'<meta name="twitter:title" content="{og_t}">', f'<meta name="twitter:description" content="{E(desc)}">',
        f'<meta name="twitter:image" content="{SITE}/og-image.jpg">'])
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "The HMM Index", "item": SITE + "/hmm-index"},
        {"@type": "ListItem", "position": 3, "name": "Dental Implant Marketing Index", "item": CANON}]}
    art = {"@context": "https://schema.org", "@type": "Article", "headline": "Dental Implant Marketing Index", "description": desc, "image": SITE + "/og-image.jpg",
           "author": {"@type": "Person", "@id": SITE + "/about#ankit-kumar", "name": "Ankit Kumar", "url": SITE + "/about"},
           "publisher": {"@type": "Organization", "@id": SITE + "/#organization", "name": "Help Me Marketing", "url": SITE, "logo": SITE + "/logo.jpg"},
           "url": CANON, "isAccessibleForFree": True}
    if not draft: art["datePublished"], art["dateModified"] = published, modified
    jsonld = "\n".join(f'<script type="application/ld+json">\n{json.dumps(x, ensure_ascii=False, separators=(",", ":"))}\n</script>' for x in (crumbs, art))
    extra = (HERE / "head_dental.html").read_text(encoding="utf-8")
    shell = (HERE / "site_shell.html").read_text(encoding="utf-8")
    for tok in ("{{META}}", "{{JSONLD}}", "{{BODY}}", "{{HEAD_EXTRA}}"): need(shell.count(tok) == 1, "shell token " + tok)
    page = shell.replace("{{META}}", meta).replace("{{JSONLD}}", jsonld).replace("{{HEAD_EXTRA}}", extra).replace("{{BODY}}", body)
    return page, used

def check_page(page, draft, used, O, ed, K=None):
    need(len(re.findall(r"<h1[\s>]", page)) == 1, "page must have exactly one H1")
    body = page.split("DENTAL INDEX REPORT BODY START", 1)[1]
    need(" style=" not in body, "no inline style attributes in the body")
    need("—" not in body and "–" not in body and "&mdash;" not in body and "&ndash;" not in body, "no em or en dashes in the body")
    need(page.count('<meta name="robots"') == 1, "exactly one robots tag")
    need(('content="noindex, nofollow"' in page) == draft, "draft pages are noindex; released pages are indexable")
    need(('"datePublished"' in page) == (not draft), "datePublished only after release")
    need(draft == (f'href="{ROUTE}/edition-{ed}"' not in page), "no link to a snapshot that does not exist yet")
    for blk in re.findall(r'<script type="application/ld\+json">\n(.*?)\n</script>', page, re.S): json.loads(blk)
    if K:
        N = K["nar"]
        need(body.count(f'<span class="lbl">{TAKE}</span>') == len(N["findings"]) + 5 + len(N["patterns"]), "a takeaway after every finding, clinic and pattern")
        if K["social"]["status"] != "collected": need("incomplete sample" in body, "a partial Instagram sample must be labelled as incomplete")
        need(">0 likes<" not in body and 'data-label="Plays">0<' not in body, "missing metrics must not render as zero")
    need(len(re.findall(r'class="card dx-test"', body)) == 3, "exactly three tests rendered")
    need('entry=research_dental#contact-form' in body and 'data-review-cta="research_dental"' in body, "service CTA must carry the dental research entry")

def csv_text(rows):
    out = io.StringIO(); w = csv.writer(out, lineterminator="\n")
    for r in rows: w.writerow(r)
    return out.getvalue()

def write_csvs(used, O, ed, K):
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    obs = [["id", "clinic", "dimension", "kind", "statement", "excerpt", "source_url", "checked_utc", "page_sha256", "limitation"]]
    for i in used:
        o = O[i]; obs.append([i, NAMES[o["clinic"]], o["dimension"], o["kind"], o["statement"], o["excerpt"], o["source_url"], o["_rec"]["fetched_utc"], o["_rec"]["sha256"], o["limitation"]])
    ads = [["record_id", "clinic", "platform", "url", "advertiser", "attribution_confidence", "attribution_basis", "treatment", "implant_related", "observed_utc",
            "status_at_observation", "library_start_date", "end_date", "last_shown_pacific", "relation_to_window", "ad_text_or_transcription", "text_basis"]]
    for a, plat, r in ad_records(K).values():
        pd = r["platform_dates"]
        ads.append([r["id"], NAMES[a], plat, r["url"], r["advertiser"]["name"], r["attribution"]["confidence"], r["attribution"]["basis"], r["treatment"]["category"],
                    r["treatment"]["implant_related"], r["observed_utc"], pd["status_at_observation"] or "", pd["started"] or "", pd["ended"] or "", pd["last_shown"] or "",
                    r["window_relation"], r["text"], r["text_basis"]])
    ig = [["shortcode", "clinic", "account", "url", "format", "published_utc", "observed_utc", "topic", "treatment", "implant_related", "call_to_action", "likes_when_observed",
           "comments_when_observed", "plays", "collaboration", "analysis_basis"]]
    for p in K["social"]["posts"]:
        m = p["metrics"]
        ig.append([p["shortcode"], NAMES[p["clinic"]], p["owner"], p["url"], p["format"], p["published_utc"], p["observed_utc"], p["topic"], p["treatment"], p["implant_relevance"],
                   p["cta"], "" if m["likes"] is None else m["likes"], "" if m["comments"] is None else m["comments"], "" if m["plays"] is None else m["plays"], p["collaboration"], p["analysis_basis"]])
    files = {}
    for name, rows in (("observations", obs), ("ads", ads), ("instagram", ig)):
        p = CSV_DIR / f"dental-index-edition-{ed}-{name}.csv"; t = csv_text(rows); p.write_text(t, encoding="utf-8"); files[name] = len(rows) - 1
    return files

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--edition", required=True)
    ap.add_argument("--target", choices=["draft", "release"], default="draft")
    ap.add_argument("--check", action="store_true"); ap.add_argument("--report", action="store_true")
    ap.add_argument("--published-at"); ap.add_argument("--modified-at")
    a = ap.parse_args(argv)
    try:
        K = load(a.edition)
        if a.report:
            validate(K, "draft"); print(json.dumps(release_report(K), indent=1)); return
        O = validate(K, a.target)
        if a.target == "release": need(a.published_at and a.modified_at, "release needs --published-at and --modified-at from the production deployment")
        page, used = render(K, O, a.target, a.published_at, a.modified_at)
        check_page(page, a.target != "release", used, O, a.edition, K)
        files = None
        if not a.check:
            files = write_csvs(used, O, a.edition, K)
            need(files["observations"] == len(used) and f"the {len(used)} website observations" in page, "download and page disagree on the number of observations")
            need(f'the {files["ads"]} ad library records' in page and f'the {files["instagram"]} observed Instagram posts' in page, "downloads and page disagree on record counts")
            PAGE.write_text(page, encoding="utf-8")
        print(f"PASS edition {a.edition} ({a.target}): {len(O)} observations, {len(used)} used on the page"
              + (f", CSVs {files}" if files else ", nothing written"))
    except BuildError as e:
        print("FAIL:", e); sys.exit(1)

if __name__ == "__main__":
    main()
