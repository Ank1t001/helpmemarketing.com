#!/usr/bin/env python3
"""Compact Apify helper for the monthly GTA MedSpa routine.

Why it exists: model-driven polling put one full get-actor-run payload (about 1k tokens, mostly a repeated
field list) into context per poll, and every later call re-read it. This tool keeps the waiting, the status
file and the downloads out of the model's context. It prints one short line per state change.

Two ways to feed it a run:
  * Direct API (watch / start / fetch): needs APIFY_TOKEN in the environment. The token is sent only in an
    Authorization header and is never printed or written to a file. Optional APIFY_API_BASE (default
    https://api.apify.com). Sessions that only have the Apify MCP connector have no token: use `status`.
  * Offline (status): reads the raw run JSON a connector call saved to a file and prints the same compact line,
    so a poll costs a few hundred tokens instead of about a thousand.

Exit codes: 0 succeeded, 2 failed/aborted/timed out (actionable message), 3 still running, 4 usage or auth error.
"""
import argparse, hashlib, json, os, sys, time, urllib.error, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
TERMINAL_OK = {"SUCCEEDED"}
TERMINAL_BAD = {"FAILED", "ABORTED", "TIMED-OUT", "TIMING-OUT", "ABORTING"}


def base():
    return os.environ.get("APIFY_API_BASE", "https://api.apify.com").rstrip("/")


