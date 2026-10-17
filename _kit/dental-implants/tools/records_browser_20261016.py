#!/usr/bin/env python3
"""Write editions/001/ads.json and social.json from the browser-20261016 evidence batch.

    python3 tools/records_browser_20261016.py

The classification decisions (attribution confidence, treatment, window relation, cover notes) are written out below so they
can be reviewed; everything else is read from the stored logs. build.py re-checks every record against the same logs.
Run once per evidence batch; a later batch gets its own script so earlier decisions stay on record.
"""
import json, re
from pathlib import Path

ED = Path(__file__).resolve().parent.parent / "editions" / "001"
B = "browser-20261016"
RAW = ED / "raw" / B
jl = lambda p: [json.loads(l) for l in (RAW / p).read_text().splitlines() if l.strip()]
LOAD = {r["tag"]: r for r in jl("logs/load_log.jsonl")}
META = json.loads((RAW / "logs/meta_parsed.json").read_text())
GCR = {r["tag"]: r for r in jl("logs/google_creatives.jsonl")}
GWIN = {r["alias"]: r for r in jl("logs/google_window.jsonl")}
BOND = json.loads((RAW / "logs/bond_google_creatives.json").read_text())
IGP = {r["shortcode"]: r for r in jl("logs/ig_posts.jsonl")}
MON = {m: i for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}

def iso(s):  # "Jan 21, 2026" -> 2026-01-21
    m = re.match(r"([A-Z][a-z]{2}) (\d{1,2}), (\d{4})", s.strip()); return f"{m[3]}-{MON[m[1]]:02d}-{int(m[2]):02d}"

WIN = ("2026-09-16", "2026-10-15")
def meta_relation(status, start, end=None):
    if status == "Inactive": return "historical_before_window" if end and end < WIN[0] else "ended_in_or_after_window"
    if start < WIN[0]: return "active_at_observation_started_before_window"
    if start <= WIN[1]: return "active_at_observation_started_in_window"
    return "started_after_window"

# Reviewed decisions for each Meta ad card (library id -> clinic, attribution, treatment, implant relevance, basis)
META_REVIEW = {
 "26002231369395543": ("studiob", "supported", "implant_full_arch", "yes", "Facebook page \"studiobdental\" has the same name as the Instagram account linked from studiobdental.ca; the text names Dr. B and an All-on-X package. Destination is Messenger and the bio link, not the website."),
 "1569086177506365": ("studiob", "supported", "veneers", "no", "Same page \"studiobdental\"; text names Studio B Dental."),
 "2023758354972864": ("nysc", "supported", "invisalign", "no", "Page named North York Smile Centre; text names North York."),
 "2192204594975485": ("nysc", "supported", "invisalign", "no", "Page named North York Smile Centre; display domain NORTHYORKSMILECENTRE.FREESMILECONSULT.CLINIC is not the clinic's website."),
 "1089709797174359": ("nysc", "supported", "invisalign", "no", "Page named North York Smile Centre."),
 "1151702920869512": ("nysc", "supported", "invisalign", "no", "Page named North York Smile Centre; display domain NORTHYORKSMILECENTRE.FREESMILECONSULT.CLINIC."),
 "28406200442344726": ("nysc", "supported", "invisalign", "no", "Page named North York Smile Centre."),
 "1085671074238286": ("nysc", "supported", "invisalign", "no", "Page named North York Smile Centre; display domain NORTHYORKSMILECENTRE.FREESMILECONSULT.CLINIC."),
 "4315299038726791": ("nysc", "uncertain", "veneers", "no", "Page \"My Smile Centre\". The @northyork.smilecentre Instagram bio names @mysmilecentre as head office and smile-by-design.ca names Dr. Jerry Jesin, who appears in the ad, but the ad does not name the North York location."),
 "2950094802022907": ("gajjar", "confirmed", "general_dentistry", "no", "Page named Dr. Neil J. Gajjar, Associates & Specialists; display destination DRGAJJAR.COM, the clinic's official domain."),
 "1911245073618549": ("gajjar", "confirmed", "general_dentistry", "no", "Same page and destination as 2950094802022907."),
 "512522885103391": ("gajjar", "confirmed", "not_treatment_marketing", "no", "Election notice for the RCDSO council, paid for by the clinic. Not treatment marketing; the library's spend and audience figures are deliberately not recorded."),
}
META_SEARCH = {"studiob": ["meta-studiob", "meta-studiob-2"], "nysc": ["meta-nysc", "meta-nysc-sbd"], "gajjar": ["meta-gajjar-dr", "meta-gajjar"],
               "dundas": ["meta-dundas"], "bond": ["meta-bond"]}
