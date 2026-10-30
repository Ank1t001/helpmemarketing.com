#!/usr/bin/env python3
"""Release preparation for the Business Cards & Spend Management Index.

  python3 release.py --dry-run OUTDIR --release-date YYYY-MM-DD
      Renders everything a release would change into OUTDIR (never into the repository):
      the live page (index, follow), the fixed edition snapshot, sitemap.xml and the
      /hmm-index hub, then runs the release checks and writes DRYRUN_REPORT.md with the
      diffs and every gate that still blocks release. The edition data is not changed.

  python3 release.py --apply
      Writes the same changes into the repository. Refuses unless edition.json already
      records the owner's release instruction (status published, approvals, published_at).
      Approvals are entered by hand from the owner's instruction; nothing here sets them.

Conventions followed (CLAUDE.md, Index pages): the snapshot lives at
/business-spend-index/edition-001 with its own canonical and one "noindex, follow", is not in
the sitemap, and is never rewritten; the live page carries no datePublished; dateModified is
added after the production deployment from its recorded ready time, in a metadata commit.
"""
import copy
import difflib
import json
import os
import re
import sys

import build
import model
import validate

SNAP_REL = 'business-spend-index/edition-%s.html'
HUB = 'hmm-index.html'
SITEMAP = 'sitemap.xml'
URL = 'https://helpmemarketing.com/business-spend-index'
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

# Hub wording that would no longer be true once a non-Instagram, unscheduled study is listed (owner's brief of 23 October 2026:
# umbrella title "The HMM Index: Marketing Research", the suggested description and source statement). Editorial proposals:
# the dry-run report lists every one, before and after, for the owner's approval. The cards' methods, dates and
# "Monthly" labels are not touched, nothing implies the studies share metrics, and nothing promises recurring updates.
OLD_DESC = 'Public Instagram benchmarks for Canadian private real estate, Ontario hair loss clinics and Ontario med spas. Built from public posts and refreshed monthly.'
SOCIAL_DESC = ('Independent research into how brands explain their products, publish content and guide prospective customers. '
               'Explore studies across real estate, hair loss, med spas and business spending.')   # 188 characters: social previews (200 max)
META_DESC = ('Independent research into how brands explain products, publish content and guide customers, '
             'across real estate, hair loss, med spas and business spending.')                    # 156 characters: meta description (158 max)


def hub_edits():
    return [
        # 1. Title (in <title>, og:title and twitter:title): "Instagram Benchmarks" implied every study is an Instagram study.
        ('The HMM Index: Instagram Benchmarks', 'The HMM Index: Marketing Research'),
        # 2. Meta description: the owner's suggested description, shortened by two words to fit 158 characters.
        ('<meta name="description" content="%s">' % OLD_DESC, '<meta name="description" content="%s">' % META_DESC),
        # 3 and 4. Social descriptions (og and twitter): the owner's suggested description in full.
        ('<meta property="og:description" content="%s">' % OLD_DESC, '<meta property="og:description" content="%s">' % SOCIAL_DESC),
        ('<meta name="twitter:description" content="%s">' % OLD_DESC, '<meta name="twitter:description" content="%s">' % SOCIAL_DESC),
        # 5. CollectionPage description (JSON-LD): the same full description.
        ('"description":"%s"' % OLD_DESC, '"description":"%s"' % SOCIAL_DESC),
        # 6. Hero subtitle: no single method or schedule is claimed for every study.
        ('<p class="hero-subtitle">Public benchmarks of what actually works on Instagram, one category at a time. Each edition is built from public posts, refreshed on a schedule, and every claim links to the post it came from.</p>',
         '<p class="hero-subtitle">Independent research, one category at a time, into how brands explain their products, publish content and guide prospective customers. Each study states its own method and update schedule.</p>'),
        # 7. Section heading: four studies, and "benchmarked" no longer fits a study that is not a benchmark.
        ('<h2 class="section-heading">Three categories, <em>benchmarked</em>.</h2>',
         '<h2 class="section-heading">Four categories, <em>researched</em>.</h2>'),
        # 8 to 10. How it works: each sentence said or implied that every study reads Instagram posts on the same signals.
        # Items 8 and 9: the owner's wording of 27 October 2026 (headings kept).
        ('<li><h3>Public data only</h3><p>I read what each business posts publicly on Instagram. No private data, no paid panels.</p></li>',
         '<li><h3>Public data only</h3><p>I review publicly available business content. The Instagram studies examine posts; the business card study examines websites, application and demo entry screens, and Instagram content. Each study explains its sources and access limitations.</p></li>'),
        ('<li><h3>Measured the same way</h3><p>Every account in an edition is read on the same public signals, such as likes, comments and recorded plays, so the comparison is consistent.</p></li>',
         '<li><h3>Consistent within each study</h3><p>Each study applies a shared checklist and records differences in coverage. The business card study separates product information, messaging, entry screens and Instagram observations. Missing evidence and unresolved account attribution are labelled. Figures from different studies are not compared.</p></li>'),
        ('<li><h3>Linked to the source</h3><p>Every claim points to the post behind it, so you can check it yourself.</p></li>',
         '<li><h3>Linked to the source</h3><p>Sources accompany the observations, with my interpretation labelled separately.</p></li>'),
    ]


