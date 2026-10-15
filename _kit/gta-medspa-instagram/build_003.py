#!/usr/bin/env python3
"""Builds the Med Spa Index edition 003 (a fixed five-account comparison) from saved records only.

    python3 derive_003.py                       # raw replies -> observations.json, metrics.json
    python3 build_003.py                        # draft: medspa-index.html (noindex), CSVs, no snapshot
    python3 build_003.py --target release --published-at ISO --modified-at ISO --modified-source TEXT
                                                # at publication: indexable page, dateModified, fixed snapshot

Editorial text lives in editions/003/body_template.html; every figure in it is a {{token}} filled from
editions/003/metrics.json, observations.json and coding.json, so no number is typed by hand. The build fails on an
unknown or missing token, on a standout post that no longer matches the data, on any em or en dash, on a second
H1, and if building twice gives a different page. Published snapshots are never rewritten. The head, nav, .msi
wrapper and footer come from the current medspa-index.html (the site's, not the kit's); only the title,
descriptions, JSON-LD, robots tag and the edition 003 style and sort script block are regenerated.
"""
import argparse, csv, datetime as dt, hashlib, html, io, json, re, statistics as st
from collections import Counter
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).parent
REPO = HERE.parent.parent
ED = HERE / "editions" / "003"
TZ = ZoneInfo("America/Toronto")
SITE = "https://helpmemarketing.com"
PAGE = REPO / "medspa-index.html"
CSV_DIR = REPO / "assets" / "index" / "medspa"
CSV_POSTS, CSV_ACCTS = "medspa-index-edition-003-posts.csv", "medspa-index-edition-003-accounts.csv"
E = html.escape
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
ALIAS = {"vitalitymdtoronto": "vit", "signature_cosmetic_clinic": "sig", "laserbodymd": "las", "skinvitality": "skv", "spamedicamedspa": "spa"}
SVC = [("injectables", "Injectables"), ("rf_microneedling", "RF microneedling"), ("body_contouring", "Body contouring"),
       ("medical_weight_loss", "Medical weight loss"), ("laser_hair_removal", "Laser hair removal"), ("iv_therapy", "IV therapy")]
# caption keywords used to count posts that name each service category (published in the methodology)
SVC_WORDS = {"injectables": ["botox", "filler", "sculptra", "injectable", "neuromodulator", "dysport", "juvederm", "skinvive", "radiesse", "injection"],
             "rf_microneedling": ["morpheus", "potenza", "scarlet", "rf microneedling"],
             "body_contouring": ["coolsculpt", "emsculpt", "bodyfx", "sculpsure", "body contour"],
             "medical_weight_loss": ["semaglutide", "ozempic", "wegovy", "mounjaro", "tirzepatide", "glp-1"],
             "laser_hair_removal": ["laser hair"], "iv_therapy": ["iv therapy", "iv drip", "nad+", "iv lounge"]}


def long_date(d, year=True):
    d = d if isinstance(d, dt.date) else dt.date.fromisoformat(str(d)[:10])
    return f"{d.day} {MONTHS[d.month - 1]}" + (f" {d.year}" if year else "")


def num(x):
    if x is None:
        raise ValueError("missing value used in text")
    x = float(x)
    return f"{x:,.0f}" if abs(x - round(x)) < 1e-9 else f"{x:,.1f}"


def med(v):
    return st.median(v) if v else None


ap = argparse.ArgumentParser()
ap.add_argument("--target", choices=["draft", "release"], default="draft")
ap.add_argument("--published-at", help="release only: ISO 8601 time of the production deployment that first publishes edition 003")
ap.add_argument("--modified-at", help="release only: ISO 8601 time with offset for dateModified")
ap.add_argument("--modified-source", help="release only: deployment id and commit behind --modified-at")
args = ap.parse_args()
if args.target == "release":
    assert args.published_at and args.modified_at and args.modified_source, "release needs --published-at, --modified-at and --modified-source"
    dt.datetime.fromisoformat(args.modified_at.replace("Z", "+00:00"))

