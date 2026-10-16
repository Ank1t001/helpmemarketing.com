#!/usr/bin/env python3
"""Builds a five-account Med Spa Index edition (004 onward) from saved records and the written reading.

    python3 derive_five.py --edition NNN          # raw replies -> observations.json, metrics.json
    python3 frames_five.py --edition NNN --fetch DIR
    python3 build_five.py --edition NNN           # draft: medspa-index.html (noindex), CSVs, no snapshot
    python3 build_five.py --edition NNN --target release --published-at ISO --modified-at ISO --modified-source TEXT
                                                  # at publication: indexable page, dateModified, fixed snapshot,
                                                  # hub and /hmm-index text, sitemap lastmod
    python3 build_five.py --edition NNN --check-live   # rebuild with the recorded release values and compare with
                                                       # medspa-index.html; writes nothing

The page structure is template_five.html. Figures are {{tokens}} computed here from editions/NNN/metrics.json,
observations.json and coding.json; the monthly reading (three findings, one card per readable account, patterns, three
tests) is editions/NNN/narrative.json, written fresh each edition with tokens for every figure. The build fails on an
unknown token, a digit typed outside a token (unless declared in coding.json literal_numbers), a missing or extra
account reading, "we", "our" or "us", an em or en dash, banned wording, a standout post without its reviewed cover
note, frame and alt text, a second H1, and if building twice gives a different page. Edition 003 is built by
build_003.py and is not rebuilt here. Published snapshots are never rewritten.
"""
import argparse, csv, datetime as dt, hashlib, html, io, json, re, statistics as st
from collections import Counter
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).parent
REPO = HERE.parent.parent
TZ = ZoneInfo("America/Toronto")
SITE = "https://helpmemarketing.com"
PAGE = REPO / "medspa-index.html"
HUB = REPO / "medspa-marketing-research.html"
IX = REPO / "hmm-index.html"
SITEMAP = REPO / "sitemap.xml"
CSV_DIR = REPO / "assets" / "index" / "medspa"
E = html.escape
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen",
         "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty"]
SVC = [("injectables", "Injectables"), ("rf_microneedling", "RF microneedling"), ("body_contouring", "Body contouring"),
       ("medical_weight_loss", "Medical weight loss"), ("laser_hair_removal", "Laser hair removal"), ("iv_therapy", "IV therapy")]
SVC_WORDS = {"injectables": ["botox", "filler", "sculptra", "injectable", "neuromodulator", "dysport", "juvederm", "skinvive", "radiesse", "injection"],
             "rf_microneedling": ["morpheus", "potenza", "scarlet", "rf microneedling"],
             "body_contouring": ["coolsculpt", "emsculpt", "bodyfx", "sculpsure", "body contour"],
             "medical_weight_loss": ["semaglutide", "ozempic", "wegovy", "mounjaro", "tirzepatide", "glp-1"],
             "laser_hair_removal": ["laser hair"], "iv_therapy": ["iv therapy", "iv drip", "nad+", "iv lounge"]}
BANNED = ["viral", "winning", "the best", "top-performing", "leverage", "unlock", "supercharge", "game-changer", "in today's fast-paced world"]
LABELS = ["What it published", "Interpretation", "Observed gap", "Limitation", "One test"]


def long_date(d, year=True):
    d = d if isinstance(d, dt.date) else dt.date.fromisoformat(str(d)[:10])
    return f"{d.day} {MONTHS[d.month - 1]}" + (f" {d.year}" if year else "")


def span(a, b):
    a, b = (x if isinstance(x, dt.date) else dt.date.fromisoformat(str(x)[:10]) for x in (a, b))
    return f"{long_date(a, a.year != b.year)} to {long_date(b)}"


def to_local(ts):
    return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(TZ)


def num(x):
    if x is None:
        raise ValueError("missing value used in text")
    x = float(x)
    return f"{x:,.0f}" if abs(x - round(x)) < 1e-9 else f"{x:,.1f}"


def med(v):
    return st.median(v) if v else None


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def edition_record(n):
    d = HERE / "editions" / n
    for f in (d / "edition.json", d / f"edition_{n}.json"):
        if f.exists():
            return json.load(open(f)), f
    return None, None


ap = argparse.ArgumentParser()
ap.add_argument("--edition", required=True)
ap.add_argument("--target", choices=["draft", "release"], default="draft")
ap.add_argument("--published-at")
ap.add_argument("--modified-at")
ap.add_argument("--modified-source")
ap.add_argument("--hub-modified-at", help="defaults to the recorded hub_modified_at, else --modified-at at first release")
ap.add_argument("--check-live", action="store_true")
ap.add_argument("--tokens", action="store_true", help="print every token and its value for this edition, then stop (use before writing narrative.json)")
args = ap.parse_args()
NNN = args.edition
assert len(NNN) == 3 and NNN.isdigit() and int(NNN) >= 4, "build_five.py builds editions 004 onward; edition 003 is build_003.py"
ED = HERE / "editions" / NNN
CFG, CFG_PATH = edition_record(NNN)
assert CFG and CFG["edition"] == NNN, f"editions/{NNN}/edition.json missing or for another edition"
if args.check_live:
    assert CFG.get("status") == "published", "--check-live needs a published edition"
    args.target, args.published_at, args.modified_at, args.modified_source = "release", CFG["published_at"], CFG["modified_at"], CFG["modified_at_source"]
if args.target == "release":
    assert args.published_at and args.modified_at and args.modified_source, "release needs --published-at, --modified-at and --modified-source"
    for v in (args.published_at, args.modified_at):
        dt.datetime.fromisoformat(v.replace("Z", "+00:00"))
FIRST_RELEASE = args.target == "release" and CFG.get("status") != "published"

COH = json.load(open(HERE / "cohort_five.json"))
ALIAS = {a["handle"]: a["alias"] for a in COH["accounts"]}
M = json.load(open(ED / "metrics.json"))
OBS = json.load(open(ED / "observations.json"))
ACC = json.load(open(ED / "accounts.json"))["accounts"]
SV = json.load(open(ED / "services.json"))
ADL = json.load(open(ED / "adlibrary.json"))
COD = json.load(open(ED / "coding.json"))
NAR = json.load(open(ED / "narrative.json")) if (ED / "narrative.json").exists() else {"edition": NNN}
LED = json.load(open(ED / "run_ledger.json"))
FR = json.load(open(ED / "frames.json"))["frames"]
PROF = {p["username"]: p for p in json.load(__import__("gzip").open(ED / "raw" / "source_profiles.json.gz", "rt"))["items"]}
assert M["edition"] == OBS["edition"] == NNN == NAR.get("edition") == COD.get("edition"), "metrics, observations, coding and narrative must all be for this edition"
assert M["window"] == OBS["window"] == CFG["window"]
W0, W1 = (dt.date.fromisoformat(x) for x in CFG["window"])
assert (W1 - W0).days == 29 and W1 == dt.date.fromisoformat(CFG["collected_on"]) - dt.timedelta(days=1)
A = {a["handle"]: a for a in ACC}
assert list(A) == list(ALIAS) == list(M["accounts"]), "the five accounts of cohort_five.json, in order"
assert set(SV["services"]) == set(ALIAS)
posts = OBS["posts"]
win = [p for p in posts if p["in_window"]]
readable = [h for h in ALIAS if M["accounts"][h]["accessible"]]
unreadable = [h for h in ALIAS if h not in readable]
own = [p for p in win if p["own_post"]]
for h in readable:
    m = M["accounts"][h]
    pw = [p for p in win if p["account"] == h]
    po = [p for p in pw if p["own_post"]]
    assert m["posts_in_window"] == len(pw) and m["own_posts"] == len(po)
    assert m["median_likes"] == med([p["likes"] for p in po if p["likes"] is not None])
    assert m["median_plays"] == med([p["plays"] for p in po if p["format"] == "reel" and p["plays"] is not None])
    assert m["coverage"] == "complete", f"{h}: coverage did not reach the window start; re-collect with a higher resultsLimit before building"
