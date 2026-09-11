# HMM Design System

> **The Quiet Disruptor — descriptive design canon for the helpmemarketing.com prototype**

**Status:** Canonical reference, current as of repository commit `0bfba56`.
**Scope:** Everything under `body.redesign-prototype` in `styles.css` (lines 3633-4418).
**Source of truth:** The prototype homepage's shipped CSS. This doc describes what exists; it is not aspirational.
**Companion docs:** `/docs/HMM_Color_System.md` (color canon), `/docs/HMM_Content_Rules.md` (voice canon, v0.2 DRAFT).
**How to use:** Every Phase 2 page migration starts here. Read in full before drafting any page brief.

---

## 1. Foundational Principles

- The homepage is canonical for visual design. All Phase 2 pages inherit from it.
- The Color System (`/docs/HMM_Color_System.md`) governs all color decisions.
- The Content Rules (`/docs/HMM_Content_Rules.md`) govern all written content.
- Every prototype-scoped rule lives under `body.redesign-prototype` selector. Page-specific markup uses `<body class="redesign-prototype">`.
- Legacy CSS still exists outside this scope. The site is in a transition state: `main` branch serves the legacy light-mode site; `redesign-prototype-homepage` branch is the canonical dark-mode site.

### Forbidden inside `body.redesign-prototype` scope
- Legacy color tokens: `--gold`, `--navy`, `--cream`, `--ivory`, `--deep`, `--ink-*`, `--line`, `--primary`, `--mint-soft`, `--white`
- Hardcoded hex values as property values (use tokens defined in Color System)
- Inline `style="color:..."` on prototype HTML elements
- Solid borders on structural elements (use rgba; solid acceptable only for state indicators)

---

## 2. Color Reference (summary)

See `/docs/HMM_Color_System.md` for full color canon. One-screen reference:

| Token | Value | Use |
|---|---|---|
| `var(--bg)` | `#0E0E0E` Obsidian | Site background |
| `var(--bg-elevated)` | `#1A1A1A` Carbon | Cards, modals, elevated surfaces |
| `var(--text)` | `#FFFFFF` Pure White | Primary text |
| `var(--text-muted)` | `#999999` Graphite | Secondary text |
| `var(--text-tertiary)` | `#8A8A8A` Slate (AA-lifted) | Tertiary text, disabled. Lifted from `#737373` to `#8A8A8A` on 2026-08-13 for WCAG AA (~4.9:1) on small text |
| `var(--cta)` | `#FF5C1A` Signal Orange | Primary CTAs + approved brand-identity accents |
| `var(--cta-hover)` | `#FF7038` Ember | CTA hover state |
| `var(--mint)` | `#00D4AA` Mint | Success/live state (never a CTA) |
| `var(--border)` | `rgba(255,255,255,0.08)` | Structural borders |
| `var(--grid-line)` | `rgba(255,255,255,0.045)` | Hero background grid |
| `var(--orange-glow)` | `rgba(255,92,26,0.18)` | Hero ambient gradient |

Token redefinition lives at `styles.css:3640-3663` under `body.redesign-prototype`.

---

## 3. Typography Scale

All values shipped as of HEAD `0bfba56`. Font families:
- `var(--serif)` = `'Fraunces', Georgia, serif`
- `var(--sans)` = `'Inter', -apple-system, system-ui, sans-serif`

### H1 — `.hero-headline`

| Property | Desktop | ≤900px |
|---|---|---|
| font-family | `var(--serif)` | — |
| font-size | 64px | 40px |
| font-weight | 400 | — |
| line-height | 1.05 | — |
| letter-spacing | -0.02em | — |
| color | `var(--text)` | — |
| margin | 0 | — |

CSS location: `styles.css:3688-3696` (desktop), `styles.css:4105` (mobile)

### H1 italic accent — `.hero-headline em`

| Property | Value |
|---|---|
| color | `var(--cta)` |
| font-style | italic |
| font-weight | 400 |

CSS location: `styles.css:3698-3702`

### H2 canonical — `.section-heading`

| Property | Desktop | ≤900px |
|---|---|---|
| font-family | `var(--serif)` | — |
| font-size | 40px | 28px |
| font-weight | 400 | — |
| line-height | 1.1 | — |
| letter-spacing | -0.015em | — |
| color | `var(--text)` | — |
| margin | 0 | — |

CSS location: `styles.css:3704-3712` (desktop), `styles.css:4106` (mobile)

### H3 canonical — `.subsection`, `.card-title`

| Property | Desktop | ≤900px |
|---|---|---|
| font-family | `var(--serif)` | — |
| font-size | 24px | 20px |
| font-weight | 500 | — |
| line-height | 1.25 | — |
| color | `var(--text)` | — |
| margin | 0 | — |

CSS location: `styles.css:3714-3722` (desktop), `styles.css:4107-4108` (mobile)

### H3 within service cards — `.service-card h3`

Same desktop values as `.subsection`/`.card-title`. **Known issue (Decision 8):** missing mobile override. Stays 24px at ≤900px. Fix pending in separate commit.

CSS location: `styles.css:3957-3963`

### Hero subtitle — `.hero-subtitle`

| Property | Value |
|---|---|
| font-size | 19px |
| line-height | 1.55 |
| color | `var(--text-muted)` |
| margin | 24px 0 0 |

No mobile override.

CSS location: `styles.css:3725-3730`

### Section deck — `.section-deck`

| Property | Value |
|---|---|
| font-size | 18px |
| line-height | 1.6 |
| color | `var(--text-muted)` |
| margin | 24px 0 0 |
| max-width | 720px |

CSS location: `styles.css:3732-3738`

### Body paragraph (inherited from `body.redesign-prototype`)

| Property | Value |
|---|---|
| font-family | `var(--sans)` |
| font-size | 17px |
| line-height | 1.6 |
| color | `var(--text)` |

No separate `p` selector. Paragraphs inherit unless overridden by component rules (`.hero-subtitle`, `.section-deck`, `.service-card p`, `.comparison-list li`, etc.).

CSS location: `styles.css:3666-3676`

### Eyebrow — `.eyebrow`

| Property | Value |
|---|---|
| display | inline-flex |
| align-items | center |
| gap | 8px |
| font-family | `var(--sans)` |
| font-size | 13px |
| font-weight | 500 |
| color | `var(--text-muted)` |
| text-transform | uppercase |
| letter-spacing | 0.12em |
| margin | 0 0 24px |

CSS location: `styles.css:3817-3828`

The `.eyebrow::before` pseudo-element is the mint live-indicator dot. CSS location: `styles.css:3830-3837`. See Component Patterns (Section 7).

---

## 4. Italic Accent Treatment

**This section exists because of the `/contact` gold-bug.** Commit `27eb63b` documented three canonical patterns. Use only these.

### Pattern 1 — H1 italic accent word

- HTML: `<em>` child element inside `h1.hero-headline`
- CSS: `body.redesign-prototype h1.hero-headline em { color: var(--cta); font-style: italic; font-weight: 400 }`
- Example: `<h1 class="hero-headline">We use AI to find your next <em>100 customers</em></h1>`

### Pattern 2 — Wordmark "Me" italic

> **Retired 2026-09-08** with the text logo. The nav no longer renders a `.logo-text` wordmark (see Pattern 3). Kept for history; do not add new instances.

- HTML: `<em>` child inside `.nav .logo`
- CSS: `body.redesign-prototype .nav .logo em { color: var(--cta) }`
- Example: `<span class="logo-text">Help<em>Me</em>Marketing</span>`

### Pattern 3 — Logo (image mark) — RETIRED text pattern below

**Current canon (locked 2026-09-08):** the logo is an image, not text.
- Nav: `<a class="logo" href="/"><img class="logo-img" src="/assets/brand/hmm-mark.svg" alt="Help Me Marketing" width="99" height="32"></a>` — mark-only SVG, 32px tall on desktop, 28px at ≤900px (`.logo-img`, unscoped so blog-dark pages match). The mark alone is the nav logo; the wordmark is not shown in the nav.
- Footer: `<img class="footer-logo" src="/assets/brand/hmm-logo-full.svg" alt="Help Me Marketing" width="150" height="69">` at the top of `.footer-cta-offer`, above the eyebrow — the full stacked lockup, 150px wide, 26px below.
- Always keep `width`/`height` attributes on both images (layout holds before CSS; no CLS).
- SVG colours are baked in (off-white `#F7F6F2`, orange `#FF5A1F`) and sit on the Obsidian ground; do not recolour via CSS. The horizontal lockup (`HMM_Logo_Package`) is held in reserve, unused.
- Related brand assets: favicon set at site root, `/og-image.png` default share image, `/logo.png` 400×400 schema logo (see CLAUDE.md → Deployment and SEO).

<details><summary>Retired: text logo "H + italic MM" (pre-2026-09-08)</summary>

- HTML: `<span class="me-italic">MM</span>` inside `.logo-mark` (NOT `<em>` — existing CSS targets `.me-italic` specifically)
- CSS: `body.redesign-prototype .logo-mark .me-italic { color: var(--cta) }`
- Italic enforced via legacy `.logo-mark .me-italic { font-style: italic }`
- Example: `<div class="logo-mark">H<span class="me-italic">MM</span></div>`

</details>

### Forbidden — never do this

- `var(--gold)` anywhere in prototype scope
- Inline `style="color:..."` on H1 or any prototype element
- `<span>` with hardcoded color attempting italic accent — use Pattern 1/2 or 3
- `class="hero-h1"` on prototype H1s (legacy class) — use `class="hero-headline"`
- `class="italic-accent"` on prototype elements — use `<em>`

---

## 5. Spacing & Layout

### Container — `.container`

