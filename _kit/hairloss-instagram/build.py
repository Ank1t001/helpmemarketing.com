#!/usr/bin/env python3
"""Assemble and validate the Hair Loss Index page and its edition snapshot. Standard library only.

  python3 build.py --edition NNN --as-of YYYY-MM-DD                build output/hair-loss-index.html and output/edition-NNN.html
  python3 build.py --edition NNN --as-of YYYY-MM-DD --check-live   also require the page to equal ../../hair-loss-index.html byte for byte

Inputs: site_shell.html (copy of the live page), report_body.html (the approved body with {{TOKENS}}),
edition.json (dates, modified_at), roster.json, editions/NNN/blocks.json (generated rows, stage tables, post log, CSV).
"""
import json, re, sys, html, argparse
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
U = "https://helpmemarketing.com/hair-loss-index"
A = "<!-- ===== HAIR LOSS INDEX REPORT BODY START"
E = "<!-- ===== HAIR LOSS INDEX REPORT BODY END ===== -->"
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
SECTIONS = ["ri-overview", "ri-rankings", "ri-journey", "ri-creative", "ri-insights", "ri-test", "ri-download", "ri-advanced", "ri-editions", "ri-data"]
HEADINGS = ["Account", "Score", "Followers", "Posts", "Reels", "Plays / foll", "Avg likes", "Avg comm", "Flag", "Top post"]
RETIRED = [r"\bpercent\b", r"\bCycle\b", r"\bcycle 0", r"\bwinning\b", "verbatim", r"\bhonest", r"\bproves\b", "proof that", r"\bbest[- ]performing\b",
           r"\bviews\b", "people per reel", "one-day", "each caption", "reaches roughly", "Instance 0", "Advanced research", "What the index says to do",
           "Take the dataset with you", "Hook, first line", r"\bbookings? (rose|grew|increased|went up)\b", "caused by the"]
LAYOUT = ["Expandables, one pattern", "UX spacing pass 2", "data-ri-reading", "data-bar-widths", ".msi.msi .flag.neutral", "bandbar neutral"]


def long(d):
    d = date.fromisoformat(d)
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def text(h):
    h = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", h))


def assemble(state, ed, as_of):
    shell = (HERE / "site_shell.html").read_text()
    body = (HERE / "report_body.html").read_text()
    blocks = json.load(open(HERE / "editions" / ed / "blocks.json"))
    nxt = state["next_scheduled_refresh"]
    tok = {"LAST_VERIFIED_LONG": long(state["scraped_at"]), "NEXT_REFRESH_LONG": long(nxt), "EDITION": ed,
           "OVERDUE": ", not yet published" if as_of > date.fromisoformat(nxt) else "", **blocks}
    for k, v in tok.items():
        body = body.replace("{{" + k + "}}", v)
    left = re.findall(r"\{\{[A-Z_0-9]+\}\}", body)
    if left:
        raise SystemExit(f"unfilled tokens: {left}")
    a, b = shell.index(A), shell.index(E) + len(E)
    page = shell[:a] + body + shell[b:]
    page, k1 = re.subn(r'("@type":"Article".*?"dateModified":")[^"]*(")', lambda m: m.group(1) + state["modified_at"] + m.group(2), page, count=1, flags=re.S)
    if k1 != 1:
        raise SystemExit("Article dateModified not found in the head")
    return page, body


