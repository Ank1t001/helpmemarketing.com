# HMM — Session Handoff

**Session date:** May 20, 2026
**Session length:** Extended — multiple major decisions
**Status of work:** /services/seo live and cleaned. Multiple paths decided for next sessions.

---

## What shipped this session

### Commit 1: feat(services/seo) — d546e62
- New `/services/seo` page (12 sections, 3 schemas, 12 internal links)
- New hero image at `/blog/images/services-seo-hero.png` (1920×1072, 668 KB)
- Updated `sitemap.xml` (replaced `/seo` entry with `/services/seo`)
- New CSS classes added to `styles.css` in SERVICE PAGE COMPONENTS section
- New `docs/BUILD_BRIEF_TEMPLATE_RULES.md` with 6 template rules for future briefs
- New `docs/BUILD_BRIEF_2_SEO.md` (canonical brief archived alongside the build)
- Activated `/seo` → `/services/seo` 308 redirect (preserves existing equity)

**Live at:** https://helpmemarketing.com/services/seo

### Commit 2: cleanup(services/seo) — 2f40e59
- Purged 21 em-dashes per Content Rules Section 2.3
- Removed "landscape" (banned phrase) on line 172
- Active voice fixes on lines 247 and 333
- Softened "anyone who does is lying" claim in 3 locations
- Added 3px gold left-border to `.outcome-card` (visual weight fix)
- FAQ JSON-LD schema updated in tandem with visible FAQ text (byte-for-byte parity)

**Validation:** /services/seo now passes Section 13 checklist except for deferred items (defensible passive instances, jargon audit, outcome card metrics audit).

---

## Decisions locked this session

### Content Rules (v1.0)
- Document: `HMM_Content_Rules_v0_2.md` added to project files
- Voice: hybrid (declarative about capabilities, warm about HMM)
- Reading level: Grade 8 default, Grade 10-12 in technical deep dives
- Banned: 21 em-dashes site-wide, "transform/transformation," "landscape," and 12 other AI-clichés
- All page builds going forward must validate against this document

### Repositioning direction
- **Path 3: Full AI-native rebrand** committed
- Services to add over time: AEO (real now), agent optimization (R&D), LLM marketing (R&D)
- Buyer expansion: Both ICPs (GTA SMB + more sophisticated AI-aware buyers)
- Grounding: Instinct (honestly acknowledged)

### Visual redesign direction
- **HMM-Color-System.docx** added to project — full dark-mode-first design system
- Obsidian primary background, Signal Orange exclusive CTA, Mint as functional state, Warm Break section for About/Process
- 60-30-10 distribution discipline locked
- **Approach: Prototype-first.** Build homepage in new system on feature branch. Validate before committing to full migration of 30+ pages.

### Hosting
- **Stay on Vercel.** Hosting question closed. Technical fit is right; no real reason to switch to HostPapa or others.

---

## Open work — queued for next sessions

### Immediate (Brief #2.7 — Homepage Prototype)
- Build new homepage in the design system spec'd in HMM-Color-System.docx
- Feature branch: `redesign-prototype-homepage`
- Vercel preview URL (auto-generated, not on main)
- Production stays unchanged until validation
- Estimated time: 8-12 hours focused work, 4-6 sessions
- Decision gate: live with prototype for ~1 week, get reaction from 1-2 trusted people, then decide on full migration
- Brief to be drafted next session

### Queued briefs (paused pending redesign decision)
- **Brief #2.5:** Lead magnet — AEO Citation Audit Template
 - Drafted, saved as `BUILD_BRIEF_2_5_LEAD_MAGNET.md`
 - Not executed — would ship on the current light-mode design
 - **Decision needed:** ship in current design now, or defer until redesign validates?
- **Brief #3-10:** Remaining 8 service pages + Bundle Builder + homepage rebuild + nav cleanup
 - All blocked by redesign decision
 - If redesign validates → these get built in new design system
 - If redesign doesn't validate → these get built in current design system

### Pending decisions
- Lead magnet: ship now in current design, or wait for redesign validation?
- AEO standalone service page (`/services/aeo`): build before or after redesign validation?
- Brief #3 (Google Ads): wait for redesign validation, or proceed in current design?

---

## Followups (technical debt)