TERMS = {"meta-studiob": "Studio B Dental", "meta-studiob-2": "Studio B Dental", "meta-nysc": "North York Smile Centre", "meta-nysc-sbd": "Smile By Design",
         "meta-gajjar-dr": "Dr. Neil J. Gajjar", "meta-gajjar": "Gajjar Dentistry", "meta-dundas": "Dundas East Dental", "meta-bond": "Bond Street Dental"}
DOMAIN = {"studiob": "studiobdental.ca", "nysc": "smile-by-design.ca", "gajjar": "drgajjar.com", "dundas": "dundaseastdental.com", "bond": "dentalimplantsclinic.ca"}

# Short descriptions for implant records shown on the page (no quoted dashes; figures must appear in the record text)
SUMMARY = {"26002231369395543": "All-on-X package with tooth extractions, four or more implants and a non-removable temporary bridge placed the same day, at $17,990 per arch; a final bridge 4 to 6 months later is listed separately at $8,900"}
WHY = {
 "DdsKsuVM8b4": "The one post in the Studio B Dental sample whose caption is about implants: a patient testimonial tagged with zirconia implant hashtags, ending with a direct message prompt for a complimentary consultation.",
 "Dd9BwhfFG0x": "A patient testimonial reel in which, by the caption, a patient describes receiving implants from Dr. Eisen; the caption adds that outcomes vary and that a consultation decides which options suit a patient.",
 "DdtiGIPlrNt": "An All-on-X question reel: the caption says people who already wear dentures may still be candidates and explains why bone levels matter, then invites registration for a free webinar.",
 "DdrBZDBHDHg": "An invitation to a live All-on-X webinar with Dr. Rob Eisen on 30 September at 8:00 PM Eastern Time, for people with multiple missing or failing teeth.",
}

# Google creatives outside the Bond window list: transcribed from each creative's screenshot
GOOGLE_REVIEW = {
 "google-nysc-cr1": ("supported", "implant", "yes", "My Smile Centre, promo.mysmilecentre.ca: \"Dental Implant Cost - Toronto Dental Implant Clinic\"", "Returned by the domain search for smile-by-design.ca; advertiser OneCore Media Corp., which the clinic website credits; display name is the head-office brand My Smile Centre."),
 "google-nysc-cr2": ("supported", "implant_full_arch", "yes", "My Smile Centre, promo.smile-by-design.ca/allon4: \"Toronto All on Four Dentistry - All On Four Centre Clinic\"", "Display URL is on the clinic's official domain; advertiser OneCore Media Corp."),
 "google-nysc-cr3": ("supported", "implant", "yes", "My Smile Centre, promo.smile-by-design.ca: \"Same-Day Dental Implants - Chipped, cracked, broken teeth\"", "Display URL is on the clinic's official domain; advertiser OneCore Media Corp."),
 "google-gajjar-cr1": ("confirmed", "general_dentistry", "no", "\"Conveniently Located In Mississauga\" (video)", "Returned by the domain search for drgajjar.com; advertiser Optio Publishing Inc."),
 "google-gajjar-cr2": ("confirmed", "general_dentistry", "no", "Dr. Neil J. Gajjar: \"Call (905) 564-2021\"; dental care for babies, kids, teens and adults in Mississauga", "Display name is the clinic; advertiser Optio Publishing Inc."),
 "google-gajjar-cr3": ("confirmed", "general_dentistry", "no", "Location ad: Dr. Neil J. Gajjar, dental clinic, Mississauga", "Location asset names the clinic; advertiser Optio Publishing Inc."),
 "google-gajjar-cr4": ("confirmed", "general_dentistry", "no", "\"Conveniently Located In Mississauga\" (video)", "Returned by the domain search for drgajjar.com; advertiser Optio Publishing Inc."),
}

