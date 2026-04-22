# DESIGN.md — HelpMeMarketing Design System

Canonical reference for the repositioned helpmemarketing.com (premium generalist agency: DTC, SaaS, Healthcare, Finance).

Extracted from `C:\Users\AnkitKumar\Downloads\helpmemarketing-mockup.html`. When the mockup and this document disagree, this document wins — it is the source of truth for implementation. Update it here first, then propagate to `styles.css`.

---

## 1. Tokens

### 1.1 Color

```css
:root {
  /* Surfaces */
  --ivory:          #FAF9F6;   /* default page background */
  --gray-surface:   #F1EFEB;   /* alt sections, hero bg, subtle panels */
  --border:         #E8E4DC;   /* hairline borders on cards + dividers */

  /* Text */
  --text-primary:   #1A1A1A;   /* headlines + body */
  --text-secondary: #6B7280;   /* supporting copy, labels */
  --text-tertiary:  #9CA3AF;   /* meta, timestamps, inactive */

  /* Dark sections */
  --navy:           #0A1628;   /* footer, CTA card, process section */
  --navy-dark:      #050B14;   /* CTA button on navy card */
  --navy-light:     #1E2D47;   /* primary button hover */

  /* Accent */
  --gold:           #C9A96E;   /* italic-accent, eyebrow dot, gold borders */
  --gold-soft:      #E4D4A8;   /* eyebrow text on dark backgrounds */

  /* Data viz ONLY (never UI chrome) */
  --chart-blue:     #2563EB;   /* sparklines, positive trend lines */
  --chart-green:    #10B981;   /* live-indicator dot, positive delta */
  --chart-red:      #EF4444;   /* negative delta (rarely used) */

  /* Type families */
  --serif: 'Fraunces', Georgia, serif;
  --sans:  'Inter', -apple-system, sans-serif;
}
```

**Icon-color pairs** used on service-card icon squares:

```css
.ic-blue    { background: #E6F1FB; color: #185FA5; }
.ic-gold    { background: #F5EDD8; color: #8B6F2E; }
.ic-sand    { background: #EDE7DD; color: #5F5144; }
.ic-green   { background: #E1F5EE; color: #0F6E56; }
.ic-navy    { background: #E1E6EE; color: #0A1628; }
.ic-crimson { background: #FCEBEB; color: #A32D2D; }
```

These are decorative, paired with monoline SVG icons. One color per service, held consistent across pages.