TYPES = COH["content_types"]
for p in win:
    c = COD["posts"].get(p["shortcode"])
    assert c, f"post {p['shortcode']} has no content coding"
    assert c["type"] in TYPES, f"{p['shortcode']}: content type {c['type']!r} is not one of {TYPES}"
    assert c.get("topic"), f"{p['shortcode']}: no topic"
stand = {M["accounts"][h]["standout"]["shortcode"]: h for h in readable if M["accounts"][h].get("standout")}
for key in ("standout_visuals", "standout_frames", "standout_titles"):
    assert set(COD.get(key, {})) == set(stand), f"coding.json {key} must be written for exactly the current standout posts (look at each new cover first)"
assert set(FR) == set(stand), "every standout post needs a self-hosted cover frame (frames_five.py)"
for sc, f in FR.items():
    fp = REPO / f["frame"].lstrip("/")
    assert fp.exists() and hashlib.sha256(fp.read_bytes()).hexdigest() == f["frame_sha256"], f"{sc}: frame file missing or changed since frames.json"

# ---- earlier five-account editions (history, comparison, corrections) -----------------------------------------
def five_editions():
    out = []
    for d in sorted((HERE / "editions").iterdir()):
        if d.is_dir() and d.name.isdigit() and int(d.name) >= 3:
            c, _ = edition_record(d.name)
            if c:
                out.append(c)
    return out


EDS = [e for e in five_editions() if e["edition"] <= NNN]
PREV = next((e for e in reversed(EDS) if e["edition"] < NNN and e.get("status") == "published"), None)
PM = json.load(open(HERE / "editions" / PREV["edition"] / "metrics.json")) if PREV else None

# ---- tokens --------------------------------------------------------------------------------------------------------
T = {"COLLECTED": long_date(CFG["collected_on"]), "WSTART": long_date(W0), "WEND": long_date(W1), "WSTART_SHORT": long_date(W0, False),
     "WINDOW_DAYS": str((W1 - W0).days + 1), "EDITION": NNN, "SERVICES_CHECKED": long_date(SV["checked_on"])}
prof_run = next(r for r in LED["runs"] if r["stage"] == "profiles")
post_run = next(r for r in LED["runs"] if r["stage"] == "posts")
cap0, cap1 = to_local(prof_run["started_at"]), to_local(prof_run["finished_at"])
fmt_t = lambda t: t.strftime("%-I:%M %p").lower().replace("am", "a.m.").replace("pm", "p.m.")
T["CAPTURE"] = f"{long_date(cap1.date())}, between {fmt_t(cap0)} and {fmt_t(cap1)} Toronto time"
T["x.records"] = num(post_run["items"])
T["x.results_limit"] = num(post_run["input"]["resultsLimit"])
T["x.caps"] = f"{sum(float(r.get('cap_usd') or 0) for r in LED['runs']):.2f}"
if PREV:
    T["PREV_EDITION"] = PREV["edition"]
    T["PREV_WINDOW"] = span(*PREV["window"])


def before_window(h):
    return sorted([p for p in posts if p["account"] == h and not p["in_window"] and not p["pinned"] and p["published_local"][:10] < W0.isoformat()],
                  key=lambda p: p["published_local"], reverse=True)


for h, al in ALIAS.items():
    m, a = M["accounts"][h], A[h]
    T[f"a.{al}.brand"] = E(a["brand"])
    T[f"a.{al}.handle"] = "@" + h
    T[f"a.{al}.ig"] = a["instagram_url"]
    if PM and PM["accounts"][h]["accessible"]:
        for f in ("followers", "posts_in_window", "own_posts", "reels", "carousels", "statics", "median_likes", "median_comments", "median_plays"):
            if PM["accounts"][h].get(f) is not None:
                T[f"prev.{al}.{f}"] = num(PM["accounts"][h][f])
    if not m["accessible"]:
        continue
    for f in ("followers", "posts_in_window", "own_posts", "collab_posts", "reels", "carousels", "statics", "likes_visible",
              "likes_hidden", "comments_counted", "reels_with_plays"):
        T[f"a.{al}.{f}"] = num(m[f])
    for f in ("median_likes", "median_comments", "median_plays"):
        if m[f] is not None:
            T[f"a.{al}.{f}"] = num(m[f])
    po = [p for p in own if p["account"] == h]
    for lab, vals in (("likes", [p["likes"] for p in po if p["likes"] is not None]), ("comments", [p["comments"] for p in po if p["comments"] is not None]),
                      ("plays", [p["plays"] for p in po if p["format"] == "reel" and p["plays"] is not None])):
        if vals:
            T[f"a.{al}.max_{lab}"], T[f"a.{al}.min_{lab}"] = num(max(vals)), num(min(vals))
    for fmt in ("reel", "carousel", "static"):
        lk = [p["likes"] for p in po if p["format"] == fmt and p["likes"] is not None]
        if lk:
            T[f"a.{al}.median_likes_{fmt}"] = num(med(lk))
    pw = sorted([p for p in win if p["account"] == h], key=lambda p: p["published_local"])
    bw = before_window(h)
    if pw:
        T[f"a.{al}.first_post"], T[f"a.{al}.last_post"] = long_date(pw[0]["published_local"]), long_date(pw[-1]["published_local"])
        T[f"a.{al}.days_since_last"] = num((W1 - dt.date.fromisoformat(pw[-1]["published_local"][:10])).days)
    for i, p in enumerate(bw[:2]):
        T[f"a.{al}.before{i + 1}"] = long_date(p["published_local"])
    if bw:
        first = dt.date.fromisoformat(pw[0]["published_local"][:10]) if pw else W1
        T[f"a.{al}.gap_days"] = num((first - dt.date.fromisoformat(bw[0]["published_local"][:10])).days)
    ct = Counter(slug(COD["posts"][p["shortcode"]]["type"]) for p in po)
    tp = Counter(slug(COD["posts"][p["shortcode"]]["topic"]) for p in po)
    for k in map(slug, TYPES):
        T[f"t.{al}.{k}"] = num(ct.get(k, 0))
    for k, v in tp.items():
        T[f"tp.{al}.{k}"] = num(v)
    s = m.get("standout")
    if s:
        sc = s["shortcode"]
        T[f"s.{al}.url"], T[f"s.{al}.date"], T[f"s.{al}.format"] = s["url"], long_date(s["published_local"]), s["format"]
        for f in ("likes", "comments", "plays", "likes_vs_median", "plays_vs_median"):
            if s.get(f) is not None:
                T[f"s.{al}.{f}"] = num(s[f])
        T[f"s.{al}.type"] = E(COD["posts"][sc]["type"])
