#!/usr/bin/env python3
"""Check that each selected account is the clinic's own account, from collected profiles and the discovery listings.

Evidence (any one confirms): the profile's external link has the clinic's website domain; the profile name or
username matches the clinic's listing name; the biography names one of the clinic's municipalities.
Failed: profile not found, private. Unconfirmed: none of the evidence. Writes editions/NNN/profiles_verified.json
and prints counts only.
"""
import argparse, gzip, json, re, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import roster_build as rb  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edition", required=True); ap.add_argument("--root", default=str(HERE))
    a = ap.parse_args()
    root = Path(a.root); ed = root / "editions" / a.edition
    roster = {c["handle"]: c for c in json.load(open(ed / "roster_eligible.json"))["clinics"]}
    listings = {r["placeId"]: r for r in json.load(gzip.open(ed / "discovery_listings.json.gz", "rt"))}
    profiles = {(p.get("username") or "").lower(): p for p in json.load(gzip.open(ed / "source_profiles.json.gz", "rt"))}
    sel = [h for h, c in roster.items() if c["selected"]]
    res = {}
    for h in sel:
        c, p = roster[h], profiles.get(h)
        if not p or p.get("error") == "not_found":
            res[h] = {"status": "failed", "reason": "profile not found"}; continue
        if p.get("private"):
            res[h] = {"status": "failed", "reason": "private account"}; continue
        ev = []
        ext = rb.domain(p.get("externalUrl"))
        if ext and ext == c.get("website_domain") and ext not in rb.PLATFORM_DOMAINS:
            ev.append("website link")
        places = [listings[i] for i in c["place_ids"] if i in listings]
        fake = {"title": p.get("fullName") or ""}
        if any(rb.name_match(h, pl) for pl in places) and rb.name_match(h, {"title": c["name"], "website": None}):
            ev.append("username matches clinic name")
        for pl in places:
            if p.get("fullName") and rb.name_match(re.sub(r"[^a-z0-9]", "", p["fullName"].lower()), pl):
                ev.append("profile name matches listing"); break
        bio = (p.get("biography") or "").lower()
        if any(m.lower() in bio for m in c["municipalities"]):
            ev.append("biography names clinic city")
        if ext and any(ext == rb.domain(pl.get("website")) for pl in places) and "website link" not in ev and ext not in rb.PLATFORM_DOMAINS:
            ev.append("website link")
        res[h] = {"status": "verified" if ev else "unconfirmed", "evidence": sorted(set(ev)),
                  "followers": p.get("followersCount"), "posts_count": p.get("postsCount"),
                  "category": p.get("businessCategoryName"), "restricted": p.get("error") == "Restricted profile"}
    # failed accounts are replaced by the next reserve in the same stratum (sample_rank_in_stratum order);
    # replacements still need their own profile check before collection
    need = Counter(roster[h]["region"] for h, v in res.items() if v["status"] == "failed")
    repl = []
    for reg, k in sorted(need.items()):
        pool = sorted((c for c in roster.values() if c["region"] == reg and not c["selected"]),
                      key=lambda c: c["sample_rank_in_stratum"])
        repl += [{"region": reg, "handle": c["handle"], "rank_in_stratum": c["sample_rank_in_stratum"]} for c in pool[:k]]
    out = {"edition": a.edition, "replacements_pending_profile_check": repl, "checked": len(sel), "counts": dict(Counter(v["status"] for v in res.values())), "accounts": res}
    json.dump(out, open(ed / "profiles_verified.json", "w"), indent=1)
    print(f"checked {len(sel)} | {out['counts']} | no posts yet {sum(1 for v in res.values() if v.get('posts_count') == 0)} | "
          f"restricted {sum(1 for v in res.values() if v.get('restricted'))} | replacements pending {len(repl)} -> {ed / 'profiles_verified.json'}")


if __name__ == "__main__":
    main()
