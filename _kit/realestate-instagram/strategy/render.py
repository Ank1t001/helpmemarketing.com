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


def roster_note():
    return ('<p class="pnote ri-roster"><b>Five firms throughout.</b> Since ' + DATE + ' the index compares '
            'Equiton, Skyline, Lankin Investments, Greybrook Realty Partners and Centurion Asset Management in every section. '
            'Instagram, the Meta Ad Library and the websites were all read on ' + DATE + '; Centurion has no corporate Instagram account, '
            'so it is compared on its website and advertising.</p>')


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
    return ('<div class="ri-view" id="ri-view-website">\n<section id="ri-website"><div class="sec-head"><h2>Website messaging</h2>\n'
            '<p class="dek">How each firm explains its investment offer and guides prospective investors to the next step.</p></div>\n'
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
    corr = ''.join('<p class="pnote"><b>Correction, %s:</b> %s</p>' % (E(c['date']), E(c['text'])) for c in w.get('corrections', []))
    ex = ' '.join('%s (%s, captured %s, SHA-256 %s&hellip;).' % (E(x['title']), E(x['page']), x['captured'], x['sha256'][:12]) for x in w['examples'])
    return ('<section id="ri-web-sources"><details class="ri-adv"><summary>Website messaging: quotes, notices and collection</summary>\n'
            '<p class="dek">Skyline, Lankin, Greybrook and Centurion were read with Chromium on ' + DATE + ' (' + E(w['captured_at'].split(', ')[1]) + '): '
            'the homepage and the main investor page. Page text is kept privately and recorded by hash in the kit. Equiton showed a bot check to that browser; '
            'it was read the same evening in the author&rsquo;s own browser. Quotes are short excerpts; figures are the firms&rsquo; own and were not verified.</p>\n'
            '<div class="ri-wgrid">' + ''.join(cards) + '</div>\n'
            '<p class="pnote"><b>Unresolved:</b> Lankin&rsquo;s ads read the same day cite a 12% to 16% targeted net return, while its homepage lists 10% to 14% '
            'for the Apartment REIT and 10% to 12% for the Growth LP. The ads may describe a different fund; this was not resolved.</p>\n' + corr +
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
    return ('<section id="ri-organic-compare"><div class="sec-head"><h2>Social Media Strategy</h2>\n'
            '<p class="dek">How four real estate investment firms present themselves on Instagram and which posts drew the most visible likes.</p></div>\n'
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
    return ('<section id="ri-org-sources"><details class="ri-adv"><summary>Organic Social: posts, themes and coverage</summary>\n'
            '<p class="dek">Posts published on each firm&rsquo;s own Instagram account, 13 September to 13 October 2026, collected for all four accounts on ' + DATE + '. '
            + E(o['centurion']) + '</p>\n'
            '<div class="tw"><table class="ri-cmpt"><thead><tr><th>Firm</th><th class="r">Posts</th><th class="r">Reels / carousels / static</th>'
            '<th>Main themes</th><th class="r">Names a fund or offering</th><th class="r">Median likes</th><th class="r">Followers</th></tr></thead><tbody>'
            + ''.join(rows) + '</tbody></table></div>\n'
            '<div class="tw"><table class="ri-cmpt ri-mix"><thead><tr><th>Theme, posts</th>' + ''.join('<th class="r">%s</th>' % E(k) for k in FIRMS[:4]) +
            '</tr></thead><tbody>' + mixrows + '</tbody></table></div>\n'
            '<p class="pnote m0">Themes are the page&rsquo;s reviewed themes; Greybrook&rsquo;s were assigned from each caption on the same scheme. '
            'Likes are not adjusted for follower count. Followers: %s</p></details></section>\n' % E(o['followers_note']))


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
                      ''.join('<td class="r">%s</td>' % pct(sc.get(s, 0), n) for s in ('awareness', 'consideration', 'decision'))))
    exs = ''.join('<article class="ri-adex"><h4>%s &middot; %s</h4><p class="ri-adq">&ldquo;%s&rdquo;</p><p>%s</p>'
                  '<p class="ri-adsrc"><a href="https://www.facebook.com/ads/library/?id=%s" target="_blank" rel="noopener nofollow">Open in the Meta Ad Library</a></p></article>'
                  % (E(x['firm']), E(x['title']), E(x['headline']), E('The headline ' + x['caption']), x['id']) for x in a['examples'])
    e, s_, l = (inv[k] for k in ('Equiton', 'Skyline', 'Lankin'))
    mn = lambda v: pct(sum(x['minimum'] for x in v), len(v))
    same = mn(s_) == mn(l)
    return ('<section id="ri-paid-compare"><div class="sec-head"><h2>Paid Social Strategy</h2>\n'
            '<p class="dek">Compare the messages and formats three firms used in %d investor ads reviewed in Canada on %s.</p></div>\n' % (total, DATE) +
            '<h3 class="ri-wh">Ad strategy at a glance</h3>\n'
            '<div class="tw"><table class="ri-wtable ri-ptable"><thead><tr><th>Firm</th><th class="r">Investor ads reviewed</th><th>Most common message</th><th class="r">Used video</th>'
            '<th class="r">Mentioned a return figure</th><th class="r">Stated a minimum investment</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>\n'
            '<p class="pnote">No active Canadian ads matched Greybrook in the search. Centurion&rsquo;s four ads were for recruitment.</p>\n'
            '<details class="ri-adv"><summary>View ad breakdown</summary>\n'
            '<p class="dek">Each percentage uses the firm&rsquo;s reviewed investor ads as its denominator. The buying stage is an interpretation of each ad&rsquo;s wording and call to action, not a measured result.</p>\n'
            '<div class="tw"><table class="ri-cmpt"><thead><tr><th>Firm</th><th class="r">Named RRSP or TFSA</th><th>Second most common message</th>'
            '<th class="r">Awareness stage</th><th class="r">Consideration stage</th><th class="r">Decision stage</th></tr></thead><tbody>' + ''.join(brk) + '</tbody></table></div>\n'
            '</details>\n'
            '<h3 class="ri-wh">One ad from each firm</h3>\n<div class="ri-adexs">' + exs + '</div>\n'
            '<h3 class="ri-wh">What stood out</h3>\n'
            '<p class="dek">Equiton stated a minimum investment in %s of its reviewed investor ads, compared with %s. That gives a prospective investor a concrete detail to check before enquiring.</p>\n'
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
    corr = ''.join('<p class="pnote"><b>Correction, %s:</b> %s</p>' % (E(c['date']), E(c['text'])) for c in a.get('corrections', []))
    ex = ' '.join('<a href="https://www.facebook.com/ads/library/?id=%s" target="_blank" rel="noopener nofollow">%s &middot; %s</a>.' % (x['id'], E(x['firm']), E(x['title'])) for x in a['examples'])
    return ('<section id="ri-paid-sources"><details class="ri-adv"><summary>Paid Social: advertisers, ad counts and method</summary>\n'
            '<p class="dek">Active ads in the Meta Ad Library in Canada, collected on ' + DATE + '. ' + E(a['method']) + ' The library shows that an ad is live; it does not show spend, reach or results. '
            'Raw output is kept privately and recorded by hash in the kit.</p>\n'
            '<div class="tw"><table class="ri-cmpt"><thead><tr><th>Firm</th><th>Advertiser page</th><th class="r">Active ads listed</th><th class="r">Read</th><th class="r">Investor ads reviewed</th><th>Messages, investor ads</th></tr></thead><tbody>'
            + ''.join(rows) + '</tbody></table></div>\n'
            '<p class="pnote"><b>%d and %d:</b> the three investor advertiser pages listed %d active ads (Equiton %d, Skyline Wealth Management %d, Lankin %d). %d were read; %d of Equiton&rsquo;s listings were not returned, and one Equiton ad (&ldquo;%s&rdquo;) was a home sale, not an investor ad, leaving %d reviewed investor ads.</p>\n'
            % (sum(len(v) for v in inv.values()), listed, listed, tot['Equiton']['active'], tot['Skyline']['active'], tot['Lankin']['active'], sum(len(v) for v in read.values()),
               tot['Equiton']['active'] - len(read['Equiton']), E(other[0]['headline']) if other else '', sum(len(v) for v in inv.values())) +
            '<p class="pnote">Each ad&rsquo;s link points to a Meta short link (fb.me); the links were not followed, so where the ads finally send people is not recorded here.</p>\n'
            + corr + '<p class="pnote m0"><b>Examples in Paid Social:</b> ' + ex + '</p>\n</details></section>\n')


def recs_section(a, o, w):
    eq = [x for x in a['records'] if x['firm'] == 'Equiton' and x['for_investors']]
    sk = [x for x in a['records'] if x['firm'] == 'Skyline']
    la = [x for x in a['records'] if x['firm'] == 'Lankin']
    pf = lambda k: (sum(x['names_fund'] for x in o['posts'] if x['firm'] == k), sum(1 for x in o['posts'] if x['firm'] == k))
    cards = [
        ('Equiton', 'Paid Social and Organic Social',
         'Its ads lead with offerings and targeted returns (%d investor ads read), while %d of its %d posts named a fund.' % ((len(eq),) + pf('Equiton')),
         'Bring one ad message into the feed, for example the apartment fund explainer as a reel, and compare its likes and comments with similar market posts. Read the website by hand to complete the comparison.'),
        ('Skyline', 'Paid Social and Website Messaging',
         'None of its %d ads states a return figure, and %s names the $50,000 minimum that its own website shows.'
         % (len(sk), 'only one' if sum(x['minimum'] for x in sk) == 1 else '%d' % sum(x['minimum'] for x in sk)),
         'Test a version of one fund ad that states the minimum and who can invest, as the website already does, against the current version, and compare enquiries per ad.'),
        ('Lankin', 'Paid Social and Website Messaging',
         'Its ads cite a 12% to 16% targeted net return; its homepage lists 10% to 14% and 10% to 12% for two funds.',
         'Make sure the page each ad sends people to names the fund behind the figure in the ad, then compare the RRSP and TFSA year-end messages on enquiries.'),
        ('Greybrook', 'Organic Social',
         'No active ads were found. Its sponsorship and community posts drew the most likes; its fund post drew 1.',
         'Test telling the U.S. Multifamily fund story through the team and the communities it already posts about, and link that post to the fund page.'),
        ('Centurion', 'Website Messaging and Paid Social',
         'No corporate Instagram account was found, its four active ads recruit staff, and its homepage leads with its Chief Economist&rsquo;s research.',
         'Test promoting one research article to investors, sending readers to the article, and measure visits from there to the REIT page.')]
    html = ''.join('<article class="ri-rcard"><h3>%s</h3><p class="ri-rarea">%s</p><dl><div><dt>What I saw</dt><dd>%s</dd></div>'
                   '<div class="ri-rtest"><dt>Recommendation</dt><dd>%s</dd></div></dl></article>' % (E(NAMES[k]), E(area), saw, E(test)) for k, area, saw, test in cards)
    return ('<section id="ri-recs-firms"><div class="sec-head"><h2>Recommendations for the five firms</h2>\n'
            '<p class="dek">One test per firm, from the website, organic and paid comparisons of ' + DATE + '. Each is a proposal to test, not a promise of better results.</p></div>\n'
            '<div class="ri-rgrid">' + html + '</div></section>\n')


def put(body, name, html):
    a, b = '<!-- STRATEGY:%s START -->' % name, '<!-- STRATEGY:%s END -->' % name
    if body.count(a) != 1 or body.count(b) != 1:
        raise ValueError('Missing markers for ' + name)
    i, j = body.index(a) + len(a), body.index(b)
    return body[:i] + '\n' + html + body[j:]


def main():
    a, o, w = load('ads.json'), load('organic.json'), load('websites.json')
    body = open(BODY, encoding='utf-8').read()
    body = put(body, 'website', website_view(w))
    body = put(body, 'websrc', website_sources(w))
    body = put(body, 'organic', organic_section(o))
    body = put(body, 'orgsrc', organic_sources(o))
    body = put(body, 'paid', paid_section(a))
    body = put(body, 'paidsrc', paid_sources(a))
    body = put(body, 'recs', recs_section(a, o, w))
    body = put(body, 'roster', roster_note() + '\n')
    if re.search(r'[–—]', body.split('<!-- STRATEGY:website START -->')[1].split('<!-- STRATEGY:website END -->')[0]):
        raise ValueError('Dash in the website view')
    with open(BODY, 'w', encoding='utf-8') as f:
        f.write(body)
    print('Rendered the strategy comparison into report_body.html')


if __name__ == '__main__':
    main()
