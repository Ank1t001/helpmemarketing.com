#!/usr/bin/env python3
"""Builds the 50-account GTA medspa Instagram benchmark (draft, or live page plus snapshot) from saved records only.

The edition number, observation window and input files come from edition.json, never from constants in this file.
Stale-value guards (see validate below) stop a build whose edition, window, cohort, counts, run ledger or inputs
do not agree. Reads the cohort (cohort_50.json), the edition's accounts state and post records, and
reconciles the counts (fails if they differ from the saved evidence), computes observed-data descriptive figures with
metric-specific denominators, and writes editions/002/draft/medspa-index-draft.html using the live page shell
(head, nav, footer chrome) with a new body. No ranking, score or leaderboard: coverage comparability is not established.
"""
import argparse, gzip, html, json, re, statistics as st
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parent.parent
import datetime as dt
from zoneinfo import ZoneInfo

CFG = json.load(open(HERE / "edition.json"))
ENO = CFG["edition"]
ED = HERE / "editions" / ENO
W0, W1 = CFG["window"]
CAP_USD = float(CFG.get("run_cap_guard", {}).get("aggregate_cap_usd", 5.0))
_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def long_date(iso, year=True):
    d = dt.date.fromisoformat(iso[:10])
    return f"{d.day} {_MONTHS[d.month - 1]}" + (f" {d.year}" if year else "")


PAGE_PATH = "/medspa-index"  # primary URL since 2026-10-15; /gta-medspa-index 301-redirects here
SNAP_PATH = f"/gta-medspa-index/edition-{ENO}" if ENO == "002" else f"{PAGE_PATH}/edition-{ENO}"  # edition 001 and 002 snapshots keep their original URLs
CDATE = long_date(CFG["scraped_at"])
WSTART, WEND = long_date(W0, False), long_date(W1)
WTXT = f"{WSTART} to {WEND}"
WSTART_LONG = long_date(W0)
MONTH_YEAR = f"{_MONTHS[int(W1[5:7]) - 1]} {W1[:4]}"
REG = ["Toronto", "Peel", "York", "Durham", "Halton", "Multi-region"]
E = html.escape


def n(x):
    return f"{x:,}"


def med(v):
    return st.median(v) if v else None


def fmt_num(x):
    x = float(x)
    return f"{x:,.0f}" if abs(x - round(x)) < 1e-9 else f"{x:,.1f}"


# ---- load and reconcile --------------------------------------------------------------------------
INP = CFG["inputs"]
for _k, _p in INP.items():  # every input must belong to this edition's folder: no reuse of another edition's data
    assert _p.startswith(f"editions/{ENO}/"), f"input {_k} ({_p}) is not under editions/{ENO}/"
scope = json.load(open(HERE / INP["accounts_state"]))
assert scope.get("edition") == ENO, f"accounts state is for edition {scope.get('edition')}, edition.json says {ENO}"
cohort50 = json.load(open(HERE / "cohort_50.json"))
roster = {c["handle"]: c for c in cohort50["accounts"]}
acc = {a["handle"]: a for a in scope["accounts"]}
rows = [json.loads(l) for l in gzip.open(HERE / INP["posts"], "rt") if l.strip()]
ledger = json.load(open(HERE / INP["run_ledger"]))
assert set(acc) == set(roster) and len(roster) == 50, "accounts state must be exactly the fixed 50-account cohort"
# window and date guards
_d0, _d1 = dt.date.fromisoformat(W0), dt.date.fromisoformat(W1)
assert W1 == CFG["scraped_at"], "window must end on the collection date"
assert (_d1 - _d0).days == CFG.get("window_days", 90), "window must be window_days long"
assert all(r["timestamp"][:10] <= W1 for r in rows), "a post is dated after the window end: stale or wrong input"
assert any(W0 <= r["timestamp"][:10] <= W1 for r in rows), "no post inside the window: stale input"
# aggregate run-cap guard ($5 across the post runs of one edition)
_caps = sum(float(r["cap_usd"]) for r in ledger["runs"])
assert _caps <= CAP_USD + 1e-9, f"sum of launched run caps {_caps} exceeds the {CAP_USD} guard"
assert not any(r.get("hit_cap") for r in ledger["runs"]), "a run reached its cap: its accounts must be classed E before a build"
assert all(set(r["accounts"]) <= set(roster) for r in ledger["runs"]), "a run covers accounts outside the cohort"
if ENO != "002":  # edition 002 text compares nothing; later editions need founder-approved sections
    for _f in ("comparison_section.html", "history_rows.html"):
        assert (ED / _f).exists(), f"edition {ENO} needs {ED / _f} (founder-approved comparison and history text)"

assert len(acc) == 50, "50 selected accounts"
cls = Counter(a["cls"] for a in acc.values())
assert sum(cls.values()) == 50 and set(cls) <= set("ABCDE"), cls
assert all((r["handle"] or "").lower() in acc for r in rows), "every row belongs to a selected account"
inw = [r for r in rows if W0 <= r["timestamp"][:10] <= W1]
outw = [r for r in rows if not (W0 <= r["timestamp"][:10] <= W1)]
assert len(inw) + len(outw) == len(rows)
assert all(r.get("pinned") for r in outw), "rows outside the window are older pinned posts"
per = Counter(r["handle"].lower() for r in inw)
assert {h for h, a in acc.items() if a["cls"] == "B"} == set(per), "class B equals accounts with in-window rows"
assert all(per.get(h, 0) == 0 for h, a in acc.items() if a["cls"] != "B")
assert len({(r["handle"], r["shortcode"]) for r in inw}) == len(inw), "no duplicate posts"
assert max(per.values()) < 200