# Bond: the 26 creatives shown in the window. basis: name = names Bond Street Dental; street = "Bond Street" location line;
# address = "113 Bond St" in the creative text; domain = only the domain or the "Dental Implants Clinic" display name.
BOND_REVIEW = {
 1: ("address", "implant", "yes", "Advanced Dental Implants; dentalimplantsclinic.ca, Toronto, 113 Bond St"),
 2: ("domain", "implant_full_arch", "yes", "Dental Implants Clinic: \"Dental Implants Clinic - Voted best dentist in Toronto\"; sitelinks \"All On 4 Dental Implants\", \"Quality Dental Implants\""),
 3: ("name", "general_dentistry", "no", "Location asset: Bond Street Dental - Toronto"),
 4: ("street", "general_dentistry", "no", "Dental Implants Clinic: \"Open 7 Days a Week - Evening & Weekend\"; Bond Street"),
 5: ("domain", "general_dentistry", "no", "\"Do root canals hurt, and what happens during the procedure?\""),
 6: ("street", "general_dentistry", "no", "Dental Implants Clinic: \"Dental Clinic Toronto\"; Bond Street; cleaning, exam and X-ray offer"),
 7: ("name", "emergency", "no", "Map ad: Bond Street Dental; \"Emergency Dentist Toronto | Same-Day Urgent\""),
 8: ("street", "general_dentistry", "no", "Dental Implants Clinic: \"Toronto Dental Clinic - Bon...\"; Bond Street"),
 9: ("street", "cosmetic", "no", "Dental Implants Clinic: \"Best Periodontist in Toronto - Cosmetic Dental Services\"; Bond Street"),
 10: ("domain", "general_dentistry", "no", "\"Complete Oral Health Plans - Book Your Appointment Today\""),
 11: ("domain", "general_dentistry", "no", "\"Need A Dentist Today?\""),
 12: ("domain", "unclear", "unclear", "Image carousel with no readable headline"),
 13: ("domain", "cosmetic", "no", "\"Get cosmetic dentistry - Same-Day Appointment Available\"; text names \"Bentway\""),
 14: ("domain", "general_dentistry", "no", "\"Family Dentist Toronto - Appointments Within 20 Minutes\" (extractions, wisdom teeth)"),
 15: ("domain", "root_canal", "no", "\"Same-Day Root Canal Visit - Affordable Root Canal\""),
 16: ("domain", "implant", "yes", "Dental Implants Clinic: \"Dental Implant At $1,599 - Affordable Implants at $1,599\"; no conditions visible in the creative"),
 17: ("street", "general_dentistry", "no", "Dental Implants Clinic: \"Dental Care When Needed - Affordable Dental Services\"; Bond Street"),
 18: ("domain", "general_dentistry", "no", "\"Stress Free Dental Visits\""),
 19: ("domain", "sedation", "no", "\"Sedation Dentistry Toronto\""),
 20: ("domain", "general_dentistry", "no", "\"Dentist appointment today - Dentist Toronto\""),
 21: ("domain", "general_dentistry", "no", "\"Call Us Today to Schedule\""),
 22: ("street", "whitening", "no", "Dental Implants Clinic, /teeth_whitening: \"Zoom Whitening for $349 - Same-Day Whitening\"; Bond Street"),
 23: ("name", "general_dentistry", "no", "Location asset: Bond Street Dental"),
 24: ("name", "general_dentistry", "no", "\"Bond Street Dental\"; display \"bond street dental/\""),
 25: ("name", "general_dentistry", "no", "Image ad: Bond Street Dental"),
 26: ("domain", "general_dentistry", "no", "Dental Implants Clinic: \"Gentle Dental Care - Vote...\""),
}
BASIS = {"name": "The creative names Bond Street Dental.", "street": "The creative's location line reads Bond Street.", "address": "The creative text gives the address 113 Bond St.",
         "domain": "Only the domain or the display name \"Dental Implants Clinic\" is shown; nothing in the creative names Bond Street Dental."}

