#!/usr/bin/env python3
"""Assemble and validate the GTA MedSpa Index page and its edition snapshot. Standard library only.

  python3 build.py --edition NNN --as-of YYYY-MM-DD           build output/gta-medspa-index.html and output/edition-NNN.html
  python3 build.py --edition NNN --as-of YYYY-MM-DD --check-live   also require the page to equal ../../gta-medspa-index.html byte for byte

Inputs: site_shell.html (copy of the live page), report_body.html (the approved body with {{TOKENS}}),
edition.json (dates, modified_at, Dataset block), editions/NNN/blocks.json (generated rows, post log, CSV).
"""
import json, re, sys, html, argparse
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
U = "https://helpmemarketing.com/gta-medspa-index"
A = "<!-- ===== GTA MEDSPA INDEX REPORT BODY START"
E = "<!-- ===== GTA MEDSPA INDEX REPORT BODY END ===== -->"
H1 = "GTA Medspa Instagram Marketing Benchmarks"
HUB = "https://helpmemarketing.com/medspa-marketing-research"
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
SECTIONS = ["ri-overview", "ri-rankings", "ri-creative", "ri-insights", "ri-test", "ri-download", "ri-advanced", "ri-editions", "ri-data", "ri-help", "faq"]
HEADINGS = ["#", "Clinic", "Area", "Score", "Median plays", "Posts", "Pattern", "Followers", "Peak reel", "Comments / 1k", "Mix"]
RETIRED = [r"\bpercent\b", r"\bCycle\b", r"\bcycle 0", "would not survive", r"\bwinning\b", "verbatim", r"\bhonest", "most expensive place", "not really competing",
           r"\bproves\b", "proof that", "only variable", "Instance 03", "The vision pass", "What the index says to do", "Advanced research",
           "Take the dataset with you", "Hook, first line", "people per reel", "reaches roughly", "leads this edition", "leading clinics", r"\bproven\b"]
LAYOUT = ["Expandables, one pattern", "UX spacing pass 2", "data-ri-reading", "data-bar-widths", ".msi.msi .flag.neutral"]


def long(d):
    d = date.fromisoformat(d)
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def text(h):
    h = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", h))


def faq_jsonld(body):
    sec = re.search(r'<section id="faq">(.*?)</section>', body, re.S).group(1)
    qa = re.findall(r"<details><summary>(.*?)</summary><p>(.*?)</p></details>", sec, re.S)
    ent = [{"@type": "Question", "name": html.unescape(re.sub(r"<[^>]+>", "", q)), "acceptedAnswer": {"@type": "Answer", "text": html.unescape(re.sub(r"<[^>]+>", "", a))}} for q, a in qa]
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": ent}


def assemble(state, ed, as_of):
    shell = (HERE / "site_shell.html").read_text()
    body = (HERE / "report_body.html").read_text()
    blocks = json.load(open(HERE / "editions" / ed / "blocks.json"))
    nxt = state["next_scheduled_refresh"]
    tok = {"LAST_VERIFIED_LONG": long(state["scraped_at"]), "NEXT_REFRESH_LONG": long(nxt), "EDITION": ed,
           "OVERDUE": ", not yet published" if as_of > date.fromisoformat(nxt) else "", **blocks}
    for k, v in tok.items():
        body = body.replace("{{" + k + "}}", v)
    left = re.findall(r"\{\{[A-Z_]+\}\}", body)
    if left:
        raise SystemExit(f"unfilled tokens: {left}")
    a, b = shell.index(A), shell.index(E) + len(E)
    page = shell[:a] + body + shell[b:]
    page, k1 = re.subn(r'("@type":"Article".*?"dateModified":")[^"]*(")', lambda m: m.group(1) + state["modified_at"] + m.group(2), page, count=1, flags=re.S)
    page, k2 = re.subn(r'\{"@context":"https://schema.org","@type":"FAQPage".*?\}(?=\n</script>)', lambda m: json.dumps(faq_jsonld(body), separators=(",", ":"), ensure_ascii=False), page, count=1, flags=re.S)
    page, k3 = re.subn(r'\{"@context":"https://schema.org","@type":"Dataset".*?\}(?=\n</script>)', lambda m: json.dumps(state["dataset"], separators=(",", ":"), ensure_ascii=False), page, count=1, flags=re.S)
    if (k1, k2, k3) != (1, 1, 1):
        raise SystemExit(f"head blocks not found: Article {k1}, FAQPage {k2}, Dataset {k3}")
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
    rep(f'"name":"{H1}","item":"{U}"}}]}}', f'"name":"{H1}","item":"{U}"}},{{"@type":"ListItem","position":4,"name":"Edition {ed}","item":"{U}/edition-{ed}"}}]}}')
    rep(f'"url":"{U}","isPartOf"', f'"url":"{U}/edition-{ed}","isPartOf"')
    rep('</div></header>\n<div class="livebar">', f'</div></header>\n<div class="note warn"><span class="lbl">Archived edition {ed}</span><p>Data collected {data_long}. This snapshot does not change. <a href="/gta-medspa-index">See the current edition</a>.</p></div>\n<div class="livebar">')
    rep(f'Data collected {data_long}. <a href="{U}">{U}</a></p>\n<p class="dek m0">This address always shows the latest edition. For a fixed version, cite the <a href="/gta-medspa-index/edition-{ed}">edition {ed} snapshot</a>.',
        f'Data collected {data_long}. <a href="{U}/edition-{ed}">{U}/edition-{ed}</a></p>\n<p class="dek m0">This is the fixed snapshot of edition {ed}. The <a href="/gta-medspa-index">current edition</a> lives at /gta-medspa-index.')
    rep(f"<td><b>{ed}</b> (this page)</td>", f"<td><b>{ed}</b> (this snapshot)</td>")
    return s


