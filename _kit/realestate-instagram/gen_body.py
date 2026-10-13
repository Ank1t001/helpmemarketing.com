#!/usr/bin/env python3
"""Generate report_body.html for an Instagram cycle from verified inputs.

Every count, median, badge and cell on the page is computed here from reindex_data.py,
ig_postlog.json, the cycle CSV and cycle_inputs.json, so the consistency rules hold by
construction:
  1. verdict badges come only from card-post likes against that account's window median;
  2. download and gate counts are tokens filled from the embedded CSV by ig_body.render;
  3. accounts with no video print "no video" in like/play and peak cells, never 0;
  4. generalisations name their exceptions (written into the editorial strings below);
  5. claim language: no "proves", "only variable" or "every frame" in generated copy.
Editorial strings are cycle-specific and must be rewritten each cycle from the evidence.
"""
import sys
sys.exit("RETIRED 2026-10-13: gen_body.py emits the pre-13-October page structure (old header, BOOST/ORGANIC flags, Advanced research). "
         "Start from report_body.html, the reviewed live body, and update its figures and editorial text from the new cycle's evidence.")
import csv, html, io, json, math, statistics as st
from collections import Counter, defaultdict
from pathlib import Path
import reindex_data as data
from build_v2 import metrics

BASE = Path(__file__).resolve().parent
CFG = json.loads((BASE / 'ig_cycle.json').read_text())
INP = json.loads((BASE / 'cycle_inputs.json').read_text())
E = html.escape
ORDER = list(data.IG_BRANDS)
SLUG = {'Skyline': 'skyline', 'Equiton': 'equiton', 'Lankin': 'lankin', 'Pier 4': 'pier-4',
        'McGillivray Capital': 'mcgillivray'}

M = metrics()
RANKED = sorted(M, key=lambda b: M[b]['rank'])
LOG = json.loads((BASE / 'ig_postlog.json').read_text())   # brand,date,fmt,theme,hook,likes,comments,plays,code
POSTS = defaultdict(list)
for r in LOG:
    POSTS[r[0]].append(r)
N = len(LOG)
COMMENTS = {b: sum(r[6] for r in POSTS[b]) for b in ORDER}
TOTAL_COMMENTS = sum(COMMENTS.values())
PRIOR = {r['brand']: (int(r['rank']), int(r.get('ig_score') or r['score'])) for r in
         csv.DictReader(io.StringIO((BASE / CFG['prior_scoreboard']).read_text(encoding='utf-8-sig')))}
REF = data.IG_REF
CYC = CFG['cycle']


def url(code):
    return f'https://www.instagram.com/p/{code}/'


def link(code, text='post'):
    return f'<a href="{url(code)}" target="_blank" rel="noopener">{text}</a>'


def num(x):
    return f'{x:,}'


def med(x):
    return f'{x:g}'


def top_post(b):
    return max(POSTS[b], key=lambda r: (r[5], r[6]))


def verdict(likes, median):
    ratio = likes / median if median else float('inf')
    if ratio >= 1.25:
        return 'ok', 'WINS', ratio
    if ratio >= 0.8:
        return 'avg', 'AVERAGE', ratio
    return 'crit', 'UNDERPERFORMS', ratio


def mix(b):
    c = Counter(r[2][0] for r in POSTS[b])
    return '·'.join(f'{c[k]}{k}' for k in 'RCS' if c[k])


def move(b):
    m = M[b]
    if b not in PRIOR:
        return 'new entry'
    pr, ps = PRIOR[b]
    d = pr - m['rank']
    ds = m['score'] - ps
    mv = 'same rank' if d == 0 else (f'up {d}' if d > 0 else f'down {-d}')
    return f"#{m['rank']}, {mv}, {'+' if ds >= 0 else '-'}{abs(ds)}"


def score_cls(s):
    return 'hi' if s >= 70 else 'mid' if s >= 45 else 'lo'


def flag_cls(f):
    return 'none' if f == 'ORGANIC' else 'heavy' if f.startswith('BOOST') else 'some'


def lv_cell(m):
    return 'no video' if not m['has_video'] else f"{m['lv']:.2f}%"


def peak_cell(m):
    return 'no video' if not m['has_video'] else (f"{m['peak']:.2f}x" if m['peak'] < 1 else f"{m['peak']:.1f}x")


def peak90(b):
    p = data.IG_PEAK_90D.get(b)
    return p['plays'] / M[b]['followers'] if p else None


ADS = INP['ads']                      # brand -> {pages:[{name, count, first, last, audience}], founder:..}
TIP = {
 'score': 'A 0 to 100 blend of three pillars: Resonance at 45 percent, Intent at 30, and Distribution honesty at 25. Momentum and Consistency are not part of this three-pillar score.',
 'foll': 'Deliberately greyed. Audience size predicts little on this page.',
 'posts': 'Company authored posts inside the 30 day window. Below 5 posts a firm is quarantined from pooled medians.',
 'mix': 'Format split: R for Reels, C for Carousels, S for Statics. Formats a firm did not publish are left out rather than shown as zero.',
 'medl': "The middle post's like count, with engagement rate beneath it. One viral outlier cannot drag a median the way it drags an average.",
 'medc': 'Median comments per post. Far harder to buy than a like.',
 'lv': 'Likes as a percentage of plays on video, the median across the window. Plays are the denominator because Instagram reports views unreliably. An account with no video in the window shows no video, not zero.',
 'peak': "The biggest reel's plays in the window divided by followers. Under 10x is normal organic range, 10 to 50x suggests a push, above 50x is the media buy band. An account with no video shows no video.",
 'flag': 'BOOST and PUSH come from plays far beyond the follower base, LOW CADENCE from too few posts to measure. The flag reads reach on the firm’s own handle; verified ad library counts sit beneath it as a separate fact.',
 'top': 'The best performing post of the window by likes, linked to the live source.',
 'cl': 'Comments as a percentage of likes. A comment costs effort, so this ratio resists buying. Healthy range in this category runs 1.5 to 5 percent. Above 5, check who is commenting.',
}


def tip(key, label, extra=''):
    return f'<span class="tip d{extra}" tabindex="0" data-tip="{E(TIP[key])}">{label}</span>'


def ads_total(b):
    return sum(p['count'] for p in ADS[b]['pages'] if p['audience'] == 'investor')


