# HMM Session Handoff — Migration Phase

**Created:** May 20, 2026 (end of extended session)
**Status:** Full migration to new design system GREENLIT
**Next session:** Migration planning + execution begins

---

## Quick orientation for next session

Read this entire document before any work begins next session. It captures:
- What's locked (decisions that cannot be re-litigated without strong reason)
- What's shipped (commits live in production)
- What's prototype state (commits on feature branch, not in production)
- What's queued (work to do next)
- What's deferred (followups not blocking)

**Single sentence summary:** Prototype validated the AI-native rebrand direction. Full migration of 30+ remaining pages now begins. Next session drafts migration plan, queued work executes systematically.

---

## What's locked

### Strategic decisions

| Decision | Locked | Notes |
|---|---|---|
| Path 3 — Full AI-native rebrand | ✓ | Validated by prototype on May 20 |
| Migration approach | ✓ | Full migration of all pages, not phased |
| Hosting | Vercel | Question closed this session |
| Repo | github.com/Ank1t001/helpmemarketing.com | |
| Production branch | `main` | Currently at commit `2f40e59` |
| Prototype branch | `redesign-prototype-homepage` | At commit `25e776e`, 5 commits ahead of main |

### Design system

| Element | Locked Value |
|---|---|
| Primary background | Obsidian `#0E0E0E` |
| Elevated surface | Carbon `#1A1A1A` |
| Primary text | Pure White `#FFFFFF` |
| Muted text | Graphite `#999999` |
| Tertiary text | Slate `#737373` |
| Primary CTA | Signal Orange `#FF5C1A` (max 2-3 uses per page) |
| CTA hover | Ember `#FF7038` |
| Functional state | Mint `#00D4AA` (success/live only, NEVER CTA) |
| Border | `rgba(255, 255, 255, 0.08)` |
| Grid lines | `rgba(255, 255, 255, 0.045)` (was 2.5%, calibrated to 4.5%) |
| Orange glow | `rgba(255, 92, 26, 0.18)` (was 12%, calibrated to 18%) |
| Warm break bg | `#F8F4ED` (for /about page only) |
| Warm break text | `#1A1A1A` (Carbon) |
| Warm break CTA | Burnt Terracotta `#C8542B` |
| Distribution | 60% background / 30% text / 10% accent |

### Typography

| Element | Family | Size | Weight | Line-height |
|---|---|---|---|---|
| H1 (hero) | Fraunces serif | 64px | 400 | 1.05 |
| H2 (section) | Fraunces serif | 40px | 400 | 1.1 |
| H3 (subsection/card) | Fraunces serif | 24px | 500 | 1.25 |
| Body | Inter sans | 17px | 400 | 1.6 |
| Hero subtitle | Inter sans | 19px | 400 | 1.55 |
| Section deck | Inter sans | 18px | 400 | 1.6 |
| Eyebrow | Inter sans | 13px | 500 | — (uppercase, 0.12em letter-spacing) |

### Layout

| Element | Value |
|---|---|
| Container max-width | 1240px |
| Container padding | 32px horizontal (desktop), 20px mobile |
| Section vertical padding | 96px (desktop), 64px (mobile) |
| Mobile breakpoint | 900px |
| Heading hierarchy | Strong (locked from comparison render) |

### Voice and content

All voice and content rules locked in `HMM_Content_Rules_v0_2.md` (v1.0 status). Mandatory for every page going forward.

Key reminders:
- No em-dashes site-wide
- Active voice as default
- Sentence case headings always
- Canadian spelling
- Beat the AI summary test for every page
- Honesty levels (Proven / Active / R&D) for every capability claim

### Positioning

| Element | Locked |
|---|---|
| Brand direction | AI-native marketing agency |
| Both ICPs | GTA SMB + sophisticated AI-aware buyers (possibly North American) |
| AEO | Active (real, deliverable) |
| Agent optimization | R&D |
| LLM marketing | R&D |
| AI Automation | Custom per client (not productized) |
| Pricing transparency | Stays a pillar, no longer leads positioning |

