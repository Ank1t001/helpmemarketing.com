# HMM Phase 2 (days 31 to 60): search intent, internal links and authority

Prepared 12 October 2026 from the live repository. Status: **plan for founder approval.** Nothing in sections 2 or 4 has been implemented yet; section 3 lists the identity facts as found.

Ground rules carried from the brief: one primary intent per commercial page; no automatic merging or rewriting of overlapping pages; no invented endorsements, link buying or unverified figures; research dates move only when a verified cycle exists.

The "candidate queries" below are hypotheses from page content, not measured demand. Validate each against Search Console (Canada, last 3 months) before treating it as a target. No keyword volume tool data was used.

## 1. Search-intent map (commercial pages)

| Page | Primary intent (one job) | Candidate related queries (to validate) | Notes |
|---|---|---|---|
| `/` | Who is Ankit / HMM and should I talk to them | Ankit Kumar marketing; Burlington digital marketer | Brand and navigation hub, not a ranking target for service terms |
| `/services` | What marketing help is available | digital marketing services Ontario | Hub that routes to the six service pages |
| `/services/performance-marketing` | Hire help running Google and Meta ads for leads or sales | Google Ads management Ontario; Meta ads for lead generation | Owns paid ads. Links to both calculators and Meta Growth OS |
| `/services/seo` | Hire help to be found in search, including AI answers | SEO services Ontario; local SEO for service businesses | **Owns the commercial SEO intent.** Broad search service |
| `/ai-seo-agency` | Understand and improve how the business appears in AI answers | AI search visibility; appear in ChatGPT answers; AEO | Narrower than `/services/seo`; must not compete for "SEO services". Keep title focused on AI search |
| `/ai-marketing-agency` | Understand how AI supports marketing overall | AI marketing agency Ontario | **Umbrella only.** Links down to AI Automation, AI SEO and the service pages; should not target SEO or automation terms itself |
| `/services/ai-automation` | Hire help automating lead follow-up and workflows | marketing automation for small business; lead follow-up automation | Owns automation intent |
| `/ai-agents-halton` | Local: AI agents for Halton businesses | AI receptionist Halton; AI chatbot Oakville | Overlaps `/services/ai-automation`. Awaiting founder direction on the AI pages; decide keep (local landing) or redirect later. Do not change now |
| `/services/branding-social` | Hire help with brand, social content and video | social media management; brand identity Ontario | |
| `/services/website-development` | Hire help building a website that brings enquiries | small business website design Ontario | |
| `/services/analytics-attribution` | Hire help making tracking and reporting trustworthy | GA4 setup; marketing attribution help | |
| `/gta-marketing-agency` | Local: a GTA business looking for a nearby marketer | marketing agency GTA; marketing agency Burlington | The local landing page |
| `/industries/healthcare` | Clinic owner looking for marketing help | clinic marketing; healthcare marketing Ontario | |
| `/industries/finance` | Finance firm looking for qualified-lead marketing | financial services marketing; investment firm lead generation | |
| `/industries/dtc` | DTC brand looking for profitable growth | DTC marketing agency; Shopify growth | |
| `/industries/saas` | SaaS company looking for demos and pipeline | SaaS marketing agency; B2B demand generation | |
| `/work`, `/portfolio` | Proof: has this person done it before | (navigational) | Evidence pages, not ranking targets |
| `/tools/marketing-audit` | Free self-serve check of what to fix first | free marketing audit; marketing checklist | |
| `/ad-calculator` | How much should I spend on ads | ad spend calculator; how much to spend on Google Ads | |
| `/ad-set-calculator` | How many Meta ad sets can my budget support | Meta learning phase calculator; how many ad sets | |
| `/seo-growth-os`, `/meta-growth-os` | Download a structured audit system | SEO audit framework; Meta ads audit framework | Titles still say "One System, Any Site/Account"; update to the new outcome headlines |
| `/hmm-index` and the three indexes | Original benchmark research | medspa Instagram benchmark; real estate Instagram benchmark | Authority assets (section 4) |