for k, v in M["pooled"].items():
    T[f"p.{k}"] = num(v)
pin = [M["accounts"][h]["posts_in_window"] for h in readable]
T["p.posts_all"], T["p.readable"], T["p.unreadable"] = num(sum(pin)), num(len(readable)), num(len(unreadable))
T["p.min_posts"], T["p.max_posts"] = num(min(pin)), num(max(pin))
for k in map(slug, TYPES):
    T[f"p.t.{k}"] = num(sum(1 for p in own if slug(COD["posts"][p["shortcode"]]["type"]) == k))
mcs = [M["accounts"][h]["median_comments"] for h in readable if M["accounts"][h]["median_comments"] is not None]
if mcs:
    T["p.min_median_comments"], T["p.max_median_comments"] = num(min(mcs)), num(max(mcs))
if own:
    mc = max(own, key=lambda p: (p["comments"] or 0, p["published_local"]))
    T["p.max_comments"], T["p.max_comments_acct"], T["p.max_comments_type"] = num(mc["comments"]), E(A[mc["account"]]["brand"]), E(COD["posts"][mc["shortcode"]]["type"])
for h1 in readable:
    for h2 in readable:
        if h1 != h2:
            for f in ("median_plays", "median_likes", "posts_in_window", "followers"):
                v1, v2 = M["accounts"][h1].get(f), M["accounts"][h2].get(f)
                if v1 is not None and v2:
                    T[f"r.{ALIAS[h1]}.{ALIAS[h2]}.{f}"] = num(round(v1 / v2, 1))
for key, words in SVC_WORDS.items():
    T[f"m.{key}"] = num(sum(1 for p in own if any(w in p["caption"].lower() for w in words)))
T["m.words"] = "; ".join(f"{lab}: {', '.join(SVC_WORDS[k])}" for k, lab in SVC)
for k, v in list(T.items()):  # word forms for small whole numbers: {{w.p.readable}} -> four, {{W.p.readable}} -> Four
    if re.fullmatch(r"\d{1,2}", v) and int(v) <= 20 and not k.isupper():
        T["w." + k], T["W." + k] = WORDS[int(v)], WORDS[int(v)].capitalize()


if args.tokens:
    for k in sorted(T):
        print(f"{{{{{k}}}}} = {T[k]}")
    raise SystemExit(0)
assert "findings" in NAR, f"editions/{NNN}/narrative.json is missing or empty: write the reading first"

# ---- text checks ----------------------------------------------------------------------------------------------------
LIT = {str(k) for k in COD.get("literal_numbers", {})}


def check_text(where, s):
    assert s and s.strip(), f"{where}: empty"
    bare = re.sub(r"\{\{[^{}]+\}\}|\(finding [123]\)", "", s)
    for d in re.findall(r"\d+(?:[.,:]\d+)*", bare):
        assert d in LIT, f"{where}: the figure {d!r} is typed by hand; use a token, or declare it in coding.json literal_numbers with its source"
    low = html.unescape(re.sub(r"<[^>]+>", " ", bare)).lower()
    assert not re.search(r"[–—]|&[mn]dash;", s), f"{where}: em or en dash"
    assert not re.search(r"\b(we|our|ours|us)\b", low), f"{where}: write in the first person singular (I, my), never we, our or us"
    for w in BANNED:
        assert w not in low, f"{where}: banned wording {w!r}"
    for w in ("todo", "tbd", "[[", "lorem"):
        assert w not in low, f"{where}: placeholder text {w!r}"


def fill(s, where):
    def one(mo):
        k = mo.group(1)
        if k not in T:
            raise KeyError(f"{where}: token {{{{{k}}}}} has no value (unknown name, or the figure does not exist this edition)")
        return T[k]
    return re.sub(r"\{\{([^{}]+)\}\}", one, s)


def rich(s, where):
    check_text(where, s)
    return fill(s, where)


# ---- generated blocks ------------------------------------------------------------------------------------------------
def restriction(h):
    p = PROF.get(h, {})
    r = p.get("restrictionReason") or ""
    m = re.search(r"(\d+) years old or over", r)
    if m:
        return f"a {m.group(1)}+ viewing restriction", r
    return ("a restricted profile" if p.get("isRestrictedProfile") else f"an error ({p.get('error') or 'no profile record'})"), r


B = {}
names = lambda hs: ", ".join(E(A[h]["brand"]) for h in hs[:-1]) + (" and " if len(hs) > 1 else "") + E(A[hs[-1]]["brand"]) if hs else ""
B["UNREADABLE_DEK"] = "".join(f" When the logged-out collection tools requested {E(A[h]['brand'])}&rsquo;s profile, Instagram returned {restriction(h)[0]}, so it could not be read; it is shown, not analysed, and not treated as inactive." for h in unreadable)
B["UNREADABLE_FAQ"] = "".join(f" Instagram returned {restriction(h)[0]} for {E(A[h]['brand'])}&rsquo;s profile to the logged-out collection tools, so it could not be read." for h in unreadable)

B["HERO"] = rich(NAR["hero"], "hero finding")
assert len(re.sub(r"<[^>]+>|\{\{[^{}]+\}\}", "", NAR["hero"])) <= 320, "hero finding: one or two short sentences"
B["COMPARABILITY"] = rich(NAR["comparability"], "comparability note")
F = NAR["findings"]
assert len(F) == 3, "exactly three findings"
fh = []
for i, f in enumerate(F, 1):
    assert "<b>Denominator:</b>" in f["text"], f"finding {i} must state its denominator (<b>Denominator:</b> ...)"
    fh.append(f'<h3>{i}. {rich(f["title"], f"finding {i} title")}</h3>\n<p class="dek">{rich(f["text"], f"finding {i}")}</p>')
B["FINDINGS"] = ('<div class="card">' + "\n".join(fh) + '\n<div class="note take"><span class="lbl">What this means for your clinic</span>\n<p>'
                 + rich(NAR["findings_takeaway"], "findings takeaway") + "</p></div></div>")


def cell(v, txt=None, cls="r", label=""):
    dv = "" if v is None else f' data-v="{v}"'
    lab = f' data-label="{label}"' if label else ""
    return f'<td class="{cls}"{dv}{lab}>{txt if txt is not None else ("Not readable" if v is None else num(v))}</td>'