brand = [r for r in inw if (r.get("owner") or "").lower() == r["handle"].lower()]
other = len(inw) - len(brand)
FMT = {"Image": "Static", "Sidecar": "Carousel", "Video": "Reel"}
fm = Counter(FMT[r["type"]] for r in brand)
reels_by = defaultdict(list)
for r in brand:
    if r["type"] == "Video" and r.get("plays") is not None:
        reels_by[r["handle"].lower()].append(r)
counts = sorted(per.values())
q = st.quantiles(counts, n=4, method="inclusive")
eligible3 = {h: v for h, v in reels_by.items() if len(v) >= 3}
acct_med_plays = [med([r["plays"] for r in v]) for v in eligible3.values()]
all3 = [r for v in eligible3.values() for r in v]
likes_vis = sum(1 for r in brand if r.get("likes") not in (None, -1))
withreel = sum(1 for h in per if reels_by.get(h))
reg_cls = defaultdict(Counter)
for h, a in acc.items():
    reg_cls[a["region"]][a["cls"]] += 1
assert sum(sum(c.values()) for c in reg_cls.values()) == 50
orig = Counter(a["origin"] for a in acc.values())
types = Counter(a["account_type"] for a in acc.values())

collab = [r for r in inw if (r.get("owner") or "").lower() != r["handle"].lower()]
assert all(r["handle"].lower() in [x.lower() for x in (r.get("coauthors") or [])] for r in collab), "every other-owner record lists the account as a co-author"
collab_video = sum(1 for r in collab if r["type"] == "Video")
collab_accounts, collab_owners = len({r["handle"].lower() for r in collab}), len({(r["owner"] or "").lower() for r in collab})
own_reels = [r for r in brand if r["type"] == "Video"]
missing_plays = sum(1 for r in own_reels if r.get("plays") is None)
missing_comments = sum(1 for r in own_reels if r.get("comments") is None or r["comments"] < 0)
likes_hidden = len(brand) - likes_vis
likes_hidden_all = sum(1 for r in inw if r.get("likes") in (None, -1))
stats = {
    "selected": 50, "classes": dict(cls), "rows_returned": len(rows), "rows_in_window": len(inw), "rows_outside_window": len(outw),
    "brand_authored_in_window": len(brand), "other_owner_in_window": other, "formats_brand": dict(fm),
    "observed_posts_per_account": {"n": len(counts), "median": med(counts), "q1": q[0], "q3": q[2], "min": counts[0], "max": counts[-1]},
    "accounts_with_observed_reel": withreel, "accounts_with_3plus_observed_reels": len(eligible3),
    "median_of_account_median_plays": med(acct_med_plays), "range_account_median_plays": [min(acct_med_plays), max(acct_med_plays)],
    "reels_in_3plus_accounts": len(all3), "pooled_median_plays": med([r["plays"] for r in all3]),
    "pooled_comments_per_1000_plays": round(sum(r["comments"] for r in all3) / sum(r["plays"] for r in all3) * 1000, 1),
    "brand_posts_visible_likes": likes_vis, "collaboration_posts": len(collab), "collaboration_videos": collab_video, "collaboration_on_accounts": collab_accounts, "collaboration_owner_accounts": collab_owners, "own_reels": len(own_reels), "own_reels_missing_plays": missing_plays, "own_reels_missing_comments": missing_comments, "own_posts_hidden_likes": likes_hidden, "origins": dict(orig), "account_types": dict(types),
}
json.dump(stats, open(ED / "draft" / "draft_figures.json", "w"), indent=1)

# ---- account table ---------------------------------------------------------------------------------
STATUS = {"A": "No recent posts (profile evidence)", "B": "Posts observed", "C": "Restricted by Instagram, not analysed",
          "E": "Could not be confirmed, not analysed"}
trs = []
for h in sorted(acc, key=lambda h: (REG.index(acc[h]["region"]), (roster[h]["name"] or h).lower())):
    a, c = acc[h], roster[h]
    nm = E(re.sub(r"\s+", " ", c["name"]).strip())
    if a["cls"] == "B":
        obs = f"{per[h]}"
        rl = f"{len(reels_by.get(h, []))}"
    elif a["cls"] == "A":
        obs, rl = "0 (see evidence)", "0"
    else:
        obs, rl = "not analysed", "not analysed"
    trs.append(f'<tr><td class="brandcell"><a href="https://www.instagram.com/{E(h)}/" target="_blank" rel="noopener">{nm}</a><span class="handle">@{E(h)}</span></td>'
               f'<td>{E(a["region"])}</td><td>{E(a["account_type"])}</td><td>{STATUS[a["cls"]]}</td><td class="r">{obs}</td><td class="r">{rl}</td></tr>')
acct_table = ('<div class="tw"><table><thead><tr><th>Account</th><th>Area</th><th>Type</th><th>Coverage status</th>'
              '<th class="r">Observed posts in window</th><th class="r">Observed own reels</th></tr></thead><tbody>\n' + "\n".join(trs) + '\n</tbody></table></div>')