def snapshot(page, ed, data_long):
    s = page
    def rep(x, y):
        nonlocal s
        if s.count(x) != 1:
            raise SystemExit(f"snapshot: expected one '{x[:60]}', found {s.count(x)}")
        s = s.replace(x, y)
    rep(f'<link rel="canonical" href="{U}">', f'<link rel="canonical" href="{U}/edition-{ed}">')
    s = re.sub(r'<meta name="robots" content="[^"]*">', f'<meta name="robots" content="noindex, follow">\n<!-- Snapshot of edition {ed}. Research content in this snapshot is never rewritten; record any later metadata fix in this comment and add a visible dated note for any visible correction. -->', s, count=1)
    rep(f'<meta property="og:url" content="{U}">', f'<meta property="og:url" content="{U}/edition-{ed}">')
    rep(f'"name": "The Hair Loss Index: Instagram", "item": "{U}"}}]}}', f'"name": "The Hair Loss Index: Instagram", "item": "{U}"}}, {{"@type": "ListItem", "position": 4, "name": "Edition {ed}", "item": "{U}/edition-{ed}"}}]}}')
    rep(f'"url":"{U}","isAccessibleForFree"', f'"url":"{U}/edition-{ed}","isAccessibleForFree"')
    rep('</div></header>\n<div class="livebar">', f'</div></header>\n<div class="note warn"><span class="lbl">Archived edition {ed}</span><p>Data collected {data_long}. This snapshot does not change. <a href="/hair-loss-index">See the current edition</a>.</p></div>\n<div class="livebar">')
    rep(f'Data collected {data_long}. <a href="{U}">{U}</a></p>\n<p class="dek m0">This address always shows the latest edition. For a fixed version, cite the <a href="/hair-loss-index/edition-{ed}">edition {ed} snapshot</a>.',
        f'Data collected {data_long}. <a href="{U}/edition-{ed}">{U}/edition-{ed}</a></p>\n<p class="dek m0">This is the fixed snapshot of edition {ed}. The <a href="/hair-loss-index">current edition</a> lives at /hair-loss-index.')
    rep(f"<td><b>{ed}</b> (this page)</td>", f"<td><b>{ed}</b> (this snapshot)</td>")
    return s


