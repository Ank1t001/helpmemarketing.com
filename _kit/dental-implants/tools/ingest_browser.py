#!/usr/bin/env python3
"""Copy a browser evidence pass into an edition's raw folder, unchanged, with a sha256 manifest and a validation report.

    python3 tools/ingest_browser.py --source DIR --edition 001 --batch browser-20261016 [--check]

DIR is the collecting session's evidence folder (dental_evidence_*.json and .md in out/, logs, pages/, shots/).
Files are copied byte for byte. The only exception: collector scripts that contain a temporary preview share token are
stored with the token replaced by REDACTED, and the manifest records both hashes. Nothing is fetched again.
The validator checks the evidence JSON against the kit's expectations: fixed edition window, collection timestamps,
source URL hosts, Instagram ownership and dates, ad identifiers present in the saved logs, and every screenshot
reference resolved to a stored file or to a recorded hash.
"""
import argparse, hashlib, json, re, shutil, sys
from datetime import datetime, date
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent.parent
TZ = ZoneInfo("America/Toronto")
TOKEN = re.compile(r"_vercel_share=[A-Za-z0-9]+")
LOGS = ["load_log.jsonl", "meta_parsed.json", "google_creatives.jsonl", "google_window.jsonl", "google_window_try1.jsonl",
        "bond_google_creatives.json", "bond_google_links.json", "ig_grid.json", "ig_posts.jsonl", "preview_results.json"]
COLLECTORS = ["load.mjs", "parse_meta.py", "gcr.mjs", "gdate.mjs", "gdate2.mjs", "gwin.mjs", "gbond.mjs", "igpost.mjs", "pv.mjs", "pv2.mjs", "pv3.mjs", "assemble.py"]
NOT_COPIED = {"jar.txt": "cookie jar for the preview share link (credential); never stored"}
# QA screenshots of our own superseded preview build: hashed, not stored. The dark-mode defect screenshot is stored.
STORE_PREVIEW = {"preview-desktop-dark-hero.png"}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def utc(s): return datetime.fromisoformat(s.replace("Z", "+00:00"))

def plan(src):
    out = []
    ev = sorted((src / "out").glob("dental_evidence_*"))
    for f in ev: out.append((f, "evidence/" + f.name))
    for n in LOGS: out.append((src / n, "logs/" + n))
    for f in sorted((src / "pages").glob("*.txt")): out.append((f, "pages/" + f.name))
    for n in COLLECTORS: out.append((src / n, "collector/" + n))
    for f in sorted((src / "shots").rglob("*.png")):
        rel = f.relative_to(src / "shots").as_posix()
        if rel.startswith("preview-") and rel not in STORE_PREVIEW: out.append((f, None))
        else: out.append((f, "shots/" + rel))
    return out