CFG = json.load(open(ED / "edition_003.json"))
M = json.load(open(ED / "metrics.json"))
OBS = json.load(open(ED / "observations.json"))
ACC = json.load(open(ED / "accounts.json"))["accounts"]
SV = json.load(open(ED / "services.json"))
ADL = json.load(open(ED / "adlibrary.json"))
COD = json.load(open(ED / "coding.json"))
LED = json.load(open(ED / "run_ledger.json"))
assert M["edition"] == OBS["edition"] == CFG["edition"] == "003"
assert M["window"] == OBS["window"] == CFG["window"], "metrics, observations and edition_003.json disagree on the window"
W0, W1 = (dt.date.fromisoformat(x) for x in CFG["window"])
assert (W1 - W0).days == 29 and W1 == dt.date.fromisoformat(CFG["collected_on"]) - dt.timedelta(days=1)
A = {a["handle"]: a for a in ACC}
assert set(A) == set(ALIAS) == set(M["accounts"]) == set(SV["services"])
posts = OBS["posts"]
win = [p for p in posts if p["in_window"]]
readable = [h for h in ALIAS if M["accounts"][h]["accessible"]]
own = [p for p in win if p["own_post"]]
# reconcile derived metrics against the observations they came from
for h in readable:
    m = M["accounts"][h]
    pw = [p for p in win if p["account"] == h]
    po = [p for p in pw if p["own_post"]]
    assert m["posts_in_window"] == len(pw) and m["own_posts"] == len(po)
    assert m["median_likes"] == med([p["likes"] for p in po if p["likes"] is not None])
    assert m["median_plays"] == med([p["plays"] for p in po if p["format"] == "reel" and p["plays"] is not None])
    assert m["coverage"] == "complete", f"{h}: coverage did not reach the window start; the page text assumes complete coverage"
for p in win:
    assert p["shortcode"] in COD["posts"], f"post {p['shortcode']} has no content coding"
assert set(COD["standout_visuals"]) == {M["accounts"][h]["standout"]["shortcode"] for h in readable}, \
    "standout visuals must be written for exactly the current standout posts (inspect the new post before describing it)"
FR = json.load(open(ED / "frames.json"))["frames"]
assert set(FR) == set(COD["standout_frames"]) == set(COD["standout_visuals"]), \
    "every standout post needs a self-hosted cover frame (frames_003.py) and reviewed alt text (coding.json standout_frames)"
for sc, f in FR.items():
    fp = REPO / f["frame"].lstrip("/")
    assert fp.exists() and hashlib.sha256(fp.read_bytes()).hexdigest() == f["frame_sha256"], f"{sc}: frame file missing or changed since frames.json"

# ---- tokens --------------------------------------------------------------------------------------
T = {"COLLECTED": long_date(CFG["collected_on"]), "WSTART": long_date(W0), "WEND": long_date(W1),
     "WSTART_SHORT": long_date(W0, False), "WINDOW_DAYS": str((W1 - W0).days + 1), "EDITION": "003"}
cap0 = dt.datetime.fromisoformat(next(r for r in LED["runs"] if r["stage"] == "profiles")["started_at"].replace("Z", "+00:00")).astimezone(TZ)
cap1 = dt.datetime.fromisoformat(M["accounts"]["laserbodymd"]["followers_captured_at"].replace("Z", "+00:00")).astimezone(TZ)
fmt_t = lambda t: t.strftime("%-I:%M %p").lower().replace("am", "a.m.").replace("pm", "p.m.")
T["CAPTURE"] = f"{long_date(cap1.date())}, between {fmt_t(cap0)} and {fmt_t(cap1)} Toronto time"
for h, al in ALIAS.items():
    m = M["accounts"][h]
    T[f"a.{al}.brand"] = E(A[h]["brand"])
    T[f"a.{al}.handle"] = "@" + h
    T[f"a.{al}.ig"] = A[h]["instagram_url"]
    if not m["accessible"]:
        continue
    for f in ("followers", "posts_in_window", "own_posts", "collab_posts", "reels", "carousels", "statics", "likes_visible",
              "likes_hidden", "median_likes", "median_comments", "comments_counted", "reels_with_plays", "median_plays"):
        T[f"a.{al}.{f}"] = num(m[f])
    s = m["standout"]
    T[f"s.{al}.url"] = s["url"]
    T[f"s.{al}.date"] = long_date(s["published_local"])
    T[f"s.{al}.format"] = s["format"]
    for f in ("likes", "comments", "plays", "likes_vs_median", "plays_vs_median"):
        if s.get(f) is not None:
            T[f"s.{al}.{f}"] = num(s[f])
    T[f"s.{al}.visual"] = COD["standout_visuals"][s["shortcode"]]
    T[f"s.{al}.img"] = FR[s["shortcode"]]["frame"]
    T[f"s.{al}.alt"] = COD["standout_frames"][s["shortcode"]]
    ct = Counter(COD["posts"][p["shortcode"]]["type"] for p in win if p["account"] == h and p["own_post"])
    tp = Counter(COD["posts"][p["shortcode"]]["topic"] for p in win if p["account"] == h and p["own_post"])
    for k, v in ct.items():
        T[f"t.{al}.{k.split()[0]}"] = num(v)
    for k, v in tp.items():
        T[f"tp.{al}.{k.split()[0]}"] = num(v)