def ads_sub(b):
    n = ads_total(b)
    plus = '+' if any(p.get('capped') for p in ADS[b]['pages']) else ''
    return f'{n}{plus} live Meta ads' if n else 'no live ads found'


# ---------------------------------------------------------------- derived figures
ELIG = [b for b in ORDER if M[b]['n'] >= 5]
CAT_ER = st.median(M[b]['er'] for b in ELIG)
theme_rows = defaultdict(list)
for r in LOG:
    theme_rows[r[3]].append(r[5])
THEMES = sorted(((t, len(v), st.median(v)) for t, v in theme_rows.items() if len(v) >= 2),
                key=lambda x: (-x[2], -x[1]))
SINGLE_THEMES = [t for t, v in theme_rows.items() if len(v) < 2]
fmt_rows = defaultdict(list)
for r in LOG:
    fmt_rows[r[2]].append(r[5])
FMTS = {f: (len(v), st.median(v)) for f, v in fmt_rows.items()}
QPOSTS = [r for r in LOG if r[4].rstrip().endswith('?') or '?' in r[4]]
Q_COMMENTS = sum(r[6] for r in QPOSTS)
Q_BRANDS = Counter(r[0] for r in QPOSTS)
COHORT = defaultdict(list)
for b in ELIG:
    COHORT[data.IG_BRANDS[b]['cohort']].append(b)
MCG = 'McGillivray Capital'
MCG_TOP = top_post(MCG)
MCG_REST = sorted(r[5] for r in POSTS[MCG] if r[8] != MCG_TOP[8])
FOUNDER = INP['founder_collab']
LANKIN_C = sorted(r[6] for r in POSTS['Lankin'])

out = []
w = out.append

# ---------------------------------------------------------------- header
w(f'''
<div class="wrap">
<header><p class="kicker">The HMM Index · Real estate · Instance 01 · Instagram</p><h1>The Real Estate Index, Instagram</h1><p class="lede">Competitive intelligence for <b>Canadian private real estate investment</b> on Instagram. <b>Five firms with a corporate Instagram account</b>, <b>{N} company posts</b> analysed across the 30 days to <b>{INP['window_label_end']}</b>, read from public data on the day of collection.</p>
<div class="byline"><span>Published by <b>Ankit Kumar, HMM, helpmemarketing.com</b></span><span>For business owners and marketing leads who want to see what their category is doing on Instagram.</span></div></header>
<div class="livebar"><span>Last verified data <b>{{{{LAST_VERIFIED}}}}</b></span><span>Next scheduled refresh <b>{{{{NEXT_REFRESH}}}}</b>{{{{OVERDUE}}}}</span><span>Cycle <b>{{{{CYCLE}}}}</b></span></div>
''')

# ---------------------------------------------------------------- overview
firms_with_ads = [b for b in ORDER if ads_total(b)]
organic_flags = [b for b in ORDER if M[b]['flag'] == 'ORGANIC']
w(f'''<section id="ri-overview"><div class="sec-head"><h2>Three findings from this cycle</h2>
<p class="dek">What a typical reader needs first. These describe the 30 days to {INP['window_label_end']} only; they don’t show cause and effect or predict future results.</p></div>
<div class="tiles">
<div class="tile"><div class="k">Posts reviewed</div><div class="v">{N}</div><div class="d">company posts in the 30-day window</div></div>
<div class="tile"><div class="k">Comments recorded</div><div class="v">{TOTAL_COMMENTS}</div><div class="d">across the whole category</div></div>
<div class="tile"><div class="k">Firms with live Meta ads</div><div class="v">{len(firms_with_ads)} of {len(ORDER)}</div><div class="d">verified in the Meta ad library</div></div>
</div>
<div class="card"><p class="dek"><b>1.</b> All {len(firms_with_ads)} firms had investor-facing ads live in the Meta ad library on the day of collection, while {len(organic_flags)} of the {len(ORDER)} scoreboard flags read ORGANIC. The flag reads reach on each firm’s own handle; it cannot see spend, so the two facts are published side by side.</p>
<p class="dek"><b>2.</b> One founder co-authored reel drew {num(MCG_TOP[5])} likes and {num(MCG_TOP[7])} plays on a {num(M[MCG]['followers'])}-follower account. The account’s other posts in the window drew {", ".join(str(x) for x in MCG_REST)} likes. One post, so this is a lead to test, not a rule.</p>
<p class="dek m0"><b>3.</b> Comments rose to {TOTAL_COMMENTS}, from 17 in cycle 003, but {COMMENTS['Lankin'] + MCG_TOP[6]} of them sit on one account’s steady {LANKIN_C[0]} to {LANKIN_C[-1]} comments per post and on that single reel. Ranks still rest on a thin signal.</p></div></section>
''')

w('''<div class="metrics-note"><b>New to these metrics?</b> Every dotted term on this page, like <span class="tip" tabindex="0" data-tip="The middle value when you line all posts up. One viral post drags an average up. The median is the typical post.">median</span>, <span class="tip" tabindex="0" data-tip="Median likes divided by followers, with the follower count frozen at collection. What a typical post earns relative to the audience that already opted in.">engagement rate</span>, <span class="tip" tabindex="0" data-tip="Comments as a percentage of likes. A comment costs effort, so this ratio resists buying. Healthy range in this category runs 1.5 to 5 percent. Above 5, check who is commenting.">comment:like ratio</span>, <span class="tip" tabindex="0" data-tip="Likes as a percentage of plays on video. Plays are used as the denominator because Instagram reports views unreliably.">like/play</span>, <span class="tip" tabindex="0" data-tip="The biggest reel’s plays divided by followers. Under 10x is normal organic range. 10 to 50x suggests a push. Above 50x is the media buy band.">peak plays / followers</span>, <span class="tip" tabindex="0" data-tip="A 0 to 100 blend of three pillars: Resonance at 45 percent, Intent at 30, and Distribution honesty at 25.">Index Score</span> or <span class="tip" tabindex="0" data-tip="A firm needs at least 5 posts in the window to enter pooled medians. Low cadence firms are quarantined and their score is capped.">cadence floor</span>, explains itself when you hover, or tap on mobile. Every claim links to the actual post it came from.</div>
''')