### Homepage content (placeholder H1, otherwise final)

| Section | Content reference |
|---|---|
| H1 | "We use AI to find your next 100 customers before your competitors do." (placeholder, real H1 refined post-evaluation) |
| Subhead | "SEO, paid media, and content. Engineered to deliver results, not impressions. Published pricing. No fluff." |
| Section 2 H2 | "Your next customer asked ChatGPT before they Googled you." |
| Section 3 H2 | "Six services. One operating system." |
| Final CTA H2 | "Get three specific things to fix in your marketing. From people who've already looked." |
| Services | 6 cards: Performance Marketing, SEO + AEO, Branding + Social, Website Development, Analytics + Attribution, AI Automation & Workflow Systems |

Full content source: `HMM_Homepage_Content_Draft_v2.md`

---

## What's shipped (production)

| Commit | Description | Live URL |
|---|---|---|
| `d546e62` | Brief #2: /services/seo full build (12 sections, 3 schemas, 12 internal links, hero image) | https://helpmemarketing.com/services/seo |
| `2f40e59` | Cleanup: em-dash purge + content rules compliance + outcome card visual fix | (same URL) |

Production main is at `2f40e59`. Untouched during prototype work.

---

## What's in prototype state (NOT in production)

**Branch:** `redesign-prototype-homepage`
**HEAD:** `25e776e`
**Status:** Live on Vercel preview URL, auth-gated, noindex protected, not merged to main

**Commits on branch (in order):**
1. `dc31182` — Initial homepage rebuild with new design system
2. `256f3e4` — Calibration round 1: grid opacity, orange glow, Mint dot, card padding, section borders
3. `8af1d92` — Calibration round 2: section padding consistency (hero, final CTA, footer)
4. `5295d04` — Calibration round 3: comparison cards (replaced table), section deck width, nav dark variant
5. `25e776e` — Calibration round 4: nav hover background, logo mark dark variant

**Files modified:** 2 only (`index.html` + `styles.css`)
**Scope containment:** All CSS scoped under `body.redesign-prototype`. Legacy CSS untouched. Other pages on the branch render with legacy styles.

**Preview URL:** `https://helpmemarketing-com-git-r-58aaba-ankit-kumars-projects-a328efd6.vercel.app/`
(Requires Vercel auth)

---

## Critical artifacts (all should be in project files or saved locally)

### Project files (canonical sources)

| File | Purpose |
|---|---|
| `HMM_Content_Rules_v0_2.md` | Voice and content rules v1.0, MANDATORY for all pages |
| `HMM-Color-System.docx` | Design system color/spacing/component specs |
| `HMM_Blog_Template_v2.docx` | Blog template (was created earlier this session) |
| `HMM_Blog_Template_V2_Master_Reference.md` | Blog template master reference |
| `HMM_Docs_CLAUDEmd_Update_Brief.md` | Earlier brief for CLAUDE.md updates |

### Build briefs and content drafts (saved separately)

| File | Purpose |
|---|---|
| `HMM_Homepage_Content_Draft_v2.md` | Source content for homepage (used by prototype) |
| `BUILD_BRIEF_2_7_HOMEPAGE_PROTOTYPE.md` | Executed brief for homepage prototype |
| `HMM_Comparison_Strong_Hierarchy.html` | Heading hierarchy comparison file (Strong locked) |
| `HMM_Comparison_Subtle_Hierarchy.html` | Heading hierarchy comparison file (rejected) |
| `HMM_Session_Handoff_2026_05_20.md` | Earlier mid-session handoff |

### Repository files (in production)

| File | Status |
|---|---|
| `index.html` (root) | Light-mode legacy on main; dark-mode prototype on branch |
| `styles.css` | Contains both legacy CSS AND new prototype CSS section |
| `services/seo.html` | Live in production, content-rules compliant |
| `docs/BUILD_BRIEF_TEMPLATE_RULES.md` | Template rules from Brief #2 |
| `docs/BUILD_BRIEF_2_SEO.md` | Brief #2 archived |
| `vercel.json` | Redirects, cleanUrls configuration |
| `sitemap.xml` | Includes /services/seo |
| `robots.txt` | AI crawler rules configured |