P_ = M["pooled"]
for k, v in P_.items():
    T[f"p.{k}"] = num(v)
T["p.posts_all"] = num(sum(M["accounts"][h]["posts_in_window"] for h in readable))
T["p.readable"] = num(len(readable))
nontreat = [p for p in own if COD["posts"][p["shortcode"]]["type"] in ("recognition", "team and people", "greeting", "trend or third-party content")]
T["p.nontreat"] = num(len(nontreat))
T["p.treat"] = num(sum(1 for p in own if COD["posts"][p["shortcode"]]["type"] == "treatment"))
mc = max(own, key=lambda p: p["comments"] or 0)
T["x.max_comments"] = num(mc["comments"])
T["x.max_comments_acct"] = E(A[mc["account"]]["brand"])
ms, mv = M["accounts"]["signature_cosmetic_clinic"]["median_plays"], M["accounts"]["vitalitymdtoronto"]["median_plays"]
T["x.ratio_plays"] = num(round(ms / mv, 1))
vit_own = [p for p in own if p["account"] == "vitalitymdtoronto"]
T["x.vit_womens"] = num(sum(1 for p in vit_own if COD["posts"][p["shortcode"]]["topic"] in ("menopause and hormones", "pelvic and sexual health")))
sig_own = [p for p in own if p["account"] == "signature_cosmetic_clinic"]
for f in ("reel", "carousel", "static"):
    T[f"x.sig_likes_{f}"] = num(med([p["likes"] for p in sig_own if p["format"] == f]))
T["x.sig_results_likes_max"] = num(max(p["likes"] for p in sig_own if COD["posts"][p["shortcode"]]["type"] == "results or patient story"))
T["x.sig_reel_plays_min"] = num(min(p["plays"] for p in sig_own if p["format"] == "reel"))
trend = [p for p in sig_own if COD["posts"][p["shortcode"]]["type"] == "trend or third-party content"]
assert len(trend) == 1
T["x.sig_trend_plays"] = num(trend[0]["plays"])
mcs = [M["accounts"][h]["median_comments"] for h in readable]
T["x.min_med_comments"], T["x.max_med_comments"] = num(min(mcs)), num(max(mcs))
assert not any(any(w in p["caption"].lower() for w in SVC_WORDS["injectables"]) for p in own if p["account"] == "vitalitymdtoronto"), \
    "the VitalityMD text says no caption named an injectable"
assert sum(1 for p in own if p["account"] == "spamedicamedspa" and COD["posts"][p["shortcode"]]["type"] != "treatment") == 2, "patterns text: two of SpaMedica's three"
T["x.sig_collab_owner"] = "@" + ", @".join(M["accounts"]["signature_cosmetic_clinic"]["collab_owners"])
T["x.vit_reel_plays_max"] =num(max(p["plays"] for p in vit_own if p["format"] == "reel"))


def before_window(h):
    return sorted([p for p in posts if p["account"] == h and not p["in_window"] and not p["pinned"] and p["published_local"][:10] < W0.isoformat()],
                  key=lambda p: p["published_local"], reverse=True)


lb = before_window("laserbodymd")
T["x.las_prev"] = long_date(lb[0]["published_local"])
T["x.las_gap_days"] = num((dt.date.fromisoformat(M["accounts"]["laserbodymd"]["standout"]["published_local"][:10]) - dt.date.fromisoformat(lb[0]["published_local"][:10])).days)
T["x.las_feb_jun"] = num(sum(1 for p in posts if p["account"] == "laserbodymd" and "2026-02-01" <= p["published_local"][:10] <= "2026-06-30"))
sb = before_window("spamedicamedspa")
T["x.spa_prev"] = long_date(sb[0]["published_local"])
T["x.spa_prev2"] = long_date(sb[1]["published_local"])
# service mentions in own-post captions (window, readable accounts)
for key, words in SVC_WORDS.items():
    T[f"m.{key}"] = num(sum(1 for p in own if any(w in p["caption"].lower() for w in words)))
