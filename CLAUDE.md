# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A hand-written static marketing site for HelpMeMarketing (healthcare/clinic growth agency). No build step, no framework, no package manager, no JS toolchain — just HTML files, one shared `styles.css`, and a `vercel.json`. Deployed to Vercel.

## Dev / preview

There is nothing to install or build. To preview locally, serve the directory with any static server and open `index.html`:

```
python -m http.server 8000
```

Vercel serves the site with `cleanUrls: true`, so links in-source point to `foo.html` but the public URLs are `/foo`. When editing links, keep the `.html` suffix in HTML files — Vercel strips it at request time. `sitemap.xml` uses the clean-URL form.

## Architecture

### Page inventory and conventions

Every page is a standalone, fully self-contained HTML document. There is **no templating, no includes, no shared partials** — the nav and footer are copy-pasted into each page. When you change the nav, footer, or any shared UI element, you must update every `.html` file.

Each page shares this skeleton:
- Same `<head>`: Google Fonts (Fraunces + Inter) preconnect + link, then `<link rel="stylesheet" href="styles.css">`.
- `<div class="app" data-screen-label="{page-id}">` — the `data-screen-label` identifies the page type (`home`, `services`, `service-detail`, `contact`, `blog`, `pricing`, `privacy`, `terms`, `about`, `work`, `ad-calculator`, `hipaa-checklist`). Service-detail pages all share the label `service-detail`.
- `<nav class="nav">` + hidden `<div class="nav-mobile-menu">`, with a mobile hamburger toggled by an inline `onclick` handler that calls `classList.toggle('open')`.
- `<div class="page-enter">` wraps the body content for the entry animation.
- Shared `<footer class="footer">` with four columns + contact.

Active nav state is set manually per page by adding `.active` to the matching `<a class="nav-link">` in **both** the desktop nav (`.nav-links`) and the mobile menu (`.nav-mobile-menu`). Pages outside the four top-level sections (contact, blog, pricing, privacy, terms, etc.) leave no link marked active.

### Page groups

- **Top-level nav**: `index.html` (Home), `services.html` (Services hub), `work.html` (Case Studies), `about.html`.
- **Service detail pages** (linked from `services.html` cards and the footer): `healthcare-seo.html`, `google-meta-ads.html`, `clinic-websites.html`, `social-media.html`, `reputation.html`, `retention.html`, `analytics.html`, `brand.html`. All use `data-screen-label="service-detail"`.
- **Conversion / resources**: `contact.html`, `pricing.html`, `blog.html`, `hipaa-checklist.html`, `ad-calculator.html`.
- **Legal**: `privacy.html`, `terms.html`.

### Styling

All styles live in `styles.css` (~1k lines). A design-token block at the top of the file defines CSS custom properties — edit these to change the palette site-wide:

- Brand/primary: `--primary` (navy `#1E4D8C`), `--primary-dark`, `--deep`, `--deep-soft`
- Accents: `--mint`, `--mint-soft`, `--coral`, `--gold`, `--butter`, `--sand`
- Neutrals: `--cream`, `--cream-warm`, `--ink`/`--ink-60`/`--ink-40`/`--ink-80`, `--line`, `--line-soft`
- Surfaces: `--radius`, `--radius-lg`, `--shadow-sm`/`-md`/`-lg`

Inline `style="..."` attributes are used heavily throughout the HTML for page-specific layout tweaks — treat `styles.css` as the source of shared components (`.nav`, `.footer`, `.card`, `.btn-*`, `.pill`, `.eyebrow`, `.hero-card`, `.services-grid`, form classes, etc.), and inline styles as per-section overrides. Keep new shared components in `styles.css`; don't add inline styles for anything reused across pages.

Breakpoints in use (see `@media` rules): `1200`, `1100`, `1000`, `960`, `900`, `720`, `680`, `640`, `560`, `520`.

### JavaScript

There is no bundler and no shared JS file. JavaScript only exists in two places:

1. **`contact.html`** — vanilla IIFE that collects the form, builds a JSON payload, and `fetch`es it to a Google Apps Script web-app endpoint (`SHEET_URL`) with `mode: 'no-cors'`. On success the form is replaced with a thank-you panel; on failure an error banner points the user to `hello@helpmemarketing.com`. Service chips are multi-select via a local `services` array. If you change the form fields, update the payload shape to match.
2. **`ad-calculator.html`** — vanilla IIFE with an in-file `BENCH` lookup of healthcare specialties → `{ cpl, convRate, ltv, label }`. Specialty buttons (`.sbtn[data-s]`) drive the calculation; inputs `#goal`, `#ltv`, `#conv` recompute budget/leads/ROAS on each change. All output goes into `#out-*` and `#row-*` elements — if you rename these, update both the markup and the `render()` function.

Elsewhere, the only JS is tiny inline `onclick` attributes (mobile-menu toggle).

### Deployment and SEO

- `vercel.json` sets `cleanUrls: true`, `trailingSlash: false`, adds `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `X-Frame-Options: SAMEORIGIN` on all responses, and caches `styles.css` for 1h (`must-revalidate`).
- `sitemap.xml` is hand-maintained — when adding or renaming a page, update it (and use the clean-URL form without `.html`).
- `robots.txt` disallows both `/pricing` and `/pricing.html`. Keep `pricing.html` out of the sitemap too; it is reachable via CTAs but intentionally not indexed.

## When making changes

- **Navigation/footer edits must be applied to every `.html` file.** There is no partial — grep the change pattern across all pages and update each one.
- **New pages**: copy the structure of an existing similar page (service pages from `healthcare-seo.html`, marketing pages from `about.html`), set `data-screen-label` appropriately, add an entry to `sitemap.xml`, and decide whether robots.txt or internal links need updating.
- **Color/theme changes** go in the `:root` variable block in `styles.css` — don't hardcode hex values in HTML inline styles if a variable already covers it.
- **Forms that submit data** should follow the `contact.html` pattern (Google Apps Script endpoint + `no-cors` JSON POST + success/error UI swap) unless there's a reason to introduce a different backend.
