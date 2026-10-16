#!/usr/bin/env python3
"""Fetch public pages as evidence. Standard library only.

    python3 tools/fetch.py --edition 001 URL [URL ...]

Saves each response gzipped under editions/NNN/raw/pages/<sha12>.html.gz and appends one record per URL to
editions/NNN/raw/fetch_log.jsonl: requested URL, final URL, HTTP status, UTC fetch time, byte length, sha256.
Never submits a form, never sends cookies, never logs in.
"""
import argparse, gzip, hashlib, json, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36 HMM-research"

ap = argparse.ArgumentParser()
ap.add_argument("--edition", required=True)
ap.add_argument("urls", nargs="+")
a = ap.parse_args()
raw = HERE / "editions" / a.edition / "raw"
(raw / "pages").mkdir(parents=True, exist_ok=True)
for url in a.urls:
    rec = {"requested_url": url, "fetched_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"})
        with urllib.request.urlopen(req, timeout=40) as r:
            body = r.read(); rec.update(status=r.status, final_url=r.geturl())
    except urllib.error.HTTPError as e:
        body = e.read() or b""; rec.update(status=e.code, final_url=url, error=f"HTTP {e.code}")
    except Exception as e:
        body = b""; rec.update(status=None, final_url=url, error=type(e).__name__ + ": " + str(e)[:200])
    h = hashlib.sha256(body).hexdigest()
    rec.update(bytes=len(body), sha256=h)
    if body:
        p = raw / "pages" / f"{h[:12]}.html.gz"
        with gzip.open(p, "wb") as f: f.write(body)
        rec["saved"] = str(p.relative_to(HERE))
    with open(raw / "fetch_log.jsonl", "a") as f: f.write(json.dumps(rec) + "\n")
    print(rec.get("status"), rec.get("final_url"), rec["bytes"], rec.get("error", ""))