T["m.words"] = "; ".join(f"{lab}: {', '.join(SVC_WORDS[k])}" for k, lab in SVC)
T["x.unattributed"] = num(len(OBS["unattributed"]))
T["x.records"] = num(next(r for r in LED["runs"] if r["stage"] == "posts")["items"])
T["x.caps"] = f"{sum(float(r.get('cap_usd') or 0) for r in LED['runs']):.2f}"

# ---- generated blocks ----------------------------------------------------------------------------
def cell(v, txt=None, cls="r"):
    dv = "" if v is None else f' data-v="{v}"'
    return f'<td class="{cls}"{dv}>{txt if txt is not None else ("Not readable" if v is None else num(v))}</td>'


rows = []
for h, al in ALIAS.items():
    m, a = M["accounts"][h], A[h]
    name = f'<td class="brandcell" data-v="{E(a["brand"])}"><a href="{a["instagram_url"]}" target="_blank" rel="noopener">{E(a["brand"])}</a><span class="handle">@{h}</span></td>'
    loc = f'<td data-v="{E(a["locations"])}">{E(a["locations"].capitalize())}</td>'
    if not m["accessible"]:
        rows.append(f"<tr>{name}{loc}" + "".join(cell(None) for _ in range(6)) + '<td class="wrap-cell" data-v="z">21+ viewing restriction: not readable</td></tr>')
        continue
    posts_txt = num(m["posts_in_window"]) + (f'<span class="cell-sub">{num(m["own_posts"])} own, {num(m["collab_posts"])} collaboration</span>' if m["collab_posts"] else "")
    mix = f'{num(m["reels"])} / {num(m["carousels"])} / {num(m["statics"])}'
    lk = num(m["median_likes"]) + f'<span class="cell-sub">likes visible on {num(m["likes_visible"])} of {num(m["own_posts"])}</span>'
    cm = num(m["median_comments"]) + f'<span class="cell-sub">{num(m["comments_counted"])} post{"s" if m["comments_counted"] != 1 else ""}</span>'
    pl = num(m["median_plays"]) + f'<span class="cell-sub">{num(m["reels_with_plays"])} reel{"s" if m["reels_with_plays"] != 1 else ""}</span>'
    rows.append(f"<tr>{name}{loc}{cell(m['followers'])}{cell(m['posts_in_window'], posts_txt)}{cell(m['reels'], mix)}"
                f"{cell(m['median_likes'], lk)}{cell(m['median_comments'], cm)}{cell(m['median_plays'], pl)}"
                f'<td class="wrap-cell" data-v="a">Complete for the window</td></tr>')
B = {"TABLE_ROWS": "\n".join(rows)}

srows = []
for h in ALIAS:
    s = SV["services"][h]
    tds = []
    for k, _ in SVC:
        e = s[k]
        mark = "Yes" if e["status"] == "Confirmed" else "Not confirmed"
        tds.append(f'<td><a href="{e["source"]}" target="_blank" rel="noopener">{mark}</a><span class="cell-sub">{E(e["detail"])}</span></td>')
    srows.append(f'<tr><td class="brandcell">{E(A[h]["brand"])}</td>{"".join(tds)}</tr>')
B["SERVICE_ROWS"] = "\n".join(srows)

arows = []
for h in ALIAS:
    a = A[h]
    arows.append(f'<tr><td class="brandcell">{E(a["brand"])}</td><td><a href="{a["instagram_url"]}" target="_blank" rel="noopener">@{h}</a></td>'
                 f'<td><a href="{a["official_website"]}" target="_blank" rel="noopener">{E(a["official_website"].split("//")[1].rstrip("/"))}</a></td>'
                 f'<td class="wrap-cell">{E(a["locations"].capitalize())}: {E(a["coverage"])}</td><td class="wrap-cell">{E(a["account_note"])} Checked {long_date(a["verification_date"])}.</td></tr>')
B["ACCOUNT_ROWS"] = "\n".join(arows)
B["ADLIB_ROWS"] = "\n".join(f'<li>{E(c["brand"])}: <a href="{E(c["source"])}" target="_blank" rel="noopener">Ad Library search</a>, {E(c["status"])} ({long_date(ADL["checked_on"])}).</li>' for c in ADL["checks"])

