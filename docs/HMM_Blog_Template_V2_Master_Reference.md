# HMM Blog Template V2 — Master Reference

**Version:** 2.0 (D-hybrid sticky TOC sidebar)
**First shipped:** Commit `2430e84`, May 5 2026, on `/blog/healthcare-marketing-channels`
**Purpose:** Single source of truth for writing new blogs and retrofitting existing ones to V2 architecture.

---

## How to use this document

Upload to any Claude conversation when starting a new blog or optimizing an existing one. Claude follows everything in this document.

When you ask for a blog, Claude must:
1. Confirm the brief (Part 1, Section A)
2. Use V2 architecture (Parts 2-5)
3. Follow voice rules (Part 1, Section B)
4. Apply the 6-element rule per H2 section (Part 1, Section C)
5. Hit minimum internal link floor (Part 2, Section D)
6. Generate a hero image using the spec template (Part 6)
7. Brief Claude Code with checkpoint discipline (Part 7)

If anything in a specific request conflicts with this document, ask before deviating.

---

# PART 1 — CONTENT & VOICE

## Section A — Confirm-before-writing checklist

Every blog request must clarify these five things before drafting starts. If any are missing or vague, Claude asks before proceeding:

| Question | Why it matters |
|---|---|
| **Topic & angle** | Determines the unique frame vs. generic coverage |
| **Target keyword OR core question** | Drives SEO structure and headings |
| **Audience** | Sets register, technical depth, examples |
| **Goal / CTA** | Determines what the conclusion drives toward |
| **Length** | Defaults to 2,150-2,550 words; flag if shorter/longer |

A 30-second clarifying question saves a full rewrite. Don't guess.

## Section B — Voice rules

### Core voice principles

- **Clear over clever.** Plain language. If a sentence needs three reads, rewrite it.
- **Conversational but credible.** Like explaining to a smart friend over coffee, not like a textbook.
- **Second person.** Use "you" for the reader, "we" for HMM. Never third person.
- **Opinionated where it counts.** Hedged, everyone-agrees content is wallpaper.
- **Canadian spelling by default.** Pick one per post and stay consistent.
- **Sentence-case headings.** Always. Never Title Case in H1, H2, H3, or H4.

### Tone register

Pick one based on topic and audience. State which one before drafting:

| Register | When to use |
|---|---|
| **Conversational & approachable** | Beginner topics, "how to" posts, small business readers |
| **Professional but warm** | Default. Strategic topics, marketing managers. |
| **Authoritative & expert** | Technical SEO, advanced ads, in-depth audits |
| **Punchy & opinionated** | Contrarian takes, industry commentary. Max 1 per month. |

### Banned phrases — never use

These are dead giveaways of AI-generated copy:

| Don't write | Write instead |
|---|---|
| leverage, utilize, utilise | use |
| empower, unlock, supercharge | help / make easier |
| crucial, pivotal, paramount | important / matters |
| a myriad of, a plethora of | many / most |
| it's widely known, experts agree | we think / in our experience |
| in today's fast-paced world, in the digital age | today / these days |
| it's no secret that, needless to say | (skip the intro phrase entirely) |
| delving into, navigating the landscape of | (start with the point) |
| game-changing, revolutionary, cutting-edge | (show, don't tell) |
| seamlessly, effortlessly, holistic | (say what you mean) |

### "Premium" rule

"Premium" is banned as a marketing adjective. It IS allowed as a noun (e.g., "premium content syndication" referring to a content distribution category, or "LinkedIn charges a premium" meaning higher cost). Self-check: would removing the word change the meaning? If no, it's the banned adjective use.

## Section C — The 6-element rule

Every major H2 section must include all six of these. If a section is missing three or more, it's fluff — rewrite it.

| # | Element | Means |
|---|---|---|
| 1 | **Explanation** | Clear, jargon-free definition. Answer: what is this thing? |
| 2 | **Example** | Concrete, real-world illustration. Use a Canadian/Ontario example where possible. |
| 3 | **Framework** | Repeatable model, checklist, or step-by-step. Name it if you can. |
| 4 | **Stats / Data** | At least one cited number, recent (past 2 years), relevant to audience |
| 5 | **Mistakes to avoid** | 1-3 specific pitfalls. Pull from real client work where possible. |
| 6 | **Action steps** | What the reader does next. Specific, bounded, doable within a week. |

### Self-audit before delivery

After drafting, run this check on each H2 section. Flag any missing elements with proposed fixes. Don't deliver a draft that hasn't been audited.

## Section D — Length and structure

### Word count targets

| Type | Target | Notes |
|---|---|---|
| **Standard blog** | 2,150-2,550 words (body) | Default. Most pieces hit this range. |
| **Short-form** | 1,200-1,500 words | For specific tactical posts only |
| **Long-form pillar** | 3,000-4,000 words | Anchor content for major topics |

### Required structural elements (in order)

1. **H1 title** — under 60 characters, includes primary keyword, benefit-led
2. **Subtitle / deck** — one-sentence summary of the takeaway
3. **Author block** — Avatar (initials) + name + title + date + read time
4. **Hero image** — 16:9, 2K resolution, brand-aligned (see Part 6)
5. **Key Takeaways box** — 3-4 bulleted takeaways, scanners get value in 10 seconds
6. **H2 sections** — each meeting the 6-element rule, with anchor IDs
7. **Featured visuals where appropriate** — diagrams inline, tables in featured cards
8. **Featured conclusion card** — for articles that need a clear takeaway moment
9. **FAQ section** — 3-5 questions from "People Also Ask," 40-60 words per answer
10. **Final CTA** — primary + optional secondary button
11. **Related reading** — 3 contextually relevant blog cards
12. **Author bio** — see standard text below

### Standard author bio (verbatim)

```
Founder of HelpMeMarketing. 9+ years building performance marketing programs for DTC, SaaS, healthcare, and finance brands. Writes about channel selection, attribution, and the unit economics of paid acquisition.
```

Use this verbatim until updated. When the bio changes, propagate sitewide via a single sweep commit.

---

# PART 2 — STRUCTURE & SEO

## Section A — HTML document structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Meta -->
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Title under 60 chars] | HelpMeMarketing</title>
  <meta name="description" content="[150-160 chars]">
  <link rel="canonical" href="https://helpmemarketing.com/blog/[slug]">
  
  <!-- OG / Twitter -->
  <meta property="og:type" content="article">
  <meta property="og:title" content="[Title]">
  <meta property="og:description" content="[Same as meta description]">
  <meta property="og:image" content="https://helpmemarketing.com/blog/images/[slug]-hero.png">
  <meta property="og:url" content="https://helpmemarketing.com/blog/[slug]">
  <meta property="article:published_time" content="[YYYY-MM-DD]">
  <meta property="article:author" content="Ankit Kumar">
  <meta property="article:section" content="[Category]">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="[Title]">
  <meta name="twitter:description" content="[Same as meta description]">
  <meta name="twitter:image" content="https://helpmemarketing.com/blog/images/[slug]-hero.png">
  
  <!-- Schema (4 blocks: see Section B) -->
  <script type="application/ld+json">{...BlogPosting...}</script>
  <script type="application/ld+json">{...FAQPage...}</script>
  <script type="application/ld+json">{...BreadcrumbList...}</script>
  <script type="application/ld+json">{...HowTo if applicable...}</script>
  
  <!-- Styles -->
  <link rel="stylesheet" href="/styles.css">
  
  <!-- Optional: voice rules HTML comment block embedded in head -->
  <!--
    [Voice rules from this template embedded for reference]
  -->