def call(method, path, body=None, raw=False):
    tok = os.environ.get("APIFY_TOKEN")
    if not tok:
        raise SystemExit("APIFY_TOKEN is not set: direct API mode is unavailable (use `status --raw FILE` with a saved connector reply)")
    req = urllib.request.Request(base() + path, method=method,
                                 data=None if body is None else json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
            return data if raw else json.loads(data)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Apify HTTP {e.code} on {method} {path.split('?')[0]}")  # token never echoed
    except urllib.error.URLError as e:
        raise SystemExit(f"Apify unreachable on {path.split('?')[0]}: {e.reason}")


def compact(run):
    run = run.get("data", run)
    ds = ((run.get("storages") or {}).get("datasets") or {}).get("default") or {}
    stats = run.get("stats") or {}
    return {
        "run_id": run.get("runId") or run.get("id"),
        "status": run.get("status"),
        "message": (run.get("statusMessage") or "")[:160],
        "dataset_id": ds.get("id") or run.get("defaultDatasetId"),
        "items": ds.get("itemCount"),
        "started_at": run.get("startedAt"),
        "finished_at": run.get("finishedAt"),
        "runtime_s": stats.get("runTimeSecs"),
        "compute_units": stats.get("computeUnits"),
        "usage_usd": run.get("usageTotalUsd"),
    }


def save_status(c, root):
    d = Path(root) / "work" / "status"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{c['run_id']}.json").write_text(json.dumps(c, indent=1))


def line(c):
    bits = [c["run_id"], c["status"]]
    if c.get("items") is not None:
        bits.append(f"{c['items']} items")
    if c.get("runtime_s") is not None:
        bits.append(f"{c['runtime_s']:.0f}s")
    if c.get("usage_usd") is not None:
        bits.append(f"${c['usage_usd']:.4f}")
    return " | ".join(str(b) for b in bits)


def verdict(c):
    s = c["status"]
    if s in TERMINAL_OK:
        return 0
    if s in TERMINAL_BAD:
        print(f"ACTION: run {c['run_id']} ended {s}: {c['message'] or 'no message'}; its dataset {c.get('dataset_id')} keeps any partial items")
        return 2
    return 3


def cmd_status(a):
    c = compact(json.load(open(a.raw)))
    save_status(c, a.root)
    print(line(c))
    v = verdict(c)
    if v == 3:
        print("NEXT: check again in 300s (do not poll faster than 120s)")
    return v


def cmd_watch(a):
    t0 = time.time()
    interval, last, same, prev_items = a.interval, None, 0, None
    while True:
        c = compact(call("GET", f"/v2/actor-runs/{a.run_id}"))
        c["run_id"] = c["run_id"] or a.run_id
        save_status(c, a.root)
        key = (c["status"], c["items"])
        if key != last:
            print(line(c), flush=True)
            last = key
        v = verdict(c)
        if v != 3:
            return v
        same = same + 1 if c["items"] == prev_items else 0
        prev_items = c["items"]
        if same >= a.stall_polls:
            print(f"NOTE: no new items for {same} polls; the run may be draining. Its dataset {c.get('dataset_id')} is readable now.", flush=True)
            same = 0
        if time.time() - t0 + interval > a.timeout:
            print(f"ACTION: still {c['status']} after {a.timeout}s; status file work/status/{c['run_id']}.json; rerun watch or read the dataset")
            return 2
        time.sleep(interval)
        interval = min(a.max_interval, interval * 1.5)


def cmd_start(a):
    inp = json.load(open(a.input))
    q = f"?maxTotalChargeUsd={a.max_charge}" if a.max_charge else ""
    run = call("POST", f"/v2/acts/{a.actor.replace('/', '~')}/runs{q}", inp)
    c = compact(run)
    c["actor"] = a.actor
    c["input_sha256"] = hashlib.sha256(Path(a.input).read_bytes()).hexdigest()[:16]
    save_status(c, a.root)
    print(line(c) + f" | input {a.input}")
    return 0


def cmd_fetch(a):
    """Download a dataset in pages to one file, resuming from saved page files; verify the count."""
    out = Path(a.out)
    pages = out.with_suffix(".pages")
    pages.mkdir(parents=True, exist_ok=True)
    total = int(a.total) if a.total else None
    off, n = 0, 0
    while total is None or off < total:
        pf = pages / f"{off:07d}.json"
        if pf.exists():
            items = json.loads(pf.read_text())
        else:
            q = f"?clean=false&format=json&limit={a.page}&offset={off}" + (f"&fields={a.fields}" if a.fields else "")
            items = json.loads(call("GET", f"/v2/datasets/{a.dataset}/items{q}", raw=True))
            pf.write_text(json.dumps(items))
        if not items:
            break
        n += len(items)
        off += a.page
        if len(items) < a.page:
            break
    allitems = []
    for pf in sorted(pages.glob("*.json")):
        allitems += json.loads(pf.read_text())
    out.write_text(json.dumps(allitems, ensure_ascii=False))
    ok = total is None or len(allitems) == total
    print(f"{'OK' if ok else 'INCOMPLETE'} {len(allitems)}/{total if total is not None else '?'} items -> {out}")
    return 0 if ok else 2


def cmd_build_input(a):
    """Write actor inputs from a saved handle list; nothing is printed except counts and paths."""
    handles = json.loads(Path(a.handles).read_text())
    handles = handles["selected"] if isinstance(handles, dict) else handles
    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    paths = []
    if a.kind == "profiles":
        p = outdir / "profiles.input.json"
        p.write_text(json.dumps({"usernames": handles}))
        paths.append(p)
    else:
        for i in range(0, len(handles), a.batch):
            p = outdir / f"posts-{i // a.batch + 1:02d}.input.json"
            p.write_text(json.dumps({
                "directUrls": [f"https://www.instagram.com/{h}/" for h in handles[i:i + a.batch]],
                "resultsType": "posts", "resultsLimit": a.limit, "onlyPostsNewerThan": a.since,
                "addParentData": False}))
            paths.append(p)
    print(f"{len(handles)} handles -> {len(paths)} input file(s) in {outdir}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(HERE))
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status"); s.add_argument("--raw", required=True); s.set_defaults(f=cmd_status)
    w = sub.add_parser("watch"); w.add_argument("--run-id", required=True)
    w.add_argument("--interval", type=float, default=60); w.add_argument("--max-interval", type=float, default=300)
    w.add_argument("--timeout", type=float, default=3600); w.add_argument("--stall-polls", type=int, default=3)
    w.set_defaults(f=cmd_watch)
    st = sub.add_parser("start"); st.add_argument("--actor", required=True); st.add_argument("--input", required=True)
    st.add_argument("--max-charge", type=float); st.set_defaults(f=cmd_start)
    f = sub.add_parser("fetch"); f.add_argument("--dataset", required=True); f.add_argument("--out", required=True)
    f.add_argument("--fields"); f.add_argument("--page", type=int, default=250); f.add_argument("--total")
    f.set_defaults(f=cmd_fetch)
    b = sub.add_parser("build-input"); b.add_argument("--kind", choices=["profiles", "posts"], required=True)
    b.add_argument("--handles", required=True); b.add_argument("--outdir", required=True)
    b.add_argument("--batch", type=int, default=50); b.add_argument("--limit", type=int, default=200)
    b.add_argument("--since"); b.set_defaults(f=cmd_build_input)
    a = ap.parse_args()
    sys.exit(a.f(a))


if __name__ == "__main__":
    main()
