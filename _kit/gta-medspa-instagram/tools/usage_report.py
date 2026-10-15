#!/usr/bin/env python3
"""Reconcile Claude token usage by stage from a Claude Code session transcript (.jsonl).

Measured: per-API-call usage (deduplicated by message id) and tool-result sizes. Stages come from a
JSON file {"stages": [{"label": ..., "from": "ISO timestamp"}]}; a call belongs to the last stage that
starts at or before it. Prints a compact table; --out writes full JSON. Nothing is estimated here.
"""
import argparse, collections, json, sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("transcript"); ap.add_argument("--stages", required=True); ap.add_argument("--out")
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.transcript) if l.strip()]
    stages = sorted(json.load(open(a.stages))["stages"], key=lambda s: s["from"])
    calls = {}
    for r in rows:
        if r.get("type") != "assistant" or not (r.get("message") or {}).get("usage"):
            continue
        m = r["message"]
        calls[m.get("id") or r.get("uuid")] = (r["timestamp"], m["usage"])  # last row of a message has final usage
    tot = collections.Counter()
    per = collections.OrderedDict((s["label"], collections.Counter()) for s in stages)
    for ts, u in calls.values():
        lab = None
        for s in stages:
            if ts >= s["from"]:
                lab = s["label"]
        lab = lab or stages[0]["label"]
        for k, v in (("calls", 1), ("cache_read", u.get("cache_read_input_tokens", 0)),
                     ("cache_created", u.get("cache_creation_input_tokens", 0)), ("output", u.get("output_tokens", 0)),
                     ("input", u.get("input_tokens", 0)),
                     ("thinking", (u.get("output_tokens_details") or {}).get("thinking_tokens", 0))):
            per[lab][k] += v
            tot[k] += v
    chk = {k: sum(c[k] for c in per.values()) for k in tot}
    assert chk == dict(tot), "stage sums must equal totals"
    print(f"{'stage':58s} {'calls':>5s} {'cache_read':>11s} {'cache_new':>10s} {'output':>7s}")
    for lab, c in per.items():
        print(f"{lab[:58]:58s} {c['calls']:5d} {c['cache_read']:11d} {c['cache_created']:10d} {c['output']:7d}")
    print(f"{'TOTAL':58s} {tot['calls']:5d} {tot['cache_read']:11d} {tot['cache_created']:10d} {tot['output']:7d}  (input {tot['input']}, thinking {tot['thinking']})")
    if a.out:
        json.dump({"totals": dict(tot), "stages": {k: dict(v) for k, v in per.items()}}, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    sys.exit(main())