def validate(page, body, snap, state, ed):
    errs = []
    def need(cond, msg):
        if not cond:
            errs.append(msg)
    er = HERE / "editions" / ed / "roster.json"  # an edition published on an earlier roster keeps it
    roster = json.load(open(er if er.exists() else HERE / "roster.json"))
    ids = re.findall(r'<section id="([^"]+)"', body)
    need(ids == SECTIONS, f"section order {ids}")
    need(not re.search(r'\sstyle="', body), "style attribute in body")
    for f, s in (("page", page), ("snapshot", snap)):
        need(not re.search(r"[–—]|&[mn]dash;", s), f"em or en dash in {f}")
    vis = text(body)
    vis_log = vis.split("Open the post log")[0]
    vis_log = re.sub(r"Corrections, .*?Edition history", " ", vis_log, flags=re.S)  # the corrections note quotes retired wording on purpose
    for w in RETIRED:
        need(not re.search(w, vis_log), f"retired wording: {w!r}")
    th = [text(x).strip() for x in re.findall(r"<th[^>]*>(.*?)</th>", re.search(r'<section id="ri-rankings">.*?</thead>', body, re.S).group(0), re.S)]
    need(th == HEADINGS, f"scoreboard headings {th}")
    rows = re.findall(r'<tr data-note="([^"]*)">\n<td class="brandcell"><a [^>]*>([^<]+)</a>', body)
    need(len(rows) == len(roster["brands"]), f"{len(rows)} scoreboard rows, expected {len(roster['brands'])} (every roster brand stays on the board)")
    need(all(len(n.strip()) > 20 for n, _ in rows), "a scoreboard row has no plain-sentence data-note")
    pos = re.findall(r'<div class="cell-sub">#(\d+) of (\d+) ranked</div>', body)
    need(pos and [int(p) for p, _ in pos] == list(range(1, len(pos) + 1)) and all(int(t) == len(pos) for _, t in pos), "ranked positions are not #1 to #N of N in order")
    lead = re.search(r"<b>Which brand leads this edition\?</b>\s*([^<]+)", body)
    need(lead and rows and html.unescape(rows[0][1]) in html.unescape(lead.group(1)), "leader answer does not name the number one brand")
    need(f"Edition {ed}. Data collected {long(state['scraped_at'])}." in vis, "citation does not read 'Edition NNN. Data collected <date>.'")
    need(re.search(rf"<td><b>{ed}</b> \(this page\)</td>", body), "edition history lacks this edition's '(this page)' row")
    need(f'GATE_SOURCE="hair-loss-cycle-{ed}"' in body and "form:'index-download'" in body and "script.google.com/macros/s/" in body, "gate source, form or endpoint changed")
    need(f"hair-loss-index-edition-{ed}-postlog.csv" in body, "download file name does not carry this edition")
    for href in re.findall(r'href="(https://www\.instagram\.com/p/[^"]*)"', body):
        if not re.fullmatch(r"https://www\.instagram\.com/p/[A-Za-z0-9_-]{10,12}/", href):
            errs.append(f"bad post link {href}")
            break
    need("api.apify.com" not in page, "Apify URL in page")
    for src in re.findall(r'<img src="([^"]+)"', body):
        need(src.startswith("/assets/index/hair-loss/") and (REPO / src.lstrip("/")).exists(), f"frame missing or off path: {src}")
    csvtxt = json.loads(re.search(r"var GATED_CSV=(\".*\");", body).group(1))
    need(len(csvtxt.strip().splitlines()) - 1 == len(re.findall(r"<tr data-brand=", body)), "CSV rows differ from post log rows")
    for wv in re.findall(r'data-w="([^"]+)"', body):
        need(0 < float(wv) <= 100, f"bar width out of range: {wv}")
    blocks = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', page, re.S)
    try:
        js = [json.loads(b) for b in blocks]
    except ValueError as e:
        js = []
        errs.append(f"JSON-LD does not parse: {e}")
    art = next((j for j in js if j.get("@type") == "Article"), {})
    need(art.get("headline") == "The Hair Loss Index", "Article headline")
    need(art.get("dateModified") == state["modified_at"], "dateModified differs from edition.json modified_at")
    need("datePublished" not in art, "datePublished present")
    need(art.get("author", {}).get("@id") == "https://helpmemarketing.com/about#ankit-kumar", "author @id")
    need(art.get("publisher", {}).get("@id") == "https://helpmemarketing.com/#organization", "publisher @id")
    need(art.get("image", {}).get("url") == "https://helpmemarketing.com/assets/index/hair-loss/og.jpg", "Article image")
    need(any(j.get("@type") == "BreadcrumbList" for j in js), "BreadcrumbList missing")
    need(page.count(f'<link rel="canonical" href="{U}">') == 1 and len(re.findall(r'name="robots"', page)) == 1 and "noindex" not in page.split("</head>")[0], "page canonical or robots")
    need("<title>The Hair Loss Index: Instagram | HelpMeMarketing</title>" in page, "title changed")
    need(snap.count(f'<link rel="canonical" href="{U}/edition-{ed}">') == 1 and len(re.findall(r'name="robots"', snap)) == 1 and 'content="noindex, follow"' in snap, "snapshot canonical or robots")
    for mk in LAYOUT:
        need(mk in page, f"layout marker missing: {mk}")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edition", required=True)
    ap.add_argument("--as-of", required=True)
    ap.add_argument("--check-live", action="store_true")
    a = ap.parse_args()
    state = json.load(open(HERE / "edition.json"))
    if state["edition"] != a.edition:
        raise SystemExit(f"edition.json is edition {state['edition']}, not {a.edition}")
    page, body = assemble(state, a.edition, date.fromisoformat(a.as_of))
    snap = snapshot(page, a.edition, long(state["scraped_at"]))
    errs = validate(page, body, snap, state, a.edition)
    out = HERE / "output"
    out.mkdir(exist_ok=True)
    (out / "hair-loss-index.html").write_text(page)
    (out / f"edition-{a.edition}.html").write_text(snap)
    if a.check_live:
        live = (REPO / "hair-loss-index.html").read_text()
        if live != page:
            errs.append("output page is not byte-identical to hair-loss-index.html: the page was changed without the kit")
    if errs:
        print("FAIL\n- " + "\n- ".join(errs))
        sys.exit(1)
    print(f"PASS edition {a.edition}: output/hair-loss-index.html and output/edition-{a.edition}.html")


if __name__ == "__main__":
    main()
