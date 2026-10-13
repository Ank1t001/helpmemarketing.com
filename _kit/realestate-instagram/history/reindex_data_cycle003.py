#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cycle 001 dataset — The Real Estate Investment Index. Scraped 2026-08-05."""

CYCLE = "001"
SCRAPED = "2026-08-05"
WINDOW = ("2026-07-06", "2026-08-05")

BRANDS = {
 "Equiton":    dict(cohort="MID",  li_foll=32152, ig_foll=18231, ig="equitoninc",
                    li="https://www.linkedin.com/company/equiton-partners",
                    igurl="https://www.instagram.com/equitoninc/", publisher=True),
 "Starlight":  dict(cohort="LARGE", li_foll=38570, ig_foll=None, ig=None,
                    li="https://www.linkedin.com/company/starlight-investments-ltd-", igurl=None),
 "Centurion":  dict(cohort="LARGE", li_foll=13859, ig_foll=None, ig=None,
                    li="https://www.linkedin.com/company/centurion-asset-mgmt", igurl=None),
 "Hazelview":  dict(cohort="LARGE", li_foll=13177, ig_foll=None, ig=None,
                    li="https://www.linkedin.com/company/hazelviewinvestments", igurl=None),
 "Skyline":    dict(cohort="MID",  li_foll=28558, ig_foll=2243, ig="skylinegroupofcompanies",
                    li="https://www.linkedin.com/company/skylinegroupofcompanies",
                    igurl="https://www.instagram.com/skylinegroupofcompanies/"),
 "Lankin":     dict(cohort="MID",  li_foll=12771, ig_foll=3994, ig="lankin_investments",
                    li="https://www.linkedin.com/company/lankin-investments",
                    igurl="https://www.instagram.com/lankin_investments/"),
 "Pier 4":     dict(cohort="BOUTIQUE", li_foll=3903, ig_foll=675, ig="pier4ltd",
                    li="https://www.linkedin.com/company/pier4ltd",
                    igurl="https://www.instagram.com/pier4ltd/"),
 "Marlin Spring": dict(cohort="BOUTIQUE", li_foll=5710, ig_foll=15021, ig="marlinspringdevelopments",
                    li="https://www.linkedin.com/company/marlin-spring-developments",
                    igurl="https://www.instagram.com/marlinspringdevelopments/"),
}


# Instagram board roster. Separate from BRANDS because the two indexes no longer
# track the same firms: Marlin Spring left the Instagram board at cycle 003 and
# McGillivray Capital entered it. The LinkedIn index still uses BRANDS.
IG_BRANDS = {
 "Skyline": dict(cohort="MID", ig_foll=2243, ig="skylinegroupofcompanies",
      igurl="https://www.instagram.com/skylinegroupofcompanies/"),
 "Equiton": dict(cohort="MID", ig_foll=18231, ig="equitoninc",
      igurl="https://www.instagram.com/equitoninc/"),
 "Lankin": dict(cohort="MID", ig_foll=3994, ig="lankin_investments",
      igurl="https://www.instagram.com/lankin_investments/"),
 "Pier 4": dict(cohort="BOUTIQUE", ig_foll=675, ig="pier4ltd",
      igurl="https://www.instagram.com/pier4ltd/"),
 "McGillivray Capital": dict(cohort="BOUTIQUE", ig_foll=503, ig="mcgillivraycapital",
      igurl="https://www.instagram.com/mcgillivraycapital/"),
}

COHORTS = {
 "LARGE":    ("Large private REIT / institutional", ["Starlight", "Centurion", "Hazelview"]),
 "MID":      ("Mid-market fund", ["Equiton", "Skyline", "Lankin"]),
 "BOUTIQUE": ("Emerging / boutique", ["Pier 4", "Marlin Spring"]),
}