# ---------------------------------------------------------------- scoreboard
pier, top1 = RANKED[0], RANKED[0]
w(f'''<section id="ri-rankings"><div class="sec-head"><h2>The scoreboard</h2>
<p class="dek">Five accounts ranked by <b>Instagram Index Score</b>, with movement against the published cycle {CFG['prior_cycle']} scoreboard.
Resonance uses engagement rate, Intent uses comment to like, and Distribution honesty uses peak plays divided by followers where <b>lower is better</b>.</p>
<p class="pnote">This is an HMM-built index of public engagement, not an official Instagram ranking, and not a measure of leads, customers or revenue. With {TOTAL_COMMENTS} comments across the category, most of them on two accounts, small differences can move ranks.</p></div>
<div class="tw"><table><thead><tr><th>Account</th><th class="r">{tip('score','Score')}</th><th class="r">{tip('foll','Followers')}</th><th class="r">{tip('posts','Posts')}</th>
<th class="r">{tip('mix','Mix')}</th><th class="r">{tip('medl','Median likes')}</th><th class="r">{tip('medc','Med comm')}</th><th class="r">{tip('lv','Like/play',' dr')}</th>
<th class="r">{tip('peak','Peak',' dr')}</th><th class="r">{tip('flag','Flag',' dr')}</th><th class="r">{tip('top','Top post',' dr')}</th></tr></thead><tbody>''')
rows = []
for b in RANKED:
    m, meta, tp = M[b], data.IG_BRANDS[b], top_post(b)
    rows.append(f'''<tr>
<td class="brandcell"><a href="{meta['igurl']}" target="_blank" rel="noopener">{b}</a>
<span class="handle">@{meta['ig']}</span>
<div><span class="chip {meta['cohort']}">{meta['cohort']}</span></div></td>
<td class="r"><span class="score {score_cls(m['score'])}">{m['score']}</span><div class="cell-sub">{move(b)}</div></td>
<td class="r vanity">{num(m['followers'])}</td><td class="r">{m['n']}</td><td class="r">{mix(b)}</td>
<td class="r">{med(m['median_likes'])}<div class="cell-sub">{m['er']:.4f}% ER</div></td>
<td class="r">{med(m['median_comments'])}</td><td class="r">{lv_cell(m)}</td><td class="r">{peak_cell(m)}</td>
<td class="r"><span class="flag {flag_cls(m['flag'])}">{m['flag']}</span><div class="cell-sub">{ads_sub(b)}</div></td>
<td class="r"><b>{num(tp[5])}</b><div class="cell-sub">{link(tp[8], 'open')}</div></td></tr>''')
w(''.join(rows) + '</tbody></table></div>\n')

p4 = M['Pier 4']
w(f'''<div class="note crit"><span class="lbl">Why the number one account published no video</span>
<p><b>Pier 4 moves to first with {p4['score']} on {p4['n']} posts and no reel in the window.</b> What we observed: its Distribution pillar
compares peak plays with followers, and with no video in the window there is no reach to measure, so under the published method it
sits at the honest end of that pillar. Its Intent score comes from {COMMENTS['Pier 4']} comments on {sum(r[5] for r in POSTS['Pier 4'])} likes,
a ratio of {p4['cl']:.2f} percent. What it may suggest: the lead over {RANKED[1]} rests on how an absence of video is scored as much as on what Pier 4 posted.
What to test: whether the order holds next cycle if Pier 4 publishes a reel.</p>
<p>The scoring method has not changed since cycle 003, and the same treatment applied to Lankin when it published no video in cycle 003.
We are publishing the sensitivity rather than adjusting the method mid-series.</p></div>
<div class="note crit"><span class="lbl">Read this before you read the rest of the ranks</span>
<p><b>{TOTAL_COMMENTS} comments across {N} posts in thirty days</b>, and Intent is 30 percent of the score. {COMMENTS['Lankin']} belong to Lankin,
{COMMENTS[MCG]} to McGillivray Capital ({MCG_TOP[6]} of them on one reel), {COMMENTS['Pier 4']} to Pier 4, {COMMENTS['Equiton']} to Equiton.
<b>Skyline recorded {COMMENTS['Skyline'] or 'none'}</b> while posting the {['','highest','second highest','third highest'][sorted(ELIG,key=lambda b:-M[b]['er']).index('Skyline')+1]} engagement rate on the board.</p>
<p>Lankin’s comments arrived at {LANKIN_C[0]} to {LANKIN_C[-1]} per post on posts with a median of {med(M['Lankin']['median_likes'])} likes, a comment to like ratio of
{M['Lankin']['cl']:.1f} percent. Above 5 percent the Intent band decays, so that volume lifts Lankin less than it seems. Public data does not show who
the commenters are, so we report the pattern without characterising it. <b>Treat the ranks as a reading of a thin signal.</b></p>
<p>Movement is read against the published cycle {CFG['prior_cycle']} scoreboard. That scoreboard listed the same scores as cycle 003 and its raw
posts were not available to recalculate, so the movement column compares against published ranks rather than a verified recalculation.</p></div></section>
''')

# ---------------------------------------------------------------- top of board
sk, eq, lk = M['Skyline'], M['Equiton'], M['Lankin']
def card(h4, h3, body):
    return f'<div class="card"><h4>{h4}</h4><h3>{h3}</h3>\n<p class="dek m0">{body}</p></div>\n'
rk = {b: M[b]['rank'] for b in ORDER}
ORD = ['', 'number one', 'number two', 'number three', 'number four', 'number five']
w(f'''<section><details class="ri-adv"><summary>What the top of the board is doing</summary>
<div class="sec-head"><h2>What the top of the board is actually doing</h2>
<p class="dek">Read from all {N} captions and the creative itself. Language and artifacts, not just counting.</p></div>
<div class="grid2">
''')
w(card(f"Pier 4, {ORD[rk['Pier 4']]}", 'Events, people and market notes, no reel',
       f"{p4['n']} posts: a Q3 events recap with the whole team in frame ({top_post('Pier 4')[5]} likes, its best), an employee award, a run for a cause, "
       f"a Top Growing Companies mention, a Halifax disposition and a steady line of market carousels. Median {med(p4['median_likes'])} likes on {num(p4['followers'])} followers. "
       f"The account also had {ads_total('Pier 4')} investor ads live from its own page, many placed on Instagram only, which do not appear in its organic numbers."))
