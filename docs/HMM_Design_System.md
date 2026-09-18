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
| Consent banner, behaviour | Shows until a choice is made; stores `hmm_consent` = granted or denied in localStorage; on every load re-asserts the stored choice (or denied by default) as a Google Consent Mode `update` for `analytics_storage`, `ad_storage`, `ad_user_data`, `ad_personalization`, and pushes a `hmm_consent_update` dataLayer event with `hmm_consent`. It emits the signal only: to gate tags, enable Consent Mode ("Require additional consent") on the GA4 and ads tags in GTM, or trigger them on `hmm_consent_update` with `hmm_consent == granted`. GTM itself loads lazily (first interaction or 3.5s idle), so the denied default is queued ahead of it, but strict default-denied gating would still want a Consent Mode `default` snippet in the head above the GTM loader. `#hmm-cookie-settings` on /privacy clears the choice and reopens the banner. `data-consent-avoid` marks a bottom-fixed control the banner must sit above |
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

Hero and OG (2026-09-11): a dedicated hero was generated (dark obsidian, orange quadrant with a scatter of clinic dots, orange bar chart; 1344x752 PNG) and stored at `/assets/index/gta-medspa/hero.webp (the 1344x752 PNG master was committed alongside it and removed on 2026-09-17 as unreferenced)`, following the `/assets/index/<instance>/` convention. The OG card at `/assets/index/gta-medspa/og.jpg (PNG until 2026-09-17)` (1200x630) composites the hero with the kicker, title, one-line deck and the HelpMeMarketing wordmark in Inter, rendered from a scratch HTML in headless Chromium. `og:image`, `twitter:image` and the Report schema `image` point at the card. The hero is not shown in the page header; none of the three Index instances carries one.

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

Industry page pass, `/industries/dtc` (2026-09-11; siblings pending): visible labels use the canon "DTC" and the breadcrumb points at `/#industries`; hero metric and case cards corrected to the Case Studies page (Shakti Warrior +312% revenue, Luxe & Charme +41% conversion rate; the unverified third card was removed and the grid is `.case-grid-2`, 16:10, one column at 900). "How DTC is different" moved from three prose paragraphs to the homepage `.pf-how` card row with `.pf-icon` badges and the scroll reveal (page carries the same IntersectionObserver script). Pain rows are `a.pain-item` links to the matching service, arrow warms to Signal Orange on hover. FAQ uses `details.svc-faq-item` with a rotating plus. Final CTA follows the homepage pattern ("Start with the DTC audit."). All industry case cards are 16:10 on phones. Placeholder clients (StackHarbor, SprintFlow, Sterling Wealth Partners, Apex Capital Advisory) were removed sitewide on founder confirmation; SaaS and finance use `.case-grid-1` (one 16:10 card, max 640px) until a second verified case exists, and the Branding & Social finance example carries no figure. Consistency pass (same day): SaaS, finance and healthcare now match DTC on every shared element: `/#industries` breadcrumb, canon eyebrow labels (SaaS, Finance, Healthcare), the `.pf-how` difference cards with icon badges and reveal (SaaS, finance; healthcare keeps its richer SEO, HIPAA, specialties and ad-spend sections instead), `a.pain-item` rows linked to services or the HIPAA checklist, `details.svc-faq-item` FAQ, and the "Start with the [industry] audit." CTA with the shared microcopy. Healthcare compaction (founder brief, same day): the HIPAA section is an intro, four `span.pf-pill` points and the checklist banner, with the four explanatory cards moved to `/industries/healthcare/hipaa-checklist` as a `.hipaa-primer` section (`.pf-how.pf-how-2`, two columns) above the checklist; the specialties grid is an 11-pill row plus a collapsed `details.spec-details` holding one line per specialty (`.spec-list`, two columns); the ad-spend table is three neutral range tiles (`.pf-results-3`, `.pf-metric.is-neutral` white) with pill links to the calculator and to `/ad-calculator/benchmarks`, where the full 11-row table already lives. Industry imagery (same day): each industry page has one abstract image in the hero-wave style (Obsidian, Signal Orange particle strands, one Mint point, subject right, empty left) at `/assets/industries/[slug].webp` (1344x752) with a 1200x630 `[slug]-og.jpg` used as that page's `og:image`. Case cards use it via `.case-image.case-ind-[slug]` under the existing orange-glow wash and a stronger bottom overlay; a second card on the same page gets `.case-flip` (mirrored) so the pair does not repeat. Generated with gpt_image_2 at 16:9. The same image also heads each industry hero as `img.hero-image.ind-hero-image` (5:3, eager, high priority) inside `.hero-visual.ind-hero-visual`, so healthcare, which has no case grid, carries its image too. The metric card with its illustrative sparkline was retired the same day (founder question; the chart implied data that did not exist): a `.ind-hero-proof` chip now sits directly below the image as a caption (founder call, 2026-09-11: off the artwork; elevated surface, hairline border, 14px above) with the verified figure in Mint (`.ind-hero-proof-figure`, Fraunces 22px) and a one-line label (`.ind-hero-proof-text`, 13px). `.hero-ctas-row` gets 32px above it (28 on phones) to match the homepage hero.

Industry consistency and interaction pass (2026-09-11). Root cause of the uneven FAQ: two `.svc-faq-item` rule sets coexisted in the prototype region (a div-era one with border-top and 22px margins, and the details one with border-bottom and 20px padding), so every item drew two rules with a gap between them. Now one rule set, sitewide for `details.svc-faq-item`: border-top per item, border-bottom on the last, summary 18px/1.4 with 16px vertical padding, the plus in a 28px ring badge that fills orange-glow on hover and focus and rotates 45 degrees when open, answers 15.5px capped at 72ch with 18px below. Industry rhythm locked: eyebrow 14px above H2, H2 20px above intro copy, 32px from any section header (`.ind-intro`, `.ind-prose`, `.section-header-row`) to its content; intro copy 17px/1.7 everywhere. `.pain-num` is a 40px ring badge matching `.pf-icon` (numeral stays neutral, ring warms on hover). Hero CTAs stack full width at 720. `.case-pill`, `.metric-label` and `.rank-badge` lifted to 12/12/11px. `.text-link` underline and hover use Signal Orange instead of the legacy gold.