# LinkedIn company-authored posts only. (brand, date, likes, comments, shares, theme, hook, url_slug)
# Employee / press / partner posts appearing on company pages are EXCLUDED before pooling.
LI = [
("Centurion","2026-08-05",10,0,2,"Culture / employer brand","At Centurion, we believe continuous learning is an investment","at-centurion-we-believe-continuous-learning-activity-7490788135287578624-LRp7"),
("Centurion","2026-07-31",6,1,0,"Culture / employer brand","Centurion Listens is our confidential Employee survey","centurion-listens-july-2026-activity-7488965576829136896-czg4"),
("Centurion","2026-07-07",40,0,4,"Culture / employer brand","At Centurion, we're committed to helping our people grow","at-centurion-were-committed-to-helping-activity-7480305468398227456-f7kw"),
("Centurion","2026-07-16",55,3,2,"Culture / employer brand","Yesterday, our team gathered to watch the FIFA World Cup Semi-Final","yesterday-our-team-at-centurions-head-office-activity-7483594520782221312-2T9s"),
("Centurion","2026-07-25",43,0,4,"CSR / community","Centurion was proud to take part in the Habitat for Humanity GTA Build Day","habitat-for-humanity-gta-build-day-activity-7486797850639519744-Tetx"),
("Centurion","2026-07-13",26,8,1,"Culture / employer brand","Congratulations to our RISE Award Winner — Imad Eddine!","congratulations-to-our-rise-award-winner-activity-7482549109388685312-1vbX"),
("Centurion","2026-07-24",17,5,0,"Culture / employer brand","Jordan Nieva, a Senior Maintenance Technician, celebrated a milestone","jordan-nieva-a-senior-maintenance-technician-activity-7486435624804044801-ncAU"),
("Centurion","2026-07-23",32,0,1,"Asset / portfolio","The Hub is a purpose-built student community located in Calgary","the-hub-is-a-purpose-built-student-community-activity-7486131334348722176-IfM_"),
("Centurion","2026-07-10",24,2,0,"Asset / portfolio","Biggin Court Apartments is a 306-suite multi-residential community","biggin-court-apartments-is-a-306-suite-multi-residential-activity-7481429546731397120-afw9"),
("Centurion","2026-07-14",24,3,0,"Culture / employer brand","Czariena Mae Dumbrique celebrated an incredible milestone","czariena-mae-dumbrique-a-senior-revenue-activity-7482896480949800961-fFd8"),
("Centurion","2026-07-29",51,1,1,"Culture / employer brand","At Centurion, we're proud to foster a workplace where Employees feel valued","multiculturalism-in-canada-potluck-activity-7488334637015027712-MVod"),
("Centurion","2026-07-27",13,2,1,"Culture / employer brand","Michelle Arthur celebrated an amazing milestone with Centurion","michelle-arthur-senior-leasing-coordinator-activity-7487522334405259265-leS_"),

("Hazelview","2026-07-27",11,0,0,"Thought leadership","Point of View | Unlocking the Potential of Public Real Estate","publicrealestate-realestateinvesting-investmentinsights-activity-7487514324480204800-SYSN"),
("Hazelview","2026-07-16",51,0,0,"Deal / transaction","Successful execution through active management.","commercialrealestate-industrialrealestate-activity-7483574946540134400-FAvf"),
("Hazelview","2026-07-14",222,2,4,"Fund / capital raise","Our sixth multi-residential fund. 25 years. $150 million at first close.","our-sixth-multi-residential-fund-25-years-activity-7482911932879097856-HLuc"),
("Hazelview","2026-07-22",24,0,0,"CSR / community","Strong communities are built through meaningful local connections.","stationhouse-bloorcrossing-bigonbloor-activity-7485717955318530048-AnW9"),
("Hazelview","2026-07-09",15,3,4,"ESG / sustainability","Real impact looks like 2,600 people supported through volunteerism","2025-sustainability-report-activity-7481021914035965952-hq-9"),
("Hazelview","2026-07-23",25,1,1,"Fund / capital raise","Innovation is an essential part of driving performance","proptech-buildtech-cleantech-activity-7486069881675608064-g0mj"),
("Hazelview","2026-08-04",41,2,1,"Market / macro","For years, Toronto's skyline story was written by condos. That's changing.","rentalhousing-canadianrealestate-multiresidential-activity-7490419754852257795-NLPN"),
("Hazelview","2026-07-28",12,2,2,"Thought leadership","Point of View Part 2: A Different Approach to Real Estate Investing","publicrealestate-alternativeinvestments-investmentinsights-activity-7487899758322212866-8ZVb"),
("Hazelview","2026-07-21",17,1,0,"Thought leadership","Artificial intelligence is reshaping commercial real estate","commercialrealestate-artificialintelligence-activity-7485353336670420992-zYCv"),
("Hazelview","2026-08-05",22,1,1,"Culture / employer brand","Celebrating 15 years of leadership, vision, and impact.","workanniversary-hazelviewculture-leadership-activity-7490765618951057409--mkE"),
("Hazelview","2026-07-07",17,1,2,"CSR / community","Creating truly inclusive communities starts before a resident moves in.","inclusivecommunities-rainbowregistered-purposebuiltrental-activity-7480274509330034688-fLGP"),

("Equiton","2026-07-30",27,0,1,"Culture / employer brand","A Day in the Life | Ivana Cacic, Manager, Investment Finance","a-day-in-the-life-ivana-cacic-manager-activity-7488687349636452352-KA3_"),
("Equiton","2026-08-04",40,4,3,"Team / hire","The strategy behind our US expansion starts with experienced people","the-strategy-behind-our-us-expansion-starts-activity-7490477865285726208-9orb"),
("Equiton","2026-07-30",14,0,3,"Earned media","Family offices are rethinking real estate. Here's why.","rethinking-real-estate-how-family-offices-activity-7488644538450763776-QEgX"),
("Equiton","2026-07-24",37,1,2,"Culture / employer brand","Once a year, our Resident Managers come together for a day of learning","carousel-activity-7486499536115376128-J2_0"),
("Equiton","2026-07-28",17,0,2,"Market / macro","The story isn't just demand. It's the balance between demand and supply.","a-shift-in-the-multifamily-market-activity-7487963236844105728-gEGP"),
("Equiton","2026-07-25",22,1,2,"Culture / employer brand","Strong companies are built on more than strategy","our-latest-town-hall-at-equiton-activity-7486752400238637057-3dMv"),
("Equiton","2026-07-27",15,0,2,"Market / macro","The market moves quickly, and so does your week.","markets-in-minutes-week-of-july-20-24-activity-7487611686141579266-oVoB"),
("Equiton","2026-07-24",19,0,4,"Thought leadership","The headlines change every day. Long-term investment decisions shouldn't.","3-trends-were-watching-ugcPost-7486104008563019776-BVz6"),
("Equiton","2026-07-28",13,2,2,"Market / macro","Demographic shifts can offer useful context alongside market data.","the-average-age-of-a-first-time-homebuyer-activity-7487963137615347713-QiB2"),
("Equiton","2026-07-23",20,2,4,"Thought leadership","Some of the most important trends in real estate don't make the front page.","long-term-fundamentals-are-the-focus-activity-7486080495106265089-oRe_"),
("Equiton","2026-07-22",18,2,4,"Market / macro","Another week, another shift in the market.","markets-in-minutes-activity-7485785992348672000-GJk_"),
("Equiton","2026-07-30",21,4,1,"Culture / employer brand","Today, we're celebrating the next generation of talent.","happy-national-intern-day-activity-7488654363293569025-dzKC"),
("Equiton","2026-07-18",35,1,4,"Milestone / expansion","For the past decade, we've helped Canadians build real wealth","for-the-past-decade-weve-helped-canadians-activity-7484260966885449728-nRMS"),
("Equiton","2026-07-17",16,0,2,"Thought leadership","US multifamily has consistently ranked among top-performing asset classes","what-decades-of-multifamily-data-show-activity-7483987941871017985-Q5MX"),
("Equiton","2026-07-09",16,1,6,"Thought leadership","Rent headlines get the attention. Occupancy tells the real story.","rent-headlines-get-the-attention-occupancy-activity-7481085845886836736-h0KL"),
("Equiton","2026-07-10",17,0,2,"Asset / portfolio","The most meaningful operational improvements are found in the details.","a-small-leak-became-a-big-opportunity-activity-7481452484675399680-ZqU4"),
("Equiton","2026-07-06",21,1,1,"Market / macro","The US is short more than 4 million homes.","the-us-is-short-more-than-4-million-homes-activity-7479890824990715904-aPs5"),
("Equiton","2026-07-14",21,2,3,"Market / macro","Canada's housing challenge is often discussed in broad terms","canadas-housing-challenge-activity-7482890017145724928-MaBO"),
("Equiton","2026-07-11",11,0,2,"Brand / aphorism","Most long-term goals aren't achieved through a single decision.","most-long-term-goals-arent-achieved-through-activity-7481663633739948032-vai0"),
("Equiton","2026-07-10",9,0,1,"Investor education","Does the Federal Reserve control mortgage rates?","does-the-federal-reserve-control-mortgage-activity-7481442310317035521-8-6N"),

("Skyline","2026-08-05",15,1,1,"ESG / sustainability","At Skyline, we invest in initiatives that strengthen our portfolio","at-skyline-we-invest-in-initiatives-that-activity-7490768692620759040-sWaG"),
("Skyline","2026-07-24",66,2,9,"Development update","SkyDev Construction Update - Sky Towers in Barrie","skydev-construction-update-construction-activity-7486450513052602368-Bi-3"),
("Skyline","2026-07-30",42,2,5,"Development update","We're pleased to share a construction progress update on Vale Apartments","were-pleased-to-share-a-construction-progress-activity-7488594751055667200-op0o"),
("Skyline","2026-07-23",44,2,4,"Asset / portfolio","River's Edge Apartments in Chatham, ON, is now 85% leased.","rivers-edge-apartments-one-of-skyline-apartment-activity-7486118037134389251-XUzk"),
("Skyline","2026-07-29",16,0,4,"Market / macro","Rental demand is evolving across Ontario","frpo-2026-summer-edition-activity-7488222412824813568-FDed"),
("Skyline","2026-07-31",104,3,4,"Milestone / expansion","Yesterday, we celebrated a major milestone at Sky Towers — topping off Tower B","yesterday-we-celebrated-a-major-milestone-activity-7489030806234075136-vcpi"),
("Skyline","2026-07-21",17,0,2,"Investor education","Bull market or bear market? Understanding the bigger picture matters.","bull-vs-bear-public-markets-and-private-activity-7485408336603922433-DbkF"),
("Skyline","2026-07-22",157,14,11,"Deal / transaction","Skyline Industrial REIT has fully leased its zero-carbon industrial park","were-pleased-to-share-that-skyline-industrial-activity-7485726374062645248-FjyC"),
("Skyline","2026-07-27",116,2,1,"CSR / community","Skyline was proud to sponsor the John Tavares Foundation's Brighter Futures Gala","earlier-this-month-skyline-was-proud-to-activity-7487507188652023808-7IOV"),
("Skyline","2026-07-10",86,0,8,"CSR / community","Yesterday, Skyliners came together for our annual Heart & Stroke Walk","yesterday-skyliners-came-together-for-our-activity-7481377137292328960-8oDr"),
("Skyline","2026-07-17",54,1,7,"Development update","Construction at 1641 Topsail Road, Paradise, NL continues to progress","construction-at-1641-topsail-road-paradise-activity-7483883309962321920-ecNL"),
("Skyline","2026-07-28",45,0,2,"Investor event","Last week, we launched our Summer Investor Information Sessions","last-week-we-launched-our-summer-investor-activity-7487869578577063936-Qgl3"),
("Skyline","2026-07-15",28,0,3,"Market / macro","The Bank of Canada held its policy interest rate at 2.25% again","the-bank-of-canada-held-its-policy-interest-activity-7483157169521991680-gYzq"),
("Skyline","2026-07-08",33,0,3,"Development update","Brampton's rental landscape is evolving — Rose Towers is helping lead the way","addressing-bramptons-rental-boom-remi-activity-7480683383639998465-XyaF"),
("Skyline","2026-07-07",48,2,6,"Thought leadership","In today's market, it's easy to get caught up in headlines and short-term noise","in-todays-market-its-easy-to-get-caught-activity-7480320305551269889-82AS"),
("Skyline","2026-07-14",46,0,6,"Development update","SkyDev Construction Update: Baycrest Apartments in Owen Sound","skydev-construction-update-construction-activity-7482826683524276224-JVC_"),
("Skyline","2026-07-21",74,4,2,"Culture / employer brand","Last week's Summer Appreciation Staff Event brought everyone together","summer-appreciation-event-activity-7485336250665627648-tlkK"),

("Lankin","2026-07-29",13,1,1,"Investor education","What could a more connected regulatory framework mean for Canada's capital markets?","ontario-capitalmarkets-investoreducation-activity-7488345142114947072-G57h"),
("Lankin","2026-07-30",67,9,4,"Culture / employer brand","Behind every high-performing team is a strong sense of connection.","lifeatlankin-teamculture-lankininvestments-activity-7488715085243367424-QS7m"),
("Lankin","2026-08-04",11,0,0,"Market / macro","The Bank of Canada has published its 2027 schedule","marketwatch-bankofcanada-interestrates-activity-7490519589676716032-_YFZ"),
("Lankin","2026-07-14",7,0,0,"Investor education","Do all residential real estate investments respond to the market the same way?","investorinsights-privaterealestate-multifamilyrealestate-activity-7482905782238314496-vCl1"),
("Lankin","2026-07-15",12,0,2,"Investor event","1 DAY TO GO! Join us for Episode 7 of Rich by REIT","richbyreit-privaterealestate-investoreducation-activity-7483293589142319105-ElO5"),
("Lankin","2026-07-22",8,0,0,"Thought leadership","Are today's housing challenges primarily a demand issue?","canadianrealestate-housingsupply-thoughtleadership-activity-7485800867703513088-W8z8"),
("Lankin","2026-07-23",103,2,0,"Team / hire","We're pleased to introduce Andrew Agatep, Vice President, Finance","meettheteam-lankininvestments-finance-activity-7486163254432645120-wxgU"),
("Lankin","2026-07-21",3,0,1,"Market / macro","Builders are completing projects faster than they are launching new ones","multifamily-canadianrealestate-marketwatch-activity-7485438482186698752-XMDe"),
("Lankin","2026-07-28",16,1,1,"Market / macro","Nearly half of Canadians are sitting on investable cash they never put to work.","nearly-half-of-canadians-are-sitting-on-investable-activity-7487982746284359680-VUZD"),
("Lankin","2026-07-07",11,0,0,"Thought leadership","Construction activity does more than shape today's housing market","canadianrealestate-privaterealestate-multifamilyrealestate-activity-7480366867740581889-AveQ"),
("Lankin","2026-07-06",14,1,1,"Investor education","What's the one market trend you're watching most closely right now?","newsletter-privaterealestate-canadianrealestate-activity-7480010220803440640-iRfB"),
("Lankin","2026-07-10",10,1,0,"Investor event","1 WEEK TO GO until we unpack one of the most overlooked parts of investing","richbyreit-privaterealestate-investoreducation-activity-7481147099976347648-kuDg"),

("Pier 4","2026-08-05",12,0,1,"Market / macro","Canada's affordability crisis continues to drive residents toward secondary markets","market-spotlight-riverview-nb-activity-7490795995103031298-5KF8"),
("Pier 4","2026-07-29",24,0,1,"Investor education","Net Asset Value (NAV) is the fundamental price of a fund per unit","reit-terms-nav-activity-7488226214113890304-ZP_U"),
("Pier 4","2026-08-04",48,1,1,"Deal / transaction","Pier 4 has completed the successful disposition of 3 apartments.","successful-disposition-activity-7490422890249572353-ETmo"),
("Pier 4","2026-07-16",16,0,1,"Investor education","Most investors hold less real estate than the research recommends.","the-role-of-reits-in-asset-allocation-activity-7483513820087209985-siqO"),
("Pier 4","2026-07-31",26,0,1,"Housekeeping","Happy Civic Holiday from all of us at Pier 4!","happy-civic-holiday-from-all-of-us-at-pier-activity-7488941579265748993-DLVZ"),
("Pier 4","2026-07-17",110,11,1,"Team / hire","A special welcome to Sarah Paskal, Vice President, Sales","a-special-welcome-to-sarah-paskal-vice-president-activity-7483889297398558722-wSIr"),
("Pier 4","2026-07-24",15,0,1,"Advisor-facing","As a financial advisor, your clients are counting on you.","questions-advisors-should-ask-about-private-activity-7486424279849312256-UJMx"),
("Pier 4","2026-07-20",28,0,1,"Culture / employer brand","Excellence in practice.","employee-values-activity-7485026567010680832-yzrt"),
("Pier 4","2026-07-23",20,0,1,"Market / macro","Toronto's affordability crisis is creating real movement.","market-spotlight-london-on-activity-7486061917413941248-47iO"),
("Pier 4","2026-07-13",30,0,0,"Culture / employer brand","Follow along as we transition through a day in the life of two Finance interns","day-in-the-life-of-finance-interns-activity-7482440639750504448-aEjW"),
("Pier 4","2026-07-06",48,1,3,"Culture / employer brand","June was a special month.","summer-party-2026-activity-7479940681667371008-i4Zb"),
("Pier 4","2026-07-08",18,0,1,"Investor education","With a $300,000 income, Cameron has two options.","with-a-300000-income-cameron-has-two-options-activity-7480635170467803136-uBFN"),
("Pier 4","2026-07-10",30,0,2,"Culture / employer brand","Q2 brought new faces and a few good games.","q2-events-recap-activity-7481360964785995776-Dun9"),

("Starlight","2026-08-01",33,1,1,"Housekeeping","Wishing everyone an enjoyable long weekend!","wishingeveryone-an-enjoyablelong-weekend-activity-7489126428924542977-YCg2"),
("Starlight","2026-08-05",18,1,0,"Culture / employer brand","As our award-winning summer student program approaches its final weeks","as-our-award-winning-summer-student-program-activity-7490787849257095168-UPpE"),
("Starlight","2026-07-17",41,0,1,"Culture / employer brand","Our interns gained advice from Dennis Mitchell, CEO and CIO of Starlight Capital","starlightinterns-starlightculture-futureleaders-activity-7483875668640808960-SRqO"),
("Starlight","2026-07-14",6,0,1,"Fund / capital raise","True North Commercial REIT Announces Timing of Q2-2026 Results","true-north-commercial-reit-announces-timing-activity-7482906098723639296-oB6L"),
("Starlight","2026-07-24",47,2,4,"Asset / portfolio","#CommunitySpotlight: The Deanwood delivers 196 modern homes in Barrie","communityspotlight-starlightinvestments-canadianresidential-activity-7486424085351059456-9DLG"),
("Starlight","2026-08-04",103,5,3,"Milestone / expansion","Lighthaus has been named a finalist for Residential Development of the Year","starlightinvestments-lighthausliverpool-buildtorent-activity-7490418576122765314-D2Ig"),
("Starlight","2026-07-07",50,0,2,"Culture / employer brand","Our interns participated in a session focused on our U.S. Residential platform","summerstudents-learning-starlightinvestments-activity-7480314020034465792-p8Un"),
("Starlight","2026-07-21",38,3,2,"Thought leadership","Starlight participated in the Connect CRE Canada Conference","starlightinvestments-purposebuiltrental-housingsupply-activity-7485336203467128832-dwOy"),
("Starlight","2026-07-23",92,2,10,"Milestone / expansion","#ICYMI: Starlight celebrated the topping off of Donvale Commons","icymi-starlightinvestments-rentalhousing-activity-7486046208587681792-I3oU"),
("Starlight","2026-07-15",8,0,1,"Fund / capital raise","True North Commercial REIT Announces July 2026 Distribution","true-north-commercial-reit-announces-july-activity-7483272568150368256-gNJG"),
("Starlight","2026-07-06",86,0,0,"ESG / sustainability","Marlee Kohn participated as a panelist at the Toronto Sustainability Summit","starlightinvestments-esg-sustainability-activity-7479999842895806464-s34c"),
("Starlight","2026-07-28",90,2,3,"CSR / community","Last month, Starlight Investments held an Impact Day for our summer students.","starlightimpact-communityengagement-starlightcares-activity-7487867901400686592-6aW8"),
("Starlight","2026-07-09",127,2,0,"Milestone / expansion","Spectra has achieved WiredScore Platinum certification.","wiredscore-buildtorent-digitalconnectivity-activity-7480982435145363456-P_zP"),
("Starlight","2026-07-30",68,1,2,"Milestone / expansion","Completion and launch of the first phase of The Parklands in Dartford, UK","starlightinvestments-buildtorent-ukresidential-activity-7488518778201231361-p4JF"),
("Starlight","2026-07-13",29,0,3,"Earned media","Starlight was featured in Maclean's for the Floor Friends children's book series","floorfriends-childrensbooks-residentengagement-activity-7482484537030037504-Ijox"),
("Starlight","2026-07-10",90,0,4,"Culture / employer brand","Our annual summer student cooking competition brought together creativity","starlightinterns-starlightcookingcompetition-activity-7481335181732118528-rG8e"),
("Starlight","2026-07-16",48,0,2,"Asset / portfolio","Centerview at Crossroads received second place in the ASID Design Excellence Awards","starlightinvestments-usresidential-activity-7483583650358288385-DTwB"),

("Marlin Spring","2026-07-28",35,0,1,"Development update","We are excited to see the continued evolution of The Queensway","realestatedevelopment-marlinspring-southetobicoke-activity-7487917453138792448-WotN"),
("Marlin Spring","2026-07-22",34,0,1,"Development update","The right location brings long-term value.","the-right-location-brings-long-term-value-activity-7485717508813938689-JIam"),
]

