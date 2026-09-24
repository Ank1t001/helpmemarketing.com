# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A hand-written static marketing site for HelpMeMarketing — a premium generalist digital marketing agency based in Ontario, Canada, serving DTC, SaaS, healthcare, and finance brands across Canada and the US. No build step, no framework, no package manager, no JS toolchain — just HTML files, one shared `styles.css`, and a `vercel.json`. Deployed to Vercel.

## Site state

The dark redesign is live. main is the production site:

- **`main` branch** — serves the **dark redesign** to the public. This is what visitors currently see at helpmemarketing.com. It is the live, canonical site.
- **`redesign-prototype-homepage` branch** — a **frozen early-prototype pointer** (~40 commits behind main). The redesign already merged to main at commit `04cbc2a`. This branch is historical only; do not treat it as a live alternate or a merge source.

All current work targets main. The codebase contains two CSS systems (legacy-scoped pages and body.redesign-prototype-scoped pages), both live on main. When working on a page, **check which CSS scope the page uses**, not which branch.

## Dev / preview

Nothing to install or build. To preview locally, serve the directory with any static server and open `index.html`:

```
python -m http.server 8000
```

Vercel serves with `cleanUrls: true`, so **write links without the `.html` suffix** (`/services/seo`, `/blog/foo`, `/` for home). This is the sitewide convention every live page uses. Vercel serves `foo.html` at `/foo`, and a request to `/foo.html` 301-redirects to `/foo`, so a `.html` link only adds a needless redirect hop. Use absolute root-relative paths (`/services/seo`), not relative ones (`../services/seo`). `sitemap.xml` uses the same clean-URL form. (The old `_healthcare/*` archive and the `blog/meta-attribution.html` stub are gone; their old URLs redirect via `vercel.json`.)

## Design & Content Canon — READ BEFORE ANY PROTOTYPE-SCOPED PAGE WORK

For any work on `body.redesign-prototype`-scoped pages (homepage, /contact, future Phase 2 migrations), three canonical docs govern decisions. Read them in order before drafting any page brief:

1. `/docs/HMM_Design_System.md` — design canon (descriptive of homepage). Typography, spacing, grids, components, italic accent patterns, form pattern, forbidden patterns.
2. `/docs/HMM_Color_System.md` — color canon. Palette, tokens, 6 Golden Rules, 10 locked decisions.
3. `/docs/HMM_Content_Rules.md` — voice canon (DRAFT v0.2). Banned phrases, EEAT, structural rules, validation checklist.

These docs do **not** apply to legacy-scoped pages. They apply only inside body.redesign-prototype scope. (Both scopes are live on main; the distinction is CSS scope, not branch.)

### Forbidden in prototype scope (recap)

- Legacy color tokens (`--gold`, `--navy`, `--cream`, `--ivory`, `--deep`, `--ink-*`, `--line`, `--primary`, `--mint-soft`, `--white`)
- Inline `style="..."` attributes on prototype HTML elements. Forbidden by default. Tactical exceptions require explicit founder approval and an inline CSS comment explaining the rescue mechanism. As of 2026-09-18 no served page carries a `style` attribute at all: the GTM noscript iframe uses `class="gtm-ns"` (rule in `styles.css`), and the three Index pages' report bodies use scoped utility classes plus `data-w` for bar widths (see the Index generator contract below).
- Hardcoded hex values as property values — use tokens defined in Color System
- `<span style="color:...">` patterns for italic accents — use `<em>` or `<span class="me-italic">` per Design System Section 4
- `class="hero-h1"` on prototype H1s — use `class="hero-headline"`
- `class="italic-accent"` on prototype elements — use `<em>`
- Em-dashes (—) in any written content (Content Rules Section 2.3) — internal docs in `/docs/` are exempt because Google doesn't index them; site content is not

### Index generator contract (gta-medspa-index, hair-loss-index, instagram-reindex)

The report body between the REPORT BODY markers is regenerated each cycle; the head, nav, `.msi` wrapper and footer persist. The persistent head carries scoped utility classes and a `data-bar-widths` script, so the generator must emit these instead of `style` attributes:

- Bars: `<span class="bar-fill" data-w="59.5">` or `<span class="tbar" data-w="42">` (0 to 100; the head script sets the width, `[data-w]` starts at 0).
- Italic table cells: add `em` to the cell's class list. Zero margin paragraphs: `m0`. Zero top margin: `mt0`. Flex weights: `fx1`, `fx12` (1.2), `fx14` (1.4). Column widths: `w-26`, `w-52` (add a `w-N` rule to the head for any new value).
- Verdict badges: `verdict ok` (mint), `verdict avg` (tertiary), `verdict crit`. Navy panel: `card navy`. Fluid inline SVG: `svg.fluid`. Muted note paragraph: `pnote`, with `mb12` when it needs the 12px bottom margin.
- Frames: self-hosted 640x800 WebP under `/assets/index/<instance>/frames/`, never hotlinked (see the Design System note of 2026-09-18).
- Publish is a body swap only. The Build Kit's `build_v2.py` emits a standalone page on its own `_sys.css`; paste only the part between the REPORT BODY markers into the site page. The site head, nav, `.msi` wrapper and footer are the site's, not the kit's.
- The head is cycle-agnostic: no cycle number, refresh date, firm count or coverage claim in `<title>`, the descriptions or the schema (fixed 2026-09-24 after "cycle 001" sat in two heads through two cycles). Those facts live in the body.
- Frames are committed to the repo as `[firm]-cycleNNN.webp` for the cycle they were read in. The kit's step "re-host to WordPress media before publish" does not apply here; the repo is the host. Frames the kit could not read (over its 262,144-byte limit) get the unreviewed-read label in the body and no frame file.
- Real Estate Index, Instagram board from cycle 003 (24 Sep 2026): Skyline, Equiton, Lankin, Pier 4, McGillivray Capital. Marlin Spring left the Instagram board (stays on LinkedIn); Starlight, Centurion and Hazelview are not carried. Wealthsimple is an out-of-category reference and never appears on the board. Wording rule: a firm "has no corporate Instagram account", never "has no Instagram account" (Hazelview runs @hazelviewproperties). Cycle 004 is the first clean comparison against this board.

### Phase 2 page migration checklist

1. Read CLAUDE.md (this file)
2. Read `/docs/HMM_Design_System.md`
3. Read `/docs/HMM_Color_System.md`
4. Read `/docs/HMM_Content_Rules.md`
5. Audit target page's current HTML for forbidden patterns (legacy tokens, inline styles, legacy class names)
6. Plan migration brief referencing canon docs by section number
7. Apply audit-first checkpoint discipline (diagnose before prescribing)

### Locked Phase 2 architectural decisions

- **Service architecture (C1):** 6 categories — Performance Marketing, SEO + AEO, Branding & Social, Website Development, Analytics & Attribution, AI Automation & Workflow Systems
- **URL scheme:** `/services/[category-slug]` (no channel sub-pages; channels live as H2 sections inside category pages)
- **Footer pattern:** F2 two-band layout (brand+tools strip + sitemap strip). Spec in `/docs/HMM_Design_System.md` §8. (F1 3-column flat is deprecated.)
- **Form taxonomy:** 7 chips in buyer language — SEO | Ads | Brand & Social | Website | Analytics | Email & retention | Not sure yet
- **`data-service` attrs:** use category slugs (`performance-marketing`, `branding-social`, etc.)
  - **Note:** "Email & retention" chip routes to `data-service="lifecycle-retention"` for now. Service category was deprecated in Phase 2.5 (replaced by AI Automation & Workflow Systems), but the chip's data-service tag is retained as a routing label for the contact form payload. Implicit category bundling: leads from this chip are handled within existing service categories (Performance Marketing covers most email & lifecycle work). Backend routing label rename deferred to the next form-code commit.
- **Logo:** image mark (locked 2026-09-08; the text "H + italic MM" pattern is retired). Nav: `<img class="logo-img" src="/assets/brand/hmm-mark.svg">` (mark-only, 32px desktop / 28px at ≤900). Footer: `<img class="footer-logo" src="/assets/brand/hmm-logo-full.svg">` (full lockup, 150px, top of the CTA offer column). Always set `width`/`height` attributes on both so layout holds before CSS. Brand colours in the SVGs: off-white `#F7F6F2`, orange `#FF5A1F`.
- **Email casing:** `Hello@helpmemarketing.com` in visible UI; lowercase `hello@` acceptable in schema/metadata

### Phase 2.5 Sweep Decisions (locked 2026-05-25)

Phase 2.5 sweep brings nav + footer to canonical consistency across all 29 in-scope HTML pages. Decisions locked in planning session:

#### Decision 1 — Footer canon: F2 two-band

