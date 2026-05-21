# PLAN.md — Repositioning Migration

Repo-local execution checklist. See `docs/HMM_Design_System.md` for the canonical design system (original `DESIGN.md` archived to `docs/archive/DESIGN_v0_pre_canonical.md`) and the full plan in `C:\Users\AnkitKumar\.claude\plans\i-m-repositioning-helpmemarketing-com-fr-soft-ritchie.md` for full context.

## Phase summary

| Phase | Scope | Gate |
|---|---|---|
| 0 | Produce design system, PLAN.md, FINDINGS.md (design system later consolidated as `docs/HMM_Design_System.md`) | ✅ historical — see `docs/archive/DESIGN_v0_pre_canonical.md` for the v0 snapshot |
| 1 | Update `:root` tokens + Fraunces font link across all 19 pages | Visual sweep of 3 pages |
| 2 | Nav, footer, CTA card — across all 19 pages (Hm mark, navy, gold, Industries column) | Visual check of nav/footer on 3 pages |
| 3 | Homepage rebuild (`index.html`) to mockup spec | `/` live review |
| 4 | Service pages — redesign using mockup patterns; archive healthcare variants | 6 service pages + hub review |
| 5 | `/industries/*` pages (4) — template decided after Phase 4 review | 4 industry pages review |
| 6 | About, Contact, Pricing, Blog, Ad-calculator, Work, `/_healthcare/` archive | Final ship review |

Commit once per phase. Stop for review before the next phase.

## URL map (Phase 4 sets up 301s in `vercel.json`)

| Old | New |
|---|---|
| `/healthcare-seo` | `/seo` |
| `/clinic-websites` | `/websites` |
| `/retention` | `/lifecycle-retention` |
| `/reputation` | `/reviews-reputation` |
| `/brand` | `/brand-content` |
| `/google-meta-ads` | `/google-meta-ads` (unchanged) |
| `/social-media` | `/social-media` (unchanged) |
| `/analytics` | `/analytics` (unchanged) |
| `/hipaa-checklist` | `/_healthcare/hipaa-checklist` |

## Healthcare content archive

- Moves to `/_healthcare/` (preserves SEO value for paid-campaign landing pages)
- `robots.txt` gains `Disallow: /_healthcare/`
- `sitemap.xml` does NOT include these URLs
- Contents: old service pages (healthcare-seo, hipaa-checklist), old ad-calculator BENCH, old case-study cards (Vanguard, Rehab Mantra, Wellspring, Bloom, Brightsmile, Aster)

## Critical rules (all phases)

1. **Never delete healthcare content** — generalize or move to `/_healthcare/`.
2. **Italic-gold accent**: one per headline max. Color `#C9A96E`. Most semantically important word only.
3. **`[PLACEHOLDER: description]` HTML comments** for every invented name, metric, quote. Greppable.
4. **URL preservation**: every renamed slug gets a 301 in `vercel.json`.
5. **No scope creep**: off-plan issues go to `FINDINGS.md`, never fixed inline.
6. **Shared-component edits touch all 19 pages** — no templating.
7. **Chart colors are data-viz only**. Never chrome/buttons/pills/text.
8. **No glassmorphism, no drop-shadows on cards, no gradient buttons.**
9. **Accessibility floor**: semantic HTML, alt text, ARIA, focus-visible, keyboard nav.
10. **Commit per phase, stop for review.**

## Open questions awaiting user input

- Real client names + metrics for homepage case grid (3 cards) and case-studies page (full grid)
- Real testimonial for homepage testimonial section
- Real industry-tile metrics (confirm or replace `+312%`, `3.2×`, `+186%`, `↓40%`)
- Generalist `BENCH` segments for `ad-calculator.html` (proposed: DTC/SaaS/Healthcare/Finance with 3–4 sub-segments each) + CPL/conv/LTV values or approval to research
- About-page founding story narrative
- Whether `/_healthcare/` needs an index.html landing page for paid campaigns
- Pricing-page tier copy + price points
