#!/usr/bin/env python3
"""Build the Dental Implant Marketing Index page (/dental-index) from the kit. Standard library only.

    python3 build.py --edition 001                 draft: noindex, no dates, no snapshot, not in the sitemap
    python3 build.py --edition 001 --check         validate only, write nothing
    python3 build.py --edition 001 --target release --published-at ISO --modified-at ISO
                                                   release: refused until every release requirement is met

Sources of truth (editions/NNN/): fetch_log.jsonl and pages/ (raw evidence), observations.json (dated, sourced
observations), comparison.json, social.json, ads.json, narrative.json, edition.json; cohort.json at the kit root.
Outputs: dental-index.html (repo root) and assets/index/dental/dental-index-edition-NNN-observations.csv. The page body is
never edited by hand.
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
BANNED = ["viral", "winning", "best-performing", "best performing", "top-performing", "leverage", "unlock", "supercharge", "game-changer",
          "guarantee", "in today's fast-paced world"]
TAKE = "What this means for your clinic"

class BuildError(Exception):
    pass

def need(cond, msg):
    if not cond: raise BuildError(msg)

def long_date(d):
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"

def toronto(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(TZ)

def clock(dt):
    h = dt.hour % 12 or 12
    return f"{h}:{dt.minute:02d} {'a.m.' if dt.hour < 12 else 'p.m.'}"

def window_last_30(collected_local):
    """The last 30 complete calendar days in America/Toronto before the collection date."""
    end = collected_local.date() - timedelta(days=1)
    return end - timedelta(days=29), end

def in_window(ts, w):
    d = toronto(ts).date()
    return w[0] <= d <= w[1]

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

def load(ed):
    D = HERE / "editions" / ed
    need(D.exists(), f"edition {ed} not found")
    j = lambda p: json.loads((D / p).read_text(encoding="utf-8"))
    log = [json.loads(l) for l in (D / "raw" / "fetch_log.jsonl").read_text().splitlines() if l.strip()]
    return {"D": D, "cohort": json.loads((HERE / "cohort.json").read_text()), "edition": j("edition.json"), "obs": j("observations.json")["observations"],
            "cmp": j("comparison.json"), "nar": j("narrative.json"), "social": j("social.json"), "ads": j("ads.json"), "log": log}

def page_text(D, rec):
    return re.sub(r"\s+", " ", (D / "raw" / "text" / f"{rec['sha256'][:12]}.txt").read_text(encoding="utf-8"))

def validate(K, target):
    D, ed = K["D"], K["edition"]
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
        if o["evidence"] == "text":
            need(re.sub(r"\s+", " ", o["excerpt"]) in page_text(D, r), f"{o['id']}: excerpt not found in the saved page text")
        elif o["evidence"] == "html":
            need(o["excerpt"] in gzip.open(HERE / r["saved"]).read().decode("utf8", "replace"), f"{o['id']}: excerpt not in the saved page source")
        else:
            need(o["kind"] == "absence" and not o["excerpt"], f"{o['id']}: only an absence may have no excerpt")
        need(urlparse(o["source_url"]).netloc.replace("www.", "") == next(c["domain"] for c in clinics if c["alias"] == o["clinic"]),
             f"{o['id']}: source is not on the clinic's official domain")
        o["_rec"] = r; O[o["id"]] = o
    N = K["nar"]

    def cites(ids, clinic=None, where=""):
        need(ids, where + ": cites no observation")
        for i in ids:
            need(i in O, f"{where}: unknown observation {i}")
            if clinic: need(O[i]["clinic"] == clinic, f"{where}: {i} belongs to another clinic")
        return ids

    def digits_ok(text, ids, where):
        hay = " ".join(page_text(D, O[i]["_rec"]) for i in ids)
        for num in re.findall(r"\$?\d[\d,]*(?:\.\d+)?%?", text):
            need(num in hay, f"{where}: the figure {num} does not appear in a cited source")

    def voice(text, where):
        need("—" not in text and "–" not in text, where + ": em or en dash")
        need(not re.search(r"\b(we|our|ours|us)\b", text, re.I), where + ": HMM voice is first person singular, never we/our/us")
        low = text.lower()
        for b in BANNED: need(b not in low, f"{where}: banned wording '{b}'")

    def takeaway(t, where):
        need(isinstance(t, str) and t.strip(), where + ": missing 'What this means for your clinic' takeaway")
        n = len([s for s in re.split(r"(?<=[.!?])\s+", t.strip()) if s])
        need(2 <= n <= 3, f"{where}: takeaway must be two or three sentences ({n})")
        need(re.search(r"\b(ask|test|measure|check)\b", t, re.I), where + ": takeaway needs one question for the team or one test")

    voice(N["summary"], "summary"); digits_ok(N["summary"], [o for o in O], "summary")
    F = N["findings"]; need(1 <= len(F) <= 4, "What stood out: one to four findings")
    for i, f in enumerate(F, 1):
        w = f"finding {i}"; cites(f["obs"], where=w)
        for k in ("title", "text", "limitation", "takeaway"):
            voice(f[k], w); digits_ok(f[k], f["obs"], w)
        takeaway(f["takeaway"], w)
    A = N["accounts"]; need(set(A) == set(ALIASES), "one account analysis per clinic")
    for a in ALIASES:
        x = A[a]; w = "account " + a
        if x.get("pending"):
            need(x.get("reason"), w + ": pending account needs a reason"); voice(x["reason"], w); continue
        cites(x["obs"], a, w)
        for k in ("positioning", "observed", "supports", "unknown", "takeaway"):
            need(x.get(k), f"{w}: missing {k}"); voice(x[k], w); digits_ok(x[k], x["obs"], w)
        takeaway(x["takeaway"], w)
    for i, p in enumerate(N["patterns"], 1):
        w = f"pattern {i}"; cites(p["obs"], where=w)
        for k in ("title", "text", "takeaway"):
            voice(p[k], w); digits_ok(p[k], p["obs"], w)
        takeaway(p["takeaway"], w)
    T = N["tests"]; need(len(T) == 3, "exactly three practical tests")
    for i, t in enumerate(T, 1):
        for k in ("title", "evidence", "hypothesis", "change", "constant", "measure", "guardrails", "compare", "insufficient"):
            need(t.get(k), f"test {i}: missing {k}"); voice(t[k], f"test {i}")
            need(not re.search(r"\d", t[k]) or k == "title", f"test {i} {k}: no invented baselines, targets or lifts (no figures)")
        need(re.search(r"\(finding [1-4]\)$", t["title"]), f"test {i}: title must end with (finding N)")
    C = K["cmp"]["rows"]; need(set(C) == set(ALIASES), "comparison needs one row per clinic")
    for a in ALIASES:
        row = C[a]
        if row.get("status") == "not_confirmed":
            need(N["accounts"][a].get("pending"), f"comparison {a}: not confirmed while the account analysis is written"); continue
        for col in K["cmp"]["columns"]:
            cell = row[col["key"]]; voice(cell["text"], f"comparison {a}"); cites(cell["obs"], a, f"comparison {a} {col['key']}")
            digits_ok(cell["text"], cell["obs"], f"comparison {a}")
    S = K["social"]; need(set(S["handles"]) == set(ALIASES), "social.json needs a handle record per clinic")
    for a, h in S["handles"].items():
        if h["status"] == "verified_link":
            o = O[h["source_obs"]]; need(o["clinic"] == a and f"instagram.com/{h['handle']}/" in o["excerpt"], f"social {a}: handle not backed by its source")
        else:
            need(h["handle"] is None and h.get("reason"), f"social {a}: unverified handle must stay empty with a reason")
    need(S["status"] in ("not_collected", "collected"), "social status")
    if S["status"] == "not_collected": need(not S["posts"] and S.get("reason") and S.get("public_reason"), "social: not collected needs a reason, a public reason and no posts")
    voice(S.get("public_reason", ""), "social public reason")
    for a, x in K["ads"]["checks"].items():
        for plat in ("meta", "google"):
            need(x[plat]["status"] in AD_STATUS, f"ads {a} {plat}: unknown status")
            if x[plat]["status"] != "not_checked": need(x[plat].get("searched_at") and x[plat].get("evidence"), f"ads {a} {plat}: a check needs a time and evidence")
    if target == "release":
        blockers = []
        if any(A[a].get("pending") for a in ALIASES): blockers.append("clinics still pending: " + ", ".join(a for a in ALIASES if A[a].get("pending")))
        if S["status"] != "collected": blockers.append("Instagram posts not collected")
        if any(x[p]["status"] == "not_checked" for x in K["ads"]["checks"].values() for p in ("meta", "google")): blockers.append("advertising not checked")
        if ed.get("status") != "ready": blockers.append("edition.json status is not 'ready' (founder review)")
        need(not blockers, "release refused: " + "; ".join(blockers))
    return O

def sources_html(ids, O):
    seen, out = [], []
    for i in ids:
        o = O[i]; u = o["source_url"]
        if u in seen: continue
        seen.append(u)
        path = urlparse(u).path.strip("/") or "home page"
        out.append(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(urlparse(u).netloc.replace("www.", ""))}/{E(path) if path != "home page" else ""}</a>' if path != "home page"
                   else f'<a href="{E(u)}" target="_blank" rel="noopener">{E(urlparse(u).netloc.replace("www.", ""))} home page</a>')
    return '<p class="pnote dx-src"><b>Sources:</b> ' + ", ".join(out) + "</p>"

def take_html(t):
    return f'<div class="note take"><span class="lbl">{TAKE}</span><p>{E(t)}</p></div>'

def render(K, O, target, published=None, modified=None):
    D, N, C, S, AD = K["D"], K["nar"], K["cmp"], K["social"], K["ads"]["checks"]
    ed = K["edition"]["edition"]; draft = target != "release"
    clin = {c["alias"]: c for c in K["cohort"]["clinics"]}
    web_times = sorted(o["_rec"]["fetched_utc"] for o in O.values())
    w_first, w_last = toronto(web_times[0]), toronto(web_times[-1])
    basis = S.get("collection_started_utc") or web_times[0]
    win = window_last_30(toronto(basis))
    W = f"{long_date(win[0])} to {long_date(win[1])}"
    web_when = f"{long_date(w_first)}, {clock(w_first)} to {clock(w_last)} Toronto time"
    handles = S["handles"]

    def ig(a):
        h = handles[a]
        return (f'<a href="https://www.instagram.com/{E(h["handle"])}/" target="_blank" rel="noopener">@{E(h["handle"])}</a>' if h["handle"] else "Not verified")

    used = sorted({i for f in N["findings"] for i in f["obs"]} | {i for a in N["accounts"].values() for i in a.get("obs", [])} |
                  {i for p in N["patterns"] for i in p["obs"]} | {i for r in C["rows"].values() for k, c in r.items() if isinstance(c, dict) for i in c.get("obs", [])})
    b = []
    status_line = "Draft for review" if draft else f"Published {long_date(datetime.fromisoformat(published).astimezone(TZ))}"
    b.append('<div class="wrap">')
    b.append('<header class="dx-head"><p class="kicker">The HMM Index &middot; Dental implants</p><h1>Dental Implant Marketing Index</h1>')
    b.append('<p class="lede">How five selected Ontario dental clinics in the Greater Toronto Area present and promote implant consultations, '
             'what an owner can compare against their own clinic, and three tests to discuss with a marketing team. A study of published marketing, '
             'not a ranking of clinics or a judgement of clinical care.</p>')
    b.append(f'<div class="byline"><span><b>Observation window</b> {W}</span><span>For dental practice owners reviewing their implant marketing.</span>'
             '<span>Research and analysis by <b><a href="/about">Ankit Kumar</a></b> &middot; Founder, <a href="/">HMM</a></span></div>')
    b.append(f'<div class="livebar"><span>Websites checked <b>{E(web_when)}</b></span><span>Instagram <b>not collected yet</b></span><span>Edition <b>{ed}</b></span><span><b>{status_line}</b></span></div>')
    b.append('<div class="dx-actions"><a class="btn btn-primary" href="#dx-compare">See the five clinics</a><a class="btn btn-outline" href="#dx-tests">Explore the three tests</a></div></header>')
    if draft:
        b.append('<div class="note warn"><span class="lbl">Draft, not published</span><p>This page is a draft for review and is hidden from search engines. '
                 'Two of the five clinic websites, every Instagram account and every advertising check are still to be verified, so findings below rest on '
                 'three clinic websites only. Missing evidence is shown as missing, never as zero.</p></div>')
    b.append('<nav class="ri-nav" aria-label="On this page"><a href="#dx-findings">What stood out</a><a href="#dx-compare">Comparison</a>'
             '<a href="#dx-examples">Content examples</a><a href="#dx-accounts">Each clinic</a><a href="#dx-patterns">Patterns</a>'
             '<a href="#dx-tests">Tests to run</a><a href="#dx-method">Method</a></nav>')
    b.append(f'<section id="dx-answer"><div class="card"><h2 class="dx-h">The short answer</h2><p class="dek m0">{E(N["summary"])}</p></div></section>')

    b.append('<section id="dx-findings"><div class="sec-head"><h2>What stood out</h2>'
             '<p class="dek">Findings from the published implant pages, consultation offers and enquiry forms of the three clinics whose websites I could read. '
             'Each names its examples and the limitation needed to read it; none claims that a feature caused better results.</p></div>')
    for i, f in enumerate(N["findings"], 1):
        b.append(f'<div class="card"><h3>{i}. {E(f["title"])}</h3><p class="dek">{E(f["text"])}</p>'
                 f'<p class="dek dx-lim"><b>Limitation.</b> {E(f["limitation"])}</p>{sources_html(f["obs"], O)}{take_html(f["takeaway"])}</div>')
    b.append("</section>")

    cols = C["columns"]
    b.append('<section id="dx-compare"><div class="sec-head"><h2>Five-clinic comparison</h2>'
             '<p class="dek">The same definitions for every clinic. &ldquo;Not confirmed&rdquo; means the evidence could not be collected yet; '
             '&ldquo;Not checked&rdquo; means the check has not run. Listed on a website is not the same as tested and working. On a phone, each clinic is shown as a card.</p></div>')
    b.append('<div class="tw cards" tabindex="0" role="region" aria-label="Five-clinic comparison table"><table class="cmp dx-cmp">'
             f'<caption class="sr-only">Implant marketing of five selected Ontario dental clinics, websites checked {E(long_date(w_first))}</caption><thead><tr><th scope="col">Clinic</th>')
    for c in cols: b.append(f'<th scope="col">{E(c["label"])}</th>')
    b.append('<th scope="col">Instagram, implant posts</th><th scope="col">Meta Ad Library</th><th scope="col">Google Ads Transparency</th></tr></thead><tbody>')
    for a in ALIASES:
        row = C["rows"][a]
        b.append(f'<tr><th scope="row" class="brandcell"><a href="{E(clin[a]["official_url"])}" target="_blank" rel="noopener">{E(NAMES[a])}</a><span class="handle">{E(clin[a]["city"])}</span></th>')
        for c in cols:
            if row.get("status") == "not_confirmed":
                b.append(f'<td class="wrap-cell dx-miss" data-label="{E(c["label"])}">Not confirmed<span class="cell-sub">{E(row["reason"])}</span></td>')
            else:
                cell = row[c["key"]]; src = O[cell["obs"][0]]["source_url"]
                b.append(f'<td class="wrap-cell" data-label="{E(c["label"])}">{E(cell["text"])}<span class="cell-sub"><a href="{E(src)}" target="_blank" rel="noopener" aria-label="Source for {E(NAMES[a])}, {E(c["label"])} (opens the clinic page)">Source</a></span></td>')
        h = handles[a]
        ig_cell = (f'{ig(a)}<span class="cell-sub">Posts not collected</span>' if h["handle"] else 'Not verified<span class="cell-sub">Handle not confirmed</span>')
        b.append(f'<td class="wrap-cell dx-miss" data-label="Instagram, implant posts">{ig_cell}</td>')
        for plat, lab in (("meta", "Meta Ad Library"), ("google", "Google Ads Transparency")):
            x = AD[a][plat]
            b.append(f'<td class="wrap-cell dx-miss" data-label="{lab}">{E(AD_STATUS[x["status"]])}</td>')
        b.append("</tr>")
    b.append("</tbody></table></div>")
    b.append(f'<p class="pnote"><b>Definitions.</b> Positioning, cost, consultation, proof and enquiry entries come from the official clinic pages checked on {E(web_when)}. '
             '&ldquo;Published cost information&rdquo; means a price or range printed by the clinic; it is not a quote and inclusions differ, so figures are not comparable between clinics. '
             'Clinic statements about outcomes or experience are reported as the clinic&rsquo;s claims. Forms were read, never submitted.</p>')
    b.append(f'<p class="pnote dlinks"><b>Download the data:</b> <a href="/assets/index/dental/dental-index-edition-{ed}-observations.csv">the {len(used)} website observations used on this page (CSV)</a>. '
             'It holds website observations only; there is no Instagram or advertising data in this draft.</p></section>')

    b.append('<section id="dx-examples"><div class="sec-head"><h2>Observed content examples</h2>'
             f'<p class="dek">Implant-related Instagram posts from the observation window, {W}, will be shown here with the post&rsquo;s cover, date, format, why it was chosen and a link to the original. '
             'No posts have been collected yet, so no example is shown and none is invented. Website pages are not presented as Instagram posts.</p></div>')
    b.append('<div class="dx-phs">')
    for a in ALIASES:
        h = handles[a]
        b.append(f'<div class="card dx-ph"><p class="kicker">{E(NAMES[a])}</p><p class="dek m0">Example pending: {"posts from " + ig(a) + " have not been collected." if h["handle"] else "the Instagram account has not been verified yet."}</p></div>')
    b.append('</div><div class="note warn"><span class="lbl">Why there are no examples yet</span>'
             f'<p>{E(S["public_reason"])} The method below explains how posts will be collected and filtered once a collection route is approved.</p></div></section>')

    b.append('<section id="dx-accounts"><div class="sec-head"><h2>Clinic by clinic</h2>'
             '<p class="dek">For each clinic: its implant positioning, what its website shows, what that evidence supports, what remains unknown, and what it means for your clinic. '
             'Observations come from the pages; interpretations are mine and are labelled as such. None of these clinics is an HMM client.</p></div>')
    for a in ALIASES:
        x = N["accounts"][a]
        b.append(f'<div class="card acct" id="dx-{a}"><h3>{E(NAMES[a])} <span class="handle">({ig(a) if handles[a]["handle"] else "Instagram not verified"})</span></h3>')
        if x.get("pending"):
            b.append(f'<div class="note warn"><span class="lbl">Evidence pending</span><p>{E(x["reason"])}</p></div>'
                     f'<div class="note take dx-pending"><span class="lbl">{TAKE}</span><p>Not written yet. A takeaway will be added only after this clinic&rsquo;s pages have been reviewed.</p></div></div>')
            continue
        for lab, k in (("Positioning", "positioning"), ("Observed marketing", "observed"), ("What the evidence supports", "supports"), ("What remains unknown", "unknown")):
            b.append(f'<p class="dek"><b>{lab}.</b> {E(x[k])}</p>')
        b.append(sources_html(x["obs"], O) + take_html(x["takeaway"]) + "</div>")
    b.append("</section>")

    b.append('<section id="dx-patterns"><div class="sec-head"><h2>Across the clinics</h2>'
             '<p class="dek">The same dimensions compared across the clinics I could read. These are observations from three selected clinics, not patterns in Ontario dentistry.</p></div>')
    for p in N["patterns"]:
        b.append(f'<div class="card"><h3>{E(p["title"])}</h3><p class="dek">{E(p["text"])}</p>{sources_html(p["obs"], O)}{take_html(p["takeaway"])}</div>')
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
        links = " &middot; ".join(f'<a href="{E(u)}" target="_blank" rel="noopener">prepared search</a>' for u in x["prepared_urls"])
        return f'<li>{E(NAMES[a])}, {name}: {E(AD_STATUS[x["status"]])}. {E(x["reason"])} Search terms: {E(", ".join(x["search_terms"]))}; {E(x["filters"])}; {links}.</li>'
    b.append('<section id="dx-method"><div class="sec-head"><h2>Method, sources and limitations</h2>'
             '<p class="dek">How the evidence was collected, what was left out and why. This research assesses published marketing, not clinical quality, treatment outcomes or patient suitability.</p></div>')
    b.append('<section><details class="ri-adv"><summary>Why these five clinics</summary><p>Five Ontario clinics in or near the Greater Toronto Area that market dental implants, '
             'chosen by the founder for comparison. It is a selected group, not a sample of the market and not a ranking. North York Smile Centre and Smile By Design are the same practice and are counted once. '
             'Five further clinics are held in reserve for possible later editions and do not appear here.</p></details></section>')
    b.append(f'<section><details class="ri-adv"><summary>Dates, identity and pages reviewed</summary><p>Observation window: {W}, the last 30 complete days in Toronto time before collection, '
             f'calculated by the build script. Websites were checked on {E(web_when)}. Instagram posts have not been collected. '
             'A clinic&rsquo;s identity, location and Instagram account come only from its official website; a dentist&rsquo;s personal account is never treated as the clinic&rsquo;s. '
             'Each page reviewed is saved with its fetch time and a fingerprint, and every quoted excerpt is checked against the saved page.</p><ul>')
    for a in ALIASES[:3]:
        urls = sorted({o["source_url"] for o in O.values() if o["clinic"] == a})
        b.append(f'<li>{E(NAMES[a])}: ' + ", ".join(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(urlparse(u).path.strip("/") or "home page")}</a>' for u in urls) + "</li>")
    b.append('<li>Dundas East Dental: <a href="https://dundaseastdental.com/" target="_blank" rel="noopener">home page</a> refused automated access (HTTP 403); not reviewed.</li>'
             '<li>Bond Street Dental: <a href="https://www.dentalimplantsclinic.ca/" target="_blank" rel="noopener">dentalimplantsclinic.ca</a> returned a challenge page (HTTP 403), which I did not bypass; '
             'its link to Bond Street Dental is not yet confirmed.</li></ul></details></section>')
    b.append('<section><details class="ri-adv"><summary>Instagram collection and implant content</summary><p>When collected, posts are filtered to the window by their publication time in Toronto, '
             'error rows are dropped, duplicates removed, and old pinned posts outside the window excluded. Clinic-owned and collaborator-owned posts are kept apart, '
             'coverage is checked for truncation, and hidden or restricted values stay missing rather than becoming zero. Implant-related posts are classified separately from general dentistry, '
             'hygiene, Invisalign and other topics, and only implant posts are compared. If there are too few implant posts for a pattern, the page says so instead of widening the window. '
             'Public likes and views are cumulative at collection, not measured at equal post ages, and no engagement ranking is shown.</p>'
             f'<p class="m0"><b>Status in this draft.</b> {E(S["public_reason"])}</p></details></section>')
    b.append('<section><details class="ri-adv"><summary>Advertising checks</summary><p>Meta Ad Library and Google Ads Transparency Center are checked separately for each clinic, '
             'after matching the advertiser to the clinic. A documented search with no results does not mean a clinic never advertises, and nothing here estimates spend, targeting or results.</p><ul>')
    for a in ALIASES:
        b.append(ad_li(a, "meta", "Meta Ad Library") + ad_li(a, "google", "Google Ads Transparency Center"))
    b.append("</ul></details></section>")
    b.append('<section><details class="ri-adv"><summary>What is not measured, and how to read the evidence</summary><p>Nothing on this page estimates advertising budgets, revenue, return on ad spend, cost per lead, '
             'consultation conversion, treatment acceptance, agency fees or appointment capacity; public pages cannot show them. A website credit to a marketing provider shows a published association, '
             'not a current contract, its value or its scope. A tracking script, pixel or separate phone number does not show that automation, retargeting or attribution works, and a stated response promise '
             'is not a measured response time. No form was submitted, no appointment booked, no photo uploaded and no clinic contacted.</p>'
             '<p class="m0">Each statement is labelled as an observation (what a page shows), a clinic claim (what a clinic says about itself, reported, not endorsed) or my interpretation.</p></details></section>')
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

def check_page(page, draft, used, O, ed):
    need(len(re.findall(r"<h1[\s>]", page)) == 1, "page must have exactly one H1")
    body = page.split("DENTAL INDEX REPORT BODY START", 1)[1]
    need(" style=" not in body, "no inline style attributes in the body")
    need("—" not in body and "–" not in body and "&mdash;" not in body and "&ndash;" not in body, "no em or en dashes in the body")
    need(page.count('<meta name="robots"') == 1, "exactly one robots tag")
    need(('content="noindex, nofollow"' in page) == draft, "draft pages are noindex; released pages are indexable")
    need(('"datePublished"' in page) == (not draft), "datePublished only after release")
    need(draft == (f'href="{ROUTE}/edition-{ed}"' not in page), "no link to a snapshot that does not exist yet")
    for blk in re.findall(r'<script type="application/ld\+json">\n(.*?)\n</script>', page, re.S): json.loads(blk)
    need(body.count(f'<span class="lbl">{TAKE}</span>') >= 3 + 5 + 3, "takeaways missing after findings, accounts or patterns")
    need(len(re.findall(r'class="card dx-test"', body)) == 3, "exactly three tests rendered")
    need('entry=research_dental#contact-form' in body and 'data-review-cta="research_dental"' in body, "service CTA must carry the dental research entry")

def write_csv(used, O, ed):
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    out = io.StringIO(); w = csv.writer(out, lineterminator="\n")
    w.writerow(["id", "clinic", "dimension", "kind", "statement", "excerpt", "source_url", "checked_utc", "page_sha256", "limitation"])
    for i in used:
        o = O[i]; w.writerow([i, NAMES[o["clinic"]], o["dimension"], o["kind"], o["statement"], o["excerpt"], o["source_url"], o["_rec"]["fetched_utc"], o["_rec"]["sha256"], o["limitation"]])
    p = CSV_DIR / f"dental-index-edition-{ed}-observations.csv"
    p.write_text(out.getvalue(), encoding="utf-8")
    return p, out.getvalue()

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--edition", required=True)
    ap.add_argument("--target", choices=["draft", "release"], default="draft")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--published-at"); ap.add_argument("--modified-at")
    a = ap.parse_args(argv)
    try:
        K = load(a.edition)
        O = validate(K, a.target)
        if a.target == "release": need(a.published_at and a.modified_at, "release needs --published-at and --modified-at from the production deployment")
        page, used = render(K, O, a.target, a.published_at, a.modified_at)
        check_page(page, a.target != "release", used, O, a.edition)
        rows = None
        if not a.check:
            p, text = write_csv(used, O, a.edition)
            rows = text.count("\n") - 1
            need(rows == len(used) and f"the {len(used)} website observations" in page, "download and page disagree on the number of observations")
            PAGE.write_text(page, encoding="utf-8")
        print(f"PASS edition {a.edition} ({a.target}): {len(O)} observations, {len(used)} used on the page" + (f", CSV {rows} rows" if rows is not None else ", nothing written"))
    except BuildError as e:
        print("FAIL:", e); sys.exit(1)

if __name__ == "__main__":
    main()
