#!/usr/bin/env python3
"""GTA MedSpa Index scoring (from edition 002). Standard library only.

Inputs (all in work/, not committed):
  posts.jsonl   one JSON object per collected post: handle (the roster account whose feed it was
                collected from), owner (ownerUsername), shortcode, timestamp (ISO 8601), type
                (Image, Sidecar, Video), plays (videoPlayCount or null), likes (likesCount; -1 or
                null when hidden), comments, caption, coauthors (list of usernames), pinned (bool)
  profiles.json {handle: followers}
Plus roster.json (committed) and edition.json (window).

Output: editions/NNN/metrics.json. Run: python3 score.py --edition NNN
"""
import json, re, sys, argparse, statistics as st
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
FMT = {"Image": "Static", "Sidecar": "Carousel", "Video": "Reel"}


def percentile(value, pool):
    """Share of the pool below the value plus half of the ties, x 100 (same rule as the Real Estate kit)."""
    if len(pool) < 2:
        return 50.0
    return (sum(x < value for x in pool) + sum(x == value for x in pool) / 2) / len(pool) * 100


def q95(values):
    v = sorted(values)
    if len(v) < 2:
        return v[0] if v else 0
    return st.quantiles(v, n=100, method="inclusive")[94]


def pearson(xs, ys):
    if len(xs) < 3:
        return None
    mx, my = st.mean(xs), st.mean(ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = sum((x - mx) ** 2 for x in xs) ** 0.5
    sy = sum((y - my) ** 2 for y in ys) ** 0.5
    return round(sxy / (sx * sy), 2) if sx and sy else None


def load_rules():
    return json.load(open(HERE / "themes.json")), json.load(open(HERE / "compliance_patterns.json"))


def theme_of(caption, themes):
    c = (caption or "").lower()
    for t in themes["order"]:
        if any(re.search(p, c) for p in themes["patterns"][t]):
            return t
    return themes["fallback"]


def compliance_flags(caption, rules):
    c = (caption or "").lower()
    hit = {}
    drug = any(re.search(p, c) for p in rules["drug"])
    cond = any(re.search(p, c) for p in rules["condition"])
    hit["drug_with_condition"] = drug and cond
    ba = any(re.search(p, c) for p in rules["before_after"])
    hit["before_after"] = ba
    hit["before_after_no_disclaimer"] = ba and not any(re.search(p, c) for p in rules["disclaimer"])
    hit["superlative_or_guarantee"] = any(re.search(p, c) for p in rules["superlative"])
    hit["testimonial"] = any(re.search(p, c) for p in rules["testimonial"])
    return hit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edition", required=True)
    a = ap.parse_args()
    state = json.load(open(HERE / "edition.json"))
    roster = json.load(open(HERE / "roster.json"))
    w0, w1 = (date.fromisoformat(d) for d in state["window"])
    themes, rules = load_rules()
    review_path = HERE / "editions" / a.edition / "compliance_review.json"
    review = json.load(open(review_path)) if review_path.exists() else {"false_positives": {}}
    follows = json.load(open(HERE / "work" / "profiles.json"))
    posts = [json.loads(l) for l in open(HERE / "work" / "posts.jsonl") if l.strip()]

    clinics = {c["handle"].lower(): c for c in roster["clinics"] if c.get("include", True)}
    feed = {h: [] for h in clinics}
    seen = set()
    for p in posts:
        h = (p.get("handle") or "").lower()
        if h not in feed:
            continue
        d = datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")).date()
        if not (w0 <= d <= w1):
            continue  # also drops pinned posts from before the window
        key = (h, p["shortcode"])
        if key in seen:
            continue
        seen.add(key)
        p["date"] = d.isoformat()
        p["fmt"] = FMT.get(p.get("type"), "Static")
        lk = p.get("likes")
        p["likes"] = None if lk is None or lk < 0 else lk
        p["brand"] = (p.get("owner") or "").lower() == h
        feed[h].append(p)

    rows = []
    for h, ps in feed.items():
        reels = [p for p in ps if p["fmt"] == "Reel" and p.get("plays") is not None]
        r = {"handle": h, "name": clinics[h]["name"], "area": clinics[h]["area"], "region": clinics[h]["region"],
             "posts": len(ps), "reels": len(reels), "posted": len(ps) > 0, "qualified": len(reels) >= 3}
        if reels:
            plays = [p["plays"] for p in reels]
            r["median_plays"] = st.median(plays)
            r["c1k"] = sum(p.get("comments", 0) for p in reels) / max(1, sum(plays)) * 1000
        rows.append(r)

    q = [r for r in rows if r["qualified"]]
    cap = q95([r["c1k"] for r in q]) if q else 0
    for r in q:
        r["c1k_capped"] = min(r["c1k"], cap)
    mp = [r["median_plays"] for r in q]
    cc = [r["c1k_capped"] for r in q]
    for r in q:
        r["score"] = round(0.7 * percentile(r["median_plays"], mp) + 0.3 * percentile(r["c1k_capped"], cc), 1)
    q.sort(key=lambda r: (-r["score"], -r["median_plays"], r["name"].lower()))
    for i, r in enumerate(q, 1):
        r["rank"] = i
    n = len(q)
    med_posts = st.median([r["posts"] for r in q]) if q else 0
    med_plays = st.median(mp) if q else 0
    for r in q:
        hp, hr = r["posts"] > med_posts, r["median_plays"] > med_plays
        r["pattern"] = "Compounding" if hp and hr else "Efficient" if hr else "Grinding" if hp else "Quiet"
    by_plays = sorted(q, key=lambda r: -r["median_plays"])
    cut = {"Leading": round(n * 0.10), "Rising": round(n * 0.25), "Field": round(n * 0.75)}
    for i, r in enumerate(by_plays):
        r["tier"] = "Leading" if i < cut["Leading"] else "Rising" if i < cut["Rising"] else "Field" if i < cut["Field"] else "Quiet"

    def grp(key):
        out = {}
        for r in q:
            out.setdefault(r[key], []).append(r)
        return {k: {"clinics": len(v), "posts": sum(x["posts"] for x in v),
                    "median_plays": st.median([x["median_plays"] for x in v])} for k, v in out.items()}

    bands = [(0, 250, "Under 250"), (250, 500, "250 to 500"), (500, 1000, "500 to 1,000"), (1000, 2000, "1,000 to 2,000"),
             (2000, 4000, "2,000 to 4,000"), (4000, 10**12, "Over 4,000")]
    hist = [{"label": l, "clinics": sum(lo <= x < hi for x in mp)} for lo, hi, l in bands]

    # compliance across every ranked clinic's posts, minus hand-reviewed false positives
    fp = review.get("false_positives", {})
    comp = {k: 0 for k in ["drug_with_condition", "before_after", "before_after_no_disclaimer", "superlative_or_guarantee", "testimonial"]}
    any_hit = 0
    tier_posts = {"Leading": [0, 0, 0], "field": [0, 0, 0]}
    matched = []
    for r in q:
        flags_c = {k: False for k in comp}
        for p in feed[r["handle"]]:
            if not p["brand"]:
                continue
            f = compliance_flags(p.get("caption"), rules)
            f = {k: v and p["shortcode"] not in fp.get(k, []) for k, v in f.items()}
            for k, v in f.items():
                if v:
                    flags_c[k] = True
                    matched.append({"handle": r["handle"], "shortcode": p["shortcode"], "pattern": k, "caption": (p.get("caption") or "")[:300]})
            for t in (["Leading", "field"] if r["tier"] == "Leading" else ["field"]):
                tier_posts[t][0] += 1
                tier_posts[t][1] += f["drug_with_condition"]
                tier_posts[t][2] += f["before_after"]
        for k, v in flags_c.items():
            comp[k] += v
        any_hit += any(flags_c.values())
    compliance = {k: round(v / n * 100) for k, v in comp.items()} if n else {}
    compliance["any_share"] = round(any_hit / n * 100) if n else 0
    compliance["captions_checked"] = sum(1 for r in q for p in feed[r["handle"]] if p["brand"] and p.get("caption"))
    compliance["leading_vs_field"] = {t: {"posts": v[0], "drug_pct": round(v[1] / v[0] * 100, 1) if v[0] else 0,
                                          "before_after_pct": round(v[2] / v[0] * 100, 1) if v[0] else 0} for t, v in tier_posts.items()}

    top = q[:25]
    detail = []
    for r in top:
        ps = sorted(feed[r["handle"]], key=lambda p: p["timestamp"], reverse=True)
        own = [p for p in ps if p["brand"]]
        reels = [p for p in own if p["fmt"] == "Reel" and p.get("plays") is not None]
        peak = max(reels, key=lambda p: p["plays"]) if reels else None
        f = follows.get(r["handle"])
        mix = {k: sum(p["fmt"] == k for p in own) for k in ("Reel", "Carousel", "Static")}
        detail.append({**r, "followers": f, "peak": peak["plays"] if peak else None, "peak_shortcode": peak["shortcode"] if peak else None,
                       "peak_x": round(peak["plays"] / f, 1) if peak and f else None,
                       "c1k_own": round(sum(p.get("comments", 0) for p in reels) / max(1, sum(p["plays"] for p in reels)) * 1000, 1) if reels else None,
                       "mix": mix, "collab_posts": sum(1 for p in ps if not p["brand"]),
                       "postlog": [{"date": p["date"], "fmt": p["fmt"], "hook": hook(p.get("caption")), "theme": theme_of(p.get("caption"), themes),
                                    "likes": p["likes"], "comments": p.get("comments", 0), "plays": p.get("plays") if p["fmt"] == "Reel" else None,
                                    "shortcode": p["shortcode"]} for p in own]})
    log = [x for d in detail for x in d["postlog"]]
    reel_plays = [x["plays"] for x in log if x["plays"] is not None]
    field_reel_median = st.median(reel_plays) if reel_plays else None
    theme_stats = {}
    for x in log:
        t = theme_stats.setdefault(x["theme"], {"posts": 0, "plays": []})
        t["posts"] += 1
        if x["plays"] is not None:
            t["plays"].append(x["plays"])
    theme_stats = {k: {"posts": v["posts"], "reels": len(v["plays"]), "median_plays": st.median(v["plays"]) if v["plays"] else None,
                       "pull": round(st.median(v["plays"]) / field_reel_median, 2) if v["plays"] and field_reel_median else None}
                   for k, v in theme_stats.items()}
    fmt_stats = {}
    for k in ("Reel", "Carousel", "Static"):
        xs = [x for x in log if x["fmt"] == k]
        lk = [x["likes"] for x in xs if x["likes"] is not None]
        fmt_stats[k] = {"posts": len(xs), "share": round(len(xs) / max(1, len(log)) * 100), "median_likes": st.median(lk) if lk else None}

    out = {"edition": a.edition, "window": state["window"], "roster_total": len(clinics),
           "posted_anything": sum(r["posted"] for r in rows), "posted_nothing": sum(not r["posted"] for r in rows),
           "under_three_reels": sum(r["posted"] and not r["qualified"] for r in rows), "ranked": n,
           "posts_ranked": sum(r["posts"] for r in q), "median_of_medians": med_plays, "median_posts": med_posts,
           "c1k_cap": round(cap, 2), "correlation_posts_plays": pearson([r["posts"] for r in q], mp),
           "patterns": grp("pattern"), "tiers": grp("tier"), "regions": grp("region"), "histogram": hist,
           "compliance": compliance, "top25": detail, "themes": theme_stats, "formats": fmt_stats,
           "field_reel_median_top25": field_reel_median, "ranking": [{k: r[k] for k in ("rank", "handle", "name", "score", "median_plays", "posts")} for r in q]}
    d = HERE / "editions" / a.edition
    d.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(d / "metrics.json", "w"), indent=1, ensure_ascii=False, default=float)
    json.dump(matched, open(HERE / "work" / "compliance_matches.json", "w"), indent=1, ensure_ascii=False)
    print(f"ranked {n} of {len(clinics)}; top: {[r['name'] for r in q[:3]]}; matched captions for review: {len(matched)}")


def hook(caption):
    for line in (caption or "").splitlines():
        line = line.strip()
        if line:
            line = line.replace("—", ", ").replace("–", " to ")
            return line if len(line) <= 150 else line[:150].rstrip() + "..."
    return ""


if __name__ == "__main__":
    main()