# Instagram, in-window only (2026-07-06 .. 2026-08-05). Non-brand-owned posts excluded.
# (brand, date, likes, comments, fmt, plays, views, shortcode)
IG = [
 ("Skyline","2026-08-25",17,0,"Static",None,None,"DceBIb0DHwP"),
 ("Skyline","2026-09-01",41,0,"Reel",484,196,"DcwWB_VAa7O"),
 ("Skyline","2026-09-02",17,0,"Reel",463,123,"Dcy4mJqjh5o"),
 ("Skyline","2026-09-03",33,0,"Reel",883,283,"Dc1Z_rfDluh"),
 ("Skyline","2026-09-15",18,0,"Static",None,None,"DdUW1WsjH9Y"),
 ("Skyline","2026-09-17",21,0,"Static",None,None,"DdZggysnAqt"),
 ("Skyline","2026-09-21",34,0,"Static",None,None,"Ddjbu8snTk8"),
 ("Skyline","2026-09-22",21,0,"Reel",424,105,"DdmHayNDQOG"),
 ("Skyline","2026-09-23",12,0,"Static",None,None,"Ddo539eIGg4"),
 ("Equiton","2026-08-25",16,0,"Carousel",None,None,"Dcd9v3HDakn"),
 ("Equiton","2026-08-25",17,0,"Reel",1092,345,"DcexI1vB9JL"),
 ("Equiton","2026-08-26",15,0,"Reel",1206,316,"DchSjAGhTEs"),
 ("Equiton","2026-08-27",13,0,"Reel",560,168,"Dcj-yF3hZxB"),
 ("Equiton","2026-08-28",18,0,"Reel",904,274,"DclzR6vhY2o"),
 ("Equiton","2026-08-31",10,0,"Carousel",None,None,"DctlotPHEnr"),
 ("Equiton","2026-08-31",12,1,"Carousel",None,None,"DcuHD9THNDz"),
 ("Equiton","2026-09-01",18,0,"Carousel",None,None,"DcwDrklnOj1"),
 ("Equiton","2026-09-01",10,0,"Carousel",None,None,"DcwvVuGnDnZ"),
 ("Equiton","2026-09-02",13,0,"Reel",903,232,"DczXeNvBu2D"),
 ("Equiton","2026-09-03",17,0,"Carousel",None,None,"Dc1FZFDnEhw"),
 ("Equiton","2026-09-04",11,0,"Reel",424,100,"Dc37dsQRyoe"),
 ("Equiton","2026-09-08",18,0,"Carousel",None,None,"DdCA1-bHEmU"),
 ("Equiton","2026-09-08",10,0,"Carousel",None,None,"DdCoYEUH3te"),
 ("Equiton","2026-09-09",14,0,"Reel",622,175,"DdFVmJrhlI7"),
 ("Equiton","2026-09-10",10,1,"Reel",502,99,"DdHwiMNhkNv"),
 ("Equiton","2026-09-12",35,0,"Reel",577,181,"DdMQjZ4h7C_"),
 ("Equiton","2026-09-14",8,0,"Carousel",None,None,"DdSUQipjRDi"),
 ("Equiton","2026-09-15",10,0,"Reel",512,145,"DdUvAQrBq0Y"),
 ("Equiton","2026-09-16",6,0,"Reel",548,189,"DdXPMwLhhL7"),
 ("Equiton","2026-09-17",19,0,"Reel",558,143,"DdZ5qiABO6v"),
 ("Equiton","2026-09-21",7,0,"Carousel",None,None,"DdkHp5vH1ch"),
 ("Equiton","2026-09-22",10,0,"Reel",228,49,"Ddm3chfh4pN"),
 ("Equiton","2026-09-23",9,0,"Carousel",None,None,"DdpEGqDCCM5"),
 ("Lankin","2026-08-25",2,0,"Static",None,None,"Dcemzm7CRF0"),
 ("Lankin","2026-08-28",5,0,"Carousel",None,None,"DcmVO-cI9_R"),
 ("Lankin","2026-09-01",4,0,"Static",None,None,"DcwoXgLiRj3"),
 ("Lankin","2026-09-02",10,0,"Static",None,None,"DczNKgPmxNh"),
 ("Lankin","2026-09-04",4,0,"Static",None,None,"Dc4W0n2x4yS"),
 ("Lankin","2026-09-09",2,0,"Static",None,None,"DdFOuh6FBZS"),
 ("Lankin","2026-09-10",5,0,"Static",None,None,"DdHzhegm5je"),
 ("Lankin","2026-09-11",4,0,"Static",None,None,"DdKYURWGOea"),
 ("Lankin","2026-09-15",3,0,"Static",None,None,"DdUu78BjlA-"),
 ("Lankin","2026-09-16",7,0,"Carousel",None,None,"DdXVfINDZzU"),
 ("Lankin","2026-09-18",0,0,"Static",None,None,"DdcgwFTl6L3"),
 ("Lankin","2026-09-22",4,0,"Static",None,None,"DdmtD5aDO_t"),
 ("Pier 4","2026-08-26",27,1,"Carousel",None,None,"DcgXFdekakj"),
 ("Pier 4","2026-08-27",12,1,"Carousel",None,None,"Dci9Is7kXUz"),
 ("Pier 4","2026-08-28",51,2,"Carousel",None,None,"DcmHB1QGCpF"),
 ("Pier 4","2026-08-31",12,2,"Carousel",None,None,"Dct83DRmL48"),
 ("Pier 4","2026-09-01",10,0,"Static",None,None,"DcwHMe3RsJB"),
 ("Pier 4","2026-09-02",4,1,"Carousel",None,None,"DcydfL7EdpC"),
 ("Pier 4","2026-09-03",4,0,"Carousel",None,None,"Dc084p1EdPY"),
 ("Pier 4","2026-09-04",5,0,"Static",None,None,"Dc09lhyxYLe"),
 ("Pier 4","2026-09-09",2,0,"Static",None,None,"DdEZwMSxPlE"),
 ("Pier 4","2026-09-10",6,2,"Carousel",None,None,"DdG9_J9Ed_S"),
 ("Pier 4","2026-09-11",8,0,"Reel",327,79,"DdJghZQxvK9"),
 ("Pier 4","2026-09-14",11,0,"Static",None,None,"DdRQSBERs0w"),
 ("Pier 4","2026-09-16",4,0,"Carousel",None,None,"DdWbDJNEV0-"),
 ("Pier 4","2026-09-17",3,0,"Carousel",None,None,"DdZA4lFERxn"),
 ("Pier 4","2026-09-18",0,0,"Carousel",None,None,"DdblkNOkXPi"),
 ("Pier 4","2026-09-21",1,1,"Static",None,None,"DdjhivAkUMg"),
 ("Pier 4","2026-09-23",1,0,"Static",None,None,"DdobY8axfu6"),
 ("McGillivray Capital","2026-08-25",21,0,"Carousel",None,None,"DcedbbnGkFD"),
 ("McGillivray Capital","2026-08-28",12,2,"Reel",502,107,"DcmAoINgJpr"),
 ("McGillivray Capital","2026-09-02",6,0,"Carousel",None,None,"DcxAf3onHoM"),
 ("McGillivray Capital","2026-09-04",11,1,"Reel",134,41,"Dc3-PkSAWbZ"),
 ("McGillivray Capital","2026-09-10",6,0,"Carousel",None,None,"DdHboLIifWC"),
 ("McGillivray Capital","2026-09-18",10,2,"Carousel",None,None,"DdcB_U8jPN5"),
]



