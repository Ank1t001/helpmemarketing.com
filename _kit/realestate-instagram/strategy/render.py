#!/usr/bin/env python3
"""Render the five-firm strategy comparison (founder, 2026-11-02) into report_body.html.

Reads ads.json, organic.json and websites.json (this folder) and writes five blocks between their markers in
../report_body.html: the Website Messaging view, the Organic and Paid strategy comparisons, the per-firm
recommendations and the Overview note. Every figure is counted here from the records. Run it after the derive
scripts, then record the new body hash in body_review.json and run build_v2.py.

The five firms are the roster from edition 006 (Equiton, Skyline, Lankin, Greybrook Realty Partners, Centurion
Asset Management). The rest of the page describes edition 005's board until the 14 November refresh.
"""
import collections, json, os, re, statistics as st
from html import escape as _e

HERE = os.path.dirname(os.path.abspath(__file__))
BODY = os.path.join(os.path.dirname(HERE), 'report_body.html')
FIRMS = ['Equiton', 'Skyline', 'Lankin', 'Greybrook', 'Centurion']
NAMES = {'Equiton': 'Equiton', 'Skyline': 'Skyline', 'Lankin': 'Lankin Investments', 'Greybrook': 'Greybrook Realty Partners',
         'Centurion': 'Centurion Asset Management'}
DATE = '2 November 2026'
E = lambda s: _e(str(s), quote=True)


def load(n):
    with open(os.path.join(HERE, n), encoding='utf-8') as f:
        return json.load(f)


def pct(a, b):
    return '%d%%' % round(100 * a / b) if b else '0%'


def plural(n, one, many=None):
    return '%d %s' % (n, one if n == 1 else (many or one + 's'))


def website_view(w):
    """Website Messaging tab (founder, 2026-11-03): one glance table (offer, evidence, next step) and two visual examples.
    The per-firm detail, exact quotes, notices, dates and corrections are in Sources & evidence (website_sources)."""
    f = w['firms']
    rows = []
    for k in FIRMS:
        g = f[k].get('glance')
        if not f[k]['read'] or not g:
            rows.append('<tr><td class="brandcell">%s</td><td colspan="3" class="em">Website messaging unavailable in this review.</td></tr>' % E(NAMES[k]))
        else:
            rows.append('<tr><td class="brandcell">%s</td><td class="wrap-cell" data-label="How it presents the offer">%s</td><td class="wrap-cell" data-label="Evidence it shows">%s</td><td class="wrap-cell" data-label="Next step">%s</td></tr>'
                        % (E(NAMES[k]), E(g['offer']), E(g['evidence']), E(g['next'])))
    figs = ''.join('<figure class="ri-wfig"><img src="%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async">'
                   '<figcaption><b>%s &middot; %s</b>%s <span>%s page, %s.</span></figcaption></figure>'
                   % (x['src'], E(x['alt']), x['width'], x['height'], E(NAMES[x['firm']] if x['firm'] != 'Centurion' else 'Centurion'), E(x['title']),
                      E(x['caption']), 'Apartment REIT', x['captured']) for x in w['examples'])
    return ('<div class="ri-view" id="ri-view-website">\n<section id="ri-website"><div class="ri-ovhero"><div class="sec-head"><h2>Website messaging</h2></div>\n'
            '<p class="ri-ovlead">How each firm explains its <em>offer</em> and guides investors.</p></div>\n'
            '<h3 class="ri-wh">Messaging at a glance</h3>\n'
            '<div class="tw"><table class="ri-wtable"><thead><tr><th>Firm</th><th>How it presents the offer</th><th>Evidence it shows</th><th>Next step</th></tr></thead>'
            '<tbody>' + ''.join(rows) + '</tbody></table></div>\n'
            '<h3 class="ri-wh">Messaging in practice</h3>\n<div class="ri-wex">' + figs + '</div>\n'
            '<p class="pnote m0">Exact quotes, return wording, notices and collection dates are in <a href="#ri-web-sources">Sources &amp; evidence</a>. '
            'Figures are the firms&rsquo; own and were not verified.</p>'
            '</section>\n</div>\n')


def website_sources(w):
    """Sources & evidence: every firm's nine fields, collection notes, corrections and the unresolved Lankin comparison."""
    f = w['firms']
    rows = [('Headline message', 'headline'), ('Products named', 'products'), ('Return language', 'returns'),
            ('Minimum investment', 'minimum'), ('Who can invest', 'who'), ('Registered accounts', 'registered'),
            ('Main call to action', 'cta'), ('Proof points', 'proof'), ('Notices', 'notice')]
    cards = []
    for k in FIRMS:
        x = f[k]
        if not x['read']:
            cards.append('<article class="ri-wcard is-unread"><h3>%s</h3><p class="ri-wsite">%s</p><p class="ri-wnote">%s</p></article>'
                         % (E(NAMES[k]), E(x['site']), E(x['note'])))
            continue
        dl = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (E(t), E(x[key])) for t, key in rows if x.get(key))
        notes = ''.join('<p class="ri-wnote">%s</p>' % E(x[n]) for n in ('also', 'read_by') if x.get(n))
        cards.append('<article class="ri-wcard"><h3>%s</h3><p class="ri-wsite">%s</p><dl>%s</dl>%s</article>'
                     % (E(NAMES[k]), E(x['site']), dl, notes))
    ex = ' '.join('%s (%s, captured %s, SHA-256 %s&hellip;).' % (E(x['title']), E(x['page']), x['captured'], x['sha256'][:12]) for x in w['examples'])
    return ('<section id="ri-web-sources"><details class="ri-adv"><summary>Website Messaging: firm profiles, quotes and collection</summary>\n'
            '<p class="dek">Skyline, Lankin, Greybrook and Centurion were read with Chromium on ' + DATE + ' (' + E(w['captured_at'].split(', ')[1]) + '): '
            'the homepage and the main investor page. Page text is kept privately and recorded by hash in the kit. Equiton showed a bot check to that browser; '
            'it was read the same evening in the author&rsquo;s own browser. Quotes are short excerpts; figures are the firms&rsquo; own and were not verified.</p>\n'
            '<div class="ri-wgrid">' + ''.join(cards) + '</div>\n'
            '<p class="pnote"><b>Unresolved:</b> Lankin&rsquo;s ads read the same day cite a 12% to 16% targeted net return, while its homepage lists 10% to 14% '
            'for the Apartment REIT and 10% to 12% for the Growth LP. The ads may describe a different fund; this was not resolved.</p>\n' +
            '<p class="pnote"><b>Checks on 3 November 2026 (HMM Ranking matrix):</b> %s Other firms: %s</p>\n' % (
                ' '.join('%s: %s.' % (E(p), E(v)) for p, v in w['matrix_check_2']['equiton_pages'].items()).replace('/individual-investors/', 'Equiton /individual-investors/', 1),
                ' '.join('%s: %s.' % (E(k), E(v)) for k, v in w['matrix_check_2']['others'].items())) +
            '<p class="pnote m0"><b>Examples in Website Messaging:</b> ' + ex + '</p>\n'
            '</details></section>\n')