def validate(page, body, snap, state, ed):
    errs = []
    def need(cond, msg):
        if not cond:
            errs.append(msg)
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
    rows = re.findall(r'<tr data-note="([^"]*)"><td class="r rank">(\d+)</td>.*?</tr>', body)
    need(len(rows) == 25, f"{len(rows)} scoreboard rows, expected 25")
    need(all(len(n.strip()) > 20 for n, _ in rows), "a scoreboard row has no plain-sentence data-note")
    need([int(r) for _, r in rows] == list(range(1, len(rows) + 1)), "scoreboard ranks are not 1 to 25 in order")
    lead = re.search(r"<b>Which clinic scored highest in this edition\?</b>\s*([^<]+)", body)
    first = re.search(r'<td class="r rank">01</td><td class="brandcell"><a [^>]*>([^<]+)</a>', body)
    need(lead and first and html.unescape(first.group(1)) in html.unescape(lead.group(1)), "highest-score answer does not name the number one clinic")
    need(f"Edition {ed}. Data collected {long(state['scraped_at'])}." in vis, "citation does not read 'Edition NNN. Data collected <date>.'")
    need(re.search(rf"<td><b>{ed}</b> \(this page\)</td>", body), "edition history lacks this edition's '(this page)' row")
    need(f'GATE_SOURCE="gta-medspa-cycle-{ed}"' in body and "form:'index-download'" in body and "script.google.com/macros/s/" in body, "gate source, form or endpoint changed")
    need(f"gta-medspa-index-edition-{ed}-postlog.csv" in body, "download file name does not carry this edition")
    for href in re.findall(r'href="(https://www\.instagram\.com/p/[^"]*)"', body):
        if not re.fullmatch(r"https://www\.instagram\.com/p/[A-Za-z0-9_-]{11}/", href):
            errs.append(f"bad post link {href}")
            break
    need("api.apify.com" not in page, "Apify URL in page")
    for src in re.findall(r'<img src="([^"]+)"', body):
        need(src.startswith("/assets/index/gta-medspa/frames/") and (REPO / src.lstrip("/")).exists(), f"frame missing or off path: {src}")
    csvtxt = json.loads(re.search(r"var GATED_CSV=(\".*\");", body).group(1))
    need(len(csvtxt.strip().splitlines()) - 1 == len(re.findall(r"<tr data-brand=", body)), "CSV rows differ from post log rows")
    blocks = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', page, re.S)
    try:
        js = [json.loads(b) for b in blocks]
    except ValueError as e:
        js = []
        errs.append(f"JSON-LD does not parse: {e}")
    art = next((j for j in js if j.get("@type") == "Article"), {})
    need(art.get("headline") == H1 and f"<h1>{H1}</h1>" in body, "Article headline or H1")
    need(art.get("isPartOf", {}).get("@id") == HUB and 'href="/medspa-marketing-research"' in body, "research hub link or isPartOf")
    bc = next((j for j in js if j.get("@type") == "BreadcrumbList"), {})
    need([i.get("item") for i in bc.get("itemListElement", [])] == ["https://helpmemarketing.com/", HUB, U], "breadcrumb path")
    need("Not measured:" in vis and "entry=research_gta_medspa" in body, "measurement note or research entry point missing")
    need(art.get("dateModified") == state["modified_at"], "dateModified differs from edition.json modified_at")
    need("datePublished" not in art, "datePublished present")
    need(art.get("author", {}).get("@id") == "https://helpmemarketing.com/about#ankit-kumar", "author @id")
    need(art.get("publisher", {}).get("@id") == "https://helpmemarketing.com/#organization", "publisher @id")
    need(art.get("image", {}).get("url") == "https://helpmemarketing.com/assets/index/gta-medspa/og.jpg", "Article image")
    fq = next((j for j in js if j.get("@type") == "FAQPage"), {})
    vq = [html.unescape(q) for q in re.findall(r"<details><summary>(.*?)</summary>", re.search(r'<section id="faq">.*?</section>', body, re.S).group(0))]
    need([q["name"] for q in fq.get("mainEntity", [])] == vq, "FAQPage questions differ from the visible FAQ")
    need(page.count(f'<link rel="canonical" href="{U}">') == 1 and len(re.findall(r'name="robots"', page)) == 1 and "noindex" not in page.split("</head>")[0], "page canonical or robots")
    need(f"<title>{H1} | HelpMeMarketing</title>" in page, "title changed")
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
    (out / "gta-medspa-index.html").write_text(page)
    (out / f"edition-{a.edition}.html").write_text(snap)
    if a.check_live:
        live = (REPO / "gta-medspa-index.html").read_text()
        if live != page:
            errs.append("output page is not byte-identical to gta-medspa-index.html: the page was changed without the kit")
    if errs:
        print("FAIL\n- " + "\n- ".join(errs))
        sys.exit(1)
    print(f"PASS edition {a.edition}: output/gta-medspa-index.html and output/edition-{a.edition}.html")


if __name__ == "__main__":
    main()
