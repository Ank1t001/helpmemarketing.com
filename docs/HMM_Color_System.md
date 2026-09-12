# HMM Color System

> **The Quiet Disruptor — palette, rules, locked decisions**

**Status:** Canonical reference, current as of repository commit `27eb63b`.
**Source:** `HMM-Color-System.docx` v1 (May 2026), reconciled with homepage audit findings.
**Companion docs:** `/docs/HMM_Design_System.md` (design canon), `/docs/HMM_Content_Rules.md` (voice canon).
**Use:** Mandatory reference for all color decisions on `body.redesign-prototype`-scoped work.

---

## 1. Core Palette

| Color | Hex | Role | Notes |
|---|---|---|---|
| Obsidian | `#0E0E0E` | Primary background | Near-black with warmth. Pure black `#000000` feels harsh. Reads as "expensive matte finish" not "cheap OLED." Used for site background, hero, footer. |
| Carbon | `#1A1A1A` | Elevated surface | One shade lighter than Obsidian. Cards, modals, scrolled nav. Six-point lightness creates hierarchy without borders. Linear / GitHub / Vercel use similar. |
| Pure White | `#FFFFFF` | Primary text | Full white on dark — not off-white. Counterintuitive but pure white creates the crispness that separates premium dark sites from muddy ones. |
| Graphite | `#999999` | Muted text | Secondary text, captions, default nav links, metadata. ~60% perceived luminance against Obsidian. Creates hierarchy. |
| Slate | `#8A8A8A` | Tertiary / disabled | Placeholder text, disabled buttons, deep metadata, decorative labels. Thin dividers. **Lifted from `#737373` to `#8A8A8A` on 2026-08-13** for WCAG AA (~4.9:1 on Obsidian; `#737373` was ~3.9:1, below the 4.5:1 small-text floor). See Decision 11. |

---

## 2. Accent Colors

| Color | Hex | Role | Notes |
|---|---|---|---|
| Signal Orange | `#FF5C1A` | Primary CTA | Calibrated to peak foveal sensitivity (580-600nm). Impossible to ignore on dark. Reserved for primary CTAs + approved brand-identity accents (see Decision 1 in Section 9). |
| Ember | `#FF7038` | CTA hover state | Signal Orange lightened ~8%. Paired with 2px upward translate + soft orange shadow. |
| Mint | `#00D4AA` | Success / live state | Functional counterpoint to orange. Success states, live indicators, checkmarks, positive metric callouts. Reads as fintech-modern (Stripe, Mercury, Ramp). Never used as a CTA. |

---

## 3. Structural Colors

| Color | Value | Role | Notes |
|---|---|---|---|
| Whisper Border | `rgba(255,255,255,0.08)` | Card borders, dividers, secondary button outlines | The most important "invisible" color — separates polished dark from flat dark. |
| Grid Lines | `rgba(255,255,255,0.045)` | Hero background grid (56px squares) | **Shipped value 0.045**, up from docx's 0.025 per Decision 4. Tuned in implementation. |
| Orange Glow | `rgba(255,92,26,0.18)` | Soft radial gradient behind hero ambient | **Shipped value 0.18**, up from docx's 0.12 per Decision 4. |

---

## 4. The 60-30-10 Distribution

| % | Role | Colors |
|---|---|---|
| 60% | Background & space | Obsidian, Carbon |
| 30% | Text & content | Pure White, Graphite, Slate |
| 10% | Accent & action | Signal Orange (~80% of accent area), Mint (functional states only) |

---

## 5. Warm Break Exception (Reserved)

Dark sites can feel cold. The solution: one warm-toned section (typically About or Process) with an inverted micro-palette. Per Decision 6, these tokens are **defined but reserved** for future implementation:

| Color | Hex | Role |
|---|---|---|
| Warm Ivory | `#F8F4ED` | Break background |
| Carbon | `#1A1A1A` | Break text (reused from elevated surface) |
| Burnt Terracotta | `#C8542B` | Break accent — sibling of Signal Orange but more grounded |

---

## 6. CSS Variables (Current Implementation)

Defined in `styles.css` `:root`. Variable names are intentionally semantic (`--cta`, `--bg-elevated`) rather than literal (`--orange`, `--gray-1`) so swapping a color later does not require touching every component.