</head>
<body>
  <nav>...</nav>
  
  <div class="blog-body">
    <article class="blog-content">
      <header class="blog-hero">...</header>
      <div class="takeaways">...</div>
      <div class="toc-mobile">...</div>  <!-- visible <900px -->
      <h2 id="...">...</h2>
      <!-- All H2 sections, FAQ, related, author bio -->
    </article>
    
    <aside class="blog-sidebar">
      <div class="toc-card">...</div>
      <div class="sidebar-cta">...</div>
    </aside>
  </div>
  
  <footer>...</footer>
  
  <!-- JS -->
  <script src="/blog/blog-template.js" defer></script>
  <script>...mobile menu toggle...</script>
</body>
</html>
```

## Section B — Required schema blocks

Every blog needs these 4 schema blocks (HowTo only when applicable):

### Block 1 — BlogPosting

```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "[Article H1]",
  "description": "[Meta description, same as <meta name='description'>]",
  "image": "https://helpmemarketing.com/blog/images/[slug]-hero.png",
  "datePublished": "[YYYY-MM-DD]",
  "dateModified": "[YYYY-MM-DD]",
  "author": {
    "@type": "Person",
    "name": "Ankit Kumar",
    "jobTitle": "Founder",
    "worksFor": {
      "@type": "Organization",
      "name": "HelpMeMarketing",
      "url": "https://helpmemarketing.com"
    },
    "url": "https://helpmemarketing.com/about"
  },
  "publisher": {
    "@type": "Organization",
    "name": "HelpMeMarketing",
    "logo": {
      "@type": "ImageObject",
      "url": "https://helpmemarketing.com/logo.png"
    }
  },
  "keywords": ["primary keyword", "semantic 1", "semantic 2", "semantic 3", "semantic 4", "semantic 5", "semantic 6"],
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://helpmemarketing.com/blog/[slug]"
  }
}
```

**Convention:** 7 keywords (1 primary + 6 semantic). Existing blogs may have 5; new blogs use 7.

### Block 2 — FAQPage

Mirror visible HTML verbatim, char-for-char:

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "[Question text exactly as shown]",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Answer text exactly as shown, no HTML]"
      }
    }
    // 3-5 questions total
  ]
}
```

### Block 3 — BreadcrumbList (4 levels)

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://helpmemarketing.com/"},
    {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://helpmemarketing.com/blog"},
    {"@type": "ListItem", "position": 3, "name": "[Category Name]", "item": "https://helpmemarketing.com/blog"},
    {"@type": "ListItem", "position": 4, "name": "[Article Title]", "item": "https://helpmemarketing.com/blog/[slug]"}
  ]
}
```

### Block 4 — HowTo (when article includes a step-by-step)

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "[How to do X in Y minutes]",
  "totalTime": "PT[N]M",
  "step": [
    {
      "@type": "HowToStep",
      "position": 1,
      "name": "[Step title]",
      "text": "[Step description, plain text, no inline links]"
    }
    // Match the actual steps in the article
  ]
}
```

## Section C — Required meta tags

Use this exact pattern (substitute the article-specific values):

```html
<title>[Title under 60 chars] | HelpMeMarketing</title>
<meta name="description" content="[150-160 chars, ends with click reason]">
<link rel="canonical" href="https://helpmemarketing.com/blog/[slug]">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
```

OG and Twitter blocks identical to Section A.

## Section D — Internal linking strategy

Every blog is also a conversion asset. Internal links move readers toward services, proof, and contact.

| Link type | Purpose | How to use |
|---|---|---|
| Related blog posts | Deepen topical authority | 2-3 per post, contextually relevant |
| Service pages | Connect content to what HMM sells | 1-2 per post |
| Industry pages | Vertical-specific authority | 1 per post if relevant vertical |
| Case studies | Social proof for claims | Where relevant |
| Contact / book a call | Main conversion point | Always in CTA section |

### Floor — minimum links per post

- **6+ internal links** for posts 1,500+ words
- **4+ internal links** for shorter posts
- **Anchor text** descriptive — "our local SEO audit process" not "click here"

### Standard slot positions

| Position | Pattern |
|---|---|
| End of H2 #1 | Italic "Related: [link]" line |
| End of H2 #2 | Italic ad-calculator or service callout |
| End of H2 #3 | Italic "Related services: link 1 · link 2 · link 3" |
| Within H2 #4 (specialty/data) | Italic link to industry/vertical page |
| Within H2 #6 (action exercise) | Inline link to ad-calculator or relevant tool |
| Final CTA | Primary button to /contact, secondary to relevant page |

## Section E — Anchor IDs

Every H2 needs an `id` attribute. Use kebab-case, descriptive, short:

```html
<h2 id="why-generic-fails">Why generic healthcare marketing advice fails</h2>
<h2 id="four-variables">The 4 Channel-Fit Variables</h2>
<h2 id="channel-by-channel">Channel-by-channel: where each one wins</h2>
<h2 id="specialty-recommendations">Specialty-by-specialty channel recommendations</h2>
<h2 id="common-mistakes">The 3 most common channel-mix mistakes</h2>
<h2 id="decision-exercise">How to actually pick: a 30-minute decision exercise</h2>
```

Plus standard sections:
- `id="faq"` on FAQ wrapper
- `id="cta"` on related-and-cta wrapper

These IDs feed the auto-generated TOC. Don't skip.

---

# PART 3 — V2 VISUAL TEMPLATE

## Section A — Layout architecture