### Followups from Brief #2 build
1. **CLAUDE.md correction** — remove Cloudflare compatibility note (no longer applies)
2. **Design-doc padding drift** — implementation diverges from the v0 design doc on hero/section padding. Reconcile against `docs/HMM_Design_System.md` (v0 archived at `docs/archive/DESIGN_v0_pre_canonical.md`).
3. **Template-decision documentation** — retroactively document in `docs/HMM_Design_System.md`: 1920×1072 hero standard, 12 new CSS classes, 5 REMAP conventions
4. **Git config committer email** — currently auto-resolves to `akumar@equiton.com` instead of HMM identity. Fix between briefs (not via history rewrite).

### Followups from cleanup commit
5. **Defensible-passive-voice audit** — lines 202, 203/382, 354 are passive but acceptable. Worth broader review of when passive is genuinely better than active.
6. **Undefined industry jargon audit** — "topical authority" and similar terms used without inline definition. Decide: define inline, replace with buyer-language, or accept as Grade 10-12 vocabulary.
7. **Outcome card metrics audit** — the metrics on /services/seo outcome cards are framed as "typical results" but aren't backed by client data. Decide: replace with real client data where available, mark as "industry benchmark" with source citation, or remove.

---

## What changed about HMM's positioning this session

The positioning we built in earlier sessions was three pillars:
1. Pricing transparency
2. Integrated full-service generalist
3. Real local Ontario partnership

You committed this session to Path 3 — evolving HMM toward an AI-native marketing agency for traditional businesses. This doesn't replace the pricing transparency pillar (it gets re-positioned as "AI lets us run leaner, so we can publish pricing"). It does shift the brand voice and visual identity significantly.

The HMM-Color-System document is the visual expression of this rebrand. The Content Rules v1.0 document is the voice expression of it. The /services/aeo service page (when built) is the first product expression of it.

The prototype homepage is the test of whether all three expressions actually produce a coherent brand experience when rendered together.

---

## Recommended next session opening

When you come back:

1. Read this handoff document
2. Read `HMM_Content_Rules_v0_2.md` once more (it locks how every page gets written going forward)
3. Read `HMM-Color-System.docx` once more (it locks the visual direction)
4. Confirm: still committed to the prototype-first homepage approach?
5. If yes: I draft Brief #2.7 (homepage prototype)
6. If something changed in your thinking between sessions: we discuss before drafting

Three things to specifically think about between sessions:

**Question 1:** The lead magnet (AEO Citation Audit Template) is drafted but not executed. If we redesign the site, the lead magnet form section gets rebuilt anyway. But if validation takes 2-3 weeks and you want a lead capture mechanism live during that time, shipping the lead magnet on the current design makes sense. **Lead magnet now in current design, or after redesign validates?**

**Question 2:** The instinct that drove the Path 3 commitment deserves one more honest examination. Between this session and the next, watch for actual signals — prospects asking about AI, competitor messaging, articles that change your view. Track what you see. If by next session the instinct has stronger evidence behind it, the prototype work proceeds confidently. If the instinct has weakened, that's important data too.

**Question 3:** The instinct + prototype path is the disciplined choice. But it's also the choice that takes longer to see results. If after next session you're feeling rushed back into "just commit to full migration," that's a sign to pause and re-examine — not a sign to speed up.

---

## Real numbers from this session

- 2 commits shipped to production
- 1 service page live (`/services/seo`)
- 21 em-dashes purged
- 21 lines added, 24 deleted in cleanup commit
- 13 content rules sections written and locked
- 0 visual issues confirmed on live page after verification
- ~5 hours of compounded conversation
- 1 major direction set (Path 3 — AI-native rebrand)
- 1 major direction validated as needing prototype gate (full redesign migration)

---

## What the session did well

- Caught and corrected my misreads from PDF/screenshot renders (twice — I learned the lesson the second time)
- Locked content rules formally instead of leaving them implicit
- Honest acknowledgment when the instinct/data balance tipped one way or the other
- Discipline on small commits (cleanup commit stayed in scope)
- The hosting question got resolved cleanly without scope creep

## What the session could have done better

- I was too verbose with options/branching decisions. Should have been more directive earlier.
- We added new questions (hosting, redesign, content rules) before resolving the previous ones (lead magnet execution, Brief #3 sequencing). Better to finish one thread before opening the next.
- The Path 3 commitment was made fast on a "maybe" gut check. The prototype gate is the right correction, but it would have been cleaner to make that gate the original decision.

---

*End of session handoff.*
*Resume: any session, this document is the starting context.*