### Overlap: SEO vs AI SEO vs AI Marketing (identify, do not merge)

| Signal | `/services/seo` | `/ai-seo-agency` | `/ai-marketing-agency` |
|---|---|---|---|
| Title | SEO and AI Search Visibility | AI SEO Agency in Canada | AI Marketing Agency in Ontario |
| Shared ground | AI search visibility appears as one capability | Whole page is AI search | Mentions AI SEO as a link only |
| Risk | Title includes "AI Search Visibility", the same phrase that heads `/ai-seo-agency` | Could split clicks for "AI search visibility" queries | Low; umbrella |
| Recommended handling | Keep; consider "SEO Services" as the title lead in a later test | Keep as the AI search page; it links to `/services/seo` and back | Keep; link down, not across |

Decision for later, with Search Console data: if both SEO pages rank for the same queries, test retitling `/services/seo` to lead with "SEO Services" before any merge.

## 2. Internal-link plan (proposed, not yet built)

Findings from the content-body link graph (nav and footer excluded):

- **Industry pages link to no service pages** (only `/work` and `/about`; SaaS also links Analytics). This is the largest gap.
- **Weakly linked commercial pages:** `/ai-agents-halton` (1 inbound), `/ai-seo-agency`, `/ai-marketing-agency`, `/industries/finance`, `/industries/saas`, `/ad-set-calculator` (2 each), `/gta-marketing-agency`, `/meta-growth-os`, `/hmm-index` (3).
- **Blog posts** mostly link to services already; some link to nothing commercial beyond `/work` (`choose-marketing-agency`, `marketing-mistakes`, `marketing-strategy-from-zero`).

| # | From | To | Suggested anchor (descriptive, varied) | Why |
|---|---|---|---|---|
| 1 | Each industry page | The two or three most relevant service pages | e.g. Healthcare to "clinic SEO" (`/services/seo`), "patient enquiry ads" (`/services/performance-marketing`), "booking follow-up" (`/services/ai-automation`) | Gives each service a vertical path; biggest gap |
| 2 | Each industry page | Its Work example and one tool | Healthcare to `/work#vanguard`; Finance to `/work#equiton`; DTC to `/work#luxe-charme`; all to `/tools/marketing-audit` | Proof next to the claim |
| 3 | `/services/performance-marketing` | `/ad-set-calculator`, `/meta-growth-os` | "check how many ad sets your budget supports"; "the Meta Growth OS audit system" | Tool pages with 2 to 3 inbound links |
| 4 | `/services/seo`, `/blog/seo-ppc-or-social`, `/blog/paid-ads-vs-organic` | `/ai-seo-agency` | "how your business appears in AI answers" | Strengthens the narrow AI search page from its parents |
| 5 | `/services/ai-automation`, `/blog/what-ai-agents-do-for-marketing` | `/ai-marketing-agency` | "how AI fits across your marketing" | Umbrella gets links from its children |
| 6 | `/services/performance-marketing`, `/services/analytics-attribution` | `/industries/finance`, `/industries/saas` | "marketing for finance firms"; "SaaS demand generation" | Lifts the two weakest industry pages |
| 7 | `/blog/choose-marketing-agency` | `/gta-marketing-agency`, `/services` | "working with a GTA marketer"; "the services I offer" | Commercial path from a high-intent post |
| 8 | `/blog/marketing-mistakes`, `/blog/marketing-strategy-from-zero` | `/tools/marketing-audit`, relevant services | "find your first priority" | Gives these posts a next step |
| 9 | `/services/branding-social`, `/work` | `/hmm-index` | "my Instagram benchmark research" | Connects research to the service it supports |
| 10 | `/about` | `/work`, `/services`, `/hmm-index` | in the body copy | About should route onward, not only receive |

Rules: one or two links per paragraph at most; descriptive anchors, no repeated exact-match anchors; no links to redirected URLs; `/ai-agents-halton` untouched until the AI-page direction is decided.

Completion check for this section: every commercial page in section 1 has at least three in-body inbound links from relevant pages, and links onward to proof (`/work`) and a next step (review or tool).