### 1.2 Typography

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;1,9..144,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
```

| Element          | Family  | Size              | Weight | Tracking  | Leading | Notes |
|------------------|---------|-------------------|--------|-----------|---------|-------|
| Body             | Inter   | 17px              | 400    | 0         | 1.6     | Default paragraph |
| Small body       | Inter   | 14px              | 400    | 0         | 1.6     | Secondary text, card body |
| Eyebrow          | Inter   | 12px UPPERCASE    | 500    | 0.15em    | 1.2     | Preceded by 4px gold dot |
| Nav link         | Inter   | 15px              | 400    | 0         | 1.2     | Hover → gold; active weight 500 |
| Button           | Inter   | 14px              | 500    | 0         | 1       | Pill (radius 100px), 12px 24px |
| H1 (hero)        | Fraunces| 84px              | 400    | -0.02em   | 1.05    | One `.italic-accent` word max |
| H2 (section)     | Fraunces| 56px              | 400    | -0.02em   | 1.05    | 52px on pain-left |
| H3 (card title)  | Fraunces| 22px              | 400    | -0.02em   | 1.1     | Service/case card titles |
| H3 (industry tile) | Inter | 17px              | 500    | 0         | 1.3     | Sans for smaller heads |
| H4 (pain item)   | Inter   | 18px              | 500    | 0         | 1.3     | Sans, part of list row |
| Metric value (hero) | Fraunces | 56px           | 400    | -0.03em   | 1       | Paired with sparkline |
| Metric-small value  | Fraunces | 22px           | 400    | 0         | 1.2     | Grid of 2 below main metric |
| Case metric         | Fraunces | 72px           | 400    | -0.03em   | 1       | White on dark overlay |
| Industry metric     | Fraunces | 28px           | 400    | 0         | 1       | Navy on ivory tile |
| Testimonial quote   | Fraunces | 42px           | 400    | -0.02em   | 1.2     | Centered, max-width 900 |
| CTA h2           | Fraunces| 60px              | 400    | -0.02em   | 1.05    | Ivory on navy card |
| Process step h3  | Inter   | 18px              | 500    | 0         | 1.3     | Ivory on navy |

**Italic styling** — Fraunces has an italic axis; use it for:
- `.italic-accent` (see rule below)
- Testimonial-quote italic variant
- Case-quote on case cards
- Logo wordmark's `Me` and logo-mark's small `m`

### 1.3 Spacing + layout

```css
.container { max-width: 1280px; margin: 0 auto; padding: 0 48px; }
section { padding: 140px 0; }
section.alt { background: var(--gray-surface); }
.section-header { margin-bottom: 72px; }
```

**Radii**: cards 16px, metric card 14px, CTA card 24px, pills/buttons 100px, icon squares 10px.

**Border**: hairline 1px `var(--border)`. Cards do NOT use drop-shadows — they use border + hover `transform: translateY(-2px)`.

**Shadow** (metric cards only): `box-shadow: 0 1px 3px rgba(26, 22, 14, 0.04);` — subtle, one layer, intentional.

---

## 2. The italic-gold accent rule

> **One italic accent per headline, maximum. Color `#C9A96E`. Reserved for the single most semantically important word in the headline.**

```css
.italic-accent {
  font-style: italic;
  color: var(--gold);
  font-weight: 400;
}
```

**Correct uses** (from mockup):
- `We scale premium brands with <em>strategy</em> and <em>performance</em>.` → one headline, two accents — allowed only when the headline has exactly two parallel concepts and both are load-bearing. Default to one.
- `Growing a premium brand shouldn't feel <em>this</em> hard.`
- `Every growth lever your brand <em>needs</em>. One team.`
- `Built for <em>premium</em> brands across industries.`
- `Results that show up <em>in the books</em>.`
- `A process built around <em>your</em> brand, not a playbook.`
- `Ready to grow the <em>right</em> way?`

**Incorrect uses** — do NOT:
- Apply gold italic to multiple phrases in the same headline just for rhythm
- Apply it to subheads, labels, or body copy
- Use it for emphasis in CTA buttons or pills
- Use a color other than `#C9A96E` for the italic

**When writing new headlines**: pick the one word that, if removed, would change the headline's meaning most. That word gets the accent. If no word stands out, the headline itself may be wrong — rewrite before adding accent.

---

## 3. Dark-section treatment

Navy `#0A1628` is the dark background for: **footer**, **CTA card** (`.cta-card`), and **process section** (`.process`).

Every dark section gets two ambient gold radial gradients — warmth without literal gold shapes:

```css
.dark-section::before {
  content: '';
  position: absolute;
  top: -100px; right: -100px;
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(201,169,110,0.08) 0%, transparent 70%);
  border-radius: 50%;
}
.dark-section::after {
  content: '';
  position: absolute;
  bottom: -150px; left: -100px;
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(201,169,110,0.05) 0%, transparent 70%);
  border-radius: 50%;
}
```

Opacity: 0.08 + 0.05 on process; 0.12 + 0.08 on CTA card (slightly warmer, punchier). Footer gets no radials — it's the quiet coda.

**Text on navy**: primary uses `var(--ivory)`; secondary/meta uses `rgba(250, 249, 246, 0.6–0.8)`. Eyebrow uses `var(--gold-soft)`. Headlines use `var(--ivory)` — italic-accent words still use `var(--gold)`.

---

## 4. Prohibitions

