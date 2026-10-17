#!/usr/bin/env python3
"""Remove third-party commenter data from an Instagram evidence batch, in place, and record it in the manifest.

    python3 tools/sanitise_comments.py --edition 001 --batch browser-20261016

No analysis in this kit reads comments, so commenters' usernames, comment text, comment timestamps and third-party audio
credits are removed from tracked evidence:
- logs/ig_posts.jsonl: the page's visible text (which held the comment thread) is dropped. Kept: post URL, shortcode,
  account, observation time, HTTP status, final URL, the clinic's own caption and public counts (og:title, og:description,
  description), og:type, and the post's own <time> (comment times dropped). The two flags the records use are derived from
  the original text before it is dropped: whether Instagram labelled the post "AI content" and whether an audio credit was
  shown (the credit's username is not kept).
- shots/ig/*.png: the right-hand panel below the account line (caption, comments, audio credit) is covered with a grey box.
  The clinic's caption stays available, word for word, in the sanitised log.
Each changed file keeps its original sha256 in the manifest, gains a new stored hash and a "sanitised" description, and
provenance.json and validation_report.json say which files are no longer byte-identical originals. Idempotent.
"""
import argparse, hashlib, json, re
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent.parent
KEEP = ("url", "shortcode", "handle", "checked_utc", "status", "final_url", "og_title", "og_desc", "description", "og_type")
# Right-hand panel of each 1280x1000 logged-out post screenshot, measured from the card borders (the panel's left edge moves
# with the media's aspect ratio). Rows 129 to 695 cover everything below the account line: caption, comments, audio credit.
PANELS = {"Dd3yAGBBrsW": (642, 978), "Dd6dymzkcvJ": (713, 1049), "Dd6yzieDLQG": (772, 1109), "Dd9BwhfFG0x": (642, 978), "DdbhpOgIMJE": (713, 1049),
          "DdrBZDBHDHg": (713, 1049), "DdrKB7AhD3b": (642, 978), "DdsKsuVM8b4": (698, 1034), "DdtiGIPlrNt": (642, 978)}
TOP, BOTTOM = 129, 695
NOTE = "Sanitised 2026-10-17: third-party comments, comment times and audio credits removed; see tools/sanitise_comments.py"

def sha(b): return hashlib.sha256(b).hexdigest()

def sanitise_log(p):
    out = []
    for l in p.read_text().splitlines():
        if not l.strip(): continue
        r = json.loads(l)
        if "text" in r:
            t = r["text"]
            r["page_flags"] = {"ai_content_label": "AI content" in t[:400], "audio_credit_shown": "Original audio" in t[:600],
                               "basis": "derived from the page text before sanitisation"}
        s = {k: r[k] for k in KEEP if k in r}
        s["times"] = r["times"][:1]
        s["page_flags"] = r["page_flags"]
        s["sanitised"] = NOTE
        out.append(json.dumps(s, ensure_ascii=False))
    p.write_text("\n".join(out) + "\n")

def redact(p):
    im = Image.open(p).convert("RGB")
    assert im.size == (1280, 1000), p
    L, R = PANELS[Path(p).stem]
    d = ImageDraw.Draw(im); d.rectangle((L + 1, TOP, R - 1, BOTTOM), fill=(200, 200, 200))
    d.text((L + 12, TOP + 12), "Redacted 2026-10-17: caption, comments and\naudio credit (caption kept in ig_posts.jsonl)", fill=(40, 40, 40))
    im.save(p, optimize=True)

def run(R):
    man = json.loads((R / "manifest.json").read_text()); byrel = {m["repo_path"]: m for m in man if m["repo_path"]}
    done = []
    targets = [("logs/ig_posts.jsonl", sanitise_log, "page text with comment thread removed; comment times dropped; page flags derived")] + \
              [(f"shots/ig/{f.name}", redact, "right-hand panel (caption, comments, audio credit) covered") for f in sorted((R / "shots/ig").glob("*.png"))]
    for rel, fn, what in targets:
        m = byrel[rel]
        if m.get("sanitised"): continue
        fn(R / rel)
        m["sha256_stored"] = sha((R / rel).read_bytes()); m["sanitised"] = what; done.append(rel)
    (R / "manifest.json").write_text(json.dumps(man, indent=1) + "\n")
    prov = json.loads((R / "provenance.json").read_text())
    prov["integrity"] = ("Files are byte-identical to the collected originals except those marked in manifest.json: 'redacted' (preview share token replaced) "
                         "and 'sanitised' (third-party commenter data removed). For those, sha256_original is the collected file and sha256_stored is the tracked file.")
    prov["sanitised_files"] = sorted(r for r, m in byrel.items() if m.get("sanitised"))
    prov["redacted_files"] = sorted(r for r, m in byrel.items() if m.get("redacted"))
    prov["sanitisation"] = NOTE
    (R / "provenance.json").write_text(json.dumps(prov, indent=1, ensure_ascii=False) + "\n")
    rep = json.loads((R / "validation_report.json").read_text())
    rep["post_ingest_changes"] = {"sanitised": prov["sanitised_files"], "note": "The validation above ran on the collected originals before sanitisation."}
    (R / "validation_report.json").write_text(json.dumps(rep, indent=1) + "\n")
    return done

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--edition", required=True); ap.add_argument("--batch", required=True)
    a = ap.parse_args()
    d = run(HERE / "editions" / a.edition / "raw" / a.batch)
    print(f"sanitised {len(d)} files" + ("" if d else " (already sanitised)"))