---

## What gets built next (migration phase)

### Phase structure

The migration breaks into rough phases. Real numbers depend on per-page complexity but the order matters.

**Phase 1: Design system finalization (4-6 hours)**
- Move prototype CSS from `body.redesign-prototype` scope to canonical CSS (becomes the new design system)
- Remove `body.redesign-prototype` body class scoping once new design is canonical
- Build out missing component patterns (forms, FAQ accordions, breadcrumbs, etc.) discovered during page-by-page migration
- Document the design system in `docs/DESIGN_SYSTEM.md`

**Phase 2: Core navigation and footer (3-4 hours)**
- Dark-mode nav becomes canonical (no longer prototype-scoped)
- Dark-mode logo becomes canonical
- New footer rebuilt in design system
- Mobile menu rebuilt

**Phase 3: Homepage finalization (4-6 hours)**
- Real H1 (replaces placeholder)
- Hero image generation (new aesthetic direction needed)
- Italic accent word decision
- Final visual polish

**Phase 4: Service pages migration (24-30 hours)**
- /services/seo (existing — gets rebuild in new system)
- /services/performance-marketing (new build)
- /services/branding-social (new build)
- /services/website-development (new build)
- /services/analytics-attribution (new build)
- /services/ai-automation (new build, R&D framing per content rules)
- Each service page: ~4-5 hours including content, schema, hero image

**Phase 5: Industry pages migration (12-16 hours)**
- /industries/dtc
- /industries/saas
- /industries/healthcare
- /industries/finance
- Each: ~3-4 hours

**Phase 6: Standalone pages (6-8 hours)**
- /about (with warm break section per design system)
- /contact
- /how-we-work
- /blog (index page)
- /privacy
- /terms

**Phase 7: Blog migration (varies)**
- All existing blog posts need dark-mode treatment
- Blog template needs to be rebuilt for dark mode
- See `HMM_Blog_Template_V2_Master_Reference.md` for current template

**Phase 8: Tools migration (4-6 hours)**
- /ad-calculator
- /tools/marketing-audit (if/when built)

**Total realistic estimate:** 60-90 hours of focused work. At 1-3 hours per session, that's 20-50 sessions.

### What gets built first next session

Real recommendation: **Phase 1 (design system finalization).** Reasons:

1. Migrating the prototype CSS from scoped-under-body-class to canonical is a one-time clean-up. Doing it before more pages get built means subsequent pages reference the canonical system, not the scoped prototype.

2. Documenting the design system formally prevents drift across the 30+ pages that follow.

3. Phase 1 doesn't touch production. Branch work continues on `redesign-prototype-homepage` (or a new branch like `redesign-design-system`).

After Phase 1, real decision point: do we ship the new design system to production all-at-once (one big merge) or page-by-page (rolling migration)?

This decision was deferred earlier in the session when we picked "build everything, ship at once." Worth re-confirming after Phase 1.

---

## Followups (deferred, captured for future)

### From Brief #2 build (still pending)

1. **CLAUDE.md correction** — remove Cloudflare compatibility note (no longer applies)
2. **Design-doc padding drift** — implementation diverges from the v0 design doc on hero/section padding. Reconcile against `docs/HMM_Design_System.md` (v0 archived at `docs/archive/DESIGN_v0_pre_canonical.md`).
3. **Template-decision documentation** — retroactively document 1920×1072 hero standard, new CSS classes, REMAP conventions in `docs/HMM_Design_System.md`
4. **Git config committer email** — currently `akumar@equiton.com`, needs HMM email before next commit

### From /services/seo cleanup commit

5. **Defensible-passive-voice audit** — broader review of when passive is genuinely better than active
6. **Undefined industry jargon audit** — "topical authority" and similar terms used without definition
7. **Outcome card metrics audit** — verify metrics against real client data, mark source or remove

