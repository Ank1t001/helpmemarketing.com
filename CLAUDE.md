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

Vercel serves with `cleanUrls: true`, so links in-source point to `foo.html` but public URLs are `/foo`. Keep the `.html` suffix in HTML files when editing links — Vercel strips it at request time. `sitemap.xml` uses the clean-URL form.

## Design & Content Canon — READ BEFORE ANY PROTOTYPE-SCOPED PAGE WORK

For any work on `body.redesign-prototype`-scoped pages (homepage, /contact, future Phase 2 migrations), three canonical docs govern decisions. Read them in order before drafting any page brief:

1. `/docs/HMM_Design_System.md` — design canon (descriptive of homepage). Typography, spacing, grids, components, italic accent patterns, form pattern, forbidden patterns.
2. `/docs/HMM_Color_System.md` — color canon. Palette, tokens, 6 Golden Rules, 10 locked decisions.
3. `/docs/HMM_Content_Rules.md` — voice canon (DRAFT v0.2). Banned phrases, EEAT, structural rules, validation checklist.

These docs do **not** apply to legacy-scoped pages. They apply only inside body.redesign-prototype scope. (Both scopes are live on main; the distinction is CSS scope, not branch.)

### Forbidden in prototype scope (recap)

- Legacy color tokens (`--gold`, `--navy`, `--cream`, `--ivory`, `--deep`, `--ink-*`, `--line`, `--primary`, `--mint-soft`, `--white`)
- Inline `style="..."` attributes on prototype HTML elements. Forbidden by default. Tactical exceptions require explicit founder approval and an inline CSS comment explaining the rescue mechanism.
- Hardcoded hex values as property values — use tokens defined in Color System
- `<span style="color:...">` patterns for italic accents — use `<em>` or `<span class="me-italic">` per Design System Section 4
- `class="hero-h1"` on prototype H1s — use `class="hero-headline"`
- `class="italic-accent"` on prototype elements — use `<em>`
- Em-dashes (—) in any written content (Content Rules Section 2.3) — internal docs in `/docs/` are exempt because Google doesn't index them; site content is not

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
- **Logo:** "HMM" with italic Signal Orange "MM" using `<span class="me-italic">` pattern
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

## Architecture (both legacy and prototype)

### Page inventory and conventions

Every page is a standalone, fully self-contained HTML document. There is **no templating, no includes, no shared partials** — the nav and footer are copy-pasted into each page. When you change the nav, footer, or any shared UI element, you must update every `.html` file.

Each page shares this skeleton:

- Same `<head>`: Google Fonts (Fraunces + Inter) preconnect + link, then `<link rel="stylesheet" href="styles.css">`.
- `<div class="app" data-screen-label="{page-id}">` — the `data-screen-label` identifies the page type (`home`, `services`, `service-detail`, `contact`, `blog`, `pricing`, `privacy`, `terms`, `about`, `work`, `ad-calculator`, `hipaa-checklist`). Service-detail pages all share the label `service-detail`.
- `<nav class="nav">` + hidden `<div class="nav-mobile-menu">`, with a mobile hamburger toggle.
- `<div class="page-enter">` wraps the body content for the entry animation.
- Shared `<footer class="footer">`.

Prototype-scoped pages additionally set `<body class="redesign-prototype">` and use the F2 two-band footer pattern (see `/docs/HMM_Design_System.md` §8) instead of the legacy 4-column footer.

Active nav state is set manually per page by adding `.active` to the matching `<a class="nav-link">` in **both** the desktop nav (`.nav-links`) and the mobile menu (`.nav-mobile-menu`).

### Page groups

- **Top-level nav:** `index.html` (Home), `services.html` (Services hub), `work.html` (Case Studies), `about.html`
- **Service detail pages (legacy-scoped):** `healthcare-seo.html`, `google-meta-ads.html`, `clinic-websites.html`, `social-media.html`, `reputation.html`, `retention.html`, `analytics.html`, `brand.html`. All used `data-screen-label="service-detail"`. These legacy files have been removed; their old URLs now 301-redirect to the `/services/[category-slug]` category pages (see `vercel.json`).
- **Conversion / resources:** `contact.html`, `pricing.html`, `blog.html`, `hipaa-checklist.html`, `ad-calculator.html`
- **Legal:** `privacy.html`, `terms.html`

### Styling

All styles live in `styles.css`. The file has two distinct regions:

**Legacy region (lines 1-~3632):** Light-mode tokens (`--navy` `#1E4D8C`, `--gold`, `--cream`, `--ink-*`, etc.), permissive about inline styles. This is what legacy-scoped pages use.

**Prototype region (lines ~3633-4418):** Dark-mode tokens defined under `body.redesign-prototype` scope (`--bg`, `--text`, `--cta`, etc.). Strict scoping. This is what body.redesign-prototype-scoped pages use.

When editing styles for prototype pages, work inside the prototype region only. When editing styles for legacy pages, work outside it. Never mix the two systems on the same page.