HUB_EDITS = hub_edits()


def plain(h):
    m = re.match(r'<meta (?:name|property)="([^"]+)" content="([^"]*)">$', h)
    if m:
        return '%s: %s' % (m.group(1), m.group(2))
    h = h.replace('</h3><p>', ': ')
    t = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h)).strip()
    return re.sub(r'\s+([.,;:])', r'\1', t)


def hub_date(day):
    y, m, d = (int(x) for x in day.split('-'))
    return '%s %d, %d' % (MONTHS[m - 1], d, y)


# Owner's wording, 27 October 2026 (card text; the first sentence is also the hub's JSON-LD description of the page).
CARD_SENTENCE = ('How six selected platforms explain business cards, spend management and cross-border payments to Canadian businesses, '
                 'alongside a review of selected Canadian and global Instagram accounts.')


def hub_card(day):
    return ('      <article class="wk-tool ix-card">\n'
            '        <a class="wk-tool-shot" href="/business-spend-index" tabindex="-1" aria-hidden="true"><img src="/assets/index/business-spend/hero.webp" alt="" width="1056" height="591" loading="lazy" decoding="async"></a>\n'
            '        <div class="wk-tool-body">\n'
            '          <p class="wk-tool-kind">Comparison &middot; Canada &middot; One edition</p>\n'
            '          <h3 class="wk-tool-title">How Six Business Finance Brands Market Their Products</h3>\n'
            '          <p class="wk-tool-who">%s An independent case study from dated public sources, not a ranking or recommendation.</p>\n'
            '          <dl class="ix-dates"><div><dt>Last updated</dt><dd>%s</dd></div><div><dt>Next update</dt><dd>Not scheduled</dd></div></dl>\n'
            '          <div class="wk-tool-links"><a class="wk-tool-cta" href="/business-spend-index">Read the case study &rarr;</a></div>\n'
            '        </div>\n'
            '      </article>\n' % (CARD_SENTENCE, hub_date(day)))


def new_hub(text, day):
    issues = []
    for old, new in hub_edits():
        n = text.count(old)
        if n == 0:
            issues.append('hub: expected text not found (the hub changed?): %s' % old[:70])
        text = text.replace(old, new)
    anchor = '<a class="wk-tool-cta" href="/medspa-marketing-research">All medspa research</a></div>\n        </div>\n      </article>\n'
    if text.count(anchor) != 1:
        issues.append('hub: could not find the end of the Med Spa Index card')
    else:
        text = text.replace(anchor, anchor + hub_card(day))
    m = re.search(r'("hasPart":\[.*?)(\]\}\s*</script>)', text, re.S)
    if not m:
        issues.append('hub: CollectionPage hasPart not found')
    else:
        part = json.dumps({'@type': 'WebPage', 'name': 'How Six Business Finance Brands Market Their Products',
                           'description': CARD_SENTENCE,
                           'url': URL}, ensure_ascii=False, separators=(',', ':'))
        text = text[:m.end(1)] + ',' + part + text[m.end(1):]
    return text, issues


