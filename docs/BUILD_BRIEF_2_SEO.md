# Build Brief #2 — Proof-of-Concept Service Page (SEO)

**For:** Claude Code execution
**Repo:** github.com/Ank1t001/helpmemarketing.com
**Estimated execution time:** 60-120 minutes
**Version:** 1.0 · May 15 2026

---

## Executive summary

**Goal:** Build `/services/seo` as the proof-of-concept service page. This page establishes the template that the other 8 service pages will follow.

**Why SEO first:** Most structurally complex (longest content, most tier scope), has existing ranking equity to protect, exercises the URL migration flow. If we can build this well, the other 8 services template cleanly.

**Scope:** One new page (`/services/seo`), update sitemap.xml, activate `/seo` → `/services/seo` redirect (already staged in commit `3b41469` but inactive until pages exist + push happens), generate one hero image, push to GitHub.

**Out of scope:** The other 8 service pages, Bundle Builder, homepage rewrite, navigation/footer updates, CLAUDE.md correction. Each of those is a separate brief.

> **⚠ Critical: Existing /seo equity**
>
> The current `/seo` page has 36 impressions/month per GSC. Migration to `/services/seo` MUST preserve this minimal but real signal. The `vercel.json` 301 redirect is already staged in commit `3b41469`. Activating it (by pushing to GitHub) only works correctly if `/services/seo` exists. Execute the build, then push everything together in ONE commit.

---

## Pre-work (read-only, before any changes)

Do these checks before any file modifications:

### 1. Confirm prep commit state

```bash
git log --oneline -5
```

**Expected:** see commit `3b41469` — "prep(pricing-rebuild): add shared tier-card/outcome-card/disclosure-card classes + stage URL redirects"

If missing: the prep commit may have been pushed/rebased; verify shared CSS classes exist in styles.css and 8 redirects exist in vercel.json before proceeding.

### 2. Verify shared CSS classes from prep commit

Confirm these 17 CSS classes exist in `styles.css`:

```
.tier-card-grid
.tier-card
.tier-card-eyebrow
.tier-card-who
.tier-card-pricing
.tier-card-pricing-meta
.tier-card-section-heading
.tier-card-fits-list (+ li + ::before)
.tier-card-excluded-list (+ li + ::before)
.tier-card-focus
.outcome-card
.outcome-card-eyebrow
.outcome-card-metric
.outcome-card-profile
.disclosure-card
.disclosure-card-label
.disclosure-card-body
```

### 3. Verify vercel.json redirect

```bash
grep -A 1 '"/seo"' vercel.json
```

**Expected:** source: `/seo`, destination: `/services/seo`, permanent: true

### 4. Verify /services/ directory

```bash
ls services/ 2>/dev/null || mkdir -p services
mkdir -p blog/images
```

---

## File structure & locations

### Files to create

- `services/seo.html` — The new service page (Vercel cleanUrls makes this serve at `/services/seo`)
- `blog/images/services-seo-hero.png` — Hero image (generate with nano-banana-pro)

### Files to modify

- `sitemap.xml` — Add `/services/seo` URL, remove `/seo` URL
- (Eventually) Delete or archive `/seo.html` after redirect activation confirmed

---

## SEO targeting (locked)

These values are locked from the Keyword → Page Mapping document. **Do not modify** without explicit founder approval.

### Primary keyword
- **`services for seo`** (Volume: 2,400 · KD: 40 · Intent: Informational)
- Note: Grammatically awkward in title tag. Title uses natural "SEO Services" phrasing; Primary keyword is embedded naturally in body content (H2 and first 200 words).

### Secondary keywords
- `local seo services` (2,400 · KD 44)
- `seo services toronto` (1,600 · KD 50)
- `toronto seo services` (1,300 · KD 53)
- `seo service` (1,000 · KD 48)

### Realistic ranking timeline
- Month 3-6: Indexed and showing for variants in position 60-100
- Month 6-12: Geographic Secondaries showing impressions in position 30-60
- Month 12-18: Primary keyword reaches position 20-40, Toronto variants page 2-3
- Month 18-24: Page 1 visibility for at least 1-2 of the locked keywords

---

## Meta tags & schema

### Title tag

```html
<title>SEO Services in Toronto & GTA | HelpMeMarketing</title>
```

49 characters. Embeds Secondary geo keyword; Primary "services for seo" covered in body.

### Meta description

```html
<meta name="description" content="SEO and AEO services for Toronto businesses. Local pack optimization, AI engine citations, content production. Published pricing from $1,500/mo.">
```

