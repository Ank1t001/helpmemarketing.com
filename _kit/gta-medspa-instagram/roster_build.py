#!/usr/bin/env python3
"""Validate a Google Maps discovery crawl into the edition roster (GTA MedSpa Index).

Input : work/listings.json (one record per Google business listing)
Output: editions/NNN/ roster_eligible.json, roster_unresolved.json, exclusions.json,
        sampling.json, discovery.json, and roster.json (all eligible accounts, or the sample).

Steps: normalise and dedupe listings -> business eligibility -> GTA geography from the
physical address (coordinates only when the address is missing) -> Instagram handle
normalisation and verification -> one record per unique account (branches counted once)
-> cap with a seeded, region-proportional sample if more than --cap accounts remain.
Selection never looks at followers, engagement, discovery order or expected ranking.
"""
import argparse, difflib, gzip, json, math, random, re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).parent

# municipality -> (region, lat, lng); used for address text and as a coordinate fallback
MUNI = {
    "Toronto": ("Toronto", 43.70, -79.40),
    "Mississauga": ("Peel", 43.589, -79.644), "Brampton": ("Peel", 43.731, -79.762),
    "Caledon": ("Peel", 43.87, -79.95),
    "Vaughan": ("York", 43.837, -79.508), "Markham": ("York", 43.856, -79.337),
    "Richmond Hill": ("York", 43.883, -79.44), "Newmarket": ("York", 44.056, -79.461),
    "Aurora": ("York", 44.006, -79.45), "King": ("York", 43.97, -79.62),
    "Whitchurch-Stouffville": ("York", 43.97, -79.24), "East Gwillimbury": ("York", 44.1, -79.45),
    "Georgina": ("York", 44.3, -79.43),
    "Pickering": ("Durham", 43.84, -79.09), "Ajax": ("Durham", 43.85, -79.02),
    "Whitby": ("Durham", 43.875, -78.94), "Oshawa": ("Durham", 43.897, -78.865),
    "Clarington": ("Durham", 43.93, -78.69), "Uxbridge": ("Durham", 44.11, -79.12),
    "Scugog": ("Durham", 44.1, -78.94), "Brock": ("Durham", 44.4, -79.1),
    "Oakville": ("Halton", 43.447, -79.683), "Burlington": ("Halton", 43.325, -79.8),
    "Milton": ("Halton", 43.518, -79.877), "Halton Hills": ("Halton", 43.65, -79.95),
}
ALIAS = {  # place names inside the five regions that map to a municipality
    "Old Toronto": "Toronto", "Etobicoke": "Toronto", "North York": "Toronto", "Scarborough": "Toronto",
    "East York": "Toronto", "York": "Toronto", "Downsview": "Toronto",
    "Bolton": "Caledon", "Palgrave": "Caledon", "Caledon East": "Caledon", "Inglewood": "Caledon",
    "Woodbridge": "Vaughan", "Thornhill": "Vaughan", "Maple": "Vaughan", "Concord": "Vaughan",
    "Kleinburg": "Vaughan", "Unionville": "Markham", "Stouffville": "Whitchurch-Stouffville",
    "Whitchurch Stouffville": "Whitchurch-Stouffville", "King City": "King", "Nobleton": "King",
    "Schomberg": "King", "Sharon": "East Gwillimbury", "Holland Landing": "East Gwillimbury",
    "Mount Albert": "East Gwillimbury", "Keswick": "Georgina", "Sutton West": "Georgina",
    "Sutton": "Georgina", "Pefferlaw": "Georgina", "Bowmanville": "Clarington", "Courtice": "Clarington",
    "Newcastle": "Clarington", "Orono": "Clarington", "Port Perry": "Scugog", "Cannington": "Brock",
    "Beaverton": "Brock", "Georgetown": "Halton Hills", "Acton": "Halton Hills",
}
# places seen in the crawl that are outside the five regions
OUTSIDE = {"Barrie", "Hamilton", "Stoney Creek", "Dundas", "Ancaster", "Waterloo", "Kitchener", "Cambridge",
           "Guelph", "Bradford", "Bradford West Gwillimbury", "Innisfil", "Innisfil Beach", "Alliston",
           "Midland", "Peterborough", "Lindsay", "Brantford", "Puslinch", "Millbrook", "Port Hope",
           "Ottawa", "Fenelon Falls", "Cookstown", "Zephyr", "Ridgeway", "Port Dover", "Port Colborne"}