reg_trs = "\n".join(
    f'<tr><td>{r}</td><td class="r">{sum(reg_cls[r].values())}</td><td class="r">{reg_cls[r]["B"]}</td><td class="r">{reg_cls[r]["A"]}</td>'
    f'<td class="r">{reg_cls[r]["C"]}</td><td class="r">{reg_cls[r]["E"]}</td></tr>' for r in REG)
reg_trs += (f'\n<tr><td><b>All regions</b></td><td class="r"><b>50</b></td><td class="r"><b>{cls["B"]}</b></td><td class="r"><b>{cls["A"]}</b></td>'
            f'<td class="r"><b>{cls["C"]}</b></td><td class="r"><b>{cls["E"]}</b></td></tr>')
tot_brand = len(brand)
pct = lambda x, d: f"{x / d * 100:.0f}%"

# ---- body ------------------------------------------------------------------------------------------
ap = argparse.ArgumentParser()
ap.add_argument("--target", choices=["draft", "release"], default="draft")
ap.add_argument("--edition", help="must equal edition.json edition (guards against building with stale values)")
ap.add_argument("--modified-at", help="ISO 8601 time with offset, the production deployment ready time; records dateModified and the visible Updated date")
ap.add_argument("--modified-source", help="where --modified-at came from (deployment id and commit)")
args = ap.parse_args()
if args.edition is not None and args.edition != ENO:
    raise SystemExit(f"stale edition: --edition {args.edition} but edition.json says {ENO}; update edition.json first")
MOD, UPDATED = None, ""
if args.modified_at:
    assert args.target == "release" and args.modified_source, "--modified-at needs --target release and --modified-source"
    _m = dt.datetime.fromisoformat(args.modified_at)
    assert _m.tzinfo is not None, "--modified-at needs a UTC offset"
    assert _m.date() >= dt.date.fromisoformat(CFG["scraped_at"]), "dateModified cannot precede the collection date"
    MOD = args.modified_at
    UPDATED = f'<span>Updated <b>{long_date(_m.astimezone(ZoneInfo("America/Toronto")).date().isoformat())}</b></span>'
# the edition record must agree with the data (stale counts stop the build)
_exp = {"selected": 50, "posts_observed": cls["B"], "profile_evidence_no_recent_posts": cls["A"], "restricted": cls["C"],
        "unconfirmed": cls["E"], "feed_posts_in_window": len(inw), "own_posts": len(brand), "collaboration_posts": len(collab)}
assert CFG["counts"] == _exp, f"edition.json counts {CFG['counts']} do not match the data {_exp}"

n_all3 = len(all3)
resv = sum(v for k, v in orig.items() if k != "original_sample")
multi_n = sum(reg_cls["Multi-region"].values())


COMPARE_DEFAULT = f'''<section id="ri-compare"><h3>Why this edition is not compared with edition 001</h3>
<div class="note"><p class="m0"><a href="/gta-medspa-index/edition-001">Edition 001</a> (10 September 2026) covered 341 accounts with a public profile, 176 of them ranked, from two collections whose full roster was not kept. Edition {ENO} uses a different, smaller and differently drawn set of accounts. Any difference between the two editions reflects who was included and how posts were collected, not a change in clinic performance, so I show no movement between them. Edition 001 is unchanged at its own address, with its corrections.</p></div></section>'''
HISTORY_DEFAULT = f'''<tr><td><b>{ENO}</b> (this page)</td><td class="wrap-cell">Observation window {WTXT}; data collected {CDATE}. <a href="{SNAP_PATH}">Snapshot</a></td><td class="wrap-cell">A selected 50-account sample with coverage groups and no ranking. The edition 001 roster was not kept, so the two editions are not compared.</td></tr>
<tr><td><b>001</b></td><td class="wrap-cell">Data collected 10 September 2026 and re-collected for the top 25 on 11 September 2026. <a href="/gta-medspa-index/edition-001">Snapshot</a></td><td class="wrap-cell">First edition: 176 ranked clinics of 341 with a public account. Revised 14 October 2026 for wording, layout and corrections, which stay recorded in the snapshot.</td></tr>'''
if ENO == "002":
    COMPARE, HISTORY_ROWS = COMPARE_DEFAULT, HISTORY_DEFAULT
else:
    COMPARE = (ED / "comparison_section.html").read_text()
    HISTORY_ROWS = (ED / "history_rows.html").read_text()