rows = []
for h, al in ALIAS.items():
    m, a = M["accounts"][h], A[h]
    name = f'<td class="brandcell" data-v="{E(a["brand"])}"><a href="{a["instagram_url"]}" target="_blank" rel="noopener">{E(a["brand"])}</a><span class="handle">@{h}</span></td>'
    loc = f'<td data-v="{E(a["locations"])}" data-label="Locations">{E(a["locations"].capitalize())}</td>'
    if not m["accessible"]:
        rows.append(f"<tr>{name}{loc}" + "".join(cell(None, cls="r nr") for _ in range(6)) + f'<td class="wrap-cell" data-v="z" data-label="Coverage">{restriction(h)[0][2:].capitalize() if restriction(h)[0].startswith("a ") else "Error"}: not readable</td></tr>')
        continue
    posts_txt = num(m["posts_in_window"]) + (f'<span class="cell-sub">{num(m["own_posts"])} own, {num(m["collab_posts"])} collaboration</span>' if m["collab_posts"] else "")
    mix = f'{num(m["reels"])} / {num(m["carousels"])} / {num(m["statics"])}'
    none = '<span class="cell-sub">no own posts</span>'
    lk = (num(m["median_likes"]) + f'<span class="cell-sub">likes visible on {num(m["likes_visible"])} of {num(m["own_posts"])}</span>') if m["median_likes"] is not None else "None visible" + (none if not m["own_posts"] else "")
    cm = (num(m["median_comments"]) + f'<span class="cell-sub">{num(m["comments_counted"])} post{"s" if m["comments_counted"] != 1 else ""}</span>') if m["median_comments"] is not None else "No own posts"
    pl = (num(m["median_plays"]) + f'<span class="cell-sub">{num(m["reels_with_plays"])} reel{"s" if m["reels_with_plays"] != 1 else ""}</span>') if m["median_plays"] is not None else "No reels"
    rows.append(f"<tr>{name}{loc}{cell(m['followers'], label='Followers')}{cell(m['posts_in_window'], posts_txt, label='Posts in window')}{cell(m['reels'], mix, label='Reels / carousels / static')}"
                f"{cell(m['median_likes'], lk, label='Median likes')}{cell(m['median_comments'], cm, label='Median comments')}{cell(m['median_plays'], pl, label='Median reel plays')}"
                f'<td class="wrap-cell" data-v="a" data-label="Coverage">Complete for the window</td></tr>')
B["TABLE_ROWS"] = "\n".join(rows)

srows = []
for h in ALIAS:
    s = SV["services"][h]
    tds = []
    for k, lab in SVC:
        e = s[k]
        mark = "Yes" if e["status"] == "Confirmed" else "Not confirmed"
        tds.append(f'<td data-label="{lab}"><a href="{e["source"]}" target="_blank" rel="noopener">{mark}</a><span class="cell-sub">{E(e["detail"])}</span></td>')
    srows.append(f'<tr><td class="brandcell">{E(A[h]["brand"])}</td>{"".join(tds)}</tr>')
B["SERVICE_ROWS"] = "\n".join(srows)

if ADL.get("result") == "not checked":
    B["ADLIB_SUMMARY"] = "Meta Ad Library could not be read for any of the five (details in the method), so this page says nothing about advertising."
    B["ADLIB_TEXT"] = ("I tried to record each brand&rsquo;s active ads as limited context. The public Ad Library page could not be read in this collection ("
                       + E(ADL["reason"].split(":")[0].rstrip(".")) + "), so no advertiser identity or active ad status was recorded, and nothing about advertising is inferred.")
else:
    B["ADLIB_SUMMARY"] = "Meta Ad Library results are listed in the method as limited context; an active ad says nothing about spend or results."
    B["ADLIB_TEXT"] = "I recorded each brand&rsquo;s active ads in the public Meta Ad Library as limited context. An active ad says nothing about spend, reach or results."
arows = []
for h in ALIAS:
    a = A[h]
    note = E(a["account_note"]) + ("" if h in readable else f" Instagram returned {restriction(h)[0]} to the logged-out collection tools, so its posts and follower count could not be read.")
    arows.append(f'<tr><td class="brandcell">{E(a["brand"])}</td><td><a href="{a["instagram_url"]}" target="_blank" rel="noopener">@{h}</a></td>'
                 f'<td><a href="{a["official_website"]}" target="_blank" rel="noopener">{E(a["official_website"].split("//")[1].rstrip("/"))}</a></td>'
                 f'<td class="wrap-cell">{E(a["locations"].capitalize())}: {E(a["coverage"])}</td><td class="wrap-cell">{note} Checked {long_date(a["verification_date"])}.</td></tr>')
B["ACCOUNT_ROWS"] = "\n".join(arows)
B["ADLIB_ROWS"] = "\n".join(f'<li>{E(c["brand"])}: <a href="{E(c["source"])}" target="_blank" rel="noopener">Ad Library search</a>, {E(c["status"])} ({long_date(ADL["checked_on"])}).</li>' for c in ADL["checks"])

cards = []
for h in readable:
    al, m = ALIAS[h], M["accounts"][h]
    s = m.get("standout")
    if not s:
        continue
    sc, brand = s["shortcode"], E(A[h]["brand"])
    only = s["rule"].startswith("only own post")
    pinned = next(p for p in win if p["shortcode"] == sc and p["account"] == h)["pinned"]
    noun = "frame" if s["format"] == "reel" else "image"
    alt = (f"Cover {noun} of {brand}&rsquo;s only {s['format']} in the window: " if only else f"Cover {noun} of {brand}&rsquo;s standout {s['format']}: ") + rich(COD["standout_frames"][sc], f"{sc} alt text")
    bl = (f"{s['format']}, {T[f's.{al}.date']}" if only else f"standout {s['format']}, {T[f's.{al}.date']}") + (", pinned at collection" if pinned else "")
    dl = []
    if only:
        dl.append(("Rule", "Only own post in the window, so no comparison within the account"))
    elif s["rule"].startswith("most visible likes"):
        dl.append(("Rule", "Most visible likes among own posts"))
    else:
        dl.append(("Rule", f"Most recorded plays among own reels (likes hidden on {num(m['likes_hidden'])} of {num(m['own_posts'])} own posts)"))
    small = f", from {num(m['own_posts'])} posts" if m["own_posts"] <= 3 else ""
    if s["likes"] is not None:
        dl.append(("Likes", num(s["likes"]) + ("" if only or not s.get("likes_vs_median") else f" ({num(s['likes_vs_median'])} times the account&rsquo;s median of {num(m['median_likes'])}{small})")))
    else:
        dl.append(("Likes", "Hidden"))
    if s["plays"] is not None:
        dl.append(("Recorded plays", num(s["plays"]) + ("" if only or not s.get("plays_vs_median") or s["rule"].startswith("most visible likes") else f" ({num(s['plays_vs_median'])} times the account&rsquo;s median of {num(m['median_plays'])})")))
    if s["rule"].startswith("most recorded plays"):
        dl = [dl[0], dl[2], dl[1]]
    dl.append(("Comments", num(s["comments"])))
    collab = COD.get("standout_collab", {}).get(sc)
    dl.append(("Collaboration", rich(collab, f"{sc} collaboration") if collab else ("Co-authored with " + ", ".join("@" + c for c in s["coauthors"]) if s["coauthors"] else "None recorded")))
    cards.append(f'<div class="frame stand">\n<div class="shot"><img src="{FR[sc]["frame"]}" alt="{alt}" width="640" height="800" loading="lazy">\n'
                 f'<span class="verdict ok">{"Only post" if only else "Standout"}</span>\n'
                 f'<span class="badge"><span class="bn">{brand}</span><span class="bl">{bl}</span></span></div>\n'
                 f'<div class="body"><h3>{rich(COD["standout_titles"][sc], f"{sc} title")}</h3>\n'
                 f'<dl>{"".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in dl)}</dl>\n'
                 f'<p>{rich(COD["standout_visuals"][sc], f"{sc} visual note")}</p>\n'
                 f'<a class="go" href="{s["url"]}" target="_blank" rel="noopener">View the post on Instagram</a></div></div>')