def shot(rel):
    assert (RAW / rel).exists(), rel
    return f"raw/{B}/{rel}"

def meta_records(alias):
    seen, out = set(), []
    for tag in META_SEARCH[alias]:
        for a in META[tag]["ads"]:
            if a["library_id"] in seen or a["library_id"] not in META_REVIEW: continue
            seen.add(a["library_id"])
            cl, conf, treat, impl, basis = META_REVIEW[a["library_id"]]
            assert cl == alias
            if a["dates"].startswith("Started running on "): start, end = iso(a["dates"][19:]), None
            else: s, e = a["dates"].split(" - "); start, end = iso(s), iso(e)
            adv = a["advertiser"] or ("Dr. Neil J. Gajjar, DDS - RCDSO Council Candidate" if a["library_id"] == "512522885103391" else None)
            text = a["text"] if treat != "not_treatment_marketing" else ""
            out.append({"id": "meta-" + a["library_id"], "platform": "meta", "url": a["library_url"],
                "advertiser": {"name": adv, "platform_verified": None},
                "attribution": {"clinic": alias, "confidence": conf, "basis": basis},
                "treatment": {"category": treat, "implant_related": impl},
                "observed_utc": LOAD[tag]["started_utc"], "observed_in": tag,
                "platform_dates": {"status_at_observation": a["status"].lower(), "started": start, "ended": end, "last_shown": None,
                                   "basis": "Meta Ad Library \"Started running on\" date; the library does not show day-by-day delivery"},
                "window_relation": meta_relation(a["status"], start, end),
                "grouped_ads": 2 if a["variants"] and "2 ads use" in a["variants"] else 1,
                "text": text, "text_basis": f"pages/{tag}.txt" if text else "not recorded (election notice)",
                "display_domain": sorted(set(a["display_domain"])), "screenshot": shot(f"shots/{tag}.png")})
            if a["library_id"] in SUMMARY: out[-1]["summary"] = SUMMARY[a["library_id"]]
    return out

def meta_check(alias, status, summary, limits):
    tags = META_SEARCH[alias]
    return {"status": status, "searched_at": LOAD[tags[0]]["started_utc"],
            "searches": [{"log_tag": t, "url": LOAD[t]["requested_url"], "terms": TERMS[t], "match": "exact phrase", "filters": "Country Canada; all ads; active and inactive",
                          "searched_utc": LOAD[t]["started_utc"], "result": META[t]["result_line"], "screenshot": shot(f"shots/{t}.png")} for t in tags],
            "summary": summary, "limits": limits, "records": meta_records(alias), "evidence": [f"raw/{B}/logs/meta_parsed.json"]}

def gtext(n): return int(re.match(r"(\d+)", n)[1])
def google_check(alias, status, summary, limits, records, advertisers):
    a = LOAD["google-" + alias]; w = GWIN[alias]
    anytime = gtext(re.search(r"\n(\d+ ads?)\n", (RAW / f"pages/google-{alias}.txt").read_text())[1])
    return {"status": status, "searched_at": a["started_utc"],
            "searches": [{"log_tag": "google-" + alias, "kind": "any_time", "url": a["requested_url"], "terms": DOMAIN[alias], "filters": "Region Canada; any time",
                          "searched_utc": a["started_utc"], "result_count": anytime, "screenshot": shot(f"shots/google-{alias}.png")},
                         {"log_tag": "google_window:" + alias, "kind": "window", "url": w["url"], "terms": DOMAIN[alias], "filters": "Region Canada; custom dates Sep 16 to Oct 15, 2026 (Pacific Time)",
                          "searched_utc": w["checked_utc"], "result_count": gtext(w["count_line"]), "date_label": w["date_label"], "screenshot": shot(f"shots/google-{alias}-window.png")}],
            "advertisers": advertisers, "summary": summary, "limits": limits, "records": records, "evidence": [f"raw/{B}/logs/google_window.jsonl"]}