| Property | Desktop | ≤900px |
|---|---|---|
| max-width | 1240px | — |
| margin | 0 auto | — |
| padding | 0 32px | 0 20px |

CSS location: `styles.css:3751-3755` (desktop), `styles.css:4110` (mobile)

### Hero — `.hero`

| Property | Desktop | ≤900px |
|---|---|---|
| padding | 72px 0 40px | 56px 0 32px |
| position | relative | — |
| overflow | hidden | — |

Asymmetric bottom (40px desktop / 32px mobile) is deliberate: it tightens the hero-to-first-section gap to ~88px. See "Sitewide vertical density" below.

CSS location: `styles.css` → `body.redesign-prototype .hero` (desktop) + `@media (max-width:900px)` block (mobile)

### Content section — `section.content-section`

| Property | Desktop | ≤900px |
|---|---|---|
| padding | 48px 0 | 32px 0 |
| border-top | `1px solid rgba(255,255,255,0.15)` | — |

CSS location: `styles.css` → `body.redesign-prototype section.content-section` (desktop) + `@media (max-width:900px)` block (mobile)

### Final CTA section — `.final-cta-section`

| Property | Desktop | ≤900px |
|---|---|---|
| padding | 48px 0 0 | padding-top 32px |

The wrapper only sets top spacing; the inner `.final-cta` card carries its own padding (see Section 9).

CSS location: `styles.css` → `body.redesign-prototype .final-cta-section`

### Sitewide vertical density (locked 2026-08-13)

The hero / content-section / final-cta rhythm was tightened ~25% from the original 96/64 spacing to the 72/48 rhythm above. This density was first tuned on the tool pages (`/ad-set-calculator`) and then adopted sitewide as the canonical rhythm for every `body.redesign-prototype` page. Blogs are excluded — they run the blog template's own spacing. Page-scoped hero/section padding overrides are no longer needed; the global rule governs. If a future page needs looser spacing, document the exception here rather than hardcoding a one-off override.

### Footer — `.footer`

| Property | Value |
|---|---|
| background | `var(--bg)` |
| border-top | `1px solid var(--border)` |
| padding | 96px 0 40px |

No mobile override. (Padding remains 96px 0 40px on mobile — flagged earlier as potentially disproportionate but unchanged.)

CSS location: `styles.css:4037-4041`

---

## 6. Grids

All grids stack at ≤900px breakpoint.

| Grid | Desktop columns | Desktop gap | Mobile (≤900px) | CSS location |
|---|---|---|---|---|
| `.hero-grid` | 1.2fr 1fr | 64px | 1fr / 40px | `3779-3786` → `4114-4117` |
| `.comparison-cards` | 1fr 1fr | 24px | 1fr / 16px | `3879-3884` → `4124-4127` |
| `.service-grid` | repeat(2, 1fr) | 24px | 1fr / 16px | `3934-3939` → `4119` |
| `.footer-grid` | 1fr 1fr 1fr | 64px | 1fr / 40px | `4043-4048` → `4120` |

No other prototype-scoped grid selectors exist.

---

## 7. Component Patterns

### Comparison cards (legacy structure)

`.comparison-card` base (`styles.css:3886-3891`):
```css
background: var(--bg-elevated);
border: 1px solid var(--border);
border-radius: 16px;
padding: 36px;
```

`.comparison-card-hmm` brand-emphasis variant (`styles.css:3893-3895`):
```css
border-color: rgba(255, 92, 26, 0.2);
```

Comparison list items (`styles.css:3917-3923`):
```css
.comparison-list li {
  padding: 14px 0;
  font-size: 15px;
  line-height: 1.55;
  color: var(--text-muted);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
```

Last child removes bottom border (`styles.css:3925-3927`).

HMM-variant cards use `var(--text)` (white) for list items instead of muted (`styles.css:3929-3931`).

### Service card (link card)

`.service-card` base (`styles.css:3941-3950`):
```css
background: var(--bg-elevated);
border: 1px solid var(--border);
border-radius: 16px;
padding: 36px;
text-decoration: none;
color: inherit;
transition: all 0.2s ease;
display: block;
```

Hover (`styles.css:3952-3955`):
```css
border-color: rgba(255, 255, 255, 0.16);
transform: translateY(-2px);
```

The card-arrow inside uses `var(--cta)` — counts as CTA affordance per Color System Decision 2.

### Card tags (`.card-tags` / `.card-tag`)

Small descriptor badges shown inside a `.service-card`, between the `<p>` and the `.card-arrow`. Introduced for the `/ai-tools` hub to label each tool with concrete specifics (capability, counts, coverage). Structure:
```html
<div class="card-tags">
  <span class="card-tag is-ai">AI Assisted</span>
  <span class="card-tag">4 platforms</span>
  <span class="card-tag">11 verticals</span>
</div>
```
- `.card-tags` — flex row, wraps, `gap: 6px`, `margin: 0 0 20px`.
- `.card-tag` — 11px/600, `padding: 5px 9px`, `border-radius: 6px`, transparent background with `1px solid var(--border)`, text `var(--text-muted)`. Outline chip so it reads on any card background.
- `.card-tag.is-ai` — the AI-capability variant: text `var(--cta)` (Signal Orange) on `var(--orange-glow)`. Use it only on the one tag per card that names the AI capability, so the orange stays a signal, not decoration (Color System Golden Rules). Neutral tags carry counts and coverage.

Tokens only, no hardcoded hex. Defined at `styles.css` under the prototype `.service-card` block.

### Tool finder (`.finder`)

The hero recommender on `/ai-tools`. A visitor describes what they are trying to do, and an AI (via `/api/tool-finder`) points them to the best-fit tool. Introduced when `/ai-tools` grew past a flat grid, so it scales as more tools ship without the visitor having to read every card. Structure:
```html
<div class="finder" id="finder">
  <form class="finder-form" id="finder-form" role="search">
    <label class="finder-label" for="finder-input">Describe what you are trying to do</label>
    <div class="finder-row">
      <input class="finder-input" id="finder-input" type="text" maxlength="500" ...>
      <button class="btn btn-primary finder-submit" id="finder-submit" type="submit">Find my tool &rarr;</button>
    </div>
  </form>
  <div class="finder-chips" id="finder-chips">
    <span class="finder-chips-label">Or start here:</span>
    <button class="finder-chip" type="button" data-q="...">How much should I spend on ads?</button>
    <!-- more chips -->
  </div>
  <div class="finder-result" id="finder-result" role="status" aria-live="polite" hidden></div>
</div>
```
- `.finder` — `max-width: 640px`, sits below the hero subtitle in place of hero CTAs.
- `.finder-row` — flex row (input + submit); collapses to a column at `max-width: 720px` with a full-width submit.
- `.finder-input` — reuses the prototype form-input visual language (`var(--bg)`, `1px solid var(--border)`, Signal Orange focus ring `0 0 0 4px rgba(255,92,26,0.15)`).
- `.finder-chip` — pill quick-picks (`border-radius: 999px`, outline). Each carries a `data-q` full-sentence query it submits on click. Hover uses `var(--orange-glow)` + `var(--cta)` border.
- `.finder-result` — AI response panel (`var(--bg-elevated)` card). `.finder-result-message` holds the copy; `.finder-result-actions` holds the recommended tool button(s).
- `.service-card.is-recommended` — the matched card in the grid below gets a Signal Orange border + glow, and the finder scrolls it into view.

**Behaviour (canon):** all JS is wired with `addEventListener` on `DOMContentLoaded`, no inline handlers. The endpoint returns `{primary_url, secondary_url, message}` constrained to the real tool URLs (enum) so links can never be hallucinated. If the API is unavailable (no `ANTHROPIC_API_KEY`, upstream error, network failure), the panel degrades to a "see all tools + book a free audit" fallback and never blocks the static grid. Tokens only, no hardcoded hex except the shared Signal Orange focus-ring rgba already used by the form pattern. Defined at `styles.css` under the prototype `.card-tag` block.

### Final CTA card (callout)

`.final-cta` (`styles.css:4011-4016`):
```css
background: var(--bg-elevated);
border-radius: 24px;
padding: 56px 64px;
text-align: center;
```

Mobile override (`styles.css:4121`):
```css
padding: 40px 24px;
```

Inner elements (`styles.css:4018-4034`):
- `.final-cta h2` — max-width 640px, margin 0 auto 24px
- `.final-cta .subhead` — max-width 540px, margin 0 auto 32px, color `var(--text-muted)`
- `.final-cta .microcopy` — margin-top 16px, font-size 13px, color `var(--text-tertiary)`, font-style italic

### Buttons

`.btn` base (`styles.css:3840-3853`):
```css
display: inline-flex;
align-items: center;
gap: 8px;
padding: 14px 28px;
font-family: var(--sans);
font-size: 15px;
font-weight: 500;
text-decoration: none;
border-radius: 8px;
transition: all 0.2s ease;
cursor: pointer;
border: 1px solid transparent;
```

Variants:

| Variant | Background | Color | Border | Box-shadow | CSS location |
|---|---|---|---|---|---|
| `.btn-primary` | `var(--cta)` | `var(--bg)` | — | `0 4px 16px rgba(255,92,26,0.25)` | `3855-3859` |
| `.btn-primary:hover` | `var(--cta-hover)` | — | — | `0 6px 20px rgba(255,92,26,0.35)`, `translateY(-1px)` | `3861-3865` |
| `.btn-outline` | transparent | `var(--text)` | `var(--border)` | — | `3867-3871` |
| `.btn-outline:hover` | `rgba(255,255,255,0.02)` | — | `rgba(255,255,255,0.2)` | — | `3873-3876` |
| `.btn-accent` (nav CTA) | `var(--cta)` | `var(--bg)` | none | `0 4px 16px rgba(255,92,26,0.25)` | `4178-4183` |
| `.btn-accent:hover` | `var(--cta-hover)` | — | — | — | `4185-4187` |