def organic_section(o):
    """Organic Social tab (founder, 2026-11-03): the glance table only; the detailed tables are in organic_sources."""
    posts = o['posts']
    glance = []
    words = {'Reel': ('reel', 'reels'), 'Carousel': ('carousel', 'carousels'), 'Static': ('image', 'images')}
    for k in FIRMS[:4]:
        p = [x for x in posts if x['firm'] == k]
        fm = collections.Counter(x['format'] for x in p).most_common()
        mixtxt = ', '.join('%d %s' % (n, words[f][n != 1]) for f, n in fm)
        nf = sum(x['names_fund'] for x in p)
        fund = ('%d of %d named a fund as the property owner.' % (nf, len(p))) if k == 'Skyline' else ('%d of %d posts named a fund or offering.' % (nf, len(p)))
        glance.append('<tr><td class="brandcell">%s</td><td class="wrap-cell" data-label="What it posts">%s</td><td class="wrap-cell" data-label="Creative mix">%s</td>'
                      '<td class="wrap-cell" data-label="How funds appear">%s</td></tr>' % (E(NAMES[k]), E(o['glance_posts'][k]), mixtxt, fund))
    return ('<section id="ri-organic-compare"><div class="ri-ovhero"><div class="sec-head"><h2>Social Media Strategy</h2></div>\n'
            '<p class="ri-ovlead">How four firms present themselves on <em>Instagram</em> and which posts drew the most likes.</p></div>\n'
            '<h3 class="ri-wh">Strategy at a glance</h3>\n'
            '<div class="tw"><table class="ri-wtable"><thead><tr><th>Firm</th><th>What it posts</th><th>Creative mix</th><th>How funds appear</th></tr></thead><tbody>'
            + ''.join(glance) + '</tbody></table></div></section>\n')


def organic_sources(o):
    """Sources & evidence: the detailed organic table, theme counts by firm, collection and Centurion notes (moved 2026-11-03)."""
    posts = o['posts']
    themes = ['Market / macro', 'Investor education', 'Development / asset', 'CSR / community', 'Culture / people', 'Team / hire', 'Brand / other']
    rows, mix = [], []
    for k in FIRMS[:4]:
        p = [x for x in posts if x['firm'] == k]
        lk = [x['likes'] for x in p if x['likes'] is not None]
        fm = collections.Counter(x['format'] for x in p)
        th = collections.Counter(x['theme'] for x in p)
        hidden = len(p) - len(lk)
        med = ('%g' % st.median(lk)) + (' <small>%d hidden</small>' % hidden if hidden else '')
        rows.append('<tr><td class="brandcell">%s<br><small>%s</small></td><td class="r">%d</td><td class="r">%d / %d / %d</td><td class="wrap-cell">%s</td>'
                    '<td class="r">%d of %d</td><td class="r">%s</td><td class="r">%s</td></tr>'
                    % (E(NAMES[k]), E(o['accounts'][k]), len(p), fm['Reel'], fm['Carousel'], fm['Static'],
                       E(', '.join('%s (%d)' % (t, n) for t, n in th.most_common(2))), sum(x['names_fund'] for x in p), len(p), med, '{:,}'.format(o['followers'][k])))
        mix.append([th.get(t, 0) for t in themes])
    mixrows = ''.join('<tr><td>%s</td>%s</tr>' % (E(t), ''.join('<td class="r">%s</td>' % (mix[j][i] or '&middot;') for j in range(4)))
                      for i, t in enumerate(themes) if any(m[i] for m in mix))
    return ('<div id="ri-org-sources"><h3>Posts and themes</h3>\n'
            '<p class="dek">Posts published on each firm&rsquo;s own Instagram account in the 30 days ending 13 October 2026 (posts dated 14 September to 13 October), collected for all four accounts on ' + DATE + '. '
            + E(o['centurion']) + '</p>\n'
            '<div class="tw"><table class="ri-cmpt"><thead><tr><th>Firm</th><th class="r">Posts</th><th class="r">Reels / carousels / static</th>'
            '<th>Main themes</th><th class="r">Names a fund or offering</th><th class="r">Median likes</th><th class="r">Followers</th></tr></thead><tbody>'
            + ''.join(rows) + '</tbody></table></div>\n'
            '<div class="tw"><table class="ri-cmpt ri-mix"><thead><tr><th>Theme, posts</th>' + ''.join('<th class="r">%s</th>' % E(k) for k in FIRMS[:4]) +
            '</tr></thead><tbody>' + mixrows + '</tbody></table></div>\n'
            '<p class="pnote m0">Themes are the page&rsquo;s reviewed themes; Greybrook&rsquo;s were assigned from each caption on the same scheme. '
            'Likes are not adjusted for follower count. Followers: %s</p></div>\n' % E(o['followers_note']))