Two-column grid with sticky right sidebar:

```
┌──────────────────────────────────────────────────────────────┐
│  NAV (sitewide)                                               │
└──────────────────────────────────────────────────────────────┘
┌────────────────────────────────────┬─────────────────────────┐
│                                    │                         │
│  ARTICLE CONTENT (max-width 760px) │   STICKY SIDEBAR (280px)│
│                                    │                         │
│  - Breadcrumb                       │   - TOC card            │
│  - Hero zone                       │     - Contents header   │
│  - Key Takeaways                   │     - Share icons       │
│  - H2 sections                     │     - Auto-gen TOC list │
│  - Featured table card             │                         │
│  - Featured conclusion card        │   - Sidebar CTA card    │
│  - FAQ                             │     - Eyebrow           │
│  - Related reading                 │     - Title             │
│  - Final CTA                       │     - Bullet list       │
│  - Author bio                      │     - Primary button    │
│                                    │     - Subnote           │
└────────────────────────────────────┴─────────────────────────┘
┌──────────────────────────────────────────────────────────────┐
│  FOOTER (sitewide)                                            │
└──────────────────────────────────────────────────────────────┘
```

At <900px viewport, sidebar hides; replaced with collapsible "Jump to section" button below Key Takeaways.

## Section B — HTML skeleton (full template)

```html
<div class="blog-body">

  <article class="blog-content">

    <!-- HERO ZONE -->
    <header class="blog-hero">
      <div class="breadcrumb">
        <a href="/">Home</a>
        <span class="sep">›</span>
        <a href="/blog">Blog</a>
        <span class="sep">›</span>
        <a href="/blog">[Category]</a>
        <span class="sep">›</span>
        [Article title shortened]
      </div>

      <div class="category-tags">
        [Category 1]
        <span class="sep">|</span>
        [Category 2]
        <span class="sep">|</span>
        [Category 3]
      </div>

      <div class="hero-zone">
        <div class="hero-text">
          <h1 class="post-title">
            [Article title with single accent word in <em class="italic-accent">italic gold</em>]
          </h1>
          <p class="post-subtitle">[One-sentence subtitle, what reader walks away with]</p>
          <div class="author-block">
            <div class="avatar">AK</div>
            <div class="author-info">
              <div class="author-name">Ankit Kumar</div>
              <div class="author-title">Founder, HelpMeMarketing</div>
            </div>
            <div class="meta-icons">
              <span>[Date in "Mon DD, YYYY" format]</span>
              <span>[N min read]</span>
            </div>
          </div>
        </div>

        <div class="hero-illustration hero-illustration--image">
          <img src="/blog/images/[slug]-hero.png"
               alt="[Descriptive alt text matching the image concept]"
               width="3000" height="1688">
        </div>
      </div>
    </header>

    <!-- KEY TAKEAWAYS -->
    <div class="takeaways">
      <h3>Key Takeaways</h3>
      <ul>
        <li>[Takeaway 1 — single biggest point]</li>
        <li>[Takeaway 2 — specific tactic or insight]</li>
        <li>[Takeaway 3 — number, stat, or concrete example]</li>
        <li>[Takeaway 4 — optional, if there's a clear 4th]</li>
      </ul>
    </div>

    <!-- MOBILE TOC (hidden >900px) -->
    <div class="toc-mobile">
      <button class="toc-mobile-toggle" aria-expanded="false" aria-controls="toc-mobile-panel">
        <span>Jump to section</span>
        <span class="toc-mobile-chevron">▼</span>
      </button>
      <div class="toc-mobile-panel" id="toc-mobile-panel">
        <ul class="toc-list-mobile"><!-- Auto-generated by JS --></ul>
      </div>
    </div>

    <!-- H2 SECTIONS — each must follow 6-element rule -->
    <h2 id="[anchor-1]">[H2 #1]</h2>
    <p>[Body prose]</p>
    <p><strong>[Bold inline emphasis where appropriate.]</strong> [More body prose]</p>
    <blockquote class="pull-quote">"[Quoted statement, ~120-150 chars max]"</blockquote>
    <p>[Continue prose]</p>
    <p><em>Related: <a href="[URL]">[Anchor text]</a></em></p>

    <h2 id="[anchor-2]">[H2 #2 — framework section]</h2>
    <p>[Body prose introducing the framework]</p>
    <p><strong>[Variable 1.]</strong> [Description]</p>
    <p><strong>[Variable 2.]</strong> [Description]</p>
    <p><strong>[Variable 3.]</strong> [Description]</p>
    <p><strong>[Variable 4.]</strong> [Description]</p>
    <p><em>Want to pressure-test? Use our <a href="/ad-calculator">ad-spend calculator</a>.</em></p>
    
    <!-- Inline framework diagram (if applicable) -->
    <div class="framework-diagram">
      <!-- Diagram HTML structure varies; centered, max-width 560px -->
    </div>

    <!-- Standard data-table H2 with featured card wrap -->
    <h2 id="[anchor-3]">[H2 with table — e.g., "Specialty recommendations"]</h2>
    <p>[Lead paragraph introducing the table]</p>
    
    <div class="featured-table-card">
      <table class="comparison-table">
        <thead><tr><th>...</th></tr></thead>
        <tbody><tr><td>...</td></tr></tbody>
      </table>
      <p class="table-source">Source: HelpMeMarketing client data, [Year range]. [Caveat about assumptions.]</p>
    </div>
    
    <p>[Closing prose]</p>
    <p><em>Related: <a>...</a></em></p>

    <!-- More H2s following 6-element rule -->
    
    <!-- Featured conclusion card (for prescriptive articles) -->
    <div class="featured-conclusion-card">
      <h3>The honest answer</h3>
      <p>[2-3 paragraphs landing the core argument]</p>
      <div class="conclusion-emphasis">[Single-line punch summary]</div>
    </div>

    <!-- FAQ -->
    <section class="blog-faq" id="faq">
      <h2>Frequently asked questions</h2>
      <details class="faq-item">
        <summary class="faq-question">[Question 1]</summary>
        <div class="faq-answer"><p>[40-60 word answer]</p></div>
      </details>
      <!-- 3-5 total -->
    </section>

    <!-- Final CTA -->
    <div class="related-and-cta" id="cta">
      <div class="final-cta">
        <h3>[CTA headline tying to article topic]</h3>
        <p>[CTA subhead]</p>
        <div class="cta-buttons">
          <a href="/contact" class="btn-primary">Start a conversation →</a>
          <a href="[secondary-url]" class="btn-secondary">[Secondary CTA] →</a>
        </div>
      </div>
    </div>

    <!-- Related reading -->
    <div class="related-reading">
      <h3>Related reading</h3>
      <div class="related-grid">
        <a href="/blog/[slug-1]" class="related-card">...</a>
        <a href="/blog/[slug-2]" class="related-card">...</a>
        <a href="/blog/[slug-3]" class="related-card">...</a>
      </div>
    </div>

    <!-- Author bio -->
    <div class="author-bio">
      <div class="bio-avatar">AK</div>
      <div class="bio-text">
        <h4>Ankit Kumar</h4>
        <p>[Standard bio from Part 1 Section D]</p>
      </div>
    </div>

  </article>

  <!-- STICKY SIDEBAR -->
  <aside class="blog-sidebar">

    <!-- TOC card -->
    <div class="toc-card">
      <div class="toc-header">
        <span class="toc-title">Contents</span>
        <div class="toc-share">
          <a href="#" class="share-icon" data-network="linkedin" aria-label="Share on LinkedIn">in</a>
          <a href="#" class="share-icon" data-network="x" aria-label="Share on X">𝕏</a>
          <a href="#" class="share-icon" data-network="facebook" aria-label="Share on Facebook">f</a>
          <a href="#" class="share-icon" data-network="copy" aria-label="Copy link">⎘</a>
        </div>
      </div>
      <ul class="toc-list" role="navigation" aria-label="Article contents">
        <!-- Auto-generated by JS -->
      </ul>
    </div>

    <!-- Sidebar CTA -->
    <div class="sidebar-cta">
      <div class="cta-eyebrow">Free · 30 min</div>
      <h4 class="cta-title">[CTA title — verb-driven, action-oriented]</h4>
      <ul class="cta-list">
        <li>[Outcome 1 — specific to article topic]</li>
        <li>[Outcome 2 — specific to article topic]</li>
        <li>[Outcome 3 — generic e.g., "30-min call, no pitch"]</li>
      </ul>
      <a href="/contact" class="cta-button">Start a conversation →</a>
      <div class="cta-subnote">No pressure. No follow-up sequence.</div>
    </div>

  </aside>

</div>
```