CLINIC_PRIMARY = {"Medical spa"}
AESTHETIC_PRIMARY = {"Skin care clinic", "Laser hair removal service", "Cosmetics industry",
                     "Plastic surgeon", "Dermatologist", "Esthetics service"}
MEDICAL_PRIMARY = {"Medical clinic", "Medical Center", "Doctor", "Medical office", "Walk-in clinic",
                   "Family practice physician", "Cosmetic surgeon", "Surgeon"}
SOFT_PRIMARY = {"Beauty salon", "Spa", "Facial spa", "Health spa", "Wellness center",
                "Health and beauty shop", "Spa and health club", "Naturopathic practitioner",
                "Permanent make-up clinic", "Hair removal service", "Waxing hair removal service"}
HARD_EXCLUDE = {
    "Massage therapist": "massage", "Massage spa": "massage", "Erotic massage": "massage",
    "Nail salon": "nail salon", "Hair salon": "hair salon", "Hairdresser": "hair salon",
    "Barber shop": "hair salon", "Day spa": "day spa", "Chiropractor": "chiropractic",
    "Physical therapy clinic": "physiotherapy", "Physical therapist": "physiotherapy",
    "Physiotherapist": "physiotherapy", "Dentist": "dental", "Dental clinic": "dental",
    "Acupuncture clinic": "acupuncture", "Hotel": "hotel", "Pharmacy": "pharmacy",
    "Make-up artist": "make-up artist", "Tattoo shop": "tattoo", "Gym": "gym",
}
SALONISH = {"Hair salon", "Nail salon", "Day spa", "Massage spa", "Massage therapist", "Hairdresser"}
STRONG_TITLE = re.compile(r"med[i]?[\s-]?spa|medi?cal|aesthetic|esthetic|laser|derm|botox|inject|cosmetic|rejuven|"
                          r"skin\s?(clinic|care|lab|studio)|plastic|cosmetic|filler|sculpt|clinic", re.I)
NOT_PROFILE = {"p", "reel", "reels", "explore", "stories", "accounts", "direct", "tv", "share", "about",
               "legal", "developer", "directory", "popular", "web", "instagram", "appstore", "oauth",
               "challenge", "privacy", "press", "api", "download", "sharer", "sharer.php", "tags"}
THIRD_PARTY_HANDLES = {"appstore", "facebook", "google", "squarespace", "wix", "shopify", "canva", "godaddy",
                       "wordpress", "weebly", "mindbodyinc", "fresha", "booksy", "janeapp", "vagaro",
                       "jane_app", "linktree", "meta", "tiktok", "youtube", "whatsapp", "threads"}
PLATFORM_DOMAINS = {"instagram.com", "facebook.com", "linktr.ee", "squarespace.com", "wixsite.com", "wix.com",
                    "janeapp.com", "square.site", "vagaro.com", "booksy.com", "fresha.com", "canva.com",
                    "business.site", "google.com", "mindbodyonline.com", "setmore.com", "calendly.com",
                    "cojilio.com", "glossgenius.com", "acuityscheduling.com", "myshopify.com", "godaddysites.com",
                    "weebly.com", "carrd.co", "beacons.ai", "tiktok.com", "youtube.com", "yelp.com", "clinikoapp.com"}
GENERIC = {"med", "medspa", "spa", "medical", "clinic", "aesthetics", "aesthetic", "esthetics", "skin", "skincare",
           "beauty", "laser", "the", "and", "inc", "ltd", "toronto", "mississauga", "brampton", "oakville",
           "markham", "vaughan", "ontario", "canada", "studio", "wellness", "centre", "center", "health", "care",
           "cosmetic", "cosmetics", "body", "face", "by", "of", "best", "hair", "removal", "treatment"}