def google_rec(tag, alias, last_shown_iso, fmt, url, review, adv, observed):
    conf, treat, impl, text, basis = review
    rel = "shown_in_window" if WIN[0] <= last_shown_iso else "historical_before_window"
    return {"id": "google-" + url.split("/creative/")[1].split("?")[0], "platform": "google", "url": url.split("?")[0] + "?region=CA",
            "advertiser": {"name": adv, "platform_verified": True}, "attribution": {"clinic": alias, "confidence": conf, "basis": basis},
            "treatment": {"category": treat, "implant_related": impl}, "observed_utc": observed, "observed_in": tag,
            "platform_dates": {"status_at_observation": None, "started": None, "ended": None, "last_shown": last_shown_iso,
                               "basis": "Google Ads Transparency Center \"Last shown\" date (Pacific Time); first shown is not displayed"},
            "window_relation": rel, "format": fmt, "text": text, "summary": text, "text_basis": "transcribed from the creative screenshot (first variation only)",
            "screenshot": shot(f"shots/{tag}.png")}

def gcr_meta(tag):
    r = GCR[tag]
    ls = re.search(r"Last shown: ([^|]+)", r["main"])[1].strip(); fm = re.search(r"Format: ([^|]+)", r["main"])[1].strip()
    return iso(ls), fm, r["url"], r["started_utc"]

ads = {"edition": "001", "schema": 2, "batch": B,
 "note": "Advertising evidence, one record per ad card or creative, with each dimension kept separate: platform, advertiser and attribution confidence (confirmed, supported, uncertain), treatment relevance, observation time, platform-reported dates and the relation to the fixed edition window. Status per clinic and platform: relevant_ads_observed, no_matching_ads_found, advertiser_uncertain, access_blocked, not_checked. A documented search with no result does not show that a clinic never advertises. Nothing here estimates spend, reach, targeting or results, and historical ads are never described as current.",
 "collected_with": "Logged-out headless Chromium in the Claude Code cloud container, 16 October 2026 (see raw/browser-20261016/provenance.json). Not the founder's Chrome.",
 "checks": {}}
C = ads["checks"]
C["studiob"] = {
 "meta": meta_check("studiob", "relevant_ads_observed", "Two ads from the page \"studiobdental\", whose name matches the clinic's Instagram account (supported, not confirmed), were running when checked, the day after the window ended: an All-on-X offer and a veneers offer. Both library start dates are before the window, and the library does not show whether either ran during it.",
                    ["Keyword search for the exact phrase only.", "The library shows a start date and current status, not delivery during the window."]),
 "google": google_check("studiob", "no_matching_ads_found", "No ads found for the domain studiobdental.ca at any time or in the window.",
                        ["Domain search only; an ad pointing to another domain, or one Google does not list, would not appear.", "Not proof that the clinic never advertises on Google."], [], [])}
C["nysc"] = {
 "meta": meta_check("nysc", "relevant_ads_observed", "Six ad cards from the page North York Smile Centre, all one Invisalign offer and none about implants, were running when checked after the window. Five have library start dates inside the window and one on 15 September, the day before it. A seventh card, a veneers ad from the page My Smile Centre, is kept separate because its link to the North York clinic is uncertain. The exact phrase \"Smile By Design\" found no ads.",
                    ["The library reported about 12 results; seven cards were shown, three of them grouping two ads.", "Keyword search for exact phrases only."]),
 "google": google_check("nysc", "relevant_ads_observed", "Three implant ads from OneCore Media Corp. point to smile-by-design.ca, last shown in November 2025. They are historical examples outside this edition's window; no ad for the domain was shown in the window.",
                        ["Domain search only.", "Only the first variation of each creative was read."],
                        [google_rec(t, "nysc", *gcr_meta(t)[:3], GOOGLE_REVIEW[t], "OneCore Media Corp.", gcr_meta(t)[3]) for t in ("google-nysc-cr1", "google-nysc-cr2", "google-nysc-cr3")],
                        [{"name": "OneCore Media Corp.", "verified": True, "relation": "Marketing provider credited on smile-by-design.ca (observation ny-credit); a published association, not a confirmed contract."}])}