Service pages pass (2026-09-11, "do the same for services"): each of the six category pages gets an abstract image in the shared particle style at `/assets/services/[slug].webp` with a 1200x630 `[slug]-og.jpg` as `og:image`; the hero becomes `.hero.svc-hero` with `.hero-grid` (text left, `.hero-visual.svc-hero-visual` right, 5:3 image) and the same `.ind-hero-proof` chip carrying the homepage figure that maps to the service (TravelUp 12x for Performance Marketing, Med Aesthetics +186% for SEO, Shakti Warrior +312% for Branding, Luxe & Charme +41% for Website, BoomerangFX 3.2x for Analytics; AI Automation has no verified client figure and shows the image only). The chip rules are unscoped so industry and service pages share them. Eyebrows read "Service · [canon name]". `.service-card` gains the orange-ring hover; `.step-num` is a 48px ring badge that warms on hover. The Performance Marketing proof card now cites TravelUp's 12x monthly bookings, matching the homepage, instead of an unlisted +38% ROAS. The `/services` hub (same day) follows suit: `.svc-hero` grid with a hub image (`/assets/services/hub.webp`, six tiles around a node) and the TravelUp 12x chip (a multi-service result, so it suits the hub), hero CTAs added (the page had none), the six `.service-card` links carry `.pf-card-top` with the homepage icon badge and 01 to 06 numbers, the FAQ moves from div markup to `details.svc-faq-item`, and the final CTA uses the shared pattern. Case Studies (`/work`, same day): hero takes the shared image grid (`/assets/work/hero.webp`, podium bars under an arrow; no chip, the proof strip beneath already carries the figures), own OG image, shared final CTA. Bug fixed: `.case-study-card p` outranked `.case-study-metric`, so result figures had been rendering as 15px muted text; now `p.case-study-metric` is the 32px Mint callout (28 on phones). Cards carry the client avatar (`img.pf-logo.case-study-logo`, both Index cards use the HMM avatar) beside the title, the orange-ring hover, equal-height flex columns and 12px tags. About (`/about`, same day): hero on the shared image grid (`/assets/about/hero.webp`, people nodes around a compass) with two CTAs where it had none, own OG image; principle numerals are 40px ring badges and rows warm on hover; a "How we work" section reuses the homepage `.pf-how` cards (founder-led, zero markup, revenue reviews) with the reveal script; final CTA is the shared "Start with the audit." pattern. Contact (`/contact`, same day): the layout is `.stack-contact.contact-layout`, a two-column grid where the copy column holds the eyebrow, sentence-case H1 ("Let's talk growth"), intro, the shared no-markup microcopy, and the contact image (`/assets/contact/hero.webp`, envelope and chat bubble, 16:10, lazy) with the Shakti Warrior +312% chip; contact details are a third grid item (`.contact-details`) under it and the form spans both rows. Below 960 the order is copy, form, details and the image is hidden, so the form starts one screen sooner on phones. Step labels and the thanks title are sentence case; direct-contact labels 12px; section bottom padding 48px (was 120). Own OG image. Form fields, names and the submit script are untouched. Blog index (`/blog`, same day): hero on the shared image grid (`/assets/blog/hero.webp`, article pages with a bookmark and bulb), own OG image; every card thumbnail is now the post's hero image (`img` inside `.bi-thumb`, object-fit cover, label overlay in a dark pill); nine posts that had no hero received one in the shared particle style at `/blog/images/[slug]-hero.{png,webp}` and now use it as their `og:image`; `.bi-grid` is two columns of vertical cards on desktop (one below 900), the featured post keeps its wide layout, cards take the orange-ring hover with a slight image zoom. Portfolio (`/portfolio`, same day): hero on the shared image grid (`/assets/portfolio/hero.webp`, clapperboard, browser and chart cards), own OG image; the five content sections carry `.pf-scope` so the homepage badge and hover rules apply; service cards get the icon badge row and "See the service" line, result cards the client avatar, build cards the compact one-line form. AI Tools hub (`/ai-tools`, same day): hero on the shared image grid (`/assets/tools/hero.webp`, open toolbox) with the tool finder staying in the copy column (`.finder` unconstrained, row wraps), own OG image; the tools section carries `.pf-scope` and each of the nine cards gets the icon badge and 01 to 09 row (clipboard, calculator, hourglass, search, target, chart, trophy for the three Index cards) with the shared hover; `.card-tag` 12px.

Legal pages (`/privacy`, `/terms`, 2026-09-11). Audit found twelve bordered `content-section` blocks with 48px padding each, paragraphs alternating between muted decks and pure-white body copy with no spacing between them, and a 150-character measure on desktop. Now: `main.legal-scope` wraps one `.legal-section` holding `.legal-layout` (220px sticky `.legal-toc` "On this page" index built from the H2s, plus `.legal-body` at 70ch). Inside the body the original sections keep their ids for anchors but lose padding and borders; H2 28px (24 on phones) with 12px below and 40px between clauses; decks, paragraphs and list items all 16.5px/1.7 in `--text-body` (78% white, Decision 13 extended to this scope); links white underlined, orange on hover; the closing "Questions?" block is `.legal-closing`. A small IntersectionObserver script marks the active clause in the index. Below 900 the index is a wrapped pill row above the text. No imagery on legal pages by design. `.pf-how .pf-ref` cards are `div`s with hover disabled. The row reveals on scroll: the homepage script adds `.js-reveal` to `.pf-how` when IntersectionObserver exists and `.is-in` once 20% of the row is visible (fires once). Cards start at opacity 0 and 18px down, rise in over 0.7s with a 120ms stagger, then a hairline highlight (`::before`, white at 32%) draws left to right across each card top. Removed under `prefers-reduced-motion`; without JS the cards render static.

Calculator pages (`/ad-calculator`, `/ad-set-calculator`, `/ad-calculator/benchmarks`, 2026-09-12). Audit found three different heroes (80/40 with a border, 72/40, and a heading-only 80/0 with a back link), three CTA patterns (dashed inline box, shared `.final-cta`, dashed card in an 80/120 section), the ad spend FAQ on the blog `.faq-item` styling, and labels down to 9px. Now: all three heroes are `.hero.svc-hero` grids with a page image (`/assets/calculators/[slug].webp`, 5:3, eager) and two `.hero-ctas` (primary anchors to `#tool` or opens the calculator; outline goes to the benchmarks, the tools hub, or the tables). No proof chip: tools carry no client figure. The tool sections sit in `section.content-section` at the canon 48/48 rhythm (ad spend tool keeps its 1120px container and sticky inputs card). Every page ends on the shared `.final-cta-section` with a 20-minute "Straight answers, no obligation" note; the ad spend tool keeps its results-adjacent CTA box but as a solid elevated card, not dashed. Ad spend FAQ moved to `details.svc-faq-item` inside `.svc-faq-wrap`. Related and methodology cards use the orange-ring hover. Benchmarks: `h3.subsection` 22px/500 with 40px above and 14px below, table headers 12px. Small-text floor applied: labels and eyebrows 12px, the two uppercase pill badges (New, assumed) 10-11px. Each page has its own OG crop. Calculator JavaScript and all input/output ids untouched; interactions verified.

HIPAA checklist (`/industries/healthcare/hipaa-checklist`, 2026-09-12). Audit found a page-local hero (80/40 with a border and its own 64px H1 class), the primer squeezed to 8px top padding to compensate, the checklist body at 40/120, five 40px H2 groups marked by 8px dots, a glowing two-column CTA card, and an 11px CTA eyebrow. Now: `.hero.svc-hero` grid with the breadcrumb above it, a shield-and-checkboxes image (`/assets/industries/hipaa-checklist.webp`), and two `.hero-ctas` (start the checklist, healthcare marketing). Primer is a canon `content-section` and its four cards carry `.pf-card-top` icon badges (file-check, server, eye-off, star) with the shared scroll reveal. The checklist section (`#checklist`, 64px scroll margin) opens with an eyebrow, `section-heading` and deck before the sticky progress card; group headings are 32px (26 on phones) with a 40px ring number badge (`.hgroup-num`, orange glow on group hover) replacing the dots; items lift with the orange-ring hover and get a focus ring; descriptions 14px, legal note 13px. Closing CTA is the shared `.final-cta-section`. Bug fixed in passing: the Reset button was hidden by a CSS `display:none` that the script's empty-string display could never override, so it never appeared; the script now controls visibility alone. Checklist script and storage key untouched. Page-specific OG crop.

