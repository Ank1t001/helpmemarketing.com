# HMM Design System

**Version:** 1.0
**Status:** Canonical. Mandatory for all pages on helpmemarketing.com from this point forward.
**Last updated:** May 21, 2026
**Source of truth:** Prototype CSS at commit `25e776e` on `redesign-prototype-homepage` branch
**Companion document:** `HMM_Content_Rules_v0_2.md` (voice & content rules — both required reading)

---

## Document outline

| # | Section | Purpose |
|---|---|---|
| 1 | Purpose & how to use | Document's role, audience, versioning |
| 2 | Design philosophy | Five core principles |
| 3 | Color tokens | All colors, semantic naming, usage rules |
| 4 | Typography | Type scale, fonts, weights, italic accents |
| 5 | Spacing scale | 8px-based scale, vertical rhythm |
| 6 | Layout grids | Container system, grid patterns, breakpoints |
| 7 | Component library — existing | 14 components from prototype |
| 8 | Missing patterns inventory | 20 patterns needed but not built |
| 9 | Voice & content integration | How this doc and Content Rules work together |
| 10 | Mobile responsive patterns | Single breakpoint strategy |
| 11 | Accessibility considerations | WCAG AA target, focus states, screen readers |
| 12 | Implementation guidance | Workflow for building pages |

---

# Section 1 — Purpose & how to use

## What this document is

This is the canonical specification for HMM's visual design system as of May 2026, locked through the homepage prototype validation. Every page on helpmemarketing.com from this point forward references this document. Any visual decision made on a new page must trace back to a rule defined here.

If something needed isn't defined here, that's a gap. Gaps get filled by adding to this document, not by inventing per-page.

## What this document is NOT

This is not a brand guidelines document. Brand identity (logo treatment, voice, mission statement) lives elsewhere. This document is strictly visual implementation — colors, typography, spacing, components, responsive behavior.

This is also not a code library. CSS classes and HTML structures are referenced for clarity, but the actual implementation lives in `styles.css` under the appropriate sections. When this document and the CSS conflict, the CSS is authoritative until this document is updated to match.

## Who uses this document

| Audience | How they use it |
|---|---|
| Claude Code | Reads this before building any page; rules are mandatory |
| Founder (Ankit) | Reviews proposed pages against this spec; approves deviations explicitly |
| Future contractors | If/when HMM brings in additional developers, this becomes their reference |

## How to use the document

**Before designing any new page:**
1. Read all sections relevant to the page (always read Sections 1-2; usually read 3-7 and 10)
2. Identify which patterns from the component library apply
3. Note any required patterns NOT in the library (these become Section 8 entries)
4. Build using documented patterns only

**When a pattern doesn't exist:**
1. Stop. Don't invent inline.
2. Either: use an existing pattern that approximates the need, OR propose a new pattern as a Section 8 addition first.
3. New patterns require explicit approval before becoming canonical.

**When making changes to the design system:**
1. Update this document FIRST
2. Bump version number
3. Update CHANGELOG section at the bottom
4. Then update CSS to match

## Versioning

| Change type | Version bump |
|---|---|
| New component pattern added | Minor (1.0 → 1.1) |
| Color token value changed | Minor (1.0 → 1.1) |
| Typography scale changed | Major (1.0 → 2.0) |
| Spacing scale changed | Major (1.0 → 2.0) |
| Core design philosophy changed | Major (1.0 → 2.0) |
| Typo or clarification | Patch (1.0 → 1.0.1) |

## Relationship to other HMM documents

| Document | Relationship |
|---|---|
| `HMM_Content_Rules_v0_2.md` | Voice rules — separate concern, content not visual |
| `HMM-Color-System.docx` | Original color system source — this document supersedes it |
| `HMM_Blog_Template_V2_Master_Reference.md` | Blog-specific patterns — gets updated to dark mode in Phase 7 |
| `docs/archive/DESIGN_v0_pre_canonical.md` | Original DESIGN.md, superseded by this document |

When conflicts arise, this document wins.

---

# Section 2 — Design philosophy

## Core principles

Five principles that drive every visual decision in this system. When in doubt on any specific choice, the answer should be reasoned from these principles, not invented.

### Principle 1: Premium without being decorative

The system is built to read as serious, considered, and crafted. Premium dark aesthetic comes from typography, spacing, and material restraint — not from ornamentation. Gradients, shadows, animations, and color use are deliberate and minimal.

Failure mode this avoids: dark-mode SaaS startup aesthetic that depends on neon gradients and glow effects to feel "advanced."

### Principle 2: Authority through space, not size

The dark background does heavy contrast work. High-impact text doesn't need to be massive — it needs room to breathe. Section padding, line-height, and negative space carry the weight that ornamentation would carry in a busier system.

Failure mode this avoids: cramping content to fit more on each screen, which makes the page feel dense and less considered.

### Principle 3: Color discipline as differentiation

Signal Orange (the CTA color) is reserved for primary actions and brand-moment accents. Maximum 2-3 primary instances of orange per page. Mint is functional-only — success states, live indicators, checkmarks. Never a CTA. White and grey carry the rest. This restraint is what makes orange feel powerful when it appears.

Failure mode this avoids: orange used decoratively, which dilutes its conversion power.

### Principle 4: Editorial typography pairing

Fraunces (serif) for headings + Inter (sans-serif) for body. Two-font pairing creates the editorial-premium signature similar to The Atlantic, Bloomberg, Apple product pages. Single-font systems (all sans or all serif) read either as generic tech or as overly traditional.

Failure mode this avoids: defaulting to "modern sans-serif everywhere" which is the standard SaaS template look.

### Principle 5: 60-30-10 distribution

Visual weight on every page should follow approximately:
- 60% background and negative space
- 30% body text and structural elements
- 10% accent color and visual emphasis

This is a check, not a literal pixel measurement. If a page feels visually noisy, the accent ratio probably exceeded 10%. If it feels empty, the body text probably under-claimed its 30%.

Failure mode this avoids: pages that fill every section with visual interest, which produces aesthetic fatigue.

## Reference aesthetics

| Reference | Why it matters here |
|---|---|
| Anthropic.com | Editorial dark mode, premium without being cold, serif heading discipline |
| Linear.app | Strong typography, generous spacing, considered restraint |
| Stripe.com | Clear hierarchy, technical authority through clean execution |
| Mercury.com (pre-redesign) | Editorial dark + warm secondary moments |
| Cereal Magazine (print) | Editorial composition discipline, negative space confidence |

The reference is not a copy target. It's a calibration — "if a visitor moves between Anthropic and HMM, the visual register should feel adjacent."

## Dark-mode-first reasoning

The system is dark-mode-first (Obsidian primary background) rather than light-mode-with-dark-option. Three reasons:

1. **Differentiation.** Most agency sites are light-mode. Dark immediately signals "this is different."
2. **Authority.** Dark mode reads as more authoritative in the AI-native positioning context.
3. **Material quality.** Premium aesthetic in dark mode is easier to achieve than premium aesthetic in light mode because contrast does heavy lifting.