---

# PART 4 — CSS SPECS

All blog template CSS lives in `styles.css` under the `BLOG TEMPLATE V2 — D-HYBRID LAYOUT` section header. New blogs reference these classes; no per-blog inline duplication.

## Section A — Brand tokens (defined in :root)

```css
:root {
  --navy: #0A1628;
  --gold: #C9A96E;
  --ivory: #FAF9F6;
  --border: #E8E4DC;
  --text-primary: #1A1A1A;
  --text-secondary: #555;
  --text-tertiary: #888;
  --text-muted: #666;
}
```

Use `var(--navy)`, `var(--gold)`, etc. throughout. Don't hardcode hex values for these.

## Section B — Layout grid

```css
.blog-body {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 48px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px 80px;
}

.blog-content {
  min-width: 0;
  max-width: 760px;
}

.blog-sidebar {
  position: sticky;
  top: 80px;
  align-self: start;
  height: fit-content;
}
```

## Section C — Typography

```css
.blog-content h2 {
  font-size: 22px;
  font-weight: 500;
  color: var(--navy);
  line-height: 1.25;
  letter-spacing: -0.01em;
  margin: 40px 0 16px;
  position: relative;
}

.blog-content h2::before {
  content: "";
  display: block;
  width: 32px;
  height: 2px;
  background: var(--gold);
  margin-bottom: 16px;
}

.blog-content h2 em {
  font-style: italic;
  color: var(--gold);
}

.blog-content h2[id] {
  scroll-margin-top: 100px;
}

.blog-content p {
  margin: 0 0 14px;
  font-size: 15px;
  line-height: 1.7;
  color: var(--text-primary);
}

.blog-content p strong {
  color: var(--navy);
  font-weight: 500;
}

.post-title {
  font-size: clamp(28px, 4vw, 44px);
  font-weight: 800;
  line-height: 1.15;
  color: var(--navy);
  letter-spacing: -0.02em;
  margin: 0 0 14px;
}

.post-title em.italic-accent {
  font-style: italic;
  color: var(--gold);
  font-weight: 800;
}

.post-subtitle {
  font-size: 17px;
  color: var(--text-secondary);
  line-height: 1.55;
  margin: 0 0 18px;
}
```

## Section D — Pull quote (featured)

```css
.blog-content .pull-quote,
.blog-content blockquote.pull-quote {
  margin: 24px 0;
  padding: 18px 24px;
  border-left: 3px solid var(--gold);
  background: rgba(201, 169, 110, 0.06);
  font-family: Georgia, 'Times New Roman', serif;
  font-style: italic;
  font-size: 15px;
  line-height: 1.5;
  color: var(--navy);
  border-radius: 0;
}

.blog-content .pull-quote::before,
.blog-content .pull-quote::after,
.blog-content blockquote.pull-quote::before,
.blog-content blockquote.pull-quote::after {
  content: none;
}
```

## Section E — Featured cards

```css
.blog-content .featured-table-card {
  background: #fff;
  border: 0.5px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  margin: 32px 0;
  box-shadow: 0 1px 3px rgba(10, 22, 40, 0.04);
}

.blog-content .featured-table-card .table-source {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 0.5px solid var(--border);
  font-size: 11px;
  font-style: italic;
  color: var(--text-tertiary);
}

.blog-content .featured-conclusion-card {
  background: #fff;
  border: 0.5px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  margin: 32px 0;
  box-shadow: 0 1px 3px rgba(10, 22, 40, 0.04);
}

.blog-content .featured-conclusion-card .conclusion-emphasis {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  font-size: 14px;
  font-weight: 500;
  color: var(--navy);
  padding-top: 14px;
  margin-top: 4px;
  border-top: 0.5px solid var(--border);
}

.blog-content .featured-conclusion-card .conclusion-emphasis::before {
  content: "★";
  color: var(--gold);
  font-size: 14px;
  flex-shrink: 0;
  line-height: 1.5;
}
```

## Section F — TOC sidebar

