#!/usr/bin/env python3
"""Prior-edition check for the monthly Med Spa Index routine. Standard library only.

    python3 check_live.py

Finds the latest published five-account edition and proves that the kit still reproduces the live medspa-index.html
byte for byte: edition 003 through build_003.py (run by the kit test in a temporary copy), editions 004 onward through
build_five.py --check-live. It also checks that every earlier snapshot exists. PASS or FAIL; nothing is written.
"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parent.parent
pub = []
for d in sorted((HERE / "editions").iterdir()):
    if d.is_dir() and d.name.isdigit() and int(d.name) >= 3:
        for f in (d / "edition.json", d / f"edition_{d.name}.json"):
            if f.exists():
                c = json.load(open(f))
                if c.get("status") == "published":
                    pub.append(d.name)
                break
if not pub:
    sys.exit("FAIL: no published five-account edition found")
latest = pub[-1]
missing = [e for e in pub if not (REPO / "medspa-index" / f"edition-{e}.html").exists()]
if missing:
    sys.exit(f"FAIL: snapshot missing for edition(s) {', '.join(missing)}")
if latest == "003":
    cmd = [sys.executable, "-m", "unittest", "-q", "tests.test_tools.Edition003.test_derive_and_draft_reproduce_committed_files"]
else:
    cmd = [sys.executable, "build_five.py", "--edition", latest, "--check-live"]
r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True)
if r.returncode:
    sys.exit(f"FAIL: edition {latest} does not reproduce the live page; someone changed medspa-index.html without updating the kit\n{r.stdout[-1500:]}{r.stderr[-1500:]}")
print(f"PASS: edition {latest} reproduces medspa-index.html; snapshots present for {', '.join(pub)}")