C["gajjar"] = {
 "meta": meta_check("gajjar", "relevant_ads_observed", "Two ad cards from the page Dr. Neil J. Gajjar, Associates & Specialists, which links to the clinic's website (confirmed), started on 12 October, inside the window, were running when checked and promote general dental care in Mississauga, not implants. An inactive 2024 election notice is recorded but is not treatment marketing. \"Gajjar Dentistry\" found no ads.",
                    ["The library reported about 6 results; three cards were shown, two of them grouping two ads.", "Keyword search for exact phrases only."]),
 "google": google_check("gajjar", "relevant_ads_observed", "Fifteen ads from Optio Publishing Inc. point to drgajjar.com; none was shown in the window. The four opened were last shown on 31 May 2026 and promote general dental care. They are historical evidence only.",
                        ["Eleven of the fifteen any-time creatives were not opened; none of the fifteen was shown in the window.", "Domain search only."],
                        [google_rec(t, "gajjar", *gcr_meta(t)[:3], GOOGLE_REVIEW[t], "Optio Publishing Inc.", gcr_meta(t)[3]) for t in ("google-gajjar-cr1", "google-gajjar-cr2", "google-gajjar-cr3", "google-gajjar-cr4")],
                        [{"name": "Optio Publishing Inc.", "verified": True, "relation": "Advertiser account running ads to the clinic's official domain; its relationship to the clinic is not stated."}])}
C["dundas"] = {
 "meta": meta_check("dundas", "no_matching_ads_found", "No ads matched the exact phrase \"Dundas East Dental\".",
                    ["Exact phrase only; a page under another name, such as a dentist's name, would not appear.", "Not proof that the clinic never advertises on Meta."]),
 "google": google_check("dundas", "no_matching_ads_found", "No ads found for the domain dundaseastdental.com at any time or in the window.",
                        ["Domain search only.", "Not proof that the clinic never advertises on Google."], [], [])}
bond_recs = []
for c in BOND:
    basis, treat, impl, text = BOND_REVIEW[c["n"]]
    conf = "uncertain" if basis == "domain" else "supported"
    r = google_rec(f"bond-google/cr{c['n']:02d}", "bond", iso(c["last_shown"]), c["format"], c["url"], (conf, treat, impl, text, BASIS[basis]), "Passion Dental Group Inc", c["checked_utc"])
    r["attribution"]["creative_evidence"] = basis
    r["variations"] = c["variations"]
    bond_recs.append(r)
C["bond"] = {
 "meta": meta_check("bond", "no_matching_ads_found", "No ads matched the exact phrase \"Bond Street Dental\".",
                    ["Exact phrase only. The Google display name \"Dental Implants Clinic\" and the advertiser \"Passion Dental Group\" were not searched on Meta.", "Not proof that the clinic never advertises on Meta."]),
 "google": google_check("bond", "advertiser_uncertain",
   "Twenty-six ads from the verified advertiser Passion Dental Group Inc pointed to dentalimplantsclinic.ca and were shown in the window, by Google's date filter in Pacific Time. Twelve name Bond Street Dental or show a Bond Street location or address; fourteen show only the domain or the name \"Dental Implants Clinic\". Three are about implants. Because the website could not be read, the link between the domain, the advertiser and Bond Street Dental is not confirmed.",
   ["The window filter uses Pacific Time, three hours behind Toronto at each end.", "Only the first variation of each creative was read.", "Creatives may vary by location."],
   bond_recs,
   [{"name": "Passion Dental Group Inc", "verified": True, "relation": "uncertain: the advertiser's relationship to Bond Street Dental is not stated in any evidence read; ads are not attributed to Bond Street Dental as a group"}])}