```css
.toc-card {
  background: #fff;
  border: 0.5px solid var(--border);
  border-radius: 10px;
  padding: 18px;
  margin-bottom: 14px;
}

.toc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  padding-bottom: 12px;
  border-bottom: 0.5px solid #eee;
}

.toc-title {
  font-size: 11px;
  font-weight: 500;
  color: var(--navy);
  text-transform: uppercase;
  letter-spacing: 1.2px;
}

.toc-share {
  display: flex;
  gap: 6px;
}

.share-icon {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  cursor: pointer;
  background: var(--ivory);
  border: 0.5px solid var(--border);
  color: var(--text-muted);
  transition: all 0.15s ease;
  text-decoration: none;
  position: relative;
}

.share-icon:hover {
  background: var(--gold);
  color: var(--navy);
  border-color: var(--gold);
}

.share-icon-tooltip {
  position: absolute;
  top: -28px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--navy);
  color: var(--ivory);
  font-size: 10px;
  padding: 3px 8px;
  border-radius: 4px;
  white-space: nowrap;
  pointer-events: none;
}

.toc-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.toc-item {
  padding: 6px 0 6px 16px;
  font-size: 12px;
  line-height: 1.45;
  cursor: pointer;
  color: var(--text-muted);
  position: relative;
  transition: color 0.15s ease;
}

.toc-item::before {
  content: "";
  position: absolute;
  left: 0;
  top: 11px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--gold);
  opacity: 0.5;
  transition: all 0.15s ease;
}

.toc-item:hover {
  color: var(--navy);
}

.toc-item:hover::before {
  opacity: 1;
}

.toc-item.active {
  color: var(--navy);
  font-weight: 500;
}

.toc-item.active::before {
  opacity: 1;
  width: 8px;
  height: 8px;
  top: 10px;
  background: var(--gold);
  box-shadow: 0 0 0 3px rgba(201, 169, 110, 0.2);
}

.toc-item:focus-visible {
  outline: 2px solid var(--gold);
  outline-offset: 2px;
}
```

## Section G — Sidebar CTA

```css
.sidebar-cta {
  background: var(--navy);
  color: var(--ivory);
  border-radius: 10px;
  padding: 18px;
  position: relative;
}

.cta-eyebrow {
  font-size: 9px;
  font-weight: 500;
  color: var(--gold);
  text-transform: uppercase;
  letter-spacing: 1.5px;
  margin-bottom: 6px;
}

.sidebar-cta .cta-title {
  font-size: 14px;
  font-weight: 500;
  margin: 0 0 10px;
  line-height: 1.3;
  color: var(--ivory);
}

.sidebar-cta .cta-list {
  list-style: none;
  padding: 0;
  margin: 0 0 14px;
}

.sidebar-cta .cta-list li {
  padding: 4px 0 4px 18px;
  position: relative;
  font-size: 11px;
  line-height: 1.45;
  color: var(--ivory);
  opacity: 0.85;
}

.sidebar-cta .cta-list li::before {
  content: "✓";
  position: absolute;
  left: 0;
  top: 3px;
  color: var(--gold);
  font-size: 10px;
  font-weight: 600;
}

.sidebar-cta .cta-button {
  display: block;
  width: 100%;
  padding: 9px 12px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
  text-align: center;
  cursor: pointer;
  border: none;
  background: var(--gold);
  color: var(--navy);
  text-decoration: none;
  transition: background 0.15s ease;
  box-sizing: border-box;
}

.sidebar-cta .cta-button:hover {
  background: #D4B57A;
}

.sidebar-cta .cta-subnote {
  font-size: 9px;
  color: var(--ivory);
  opacity: 0.55;
  text-align: center;
  margin-top: 8px;
  font-style: italic;
}
```

## Section H — Mobile TOC

```css
.toc-mobile {
  display: none;
  margin: 16px 0 24px;
}

.toc-mobile-toggle {
  width: 100%;
  background: var(--ivory);
  border: 0.5px solid var(--border);
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 13px;
  font-weight: 500;
  color: var(--navy);
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.toc-mobile-toggle.open .toc-mobile-chevron {
  transform: rotate(180deg);
}

.toc-mobile-chevron {
  transition: transform 0.2s ease;
  font-size: 10px;
  color: var(--gold);
}

.toc-mobile-panel {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
}

.toc-mobile-panel.open {
  max-height: 600px;
  padding-top: 8px;
}

.toc-list-mobile {
  list-style: none;
  padding: 0;
  margin: 0;
  background: #fff;
  border: 0.5px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}

.toc-list-mobile li {
  padding: 12px 16px;
  border-bottom: 0.5px solid var(--border);
  font-size: 13px;
  color: var(--text-muted);
  cursor: pointer;
}

.toc-list-mobile li:last-child {
  border-bottom: none;
}

.toc-list-mobile li:hover {
  background: var(--ivory);
  color: var(--navy);
}
```

## Section I — Mobile breakpoint

```css
@media (max-width: 900px) {
  .blog-body {
    grid-template-columns: 1fr;
    gap: 0;
    padding: 24px 16px 64px;
  }
  
  .blog-sidebar {
    display: none;
  }
  
  .toc-mobile {
    display: block;
  }
  
  .blog-content {
    max-width: 100%;
  }
  
  .hero-zone {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}
```

## Section J — Hero zone

```css
.hero-zone {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 56px;
  align-items: center;
  margin-bottom: 32px;
}

.hero-illustration--image {
  padding: 0;
  background: transparent;
  min-height: 0;
  overflow: hidden;
}

.hero-illustration--image img {
  width: 100%;
  height: auto;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  display: block;
  border-radius: 16px;
}

.author-block {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--text-muted);
  flex-wrap: wrap;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--navy);
  color: var(--ivory);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 500;
  flex-shrink: 0;
}

.author-info .author-name {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 13px;
}

.author-info .author-title {
  font-size: 11px;
  color: var(--text-tertiary);
}

.meta-icons {
  display: flex;
  gap: 16px;
  margin-left: auto;
  font-size: 11px;
  color: var(--text-tertiary);
}
```

---

# PART 5 — JAVASCRIPT TEMPLATE

External file: `/blog/blog-template.js` (single source of truth across all blogs).

Reference from blog HTML:

```html
<script src="/blog/blog-template.js" defer></script>
```

## Full JS file content