def body(draft):
    banner = ('<div class="note warn"><span class="lbl">Draft for review, not published</span>\n'
              '<p class="m0">This is a local draft built from saved records. It has not been through the publication review.</p></div>\n') if draft else ""
    return f'''<div class="wrap">
<header><p class="kicker">The HMM Index &middot; Instagram</p><h1>Med Spa Index</h1><p class="lede">Instagram video activity at 50 selected med spas in the Greater Toronto Area (Toronto, Peel, York, Durham and Halton), observed over the 90 days from {WTXT}.</p>
<div class="byline"><span><b>Observation window</b> {WTXT}</span><span>For clinic owners and marketing leads.</span><span>Research and analysis by <b><a href="/about">Ankit Kumar</a></b> &middot; Founder, <a href="/">HMM</a></span></div>
<div class="livebar"><span>Data collected <b>{CDATE}</b></span><span>Edition <b>{ENO}</b></span>{UPDATED}</div></header>
{banner}<section id="ri-why"><div class="sec-head"><h2>What I investigated and why it matters</h2></div>
<p class="dek">I wanted to describe how med spas in the Greater Toronto Area use Instagram video: whether they posted, what they posted and what the public play and comment counts record. I looked at 50 accounts in Toronto, Peel, York, Durham and Halton, drawn at random, in proportion to region, from med spas I found through Google Maps searches, over the 90 days from {WTXT}. This is a benchmark of a sample: not every GTA clinic, and not a ranking of clinics.</p>
<p class="dek">It matters to clinic owners because Instagram video is one place to spend limited marketing time, and a measured description of local activity can serve as a reference point when you look at your own record. The figures do not show enquiries, bookings or revenue, and they do not show what works. How the accounts were chosen, how completely they could be observed and where the study stops are set out in the last section.</p></section>
<section id="ri-overview"><div class="sec-head"><h2>What I observed</h2></div>
<div class="tiles">
<div class="tile"><div class="k">Accounts selected</div><div class="v">50</div></div>
<div class="tile"><div class="k">With posts observed in the window</div><div class="v">{cls["B"]}</div></div>
<div class="tile"><div class="k">Profile evidence of no recent posts</div><div class="v">{cls["A"]}</div></div>
<div class="tile"><div class="k">Restricted or unconfirmed</div><div class="v">{cls["C"] + cls["E"]}</div></div>
<div class="tile"><div class="k">Posts observed on their feeds in the window</div><div class="v">{n(len(inw))}</div></div>
</div>
<p class="pnote"><b>Coverage.</b> Selected 50. Posting activity is analysed for 48 of the 50: {cls["B"]} had posts in the window and {cls["A"]} showed no posts in it on their profile pages. {cls["C"]} account is restricted by Instagram and {cls["E"]} could not be confirmed. Those two are shown as such, are not counted as inactive and are left out of every calculation. Post-level figures below use the {cls["B"]} accounts with observed posts.</p>
<div class="note mt0"><span class="lbl">What this edition measures</span>
<p><b>Measured:</b> the posts, recorded reel plays, comments and likes visible on each account&rsquo;s public Instagram feed. <b>Not measured:</b> enquiries, booked or attended consultations, treatments sold or revenue. Comments are a public signal, never bookings. There is no score and no leaderboard in this edition: how completely each account&rsquo;s posts were collected is not comparable across accounts, so ordering clinics would overstate what the data can support.</p></div>
<div class="card"><h3>Reels were the largest share of observed posts, but the picture is incomplete</h3>
<p class="dek">Among the {tot_brand} observed posts that the {cls["B"]} posting accounts published themselves, {fm["Reel"]} ({pct(fm["Reel"], tot_brand)}) were reels, {fm["Static"]} ({pct(fm["Static"], tot_brand)}) static images and {fm["Carousel"]} ({pct(fm["Carousel"], tot_brand)}) carousels. {withreel} of the {cls["B"]} accounts had at least one own reel. <b>Denominator:</b> {tot_brand} own posts from {cls["B"]} accounts. Collaboration posts are not in this count (see the definitions below). These shares describe the posts that were collected, not every post these accounts published, and not clinics in general.</p>
<h3>Observed posts per account varied widely</h3>
<p class="dek">Across the {cls["B"]} posting accounts, the number of posts observed on the feed in the window had a median of {fmt_num(stats["observed_posts_per_account"]["median"])} (middle half {fmt_num(q[0])} to {fmt_num(q[2])}, lowest {counts[0]}, highest {counts[-1]}). <b>Denominator:</b> all {n(len(inw))} in-window posts returned on those {cls["B"]} feeds, which are the {tot_brand} own posts plus {len(collab)} collaboration posts. It is a count of collected posts, not a verified posting frequency: the collection tool filtered by date, so complete paging of every account&rsquo;s window cannot be shown from the records.</p>
<h3>Recorded plays per reel were spread across a wide range</h3>
<p class="dek">{len(eligible3)} of the {cls["B"]} accounts had three or more own reels with recorded plays. Their recorded plays per reel had a median of {fmt_num(stats["median_of_account_median_plays"])} when each account&rsquo;s median is taken first (lowest account median {fmt_num(stats["range_account_median_plays"][0])}, highest {fmt_num(stats["range_account_median_plays"][1])}), and {fmt_num(stats["pooled_median_plays"])} across all {n_all3} of those reels pooled. Those {n_all3} reels drew {stats["pooled_comments_per_1000_plays"]} public comments per 1,000 recorded plays in total. <b>Denominator:</b> {len(eligible3)} accounts and {n_all3} own reels, out of {len(own_reels)} own reels on the {cls["B"]} accounts. Pooled figures weigh accounts with more reels more heavily. They describe this sample and imply no cause and no ordering of accounts.</p>
<p class="pnote m0"><em>These findings describe this sample, not bookings, patients, revenue or cause and effect. Likes were hidden on {likes_hidden} of the {tot_brand} own posts, so no like-based comparison is made.</em></p></div></section>
<section id="ri-coverage"><div class="sec-head"><h2>Supporting figures: which accounts could be analysed</h2>
<p class="dek">Each account is placed in one group, and the groups are never merged. A restricted or unconfirmed account is not an inactive one.</p></div>
<div class="tw"><table><thead><tr><th>Area</th><th class="r">Selected</th><th class="r">Posts observed</th><th class="r">No recent posts</th><th class="r">Restricted</th><th class="r">Unconfirmed</th></tr></thead><tbody>
{reg_trs}
</tbody></table></div>
<div class="grid2">
<div class="card"><h4>Posts observed ({cls["B"]})</h4><p class="dek m0">One or more posts inside the window were collected from the feed.</p></div>
<div class="card"><h4>No recent posts ({cls["A"]})</h4><p class="dek m0">The profile could be read and its newest posts, or its post count of zero, show nothing since {WSTART}. This rests on the latest posts a profile page shows (up to 12), so it is evidence of no recent posts, not a count of zero from a full feed.</p></div>
<div class="card"><h4>Restricted ({cls["C"]})</h4><p class="dek m0">Instagram restricts the profile (an age gate), so the public tools could not read its posts. Selected, shown, not analysed, not counted as inactive.</p></div>
<div class="card"><h4>Unconfirmed ({cls["E"]})</h4><p class="dek m0">The profile was reachable but showed no post count or latest posts, and the post collection returned nothing. Whether it posted is not established.</p></div>
</div>
<section><details class="ri-adv"><summary>The 50 accounts</summary>
<p class="pnote">Listed by area and then name, not by any result. Observed posts are all collected feed posts in the window (collaboration posts included); observed own reels are reels the account published itself.</p>
{acct_table}
</details></section>
</section>
<section id="ri-interpretation"><div class="sec-head"><h2>What this could mean for a clinic</h2></div>
<div class="note mt0"><span class="lbl">Interpretation, not a measured finding</span>
<p>The figures above describe 50 selected accounts. They can serve as a rough reference point for your own account: for example, how many posts appeared on a feed in the window (the median was {fmt_num(stats["observed_posts_per_account"]["median"])} among the {cls["B"]} accounts that posted) and how recorded reel plays were spread. They do not show that posting more, or using more reels, leads to more plays, enquiries or bookings, and the accounts in the sample are not a ranking or a standard to match. Accounts that are restricted, unconfirmed or showed no recent posts are shown separately and say nothing about how those clinics perform.</p></div></section>
<section id="ri-help"><div class="sec-head"><h2>If you want your own account read this way</h2></div>
<div class="card"><p class="dek m0">This benchmark does not tell you how your clinic compares. If you would like your own Instagram video activity read against the same measures, <a href="/contact?intent=review&amp;entry=research_gta_medspa#contact-form" data-review-cta="research_gta_medspa">ask for a free marketing review</a>.</p></div></section>
<section id="ri-method"><div class="sec-head"><h2>Selection method, coverage and limitations</h2>
<p class="dek">The study covers med spas in Toronto, Peel, York, Durham and Halton, observed from {WTXT}. Fifty accounts were selected as follows.</p></div>
<section id="ri-frame"><h3>How the 50 accounts were chosen</h3>
<ol>
<li>Google Maps searches for medical spas across Toronto, Peel, York, Durham and Halton (60 searches, each capped at 60 places) returned 2,842 unique business listings.</li>
<li>Listings that were not aesthetics clinics, or were outside the five regions, were removed. Listings with an official Instagram link on the clinic&rsquo;s website or Google listing were grouped by account, so a shared account counts once. That left 872 eligible accounts.</li>
<li>A region-proportional random sample of 600 was drawn, with Toronto, Peel, York, Durham, Halton and accounts that span regions as separate groups. A profile check left 596 accounts.</li>
<li>From those 596, 50 were drawn the same way (fixed seed, region-proportional, shuffled by account name), before any post was read: Toronto 13, Peel 7, York 14, Durham 6, Halton 7 and {multi_n} spanning more than one region. Nothing was chosen on followers, engagement, results or whether collection worked. Of the 50, {types["single-location"]} are single-location accounts, {types["multi-location group"]} are multi-location groups and {types["chain (4 or more branches)"]} is a chain.</li></ol>
<div class="note warn"><span class="lbl">Selection effects and one error in the public-access check</span>
<p><b>Not every selected account passed a public-access test.</b> The profile check that decided who stayed in the pool treated Instagram&rsquo;s &ldquo;Restricted profile&rdquo; status as public. Twelve restricted accounts therefore stayed in the pool of 596, and one of them was drawn into the 50. It is kept in the sample, shown as restricted and left out of every calculation. I have not replaced it.</p>
<p><b>Accounts needed a public profile at selection time and an official link.</b> Clinics with no Instagram link on their listing (647 listings) or an unverified link (49) are outside the frame. {resv} of the 50 are reserve substitutes, drawn in a fixed order from the same region, for original draws whose profile was not found or was private; four such places in the larger pool were left unfilled.</p>
<p class="m0"><b>So the 50 are a sample of a sample.</b> Google Maps discovery from capped searches does not find every GTA clinic. The results describe these accounts, not the market.</p></div></section>
<section id="ri-limits"><h3>Limitations in brief</h3>
<ul>
<li>The 50 are a sample of a sample: Google Maps discovery from capped searches does not find every GTA clinic.</li>
<li>Posts are observed, not counted from a verified full feed: the collection tool filtered by date, so complete paging of every window cannot be shown.</li>
<li>&ldquo;No recent posts&rdquo; rests on the latest posts a profile page shows, not on a full feed.</li>
<li>Restricted and unconfirmed accounts are shown as such and are not analysed or counted as inactive.</li>
<li>Comments are a public signal, never bookings, and recorded plays are not reach.</li>
<li>There is no ranking or score, and this edition is not compared with edition 001.</li></ul></section>
{COMPARE}
<section id="ri-advanced"><h3>Methodology, citation and edition history</h3>
<section><details class="ri-adv"><summary>How the figures are defined</summary>
<ul>
<li><b>Posts observed on the feed ({n(len(inw))}).</b> Every post returned for the 50 accounts and dated inside the window, {WTXT}, both days included. It is the {tot_brand} posts the accounts published plus {len(collab)} collaboration posts.</li>
<li><b>Collaboration posts ({len(collab)}).</b> Instagram collaboration posts appear on each collaborator&rsquo;s feed but record one account as the owner. In all {len(collab)}, the selected account is listed as a co-author and another account is recorded as owner ({collab_owners} different owners, appearing on the feeds of {collab_accounts} of the 50 accounts; {collab_video} are videos). They are real posts on the account&rsquo;s feed, not unrelated content. They count in observed posts per account. They are left out of the format shares and the reel and comment figures, because the play and comment counts belong to the post owner and would otherwise be counted under more than one account.</li>
<li><b>Own posts ({tot_brand}).</b> Posts where the selected account is the recorded owner. {sum(1 for r in brand if r.get("coauthors"))} of them also list co-authors; they stay in as own posts.</li>
<li><b>Median {fmt_num(stats["observed_posts_per_account"]["median"])} observed posts per account.</b> Taken over the {cls["B"]} accounts with posts observed, using all {n(len(inw))} posts on their feeds, collaboration posts included. The {cls["A"]} accounts with no recent posts, the restricted account and the unconfirmed account are not in this median.</li>
<li><b>Format shares.</b> The {tot_brand} own posts only. A reel is a video post, a carousel is a multi-image post and a static post is a single image.</li>
<li><b>Reel plays and comments.</b> The {len(own_reels)} own reels on the {cls["B"]} accounts, limited to the {len(eligible3)} accounts with three or more of them ({n_all3} reels). Recorded plays are the video play counts Instagram showed when the post was collected. All {len(own_reels)} own reels had a recorded play count and a comment count, so none was dropped for missing data. Comments per 1,000 plays is the total comments divided by the total plays across those {n_all3} reels, times 1,000.</li>
<li><b>Likes.</b> Hidden on {likes_hidden} of the {tot_brand} own posts ({likes_hidden_all} of all {n(len(inw))} feed posts, which adds {likes_hidden_all - likes_hidden} of the {len(collab)} collaboration posts), so likes are not used in any comparison. Missing values are never filled in or treated as zero.</li></ul></details></section>
<section><details class="ri-adv"><summary>How the posts were collected and counted</summary>
<p>Posts were collected on {CDATE} from each account&rsquo;s public Instagram feed with the Apify Instagram scraper, in five runs of ten accounts, with a limit of 200 posts per account and a start date of {WSTART_LONG}. The tool returned {n(len(rows))} posts for the 50 accounts. {len(outw)} were older pinned posts dated before the window and are excluded; {n(len(inw))} fall inside the window. No account reached the 200-post limit (the highest had {counts[-1]}), and no run reached its spending cap.</p>
<p><b>What the records cannot prove.</b> The date filter drops older posts before they can be inspected, so I cannot show that every account&rsquo;s window was paged to its start. Restricted-page errors came back for some runs without an account name, so a partial restriction cannot be ruled out for any account. These counts are observed posts, not a census of everything published.</p>
<p><b>Reconciliation.</b> 50 selected = {cls["B"]} with observed posts + {cls["A"]} with profile evidence of no recent posts + {cls["C"]} restricted + {cls["E"]} unconfirmed. {n(len(rows))} posts returned = {n(len(inw))} in the window + {len(outw)} outside it. Every post belongs to a selected account.</p></details></section>
<div class="grid2">
<div class="card"><h4>About the researcher</h4>
<p class="dek">Ankit Kumar is the founder of Help Me Marketing. His work covers performance marketing, conversion tracking and competitive research. Through The HMM Index, he analyses marketing activity and explains the patterns, limitations and practical questions behind the numbers.</p>
<p class="dek m0"><a href="/about">About Ankit</a> &middot; <a href="/work">Explore HMM&rsquo;s work</a></p></div>
<div class="card" id="ri-cite"><h4>Cite this research</h4>
<p class="dek">Ankit Kumar, Help Me Marketing. <i>Med Spa Index</i> (The HMM Index). Edition {ENO}. Data collected {CDATE}. <a href="https://helpmemarketing.com{PAGE_PATH}">https://helpmemarketing.com{PAGE_PATH}</a></p>
<p class="dek m0">For a fixed version, cite the <a href="{SNAP_PATH}">edition {ENO} snapshot</a>. The earlier edition is at its <a href="/gta-medspa-index/edition-001">edition 001 snapshot</a>. <a href="#ri-editions">Edition history</a></p></div></div>
<section id="ri-editions"><details class="ri-adv"><summary>Edition history</summary>
<div class="tw"><table><thead><tr><th>Edition</th><th>Dates</th><th>What changed</th></tr></thead><tbody>
{HISTORY_ROWS}
</tbody></table></div>
<p class="pnote">This address always shows the latest edition. Snapshots keep each edition at a fixed address.</p></details></section></section>
</section>
<footer>
<div class="about"><p><b>About this index.</b> The Med Spa Index is part of <b>The HMM Index</b> by Help Me Marketing. Edition {ENO} reports public Instagram activity from a 50-account sample of med spas in the Greater Toronto Area (Toronto, Peel, York, Durham and Halton), with its sampling frame and limits on this page.</p></div>
<div class="byline-block">
<p><b>Med Spa Index</b> &middot; an instance of <b>The HMM Index</b> by HMM &middot; built and reviewed by <b>Ankit Kumar</b>, Founder, HMM &middot; <a href="https://www.instagram.com/helpmemarketing1/" target="_blank" rel="noopener">@helpmemarketing1</a> &middot; <a href="#ri-advanced">methodology</a></p>
<div class="socials"><a href="https://www.instagram.com/helpmemarketing1/" target="_blank" rel="noopener">Instagram</a>
<a href="https://www.linkedin.com/company/helpmemarketing/" target="_blank" rel="noopener">LinkedIn</a>
<a href="https://www.facebook.com/helpmemarketing1" target="_blank" rel="noopener">Facebook</a></div>
<p>Data collected <b>{CDATE}</b> &middot; edition <b>{ENO}</b></p>
<p>Clinic names are used to report publicly available data and imply no relationship with Help Me Marketing.</p>
</div></footer></div>
'''