1. **No glassmorphism.** Nav uses `rgba(250, 249, 246, 0.95)` + `backdrop-filter: blur(12px)`, 1px bottom border. That's it. No frosted-glass panels, no blurred translucent cards.
2. **No drop-shadows on cards** (service, industry, case, pain-item rows). Hairline border only. The single exception is the metric card (hero): `box-shadow: 0 1px 3px rgba(26, 22, 14, 0.04)` — flat, single-layer, intentional.
3. **No gradient buttons.** Buttons are solid `--navy` (primary), transparent with border (outline), or solid `--navy-dark` with rgba white border (on-dark primary). Hover changes background or border color, never introduces a gradient.
4. **Chart colors (`--chart-blue`, `--chart-green`, `--chart-red`) are reserved for data viz inside metric cards.** They appear on: sparkline strokes/fills, live-dot, delta arrows (↑/↓), and inside metric-small values. They MUST NOT appear on: buttons, pills, nav, footer, text accents, CTA cards, or any UI chrome. If a non-data element needs color, use navy, gold, or text tokens.
5. **No gradient headlines, no gradient text.** Italic-accent is solid gold.
6. **No outer glow or neon effects.** Soft radial gold in dark sections is the ceiling for "atmospheric" effects.

---

## 5. Component patterns

### 5.1 Nav

```html
<nav>
  <div class="nav-inner">
    <div class="logo">
      <div class="logo-mark">H<span class="me-italic">m</span></div>
      Help<span class="wordmark-italic">Me</span>Marketing
    </div>
    <ul class="nav-links">
      <li><a href="#" class="active">Home</a></li>
      <li><a href="#">Services</a></li>
      <li><a href="#">Case Studies</a></li>
      <li><a href="#">About</a></li>
    </ul>
    <a href="#" class="btn btn-primary">Book a free audit <span class="arrow">→</span></a>
  </div>
</nav>
```

```css
nav {
  position: sticky; top: 0; z-index: 100;
  background: rgba(250, 249, 246, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
}
.nav-inner {
  max-width: 1280px; margin: 0 auto;
  padding: 20px 48px;
  display: flex; align-items: center; justify-content: space-between;
}
.logo { font-family: var(--serif); font-size: 22px; font-weight: 500; letter-spacing: -0.02em; display: flex; align-items: center; gap: 8px; }
.logo-mark {
  width: 32px; height: 32px; background: var(--navy); color: var(--ivory);
  border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--serif); font-size: 16px; font-weight: 500;
}
.logo-mark .me-italic { font-style: italic; color: var(--gold); margin-left: 1px; }
.wordmark-italic { font-style: italic; color: var(--gold); font-weight: 400; }
.nav-links { display: flex; gap: 36px; list-style: none; }
.nav-links a { color: var(--text-primary); font-size: 15px; font-weight: 400; transition: color .2s; }
.nav-links a:hover { color: var(--gold); }
.nav-links a.active { font-weight: 500; }
```

**Do NOT** include a "Health & Care" pill or any vertical pill. No industries link in main nav.

### 5.2 Footer

```html
<footer>
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <div class="logo"> …Hm mark + wordmark… </div>
        <p>A growth partner built for premium brands. Ethical marketing that scales — across industries, without the playbook.</p>
        <div class="footer-badges">
          <span class="footer-badge">Google Partner</span>
          <span class="footer-badge">Meta Partner</span>
          <span class="footer-badge">Shopify Partner</span>
        </div>
      </div>
      <div class="footer-col"><h5>Services</h5><ul>…</ul></div>
      <div class="footer-col"><h5>Industries</h5><ul>…</ul></div>
      <div class="footer-col"><h5>Company</h5><ul>…</ul></div>
      <div class="footer-col"><h5>Resources</h5><ul>…</ul></div>
    </div>
    <div class="footer-bottom">
      <span>© 2026 HelpMeMarketing Inc.</span>
      <div><a href="#">Privacy</a><a href="#">Terms</a></div>
    </div>
  </div>
</footer>
```

