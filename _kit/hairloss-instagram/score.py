#!/usr/bin/env python3
"""Hair Loss Index scoring (from edition 002). Standard library only.

Inputs (all in work/, not committed):
  posts.jsonl   one JSON object per collected post: handle (the roster handle whose feed it was collected
                from), owner (ownerUsername), shortcode, timestamp (ISO 8601), type (Image, Sidecar, Video),
                plays (videoPlayCount or null), likes (likesCount; -1 or null when hidden), comments, caption,
                coauthors (list of usernames), pinned (bool)
  profiles.json {handle: followers}
Plus, committed: roster.json, edition.json (window), themes.json, asks.json and, written in review,
  editions/NNN/conversion.json   {"reviewed": true, "brands": {name: {"ask": "booking"|"general"|"none",
                                  "ask_text", "route", "steps": 1|2|3|null, "steps_text"}}}
  editions/NNN/ads.json          {"checked_at": "YYYY-MM-DD", "brands": {name: active ad count}}
  editions/NNN/theme_overrides.json (optional) {shortcode: theme}

Run twice: the first run writes work/conversion_proposed.json and work/theme_review.json for review and stops
if conversion.json or ads.json is missing; the second run writes editions/NNN/metrics.json.
Run: python3 score.py --edition NNN
"""
import json, re, sys, argparse, statistics as st
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
FMT = {"Image": "Static", "Sidecar": "Carousel", "Video": "Reel"}
WEIGHTS = {"discovery": 0.30, "interest": 0.20, "consideration": 0.30, "conversion": 0.20}
ASK_POINTS = {"booking": 50, "general": 25, "none": 0}
STEP_POINTS = {1: 50, 2: 35, 3: 20}
MIN_POSTS = 5


def percentile(value, pool):
    """Share of the pool below the value plus half of the ties, x 100 (same rule as the other Index kits).
    Ranked brands are scored within the ranked pool; brands with fewer than five posts against it."""
    if not pool:
        return 50.0
    return (sum(x < value for x in pool) + sum(x == value for x in pool) / 2) / len(pool) * 100


def hook(caption):
    for line in (caption or "").splitlines():
        line = line.strip()
        if line:
            line = line.replace("—", ", ").replace("–", " to ")
            return line if len(line) <= 150 else line[:150].rstrip() + "..."
    return ""


def theme_of(caption, themes):
    c = (caption or "").lower()
    for t in themes["order"]:
        if any(re.search(p, c) for p in themes["patterns"][t]):
            return t
    return themes["fallback"]