def paid_section(a):
    """Paid Social tab (founder, 2026-11-03): one glance table, a collapsed breakdown, one ad per firm and one finding.
    Counts, advertisers, links and method are in Sources & evidence (paid_sources)."""
    rec = a['records']
    inv = {k: [x for x in rec if x['firm'] == k and x['for_investors']] for k in ('Equiton', 'Skyline', 'Lankin')}
    total = sum(len(v) for v in inv.values())
    names = {'Equiton': 'Equiton', 'Skyline': 'Skyline Wealth Management', 'Lankin': 'Lankin Investments'}
    rows, brk = [], []
    for k, v in inv.items():
        n = len(v); g = a['glance'][k]
        m = sum(x['focus'] == g['focus'] for x in v)
        fc = collections.Counter(x['focus'] for x in v).most_common()
        assert fc[0][0] == g['focus'], k
        rows.append('<tr><td class="brandcell">%s</td><td class="r" data-label="Investor ads reviewed">%d</td><td class="wrap-cell" data-label="Most common message">%s, %s (%d of %d)</td>'
                    '<td class="r" data-label="Used video">%s</td><td class="r" data-label="Mentioned a return figure">%s</td><td class="r" data-label="Stated a minimum investment">%s</td></tr>'
                    % (E(names[k]), n, E(g['label']), pct(m, n), m, n, pct(sum(x['format'] == 'video' for x in v), n),
                       pct(sum(x['return_figure'] for x in v), n), pct(sum(x['minimum'] for x in v), n)))
        sc = collections.Counter(x['stage'] for x in v)
        second = '%s, %s' % (fc[1][0], pct(fc[1][1], n)) if len(fc) > 1 else '&middot;'
        brk.append('<tr><td class="brandcell">%s</td><td class="r">%s</td><td class="wrap-cell">%s</td>%s</tr>'
                   % (E(names[k]), pct(sum(x['registered_accounts'] for x in v), n), second,
                      ''.join('<td class="r">%s (%d)</td>' % (pct(sc.get(s, 0), n), sc.get(s, 0)) for s in ('awareness', 'consideration', 'decision'))))
    exs = ''.join('<article class="ri-adex"><h4>%s &middot; %s</h4><p class="ri-adq">&ldquo;%s&rdquo;</p><p>%s</p>'
                  '<p class="ri-adsrc"><a href="https://www.facebook.com/ads/library/?id=%s" target="_blank" rel="noopener nofollow">Open in the Meta Ad Library</a></p></article>'
                  % (E(x['firm']), E(x['title']), E(x['headline']), E('The headline ' + x['caption']), x['id']) for x in a['examples'])
    e, s_, l = (inv[k] for k in ('Equiton', 'Skyline', 'Lankin'))
    mn = lambda v: pct(sum(x['minimum'] for x in v), len(v))
    same = mn(s_) == mn(l)
    return ('<section id="ri-paid-compare"><div class="ri-ovhero"><div class="sec-head"><h2>Paid Social Strategy</h2></div>\n'
            '<p class="ri-ovlead">Messages and formats in <em>%d investor ads</em> from three firms, reviewed %s.</p></div>\n' % (total, DATE) +
            '<h3 class="ri-wh">Ad strategy at a glance</h3>\n'
            '<div class="tw"><table class="ri-wtable ri-ptable"><thead><tr><th>Firm</th><th class="r">Investor ads reviewed</th><th>Most common message</th><th class="r">Used video</th>'
            '<th class="r">Mentioned a return figure</th><th class="r">Stated a minimum investment</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>\n'
            '<p class="pnote">No active Canadian ads matched Greybrook in the search. Centurion&rsquo;s four ads were for recruitment.</p>\n'
            '<details class="ri-adv"><summary>View ad breakdown</summary>\n'
            '<p class="dek">Each percentage uses the firm&rsquo;s reviewed investor ads as its denominator; stage columns show the number of ads in brackets, and rounding can make a row total 99% or 101%. The buying stage is an interpretation of each ad&rsquo;s wording and call to action, not a measured result.</p>\n'
            '<div class="tw"><table class="ri-cmpt"><thead><tr><th>Firm</th><th class="r">Named RRSP or TFSA</th><th>Second most common message</th>'
            '<th class="r">Awareness stage</th><th class="r">Consideration stage</th><th class="r">Decision stage</th></tr></thead><tbody>' + ''.join(brk) + '</tbody></table></div>\n'
            '</details>\n'
            '<h3 class="ri-wh">One ad from each firm</h3>\n<div class="ri-adexs">' + exs + '</div>\n'
            '<h3 class="ri-wh">What stood out</h3>\n'
            '<p class="dek">Equiton stated a minimum investment in %s of its reviewed investor ads, compared with %s. That gives a prospective investor a concrete detail to check before enquiring. These shares count the ad text only: Skyline&rsquo;s lead forms ask whether the reader has $50,000 to invest (see HMM Ranking).</p>\n'
            % (mn(e), ('%s for both Skyline and Lankin' % mn(s_)) if same else ('%s for Skyline and %s for Lankin' % (mn(s_), mn(l)))) +
            '<p class="dek m0">The feed and the ads can tell different stories: Skyline&rsquo;s corporate Instagram feed featured construction and leasing updates, while Skyline Wealth Management advertised individual funds.</p>'
            '</section>\n')