## 3. Business identity consistency

Found on 12 October 2026:

| Item | Site | Status |
|---|---|---|
| Base | **Halton Hills, Ontario** since 12 Oct 2026 (founder decision; was Burlington) in footers, FAQ answers, GTA page and `addressLocality` | Consistent across served pages after the update |
| Old addresses | "Mississauga, Ontario" survives only in `/docs/_healthcare/*` (archive, not served) | No action needed for the live site |
| Email | `Hello@helpmemarketing.com` visible; `hello@` in schema | Consistent with the casing rule |
| Phone | None published | Consistent (no number to mismatch) |
| sameAs profiles | Instagram `helpmemarketing1`, LinkedIn `company/helpmemarketing`, Facebook `helpmemarketing1`, Google Maps | Same three social profiles everywhere |
| Google Business Profile | Maps place pin at 43.637, −79.871 (Halton Hills) | Resolved: matches the Halton Hills base; link kept |
| Two Maps URL forms | `/maps/place/...` (2 pages) and `/maps?cid=...` (1 page) | Low priority; standardise on the cid form after the profile is confirmed |

## 4. Authority: evidence-led outreach list

Only original, verifiable HMM assets are pitched. No paid links, no link exchanges, no claimed endorsements, and no named publication is listed here until it has been checked as real, active and relevant.

### Assets that can be pitched

| Asset | What it offers a publication | Verified basis |
|---|---|---|
| GTA MedSpa Index (cycle 001, 10 Sep 2026) | Benchmark of 176 GTA medspas' Instagram reach; regulatory-exposure finding | Published dataset and post log |
| Hair Loss Index (cycle 001, 8 Sep 2026) | Reach vs response in a niche local category | Published dataset |
| Real Estate Index (cycle 003, 24 Sep 2026) | Instagram activity of Canadian private real estate firms | Published dataset; note the 5 Oct refresh is not yet published |
| Canadian marketing cost guide | Typical CAD market ranges | Labelled as market ranges, not HMM prices |
| AdSpend and Meta Learning Phase calculators | Free tools for readers | Live, no email gate |

### Outlet types to research (names to be verified before contact)

| Type | Fit | Angle | Verify before adding a name |
|---|---|---|---|
| Canadian medical aesthetics trade publications and associations | MedSpa Index | Instagram reach benchmark and the advertising-compliance finding | Real masthead, editorial contact, accepts contributed data |
| Ontario and GTA business news (local business sections, chambers of commerce newsletters) | GTA page, cost guide | Local small-business marketing data | Active publication, local relevance |
| Canadian real estate investment newsletters and podcasts | Real Estate Index | How private real estate firms use Instagram | Audience of investors or operators |
| Hair loss and trichology professional communities | Hair Loss Index | Reach vs booking path in the category | Professional, not consumer forums |
| Marketing communities (local meetups, Canadian marketing associations, relevant subreddits with self-promotion rules followed) | Calculators, Growth OS | Free tools and method, shared within community rules | Community rules permit sharing |
| Podcasts on small-business marketing in Canada | Founder expertise | The research method and findings | Recent episodes, guest format |

Each entry in the working list (to be built from this table) records: outlet, contact, asset pitched, date, response, and the resulting link or mention. Pitch only the latest verified cycle and include its date.

## 5. Research timestamps

| Page | Last verified data | Next scheduled | Action |
|---|---|---|---|
| `/realestate-index` | 24 Sep 2026 | 5 Oct 2026, not yet published | Keep cycle 003 visible; update only when cycle 004 is verified |
| `/hair-loss-index` | 8 Sep 2026 | 8 Oct 2026, not yet published | Same |
| `/gta-medspa-index` | 10 Sep 2026 | 10 Dec 2026 | On schedule |

## 6. What needs a decision

1. Approve the internal-link plan (section 2) so it can be built page by page.
2. Check the Google Business Profile location (section 3).
3. Confirm the outlet types in section 4, then the named list can be researched and verified.
4. Provide Search Console exports (Canada, 3 months, queries by page) to validate section 1.