# ---- shell -----------------------------------------------------------------------------------------
BASE = "https://helpmemarketing.com"
OG = BASE + "/assets/index/gta-medspa/medspa-index-og.jpg"
H1 = "Med Spa Index"
TITLE = "Med Spa Index"
DESC = "A 50-account observational study of how Greater Toronto Area med spas use Instagram video, with sampling, coverage and limits shown. By Ankit Kumar."
SNAP_TITLE = f"Med Spa Index Edition {ENO}"
SNAP_DESC = f"Fixed snapshot of edition {ENO} of the Med Spa Index: a selected 50-account study of Instagram video at GTA med spas, collected {CDATE}."
for t, d in ((TITLE, DESC), (SNAP_TITLE, SNAP_DESC)):
    assert 30 <= len(t + " | HelpMeMarketing") <= 60 and 70 <= len(d) <= 158, (t, len(t) + 18, len(d))

raw = open(HERE / "site_shell.html").read()
raw = re.sub(r"<script data-ri-reading>.*?</script>\n?", "", raw, flags=re.S)
raw = re.sub(r"<script data-bar-widths>.*?</script>\n?", "", raw, flags=re.S)
assert "data-ri-reading" not in raw and "data-bar-widths" not in raw
raw = raw.replace("/assets/index/gta-medspa/hero.webp", "/assets/index/gta-medspa/medspa-index-hero.webp")
raw = raw.replace(BASE + "/assets/index/gta-medspa/og.jpg", OG)