Marketing audit (`/tools/marketing-audit`, 2026-09-12). Audit found the whole page inside a 760px centred column: a sans-weight H1 with no image, an "8 questions · 5 minutes · Free" meta line, then the wizard, then a 72px-padded prose block with 30px H2s, a bullet list for the five dimensions, div-based FAQ, and no closing CTA. Now: `.hero.svc-hero` grid with a five-axis radar image (`/assets/tools/marketing-audit.webp`), sentence-case H1 ("Score your marketing maturity in five minutes."), two `.hero-ctas` (start the audit, how it's scored) and the meta line kept under them as `.audit-meta`. The wizard sits in `section#audit.content-section` (64px scroll margin) with `.audit-page` reduced to a 760px centred column and no padding of its own; the inline `style` attributes on the progress fill and honeypot moved to page CSS (the script still drives the fill width). Prose is split into canon sections with eyebrows and `section-heading`s: Background, then How it's scored as five `.pf-ref` cards (`.audit-dims`, 5 columns, 2 at 900, 1 at 720) with target, speakerphone, funnel, repeat and bar-chart icon badges and the shared reveal, then Reading the result, then FAQ as `details.svc-faq-item`, then the shared `.final-cta-section`. Audit tool labels in styles.css lifted from 11px to 12px (dimension tag, gate preview label, recommendation labels, internal-links heading, final CTA label, progress dimension). Wizard, gate and results scripts untouched; walked to the gate at both widths. Page-specific OG crop.

Blog index, second look (`/blog`, 2026-09-12). Audit found the filter chips out of step with the posts: SaaS, Finance and SEO chips matched no post (an empty grid with no message), while nine posts (six Marketing Strategy, three Agency) had no chip at all and were reachable only under All. Chips now mirror the real categories: All, Marketing strategy, Working with agencies (the three Agency Selection/Pricing/Services posts share `data-cat="Agencies"`; their meta labels are unchanged), Paid media, Analytics, Healthcare, DTC, AI & automation. A `.bi-empty` notice with a "Show all posts" reset appears if a filter ever yields nothing. The "HelpMe · Blog" overlay label on every thumbnail is retired now that all 14 cards carry a real image; the featured thumbnail loads eagerly; the featured card's author line matches the posts (AK, Ankit Kumar, Founder). Card hover, thumbnail zoom and the 2-column grid from the first pass are unchanged.

Homepage, second look (`/`, 2026-09-12). With the rest of the site settled, the audit found only edge differences: the hero eyebrow was Title Case ("AI-Native Marketing") where every other eyebrow is sentence case; the "How we work" section was the one section without an eyebrow or an italic accent in its heading; the final CTA had a single action where every other page offers a primary plus an outline; the ticker avatars were lazy-loaded inside an overflow-hidden marquee, so the second set never intersected the viewport and popped in blank as the strip scrolled; `.pf-pill-kind` and `.pf-ratio` sat at 11px. Now: "AI-native marketing" eyebrow, "How we work" eyebrow with `<em>before</em>` in the heading, "See the case studies" outline action beside "Book a free audit", eager ticker avatars, 12px pill kinds and ratio badges. Everything else (ticker, reveal, icon badges, builds, creative, industries, rhythm) was already on canon and is unchanged.

GTA marketing agency page (`/gta-marketing-agency`, 2026-09-12). Audit found a text-only hero, Title Case eyebrow, a five-line price bullet list, four long market-pattern bullets, six service cards without badges, a plain city list, and a single-action final CTA. Now: `.hero.svc-hero` grid with a particle Toronto skyline (`/assets/gta/hero.webp`) and the local proof chip (+92% consult requests, Vanguard Pharmacy, Toronto, 6 months); eyebrow "Greater Toronto Area · Marketing agency". Price ranges are five neutral-white `.pf-result` tiles (`.gta-price-grid`, 24px figures, 5 columns, 2 at 900, 1 at 720) with a 13px note each. Market patterns are `ol.gta-patterns` cards with 40px ring numbers (`.gta-num`) that glow orange on hover. The six service cards carry the hub's icon badges and kind numbers. Cities render as `.pf-pill`s. Final CTA gains "See all services". Page-specific OG crop.

Homepage hero image swap (2026-09-12). The particle wave (`/images/hero-particle-wave.webp`, 1108x663, file removed 2026-09-17) is replaced by a radar sweep revealing a teal cluster (`/assets/home/hero.webp`, 1344x752), chosen from three candidates because it maps to "find your next 100 customers"; the lens and network alternates were kept beside it as `hero-alt-lens.webp` and `hero-alt-network.webp` until the 2026-09-17 dead-asset sweep removed them; both remain in git history.webp` so a swap is a one-line change. Preload link and alt text updated; the old file stays in `/images` for the git history.

Growth OS framework pages (`/seo-growth-os`, `/meta-growth-os`, 2026-09-12). Both are dense one-off tool pages with their own component CSS, kept as-is inside a scope (`.sgos`, new `.mgos`) so nothing leaks either way. Audit found the SEO page already in the site shell but with its own hero (orange-square brand row, custom `.cta` buttons, 34px wrap padding, 52px section margins) and a closing card, and the Meta page entirely outside the shell: no `body.redesign-prototype`, its own sticky nav with the retired "H MM" text logo, its own four-column footer, Segoe UI, sans-800 headings, absolute helpmemarketing.com links, nine inline styles, Unicode box icons, and "terracotta" as an accent. Now: both open on the shared `.hero.svc-hero` grid with a generated image (`/assets/growth-os/seo.webp` gears-and-ranking-ladder, `/assets/growth-os/meta.webp` ad-funnel-chart-refresh loop), a "Framework · …" eyebrow, `hero-headline` with `<em>`, `.hero-ctas` (the download button keeps its `data-gate-open` / `data-dl` hook) and a new shared `.hero-note` (13px tertiary line under hero CTAs, added to styles.css); both close on the shared `.final-cta-section` (Meta keeps `id="download"`). Rhythm is 48px between sections (32 on phones). The Meta page is transplanted into the canonical nav and F2 footer, its CSS scoped under `.mgos` with `:root`/`body`/`*` mapped onto the wrapper, Inter body type, Fraunces 40/400 H2s with italic orange `<em>`, heading weights 800 lifted to 600, terracotta tokens mapped to Signal Orange (copy updated), Tabler SVGs for the two tool icons, root-relative links, inline styles moved to classes, download modal parked after the footer in its own `.mgos` wrapper (outside `.page-enter`, like the SEO gate). Small-text floor on both: nothing under 10px, labels 12px; the dense tier and stage tags sit at 10px by design. Pickers, command copy, SEO gate (Apps Script) and Meta modal/zip download verified at both widths. Page-specific OG crops.

GTA MedSpa Index (`/gta-medspa-index`, 2026-09-12). The report body between the REPORT BODY markers is regenerated every cycle (002 lands 10 Dec), so this pass touches only what stays put: the head, the shell around the markers, and the page CSS. Audit found the page outside the shell (no prototype body class, its own sticky nav with the retired "HelpMeMarketing" text logo, no site footer, system-ui type, sans-700 headings, an orange kicker, card-style FAQ, labels down to 9px). Now: `body.redesign-prototype`, `.app[data-screen-label="gta-medspa-index"]`, the canonical nav (Case Studies active), `.page-enter`, a `.msi` wrapper around the markers, and the F2 footer after them. The report's own CSS is scoped as `.msi.msi …` (doubled so it outranks the `body.redesign-prototype` tag rules in styles.css; `:root`/`body`/`*` map onto the wrapper; the old nav rules are dropped) and a neutraliser block zeroes the few unscoped styles.css rules that reach plain tags (section padding, h4 colour, li padding, .cta-card colour). CSS-only alignment of the regenerated body: the report `<header>` becomes the hero grid with the existing index illustration painted by `header::after` (`/assets/index/gta-medspa/hero.webp`), kicker muted and 12px, Fraunces H1 (64/40) and 32px H2s, 48px section rhythm (32 on phones), FAQ `details` restyled to the site ring badge with rotating plus, `.cta-btn` on the 8px radius, `.cta-card` centred, tables at 12px with 7px cell padding and wrapping headers so the scoreboard fits its card at desktop width (Inter runs wider than the system font the tables were tuned for). Small-text floor: nothing under 10px, labels 12px. The `style="width:NN%"` bars are data-bound output of the index generator and are the one sanctioned inline-style exception on the page (comment in the head CSS); flagged for founder approval. Gate form, tooltips, post-log tabs and scripts untouched. Marker comment updated so the next cycle paste keeps the shell.

Hair Loss Index and Real Estate Index (`/hair-loss-index`, `/instagram-reindex`, 2026-09-12). Same HMM Index template as the MedSpa page, same regenerate-each-cycle markers, same treatment applied by one reusable transform: prototype body class, canonical nav (Case Studies active), `.msi` wrapper around the markers, F2 footer after them, the report CSS scoped as `.msi.msi` with the MedSpa alignment block (hero grid via `header::after`, muted kicker, Fraunces headings, 48/32 rhythm, FAQ ring badge, table tightening, small-text floor) and generated hero illustrations (`/assets/index/hair-loss/hero.webp` hair strands rising from a root with post frames; `/assets/index/real-estate/hero.webp` house and tower outlines under a stack of post frames) with matching OG crops. The SVG chart card and bar widths inside the regenerated body carry inline styles from the index generator, the same sanctioned exception as the MedSpa page. Marker comments updated so the next cycle paste keeps the shell.

Case Studies, second look (`/work`, 2026-09-12). Already on canon from the first pass; the case grid section was the one section on the site without a heading, and the final CTA had a single action. Now: "Selected work" eyebrow, "Nine engagements. The numbers behind each." heading and a deck stating the measurement basis, plus a "See the portfolio" outline action beside "Book a free audit".

Tools and indexes surfacing (2026-09-12, founder brief). Homepage builds section reduced (747px to 601px at desktop, 1458 to 1023 on phones): the six client-page cards drop their descriptions and use `.pf-builds-mini` (14px padding, 16px titles, url line only; 2 columns at 900, 1 at 720); the pill row is renamed "Free AI tools and research" and now reads Marketing Audit, Ad Spend Calculator, SEO Growth OS, Meta Growth OS, "The HMM Indexes, all three" (to `/ai-tools#indexes`) and "Every free tool" (`/ai-tools`); the single-index pill and the Service documentation pill are gone. AI tools hub splits its nine cards: `#tools` keeps the six tools and frameworks, a new `#indexes` section ("Research" eyebrow, "The HMM Index: three live benchmarks.") holds the three indexes on a new `.service-grid-3` (3 columns, 1 at 900) with `Instance 01/02/03` kinds instead of the old 07 to 09 numbering; `#indexes` carries a 64px scroll margin. The finder still matches cards by `data-tool`, so the move is transparent to it. Services hub loses the "What each one does" lever list, which repeated the six category cards directly above it. Case Studies gains two sections after the case grid: "Three live indexes" (`#indexes`, same three cards) and "Six free tools and frameworks" (`#tools`, the six tool cards), both on the hub's card markup without `data-tool` attributes.

CTA labels and colours (2026-09-12, founder brief). Sitewide rule by destination: any button to `/contact` reads "Need Help? Let's Talk" (trailing arrow kept where the button had one, inline arrow icon kept in the footer), any button to `/tools/marketing-audit` reads "Free AI Audit". Applied across 48 files and both audit scripts: nav pills, mobile menu, hero and final CTA buttons, blog sidebar and closing buttons, footer offer and tool buttons, the homepage pill, the Growth OS setup buttons, the Index pages' clinic-position button, and the card arrows on the audit tool cards ("Free AI Audit →"). Prose links ("tell us", "bring in help", the footer "Contact" sitemap link) are sentences, not buttons, and are unchanged. Colour: see Colour System Decision 14 (orange fill for contact, Mint outline for the audit).

Instagram in the footer social row (2026-09-13). `https://www.instagram.com/helpmemarketing1/` joins LinkedIn and Facebook in `.footer-social` on all 48 pages (`/assets/brand/instagram-color.svg`, 16px, `.logo-instagram`), and in the Organization schema `sameAs` on the three pages that carry it (home, AI marketing agency, AI agents Halton).

Phone-width overflow fixes (2026-09-16, from the SEO Growth OS run). REC-307: `/portfolio` scrolled sideways at 320 and 375px because the two-column `.pf-results` track could not shrink below the nowrap client line in each tile. Tracks are now `minmax(0, 1fr)` with `min-width: 0` on `.pf-result`, wrapping `.pf-client`, and `overflow-wrap: anywhere` on labels. The same sweep, run on all 48 pages at both widths, found two more the report's 23-URL sample did not cover: `/work` at 320 (case-study card header could not wrap; now `minmax(0, 1fr)`, `min-width: 0`, header `flex-wrap`) and `/ad-calculator` at both widths (the 420px inputs column had no phone rule; now single column below 900 with the inputs card static, two-column button grids and single-column stat and breakdown grids below 720). All 48 pages pass at 320 and 375 after the fix. Verified in the same pass: `/hipaa-checklist` is a permanent 301 in `vercel.json`, not a rewrite.

REC-205 and LCP (2026-09-16). Main-thread blocking on the Index template: the cost was the DOM itself (7,442 nodes on the MedSpa page, most of them the 488-row post log), not the tab and filter scripts. The three Index pages now set `content-visibility: auto` with a 640px intrinsic-size placeholder on every report section except the header and first section, so off-screen sections skip layout and paint until they approach the viewport. Local reading under 4x CPU throttling on a phone viewport: MedSpa blocking time 822 to 1,740ms before, 31 to 86ms after; Hair Loss 335 to 346ms before, 33 to 52ms after. CSS-only, in the head, so it survives the cycle regeneration. One side effect handled: a hash jump would land short because sections above the target render at full size after the jump, so a small head script (also outside the regenerated body) switches the deferral off for that visit via `.msi-hash` and re-jumps once layout and lazy images settle; verified on `#faq` for both load-with-hash and in-page hash change under 4x CPU throttling. LCP on `/ai-marketing-agency`: the page has no image, its LCP element is the H1, and locally it performs the same as the other templates, so the report's 4 to 6.5s reading is most likely run variance. One sitewide cause was real and is fixed: the `.page-enter` entry animation faded from opacity 0 over 350ms, and Chrome does not count an element as painted until it is visible, so every page's hero headline registered LCP roughly 350ms after the logo. `pageIn` is now the 8px slide only. What remains in the LCP path on every page is the render-blocking chain of `styles.css` (56KB brotli on the CDN) and the Google Fonts stylesheet; neither is page-specific.

Self-hosted fonts (2026-09-16). The Google Fonts stylesheet was a cross-origin render-blocking request plus a second connection on every page. The site now serves the exact woff2 files Google was serving for its request, from `/assets/fonts`: Fraunces variable (opsz 9 to 144, wght 400 to 500 upright; 400 italic) and Inter variable (wght 400 to 700), latin and latin-ext subsets only, six files, 340KB on disk of which a typical page loads three (Fraunces latin, Fraunces italic latin, Inter latin, about 158KB) thanks to `unicode-range`. The `@font-face` block sits at the top of `styles.css` with `font-display: swap`; every page preloads the two latin files used above the fold; `vercel.json` serves `/assets/fonts/*` immutable for a year. Cyrillic, Greek and Vietnamese subsets were dropped: the site is English. Verified locally that all three faces load from the site, the H1 renders in Fraunces, and no request leaves for fonts.googleapis.com or fonts.gstatic.com.

CSS trim (2026-09-16). `styles.css` went from 275KB to 212KB (5,715 lines) by removing 578 rules that could never match: every one needs a class or id that appears in no served HTML file and in no JS string literal (script blocks and the three `.js` files are scanned for quoted tokens, so classes added by `classList` count as present). By region: legacy 405 rules (72KB to 30KB, mostly the retired service-detail, pricing, reviews carousel, compliance strip, F1 footer and testimonial components), blog template 29 rules (the pre-V2 `.blog-article`, `.blog-tldr`, `.blog-data-table` family), prototype 144 rules (`.sched-*` multi-step form from the removed `/schedule-a-call` page, `.tier-card`, `.pf-refs-compact`, `.hero-visual-2x2`, the F1 `.footer-column` grid, `.metric-card` and `.live-indicator`). Rule-usage coverage from Chrome (48 pages, 13 viewport widths from 370 to 1440, scrolled, with details, tabs and the mobile menu opened) was collected as a second signal but not used to delete anything: it reports rules for elements inside hidden containers as unused (the audit gate preview, the newsletter thank-you), so it cannot prove a rule dead on its own. Verification: computed styles of every element on every page (33 properties, 48 pages, widths 1440, 1050, 850, 600 and 390) were snapshotted before and after; the only differences were mid-animation transforms and opacities, and re-measuring those elements with both stylesheets gave identical values. The parser used for the walk blanks comments before scanning braces (four comments in the file contain braces, which is what broke the first attempt). Section 18 below documents the multi-step form pattern whose CSS is now gone with its page; the section stays as the spec to rebuild from if `/schedule-a-call` returns.

JS trim (2026-09-16). Same pass over the two shared scripts. `/blog/blog-template.js` (6.4KB) has nothing dead: every hook it touches (`.toc-list`, `.toc-list-mobile`, `.toc-mobile-toggle`, `.toc-mobile-panel`, `.share-icon[data-network]` with all four networks) exists on all 14 posts, and the clipboard fallback is the path older browsers still take. Left as is. `/tools/marketing-audit.js` (20.4KB to 19.3KB) lost `setupNavHamburger`, which bound to `#audit-nav-ham`, an id that no longer exists since the page took the sitewide nav (the legacy inline hamburger handles it), an unused `direction` argument on `showQuestion`, the `escapeAttr` alias and a one-call `getAnsweredCount` helper, plus the stale "Cloudflare compatibility" header comment. `/tools/marketing-audit-content.js` lost `tierOrder` and the four `range` strings, which nothing reads. Verified by driving the wizard end to end with Playwright at 1440 and 390: all eight questions with counter and dimension label, arrow-key advance, "See my results" on the last step, tier preview, invalid-email guard, results render with badge, three sections, four related links and the contact CTA when the Apps Script POST succeeds, error banner and re-enabled submit when it fails, and the mobile menu still opens. Blog template checked the same way: TOC built on desktop and phone, mobile panel opens and closes on pick, active-section highlight follows a click, share popup opens, copy link writes the URL and shows "Copied!" for two seconds.

Cookie banner and bottom-pinned controls (2026-09-17). On phones the audit wizard's Previous/Next bar is fixed to the bottom edge (768px and below) and the consent banner is fixed there too, so the banner covered the Next button until dismissed. `consent.js` now offsets itself above any element carrying `data-consent-avoid`: it measures the element, applies the height as `--hmm-consent-offset` on the banner (`bottom: calc(12px + offset)`) only while the element is actually pinned to the viewport bottom, and re-measures on resize, through a ResizeObserver on the element, and at 450ms and 1200ms after showing, because the `.page-enter` slide transforms an ancestor for its first 350ms and a fixed child measures against that ancestor rather than the viewport until it ends. The attribute is the whole contract: add it to any future bottom-fixed control and the banner clears it. Only `.audit-wizard-nav` carries it today. Verified at 390 and 768 (banner bottom 12px above the bar, Next clickable with the banner up), at 1440 (bar inline, banner at the edge), after rotating to a width where the bar goes inline (offset drops to 0), after the bar is hidden (offset drops to 0), and on the homepage and MedSpa Index (no change).

consent.js trim (2026-09-17). Audited the way the other scripts were: no dead branches. Every function runs on every page, the CSS it injects is all reachable (link, hover, focus-visible, reduced-motion, 720px variant), and the one optional hook, `#hmm-cookie-settings`, is live on /privacy. What went was shipped weight: the 1.3KB header comment (a fifth of the file) that explained GTM gating now lives in the "Consent banner, behaviour" row above, and the bottom-offset code queried `[data-consent-avoid]` twice. 7.8KB to 6.6KB. Verified the whole flow with Playwright: banner on first visit with the denied default already on the dataLayer, decline stores and emits denied and removes the banner, no banner on return with the stored choice re-asserted, the privacy reset link reopens it with a single style tag, accept stores and emits granted, and the wizard-nav offset still applies on the audit page.

marketing-audit-content.js audit (2026-09-17). Data file, so "dead" means references nothing serves. Found four: the Foundational and Growing tiers linked `/google-meta-ads` and the Scaling and Advanced tiers linked `/analytics`, both retired service URLs that 301 to the category pages. They now point straight at `/services/performance-marketing` and `/services/analytics-attribution` (the analytics label reads "Explore: Analytics and attribution services"). Every other link (five blog posts, `/ad-calculator`, `/contact`) resolves, all three contact links already carry "Need Help? Let's Talk", no em or en dashes in rendered copy, every class in the HTML strings has CSS. The header comment drops a stale build note and now states the two rules for editing the file. Whitespace inside the template literals (745 bytes) and the four tier banner comments stay: the file is copy the founder edits by hand, and readability is worth more than a kilobyte. Verified by rendering all four tiers through the live wizard locally and fetching every rendered link: all 200, no redirects.

vercel.json trim (2026-09-17). Dead here means routing rules production never reaches, proven by probing the live site. Removed 24 of 74 rules, 8.9KB to 6.2KB. (1) Nine `.html` redirects (`/healthcare-seo.html`, `/pricing.html`, the rest of that family): `cleanUrls` answers any `.html` request with a 308 to the extensionless path before the redirect table is consulted, even for files that do not exist, so those entries could never fire; the extensionless redirect then does the work, as it did before. (2) Eleven `/blog/slug` to `/blog/slug.html` rewrites: `cleanUrls` already serves them, and the three newest posts had no rewrite and serve identically. (3) Four rewrites sending `/CLAUDE.md`, `/FINDINGS.md`, `/PLAN.md` and `/docs/*` to 404: those paths are excluded from the deployment by `.vercelignore` and already 404. One redirect corrected: `/_healthcare/case-studies` pointed at `/industries/healthcare#case-studies`, an anchor that page does not have, so it now goes to `/work`. Two leaks closed while probing: `HMM_Session_Handoff_2026_05_20.md` and `HMM_Session_Handoff_Migration_Phase.md` were publicly served at the root; `.vercelignore` now excludes `HMM_Session_Handoff_*.md`. `meta-growth-os.zip` is the Meta Growth OS download and stays. Kept everything else: the www to apex redirect, 25 retired-URL redirects including the WordPress-era `/servicess/*` and `/bussiness/*` paths, the 410 rewrites for feed and wp-* probes, and the three header rules. Both open items closed the same day by founder decision: `blog/meta-attribution.html` deleted (its redirect already answered the URL), and `styles.css` now ships `max-age=600, must-revalidate`, so a returning visitor's navigations within 10 minutes reuse the cached stylesheet without a round trip on the critical path, and a CSS change reaches everyone within 10 minutes. Fonts stay immutable for a year because their filenames never change.

robots.txt and sitemap.xml trim (2026-09-17). robots.txt had ten user-agent blocks, nine of them naming an AI or search crawler, all saying the same `Allow: /` as the wildcard; a per-bot block only matters when it differs from the wildcard, so they were no-ops. Now one wildcard block, a comment saying AI crawlers are welcome, and the sitemap line (376 to 229 bytes). sitemap.xml was structurally sound (48 entries, every one a served page returning 200, canonical matching, none noindex, no page missing, no duplicates, clean-URL form throughout) but carried two dead tags and one wrong one: `changefreq` and `priority` are documented as ignored by Google and Bing, and every `lastmod` was stale (April to September dates on pages that all changed on 2026-09-16), which makes search engines distrust the field. Entries are now `loc` plus `lastmod` taken from the last git commit touching the file, and CLAUDE.md carries the one-liner to refresh them after a sweep. 8.7KB to 5.6KB. Verified: XML parses, 48 URLs, every URL fetched live at 200.

API functions audit (2026-09-17). `/api/gone.js` and `/api/tool-finder.js` are the only serverless code and both are live: every `/api/gone` rewrite source still exists in `vercel.json` and returns 410 with `X-Robots-Tag: noindex`; the finder refuses GET (405) and an empty query (400), answers a real query in about three seconds, and its nine-tool catalog matches the nine `data-tool` cards and the page-side name map on `/ai-tools` exactly. Nothing dead in either. Two small edits: the gone.js header listed a "Group B" of sources from an earlier vercel.json layout and now lists the actual rewrite sources; the finder's system prompt now asks for Canadian spelling, matching the house voice rules (a live answer had come back with "optimization"). Serverless files never reach the browser, so comment weight was not a factor here. Not changed: the model id, request shape and structured-output schema, which work in production.

Ignore files audit (2026-09-17). `.gitignore` is one line, `.claude/`, and it is live (it keeps Claude Code's local settings out of the repo); nothing to trim. `.vercelignore` had one dead rule, `/_healthcare/`, for a directory that no longer exists; removed, and the header now states the rule that every path listed must exist in the repo. The other six entries each match a tracked file or folder and each was confirmed to 404 on production. Found while checking: a leftover local `.audit-fonts/` scratch folder (580KB of woff2 from the font audit, ignored only through the container's `.git/info/exclude`, never in git) was deleted. Three tracked files are served publicly but referenced by nothing on the site: `images/hero-particle-wave.png` (903KB), `images/hero-particle-wave.webp` (56KB) and `og-image.svg` (2KB), all last touched 2026-08-13. They are the only entries in `/images/` (every live image lives under `/assets/`); left in place pending a founder call, since deleting tracked assets is beyond an ignore-file trim.

Dead-asset sweep (2026-09-17, founder call). Every tracked non-text file (149) was checked for a reference in any served text file: HTML `src`, `srcset`, `href`, `poster`, `content`, JSON-LD, CSS `url()`, JS strings, sitemap. No script builds asset paths by concatenation, so a basename match is sufficient and over-inclusive. 137 are live. Ten were not, all removed (1.15MB): the three above from `/images/` and the root `og-image.svg`; `assets/brand/facebook.svg`, `google.svg`, `linkedin.svg` and `meta.svg`, monochrome versions superseded by the `-color.svg` set every footer uses; `assets/home/hero-alt-lens.webp` and `hero-alt-network.webp`, the two homepage hero alternates generated on 2026-09-12 and never chosen (recoverable from git history at that commit if wanted); and `favicon-512x512.png`, which no page linked and which only a web manifest would use. The `/images/` folder is now gone; all live imagery is under `/assets/`. Exempt by design: `cff6589d2b8f4a74bc70e1588e70efe4.txt` is the IndexNow key file that Bing fetches, referenced by nothing on the site. Verified after removal by loading all 48 pages locally and checking every `<img>` decoded with a non-zero width and no request returned 404.

Blog images folder (2026-09-17). Nothing unreferenced: each of the 14 posts had a webp for the page and a 2K PNG master. The PNGs were 12.1MB of the folder's 13MB and served only `og:image`, `twitter:image` and (on five posts) the BlogPosting `image`, where every other page on the site uses a 1200x630 JPG. Each PNG was resized to cover and centre-cropped to 1200x630 at JPEG q80 progressive (`[slug]-og.jpg`, 16 to 83KB, 732KB for all 14), every post's three references repointed, `og:image:width` and `og:image:height` meta added to all 14 (only the non-blog pages had them), and the PNGs removed from the repo; the masters stay local per the template workflow. Folder 13MB to 1.4MB. Blog Template Master Reference bumped to 2.8 (head template, schema, hero markup, Part 6 spec table and workflow all say webp + og.jpg now); CLAUDE.md hero-image bullets match. Verified locally: all 28 social, schema and page image URLs across the 14 posts fetch at 200, every og.jpg is exactly 1200x630, and every post carries the width and height meta.

Assets folder weight pass (2026-09-17). All 109 files under `/assets` inventoried with size, dimensions and use. The hero webps (1344x752, 17 to 83KB), the OG JPEGs (1200x630, 47 to 97KB), the six font files, brand SVGs, client marks and portfolio posters are all sized for their jobs and were left alone. Three things were not: `assets/index/gta-medspa/hero.png` (959KB) was referenced by nothing, having slipped through the earlier sweep only because its basename matched the blog hero PNGs that existed at the time; removed. `assets/index/gta-medspa/og.png` (489KB) was the one OG image on the site still stored as PNG; now `og.jpg` at 55KB, the three head references updated. The eight MedSpa reel cover frames were 720 to 1080 wide (99 to 153KB each) for a four-column grid that renders them at about 260px; downscaled in place to 640 wide at q80 (57 to 81KB), same filenames so the regenerated report body keeps working, same aspect so the `width`/`height` attributes still reserve the right box. Folder 8.2MB to 6.4MB. The two portfolio mp4 clips (1.1MB together) are the largest remaining files and are legitimately video. Verified locally by loading the MedSpa page with every frame forced to decode and no request returning 4xx.

Portfolio clips audit (2026-09-17). The two mp4s (`clip-founder`, 738KB, 14.2s; `clip-transfer`, 372KB, 11.9s) are already as lean as they should be, so nothing changed. Both are H.264 Main at 480x854, 30fps, 368 and 190kbps video with mono 48 to 55kbps AAC, `moov` ahead of `mdat` so playback starts before the download finishes. Test re-encodes with x264 at slow preset came out larger at every sensible quality (crf 26 and 28 both above the originals), which means the source encoder already spent the bits well; anything smaller costs visible quality at the lightbox's rendered size. Loading is right too: the clips are never requested on page load (the grid shows jpg posters; the lightbox creates the `<video>` on click), confirmed with a network log at 1440 and 390 on both `/portfolio` and the homepage. One caveat on verification: the Playwright Chromium in the build environment ships without an H.264 decoder (`canPlayType` returns empty for avc1, "probably" for VP9 and AV1), so the click-to-play step could not be exercised here; H.264 in MP4 is the one format every shipping browser decodes, which is why the clips use it. A VP9 or AV1 variant would be smaller but would need a `<source>` fallback chain for Safari on older macOS and iOS, more files to maintain, for a page where the clip only loads on an explicit tap.

Client marks (2026-09-18). The eight marks in `/assets/clients` render at 28x28 in the proof ticker, the results tiles and the Case Studies cards (33 references across the homepage, `/work` and `/portfolio`). They were 96x96 RGBA PNGs, 2.7 to 8.2KB, 35.8KB together, with no metadata chunks to strip; lossless re-optimisation saved under a kilobyte. Converted to WebP at quality 85 with alpha, same 96px (3.4x the CSS size, enough for 3x screens): 1.4 to 2.8KB each, 14.3KB together, 60% smaller. All 33 references repointed, PNGs removed. Verified by decoding every mark on the three pages at 2x device scale with no 4xx, and by a ticker screenshot at 2x where the marks are indistinguishable from the PNGs.

Brand SVGs (2026-09-18). The seven files in `/assets/brand` were hand-authored and already free of editor metadata, so the pass was a minifier run (svgo 3, preset-default with `removeViewBox` off so the marks keep scaling from CSS): whitespace out, path data compacted, repeated fills hoisted. 13,463 to 8,033 bytes across the set; the two HMM marks halved (`hmm-logo-full.svg` 5,790 to 2,336, `hmm-mark.svg` 2,242 to 1,086) because their traced paths were long-hand absolute commands. Precision: the two HMM marks and the Meta mark at two decimals, the four 24-unit social icons at three, chosen by rendering each file before and after at 512px on the site background and counting changed pixels: zero for Facebook, Google and LinkedIn, four for each HMM mark, seventeen for Meta, and about 1,100 antialiasing pixels along Instagram's edges at that 32x magnification, none of which survives at the 16px the footer renders. The `role="img"` and `aria-label` inside the social files were dropped by the minifier; every use is an `<img>` whose own `alt` and `aria-hidden` govern, so nothing is lost. Filenames unchanged, no page edits.

Fonts folder (2026-09-18). The six woff2 files Google had served still carried the full weight axis (Fraunces upright 100 to 900, Inter 100 to 900) even though the `@font-face` rules declare 400 to 500 and 400 to 700, and a browser already clamps any requested weight to the declared range (the 800 in the SEO Growth OS page and the 600 to 660 on the MedSpa Index render at 700 either way). Each variable font was re-instanced with fontTools to exactly the declared range, keeping the Fraunces optical-size axis intact: `fraunces-latin` 65 to 53KB, `fraunces-latin-ext` 57 to 48KB, `inter-latin` 47 to 35KB, `inter-latin-ext` 83 to 57KB; the two italic files have no weight axis and are unchanged. Folder 348KB to 280KB; the three files a typical page loads go from 158KB to 129KB. Verified by screenshotting the homepage, the SEO Growth OS page, the MedSpa Index and a blog post at 1440 with the old files served through a route override versus the new ones: same layout to the pixel (identical page heights and text positions) with only sub-pixel antialiasing differences along glyph edges from the re-baked default instance, confirmed by eye on the hero and the densest-diff region; run-to-run noise with identical fonts was zero. Latin-ext: a scan of every served page and script found exactly one character outside the latin subsets, the rupee sign on the ad-set calculator, so the latin-ext files download on that page only (105KB for one glyph) and never elsewhere. Left as is; folding U+20B9 into the latin subset would need the full source fonts.

Favicons (2026-09-18). Three files are linked from every page: `favicon.ico`, `favicon-32x32.png` (602B) and `favicon-192x192.png` (8.7KB, apple-touch). The `.ico` was 23KB because it carried six frames, 16 through 256px; browsers read the 16 and 32 frames from an `.ico` and take anything larger from the PNG links, so the four big frames were never used. Rebuilt with the original 16 and 32 frames only, pixel-identical (zero differing pixels on both), uncompressed BMP entries rather than PNG-in-ICO so the oldest clients still parse it: 5.2KB. The link's `sizes="any"` (which means "scales to any size", true of an SVG, not an `.ico`) is now `sizes="16x16 32x32"` on all 48 pages. Verified by fetching all three files from a local server and parsing them, and by reading a nested page's icon links. Flagged, not changed: `og-image.png`, the default social image on the seven pages without their own, is a 260KB PNG where every other OG image on the site is a 1200x630 JPEG at 50 to 100KB; same treatment as the blog OG images would cut it to about a third.

Default OG image (2026-09-18, founder call). `og-image.png` (253KB) is now `og-image.jpg`, 1200x630 at JPEG quality 88 (a notch above the site's usual 80 because the logo is high-contrast line art where ringing shows first), 33KB. Thirteen references across the seven pages that use the default (homepage, privacy, terms, the three AI agency pages, and the healthcare industry page's Service schema) repointed; `og:image:width` and `height` meta added to the two of those pages that lacked them. The PNG is out of the repo. Verified by viewing the JPEG and by fetching it and every repointed page locally.

Schema logo (2026-09-18). `logo.png` (400x400, 35KB) is referenced only inside JSON-LD, 14 times across 13 pages as the Organization `logo` or `image`, so no visitor ever downloads it; only Google's and Bing's crawlers do. Still worth normalising: it is now `logo.jpg` at quality 88 (7.6KB, the same treatment as the default OG image; line art on a solid background compresses cleanly and the file stays above Google's 112px minimum). Lossless PNG optimisation would have saved under 2KB; WebP would have been 3.5KB but JPEG is the format every structured-data consumer accepts without question. All 14 references repointed, every JSON-LD block on the site (104) re-parsed as valid, and the three industry pages whose schema tag carries an extra attribute checked separately. PNG removed. Every brand asset at the root is now sized for its job: favicon.ico 5KB, favicon PNGs 0.6 and 8.7KB, og-image.jpg 33KB, logo.jpg 7.6KB.

Favicon PNGs (2026-09-18). Format is fixed: the Apple touch icon must be PNG and Safari does not take WebP favicons, so the levers were lossless optimisation and palette size. `favicon-32x32.png` (602B, 128 colours) is already optimal: lossless re-encoding saves 2 bytes and a palette version is larger. Left alone. `favicon-192x192.png` (8.7KB, 848 colours, RGB) re-encoded as a 256-colour palette PNG: 5.6KB, 36% smaller, with 19 of 36,864 pixels differing by at most 16 of 255, antialiasing along the strokes that no home-screen icon shows. Lossless alone would have saved 2.6%. Verified by decoding the new file and diffing it against the original, and by fetching it live.

Index page frames (2026-09-18). The reel cover frames render in a `.shot` box with `aspect-ratio: 4/5` and `object-fit: cover`, 254px wide at desktop and 340px on phones, so a 9:16 file is centre-cropped to 4:5 by the browser and the top and bottom fifth of its bytes never paint. Every frame is now a 640x800 WebP at quality 80, centre-cropped to that box before upload: MedSpa eight frames 547KB to 283KB, Hair Loss eight frames 512KB to 364KB, same basenames with `.webp`, both report bodies repointed, JPEGs removed. The Real Estate Index was the real finding: its eight frames were hotlinked from `api.apify.com` key-value stores with signed URLs, no `width` attribute, and three of the eight (Centurion, Starlight, Hazelview) already return "Key-value Store was not found", so those cards had been showing the template's operator-facing fallback ("Frame unavailable. Re-host this image.") to visitors. The five that still resolved (83 to 310KB, up to 1080 wide) are self-hosted at `/assets/index/real-estate/frames/[firm]-cycle001.webp`, 892KB fetched to 226KB served; the three that are gone have no `<img>` at all, and the fallback pseudo-element on all three Index pages' persistent head CSS now reads "Frame no longer available at the source", a visitor sentence rather than an instruction. Verified at 1440 and 390 on all three pages: every remaining frame decodes at 640x800 from `/assets`, no external image requests, no 4xx, box sizes unchanged, the three empty shots show the fallback once. Standing caveat, same as the MedSpa frames pass: the report bodies regenerate each cycle, so the generator has to emit self-hosted 640x800 WebP frames (and a local copy of anything it scrapes) or the next cycle reintroduces hotlinks that expire.

Hero images, right-sized (2026-09-18). Measured across every template at 1440, 1024, 768 and 390: the hero image never renders wider than 522 CSS px (505 in the two-column grid at desktop, 520 in the single column at 768, 350 on a 390 phone, and the three Index pages' `header::after` background at 504 to 520). The files were 1344x752, so on a 2x screen a quarter of every hero's pixels were downscaled away and a phone downloaded the full desktop file. Now each of the 26 page heroes is 1056x591 (2x of 522) with a 704x394 sibling (2x of a 352px phone column), both WebP quality 80, re-encoded from the 1344 files; the three Index backgrounds are 1056 only. Every hero `<img>` carries `width="1056" height="591"`, a two-candidate `srcset` and `sizes="(max-width: 900px) calc(100vw - 40px), 522px"`; the homepage preload gained matching `imagesrcset`/`imagesizes` so it fetches the same candidate the tag will pick. Bytes: the 26 primary files 1,616KB to 990KB; the 26 phone files total 471KB, about 18KB each against 62KB before. Verified with Playwright at 2x device scale: desktop and 768 pick the 1056 file, 390 picks the 704 file, exactly one hero request per page (no preload double-fetch on the homepage), the contact page's lazy hero makes no request at widths where it is hidden, no 4xx; a before-and-after diff of the rendered SEO hero at 1440 shows a mean difference under 2 of 255 from resampling, indistinguishable by eye. Blog post heroes are a separate template (`/blog/images`, 1344 wide) and were not touched.

Blog hero images (2026-09-18). Measured the same way: the post hero renders at 760 CSS px in the article column at 1440 (648 at 1024 beside the sidebar, 736 at 768, 358 on a 390 phone) and the blog index cards at 590 and 524 at desktop, 676 at 768, 314 on a phone. At 2x, 760 wants 1520px, so the existing 1344 files stay as the desktop candidate (three posts are 1376 or 1600 wide and keep their own width descriptor). What was wrong was the phone: a 358px column downloading a 1344-wide file. Each post now has a `[slug]-hero-720.webp` (720 wide, quality 80, 214KB for all 14 against 624KB for the full set), and both the post hero and the blog index card carry a two-candidate `srcset` with `sizes="(max-width: 900px) calc(100vw - 32px), 760px"` on posts and `calc(100vw - 76px), 590px` on cards. Verified at 2x device scale with Playwright: posts and the index pick the full file at 1440 and 768 and the 720 file at 390, one request per image, no duplicates, no 4xx, all 14 index cards decode after scrolling. Blog Template Master Reference 2.9 carries the template markup, the three-derivative spec and the workflow step; CLAUDE.md's hero bullet matches.

OG JPEGs audit (2026-09-18). All 43 social images (26 under `/assets`, 14 blog, the MedSpa card and the root default) are 1200x630, referenced only from their own page as `og:image`, `twitter:image` and where present the schema `image`, with no duplicates and no broken references; the root `og-image.jpg` is the shared default on six pages. Re-encoding every file at quality 80 would save 191KB of 2.8MB (7%), which means they already sit at about that quality, so the files were left alone: a second lossy pass for 7% is a bad trade on images that only social scrapers fetch. Eleven are baseline rather than progressive JPEG; that changes nothing for a scraper and re-encoding to fix it would cost the same second pass. One gap closed: seven pages (`/ad-set-calculator`, `/ai-tools`, `/hair-loss-index`, `/instagram-reindex`, `/portfolio`, `/seo-growth-os`, `/tools/marketing-audit`) declared no `og:image:width`/`height`, so scrapers had to fetch the file before sizing the card; all 48 pages now carry `1200`/`630`.

styles.css blog region trim (2026-09-18). The region between the `BLOG TEMPLATE V2` header and `body.redesign-prototype {` (the blog template, the marketing-audit tool block and the dark-theme overrides; 518 rules, 75KB, 35% of the file) was audited three ways. Selectors whose classes exist nowhere had already gone in the September 16 prune, so nothing was dead by that test. Twenty-one selectors are declared more than once in the same media context; twelve declarations in those pairs are set again by the later rule with the same selector and can never win, so the earlier copies were removed (265 bytes, the cascade result is unchanged by definition). The rules themselves were not merged: moving properties past intervening rules of equal specificity could change the cascade. The real weight was prose: 12.7KB of comments in 110 blocks, seventeen of them multi-paragraph histories (the Phase 1 consolidation note alone was 2.2KB and described an architecture and an HTML bug that no longer exist). Each long comment is now its one-line title plus a pointer to the Master Reference and Design System, where the rationale already lives; short comments were left as they were. Blank-line runs collapsed. Region 75.2KB to 69.1KB, file 211.8KB to 205.7KB. Verified by snapshotting computed styles of every element on all 14 posts, the blog index and the marketing audit page at 1440 and 390 before and after: identical apart from the known animation-timing noise. A first attempt cut the later declaration instead of the earlier one and the snapshot caught it (321 elements moved), which is the reason this check runs on every CSS change.

styles.css prototype region trim (2026-09-18). The region from `body.redesign-prototype {` to the end of the file (598 rules, 107KB, 52% of the file) got the same three audits. No dead selectors remained from the September 16 prune. Twenty-eight selectors are declared more than once in the same media context and 28 declarations in those pairs are re-set by the later rule, so the earlier copies were removed (none were in-rule fallbacks, which the script now checks for explicitly). Comments were 24KB in 145 blocks, 65 of them long; 54 were condensed to their one-line title plus a pointer to this document, and 11 were kept in full because they record a founder decision, a deprecation, or the rescue mechanism behind an approved exception (the token-shimming note, the CTA colour rule, the F2 footer spec, the ticker, the homepage consistency pass, the approved 2026-09-09 design pass). Two headers whose rules were pruned on the 16th (the deprecated F1 footer blocks) were dropped; the `/schedule-a-call` header stays because live form rules (`.hp-field`, `.req`, `.form-select`) still sit under it. Region 106.9KB to 96.1KB; file 205.7KB to 194.8KB, 275.6KB at the start of the week. Verified by computed-style snapshots of every element on all 48 pages at 1440 and 390 before and after: the only differences are animation timing and the local server port embedded in resolved background URLs. A first attempt also dropped every comment that was immediately followed by another comment; that removed 37 including a protected banner stacked above a sub-note, so it was reverted and only the two named orphans were removed by hand.

styles.css legacy region trim (2026-09-18), done in one pass. The region between the `@font-face` block and the `BLOG TEMPLATE V2` header (187 rules, 27KB, 13% of the file) had already lost 405 rules in the September 16 prune, so there was little left: three selectors declared twice in the same context with four declarations re-set by the later rule (`section` and `.container` padding, `.cta-card` radius and padding), removed; ten long comments, nine condensed to their title and one kept in full (the service-page component header carries a "must" rule); no orphaned headers. Region 27.0KB to 26.1KB, file 194.8KB to 193.9KB. Verified against the snapshot taken after the prototype trim (the file had not changed in between) by re-snapshotting all 48 pages at 1440 and 390: only animation timing and the local server port differ. That closes the stylesheet pass: 275.6KB at the start of the week to 193.9KB, 1,303 rules, three regions with one-line comment headers and eleven protected notes, every step verified by computed-style snapshots of every element on every page.

Inline styles, sitewide (2026-09-18, founder call to audit and fix in one pass). 400 `style` attributes on 48 pages. Forty-eight were the one GTM noscript iframe per page (`display:none;visibility:hidden`, the stock snippet): now `class="gtm-ns"` with the rule in `styles.css` ahead of the blog region. The other 352 were all in the three Index report bodies: 234 italic table cells, 48 bar widths, 18 zero-margin deks, 18 flex weights, 16 verdict badge colours, 17 column widths, two navy panels, two fluid SVGs, two muted notes and one zero top margin. Each kind now maps to a scoped utility class in the persistent head CSS (`.em`, `.m0`, `.mt0`, `.fx1/.fx12/.fx14`, `.w-26/.w-52`, `.verdict.ok/.avg/.crit`, `.card.navy`, `svg.fluid`, `.pnote[.mb12]`), and bar widths moved to `data-w` with a `data-bar-widths` head script that sets the width on DOMContentLoaded (`[data-w]` starts at width 0, so a bar never flashes full). No page on the site carries a `style` attribute now, which closes the open item that had these bars listed as a generator-output exception awaiting approval. Verified by computed-style snapshots of every element on the three Index pages at 1440 and 390 before and after: identical apart from the pulse-ring box-shadow, so every bar width, italic cell, margin, flex weight and badge colour reproduced exactly. The generator contract is in CLAUDE.md; until the generator adopts it, the next cycle's body will reintroduce inline styles and this conversion will need re-running (the head CSS and script persist, so re-running is the same one-pass script).

Inline event handlers (2026-09-18). One kind existed: the nav hamburger's `onclick` on all 48 pages, a three-statement toggle that set no ARIA state and could only be closed by tapping the button again. Replaced by `/site.js` (1.4KB, `defer`, loaded after `consent.js` on every page): `addEventListener` on the button, `aria-expanded` kept in step, and the menu also closes on a link tap, on Escape (returning focus to the button) and on a click outside it. The button gained `type="button"`, `aria-expanded="false"` and `aria-controls`; the menu div gained `id="nav-mobile-menu"`. No served page now carries an `on*` attribute or a `style` attribute. Verified with Playwright at 390 on five templates (homepage, a post, an Index page, the audit tool, a service page): open, close, Escape, outside click and link tap all behave, `aria-expanded` tracks, no page errors; at 1440 the hamburger stays hidden.

JSON-LD audit (2026-09-18). 129 blocks on 48 pages, 138KB of JSON (129KB minified; left readable, the 7% is not worth it on a per-page basis). Types: BreadcrumbList on 47 pages, FAQPage on 31, BlogPosting on 14, Service on 12, HowTo on 5, ProfessionalService on 4, ItemList on 4, and one each of Organization, WebSite, Blog, ContactPage, CollectionPage, Report, Dataset, WebApplication, plus two SoftwareApplication, two Article and two WebPage. Structural checks all clean: every block parses, every internal URL and image resolves to a served page or file with no redirects, no page lacks schema, no page repeats a type, every `@id` a block references is defined on the site. Semantic checks: every `FAQPage` question is a visible `<summary>` (a first pass flagged all 31 pages because the summaries carry a "+" toggle glyph in their text; normalised, all match); every `datePublished` equals its `article:published_time`; every breadcrumb ends at its own page; `dateModified` on the 14 posts and two Index pages is older than the last commit but matches each page's visible "Updated" line, so it is an editorial date and was left alone (template sweeps are not content updates). One real defect: ten `headline` values (eight posts, both Index pages) were Title Case or reworded versions of the H1, in two cases a different sentence. Google asks for the headline to match the visible title, so each now equals its H1, trailing period dropped, all under the 110-character limit. HowTo (five pages) and FAQPage no longer earn Google rich results for a commercial site since 2023 but remain valid, honest structured data that AI answer engines read; kept.

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