Breakpoints in legacy CSS: 1200, 1100, 1000, 960, 900, 720, 680, 640, 560, 520.
Breakpoints in prototype CSS: 900 (primary), 720 (secondary). Don't introduce other breakpoints in prototype scope.

### JavaScript

No bundler, no shared JS file. JavaScript only exists in two places:

1. **`contact.html`** — vanilla IIFE that collects the form, builds a JSON payload, and `fetch`es it to a Google Apps Script web-app endpoint (`SHEET_URL`) with `mode: 'no-cors'`. On success the form is replaced with a thank-you panel; on failure an error banner points the user to `Hello@helpmemarketing.com`. Service chips are multi-select via a local `services` array. If you change the form fields, update the payload shape to match.
2. **`ad-calculator.html`** — vanilla IIFE with an in-file `BENCH` lookup of healthcare specialties → `{ cpl, convRate, ltv, label }`. Specialty buttons (`.sbtn[data-s]`) drive the calculation; inputs `#goal`, `#ltv`, `#conv` recompute budget/leads/ROAS on each change. All output goes into `#out-*` and `#row-*` elements — if you rename these, update both the markup and the `render()` function.

Elsewhere, the only JS is tiny inline event handlers (mobile-menu toggle). **Note for prototype work:** keep prototype HTML free of inline behavior — use `addEventListener` + `DOMContentLoaded` for any prototype-scoped JS. Legacy pages can keep their inline `onclick`.

### Deployment and SEO

- `vercel.json` sets `cleanUrls: true`, `trailingSlash: false`, adds `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `X-Frame-Options: SAMEORIGIN` on all responses, and caches `styles.css` for 1h (`must-revalidate`).
- `sitemap.xml` is hand-maintained — when adding or renaming a page, update it (use the clean-URL form without `.html`).
- `robots.txt` disallows both `/pricing` and `/pricing.html`. Keep `pricing.html` out of the sitemap too — it is reachable via CTAs but intentionally not indexed.

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

The reference blog implementing all V2 patterns is:
`/blog/healthcare-marketing-channels.html`

### Hero images
- Generated with nano-banana-pro skill
- 16:9, 2K, PNG, brand-aligned (muted gold + ivory)
- Stored at `/blog/images/[slug]-hero.png`
- JSON spec template in Part 6 Section B of master reference

### Voice rules (summary)
- Plain English; no banned phrases (leverage, unlock, supercharge, in today's fast-paced world, etc.)
- Sentence-case headings always
- Canadian spelling
- Second person ("you" + "we")
- See Part 1 Section B of master reference for full list

### Visual hierarchy
- H2: 22px / 500 weight / navy / 32px gold accent rule above
- Pull quotes: serif italic, gold left border, tinted background
- Featured tables: wrapped in `.featured-table-card`
- Featured conclusions: wrapped in `.featured-conclusion-card` with star marker
- Author bio: standard text in Part 1 Section D — update via single sweep when changes

### Standard internal linking floor
- 6+ internal links for posts 1,500+ words
- Standard slot positions in Part 2 Section D

### Common gotchas
- Cloudflare strips inline `onclick` — always use `addEventListener`
- "branches" in image specs reads as biological tree — use "ribbons" / "paths" / "strands"
- `position: sticky` parent must NOT have overflow set
- Don't propagate corrupted FAQ markup from older blogs (stray `<div class="related-and-cta">` inside FAQ items)

### Updating the template
When the template evolves (new pattern, voice rule change, layout shift), update `/docs/HMM_Blog_Template_V2_Master_Reference.md` in the same commit. Bump version + changelog at the bottom of the doc.

## Working style

Standard discipline for any non-trivial change:

1. **Audit-first.** Read the relevant files and diagnose before prescribing. Don't propose a fix until you understand the cascade.
2. **Checkpoint discipline.** For multi-step changes (especially Phase 2 migrations), pause at each checkpoint for founder approval before proceeding. Don't bundle.
3. **Single copy-pasteable briefs.** Briefs from the founder should be self-contained, no surrounding chat commentary above or below the brief content.
4. **Followup logging.** Known followups go in commit message footers AND in working memory. Update `/docs/HMM_Design_System.md` Section 15 (Open Items) when followups become permanent canon decisions.

## Common gotchas (prototype-specific)

- **Avoid inline `onclick` on prototype HTML.** Use `addEventListener` + `DOMContentLoaded` for consistency with the prototype's "no inline behavior" convention. (The legacy mobile-menu uses inline `onclick`; that's fine on legacy pages but not prototype-scoped ones.)
- `position: sticky` parents must NOT have overflow set. The blog sidebar broke once because of this.
- The `.app` wrapper paints white by default in legacy CSS. Prototype pages need `body.redesign-prototype .app { background: transparent }` (already shipped at commit `ce577a6`).
- Don't mix `hero-h1` and `hero-headline` classes. Legacy pages use `hero-h1`; prototype uses `hero-headline`. They have different CSS rules.
- Don't mix `.italic-accent` span and `<em>` patterns. Legacy uses `<span class="italic-accent">`; prototype uses `<em>`. Conflating them produces the `/contact` gold bug.