w(card(f"McGillivray Capital, {ORD[rk[MCG]]}", 'One founder reel, four quiet posts',
       f"{M[MCG]['n']} posts, exactly the cadence floor. The founder co-authored reel took {num(MCG_TOP[5])} likes and {num(MCG_TOP[7])} plays; the other four took "
       f"{', '.join(str(x) for x in MCG_REST)}. Median {med(M[MCG]['median_likes'])} likes. That reel carries the BOOST flag and costs the account the Distribution pillar, "
       f"and its engagement rate and comment ratio still hold second place. Read the boost ledger before reading the flag."))
w(card(f"Skyline, {ORD[rk['Skyline']]}", 'Highest median likes, no comments',
       f"{sk['n']} posts and a median of {med(sk['median_likes'])} likes on {num(sk['followers'])} followers, {sk['er']:.3f} percent. Its best posts were community stories: "
       f"a charity golf classic ({top_post('Skyline')[5]} likes), a leadership conference visit and a National Tree Day post. "
       f"Not one post drew a comment, which zeroes 30 percent of the score. Its construction and leasing updates remain the bulk of the calendar."))
w(card(f"Equiton, {ORD[rk['Equiton']]}", 'The largest audience and the lowest rate',
       f"{eq['n']} posts to {num(eq['followers'])} followers, a median of {med(eq['median_likes'])} likes ({eq['er']:.3f} percent) and {COMMENTS['Equiton']} comment. "
       f"Its best post is a lifestyle reel on not having to fix the dishwasher ({top_post('Equiton')[5]} likes). Equiton also had at least {ads_total('Equiton')} ads live, "
       f"the most in the index; paid delivery does not show in organic like counts."))
w('''</div>
<div class="note"><span class="lbl">Your takeaway, any category</span>
<p>When a ranking moves, find the pillar with the smallest denominator and check it first. This cycle that is comments again, and the
treatment of an account with no video. A scoreboard is only as stable as its scarcest input.</p></div></details></section>
''')

# ---------------------------------------------------------------- vision pass
FR = INP['frames']
w(f'''<section id="ri-creative"><div class="sec-head"><h2>The vision pass</h2>
<p class="dek">Everything above came from text and metrics. Here is the opening frame of each firm’s top post of the window, one per ranked firm,
read this cycle. Badges compare that post’s likes with the account’s own median for the window, nothing else.</p></div>
<div class="frames">''')
for b in ORDER:
    tp, f = top_post(b), FR[b]
    cls, lab, ratio = verdict(tp[5], M[b]['median_likes'])
    w(f'''<div class="frame">
<div class="shot"><img src="/assets/index/real-estate/frames/{SLUG[b]}-cycle{CYC}.webp" alt="{E(f['alt'])}" loading="lazy">
<span class="verdict {cls}">{lab}</span>
<span class="badge"><span class="bn">{b}</span><span class="bl">{E(f['label'])}</span></span></div>
<div class="body"><p><b>In frame:</b> {f['in_frame']}</p><p>{f['read']}</p>
<div class="fmets"><span>likes<b>{num(tp[5])}</b></span><span>vs median<b>{ratio:.1f}x</b></span></div>
<a class="go" href="{url(tp[8])}" target="_blank" rel="noopener">Open the post</a></div></div>''')
w(f'''</div>
<div class="note"><span class="lbl">The pattern across five frames</span><p>{INP['frame_pattern']}</p></div></section>
''')

# ---------------------------------------------------------------- bands
def band_read_er():
    strong = [b for b in ELIG if M[b]['er'] > 0.35]
    normal = [b for b in ELIG if 0.06 <= M[b]['er'] <= 0.35]
    low = [b for b in ELIG if M[b]['er'] < 0.06]
    s = f"{', '.join(strong)} clear the strong band." if strong else 'No account clears the strong band.'
    if normal: s += f" {', '.join(normal)} sit in the normal band."
    if low: s += f" {', '.join(low)} sit below it."
    return s
w(f'''<section><div class="sec-head"><h2>What good looks like</h2>
<p class="dek">Provisional bands derived from cycles 001 to 003 of this category, not imported from consumer Instagram.</p></div>
<div class="band"><h4>Instagram engagement rate</h4>
<div class="bandbar"><span class="bl fx1">below 0.06%, trouble</span><span class="bm fx12">0.06 to 0.35%, normal</span><span class="bh fx1">above 0.35%, strong</span></div>
<p class="micro"><b>Read:</b> {band_read_er()} The three accounts in the strong band are the three smallest audiences on the board.</p></div>
<div class="band"><h4>Comment to like ratio</h4>
<div class="bandbar"><span class="bl fx1">below 1.5%, passive</span><span class="bm fx14">1.5 to 5%, healthy</span><span class="bh fx1">above 5%, check the audience</span></div>
<p class="micro"><b>Read:</b> McGillivray Capital at {M[MCG]['cl']:.2f} percent is the only account inside the healthy band. Pier 4 at {p4['cl']:.2f} and Lankin at {lk['cl']:.1f} sit above it; Equiton at {eq['cl']:.2f} and Skyline at {sk['cl']:.2f} sit below it.</p></div>
<div class="band"><h4>Peak plays divided by followers</h4>
<div class="bandbar"><span class="bl fx1">below 10x, organic range</span><span class="bm fx12">10 to 50x, likely pushed</span><span class="bh fx1">above 50x, media buy band</span></div>
<p class="micro"><b>Read:</b> three of the four accounts with video sit under half their follower count. The exception is McGillivray Capital at {M[MCG]['peak']:.1f}x, from a reel co-authored with a founder account of {num(FOUNDER['followers'])} followers; against the combined audience that reel is {FOUNDER['plays_vs_combined']:.2f}x. Pier 4 published no video.</p></div>
<div class="note"><span class="lbl">Your takeaway, any category</span>
<p>Benchmarks are category and size specific, but these three bands work everywhere. Compute them for your market once and every competitor number you see afterwards has context.</p></div></section>
''')