def validate(src, edition_dir, manifest):
    errs, notes = [], []
    E = json.loads(next((src / "out").glob("dental_evidence_*.json")).read_text())
    ed = json.loads((edition_dir / "edition.json").read_text())
    W = ed["window"]
    rw = E["research_window"]
    if (rw["start"], rw["end"], rw["timezone"]) != (W["start"], W["end"], W["timezone"]): errs.append("evidence window differs from edition.json window")
    for k in ("schema", "edition", "prepared_utc", "research_window", "collector", "clinics", "social_identities", "instagram", "ads", "ads_summary", "preview_verification", "unresolved_gaps"):
        if k not in E: errs.append("missing top-level key " + k)
    if E.get("edition") != ed["edition"]: errs.append("edition mismatch")
    if "Not the founder" not in E["collector"]["not"]: errs.append("collector provenance must say it was not the founder's Chrome")
    # collection timestamps: every load in the logs falls inside the pass
    loads = [json.loads(l) for l in (src / "load_log.jsonl").read_text().splitlines() if l.strip()]
    t = sorted(utc(r["started_utc"]) for r in loads)
    for r in [json.loads(l) for l in (src / "ig_posts.jsonl").read_text().splitlines() if l.strip()]: t.append(utc(r["checked_utc"]))
    t.sort(); notes.append(f"browser loads {t[0].isoformat()} to {t[-1].isoformat()}")
    if not all(x.date() == date(2026, 10, 16) for x in t): errs.append("a browser load is not dated 16 October 2026 UTC")
    if any(x.astimezone(TZ).date() <= date.fromisoformat(W["end"]) for x in t): errs.append("a browser load falls inside the research window; collection must follow it")
    # source URL hosts
    for a, x in E["ads"].items():
        for s in x["meta"]["searches"]:
            u = urlparse(s["url"])
            if u.netloc != "www.facebook.com" or not u.path.startswith("/ads/library"): errs.append(f"{a} meta search host {u.netloc}{u.path}")
        g = x["google"]
        for k in ("any_time", "window"):
            if urlparse(g[k]["url"]).netloc != "adstransparency.google.com": errs.append(f"{a} google {k} host")
        if g["window"]["date_label"] != "Custom Sep 16 – Oct 15, 2026": errs.append(f"{a} google window filter label {g['window']['date_label']!r}")
    # Instagram posts: owner is a verified handle, URL matches, date inside the window
    handles = {v["handle"] for v in E["social_identities"].values() if v.get("status") == "verified_link"}
    raw_posts = {json.loads(l)["shortcode"]: json.loads(l) for l in (src / "ig_posts.jsonl").read_text().splitlines() if l.strip()}
    for p in E["instagram"]["posts"]:
        if p["owner"] not in handles: errs.append(f"post {p['shortcode']} owner {p['owner']} is not a verified handle")
        if not re.fullmatch(rf"https://www\.instagram\.com/{re.escape(p['owner'])}/(p|reel)/{p['shortcode']}/", p["url"]): errs.append(f"post {p['shortcode']} URL")
        d = utc(p["published_utc"]).astimezone(TZ).date()
        if not (date.fromisoformat(W["start"]) <= d <= date.fromisoformat(W["end"])): errs.append(f"post {p['shortcode']} outside window")
        r = raw_posts.get(p["shortcode"])
        if not r: errs.append(f"post {p['shortcode']} not in ig_posts.jsonl"); continue
        if r["times"][0]["dt"] != p["published_utc"]: errs.append(f"post {p['shortcode']} date differs from the page <time>")
        m = re.match(r"([\d,]+) likes, ([\d,]+) comments", r["og_desc"] or "")
        if not m or (int(m[1].replace(",", "")), int(m[2].replace(",", ""))) != (p["likes"], p["comments"]): errs.append(f"post {p['shortcode']} metrics differ from the page")
        if p["plays"]["value"] is not None: errs.append(f"post {p['shortcode']} plays must stay missing")
        if p["video_watched"]: errs.append(f"post {p['shortcode']} video_watched")
    # ad identifiers present in saved evidence
    meta = json.loads((src / "meta_parsed.json").read_text())
    ids = {a["library_id"] for v in meta.values() for a in v["ads"]}
    for a, x in E["ads"].items():
        for ad in x["meta"].get("ads", []):
            if ad["library_id"] not in ids: errs.append(f"{a} meta library id {ad['library_id']} not in meta_parsed.json")
    bond = json.loads((src / "bond_google_creatives.json").read_text())
    if len(bond) != 26 or len({c["url"] for c in bond}) != 26: errs.append("Bond creatives must be 26 distinct records")
    if E["ads"]["bond"]["google"]["window_count"] != 26: errs.append("Bond window count")
    # screenshot references
    stored = {m["original_path"]: m for m in manifest}
    refs = set(re.findall(r'"(/tmp/[^"]+\.png)"', json.dumps(E)))
    for r in sorted(refs):
        m = stored.get(r)
        if not m: errs.append("screenshot reference not found in the source folder: " + r)
        elif not m["repo_path"]: notes.append("hash only (QA screenshot of a superseded preview build): " + Path(r).name)
    return E, errs, notes, len(refs)

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True); ap.add_argument("--edition", required=True); ap.add_argument("--batch", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    src = Path(a.source).resolve(); edir = HERE / "editions" / a.edition; dest = edir / "raw" / a.batch
    if not src.exists(): print("FAIL: source folder not found:", src); sys.exit(1)
    items, manifest = plan(src), []
    missing = [str(f) for f, _ in items if not f.exists()]
    if missing: print("FAIL: missing source files:", *missing, sep="\n  "); sys.exit(1)
    for f, rel in items:
        data = f.read_bytes(); stored = data; red = False
        if rel and rel.startswith("collector/") and TOKEN.search(data.decode("utf8", "replace")):
            stored = TOKEN.sub("_vercel_share=REDACTED", data.decode("utf8")).encode("utf8"); red = True
        manifest.append({"original_path": str(f), "repo_path": rel, "bytes": len(data), "sha256_original": hashlib.sha256(data).hexdigest(),
                         "sha256_stored": hashlib.sha256(stored).hexdigest() if rel else None, "redacted": red})
        if rel and not a.check:
            (dest / rel).parent.mkdir(parents=True, exist_ok=True); (dest / rel).write_bytes(stored)
    E, errs, notes, nref = validate(src, edir, manifest)
    report = {"batch": a.batch, "source": str(src), "ingested_by": "tools/ingest_browser.py", "files": len(manifest),
              "stored": sum(1 for m in manifest if m["repo_path"]), "hash_only": sum(1 for m in manifest if not m["repo_path"]),
              "redacted": [m["repo_path"] for m in manifest if m["redacted"]], "not_copied": NOT_COPIED,
              "screenshot_references": nref, "errors": errs, "notes": notes, "result": "PASS" if not errs else "FAIL"}
    prov = {"collector": E["collector"], "evidence_prepared_utc": E["prepared_utc"], "research_window": E["research_window"],
            "session": "Claude Code cloud session session_018Zqg63gvGy44sVUM5NEbiy (container scratchpad ede75233-c5c6-5154-983e-51b967a674c5)",
            "browser": "Headless Chromium launched by Playwright, logged out, through the container's outbound proxy. Not the founder's Chrome.",
            "repeat_loads": ["Meta Ad Library search for \"Studio B Dental\" loaded twice (the second added scrolling and a full-page screenshot); identical results.",
                             "Google Ads Transparency window searches loaded twice for all five domains: the first run's parser read the wrong line (google_window_try1.jsonl), the second run (google_window.jsonl) is the record. Neither run was refused."],
            "refusals": ["dundaseastdental.com: \"VPN or Proxy Detected\" panel, not bypassed", "dentalimplantsclinic.ca: Cloudflare security check, not passed",
                         "instagram.com/gajjardentistry: HTTP 429 and login redirect, not retried"]}
    if not a.check:
        (dest / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
        (dest / "validation_report.json").write_text(json.dumps(report, indent=1) + "\n")
        (dest / "provenance.json").write_text(json.dumps(prov, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: report[k] for k in ("result", "files", "stored", "hash_only", "redacted", "screenshot_references", "errors")}, indent=1))
    for n in notes: print("note:", n)
    sys.exit(0 if not errs else 1)

if __name__ == "__main__":
    main()
