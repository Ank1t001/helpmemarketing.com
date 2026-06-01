# HMM Phase 2 Migration Reference

**Purpose:** Single source of truth for all Phase 2 work on helpmemarketing.com. Read this at the start of every Phase 2 session before writing any brief or making any architectural decision.

**Companion canonical docs (already in this Claude.ai project):**
- `HMM-Color-System.docx` — full color palette spec, 6 Golden Rules, CSS variables
- `HMM_Content_Rules_v0_2.md` — voice canon, banned phrases, EEAT, validation checklist

**Companion docs (in the GitHub repo at github.com/Ank1t001/helpmemarketing.com):**
- `/docs/HMM_Design_System.md` — descriptive doc of homepage as canonical pattern
- `/docs/HMM_Color_System.md` — repo version of the color spec for Claude Code
- `/docs/HMM_Content_Rules.md` — repo version of voice canon for Claude Code

**Status:** Live document. Update at the end of each Phase 2 session if new patterns lock or new decisions are made.

**Last updated:** June 1, 2026 (end of session that completed Phase 2 blog migration + the em-dash content cleanup pass across all 10 in-scope blogs)

---

## 1. Where We Are

### Phase progress

**Companion-page track (services):**
- Phase 1 (homepage shippability): Complete. Commits 0cc3e9d, b60ac6e, d232097.
- `/contact` migration: Complete (commits d232097 + ce577a6 white-band fix).
- `/services`, `/services/seo`, + 5 category pages: still pending (not yet started).

**Blog migration track (the focus of late-May / June 1 sessions): COMPLETE on `redesign-prototype-homepage`.**
- **Phase 1 — structural:** all 8 old-structure blogs migrated to V5 D-hybrid (structure signature `2f5ae86a`). Commits `2e4662b`, `8755e1c`.
- **Phase 2 — dark + chrome + author-line + text-only hero:** all 12 main blogs. Commits `af445a1`, `f13ca86`, `137d970`, `40ba53f`.
  - **Text-only hero is the permanent house style** (the real-hero PNG pass was cancelled, not deferred). `og:image`/`twitter:image` stay `/og-image.svg` sitewide; no per-blog hero images, no BlogPosting `image` key. Exception: `paid-ads-vs-organic` retains an image hero (uses the shared `.hero-illustration--image` rule); the other 11 are text-only.
- **Em-dash content cleanup pass:** 10 in-scope blogs, 303 in-scope em-dashes replaced per founder per-instance rulings. Commits `8e56cc4`, `18220bc`, `8571f07`, `ee6b140`.
  - 0 en-dashes touched (ranges preserved). 2 H2 anchor ids preserved (`strategy-stage-by-stage`, `seven-mistakes`). 4 ★ (U+2605) preserved. FAQPage schema re-baselined per blog. `paid-ads-vs-organic` + `healthcare-marketing-channels` had 0 in-scope (all em-dashes in HTML comments).
- **Lone outlier:** `meta-attribution` (older-arch, partial-nav) — not yet migrated, on its own track.

*Blog migration specifics (the ~17-op structural transform, text-only-hero house style, dark+chrome pattern, the FAQ schema-sync rule, embedded-`<style>` surgery, ★ and H2-anchor preservation) are canonicalized in `HMM_Blog_Template_V2_Master_Reference.md` — that file is the blog canon; this section is status only.*

### Repo state

- Main branch: `main` — still serves the old light-mode site to the public.
- Working branch: `redesign-prototype-homepage` at `ee6b140` — all blog Phase 1 + Phase 2 + em-dash work.
- **Merge `redesign-prototype-homepage` → `main` is the next major milestone (the production ship).** Full diff review first.
- Known pre-merge cleanup: cross-batch footer drift (Batch-1 blogs use footer md5 `9662d817`, Batch-2 use `c57c2445`; nav is uniform `babdc26e`) — reconcile footer to one canonical before merge.

### Founder strategic position

- 200-1000 monthly visitors to homepage
- Velocity > polish, but velocity into the wrong destination is worse than slowing to map
- Path A locked: migrate companion pages first, then ship clean (vs. shipping homepage alone with inconsistent companions)
- Realistic Phase 2 timeline: 2-3 weeks of focused work across multiple sessions

---

## 2. Locked Architectural Decisions

### Service architecture: C1 (locked)