up = [E(A[FR[sc]["account"]]["brand"]) for sc in FR if FR[sc].get("upscaled")]
note = "Frames are cropped to the same 4:5 shape, so the edges of taller covers are trimmed."
if up:
    note += f" {names([h for h in ALIAS if E(A[h]['brand']) in up])}&rsquo;s cover{'s were' if len(up) > 1 else ' was'} returned at a smaller size and {'are' if len(up) > 1 else 'is'} enlarged here, so {'they look' if len(up) > 1 else 'it looks'} softer than the post."
warn = []
for h in unreadable:
    warn.append(f'<div class="note warn"><span class="lbl">{E(A[h]["brand"])}: no standout post</span><p>Instagram returned {restriction(h)[0]} when the logged-out collection tools requested '
                f'<a href="{A[h]["instagram_url"]}" target="_blank" rel="noopener">@{h}</a>, so no post, like, play or follower count could be read. Missing data is not zero, and nothing is inferred about how often the account posted.</p></div>')
for h in readable:
    if not M["accounts"][h].get("standout"):
        warn.append(f'<div class="note warn"><span class="lbl">{E(A[h]["brand"])}: no standout post</span><p>{E(A[h]["brand"])} published no post of its own in the window, so there is no standout post. This is an observed zero for the window, not missing data.</p></div>')
B["STANDOUTS"] = '<div class="frames">\n' + "\n".join(cards) + f'\n</div>\n<p class="pnote">{note}</p>' + ("\n" + "\n".join(warn) if warn else "")

acct = []
NA = NAR["accounts"]
assert set(NA) == {ALIAS[h] for h in readable}, f"narrative.json accounts must be exactly the readable accounts: {sorted(ALIAS[h] for h in readable)}"
for h in ALIAS:
    al, brand = ALIAS[h], E(A[h]["brand"])
    head = f'<div class="card acct"><h3>{brand} (<a href="{A[h]["instagram_url"]}" target="_blank" rel="noopener">@{h}</a>)</h3>'
    if h in unreadable:
        what, reason = restriction(h)
        quote = f" (its reply: &ldquo;{E(reason)}&rdquo;)" if reason else ""
        acct.append(head + f'\n<p class="dek"><b>What could be read.</b> Only the profile header: the account exists and is linked from the brand&rsquo;s website. Instagram returned {what} when the logged-out collection tools I used requested the profile{quote}, so posts, likes, plays and followers could not be collected.</p>'
                    '\n<p class="dek"><b>Interpretation.</b> None about its content or how often it posts. The reason for the restriction is not known from public data.</p>'
                    '\n<p class="dek m0"><b>Limitation.</b> The account was not replaced and is not counted as inactive. A future edition can include it only if its posts become readable to the same tools.</p>'
                    f'\n<div class="note take"><span class="lbl">What this means for your clinic</span><p>Instagram returned {what} when the logged-out collection tools requested {brand}&rsquo;s profile. Ask your team whether your clinic&rsquo;s viewing restrictions are intentional and appropriate for its services.</p></div></div>')
        continue
    blocks = NA[al]["blocks"]
    labels = [b[0] for b in blocks]
    assert labels[0] == "What it published" and labels[-1] == "One test" and all(l in LABELS for l in labels) and len(set(labels)) == len(labels), \
        f"{al}: blocks run What it published, then Interpretation or Observed gap, Limitation, and end with One test"
    ps = [f'<p class="dek{" m0" if i == len(blocks) - 1 else ""}"><b>{lab}.</b> {rich(txt, f"{al} {lab}")}</p>' for i, (lab, txt) in enumerate(blocks)]
    acct.append(head + "\n" + "\n".join(ps) + f'\n<div class="note take"><span class="lbl">What this means for your clinic</span><p>{rich(NA[al]["takeaway"], f"{al} takeaway")}</p></div></div>')
B["ACCOUNTS"] = "\n\n".join(acct)

P = NAR["patterns"]
assert 2 <= len(P) <= 5, "two to five patterns"
B["PATTERNS"] = ('<div class="card">\n' + "\n".join(f'<p class="dek"><b>{rich(p["title"], "pattern title")}.</b> {rich(p["text"], "pattern")}</p>' for p in P)
                 + f'\n<div class="note take"><span class="lbl">What this means for your clinic</span><p>{rich(NAR["patterns_takeaway"], "patterns takeaway")}</p></div></div>')
TS = NAR["tests"]
assert len(TS) == 3, "exactly three tests"
for i, t_ in enumerate(TS, 1):
    assert re.search(r"\(finding [123]\)$", t_["title"]), f"test {i} title ends with (finding N)"
B["TESTS"] = "\n".join(f'<li><b>{rich(t_["title"], f"test {i} title")}.</b> Compare: {rich(t_["compare"], f"test {i} compare")} Measure: {rich(t_["measure"], f"test {i} measure")}</li>' for i, t_ in enumerate(TS, 1))

errs = [r for r in OBS["unattributed"]]
if errs:
    B["UNATTRIBUTED"] = f" {num(len(errs))} record{'s were errors' if len(errs) != 1 else ' was an error'} without a post (" + "; ".join(
        (f"the {E(A[(r.get('inputUrl') or '').rstrip('/').split('/')[-1]]['brand'])} profile, returned with {restriction((r.get('inputUrl') or '').rstrip('/').split('/')[-1])[0]}"
         if (r.get("inputUrl") or "").rstrip("/").split("/")[-1] in A else "a record not linked to any cohort account") for r in errs) + ") and set aside."
else:
    B["UNATTRIBUTED"] = ""
B["SHARED"] = " No post was shared between two cohort accounts." if not M["pooled"]["shared_between_cohort_accounts"] else f" {num(M['pooled']['shared_between_cohort_accounts'])} post(s) appeared on two cohort feeds and count once in pooled figures."
coll = [(h, M["accounts"][h]["collab_owners"]) for h in readable if M["accounts"][h]["collab_posts"]]
B["COLLABS"] = ((f"{num(M['pooled']['collab_posts'])} collaboration post{'s' if M['pooled']['collab_posts'] != 1 else ''} appeared on {'a readable feed' if len(coll) == 1 else 'readable feeds'} in the window ("
                 + "; ".join(f"{E(A[h]['brand'])}, owned by " + ", ".join("@" + o for o in ow) for h, ow in coll) + ").") if coll else "No collaboration post owned by another account appeared on a readable feed in the window.") \
    + (" No standout post was co-authored." if not any(M["accounts"][h]["standout"]["coauthors"] for h in readable if M["accounts"][h].get("standout")) else "") \
    + " Whether a tag or collaboration brought views or likes from another account&rsquo;s followers is not shown by public counts."
B["MISSING"] = f"Hidden likes ({num(M['pooled']['likes_hidden'])} own posts)" + ("".join(f" and the account behind {restriction(h)[0]}" for h in unreadable)) + " are recorded as missing, never as zero."