def new_sitemap(text, day):
    issues = []
    block = '  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n  </url>\n' % (URL, day)
    anchor = re.search(r'  <url>\n    <loc>https://helpmemarketing.com/medspa-index</loc>\n    <lastmod>[^<]*</lastmod>\n  </url>\n', text)
    if '<loc>%s</loc>' % URL in text:
        issues.append('sitemap: already lists the page')
    elif not anchor:
        issues.append('sitemap: Med Spa Index entry not found')
    else:
        text = text[:anchor.end()] + block + text[anchor.end():]
    text, n = re.subn(r'(<loc>https://helpmemarketing.com/hmm-index</loc>\s*<lastmod>)[^<]*(</lastmod>)', r'\g<1>%s\2' % day, text)
    if n != 1:
        issues.append('sitemap: hmm-index entry not found')
    return text, issues


def release_ctx(day):
    c = build.Ctx()
    c.edition = copy.deepcopy(c.edition)
    c.edition['status'] = 'published'
    c.edition['published_at'] = c.edition.get('published_at') or day
    c.release_date = day
    c.mode = 'release'   # so validate.check_inputs applies the release gates (the Instagram approval among them)
    return c


def render_all(day, strict):
    c = release_ctx(day)
    gate = validate.check_inputs(c)
    c.mode = 'release'
    live, csvtext, _ = build.render(c, 'release', strict=strict)
    c2 = release_ctx(day)
    snap, _, _ = build.render(c2, 'snapshot', strict=strict)
    snap_path = '/business-spend-index/edition-%s' % c.edition['edition']
    errs = ['release page: ' + e for e in validate.check_outputs(c, live, csvtext, extra_paths=(snap_path,))]
    errs += ['snapshot: ' + e for e in validate.check_outputs(c2, snap, csvtext, extra_paths=(snap_path,))]
    return c, gate, live, snap, csvtext, errs


def read(rel):
    with open(os.path.join(model.ROOT, rel), encoding='utf-8') as f:
        return f.read()


def udiff(rel, old, new, n=2):
    return ''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), 'a/' + rel, 'b/' + rel, n=n))