148 characters.

### Canonical

```html
<link rel="canonical" href="https://helpmemarketing.com/services/seo">
```

### Open Graph + Twitter

```html
<meta property="og:title" content="SEO Services in Toronto & GTA | HelpMeMarketing">
<meta property="og:description" content="SEO and AEO services for Toronto businesses. Published pricing from $1,500/mo.">
<meta property="og:url" content="https://helpmemarketing.com/services/seo">
<meta property="og:image" content="https://helpmemarketing.com/blog/images/services-seo-hero.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="HelpMeMarketing">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="SEO Services in Toronto & GTA | HelpMeMarketing">
<meta name="twitter:description" content="SEO and AEO services for Toronto businesses. Published pricing from $1,500/mo.">
<meta name="twitter:image" content="https://helpmemarketing.com/blog/images/services-seo-hero.png">
```

### BreadcrumbList schema

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://helpmemarketing.com/"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Services",
      "item": "https://helpmemarketing.com/services"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "SEO Services",
      "item": "https://helpmemarketing.com/services/seo"
    }
  ]
}
</script>
```

### Service schema

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Service",
  "name": "SEO Services",
  "serviceType": "Search Engine Optimization",
  "provider": {
    "@type": "Organization",
    "name": "HelpMeMarketing",
    "url": "https://helpmemarketing.com",
    "logo": "https://helpmemarketing.com/logo.svg"
  },
  "areaServed": [
    {"@type": "Country", "name": "Canada"},
    {"@type": "Country", "name": "United States"}
  ],
  "description": "SEO and AEO services for Toronto businesses. Local pack optimization, AI engine citations, content production. Three engagement tiers from $1,500/month.",
  "offers": [
    {
      "@type": "Offer",
      "name": "Foundation",
      "price": "1500-2100",
      "priceCurrency": "CAD",
      "description": "Local or single-location businesses building organic foundation"
    },
    {
      "@type": "Offer",
      "name": "Growth",
      "price": "2100-3500",
      "priceCurrency": "CAD",
      "description": "Mid-sized businesses scaling SEO across multiple keyword clusters"
    },
    {
      "@type": "Offer",
      "name": "Scale",
      "price": "3500+",
      "priceCurrency": "CAD",
      "description": "Established businesses running SEO and AEO as a primary growth program"
    }
  ]
}
</script>
```

### FAQPage schema

> **Important:** This must match the visible FAQ section exactly. If FAQ content changes, update schema to match.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How long does SEO take to show results?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Meaningful SEO ranking shifts typically take 6-12 months. Most engagements show early signals at month 3-4 (local pack movement, first content pieces ranking), with full ranking and traffic results landing between months 6-12. The 6-month minimum on our engagements gives the work time to compound."
      }
    },
    {
      "@type": "Question",
      "name": "What's the difference between SEO and AEO?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "SEO targets traditional search engines (Google, Bing) where users click through to your site. AEO (Answer Engine Optimization) targets AI engines like ChatGPT, Perplexity, and Google AI Overviews where your content is cited within the AI response. Both matter in 2026 because users increasingly search both ways."
      }
    },
    {
      "@type": "Question",
      "name": "Why is your SEO pricing higher than $1,000/month options?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "At $1,500-$2,100/month our Foundation tier includes ongoing content production (1 new piece + 1 optimization per month), AEO Layer 1+2 setup, full Google Business Profile management, local citations, and basic schema. Agencies charging $1,000 typically include only audits and minor on-page changes without ongoing content production. Content is the largest cost driver in real SEO work."
      }
    },
    {
      "@type": "Question",
      "name": "Do you guarantee rankings?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No, and anyone who does is lying. Google doesn't share ranking algorithms, and ranking factors change constantly. We commit to consistent execution of best practices and transparent monthly reporting on what's working and what isn't."
      }
    },
    {
      "@type": "Question",
      "name": "What's included in your AEO work?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "AEO has four layers in our framework. Layer 1: AEO-friendly content structure (clear definitions, comparisons, lists). Layer 2: Schema implementation for FAQ, HowTo, Article. Layer 3: AI citation tracking on priority queries. Layer 4: Active citation engineering — content optimized to be the cited answer in AI responses."
      }
    }
  ]
}
</script>
```

---

## Page content (HTML body)

> Use the existing site shell (header, footer, nav) — match the structure other pages on the site use. Check an existing page like `/seo.html` or `/website-design.html` for reference.

### Section 1: Hero zone

```html
<section class="hero-zone services-hero">
  <div class="container">
    <div class="hero-content">
      <p class="hero-eyebrow">SEO &amp; AEO Services</p>
      <h1 class="hero-headline">SEO services for Toronto businesses, built for AI search and traditional rankings</h1>
      <p class="hero-deck">Most SEO services in Toronto still optimize for 2018 — keyword density, exact-match anchors, and link counts. We optimize for what actually moves rankings in 2026: content depth, AEO citations, and local signals that compound over 6-12 months.</p>
      <div class="hero-cta">
        <a href="/contact" class="btn btn-primary">Book a free SEO audit</a>
        <a href="#tiers" class="btn btn-secondary">See pricing tiers</a>
      </div>
    </div>
    <div class="hero-visual">
      <img src="/blog/images/services-seo-hero.png" alt="SEO services with AEO and traditional ranking strategy" loading="eager" width="600" height="400">
    </div>
  </div>