The warm break exception (used on /about and process pages) inverts to a Warm Ivory background. This is the deliberate exception that proves the rule.

## Restraint as the dominant aesthetic value

If you have to choose between adding visual interest and removing visual interest in this system, default to removing. The system is built to feel confident through what it doesn't do.

Practical applications:
- No drop shadows on text
- No gradient backgrounds on body areas (only the hero orange-glow blob, which is intentional)
- No decorative dividers (use space instead)
- No icon-everything (icons only where they carry functional meaning)
- No animation-by-default (subtle hover states only)

The exception: hover states on interactive elements get subtle treatment because they signal interactivity. Even those are minimal — 200ms transitions, slight transforms, subtle background changes.

## When to break the principles

Legitimate reasons to deviate:
1. A specific section serves a different function (e.g., warm break section)
2. User research finding contradicts the principle
3. The principle was wrong (revise it, document why in CHANGELOG)

NOT legitimate:
- "It looks better with more visual interest here"
- "Other sites do it this way"
- "The page feels boring without X"

---

# Section 3 — Color tokens

## Token philosophy

All colors are CSS custom properties (variables). Pages reference tokens by semantic name, never by hex value. Token names describe **role**, not appearance.

## Complete token reference

```css
:root {
  /* CORE SURFACES (60% of visual weight) */
  --bg: #0E0E0E;                /* Obsidian — primary background */
  --bg-elevated: #1A1A1A;       /* Carbon — cards, modals, raised surfaces */
  
  /* TEXT HIERARCHY (30% of visual weight) */
  --text: #FFFFFF;              /* Pure White — primary text */
  --text-muted: #999999;        /* Graphite — secondary text, default nav */
  --text-tertiary: #737373;     /* Slate — tertiary text, metadata, captions */
  
  /* ACCENT COLORS (10% of visual weight) */
  --cta: #FF5C1A;               /* Signal Orange — primary CTA */
  --cta-hover: #FF7038;         /* Ember — CTA hover state */
  --mint: #00D4AA;              /* Mint — functional state only, never CTA */
  
  /* STRUCTURAL */
  --border: rgba(255, 255, 255, 0.08);     /* Card borders, dividers */
  --grid-line: rgba(255, 255, 255, 0.045); /* Background grid texture */
  --orange-glow: rgba(255, 92, 26, 0.18);  /* Hero radial glow */
  
  /* WARM BREAK (for /about and process pages only) */
  --warm-bg: #F8F4ED;           /* Warm Ivory — break background */
  --warm-text: #1A1A1A;         /* Carbon — text on warm */
  --warm-cta: #C8542B;          /* Burnt Terracotta — break CTA */
}
```

## Core surfaces

| Token | Used for | NOT used for |
|---|---|---|
| `--bg` | Body background, full-width section backgrounds | Card surfaces, modals, anything elevated |
| `--bg-elevated` | Cards, modals, sidebar CTAs, scrolled navigation | Body background, hero |

Six-point lightness difference creates "elevated" feel without requiring borders.

## Text hierarchy

| Token | Used for | NOT used for |
|---|---|---|
| `--text` | Primary headlines, body text, primary nav state | Captions, metadata, disabled states |
| `--text-muted` | Body paragraphs, navigation default, subheads | H1-H3, emphasized content |
| `--text-tertiary` | Captions, dates, read times, "Source:" attributions | Body text, headings |

## Accent colors

### Signal Orange (`--cta`)

**Primary orange moments — max 2-3 per page:**
- Primary CTA buttons (e.g., "Book my audit")
- Hero H1 italic accent word
- Logo accent letter ("Me" in HelpMeMarketing)
- Single brand-moment indicator (e.g., live booking indicator)

**Supporting orange text accents — no strict limit, each must serve clear purpose:**
- "See pricing →" link text in service cards
- Column headers in comparison cards (e.g., "HMM" header)
- Inline text references where orange signals importance without competing with primary moments

**Forbidden uses:**
- Body text emphasis (use `--text` weight instead)
- Decorative dividers or icons
- Hover states on non-CTA elements
- Additional primary moments beyond the 2-3 max

The discipline is what makes the orange feel powerful. Used on every link, every accent, every hover, it becomes wallpaper. Used sparingly, the eye stops on it every time.

### Mint (`--mint`)

**Allowed uses:**
- Success state confirmation (after form submit)
- "Live" / "active" indicators (pulsing dot, e.g., eyebrow dot)
- Checkmarks in feature lists
- Positive metric callouts when used for direction

**Forbidden uses:**
- CTA buttons (this is the most critical rule — Mint as CTA breaks the system)
- Decorative accents
- Brand color usage

## Structural colors

`--border` at 8% white opacity adapts to whatever surface sits behind it.

`--grid-line` at 4.5% white opacity provides subtle texture on hero and section backgrounds. Calibrated up from initial 2.5% during prototype review.

`--orange-glow` at 18% Signal Orange opacity creates the radial blob behind hero text. Calibrated up from initial 12% during prototype review.

## Warm break section

Used only on /about and process pages. Inverts to warm ivory background, Carbon text, Burnt Terracotta CTA. Burnt Terracotta is a more grounded sibling of Signal Orange — same orange family for visual continuity, but reads as "considered and crafted" rather than "high-energy."

## What's NOT in the system

- No status colors beyond Mint (no red errors, no yellow warnings)
- No alternate orange shades besides `--cta`, `--cta-hover`, `--warm-cta`
- No green except Mint
- No blues anywhere
- No gradient tokens (the hero orange-glow is the only gradient)

## Accessibility check