# history and corrections from every five-account edition up to this one
def hist_dates(e, current):
    w = f"Window {span(*e['window'])}; data collected {long_date(e['collected_on'])}."
    if current and args.target != "release":
        return f"Not yet published (release candidate). {w} A fixed snapshot is created at publication."
    pub = args.published_at if current else e["published_at"]
    return f"Published {long_date(to_local(pub).date())}. {w} <a href=\"/medspa-index/edition-{e['edition']}\">Snapshot</a>"


hist = []
for e in sorted(EDS, key=lambda e: e["edition"], reverse=True):
    cur = e["edition"] == NNN
    if not cur and e.get("status") != "published":
        continue
    note = e.get("history_note") or COH["history_notes"].get(e["edition"]) or COH["history_note_default"]
    assert note, f"edition {e['edition']}: history_note missing"
    hist.append(f'<tr><td><b>{e["edition"]}</b>{" (this page)" if cur else ""}</td><td class="wrap-cell">{hist_dates(e, cur)}</td><td class="wrap-cell">{note}</td></tr>')
hist += COH["legacy_history"]
B["HISTORY"] = "\n".join(hist)
B["CITE_SNAPSHOT"] = (f'For a fixed version, cite the <a href="/medspa-index/edition-{NNN}">edition {NNN} snapshot</a>.' if args.target == "release"
                      else f"A fixed edition {NNN} snapshot will be created at publication; until then, cite this address with the collection date.")
corr = []
for e in sorted(EDS, key=lambda e: e["edition"], reverse=True):
    cf = HERE / "editions" / e["edition"] / "corrections.json"
    if cf.exists():
        for c in json.load(open(cf))["notes"]:
            pre = "" if e["edition"] == NNN else f"Edition {e['edition']}. "
            corr.append(f'<p class="m0"><b>{E(c["kind"])}, {long_date(c["date"])}.</b> {pre}{c["text"]}</p>')
B["CORRECTIONS"] = ("\n" + "\n".join(corr)) if corr else ""

tpl = (HERE / "template_five.html").read_text()
tpl = tpl[tpl.index("-->") + 4:]


def tfill(mo):
    k = mo.group(1)
    if k.startswith("BLOCK:"):
        return B[k[6:]]
    if k not in T:
        raise KeyError(f"template token {{{{{k}}}}} has no value")
    return T[k]


body = re.sub(r"\{\{([^{}]+)\}\}", tfill, tpl).rstrip("\n")
assert "{{" not in body and "}}" not in body
assert not re.search(r"[–—]|&[mn]dash;", body), "em or en dash in the body"
assert body.count("<h1") == 1
low = body.lower()
for w in BANNED:
    assert w not in low, f"banned wording: {w}"
assert 'href="/contact?intent=review&amp;entry=research_gta_medspa#contact-form" data-review-cta="research_gta_medspa"' in body
assert not re.search(r"\sstyle=", body), "style attribute in the body"
faq = re.findall(r'<details class="ri-adv faq"><summary>(.*?)</summary>\s*<p>(.*?)</p>', body, re.S)
assert len(faq) >= 3
strip = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s)).strip()

# ---- head --------------------------------------------------------------------------------------------------------
TITLE = "Med Spa Index: Ontario Med Spa Instagram | HelpMeMarketing"
DESC = "How five selected Ontario med spas use Instagram: posts, formats, visible likes, comments and reel plays, with three tests a clinic could run. By Ankit Kumar."
OG_DESC = "Five selected Ontario med spas on Instagram: what they post, the visible response, and three tests a clinic owner could run."
OG_TITLE = TITLE.replace(" | HelpMeMarketing", "")
OG_IMG = f"{SITE}/assets/index/gta-medspa/medspa-index-og.jpg"
CSV_POSTS, CSV_ACCTS = f"medspa-index-edition-{NNN}-posts.csv", f"medspa-index-edition-{NNN}-accounts.csv"
article = {"@context": "https://schema.org", "@type": "Article", "headline": "Med Spa Index", "description": DESC,
           "image": {"@type": "ImageObject", "url": OG_IMG, "width": 1200, "height": 630},
           "author": {"@type": "Person", "@id": f"{SITE}/about#ankit-kumar", "name": "Ankit Kumar", "url": f"{SITE}/about"},
           "publisher": {"@type": "Organization", "@id": f"{SITE}/#organization", "name": "HelpMeMarketing", "url": f"{SITE}/"},
           "mainEntityOfPage": f"{SITE}/medspa-index",
           "isPartOf": {"@type": "WebPage", "@id": f"{SITE}/medspa-marketing-research", "url": f"{SITE}/medspa-marketing-research"},
           "about": "Instagram posting activity and visible engagement of five selected Ontario med spa accounts"}
if args.target == "release":
    article["dateModified"] = args.modified_at
rd = "all five selected Ontario med spa accounts" if not unreadable else f"{WORDS[len(readable)]} of five selected Ontario med spa accounts ({WORDS[len(unreadable)]} not readable)"
dataset = {"@context": "https://schema.org", "@type": "Dataset",
           "name": f"Med Spa Index edition {NNN}: Instagram posts of five selected Ontario med spa accounts",
           "description": f"Public Instagram posts published between {T['WSTART']} and {T['WEND']} by {rd}, with format, visible likes, comments and recorded reel plays. It does not include enquiries, consultations or revenue and is not a sample of the market.",
           "url": f"{SITE}/medspa-index", "license": f"{SITE}/terms",
           "creator": {"@type": "Person", "@id": f"{SITE}/about#ankit-kumar", "name": "Ankit Kumar"},
           "temporalCoverage": f"{W0.isoformat()}/{W1.isoformat()}",
           "spatialCoverage": {"@type": "Place", "name": "Ontario, Canada"},
           "variableMeasured": ["Posts in window", "Post format", "Visible likes", "Comments", "Recorded reel plays", "Followers at capture"],
           "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": f"{SITE}/assets/index/medspa/{CSV_POSTS}"},
                            {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": f"{SITE}/assets/index/medspa/{CSV_ACCTS}"}]}
faqld = {"@context": "https://schema.org", "@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in faq]}
crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
    {"@type": "ListItem", "position": 2, "name": "Medspa Marketing Research", "item": f"{SITE}/medspa-marketing-research"},
    {"@type": "ListItem", "position": 3, "name": "Med Spa Index", "item": f"{SITE}/medspa-index"}]}
snap_crumb = {**crumb, "itemListElement": crumb["itemListElement"] + [
    {"@type": "ListItem", "position": 4, "name": f"Edition {NNN}", "item": f"{SITE}/medspa-index/edition-{NNN}"}]}
LDS = {m: "\n".join(f'<script type="application/ld+json">\n{json.dumps(x, ensure_ascii=False, separators=(",", ":"))}\n</script>' for x in (c, article, dataset, faqld))
       for m, c in (("page", crumb), ("snapshot", snap_crumb))}
EXTRA = (HERE / "head_five.html").read_text().strip()


def sub1(pat, rep, s, flags=0):
    s2, n = re.subn(pat, lambda _: rep, s, count=1, flags=flags)
    assert n == 1, f"head pattern not found: {pat}"
    return s2