def paid_sources(a):
    """Sources & evidence: advertiser pages, library counts and their reconciliation, the detailed per-firm table, examples and method."""
    rec = a['records']; tot = a['library_totals']
    inv = {k: [x for x in rec if x['firm'] == k and x['for_investors']] for k in ('Equiton', 'Skyline', 'Lankin')}
    read = {k: [x for x in rec if x['firm'] == k] for k in ('Equiton', 'Skyline', 'Lankin')}
    listed = sum(tot[k]['active'] for k in inv)
    rows = []
    for k in FIRMS:
        t = tot[k]
        if k == 'Greybrook':
            rows.append('<tr><td class="brandcell">%s</td><td>&middot;</td><td class="r">0</td><td class="r">&middot;</td><td class="r">&middot;</td><td class="wrap-cell">%s</td></tr>' % (E(NAMES[k]), E(t['note'])))
            continue
        r = [x for x in rec if x['firm'] == k]; v = [x for x in r if x['for_investors']]
        fc = ', '.join('%s (%d)' % (f, n) for f, n in collections.Counter(x['focus'] for x in v).most_common(3)) or 'recruitment, not investor-facing'
        rows.append('<tr><td class="brandcell">%s</td><td>%s</td><td class="r">%d</td><td class="r">%d</td><td class="r">%d</td><td class="wrap-cell">%s</td></tr>'
                    % (E(NAMES[k]), E(t['page']), t['active'], len(r), len(v), E(fc)))
    sl = tot['Skyline Living (resident leasing)']
    rows.append('<tr><td class="brandcell">Skyline</td><td>%s</td><td class="r">%d</td><td class="r">&middot;</td><td class="r">0</td><td class="wrap-cell">Resident leasing ads, not investor-facing</td></tr>' % (E(sl['page']), sl['active']))
    other = [x for x in read['Equiton'] if not x['for_investors']]
    ex = ' '.join('<a href="https://www.facebook.com/ads/library/?id=%s" target="_blank" rel="noopener nofollow">%s &middot; %s</a>.' % (x['id'], E(x['firm']), E(x['title'])) for x in a['examples'])
    return ('<div id="ri-paid-sources"><h3>Advertisers and ad counts</h3>\n'
            '<p class="dek">Active ads in the Meta Ad Library in Canada, collected on ' + DATE + '. ' + E(a['method']) + ' The library shows that an ad is live; it does not show spend, reach or results. '
            'Raw output is kept privately and recorded by hash in the kit.</p>\n'
            '<div class="tw"><table class="ri-cmpt"><thead><tr><th>Firm</th><th>Advertiser page</th><th class="r">Active ads listed</th><th class="r">Read</th><th class="r">Investor ads reviewed</th><th>Messages, investor ads</th></tr></thead><tbody>'
            + ''.join(rows) + '</tbody></table></div>\n'
            '<p class="pnote"><b>%d and %d:</b> the three investor advertiser pages listed %d active ads (Equiton %d, Skyline Wealth Management %d, Lankin %d). %d were read; %d of Equiton&rsquo;s listings were not returned, and one Equiton ad (&ldquo;%s&rdquo;) was a home sale, not an investor ad, leaving %d reviewed investor ads.</p>\n'
            % (sum(len(v) for v in inv.values()), listed, listed, tot['Equiton']['active'], tot['Skyline']['active'], tot['Lankin']['active'], sum(len(v) for v in read.values()),
               tot['Equiton']['active'] - len(read['Equiton']), E(other[0]['headline']) if other else '', sum(len(v) for v in inv.values())) +
            '<p class="pnote">On ' + DATE + ' most ad links pointed to a Meta short link (fb.me) and were not followed. Where the ads send people was checked separately on 3 November 2026; see &ldquo;Ad destinations&rdquo; below and the last block of HMM Ranking.</p>\n' + dest_sources() +
            '<p class="pnote m0"><b>Examples in Paid Social:</b> ' + ex + '</p>\n</div>\n')


def dest_sources():
    """Sources & evidence: the 3 November ad-destination check (collection, rules, browser checks, listed links)."""
    dd = json.load(open(os.path.join(HERE, 'ad_destinations.json')))
    ck = json.load(open(os.path.join(HERE, 'ad_destination_checks.json')))
    c = dd['collected']; n = dd['counts']
    prior = sum(r['in_2_november_review'] for r in dd['records'])
    links = ''.join('<li>%s: %s</li>' % (E(u.replace('https://', '')), E(('redirects to ' + v['final_url'].replace('https://', '') + '; ' if v['final_url'] != u else '') + ('&ldquo;page not found&rdquo;' if v['status'] == 404 else ('bot check shown to the collector' if v['status'] == 403 else v['title']))).replace('&amp;ldquo;', '&ldquo;').replace('&amp;rdquo;', '&rdquo;'))
                    for u, v in dd['listed_links_opened'].items())
    def when(t):
        return '3 November, ' + t[11:16] + ((' to ' + t.split(' to ')[1]) if ' to ' in t else '') + ' Toronto time'
    checks = ''.join('<li>%s: %d ads, %s</li>' % (E(when(x['checked'])), len(x['ids']),
                     'classified by the page the button points to (Meta labels them URL-link ads; all versions checked)' if x.get('resolve_by_url_label') else E(x['destination'])) for x in ck['checks'])
    return ('<h3>Ad destinations, 3 November 2026</h3>\n'
            '<p class="dek">The three investor advertiser pages were collected again with apify/facebook-ads-scraper (run %s, %s to %s Toronto time): %d investor ads (%s), %d of them in the %s review by ad ID. '
            'A Meta form is counted only where the library record shows the form&rsquo;s questions; a record with a form and a website link, or a page behind a bot check, stays Unverified and in the denominator. '
            '&ldquo;Names the offer&rdquo; compares the fund, development or event named in the ad with the visible destination text, form disclaimers excluded. Raw output and page text are private; SHA-256 %s&hellip;.</p>\n'
            % (E(c['run']), c['started'][11:16], c['finished'][11:16], len(dd['records']), ', '.join('%s %d' % (E(NAMES[k]), v) for k, v in sorted(n.items())), prior, DATE, dd['raw_sha256'][:12]) +
            '<p class="pnote mb12"><b>Read-only checks in the author&rsquo;s own browser:</b></p><ul class="ri-themedefs">' + checks + '</ul>\n'
            '<p class="pnote mb12"><b>Listed links opened on 3 November:</b></p><ul class="ri-themedefs">' + links + '</ul>\n')


