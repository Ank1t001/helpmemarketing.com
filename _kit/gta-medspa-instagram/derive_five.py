#!/usr/bin/env python3
"""Five-account Med Spa Index, any edition from 003: raw collection -> observations -> derived metrics.

    python3 derive_five.py --edition NNN

Reads only files under editions/NNN/ (raw Apify replies saved verbatim, the account verification record, the
edition record and the run ledger), never figures from an earlier edition. Writes:
  editions/NNN/observations.json  one row per post returned for a cohort account (raw observed values, with
                                   hidden likes kept as null plus likes_hidden=true, never 0)
  editions/NNN/metrics.json       per-account derived metrics with their denominators and coverage
Every count is reconciled with asserts; the build stops on any disagreement. The cohort must equal
cohort_five.json: the same five accounts every edition, never replaced or added to.
For edition 003 this reproduces the committed files of derive_003.py byte for byte (tests.test_tools).

Window: the 15th of the previous month to the 14th of the collection month, America/Toronto (window_five.py).
"""
import argparse, datetime as dt, gzip, json, statistics as st
from collections import Counter
from pathlib import Path
from zoneinfo import ZoneInfo

ap = argparse.ArgumentParser()
ap.add_argument("--edition", required=True, help="three digits, 003 or later")
NNN = ap.parse_args().edition
assert len(NNN) == 3 and NNN.isdigit() and int(NNN) >= 3, "edition is three digits, 003 or later"
HERE = Path(__file__).parent
ED = HERE / "editions" / NNN
TZ = ZoneInfo("America/Toronto")
CFG = json.load(open(ED / "edition.json" if (ED / "edition.json").exists() else ED / f"edition_{NNN}.json"))
assert CFG["edition"] == NNN
COLLECTED = dt.date.fromisoformat(CFG["collected_on"])
from window_five import window
W_START, W_END = window(COLLECTED)                  # the 15th of the previous month to the 14th, both included
assert (W_START.isoformat(), W_END.isoformat()) == tuple(CFG["window"]), "the edition record's window must be the 15th of the previous month to the 14th (window_five.py)"
T0 = dt.datetime.combine(W_START, dt.time(0), TZ)
T1 = dt.datetime.combine(W_END + dt.timedelta(days=1), dt.time(0), TZ)
FMT = {"Video": "reel", "Sidecar": "carousel", "Image": "static"}


def local(ts):
    return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(TZ)


def med(v):
    return st.median(v) if v else None


accounts = json.load(open(ED / "accounts.json"))["accounts"]
handles = [a["handle"] for a in accounts]
assert len(handles) == 5 == len(set(handles)), "the cohort is exactly five accounts"
assert handles == [a["handle"] for a in json.load(open(HERE / "cohort_five.json"))["accounts"]], \
    "editions/NNN/accounts.json must list the five accounts of cohort_five.json, in its order: never replace or add accounts"
ledger = json.load(open(ED / "run_ledger.json"))
assert sum(float(r.get("cap_usd") or 0) for r in ledger["runs"]) <= 5.0 + 1e-9, "run caps exceed the 5 USD guard"
assert not any(r.get("hit_cap") for r in ledger["runs"]), "a run reached its cap"
prof = json.load(gzip.open(ED / "raw" / "source_profiles.json.gz", "rt"))
posts_run = next(r for r in ledger["runs"] if r["stage"] == "posts")
prof_by = {p["username"]: p for p in prof["items"]}
assert set(prof_by) == set(handles), "one profile record per cohort account"
raw = [json.loads(l) for l in gzip.open(ED / "raw" / "source_posts.jsonl.gz", "rt") if l.strip()]
assert len(raw) == posts_run["items"], f"saved post records ({len(raw)}) differ from the run ledger ({posts_run['items']})"

obs, unattributed = [], []
for r in raw:
    src = (r.get("inputUrl") or "").rstrip("/").split("/")[-1]
    if src not in handles or not r.get("timestamp"):
        unattributed.append({"inputUrl": r.get("inputUrl"), "error": r.get("error"), "owner": r.get("ownerUsername"), "shortCode": r.get("shortCode")})
        continue
    t = local(r["timestamp"])
    lk = r.get("likesCount")
    co = [c.get("username") for c in (r.get("coauthorProducers") or []) if c.get("username")]
    owner = r.get("ownerUsername")
    obs.append({
        "account": src, "shortcode": r["shortCode"], "url": f"https://www.instagram.com/p/{r['shortCode']}/",
        "published_utc": r["timestamp"], "published_local": t.isoformat(), "in_window": T0 <= t < T1,
        "format": FMT[r["type"]], "product_type": r.get("productType"),
        "likes": None if lk in (None, -1) else lk, "likes_hidden": lk == -1,
        "comments": r.get("commentsCount"), "comments_disabled": bool(r.get("isCommentsDisabled")),
        "plays": r.get("videoPlayCount") if r["type"] == "Video" else None,
        "pinned": bool(r.get("isPinned")), "paid_partnership": bool(r.get("paidPartnership")),
        "owner": owner, "own_post": owner == src, "coauthors": co,
        "caption": r.get("caption") or "",
    })
assert len(obs) + len(unattributed) == len(raw)
assert len({(o["account"], o["shortcode"]) for o in obs}) == len(obs), "duplicate post records"