```css
:root {
  /* Core surfaces */
  --bg: #0E0E0E;
  --bg-elevated: #1A1A1A;

  /* Text hierarchy */
  --text: #FFFFFF;
  --text-muted: #999999;
  --text-tertiary: #8A8A8A;  /* AA-lifted from #737373 — see Decision 11 */
  --text-body: rgba(255, 255, 255, 0.78);  /* body.blog-dark only — see Decision 13 */

  /* Accents */
  --cta: #FF5C1A;
  --cta-hover: #FF7038;
  --mint: #00D4AA;

  /* Structural */
  --border: rgba(255, 255, 255, 0.08);
  --grid-line: rgba(255, 255, 255, 0.045);
  --orange-glow: rgba(255, 92, 26, 0.18);

  /* Warm-break section (reserved) */
  --warm-bg: #F8F4ED;
  --warm-text: #1A1A1A;
  --warm-cta: #C8542B;
}
```

---

## 7. Reserved Tokens (Decision 9 — Future Implementation)

Documented as reserved. **NOT yet implemented** in `styles.css`. Will be added in a separate commit before any major component refactor.

```css
/* Reserved — add before next major refactor */
--surface-subtle: rgba(255, 255, 255, 0.02);  /* wash hovers */
--surface-hover: rgba(255, 255, 255, 0.05);   /* nav/button hovers */
--border-strong: rgba(255, 255, 255, 0.16);   /* card hover borders */
--cta-glow-soft: rgba(255, 92, 26, 0.15);     /* focus glow */
--cta-glow-strong: rgba(255, 92, 26, 0.35);   /* button hover shadow */
```

---

## 8. Golden Rules (Post-Reconciliation)

### Rule 1 — Signal Orange on CTAs (REFRAMED per Decision 1)

The docx's original "max 2 non-CTA usages per page" cap was too strict for actual brand language. Reframed:

**ALWAYS used on:**
- Primary CTA buttons (background, hover state, glow shadow)
- Click affordances inside actionable cards (e.g., card arrows where the whole card is the CTA)

**ACCEPTABLE brand-identity accents** (not subject to a cap):
- Logo mark italic ("MM")
- Wordmark italic ("Me")
- H1 italic accent words (e.g., "100 customers", "growth")
- Hero ambient glow (`.hero::before`)
- Brand-comparison emphasis (HMM card border + title)

**NEVER used on:**
- Body text
- Regular structural borders (use `rgba` per Rule 4)
- Non-CTA backgrounds
- Decorative elements without brand-identity purpose

### Rule 2 — Never use Mint as a CTA

Mint is a functional color (success, live, checkmark). Using it as a button color sends mixed signals about whether something is actionable or already completed. The eyebrow mint dot is acceptable as a live-indicator decoration.

### Rule 3 — Pure white text only on dark backgrounds

Off-white reads as muddy. `#FFFFFF` is what separates premium dark sites from amateur ones. The Graphite (`#999999`) and Slate (`#737373`) tiers are intentional secondary-tier greys, not "off-white" — they're explicit hierarchy colors.

### Rule 4 — Borders use rgba, except state indicators (AMENDED per Decision 3)

Structural borders use rgba (cards, dividers, containers): `var(--border)` = `rgba(255,255,255,0.08)`.

State indicators may use solid token colors:
- `:focus` → solid `var(--cta)` for accessibility/visibility
- `:error` → may use solid error tokens
- `:active` → may use solid token if state-communication needs it

### Rule 5 — Warm-break section uses Burnt Terracotta

Same color family as Signal Orange, different energy. Per Decision 6, tokens defined but no current usage. Reserved for future About or Process page warm-break section.

### Rule 6 — Subtle grid or glow on every dark hero

Per Decision 4, **shipped opacities are canonical** (grid 0.045, glow 0.18). The docx's 0.025 / 0.12 were pre-implementation values; the shipped values were tuned in implementation against the actual hero composition.

---

## 9. Locked Decisions (Audit Reconciliation)

These 10 decisions were founder-locked after the homepage design system audit (against commit `ce577a6`). They modify or extend the original docx specifications to match shipped reality.

### Decision 1 — Signal Orange application REFRAMED

The docx's "max 2 non-CTA usages per page" cap was too strict. Replaced with the categorized rules in Section 8 Rule 1 above. Brand-identity accents (logo, wordmark, H1 italic, hero glow, brand-comparison emphasis) are acceptable without a cap. Forbidden uses (body text, structural borders, non-CTA backgrounds, decorative non-brand elements) remain forbidden.

### Decision 2 — Service-card arrow counts as CTA affordance

When the entire card is a clickable CTA (e.g., service-grid cards linking to service pages), the inline arrow is a CTA affordance, not a separate non-CTA Signal Orange usage.

### Decision 3 — Focus-state borders may use solid var(--cta)

Rule 4's "borders use rgba" applies to structural borders. State indicators (`:focus`, `:error`, `:active`) may use solid token colors for accessibility and visibility. Codified in Section 8 Rule 4.

### Decision 4 — Opacity values: shipped reality is canonical