def recs_section(a, o, w):
    """Recommendations tab (founder, 2026-11-03): one card per firm with what stood out, a test and a proposed measure.
    The figures in each observation are checked against the evidence files here."""
    rec = a['records']
    inv = lambda k: [x for x in rec if x['firm'] == k and x['for_investors']]
    posts = lambda k: [x for x in o['posts'] if x['firm'] == k]
    eq_fund = sum(x['names_fund'] for x in posts('Equiton')); eq_n = len(posts('Equiton'))
    sk_min = sum(x['minimum'] for x in inv('Skyline')); sk_n = len(inv('Skyline'))
    gb = [x for x in posts('Greybrook') if x['likes'] is not None]
    gb_top = max(x['likes'] for x in gb); gb_fund = [x['likes'] for x in posts('Greybrook') if x['names_fund']]
    ce = [x for x in rec if x['firm'] == 'Centurion']
    assert (eq_fund, eq_n) == (1, 14) and (sk_min, sk_n) == (1, 16) and gb_top == 116 and gb_fund == [1], (eq_fund, eq_n, sk_min, sk_n, gb_top, gb_fund)
    assert len(ce) == 4 and not any(x['for_investors'] for x in ce)
    assert '$50,000' in w['firms']['Skyline']['minimum']
    words = {1: 'one', 4: 'four'}
    cards = [
        ('Equiton', 'Its investor ads featured specific offerings, while only %d of %d Instagram posts named a fund.' % (eq_fund, eq_n),
         'Turn one apartment fund ad message into a short explainer reel. Compare it with a market-update reel of similar length.',
         'Saves per 1,000 accounts reached.'),
        ('Skyline', 'Its Apartment REIT page states a $50,000 minimum. Only %d of %d reviewed investor ads mentioned a minimum, although its lead forms ask whether the reader has $50,000 to invest.' % (sk_min, sk_n),
         'Run two versions of the Apartment REIT ad. Add the minimum to one and keep the audience, creative and budget comparable.',
         'Cost per enquiry that meets the fund&rsquo;s eligibility criteria.'),
        ('Lankin', 'The reviewed ads and website cited different target return ranges. The research could not confirm whether they referred to the same fund.',
         'First verify which fund each figure describes. Then test naming the fund in the ad headline, with both versions linking to the same verified fund page.',
         'Qualified enquiries per 100 landing-page visits.'),
        ('Greybrook', 'Its hockey sponsorship received %d visible likes. Its fund post received %s.' % (gb_top, words[gb_fund[0]]),
         'Explain the same fund topic in two carousels. Open one with a member of the investment team and the other with the existing fund headline. Give each a trackable route to the fund page.',
         'Fund-page visits per 1,000 accounts reached.'),
        ('Centurion', 'Its website featured the Chief Economist&rsquo;s research. All %s active ads found were for recruitment.' % words[len(ce)],
         'Promote one research article to investors and link it to the Apartment REIT page.',
         'Share of ad-referred article visitors who continue to the REIT page.')]
    # Second Lankin test (founder, 2026-11-03): one minimum across ads, form and page, from the 3 November checks.
    al = w['matrix_check_2']['ad_landing']
    assert '$10,000' in al and '$5,000 or more' in al and 'from a minimum of $25,000' in w['matrix_check_2']['others']['Lankin']
    extra = {'Lankin': ('Two of its ads say &ldquo;Invest in Private Real Estate with $10,000&rdquo;, one of its forms asks about &ldquo;$5,000 or more&rdquo;, and a campaign page states a $25,000 minimum; its website leaves the minimum to the call.',
                        'Show one minimum in the ad, the form and the page it links to. Compare enquiries with the current mixed figures over the same period.',
                        'Share of enquiries that meet the minimum.')}
    def block(obs, test, meas):
        return ('<p class="ri-robs">%s</p><dl><div class="ri-rtest"><dt>Test</dt><dd>%s</dd></div>'
                '<div class="ri-rmeasure"><dt>Measure</dt><dd>%s</dd></div></dl>' % (obs, test, meas))
    html = ''.join('<article class="ri-rcard"><h3>%s</h3>%s%s</article>' % (E(NAMES[k]), block(obs, test, meas),
                   ('<div class="ri-rsecond">' + block(*extra[k]) + '</div>') if k in extra else '') for k, obs, test, meas in cards)
    return ('<section id="ri-recs-firms"><div class="ri-ovhero"><div class="sec-head"><h2>Recommendations</h2></div>\n'
            '<p class="ri-ovlead">A <em>marketing test</em> for each firm, from its website, Instagram and Meta ads.</p></div>\n'
            '<div class="ri-rgrid">' + html + '</div>\n'
            '<p class="pnote m0">Each measure is a proposed metric for the firm to track. The public research supplies the observation behind each test, not its result.</p></section>\n')



def sources_head(a, o, w):
    """Sources & evidence header (founder, 2026-11-03): title, one line and an at-a-glance strip, as on the Business index."""
    posts = len(o['posts'])
    ads = sum(1 for x in a['records'] if x['for_investors'])
    sites = sum(1 for k in FIRMS if w['firms'][k]['read'])
    stats = [('Instagram posts reviewed', '%d' % posts), ('Investor ads reviewed', '%d' % ads), ('Websites read', '%d of %d' % (sites, len(FIRMS))), ('Instagram and ads collected', DATE)]
    ex_dates = sorted({x['captured'] for x in w['examples']})
    assert len(ex_dates) == 1, ex_dates
    return ('<section id="ri-sources-head"><div class="sec-head"><h2>Sources &amp; evidence</h2>\n'
            '<p class="dek">The evidence behind each tab, how it was collected and calculated, what changed, and the data to download.</p>\n'
            '<p class="dek">Each date has one purpose: Instagram posts and Meta ads were collected, and the five websites read, on ' + DATE + '; the two website examples were captured, the Centurion minimum verified, and the ad destinations and the HMM Ranking website matrix checked, on ' + E(ex_dates[0]) + '.</p></div>\n'
            '<dl class="ri-sstats" aria-label="Sources and evidence at a glance">' + ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (E(k), v) for k, v in stats) + '</dl></section>\n')