```css
footer { background: var(--navy); color: var(--ivory); padding: 80px 0 40px; }
.footer-grid { display: grid; grid-template-columns: 1.5fr repeat(4, 1fr); gap: 48px; margin-bottom: 64px; }
.footer-brand p { font-size: 14px; color: rgba(250, 249, 246, 0.6); line-height: 1.5; max-width: 280px; margin-bottom: 24px; }
.footer-badges { display: flex; flex-wrap: wrap; gap: 8px; }
.footer-badge { font-size: 11px; padding: 6px 12px; border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 100px; color: rgba(250, 249, 246, 0.8); }
.footer-col h5 { font-family: var(--sans); font-size: 12px; text-transform: uppercase; letter-spacing: 0.15em; color: rgba(250, 249, 246, 0.5); font-weight: 500; margin-bottom: 20px; }
.footer-col a { color: rgba(250, 249, 246, 0.8); font-size: 14px; transition: color .2s; }
.footer-col a:hover { color: var(--gold); }
.footer-bottom { padding-top: 32px; border-top: 1px solid rgba(255, 255, 255, 0.1); display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: rgba(250, 249, 246, 0.5); }
```

**Column order**: Brand (1.5fr) | Services | Industries | Company | Resources. Industries column is new — DTC & E-commerce / SaaS & Tech / Healthcare / Finance. No "HIPAA-aware" badge anywhere.

### 5.3 Buttons

```css
.btn { display: inline-flex; align-items: center; gap: 8px; padding: 12px 24px; border-radius: 100px; font-family: var(--sans); font-size: 14px; font-weight: 500; text-decoration: none; transition: all .2s; border: none; cursor: pointer; }
.btn-primary       { background: var(--navy); color: var(--ivory); }
.btn-primary:hover { background: var(--navy-light); }
.btn-outline       { background: transparent; color: var(--text-primary); border: 1px solid var(--border); }
.btn-outline:hover { border-color: var(--navy); }
.btn-outline-light       { background: transparent; color: var(--ivory); border: 1px solid rgba(255,255,255,0.2); }
.btn-outline-light:hover { border-color: rgba(255,255,255,0.5); }
.btn-cta-primary       { background: var(--navy-dark); color: var(--ivory); border: 1px solid rgba(255,255,255,0.1); }
.btn-cta-primary:hover { background: black; }
.arrow { font-size: 14px; transition: transform .2s; }
.btn:hover .arrow { transform: translateX(2px); }
.text-link { color: var(--text-primary); text-decoration: none; font-size: 14px; font-weight: 500; border-bottom: 1px solid var(--gold); padding-bottom: 2px; transition: color .2s; }
.text-link:hover { color: var(--gold); }
```

### 5.4 Eyebrow

```html
<span class="eyebrow">What we do</span>
<span class="eyebrow on-dark">How we work</span>
```

```css
.eyebrow { font-family: var(--sans); font-size: 12px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.15em; color: var(--navy); display: inline-flex; align-items: center; gap: 8px; }
.eyebrow::before { content: ''; width: 4px; height: 4px; border-radius: 50%; background: var(--gold); }
.eyebrow.on-dark         { color: var(--gold-soft); }
.eyebrow.on-dark::before { background: var(--gold); }
```

### 5.5 Hero + metric card

```html
<section class="hero">
  <div class="container">
    <div class="hero-grid">
      <div>
        <span class="eyebrow">A premium growth partner</span>
        <h1>We scale premium brands with <span class="italic-accent">strategy</span>.</h1>
        <p class="hero-subtitle">Growth marketing for DTC, SaaS, healthcare, and finance brands — priced on outcomes, not hours.</p>
        <div class="hero-ctas">
          <a href="#" class="btn btn-primary">Get my free growth audit <span class="arrow">→</span></a>
          <a href="#" class="text-link">See real client results →</a>
        </div>
      </div>
      <div class="hero-visual">
        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-label">Bookings · last 30 days</span>
            <span class="live-indicator"><span class="live-dot"></span> Live</span>
          </div>
          <div class="metric-value">+38% <span class="metric-delta">↑ MoM</span></div>
          <div class="metric-sparkline"><!-- svg --></div>
        </div>
        <div class="metric-grid">
          <div class="metric-small">…</div>
          <div class="metric-small">…</div>
        </div>
      </div>
    </div>
  </div>
</section>
```