```javascript
/* HelpMeMarketing — Blog Template V2 (D-hybrid)
 * Auto-generates TOC, drives active-section highlighting via
 * IntersectionObserver, handles mobile collapsible TOC, and wires
 * up share-icon click handlers. Single source of truth for all
 * blog pages using the V2 template.
 */
(function () {
  'use strict';

  function init() {
    var headings = document.querySelectorAll('.blog-content h2[id]');
    if (headings.length === 0) return;

    var tocList = document.querySelector('.toc-list');
    var tocListMobile = document.querySelector('.toc-list-mobile');

    // Build desktop TOC
    if (tocList) {
      headings.forEach(function (h) {
        var li = document.createElement('li');
        li.className = 'toc-item';
        li.dataset.target = h.id;
        li.textContent = h.textContent;
        li.setAttribute('role', 'link');
        li.setAttribute('tabindex', '0');
        li.addEventListener('click', function () { scrollToHeading(h.id); });
        li.addEventListener('keydown', function (e) {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            scrollToHeading(h.id);
          }
        });
        tocList.appendChild(li);
      });
    }

    // Build mobile TOC (mirror)
    if (tocListMobile) {
      headings.forEach(function (h) {
        var li = document.createElement('li');
        li.dataset.target = h.id;
        li.textContent = h.textContent;
        li.setAttribute('role', 'link');
        li.setAttribute('tabindex', '0');
        li.addEventListener('click', function () {
          scrollToHeading(h.id);
          closeMobilePanel();
        });
        li.addEventListener('keydown', function (e) {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            scrollToHeading(h.id);
            closeMobilePanel();
          }
        });
        tocListMobile.appendChild(li);
      });
    }

    function scrollToHeading(id) {
      var target = document.getElementById(id);
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function closeMobilePanel() {
      var panel = document.querySelector('.toc-mobile-panel');
      var toggle = document.querySelector('.toc-mobile-toggle');
      if (panel && toggle) {
        panel.classList.remove('open');
        toggle.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    }

    // Active section highlighting
    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              var id = entry.target.id;
              document.querySelectorAll('.toc-item').forEach(function (i) {
                i.classList.remove('active');
              });
              var activeItem = document.querySelector('.toc-item[data-target="' + id + '"]');
              if (activeItem) activeItem.classList.add('active');
            }
          });
        },
        { rootMargin: '-80px 0px -60% 0px', threshold: 0 }
      );
      headings.forEach(function (h) { observer.observe(h); });
    }

    // Mobile collapsible TOC toggle
    var mobileToggle = document.querySelector('.toc-mobile-toggle');
    var mobilePanel = document.querySelector('.toc-mobile-panel');
    if (mobileToggle && mobilePanel) {
      mobileToggle.addEventListener('click', function () {
        var isOpen = mobilePanel.classList.toggle('open');
        mobileToggle.classList.toggle('open', isOpen);
        mobileToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      });
    }

    // Share icon handlers
    var shareIcons = document.querySelectorAll('.share-icon[data-network]');
    shareIcons.forEach(function (icon) {
      icon.addEventListener('click', function (e) {
        e.preventDefault();
        var network = icon.dataset.network;
        var pageUrl = window.location.href;
        var pageTitle = document.title;
        var shareUrl = '';

        if (network === 'linkedin') {
          shareUrl = 'https://www.linkedin.com/sharing/share-offsite/?url=' + encodeURIComponent(pageUrl);
        } else if (network === 'x') {
          shareUrl = 'https://twitter.com/intent/tweet?url=' + encodeURIComponent(pageUrl) + '&text=' + encodeURIComponent(pageTitle);
        } else if (network === 'facebook') {
          shareUrl = 'https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(pageUrl);
        } else if (network === 'copy') {
          copyToClipboard(pageUrl, icon);
          return;
        }

        if (shareUrl) window.open(shareUrl, '_blank', 'noopener,noreferrer');
      });
    });

    function copyToClipboard(text, icon) {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(
          function () { showCopiedFeedback(icon); },
          function () { fallbackCopy(text, icon); }
        );
      } else {
        fallbackCopy(text, icon);
      }
    }

    function fallbackCopy(text, icon) {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      ta.setAttribute('readonly', '');
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); showCopiedFeedback(icon); } catch (e) { /* silent */ }
      document.body.removeChild(ta);
    }

    function showCopiedFeedback(icon) {
      var existing = icon.querySelector('.share-icon-tooltip');
      if (existing) icon.removeChild(existing);
      var tooltip = document.createElement('span');
      tooltip.className = 'share-icon-tooltip';
      tooltip.textContent = 'Copied!';
      icon.appendChild(tooltip);
      setTimeout(function () {
        if (tooltip.parentNode === icon) icon.removeChild(tooltip);
      }, 2000);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
```

This file is shared across all V2 blogs. Don't duplicate inline. Don't fork per-blog versions.

---

# PART 6 — IMAGE WORKFLOW

## Section A — Hero image specs

| Spec | Value |
|---|---|
| **Format** | PNG (compress to WebP in deferred follow-up if size matters) |
| **Aspect ratio** | 16:9 |
| **Resolution** | 2K (~3000×1688) |
| **Path** | `/blog/images/[slug]-hero.png` |
| **Style** | Brand-aligned: muted gold + ivory, editorial aesthetic, no medical/stock imagery |
| **Tool** | nano-banana-pro (Google Gemini 3 Pro Image) via Claude Code skill |

## Section B — JSON spec template

Use this template for every new blog hero. Fill the `subject.concept` field with the article-specific visual idea.