# ---------------------------------------------------------------- themes
top_m = THEMES[0][2]
trs = ''.join(f'<tr><td><b>{E(t)}</b></td><td class="r">{n}</td><td class="r"><b>{med(m)}</b></td><td class="w-26"><span class="tbar" data-w="{round(m / top_m * 100)}"></span></td><td class="wrap-cell">{E(INP["theme_reads"].get(t, ""))}</td></tr>' for t, n, m in THEMES)
single = f" {', '.join(SINGLE_THEMES)} had a single post and is left out of the table." if SINGLE_THEMES else ''
w(f'''<section id="ri-insights"><div class="sec-head"><h2>Which content themes received more engagement in this sample</h2>
<p class="dek">Median likes by caption-read theme across all {N} in-window posts.{single} Likes are not adjusted for follower count or posting frequency, and some themes have few posts, so treat this as ideas to test, not proof.</p></div>
<div class="tw"><table>
<thead><tr><th>Theme</th><th class="r">Posts</th><th class="r">Median likes</th><th>Relative pull</th><th>The read</th></tr></thead>
<tbody>{trs}</tbody></table></div>
<div class="note crit"><span class="lbl">The theme pattern, read with its exceptions</span>
<p>{INP['theme_note']}</p>
<p><b>Question-led captions:</b> {len(QPOSTS)} of {N} posts carry a question in the first line ({', '.join(f'{v} from {k}' for k, v in Q_BRANDS.most_common())}). Together they drew {Q_COMMENTS} comments, {sum(r[6] for r in QPOSTS if r[0]=='Lankin')} of them on Lankin posts, where comments arrived at a similar rate whether or not the caption asked a question.</p></div>
<div class="note"><span class="lbl">Your takeaway, any category</span>
<p>Count your own last 30 posts by theme, then look at where engagement actually came from. Many brands find most of their calendar sits in their weakest theme.</p></div></section>
''')

# ---------------------------------------------------------------- format
fm = ''.join(f'<div class="fmt"><span class="fk">{f}</span><div class="fv">{med(FMTS[f][1])}</div><span class="fn">{FMTS[f][0]} posts, median likes</span></div>' for f in ('Reel', 'Carousel', 'Static') if f in FMTS)
w(f'''<section><div class="sec-head"><h2>Format</h2>
<p class="dek">Median likes by format across the ranked board.</p></div>
<div class="fmts">{fm}</div>
<div class="note warn"><span class="lbl">The finding, held loosely</span>
<p>{INP['format_note']}</p></div></section>
''')

# ---------------------------------------------------------------- tests
tr = ''.join(f'<tr><td>{E(a)}</td><td>{E(b)}</td></tr>' for a, b in INP['tests'])
w(f'''<section id="ri-test"><div class="sec-head"><h2>What could be tested next</h2>
<p class="dek">Proposed experiments based on this cycle’s observations, not promises of better results.</p></div>
<div class="tw"><table><thead><tr><th>Observation</th><th>Possible test</th></tr></thead><tbody>
{tr}
</tbody></table></div></section>

<section id="ri-advanced"><div class="sec-head"><h2>Advanced research and methodology</h2>
<p class="dek">The full analysis behind the findings. Open any section to read it.</p></div></section>
''')

# ---------------------------------------------------------------- roster and baseline
w(f'''<section><details class="ri-adv"><summary>Roster, comparison basis and a correction</summary>
<div class="note warn mt0"><span class="lbl">What changed and what did not</span>
<p><b>The roster is unchanged since cycle 003:</b> Skyline, Equiton, Lankin, Pier 4 and McGillivray Capital. Marlin Spring left this board at
cycle 003 after three consecutive windows at two posts. Because Resonance and Distribution are <b>percentile</b> pillars, any future roster change
re-ranks every firm, and this page will say so when it happens.</p>
<p><b>Comparison basis.</b> The cycle {CFG['prior_cycle']} scoreboard published on 5 October listed the same scores and ranks as cycle 003. Its raw posts
could not be recovered to recalculate it, so the movement column on this page compares against those published ranks. The scoring code was
re-run against the cycle 003 posts and reproduced all five published cycle 003 scores exactly before this cycle’s numbers were used.</p>
<p><b>Correction.</b> Cycle 003 said McGillivray Capital’s ads were the only documented live paid social in this index. This cycle’s wider search of
the Meta ad library found active ads for all five firms, and several began before the cycle 003 window closed: Equiton’s earliest live ad dates
from {ADS['Equiton']['first']}, Pier 4’s from {ADS['Pier 4']['first']} and Lankin’s from {ADS['Lankin']['first']}. The earlier statement was incomplete.</p></div></details></section>
''')

# ---------------------------------------------------------------- pulse
w(f'''<section><details class="ri-adv"><summary>Category pulse</summary>
<div class="sec-head"><h2>Category pulse</h2></div>
<div class="tiles">
<div class="tile"><div class="k">Category median ER</div><div class="v">{CAT_ER:.3f}%</div><div class="d">pooled across {len(ELIG)} accounts at or above the cadence floor</div></div>
<div class="tile"><div class="k">Number one</div><div class="v">{RANKED[0]}</div><div class="d">Score {M[RANKED[0]]['score']}, {move(RANKED[0])}</div></div>
<div class="tile"><div class="k">Comments, whole category</div><div class="v">{TOTAL_COMMENTS}</div><div class="d">across {N} posts and five firms, in thirty days</div></div>
<div class="tile"><div class="k">Boost signals</div><div class="v">{sum(1 for b in ORDER if M[b]['flag'].startswith(('BOOST','PUSH')))}</div><div class="d">plays far beyond the follower base, on one co-authored reel</div></div>
<div class="tile"><div class="k">Live investor ads</div><div class="v">{sum(ads_total(b) for b in ORDER)}+</div><div class="d">across all five firms, a minimum count</div></div>
</div></details></section>
''')

# ---------------------------------------------------------------- category story
w(f'''<section><details class="ri-adv"><summary>The category story</summary>
<div class="sec-head"><h2>The category story</h2>
<p class="dek">A paid category with a quiet feed.</p></div>
<div class="card"><h4>The narrative finding of cycle {CYC}</h4>
<p class="dek">{INP['story'][0]}</p>
<p class="dek">{INP['story'][1]}</p>
<p class="dek m0">{INP['story'][2]}</p></div>
<div class="note"><span class="lbl">Your takeaway, any category</span>
<p>Read a competitor’s feed and its ad library together. The feed shows what an audience chose to engage with; the ad library shows what the firm chose to pay for. Either alone misleads.</p></div></details></section>
''')