</section>
```

### Section 2: Why most SEO services in Toronto still optimize for 2018

> This H2 covers Primary keyword "services for seo" naturally. Content positions HMM against generic SEO agencies.

```html
<section class="prose-block">
  <div class="container container-narrow">
    <h2>Why most SEO services in Toronto still optimize for 2018</h2>
    <p>Most agencies offering services for SEO in Toronto haven't updated their playbook since Google's last major algorithm refresh. They build keyword-stuffed pages, chase exact-match backlinks, and report on metrics that don't track to revenue. The work shows on a monthly report. It doesn't show on your bookings.</p>
    <p>The search landscape changed in 2024-2025. Google's AI Overviews now appear above traditional results for roughly 30% of commercial queries. ChatGPT and Perplexity collectively handle hundreds of millions of search queries monthly. Buyers research with AI engines first, then verify with Google, then call.</p>
    <p>The agencies still optimizing only for the blue links are losing ground. The agencies winning are doing both — SEO for Google rankings and AEO for AI engine citations — because that's where attention actually is.</p>
  </div>
</section>
```

### Section 3: How we approach local SEO

> This H2 covers Secondary keyword "local seo services" naturally.

```html
<section class="prose-block">
  <div class="container container-narrow">
    <h2>How we approach local SEO for Toronto businesses</h2>
    <p>Local SEO services aren't generic SEO with a city name added. The discipline is different. Local pack rankings depend on Google Business Profile signals, NAP consistency across citations, and local-intent content. Traditional SEO factors (backlinks, content depth) matter, but they're table stakes.</p>
    <p>For GTA businesses, we focus on four levers in this order:</p>
    <ol>
      <li><strong>Google Business Profile optimization</strong> — Categories, services, hours, photos, posts, Q&amp;A management. The single biggest local SEO lever.</li>
      <li><strong>NAP consistency across citations</strong> — Cleaning up incorrect business listings across directories (Yelp, Yellow Pages, BBB, industry-specific directories).</li>
      <li><strong>Local-intent content</strong> — Service pages that genuinely answer what a Toronto buyer is searching for, not generic content with "Toronto" sprinkled in.</li>
      <li><strong>Local schema implementation</strong> — LocalBusiness schema, Service schema, Review schema. The technical work that helps Google understand who you are and where.</li>
    </ol>
    <p>Most local SEO services in Toronto either skip steps 2 and 4 (technical depth gap) or do them once and forget them (maintenance gap). Both fail over time.</p>
  </div>