def dry_run(out, day):
    c, gate, live, snap, csvtext, errs = render_all(day, strict=False)
    hub, hub_issues = new_hub(read(HUB), day)
    sm, sm_issues = new_sitemap(read(SITEMAP), day)
    snap_rel = SNAP_REL % c.edition['edition']
    files = {'business-spend-index.html': live, snap_rel: snap, HUB: hub, SITEMAP: sm}
    for rel, text in files.items():
        p = os.path.join(out, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(text)
    diffs = {rel: udiff(rel, read(rel) if os.path.exists(os.path.join(model.ROOT, rel)) else '', text)
             for rel, text in files.items() if rel != snap_rel}
    for rel, d in diffs.items():
        with open(os.path.join(out, rel.replace('/', '_') + '.diff'), 'w', encoding='utf-8') as f:
            f.write(d)
    same_body = live[live.index('REPORT BODY START'):] == snap[snap.index('REPORT BODY START'):]
    lines = ['# Release dry run: Business Cards & Spend Management Index, edition %s' % c.edition['edition'], '',
             'Assumed release date: %s (Toronto). Nothing in the repository or edition.json was changed.' % day, '',
             '## Output checks', '']
    lines += ['- PASS: release page and snapshot checks'] if not errs else ['- FAIL: ' + e for e in errs]
    lines += ['- %s: snapshot body is identical to the release body' % ('PASS' if same_body else 'FAIL'),
              '- %s: sitemap and hub edits applied' % ('PASS' if not (hub_issues or sm_issues) else 'FAIL')]
    lines += ['- ' + x for x in hub_issues + sm_issues]
    lines += ['', '## Release gates still closed (from the edition data, as they should be until the owner decides)', '']
    lines += ['- ' + g for g in gate] or ['- none']
    lines += ['', '## Files a release would write', '']
    for rel, text in files.items():
        lines.append('- `%s` (%d bytes)%s' % (rel, len(text.encode()), ', new' if not os.path.exists(os.path.join(model.ROOT, rel)) else ''))
    lines += ['', '## Hub wording changes that need the owner\'s approval', '',
              'The umbrella title, description and source statement follow the owner\'s brief of 23 October 2026. Only wording that implied every study reads Instagram, shares the same signals or refreshes monthly is broadened; the three existing cards, their methods, dates and "Monthly" labels are unchanged, and nothing promises recurring updates for the business card study.', '']
    hub_now = read(HUB)
    for i, (old, new) in enumerate(hub_edits(), 1):
        lines += ['%d. Applies in %d place%s on /hmm-index.' % (i, hub_now.count(old), '' if hub_now.count(old) == 1 else 's'),
                  '   - was: %s' % plain(old), '   - now: %s' % plain(new)]
    lines += ['', 'The new card uses `/assets/index/business-spend/hero.webp` (1056x591, with a 704x394 variant), rendered from `artwork.html` in the Med Spa card pattern: text and outline shapes only, no provider screenshots or logos.', '']
    with open(os.path.join(out, 'DRYRUN_REPORT.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    return 1 if (errs or hub_issues or sm_issues or not same_body) else 0


def apply():
    c = build.Ctx()
    if c.edition['status'] != 'published':
        print('Refused: edition.json status is %r. Record the owner\'s release instruction first (status, approvals, published_at).' % c.edition['status'])
        return 1
    gate = validate.check_inputs(c)
    if gate:
        print('Refused:\n' + '\n'.join(gate))
        return 1
    day = c.edition['published_at'][:10]
    c, gate, live, snap, csvtext, errs = render_all(day, strict=True)
    if errs:
        print('Refused:\n' + '\n'.join(errs))
        return 1
    snap_rel = SNAP_REL % c.edition['edition']
    if os.path.exists(os.path.join(model.ROOT, snap_rel)) and read(snap_rel) != snap:
        print('Refused: %s exists and differs; a published snapshot is never rewritten.' % snap_rel)
        return 1
    hub, hi = new_hub(read(HUB), day)
    sm, si = new_sitemap(read(SITEMAP), day)
    if hi or si:
        print('Refused:\n' + '\n'.join(hi + si))
        return 1
    os.makedirs(os.path.join(model.ROOT, os.path.dirname(snap_rel)), exist_ok=True)
    out = [(build.PAGE, live), (os.path.join(model.ROOT, snap_rel), snap), (os.path.join(model.ROOT, HUB), hub),
           (os.path.join(model.ROOT, SITEMAP), sm), (build.CSV_PATH, csvtext)]
    if c.social:
        out.append((build.SOCIAL_CSV_PATH, build.social.render_csv(c.social)))
    for rel, text in out:
        with open(rel, 'w', encoding='utf-8') as f:
            f.write(text)
    print('Release files written. Review the diff, then commit.')
    return 0


def main(argv):
    if '--dry-run' in argv:
        out = argv[argv.index('--dry-run') + 1]
        if os.path.abspath(out).startswith(os.path.abspath(model.ROOT) + os.sep):
            print('Refused: the dry-run folder must be outside the repository.')
            return 2
        if '--release-date' not in argv:
            print(__doc__)
            return 2
        day = argv[argv.index('--release-date') + 1]
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', day):
            print('--release-date is YYYY-MM-DD')
            return 2
        return dry_run(out, day)
    if '--apply' in argv:
        return apply()
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