def sub1(pat, rep, s):
    out, k = re.subn(pat, lambda m: m.group(1) + rep, s, 1)
    assert k == 1, pat
    return out


def make(mode):
    """mode: draft, live or snapshot."""
    s = raw
    snap = mode == "snapshot"
    t, d = (SNAP_TITLE, SNAP_DESC) if snap else (TITLE, DESC)
    url = BASE + (SNAP_PATH if snap else PAGE_PATH)
    s = re.sub(r"<title>.*?</title>", f"<title>{t} | HelpMeMarketing</title>", s, 1)
    s = sub1(r'(<meta name="description" content=")[^"]*', d, s)
    s = sub1(r'(<meta property="og:title" content=")[^"]*', t, s)
    s = sub1(r'(<meta name="twitter:title" content=")[^"]*', t, s)
    s = sub1(r'(<meta property="og:description" content=")[^"]*', d, s)
    s = sub1(r'(<meta name="twitter:description" content=")[^"]*', d, s)
    s = sub1(r'(<meta property="og:url" content=")[^"]*', url, s)
    s = sub1(r'(<link rel="canonical" href=")[^"]*', url, s)
    s = sub1(r'(<meta property="og:image:alt" content=")[^"]*', "HMM research graphic: Med Spa Index, a selected 50-account study of GTA med spas on Instagram", s)
    robots = {"draft": "noindex, nofollow", "snapshot": "noindex, follow"}.get(mode)
    if robots:
        s = re.sub(r'<meta name="robots" content="[^"]*">', f'<meta name="robots" content="{robots}">', s, 1)
    if snap:
        s = s.replace("</head>", f"<!-- Snapshot of edition {ENO} as first published. Research content in this snapshot is never rewritten; record any later metadata fix in this comment and add a visible dated note for any visible correction. -->\n</head>", 1) \
            if "<!-- Snapshot of edition" not in s else s
    s = s.replace('<meta property="article:published_time" content="2026-09-10">\n', "")

    def ld(m):
        j = json.loads(m.group(1))
        ty = j.get("@type")
        if ty == "FAQPage":
            return ""
        if ty == "BreadcrumbList":
            items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": BASE + "/"},
                     {"@type": "ListItem", "position": 2, "name": "Medspa Marketing Research", "item": BASE + "/medspa-marketing-research"}]
            if snap:
                items += [{"@type": "ListItem", "position": 3, "name": "Med Spa Index", "item": BASE + PAGE_PATH},
                          {"@type": "ListItem", "position": 4, "name": f"Edition {ENO}", "item": url}]
            else:
                items += [{"@type": "ListItem", "position": 3, "name": H1, "item": url}]
            j["itemListElement"] = items
        if ty == "Article":
            j["headline"], j["description"], j["url"] = H1, d, url
            j["image"] = {"@type": "ImageObject", "url": OG, "width": 1200, "height": 630}
            if MOD:
                j["dateModified"] = MOD  # the production deployment ready time, passed in at publication
            else:
                j.pop("dateModified", None)  # never guessed
            if snap:
                j.pop("isPartOf", None)
        if ty == "Dataset":
            j["name"] = "GTA medspa Instagram activity, 50-account sample, 90 days to October 2026"
            j["description"] = (f"Public Instagram posts, recorded reel plays, likes and comments for a region-proportional random sample of 50 medical spa accounts in Toronto, Peel, York, Durham and Halton; "
                                f"{cls['B']} had posts observed between {WSTART} and {WEND}. It does not include enquiries, consultations or revenue and is not a census of GTA clinics.")
            j["temporalCoverage"] = f"{W0}/{W1}"
            j["url"] = url
            j["variableMeasured"] = ["Observed posts", "Recorded reel plays", "Comments", "Likes where visible"]
        return '<script type="application/ld+json">\n' + json.dumps(j, ensure_ascii=False, separators=(",", ":")) + "\n</script>"

    s = re.sub(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', ld, s, flags=re.S)
    a = s.index("<!-- ===== GTA MEDSPA INDEX REPORT BODY START =====")
    a = s.index("\n", a) + 1
    b = s.index("<!-- ===== GTA MEDSPA INDEX REPORT BODY END")
    return s[:a] + body(mode == "draft") + s[b:]


if args.target == "draft":
    (ED / "draft" / "medspa-index-draft.html").write_text(make("draft"))
    print("draft written")
else:
    (REPO / "medspa-index.html").write_text(make("live"))
    snapf = REPO / SNAP_PATH.lstrip("/")
    snapf = snapf.with_name(snapf.name + ".html")
    if snapf.exists():  # a published snapshot is never rewritten
        print(f"snapshot kept as published: {snapf.relative_to(REPO)}")
    else:
        snapf.parent.mkdir(parents=True, exist_ok=True)
        snapf.write_text(make("snapshot"))
    # local Sheet export files (not written to Sheets)
    sd = ED / "sheet"
    sd.mkdir(exist_ok=True)
    tab = lambda rows: "\n".join("\t".join(str(c).replace("\t", " ").replace("\n", " ") for c in r) for r in rows) + "\n"
    acc_rows = [["handle", "name", "region", "account_type", "origin", "class", "class_meaning", "observed_feed_posts", "observed_own_posts", "observed_own_reels"]]
    meaning = {"A": "profile evidence of no recent posts", "B": "posts observed", "C": "restricted, not analysed", "E": "unconfirmed, not analysed"}
    ownc = Counter(r["handle"].lower() for r in brand)
    for h in sorted(acc, key=lambda h: (REG.index(acc[h]["region"]), h)):
        a_ = acc[h]
        acc_rows.append([h, roster[h]["name"], a_["region"], a_["account_type"], a_["origin"], a_["cls"], meaning[a_["cls"]],
                         per.get(h, "") if a_["cls"] == "B" else "", ownc.get(h, "") if a_["cls"] == "B" else "", len(reels_by.get(h, [])) if a_["cls"] == "B" else ""])
    (sd / f"E{ENO}_accounts.tsv").write_text(tab(acc_rows))
    log = [["handle", "owner", "own_post", "shortcode", "date", "format", "plays", "likes_visible", "comments", "pinned"]]
    for r in sorted(inw, key=lambda r: (r["handle"].lower(), r["timestamp"])):
        own = (r.get("owner") or "").lower() == r["handle"].lower()
        log.append([r["handle"], r["owner"], "yes" if own else "no (collaboration)", r["shortcode"], r["timestamp"][:10], FMT[r["type"]],
                    r["plays"] if r["plays"] is not None else "", "yes" if r.get("likes") not in (None, -1) else "no", r["comments"], "yes" if r.get("pinned") else "no"])
    (sd / f"E{ENO}_postlog.tsv").write_text(tab(log))
    row = [ENO, CFG["scraped_at"], W0, W1, "candidate", 50, cls["B"] + cls["A"], cls["B"], cls["A"], cls["C"], cls["E"], len(inw), len(brand), len(collab), len(rows), len(outw),
           "selected 50-account observational study; no score or rank"]
    (sd / "editions_row.tsv").write_text(tab([row]))
    if MOD:
        import datetime
        hub = REPO / "medspa-marketing-research.html"
        h = hub.read_text()
        h, k1 = re.subn(r'("dateModified":")[^"]*', lambda m: m.group(1) + MOD, h, 1)
        tor = long_date(dt.datetime.fromisoformat(MOD).astimezone(ZoneInfo("America/Toronto")).date().isoformat())
        h, k2 = re.subn(r"(Published \d+ \w+ \d{4} &middot; Updated )\d+ \w+ \d{4}", lambda m: m.group(1) + tor, h, 1)
        assert k1 == 1 and k2 == 1, "research hub date markers not found"
        hub.write_text(h)
        CFG["modified_at"], CFG["modified_at_source"] = MOD, args.modified_source
        json.dump(CFG, open(HERE / "edition.json", "w"), indent=1, ensure_ascii=False)
    print(f"release files written; sheet export: {len(acc_rows) - 1} accounts, {len(log) - 1} posts")
print(json.dumps({k: stats[k] for k in ("classes", "rows_in_window", "brand_authored_in_window", "collaboration_posts", "collaboration_videos", "collaboration_on_accounts", "collaboration_owner_accounts", "own_reels", "own_reels_missing_plays", "own_reels_missing_comments", "own_posts_hidden_likes", "accounts_with_3plus_observed_reels", "reels_in_3plus_accounts")}))