def corrections(a, o, w):
    """One list of dated corrections from the evidence files (websites, ads, organic)."""
    items = []
    for src, label in ((w, 'Website Messaging'), (a, 'Paid Social'), (o, 'Organic Social')):
        for c in src.get('corrections', []):
            items.append((c['date'], label, c['text']))
    items.sort()
    return ('<section id="ri-corrections"><details class="ri-adv"><summary>Corrections</summary>\n'
            '<p class="dek">Changes made to this edition&rsquo;s figures or wording after publication, with the date and the tab each affects.</p>\n<ul class="ri-corr">'
            + ''.join('<li><b>%s, %s.</b> %s</li>' % (E(d), E(l), E(t)) for d, l, t in items) + '</ul></details></section>\n')

def put(body, name, html):
    a, b = '<!-- STRATEGY:%s START -->' % name, '<!-- STRATEGY:%s END -->' % name
    if body.count(a) != 1 or body.count(b) != 1:
        raise ValueError('Missing markers for ' + name)
    i, j = body.index(a) + len(a), body.index(b)
    return body[:i] + '\n' + html + body[j:]


# HMM Ranking comparisons (founder brief, 2026-11-03): one place to compare the firms across websites, Instagram and Meta ads.
# Each block answers one reader question and links to the tab with the examples. Ad destinations are added only once verified.
LEVEL = {'ad': 'Ad landing', 'home': 'Homepage', 'product': 'Product page', 'call': 'Discussed on a call', 'not_found': 'Not found'}
MATRIX_COLS = [('fund', 'Names the fund'), ('minimum', 'Minimum investment'), ('eligibility', 'Who can invest'), ('next', 'Next step')]


def rank_website(w):
    """Where a reader first meets each answer (founder, 2026-11-03): ad landing, homepage, product page, a call, or not found."""
    rows = []
    for k in FIRMS:
        m = w['firms'][k]['matrix']
        assert all(m[c][0] in LEVEL for c, _ in MATRIX_COLS), k
        up = sum(m[c][0] in ('ad', 'home') for c, _ in MATRIX_COLS)
        deep = sum(m[c][0] == 'product' for c, _ in MATRIX_COLS)
        rows.append((-up, -deep, NAMES[k], k, m, up))
    rows.sort()
    body = ''
    for _, _, name, k, m, up in rows:
        cells = ''.join('<td class="ri-mx ri-mx-%s" data-label="%s"><span class="ri-mxs">%s</span>%s</td>'
                        % (m[c][0], E(lab), LEVEL[m[c][0]], ('<span class="ri-mxd">%s</span>' % E(m[c][1])) if m[c][1] else '')
                        for c, lab in MATRIX_COLS)
        body += '<tr><td class="brandcell">%s</td>%s<td class="r ri-mxn" data-label="Up front">%d of %d</td></tr>' % (E(name), cells, up, len(MATRIX_COLS))
    return ('<div id="ri-cmp-website" class="ri-cblock"><div class="sec-head"><h2>What can an investor learn before enquiring?</h2>\n'
            '<p class="dek">Where a reader first meets each answer: the ad landing, the homepage, a product page, or only on a call. Checked 2 and 3 November 2026; sorted by answers up front.</p></div>\n'
            '<div class="tw"><table class="ri-wtable ri-mxt"><thead><tr><th>Firm</th>' + ''.join('<th>%s</th>' % E(l) for _, l in MATRIX_COLS) +
            '<th class="r">Up front</th></tr></thead><tbody>' + body + '</tbody></table></div>\n'
            '<p class="pnote">Ad landing covers the Meta forms and pages the ads were verified to reach on 3 November; Greybrook and Centurion had no active investor ads. '
            'Equiton states its investor criteria only inside an image on five fund pages, so a text-only reader or search engine does not see them. '
            'Lankin&rsquo;s numbers differ by place: two of its ads say &ldquo;Invest in Private Real Estate with $10,000&rdquo;, one of its forms asks about &ldquo;$5,000 or more&rdquo;, and the campaign page one of its ads links to states a $25,000 minimum. '
            '&ldquo;Not found&rdquo; covers only the pages reviewed, listed in Sources &amp; evidence.</p>\n'
            '<p class="ri-vlink"><a href="#ri-view-website">See the pages in Website Messaging <span aria-hidden="true">&rarr;</span></a></p></div>\n')