```json
{
  "_meta": {
    "blog_slug": "[slug]",
    "spec_version": "1.0",
    "based_on_template": "HMM_Blog_Hero_v1",
    "concept_summary": "[One-line description]"
  },

  "format": {
    "aspect_ratio": "16:9",
    "size": "2K",
    "output_format": "PNG",
    "intended_use": "blog post hero image"
  },

  "brand_tokens": {
    "navy_primary": "#0A1628",
    "gold_accent": "#C9A96E",
    "ivory_background": "#FAF9F6",
    "use_strategy": "Ivory dominates as primary surface. Muted gold is the only color used on the subject. Navy is not used in this image."
  },

  "composition": {
    "subject_placement": "left third of frame",
    "negative_space": "right two-thirds of frame deliberately empty",
    "depth": "shallow — single foreground subject plus surface, no busy backgrounds",
    "framing": "editorial — feels like a design magazine cover, not corporate stock"
  },

  "lighting": {
    "direction": "soft directional light from upper-left",
    "quality": "diffused, warm, slightly overcast — not harsh studio lighting",
    "shadows": "gentle warm-grey contact shadows beneath each paper element, not deep blacks",
    "mood": "calm, considered, hand-crafted feeling"
  },

  "surface": {
    "material": "warm ivory matte paper with fine subtle grain",
    "texture": "minimal — visible enough to feel tactile, not enough to compete with subject",
    "color_temperature": "warm, slightly off-white"
  },

  "aesthetic_anchors": {
    "primary_reference": "design magazine editorial — Kinfolk, Cereal Magazine, Monocle aesthetic",
    "avoid": "corporate stock photography, generic startup illustration, oversaturated colors, busy compositions, anything that reads as AI-generated",
    "execution": "photorealistic studio aesthetic with crafted hand-made feel"
  },

  "subject": {
    "concept": "[FILL IN: One paragraph describing the visual concept. Avoid 'branches' (reads as biological tree). Use 'ribbons', 'paths', 'distinct strands', 'parallel routes' for divergent metaphors.]",
    "concept_constraints": [
      "subject must be abstract — no medical imagery, no devices, no people, no buildings",
      "subject must feel physical/tactile — visible paper texture, hand-cut imperfections",
      "no rendered text in the image"
    ]
  },

  "color_application": {
    "primary_color_in_subject": "muted gold #C9A96E",
    "background_color": "warm ivory #FAF9F6",
    "color_count_max": 2,
    "saturation": "muted, never neon, never high-saturation",
    "treatment": "matte finish, not glossy or metallic shine"
  },

  "rendering_directives": {
    "style": "photorealistic editorial photography",
    "camera_angle": "slight overhead angle (approximately 15-20 degrees from top-down), never flat top-down",
    "focus": "sharp on the entire subject, slight bokeh on surface texture toward edges",
    "post_processing": "minimal — no heavy filters, no faux film grain, no obvious vignette",
    "text_in_image": "none"
  },

  "negative_prompts": {
    "absolutely_avoid": [
      "stock photo aesthetic",
      "people, hands, body parts",
      "medical imagery (stethoscopes, charts, devices, scrubs)",
      "computer screens, phones, devices",
      "office settings",
      "neon or saturated colors",
      "glossy or metallic finishes",
      "obvious AI artifacts",
      "drop shadows that look digital",
      "gradient backgrounds",
      "competing focal points",
      "cluttered compositions",
      "hand-drawn cartoon style",
      "infographic-style elements",
      "typography rendered into the image",
      "branded logos of any kind",
      "tree branches, twigs, plant material, biological branching, root systems",
      "literal arrows, signs, or directional indicators"
    ]
  }
}
```

## Section C — Iteration workflow

Generated images go through visual review. Expected iteration pattern:

| Round | What's tested | Common failures |
|---|---|---|
| **v01** | Concept interpretation | Model misreads keyword (e.g., "branches" → tree) |
| **v02** | Composition refinement | Emphasis cue placement, count clarity |
| **v03** | Production-ready | Should ship from here |

After 3 iterations, if the concept still isn't landing, switch concept entirely rather than keep iterating.

### Visual review checklist

