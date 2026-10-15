#!/usr/bin/env python3
"""Local draft of the 50-account GTA medspa Instagram benchmark (edition 002) from saved records only.

Reads editions/002/scope_50_accounts.json, source_posts_pilot.jsonl.gz, cohort_frozen.json and roster_eligible.json,
reconciles the counts (fails if they differ from the saved evidence), computes observed-data descriptive figures with
metric-specific denominators, and writes editions/002/draft/gta-medspa-index-50-draft.html using the live page shell
(head, nav, footer chrome) with a new body. No ranking, score or leaderboard: coverage comparability is not established.
"""
import gzip, html, json, re, statistics as st
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
ED = HERE / "editions" / "002"
W0, W1 = "2026-07-17", "2026-10-15"
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
scope = json.load(open(ED / "scope_50_accounts.json"))
cohort = {c["handle"]: c for c in json.load(open(ED / "cohort_frozen.json")).get("accounts", [])} \
    if isinstance(json.load(open(ED / "cohort_frozen.json")), dict) and "accounts" in json.load(open(ED / "cohort_frozen.json")) else {}
roster = {c["handle"]: c for c in json.load(open(ED / "roster_eligible.json"))["clinics"]}
acc = {a["handle"]: a for a in scope["accounts"]}
rows = [json.loads(l) for l in gzip.open(ED / "source_posts_pilot.jsonl.gz", "rt") if l.strip()]

assert len(acc) == 50, "50 selected accounts"
cls = Counter(a["cls"] for a in acc.values())
assert dict(cls) == {"A": 12, "B": 36, "C": 1, "E": 1}, cls
assert all(h in roster and roster[h]["selected"] or h in roster for h in acc), "every account is in the roster"
assert all((r["handle"] or "").lower() in acc for r in rows), "every row belongs to a selected account"
inw = [r for r in rows if W0 <= r["timestamp"][:10] <= W1]
outw = [r for r in rows if not (W0 <= r["timestamp"][:10] <= W1)]
assert (len(rows), len(inw), len(outw)) == (824, 783, 41), (len(rows), len(inw), len(outw))
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
assert {r: sum(c.values()) for r, c in reg_cls.items()} == {"York": 14, "Toronto": 13, "Peel": 7, "Halton": 7, "Durham": 6, "Multi-region": 3}
orig = Counter(a["origin"] for a in acc.values())
types = Counter(a["account_type"] for a in acc.values())