# ---------------------------------------------------------------- cautionary tale
eqq = [r for r in POSTS['Equiton'] if r[3] == 'Market / macro']
w(f'''<section><details class="ri-adv"><summary>High posting, low visible engagement</summary>
<div class="sec-head"><h2>High posting, low visible engagement</h2>
<p class="dek">The largest audience on the board and the lowest engagement rate this cycle.</p></div>
<div class="card"><h4>Equiton, {num(eq['followers'])} followers, {eq['n']} posts, {med(eq['median_likes'])} median likes</h4>
<p class="dek">Equiton published {eq['n']} times in thirty days, {Counter(r[2] for r in POSTS['Equiton'])['Reel']} of them reels, to the largest audience in the index, and drew
{COMMENTS['Equiton']} comment. Its engagement rate of {eq['er']:.3f} percent is the lowest on the board. Its {len(eqq)} market round ups drew a median of
{med(st.median(r[5] for r in eqq))} likes.</p>
<p class="dek">At the same time it had at least {ads_total('Equiton')} ads live in the Meta ad library, some running since {ADS['Equiton']['first']}, including an
investor evening that began advertising on {ADS['Equiton']['event_start']}. What we observed: heavy paid activity alongside the quietest organic feed per follower.
What it may suggest: the organic feed is not where this firm is trying to win attention. What to test: whether organic posts that echo a live ad’s
message draw more than the round ups do.</p>
<p class="dek m0">Its best organic post this cycle was a lifestyle reel about not having to deal with a broken dishwasher, {top_post('Equiton')[5]} likes, about twice its median.</p></div>
<div class="note"><span class="lbl">Your takeaway, any category</span>
<p>Posting volume and ad spend are inputs. Engagement per follower is the output. When inputs rise and the output does not move, the content is the place to look first.</p></div></details></section>
''')

# ---------------------------------------------------------------- positioning map
X0, X1, Y0, Y1 = 70, 730, 30, 372
LMIN, LMAX = math.log10(0.02), math.log10(100)
def px(p):
    return X0 + (math.log10(max(p, 0.02)) - LMIN) / (LMAX - LMIN) * (X1 - X0)
def py(lv):
    return Y1 - min(lv, 6) / 6 * (Y1 - Y0)
COL = {'Skyline': '#00D4AA', 'Equiton': '#999999', 'Lankin': '#E36B6B', 'Pier 4': '#E0A12C', MCG: '#7B8FF7'}
svg = [f'<svg class="fluid" viewbox="0 0 760 430" role="img" aria-label="Paid push versus resonance">',
       f'<line x1="{px(10):.1f}" x2="{px(10):.1f}" y1="{Y0}" y2="{Y1}" stroke="rgba(255,255,255,.14)" stroke-dasharray="4 5"></line>',
       f'<line x1="{X0}" x2="{X1}" y1="{py(3):.1f}" y2="{py(3):.1f}" stroke="rgba(255,255,255,.14)" stroke-dasharray="4 5"></line>',
       '<text x="78" y="46" fill="#999999" font-size="10.5" font-weight="600" font-family="system-ui" letter-spacing=".08em">EARNED AND LANDING</text>',
       '<text x="722" y="46" fill="#00D4AA" text-anchor="end" font-size="10.5" font-weight="600" font-family="system-ui" letter-spacing=".08em">BIG REACH + HIGH RESONANCE</text>',
       '<text x="78" y="364" fill="#737373" font-size="10.5" font-weight="600" font-family="system-ui" letter-spacing=".08em">QUIET</text>',
       '<text x="722" y="364" fill="#737373" text-anchor="end" font-size="10.5" font-weight="600" font-family="system-ui" letter-spacing=".08em">BIG REACH, LOW RESPONSE</text>',
       f'<line x1="{X0}" x2="{X1}" y1="{Y1}" y2="{Y1}" stroke="rgba(255,255,255,.25)"></line>',
       f'<line x1="{X0}" x2="{X0}" y1="{Y0}" y2="{Y1}" stroke="rgba(255,255,255,.25)"></line>']
for b in ORDER:
    m = M[b]
    if not m['has_video']:
        continue
    x, y = px(m['peak']), py(m['lv'])
    r = 8 + 2.6 * (math.log10(m['followers']) - 2.5)
    nm = 'McGillivray' if b == MCG else b
    anchor = 'end' if x > 640 else 'middle'
    tx = x - r - 4 if anchor == 'end' else x
    ty = y + 4 if anchor == 'end' else y - r - 6
    svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="none" stroke="{COL[b]}" stroke-width="2.5"><title>{b}: peak {m["peak"]:.2f}x, median like per play {m["lv"]:.2f} percent</title></circle>')
    svg.append(f'<text x="{tx:.1f}" y="{ty:.1f}" fill="#FFFFFF" text-anchor="{anchor}" font-size="12" font-weight="650" font-family="system-ui">{nm}</text>')
novid = [b for b in ORDER if not M[b]['has_video']]
if novid:
    svg.append(f'<text x="722" y="348" fill="#737373" text-anchor="end" font-size="10.5" font-family="system-ui">{" and ".join(novid)} published no video, so cannot be plotted</text>')
svg.append('<text x="400" y="420" fill="#999999" text-anchor="middle" font-size="12" font-family="system-ui">PAID PUSH: peak plays / followers, log scale</text>')
svg.append('<text x="16" y="201" fill="#999999" text-anchor="middle" font-size="12" font-family="system-ui" transform="rotate(-90 16 201)">RESONANCE: median like / play</text></svg>')
w(f'''<section><details class="ri-adv"><summary>The creative positioning map</summary>
<div class="sec-head"><h2>The creative positioning map</h2>
<p class="dek">Every axis is a measured number. <b>X, reach beyond the base:</b> peak plays divided by followers, log scale. <b>Y, resonance:</b> median like per play.
Plays are the denominator throughout. The dashed vertical line marks 10x. Hover any circle.</p></div>
<div class="card navy">{''.join(svg)}</div>
<div class="note warn"><span class="lbl">What changed on this chart</span>
<p>{INP['map_note']}</p></div>
<div class="note"><span class="lbl">Your takeaway, any category</span>
<p>Plot your market on these two axes. Plays that run far beyond the follower base are worth a second look in the ad library and in any co-authored posts before you read it as earned.</p></div></details></section>
''')