C["bond"]["google"]["identity"] = {"domain_is_bond_street_dental": "uncertain", "basis": "Supported by Google ad records only (location assets and names in 12 creatives); not verified on the official site, which showed a Cloudflare security check."}
(ED / "ads.json").write_text(json.dumps(ads, indent=1, ensure_ascii=False) + "\n")

# ---------- Instagram ----------
POSTS = {  # shortcode: (alias, topic, treatment, implant relevance, cta, cover note)
 "Dd6yzieDLQG": ("studiob", "Cosmetic dentist trend post", "veneers", "no", "None in the caption", "partly visible behind Instagram's sign-up prompt: Studio B Dental branding and veneer text"),
 "Dd3yAGBBrsW": ("studiob", "Behind the scenes at the clinic", "clinic_culture", "no", "None in the caption", "not visible, because the video did not load in the logged-out view"),
 "DdsKsuVM8b4": ("studiob", "Patient testimonial; hashtags name zirconia implants", "implant", "yes", "Direct message to book a complimentary consultation", "partly visible behind the sign-up prompt: a branded quote card headed \"REAL PATIENT. REAL RESULTS.\""),
 "DdrKB7AhD3b": ("studiob", "Process and transformation; hashtags include implant surgery and porcelain veneers", "unclear", "unclear", "Bio link to book a complimentary consultation", "not visible, because the video did not load in the logged-out view"),
 "Dd9BwhfFG0x": ("nysc", "Implant patient testimonial with Dr. Eisen", "implant", "yes", "Contact the clinic to book a consultation", "not visible, because the video did not load in the logged-out view"),
 "Dd6dymzkcvJ": ("nysc", "Emergency dentistry", "emergency", "no", "Contact the clinic for an emergency appointment", "partly visible behind the sign-up prompt: a person holding their jaw, emergency headline"),
 "DdtiGIPlrNt": ("nysc", "All-on-X question: dentures and bone levels", "implant_full_arch", "yes", "Register for a free webinar", "not visible, because the video did not load in the logged-out view"),
 "DdrBZDBHDHg": ("nysc", "All-on-X live webinar on 30 September with Dr. Rob Eisen", "implant_full_arch", "yes", "Register for the webinar", "partly visible behind the sign-up prompt: \"UPCOMING LIVE WEBINAR\", \"ALL-ON-X DENTAL IMPLANTS\""),
 "DdbhpOgIMJE": ("nysc", "Invisalign wear time", "invisalign", "no", "None in the caption", "partly visible behind the sign-up prompt: \"MYTH OR FACT\" Invisalign card"),
}
HANDLE = {"studiob": "studiobdental", "nysc": "northyork.smilecentre"}
posts = []
for sc, (alias, topic, treat, impl, cta, cover) in POSTS.items():
    r = IGP[sc]
    m = re.match(r"([\d,]+) likes, ([\d,]+) comments", r["og_desc"])
    cap = re.sub(r'^.*? on Instagram: "', "", r["og_title"]).rstrip('"').split("\n")[0].strip()
    posts.append({"shortcode": sc, "url": r["url"], "clinic": alias, "owner": r["handle"], "collaboration": "none_shown",
                  "format": "reel" if "/reel/" in r["url"] else "image_or_carousel", "published_utc": r["times"][0]["dt"],
                  "published_basis": "the post page's <time datetime> value", "observed_utc": r["checked_utc"],
                  "caption_first_line": cap, "topic": topic, "treatment": treat, "implant_relevance": impl, "cta": cta,
                  "cover": cover, **({"why": WHY[sc]} if sc in WHY else {}), "analysis_basis": "caption and visible cover only; videos not watched",
                  "metrics": {"likes": int(m[1].replace(",", "")), "comments": int(m[2].replace(",", "")), "plays": None,
                              "plays_status": "missing: not shown to a logged-out visitor", "basis": "public counts at observation; post ages differ"},
                  "ai_content_label": r["page_flags"]["ai_content_label"], "video_watched": False, "screenshot": shot(f"shots/ig/{sc}.png")})