def rank_organic(o):
    fm = {'Reel': 'reels', 'Carousel': 'carousels', 'Static': 'static'}
    cnt = {k: collections.Counter(fm.get(p['format'], 'static') for p in o['posts'] if p['firm'] == k) for k in FIRMS if k != 'Centurion'}
    assert sum(sum(c.values()) for c in cnt.values()) == len(o['posts'])
    order = sorted(cnt, key=lambda k: (-sum(cnt[k].values()), NAMES[k]))
    mx = max(sum(c.values()) for c in cnt.values())
    li = ''
    for k in order:
        c = cnt[k]; n = sum(c.values())
        segs = ''.join('<span class="ri-seg ri-seg-%s" data-w="%.1f" title="%s: %d"></span>' % (f, 100 * c[f] / mx, f.capitalize() if f != 'static' else 'Static posts', c[f]) for f in ('reels', 'carousels', 'static') if c[f])
        txt = ' &middot; '.join('%d %s' % (c[f], {'reels': 'reel' if c[f] == 1 else 'reels', 'carousels': 'carousel' if c[f] == 1 else 'carousels', 'static': 'static'}[f]) for f in ('reels', 'carousels', 'static'))
        li += '<li class="ri-frow"><span class="ri-fname">%s</span><span class="ri-fbar">%s</span><span class="ri-fn">%d posts</span><span class="ri-ftxt">%s</span></li>' % (E(NAMES[k]), segs, n, txt)
    li += '<li class="ri-frow ri-frow-none"><span class="ri-fname">%s</span><span class="ri-ftxt">No corporate Instagram account found</span></li>' % E(NAMES['Centurion'])
    return ('<div class="sec-head ri-cblock-head"><h2>Which firms post most often, and what engagement do they receive?</h2>\n'
            '<p class="dek">Posts on each firm&rsquo;s own Instagram account in the reporting window, by format, then engagement by the metric you choose.</p></div>\n'
            '<div class="ri-fmt"><p class="ri-cmp-h">Post formats</p><ul class="ri-flegend" aria-hidden="true"><li><i class="ri-seg-reels"></i>Reels</li><li><i class="ri-seg-carousels"></i>Carousels</li><li><i class="ri-seg-static"></i>Static posts</li></ul>'
            '<ul class="ri-fbars">' + li + '</ul></div>\n')


def rank_paid(a):
    inv = collections.OrderedDict((k, [x for x in a['records'] if x['for_investors'] and x['firm'] == k]) for k in ('Equiton', 'Skyline', 'Lankin'))
    firms = sorted(inv, key=lambda k: (-len(inv[k]), NAMES[k]))
    themes = collections.Counter(x['focus'] for v in inv.values() for x in v)
    head = ''.join('<th class="r">%s<small>%d ads</small></th>' % (E(NAMES[k]), len(inv[k])) for k in firms)
    trs = ''
    for t, _ in sorted(themes.items(), key=lambda p: (-p[1], p[0])):
        tds = ''
        for k in firms:
            c = sum(x['focus'] == t for x in inv[k]); n = len(inv[k])
            tds += '<td class="r ri-hm" data-label="%s"><span class="ri-hmv">%s <small>(%d)</small></span><span class="ri-hmb"><span class="bar-fill" data-w="%.1f"></span></span></td>' % (E(NAMES[k]), pct(c, n), c, 100 * c / n)
        trs += '<tr><td>%s</td>%s</tr>' % (E(t[0].upper() + t[1:]), tds)
    meas = [('Used video', lambda x: x['format'] == 'video'), ('Mentioned a return figure', lambda x: x['return_figure']), ('Stated a minimum investment', lambda x: x['minimum'])]
    mb = ''
    for lab, f in meas:
        vals = sorted(((sum(f(x) for x in inv[k]), len(inv[k]), k) for k in firms), key=lambda p: (-p[0] / p[1], NAMES[p[2]]))
        mb += '<div class="ri-meas"><p class="ri-cmp-h">%s</p><ol class="ri-mbars">%s</ol></div>' % (E(lab), ''.join(
            '<li><span class="ri-fname">%s</span><span class="ri-track"><span class="bar-fill" data-w="%.1f"></span></span><span class="ri-val">%s <small>(%d of %d)</small></span></li>' % (E(NAMES[k]), 100 * c / n, pct(c, n), c, n) for c, n, k in vals))
    total = sum(len(v) for v in inv.values())
    return ('<section id="ri-cmp-paid" class="ri-cblock"><div class="sec-head"><h2>How does each firm vary its ads?</h2>\n'
            '<p class="dek">The %d investor ads reviewed in the Meta Ad Library on %s. No active Canadian ads matched Greybrook in the search, and Centurion&rsquo;s ads were for recruitment.</p></div>\n' % (total, DATE) +
            '<p class="ri-cmp-h">Message theme, share of each firm&rsquo;s ads</p>'
            '<div class="tw"><table class="ri-hmt"><thead><tr><th>Message theme</th>' + head + '</tr></thead><tbody>' + trs + '</tbody></table></div>\n'
            '<p class="pnote">Each ad has one main message theme, so a firm&rsquo;s column adds up to 100% (rounding aside). Counts in brackets.</p>\n'
            '<div class="ri-measg">' + mb + '</div>\n'
            '<p class="pnote">Measured separately because one ad can use video, name a return figure and state a minimum at once. Sorted by share, highest first.</p>\n'
            '<p class="ri-vlink"><a href="#ri-view-paid">See the ads in Paid Social <span aria-hidden="true">&rarr;</span></a></p></section>\n')


DEST_TYPES = ['Meta form', 'Campaign landing page', 'Fund or product page', 'Homepage or other general page', 'Booking page', 'Page not found', 'Unverified']