- `--grid-line: rgba(255,255,255,0.045)` (docx had 0.025)
- `--orange-glow: rgba(255,92,26,0.18)` (docx had 0.12)

These were tuned during implementation against the actual hero composition. The shipped values are now canonical; docx values are superseded.

### Decision 5 — Two breakpoints codified

- `900px` primary (major layout flip): typography mobile sizes, container padding, section padding, all grid stacks, hero CTA stack, nav-main-cta hide
- `720px` secondary (component-level adjustments): `.footer-baseline` stacks vertically

Other historical breakpoints in legacy CSS (`1200`, `1100`, `1000`, `960`, `680`, `640`, `560`, `520`) are not used in `body.redesign-prototype` scope.

### Decision 6 — Warm-break tokens reserved

Three tokens defined in `:root` for future warm-break section. No current usage. Do not use these tokens until a warm-break section is designed and shipped.

### Decision 7 — `.bullet-list` reserved

Class defined in prototype CSS but unused on homepage. Status: reserved. Verify usage on other pages during their migration; remove if unused sitewide after Phase 2.

### Decision 8 — `.service-card h3` mobile font-size override

Currently stays at 24px on mobile (no mobile override matches). Known issue. Fix is to add a 20px override at `@media (max-width: 900px)` in a small separate follow-up commit. Not blocking.

### Decision 9 — Tier-system tokens reserved (not implemented)

Five tokens documented in Section 7 but not yet added to `styles.css`. Will be added in a separate commit before any major component refactor. Document them here so future component patterns can be designed against these tokens.

### Decision 10 — This file's existence

Markdown version of the Color System docx, committed to the repo so Claude Code can read it on every session. The docx remains the prepared-by-Claude source in the Claude.ai project; this markdown is the canonical machine-readable version.

### Decision 12 — Positive-result figures use Mint, sitewide (locked 2026-08-13)

Mint's "positive metric callout" role (Section 2) is now **enforced across all results-bearing prototype pages**, not just the tool pages. Any figure that communicates a positive outcome — case-study result numbers, proof-strip figures, metric deltas, metric sparklines, proof stats — is rendered in `var(--mint)`. This replaced three inconsistent prior treatments: legacy emerald `#10B981` (industry metric deltas), off-canon blue `#2563EB` (industry sparklines), and Signal Orange (`work.html` case + proof figures, which read as CTAs when they are actually outcomes).

Rules that keep this canon-safe:
- **Figures only, not their labels.** The result number is Mint; its qualifier/label stays `var(--text-muted)`. The big neutral number in a `.metric-value` stays white — the *delta* is the Mint slot.
- **Mint never becomes a CTA** (Rule 2 still holds). Every button, nav, and primary action stays Signal Orange. Orange remains the ~80%-of-accent primary; Mint is the functional-result counterpoint.
- **Purely decorative or content-only pages** (privacy, terms, about) legitimately stay single-accent — there is no positive metric to color.

Components affected: `.case-study-metric` / `.proof-strip-figure` (work), `.pm-proof-stat` (performance-marketing), `.metric-delta` + `.metric-sparkline` (industry pages, scoped under `[data-screen-label="industry"]`). Sparkline SVGs were converted from a hardcoded hex to `var(--mint)` (SVG presentation attributes accept `var()`), removing an off-canon literal.

**Sparkline fill implementation (updated 2026-09-01):** industry-page `.metric-sparkline` area fills now use a flat `fill="var(--mint)" fill-opacity="0.12"` on the closed area path, not an inline `<defs><linearGradient>` gradient. The gradient produced a "closing tag / open tag do not match" parse error in DataForSEO's (non-SVG-aware) on-page crawler at every `</linearGradient>` — valid HTML5 foreign content that browsers and Google parse fine, but it suppressed a clean crawl. The flat mint fill is visually near-identical at 60px sparkline height, removes the flagged construct, and keeps the Mint token. Applied to all four industry pages (finance, healthcare, dtc, saas). The stroke line above the fill is unchanged (`stroke="var(--mint)"`).

### Decision 11 — Tertiary token AA lift (`#737373` → `#8A8A8A`), locked 2026-08-13

`--text-tertiary` was raised from `#737373` (Slate, ~3.9:1 on Obsidian) to `#8A8A8A` (~4.9:1) to clear the WCAG AA 4.5:1 floor for small tertiary text. The change was first proven as a per-tool override on `/ad-set-calculator`, then promoted to the global `body.redesign-prototype` token so every dark page benefits and the page-level override could be removed. The blog token (`body.blog-dark`) is a separate scope and was **not** changed at the time (lifted 2026-09-09, see below). "Slate" remains the color's name; only its shipped value moved.