</section>
```

### Section 4: AEO — getting cited in AI engines

> Differentiator section. Most competitors don't offer AEO as a distinct service.

```html
<section class="prose-block">
  <div class="container container-narrow">
    <h2>AEO — getting cited in AI engines like ChatGPT and Perplexity</h2>
    <p>AEO (Answer Engine Optimization) is what SEO becomes when the answer engine is an AI model, not a search results page. A user asks ChatGPT "who's the best dental marketing agency in Toronto?" and ChatGPT cites three sources in its answer. Being cited matters more than being in position #1 on Google.</p>
    <p>Our AEO framework has four layers, applied across content production and on-page optimization:</p>
    <ul>
      <li><strong>Layer 1 — Content structure</strong>: Clear definitions, comparisons, structured lists, FAQs. The patterns AI engines extract well.</li>
      <li><strong>Layer 2 — Schema implementation</strong>: FAQ schema, HowTo schema, Article schema. Machine-readable signals about what your content actually says.</li>
      <li><strong>Layer 3 — Citation tracking</strong>: Monitoring AI citations for priority queries using tools like Profound and Adscoop. Knowing where your content is being cited (or isn't).</li>
      <li><strong>Layer 4 — Citation engineering</strong>: Content explicitly written to be the cited answer. Strong opening sentences, clear authority signals, factual specificity.</li>
    </ul>
    <p>HMM applies Layer 1+2 at the Foundation tier, Layers 1-3 at Growth, and all four at Scale. The work compounds: traditional SEO improvements also help AI citations, and AI citation improvements drive traditional rankings up through brand search.</p>
  </div>
</section>
```

### Section 5: Three engagement tiers

> Core of the page. Uses `.tier-card-grid` + `.tier-card` classes from commit `3b41469`. Three identically-structured cards (Foundation, Growth, Scale).

```html
<section class="tiers-section" id="tiers">
  <div class="container">
    <h2>Three engagement tiers</h2>
    <p class="section-deck">Pick the tier that fits your scale. All tiers are 6-month minimum, then month-to-month. Setup is $500 flat across all tiers.</p>
    <div class="tier-card-grid">

      <!-- FOUNDATION CARD -->
      <div class="tier-card">
        <p class="tier-card-eyebrow">Foundation</p>
        <p class="tier-card-who">For: Local or single-location businesses building organic foundation in the GTA where SEO is a primary or only acquisition channel they're investing in.</p>
        <p class="tier-card-pricing">$1,500-$2,100/month</p>
        <p class="tier-card-pricing-meta">+ $500 flat setup · 6-month minimum (results timeline: 6-12 months)</p>
        <h3 class="tier-card-section-heading">What's included</h3>
        <ul class="tier-card-fits-list">
          <li>Content production: 1 new piece per month (1,500-2,000 words, AEO-formatted) + 1 existing page optimization per month</li>
          <li>AEO Layer 1 + partial Layer 2 (AEO-friendly content + basic schema on key pages)</li>
          <li>On-page SEO across 5-8 pages per month</li>
          <li>Google Business Profile management + monthly posts (single location)</li>
          <li>Local citations + NAP consistency</li>
          <li>Basic schema (Organization, LocalBusiness, FAQPage where applicable)</li>
          <li>Local pack ranking monitoring</li>
          <li>Monthly performance report</li>
        </ul>
        <h3 class="tier-card-section-heading">Not included</h3>
        <ul class="tier-card-excluded-list">
          <li>Outbound link building</li>
          <li>Digital PR</li>
          <li>Content beyond 1+1 monthly volume</li>
          <li>Multi-location SEO</li>
        </ul>
        <h3 class="tier-card-section-heading">Typical focus at this tier</h3>
        <p class="tier-card-focus">Local visibility and consistent foundation. Building local pack rankings, GBP performance, and a content publishing cadence that compounds over 6-12 months.</p>
      </div>

      <!-- GROWTH CARD -->
      <div class="tier-card">
        <p class="tier-card-eyebrow">Growth</p>
        <p class="tier-card-who">For: Mid-sized businesses scaling SEO across multiple keyword clusters where SEO is one of 2-3 acquisition channels actively being invested in.</p>
        <p class="tier-card-pricing">$2,100-$3,500/month</p>
        <p class="tier-card-pricing-meta">+ $500 flat setup · 6-month minimum (results timeline: 6-12 months)</p>
        <h3 class="tier-card-section-heading">What's included</h3>
        <ul class="tier-card-fits-list">
          <li>Everything in Foundation, plus:</li>
          <li>Content production: 2 new pieces per month (1,500-2,500 words each) + 2 existing page optimizations</li>
          <li>AEO Layers 1-3 (citation tracking added)</li>
          <li>On-page SEO across 10-15 pages per month</li>
          <li>Multi-location GBP management (up to 5 locations)</li>
          <li>Advanced schema (Service, Product, FAQ, HowTo, Article)</li>
          <li>Topic cluster strategy + content gap analysis</li>
          <li>Internal linking optimization</li>
          <li>Bi-weekly performance reviews</li>
        </ul>
        <h3 class="tier-card-section-heading">Not included</h3>
        <ul class="tier-card-excluded-list">
          <li>Outbound link building (available add-on)</li>
          <li>Digital PR (available add-on)</li>
          <li>Content beyond 2+2 monthly volume</li>
        </ul>
        <h3 class="tier-card-section-heading">Typical focus at this tier</h3>
        <p class="tier-card-focus">Scaling beyond foundational rankings. Building topical authority across keyword clusters, expanding AEO citation coverage, and measuring contribution to revenue.</p>
      </div>

      <!-- SCALE CARD -->
      <div class="tier-card">
        <p class="tier-card-eyebrow">Scale</p>
        <p class="tier-card-who">For: Established businesses running SEO and AEO as a primary growth program with content production at meaningful scale and clear attribution requirements.</p>
        <p class="tier-card-pricing">$3,500+/month</p>
        <p class="tier-card-pricing-meta">+ $500 flat setup · 6-month minimum (results timeline: 6-12 months)</p>
        <h3 class="tier-card-section-heading">What's included</h3>
        <ul class="tier-card-fits-list">
          <li>Everything in Growth, plus:</li>
          <li>Content production: 4+ pieces per month (long-form, pillar content, comparison pages)</li>
          <li>AEO Layers 1-4 (full citation engineering)</li>
          <li>Unlimited on-page SEO optimization</li>
          <li>Multi-location GBP management (unlimited locations)</li>
          <li>Custom schema architecture</li>
          <li>Outbound link building (5-10 placements/month)</li>
          <li>Digital PR for high-authority placements</li>
          <li>Custom reporting dashboard</li>
          <li>Weekly strategy calls</li>
        </ul>
        <h3 class="tier-card-section-heading">Not included</h3>
        <ul class="tier-card-excluded-list">
          <li>Paid media management (separate Google Ads / Meta Ads services)</li>
        </ul>
        <h3 class="tier-card-section-heading">Typical focus at this tier</h3>
        <p class="tier-card-focus">SEO and AEO as a primary growth program. Content velocity at scale, citation engineering, and meaningful contribution to revenue pipeline.</p>
      </div>

    </div>
  </div>
</section>
```

### Section 6: What this looks like in practice

> Uses `.outcome-card` classes from commit `3b41469`. Typical-results framing (not specific client claims).

```html
<section class="outcomes-section">
  <div class="container container-narrow">
    <h2>What this looks like in practice</h2>
    <p class="section-deck">Typical results we see for SEO clients at each tier. Specific outcomes vary by industry, market, and starting position. We share real engagement examples and case studies during the discovery call.</p>
    <div class="outcome-grid">
      <div class="outcome-card">
        <p class="outcome-card-eyebrow">Foundation tier · Typical result</p>
        <p class="outcome-card-metric">Local and single-location clients typically see top-3 local pack rankings for 15-25 priority queries within 6 months and 100-200% organic traffic growth YoY.</p>
        <p class="outcome-card-profile">Local service businesses and single-location practices in the GTA. Results scale with market competition and content publishing consistency.</p>
      </div>
      <div class="outcome-card">
        <p class="outcome-card-eyebrow">Growth tier · Typical result</p>
        <p class="outcome-card-metric">Mid-sized businesses typically see non-brand organic revenue grow 50-100% over 9 months, with 200-400 keywords ranking in the top 10.</p>
        <p class="outcome-card-profile">Established businesses scaling SEO across multiple keyword clusters. Results depend on content depth and link building consistency.</p>
      </div>
      <div class="outcome-card">
        <p class="outcome-card-eyebrow">Scale tier · Typical result</p>
        <p class="outcome-card-metric">Content-led businesses typically see AI engine citations on 8-15 priority queries within 90 days and 150-250% increase in organic-sourced pipeline over 12 months.</p>
        <p class="outcome-card-profile">Established businesses running SEO + AEO as a primary growth program. Results scale with content production capacity and competitive positioning.</p>
      </div>
    </div>
  </div>
</section>
```

### Section 7: About our pricing (disclosure)

```html
<section class="disclosure-section">
  <div class="container container-narrow">
    <div class="disclosure-card">
      <p class="disclosure-card-label">About our pricing</p>
      <p class="disclosure-card-body">We publish our pricing because guessing wastes everyone's time. The rates above are what we charge — not a starting price, not a teaser. They reflect what good SEO work costs when an agency operates without the bloat of larger shops. Engagements signed at these rates are locked in for the duration of the agreement.</p>
    </div>
  </div>
</section>
```

### Section 8: Terms & commitment

```html
<section class="prose-block">
  <div class="container container-narrow">
    <h2>Terms &amp; commitment</h2>
    <p>6-month minimum commitment, then month-to-month with 30-day notice. SEO typically takes 6-12 months to produce meaningful ranking shifts. The 6-month minimum gives the work time to start showing signal (typically by month 3-4 — local pack movement, GBP lift, first content pieces ranking). Full ranking and traffic results usually land between months 6-12.</p>
    <p>If you need leads in the next 90 days, SEO isn't the right channel for that timeline. Paid ads is. We'll tell you that on the discovery call rather than take an engagement that's going to disappoint you.</p>
  </div>
</section>
```

### Section 9: Not for you if

```html
<section class="prose-block">
  <div class="container container-narrow">
    <h2>Not for you if</h2>
    <ul class="caveat-list">
      <li>You need leads in the next 30 days (SEO is a 6-18 month investment)</li>
      <li>You're not willing to publish content regularly (SEO without content is technical hygiene, not growth)</li>
      <li>Your site has been penalized by Google and needs recovery work (we'll refer you to a specialist)</li>
      <li>You want guaranteed rankings — nobody can guarantee them, and anyone who does is lying</li>
    </ul>
  </div>
</section>
```

### Section 10: FAQ

> Must match FAQPage schema exactly.

```html
<section class="faq-section">
  <div class="container container-narrow">
    <h2>Frequently asked questions</h2>
    <details class="faq-item">
      <summary>How long does SEO take to show results?</summary>
      <p>Meaningful SEO ranking shifts typically take 6-12 months. Most engagements show early signals at month 3-4 (local pack movement, first content pieces ranking), with full ranking and traffic results landing between months 6-12. The 6-month minimum on our engagements gives the work time to compound.</p>
    </details>
    <details class="faq-item">
      <summary>What's the difference between SEO and AEO?</summary>
      <p>SEO targets traditional search engines (Google, Bing) where users click through to your site. AEO (Answer Engine Optimization) targets AI engines like ChatGPT, Perplexity, and Google AI Overviews where your content is cited within the AI response. Both matter in 2026 because users increasingly search both ways.</p>
    </details>
    <details class="faq-item">
      <summary>Why is your SEO pricing higher than $1,000/month options?</summary>
      <p>At $1,500-$2,100/month our Foundation tier includes ongoing content production (1 new piece + 1 optimization per month), AEO Layer 1+2 setup, full Google Business Profile management, local citations, and basic schema. Agencies charging $1,000 typically include only audits and minor on-page changes without ongoing content production. Content is the largest cost driver in real SEO work.</p>
    </details>
    <details class="faq-item">
      <summary>Do you guarantee rankings?</summary>
      <p>No, and anyone who does is lying. Google doesn't share ranking algorithms, and ranking factors change constantly. We commit to consistent execution of best practices and transparent monthly reporting on what's working and what isn't.</p>
    </details>
    <details class="faq-item">
      <summary>What's included in your AEO work?</summary>
      <p>AEO has four layers in our framework. Layer 1: AEO-friendly content structure (clear definitions, comparisons, lists). Layer 2: Schema implementation for FAQ, HowTo, Article. Layer 3: AI citation tracking on priority queries. Layer 4: Active citation engineering — content optimized to be the cited answer in AI responses.</p>
    </details>
  </div>
</section>
```

### Section 11: Final CTA

```html
<section class="final-cta">
  <div class="container container-narrow">
    <h2>Ready to start with SEO?</h2>
    <p>Book a free 30-minute SEO audit. We'll look at your current rankings, identify the 3 highest-impact opportunities, and tell you honestly whether SEO is the right channel for your goals right now.</p>
    <div class="cta-buttons">
      <a href="/contact" class="btn btn-primary">Book a free SEO audit</a>
      <a href="/services/bundle" class="btn btn-secondary">Build a service stack</a>
    </div>
  </div>
</section>
```

---

## Internal links (exact anchor text & destinations)

Distribute these across hero, body, and CTAs. Don't cluster all in one section.

### Service → Service (inline in body)
- "Google Ads management" → `/services/google-ads-management` (in Section 4 about AEO, when mentioning paid as complementary)
- "web design and development" → `/services/web-design-development` (in Section 3 about local SEO)
- "analytics and attribution" → `/services/analytics-attribution` (in Section 5 tier cards, when discussing reporting)

### Service → Industry (inline)
- "healthcare practices" → `/industries/healthcare`
- "DTC brands" → `/industries/dtc`
- "SaaS companies" → `/industries/saas`

### Service → Bundle Builder
- "Build a service stack" → `/services/bundle` (final CTA)
- "combine SEO with paid services" → `/services/bundle` (in tier cards if natural)

### Service → Blog (related reading at bottom)
- "What marketing services do I need?" → `/blog/what-services-do-i-need`
- "How much does digital marketing cost?" → `/blog/digital-marketing-cost`
- "SEO, PPC, or social — which channel matters most?" → `/blog/seo-ppc-or-social`

### Page → Contact (CTAs)
- "Book a free SEO audit" → `/contact` (hero + final CTA)

**Total: ~10-12 internal links.**

---

## Hero image generation

### Tool
Use **nano-banana-pro** skill in Claude Code environment.

### Specs
- Format: PNG
- Aspect ratio: 16:9 (3000×1688 px target)
- File path: `/blog/images/services-seo-hero.png`
- Compression: Aim for <500KB, max 1MB

### Visual concept prompt

```
Editorial photography style, 16:9 ratio, top-down or 30-degree angle shot.

Subject: Several layers of muted gold paper ribbons or sashes arranged on a warm ivory surface, suggesting layered citations or stacked rankings. The ribbons should flow naturally, not stacked perfectly — slightly overlapping, with shadows.

Material cues: matte paper texture (not glossy), subtle paper-grain detail.

Colors: HMM brand muted gold (#C9A96E), warm ivory background (#FAF9F6). No navy in the image itself. No other colors.

Lighting: soft, diffused, natural daylight from upper-left. Warm-grey shadows beneath ribbons.

Style anchors: design magazine editorial photography (Kinfolk, Cereal, Monocle aesthetic). Premium, considered, not corporate stock.

Avoid: People, hands, devices, screens, generic stock photo aesthetic, neon colors, glossy finishes, drop shadows, gradient backgrounds, infographic elements, typography, tree branches, literal arrows.
```

### Alt text
`SEO services with AEO and traditional ranking strategy`

(Describes visual + page context. Don't keyword-stuff.)

---

## Sitemap & redirect activation

### sitemap.xml — add this entry

```xml
<url>
  <loc>https://helpmemarketing.com/services/seo</loc>
  <lastmod>2026-05-15</lastmod>
  <changefreq>monthly</changefreq>
  <priority>0.8</priority>
</url>
```

### sitemap.xml — remove the old /seo entry

```xml
<!-- REMOVE this entry: -->
<url>
  <loc>https://helpmemarketing.com/seo</loc>
  ...
</url>
```

### Redirect activation timing — critical

The `/seo` → `/services/seo` redirect is already staged in `vercel.json` from commit `3b41469`. It activates when:
1. `vercel.json` is pushed to GitHub (currently local-only)
2. Vercel deploys the change (30-60 seconds after push)

**Push `services/seo.html` + `sitemap.xml` + `vercel.json` in the SAME commit.** If `vercel.json` is pushed alone, users hitting `/seo` get redirected to a 404.

---

## Execution sequence (7 checkpoints)

> After EACH step, stop and report what you did. Wait for "proceed" before moving to next step.

### Step 1: Pre-flight checks
- `git log --oneline -5` (confirm commit `3b41469` exists)
- Verify the 17 CSS classes exist in `styles.css`
- Verify `vercel.json` has `/seo` redirect staged
- Verify `services/` directory exists (create if not)

**Report:** results of all four checks.

### Step 2: Generate hero image
- Use nano-banana-pro with the visual concept prompt above
- Generate 3-5 variations, pick the strongest
- Save to `/blog/images/services-seo-hero.png`
- Verify file size <1MB (compress if needed)

**Report:** show me the chosen image before proceeding.

### Step 3: Create services/seo.html
- Use the full HTML structure from Sections 1-11 above
- Apply meta tags + 3 schema blocks (BreadcrumbList, Service, FAQPage)
- Use existing site shell (header, footer, nav) — match other pages
- Apply CSS classes from commit `3b41469`

**Report:** path of created file + file size.

### Step 4: Update sitemap.xml
- Add new entry for `/services/seo`
- Remove old entry for `/seo`
- Maintain alphabetical ordering

**Report:** show diff of sitemap.xml.

### Step 5: Local testing
- If Vercel CLI available: `vercel dev`
- Open `http://localhost:3000/services/seo`
- Verify page renders, all sections appear
- Test schema with Google Rich Results Test on rendered HTML

**Report:** what works, what doesn't.

### Step 6: Commit & push
- `git add services/seo.html blog/images/services-seo-hero.png sitemap.xml`
- `git commit -m "feat(services/seo): proof-of-concept service page rebuild — SEO services"`
- `git push origin main`
- Verify Vercel deployment succeeds

**Report:** commit hash, deployment URL, deployment status.

### Step 7: Post-deploy verification
- Test `https://helpmemarketing.com/services/seo` loads
- Test `https://helpmemarketing.com/seo` redirects to `/services/seo` (curl -I to confirm 301 status)
- Test schemas with Google Rich Results Test on live URL
- Submit URL to GSC for indexing

**Report:** all checks pass/fail.

---

## Verification checklist (post-deploy)

### Page rendering
- [ ] Page loads at `https://helpmemarketing.com/services/seo`
- [ ] Hero image displays (not broken)
- [ ] All 11 content sections render in order
- [ ] Three tier cards display correctly on desktop and mobile
- [ ] FAQ accordions expand/collapse
- [ ] CTAs are clickable and lead to correct pages

### SEO infrastructure
- [ ] Title tag shows in browser tab
- [ ] Meta description shows in Google search preview
- [ ] Canonical URL is correct
- [ ] OG tags show in social preview (Facebook debugger / Twitter card validator)
- [ ] BreadcrumbList schema validates (Google Rich Results Test)
- [ ] Service schema validates
- [ ] FAQPage schema validates
- [ ] All schema visible in "View Source"

### URL migration
- [ ] `https://helpmemarketing.com/seo` returns 301 to `/services/seo` (test with `curl -I`)
- [ ] sitemap.xml shows `/services/seo`, no `/seo`
- [ ] Submit sitemap.xml in GSC

### Internal links
- [ ] All internal links resolve (no 404s)
- [ ] Anchor text matches documented values
- [ ] Outbound links to `/services/google-ads-management`, etc. exist (placeholders for now — pages don't exist yet)

### Performance
- [ ] PageSpeed Insights >85 mobile, >90 desktop
- [ ] LCP <2.5s, INP <200ms, CLS <0.1
- [ ] Hero image <1MB, compressed
- [ ] No console errors in browser devtools

---

## Out of scope (DO NOT DO)

- Build the other 8 service pages
- Build the Bundle Builder calculator
- Build or update `/services` hub page
- Update homepage
- Update main navigation or footer
- Remove dropped services from sitemap (`/lifecycle-retention`, `/reviews-reputation`, `/brand-content`) — done in later cleanup
- Update `CLAUDE.md` to remove Cloudflare compatibility note
- Create case studies or work portfolio entries
- Update any blog articles
- Image optimization for blog post images
- Email signup forms or newsletter

---

## Risks & honest notes

### Risk 1: Hero image quality
nano-banana-pro can fail to produce usable results. If 3+ unusable variations:
- (a) Try simpler prompt
- (b) Use existing stock photo with HMM color adjustment
- (c) Skip hero temporarily, use CSS gradient placeholder

### Risk 2: Existing /seo equity loss
Redirect should preserve the small ranking signal from `/seo`. But Google sometimes treats 301s to substantially different content as "soft 404" equivalents. If `/services/seo` doesn't rank for SEO queries within 30 days, we've lost signal. Monitor in GSC.

### Risk 3: Template establishes patterns
Every decision here gets replicated 8 more times. If a CSS class doesn't work well, HTML structure is awkward, or internal linking feels off — flag it now. Fixing 1 page is easy. Fixing 9 pages later is painful.

### Risk 4: Schema validation
All 3 schema blocks need to validate in Google Rich Results Test. If any fail, Google may not display rich results — costs CTR. Validate BEFORE pushing.

### Risk 5: Stale prep commit
Prep commit `3b41469` is local-only. If lost (forced rebase, accidental reset), shared CSS classes won't exist and this build fails. Verify in Step 1.

---

## After this build completes

### Immediate next steps
- Founder reviews live page at `https://helpmemarketing.com/services/seo`
- Founder approves or flags structural issues
- If approved: this becomes the template for the other 8 service pages
- If structural issues: fix in `/services/seo` before building others

### Subsequent build briefs (after approval)
- Brief #3: Google Ads service page
- Brief #4: Meta Ads service page
- Brief #5: LinkedIn + TikTok Ads (batched)
- Brief #6: Social Media + Branding (batched)
- Brief #7: Web Design + Analytics (batched)
- Brief #8: Bundle Builder calculator (separate, most complex)
- Brief #9: Homepage + `/services` hub rebuild
- Brief #10: Navigation + footer + sitemap cleanup

### Realistic timeline
From this brief to all 9 service pages + Bundle Builder live: roughly 4-6 weeks at 1-2 briefs/week pace. Faster possible if template holds; slower if structural issues emerge.

---

*End of Build Brief #2*
*Phase 1 Build · v1.0 · May 15 2026*