### Nav

Sticky behavior inherited from legacy `.nav` rule (`styles.css:95-100`):
```css
position: sticky;
top: 0;
z-index: 50;
backdrop-filter: blur(12px);
```

Prototype overrides (`styles.css:4140-4143`):
```css
background: var(--bg);
border-bottom: 1px solid var(--border);
```

Logo italic ("Me") uses Pattern 2 from Section 4. Logo mark italic ("MM") uses Pattern 3.

Nav links (`styles.css:4164-4176`):
- Base: `color: var(--text-muted)`
- Hover/active: `color: var(--text)`, `background: rgba(255,255,255,0.05)`

Hamburger (`styles.css:4201-4216`):
- Base: transparent background, `1px solid rgba(255,255,255,0.25)` border, `var(--text)` icon
- Hover: `rgba(255,255,255,0.45)` border, `rgba(255,255,255,0.05)` background

Mobile (≤900px) hides `.nav-main-cta` (`styles.css:4133-4136`).

Mobile nav fit (≤900px, added 2026-09-09): the outline CTA and the hamburger are fluid so the nav fits a 320px viewport without a third breakpoint. `.nav-cta .btn-outline` uses `padding: 10px clamp(10px, 3.75vw, 14px)` and `font-size: clamp(11px, 3.5vw, 13px)`; `.nav-hamburger` uses `clamp(36px, 11vw, 40px)` for width and height. Every clamp resolves to its max from 375px up, so only sub-375 phones see the smaller sizes (at 320px: 11.2px CTA text, 12px padding, 36px hamburger, 3px of right padding left). Do not add a 360px or 320px media query to solve this; the fluid rule is the canonical pattern.

### Footer

Footer architecture has its own dedicated section. See **§8 — Footer Architecture (F2 two-band)** below.

### Eyebrow

`.eyebrow` typography in Section 3. The mint live-indicator dot (`styles.css:3830-3837`):
```css
.eyebrow::before {
  content: "";
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--mint);
  box-shadow: 0 0 16px var(--mint), 0 0 4px var(--mint);
}
```

### Hero ambient glow

`.hero::before` (`styles.css:3768-3777`):
```css
content: "";
position: absolute;
top: 20%;
left: 10%;
width: 800px;
height: 800px;
background: radial-gradient(circle, var(--orange-glow) 0%, transparent 70%);
pointer-events: none;
```

Confirms Color System Decision 4 shipped value: `--orange-glow: rgba(255,92,26,0.18)`.

### Hero CTAs

Desktop layout (`styles.css:3792-3798`): flex row, gap 16px, margin-top 32px, flex-wrap wrap.
Mobile (`styles.css:4129-4131`): column, align-items flex-start.

### Hero image

`.hero-visual` (`styles.css:3800-3804`): block, height auto, min-width 0.
`.hero-image` (`styles.css:3806-3814`): width 100%, aspect-ratio 5/3, object-fit cover, border-radius 16px.

### Industry page components (`/industries/*`, added 2026-09-09)

The four industry pages (`finance`, `healthcare`, `dtc`, `saas`) are prototype-scoped and carry `data-screen-label="industry"`. They reuse legacy homepage layout classes (`.home-hero`, `.pain-grid`, `.case-card`, `.cta-card`) through the industry token shim at the top of the industry region in `styles.css`, plus these shared components, all scoped to `body.redesign-prototype [data-screen-label="industry"]`:

| Class | Purpose |
|---|---|
| `section.ind-section` / `.alt-tint` | Content band on the canon 48px rhythm with the content-section hairline (every section except the hero and the final CTA gets it); `.alt-tint` adds `rgba(255,255,255,0.02)` |
| `.ind-prose` | Prose column, max-width 820px; H2 on the canon 40px/28px scale, 17px muted paragraphs, orange underlined links |
| `h1.hero-headline`, `h2.section-heading` | Every industry H1 and H2 carries the canon class (64/40 and 40/28). `.section-header-row h2` and `.ind-intro h2` are pinned to 40px; `.rank-demo-text h3` to the 24px/500 H3 |
| `.home-hero` | Canon hero rhythm 72px 0 40px (56/32 on mobile), eyebrow 24px above the headline |
| `.pain-num`, `.heal-num` | Tertiary grey numerals; the HIPAA banner eyebrow is the canonical muted eyebrow. Orange is reserved for CTAs, the `em` accent and the ranking demo's "our client" row |
| `.case-card` / `.case-image` / `.case-metric` / `.case-pill` | Elevated dark card, soft Signal Orange radial glow top-right, result figure in Mint (Decision 12), outline pills. The legacy `.case-1/2/3` and healthcare `.case-rose/teal/amber` hex gradients are gone |
| Final CTA | The canon `.final-cta-section` card (eyebrow, `h2.section-heading`, `.subhead`, `.btn-primary`) replaces the legacy two-column `.cta-card` |
| `.ind-services-deck` | Deck under the services heading, 16px muted |
| `.ind-faq` / `.ind-faq-item` | FAQ list, 880px; 19px question, 15.5px muted answer, hairline dividers |
| `.ind-breadcrumb` | 13px tertiary breadcrumb with `.sep`; never inline-styled |
| `h1 em`, `h2 em`, `h3 em` | Italic accent in Signal Orange. `.italic-accent` is forbidden here as everywhere in prototype scope |
| `.live-indicator` / `.live-dot` | Mint (was legacy emerald) |
| `.rank-meta svg` | 12px filled star, healthcare ranking demo; never a text glyph or emoji |

Healthcare keeps a page-local `<style>` block for its page-specific components (`.heal-grid`, `.rank-demo`, `.hipaa-*`, `.spec-grid`, `.bench-table`), prototype tokens only. Until 9 Sep 2026 finance, dtc and saas each shipped an identical copy of the shared block inline; it now lives once in `styles.css`.

### Services pages (`/services`, `/services/*`, pass of 2026-09-09)

The hub and the six category pages were already on the canon type scale and rhythm. The pass fixed hygiene and one layout bug:

| Item | Rule |
|---|---|
| `.step-flow` on phones | Stacks to one column at ≤720px with the connector line hidden. There was no mobile rule before, so three ~110px columns overflowed at 390px |
| `.step-flow .step-num` | White numeral in a `rgba(255,255,255,0.2)` ring. Was Signal Orange; numerals are not a brand accent |
| `.svc-faq-wrap` | 1080px, 32px above; the FAQ wrapper on every category page. Replaces an inline `style` div |
| `.svc-detail`, `.svc-faq` (hub), `.pm-*` (performance marketing) | Live in `styles.css`, not page `<style>` blocks. `.svc-detail h3` is the 24px H3; `.svc-faq-item h3` is 19px like the industry FAQ |
| `.pm-callout-h3 em` | Signal Orange italic, same as the heading accent rule |
| `.nav-mobile-menu .mobile-cta-row` | `var(--border)` divider. The legacy light `--line-soft` showed through on every prototype page's open mobile menu |
| `em` in headings | The 43 `<em class="italic-accent">` on the category pages are plain `<em>`. `.italic-accent` still appears on `about`, `work`, `blog` index, `ad-calculator`, `tools/marketing-audit` and `industries/healthcare/hipaa-checklist`; those pages have not had this pass |

### Remaining pages pass (2026-09-09)

Hygiene applied to about, work, contact, ad-calculator and its benchmarks page, ad-set-calculator, the HIPAA checklist, the marketing audit tool, privacy, terms and the GTA page, plus the sitewide consent banner:

| Item | Rule |
|---|---|
| `.eyebrow-dot` | Mint in prototype scope. The legacy rule painted it gold (`#C9A96E`) on every page that used the span |
| `.about-value-row`, `.contact-contacts` | `var(--border)` dividers (were legacy `--line` / `--line-soft`) |
| `.finder-input` | `var(--bg)` (was a `#161616` literal) |
| Consent banner (`consent.js`) | Tokens with hex fallbacks: elevated surface, `--border`, `--cta` accept button, `--text`. The fallbacks exist because the banner also renders on the own-scope Index pages |
| Numerals and figures | `.about-value-num` tertiary; calculator result figures (`.adc-b-cta`, `.asc-weekly strong`, `.asc-verdict strong`) white; the best ad-set result Mint; `.asc-gallery-sec` labels muted. Warning and interactive states keep orange |
| Headings | `.about-principles-h2` 40/28, `.hipaa-h1` 64, `.hgroup-title` 40/28, `.hipaa-cta-title` 24/20, privacy and terms H1 and the marketing-audit H1 on `hero-headline` |
| `em` accents | `.italic-accent` removed from every prototype page |
| Mint literals | `#00D4AA` in the HIPAA checklist and the ad-set calculator replaced with `var(--mint)` |

### Blog index (`/blog`, rebuilt 2026-09-09)

The index was the last light-theme build inside prototype scope (185 inline styles, legacy tokens, 28 hex literals, a 78px `h1.serif`). It now uses the canon hero (`.hero`, `.eyebrow`, `h1.hero-headline`, `.hero-subtitle`), `section.content-section`, the §9 `.chip` / `.chip-on` for the category filter (with `aria-pressed`), and these components, all `body.redesign-prototype`-scoped:

| Class | Purpose |
|---|---|
| `.bi-feature` / `.bi-card` | Elevated dark card, `1px var(--border)`, 16px radius; feature is 1.2fr/1fr, cards 1fr/1.6fr; both stack at ≤900 / ≤720 |
| `.bi-thumb` | 16:9 placeholder on `var(--bg)` with the case-card Signal Orange radial glow; `.bi-thumb-word` ghost word in Fraunces at 6% white; `.bi-thumb-label` muted eyebrow. Replaces the navy gradients and gold glows |
| `.bi-meta`, `.bi-meta-sep`, `.bi-meta-featured` | 12px muted meta row; "Featured" is white 600 uppercase, not gold |
| `.bi-title-lg`, `.bi-title` | Fraunces 32/400 (feature) and 24/500 (card, the H3 scale) |
| `.bi-excerpt`, `.bi-author`, `.bi-avatar` | Muted excerpt; author row with a `var(--bg)` avatar (was legacy `--primary`) |
| `.bi-news-*` | Newsletter band: `h2.section-heading`, `.section-deck`, `.form-input` + `.btn-primary`, Mint check in the thanks panel. Show/hide uses the `hidden` attribute |
| `.bpost.is-hidden` | Filter state class; the script no longer writes inline styles |
| `.sr-only` | Visually hidden utility (newsletter email label) |

The `.eyebrow-dot` span is hidden in prototype scope: `.eyebrow::before` already draws the Mint dot, and pages that carried the span showed two dots.

### `/seo-growth-os` (migrated 2026-09-09)

Founder call: migrate rather than declare own-scope. The `.sgos` page block keeps its product-UI components (nodes, badges, matrix, command block) and now runs Inter for text and the canon heading scale: H1 Fraunces 64/40, H2 40/28, H3 24 and 20 at 500. Eyebrows are the canonical muted 13px (were Mint 11px/700); the "your business" badges use `--cta` on `--orange-glow` instead of the reserved warm-break terracotta, and the terracotta tokens are gone from the page. The comparison matrix checks are Tabler SVGs.

`/meta-growth-os` stays own-scope (no body class) but follows the content rules: em dashes replaced in the title, the prompt block and the copy; the matrix checks are SVGs.

---

### The HMM Index shell, instance 03 (`/gta-medspa-index`, added 2026-09-10)

Own-scope page (no body class), same shell as `/instagram-reindex` and `/hair-loss-index`: page-local token block with `--text-tertiary: #8A8A8A` (Color System Decision 11), `html,body{overflow-x:clip}`, `.hmm-nav` integration nav, `.wrap` / `header` / `.kicker` / `.lede` / `.byline` / `.livebar` / `.tiles` / `.card` / `.note` / `.tw` table / `details` FAQ / `.cta-btn` / warm-break `.about` footer. The artifact arrived as a light navy-and-gold standalone build; it was ported into the shell so all three instances read as one series. Unused shell blocks (pipeline, vision frames, log tabs, email gate, cohort bands) were not carried over.

Page components added for this instance, all built from the shell tokens:

| Component | Spec |
|---|---|
| `.takeaways` | `.card` with `h4` eyebrow and a counter-numbered `ol`; numerals are 11px tertiary, lead-ins white `b`, body muted |
| `.prose` | 760px measure, 16px muted paragraphs, `b`/`strong`/`em` white |
| `figure` / `figcaption` | figure margin `--s5` above; caption 12.5px tertiary above a `--border` rule |
| `.quad-wrap` / `.quad` / `.cell` | 2x2 cadence x reach grid on `--bg-elevated` cards; axis labels 10.5px tertiary uppercase (vertical on desktop, horizontal at ≤760); cell `.tag` + `.qdot` colour by state: `.comp` Mint, `.eff` warn, `.grind` crit, `.quiet` tertiary; `.big` count 34px white |
| `.bars` / `.bar-row` | 132px label / track / 56px value grid (96/50 at ≤760); fill is 85% white on an elevated track, value white tabular. Widths are inline `style="width:%"`, the same precedent as `.tbar` on `/hair-loss-index` |
| Tier strip | reuses `.tiles` (`.tiles.mt` adds `--s5` top margin) |
| `.flag.comp` / `.flag.eff` | pattern pills in the top-25 table: Mint outline for Compounding, warn outline for Efficient. `td.rank` tertiary, `td.area` nowrap, score is `b.score` white |
| `.note.crit` + `.risk-row` | regulatory exposure list: 1fr / 80px grid rows, `.sub` 12.5px muted, `.pct` 22px crit (functional state, not a brand accent) |
| `.method dl` | 140px `dt` (11px tertiary uppercase) / `dd` (14.5px muted) rows with `--border` rules; stacks at ≤760 |
| `.cta-card` | elevated card with the header's orange glow at top-right, `h2`, muted `p`, `.cta-btn` (the page's only Signal Orange UI element besides the kicker and nav CTA) |

Livebar carries the full shell set: Last synced 10 Sep 2026, Next refresh 10 Dec 2026, Cadence every 90 days (founder call 2026-09-11: quarterly, matching the 90-day window), Cycle 001.

Parity pass (2026-09-11), after comparing against `/instagram-reindex`: the shell's `.metrics-note` card and `.tip` tooltips were added (12 dotted terms: median reach, response, Index score, qualified, correlation; table headers use `.tip.d` / `.tip.d.dr` so they open downward inside the `.tw` scroller, and `.tile .k .tip` keeps the tile label tertiary). A "What the index says to do" section was added before Method, four `.card`s in a `.read-grid` (fixed 2x2, single column at ≤760) with `h4` eyebrow, `h3` and `p.dek`. Every line in it is drawn from a finding on the page; nothing new was computed.

Hero and OG (2026-09-11): a dedicated hero was generated (dark obsidian, orange quadrant with a scatter of clinic dots, orange bar chart; 1344x752 PNG) and stored at `/assets/index/gta-medspa/hero.png`, following the `/assets/index/<instance>/` convention. The OG card at `/assets/index/gta-medspa/og.png` (1200x630) composites the hero with the kicker, title, one-line deck and the HelpMeMarketing wordmark in Inter, rendered from a scratch HTML in headless Chromium. `og:image`, `twitter:image` and the Report schema `image` point at the card. The hero is not shown in the page header; none of the three Index instances carries one.

Format parity pass (2026-09-11, founder: "it is still different from /instagram-reindex"): the page was re-sequenced into the Real Estate dashboard order using only figures already on the page. Order is now: coverage `.note.crit` (176 of 341) > Category pulse (five `.tiles`: category median reach, number one, coverage, cadence effect, regulatory exposure) > What the data says > The scoreboard (top 25, scores 90+ in `.score.hi` Mint, the rest `.score.mid` white; a movement column is promised for cycle 002) > What the top of the board is actually doing (three `.card`s in `.grid3` with `.bigno`) > The cadence read > The cohort read (four `.card.coh-card` in `.read-grid` with `.bigno` and `.members`, replacing the tier tiles) > The regional read > The compliance ledger > What the index says to do > Frequently asked > Method and limits > Take the dataset with you > CTA card. The "Finding one to four" eyebrows became read names to match instances 01 and 02.

Email gate (2026-09-11): the Real Estate `.gate` pattern is live on this page with tokenised CSS (`var(--bg)` input, `var(--cta)` focus, `var(--mint)` / `var(--crit)` messages). It posts to the existing Apps Script endpoint with source `gta-medspa-cycle-001` and downloads `gta-medspa-index-cycle-001-top25.csv` (rank, clinic, area, Index score, median reach, posts, pattern; the 25 rows on the page). The CSV is embedded as a JSON string literal so clinic names with quotes cannot break the script. When the ranked dataset arrives, the same gate carries positions 26 to 176.

Email gate on `/hair-loss-index` (2026-09-11): the same `.gate` block and script now sit as "Take the dataset with you" after Method and limits, source `hair-loss-cycle-001`, downloading `hair-loss-index-cycle-001-postlog.csv` (the 167 brand-authored rows of the on-page post log: brand, date, format, hook, likes, comments, plays, link). All three Index instances now carry the gate.

Post-level build (2026-09-11, founder: "we don't have vision pass, scoreboard, the creative positioning map, the full post log"): the 25 ranked accounts were resolved to Instagram handles (DataForSEO SERP, clinic websites, Apify user search, then confirmed by Apify profile scrape) and re-collected on 11 September with `apify/instagram-scraper` (up to 30 most recent posts per account, 552 posts, 488 brand-authored and 64 collaborator-authored). Data lives in the session scratchpad only; the page carries the derived figures and the gated CSV. Sections added, all shell components:

| Section | Components | Source |
|---|---|---|
| The scoreboard (extended) | `.brandcell` linked name + `.handle`; new columns Followers, Peak reel (`b` + `.cell-sub` x-followers), Comments / 1k, Mix (`.cell-sub` R/C/S); `.tip.d` headers | ranking columns from 10 Sep, new columns from the 11 Sep re-collection; the dek says so |
| The vision pass | `.frames` / `.frame` (shell block restored): `.shot` img, `.verdict` with four state classes (`.v-hook` Mint, `.v-person` warn, `.v-promo` orange, `.v-proc` tertiary), `.badge`, `.fmets`, `.go` link; `.note` read | cover frame of each top-8 account's most-played brand-authored reel, self-hosted at `/assets/index/gta-medspa/frames/NN-handle.jpg` (position 7 has no brand-authored reel; position 9 takes the slot) |
| The creative positioning map | `.quad-wrap` / `.quad` / `.cell` reused with `.cell-list` (ranked `li` with `.vanity` metrics) | computed, not judged: x = share of posts that are reels (split 50%), y = comments per 1k reel plays (split at field median 1.7) |
| The collaborator ledger | `.tw` table + `.note.warn` | the 64 co-authored posts, per brand, with authors; excluded from every brand figure |
| Which content themes actually work | `.tw` table with `.score` hi/mid/lo relative pull | keyword-tagged captions (seven themes), reel medians vs field median 2,550; labelled a keyword read |
| Format | `.fmts` / `.fmt` (shell block restored) | reels / statics / carousels with median likes |
| The full post log | `.logtabs` / `.logtab` (26 tabs) + `#postlog` `.tw` table with `data-brand` rows, `.hook` italic; filter via `addEventListener` on `DOMContentLoaded` toggling the `hidden` attribute (no inline handlers, no `style.display`) | 488 rows, newest first, every row linked |
| Method and limits | `.note` "Two collections, one window" + handle-resolution note | mirrors the Hair Loss Index precedent: the ranking stays as published until cycle 002 re-scores from one collection |