metrics, cover = {}, {}
for h in handles:
    p = prof_by[h]
    rows = [o for o in obs if o["account"] == h]
    restricted = (p.get("error") == "Restricted profile") or not rows
    m = {"handle": h, "profile_error": p.get("error"), "followers": p.get("followersCount"),
         "followers_captured_at": prof["finished_at"], "accessible": not restricted}
    if restricted:
        m.update({"coverage": "inaccessible", "reason": "Instagram returned a restricted profile; no posts or follower count could be read"})
        metrics[h] = m
        continue
    unpinned = [o for o in rows if not o["pinned"]]
    oldest = min(unpinned, key=lambda o: o["published_local"])
    complete = local(oldest["published_utc"]) < T0
    win = [o for o in rows if o["in_window"]]
    # pinned posts published before the window are excluded by date; pinned posts published inside it stay in
    assert all(T0 <= local(o["published_utc"]) < T1 for o in win)
    own = [o for o in win if o["own_post"]]
    collab = [o for o in win if not o["own_post"]]
    fm = Counter(o["format"] for o in own)
    lk = [o["likes"] for o in own if o["likes"] is not None]
    cm = [o["comments"] for o in own if o["comments"] is not None and not o["comments_disabled"]]
    pl = [o["plays"] for o in own if o["format"] == "reel" and o["plays"] is not None]
    m.update({
        "coverage": "complete" if complete else "incomplete",
        "records_returned": len(rows), "oldest_unpinned_local": oldest["published_local"],
        "posts_in_window": len(win), "own_posts": len(own), "collab_posts": len(collab),
        "collab_owners": sorted({o["owner"] for o in collab}),
        "own_with_coauthors": sum(1 for o in own if o["coauthors"]),
        "paid_partnership_posts": sum(1 for o in win if o["paid_partnership"]),
        "reels": fm.get("reel", 0), "carousels": fm.get("carousel", 0), "statics": fm.get("static", 0),
        "likes_visible": len(lk), "likes_hidden": sum(1 for o in own if o["likes_hidden"]),
        "median_likes": med(lk), "comments_counted": len(cm), "median_comments": med(cm),
        "reels_with_plays": len(pl), "median_plays": med(pl),
        "pinned_in_window": sum(1 for o in win if o["pinned"]),
        "pinned_excluded": sum(1 for o in rows if o["pinned"] and not o["in_window"]),
    })
    assert m["reels"] + m["carousels"] + m["statics"] == m["own_posts"]
    assert m["own_posts"] + m["collab_posts"] == m["posts_in_window"]
    assert m["likes_visible"] + m["likes_hidden"] == m["own_posts"]
    # standout rule: most visible likes among own posts when likes are visible on every own post and there are
    # at least two; otherwise most recorded plays among own reels; a single post is shown as the only post.
    if len(own) == 1:
        s, rule = own[0], "only own post in the window"
    elif own and m["likes_hidden"] == 0:
        s, rule = max(own, key=lambda o: (o["likes"], o["comments"] or 0)), "most visible likes among own posts"
    elif pl:
        s, rule = max((o for o in own if o["format"] == "reel" and o["plays"] is not None), key=lambda o: o["plays"]), \
            "most recorded plays among own reels (likes hidden on some own posts)"
    else:
        s, rule = None, "no eligible post"
    if s:
        m["standout"] = {"shortcode": s["shortcode"], "url": s["url"], "rule": rule, "format": s["format"],
                         "published_local": s["published_local"], "likes": s["likes"], "comments": s["comments"],
                         "plays": s["plays"], "own_post": s["own_post"], "coauthors": s["coauthors"],
                         "likes_vs_median": (round(s["likes"] / m["median_likes"], 1) if s["likes"] is not None and m["median_likes"] else None),
                         "plays_vs_median": (round(s["plays"] / m["median_plays"], 1) if s["plays"] is not None and m["median_plays"] else None)}
    metrics[h] = m

# pooled figures (own posts only, so a collaboration post shared by two cohort accounts can never count twice)
acc_ok = [h for h in handles if metrics[h]["accessible"]]
own_all = [o for o in obs if o["in_window"] and o["own_post"] and o["account"] in acc_ok]
keys = [(o["owner"], o["shortcode"]) for o in own_all]
assert len(keys) == len(set(keys)), "a post is counted twice in pooled figures"
shared = Counter(o["shortcode"] for o in obs if o["in_window"])
pooled = {"accounts": len(acc_ok), "own_posts": len(own_all),
          "reels": sum(1 for o in own_all if o["format"] == "reel"),
          "carousels": sum(1 for o in own_all if o["format"] == "carousel"),
          "statics": sum(1 for o in own_all if o["format"] == "static"),
          "collab_posts": sum(metrics[h]["collab_posts"] for h in acc_ok),
          "shared_between_cohort_accounts": sum(1 for v in shared.values() if v > 1),
          "likes_hidden": sum(metrics[h]["likes_hidden"] for h in acc_ok),
          "paid_partnership_posts": sum(metrics[h]["paid_partnership_posts"] for h in acc_ok)}
out = {"edition": NNN, "collected_on": CFG["collected_on"], "window": [W_START.isoformat(), W_END.isoformat()],
       "timezone": "America/Toronto", "accounts": metrics, "pooled": pooled,
       "unattributed_records": unattributed}
json.dump({"edition": NNN, "window": out["window"], "posts": obs, "unattributed": unattributed},
          open(ED / "observations.json", "w"), indent=1, ensure_ascii=False)
json.dump(out, open(ED / "metrics.json", "w"), indent=1, ensure_ascii=False)
if __name__ == "__main__":
    for h in handles:
        m = metrics[h]
        print(h, m["coverage"], {k: m.get(k) for k in ("followers", "posts_in_window", "own_posts", "collab_posts", "reels", "carousels", "statics",
                                                         "likes_visible", "median_likes", "median_comments", "reels_with_plays", "median_plays")},
              (m.get("standout") or {}).get("shortcode"), (m.get("standout") or {}).get("rule"))
    print("pooled", pooled, "unattributed", len(unattributed))