```css
.hero { background: var(--gray-surface); padding: 100px 0 140px; position: relative; overflow: hidden; }
.hero-grid { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 80px; align-items: center; }
.hero h1 { font-size: 84px; margin: 24px 0 28px; }
.hero-subtitle { font-size: 18px; color: var(--text-secondary); line-height: 1.5; margin-bottom: 40px; max-width: 520px; }
.hero-ctas { display: flex; gap: 20px; align-items: center; }

.metric-card { background: white; border-radius: 14px; padding: 24px; box-shadow: 0 1px 3px rgba(26,22,14,0.04); border: 1px solid var(--border); }
.metric-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.metric-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.12em; color: var(--text-secondary); font-weight: 500; }
.live-indicator { display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--chart-green); font-weight: 500; }
.live-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--chart-green); animation: pulse 2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
.metric-value { font-family: var(--serif); font-size: 56px; font-weight: 400; letter-spacing: -0.03em; line-height: 1; display: flex; align-items: baseline; gap: 8px; }
.metric-delta { font-size: 14px; color: var(--chart-green); font-weight: 500; }
.metric-sparkline { margin-top: 20px; height: 60px; }

.metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 12px; }
.metric-small { background: white; border: 1px solid var(--border); border-radius: 12px; padding: 18px; }
.metric-small-label { font-size: 11px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px; }
.metric-small-value { font-family: var(--serif); font-size: 22px; font-weight: 400; }
.metric-small-delta { font-size: 12px; color: var(--chart-green); margin-left: 4px; }
```

Sparkline uses `--chart-blue` for stroke + 0.18/0 gradient fill. This is the one place chart colors appear on the homepage.

### 5.6 Service card

```html
<div class="service-card">
  <div class="service-icon ic-blue">
    <svg class="svc-icon-svg" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5">…</svg>
  </div>
  <h3>SEO</h3>
  <p>Outrank competitors for every search your buyers actually run. Editorial content, technical SEO, and links.</p>
  <a href="#" class="service-link">Explore →</a>
</div>
```

```css
.services-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.service-card { background: var(--ivory); border: 1px solid var(--border); border-radius: 16px; padding: 32px; transition: all .25s; cursor: pointer; }
.service-card:hover { border-color: var(--navy); transform: translateY(-2px); }
.service-icon { width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 28px; }
.svc-icon-svg { width: 20px; height: 20px; }
.service-card h3 { font-size: 22px; margin-bottom: 10px; }
.service-card p { font-size: 14px; color: var(--text-secondary); margin-bottom: 24px; line-height: 1.6; }
.service-link { font-size: 13px; color: var(--text-primary); font-weight: 500; text-transform: uppercase; letter-spacing: 0.1em; display: inline-flex; align-items: center; gap: 6px; border-bottom: 1px solid var(--gold); padding-bottom: 2px; text-decoration: none; }
```

**Six services with locked icon-color mapping**:

| Service                  | Icon class   | Mockup icon motif |
|--------------------------|--------------|-------------------|
| SEO                      | `ic-blue`    | Magnifier         |
| Google & Meta Ads        | `ic-gold`    | Concentric circles (target) |
| Website Design           | `ic-sand`    | Browser window    |
| Social Media             | `ic-green`   | Speech bubble     |
| Brand & Content          | `ic-navy`    | Plus / compass    |
| Lifecycle & Retention    | `ic-crimson` | Plus in circle    |

### 5.7 Industry tile