The gate now downloads the full post log (`gta-medspa-index-cycle-001-postlog.csv`: rank, clinic, handle, date, format, theme, hook, likes, comments, plays, url). `.logtab.active` uses `var(--text)` / `var(--bg)` instead of the shell's hex.

Handle resolution notes that matter for cycle 002: Caras Clinic publishes as `@injectablesbymina` (`@carasclinic` is an empty pointer); Mirror by Nurse Yara's feed is 29 of 30 collaborator-authored (`@nurse.yara` and four `mirror.*` staff accounts); Hazel Aesthetics is `@hazelaesthetics_` (Aurora in bio, Newmarket in the ranking); SOL Skin resolves to the twelve-location group account `@solskin.spa`, whose 90-day feed is 26 statics, three carousels and one reel; Timeless Medispa is `@_timelessmedispa` (Brampton), which returned exactly the 7 in-window posts the ranking counted.

Still pending the ranked dataset: positions 26 to 176 in the gated CSV. Not built: a boost ledger (no Meta Ad Library read was taken; zero posts in the re-collection carry the paid-partnership flag).

Registries updated in the same commit: `sitemap.xml`, `/ai-tools` (card 9, ItemList position 9, client `TOOLS` map), `api/tool-finder.js` catalog, `/work` (case-study card + ItemList position 1). Breadcrumb schema is Home > Case Studies > page, matching the other two instances (the artifact pointed at a nonexistent `/index-series` hub). OG image is the site default; the artifact referenced `/images/gta-medspa-index-hero.png`, which does not exist.

### Portfolio page (`/portfolio`, added 2026-09-11)

