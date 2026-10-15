#!/usr/bin/env python3
"""Stage checkpoints for one edition: editions/NNN/checkpoint.json.

A stage is `done` only when its recorded files exist and still hash to the recorded value, so a resumed
run skips finished work (downloads, roster validation, collections) and never repeats a paid stage.

  checkpoint.py set --edition 002 --stage roster_validated --files a.json b.json --meta k=v ...
  checkpoint.py check --edition 002            # one line per stage: done / stale / pending, and the next stage
"""
import argparse, hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
STAGES = ["discovery_export", "roster_validated", "sample_selected", "profiles_collected", "profiles_verified",
          "posts_collected", "scored", "built", "preview_published", "data_saved"]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(root, ed):
    f = Path(root) / "editions" / ed / "checkpoint.json"
    return f, (json.loads(f.read_text()) if f.exists() else {"edition": ed, "stages": {}})


def rel(root, p):
    p = Path(p).resolve()
    return str(p.relative_to(Path(root).resolve()))


def state(root, ed):
    f, d = load(root, ed)
    out = {}
    for st in STAGES:
        rec = d["stages"].get(st)
        if not rec:
            out[st] = "pending"
            continue
        bad = [x for x, h in rec["files"].items() if not (Path(root) / x).exists() or sha(Path(root) / x) != h]
        out[st] = "stale" if bad else "done"
    nxt = next((s for s in STAGES if out[s] != "done"), None)
    return out, nxt, d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(HERE))
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("set"); s.add_argument("--edition", required=True); s.add_argument("--stage", required=True, choices=STAGES)
    s.add_argument("--files", nargs="*", default=[]); s.add_argument("--meta", nargs="*", default=[])
    c = sub.add_parser("check"); c.add_argument("--edition", required=True)
    a = ap.parse_args()
    if a.cmd == "set":
        f, d = load(a.root, a.edition)
        d["stages"][a.stage] = {"files": {rel(a.root, x): sha(x) for x in a.files},
                                "meta": dict(m.split("=", 1) for m in a.meta)}
        f.write_text(json.dumps(d, indent=1))
        print(f"{a.stage}: recorded {len(a.files)} file(s)")
        return 0
    out, nxt, d = state(a.root, a.edition)
    for st in STAGES:
        m = d["stages"].get(st, {}).get("meta", {})
        print(f"{st:20s} {out[st]:8s} {' '.join(f'{k}={v}' for k, v in m.items())}")
    print(f"NEXT: {nxt or 'all stages done'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