```html
<div class="industry-tile">
  <div class="industry-illustration"><div class="illus-circle"><!-- monoline svg --></div></div>
  <h3>DTC & E-commerce</h3>
  <p>Scale acquisition and retention for premium consumer brands.</p>
  <div class="industry-metric">
    <div class="industry-metric-value">+312%</div>
    <div class="industry-metric-label">Avg. revenue lift, 12 mo</div>
  </div>
</div>
```

```css
.industries-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.industry-tile { background: var(--ivory); border: 1px solid var(--border); border-radius: 16px; padding: 36px 28px; transition: all .25s; cursor: pointer; }
.industry-tile:hover { border-color: var(--navy); transform: translateY(-2px); }
.industry-illustration { width: 56px; height: 56px; margin-bottom: 28px; display: flex; align-items: center; justify-content: center; }
.illus-circle { background: var(--gray-surface); width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.industry-tile h3 { font-family: var(--sans); font-size: 17px; font-weight: 500; margin-bottom: 8px; }
.industry-tile p { font-size: 13px; color: var(--text-secondary); margin-bottom: 24px; line-height: 1.5; min-height: 40px; }
.industry-metric { padding-top: 20px; border-top: 1px solid var(--border); }
.industry-metric-value { font-family: var(--serif); font-size: 28px; font-weight: 400; color: var(--navy); }
.industry-metric-label { font-size: 12px; color: var(--text-secondary); margin-top: 4px; }
```

### 5.8 Case study card

```html
<div class="case-card">
  <div class="case-image case-1"></div>
  <div class="case-overlay"></div>
  <div class="case-content">
    <div class="case-top">
      <span class="case-pill">DTC</span>
      <span class="case-pill">6 months</span>
    </div>
    <div>
      <div class="case-metric">+312%</div>
      <div class="case-name">Arden & Oak</div>
      <div class="case-vertical">Premium skincare · Toronto</div>
      <div class="case-quote">"First agency that treated our P&L like their own."</div>
    </div>
  </div>
</div>
```

```css
.case-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.case-card { border-radius: 16px; overflow: hidden; position: relative; aspect-ratio: 4 / 5; cursor: pointer; transition: transform .3s; }
.case-card:hover { transform: translateY(-3px); }
.case-image { position: absolute; inset: 0; background-size: cover; background-position: center; }
.case-overlay { position: absolute; inset: 0; background: linear-gradient(to bottom, rgba(10,22,40,0.15) 0%, rgba(10,22,40,0.35) 50%, rgba(10,22,40,0.85) 100%); }
.case-content { position: absolute; inset: 0; padding: 24px; display: flex; flex-direction: column; justify-content: space-between; color: white; }
.case-top { display: flex; justify-content: space-between; }
.case-pill { background: rgba(255,255,255,0.95); color: var(--navy); font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.1em; padding: 6px 12px; border-radius: 100px; }
.case-metric { font-family: var(--serif); font-size: 72px; font-weight: 400; line-height: 1; letter-spacing: -0.03em; margin-bottom: 16px; }
.case-name { font-size: 14px; font-weight: 500; margin-bottom: 4px; }
.case-vertical { font-size: 12px; opacity: 0.8; margin-bottom: 14px; }
.case-quote { font-family: var(--serif); font-style: italic; font-size: 14px; opacity: 0.9; line-height: 1.4; }

/* Background placeholder gradients — replace with real photography */
.case-1 { background: linear-gradient(135deg, #D4A574 0%, #8B5A3C 100%); }
.case-2 { background: linear-gradient(135deg, #4A6B8A 0%, #1E2D47 100%); }
.case-3 { background: linear-gradient(135deg, #A8AFB8 0%, #4A5159 100%); }
```

**Content slots**: vertical pill, duration pill, metric, client, vertical+location, italic quote. When migrating old work.html cards, map `data-tag` values from healthcare verticals to new segments (DTC/SaaS/Healthcare/Finance).

### 5.9 Pain-point list