# ---------------------------------------------------------------- boost ledger
lr = []
for b in RANKED:
    m = M[b]
    p30 = 'no video' if not m['has_video'] else f"{m['peak']:.2f}x"
    p9 = peak90(b)
    p9s = 'no video' if p9 is None else f'{p9:.2f}x'
    lr.append(f'<tr><td class="brandcell">{b}</td><td class="r">{p30}<div class="cell-sub">30 day</div></td><td class="r">{p9s}<div class="cell-sub">90 day</div></td>'
              f'<td class="r">{m["cl"]:.2f}%</td><td class="wrap-cell">{INP["ledger"][b]}</td><td class="r"><span class="flag {flag_cls(m["flag"])}">{m["flag"]}</span><div class="cell-sub">{ads_sub(b)}</div></td></tr>')
w(f'''<section><details class="ri-adv"><summary>The boost ledger</summary>
<div class="sec-head"><h2>The boost ledger</h2>
<p class="dek">Ratios that resist buying, read together, with the 30 day peak set against the 90 day peak, and the ad library count beside each flag.
Directional flags from public data, never spend receipts.</p></div>
<div class="tw"><table><thead><tr><th>Account</th><th class="r">{tip('peak','Peak / foll')}</th><th class="r">90 day peak</th><th class="r">{tip('cl','Comment:like')}</th><th>The read</th><th class="r">{tip('flag','Flag',' dr')}</th></tr></thead><tbody>{''.join(lr)}</tbody></table></div>
<div class="note warn"><span class="lbl">What this ledger can and cannot see</span>
<p>{INP['ledger_note']}</p></div></details></section>
''')

# ---------------------------------------------------------------- campaign watch
cw = ''.join(f'<tr><td class="brandcell">{b}</td><td>{E(sig)}</td>\n<td class="wrap-cell">{what}</td>\n<td class="r">{dens}</td><td class="r"><span class="flag {fc}">{st_}</span></td></tr>\n'
             for b, sig, what, dens, fc, st_ in INP['campaigns'])
w(f'''<section><details class="ri-adv"><summary>Campaign watch</summary>
<div class="sec-head"><h2>Campaign watch</h2>
<p class="dek">What is running, read from recurring language and formats across {N} captions, plus active ads in the Meta ad library on the day of collection.
Each organic row links to a live example.</p></div>
<div class="tw"><table>
<thead><tr><th>Account</th><th>Signal</th><th>What it is</th><th class="r">Density</th><th class="r">Status</th></tr></thead>
<tbody>
{cw}</tbody></table></div>
<div class="note"><span class="lbl">How the ad counts were taken</span>
<p>Active ads in Canada were searched by exact phrase for each firm’s name and its known founder advertiser, then grouped by the advertiser page that placed them.
Counts are minimums: a keyword search misses ads that never name the firm, and one search returned its maximum of 25 results. Resident leasing pages
are listed separately from investor-facing pages. The library shows that an ad is live; it does not show budget, reach or results.</p></div>
<div class="note"><span class="lbl">Your takeaway, any category</span>
<p>A competitor’s campaign calendar is reconstructable from public posts. The ad library adds the half you cannot see in the feed.</p></div></details></section>
''')

# ---------------------------------------------------------------- cohort
def coh_er(c):
    return st.median(M[b]['er'] for b in COHORT[c])
w(f'''<section><details class="ri-adv"><summary>The cohort read</summary>
<div class="sec-head"><h2>The cohort read</h2>
<p class="dek">Pooled median engagement rate per cohort, low cadence accounts excluded before pooling.</p></div>
<div class="grid3">
<div class="card coh-card"><h4>Mid market fund</h4>
<div class="bigno">{coh_er('MID'):.3f}%</div><p class="micro">pooled median engagement rate</p>
<p class="members">{', '.join(COHORT['MID'])}</p>
<p class="dek m0">The widest spread still sits inside one cohort: Skyline at {sk['er']:.3f}, Lankin at {lk['er']:.3f}, Equiton at {eq['er']:.3f}. Same cohort, same platform,
roughly a {sk['er']/eq['er']:.0f} times gap from top to bottom.</p></div>
<div class="card coh-card"><h4>Emerging and boutique</h4>
<div class="bigno">{coh_er('BOUTIQUE'):.3f}%</div><p class="micro">pooled median engagement rate</p>
<p class="members">{', '.join(COHORT['BOUTIQUE'])}</p>
<p class="dek m0">Both boutiques sit above two of the three mid market funds on engagement rate, on {num(p4['followers'])} and {num(M[MCG]['followers'])} followers. Skyline is the exception, ahead of Pier 4.</p></div>
<div class="card coh-card"><h4>Roster</h4>
<div class="bigno">5</div><p class="micro">ranked firms, unchanged since cycle 003</p>
<p class="members">Marlin Spring left at cycle 003</p>
<p class="dek m0">Marlin Spring left this board after three consecutive windows at two posts. Stated here rather than quietly dropped, because an index that changes its constituents without saying so is not worth citing.</p></div></div>
<div class="note"><span class="lbl">Your takeaway, any category</span>
<p>Never pool one median across a whole category. A number that mixes an {num(eq['followers'])} follower account with a {num(M[MCG]['followers'])} follower boutique describes nobody.</p></div></details></section>
''')

# ---------------------------------------------------------------- reference
w(f'''<section><details class="ri-adv"><summary>Outside the category, for scale</summary>
<div class="sec-head"><h2>Outside the category, for scale</h2>
<p class="dek">One account that is <b>not a real estate firm</b>, shown for comparison only. <b>Wealthsimple is never pooled into any
median, percentile or score on this page</b> and does not appear on the scoreboard.</p></div>
<div class="grid2">
<div class="card"><h4>Wealthsimple, reference only</h4><h3>Same country, same investor audience, different scale</h3>
<p class="dek m0">{num(REF['foll'])} followers, {REF['n']} posts in the same thirty day window, a median of
{med(REF['medL'])} likes and <b>a median of {med(REF['medC'])} comments</b>. Its best post of the window took {num(REF['top'])} likes. Format mix {REF['mix']}.</p></div>
<div class="card"><h4>The number that matters</h4><h3>{REF['sumC']} against {TOTAL_COMMENTS}</h3>
<p class="dek m0">Wealthsimple drew <b>{REF['sumC']} comments on {REF['n']} posts</b>. The five ranked real estate firms drew <b>{TOTAL_COMMENTS} comments on {N} posts</b>
in the same window. Its engagement rate, {REF['er']:.3f} percent, is lower than {sum(1 for b in ELIG if M[b]['er'] > REF['er'])} of the five firms on the board, so the gap is
in conversation rather than in rate.</p></div></div>
<div class="note crit"><span class="lbl">Why this is a reference and not a competitor</span>
<p><b>Comparing a fintech to a private REIT on a single score would be misleading</b>, so this page does not do it. Different category, different audience.
Its comment to like ratio of {REF['cl']:.2f} percent sits inside the healthy band. The only comparison worth drawing is that the ceiling for investor
conversation on this platform in Canada is higher than this category reaches.</p></div></details></section>
''')