**6 top-level categories, no channel sub-pages.** Channels live as H2 sections inside category pages.

1. Performance Marketing (channels: Google Ads, Meta Ads, LinkedIn Ads, TikTok Ads — confirm actuals when building page)
2. SEO + AEO
3. Branding & Social
4. Website Development
5. Analytics & Attribution
6. Lifecycle & Retention

**Why C1 not C2:** Smaller scope, concentrated SEO weight, easier maintenance, future-flexible. Channel sub-pages can be added later if a single channel becomes >40% revenue or warrants dedicated paid traffic.

### URL scheme: `/services/[category-slug]` (locked)

Canonical URLs:
- `/services/performance-marketing`
- `/services/seo`
- `/services/branding-social`
- `/services/website-development`
- `/services/analytics-attribution`
- `/services/lifecycle-retention`
- `/services` — overview/hub page (kept)

**8 legacy `.html` files at root will be 301-redirected** to new structure in a future commit (when category pages exist). NOT this commit's scope.

**Mapping for redirects:**
- `seo.html` → `/services/seo`
- `google-meta-ads.html` → `/services/performance-marketing`
- `website-design.html` → `/services/website-development`
- `social-media.html` → `/services/branding-social`
- `brand-content.html` → `/services/branding-social`
- `reviews-reputation.html` → `/services/branding-social#reviews`
- `lifecycle-retention.html` → `/services/lifecycle-retention`
- `analytics.html` → `/services/analytics-attribution`

### Footer architecture (locked)

**3 columns + footer-baseline.** Brand column and Resources column dropped sitewide.

**Columns:** Services | Industries | Company.

**Footer Services column** (lists 6 category names, links to new URLs):
- Performance Marketing → `/services/performance-marketing`
- SEO + AEO → `/services/seo`
- Branding & Social → `/services/branding-social`
- Website Development → `/services/website-development`
- Analytics & Attribution → `/services/analytics-attribution`
- Lifecycle & Retention → `/services/lifecycle-retention`

**Footer Industries column** (unchanged):
- DTC, SaaS, Healthcare, Finance — each links to `/industries/[slug]`

**Footer Company column:**
- About, Case Studies (`/work`), Pricing, Blog, Contact

**Footer-baseline** holds: copyright + Privacy/Terms (left) and Partner badges + Hello@helpmemarketing.com (right). Stacks vertically at ≤720px.