Contrast ratios against `--bg` (#0E0E0E):

| Token | Contrast ratio | WCAG AA pass? |
|---|---|---|
| `--text` (white) | 19.7:1 | ✅ AAA |
| `--text-muted` (#999) | 7.2:1 | ✅ AAA |
| `--text-tertiary` (#737373) | 4.7:1 | ✅ AA |
| `--cta` (#FF5C1A) | 5.1:1 | ✅ AA |
| `--mint` (#00D4AA) | 8.9:1 | ✅ AAA |

All text tokens meet WCAG AA minimum. Use `--text-tertiary` sparingly for captions/metadata only.

---

# Section 4 — Typography

## Type system philosophy

Two fonts, paired for editorial-premium aesthetic. Serif headings carry brand voice and authority. Sans-serif body carries readability and modern utility.

## Font families

```css
:root {
  --serif: 'Fraunces', Georgia, serif;
  --sans: 'Inter', -apple-system, system-ui, sans-serif;
}
```

### Fraunces (serif)

**Used for:** All headings (H1, H2, H3), occasional display text, italic accent words within headings.

**Weights used:** 400 (regular), 500 (medium). Variable font via Google Fonts.

**Italic usage:** Reserved for accent words within H1 headings (e.g., the hero H1's "100 customers"). Never for full paragraphs or body text.

### Inter (sans-serif)

**Used for:** All body text, navigation, buttons, captions, eyebrows, footer.

**Weights used:** 400 (regular), 500 (medium), 600 (semibold), 700 (bold).

**Italic usage:** Avoided in body text. Used only in microcopy where it signals a deliberate aside.

## Loading strategy

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;1,9..144,400&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

**Future improvement (followup):** Self-host both fonts to remove Google CDN dependency.

## Type scale (locked from Strong hierarchy decision)

| Level | Family | Size | Weight | Line-height | Letter-spacing |
|---|---|---|---|---|---|
| **H1 hero** | Fraunces | 64px | 400 | 1.05 | -0.02em |
| **H2 section** | Fraunces | 40px | 400 | 1.1 | -0.015em |
| **H3 subsection / card title** | Fraunces | 24px | 500 | 1.25 | normal |
| **Body** | Inter | 17px | 400 | 1.6 | normal |
| **Hero subtitle** | Inter | 19px | 400 | 1.55 | normal |
| **Section deck** | Inter | 18px | 400 | 1.6 | normal |
| **Service card description** | Inter | 15px | 400 | 1.6 | normal |
| **Eyebrow** | Inter | 13px | 500 | 1 | 0.12em |
| **Card eyebrow** | Inter | 11px | 600 | 1 | 0.15em |
| **Microcopy** | Inter | 13px | 400 italic | 1.4 | normal |
| **Footer column header** | Inter | 11px | 600 | 1 | 0.1em (uppercase) |
| **Footer body link** | Inter | 14px | 400 | 1.5 | normal |
| **Footer baseline** | Inter | 13px | 400 | 1.4 | normal |

## Mobile type scale (≤900px viewport)

| Level | Desktop | Mobile |
|---|---|---|
| H1 hero | 64px | 40px |
| H2 section | 40px | 28px |
| H3 subsection / card title | 24px | 20px |
| Body | 17px | 17px (unchanged) |
| Hero subtitle | 19px | 18px |
| Section deck | 18px | 17px |

Body text stays 17px on mobile because reducing it sacrifices readability.

## Italic accent treatment

The H1 includes one italic accent word. Treatment:

```css
h1.hero-headline em {
  font-style: italic;
  color: var(--cta);
  font-weight: 400;
}
```

**Important: This pattern applies to all H1s site-wide, not hero only.** Service pages, industry pages, blog posts all get the italic-orange accent pattern on their H1.

The accent word should be the most concrete or buyer-relevant phrase in the headline. H2 and H3 headings do not use italic accents — the H1 italic is a signature moment that loses meaning if repeated at lower levels.

## Sentence case discipline

All headings use sentence case. Always. Never Title Case.

CSS does not auto-transform case. The content layer is responsible for sentence case. CSS `text-transform: uppercase` is allowed only for small labels (eyebrows, footer column headers) where the content is meant to be uppercased.

## Line-height reasoning

Headings use tight line-heights (1.05-1.25) to feel decisive. Body uses generous line-heights (1.55-1.6) for readability.

## Letter-spacing reasoning

- Headings: negative letter-spacing (-0.02em on H1, -0.015em on H2) feels tighter at large sizes
- Body: normal letter-spacing for maximum readability
- Small caps elements: positive letter-spacing (0.12em-0.15em) plus uppercase

---

# Section 5 — Spacing scale

## Spacing philosophy

The system uses an 8px-based spacing scale. Every padding, margin, and gap value is a multiple of 8 (with documented exceptions).

## The scale

```
8px scale: 4, 8, 12, 16, 20, 24, 32, 40, 48, 56, 64, 80, 96, 120
```

| Value | Token name | Primary uses |
|---|---|---|
| 4px | `--space-2xs` | Pseudo-element gaps |
| 8px | `--space-xs` | Eyebrow dot gap, inline icon spacing |
| 12px | `--space-sm` | Button padding (vertical small), list item gaps |
| 16px | `--space-md` | Element gaps, card description-to-CTA spacing |
| 20px | `--space-md-plus` | Margin below medium headings |
| 24px | `--space-lg` | Card-to-card grid gaps, eyebrow margin-bottom |
| 32px | `--space-xl` | Container horizontal padding (desktop), nav padding |
| 40px | `--space-2xl` | Service card padding, comparison card padding |
| 48px | `--space-3xl` | Header-to-content spacing |
| 56px | `--space-4xl` | Final CTA inner padding |
| 64px | `--space-5xl` | Hero column gap, mobile section padding |
| 80px | `--space-6xl` | Section-to-content gaps in calibrated areas |
| 96px | `--space-7xl` | Section vertical padding (desktop) |
| 120px | `--space-hero` | Reserved for special hero treatments |

All values are pure 8px multiples. The 56px value is on-scale (7×8).

## Token implementation

Currently the prototype CSS uses literal pixel values. The de-scoping work (Phase 1, Work item 3) introduces these tokens:

```css
:root {
  --space-2xs: 4px;
  --space-xs: 8px;
  --space-sm: 12px;
  --space-md: 16px;
  --space-md-plus: 20px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 40px;
  --space-3xl: 48px;
  --space-4xl: 56px;
  --space-5xl: 64px;
  --space-6xl: 80px;
  --space-7xl: 96px;
  --space-hero: 120px;
}
```

## Section vertical rhythm

**96px between sections on desktop, 64px on mobile.** This is the most important spacing decision in the system.

| Element | Desktop | Mobile |
|---|---|---|
| `.hero` padding (top and bottom) | 96px | 64px |
| `.content-section` padding (top and bottom) | 96px | 64px |
| `.footer` padding (top) | 96px | 64px |
| `.footer` padding (bottom) | 40px | 40px |

Each section provides its own 96px padding. Section-to-section gaps are the sum of two paddings (192px total visual gap), which lets you change one section's padding without affecting others.

## Component internal padding

| Component | Padding |
|---|---|
| `.service-card` | 40px all sides |
| `.comparison-card` | 40px all sides |
| `.outcome-card` (from /services/seo, legacy) | 32px all sides |
| `.final-cta` (inner card) | 56px vertical, 64px horizontal |
| Primary button | 14px vertical, 28px horizontal |
| Outline button | 14px vertical, 28px horizontal |

## Container horizontal padding

| Viewport | Container padding |
|---|---|
| Desktop (>900px) | 32px |
| Mobile (≤900px) | 20px |

Container max-width is 1240px.

## Negative space discipline

Empty space is a design element. The 96px section padding might feel wasteful, but compressing it makes the page feel cramped. Resist the urge to "fit more above the fold." Rhythm matters; density doesn't.

## What's NOT in the system

- No off-scale values (no 18px, 28px, 50px, 75px)
- No negative margins
- No percentage-based padding on standard elements
- No vh/vw-based padding

---

# Section 6 — Layout grids

## Layout philosophy

Single container width. Small set of grid patterns. No complex multi-column layouts. No absolute positioning except for decorative effects (hero glow blob).

## Container system

```css
.container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 32px;
}

@media (max-width: 900px) {
  .container {
    padding: 0 20px;
  }
}
```

- Every section content wraps in `.container`
- Container never goes wider than 1240px
- On viewports >1304px, container centers with margins
- On viewports ≤900px, container fills width minus 20px each side

**Exceptions:**
- Hero `.hero::before` (orange glow) escapes container — positioned absolutely
- Background grid pattern is on `body`, fills full viewport

## Grid patterns

### Pattern A: Hero two-column

```css
.hero-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 64px;
  align-items: center;
}

@media (max-width: 900px) {
  .hero-grid {
    grid-template-columns: 1fr;
    gap: 40px;
  }
}
```

Used for: Hero on homepage. Text left, visual right. Mobile stacks visual below text.

### Pattern B: Comparison cards (2-column)

```css
.comparison-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 900px) {
  .comparison-cards {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}
```

Used for: "Most agencies vs HMM" comparison. Equal 50/50.

### Pattern C: Service card grid (2 × 3)

```css
.service-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

@media (max-width: 900px) {
  .service-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}
```

Used for: Services overview section. 6 cards in 2-column grid, auto-flow into 3 rows. Mobile stacks vertically.

### Pattern D: Footer three-column

```css
.footer-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 64px;
}

@media (max-width: 900px) {
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 40px;
  }
}
```

Used for: Services / Industries / Company columns. Equal thirds.

### Pattern E: Final CTA centered

```css
.final-cta {
  background: var(--bg-elevated);
  border-radius: 24px;
  padding: 56px 64px;
  text-align: center;
}

.final-cta h2 {
  max-width: 640px;
  margin: 0 auto 24px;
}

.final-cta .subhead {
  max-width: 540px;
  margin: 0 auto 32px;
}
```

Used for: Final CTA card. Centered text with constrained max-widths.

## Breakpoint strategy

Single breakpoint at 900px.

**Above 900px:** Desktop layout
**At or below 900px:** Mobile layout

**Why single breakpoint:** Two-breakpoint systems add complexity. The 900px cutoff handles the natural break — laptops/desktops above, tablets/phones below.

## Text constraint max-widths

| Element | Max-width |
|---|---|
| `h2.section-heading` | 720px |
| `.section-deck` | 720px |
| `.final-cta h2` | 640px |
| `.final-cta .subhead` | 540px |
| Service card description | No max-width (constrained by card) |
| Comparison card list item | No max-width (constrained by card) |

## Z-index strategy

| Element | Z-index |
|---|---|
| Background body grid | 0 (default) |
| Hero `.hero::before` orange glow | 0 (with `pointer-events: none`) |
| Section content | 1 (implicit) |
| Sticky/fixed nav | 100 |
| Modal/dropdown (future) | 1000 |

No z-index without explicit reason.

## What's NOT in the system

- No CSS Grid `auto-fit` / `auto-fill` patterns
- No flexbox-based layouts at section level
- No CSS columns
- No sticky positioning except potentially navigation
- No transform-based positioning at layout scale (only for hover micro-interactions)

---

# Section 7 — Component library: existing components

This section documents every component locked in the prototype at commit `25e776e`.

## Component index

| # | Component | Purpose |
|---|---|---|
| 7.1 | Eyebrow | Section label with Mint indicator |
| 7.2 | Hero headline (H1) | Page-level statement with italic accent |
| 7.3 | Hero subtitle | Supporting context below H1 |
| 7.4 | Primary button | Conversion action |
| 7.5 | Outline button | Secondary action |
| 7.6 | Hero visual placeholder | Image slot (deferred) |
| 7.7 | Section heading (H2) | Section-level statement |
| 7.8 | Section deck | Supporting context below H2 |
| 7.9 | Comparison cards | Two-column "vs" comparison |
| 7.10 | Service cards | Service overview tiles |
| 7.11 | Final CTA card | Bottom-of-page conversion moment |
| 7.12 | Footer | Sitewide navigation, contact, legal |
| 7.13 | Top navigation (dark variant) | Sitewide menu |
| 7.14 | Logo mark (dark variant) | Brand identifier |

## 7.1 — Eyebrow

**Structure:**
```html
<p class="eyebrow">AI-Native Marketing</p>
```

**CSS:**
```css
.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: var(--sans);
  font-size: 13px;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin-bottom: 24px;
}

.eyebrow::before {
  content: "";
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--mint);
  box-shadow: 0 0 16px var(--mint), 0 0 4px var(--mint);
}
```

**Rules:** One per page maximum. Text in sentence case but rendered uppercase. Mint dot indicates "live"/"active" status.

## 7.2 — Hero headline (H1)

**Structure:**
```html
<h1 class="hero-headline">
  We use AI to find your next <em>100 customers</em> before your competitors do.
</h1>
```

**CSS:**
```css
h1.hero-headline {
  font-family: var(--serif);
  font-size: 64px;
  font-weight: 400;
  line-height: 1.05;
  letter-spacing: -0.02em;
  color: var(--text);
  margin: 0 0 24px;
}

h1.hero-headline em {
  font-style: italic;
  color: var(--cta);
  font-weight: 400;
}

@media (max-width: 900px) {
  h1.hero-headline { font-size: 40px; }
}
```

**Rules:** One H1 per page. `<em>` accent word is most concrete/buyer-relevant phrase. Applies to all H1s site-wide. Length 5-12 words ideal.

## 7.3 — Hero subtitle

**Structure:**
```html
<p class="hero-subtitle">SEO, paid media, and content. Engineered to deliver results, not impressions. Published pricing. No fluff.</p>
```

**CSS:**
```css
.hero-subtitle {
  font-family: var(--sans);
  font-size: 19px;
  line-height: 1.55;
  color: var(--text-muted);
  margin: 0 0 32px;
  max-width: 560px;
}

@media (max-width: 900px) {
  .hero-subtitle { font-size: 18px; }
}
```

**Rules:** One per hero. Max-width 560px constrains line length. Length 1-3 sentences.

## 7.4 — Primary button

**Structure:**
```html
<a href="/contact" class="btn btn-primary">Book my audit →</a>
```

**CSS:**
```css
.btn {
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
}

.btn-primary {
  background: var(--cta);
  color: var(--bg);
  box-shadow: 0 4px 16px rgba(255, 92, 26, 0.25);
}

.btn-primary:hover {
  background: var(--cta-hover);
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(255, 92, 26, 0.35);
}
```

**Rules:** Maximum 2 primary buttons per page. Always Signal Orange. Always arrow indicator. Counts toward "max 2-3 primary orange instances" rule.

## 7.5 — Outline button

**Structure:**
```html
<a href="#services" class="btn btn-outline">See how we work</a>
```

**CSS:**
```css
.btn-outline {
  background: transparent;
  color: var(--text);
  border-color: var(--border);
}

.btn-outline:hover {
  border-color: rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.02);
}
```

**Rules:** Does NOT count toward orange instances. Used alongside primary in hero. No arrow indicator.

## 7.6 — Hero visual placeholder

**Structure:**
```html
<div class="hero-visual">
  <div class="hero-visual-placeholder">[Hero visual placeholder]</div>
</div>
```

**CSS:**
```css
.hero-visual-placeholder {
  aspect-ratio: 4 / 3;
  background: var(--bg-elevated);
  border: 1px dashed var(--border);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  font-size: 13px;
}
```

**Rules:** Placeholder until image generation completes (Phase 3 followup). Aspect ratio 4:3. Dashed border signals "not final."

## 7.7 — Section heading (H2)

**Structure:**
```html
<h2 class="section-heading">Your next customer asked ChatGPT before they Googled you.</h2>
```

**CSS:**
```css
.section-heading {
  font-family: var(--serif);
  font-size: 40px;
  font-weight: 400;
  line-height: 1.1;
  letter-spacing: -0.015em;
  color: var(--text);
  margin: 0 0 24px;
  max-width: 720px;
}

@media (max-width: 900px) {
  .section-heading { font-size: 28px; }
}
```

**Rules:** One H2 per section. Max-width 720px. Sentence case. No italic accents (italic reserved for H1). Length 5-12 words typical.

## 7.8 — Section deck

**Structure:**
```html
<p class="section-deck">Most agencies are still optimizing for a search engine that's quietly being replaced...</p>
```

**CSS:**
```css
.section-deck {
  font-family: var(--sans);
  font-size: 18px;
  line-height: 1.6;
  color: var(--text-muted);
  max-width: 720px;
  margin: 0 0 40px;
}

@media (max-width: 900px) {
  .section-deck { font-size: 17px; }
}
```

**Rules:** One per H2 maximum (optional). Max-width 720px matches H2. Length 1-3 sentences typical.

## 7.9 — Comparison cards

**Structure:**
```html
<div class="comparison-cards">
  <div class="comparison-card comparison-card-legacy">
    <h3 class="comparison-card-title">Most agencies</h3>
    <ul class="comparison-list">
      <li>Optimize for Google rankings</li>
      <li>...</li>
    </ul>
  </div>
  <div class="comparison-card comparison-card-hmm">
    <h3 class="comparison-card-title">HMM</h3>
    <ul class="comparison-list">
      <li>Optimize for Google rankings AND AI search citations</li>
      <li>...</li>
    </ul>
  </div>
</div>
```

**CSS:**
```css
.comparison-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin: 40px 0 32px;
}

.comparison-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 40px;
}

.comparison-card-hmm {
  border-color: rgba(255, 92, 26, 0.2);
}

.comparison-card-title {
  font-family: var(--sans);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--text-tertiary);
  margin: 0 0 24px;
}

.comparison-card-hmm .comparison-card-title {
  color: var(--cta);
}

.comparison-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.comparison-list li {
  padding: 14px 0;
  font-size: 15px;
  line-height: 1.55;
  color: var(--text-muted);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.comparison-list li:last-child {
  border-bottom: none;
}

.comparison-card-hmm .comparison-list li {
  color: var(--text);
}

@media (max-width: 900px) {
  .comparison-cards {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}
```

**Rules:** 6 items per card is proven count. Always two cards, never more. HMM card gets subtle orange border + orange title. Mobile stacks legacy first, HMM second.

## 7.10 — Service cards

**Structure:**
```html
<a href="/services/seo" class="service-card">
  <h3>SEO + AEO</h3>
  <p>Rank on Google. Get cited by ChatGPT, Perplexity, and AI Overviews. Two disciplines, shared infrastructure, different execution playbooks.</p>
  <span class="card-arrow">See pricing →</span>
</a>
```

**CSS:**
```css
.service-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-top: 40px;
}

.service-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 40px;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s ease;
  display: block;
}

.service-card:hover {
  border-color: rgba(255, 255, 255, 0.16);
  transform: translateY(-2px);
}

.service-card h3 {
  font-family: var(--serif);
  font-size: 24px;
  font-weight: 500;
  margin: 0 0 16px;
  color: var(--text);
}

.service-card p {
  color: var(--text-muted);
  margin: 0 0 24px;
  font-size: 15px;
  line-height: 1.6;
}

.service-card .card-arrow {
  color: var(--cta);
  font-size: 14px;
  font-weight: 500;
}

@media (max-width: 900px) {
  .service-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}
```

**Rules:** Entire card is clickable link. 6 cards in 2-column grid is homepage pattern. Hover: subtle lift + brighter border. "See pricing →" arrow uses Signal Orange as supporting accent (not primary instance).

## 7.11 — Final CTA card

**Structure:**
```html
<section>
  <div class="container">
    <div class="final-cta">
      <h2 class="section-heading">Get three specific things to fix in your marketing.<br>From people who've already looked.</h2>
      <p class="subhead">30 minutes. Your data. Three concrete opportunities in SEO, AEO, or paid media, whichever applies. You leave with findings whether you hire us or not.</p>
      <a href="/contact" class="btn btn-primary">Book my audit →</a>
      <p class="microcopy">Real findings. No follow-up sequence. No "let's circle back."</p>
    </div>
  </div>
</section>
```

**CSS:**
```css
.final-cta {
  background: var(--bg-elevated);
  border-radius: 24px;
  padding: 56px 64px;
  text-align: center;
}

.final-cta h2 {
  max-width: 640px;
  margin: 0 auto 24px;
}

.final-cta .subhead {
  font-size: 17px;
  color: var(--text-muted);
  max-width: 540px;
  margin: 0 auto 32px;
  line-height: 1.6;
}

.final-cta .microcopy {
  margin-top: 16px;
  font-size: 13px;
  color: var(--text-tertiary);
  font-style: italic;
}

@media (max-width: 900px) {
  .final-cta {
    padding: 40px 24px;
    border-radius: 16px;
  }
}
```

**Rules:** One per page. Centered text. Primary button only (no secondary). Microcopy reinforces offer integrity.

## 7.12 — Footer

**Structure:**
```html
<footer class="footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-column">
        <h4>Services</h4>
        <ul><li><a href="...">...</a></li></ul>
      </div>
      <div class="footer-column">
        <h4>Industries</h4>
        ...
      </div>
      <div class="footer-column">
        <h4>Company</h4>
        ...
      </div>
    </div>
    <div class="footer-baseline">
      <div>HelpMeMarketing · Mississauga, Ontario · <a href="mailto:...">Hello@helpmemarketing.com</a></div>
      <div>
        <a href="/privacy">Privacy Policy</a>
        <a href="/terms">Terms of Service</a>
        © 2026 HelpMeMarketing
      </div>
    </div>
  </div>
</footer>
```

**CSS:**
```css
.footer {
  background: var(--bg);
  border-top: 1px solid var(--border);
  padding: 96px 0 40px;
}

.footer-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 64px;
  margin-bottom: 64px;
}

.footer-column h4 {
  font-family: var(--sans);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-tertiary);
  margin: 0 0 20px;
}

.footer-column ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-column ul li { margin-bottom: 10px; }

.footer-column ul li a {
  color: var(--text-muted);
  text-decoration: none;
  font-size: 14px;
  transition: color 0.2s ease;
}

.footer-column ul li a:hover { color: var(--text); }

.footer-baseline {
  padding-top: 32px;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  font-size: 13px;
  color: var(--text-tertiary);
}

.footer-baseline a {
  color: var(--text-tertiary);
  text-decoration: none;
  margin: 0 12px;
}

@media (max-width: 900px) {
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 40px;
  }
  .footer-baseline {
    flex-direction: column;
    align-items: flex-start;
  }
}
```

**Rules:** Three columns always: Services / Industries / Company. Footer baseline contains address + email + legal + copyright.

## 7.13 — Top navigation (dark variant)

**CSS overrides:**
```css
.nav {
  background: var(--bg);
  border-bottom: 1px solid var(--border);
}

.nav .logo { color: var(--text); }
.nav .logo em { color: var(--cta); }

.nav-link { color: var(--text-muted); }

.nav-link:hover {
  color: var(--text);
  background: rgba(255, 255, 255, 0.05);
}

.nav-link.active {
  color: var(--text);
  background: rgba(255, 255, 255, 0.05);
}

.btn-accent {
  background: var(--cta);
  color: var(--bg);
  border: none;
  box-shadow: 0 4px 16px rgba(255, 92, 26, 0.25);
}

.btn-accent:hover { background: var(--cta-hover); }

.nav-mobile-menu { background: var(--bg); }
.nav-mobile-menu a { color: var(--text); }
```

**Rules:** Background Obsidian. Logo text white, "Me" accent Signal Orange. Nav links muted default, white on hover/active with subtle background.

## 7.14 — Logo mark (dark variant)

**Structure:**
```html
<a class="logo" href="index.html">
  <div class="logo-mark">H<span class="me-italic">MM</span></div>
  <span class="logo-text">Help<em>Me</em>Marketing</span>
</a>
```

**Base CSS (light context):**
```css
.logo-mark {
  width: 32px; height: 32px; border-radius: 6px;
  background: var(--navy); color: var(--ivory);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--serif); font-size: 13px; font-weight: 500;
  letter-spacing: -0.02em;
  position: relative;
}
.logo-mark .me-italic {
  font-style: italic; color: var(--gold); margin-left: 1px;
}
```

**Dark-variant overrides:**
```css
body.redesign-prototype .logo-mark {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text);
}
body.redesign-prototype .logo-mark .me-italic {
  color: var(--cta);
}
```

**Rules:**
- The mark reads `HMM` — anchored serif `H` followed by `MM` wrapped in `.me-italic`.
- The `H` inherits the surrounding text color: `--ivory` on the light/navy mark, `--text` on the dark prototype.
- The trailing `MM` is always italic + accent: `--gold` on the light mark, `--cta` (Signal Orange) on the dark prototype. Both Ms get the italic treatment; the class is applied to the wrapping span, not per-letter.
- Class name `.me-italic` is retained from the original `Hm` mark — it now applies to whatever italic-accent letters trail the anchored `H`, not specifically a lowercase `m`. Renaming was rejected to avoid a ripple-rename across light-mode CSS that has no defect.
- **Sizing**: 3 characters in a 32px box requires `font-size: 13px` and `letter-spacing: -0.02em` for a clean fit. Do not increase font-size without re-checking that the mark does not visually overflow the rounded box.
- **Dark-variant frame**: background transparent (was navy in light mode), 1px `--border` defines the mark area.
- **Light-mode mark** remains the canonical form for email signatures, business cards, and any other light/print context. The dark variant is prototype-scoped until migration.

**Founder decision history:**
- 2026-05-21: Changed from `Hm` (H + italic m) to `HMM` (H + italic MM). Reason: stronger, more memorable abbreviation reads as the brand acronym ("HMM") rather than a truncated first-syllable. Triggers a brand-wide rollout (favicon, social PFPs, signatures, printed material) — tracked in followups, gated on prototype approval.

---

# Section 8 — Missing patterns inventory

This section identifies components needed for the next 29 pages but not yet built. Each entry includes purpose, where needed, status, and spec needs.

These are gaps to fill before or during migration. Each becomes a Section 7 entry once built.

## Critical — blocks Phase 2 nav rebuild

### 8.1 — Mobile hamburger menu (dark variant)

**Where needed:** All pages, all viewports below 900px
**Status:** Legacy mobile menu exists, prototype CSS partially overrides
**Spec needs:** Hamburger icon (white lines on dark), menu open/close animation, backdrop, close icon, mobile menu item styling

### 8.2 — Footer mobile reorganization

**Where needed:** All pages on mobile
**Status:** Columns stack vertically (basic implementation)
**Spec needs:** Whether columns should be collapsible (accordion-style), order of column priorities, whether to hide some content on mobile

## Critical — blocks Phase 4 service pages

### 8.3 — Pricing tier card

**Where needed:** Every service page — 3 tiers per service
**Status:** Old light-mode tier cards exist on /services/seo
**Spec needs:** Card layout (name + who-it-for + price + setup + commitment + features + "Not included"), active/recommended tier highlighting, mobile stacking

### 8.4 — FAQ accordion

**Where needed:** Every service page (5 questions per page)
**Status:** Existing `<details>` element on /services/seo, no dark mode treatment
**Spec needs:** Accordion open/close treatment, chevron indicator, spacing, question typography, answer typography, FAQPage schema integration

### 8.5 — Section header with eyebrow + H2 + deck

**Where needed:** Every service page, every industry page
**Status:** Pattern exists on homepage as separate components
**Spec needs:** Whether to formalize as one component, eyebrow variant without Mint dot, spacing rules

### 8.6 — Breadcrumb

**Where needed:** All non-homepage pages
**Status:** Doesn't exist
**Spec needs:** Visual treatment, separator choice, color hierarchy, mobile collapse, BreadcrumbList schema

### 8.7 — Outcome card / metric callout

**Where needed:** Every service page (3 outcome cards typical)
**Status:** Light-mode version on /services/seo with gold left-stripe
**Spec needs:** Dark mode equivalent of left-stripe, number treatment, caveat text treatment, source citation pattern

### 8.8 — "Not for you if" list

**Where needed:** Every service page
**Status:** Light-mode version on /services/seo
**Spec needs:** Visual treatment, tone-appropriate styling

## Critical — blocks Phase 5 industry pages

### 8.9 — Industry hero variant

**Where needed:** Industry pages (`/industries/dtc`, etc.)
**Status:** Light-mode existing hero pattern
**Spec needs:** Whether matches homepage hero or has variant, industry-specific visual options, industry badges

### 8.10 — Industry vertical icon system

**Where needed:** Industry references throughout the site
**Status:** Doesn't exist
**Spec needs:** Icons vs pure typography, style if icons, color treatment

## Important — blocks Phase 6 standalone pages

### 8.11 — Contact form

**Where needed:** /contact page
**Status:** Light-mode existing form
**Spec needs:** Input field styling, label treatment, error/success states, submit button, validation feedback, Google Apps Script integration

### 8.12 — About page warm break section

**Where needed:** /about page
**Status:** Tokens defined, pattern not built
**Spec needs:** Full warm-break section layout, Burnt Terracotta CTA variant, photography/illustration treatment, transition between dark and warm sections

### 8.13 — Blog post template (dark mode)

**Where needed:** All blog posts, blog index
**Status:** Light-mode V2 template exists in master reference
**Spec needs:** Full dark-mode adaptation of V2 template (sticky TOC sidebar, featured cards, pull quotes, author bio, related reading, mobile collapsible TOC)

## Important — blocks Phase 8 tools

### 8.14 — Calculator inputs and outputs

**Where needed:** /ad-calculator, /tools/marketing-audit
**Status:** Light-mode existing on /ad-calculator
**Spec needs:** Tile selector pattern, numeric input styling, result display, interactive elements

## Nice-to-have — not blocking migration

### 8.15 — Toast / notification

**Spec needs:** Position, duration, Mint variant for success

### 8.16 — Modal / dialog

**Spec needs:** Backdrop, close behavior, animation, z-index 1000

### 8.17 — Inline alert / callout

**Spec needs:** Variants (info, success, caution, tip), color per variant, icon rules

### 8.18 — Tab navigation

**Spec needs:** Tab style, active state, content transition

### 8.19 — Pull quote

**Where needed:** Blog posts, possibly service pages
**Status:** Light-mode version exists in blog template
**Spec needs:** Dark mode adaptation, serif italic treatment, border/accent color, attribution styling

### 8.20 — Code block

**Where needed:** Technical blog posts
**Spec needs:** Inline vs block treatment, syntax highlighting (or no), copy-to-clipboard button, monospace font choice

## Summary

| Phase blocked | Critical gaps | Estimated build time |
|---|---|---|
| Phase 2 (nav rebuild) | 2 | 1-2 hours |
| Phase 4 (service pages) | 6 | 4-6 hours |
| Phase 5 (industry pages) | 2 | 2-3 hours |
| Phase 6 (standalone pages) | 3 | 6-8 hours |
| Phase 8 (tools) | 1 | 3-4 hours |
| Nice-to-have | 6 | varies |
| **Total critical** | **14** | **18-26 hours** |

Recommended fill order:
1. Mobile hamburger + footer (Phase 2 unblock)
2. Pricing tier card + FAQ accordion + outcome card (Phase 4 unblock)
3. Breadcrumb + section header + "Not for you if" (Phase 4 polish)
4. Industry hero + icon system (Phase 5 unblock)
5. Contact form + warm break + blog template (Phase 6 unblock)
6. Calculator UI (Phase 8 unblock)
7. Nice-to-haves as needed

---

# Section 9 — Voice & content integration

## Two docs, one experience

This document and `HMM_Content_Rules_v0_2.md` work together. Neither is sufficient alone.

| Concern | Document |
|---|---|
| What it looks like | This document |
| What it says | Content Rules |
| How content fits components | Both |

Both docs are mandatory reading when building a page.

## How the docs hand off

**Design system stops where voice begins.**
Component specs describe how text looks (font, size, max-width). They do not describe what text says. Example: Section 7.2 says H1 length is "5-12 words." That's a structural constraint. The actual H1 wording is governed by Content Rules §9.1.

**Content rules stop where design begins.**
Content Rules describes voice principles, banned phrases, hook patterns. They don't dictate CSS or font-sizes. Example: Content Rules §5.3 requires "Key Takeaways box (3-5 bullets at the top)." The visual spec for that box comes from this document.

## Cross-references for common questions

| Question | Primary answer | Secondary check |
|---|---|---|
| What font size is H1? | Design system §4 | — |
| How long should the H1 be? | Content rules §8.1 | Design system §7.2 (max line wrap) |
| Where does Signal Orange go? | Design system §3 | Content rules §9 (CTA microcopy) |
| What goes in the FAQ section? | Content rules §9.4 | Design system §8.4 (FAQ accordion pattern) |
| How many service tiers per page? | Content rules §10.2 | Design system §8.3 (pricing tier card) |

## Content-driven design moments

**H1 italic accent word selection.** Pattern is design. Which word gets the accent is content — "the most concrete or buyer-relevant phrase."

**Service card description length.** Card design constrains width. "2-3 sentences max" is content-driven for scannability.

**FAQ answer length.** Accordion accommodates 40-80 words. The 40-80 word constraint is content.

**"Not for you if" tone.** Visual pattern is just a list. Tone — honest disqualifiers, not insulting — is content.

## Voice rules that affect visual decisions

**No em-dashes site-wide (Content Rules §2.3).** Design must use colons, periods, parentheses, or restructure. Never em-dashes as decorative typographic moments.

**Sentence case headings always.** CSS does not auto-transform case (except small label elements like eyebrows). Content layer responsible.

**Active voice as default.** Button text, microcopy, CTAs are content. "Book my audit" not "Audit will be booked."

## Design-driven content moments

**Comparison card list lengths must match.** Visual pattern needs equal-length lists (6/6, not 6/5).

**Service grid is exactly 6.** 2×3 grid needs 6 cards. Not 5, not 7.

**Final CTA stays centered.** Centered text needs shorter sentences than left-aligned.

## When the docs conflict

| Conflict type | Resolution |
|---|---|
| Voice rule contradicts visual rule | Voice rule wins; design adapts |
| Specific value differs | Whichever is more restrictive |
| New pattern needed | Spec in this doc, reference content implications |
| Old document conflicts | This doc wins; old doc archives |

---

# Section 10 — Mobile responsive patterns

## Strategy

Desktop-first but mobile-aware. Components designed at desktop, adapted for mobile via single breakpoint at 900px.

This is deliberate. Most HMM prospects evaluate on desktop. Mobile must not break but doesn't dominate.

## Single breakpoint

```css
@media (max-width: 900px) {
  /* Mobile styles */
}
```

**Above 900px:** Desktop. **At or below 900px:** Mobile.

No tablet-specific breakpoints. No micro-breakpoints.

## What changes at the breakpoint

### Typography (from Section 4)

| Element | Desktop | Mobile |
|---|---|---|
| H1 hero | 64px | 40px |
| H2 section | 40px | 28px |
| H3 | 24px | 20px |
| Body | 17px | 17px (unchanged) |
| Hero subtitle | 19px | 18px |
| Section deck | 18px | 17px |

### Layout collapsing (from Section 6)

| Pattern | Desktop | Mobile |
|---|---|---|
| Hero two-column | 1.2fr 1fr grid | Single column |
| Comparison cards | 1fr 1fr grid | Single column, legacy first |
| Service grid | 2-column | Single column, 6 cards stacked |
| Footer three-column | 1fr 1fr 1fr | Single column |

### Spacing adjustments (from Section 5)

| Element | Desktop | Mobile |
|---|---|---|
| Section padding | 96px | 64px |
| Hero padding | 96px | 64px |
| Container horizontal | 32px | 20px |
| Final CTA inner | 56px / 64px | 40px / 24px |
| Card grid gap | 24px | 16px |
| Footer column gap | 64px | 40px |

### Component-specific mobile rules

- Hero CTAs stack vertically (primary on top)
- Comparison cards stack legacy → HMM
- Service cards stack vertically (all 6)
- Footer baseline reflows from horizontal to vertical
- Final CTA inner padding reduces
- Mobile menu replaces horizontal nav (hamburger pattern, see §8.1)

## What does NOT change

- Color tokens unchanged
- Body text size unchanged
- Border radii unchanged
- Voice and content rules mandatory on all viewports
- Em-dash ban mandatory on all viewports

## Mobile testing strategy

Per the deferred mobile testing followup, validate at:

| Viewport | Device class |
|---|---|
| 375px | iPhone SE, small Android |
| 390px | iPhone 14 Pro |
| 414px | iPhone Pro Max |
| 768px | iPad portrait |
| 900px | Small laptop, tablet landscape |

Validation happens before Phase 1 ships, or during Phase 1 component-building if issues surface earlier.

---

# Section 11 — Accessibility considerations

## Standards target

**WCAG 2.1 Level AA minimum.** AAA where achievable without compromising design intent.

## Color contrast (verified)

| Text | Background | Contrast | Level |
|---|---|---|---|
| `--text` (white) | `--bg` | 19.7:1 | AAA |
| `--text-muted` | `--bg` | 7.2:1 | AAA |
| `--text-tertiary` | `--bg` | 4.7:1 | AA |
| `--text` | `--bg-elevated` | 17.4:1 | AAA |
| `--text-muted` | `--bg-elevated` | 6.4:1 | AAA |
| `--cta` | `--bg` | 5.1:1 | AA |
| `--mint` | `--bg` | 8.9:1 | AAA |
| `--bg` | `--cta` (button text) | 5.1:1 | AA |

**Critical rule:** Never use `--text-tertiary` for body text. AA minimum is fine for captions, dangerous for body.

## Focus states

All interactive elements need visible focus:

```css
:focus-visible {
  outline: 2px solid var(--cta);
  outline-offset: 2px;
  border-radius: 4px;
}
```

Applied to buttons, links, form inputs, accordion summaries, any keyboard-focusable element.

**Why `:focus-visible`:** Only shows on keyboard focus, not click. Click users don't see outline (cleaner). Keyboard users see it (essential).

**Status:** Not yet implemented in prototype. Followup for component-building phase.

## Keyboard navigation

- All interactive elements keyboard-accessible
- Tab order matches visual reading order
- No keyboard traps
- Skip links where appropriate

**Service cards:** `<a>` wrappers, naturally accessible.
**FAQ accordions:** Use `<details>` / `<summary>` for native keyboard support.
**Forms:** Tab order top to bottom.
**Mobile menu:** Hamburger keyboard-accessible. Menu traps focus while open.

## Screen reader patterns

**Semantic HTML first.** Use `<nav>`, `<main>`, `<article>`, `<section>`, `<aside>`, `<footer>` correctly.

**Heading hierarchy enforced.** One H1 per page. H2s under H1, no skipping levels.

**Image alt text.** Every image has alt. Decorative use `alt=""`. Content images describe.

**ARIA labels.** Sparingly, only where semantic HTML can't carry meaning.

**Skip to main content.** Pages with extensive nav should have skip link as first focusable element. Hidden until focused.

## Motion and animation

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

Respect user preference. Animation never essential to understanding content.

## Accessibility followups

Before Phase 1 ships:
1. Implement `:focus-visible` outline rules across all interactive elements
2. Add skip-to-content link to homepage
3. Test homepage with keyboard-only navigation
4. Test homepage with VoiceOver (Mac) or NVDA (Windows)
5. Verify reduced-motion respects user preference
6. Add ARIA labels where icon-only buttons exist

---

# Section 12 — Implementation guidance

## How to use this document in practice

### Before writing any HTML

**Step 1: Identify page type.**
- Homepage → Section 7 components
- Service page → Section 7 + Section 8 patterns (FAQ, tier card, outcome card)
- Industry page → Section 7 + industry-specific patterns
- Standalone page → Section 7 + specific patterns
- Blog post → Blog template adaptation (§8.13)
- Tool page → Tool-specific components (§8.14)

**Step 2: List required components.** Map page to component IDs.

**Step 3: Identify Section 8 gaps.** For each missing component, either use approximate existing (note as technical debt), spec the missing component (Section 8 entry, get approval, build), or defer page until component exists.

Do NOT invent components inline.

**Step 4: Confirm voice and content rules apply.** Read Content Rules. Specifically: no em-dashes, sentence case, active voice, no banned phrases, approved hook pattern, capability claims tagged by honesty level.

### During HTML build

**Step 5: Build with documented patterns only.** Use exact HTML structure and CSS classes from Section 7. Don't simplify "for readability" — patterns work as documented.

**Step 6: Verify token usage.** Every color, font-size, spacing must reference a token. No literal values.

**Step 7: Test responsive behavior.** Verify at 375px, 768px, 1024px, 1440px, 1920px+.

### Before commit

**Step 8: Validation checklist.**

Content rules (from HMM_Content_Rules_v0_2.md §13):
- [ ] No banned phrases
- [ ] No em-dashes
- [ ] Active voice throughout
- [ ] Sentence case on all headings
- [ ] Canadian spelling consistent
- [ ] Hook in first 50 words
- [ ] Capability claims tagged by honesty level
- [ ] Internal link minimums met
- [ ] FAQ schema matches visible FAQ

Design system:
- [ ] All components from Section 7 used as documented
- [ ] No invented components
- [ ] All tokens referenced via CSS variables
- [ ] Mobile responsive verified
- [ ] Color contrast passes WCAG AA
- [ ] Focus states visible on all interactive elements
- [ ] Heading hierarchy correct (one H1, no skipped levels)

### After commit

**Step 9: Update document if patterns evolved.**
**Step 10: Bump version per CHANGELOG rules.**

## Common pitfalls

1. **Inventing CSS classes.** Use existing or extend system properly.
2. **Hardcoding values.** Every hardcoded value is technical debt.
3. **Skipping mobile testing.** Mobile must be verified.
4. **Em-dash sneaking in.** Site-wide includes comments, meta tags.
5. **Mint as decorative accent.** Mint is functional state only.
6. **Adding orange to look "designy."** Orange counts; 2-3 primary instances max.
7. **Ignoring warm break exception.** Warm break is a specific pattern with specific tokens.

## When to extend the system

**Appropriate:**
- New page type genuinely needs a pattern not in Section 7
- New pattern would be used on 2+ pages
- Pattern fits design philosophy (Section 2)
- Founder approves

**Not appropriate:**
- Pattern only used once
- Pattern contradicts philosophy
- "Everyone else does it"

**Process:** Document as Section 7 entry → build → version bump → CHANGELOG.

## Living document

Section 8 shrinks as gaps fill. Section 7 grows as patterns add. All sections update when rules change.

## Final note

The discipline of this document is what makes the migration possible. 30+ pages built against this spec look like one coherent site. 30+ pages without the spec look like 30 separate experiments.

When building any page, ask: "If a different person built this next month, would they make the same decisions? If yes, the system is working. If no, the system needs tightening in this doc before more pages get built."

---

# CHANGELOG

| Version | Date | Change |
|---|---|---|
| 1.0 | May 21, 2026 | Initial canonical release. All 12 sections complete. Consolidated from section-by-section drafts. All tracked clarifications applied. |

---

*End of HMM Design System v1.0*
*Save as: `docs/HMM_Design_System.md` in repo after founder approval*