# ---------------------------------------------------------------- post log
tabs = ''.join(f'<button class="logtab" data-b="{E(b)}">{E(b)}</button>' for b in RANKED)
body_rows = []
for r in sorted(LOG, key=lambda r: (r[0], r[1])):
    body_rows.append(f'<tr data-brand="{E(r[0])}"><td class="brandcell">{E(r[0])}</td><td class="r">{r[1]}</td><td><span class="chip">{r[2]}</span></td>'
                     f'<td class="wrap-cell em">"{E(r[4])}"</td><td class="r">{r[5]}</td><td class="r">{r[6]}</td><td class="r">{r[7]}</td><td class="r">{link(r[8])}</td></tr>')
w(f'''<section id="ri-data"><div class="sec-head"><h2>The full post log</h2>
<p class="dek">All {N} in-window posts from the five ranked firms, every metric, every link. Pick an account to filter. Hooks are
the caption’s first line, verbatim, with dashes normalised to commas or to the word "to" between numbers. The downloadable
CSV additionally carries the {{{{REFERENCE_ROWS}}}} Wealthsimple reference rows, tagged so they can never be pooled by mistake.</p></div>
<div class="logtabs"><button class="logtab active" data-b="All">All</button>{tabs}</div>
<div class="tw"><table id="postlog">
<thead><tr><th>Account</th><th class="r">Date</th><th>Format</th><th>Hook, first line</th>
<th class="r">Likes</th><th class="r">Comments</th><th class="r">Plays</th><th class="r">Link</th></tr></thead>
<tbody>{''.join(body_rows)}</tbody></table></div></section>
''')

# ---------------------------------------------------------------- gate (endpoint and payload copied from the current site body)
w('''<section><div class="sec-head"><h2>Take the dataset with you</h2>
<p class="dek">The complete cycle {{CYCLE}} Instagram post log: {{CSV_ROWS}} rows, including {{RANKED_ROWS}} ranked-firm rows and {{REFERENCE_ROWS}} out-of-category reference rows. Each row links to its source post. Reference rows are excluded from rankings.</p></div>
<div class="gate"><h4>Free, gated by email</h4><h3>Get the full post log</h3>
<p class="dek">Drop your email and the CSV downloads instantly. You will also get each new cycle when it refreshes.</p>
<form class="gate-form" id="gateform">
<input type="email" id="gate-email" placeholder="you@company.com" autocomplete="email" required>
<button class="cta-btn" id="gate-btn" type="submit">Get the CSV</button></form>
<p class="gate-msg" id="gate-msg"></p>
<p class="gate-privacy">One list, no spam. Your email is used for index cycle updates only and never shared.</p></div>
<p class="pnote">Want a second opinion on your own marketing? Send your website and I’ll review the publicly visible parts and share what I’d improve first. <a href="/contact?intent=review#contact-form">Get my free marketing review</a>. It isn’t a full competitor study.</p></section>
''')
w(INP['gate_script'])

# ---------------------------------------------------------------- FAQ
faq = ''.join(f'<details><summary>{E(q)}</summary><p>{a}</p></details>\n' for q, a in INP['faq'])
w(f'''<section><div class="sec-head"><h2>Frequently asked</h2></div>
{faq}</section>

<script>
document.querySelectorAll('.logtab').forEach(function(btn){{
  btn.addEventListener('click', function(){{
    document.querySelectorAll('.logtab').forEach(function(b){{b.classList.remove('active')}});
    btn.classList.add('active');
    var want = btn.getAttribute('data-b');
    document.querySelectorAll('#postlog tbody tr').forEach(function(tr){{
      tr.style.display = (want==='All' || tr.getAttribute('data-brand')===want) ? '' : 'none';
    }});
  }});
}});
</script>
<footer>
<div class="about"><p><b>About this index.</b> The Real Estate Index is the first instance of <b>The HMM Index</b>,
a network of competitive intelligence dashboards built by HMM. It benchmarks Instagram engagement for
five Canadian private real estate investment firms with a corporate Instagram account, across mid market fund and emerging
boutique cohorts, using median based engagement rates, comment to like ratios, plays to follower analysis, active ad library entries
and frame level creative reads. It is built to be cited: public to read, refreshed in place at this URL,
with every claim linked to its source post. Methodology frameworks are published at
<a href="https://helpmemarketing.com" target="_blank" rel="noopener">helpmemarketing.com</a>.</p></div>
<div class="byline-block">
<p><b>The Real Estate Index</b> · an instance of <b>The HMM Index</b> by HMM · built and reviewed by
<b>Ankit Kumar</b>, Growth Architect and Founder, HMM ·
<a href="https://www.instagram.com/helpmemarketing1/" target="_blank" rel="noopener">@helpmemarketing1</a> ·
frameworks at <a href="https://helpmemarketing.com" target="_blank" rel="noopener">helpmemarketing.com</a></p>
<div class="socials">
<a href="https://www.instagram.com/helpmemarketing1/" target="_blank" rel="noopener">Instagram</a>
<a href="https://www.linkedin.com/company/helpmemarketing/" target="_blank" rel="noopener">LinkedIn</a>
<a href="https://www.facebook.com/helpmemarketing1" target="_blank" rel="noopener">Facebook</a></div>
<p>Last verified data <b>{{{{LAST_VERIFIED}}}}</b> · cycle <b>{{{{CYCLE}}}}</b> · Next scheduled refresh <b>{{{{NEXT_REFRESH}}}}</b>{{{{OVERDUE}}}}</p>
</div></footer></div>
''')

(BASE / 'report_body.html').write_text(''.join(out), encoding='utf-8')
print('report_body.html written', len(''.join(out)))
