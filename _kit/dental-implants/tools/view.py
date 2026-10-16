#!/usr/bin/env python3
"""Print a saved page's text without the lines it shares with its site's home page (navigation and footer)."""
import json, sys
from pathlib import Path
from urllib.parse import urlparse
R = Path(__file__).resolve().parent.parent / "editions" / sys.argv[1] / "raw"
log = [json.loads(l) for l in open(R / "fetch_log.jsonl") if '"status": 200' in l]
txt = lambda r: (R / "text" / f"{r['sha256'][:12]}.txt").read_text()
for url in sys.argv[2:]:
    r = next(x for x in reversed(log) if x["final_url"] == url)
    host = urlparse(url).netloc
    home = next((x for x in log if urlparse(x["final_url"]).netloc == host and urlparse(x["final_url"]).path in ("", "/")), None)
    common = set(txt(home).split("\n")) if home and home is not r else set()
    seen = set(); out = []
    for line in txt(r).split("\n"):
        if line in common or line in seen: continue
        seen.add(line); out.append(line)
    print(f"##### {url} fetched {r['fetched_utc']} sha {r['sha256'][:12]}"); print("\n".join(out))