# edition history (no publication date for 003 until release)
if args.target == "release":
    h003 = f'Published {long_date(args.published_at)}. Window {T["WSTART"]} to {T["WEND"]}; data collected {T["COLLECTED"]}. <a href="/medspa-index/edition-003">Snapshot</a>'
else:
    h003 = f'Not yet published (release candidate). Window {T["WSTART"]} to {T["WEND"]}; data collected {T["COLLECTED"]}. A fixed snapshot is created at publication.'
B["HISTORY_003"] = h003
B["CITE_SNAPSHOT"] = ('For a fixed version, cite the <a href="/medspa-index/edition-003">edition 003 snapshot</a>.' if args.target == "release"
                      else "A fixed edition 003 snapshot will be created at publication; until then, cite this address with the collection date.")

tpl = (ED / "body_template.html").read_text()
used = set(re.findall(r"\{\{([^{}]+)\}\}", tpl))


def fill(mo):
    k = mo.group(1)
    if k.startswith("BLOCK:"):
        return B[k[6:]]
    if k not in T:
        raise KeyError(f"template token {{{{{k}}}}} has no value: check the data or the template")
    return T[k]


body = re.sub(r"\{\{([^{}]+)\}\}", fill, tpl)
assert "{{" not in body and "}}" not in body
assert "—" not in body and "–" not in body and "&mdash;" not in body and "&ndash;" not in body, "em or en dash in the body"
assert body.count("<h1") == 1, "exactly one H1"
for w in ("viral", "winning", "the best", "top-performing"):
    assert w not in body.lower(), f"banned wording: {w}"
assert 'href="/contact?intent=review&amp;entry=research_gta_medspa#contact-form" data-review-cta="research_gta_medspa"' in body, "the review CTA must keep its destination and entry value"

# FAQ JSON-LD from the visible FAQ
faq = re.findall(r'<details class="ri-adv faq"><summary>(.*?)</summary>\s*<p>(.*?)</p>', body, re.S)
assert len(faq) >= 3
strip = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s)).strip()

# ---- head ----------------------------------------------------------------------------------------
TITLE = "Med Spa Index: Ontario Med Spa Instagram | HelpMeMarketing"
DESC = "How five selected Ontario med spas use Instagram: posts, formats, visible likes, comments and reel plays, with three tests a clinic could run. By Ankit Kumar."
OG_DESC = "Five selected Ontario med spas on Instagram: what they post, the visible response, and three tests a clinic owner could run."
assert 30 <= len(TITLE) <= 60 and TITLE.endswith(" | HelpMeMarketing"), len(TITLE)
assert 70 <= len(DESC) <= 158, len(DESC)
assert len(OG_DESC) <= 200
OG_TITLE = TITLE.replace(" | HelpMeMarketing", "")
OG_IMG = f"{SITE}/assets/index/gta-medspa/medspa-index-og.jpg"
article = {"@context": "https://schema.org", "@type": "Article", "headline": "Med Spa Index", "description": DESC,
           "image": {"@type": "ImageObject", "url": OG_IMG, "width": 1200, "height": 630},
           "author": {"@type": "Person", "@id": f"{SITE}/about#ankit-kumar", "name": "Ankit Kumar", "url": f"{SITE}/about"},
           "publisher": {"@type": "Organization", "@id": f"{SITE}/#organization", "name": "HelpMeMarketing", "url": f"{SITE}/"},
           "mainEntityOfPage": f"{SITE}/medspa-index",
           "isPartOf": {"@type": "WebPage", "@id": f"{SITE}/medspa-marketing-research", "url": f"{SITE}/medspa-marketing-research"},
           "about": "Instagram posting activity and visible engagement of five selected Ontario med spa accounts"}
if args.target == "release":
    article["dateModified"] = args.modified_at
