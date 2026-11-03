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
    rec = a['records']
    tot = a['library_totals']
    order = ['development offering', 'fund offer', 'registered accounts and tax', 'track record', 'investor event', 'investor education']
    rows, st_rows, ex = [], [], []
    info = {}
    for k in FIRMS:
        r = [x for x in rec if x['firm'] == k]
        inv = [x for x in r if x['for_investors']]
        info[k] = (r, inv)
        total = tot[k]['active']
        if not r:
            rows.append('<tr><td class="brandcell">%s</td><td class="r">0</td><td colspan="6" class="wrap-cell">%s</td></tr>' % (E(NAMES[k]), E(tot[k]['note'])))
            continue
        if not inv:
            rows.append('<tr><td class="brandcell">%s</td><td class="r">%d</td><td colspan="6" class="wrap-cell">All %d active ads are recruitment ads (&ldquo;%s&rdquo;), running since %s. '
                        'None was aimed at investors.</td></tr>' % (E(NAMES[k]), total, len(r), E(r[0]['headline']), E(min(x['start'] for x in r))))
            continue
        fc = collections.Counter(x['focus'] for x in inv)
        focus = ', '.join('%s (%d)' % (f, n) for f, n in fc.most_common(2))
        dest = collections.Counter(x['destination'] for x in inv).most_common(1)[0]
        n = len(inv)
        more = '' if tot[k].get('complete', True) else '<br><small>library total; %d read</small>' % len(r)
        rows.append('<tr><td class="brandcell">%s<br><small>%s</small></td><td class="r">%d%s</td><td class="wrap-cell">%s</td><td class="r">%s</td><td class="r">%s</td>'
                    '<td class="r">%s</td><td class="r">%s</td><td class="wrap-cell">%s (%d of %d)</td></tr>'
                    % (E(NAMES[k]), E(tot[k]['page']), total, more, E(focus), pct(sum(x['format'] == 'video' for x in inv), n),
                       pct(sum(x['return_figure'] for x in inv), n), pct(sum(x['registered_accounts'] for x in inv), n),
                       pct(sum(x['minimum'] for x in inv), n), E(dest[0]), dest[1], n))
        sc = collections.Counter(x['stage'] for x in inv)
        st_rows.append('<tr><td>%s</td>%s<td class="r">%d</td></tr>' % (E(NAMES[k]), ''.join('<td class="r">%d</td>' % sc.get(s, 0) for s in ('awareness', 'consideration', 'decision')), n))
        top = [x for x in inv if x['headline']][:1] or inv[:1]
        if top:
            x = sorted([y for y in inv if y['headline']] or inv, key=lambda y: (-y['versions'], y['start']))[0]
            ex.append('<li><b>%s</b>: &ldquo;%s&rdquo;, %s, running since %s. <a href="%s" target="_blank" rel="noopener nofollow">Open in the Ad Library</a></li>'
                      % (E(NAMES[k]), E(x['headline'] or 'untitled'), E(x['focus']), E(x['start']), E(x['library_url'])))
    eq_r, eq = info['Equiton']; sk_r, sk = info['Skyline']; la_r, la = info['Lankin']
    fc_e = collections.Counter(x['focus'] for x in eq)
    points = [
        'Three of the five firms had investor ads running in Canada on %s. No active ads matched Greybrook, and Centurion&rsquo;s four were recruitment ads.' % DATE,
        'Each ran a different message. Equiton&rsquo;s most common was its luxury development offering (%d of %d investor ads), headlined with a targeted return; '
        'Lankin&rsquo;s was registered accounts at year-end, RRSP and TFSA (%d of %d); Skyline promoted its funds one by one (%d of %d).'
        % (fc_e['development offering'], len(eq), collections.Counter(x['focus'] for x in la)['registered accounts and tax'], len(la),
           collections.Counter(x['focus'] for x in sk)['fund offer'], len(sk)),
        'Return figures appear in %s of Lankin&rsquo;s and %s of Equiton&rsquo;s investor ads, and in none of Skyline&rsquo;s, which describe &ldquo;historically stable returns&rdquo; instead.'
        % (pct(sum(x['return_figure'] for x in la), len(la)), pct(sum(x['return_figure'] for x in eq), len(eq))),
        'Most ads send people to a Meta link (fb.me) rather than the firm&rsquo;s site: all %d of Skyline&rsquo;s and %d of Equiton&rsquo;s %d. %d of Skyline&rsquo;s ads name a town (Oakville or Orangeville).'
        % (len(sk), sum(x['destination'] == 'Meta link (fb.me)' for x in eq), len(eq), sum(x['local'] for x in sk)),
        'Equiton also ran %s for a home sale and Skyline Living ran %d resident leasing ads; neither is counted as investor-facing.'
        % (plural(sum(1 for x in eq_r if not x['for_investors']), 'ad'), tot['Skyline Living (resident leasing)']['active'])]
    return ('<section id="ri-paid-compare"><div class="sec-head"><h2>Paid strategy compared</h2>\n'
            '<p class="dek">Active ads in the Meta Ad Library in Canada on ' + DATE + ', read for each firm&rsquo;s advertiser pages. The library shows that an ad is live; '
            'it does not show spend, reach or results.</p></div>\n' + roster_note() +
            '\n<div class="card ri-points"><h3>What stood out</h3><ul>' + ''.join('<li>%s</li>' % p for p in points) + '</ul></div>\n'
            '<div class="tw"><table class="ri-cmpt"><thead><tr><th>Firm</th><th class="r">Active ads</th><th>Main focus, investor ads</th><th class="r">Video</th>'
            '<th class="r">Return figure</th><th class="r">RRSP or TFSA</th><th class="r">Minimum named</th><th>Where ads send people</th></tr></thead><tbody>'
            + ''.join(rows) + '</tbody></table></div>\n'
            '<div class="tw"><table class="ri-cmpt ri-mix"><thead><tr><th>Likely buying stage, investor ads</th><th class="r">Awareness</th><th class="r">Consideration</th>'
            '<th class="r">Decision</th><th class="r">Ads</th></tr></thead><tbody>' + ''.join(st_rows) + '</tbody></table></div>\n'
            '<div class="card"><h3>One example per firm</h3><ul class="ri-ex">' + ''.join(ex) + '</ul></div>\n'
            '<div class="note"><span class="lbl">How the ads were read</span><p>%s Percentages are of each firm&rsquo;s investor-facing ads read; '
            'a stage is a reading of the ad&rsquo;s wording and call to action, not a measured result. Equiton&rsquo;s and Lankin&rsquo;s pages hold more ads than were returned; '
            'the library total is shown with the number read.</p></div></section>\n' % E(a['method']))


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
         'None of its %d ads states a return figure, %s names the $50,000 minimum that its own website shows, and every one sends people to a Meta link.'
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
    body = put(body, 'recs', recs_section(a, o, w))
    body = put(body, 'roster', roster_note() + '\n')
    if re.search(r'[–—]', body.split('<!-- STRATEGY:website START -->')[1].split('<!-- STRATEGY:website END -->')[0]):
        raise ValueError('Dash in the website view')
    with open(BODY, 'w', encoding='utf-8') as f:
        f.write(body)
    print('Rendered the strategy comparison into report_body.html')


if __name__ == '__main__':
    main()