def alnum(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def domain(url):
    if not url:
        return None
    try:
        h = urlparse(url if "//" in url else "//" + url).netloc.lower().split(":")[0]
    except ValueError:
        return None
    h = re.sub(r"^www\.", "", h)
    parts = h.split(".")
    if len(parts) >= 3 and parts[-2] in ("co", "com", "on") and len(parts[-1]) == 2:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:]) if len(parts) >= 2 else h


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    d = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(d))


def handles_of(rec):
    out = []
    for u in rec.get("instagrams") or []:
        m = re.search(r"instagram\.com/([^/?#\s]+)", u, re.I)
        if not m:
            continue
        h = m.group(1).lower().strip(".")
        if h in NOT_PROFILE or h in THIRD_PARTY_HANDLES or not re.fullmatch(r"[a-z0-9._]{1,30}", h):
            continue
        if h not in out:
            out.append(h)
    return out


def place_city(rec):
    """Municipality from the physical address text. Returns (name or None, outside flag)."""
    addr = rec.get("address") or ""
    m = re.search(r",\s*([^,]+),\s*(?:ON|Ontario)\b", addr)
    c = (m.group(1).strip() if m else None) or rec.get("city")
    if not c:
        return None, False
    c = re.sub(r"\s+", " ", c)
    if c in MUNI:
        return c, False
    if c in ALIAS:
        return ALIAS[c], False
    if c in OUTSIDE:
        return None, True
    return None, False


def geography(rec):
    """Region, municipality, method, note. Address first; coordinates only if the address is missing."""
    addr = rec.get("address") or ""
    loc = rec.get("location") or {}
    ll = (loc.get("lat"), loc.get("lng")) if loc.get("lat") is not None else None
    pc = (rec.get("postalCode") or "").upper()
    if addr and not re.search(r"\b(ON|Ontario)\b", addr):
        return None, None, "address", "address not in Ontario"
    city, outside = place_city(rec)
    if outside:
        return None, None, "address", "address outside the five regions"
    if city:
        if pc.startswith("M") and city != "Toronto":
            return None, None, "address", "postal code and city disagree"
        if ll and km(ll, MUNI[city][1:]) > 45:
            return None, None, "address", "coordinates disagree with address city"
        return MUNI[city][0], city, "address", ""
    if pc.startswith("M"):
        return "Toronto", "Toronto", "postal code", ""
    if ll:  # no usable address: nearest municipality centre, accepted only when close
        best = min(MUNI, key=lambda m: km(ll, MUNI[m][1:]))
        d = km(ll, MUNI[best][1:])
        if d <= 18 and 43.2 < ll[0] < 44.5 and -80.2 < ll[1] < -78.6:
            return MUNI[best][0], best, "coordinates (approximate)", f"{d:.0f} km from {best} centre"
        return None, None, "coordinates", "no address and coordinates not clearly inside a municipality"
    return None, None, "none", "no address or coordinates"


def eligibility(rec):
    prim = rec.get("categoryName") or ""
    cats = rec.get("categories") or []
    title = rec.get("title") or ""
    if rec.get("permanentlyClosed"):
        return False, "permanently closed"
    if prim in HARD_EXCLUDE:
        return False, f"not an aesthetics clinic ({HARD_EXCLUDE[prim]})"
    salonish = [c for c in cats if c in SALONISH]
    strong = bool(STRONG_TITLE.search(title))
    if prim in CLINIC_PRIMARY:
        if salonish and not strong:
            return False, "day spa or salon listing"
        return True, "medical spa category"
    if prim in AESTHETIC_PRIMARY or prim in MEDICAL_PRIMARY:
        if salonish and not strong:
            return False, "day spa or salon listing"
        if prim in MEDICAL_PRIMARY and not ("Medical spa" in cats or strong):
            return False, "general medical listing without aesthetics signal"
        return True, "aesthetics or laser clinic category"
    if "Medical spa" in cats or (prim in SOFT_PRIMARY and strong):
        if salonish and not strong:
            return False, "day spa or salon listing"
        return True, "medical spa listed as a secondary category" if "Medical spa" in cats else "clinic wording in name"
    return False, "not an aesthetics clinic (category and name)"