dataset = {"@context": "https://schema.org", "@type": "Dataset",
           "name": "Med Spa Index edition 003: Instagram posts of five selected Ontario med spa accounts",
           "description": f"Public Instagram posts published between {T['WSTART']} and {T['WEND']} by four of five selected Ontario med spa accounts (one was not readable), with format, visible likes, comments and recorded reel plays. It does not include enquiries, consultations or revenue and is not a sample of the market.",
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
# the snapshot's breadcrumb ends at the snapshot itself, as on the edition 002 snapshot
snap_crumb = {**crumb, "itemListElement": crumb["itemListElement"] + [
    {"@type": "ListItem", "position": 4, "name": "Edition 003", "item": f"{SITE}/medspa-index/edition-003"}]}
LDS = {m: "\n".join(f'<script type="application/ld+json">\n{json.dumps(x, ensure_ascii=False, separators=(",", ":"))}\n</script>' for x in (c, article, dataset, faqld))
       for m, c in (("page", crumb), ("snapshot", snap_crumb))}
EXTRA = (HERE / "editions" / "003" / "head_extra.html").read_text().strip()


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
    canon = f"{SITE}/medspa-index/edition-003" if mode == "snapshot" else f"{SITE}/medspa-index"
    s = sub1(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{canon}">', s)
    s = sub1(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{canon}">', s)
    s = sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{E(OG_TITLE)}">', s)
    s = sub1(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{E(OG_TITLE)}">', s)
    s = sub1(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{E(OG_DESC)}">', s)
    s = sub1(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{E(OG_DESC)}">', s)
    s = sub1(r'<meta property="og:image:alt" content="[^"]*">', '<meta property="og:image:alt" content="HMM research graphic: Med Spa Index, a comparison of five selected Ontario med spa Instagram accounts">', s)
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', "", s, flags=re.S)
    gtm = "<!-- End Google Tag Manager -->\n"
    assert s.count(gtm) == 1, "the head must carry one GTM loader end marker"
    s = s.replace(gtm, gtm + LDS["snapshot" if mode == "snapshot" else "page"] + "\n", 1)
    assert s.count("application/ld+json") == 4, "JSON-LD blocks not placed"
    s = re.sub(r"\n<!-- MSI003 START -->.*?<!-- MSI003 END -->", "", s, flags=re.S)
    s = sub1(r"</style></head>", "</style>\n<!-- MSI003 START -->\n" + EXTRA + "\n<!-- MSI003 END --></head>", s)
    a = s.index("<!-- ===== GTA MEDSPA INDEX REPORT BODY START")
    a = s.index("\n", a) + 1
    b = s.index("<!-- ===== GTA MEDSPA INDEX REPORT BODY END")
    s = s[:a] + body + "\n" + s[b:]
    if mode == "snapshot":
        s = s.replace("</head>", "<!-- Snapshot of edition 003 as first published. Research content in this snapshot is never rewritten; record any later metadata fix in this comment. -->\n</head>", 1)
    return s


shell = PAGE.read_text()
mode = "live" if args.target == "release" else "draft"
out = make(shell, mode)
assert make(out, mode) == out, "the build is not idempotent"
assert out.count("<h1") == 1
if mode == "draft" and CFG.get("status") == "published":  # a draft build would turn the live page into a noindex draft
    raise SystemExit("edition 003 is published: rebuild with --target release and the published_at, modified_at and modified_at_source recorded in editions/003/edition_003.json")
PAGE.write_text(out)

# ---- dataset CSVs (the actual current dataset behind the page) -------------------------------------
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

# ---- snapshot (release only, never rewritten) ------------------------------------------------------
if args.target == "release":
    snap = REPO / "medspa-index" / "edition-003.html"
    if snap.exists():
        print(f"snapshot kept as published: {snap.relative_to(REPO)}")
    else:
        snap.parent.mkdir(exist_ok=True)
        snap.write_text(make(out, "snapshot"))
    hub = REPO / "medspa-marketing-research.html"  # the hub card describes edition 003, so its dates follow this release
    h = hub.read_text()
    h, k1 = re.subn(r'("dateModified":")[^"]*', lambda m: m.group(1) + args.modified_at, h, 1)
    tor = long_date(dt.datetime.fromisoformat(args.modified_at.replace("Z", "+00:00")).astimezone(TZ).date())
    h, k2 = re.subn(r"(Published \d+ \w+ \d{4} &middot; Updated )\d+ \w+ \d{4}", lambda m: m.group(1) + tor, h, 1)
    assert k1 == 1 and k2 == 1, "research hub date markers not found"
    hub.write_text(h)
    CFG.update({"status": "published", "published_at": args.published_at, "modified_at": args.modified_at, "modified_at_source": args.modified_source})
    json.dump(CFG, open(ED / "edition_003.json", "w"), indent=1)
print(f"PASS {args.target}: medspa-index.html ({len(out):,} bytes), {len(used)} tokens, {len(faq)} FAQ, CSVs in assets/index/medspa/")
