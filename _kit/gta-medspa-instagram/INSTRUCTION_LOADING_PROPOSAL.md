# Proposal: reduce automatically loaded instructions (not applied)

Status: proposal only. The root `CLAUDE.md` is unchanged. Nothing here changes research methodology, the 600-account guard, preview rules or any other index.

## What loads at session start (measured from the 2026-10-15 transcript)
| Item | Size (characters) | Where it comes from |
|---|---|---|
| `CLAUDE.md` instructions attachment | 54,602 (file 53,729 bytes, 307 lines) | repo root, always loaded |
| Skill listing | 33,427 | account-level skills and plugins, about 70 entries, mostly unrelated to this routine |
| System prompt snapshot | 35,444 | harness plus the routine's cloud-session text |
| MCP instructions | 4,449 | Apify and Google Drive (more arrive as servers connect) |
| Deferred tool names, agent listing | 2,769 and 2,893 | harness |
| First API call, all of the above | about 84,000 tokens (measured: 55,820 cache-created + 28,058 cache-read) | |

That 84k is re-read from cache on every call. Across 76 calls so far it accounts for at least 6.4M of 13.8M cache-read tokens (derived lower bound: 84k times 76, context only grows).

## Largest `CLAUDE.md` sections (bytes)
JavaScript and forms (14,993: contact form, marketing audit, homepage tour, consent, Apps Script); Index generator contract (9,505, covering all four index instances); Deployment and SEO (5,739); Phase 2.5 decisions (2,623); Phase 2 architecture (2,062); the rest are under 2,000 each.

For the GTA routine only the Index generator contract, parts of Deployment and SEO (no em dashes, titles, JSON-LD) and the voice rules are relevant. The JavaScript and forms section (28% of the file) is not.

## Proposed options (smallest risk first)
1. **Routine-specific entry point.** Add `_kit/gta-medspa-instagram/ROUTINE_BRIEF.md` (about 3 KB): the rules this routine needs, with links to the sections of `CLAUDE.md` for the rest. The routine prompt says "read the brief, then the kit README and EDITORIAL_RULES" and no longer says "read CLAUDE.md first". Saves reading cost on demand; does not change what auto-loads.
2. **Path-scoped rule files.** Move per-area sections (JavaScript and forms, blog template, Phase 2 history, per-index contracts) to `docs/` or `.claude/rules/` files that load only when matching files are touched, leaving a short root `CLAUDE.md` (shared rules, page conventions, index contract summary, pointers). Biggest reduction; needs a careful move, a check that no rule is lost, and a test that other routines (Real Estate, Hair Loss) still find their rules.
3. **Skill listing.** The 33 KB listing is account-level, outside the repo. Disabling unused skills for scheduled routines is a settings change the founder would make; the repo cannot do it.
4. **MCP instructions.** Connect only the servers a routine needs (Apify, Drive, Sheets, Vercel, GitHub). Fewer servers means fewer instruction blocks.

## Rules that must stay shared and visible
Em-dash and banned-phrase rules, Canadian spelling and first-person voice, the Index generator contract (head contract, no inline `style`, cycle-agnostic head, frames self-hosted), the instance-specific mirror-into-kit requirement for each index, pricing and location rules, clean-URL convention, sitemap rules, the `.vercelignore` rule for `_kit/`, consent and privacy rules, and the canon-doc pointers.

## Process if approved
Run option 1 first (low risk). For option 2, move text verbatim, add pointers, diff the old and new rule sets mechanically, then run the Real Estate and Hair Loss kit checks (`build.py --check-live`) before merging.
