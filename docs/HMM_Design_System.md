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
| `var(--text-tertiary)` | `#737373` Slate | Tertiary text, disabled |
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

- HTML: `<em>` child inside `.nav .logo`
- CSS: `body.redesign-prototype .nav .logo em { color: var(--cta) }`
- Example: `<span class="logo-text">Help<em>Me</em>Marketing</span>`

### Pattern 3 — Logo mark "MM" italic

- HTML: `<span class="me-italic">MM</span>` inside `.logo-mark` (NOT `<em>` — existing CSS targets `.me-italic` specifically)
- CSS: `body.redesign-prototype .logo-mark .me-italic { color: var(--cta) }`
- Italic enforced via legacy `.logo-mark .me-italic { font-style: italic }`
- Example: `<div class="logo-mark">H<span class="me-italic">MM</span></div>`

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
| padding | 96px 0 | 64px 0 |
| position | relative | — |
| overflow | hidden | — |

CSS location: `styles.css:3762-3766` (desktop), `styles.css:4112` (mobile)

### Content section — `section.content-section`

| Property | Desktop | ≤900px |
|---|---|---|
| padding | 96px 0 | 64px 0 |
| border-top | `1px solid rgba(255,255,255,0.15)` | — |

CSS location: `styles.css:3757-3760` (desktop), `styles.css:4111` (mobile)

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

---

## 8. Footer Architecture (F2 two-band)

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
- Sitemap heading: `var(--text-tertiary)` = `#737373`
- Sitemap link: `var(--text-muted)` = `#999999`
- Baseline text: `var(--text-tertiary)` = `#737373`

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

3 columns: Services / Industries / Company

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

#### Baseline

Two-line layout on the left, vertical-stacked legal on the right:

Left cluster (vertical):
- Partner badges (Google Partner · Meta Partner) inline
- "HelpMeMarketing · Mississauga, Ontario · Hello@helpmemarketing.com"

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

*HMM Design System v1.0 — first markdown commit*
*Source: Homepage prototype CSS at HEAD `0bfba56`*
*Companion canon: `/docs/HMM_Color_System.md`, `/docs/HMM_Content_Rules.md`*