```html
<div class="pain-grid">
  <div class="pain-left">
    <span class="eyebrow">Sound familiar?</span>
    <h2>Growing a premium brand shouldn't feel <span class="italic-accent">this</span> hard.</h2>
    <p>Supporting context paragraph.</p>
  </div>
  <ul class="pain-list">
    <li class="pain-item">
      <span class="pain-num">01</span>
      <div class="pain-text"><h4>Flat revenue</h4><p>Body copy.</p></div>
      <span class="pain-arrow">→</span>
    </li>
    …
  </ul>
</div>
```

```css
.pain-grid { display: grid; grid-template-columns: 1fr 1.3fr; gap: 80px; align-items: start; }
.pain-left h2 { font-size: 52px; }
.pain-left p  { color: var(--text-secondary); margin-top: 24px; font-size: 16px; max-width: 400px; }
.pain-list { list-style: none; }
.pain-item { display: grid; grid-template-columns: 48px 1fr auto; gap: 24px; padding: 28px 0; border-top: 1px solid var(--border); align-items: center; cursor: pointer; transition: all .2s; }
.pain-item:last-child { border-bottom: 1px solid var(--border); }
.pain-item:hover { padding-left: 8px; }
.pain-num { font-family: var(--serif); font-size: 16px; color: var(--gold); font-weight: 500; }
.pain-text h4 { font-family: var(--sans); font-size: 18px; font-weight: 500; margin-bottom: 4px; color: var(--text-primary); }
.pain-text p  { font-size: 14px; color: var(--text-secondary); margin: 0; }
.pain-arrow   { color: var(--text-tertiary); font-size: 16px; }
```

Exactly four items, numbered 01–04. Numbers are small serif gold — NOT large.

### 5.10 Process steps (dark navy section)

```html
<section class="process">
  <div class="container">
    <div class="section-header centered">
      <span class="eyebrow on-dark">How we work</span>
      <h2>A process built around <span class="italic-accent">your</span> brand, not a playbook.</h2>
    </div>
    <div class="process-steps">
      <div class="process-line"></div>
      <div class="process-step">
        <div class="step-circle">01</div>
        <div class="process-step-label">Step 01</div>
        <h3>Discovery audit</h3>
        <p>Free 45-min deep dive. We review your funnel, spend, and competitive landscape.</p>
      </div>
      …
    </div>
  </div>
</section>
```

```css
.process { background: var(--navy); color: var(--ivory); padding: 140px 0; position: relative; overflow: hidden; }
.process::before, .process::after { /* gold radial gradients, 0.08 + 0.05 opacity */ }
.process .section-header h2 { color: var(--ivory); }
.process-steps { display: grid; grid-template-columns: repeat(4, 1fr); gap: 32px; position: relative; margin-top: 20px; }
.process-line { position: absolute; top: 24px; left: 12%; right: 12%; height: 1px; background: rgba(201,169,110,0.3); }
.process-step { position: relative; z-index: 2; }
.step-circle { width: 48px; height: 48px; border-radius: 50%; background: var(--navy); border: 1px solid var(--gold); display: flex; align-items: center; justify-content: center; font-family: var(--serif); font-size: 18px; color: var(--gold); margin-bottom: 28px; }
.process-step-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.15em; color: var(--gold); margin-bottom: 8px; }
.process-step h3 { font-family: var(--sans); font-size: 18px; font-weight: 500; color: var(--ivory); margin-bottom: 8px; }
.process-step p  { font-size: 14px; color: rgba(250,249,246,0.6); line-height: 1.5; }
```

Exactly four steps: Discovery audit → Growth blueprint → Launch & iterate → Scale.

### 5.11 Testimonial

```html
<section class="testimonial">
  <div class="container">
    <span class="eyebrow">One client's words</span>
    <blockquote class="testimonial-quote">"…acted like a partner instead of a <span class="italic-accent">vendor</span>…"</blockquote>
    <div class="testimonial-author">
      <div class="author-avatar">SM</div>
      <div class="author-info">
        <div class="author-name">Sarah Matsuda</div>
        <div class="author-title">Founder & CEO, Arden & Oak</div>
      </div>
    </div>
  </div>
</section>
```