def make(shell, mode):
    s = shell
    s = sub1(r"<title>.*?</title>", f"<title>{E(TITLE)}</title>", s)
    s = sub1(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{E(DESC)}">', s)
    robots = {"draft": "noindex, nofollow", "snapshot": "noindex, follow"}.get(mode, "index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1")
    s = sub1(r'<meta name="robots" content="[^"]*">', f'<meta name="robots" content="{robots}">', s)
    canon = f"{SITE}/medspa-index/edition-{NNN}" if mode == "snapshot" else f"{SITE}/medspa-index"
    s = sub1(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{canon}">', s)
    s = sub1(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{canon}">', s)
    s = sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{E(OG_TITLE)}">', s)
    s = sub1(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{E(OG_TITLE)}">', s)
    s = sub1(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{E(OG_DESC)}">', s)
    s = sub1(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{E(OG_DESC)}">', s)
    s = sub1(r'<meta property="og:image:alt" content="[^"]*">', '<meta property="og:image:alt" content="HMM research graphic: Med Spa Index, a comparison of five selected Ontario med spa Instagram accounts">', s)
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', "", s, flags=re.S)
    gtm = "<!-- End Google Tag Manager -->\n"
    assert s.count(gtm) == 1
    s = s.replace(gtm, gtm + LDS["snapshot" if mode == "snapshot" else "page"] + "\n", 1)
    s = re.sub(r"\n<!-- MSI00\d START -->.*?<!-- MSI00\d END -->", "", s, flags=re.S)
    s = re.sub(r"\n<!-- MSI5 START -->.*?<!-- MSI5 END -->", "", s, flags=re.S)
    s = re.sub(r"<!-- Snapshot of edition \d{3} as first published\..*?-->\n", "", s, flags=re.S)
    s = sub1(r"</style></head>", "</style>\n<!-- MSI5 START -->\n" + EXTRA + "\n<!-- MSI5 END --></head>", s)
    a = s.index("<!-- ===== GTA MEDSPA INDEX REPORT BODY START")
    a = s.index("\n", a) + 1
    b = s.index("<!-- ===== GTA MEDSPA INDEX REPORT BODY END")
    s = s[:a] + body + "\n" + s[b:]
    if mode == "snapshot":
        s = s.replace("</head>", f"<!-- Snapshot of edition {NNN} as first published. Research content in this snapshot is never rewritten; record any later metadata fix in this comment. -->\n</head>", 1)
    return s


shell = PAGE.read_text()
mode = "live" if args.target == "release" else "draft"
out = make(shell, mode)
assert make(out, mode) == out, "the build is not idempotent"
assert out.count("<h1") == 1
if args.check_live:
    assert out == shell, "the live page differs from a rebuild of the recorded edition: someone changed medspa-index.html without updating the kit"
    print(f"PASS check-live: edition {NNN} reproduces medspa-index.html")
    raise SystemExit(0)
if mode == "draft" and CFG.get("status") == "published":
    raise SystemExit(f"edition {NNN} is published: rebuild with --target release and the values recorded in its edition.json")
PAGE.write_text(out)

# ---- dataset CSVs ------------------------------------------------------------------------------------------------
CSV_DIR.mkdir(parents=True, exist_ok=True)
buf = io.StringIO()
w = csv.writer(buf, lineterminator="\n")
w.writerow(["account", "post_url", "published_toronto", "format", "own_post", "recorded_owner", "coauthors", "likes", "likes_hidden",
            "comments", "reel_plays", "pinned", "paid_partnership_label", "content_type", "topic"])
for p in sorted(win, key=lambda p: (p["account"], p["published_local"])):
    c = COD["posts"][p["shortcode"]]
    w.writerow([p["account"], p["url"], p["published_local"], p["format"], p["own_post"], p["owner"], " ".join(p["coauthors"]),
                "" if p["likes"] is None else p["likes"], p["likes_hidden"], p["comments"], "" if p["plays"] is None else p["plays"],
                p["pinned"], p["paid_partnership"], c["type"], c["topic"]])
(CSV_DIR / CSV_POSTS).write_text(buf.getvalue())
buf = io.StringIO()
w = csv.writer(buf, lineterminator="\n")
w.writerow(["brand", "handle", "instagram_url", "official_website", "locations", "coverage_note", "readable", "followers", "followers_captured_utc",
            "posts_in_window", "own_posts", "collaboration_posts", "reels", "carousels", "static", "likes_visible_on", "median_visible_likes",
            "median_comments", "reels_with_plays", "median_reel_plays", "window_start", "window_end"])
for h in ALIAS:
    m, a = M["accounts"][h], A[h]
    g = lambda k: "" if m.get(k) is None else m.get(k)
    w.writerow([a["brand"], h, a["instagram_url"], a["official_website"], a["locations"], a["coverage"], m["accessible"], g("followers"),
                m["followers_captured_at"], g("posts_in_window"), g("own_posts"), g("collab_posts"), g("reels"), g("carousels"), g("statics"),
                g("likes_visible"), g("median_likes"), g("median_comments"), g("reels_with_plays"), g("median_plays"), W0.isoformat(), W1.isoformat()])
(CSV_DIR / CSV_ACCTS).write_text(buf.getvalue())


# ---- hub and /hmm-index text (elements tagged data-msi) ----------------------------------------------------------------
def put(s, key, inner, where):
    pat = re.compile(r'(<(\w+)[^>]*\sdata-msi="' + key + r'"[^>]*>)(.*?)(</\2>)', re.S)
    s2, n = pat.subn(lambda mo: mo.group(1) + inner + mo.group(4), s, count=1)
    assert n == 1, f"{where}: element data-msi=\"{key}\" not found"
    return s2


def hub_texts(latest, pubs):
    L = latest["edition"]
    earlier = [e for e in pubs if e["edition"] < L]
    lm = json.load(open(HERE / "editions" / L / "metrics.json"))
    rd_ = [h for h in ALIAS if lm["accounts"][h]["accessible"]]
    ur_ = [h for h in ALIAS if h not in rd_]
    pw_ = [lm["accounts"][h]["posts_in_window"] for h in rd_]
    names5 = names(list(ALIAS))
    lg = COH["hub_legacy"]
    wl = latest["window"]
    rng = f"{num(min(pw_))} to {num(max(pw_))}"
    first = "003"
    t = {}
    t["who"] = (f"A comparison of five selected Ontario med spa Instagram accounts: what they posted, the visible response and three tests a clinic could run. "
                f"Edition {L} covers {span(*wl)} and re-collects the five accounts first compared in edition {first}; editions 001 and 002 studied larger Greater Toronto Area samples.")
    t["pts1"] = (f"{'All five accounts could be read' if not ur_ else WORDS[len(rd_)].capitalize() + ' of the five accounts could be read'}; posts in the window ranged from {rng}")
    t["links"] = ('<a class="wk-tool-cta" href="/medspa-index">Read the Med Spa Index &rarr;</a>'
                  + "".join(f'<a class="wk-tool-cta" href="/medspa-index/edition-{e["edition"]}">Edition {e["edition"]} snapshot</a>' for e in sorted(earlier, key=lambda e: e["edition"], reverse=True))
                  + '<a class="wk-tool-cta" href="/gta-medspa-index/edition-002">Edition 002 snapshot</a><a class="wk-tool-cta" href="/gta-medspa-index/edition-001">Edition 001 snapshot</a>')
    t["geo"] = f"Editions {first} to {L}: the same five Ontario med spa brands, single and multi-location. " + lg["geo"]
    t["period"] = (f"Edition {L} covers the 30 days from {span(*wl)}, collected on {long_date(latest['collected_on'], False)}. "
                   + "".join(f"Edition {e['edition']} covered {span(*e['window'])}. " for e in sorted(earlier, key=lambda e: e["edition"], reverse=True)) + lg["period"])
    t["sample"] = (f"Editions {first} to {L}: the same five named accounts chosen editorially ({names5})"
                   + ("".join(f"; in edition {L}, Instagram returned {restriction_for(L, h)} for {E(A[h]['brand'])}&rsquo;s profile, so it could not be read" for h in ur_)) + ". " + lg["sample"])
    t["limits"] = (f"Edition {L} compares {WORDS[len(rd_)]} readable account{'s' if len(rd_) != 1 else ''} with {WORDS[min(pw_)] if min(pw_) <= 20 else num(min(pw_))} to {WORDS[max(pw_)] if max(pw_) <= 20 else num(max(pw_))} posts each, so its medians describe little; "
                   f"editions {first} onward use the same accounts and method, so a change between them is an observation, not a trend. " + lg["limits"])
    t["learn"] = f"Edition {L}: what five clinics posted, the response each received and practical tests for your own account. " + lg["learn"]
    t["ix-latest"] = f"Edition {L}, collected {long_date(latest['collected_on'])}"
    t["ix-pts1"] = f"Five accounts selected; {'all five' if not ur_ else WORDS[len(rd_)]} readable, with {rng} posts each in the window"
    return t


def restriction_for(ed, h):
    p = {x["username"]: x for x in json.load(__import__("gzip").open(HERE / "editions" / ed / "raw" / "source_profiles.json.gz", "rt"))["items"]}.get(h, {})
    m = re.search(r"(\d+) years old or over", p.get("restrictionReason") or "")
    return f"a {m.group(1)}+ viewing restriction" if m else "a restricted profile"


def schedule_dl(latest_text, collected):
    sc = COH["schedule"]
    if sc.get("active"):
        return (f'<div><dt>Refresh plan</dt><dd>Monthly, collection scheduled on the {sc["day"]}th</dd></div><div><dt>Latest published data</dt><dd>{latest_text}</dd></div>'
                f'<div><dt>Next scheduled collection</dt><dd data-ix-next="{sc["day"]}" data-ix-tz="America/Toronto" data-ix-latest="{collected}">The {sc["day"]}th of each month</dd></div>')
    return (f'<div><dt>Refresh plan</dt><dd>Re-collect the same five accounts; timing to be confirmed</dd></div><div><dt>Latest published data</dt><dd>{latest_text}</dd></div>'
            '<div><dt>Next scheduled collection</dt><dd>To be confirmed</dd></div>')


def apply_hub_and_index():
    pubs = [e for e in five_editions() if e.get("status") == "published" or e["edition"] == NNN]
    latest = max(pubs, key=lambda e: e["edition"])
    t = hub_texts(latest, pubs)
    h = HUB.read_text()
    for k in ("who", "pts1", "links", "geo", "period", "sample", "limits", "learn"):
        h = put(h, k, t[k], "hub")
    ix = IX.read_text()
    ix = put(ix, "ix-dates", schedule_dl(t["ix-latest"], latest["collected_on"]), "/hmm-index")
    ix = put(ix, "ix-pts1", t["ix-pts1"], "/hmm-index")
    return h, ix


# ---- release: snapshot, hub, /hmm-index, sitemap, edition record ----------------------------------------------------
if args.target == "release":
    snap = REPO / "medspa-index" / f"edition-{NNN}.html"
    provisional = str(CFG.get("modified_at_source", "")).startswith("provisional")
    if snap.exists():
        if provisional and args.modified_at != CFG["modified_at"]:
            # recording the production time over the provisional release time: a metadata fix, noted in the snapshot head
            sn = snap.read_text()
            old_t = CFG["modified_at"]
            assert sn.count(f'"dateModified":"{old_t}"') == 1, "snapshot dateModified is not the provisional release time"
            sn = sn.replace(f'"dateModified":"{old_t}"', f'"dateModified":"{args.modified_at}"')
            c = "record any later metadata fix in this comment."
            sn = sn.replace(c, c + f" Metadata fix, {long_date(to_local(args.modified_at).date())}: Article dateModified changed from the provisional release time ({old_t}) to the production deployment ready time ({args.modified_at}, {E(args.modified_source)}). Research content unchanged.", 1)
            snap.write_text(sn)
            print(f"snapshot dateModified recorded: {snap.relative_to(REPO)}")
        else:
            print(f"snapshot kept as published: {snap.relative_to(REPO)}")
    else:
        snap.parent.mkdir(exist_ok=True)
        snap.write_text(make(out, "snapshot"))
    if args.hub_modified_at:
        hub_mod = args.hub_modified_at
    elif provisional and CFG.get("hub_modified_at") == CFG.get("modified_at"):
        hub_mod = args.modified_at  # the hub changed in this release, so it takes the recorded production time too
    else:
        hub_mod = CFG.get("hub_modified_at") or args.modified_at
    if FIRST_RELEASE:
        CFG.update({"status": "published"})
        json.dump(CFG, open(CFG_PATH, "w"), indent=1)
        h, ix = apply_hub_and_index()
        hub_mod = args.hub_modified_at or args.modified_at
    else:
        h, ix = HUB.read_text(), IX.read_text()
    h, k1 = re.subn(r'("dateModified":")[^"]*', lambda m: m.group(1) + hub_mod, h, 1)
    tor = long_date(to_local(hub_mod).date())
    h, k2 = re.subn(r"(Published \d+ \w+ \d{4} &middot; Updated )\d+ \w+ \d{4}", lambda m: m.group(1) + tor, h, 1)
    assert k1 == 1 and k2 == 1, "research hub date markers not found"
    HUB.write_text(h)
    IX.write_text(ix)
    if FIRST_RELEASE:
        sm = SITEMAP.read_text()
        day = to_local(args.modified_at).date().isoformat()
        for path in ("medspa-index", "medspa-marketing-research", "hmm-index"):
            sm, n = re.subn(r"(<loc>https://helpmemarketing\.com/" + path + r"</loc>\s*<lastmod>)[^<]*", lambda m: m.group(1) + day, sm, 1)
            assert n == 1, f"sitemap entry for /{path} not found"
        SITEMAP.write_text(sm)
    CFG.update({"status": "published", "published_at": args.published_at, "modified_at": args.modified_at, "modified_at_source": args.modified_source, "hub_modified_at": hub_mod})
    json.dump(CFG, open(CFG_PATH, "w"), indent=1)
print(f"PASS {args.target}: edition {NNN}, medspa-index.html ({len(out):,} bytes), {len(faq)} FAQ, {len(readable)} readable accounts, CSVs in assets/index/medspa/")