Founder supplied a standalone artifact already written in the prototype tokens; it was ported onto the canonical shell rather than shipped standalone: shared nav (Case Studies active), `.hero` with `.eyebrow` / `h1.hero-headline` / `.hero-subtitle` / `.hero-ctas`, `section.content-section` blocks with the canon `.section-heading` `<em>` accent and `.section-deck`, the `.final-cta-section` callout, the F2 footer, `styles.css` tokens (so `--text-tertiary` is the Decision 11 value, not the artifact's `#737373`). `data-screen-label="portfolio"`. Page components are namespaced `pf-*` and scoped to the label in the prototype region of `styles.css`:

| Component | Spec |
|---|---|
| `.pf-head` | section header row: heading block left, `.section-deck` right, wraps at narrow widths |
| `.pf-services` / `.pf-service` | 3-column grid of elevated cards linking to the six `/services/*` pages; `.pf-num` index is tertiary uppercase (the artifact had it in Signal Orange; Rule 1 moves numerals off orange); Fraunces 20/500 `h3`, muted 14px `p` |
| `.pf-platforms` | inline list with tertiary 4px dots |
| `.pf-results` / `.pf-result` | 4-column (2 at ≤900) result cards; `.pf-metric` Fraunces 34/500 in `var(--mint)` per Decision 12 (artifact used orange); `.pf-label` muted uppercase; `.pf-client` white above a `--border` rule; `.pf-work` muted. Eighth card added for the GTA MedSpa Index |
| `.pf-builds` / `.pf-build`, `.pf-refs` / `.pf-ref` | 3-column card links; `.pf-url` / `.pf-kind` muted, white on hover (artifact used orange link accents) |
| `.pf-media-grid` / `.pf-media` | 6 columns (3 at ≤900, 2 at ≤720); `.pf-frame` 4:5 with `.pf-ratio` tag and `.pf-play` button that turns orange on hover; two `<button>` cards open the lightbox, four `<a>` cards open Facebook reels |
| `.pf-lb` | fixed lightbox with a `<video controls autoplay playsinline>`; Escape, backdrop click and the close button all close it and return focus; `body.pf-lb-open` locks scroll; wired with `addEventListener` on `DOMContentLoaded` |

Homepage reuse (2026-09-11, founder call): the homepage dropped the "Most agencies vs HMM" comparison cards and their closing line (the ChatGPT heading and deck above them stay), and now carries three `pf-*` sections in the portfolio pattern: What we do (`.pf-services` + `.pf-platforms`, replacing the old `.service-grid`), Creative (`.pf-media-grid` + lightbox) and Reference material (`.pf-refs`). The homepage has no `.app` wrapper, so the shared block is scoped `body.redesign-prototype :is([data-screen-label="portfolio"], .pf-scope)` and each reused section carries `pf-scope`; the lightbox sits inside a `.pf-scope` div before the closing body tag. The `.comparison-cards` / `.section-closing` CSS stays for the other pages that still use those classes. The homepage final CTA now uses the canon `.final-cta-section` callout with the portfolio copy ("Start with the audit"), keeping the GTA agency link as a second microcopy line.

Homepage story order (copy and CRO pass, founder-approved 2026-09-11): Hero (subtitle now names the four industries; "See how we work" points at `#how-we-work`) > Proof strip (`.pf-results`, the eight portfolio result cards) > The contrast, completed (`#how-we-work`: the ChatGPT heading and deck, "peer-reviewed decisions" corrected to "recommendations from AI assistants and from peers", plus three `.pf-ref` cards in a `.pf-how` row: founder-led team, zero-markup spend and no twelve month lock, monthly reviews that show revenue; these restate the substance of the removed comparison cards) > What we do > Live builds (`.pf-builds`) > Creative > Industries (`.pf-industries`, four `a.pf-industry` cards to `/industries/*`, copy from each industry page's own headline and description) > Final CTA > footer. (Revised 2026-09-11: the "Keep reading" section was removed and its six reference links folded into Live builds as a compact "Published work" row: `.pf-subhead` label, then `.pf-refs.pf-refs-compact` tiles carrying only `.pf-kind`, `h3` and `.pf-url`. Three columns, two at 900 and 720. The `#resources` anchor now sits on the subhead.)

Visual-consistency pass (2026-09-11, founder request: the ChatGPT and services cards read as static next to the colourful hero and ticker). New shared pieces inside `.pf-scope`: `.pf-card-top` (flex row: icon badge left, eyebrow or number right) and `.pf-icon` (40px circle, 36 on phones, 5% white fill, hairline border, inline Tabler stroke icon in Mint at rest). Hover on `a.pf-service`, `a.pf-industry` and `a.pf-build`: border warms to 45% Signal Orange with an `--orange-glow` ring and a deeper shadow; the badge fills with orange-glow, its icon turns Signal Orange and scales 1.06; the `.pf-url` line brightens to white. `.pf-how .pf-ref` cards (divs) only swap the badge on hover. Services cards gained a "See the service" `.pf-url` line. Orange remains decorative and on link lines only. Live builds now use `.pf-builds-compact` (18/20px padding, 18px h3, one-line 13.5px description) and Published work is a `.pf-pills` row of `a.pf-pill` (999px radius, `.pf-pill-kind` uppercase prefix, orange-glow hover) replacing the compact tiles.

Industry page pass, `/industries/dtc` (2026-09-11; siblings pending): visible labels use the canon "DTC" and the breadcrumb points at `/#industries`; hero metric and case cards corrected to the Case Studies page (Shakti Warrior +312% revenue, Luxe & Charme +41% conversion rate; the unverified third card was removed and the grid is `.case-grid-2`, 16:10, one column at 900). "How DTC is different" moved from three prose paragraphs to the homepage `.pf-how` card row with `.pf-icon` badges and the scroll reveal (page carries the same IntersectionObserver script). Pain rows are `a.pain-item` links to the matching service, arrow warms to Signal Orange on hover. FAQ uses `details.svc-faq-item` with a rotating plus. Final CTA follows the homepage pattern ("Start with the DTC audit."). All industry case cards are 16:10 on phones. Placeholder clients (StackHarbor, SprintFlow, Sterling Wealth Partners, Apex Capital Advisory) were removed sitewide on founder confirmation; SaaS and finance use `.case-grid-1` (one 16:10 card, max 640px) until a second verified case exists, and the Branding & Social finance example carries no figure. Consistency pass (same day): SaaS, finance and healthcare now match DTC on every shared element: `/#industries` breadcrumb, canon eyebrow labels (SaaS, Finance, Healthcare), the `.pf-how` difference cards with icon badges and reveal (SaaS, finance; healthcare keeps its richer SEO, HIPAA, specialties and ad-spend sections instead), `a.pain-item` rows linked to services or the HIPAA checklist, `details.svc-faq-item` FAQ, and the "Start with the [industry] audit." CTA with the shared microcopy. Healthcare compaction (founder brief, same day): the HIPAA section is an intro, four `span.pf-pill` points and the checklist banner, with the four explanatory cards moved to `/industries/healthcare/hipaa-checklist` as a `.hipaa-primer` section (`.pf-how.pf-how-2`, two columns) above the checklist; the specialties grid is an 11-pill row plus a collapsed `details.spec-details` holding one line per specialty (`.spec-list`, two columns); the ad-spend table is three neutral range tiles (`.pf-results-3`, `.pf-metric.is-neutral` white) with pill links to the calculator and to `/ad-calculator/benchmarks`, where the full 11-row table already lives. Industry imagery (same day): each industry page has one abstract image in the hero-wave style (Obsidian, Signal Orange particle strands, one Mint point, subject right, empty left) at `/assets/industries/[slug].webp` (1344x752) with a 1200x630 `[slug]-og.jpg` used as that page's `og:image`. Case cards use it via `.case-image.case-ind-[slug]` under the existing orange-glow wash and a stronger bottom overlay; a second card on the same page gets `.case-flip` (mirrored) so the pair does not repeat. Generated with gpt_image_2 at 16:9. The same image also heads each industry hero as `img.hero-image.ind-hero-image` (5:3, eager, high priority) inside `.hero-visual.ind-hero-visual`, with the metric card overlapping its lower edge by 48px (36 on phones) so healthcare, which has no case grid, carries its image too.

Industry consistency and interaction pass (2026-09-11). Root cause of the uneven FAQ: two `.svc-faq-item` rule sets coexisted in the prototype region (a div-era one with border-top and 22px margins, and the details one with border-bottom and 20px padding), so every item drew two rules with a gap between them. Now one rule set, sitewide for `details.svc-faq-item`: border-top per item, border-bottom on the last, summary 18px/1.4 with 16px vertical padding, the plus in a 28px ring badge that fills orange-glow on hover and focus and rotates 45 degrees when open, answers 15.5px capped at 72ch with 18px below. Industry rhythm locked: eyebrow 14px above H2, H2 20px above intro copy, 32px from any section header (`.ind-intro`, `.ind-prose`, `.section-header-row`) to its content; intro copy 17px/1.7 everywhere. `.pain-num` is a 40px ring badge matching `.pf-icon` (numeral stays neutral, ring warms on hover). Hero CTAs stack full width at 720. `.case-pill`, `.metric-label` and `.rank-badge` lifted to 12/12/11px. `.text-link` underline and hover use Signal Orange instead of the legacy gold. `.pf-how .pf-ref` cards are `div`s with hover disabled. The row reveals on scroll: the homepage script adds `.js-reveal` to `.pf-how` when IntersectionObserver exists and `.is-in` once 20% of the row is visible (fires once). Cards start at opacity 0 and 18px down, rise in over 0.7s with a 120ms stagger, then a hairline highlight (`::before`, white at 32%) draws left to right across each card top. Removed under `prefers-reduced-motion`; without JS the cards render static.

Proof ticker (homepage only, 2026-09-11): the eight `.pf-result` cards run as one continuously scrolling strip instead of the 4x2 grid. Markup: `.pf-ticker` (overflow hidden, edge fade via `mask-image`) > `.pf-ticker-track` (flex, `width: max-content`, `animation: pf-ticker 56s linear infinite`) > two `.pf-results.pf-ticker-set` children holding identical card sets; the second set is `aria-hidden="true"` and its link carries `tabindex="-1"`. The keyframe translates the track by `-50%`, which equals exactly one set plus its trailing gap, so the loop is seamless. Cards are fixed at 272px (236px at 720). The animation pauses on `:hover` and `:focus-within`. Under `prefers-reduced-motion: reduce` the animation is removed, the mask is dropped, the duplicate set is hidden and the strip becomes a plain horizontal scroller. Direction is right-to-left (reading order); flip with `animation-direction: reverse` if ever needed. The portfolio page keeps the static grid.

Homepage mobile and accessibility pass (2026-09-11), applied after a Playwright audit at 390 and 1440: `<main id="main-content">` wraps the page content and a `.skip-link` (off-canvas until focused, Signal Orange pill) precedes the nav; the hero image carries `fetchpriority="high"` plus a desktop-only `<link rel="preload" media="(min-width: 901px)">` since it sits below the fold on phones; `<meta name="theme-color">` is Obsidian. Type floor on pf-* cards lifted: `.pf-label` 12px, `.pf-work` 13px, `.pf-num`/`.pf-kind` 12px. Footer social icons get a 40px hit area via padding and negative margin. At 720: hero CTAs are full width and centred, `.hero-subtitle` 17px, pf-* cards 20px padding with 12px gaps, `.pf-platforms` tighter, and the footer address separator dot is hidden because the line wraps. The consent banner (consent.js) is compact at 720: 13px type, 14px padding. Each ticker card carries a client avatar: `<img class="pf-logo">` inside `.pf-client` (flex row, 10px gap), 28px circle, sourced from `/assets/clients/[slug].png`. Avatars are pre-composed 96px circular PNGs (white disc with the client mark; TravelUp is its brand blue with a white wordmark; Med Aesthetics is an "MA" monogram in Inter because no mark exists; the GTA MedSpa Index is the HMM mark on Obsidian with a hairline ring). Compose new ones the same way rather than styling raw logos in CSS.

Media lives at `/assets/portfolio/` (two mp4 clips with jpg posters, four reel posters). Schema: BreadcrumbList (Home > Case Studies > Portfolio) and CollectionPage with the five external builds as `hasPart`. `/work` gained a "See the portfolio" outline button in its hero; sitemap entry added. Top nav unchanged (Decision 4).

## 8. Footer Architecture

> **Current canon: Footer v3 (Direction F — CTA-forward). Locked 2026-09-03.**
> v3 replaces the F2 two-band footer on all 42 `body.redesign-prototype` pages. F2 (and F1 before it) are deprecated. The F2 spec below is retained for history only.
>
> **v3 structure** (`.footer > .container`):
> - `.footer-cta` (grid, 1.4fr / 1.4fr; stacks at 900px) — **left** `.footer-cta-offer`: eyebrow "Free · No obligation", Fraunces headline "Ready to grow the *right* way?", orange `.footer-cta-btn` "Book a free audit" → `/contact` (the **only** solid/filled button in the footer, `--cta`), then `.footer-cta-nap` — a real `<address>` (font-style normal) reading "Burlington, Ontario, Canada · Hello@helpmemarketing.com" (**no phone** anywhere; **no city-list line**; GBP link is schema-only, not visible). **right** `.footer-cta-links`: three `.footer-linkcol` — Industries / Company / Free tools. Services column dropped (lives in the top nav). Company column links, in order: About, Case Studies, Portfolio (added 2026-09-11, founder call), Blog, Contact. **Free tools** render as `.footer-tool-btn` — mint (`--mint`) **outline** buttons (the only secondary-button style; ≥44px tall on mobile), a deliberate one-solid-orange / two-mint-outline hierarchy.
> - `.footer-base` (flex, space-between; stacks at 720px) — **left** `.footer-partners`: two `.footer-partner` marks, Meta + Google, each an icon + caption ("Meta Partner", "Google Partner"). **right** `.footer-base-right`: `.footer-social` (LinkedIn + Facebook icons) · separator · `.footer-legal` (Privacy · Terms · © 2026 HelpMeMarketing).
> - **Brand logos** are true-colour SVGs in `/assets/brand/` (`meta-color.svg` — mark extracted from Meta's official lockup, Meta-blue gradient; `google-color.svg` — 4-colour G; `linkedin-color.svg` / `facebook-color.svg` — brand-blue). Rendered as `<img class="footer-brand-logo logo-*">` (not CSS mask, since colour can't be masked); ~15-16px, `opacity:.95` at rest, `1` on social hover. Swap the SVG file to change a logo. (A monochrome mask set — `meta.svg` etc. + `.footer-brand-ico`/`.ico-*` — also exists in `/assets/brand/` and `styles.css` history if a single-tone treatment is ever wanted.)
> - CTA note: v3's footer CTA intentionally repeats the audit ask; on the 33 pages that also have a `.final-cta` section it stacks below that section (founder-approved 2026-09-03).
>
> ---
>
> ### (Deprecated) F2 two-band

Pattern: Two-band horizontal layout. Upper band carries brand identity and tool discovery. Lower band carries sitemap and baseline.

Purpose: Tool discovery is the primary engagement goal. Upper band gives tools featured visual real estate. Lower band serves utility navigation without dominating.

Status: F2 supersedes F1 (3-column flat). F1 is deprecated. All migrated prototype pages and all Phase 2.5 sweep pages use F2.

#### Structural blocks

```
.footer
  .footer-band-brand           (upper band: brand statement + tool cards)
    .footer-brand-statement    (left: logo + headline + descriptor)
    .footer-tools-grid         (right: 2-up tool cards)
      .footer-tool-card        (icon + title + description + affordance)
  .footer-band-utility         (lower band: sitemap + baseline)
    .footer-utility-grid       (3-col: Services / Industries / Company)
      .footer-column
    .footer-baseline           (location + email + copyright + legal)
```

#### Colors

Single-band dark background per the locked Color System; no separate token introduced for the lower band. Both bands use `var(--bg)` = `#0E0E0E`. Visual band separation comes from a hairline divider, not a background color change.

- Footer background: `var(--bg)` = `#0E0E0E`
- Band separator: `1px solid var(--border)` = `rgba(255,255,255,0.08)`
- Tool card surface: `var(--bg-elevated)` = `#1A1A1A`
- Tool card border (default): `var(--border)` = `rgba(255,255,255,0.08)`
- Tool card border (hover): `rgba(255,255,255,0.16)` — Tier system token `--border-strong` once shipped
- Tool card icon background: `var(--orange-glow)` = `rgba(255,92,26,0.18)`
- Tool card icon color: `var(--cta)` = `#FF5C1A`
- Sitemap heading: `var(--text-tertiary)` = `#8A8A8A`
- Sitemap link: `var(--text-muted)` = `#999999`
- Baseline text: `var(--text-tertiary)` = `#8A8A8A`

#### Typography

- Brand statement headline: `22px` / `400` / `Georgia, serif` / line-height `1.35`. The accent word uses `<em class="italic-accent">` with `color: var(--cta)`.
- Brand statement descriptor: `13px` / `400` / sans / `var(--text-muted)` / line-height `1.65`
- Tool card title: `14px` / `500` / sans / `var(--text)`
- Tool card description: `12px` / `400` / sans / `var(--text-muted)` / line-height `1.55`
- Tool card affordance: `12px` / `500` / sans / `var(--cta)` with trailing arrow
- Sitemap column heading: `10px` / `600` / sans / `var(--text-tertiary)` / letter-spacing `1.5px` / uppercase
- Sitemap link: `12px` / `400` / sans / `var(--text-muted)`
- Baseline text: `11px` / `400` / sans / `var(--text-tertiary)`

#### Spacing

- Footer outer wrapper: no padding; each band sets its own padding
- Upper band padding: `48px 40px` (desktop), `32px 24px` (≤900px)
- Lower band padding: `36px 40px 24px` (desktop), `28px 24px 20px` (≤900px)
- Brand-statement-to-tools gap: `56px` (desktop); wraps to column at `≤900px`
- Tool cards gap: `16px`
- Sitemap columns gap: `40px` (desktop); collapses to 2-col at `≤900px`, 1-col at `≤720px`
- Band separator: hairline divider, spans full width between bands
- Baseline separator: `1px solid var(--border)` above baseline within lower band

#### Tool card component

Each `.footer-tool-card` contains:
1. Icon block: `28px × 28px`, rounded `6px`, Orange Glow background, CTA-color icon. Implementation: inline SVG copying Tabler Icons path data (24×24 viewBox, currentColor stroke, round caps). Tabler Icons library is NOT loaded in the project; icons are inline only.
2. Title: `14px` medium, white
3. Description: `12px` regular, muted, single-line constrained
4. Affordance: `12px` medium CTA-color with trailing arrow

Hover state: border color brightens from `var(--border)` to `rgba(255,255,255,0.16)`. No translate. No shadow.

#### Mobile breakpoints

- `≤900px`: Upper band stacks (brand statement above tool cards). Lower band sitemap collapses to 2-column. Baseline horizontal but wraps if narrow.
- `≤720px`: Lower band sitemap collapses to single column. Baseline stacks vertically.

#### Tool cards content (current)

Card 1 — Ad Spend Calculator
- Icon: Tabler `ti-calculator` (inline SVG, path data copied from tabler-icons.io)
- Title: "Ad Spend Calculator"
- Description: "Model CPL, ROAS, and budget across 4 platforms × 11 verticals."
- Affordance: "Run the numbers →"
- Link: `/ad-calculator`

Card 2 — Marketing Audit
- Icon: Tabler `ti-checkup-list` (inline SVG, path data copied from tabler-icons.io)
- Title: "Marketing Audit"
- Description: "Score your marketing maturity across 5 dimensions in 10 min."
- Affordance: "Take the audit →"
- Link: `/tools/marketing-audit`

#### Brand statement (canonical text)

Headline (with serif italic accent on the second sentence):
> **Try a tool. *No email gate.***

Descriptor:
> Free utilities built from our actual client work. Use them, share them, run the numbers yourself.

Markup: `<em class="italic-accent">No email gate.</em>` for the orange accent.

#### Lower band — utility grid

4 columns: Services / Industries / Company / Contact. Grid `1fr 1fr 1fr 1.3fr` (Contact column slightly wider); collapses to `1fr 1fr` (2x2) at 900px and `1fr` at 720px. (Was 3 columns before the 2 Sep 2026 entity-wiring patch, which added the Contact NAP column.)

Services column (6 items, all link to `/services/[slug]`):
- Performance Marketing → `/services/performance-marketing`
- SEO & AEO → `/services/seo`
- Branding & Social → `/services/branding-social`
- Website Development → `/services/website-development`
- Analytics & Attribution → `/services/analytics-attribution`
- AI Automation & Workflow Systems → `/services/ai-automation`

Industries column (4 items):
- DTC → `/industries/dtc`
- SaaS → `/industries/saas`
- Healthcare → `/industries/healthcare`
- Finance → `/industries/finance`

Company column (5 items):
- About → `/about`
- Case Studies → `/work`
- Pricing → `/pricing`
- Blog → `/blog`
- Contact → `/contact`

Contact column (`.footer-column.footer-contact`) — NAP + owned profiles (entity wiring, 2 Sep 2026):
- `<h4>Contact</h4>`
- `<address>` (font-style normal): `Burlington, Ontario, Canada`, then `tel:+14168239694` shown as `(416) 823-9694`, then `mailto:Hello@helpmemarketing.com`
- `.footer-areas` line: "Serving Burlington, Oakville, Milton, Halton Hills, Hamilton and the Greater Toronto Area."
- `.footer-social` list: Google Business Profile (`maps?cid=7855304921006956254`), LinkedIn, Facebook — each `rel="noopener" target="_blank"`
- Strings must match the homepage JSON-LD `#organization` block and the `/contact` NAP block character-for-character. Instagram is deliberately omitted from the visible footer (dormant account) though it remains in the schema `sameAs`.

#### Baseline

Two-line layout on the left, vertical-stacked legal on the right:

Left cluster (vertical):
- Partner badges (Google Partner · Meta Partner) inline
- `.footer-baseline-meta`: "Help Me Marketing · GTA marketing agency · Hello@helpmemarketing.com" (business name spelled "Help Me Marketing" with spaces, normalized sitewide 2 Sep 2026)

Right cluster (vertical stack):
- Privacy Policy
- Terms of Service
- © 2026 HelpMeMarketing

#### Forbidden patterns specific to footer

- No "Shopify Partner" badge
- No "DTC & E-commerce" label (use "DTC")
- No "Case studies" lowercase (use "Case Studies")
- No "© 2026 HelpMeMarketing Inc." (drop "Inc.")
- No lowercase `hello@helpmemarketing.com` in visible text (use `Hello@`)
- No inline styles on any `.footer-*` element
- No "Lifecycle & Retention" as a service category (deprecated; replaced by AI Automation & Workflow Systems)

---

## 9. Form Pattern (reusable across prototype forms)

The contact-page CSS block (`styles.css:4218-4416`) ships a complete dark-variant form pattern that's not contact-specific. **Every future prototype-scoped form (service inquiry, audit request, future contact variants) should reuse these components.**

### Components

| Component | Selector | CSS location |
|---|---|---|
| Form surface | `.contact-form` | 4246 |
| Field label | `.form-label` | 4253 |
| Label hint (optional/required) | `.form-label-hint` | 4257 |
| Text input | `.form-input` | 4262-4284 |
| Textarea | `.form-textarea` | 4262-4284 (shared) |
| Prefixed input wrapper | `.form-prefix-wrap` | 4287-4310 |
| Prefix label | `.form-prefix` | 4287-4310 |
| Prefixed input element | `.form-input-prefixed` | 4287-4310 |
| Multi-select chip | `.chip` | 4313-4329 |
| Chip selected state | `.chip.chip-on` | 4313-4329 |
| Error banner | `.contact-err` | 4334-4343 |
| Submit button | `.contact-submit` | 4346-4353 |
| Form footer microcopy | `.contact-privacy-mini` | 4356-4360 |
| Thank-you success panel | `.contact-thanks` | 4363-4372 |
| Thank-you glyph | `.contact-thanks-glyph` | 4363-4372 |

### Focus pattern (Decision 3 state-indicator exception)

`.form-input:focus`, `.form-textarea:focus`, `.form-prefix-wrap:focus-within` (`styles.css:4279-4284, 4296-4299`):
```css
border: 1px solid var(--cta);
box-shadow: 0 0 0 4px rgba(255, 92, 26, 0.15);
```

This is the canonical focus pattern. Solid `var(--cta)` border + soft CTA glow.

### Naming caveat

These selectors live under the "PROTOTYPE — CONTACT PAGE" section header in styles.css but are **functionally generic**. When building future forms, reuse the selectors. Do not duplicate or fork into `.audit-form .audit-input` patterns.

---

## 10. Local Token Shim Mechanism (tactical pattern)

Two local token shims exist in prototype scope (`styles.css:4235-4243`):

```css
body.redesign-prototype .contact-aside {
  --text-primary: var(--text);
  --text-secondary: var(--text-muted);
}

body.redesign-prototype .contact-thanks {
  --deep: var(--text);
  --ink-60: var(--text-muted);
}
```

### What they do

These rescue legacy inline styles like `style="color:var(--text-primary)"` or `style="color:var(--deep)"` without rewriting the HTML. The inline style references a token; the shim redefines that token within a specific scope to map onto a prototype-canonical token.

### When to use this pattern

**As a tactical workaround during migration**, when:
- Source HTML has inline styles using legacy token names
- Rewriting all the inline styles is out of scope for the commit
- The visual result of the shim matches the canonical pattern

**Never as the canonical approach.** The canonical approach is no inline styles, prototype-scoped CSS only. If a page systematically uses inline styles with legacy tokens, plan a follow-up commit to remove them.

### Risk

Local token shims are **fragile**. If a future contributor removes the inline style without understanding the shim, OR removes the shim without understanding the inline style, the affected element breaks. Document any new shim with an inline CSS comment explaining the rescue mechanism.

---

## 11. Decision 9 — Tokens Currently Hardcoded as Literals

Color System Section 7 lists 5 "reserved" tokens. The diagnostic against HEAD `0bfba56` revealed these tokens are **not actually reserved** — the rgba values are already used as hardcoded literals throughout prototype CSS.

| Reserved token | Shipped value | Current literal usages |
|---|---|---|
| `--surface-subtle` | `rgba(255,255,255,0.02)` | `.btn-outline:hover` (3875), `.contact-privacy-mini` (4357) |
| `--surface-hover` | `rgba(255,255,255,0.05)` | `.nav-link:hover` (4170), `.nav-link.active` (4175), `.comparison-list li border-bottom` (3922), `.nav-hamburger:hover` (4209), `.chip:hover` (4320) |
| `--border-strong` | `rgba(255,255,255,0.16)` | `.service-card:hover` (3953) |
| `--cta-glow-soft` | `rgba(255,92,26,0.15)` | `.form-input:focus`, `.form-prefix-wrap:focus-within` (4283, 4298) |
| `--cta-glow-strong` | `rgba(255,92,26,0.35)` | `.btn-primary:hover` (3864) |

### Implication

The 5 "reserved" tokens are deduplication candidates, not new design language. When Decision 9 ships (separate commit), it's a refactor — replacing literals with token references — not a new pattern.

**Until Decision 9 ships:** keep using the literals consistently. Don't invent new opacities for these use cases. If a new component needs a hover wash, use `rgba(255,255,255,0.05)` (the future `--surface-hover` value), not a one-off `rgba(255,255,255,0.06)`.

---

## 12. Additional Opacity Values — Pending Founder Review

The diagnostic surfaced additional rgba opacities used in prototype CSS that aren't covered by the 5 reserved tokens above. **These are NOT yet named tokens. Founder decision pending on whether to tokenize them.**

| Value | Used at | Use case |
|---|---|---|
| `rgba(255,92,26,0.1)` | `.chip.chip-on` (4326) | Selected-chip tint |
| `rgba(255,92,26,0.2)` | `.comparison-card-hmm` border (3894) | Brand emphasis border |
| `rgba(255,92,26,0.25)` | `.btn-primary` shadow, `.btn-accent` shadow (3858, 4182) | CTA button base shadow |
| `rgba(255,92,26,0.45)` | `.contact-thanks-glyph` shadow (4371) | Success state glyph glow |
| `rgba(255,255,255,0.03)` | `.form-prefix` background (4302) | Inner-form subtle wash |
| `rgba(255,255,255,0.15)` | `section.content-section` border-top (3759) | Inter-section divider |
| `rgba(255,255,255,0.2)` | `.form-input:hover` (4276), `.form-prefix-wrap:hover` (4293), `.btn-outline:hover` (3874), `.chip` border base (4315) | Hover/active border (used 4x — token candidate) |
| `rgba(255,255,255,0.25)` | `.nav-hamburger` border base (4203) | Hamburger button outline |
| `rgba(255,255,255,0.3)` | `.chip:hover` border (4321) | Chip hover border |
| `rgba(255,255,255,0.45)` | `.nav-hamburger:hover` border (4208) | Hamburger hover border |

**Action:** Until founder review, use these literals consistently. The `rgba(255,255,255,0.2)` hover border in particular is used 4 times and is a clear future token candidate.

---

## 13. Breakpoints

Per Color System Decision 5, two breakpoints in active use under prototype scope. The diagnostic confirmed no others.

### `@media (max-width: 900px)` — primary

Major layout flip. CSS location: `styles.css:4103-4137`.

What changes:
- Typography mobile sizes (H1 40px, H2 28px, H3 20px)
- Container padding 32px → 20px
- Section/hero padding 96px → 64px
- All grids stack to 1fr
- Hero CTAs stack column
- `.nav-main-cta` hides

### `@media (max-width: 720px)` — secondary

Component-level adjustments only. CSS location: `styles.css:4406-4416`.

What changes:
- `.footer-baseline` stacks vertically (gap 24px)
- `.footer-baseline-meta` becomes full-width

### Forbidden breakpoints

Do NOT use any of these inside prototype-scoped rules: 1200, 1100, 1000, 960, 680, 640, 560, 520, 480. These exist in legacy CSS but are not used in prototype scope.

---

## 14. Transitions & Hover Patterns

| Selector | Transition | CSS location |
|---|---|---|
| `.btn` (base) | `all 0.2s ease` | 3850 |
| `.service-card` (base) | `all 0.2s ease` | 3948 |
| `.footer-column ul li a` | `color 0.2s ease` | 4074 |

Hover lifts:
| Selector | Transform | CSS location |
|---|---|---|
| `.btn-primary:hover` | `translateY(-1px)` | 3863 |
| `.service-card:hover` | `translateY(-2px)` | 3954 |

The pattern: 0.2s ease, lift by 1-2px, increase shadow on CTAs.

---

## 15. Migration Standards (Phase 2 page builds)

Every Phase 2 page migration must:
1. Use `<body class="redesign-prototype">` 
2. Use `<div class="app">` wrapper
3. Use the F2 footer pattern (see §8 — Footer Architecture)
4. Use the canonical italic accent patterns (Section 4) — no `.italic-accent` class, no inline color styles
5. Use `.hero-headline` for hero H1s, `.section-heading` for H2s, `.subsection` or `.card-title` for H3s
6. Reference shared form components from Section 9 if the page has a form
7. Use only the 2 codified breakpoints from Section 13
8. Use only the color tokens defined in `/docs/HMM_Color_System.md`
9. Follow voice rules from `/docs/HMM_Content_Rules.md`

### Locked Phase 2 architectural decisions

- **Service architecture:** 6 categories (C1) — Performance Marketing, SEO + AEO, Branding & Social, Website Development, Analytics & Attribution, AI Automation & Workflow Systems
- **URL scheme:** `/services/[category-slug]`
- **Form taxonomy (7 chips):** SEO | Ads | Brand & Social | Website | Analytics | Email & retention | Not sure yet
- **`data-service` attrs** use category slugs (`performance-marketing`, `branding-social`, etc.)
- **Logo:** HMM with italic Signal Orange "MM" (Pattern 3 from Section 4)
- **Email casing:** `Hello@helpmemarketing.com` (visible UI); lowercase `hello@` acceptable in schema/metadata

---

## 16. Open Items

### Known followups (not blocking current work)

- `.bullet-list` usage check (Color System Decision 7) — class defined but unused on homepage
- 5 "reserved" tokens implementation (Color System Decision 9) — see Section 11 above
- `.service-card h3` mobile font-size override (Decision 8) — add 20px at ≤900px in separate commit
- Additional opacity values founder review (Section 12)
- `/services` Phase 2 migration — uses this doc as primary brief authority
- HMM_Content_Rules v0.2 → v1.0 lock — currently DRAFT awaiting founder approval
- Thank-you panel H2 anti-pattern at `contact.html:158` — inline `style="color:var(--deep)"` rescued by local token shim (Section 10); codify canonical H2 pattern when `/services` migration begins

### Site state caveat

`main` branch currently serves the legacy light-mode site. `redesign-prototype-homepage` branch (this doc's source of truth) is the canonical dark-mode site. When Phase 3 merges to main, this doc's "current as of `0bfba56`" reference will need updating, and any legacy CSS still referenced should be flagged for cleanup.

---

## 17. Updating This Doc

When the prototype's design system evolves:
1. Update `styles.css` first
2. Update this doc to match shipped reality in the same commit
3. Bump the "Status" line at the top with the new commit reference
4. If a pattern is added that wasn't here before, add it to the appropriate section and reference its CSS location

This doc is **descriptive of shipped reality**, not aspirational. New patterns require shipping first, then documenting.

---

## 18. Multi-Step Form Pattern (`/schedule-a-call`)

Added for the three-step qualifying form. Reuses the Section 9 form pattern
(`.form-label`, `.form-input`, `.form-textarea`, `.chip` / `.chip-on`,
`.contact-err`, `.contact-thanks-glyph`) and adds only what a stepped form needs.
CSS lives at the end of the prototype region in `styles.css`.

### When to use

A form with more than about eight fields. Below that, a single grouped page is
simpler and converts about the same. Above it, splitting reliably beats one long
column, because the visible commitment at any moment stays small.

### Components

| Class | Purpose |
|---|---|
| `.sched-step` / `.sched-step.on` | One `<fieldset>` per step. Only `.on` is displayed. |
| `.sched-legend` | Step label. Mint, uppercase, 11px, matching the eyebrow treatment. |
| `.sched-progress` / `.sched-steps` / `.sched-dot` | Step header. `.on` marks current, `.done` marks completed (mint fill). |
| `.sched-bar` / `#sched-bar-fill` | Progress bar. Width is set in JS as `step / total`. |
| `.sched-nav` | Back and Continue row. Reverses to a stacked column under 720px. |
| `.sched-why` | Small tertiary note under a field explaining why it is asked. |
| `.req` | The asterisk on required labels. Signal Orange, not red. |
| `.hp-field` | Honeypot wrapper, positioned off-canvas rather than `display:none`. |
| `.sched-thanks` | Success panel, replaces the form in place. |

### Rules

- **Validate per step, not per form.** Check only the fields inside the step
  being left. Validating everything up front fires errors for fields the person
  has not reached yet.
- **Keep the error element outside the fieldsets.** Put it inside a step and it
  is hidden on every other step, so validation appears to fail silently. This
  was a real bug caught in review, not a hypothetical.
- **Required fields belong in the first and last steps.** The middle step should
  be skippable, so an unsure visitor keeps moving instead of abandoning.
- **`.sched-why` earns intrusive questions.** Budget and revenue convert far
  better with one line explaining what the answer is used for.
- **Native `<select>` needs its own dark styling.** The popup list is drawn by
  the OS and inherits nothing from `.form-input`, so `.form-select option` sets
  its own background. Omit it and the list renders white-on-white on some
  platforms.
- `novalidate` on the form, validation in JS, so error copy matches house voice
  rather than the browser default.

---

*HMM Design System v1.0 — first markdown commit*
*Source: Homepage prototype CSS at HEAD `0bfba56`*
*Companion canon: `/docs/HMM_Color_System.md`, `/docs/HMM_Content_Rules.md`*