F2 replaces F1 as the canonical footer pattern. Two-band layout: brand + tools (upper) and sitemap + baseline (lower). Full spec in `/docs/HMM_Design_System.md` §8.

#### Decision 2 — Service architecture swap

AI Automation & Workflow Systems replaces Lifecycle & Retention as the 6th canonical service category. URL: `/services/ai-automation`. No legacy URL redirect (new category, no existing page).

Strategic context: Lifecycle & Retention was originally included to capture signal data for a potential future service launch. Founder decision to swap to AI Automation reflects evolving service offering and current demand signal.

#### Decision 3 — Labels and casing

Sitewide canon:
- "DTC" (not "DTC & E-commerce")
- "Case Studies" Title Case (not "Case studies")
- "© 2026 HelpMeMarketing" (drop "Inc.")
- `Hello@helpmemarketing.com` (capitalized H)

#### Decision 4 — Top nav stays unchanged

Home / Services / Case Studies / About + "Book a free audit" CTA. Blog stays in footer. Tools stay in footer (showcased in F2 upper band). No new top-nav items added during Phase 2.5.

#### Decision 5 — Sweep sequencing

1. Update canon docs (this commit)
2. Implement F2 on 3 prototype pages (homepage, /contact, /services) — separate session
3. Sweep 26 legacy pages to F2 + canonical nav in 2 batches:
   - Batch 1: 15 root pages
   - Batch 2: 11 nested/special pages (industries/*, services/seo, _healthcare/*, tools/*, industries/healthcare/*)

#### Decision 6 — Tool cards in F2 upper band

Two cards: Ad Spend Calculator (`/ad-calculator`) and Marketing Audit (`/tools/marketing-audit`). Both ship at footer rollout; Marketing Audit content is still in development but link resolves.

### Phase 2 progress

- ✓ Homepage prototype (Phase 1) — commits `0cc3e9d`, `b60ac6e`, `d232097`
- ✓ /contact migration — commits `d232097`, `ce577a6`, `27eb63b`
- ✓ Canon docs in repo — commits `bc2afd7` (Color), `0bfba56` (Content), `cad7398` (Design), `82fba35` (CLAUDE.md)
- ✓ /services overview page — commit `87d560c`
- ✓ Phase 2.5 sweep — F2 implementation + 26-page sweep complete
- ✓ /services/seo migration — shipped
- ✓ 5 remaining category pages — shipped (Performance Marketing, Branding & Social, Website Development, Analytics & Attribution, AI Automation & Workflow Systems)
- ✓ Redesign merged to `main` at `04cbc2a` (dark redesign production ship)

### Sitewide consistency pass (locked 2026-08-13)

Two prototype-scope canon changes, derived from auditing `/ad-set-calculator` as the reference page. Both are **global** (all `body.redesign-prototype` pages; blogs excluded — the blog `body.blog-dark` scope is untouched):

- **Vertical density tightened ~25%.** Canonical rhythm is now `.hero` `72px 0 40px` (mobile `56px 0 32px`), `section.content-section` `48px 0` (mobile `32px 0`), `.final-cta-section` `48px 0 0` (mobile top `32px`) — was 96/64. Set once in global `styles.css`; per-page hero/section padding overrides are no longer needed (removed from `/ad-set-calculator`). Spec in `/docs/HMM_Design_System.md` §5 ("Sitewide vertical density").
- **`--text-tertiary` AA lift:** `#737373` → `#8A8A8A` (WCAG AA ~4.9:1 on Obsidian). Global prototype token; page-local override on `/ad-set-calculator` removed. Extended to `body.blog-dark` and the Index pages on 2026-09-09, so the lift is now sitewide. See `/docs/HMM_Color_System.md` Decision 11.
- **Functional-Mint pass (positive results = Mint):** positive-result figures now render in `var(--mint)` across results-bearing pages, matching the `/ad-set-calculator` treatment and replacing three inconsistent prior colors (emerald `#10B981` on industry deltas, off-canon blue `#2563EB` on industry sparklines, Signal Orange on `work.html` case/proof figures). Components: `.case-study-metric` + `.proof-strip-figure` (work), `.pm-proof-stat` (performance-marketing), `.metric-delta` + `.metric-sparkline` (industry pages, scoped). Figures only — labels stay muted, big neutral numbers stay white, Mint never a CTA. See `/docs/HMM_Color_System.md` Decision 12.

## Architecture (both legacy and prototype)

### Page inventory and conventions

Every page is a standalone, fully self-contained HTML document. There is **no templating, no includes, no shared partials** — the nav and footer are copy-pasted into each page. When you change the nav, footer, or any shared UI element, you must update every `.html` file.

Each page shares this skeleton:

- Same `<head>`: two font preloads (`/assets/fonts/fraunces-latin.woff2`, `/assets/fonts/inter-latin.woff2`, `as="font" crossorigin`), then `<link rel="stylesheet" href="/styles.css">`. Fonts are self-hosted since 2026-09-16: the `@font-face` block at the top of `styles.css` serves Fraunces (variable, 400 to 500 upright, 400 italic) and Inter (variable, 400 to 700) in latin and latin-ext from `/assets/fonts`. No Google Fonts link or preconnect on any page.
- `<div class="app" data-screen-label="{page-id}">` — the `data-screen-label` identifies the page type (`home`, `services`, `service-detail`, `contact`, `blog`, `privacy`, `terms`, `about`, `work`, `ad-calculator`, `hipaa-checklist`). Service-detail pages all share the label `service-detail`.
- `<nav class="nav">` + hidden `<div class="nav-mobile-menu">`, with a mobile hamburger toggle.
- `<div class="page-enter">` wraps the body content for the entry animation.
- Shared `<footer class="footer">`.

Prototype-scoped pages additionally set `<body class="redesign-prototype">` and use the F2 two-band footer pattern (see `/docs/HMM_Design_System.md` §8) instead of the legacy 4-column footer.

Active nav state is set manually per page by adding `.active` to the matching `<a class="nav-link">` in **both** the desktop nav (`.nav-links`) and the mobile menu (`.nav-mobile-menu`).

### Page groups

- **Top-level nav:** `index.html` (Home), `services.html` (Services hub), `work.html` (Case Studies), `about.html`
- **Service detail pages (legacy-scoped):** `healthcare-seo.html`, `google-meta-ads.html`, `clinic-websites.html`, `social-media.html`, `reputation.html`, `retention.html`, `analytics.html`, `brand.html`. All used `data-screen-label="service-detail"`. These legacy files have been removed; their old URLs now 301-redirect to the `/services/[category-slug]` category pages (see `vercel.json`).
- **Conversion / resources:** `contact.html`, `blog.html`, `hipaa-checklist.html`, `ad-calculator.html`
- **Legal:** `privacy.html`, `terms.html`

### Styling

All styles live in `styles.css`. The file has two distinct regions:

**Legacy region (after the `@font-face` block, up to the `BLOG TEMPLATE V2` header, ~line 869):** Light-mode tokens (`--navy` `#1E4D8C`, `--gold`, `--cream`, `--ink-*`, etc.), permissive about inline styles. This is what legacy-scoped pages use. Trimmed the same way as the other two regions on 2026-09-18 (one-line comment headers, no overridden declarations); it is 26KB and carries the shared nav and footer base rules every page still uses.

**Blog region (`BLOG TEMPLATE V2` header to `body.redesign-prototype {`, ~lines 869-3651):** the `body.blog-dark` template, plus the marketing-audit tool block that sits between them. Comments in this region are one-line headers; the history behind each block lives in the Master Reference and Design System, not in the stylesheet. **Prototype region (from `body.redesign-prototype {`, ~line 3651, to end of file):** Dark-mode tokens defined under `body.redesign-prototype` scope (`--bg`, `--text`, `--cta`, etc.). Strict scoping. This is what body.redesign-prototype-scoped pages use. Comments here are one-line headers too, with eleven kept in full because they record a founder decision, a deprecation, or the rescue mechanism behind an approved inline-style exception (token shimming, the CTA colour rule, the F2 footer spec); keep those, and put new history in the Design System rather than the stylesheet.

When editing styles for prototype pages, work inside the prototype region only. When editing styles for legacy pages, work outside it. Never mix the two systems on the same page.

Breakpoints in legacy CSS: 1200, 1100, 1000, 960, 900, 720, 680, 640, 560, 520.
Breakpoints in prototype CSS: 900 (primary), 720 (secondary). Don't introduce other breakpoints in prototype scope.

### JavaScript

No bundler. Two small shared files load on every page with `defer`: `/consent.js` (cookie banner) and `/site.js` (the mobile nav: hamburger toggle with `aria-expanded`, close on link tap, Escape and outside click; added 2026-09-18 when the last inline `onclick` came out). Page features live in their own scripts:

1. **`contact.html`** — vanilla IIFE that collects the form, builds a JSON payload, and `fetch`es it to a Google Apps Script web-app endpoint (`SHEET_URL`) with `mode: 'no-cors'`. On success the form is replaced with a thank-you panel; on failure an error banner points the user to `Hello@helpmemarketing.com`. Service chips are multi-select via a local `services` array. If you change the form fields, update the payload shape to match.
2. **`ad-calculator.html`** — vanilla IIFE with an in-file `BENCH` lookup of healthcare specialties → `{ cpl, convRate, ltv, label }`. Specialty buttons (`.sbtn[data-s]`) drive the calculation; inputs `#goal`, `#ltv`, `#conv` recompute budget/leads/ROAS on each change. All output goes into `#out-*` and `#row-*` elements — if you rename these, update both the markup and the `render()` function.

No page carries an inline event handler attribute (`onclick` etc.) as of 2026-09-18. Use `addEventListener` + `DOMContentLoaded` for any new behaviour, on every page, and put sitewide chrome behaviour in `site.js`.

### Deployment and SEO

- `vercel.json` sets `cleanUrls: true`, `trailingSlash: false`, adds `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `X-Frame-Options: SAMEORIGIN` on all responses, and serves `styles.css` with `max-age=600, must-revalidate` (returning visitors reuse it for 10 minutes without a round trip, then revalidate; a CSS change reaches them within 10 minutes) and `/assets/fonts/*` immutable for a year. Note the `.html` request form never reaches a redirect: `cleanUrls` 308s `/foo.html` to `/foo` first, so redirects are written for the extensionless path only. Internal files are kept out of the deployment by `.vercelignore`, not by rewrites.
- **Brand assets (2026-09-08):** `/favicon.ico` (16 and 32 frames only, 5KB; `sizes="16x16 32x32"` on its link) + `/favicon-32x32.png` (0.6KB, already optimal), `/favicon-192x192.png` (apple-touch, 256-colour palette PNG, 5.6KB since 2026-09-18), linked from every page `<head>` (a 512px file existed but nothing linked it and there is no web manifest; removed 2026-09-17); `/og-image.jpg` (1200×630 JPEG, 33KB; was a 253KB PNG until 2026-09-18) is the default `og:image`/`twitter:image` on the seven pages without their own (blog posts and most landing pages keep their own OG); `/logo.jpg` (400×400 JPEG, 7.6KB; was a 35KB PNG until 2026-09-18) is the schema `logo`/`image`, fetched only by crawlers. Source package: HMM_Logo_Package.
- `styles.css` was pruned on 2026-09-16 (578 dead rules, 275KB to 212KB). Dead means the selector requires a class or id that appears in no served HTML file and no JS string literal. Re-run the same check before adding CSS back for a retired component; see `/docs/HMM_Design_System.md` (CSS trim note) for the method.
- `sitemap.xml` is hand-maintained — when adding or renaming a page, update it (use the clean-URL form without `.html`). Entries carry `loc` and `lastmod` only (`changefreq` and `priority` are ignored by Google and Bing and were dropped on 2026-09-17). `lastmod` must be true or search engines ignore it: it is the date of the last commit that touched the page's file. Refresh every entry after a sweep with:

  ```
  python3 -c "import re,subprocess;s=open('sitemap.xml').read();print(re.sub(r'<loc>(.*?)</loc>\s*<lastmod>.*?</lastmod>',lambda m:m.group(0).replace(re.search(r'<lastmod>(.*?)</lastmod>',m.group(0)).group(1),subprocess.run(['git','log','-1','--format=%as','--',('index.html' if m.group(1).endswith('.com/') else m.group(1).split('.com/')[1]+'.html')],capture_output=True,text=True).stdout.strip()),s),end='')" > sitemap.new && mv sitemap.new sitemap.xml
  ```

- **Titles, descriptions and social copy (audited 2026-09-18):** `<title>` 30 to 60 characters, Title Case, ending ` | HelpMeMarketing` on pages where that fits (posts never carry it; four pages whose descriptive title already fills the budget do not either). `<meta name="description">` 70 to 158 characters, plain sentences, no em dashes, no banned phrases. `og:title` is the title without the brand suffix (`og:site_name` already carries the brand; the homepage uses `HelpMeMarketing: AI-Native Marketing Agency, Ontario`), `twitter:title` equals `og:title`, `twitter:description` equals `og:description`, and `og:description` may be a shorter social variant of the meta description but never over 200 characters. The brand is written `HelpMeMarketing` in every title and card; `Help Me Marketing Inc.` appears only as the legal entity on the legal pages. No two pages share a title or a description.
- **JSON-LD (129 blocks across 48 pages, audited 2026-09-18):** every page carries a `BreadcrumbList`; posts carry `BlogPosting` + `FAQPage`; service, industry and tool pages carry their type + `FAQPage`. Rules that the audit enforces: every block parses; every URL and image in a block resolves to a served page or file (no redirected URLs); `headline` equals the visible H1 (sentence case, no trailing period, under 110 characters); `datePublished` equals `article:published_time`; `dateModified` is editorial and matches the post's visible "Updated" line, not the last commit; every `FAQPage` question is a visible `<summary>` on the page; the last breadcrumb is the page itself. Re-run the check in `/docs/HMM_Design_System.md` (JSON-LD audit note) after touching a head.
- `robots.txt` is a single wildcard allow plus the sitemap line. Per-bot blocks that repeat the wildcard change nothing; add a block only to disallow something for a specific crawler.
- `pricing.html` was removed (commit `b80babb`); `/pricing` and `/pricing.html` now 301-redirect to `/contact` (see `vercel.json`). No pricing entry remains in `robots.txt` or `sitemap.xml`.

## When making changes

### For legacy-scoped pages

- Use legacy tokens (`--navy`, `--gold`, etc.). Don't introduce prototype tokens.
- Inline styles are tolerated where the existing page uses them.
- Follow the existing 4-column footer pattern.
- Navigation/footer edits must be applied to every `.html` file in scope.

### For prototype-scoped pages (body.redesign-prototype)

- Read the three canon docs first. No exceptions.
- Use prototype tokens only. Never legacy tokens.
- Inline `style="..."` attributes forbidden by default. Tactical exceptions require explicit founder approval and an inline CSS comment.
- Follow the F2 footer pattern (see `/docs/HMM_Design_System.md` §8).
- All new components and patterns must be added to `/docs/HMM_Design_System.md` in the same commit.

### Universal (both systems)

- **New pages:** copy the structure of an existing similar page that uses the same system (legacy or prototype). Set `data-screen-label` appropriately, add an entry to `sitemap.xml`, decide whether `robots.txt` or internal links need updating.
- **Page hero images (not blog):** two WebP files per hero, `name.webp` 1056x591 and `name-704.webp` 704x394, both quality 80. The tag carries `width="1056" height="591"`, `srcset="/path/name-704.webp 704w, /path/name.webp 1056w"` and `sizes="(max-width: 900px) calc(100vw - 40px), 522px"`; the hero never renders wider than 522 CSS px, so 1056 covers 2x screens and 704 covers phones. The Index pages use the 1056 file as a CSS background. Keep the homepage preload's `imagesrcset`/`imagesizes` in step with the tag.
- **Forms that submit data** should follow the `contact.html` pattern (Google Apps Script endpoint + `no-cors` JSON POST + success/error UI swap) unless there's a reason to introduce a different backend.

## Blog template

All blog work follows the V2 D-hybrid template (sticky TOC sidebar, featured cards, hero image workflow). Master reference at:

`/docs/HMM_Blog_Template_V2_Master_Reference.md`

When asked to write a new blog or retrofit an existing one:

1. Read the master reference first
2. Follow the 5-question confirm-before-writing checklist (Part 1 Section A)
3. Apply 6-element rule per H2 section (Part 1 Section C)
4. Use V2 visual template (Part 3) — sticky TOC sidebar, featured cards, mobile collapsible TOC
5. Reference shared CSS in `styles.css` under the `BLOG TEMPLATE V2 — D-HYBRID LAYOUT` section header
6. Reference shared JS at `/blog/blog-template.js`
7. Use 5-checkpoint discipline for all builds (Part 7 Section C)
8. Add the post's card to `blog.html` (plus a filter chip if it's a new category), folded into the same Claude Code build at CP4/CP5 — not a separate follow-up. Two posts shipped unlisted this session when this step was missed.

The reference blog implementing all V2 patterns is:
`/blog/healthcare-marketing-channels.html`

### Hero images
- Generated tool-agnostic: nano-banana-pro skill (in-build) or Higgsfield/Recraft connector (generate, then hand off the PNG)
- 16:9, 2K, PNG master kept local. Default aesthetic: dark obsidian + Signal Orange (canonical); muted gold + ivory is an acceptable alternative
- Committed as three derivatives: `/blog/images/[slug]-hero.webp` (1344 wide, the desktop page image), `/blog/images/[slug]-hero-720.webp` (720 wide, the phone candidate; both sit in the hero's and the index card's `srcset`, see the Master Reference) and `/blog/images/[slug]-og.jpg` (1200x630, `og:image`, `twitter:image`, schema `image`). No PNG in the repo (2026-09-17)
- JSON spec template in Part 6 Section B of master reference

### Voice rules (summary)
- Plain English; no banned phrases (leverage, unlock, supercharge, in today's fast-paced world, etc.)
- Sentence-case headings always
- Canadian spelling
- Second person ("you" + "we")
- See Part 1 Section B of master reference for full list

### Visual hierarchy
- H2: Fraunces 28px / 500 weight / var(--text) / 36px Signal Orange (var(--cta)) accent rule above, 48px above and 20px below
- Body copy: var(--text-body) (78% white, Colour System Decision 13) for paragraphs, list items and FAQ answers; var(--text-muted) for subtitles, captions and meta
- Pull quotes: Fraunces italic 20px, Signal Orange (var(--cta)) left border, 8% orange tint (rgba(255,92,26,0.08)), radius 0 12px 12px 0
- Diagram titles: canonical eyebrow (Inter 13px uppercase, var(--text-muted)); icons are inline Tabler SVGs, never emoji
- Featured tables: wrapped in `.featured-table-card`
- Featured conclusions: wrapped in `.featured-conclusion-card` with star marker
- Author bio: standard text in Part 1 Section D — update via single sweep when changes

### Standard internal linking floor
- 6+ internal links for posts 1,500+ words
- Standard slot positions in Part 2 Section D

### Common gotchas
- Use `addEventListener` (not inline `onclick`) for blog JS — a consistency convention, not a platform constraint. The site is pure Vercel; the old "Cloudflare strips onclick" note was stale.
- "branches" in image specs reads as biological tree — use "ribbons" / "paths" / "strands"
- `position: sticky` parent must NOT have overflow set
- Don't propagate corrupted FAQ markup from older blogs (stray `<div class="related-and-cta">` inside FAQ items)
- Post shipped but missing from `/blog`: add the post's `blog.html` index card during the build (CP4/CP5), not as a follow-up

### Updating the template
When the template evolves (new pattern, voice rule change, layout shift), update `/docs/HMM_Blog_Template_V2_Master_Reference.md` in the same commit. Bump version + changelog at the bottom of the doc.

## Working style

Standard discipline for any non-trivial change:

1. **Audit-first.** Read the relevant files and diagnose before prescribing. Don't propose a fix until you understand the cascade.
2. **Checkpoint discipline.** For multi-step changes (especially Phase 2 migrations), pause at each checkpoint for founder approval before proceeding. Don't bundle.
3. **Single copy-pasteable briefs.** Briefs from the founder should be self-contained, no surrounding chat commentary above or below the brief content.
4. **Followup logging.** Known followups go in commit message footers AND in working memory. Update `/docs/HMM_Design_System.md` Section 15 (Open Items) when followups become permanent canon decisions.

## Common gotchas (prototype-specific)

- **No inline `onclick` anywhere.** Use `addEventListener` + `DOMContentLoaded`. The mobile menu is handled by `site.js` on every page; the hamburger markup is `<button class="nav-hamburger" type="button" aria-label="Menu" aria-expanded="false" aria-controls="nav-mobile-menu">` and the menu div carries `id="nav-mobile-menu"`.
- `position: sticky` parents must NOT have overflow set. The blog sidebar broke once because of this.
- The `.app` wrapper paints white by default in legacy CSS. Prototype pages need `body.redesign-prototype .app { background: transparent }` (already shipped at commit `ce577a6`).
- Don't mix `hero-h1` and `hero-headline` classes. Legacy pages use `hero-h1`; prototype uses `hero-headline`. They have different CSS rules.
- Don't mix `.italic-accent` span and `<em>` patterns. Legacy uses `<span class="italic-accent">`; prototype uses `<em>`. Conflating them produces the `/contact` gold bug.