posts.sort(key=lambda p: (p["clinic"], p["published_utc"]))
social = {"edition": "001", "platform": "Instagram", "schema": 2, "status": "partial_sample", "batch": B,
 "collection_started_utc": LOAD["ig-studiobdental"]["started_utc"],
 "method": "Logged-out headless Chromium: one load of each verified profile, then one load of each grid item dated inside the window. No login, cookies or paid collection. Not the founder's Chrome.",
 "reason": "Partial sample. The two readable profiles showed a logged-out grid of 12 items that spans the window, but completeness was not confirmed against a logged-in view or a collector; @gajjardentistry was refused (HTTP 429); Dundas East Dental and Bond Street Dental have no verified handle. A first logged-out request on 2026-10-16T18:19:18Z had also been refused (HTTP 429).",
 "public_reason": "Instagram evidence in this draft is an incomplete sample: nine posts observed on two accounts in a logged-out browser. The third account refused the request, and two clinics have no verified account yet. These are observed posts, not a complete record of what the accounts published, so no frequency or totals for the window are given.",
 "handles": {
  "studiob": {"handle": "studiobdental", "status": "verified_link", "source_obs": "sb-ig", "profile_checked_utc": LOAD["ig-studiobdental"]["started_utc"], "profile_http": 200,
              "note": "Display name on the profile is Charles Botbol; the bio links studiobdental.ca. The account is the one the clinic website links."},
  "nysc": {"handle": "northyork.smilecentre", "status": "verified_link", "source_obs": "ny-ig", "profile_checked_utc": LOAD["ig-northyork.smilecentre"]["started_utc"], "profile_http": 200,
           "note": "Bio names @mysmilecentre as head office and links smile-by-design.ca."},
  "gajjar": {"handle": "gajjardentistry", "status": "verified_link", "source_obs": "gj-ig", "profile_checked_utc": LOAD["ig-gajjardentistry"]["started_utc"], "profile_http": 429},
  "dundas": {"handle": None, "status": "not_verified", "reason": "Official website showed a \"VPN or Proxy Detected\" panel; no handle may be assumed."},
  "bond": {"handle": None, "status": "not_verified", "reason": "Official website showed a Cloudflare security check; no handle may be assumed."}},
 "coverage": {
  "studiob": {"status": "probable_not_confirmed", "grid_items_visible": 12, "posts_read": 4, "basis": "The logged-out grid showed three items first that are older than the window (likely pinned), then items running from about 12 August to 30 September 2026 by dates estimated from post identifiers. The four items estimated inside the window were opened and their dates read from the post pages. No item estimated at 1 to 15 October appeared."},
  "nysc": {"status": "probable_not_confirmed", "grid_items_visible": 12, "posts_read": 5, "basis": "The logged-out grid ran from about 14 August to 1 October 2026 by dates estimated from post identifiers. The five items estimated inside the window were opened and their dates read from the post pages. No item estimated at 2 to 15 October appeared."},
  "gajjar": {"status": "blocked", "grid_items_visible": None, "posts_read": 0, "basis": "Profile request refused: HTTP 429 and a login redirect at 19:11 UTC on 16 October 2026; not retried."},
  "dundas": {"status": "handle_not_verified", "grid_items_visible": None, "posts_read": 0, "basis": "No verified handle."},
  "bond": {"status": "handle_not_verified", "grid_items_visible": None, "posts_read": 0, "basis": "No verified handle."}},
 "posts": posts}
(ED / "social.json").write_text(json.dumps(social, indent=1, ensure_ascii=False) + "\n")
print("ads records:", {a: {p: len(x[p]["records"]) for p in x} for a, x in C.items()}, "posts:", len(posts))
