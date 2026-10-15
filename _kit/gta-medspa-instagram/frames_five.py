#!/usr/bin/env python3
"""Self-hosted cover frames for the standout posts of a five-account edition (003 onward).

    python3 frames_five.py --edition NNN --fetch DIR    # download each standout's cover (displayUrl in the saved post record) into DIR, then build
    python3 frames_five.py --edition NNN --from DIR     # build from covers already in DIR (named <shortcode>.jpg)

Crop offsets live in editions/NNN/coding.json "frame_crop" {shortcode: share of the extra height cut from the top}; set one
per standout after looking at the cover (0.5 centres it; lower keeps more of the top, where overlay text usually sits).

For each current standout post (metrics.json) it takes the cover image Instagram returned in the same saved record
(raw/source_posts.jsonl.gz, field displayUrl), crops it to 4:5 (the vertical offset per post keeps the overlay text in
frame, see CROP), resizes to 640x800 with LANCZOS and writes WebP quality 80, method 6, to
/assets/index/medspa/frames/<handle>-cycleNNN.webp. editions/NNN/frames.json records the source shortcode, the CDN
host, the download time, the original size, the crop box and the hash of both files, so each frame can be traced to the
post it shows. Instagram CDN links expire, so the originals are not kept in the repo; a committed frame is never
re-downloaded. The alt text for each frame lives in coding.json "standout_frames" and is written from the reviewed
cover, not from the caption.
"""
import argparse, datetime as dt, gzip, hashlib, json, subprocess, sys
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image

HERE = Path(__file__).parent
ED = None
REPO = HERE.parent.parent
OUT = REPO / "assets" / "index" / "medspa" / "frames"

ap = argparse.ArgumentParser()
ap.add_argument("--edition", required=True)
g = ap.add_mutually_exclusive_group(required=True)
g.add_argument("--fetch", metavar="DIR")
g.add_argument("--from", dest="src", metavar="DIR")
a = ap.parse_args()
NNN = a.edition
assert len(NNN) == 3 and NNN.isdigit() and int(NNN) >= 3
ED = HERE / "editions" / NNN
CROP = json.load(open(ED / "coding.json")).get("frame_crop", {})
src = Path(a.fetch or a.src)
src.mkdir(parents=True, exist_ok=True)

M = json.load(open(ED / "metrics.json"))
stand = {m["standout"]["shortcode"]: h for h, m in M["accounts"].items() if m.get("standout")}
rec = {}
for line in gzip.open(ED / "raw" / "source_posts.jsonl.gz", "rt"):
    r = json.loads(line)
    if r.get("shortCode") in stand:
        rec[r["shortCode"]] = r
assert set(rec) == set(stand), f"saved records missing for {set(stand) - set(rec)}"
missing = sorted(set(stand) - set(CROP))
if missing:  # first pass: save the covers so they can be looked at, then stop until frame_crop is set
    for sc in missing:
        jpg = src / f"{sc}.jpg"
        if a.fetch and not jpg.exists():
            res = subprocess.run(["curl", "-sS", "-L", "--fail", "-o", str(jpg), rec[sc]["displayUrl"]], capture_output=True, text=True)
            if res.returncode:
                sys.exit(f"{sc}: cover download failed ({res.stderr.strip()[:120]}); the CDN link may have expired, re-collect the post record")
    sys.exit(f"covers saved in {src} as <shortcode>.jpg for {missing}: look at each, write coding.json standout_visuals, standout_frames, "
             f"standout_titles and frame_crop, then run again with --from {src}")
assert set(CROP) == set(stand), "coding.json frame_crop must hold an offset for exactly the current standout posts"

old = json.load(open(ED / "frames.json"))["frames"] if (ED / "frames.json").exists() else {}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
OUT.mkdir(parents=True, exist_ok=True)
frames = {}
for sc, h in stand.items():
    dst = OUT / f"{h}-cycle{NNN}.webp"
    if dst.exists() and sc in old and old[sc]["frame_sha256"] == sha(dst):
        frames[sc] = old[sc]
        continue
    jpg = src / f"{sc}.jpg"
    fetched = None
    if a.fetch and not jpg.exists():
        res = subprocess.run(["curl", "-sS", "-L", "--fail", "-o", str(jpg), rec[sc]["displayUrl"]], capture_output=True, text=True)
        if res.returncode:
            sys.exit(f"{sc}: cover download failed ({res.stderr.strip()[:120]}); the CDN link may have expired, re-collect the post record")
        fetched = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    assert jpg.exists(), f"{jpg} missing"
    fetched = fetched or dt.datetime.fromtimestamp(jpg.stat().st_mtime, dt.timezone.utc).isoformat(timespec="seconds")  # --from: the file time of the download
    im = Image.open(jpg).convert("RGB")
    w, hgt = im.size
    cw, ch = (w, round(w * 5 / 4)) if hgt * 4 >= w * 5 else (round(hgt * 4 / 5), hgt)
    x0 = (w - cw) // 2
    y0 = round((hgt - ch) * CROP[sc])
    im.crop((x0, y0, x0 + cw, y0 + ch)).resize((640, 800), Image.LANCZOS).save(dst, "WEBP", quality=80, method=6)
    frames[sc] = {"account": h, "post_url": rec[sc]["url"], "source_field": "displayUrl", "cdn_host": urlparse(rec[sc]["displayUrl"]).netloc,
                  "downloaded_utc": fetched or (old.get(sc) or {}).get("downloaded_utc"), "original_px": [w, hgt],
                  "crop_box": [x0, y0, x0 + cw, y0 + ch], "upscaled": cw < 640, "source_sha256": sha(jpg),
                  "frame": f"/assets/index/medspa/frames/{dst.name}", "frame_sha256": sha(dst)}
json.dump({"edition": NNN, "note": "Cover frames of the standout posts, from the displayUrl in the saved post record; originals not kept (CDN links expire).",
           "frames": frames}, open(ED / "frames.json", "w"), indent=1)
for sc, f in frames.items():
    print(sc, f["account"], f["original_px"], "crop", f["crop_box"], "upscaled" if f["upscaled"] else "", f["frame"])