stats = {
    "selected": 50, "classes": dict(cls), "rows_returned": len(rows), "rows_in_window": len(inw), "rows_outside_window": len(outw),
    "brand_authored_in_window": len(brand), "other_owner_in_window": other, "formats_brand": dict(fm),
    "observed_posts_per_account": {"n": len(counts), "median": med(counts), "q1": q[0], "q3": q[2], "min": counts[0], "max": counts[-1]},
    "accounts_with_observed_reel": withreel, "accounts_with_3plus_observed_reels": len(eligible3),
    "median_of_account_median_plays": med(acct_med_plays), "range_account_median_plays": [min(acct_med_plays), max(acct_med_plays)],
    "reels_in_3plus_accounts": len(all3), "pooled_median_plays": med([r["plays"] for r in all3]),
    "pooled_comments_per_1000_plays": round(sum(r["comments"] for r in all3) / sum(r["plays"] for r in all3) * 1000, 1),
    "brand_posts_visible_likes": likes_vis, "origins": dict(orig), "account_types": dict(types),
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
BODY = f'''<div class="wrap">
<header><p class="kicker">The GTA MedSpa Index &middot; The HMM Index</p><h1>50-account GTA medspa Instagram benchmark</h1><p class="lede">I looked at the Instagram video activity of 50 medspa accounts in the Greater Toronto Area over the 90 days from 17 July to 15 October 2026. The 50 are a region-proportional random sample of accounts I found through Google Maps searches, so this is a benchmark of a sample: not every GTA clinic, and not a ranking of clinics.</p>
<div class="byline"><span><b>90 days</b> from 17 July to 15 October 2026</span><span>For clinic owners and marketing leads.</span><span>Research and analysis by <b><a href="/about">Ankit Kumar</a></b> &middot; Founder, <a href="/">HMM</a></span></div>
<div class="livebar"><span>Data collected <b>15 October 2026</b></span><span>Edition <b>002</b></span></div></header>
<div class="note warn"><span class="lbl">Draft for review, not published</span>
<p class="m0">This is a local draft built from saved records. It has not been through the publication review.</p></div>
<section id="ri-overview"><div class="sec-head"><h2>What this edition covers</h2></div>
<div class="tiles">
<div class="tile"><div class="k">Accounts selected</div><div class="v">50</div></div>
<div class="tile"><div class="k">With posts observed in the window</div><div class="v">{cls["B"]}</div></div>
<div class="tile"><div class="k">Profile evidence of no recent posts</div><div class="v">{cls["A"]}</div></div>
<div class="tile"><div class="k">Restricted or unconfirmed</div><div class="v">{cls["C"] + cls["E"]}</div></div>
<div class="tile"><div class="k">Observed posts in the window</div><div class="v">{n(len(inw))}</div></div>
</div>
<p class="pnote"><b>Coverage.</b> Selected 50. Posting activity is analysed for 48: {cls["B"]} posted in the window and {cls["A"]} had no posts in it, judged from their profile pages. {cls["C"]} account is restricted by Instagram and {cls["E"]} could not be confirmed, so both are shown as such, are not counted as inactive and are left out of every calculation.</p>
<div class="note mt0"><span class="lbl">What this edition measures</span>
<p><b>Measured:</b> the posts, recorded reel plays, comments and likes visible on each account&rsquo;s public Instagram feed. <b>Not measured:</b> enquiries, booked or attended consultations, treatments sold or revenue. Comments are a public signal, never bookings. There is no score and no leaderboard in this edition: how completely each account&rsquo;s posts were collected is not comparable across accounts, so ordering clinics would overstate what the data can support.</p></div>
<div class="card"><h3>Reels were the largest share of observed posts, but the picture is incomplete</h3>
<p class="dek">Among the {tot_brand} observed posts that the {cls["B"]} posting accounts published themselves, {fm["Reel"]} ({pct(fm["Reel"], tot_brand)}) were reels, {fm["Static"]} ({pct(fm["Static"], tot_brand)}) static images and {fm["Carousel"]} ({pct(fm["Carousel"], tot_brand)}) carousels. {withreel} of the {cls["B"]} had at least one observed reel. These shares describe the posts that were collected for these accounts, not every post they published, and not clinics in general.</p>
<h3>Observed posts per account varied widely</h3>
<p class="dek">Across the {cls["B"]} posting accounts, the number of observed posts in the window had a median of {fmt_num(stats["observed_posts_per_account"]["median"])} (middle half {fmt_num(q[0])} to {fmt_num(q[2])}, lowest {counts[0]}, highest {counts[-1]}). This is a count of collected posts, not a verified posting frequency: the collection tool filtered by date, so complete paging of every account&rsquo;s window cannot be shown from the records.</p>
<h3>Recorded plays per reel were spread across a wide range</h3>
<p class="dek">{len(eligible3)} of the {cls["B"]} accounts had three or more observed own reels. Their recorded plays per reel had a median of {fmt_num(stats["median_of_account_median_plays"])} when each account&rsquo;s median is taken first (lowest account median {fmt_num(stats["range_account_median_plays"][0])}, highest {fmt_num(stats["range_account_median_plays"][1])}), and {fmt_num(stats["pooled_median_plays"])} across all {len(all3)} of those reels pooled. Those {len(all3)} reels drew {stats["pooled_comments_per_1000_plays"]} public comments per 1,000 recorded plays in total. Pooled figures weigh accounts with more reels more heavily. They describe this sample and imply no cause and no ordering of accounts.</p>
<p class="pnote m0"><em>These findings describe this sample, not bookings, patients, revenue or cause and effect. Likes were hidden on {tot_brand - likes_vis} of the {tot_brand} own posts, so no like-based comparison is made.</em></p></div></section>
<section id="ri-coverage"><div class="sec-head"><h2>Which accounts could be analysed</h2>
<p class="dek">Each account is placed in one group, and the groups are never merged. A restricted or unconfirmed account is not an inactive one.</p></div>
<div class="tw"><table><thead><tr><th>Area</th><th class="r">Selected</th><th class="r">Posts observed</th><th class="r">No recent posts</th><th class="r">Restricted</th><th class="r">Unconfirmed</th></tr></thead><tbody>
{reg_trs}
</tbody></table></div>
<div class="grid2">
<div class="card"><h4>Posts observed ({cls["B"]})</h4><p class="dek m0">One or more posts inside the window were collected from the feed.</p></div>
<div class="card"><h4>No recent posts ({cls["A"]})</h4><p class="dek m0">The profile could be read and its newest posts, or its post count of zero, show nothing since 17 July. This rests on the latest posts a profile page shows (up to 12), so it is evidence of no recent posts, not a count of zero from a full feed.</p></div>
<div class="card"><h4>Restricted ({cls["C"]})</h4><p class="dek m0">Instagram restricts the profile (an age gate), so the public tools could not read its posts. Selected, shown, not analysed, not counted as inactive.</p></div>
<div class="card"><h4>Unconfirmed ({cls["E"]})</h4><p class="dek m0">The profile was reachable but showed no post count or latest posts, and the post collection returned nothing. Whether it posted is not established.</p></div>
</div></section>
<section id="ri-frame"><div class="sec-head"><h2>How the 50 accounts were chosen</h2></div>
<ol>
<li>Google Maps searches for medical spas across Toronto, Peel, York, Durham and Halton (60 searches, each capped at 60 places) returned 2,842 unique business listings.</li>
<li>Listings that were not aesthetics clinics, or were outside the five regions, were removed. Listings with an official Instagram link on the clinic&rsquo;s website or Google listing were grouped by account, so a shared account counts once. That left 872 eligible accounts.</li>
<li>A region-proportional random sample of 600 was drawn, with Toronto, Peel, York, Durham, Halton and accounts that span regions as separate groups. A profile check left 596 accounts.</li>
<li>From those 596, 50 were drawn the same way (fixed seed, region-proportional, shuffled by account name), before any post was read: Toronto 13, Peel 7, York 14, Durham 6, Halton 7 and {reg_cls["Multi-region"]["B"] + reg_cls["Multi-region"]["C"] + reg_cls["Multi-region"]["A"] + reg_cls["Multi-region"]["E"]} spanning more than one region. Nothing was chosen on followers, engagement, results or whether collection worked. Of the 50, {types["single-location"]} are single-location accounts, {types["multi-location group"]} are multi-location groups and {types["chain (4 or more branches)"]} is a chain.</li></ol>
<div class="note warn"><span class="lbl">Selection effects and one error in the public-access check</span>
<p><b>Not every selected account passed a public-access test.</b> The profile check that decided who stayed in the pool treated Instagram&rsquo;s &ldquo;Restricted profile&rdquo; status as public. Twelve restricted accounts therefore stayed in the pool of 596, and one of them was drawn into the 50. It is kept in the sample, shown as restricted and left out of every calculation. I have not replaced it.</p>
<p><b>Accounts needed a public profile at selection time and an official link.</b> Clinics with no Instagram link on their listing (647 listings) or an unverified link (49) are outside the frame. {orig["reserve_substitute"] if "reserve_substitute" in orig else sum(v for k, v in orig.items() if k != "original_sample")} of the 50 are reserve substitutes, drawn in a fixed order from the same region, for original draws whose profile was not found or was private; four such places in the larger pool were left unfilled.</p>
<p class="m0"><b>So the 50 are a sample of a sample.</b> Google Maps discovery from capped searches does not find every GTA clinic. The results describe these accounts, not the market.</p></div></section>
<section id="ri-compare"><div class="sec-head"><h2>Why this edition is not compared with edition 001</h2></div>
<div class="note"><p class="m0"><a href="/gta-medspa-index/edition-001">Edition 001</a> (10 September 2026) covered 341 accounts with a public profile, 176 of them ranked, from two collections whose full roster was not kept. Edition 002 uses a different, smaller and differently drawn set of accounts. Any difference between the two editions reflects who was included and how posts were collected, not a change in clinic performance, so I show no movement between them. Edition 001 is unchanged at its own address.</p></div></section>
<section id="ri-advanced"><div class="sec-head"><h2>Research and methodology</h2></div>
<section><details class="ri-adv"><summary>How the posts were collected and counted</summary>
<p>Posts were collected on 15 October 2026 from each account&rsquo;s public Instagram feed with the Apify Instagram scraper, in five runs of ten accounts, with a limit of 200 posts per account and a start date of 17 July 2026. The tool returned {n(len(rows))} posts for the 50 accounts. {len(outw)} were older pinned posts dated before the window and are excluded; {n(len(inw))} fall inside the window of 17 July to 15 October 2026, both days included. {len(brand)} of those were published by the account itself and {other} came from feeds where the post is owned by another account (co-authored or collaboration posts); the format shares above use the account&rsquo;s own posts. No account reached the 200-post limit (the highest had {counts[-1]}), and no run reached its spending cap.</p>
<p><b>What the records cannot prove.</b> The date filter drops older posts before they can be inspected, so I cannot show that every account&rsquo;s window was paged to its start. Restricted-page errors came back for some runs without an account name, so a partial restriction cannot be ruled out for any account. These counts are observed posts, not a census of everything published. A reel is a video post, and recorded plays are the play counts Instagram showed when the post was collected.</p>
<p><b>Reconciliation.</b> 50 selected = {cls["B"]} with observed posts + {cls["A"]} with profile evidence of no recent posts + {cls["C"]} restricted + {cls["E"]} unconfirmed. {n(len(rows))} posts returned = {n(len(inw))} in the window + {len(outw)} outside it. Every post belongs to a selected account.</p></details></section>
<section><details class="ri-adv"><summary>The 50 accounts</summary>
<p class="pnote">Listed by area and then name, not by any result. Observed counts are collected posts in the window, not verified posting frequency.</p>
{acct_table}
</details></section>
<div class="grid2">
<div class="card"><h4>About the researcher</h4>
<p class="dek">Ankit Kumar is the founder of Help Me Marketing. His work covers performance marketing, conversion tracking and competitive research. Through The HMM Index, he analyses marketing activity and explains the patterns, limitations and practical questions behind the numbers.</p>
<p class="dek m0"><a href="/about">About Ankit</a> &middot; <a href="/work">Explore HMM&rsquo;s work</a></p></div>
<div class="card" id="ri-cite"><h4>Cite this research</h4>
<p class="dek">Ankit Kumar, Help Me Marketing. <i>50-account GTA medspa Instagram benchmark</i> (The GTA MedSpa Index). Edition 002. Data collected 15 October 2026. <a href="https://helpmemarketing.com/gta-medspa-index">https://helpmemarketing.com/gta-medspa-index</a></p>
<p class="dek m0">For a fixed version of the earlier edition, cite the <a href="/gta-medspa-index/edition-001">edition 001 snapshot</a>. <a href="#ri-editions">Edition history</a></p></div></div>
<section id="ri-editions"><details class="ri-adv"><summary>Edition history</summary>
<div class="tw"><table><thead><tr><th>Edition</th><th>Dates</th><th>What changed</th></tr></thead><tbody>
<tr><td><b>002</b> (this page)</td><td class="wrap-cell">Data collected 15 October 2026</td><td class="wrap-cell">A 50-account sample with coverage groups and no ranking. The edition 001 roster was not kept, so the two editions are not compared.</td></tr>
<tr><td><b>001</b></td><td class="wrap-cell">Data collected 10 September 2026 and re-collected for the top 25 on 11 September 2026. <a href="/gta-medspa-index/edition-001">Snapshot</a></td><td class="wrap-cell">First edition: 176 ranked clinics of 341 with a public account.</td></tr>
</tbody></table></div></details></section></section>
<footer>
<div class="about"><p><b>About this index.</b> The GTA MedSpa Index is part of <b>The HMM Index</b> by Help Me Marketing. Edition 002 reports public Instagram activity from a 50-account sample of medical spas in Toronto, Peel, York, Durham and Halton, with its sampling frame and limits on this page.</p></div>
<div class="byline-block">
<p><b>The GTA MedSpa Index</b> &middot; an instance of <b>The HMM Index</b> by HMM &middot; built and reviewed by <b>Ankit Kumar</b>, Founder, HMM &middot; <a href="https://www.instagram.com/helpmemarketing1/" target="_blank" rel="noopener">@helpmemarketing1</a> &middot; <a href="#ri-advanced">methodology</a></p>
<div class="socials"><a href="https://www.instagram.com/helpmemarketing1/" target="_blank" rel="noopener">Instagram</a>
<a href="https://www.linkedin.com/company/helpmemarketing/" target="_blank" rel="noopener">LinkedIn</a>
<a href="https://www.facebook.com/helpmemarketing1" target="_blank" rel="noopener">Facebook</a></div>
<p>Data collected <b>15 October 2026</b> &middot; edition <b>002</b></p>
<p>Clinic names are used to report publicly available data and imply no relationship with Help Me Marketing.</p>
</div></footer></div>
'''

# ---- shell: head metadata and JSON-LD, then the new body ------------------------------------------
shell = open(HERE / "site_shell.html").read()
TITLE = "50-account GTA medspa Instagram benchmark"
DESC = "A benchmark of Instagram video activity across 50 medspa accounts in the Greater Toronto Area, with coverage, sampling and limits shown. By Ankit Kumar."
assert 30 <= len(TITLE + " | HelpMeMarketing") <= 60 and 70 <= len(DESC) <= 158, (len(TITLE) + 18, len(DESC))
shell = re.sub(r"<title>.*?</title>", f"<title>{TITLE} | HelpMeMarketing</title>", shell, 1)
shell = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + DESC, shell, 1)
shell = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + TITLE, shell, 1)
shell = re.sub(r'(<meta name="twitter:title" content=")[^"]*', lambda m: m.group(1) + TITLE, shell, 1)
shell = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + DESC, shell, 1)
shell = re.sub(r'(<meta name="twitter:description" content=")[^"]*', lambda m: m.group(1) + DESC, shell, 1)
shell = re.sub(r'(<meta property="og:image:alt" content=")[^"]*', lambda m: m.group(1) + "The GTA MedSpa Index: a 50-account benchmark of Instagram video activity", shell, 1)
shell = re.sub(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="noindex, nofollow">', shell, 1)
shell = re.sub(r'<meta property="article:published_time" content="[^"]*">\n', "", shell, 1)


def ld(m):
    d = json.loads(m.group(1))
    t = d.get("@type")
    if t == "FAQPage":
        return ""
    if t == "Article":
        d["headline"], d["description"] = TITLE, DESC
        d.pop("dateModified", None)
    if t == "Dataset":
        d["name"] = "GTA medspa Instagram activity, 50-account sample, 90 days to October 2026"
        d["description"] = (f"Public Instagram posts, recorded reel plays, likes and comments for a region-proportional random sample of 50 medical spa accounts in Toronto, Peel, York, Durham and Halton, "
                            f"{cls['B']} of which had posts observed between 17 July and 15 October 2026. It does not include enquiries, consultations or revenue and is not a census of GTA clinics.")
        d["temporalCoverage"] = f"{W0}/{W1}"
        d["variableMeasured"] = ["Observed posts", "Recorded reel plays", "Comments", "Likes (where visible)"]
    return '<script type="application/ld+json">\n' + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + "\n</script>"


shell = re.sub(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', ld, shell, flags=re.S)
a = shell.index("<!-- ===== GTA MEDSPA INDEX REPORT BODY START =====")
a = shell.index("\n", a) + 1
b = shell.index("<!-- ===== GTA MEDSPA INDEX REPORT BODY END")
out = shell[:a] + BODY + shell[b:]
(ED / "draft" / "gta-medspa-index-50-draft.html").write_text(out)
print(f"draft written: {len(out):,} chars; figures -> draft/draft_figures.json")
print(json.dumps({k: stats[k] for k in ("classes", "rows_in_window", "brand_authored_in_window", "formats_brand", "observed_posts_per_account", "accounts_with_3plus_observed_reels", "median_of_account_median_plays", "pooled_median_plays", "pooled_comments_per_1000_plays")}))
