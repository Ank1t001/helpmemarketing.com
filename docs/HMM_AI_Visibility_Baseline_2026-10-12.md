# HMM AI visibility baseline, 2026-10-12

First baseline of whether AI answer tools mention or cite HelpMeMarketing (HMM, Ankit Kumar, helpmemarketing.com) for 15 buyer questions. Row-level results are in `HMM_AI_Visibility_Baseline_2026-10-12.csv` (60 rows: 15 questions x 4 platforms).

## Method actually used

Each question was run once per platform, in the same order, with no follow-ups, on 2026-10-12 (about 14:57 to 15:02 UTC). All calls went through the DataForSEO MCP tools, not a browser.

| Platform | Tool | Settings |
|---|---|---|
| Google AI Overview | `serp_organic_live_advanced` | google, location "Ontario,Canada" (accepted, no fallback needed), language en, desktop, depth 10 |
| ChatGPT | `ai_optimization_chat_gpt_scraper` | location Canada, language en, force_web_search true. The response does not name the model |
| Perplexity | `ai_optimization_llm_response` | llm_type perplexity, model `sonar` (the base model listed by `ai_optimization_llm_models`, alongside sonar-pro and sonar-reasoning-pro), web_search true |
| Microsoft Copilot | none | Not run: no access from this environment; run manually |

What differs from the planned logged-out consumer method:

- **Google:** the SERP API flagged an AI Overview on 13 of 15 questions, but every one came back as `asynchronous_ai_overview: true` with no text and no references. So for Google, AI Overview mentions and citations could not be measured at all. Those rows say "Not measurable". Organic top 10 presence is recorded instead.
- **ChatGPT:** a scraper of ChatGPT with web search forced on, located in Canada. It is close to a consumer answer, but it is not a logged-out browser session, and the model version is not shown.
- **Perplexity:** the `sonar` API model, not the logged-in or logged-out consumer app. Location cannot be set, so answers are not localised to Ontario.
- **Copilot:** not tested.

How rows were scored: "HMM mentioned" means the name HelpMeMarketing, Help Me Marketing, Ankit Kumar or the domain appears in the answer text. "HMM cited with a link" means a helpmemarketing.com URL appears in the answer's links or source list. Nothing was inferred beyond what the responses contained.

## Summary counts

Mentions / citations with a link, out of the questions in each area. Google counts are for organic top 10 only, because AI Overview content was not returned.

| Area (questions) | Google AI Overview | Google organic top 10 | ChatGPT mentioned | ChatGPT cited | Perplexity mentioned | Perplexity cited | Copilot |
|---|---|---|---|---|---|---|---|
| Marketing agency (3) | Not measurable | 0 | 0 | 0 | 0 | 0 | Not run |
| SEO and AI search (3) | Not measurable | 0 | 0 | 0 | 0 | 0 | Not run |
| Performance marketing (2) | Not measurable | 0 | 0 | 0 | 0 | 0 | Not run |
| Marketing automation (1) | Not measurable | 0 | 0 | 0 | 0 | 0 | Not run |
| Marketing tools (3) | Not measurable | 1 | 1 | 1 | 0 | 0 | Not run |
| Original research (3) | Not measurable | 0 | 0 | 0 | 0 | 2 | Not run |
| **Total (15)** | **Not measurable** | **1** | **1** | **1** | **0** | **2** | **Not run** |

The four HMM appearances:

1. **ChatGPT, "Ad spend calculator by customer goal":** named first as "HelpMeMarketing AdSpend Calculator (Best for customer goals)" and cited `https://helpmemarketing.com/ad-calculator` in its sources. The in-text link was malformed (it rendered as `https://helpme`), but the source list carried the correct URL.
2. **Perplexity, "Instagram benchmarks for hair loss clinics in Ontario":** cited `https://helpmemarketing.com/hair-loss-index` as source 1 and used its figures (Hair Loss Lab Sudbury, 86,183 Reel plays from 24 Reels in 90 days, 836 followers). The answer text does not name HMM.
3. **Perplexity, "Instagram benchmarks for GTA medical spas":** `https://helpmemarketing.com/work` was in the source list as source 2, but no sentence in the answer points to it. HMM is not named.
4. **Google organic, "Free marketing audit tool for small businesses":** `https://helpmemarketing.com/tools/marketing-audit` ranked organic position 4. The AI Overview on that page could not be read.

HMM did not appear on any platform for the nine agency, SEO, AI search, paid ads or automation questions, including "Marketing consultant in Halton Hills".

## Most-cited other domains

Counted as the number of answers (ChatGPT plus Perplexity, 30 answers) that cited each domain at least once:

| Domain | Answers citing it | Where |
|---|---|---|
| sortlist.com | 3 | Perplexity (agency, Halton Hills, SEO questions) |
| agencies.semrush.com | 3 | Perplexity (agency, automation, AI visibility questions) |
| clutch.co | 3 | ChatGPT twice, Perplexity once |
| hellodarwin.com | 3 | Perplexity |
| thesocialshepherd.ca | 2 | ChatGPT (ads management, ads budget) |
| owlsdigital.com | 2 | ChatGPT and Perplexity (ads budget) |
| ap-digital.ca | 2 | ChatGPT and Perplexity (ads budget) |
| outgrow.ca | 2 | Perplexity (ads management, ads budget) |
| searchandgather.co | 2 | ChatGPT and Perplexity (paid ads, analytics, automation) |
| thinkprofits.com | 2 | ChatGPT and Perplexity (ads management) |
| searchenginepeople.com | 2 | ChatGPT and Perplexity (AI visibility services) |
| doodleweb.ca | 2 | ChatGPT and Perplexity (AI search questions) |

Directories and listicles (Sortlist, Semrush Agency Partners, Clutch, helloDarwin, The Manifest, RevenueBase) are the main route by which agencies get named in the "who" questions. For Halton Hills specifically, ChatGPT named CA14 Marketing, Main Street Marketing, The Iconic Management and CloudSprout, and Perplexity named En Passant Media, Circus Strategic Communications, Coders Cube, CA14, Pluto IT and NinjaPromo.

## Errors and limitations

- Google SERP calls for "Who manages Google and Meta ads for Canadian small businesses?" and "Ad spend calculator by customer goal" each returned API error 40101 (Internal SE Server Error) on the first try. Both succeeded on the single retry, and the retry is what is recorded.
- No other call errored, and no answer refused.
- Google AI Overview text and references were never returned (asynchronous), so the Google AI Overview column holds no measurement. A manual check in a logged-out browser is needed to fill it.
- Copilot was not run.
- Each question was asked once. AI answers vary between runs, users and days, so a single run is a snapshot, not a stable rate.
- Perplexity ran through the API (`sonar`), which can differ from the consumer app, and had no location set.
- ChatGPT's model version is not exposed by the scraper.
- The Google organic check covered the first 10 organic results only (local pack, ads and forums are listed in the CSV notes where they appeared, but they were not counted as organic positions).