**Class names** (use existing prototype homepage classes, don't invent new ones):
- `.footer-grid` for the 3-column row
- `.footer-column` for each column
- `.footer-column h4` for column headings
- `.footer-baseline` for the bottom row
- `.footer-baseline-meta` for badges + email cluster

### Form chip taxonomy (locked)

**7 chips in buyer language, in order:**
1. SEO
2. Ads
3. Brand & Social
4. Website
5. Analytics
6. Email & retention
7. Not sure yet

**Data-service attrs use internal category slugs** (for clean Apps Script payload):
- SEO → `data-service="seo"`
- Ads → `data-service="performance-marketing"`
- Brand & Social → `data-service="branding-social"`
- Website → `data-service="website-development"`
- Analytics → `data-service="analytics-attribution"`
- Email & retention → `data-service="lifecycle-retention"`
- Not sure yet → `data-service="not-sure"`

### Other locked details

- **Email casing:** `Hello@helpmemarketing.com` for visible UI text. `hello@` acceptable in schema/JSON-LD/JS error strings (RFC + schema convention).
- **Partner badges:** Google Partner + Meta Partner only. Shopify Partner dropped (not active).
- **Logo:** "HMM" pattern — `H` + `<span class="me-italic">MM</span>` (NOT `<em>MM</em>` — the existing CSS targets `.me-italic`, not `<em>`)
- **Wordmark "Me":** `<em>` inside `.nav .logo` — existing CSS targets `<em>` directly here, NOT `<span>`

---

## 3. Design System — 10 Locked Decisions (audit reconciliation)

These were locked after a homepage design system audit found deviations between the Color System spec and shipped homepage CSS.

**Decision 1: Signal Orange application (REFRAMED)**
- ALWAYS used on: Primary CTAs (buttons, click affordances), CTA box-shadow glows
- ACCEPTABLE brand-identity accents (not subject to a cap):
  - Logo mark italic "MM"
  - Wordmark italic "Me"
  - H1 italic accent words (e.g., "100 customers")
  - Hero ambient glow (.hero::before)
  - Brand-comparison emphasis (HMM card border/title)
  - CTA arrows inside actionable cards (whole card is the CTA)
- NEVER used on: body text, regular structural borders, non-CTA backgrounds, decorative elements without brand-identity purpose
- **This supersedes the Color System docx's "Maximum two non-CTA usages per page" rule.** The cap was too strict for actual brand language.

**Decision 2: Service-card arrow** — Counted as CTA affordance (whole card is the CTA), not a non-CTA Signal Orange usage.

**Decision 3: Focus-state borders** — Solid `var(--cta)` is a valid exception to Rule 4. Structural borders use rgba; state indicators (`:focus`, `:error`, `:active`) may use solid token colors for accessibility/visibility.

**Decision 4: Opacity values** — Shipped values are canonical:
- `--grid-line: rgba(255,255,255,0.045)` (NOT the docx's 0.025)
- `--orange-glow: rgba(255,92,26,0.18)` (NOT the docx's 0.12)
- These were tuned during implementation against the actual hero composition.

**Decision 5: Two breakpoints codified**
- 900px primary (major layout flip)
- 720px secondary (component-level adjustments, e.g., footer-baseline stack)

**Decision 6: Warm-break tokens** — Kept as reserved. Tokens defined (`--warm-bg`, `--warm-text`, `--warm-cta`) for future warm-break section. No current usage.

**Decision 7: `.bullet-list`** — Defined in prototype CSS but unused on homepage. Status: reserved. Verify usage on other pages during their migration; remove if unused sitewide.

**Decision 8: `.service-card h3` mobile fix** — Currently stays at 24px on mobile (no mobile override matches). Fix: add 20px override at ≤900px. Deferred to a small follow-up commit, not blocking.

**Decision 9: Tier system tokens (RESERVED — not yet in styles.css)**
- `--surface-subtle: rgba(255,255,255,0.02)` — wash hovers
- `--surface-hover: rgba(255,255,255,0.05)` — nav/button hovers
- `--border-strong: rgba(255,255,255,0.16)` — card hover borders
- `--cta-glow-soft: rgba(255,92,26,0.15)` — focus glow
- `--cta-glow-strong: rgba(255,92,26,0.35)` — button hover shadow
- **Status:** Documented in Color System markdown but NOT yet implemented. Will be added before any major component refactor.

**Decision 10: Color System docx** — Markdown version committed to `/docs/HMM_Color_System.md`. Source docx remains in this Claude.ai project for reference.

---

## 4. Italic Accent Treatment — Three Patterns

**This is the section that prevents `/contact`-gold-style bugs.** The `/contact` migration shipped with `<span style="color:var(--gold)">Me</span>` which silently bypassed prototype italic-accent CSS. Three correct patterns:

### Pattern 1: H1 italic accent word
- HTML: `<em>` child inside `h1.hero-headline`
- CSS: `body.redesign-prototype h1.hero-headline em { color: var(--cta); font-style: italic; font-weight: 400 }`
- Example: `<h1>We use AI to find your next <em>100 customers</em></h1>`

### Pattern 2: Wordmark "Me" italic
- HTML: `<em>` child inside `.nav .logo`
- CSS: `body.redesign-prototype .nav .logo em { color: var(--cta) }`
- Example: `<span class="logo-text">Help<em>Me</em>Marketing</span>`

### Pattern 3: Logo mark "MM" italic
- HTML: `<span class="me-italic">MM</span>` inside `.logo-mark` (NOT `<em>` — existing CSS specifically targets `.me-italic`)
- CSS: `body.redesign-prototype .logo-mark .me-italic { color: var(--cta) }`
- Italic enforced via legacy `.logo-mark .me-italic { font-style: italic }`
- Example: `<div class="logo-mark">H<span class="me-italic">MM</span></div>`

### Forbidden — never do this
- `var(--gold)` anywhere in `body.redesign-prototype` scope
- Inline `style="color:..."` on prototype HTML elements
- `<span>` with hardcoded color attempting italic accent — use `<em>` (patterns 1/2) or `<span class="me-italic">` (pattern 3)

---

## 5. Forbidden Patterns (full list)

### Forbidden in CSS (under `body.redesign-prototype` scope)
- Legacy color tokens: `var(--gold)`, `var(--navy)`, `var(--cream)`, `var(--ivory)`, `var(--deep)`, `var(--ink-*)`, `var(--line)`, `var(--primary)`, `var(--mint-soft)`, `var(--white)`
- Hardcoded hex values as property values (existing definitions are tokens only)
- Solid borders on structural elements (use rgba; solid acceptable only for state indicators per Decision 3)

### Forbidden in HTML
- Inline `style="color:..."` on prototype elements
- `<span style="color:var(--gold)">` patterns for italic accents — use the three patterns above
- Footer logo with `style="background:var(--ivory); color:var(--navy)"` overrides
- Any markup that relies on legacy tokens being inherited

### Forbidden in written content (per HMM_Content_Rules_v0_2.md)
- All AI-generated tells: leverage, utilize, empower, supercharge, crucial, pivotal, paramount, seamless, holistic, delve, navigate the landscape, game-changing, revolutionary, cutting-edge
- AI clichés: transform, revolutionize, intelligent solutions, AI-powered (as filler), next-generation, synergy, ecosystem (as buzzword), democratize, paradigm shift, disruption, at scale (as filler), reimagine
- Em-dashes (—) anywhere — use periods, commas, parentheses, or colons
- "Premium" as marketing adjective
- "Just" in promotional contexts
- "#1" or "best" without verifiable ranking
- "Guaranteed results"
- Title Case on headings (always sentence case)

---

## 6. Phase 2 Page Migration Workflow

### Pre-flight (every page)
1. Read this reference doc in full
2. Read `HMM-Color-System.docx` (in project files)
3. Read `HMM_Content_Rules_v0_2.md` (in project files)
4. Confirm the page's current state — pull live page or read current HTML
5. Identify any legacy patterns/inline styles/forbidden tokens

### Brief writing (every page)
1. Use audit-first structure — Claude Code reads existing files before any edits
2. Pause-for-approval at every checkpoint (don't bundle)
3. Reference canonical docs by exact filename (don't re-state rules; cite them)
4. Use copy-paste-ready single-block briefs (no surrounding commentary)
5. Apply the locked architectural decisions from Section 2
6. Apply the design decisions from Section 3
7. Apply the italic accent patterns from Section 4 if H1 or logo treatment applies

### Standard checkpoint structure (every brief)
- Checkpoint 1: Pre-work read (no edits, just diagnosis + scope confirmation)
- Checkpoint 2: HTML changes (if applicable)
- Checkpoint 3: CSS changes (if applicable)
- Checkpoint 4: Self-verification (form JS integrity if forms touched, no legacy tokens used, all decisions applied)
- Checkpoint 5: Pre-commit review (diff stats, commit message, risks)

### Verification (every page after commit)
1. Open Vercel preview URL
2. Desktop verification at 1440px+
3. DevTools verification at 375px (mobile)
4. DevTools verification at 768px (tablet)
5. White-background sweep (run console script to check for `rgb(255,255,255)` on wrapper elements — added to checklist after `/contact` white-band issue)
6. If page has a form: submit test entry, verify Apps Script payload, verify thank-you state

### Console script for white-background check (run after any migration)
```javascript
document.querySelectorAll('*').forEach(el => {
  const bg = getComputedStyle(el).backgroundColor;
  if (bg.match(/255,\s*255,\s*255/) || bg.includes('rgb(250') || bg.includes('rgb(248')) {
    console.log('LIGHT BG:', el.tagName, el.className, bg);
  }
});
```

Expected: only the honeypot `INPUT` (positioned offscreen) returns. Anything else is a legacy wrapper that needs prototype override.

---

## 7. Working Style — Operating Principles

### Brief writing
- Single copy-pasteable block, no surrounding chat commentary
- Briefs format for Claude Code, not for humans skimming
- Cite canonical docs as authority; don't restate rules
- Include explicit "Out of scope" section
- Include estimated commit size + time
- Include risk audit before commit

### Checkpoint discipline
- Pause-for-approval at every checkpoint
- "Just keep going" without approval is a process violation (even if the work is technically correct)
- If Claude Code skips a checkpoint, flag it; don't silently accept

### Decision discipline
- Lock decisions explicitly ("Lock Option A" not "let's do A")
- Document decisions in this reference doc as they lock
- Don't re-litigate locked decisions without new information
- "I want to discuss" is a valid response — slow down is fine

### Audit-first discipline
- Read files before editing them (catches inherited legacy patterns)
- Diagnose before prescribing (the `.app` white-bg root cause needed diagnosis, not guessing)
- Console-script verify visual claims (DevTools beats source-code inference)

### Followup tracking
- Log followups in commit messages (immutable record)
- Log followups in Claude Code's user-home memory (working list)
- Update this doc when a followup becomes a locked decision

---

## 8. Open Items / Followups

### Known followups (not blocking current work)
- `.bullet-list` usage check (Decision 7) — defined but unused on homepage
- Tier system tokens implementation (Decision 9) — 5 tokens documented, need styles.css addition before component refactor
- `.service-card h3` mobile font-size override (Decision 8) — 20px at ≤900px
- HMM_Content_Rules v0.2 → v1.0 lock (founder approval session)
- Legacy CSS specificity bug at styles.css:137/147 (`.btn` overriding `.nav-main-cta` display:none) — affects live site, fix in `main` branch cleanup commit
- Sitewide email-casing sweep (Hello@ vs hello@) — minor inconsistency
- Sitewide audit for stale Shopify Partner badges
- Update homepage footer to match `/contact` pattern (add partner badges + email to footer-baseline)
- `/contact` og:image update to align with redesign aesthetic
- Structural HTML drift: `index.html` has no `.app` wrapper; other 29 pages do — normalize during a future Phase 2 cleanup

### Lifecycle & Retention positioning honesty
Lifecycle is marked R&D in Content Rules Section 7.3 but elevated to top-level category. When building that page, decide:
- Label as Active/R&D honestly per Content Rules, OR
- Re-tier to Proven before the page ships

### Next priorities (in order)
1. **Pre-merge cleanup followups** (the blog track): commit this doc to `/docs/`; `body.blog-dark .author-line .dot` contrast fix; dead-CSS cleanup (orphan `body.blog-dark .author-block` rules, V5-unused since the author-line rewrite in `40ba53f`, + the orphan V5 hero PNG `healthcare-marketing-channels-hero.png` on disk); **cross-batch chrome sweep** (footer drift: Batch-1 footer md5 `9662d817` vs Batch-2 `c57c2445`; nav uniform `babdc26e` — reconcile footer to one canonical).
2. **Merge `redesign-prototype-homepage` → `main`** (production ship — full diff review first).
3. `meta-attribution` migration (older-arch outlier, separate track).
4. Companion-page track resumes: `/services` overview, `/services/seo`, 5 category pages.
5. Optional: zero-in-scope blog comment sweep (em-dashes in HTML comments on `paid-ads-vs-organic` + `healthcare-marketing-channels` — hygiene only, exempt per Content Rules §2.3).

---

## 9. How to Update This Doc

When a new pattern locks or a new decision is made:
1. Add it to the relevant section
2. Update the "Last updated" date at the top
3. If the decision conflicts with the Color System docx or Content Rules, flag it explicitly here AND raise the question of whether to update the source docs
4. Memory entries in Claude.ai are derived from this doc — they get refreshed when this doc updates

This doc is the working canon. The Color System docx and Content Rules v0.2 are the principle canon. When this doc and the principle canon disagree, the principle canon usually wins — unless the founder has explicitly locked a deviation (e.g., Decision 1 reframing Rule 1).

---

---

## 10. Changelog

| Date | Change |
|---|---|
| May 21, 2026 | `/contact` migration + white-band fix shipped. Doc established as Phase 2 working canon. |
| June 1, 2026 | Blog migration track completed on `redesign-prototype-homepage`: Phase 1 structural (8 blogs → V5 D-hybrid `2f5ae86a`), Phase 2 dark + canon chrome + simplified author-line + text-only hero (12 blogs), em-dash content cleanup pass (10 blogs, 303 in-scope em-dashes replaced, 0 en-dashes touched, 2 H2 anchors + 4 ★ preserved). Text-only hero locked as permanent house style (real-hero PNG pass cancelled). Cross-batch footer drift identified (`9662d817` vs `c57c2445`) — flagged for pre-merge sweep. Status sections updated; blog specifics deferred to `HMM_Blog_Template_V2_Master_Reference.md`. |

---

*End of HMM Phase 2 Migration Reference*
*Maintained by: Ankit Kumar (founder) + Claude.ai (assistant)*
*Update cadence: End of each Phase 2 session, or when locked decisions change*