# Posts excluded from company medians (surfaced on company pages but not company-authored)
EXCLUDED = [
 ("Centurion","Carl Gomez, Chief Economist","Employee post on BoC rate announcement",27,1,3),
 ("Centurion","Vanessa T., CREBTV","Press/media post quoting Centurion's economist",6,0,1),
 ("Equiton","Jason Roque, Founder & CEO","Founder post on Brookfield 2026 outlook",24,1,1),
 ("Skyline","Sina Najibi, CAMi Management","Contractor post about a Skyline project",15,5,4),
]

# Highest single Instagram video published inside the last 90 days, rebuilt every cycle.
IG_PEAK_90D = {
 "Skyline": dict(plays=1252, views=30, likes=62, date="2026-07-10", code="DankoGwFNDH"),
 "Equiton": dict(plays=1434, views=396, likes=36, date="2026-06-26", code="DaD_eE7gL_7"),
 "Lankin": dict(plays=359, views=31, likes=6, date="2026-07-10", code="Dal71Y6DGZV"),
 "Pier 4": dict(plays=4633, views=570, likes=14, date="2026-07-13", code="DavJJL6xnNB"),
 "McGillivray Capital": dict(plays=502, views=107, likes=12, date="2026-08-28", code="DcmAoINgJpr"),
}

# Out of category reference account. Wealthsimple is NOT a real estate firm and is
# NEVER pooled into any category median, percentile or score. It exists on the page
# as a comparison of what an investor facing Canadian brand does on this platform.
IG_REF = dict(
 name="Wealthsimple", handle="wealthsimple",
 url="https://www.instagram.com/wealthsimple/",
 foll=243224, n=10, n90=46,
 medL=287.0, medC=12.0,
 sumL=5526, sumC=231,
 er=0.1180, cl=4.18,
 mix="4C·3S·3R",
 top=2196, topcode="DcmZq_jj0py",
)