**Amendment, 2026-09-09 (Index pages).** The HMM Index pages (`/instagram-reindex`, `/hair-loss-index`) do not use `body.redesign-prototype`. Each carries its own page-scoped `:root` token block, so the global lift never reached them: `/instagram-reindex` shipped `#737373` in its token block and in three hardcoded `fill="#737373"` SVG chart labels at 10 to 10.5px, exactly the small-text case this floor exists for. All four are now `#8A8A8A`, and `/hair-loss-index` shipped lifted. **Rule:** any new Index instance must define `--text-tertiary: #8A8A8A` in its own token block, and SVG text inside an Index page must use the token or the lifted value, never `#737373`. Decision 11 governs the Index scope explicitly even though the rest of the prototype canon does not.

**Amendment, 2026-09-09 (blog scope).** `body.blog-dark` in `styles.css` was the last scope still shipping `#737373`; Decision 11 had deliberately excluded it in August 2026. Founder call on 9 Sep 2026: lift it. The blog token is now `#8A8A8A`, so every dark scope on the site (prototype, blog, Index pages) shares one tertiary value. No blog page hardcodes the old hex. Decision 11 now applies sitewide with no exclusions; "Slate" keeps its name and `#737373` is retired everywhere except the legacy light-mode region, which never used it.


### Decision 13 — Long-form body-copy token `--text-body` (blog scope), locked 2026-09-09

Blog paragraphs shipped in `--text-muted` (`#999999`, ~6.3:1) while FAQ answers and some closing paragraphs were pure white, so a 3,000-word post flipped tone mid-read. Rule 3 makes pure white the body colour on prototype pages, but at 17px over thousands of words it is harsh on Obsidian. Founder call on 9 Sep 2026: a third text step, **`--text-body: rgba(255, 255, 255, 0.78)`** (renders ~`#C7C7C7`, ~11:1 on Obsidian), defined on `body.blog-dark` only. It is the colour of every paragraph, list item, lever description, FAQ answer and featured-card paragraph inside a post. `--text` stays for headings, strong text and UI; `--text-muted` stays for subtitles, captions, meta lines and card body copy; `--text-tertiary` stays for the smallest labels. The token is not defined in `body.redesign-prototype`; prototype pages keep Rule 3 as written. The pull quote tint on blogs is `rgba(255, 92, 26, 0.08)`, a new opacity step below `--orange-glow` (18%), recorded here under Decision 4.

---

## 10. Forbidden Patterns

### In CSS (under `body.redesign-prototype` scope)
- Legacy color tokens: `--gold`, `--navy`, `--cream`, `--ivory`, `--deep`, `--ink-*`, `--line`, `--primary`, `--mint-soft`, `--white`
- Hardcoded hex values as property values (existing definitions are tokens only)
- Solid borders on structural elements (use rgba; solid acceptable only for state indicators per Decision 3)

### In HTML
- Inline `style="color:..."` on prototype elements
- `<span style="color:var(--gold)">` patterns for italic accents — use `<em>` or `<span class="me-italic">` per `/docs/HMM_Design_System.md` Section 4
- Footer logo with inline style overrides
- Any markup that relies on legacy tokens being inherited

---

## 11. Updating This Doc

When the color system evolves:
1. Update `styles.css` first
2. Update this doc to match shipped reality in the same commit
3. Bump the "Status" line at the top with the new commit reference
4. If a Golden Rule changes, update both Section 8 (Rules) AND Section 9 (Decisions) — the Decisions section is the audit trail

This doc is **descriptive of shipped reality**, not aspirational. Aspirational color experiments should live in `/docs/proposals/` first, then become canon after they ship.

---

*HMM Color System v1.0 — first markdown commit*
*Source: HMM-Color-System.docx (May 2026)*
*Reconciled: Homepage design audit, locked 10 decisions, founder-approved*

### Decision 14 — CTA colour by destination (founder decision, 2026-09-12)

Every button whose destination is `/contact` reads **"Need Help? Let's Talk"** and is the Signal Orange fill (`var(--cta)`, `#0E0E0E` text). Every button whose destination is `/tools/marketing-audit` reads **"Free AI Audit"** and is the **Mint outline** (transparent, `var(--mint)` text and 1px border, the footer tool-card treatment). This is a deliberate founder exception to "Mint never a CTA" (Decision 12): the audit is the free diagnostic, the orange button is the conversation. Implemented once in `styles.css` by destination attribute selectors so every scope (prototype, blog-dark, the Growth OS and Index page scopes) agrees; download and gate triggers that fall back to `/contact` are excluded. In the nav this makes the main pill Mint outline and the secondary pill orange; on the two Growth OS pages the download buttons step back to the white outline so the orange contact button carries the page.