def name_match(handle, rec):
    h = alnum(handle)
    t = alnum(rec.get("title"))
    d = alnum((domain(rec.get("website")) or "").split(".")[0]) if domain(rec.get("website")) not in PLATFORM_DOMAINS else ""
    words = [w for w in re.findall(r"[a-z0-9]+", (rec.get("title") or "").lower()) if len(w) >= 4 and w not in GENERIC]
    if any(w in h for w in words):
        return "name"
    if d and len(d) >= 5 and (d in h or h in d) and len(h) >= 4:
        return "website"
    if h and t and difflib.SequenceMatcher(None, h, t).ratio() >= 0.62:
        return "similar"
    if h and t:
        sm = difflib.SequenceMatcher(None, h, t).find_longest_match(0, len(h), 0, len(t))
        if sm.size >= 6 and sm.size >= 0.5 * len(h) and not set(re.findall(r"[a-z]+", h)) <= GENERIC:
            return "similar"
    allw = [w for w in re.findall(r"[a-z0-9]+", (rec.get("title") or "").lower()) if w not in ("the", "and", "of", "by")]
    ini = "".join(w[0] for w in allw)
    if len(ini) >= 2 and h.startswith(ini[:2]) and len(ini) >= 2 and any(h.startswith(ini[:k]) for k in (2, 3, 4) if len(ini) >= k):
        if h.startswith(ini[:min(len(ini), 3)]) or h.startswith(ini[:2]) and len(allw) <= 3:
            return "acronym"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edition", required=True)
    ap.add_argument("--cap", type=int, default=600)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--built-at", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--root", default=str(HERE), help="kit folder holding work/ and editions/ (tests use a temp copy)")
    ap.add_argument("--full", action="store_true", help="print the whole summary instead of the compact form")
    a = ap.parse_args()
    root = Path(a.root)
    ed = root / "editions" / a.edition
    ed.mkdir(parents=True, exist_ok=True)
    listings = json.load(open(root / "work" / "listings.json"))
    ids = [r["placeId"] for r in listings]
    assert len(ids) == len(set(ids)), "placeId must be unique"

    excl = []  # exclusion log, one row per listing or account
    unresolved = []
    cand = []  # listings that passed business and geography checks
    reason_counts = Counter()
    for r in listings:
        ok, why = eligibility(r)
        if not ok:
            excl.append({"stage": "business", "placeId": r["placeId"], "title": r.get("title"), "reason": why})
            reason_counts[why] += 1
            continue
        region, muni, how, note = geography(r)
        if not region:
            why = "outside the five GTA regions or location unverified: " + note
            excl.append({"stage": "geography", "placeId": r["placeId"], "title": r.get("title"),
                         "address": r.get("address"), "reason": why})
            reason_counts["outside GTA or location unverified"] += 1
            continue
        r["_region"], r["_muni"], r["_geo"], r["_geo_note"] = region, muni, how, note
        r["_why"] = why
        cand.append(r)

    # branch identity: a physical branch is one placeId; same street + postal code merges listings
    def branch_key(r):
        if r.get("street") and r.get("postalCode"):
            return alnum(r["street"]) + alnum(r["postalCode"])
        return r["placeId"]

    # sibling-domain resolution for listings with no Instagram link in the crawl
    dom_handles = defaultdict(Counter)
    for r in cand:
        d = domain(r.get("website"))
        if d and d not in PLATFORM_DOMAINS:
            hs = handles_of(r)
            if hs:
                best = max(hs, key=lambda h: (name_match(h, r) is not None, -hs.index(h)))
                dom_handles[d][best] += 1

    acct = defaultdict(lambda: {"places": [], "alts": set()})
    for r in cand:
        hs = handles_of(r)
        how = "listing contact data"
        if not hs:
            d = domain(r.get("website"))
            if d in dom_handles and len(dom_handles[d]) == 1:
                hs = [next(iter(dom_handles[d]))]
                how = "same website domain as a branch with a linked account"
            else:
                unresolved.append({"placeId": r["placeId"], "title": r.get("title"), "address": r.get("address"),
                                   "region": r["_region"], "municipality": r["_muni"], "website": r.get("website"),
                                   "status": "account unresolved",
                                   "note": "no Instagram link in the Google listing data; not the same as having no account"})
                continue
        best = max(hs, key=lambda h: (name_match(h, r) is not None, -hs.index(h)))
        acct[best]["places"].append((r, how, name_match(best, r)))
        acct[best]["alts"].update(h for h in hs if h != best)

    # a handle linked from many listings with different names and domains is not one clinic's account
    roster, rejected = [], []
    for h, v in acct.items():
        places = v["places"]
        branches = {branch_key(p[0]): p[0] for p in places}
        titles = [p[0].get("title") or "" for p in places]
        doms = {domain(p[0].get("website")) for p in places} - {None} - PLATFORM_DOMAINS
        matches = [p[2] for p in places if p[2]]
        if not matches:
            rejected.append((h, "handle does not match the clinic name or website; verify before use", places))
            continue
        if len(branches) >= 3 and len(doms) >= 3 and len(matches) < len(places) / 2:
            rejected.append((h, "handle shared by unrelated listings", places))
            continue
        regs = {p[0]["_region"] for p in places}
        region = next(iter(regs)) if len(regs) == 1 else "Multi-region"
        munis = sorted({p[0]["_muni"] for p in places})
        nb = len(branches)
        atype = "single-location" if nb == 1 else ("chain (4 or more branches)" if nb >= 4 else "multi-location group")
        # display name: shortest listing title that matches the handle, else first title
        pick = sorted(places, key=lambda p: (p[2] is None, len(p[0].get("title") or "")))[0][0]
        name = pick.get("title") if nb == 1 else (re.split(r"\s+[-|–]\s+", pick.get("title") or "")[0].strip())
        roster.append({
            "handle": h, "name": name, "area": munis[0] if len(munis) == 1 else "Multi-location",
            "region": region, "include": True, "exclude_reason": None, "account_type": atype,
            "branches": nb, "listings": len(places), "place_ids": sorted(p[0]["placeId"] for p in places),
            "municipalities": munis, "website_domain": sorted(doms)[0] if doms else None,
            "handle_source": sorted({p[1] for p in places}),
            "verified_by": sorted({m for m in matches}),
            "geo_methods": sorted({p[0]["_geo"] for p in places}),
            "alternate_handles": sorted(v["alts"]),
        })
    unverified = []
    for h, why, places in rejected:
        for p in places:
            unverified.append({"placeId": p[0]["placeId"], "title": p[0].get("title"), "address": p[0].get("address"),
                               "region": p[0]["_region"], "linked_handle": h, "status": "account unverified",
                               "note": why})
        reason_counts["account unverified (kept apart, not ranked): " + why] += 1

    # group account and branch account of the same website domain are never both ranked
    bydom = defaultdict(list)
    for c in roster:
        if c["website_domain"]:
            bydom[c["website_domain"]].append(c)
    drop = set()
    for d, cs in bydom.items():
        for g in [c for c in cs if c["branches"] >= 2]:
            for c in cs:
                if c is not g and c["branches"] == 1 and c["handle"] not in drop and set(c["municipalities"]) <= set(g["municipalities"]):
                    drop.add(c["handle"])
    kept = []
    for c in roster:
        if c["handle"] in drop:
            excl.append({"stage": "account", "handle": c["handle"], "title": c["name"],
                         "reason": "branch account of a group account on the same website; the group account is ranked"})
            reason_counts["branch account of a group account"] += 1
        else:
            kept.append(c)
    roster = sorted(kept, key=lambda c: c["handle"])

    # sampling
    regs = ["Toronto", "Peel", "York", "Durham", "Halton", "Multi-region"]
    strata = {r: [c for c in roster if c["region"] == r] for r in regs}
    total = len(roster)
    sampling = {"required": total > a.cap, "cap": a.cap, "eligible_accounts": total,
                "seed": a.seed, "method": None, "allocation": {}, "selected": []}
    if total <= a.cap:
        selected = roster
        sampling["method"] = "no sampling: every eligible account selected"
        sampling["allocation"] = {r: {"eligible": len(strata[r]), "selected": len(strata[r])} for r in regs}
    else:
        sampling["method"] = ("stratified random sample, proportional allocation by region "
                              "(Toronto, Peel, York, Durham, Halton, Multi-region as its own stratum), "
                              "largest-remainder rounding; within a stratum handles are sorted alphabetically and "
                              "shuffled with random.Random(seed); the first n are selected; no use of followers, "
                              "engagement, discovery order or expected rank")
        quota = {r: len(strata[r]) * a.cap / total for r in regs}
        alloc = {r: int(quota[r]) for r in regs}
        rem = a.cap - sum(alloc.values())
        for r in sorted(regs, key=lambda r: (-(quota[r] - alloc[r]), r))[:rem]:
            alloc[r] += 1
        selected = []
        for r in regs:
            pool = sorted(strata[r], key=lambda c: c["handle"])
            rng = random.Random(f"{a.seed}:{r}")
            rng.shuffle(pool)
            pick = pool[:alloc[r]]
            for i, c in enumerate(pool):
                c["sample_rank_in_stratum"] = i + 1
            selected += pick
            sampling["allocation"][r] = {"eligible": len(strata[r]), "quota": round(quota[r], 2),
                                         "selected": len(pick)}
    sel_handles = sorted(c["handle"] for c in selected)
    sampling["selected"] = sel_handles
    sampling["selected_count"] = len(sel_handles)
    sampling["reserve_order"] = "within each stratum, sample_rank_in_stratum in roster_eligible.json (replacements use the next rank)"

    sel = set(sel_handles)
    for c in roster:
        c["selected"] = c["handle"] in sel
    json.dump({"built_at": a.built_at, "source": a.run_id, "frame": "Google Maps listings from 60 searches",
               "clinics": [dict(c, include=c["selected"]) for c in roster]},
              open(ed / "roster_eligible.json", "w"), indent=1, ensure_ascii=False)
    json.dump({"built_at": a.built_at, "source": a.run_id,
               "sampled_from": len(roster) if total > a.cap else None,
               "clinics": [{k: c[k] for k in ("handle", "name", "area", "region", "include", "exclude_reason",
                                              "place_ids", "account_type", "branches")}
                           for c in selected]},
              open(root / "roster.json", "w"), indent=1, ensure_ascii=False)
    json.dump(unresolved, open(ed / "roster_unresolved.json", "w"), indent=1, ensure_ascii=False)
    json.dump(unverified, open(ed / "roster_unverified.json", "w"), indent=1, ensure_ascii=False)
    json.dump(excl, open(ed / "exclusions.json", "w"), indent=1, ensure_ascii=False)
    json.dump(sampling, open(ed / "sampling.json", "w"), indent=1)
    types = Counter(c["account_type"] for c in roster)
    summary = {
        "listings": len(listings), "business_excluded": sum(1 for e in excl if e["stage"] == "business"),
        "geography_excluded": sum(1 for e in excl if e["stage"] == "geography"),
        "gta_aesthetics_listings": len(cand), "unresolved_listings": len(unresolved),
        "accounts_unverified": len(rejected), "unverified_listings": len(unverified), "branch_accounts_dropped": len(drop),
        "unique_accounts": len(roster), "account_types": dict(types),
        "regions": {r: len(strata[r]) for r in regs}, "selected": len(sel_handles),
        "exclusion_reasons": reason_counts.most_common(),
    }
    json.dump(summary, open(ed / "roster_summary.json", "w"), indent=1)
    if a.full:
        print(json.dumps(summary, indent=1))
    else:  # compact: counts and paths only; full detail stays in roster_summary.json and exclusions.json
        top = "; ".join(f"{k} {v}" for k, v in summary["exclusion_reasons"][:4])
        print(f"listings {summary['listings']} | gta aesthetics listings {summary['gta_aesthetics_listings']} | "
              f"unique accounts {summary['unique_accounts']} {summary['account_types']} | regions {summary['regions']}")
        print(f"unresolved listings {summary['unresolved_listings']} | unverified listings {summary['unverified_listings']} | "
              f"selected {summary['selected']} (cap {a.cap}, seed {a.seed}) | top reasons: {top}")
        print(f"files: {ed}/roster_summary.json, roster_eligible.json, exclusions.json, sampling.json")


if __name__ == "__main__":
    main()
