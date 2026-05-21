# Project followups — post-sprint cleanup

Items deferred during the May 2026 pricing-rebuild + design-system build sprint. Verify each item still applies before acting.

---

## CLAUDE.md Cloudflare correction

**Status:** Pending
**Description:** CLAUDE.md contains a Cloudflare compatibility note that no longer applies (we moved away from Cloudflare interference patterns when we adopted the dark-mode prototype scoping). Remove or update the relevant section in CLAUDE.md.

---

## Committer email fix

**Status:** Resolved 2026-05-21
**Description:** Git committer identity was auto-resolving to akumar@equiton.com on multiple past commits. Fixed forward by setting `git config user.email "Hello@helpmemarketing.com"`. Past commits left as-is (not amended).

---

## Template-decision documentation

**Status:** Pending
**Description:** DESIGN.md drift was resolved when the canonical design system shipped. The remaining template-decision documentation work: retroactively document in the canonical design system Section 7 (or appropriate location): 1920×1072 hero image standard, 12 new CSS classes from Brief #2 build, the 5 REMAP conventions from that brief.

---

## /services/seo outcome card metrics audit

**Status:** Pending
**Description:** The metrics on `/services/seo` outcome cards are framed as "typical results" but aren't backed by client data. Decide: replace with real client data where available, mark as "industry benchmark" with source citation, or remove. Per content rules §9.2 (no invented numbers).

---

## /services/seo defensible-passive-voice audit

**Status:** Pending
**Description:** During the `/services/seo` cleanup commit, three passive-voice instances were flagged as "defensible" (lines 202, 203/382, 354). Broader review needed on when passive is genuinely better than active. Could become a content rules clarification.

---

## /services/seo undefined industry jargon audit

**Status:** Pending
**Description:** Terms like "topical authority" used without inline definition on `/services/seo`. Decide per term: define inline, replace with buyer-language, or accept as Grade 10-12 vocabulary in technical sections.

---

## Hero image generation for new design system

**Status:** Pending (Phase 3 of migration plan)
**Description:** Current "gold paper ribbons" hero image style was designed for ivory background. Won't work on Obsidian. Needs new visual direction — abstract dark-mode editorial visual aligned with new color system. Currently using dashed-border placeholder div.

---

## Real H1 refinement

**Status:** Pending (post-prototype-evaluation)
**Description:** Current homepage H1 "We use AI to find your next 100 customers before your competitors do" is locked as placeholder. Real H1 to be refined after prototype evaluation period completes.

---

## H1 italic accent word decision

**Status:** Pending
**Description:** Current italic-orange accent is on "100 customers" in homepage H1. Confirm this is the right word OR identify a better choice once real H1 is locked. Per design system §4, accent word should be the most concrete or buyer-relevant phrase.

---

## Mobile responsive validation

**Status:** Pending (before Phase 1 ships)
**Description:** Prototype was reviewed at desktop only. Mobile responsive behavior at 375px (iPhone SE), 390px (iPhone 14 Pro), 414px (iPhone Pro Max), 768px (iPad portrait), 900px (small laptop) needs validation before Phase 1 work completes. Identified in canonical design system §6 and §10.

---

## Self-host Fraunces + Inter fonts

**Status:** Pending (Phase 7 followup per design system §4)
**Description:** Currently loading from Google Fonts CDN. Self-hosting removes 200-300ms first-paint latency. Adds ~150KB to repo. Worth doing before site fully migrates.

---

## Accessibility followups

**Status:** Pending (before Phase 1 ships, per design system §11)
**Description:** Six items:
1. Implement `:focus-visible` outline rules across all interactive elements
2. Add skip-to-content link to homepage
3. Test homepage with keyboard-only navigation
4. Test homepage with VoiceOver (Mac) or NVDA (Windows)
5. Verify reduced-motion respects user preference
6. Add ARIA labels where icon-only buttons exist (hamburger menu when built)

---

## Brand-wide logo mark rollout

**Decision date:** May 21, 2026
**Trigger:** Design system v1.0 introduces new "HMM" logo mark (replacing previous "Hm")
**Scope:** Update logo mark across all non-website brand surfaces

**Locations needing update:**
- Favicon (currently "Hm" — needs HMM version with appropriate sizing for 16×16 / 32×32 / apple-touch-icon)
- Social profile pictures (LinkedIn, any other active social accounts)
- Email signatures (Founder's email signature, any other team members)
- Business cards
- Any printed material (one-pagers, proposals, slide decks)
- Any client-facing assets (proposal templates, report templates, invoice templates)

**Status:** Pending. Website mark updates immediately via prototype work. Brand-wide rollout is its own project.

**Acceptance criteria:**
- Every brand surface uses "HMM" mark (H white + MM italic Signal Orange in dark contexts, light variant equivalent in print/light contexts)
- Old "Hm" mark removed everywhere it appears
- Updated brand asset library documented somewhere accessible

**Owner:** Founder (Ankit)