| Criterion | Pass condition |
|---|---|
| Brand alignment | Muted gold visible (close to #C9A96E), ivory background (close to #FAF9F6) |
| Composition | Subject on left, negative space on right two-thirds |
| Conceptual clarity | Viewer "gets it" without explanation |
| Editorial feel | Reads as magazine cover, not stock photo |
| No AI tells | No weird artifacts, paper texture looks real |
| Lighting consistency | Soft from upper-left, warm shadows |

5/6 pass → ship. 3-4/6 → one targeted iteration. <3/6 → re-concept.

## Section D — File handling

| Step | Detail |
|---|---|
| **Generate locally** | `D:\AI Projects\Image_Studio\[slug]_hero_v[N].png` |
| **Copy to repo** | `/blog/images/[slug]-hero.png` (note hyphen, not underscore, in repo path) |
| **Commit** | Repo path included in blog HTML, OG tags, Twitter Cards, BlogPosting schema |
| **Spec file** | `[slug]_hero.spec.json` kept LOCAL only — not committed |

## Section E — Alt text

Match the actual visual concept descriptively. Examples:

- "Four muted-gold paper ribbons fanning right from a single starting point — illustrating the choice between marketing channels for healthcare practices"
- "Gold thread sewing through a stack of muted ivory papers — illustrating the connection between attribution and unit economics"

Don't write alt text that says "hero image" or "blog illustration." Describe what's in the image AND what it illustrates.

---

# PART 7 — WORKFLOW

## Section A — Sequence for new blog

When a new blog is requested, follow this exact sequence:

| Step | What happens |
|---|---|
| 1. **Confirm brief** | Ask the 5 questions from Part 1 Section A |
| 2. **Competitor scan** | Pull top 3 ranking posts for the keyword. Note coverage gaps. State the unique angle. |
| 3. **Propose outline** | H1, subtitle, H2/H3 structure, proposed visuals, internal link plan. **Wait for approval.** |
| 4. **State tone register** | Tell user which of the 4 registers (Part 1 Section B) and why |
| 5. **Generate hero image** | JSON spec → nano-banana-pro → visual review → iterate or ship |
| 6. **Draft the post** | Every H2 hits 6-element rule. Minimum 4 internal links. |
| 7. **Self-audit** | Run 6-element check on each H2. Run 10-second scan test. Flag weak spots. |
| 8. **Deliver metadata** | Meta title, meta description, URL slug, social captions |
| 9. **Write build brief for Claude Code** | See Section B below |
| 10. **Checkpoint-discipline build** | 5-checkpoint pattern (see Section C) |

## Section B — Build brief for Claude Code

When handing off blog content to Claude Code for HTML build, the brief must include:

| Element | Required content |
|---|---|
| **Goal** | One-sentence description of what's being built |
| **Out of scope** | Explicit list of what NOT to touch |
| **Pre-work** | Files Claude Code reads first, what to confirm |
| **Layout spec** | Reference Part 3 of this document |
| **Schema spec** | Reference Part 2 Section B |
| **Internal link map** | Per-post mapping with anchor text + target URL |
| **Hero image path** | Local path + repo destination |
| **Build sequence** | 5 checkpoints with explicit pause-for-approval points |
| **Commit message** | Pre-written, paste verbatim |

## Section C — Checkpoint discipline (5-checkpoint pattern)

Every blog build (new or retrofit) runs through 5 checkpoints with user approval between each:

| CP | Focus | Estimated time |
|---|---|---|
| **1 — Pre-work** | Read existing files, identify patterns, flag decisions | ~5-10 min |
| **2 — Architecture/scaffold** | HTML structure + image placement | ~15-25 min |
| **3 — Body content + links** | Full prose, internal links verified | ~20-30 min |
| **4 — Schema + final polish** | All schemas validated, sitemap entry, hero image | ~10-15 min |
| **5 — Pre-commit review** | Diff stats, commit message, risks flagged | ~5-10 min |

After CP5: commit, push, deploy, post-deploy verification.

Total realistic estimate: 60-100 minutes per blog from brief to live.

## Section D — Common gotchas

These have all bitten us in past sessions. Watch for them:

| Gotcha | Mitigation |
|---|---|
| Cloudflare strips inline `onclick` | Always use `addEventListener` + `DOMContentLoaded` |
| Vercel cleanUrls strips `.html` before redirects evaluate | Redirect sources must use clean form |
| "branches" in image spec → biological tree | Use "ribbons", "paths", "strands" instead |
| FAQ markup in some existing blogs has stray `<div>` tags | Don't copy this bug forward |
| Emoji renders inconsistently across OS/browsers | Use SVG icons or plain text |
| Hero image too large (2.45 MB) | Compress to WebP in deferred follow-up |
| `position: sticky` parent has overflow set | Sidebar parent (`.blog-body`) must NOT have overflow defined |
| `IntersectionObserver` rootMargin tuned to nav height | If sitewide nav height changes, scroll-spy timing drifts |

## Section E — Retrofit considerations

When migrating an existing blog to V2 template:

| Step | What happens |
|---|---|
| 1. Read existing blog file | Identify content, schema, internal links |
| 2. Restructure HTML | Replace old layout with new `.blog-body` grid |
| 3. Apply new CSS classes | Use BLOG TEMPLATE V2 classes from styles.css |
| 4. Add TOC sidebar | Empty wrapper; JS auto-populates |
| 5. Add sidebar CTA | Outcome-bullet pattern |
| 6. Add mobile TOC | Below Key Takeaways |
| 7. Reference blog-template.js | `<script src="/blog/blog-template.js" defer>` |
| 8. Add scroll-margin-top to H2[id] | For clean anchor jumps |
| 9. Update breadcrumb plural→singular | `.breadcrumbs` → `.breadcrumb` |
| 10. Wrap hero in `.blog-hero` | Per V2 structure |
| 11. Update author block | `.author-line` → `.author-block` with subelements |
| 12. Replace bio text | Use current standard from Part 1 Section D |

Each retrofit is its own commit. Batch 2-3 blogs per commit if logically related (same vertical, same topic cluster).

---

# PART 8 — QUICK REFERENCE CARDS

## Card 1 — New blog checklist

```
☐ Confirmed: topic, keyword, audience, CTA, length
☐ Competitor scan completed
☐ Outline approved
☐ Tone register stated
☐ Hero image generated (v01 → v02 if needed)
☐ Hero image visually reviewed against 6-criterion checklist
☐ Draft written: 6-element rule per H2 ✓
☐ Internal links: minimum 4 ✓
☐ Pull quote: at least 1, in serif italic featured style
☐ Featured table card: if data table present
☐ Featured conclusion card: if prescriptive article
☐ FAQ: 3-5 questions, 40-60 words each
☐ Schema: BlogPosting + FAQPage + BreadcrumbList + HowTo (if applicable)
☐ Anchor IDs on all H2s
☐ Word count: 2,150-2,550 (or document if outside range)
☐ Self-audit: 6-element check passed
☐ Self-audit: 10-second scan test passed
☐ Build brief for Claude Code written
☐ 5-checkpoint discipline followed
☐ Sitemap entry added
☐ All schemas parse on live deploy
☐ All anchor IDs resolve on live deploy
```

## Card 2 — Voice quick check

```
✗ leverage, utilize, empower, unlock, supercharge
✗ crucial, pivotal, paramount
✗ a myriad of, a plethora of
✗ in today's fast-paced world
✗ delve, navigate the landscape
✗ seamlessly, effortlessly, holistic
✗ premium (as marketing adjective)

✓ use, help, important, many, today
✓ second person ("you" + "we")
✓ Canadian spelling
✓ Sentence case headings always
✓ Specific numbers, named tools, real examples
```

## Card 3 — File reference

```
Blog HTML:        /blog/[slug].html
Hero image:       /blog/images/[slug]-hero.png
Shared CSS:       /styles.css (BLOG TEMPLATE V2 section)
Shared JS:        /blog/blog-template.js
Sitemap entry:    /sitemap.xml (clustered with other /blog/* URLs)
Local image dev:  D:\AI Projects\Image_Studio\
Local spec file:  [slug]_hero.spec.json (LOCAL ONLY, not committed)
```

## Card 4 — Internal link slots (recommended pattern)

```
H2 #1 closer:  Italic "Related: [link to industry/category page]"
H2 #2 closer:  Italic ad-calculator or framework callout
H2 #3 closer:  Italic "Related services: SEO · Ads · Reviews"
H2 #4 (data):  Italic link to industry/vertical page
H2 #6 (action): Inline link to ad-calculator
Final CTA:     Primary button → /contact
                Secondary button → relevant industry/playbook
```

## Card 5 — Schema validation flow

```
1. node JSON.parse on each <script type="application/ld+json"> block
2. https://validator.schema.org → paste URL
3. https://search.google.com/test/rich-results → paste URL
4. GSC URL Inspection → Request Indexing
5. GSC Sitemaps → Resubmit
```

## Card 6 — Image generation sequence

```
1. Fill JSON spec (Part 6 Section B) — concept paragraph specific to article
2. Run nano-banana-pro: 16:9 / 2K / PNG
3. Visual review against 6-criterion checklist (Part 6 Section C)
4. If 5/6 pass → save as v01-final, copy to repo
5. If 3-4/6 pass → identify ONE handle to adjust, generate v02
6. If <3/6 pass → re-concept the spec
7. Max 3 iterations before re-concepting
8. Commit final to repo as /blog/images/[slug]-hero.png
9. Keep .spec.json LOCAL only
```

---

# APPENDIX — REFERENCE BLOG

The first blog built on V2 template is `/blog/healthcare-marketing-channels`.

Reference it for:
- Visual examples of all V2 elements
- Real prose examples in the authoritative tone register
- Featured conclusion card pattern
- 4-variable framework callout pattern
- 11-row specialty data table inside featured-table-card
- HowTo schema (4-step decision exercise)
- Real internal linking density (8 links across the article)

When uncertain about a pattern, view that blog's source as the canonical implementation.

---

# CHANGELOG

| Version | Date | Changes |
|---|---|---|
| 2.0 | May 5 2026 | Initial V2 template (D-hybrid sticky TOC sidebar). Replaces V1 (2-column body-layout with right-column visuals). |

---

*End of HMM Blog Template V2 Master Reference*
*Maintained by: Ankit Kumar / HelpMeMarketing*
*Update cadence: When template changes ship to production*