def has(caption, pats):
    c = (caption or "").lower()
    return any(re.search(p, c) for p in pats)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edition", required=True)
    a = ap.parse_args()
    d = HERE / "editions" / a.edition
    d.mkdir(parents=True, exist_ok=True)
    state = json.load(open(HERE / "edition.json"))
    roster = json.load(open(HERE / "roster.json"))
    themes = json.load(open(HERE / "themes.json"))
    asks = json.load(open(HERE / "asks.json"))
    ovr_path = d / "theme_overrides.json"
    overrides = json.load(open(ovr_path)) if ovr_path.exists() else {}
    w0, w1 = (date.fromisoformat(x) for x in state["window"])
    follows = {k.lower(): v for k, v in json.load(open(HERE / "work" / "profiles.json")).items()}
    posts = [json.loads(l) for l in open(HERE / "work" / "posts.jsonl") if l.strip()]

    brands = roster["brands"]
    owner_of = {h.lower(): b["name"] for b in brands for h in b["handles"]}
    own, collab, seen = {b["name"]: [] for b in brands}, [], set()
    for p in posts:
        h = (p.get("handle") or "").lower()
        if h not in owner_of:
            continue
        dt = datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")).date()
        if not (w0 <= dt <= w1):
            continue  # also drops pinned posts from before the window
        if p["shortcode"] in seen:
            continue  # a post on two of one brand's handles counts once
        seen.add(p["shortcode"])
        p["date"] = dt.isoformat()
        p["fmt"] = FMT.get(p.get("type"), "Static")
        lk = p.get("likes")
        p["likes"] = None if lk is None or lk < 0 else lk
        p["comments"] = p.get("comments") or 0
        p["theme"] = overrides.get(p["shortcode"]) or theme_of(p.get("caption"), themes)
        name = owner_of[h]
        if owner_of.get((p.get("owner") or "").lower()) == name:
            own[name].append(p)
        else:
            collab.append({"brand": name, "owner": p.get("owner"), "shortcode": p["shortcode"], "date": p["date"], "fmt": p["fmt"],
                           "likes": p["likes"], "comments": p["comments"], "plays": p.get("plays") if p["fmt"] == "Reel" else None,
                           "hook": hook(p.get("caption"))})
    # brands whose likes all read exactly 3 are treated as hidden (a known scraper artefact)
    for name, ps in own.items():
        if len(ps) >= 3 and all(p["likes"] == 3 for p in ps):
            for p in ps:
                p["likes"] = None

    # review aids for the caption ask and themes
    proposed, theme_review = {}, []
    for b in brands:
        ps = own[b["name"]]
        bk = [p["shortcode"] for p in ps if has(p.get("caption"), asks["booking"])]
        gn = [p["shortcode"] for p in ps if has(p.get("caption"), asks["general"]) and p["shortcode"] not in bk]
        share = len(bk) / len(ps) if ps else 0
        proposed[b["name"]] = {"posts": len(ps), "booking_ask_posts": bk, "general_ask_posts": gn,
                               "proposed_ask": "booking" if share >= 0.25 else "general" if bk or gn else "none"}
        for p in ps:
            theme_review.append({"brand": b["name"], "shortcode": p["shortcode"], "theme": p["theme"], "caption": (p.get("caption") or "")[:240]})
    (HERE / "work").mkdir(exist_ok=True)
    json.dump(proposed, open(HERE / "work" / "conversion_proposed.json", "w"), indent=1, ensure_ascii=False)
    json.dump(theme_review, open(HERE / "work" / "theme_review.json", "w"), indent=1, ensure_ascii=False)
    conv_path, ads_path = d / "conversion.json", d / "ads.json"
    missing = [p.name for p in (conv_path, ads_path) if not p.exists()]
    if missing:
        sys.exit(f"review first: write editions/{a.edition}/{' and '.join(missing)} (see work/conversion_proposed.json), then run again")
    conv = json.load(open(conv_path))
    if not conv.get("reviewed"):
        sys.exit("conversion.json is not marked reviewed")
    ads = json.load(open(ads_path))

    rows = []
    for b in brands:
        ps = sorted(own[b["name"]], key=lambda p: p["timestamp"], reverse=True)
        fol = sum(follows.get(h.lower()) or 0 for h in b["handles"]) or None
        reels = [p for p in ps if p["fmt"] == "Reel" and p.get("plays") is not None]
        liked = [p["likes"] for p in ps if p["likes"] is not None]
        r = {"name": b["name"], "group": b["group"], "handles": b["handles"], "frame_slug": b["frame_slug"], "followers": fol,
             "posts": len(ps), "reels": sum(p["fmt"] == "Reel" for p in ps), "ads": ads.get("brands", {}).get(b["name"], 0)}
        c = conv["brands"].get(b["name"], {})
        r["conversion"] = {k: c.get(k) for k in ("ask", "ask_text", "route", "steps", "steps_text")}
        if ps:
            r["reel_share"] = round(r["reels"] / len(ps) * 100)
            r["avg_plays"] = st.mean(p["plays"] for p in reels) if reels else None
            r["total_plays"] = sum(p["plays"] for p in reels) if reels else None
            r["ppf"] = r["avg_plays"] / fol if reels and fol else None
            r["avg_likes"] = st.mean(liked) if liked else None
            r["median_likes"] = st.median(liked) if liked else None
            r["total_comments"] = sum(p["comments"] for p in ps)
            r["avg_comments"] = r["total_comments"] / len(ps)
            r["median_comments"] = st.median(p["comments"] for p in ps)
            r["zero_comment_posts"] = sum(p["comments"] == 0 for p in ps)
            r["er"] = (r["avg_likes"] + r["avg_comments"]) / fol * 100 if fol and r["avg_likes"] is not None else None
            r["c2l"] = r["total_comments"] / sum(liked) * 100 if liked and sum(liked) else None
            top = max((p for p in ps if p["likes"] is not None), key=lambda p: (p["likes"], p["timestamp"]), default=None)
            r["top"] = {"shortcode": top["shortcode"], "likes": top["likes"], "fmt": top["fmt"], "plays": top.get("plays") if top["fmt"] == "Reel" else None,
                        "x_median": round(top["likes"] / r["median_likes"], 1) if r["median_likes"] else None, "hook": hook(top.get("caption"))} if top else None
            peak = max(reels, key=lambda p: p["plays"]) if reels else None
            r["peak"] = {"shortcode": peak["shortcode"], "plays": peak["plays"], "x_followers": round(peak["plays"] / fol, 2) if fol else None} if peak else None
            r["postlog"] = [{"date": p["date"], "fmt": p["fmt"], "hook": hook(p.get("caption")), "theme": p["theme"], "likes": p["likes"],
                             "comments": p["comments"], "plays": p.get("plays") if p["fmt"] == "Reel" else None, "shortcode": p["shortcode"]} for p in ps]
        else:
            r["postlog"] = []
        r["ranked"] = len(ps) >= MIN_POSTS
        ppf = r.get("ppf")
        r["flag"] = ("No posts" if not ps else "Fewer than 5 posts" if not r["ranked"] else "no video" if ppf is None
                     else "Above 1x" if ppf > 1 else "0.25 to 1x" if ppf >= 0.25 else "Below 0.25x")
        rows.append(r)

    ranked = [r for r in rows if r["ranked"]]
    pools = {"discovery": [r.get("ppf") or 0 for r in ranked], "interest": [r.get("er") or 0 for r in ranked],
             "consideration": [r["avg_comments"] for r in ranked]}
    for r in rows:
        if not r["posts"]:
            r["score"], r["pillars"] = None, None
            continue
        cv = r["conversion"]
        pil = {"discovery": percentile(r.get("ppf") or 0, pools["discovery"]), "interest": percentile(r.get("er") or 0, pools["interest"]),
               "consideration": percentile(r["avg_comments"], pools["consideration"]),
               "conversion": ASK_POINTS.get(cv.get("ask") or "none", 0) + STEP_POINTS.get(cv.get("steps"), 0)}
        r["pillars"] = {k: round(v, 1) for k, v in pil.items()}
        r["score"] = round(sum(WEIGHTS[k] * v for k, v in pil.items()))
    ranked.sort(key=lambda r: (-r["score"], -r["avg_comments"], r["name"].lower()))
    for i, r in enumerate(ranked, 1):
        r["rank"] = i
    rest = sorted([r for r in rows if not r["ranked"]], key=lambda r: (r["score"] is None, -(r["score"] or 0), r["name"].lower()))
    board = ranked + rest

    log = [p for r in board for p in r["postlog"]]
    tstats = {}
    for p in log:
        t = tstats.setdefault(p["theme"], {"posts": 0, "likes": [], "brands": {}})
        t["posts"] += 1
        if p["likes"] is not None:
            t["likes"].append(p["likes"])
    for r in board:
        for p in r["postlog"]:
            b = tstats[p["theme"]]["brands"]
            b[r["name"]] = b.get(r["name"], 0) + 1
    themes_out = {k: {"posts": v["posts"], "median_likes": st.median(v["likes"]) if v["likes"] else None,
                      "share": round(v["posts"] / len(log) * 100) if log else 0,
                      "top_brand": max(v["brands"].items(), key=lambda x: x[1]) if v["brands"] else None, "brands": len(v["brands"])}
                  for k, v in sorted(tstats.items(), key=lambda x: -(st.median(x[1]["likes"]) if x[1]["likes"] else -1))}
    fmts = {}
    for k in ("Reel", "Carousel", "Static"):
        xs = [p for p in log if p["fmt"] == k]
        lk = [p["likes"] for p in xs if p["likes"] is not None]
        fmts[k] = {"posts": len(xs), "median_likes": st.median(lk) if lk else None}
    stage1 = sorted([r for r in board if r.get("ppf") is not None], key=lambda r: -r["ppf"])
    stage2 = sorted([r for r in board if r["posts"]], key=lambda r: -r["avg_comments"])

    out = {"edition": a.edition, "window": state["window"], "scraped_at": state["scraped_at"], "weights": WEIGHTS,
           "brands_total": len(brands), "handles_total": sum(len(b["handles"]) for b in brands), "ranked": len(ranked),
           "posts_analysed": len(log), "comments_recorded": sum(p["comments"] for p in log),
           "brands_with_ads": sum(1 for r in board if r["ads"]), "ads_checked_at": ads.get("checked_at"),
           "collab_posts": collab, "board": board, "themes": themes_out, "formats": fmts,
           "stage1": [{"name": r["name"], "ppf": r["ppf"]} for r in stage1],
           "stage2": [{"name": r["name"], "avg_comments": r["avg_comments"]} for r in stage2]}
    json.dump(out, open(d / "metrics.json", "w"), indent=1, ensure_ascii=False, default=float)
    print(f"{len(log)} posts; ranked {len(ranked)} of {len(brands)}; board: {[(r['name'], r['score']) for r in board]}")


if __name__ == "__main__":
    main()
