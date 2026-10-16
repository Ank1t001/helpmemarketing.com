# Dental Implant Marketing Index, edition 001: evidence pass, 16 October 2026

Window fixed at 16 September to 15 October 2026, America/Toronto. Checks ran 18:50 to 19:13 UTC (2:50 to 3:13 p.m. Toronto) in headless Chromium in the Claude Code cloud container. This was not the founder's Chrome: there was no login, no exported cookies, no paid collection and no form submission. Each URL was loaded once, and a refusal was recorded, not retried. Machine-readable record: `dental_evidence_001_2026-10-16.json` (same folder).

## 1. Blocked clinic websites
| Clinic | Checked (UTC) | Result |
|---|---|---|
| Dundas East Dental, dundaseastdental.com | 18:54:17 | HTTP 200, but the page shows only "VPN or Proxy Detected. Please disable your VPN or Proxy to browse this website." Not bypassed. Content behind the panel was not read. |
| Bond Street Dental, dentalimplantsclinic.ca | 18:54:32 | Cloudflare "Performing security verification" (HTTP 403). Not passed. |

The website itself does not confirm that dentalimplantsclinic.ca is Bond Street Dental. Google ad records corroborate it: 26 ads in the window from Passion Dental Group Inc (Verified), with location assets "Bond Street Dental - Toronto" and one creative showing "113 Bond St".

## 2. Social identities
| Clinic | Handle | Status |
|---|---|---|
| Studio B | @studiobdental | Linked from the website; bio links studiobdental.ca. The display name is "Charles Botbol". |
| NYSC | @northyork.smilecentre | Linked from the website; bio links smile-by-design.ca and says "Head office @mysmilecentre". |
| Gajjar | @gajjardentistry | Linked from the website. Profile refused (HTTP 429, login redirect, 19:11:04Z). |
| Dundas | none | Not verified (site blocked). |
| Bond | none | Not verified (site blocked). |

## 3. Instagram, 16 Sep to 15 Oct
9 posts were read from the post pages: Studio B 4 and NYSC 5. The record for each post includes the URL, the date taken from the post's own timestamp, likes and comments. Plays are recorded as missing because they are not shown when logged out. Videos were not watched.

Implant posts:
- Studio B: 1 (a zirconia implant testimonial), plus 1 unclear (implant only in a hashtag).
- NYSC: 3 (an implant testimonial, an All-on-X FAQ and an All-on-X webinar).

Coverage is **probable, not complete**. The logged-out grid of 12 items spans the window on both accounts, and no posts appear after 30 September (Studio B) or 1 October (NYSC). Gajjar, Dundas and Bond were not collected.

## 4. Ad records (10)
| Clinic | Meta Ad Library | Google Ads Transparency |
|---|---|---|
| Studio B | Relevant ads observed. 2 active ads: one All-on-X ad says "$17,990 PER ARCH" plus an $8,900 final bridge (the website says "from $17,900"); one veneers ad. | No matching ads found (0, any time). |
| NYSC | Relevant ads observed. 6 Invisalign ads, none for implants. One "My Smile Centre" veneers ad has an uncertain advertiser identity. | Relevant ads observed, but outside the window. OneCore Media Corp.: 3 implant ads, last shown Nov 2025; 0 in the window. |
| Gajjar | Relevant ads observed. 2 general-dentistry ads started 12 Oct. A 2024 election ad was excluded. | Relevant ads observed, but outside the window. Optio Publishing Inc.: 15 ads any time, 0 in the window. |
| Dundas | No matching ads found. | No matching ads found. |
| Bond | No matching ads found ("Bond Street Dental"). | Advertiser identity uncertain. Passion Dental Group Inc: 26 in the window, all opened; 3 about implants, including "Dental Implant At $1,599". |

No spend, reach, targeting or results are recorded.

## 5. Preview
These checks passed:
- noindex and canonical
- one H1
- no overflow at 1280 or 390
- all 9 anchors
- the mobile menu
- comparison cards on mobile
- the CSV link (38 rows)
- exactly 3 tests
- 12 takeaways (2 pending)
- 70 Tab stops, each with a visible focus outline
- Enter opens and closes all 6 summaries
- 0 contrast failures in light mode
- the CTA keeps `entry=research_dental` and `contact_view` fires with it, without submitting

**Observed problem:** in dark mode the hero button "See the five clinics" has grey text on orange, a contrast of 1.08:1. The cause is the shared rule `.msi.msi a { color: var(--text-muted) }` overriding `.btn-primary`.

## 6. Unresolved gaps
See `unresolved_gaps` in the JSON. In short:
- the Dundas and Bond websites, their handles, and the Bond identity as stated on the site itself;
- Gajjar's Instagram;
- complete (not probable) Instagram coverage, and plays;
- the Studio B price conflict;
- Bond Meta searches under other names;
- the dark-mode button contrast;
- the Apps Script redeploy and founder review.
