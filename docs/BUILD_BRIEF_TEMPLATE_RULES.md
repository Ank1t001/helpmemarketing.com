# Build Brief Template Rules

**Purpose:** Canonical rules for authoring service-page build briefs (#3 through #10 in the pricing rebuild sprint). Decisions in this doc are locked from the proof-of-concept build of `/services/seo` (Brief #2, commit lands in Step 6).

**Status:** Living document. Update when new template rules emerge.
**Created:** 2026-05-15

---

## Rule 1 — H1 length and treatment

**Rule:** Hero H1 must be **5-7 words max**, brand-voiced (not SEO-stuffed), with **exactly one** `italic-accent` word.

**Why:** The brief author's instinct is to cram primary keyword + secondary + geo into the H1. At the brand's hero h1 sizing (`clamp(48px, 6.5vw, 84px)`, max 84px), anything longer than ~7 words wraps to 3-4 lines and looks awkward. Modern Google semantic search picks up keywords from H2/subhead with the same weight as H1 — the H1 doesn't need to carry the keyword load.

**Pattern:**
- `/seo.html`: "Editorial *SEO* that fills pipelines."
- `/website-design.html`: "Websites that *convert*, not just impress."
- `/services/seo` (new): "SEO that *compounds*, not chases."

**How to apply:** Brief authors write the H1 in brand voice (5-7 words). Keyword targeting moves to the subhead/H2 + body content. The italic-accent word should be the load-bearing differentiator (the verb or noun that, if removed, would change the headline's meaning most).

---

## Rule 2 — FAQ summary markup must include the icon span

**Rule:** Every `<details class="faq-item"><summary>` must include `<span class="faq-icon" aria-hidden="true">+</span>` immediately before `</summary>`.

**Why:** The existing `.faq-item[open] .faq-icon { transform: rotate(45deg); }` rule in styles.css depends on this span. Without it, the open/close affordance is invisible. The CSS could be refactored to use `::after` instead, but a sitewide audit of `.faq-item` usage is needed first — deferred to a separate cleanup.

**Pattern:**
```html
<details class="faq-item">
  <summary>How long does SEO take to show results?<span class="faq-icon" aria-hidden="true">+</span></summary>
  <p>Meaningful SEO ranking shifts typically take 6-12 months...</p>
</details>
```

**How to apply:** Brief authors include the span in every FAQ summary. If you forget, the FAQ visually breaks — the icon span is load-bearing.

---

## Rule 3 — Hero image dimensions are locked

**Rule:** Service-page hero images are **1920×1072 px PNG, <900 KB**. HTML attrs: `width="1920" height="1072"`.

**Why:** Established in Brief #2 Step 2 after testing. 1920 wide is 3× retina-safe for the ~640 px CSS hero slot. Going higher (3000 px source) busts the file-size cap or requires aggressive palette quantization with visible artifacts on photo-realistic content. 4K source is generated and archived in Image_Studio for future re-use at different targets.

**Pattern:**
```html
<img src="/blog/images/services-[name]-hero.png"
     alt="..."
     loading="eager"
     width="1920"
     height="1072">
```

**How to apply:** Brief authors specify `width="1920" height="1072"`. Image-generation step downscales the 4K source to 1920×1072 and compresses to <900 KB via PIL 64-color palette quantization (see Brief #2 Step 2 for the compression chain).

---

## Rule 4 — REMAPs are locked: use existing class names natively

**Rule:** Briefs must use these existing classes natively. Do NOT invent parallel class names that have to be remapped later.

| Don't write | Write instead | Why |
|---|---|---|
| `<p class="hero-eyebrow">Service Name</p>` | `<span class="eyebrow"><span class="eyebrow-dot"></span>Service Name</span>` | Existing site convention; styled at line 179 of styles.css |
| `<p class="hero-deck">...</p>` | `<p class="hero-subtitle">...</p>` | Existing class at line 1382 |
| `<div class="hero-cta">...</div>` | `<div class="hero-ctas-row">...</div>` | Existing class at line 1386 |
| `class="btn btn-secondary"` | `class="btn btn-outline"` | `.btn-outline` exists at line 158; site has no `.btn-secondary` |
| `<div class="hero-visual">` (single image) | `<div class="services-hero-visual">` | Existing `.hero-visual` is a 2-col metric-card grid; this is a separate single-image variant |

**Why:** Brief #2 surfaced 5 class names that the brief invented but that didn't exist in styles.css. Each one required either a CSS addition or a remap. Locking these now means the next 8 briefs go straight to code without remapping.

**How to apply:** Brief author copies the "Use these class names" column verbatim into the brief's HTML examples.

---

## Rule 6 — Prose consistency with brand positioning

**Rule:** When prose lists specific industries, verticals, or use cases, verify the list against HMM's broader positioning doc (DESIGN.md, homepage, services hub) to avoid implying exclusion of verticals HMM actually serves.

**Why:** HMM serves four verticals: DTC, SaaS, Healthcare, Finance. Prose that names three of them (e.g., "healthcare practices, DTC brands, and SaaS companies") can read as exhaustive if framed wrong. Wording like *"we currently focus on..."* or *"the verticals we serve are..."* implies exclusivity — Finance buyers reading the page would feel un-served.

**Right framings (non-exclusionary):**
- "whether that's healthcare practices, DTC brands, or SaaS companies" — examples, not list
- "this applies across healthcare practices, DTC brands, and SaaS companies" — application examples
- "for industries like healthcare, DTC, and SaaS" — explicit "like" hedge
- "for example, healthcare practices, DTC brands, and SaaS companies" — explicit example marker

**Wrong framings (read as exclusionary):**
- "we currently focus on healthcare practices, DTC brands, and SaaS companies" — implies these only
- "the verticals we serve include..." — depending on context, can read as closed list
- "for healthcare practices, DTC brands, and SaaS companies, [X] differs" — leading-with-list can imply scope is just these three

**How to apply:** Brief authors writing prose with industry lists pause and ask: *"If a Finance buyer read this sentence, would they feel HMM is for them?"* If the answer is no, restructure.

Surfaced in Brief #2 Section 4 prose review (initial Option C draft used "we currently focus on" — caught during review, revised to "this applies across").

---

## Rule 5 — Path conventions (interim until Brief #10)

**Rule for nested `/services/[name]/` pages:**

- **Body content internal links (`<a href>` to other services, industries, blog, contact)** → absolute clean URLs starting with `/`. Examples: `/contact`, `/services/google-ads-management`, `/industries/healthcare`, `/blog/seo-ppc-or-social`.
- **Nav and footer links to root-level pages** → relative `../` paths. Examples: `../index.html`, `../about.html`, `../seo.html`, `../industries/dtc.html`.
- **Same-page anchors** → `#anchor-id`. Examples: `#tiers`.
- **Hero image src** → absolute path starting with `/`. Example: `/blog/images/services-seo-hero.png`.

**Why:** Nested pages can't use the root-level relative paths that existing service pages use (`index.html` from `/services/seo` resolves to `/services/index.html` — 404). Until Brief #10 converts nav/footer site-wide to absolute paths, services pages use this hybrid.

**How to apply:** Brief authors specify body links as absolute URLs. Nav/footer markup is copied from the proof-of-concept `services/seo.html` with `../` paths already in place.

---

## Required sections (the 12-section template)

Every service page must include these sections in order. Established in Brief #2.

| # | Section | Wrapper class | Notes |
|---|---|---|---|
| 1 | Hero | `<section class="hero-zone services-hero">` | eyebrow + h1 + subtitle + 2 CTAs + image |
| 2 | "Why [intro positioning]" h2 | `<section class="prose-block">` | 3-paragraph industry framing |
| 3 | "How we approach [local/specific facet]" h2 | `<section class="prose-block">` | Body + 4-item ordered list + closing paragraph (often the natural place for a service↔service inline link) |
| 4 | "[Differentiator concept]" h2 | `<section class="prose-block">` | Body + 4-item unordered list + closing paragraph (often the natural place for service↔industry inline links) |
| 5 | "Three engagement tiers" h2 | `<section class="tiers-section" id="tiers">` | `.tier-card-grid` with 3 `.tier-card` (Foundation / Growth / Scale) |
| 6 | "What this looks like in practice" h2 | `<section class="outcomes-section">` | `.outcome-grid` with 3 `.outcome-card` (one per tier) |
| 7 | "About our pricing" | `<section class="disclosure-section">` | 1× `.disclosure-card` |
| 8 | "Terms & commitment" h2 | `<section class="prose-block">` | 2 paragraphs |
| 9 | "Not for you if" h2 | `<section class="prose-block">` | `.caveat-list` with 4 items |
| 10 | "Frequently asked questions" h2 | `<section class="faq-section">` | 5× `<details class="faq-item">` — must match FAQPage schema exactly |
| 10b | "Related reading" h2 | `<section class="related-reading">` | `.related-grid` with 3× `.related-card` linking to blog |
| 11 | "Ready to [start]?" h2 | `<section class="final-cta">` | 2 CTAs (primary + outline) |

---

## Internal link plan (target: 12 links per page)

Brief #2 established this distribution. Future briefs replicate the pattern.

| Where | Count | Pattern |
|---|---|---|
| Hero CTAs | 2 | `Book a free [service] audit` → `/contact` + `See pricing tiers` → `#tiers` |
| Section 3 closing paragraph | 1 | Service↔service inline link (e.g., "we pair this with our [paid/web/etc] service") |
| Section 4 closing paragraph | 3 | Service↔industry inline links (healthcare + DTC + SaaS, contextualized to the service) |
| Section 5 Scale tier bullet (or natural location) | 1 | Service↔service inline link (e.g., analytics, branding, etc.) |
| Related reading section | 3 | Service↔blog links to evergreen guides |
| Final CTA | 2 | `Book a free [service] audit` → `/contact` + `Build a service stack` → `/services/bundle` |
| **Total** | **12** | |

The Section 3 / Section 4 / Section 5 inline links need natural anchor text in the body prose — brief authors should write the prose to include the link target words. **Don't leave them for Step 3 to invent.**

---

## Required CSS classes (do NOT redefine in briefs)

These are already defined in `styles.css`. Briefs reference them; briefs do NOT add new CSS for them.

### From commit `3b41469` (SERVICE PAGE COMPONENTS section, lines 1024-1165)
- `.tier-card-grid`, `.tier-card`, `.tier-card-eyebrow`, `.tier-card-who`, `.tier-card-pricing`, `.tier-card-pricing-meta`, `.tier-card-section-heading`, `.tier-card-fits-list` (+ li + ::before), `.tier-card-excluded-list` (+ li + ::before), `.tier-card-focus`
- `.outcome-card`, `.outcome-card-eyebrow`, `.outcome-card-metric`, `.outcome-card-profile`
- `.disclosure-card`, `.disclosure-card-label`, `.disclosure-card-body`

### From this build (SERVICE PAGE LAYOUT section, lines 1166+)
- `.hero-zone`, `.services-hero`, `.hero-content`, `.hero-headline`, `.services-hero-visual`
- `.prose-block` (with `h2`, `p`, `ol`, `ul`, `li`, `strong` descendants)
- `.section-deck`
- `.tiers-section h2`, `.outcomes-section h2` (section wrappers inherit default `section { padding: 88px 0 }`)
- `.outcome-grid`
- `.caveat-list` (+ li + ::before)
- `.related-reading`, `.related-grid`, `.related-card`, `.related-card-eyebrow`

### From historical site CSS (always available)
- `.container`, `.container-narrow`, `.eyebrow`, `.eyebrow-dot`, `.italic-accent`
- `.btn`, `.btn-primary`, `.btn-outline`, `.btn-accent`
- `.hero-subtitle`, `.hero-ctas-row`
- `.faq-section`, `.faq-item`, `.faq-icon`
- `.final-cta`, `.cta-buttons`
- `.nav`, `.nav-inner`, `.nav-links`, `.nav-link`, `.nav-link.active`, `.nav-mobile-menu`, `.footer`

**Brief authors:** if you need a class that's not on this list, flag it in the brief. Don't introduce it silently.

---

## Pre-flight class-existence audit (new responsibility for brief authors)

Brief #2 caught 15 class names that didn't exist in styles.css after the prep commit. Going forward:

**Every brief author must verify, before submitting the brief:**
1. Every CSS class used in the brief's HTML examples is in the "Required CSS classes" list above OR explicitly flagged as a new class with proposed CSS spec.
2. Every internal link destination either exists in the sitemap OR is explicitly noted as "will exist after Brief #N".
3. Every JSON-LD schema block is valid (validate with Google Rich Results Test on a paste of the schema before submitting).
4. FAQ visible content matches FAQPage schema text exactly (copy-paste both from the same source).

If the brief author skips this audit, the executor (Claude Code) catches the gaps in Step 3 of execution — wastes a checkpoint cycle.

---

## Documentation followups noted during the build sprint

See `memory/project_pricing_rebuild_followups.md` for items to address post-sprint:
- CLAUDE.md Cloudflare rule correction
- DESIGN.md hero/section padding drift
- Template-establishing decisions to retroactively document in DESIGN.md

---

*End of template rules · v1.0*