```css
.testimonial { padding: 140px 0; text-align: center; }
.testimonial-quote { font-family: var(--serif); font-size: 42px; line-height: 1.2; letter-spacing: -0.02em; max-width: 900px; margin: 0 auto 40px; font-weight: 400; }
.testimonial-author { display: flex; align-items: center; justify-content: center; gap: 14px; margin-top: 32px; }
.author-avatar { width: 44px; height: 44px; border-radius: 50%; background: linear-gradient(135deg, #D4A574 0%, #8B5A3C 100%); display: flex; align-items: center; justify-content: center; color: white; font-family: var(--serif); font-size: 16px; }
.author-info { text-align: left; }
.author-name { font-size: 15px; font-weight: 500; color: var(--text-primary); }
.author-title { font-size: 13px; color: var(--text-secondary); }
```

Avatar uses a warm gradient — this is the ONE place a gradient appears in UI (not counting case-card placeholders, which are also placeholders for photography). When real client photos arrive, swap avatar for `background-image`.

### 5.12 Final CTA card

```html
<section class="final-cta">
  <div class="container">
    <div class="cta-card">
      <div class="cta-inner">
        <span class="eyebrow on-dark">Free · no-obligation</span>
        <h2>Ready to grow the <span class="italic-accent">right</span> way?</h2>
        <p>Book a 45-minute audit with our growth team. We'll show you exactly where revenue is leaking — and what to do about it.</p>
        <div class="cta-buttons">
          <a href="#" class="btn btn-cta-primary">Claim your free audit <span class="arrow">→</span></a>
          <a href="#" class="btn btn-outline-light">See pricing</a>
        </div>
      </div>
    </div>
  </div>
</section>
```

```css
.final-cta { padding: 80px 0 140px; }
.cta-card { background: var(--navy); color: var(--ivory); border-radius: 24px; padding: 80px 72px; position: relative; overflow: hidden; }
.cta-card::before { /* gold radial 0.12, top-right */ }
.cta-card::after  { /* gold radial 0.08, bottom-right */ }
.cta-inner { position: relative; z-index: 2; max-width: 620px; }
.cta-inner h2 { color: var(--ivory); font-size: 60px; margin: 20px 0 24px; }
.cta-inner p  { color: rgba(250,249,246,0.7); font-size: 17px; margin-bottom: 40px; max-width: 480px; line-height: 1.5; }
.cta-buttons  { display: flex; gap: 16px; }
```

---

## 6. Section composition

Section padding `140px 0` is the default. `.final-cta` uses `80px 0 140px` (tight top). `.hero` uses `100px 0 140px`.

Alternating section backgrounds (ivory → gray-surface → ivory → …) create rhythm. `.alt` class flips a section to `--gray-surface`. Process and footer are navy. This is the full palette rotation — no other section colors are introduced.

---

## 7. Implementation notes

- **Fraunces** ships with an optical-size axis (`opsz 9..144`). The Google Fonts URL above loads the variable axis; browsers pick the right optical size automatically. Do not hardcode `font-variation-settings` unless a specific typographic tweak requires it.
- **Italic accent** uses Fraunces's italic style (ital 1). This is the reason Fraunces was chosen over Instrument Serif — its italic is more distinct and the opsz axis tunes well to large display sizes.
- **Chart color contrast**: `#2563EB` (WCAG AA against ivory), `#10B981` (AA large), `#EF4444` (AA). If used on navy, verify contrast — typically OK for the sparkline stroke but not small labels.
- **Focus-visible** on all interactive elements: `outline: 2px solid var(--gold); outline-offset: 2px; border-radius: 4px;` — never rely on color alone.
- **Motion**: only two motion patterns ship today — `pulse` on the live-dot (2s infinite) and `transform: translateY(-2px/-3px)` on card hover (250–300ms). Don't introduce more without a reason.