def rank_dest(dd):
    """Ad destinations (founder brief, 2026-11-03): a separately dated update; unverified destinations stay in the denominator."""
    recs = dd['records']
    firms = sorted({r['firm'] for r in recs}, key=lambda k: (-sum(r['firm'] == k for r in recs), NAMES[k]))
    n = {k: sum(r['firm'] == k for r in recs) for k in firms}
    assert set(r['destination'] for r in recs) <= set(DEST_TYPES)
    def cell(c, tot, lab):
        return '<td class="r ri-hm" data-label="%s"><span class="ri-hmv">%s <small>(%d)</small></span><span class="ri-hmb"><span class="bar-fill" data-w="%.1f"></span></span></td>' % (E(lab), pct(c, tot), c, 100 * c / tot if tot else 0)
    t1 = ''.join('<tr><td>%s</td>%s</tr>' % (E(t), ''.join(cell(sum(r['firm'] == k and r['destination'] == t for r in recs), n[k], NAMES[k]) for k in firms)) for t in DEST_TYPES)
    t2 = ''
    for k in firms:
        nm = [r for r in recs if r['firm'] == k and r['offer_named']]
        c = collections.Counter(r['presents_offer'] for r in nm)
        t2 += '<tr><td class="brandcell">%s</td><td class="r" data-label="Ads naming an offer">%d of %d</td>%s</tr>' % (E(NAMES[k]), len(nm), n[k], ''.join(
            '<td class="r" data-label="%s">%s <small>(%d)</small></td>' % (lab, pct(c[v], len(nm)), c[v]) if nm else '<td class="r" data-label="%s">&middot;</td>' % lab
            for v, lab in (('Yes', 'Destination names it'), ('No', 'Destination does not'), ('Unverified', 'Unverified'))))
    total = len(recs); prior = sum(r['in_2_november_review'] for r in recs)
    unv_form = sum(r['destination'] == 'Unverified' and 'instant form' in r['basis'] for r in recs)
    unv_bot = sum(r['destination'] == 'Unverified' and 'bot check' in r['basis'] for r in recs)
    bridle = sum(r['offer_named'] == 'Bridleview Residences' and r['destination'] == 'Meta form' and r['presents_offer'] == 'No' for r in recs)
    lk = dd['listed_links_opened']
    nf = [u.replace('https://', '') for u, v in lk.items() if v['status'] == 404]
    lr = [r for r in recs if r['firm'] == 'Lankin' and 'URL link' in r['basis']]
    n404 = sum(r['destination'] == 'Page not found' for r in lr)
    nred = sum((r['listed_link'] or '').endswith('lankin.com/investment/') for r in lr)
    ncamp = sum('private-reit' in (r['listed_link'] or '') for r in lr)
    assert bridle and len(nf) == 2 and len(lr) == 14 and n404 == 6 and nred == 7 and ncamp == 1
    usf = [r for r in recs if r['offer_named'] == 'US Apartment Fund' and r['destination'] == 'Fund or product page']
    return ('<section id="ri-cmp-dest" class="ri-cblock"><div class="sec-head"><h2>Where does each investor ad take the reader?</h2>\n'
            '<p class="dek">Checked separately on 3 November 2026: %d active investor ads (%s), %d of them in the 2 November review. Unverified destinations stay in each firm&rsquo;s total.</p></div>\n'
            % (total, ', '.join('%s %d' % (E(NAMES[k]), n[k]) for k in firms), prior) +
            '<p class="ri-cmp-h">Destination, share of each firm&rsquo;s ads</p>'
            '<div class="tw"><table class="ri-hmt"><thead><tr><th>Destination</th>' + ''.join('<th class="r">%s<small>%d ads</small></th>' % (E(NAMES[k]), n[k]) for k in firms) +
            '</tr></thead><tbody>' + t1 + '</tbody></table></div>\n'
            '<p class="ri-cmp-h">Ads that name a specific fund, development or event: does the destination name it too?</p>'
            '<div class="tw"><table class="ri-wtable ri-ptable"><thead><tr><th>Firm</th><th class="r">Ads naming an offer</th><th class="r">Destination names it</th><th class="r">Destination does not</th><th class="r">Unverified</th></tr></thead><tbody>' + t2 + '</tbody></table></div>\n'
            '<p class="pnote">Meta form is counted only where the library record shows the form&rsquo;s questions.%s '
            'Equiton&rsquo;s %d Bridleview Residences forms show the 24%% target return and $25,000 minimum but name the development only in the disclaimer. '
            'The booking page is a Calendly calendar that names no fund. Lankin&rsquo;s %d website-link ads are counted by the page their button points to: Meta labels each &ldquo;This ad is from a URL link&rdquo; and all their versions point to a lankin.com address (checked in a browser on 3 November), though a Meta form is attached to each as an extra asset and the live ad cannot be seen. %d point to an address that shows &ldquo;page not found&rdquo; (%s), %d to one that redirects to Lankin&rsquo;s partnerships page for institutional and direct partners, and %d to its campaign page.</p>\n'
            % ((' Unverified covers %d ads.' % (unv_form + unv_bot)) if (unv_form + unv_bot) else '', bridle, len(lr), n404, ' and '.join(nf), nred, ncamp) +
            ('<p class="pnote">Equiton&rsquo;s %d US Apartment Fund ads lead to a landing page for that fund, which states the $25,000 minimum and the 8&ndash;12%% target return (read in a browser on 3 November, after the page showed a bot check to the collector). '
             'Two details differ: the ads say &ldquo;RRSP, TFSA &amp; RESP eligible&rdquo; while the page names RRSP and TFSA only, and the ads say &ldquo;qualified investors&rdquo; while the page does not say who can invest.</p>\n' % len(usf) if usf else '') +
            '<p class="ri-vlink"><a href="#ri-view-paid">See the ads in Paid Social <span aria-hidden="true">&rarr;</span></a></p></section>\n')


def main():
    a, o, w = load('ads.json'), load('organic.json'), load('websites.json')
    body = open(BODY, encoding='utf-8').read()
    body = put(body, 'website', website_view(w))
    body = put(body, 'websrc', website_sources(w))
    body = put(body, 'srchead', sources_head(a, o, w))
    body = put(body, 'corr', corrections(a, o, w))
    body = put(body, 'organic', organic_section(o))
    body = put(body, 'orgsrc', organic_sources(o))
    body = put(body, 'paid', paid_section(a))
    body = put(body, 'paidsrc', paid_sources(a))
    body = put(body, 'recs', recs_section(a, o, w))
    body = put(body, 'rankweb', rank_website(w))
    body = put(body, 'rankorg', rank_organic(o))
    body = put(body, 'rankpaid', rank_paid(a))
    body = put(body, 'rankdest', rank_dest(json.load(open(os.path.join(HERE, 'ad_destinations.json')))))
    if re.search(r'[–—]', body.split('<!-- STRATEGY:website START -->')[1].split('<!-- STRATEGY:website END -->')[0]):
        raise ValueError('Dash in the website view')
    with open(BODY, 'w', encoding='utf-8') as f:
        f.write(body)
    print('Rendered the strategy comparison into report_body.html')


if __name__ == '__main__':
    main()