### From homepage prototype work

8. **Real H1 refinement** — placeholder "AI-native marketing for traditional businesses" used; final H1 wording figured out post-evaluation
9. **Italic accent word decision** — which word in H1 gets orange italic ("100 customers" current default)
10. **Hero image generation** — new aesthetic direction (gold-paper-ribbons won't work on Obsidian); abstract dark-mode editorial visual aligned with new color system
11. **Mint pulse animation on eyebrow dot** — currently static glow; could add subtle pulse keyframe
12. **Self-hosting Fraunces + Inter** — move fonts from Google CDN to repo for performance
13. **Migration of /services/seo to new design system** — currently in light-mode, needs full rebuild
14. **Lead magnet brief execution** — AEO Citation Audit Template drafted but not built; ship in current design or wait for full migration?
15. **Trust signals** — Partner badges (Google + Meta) when ready, client logos/testimonials when clients agree
16. **Brand identity question on logo mark** — dark variant is live on prototype; deeper question of whether original logo needs evolution to match AI-native positioning

---

## Real read on session decisions

### What this session did well

- **Prototype gate protected against premature 60-90 hour commitment.** Six hours ago direction was instinct; now it's grounded in a rendered page.
- **Content Rules v1.0 locked formally.** Every page going forward has a quality bar.
- **Hosting question closed cleanly without scope creep.**
- **/services/seo shipped + cleaned to content-rules compliance** before any redesign work started.
- **Each calibration round produced smaller delta than the last.** Clean convergence pattern.
- **Scope discipline held throughout.** All prototype work isolated to feature branch and body-class scoping. Zero risk to production.

### What could have been done better

- **Too many forks per question early in the session.** Lots of "pick A/B/C/D/E" when single-stream questions would have moved faster.
- **The Path 3 commitment was made on instinct with a "maybe" gut check.** Prototype gate was the right correction but it would have been cleaner to start with the gate.
- **Multiple decisions made under fatigue at end of session.** Some of those (full migration commitment, no-prototype-first answer) needed pushback before they landed in better form.

### Honest read on the migration commitment

You greenlit migration at end of an extended session. The prototype validated the direction — that's real data. But the next 60-90 hours of work is a significant commitment that benefits from one more honesty check at session start:

**Before migration begins next session, ask yourself:**
- Is the prototype still landing well after living with it for several days?
- Did anyone whose judgment you trust react to the preview URL?
- Are there specific things you noticed that need to be in the migration plan?

If all answers point toward "yes, proceed" — migration begins.
If any answer surfaces real reservations — we adjust before committing.

This isn't pushback. It's the same prototype gate discipline applied at the migration commit moment.

---

## Recommended next session opening

When you come back:

1. **Open the preview URL again.** First impression after a few days is different from first impression in the session it was built. Notice what changed in your perception.

2. **Read this handoff document.** Confirms what's locked, what's pending.

3. **Confirm migration commitment.** Either reaffirm or refine before next work begins.

4. **Start with Phase 1 (design system finalization).** Or wherever feels right based on fresh assessment.

5. **Hand to Claude Code with a fresh brief for whatever phase starts first.**

---

## Quick reference card

```
PROJECT: HelpMeMarketing rebrand
REPO: github.com/Ank1t001/helpmemarketing.com
PRODUCTION: main branch @ 2f40e59 (light-mode, current site)
PROTOTYPE: redesign-prototype-homepage branch @ 25e776e (dark-mode rebrand)
PREVIEW: https://helpmemarketing-com-git-r-58aaba-ankit-kumars-projects-a328efd6.vercel.app/
HOSTING: Vercel (confirmed staying)
NEXT PHASE: Design system finalization (Phase 1 of 8)
DECISION GATE: Confirm migration commitment after evaluation period
```

---

*End of HMM Session Handoff — Migration Phase*
*This document is the canonical session-resume artifact*
*Save to project files OR keep this conversation accessible for next session*
