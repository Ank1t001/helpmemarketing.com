import json, re, os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
EV='/tmp/claude-0/-home-user-helpmemarketing-com/ede75233-c5c6-5154-983e-51b967a674c5/scratchpad/evidence'
KIT='/home/user/helpmemarketing.com/_kit/dental-implants/editions/001'
TZ=ZoneInfo('America/Toronto')
def tor(u): return datetime.fromisoformat(u.replace('Z','+00:00')).astimezone(TZ).strftime('%Y-%m-%d %H:%M %Z')
L={json.loads(l)['tag']:json.loads(l) for l in open(f'{EV}/load_log.jsonl')}
obs={o['id']:o for o in json.load(open(f'{KIT}/observations.json'))['observations']}
flog={}
for l in open(f'{KIT}/raw/fetch_log.jsonl'):
    r=json.loads(l); flog.setdefault(r['requested_url'],r); flog.setdefault(r.get('final_url'),r)
def ref(*ids):
    out=[]
    for i in ids:
        o=obs[i]; f=flog.get(o['source_url'],{})
        out.append({'observation_id':i,'kind':o['kind'],'excerpt':o['excerpt'],'source_url':o['source_url'],'fetched_utc':f.get('fetched_utc')})
    return out
MISS={'value':None,'status':'missing'}
def shot(n): return f'{EV}/shots/{n}'

doc={'schema':'hmm-dental-index-evidence/1','edition':'001','prepared_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),
 'research_window':{'start':'2026-09-16','end':'2026-10-15','inclusive':True,'timezone':'America/Toronto','note':'Fixed. Not moved forward.'},
 'collector':{'tool':'Headless Chromium (Playwright) in the Claude Code cloud container, through the container\'s outbound proxy','not':'Not the founder\'s Chrome; no logged-in session; no cookies exported; no paid collection; no form submitted; no challenge bypassed','one_attempt_rule':'Each URL loaded once; a refusal was recorded and not retried'},
 'status_vocabulary':{'ads':['relevant_ads_observed','no_matching_ads_found','advertiser_uncertain','access_blocked','not_checked'],'ads_definition':'relevant_ads_observed = ads whose advertiser or creative can be tied to the clinic under study (implant relevance and window are separate fields)','missing':'A hidden or unavailable metric is null with status missing, never zero'},
}

# 1. clinics
blk=lambda tag,reason:{'requested_url':L[tag]['requested_url'],'checked_utc':L[tag]['started_utc'],'checked_toronto':tor(L[tag]['started_utc']),'http_status':L[tag].get('status'),'server':L[tag].get('headers_server'),'title':L[tag].get('title'),'visible_text':open(f'{EV}/pages/{tag}.txt').read().strip()[:400],'html_sha256':L[tag]['html_sha256'],'screenshot':shot(tag+'.png'),'outcome':reason}
clinics={}
clinics['studiob']={'name':'Studio B Dental','domain':'studiobdental.ca','website_status':'reviewed 2026-10-16 18:14 to 18:19 UTC (prior run, kit fetch log)',
 'address':ref('sb-addr'),'phone':{'value':None,'status':'missing','note':'Not recorded in edition 001 observations; not re-fetched in this task'},
 'implant_and_full_arch_urls':sorted({o['source_url'] for k,o in obs.items() if o['clinic']=='studiob' and o['dimension'] in ('positioning','cost')}),
 'consultation_offer_and_fee':ref('sb-consult-options','sb-consult-credit','sb-arch-screen'),
 'cost':ref('sb-arch-fee','sb-arch-phases','sb-single-range','sb-full-range'),'financing':ref('sb-finance'),
 'enquiry_route_and_fields':ref('sb-form'),'what_happens_next':ref('sb-next'),'instagram_link':ref('sb-ig'),
 'cost_breakdown':{'scope':'single, per arch and full mouth figures published on different pages (see cost refs)','materials':ref('sb-zirconia'),'temporary_vs_final':ref('sb-arch-phases'),'inclusions_exclusions_conditions':{'value':None,'status':'missing','note':'Not separately recorded beyond the cost excerpts'}},
 'new_evidence_this_task':['Meta ad 26002231369395543 states "$17,990 PER ARCH" with "Final bridge (4–6 months later): $8,900"; the website observation sb-arch-fee reads "FEE: from $17,900". Recorded as observed in two sources; not reconciled.']}
clinics['nysc']={'name':'North York Smile Centre','domain':'smile-by-design.ca','website_status':'reviewed (prior run, kit fetch log)',
 'identity':ref('ny-identity'),'phone':{'value':None,'status':'missing','note':'Not recorded in edition 001 observations'},
 'implant_and_full_arch_urls':sorted({o['source_url'] for k,o in obs.items() if o['clinic']=='nysc' and o['dimension'] in ('positioning','cost')}),
 'consultation_offer_and_fee':ref('ny-free','ny-noobligation'),'cost':ref('ny-single-range','ny-tiers','ny-tier-essential'),'financing':ref('ny-tier-monthly','ny-finance'),
 'enquiry_route_and_fields':ref('ny-form','nyx-req'),'what_happens_next':ref('ny-next'),'instagram_link':ref('ny-ig'),
 'new_evidence_this_task':['Instagram bio of @northyork.smilecentre reads "Head office @mysmilecentre" (profile load 2026-10-16T19:10:52Z).','Instagram posts name Dr. Rob Eisen; the website names Dr. Rob Eisen and Dr. Jerry Jesin (kit raw text 1086bc682868).']}
clinics['gajjar']={'name':'Dr. Neil J. Gajjar Associates & Specialists','domain':'drgajjar.com','website_status':'reviewed (prior run, kit fetch log)',
 'address':ref('gj-addr'),'phone':{'value':None,'status':'missing','note':'Not recorded in observations. A Google ad creative (Optio Publishing Inc., last shown 31 May 2026) shows "Call (905) 564-2021"; that is ad evidence, not a website observation'},
 'implant_and_full_arch_urls':sorted({o['source_url'] for k,o in obs.items() if o['clinic']=='gajjar' and o['dimension'] in ('positioning','education')}),
 'consultation_offer_and_fee':ref('gj-consult'),'cost':ref('gj-noprice'),'financing':{'value':None,'status':'missing'},
 'enquiry_route_and_fields':ref('gj-form'),'what_happens_next':ref('gj-nonext'),'instagram_link':ref('gj-ig')}
for a,name,dom,tag,why in [('dundas','Dundas East Dental','dundaseastdental.com','dundas-home','Access blocked: the page loaded (HTTP 200) but displayed only a "VPN or Proxy Detected. Please disable your VPN or Proxy to browse this website." panel. Not bypassed. Content behind the panel was not read or used; the saved HTML body was deleted, only its hash kept.'),
                           ('bond','Bond Street Dental','dentalimplantsclinic.ca','bond-home','Access blocked: Cloudflare "Performing security verification" challenge (HTTP 403). Not passed or bypassed.')]:
    clinics[a]={'name':name,'domain':dom,'website_status':'blocked','browser_check':blk(tag,why),
      'prior_block':'HTTP 403 to urllib at 2026-10-16T18:14:33Z (dundas) / Cloudflare 403 at 18:14:34Z (bond), see kit fetch_log.jsonl',
      **{k:dict(MISS) for k in ['address','phone','implant_url','full_arch_url','consultation_offer_and_fee','cost','financing','enquiry_route_and_fields','what_happens_next','instagram_link']}}
clinics['bond']['identifies_bond_street_dental']={'from_website':'not_verified (site blocked)','third_party_corroboration':[
 'Google Ads Transparency, domain dentalimplantsclinic.ca, Canada, 16 Sep to 15 Oct 2026: 26 ads, advertiser "Passion Dental Group Inc" (Verified). Creatives show location assets "Bond Street Dental - Toronto" and "Bond Street Dental", display name "Dental Implants Clinic" with "Bond Street", and one ad text "113 Bond St" (creative CR02067580969778413569).'],
 'conclusion':'Ad records link the domain to a listing named Bond Street Dental and to Passion Dental Group Inc. The website itself was not read, so the identity is corroborated, not verified. Do not treat the address 113 Bond St as a website observation.'}
clinics['dundas']['leads_not_used']='Cached copy in leads.json (Dr. Ammar Taimish, all-inclusive full-arch prices) remains unverified.'
doc['clinics']=clinics

# 2. social identities
doc['social_identities']={
 'studiob':{'handle':'studiobdental','status':'verified_link','basis':['official website links the handle (obs sb-ig)','profile bio links www.studiobdental.ca/virtual-consult (profile load 2026-10-16T19:10:39Z)'],'profile_name':'Charles Botbol','note':'Display name is the dentist\'s name; the account is the one the clinic website links, with the clinic URL in its bio. Followers shown 88.7K (logged-out header, 2026-10-16).','screenshot':shot('ig-studiobdental.png')},
 'nysc':{'handle':'northyork.smilecentre','status':'verified_link','basis':['official website links the handle (obs ny-ig)','bio links www.smile-by-design.ca'],'profile_name':'North York Smile Centre','note':'Bio: "Head office @mysmilecentre". @mysmilecentre not opened. Followers shown 271.','screenshot':shot('ig-northyork.smilecentre.png')},
 'gajjar':{'handle':'gajjardentistry','status':'verified_link','basis':['official website links the handle (obs gj-ig)'],'profile_check':{'checked_utc':L['ig-gajjardentistry']['started_utc'],'http_status':429,'final_url':L['ig-gajjardentistry']['final_url'],'outcome':'Refused (HTTP 429, redirected to login). Not retried.'}},
 'dundas':{'handle':None,'status':'not_verified','reason':'Official website blocked; no handle may be assumed. Meta Ad Library exact-phrase "Dundas East Dental" found no ads, so no page identity from Meta either.'},
 'bond':{'handle':None,'status':'not_verified','reason':'Official website blocked; no handle may be assumed. Meta Ad Library exact-phrase "Bond Street Dental" found no ads.'}}
doc['facebook_ad_pages_observed']={'studiob':'"studiobdental" (ad text names Studio B Dental and Dr. Charles Botbol; the website names Dr. Charles Botbol)','nysc':'"North York Smile Centre"; also "My Smile Centre" (head-office brand named in the NYSC Instagram bio; its ad names Dr. Jerry Jesin, whom the NYSC website names)','gajjar':'"Dr. Neil J. Gajjar, Associates & Specialists" and "Dr. Neil J. Gajjar, DDS - RCDSO Council Candidate"'}

# 3. instagram
G={r['shortcode']:r for r in json.load(open(f'{EV}/ig_grid.json'))}
CLS={'Dd6yzieDLQG':('cosmetic / veneers humour','no','none in caption'),
 'Dd3yAGBBrsW':('behind the scenes, clinic culture','no','none in caption'),
 'DdsKsuVM8b4':('patient testimonial; hashtags #dentalimplant #zirconiaimplant #ceraroot','yes (caption hashtags name zirconia implants)','DM to book complimentary consultation'),
 'DdrKB7AhD3b':('process and transformation; hashtags #porcelainveneers #implantsurgery','unclear (hashtag only; video not watched)','link in bio to book complimentary consultation'),
 'Dd9BwhfFG0x':('implant patient testimonial with Dr. Eisen','yes','contact Smile Centre to book a consultation'),
 'Dd6dymzkcvJ':('emergency dentistry','no','contact to book an emergency appointment'),
 'DdtiGIPlrNt':('All-on-X FAQ: dentures, bone levels','yes (full arch)','register for free webinar (webinar.mysmilecentre.ca)'),
 'DdrBZDBHDHg':('All-on-X live webinar, 30 September, Dr. Rob Eisen','yes (full arch)','register for webinar (webinar.mysmilecentre.ca)'),
 'DdbhpOgIMJE':('Invisalign wear time','no','none in caption')}
posts=[]
for l in open(f'{EV}/ig_posts.jsonl'):
    r=json.loads(l); sc=r['shortcode']; t=r['times'][0]['dt']
    m=re.match(r'([\d,]+) likes, ([\d,]+) comments',r['og_desc'] or '')
    cap=re.sub(r'^.*? on Instagram: "','',r['og_title'] or '').rstrip('"')
    topic,rel,cta=CLS[sc]
    posts.append({'url':r['url'],'shortcode':sc,'owner':r['handle'],'collaboration':'none shown on the logged-out post page','format':'reel' if '/reel/' in r['url'] else 'post (photo or carousel; not distinguished logged out)',
      'published_utc':t,'published_toronto':tor(t),'og_description_date':re.search(r'on ([A-Z][a-z]+ \d+, \d{4})',r['og_desc']).group(1),
      'caption_first_line':cap.split('\n')[0].strip(),'topic':topic,'implant_relevance':rel,'cta':cta,
      'likes':int(m.group(1).replace(',','')) if m else None,'comments':int(m.group(2).replace(',','')) if m else None,'plays':{'value':None,'status':'missing','note':'not shown logged out'},
      'ai_content_label':'AI content' in r['text'][:400],'video_watched':False,'checked_utc':r['checked_utc'],'evidence':{'screenshot':shot('ig/'+sc+'.png'),'source':'og:description and <time datetime> of the post page'}})
posts.sort(key=lambda p:(p['owner'],p['published_utc']))
grid=[{k:v for k,v in g.items()} for g in G.values()]
doc['instagram']={'window':'2026-09-16 to 2026-10-15 Toronto','posts':posts,
 'coverage':{
  'studiobdental':{'grid_items_visible_logged_out':12,'in_window_posts_read':4,'pinned_or_out_of_order_at_top':['DXWwI1lFE0N (about 20 Apr 2026)','DYnndUkhcR- (about 21 May 2026)','C7X32NgJEE0 (about 24 May 2024)'],'oldest_grid_item':'Db77RV4hiNr, about 12 Aug 2026','newest_non_pinned':'Dd6yzieDLQG, 30 Sep 2026','assessment':'The visible grid runs from before the window start to 30 September, so it appears to contain every post in the window. No post between 1 and 15 October appeared. Not confirmed against a logged-in view; call it probable, not complete. Stories, deleted or archived posts and collaborator-owned posts on other accounts are not covered.'},
  'northyork.smilecentre':{'grid_items_visible_logged_out':12,'in_window_posts_read':5,'oldest_grid_item':'DcBkbRzIAf1, about 14 Aug 2026','newest':'Dd9BwhfFG0x, 1 Oct 2026','assessment':'Same as above: probable, not complete. No post between 2 and 15 October appeared.'},
  'gajjardentistry':{'in_window_posts_read':0,'assessment':'Not collected: profile request refused (HTTP 429, login redirect) at 2026-10-16T19:11:04Z; not retried.'},
  'dundas':{'assessment':'Not collected: no verified handle.'},'bond':{'assessment':'Not collected: no verified handle.'}},
 'grid_dates_note':'Grid dates were estimated from shortcodes only to decide which posts to open; every recorded date comes from the post page itself. For Dd6yzieDLQG the post time is 2026-09-30T18:30:07Z while og:description says September 29; the <time> value is used.',
 'grid_items':grid}

# 4. ads
mp=json.load(open(f'{EV}/meta_parsed.json'))
def meta_ads(tag,keep=None):
    out=[]
    for a in mp[tag]['ads']:
        out.append({'library_id':a['library_id'],'library_url':a['library_url'],'status_at_check':a['status'],'dates':a['dates'],'advertiser_page':a['advertiser'],'variants':a['variants'],'display_domain':a['display_domain'],'first_line':a['first_line']})
    return out
M='https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=CA&search_type=keyword_exact_phrase&q='
def mrec(tag): r=L[tag]; return {'url':r['requested_url'],'checked_utc':r['started_utc'],'result_line':mp[tag]['result_line'],'screenshot':shot(tag+'.png')}
gw={json.loads(l)['alias']:json.loads(l) for l in open(f'{EV}/google_window.jsonl')}
def gcount(tag): return int(re.search(r'\n(\d+) ads?\n',open(f'{EV}/pages/{tag}.txt').read()).group(1))
def grec(a,dom):
    r=L['google-'+a]; w=gw[a]
    return {'search':f'domain {dom}, region Canada','any_time':{'url':r['requested_url'],'checked_utc':r['started_utc'],'ads':gcount('google-'+a),'screenshot':shot('google-'+a+'.png')},
            'window':{'url':w['url'],'checked_utc':w['checked_utc'],'date_label':w['date_label'],'ads':int(w['count_line'].split()[0]),'advertisers':w['advertisers'],'screenshot':shot('google-'+a+'-window.png'),
                      'timezone_note':'Ads Transparency dates are Pacific Time; the window filter is 16 Sep to 15 Oct PT, 3 hours behind Toronto at each end'}}
GC={json.loads(l)['tag']:json.loads(l) for l in open(f'{EV}/google_creatives.jsonl')}
def gcr(tag,**kw):
    r=GC[tag]; ls=re.search(r'Last shown: ([^|]+)',r['main']).group(1).strip(); fm=re.search(r'Format: ([^|]+)',r['main']).group(1).strip()
    return {'creative_url':r['url'],'checked_utc':r['started_utc'],'last_shown':ls,'format':fm,'screenshot':shot(tag+'.png'),**kw}
bondcr=json.load(open(f'{EV}/bond_google_creatives.json'))
BT={1:'Advanced Dental Implants (location ad, dentalimplantsclinic.ca, Toronto)',2:'Dental Implants Clinic - Voted best dentist in Toronto; sitelinks "All On 4 Dental Implants", "Quality Dental Implants"',3:'Location asset: Bond Street Dental - Toronto, 4.5 (1,071)',4:'Open 7 Days a Week - Evening & Weekend...; Bond Street',5:'Do root canals hurt, and what happens during the procedure?',6:'Dental Clinic Toronto; "$99 dental cleaning, exam & digital X-Rays deal"',7:'Map ad: Bond Street Dental; Emergency Dentist Toronto | Same-Day Urgent',8:'Toronto Dental Clinic - Bon...; Bond Street',9:'Best Periodontist in Toronto - Cosmetic Dental Services',10:'Complete Oral Health Plans - Book Your Appointment Today',11:'Need A Dentist Today?',12:'Image carousel, no readable headline',13:'Get cosmetic dentistry - Same-Day Appointment Available; text mentions "Bentway"',14:'Family Dentist Toronto - Appointments Within 20 Minutes (extractions, wisdom teeth)',15:'Same-Day Root Canal Visit - Affordable Root Canal',16:'Dental Implant At $1,599 - Affordable Implants at $1,599',17:'Dental Care When Needed - Affordable Dental Services; Bond Street',18:'Stress Free Dental Visits',19:'Sedation Dentistry Toronto',20:'Dentist appointment today - Dentist Toronto; "available 7 days a week, 365 days a year"',21:'Call Us Today to Schedule',22:'Zoom Whitening for $349 - Same-Day Whitening (teeth_whitening page)',23:'Location asset: Bond Street Dental 4.5 (1.1K)',24:'Bond Street Dental; "We\'re the dentist near you available 7 days a week, 365 days a year"',25:'Image ad: Bond Street Dental',26:'Gentle Dental Care - Vote...; "Flexible scheduling"'}
IMPL={1,2,16}
ads={
 'studiob':{'meta':{'status':'relevant_ads_observed','searches':[mrec('meta-studiob'),mrec('meta-studiob-2')],'note':'Searched twice (second load added scrolling and a full-page screenshot); identical results.','advertiser':'Facebook page "studiobdental"','ads':meta_ads('meta-studiob-2'),
     'implant_ads':[{'library_id':'26002231369395543','in_window':'active at check, started 21 Jan 2026, so running during the window unless paused (the library shows no pause history)','offer_text':'All-on-X package: tooth extractions, 4+ implants, non-removable temporary bridge same day, "$17,990 PER ARCH"; "Final bridge (4–6 months later): $8,900"; Beautifi financing; free in-office and virtual consultations, free panoramic X-ray, full records appointment "$450 in value - FREE"','destination':'Send Message (Messenger) and bio link; no website URL shown'}],
     'other_ads':['1569086177506365: veneers promotion, started 26 Feb 2026, active, display domain INSTAGRAM.COM']},
   'google':{'status':'no_matching_ads_found',**grec('studiob','studiobdental.ca'),'note':'0 ads for the domain at any time. Not proof that the clinic never advertises on Google.'}},
 'nysc':{'meta':{'status':'relevant_ads_observed','searches':[mrec('meta-nysc'),mrec('meta-nysc-sbd')],'advertiser':'Facebook page "North York Smile Centre"','ads':meta_ads('meta-nysc'),
     'implant_ads':[],'note':'All six "North York Smile Centre" ads are one Invisalign offer ($2,000 off plus free scan, X-ray, exam and extras), started 15 Sep to 5 Oct 2026, destination display NORTHYORKSMILECENTRE.FREESMILECONSULT.CLINIC. No implant ad found in these searches. "Smile By Design" exact phrase: no ads.',
     'advertiser_uncertain_items':[{'library_id':'4315299038726791','page':'My Smile Centre','why':'Veneers ad naming Dr. Jerry Jesin "at Smile Centre", started 8 Apr 2026. The NYSC Instagram bio names @mysmilecentre as head office and the NYSC site names Dr. Jesin, but the ad does not name the North York location.'}]},
   'google':{'status':'relevant_ads_observed',**grec('nysc','smile-by-design.ca'),'advertiser':'OneCore Media Corp. (Verified); the website credits OneCore Media (obs ny-credit)','creatives':[
       gcr('google-nysc-cr1',display='My Smile Centre, promo.mysmilecentre.ca',headline='Dental Implant Cost - Toronto Dental Implant Clinic',implant='yes'),
       gcr('google-nysc-cr2',display='My Smile Centre, promo.smile-by-design.ca/allon4',headline='Toronto All on Four Dentistry - All On Four Centre Clinic',implant='yes'),
       gcr('google-nysc-cr3',display='My Smile Centre, promo.smile-by-design.ca',headline='Same-Day Dental Implants - Chipped, cracked, broken teeth',implant='yes')],
     'in_window':'No. 3 ads at any time, all last shown in November 2025; 0 ads in the window.'}},
 'gajjar':{'meta':{'status':'relevant_ads_observed','searches':[mrec('meta-gajjar-dr'),mrec('meta-gajjar')],'advertiser':'Facebook page "Dr. Neil J. Gajjar, Associates & Specialists"','ads':meta_ads('meta-gajjar-dr'),
     'implant_ads':[],'note':'Two active ads started 12 Oct 2026 (inside the window): "Let Dr. Gajjar and his team provide you and your family with dental care in Mississauga", destination DRGAJJAR.COM. General dentistry, not implants. Also one inactive 2024 RCDSO council election ad, outside the window and not marketing; its spend and audience figures are deliberately not recorded. "Gajjar Dentistry": no ads.'},
   'google':{'status':'relevant_ads_observed',**grec('gajjar','drgajjar.com'),'advertiser':'Optio Publishing Inc. (Verified); creatives display "Dr. Neil J. Gajjar" and point to www.drgajjar.com and /cdcp','creatives':[gcr(f'google-gajjar-cr{i}') for i in range(1,5)],
     'in_window':'No. 15 ads at any time; the 4 opened were last shown 31 May 2026; 0 ads in the window. Topics seen: Mississauga family dentists, CDCP accepted. No implant creative seen in the 4 opened (11 not opened).'}},
 'dundas':{'meta':{'status':'no_matching_ads_found','searches':[mrec('meta-dundas')],'note':'Exact phrase "Dundas East Dental", Canada, all ads, all statuses. Not proof of no advertising.'},
   'google':{'status':'no_matching_ads_found',**grec('dundas','dundaseastdental.com'),'note':'0 ads at any time for the domain.'}},
 'bond':{'meta':{'status':'no_matching_ads_found','searches':[mrec('meta-bond')],'note':'Exact phrase "Bond Street Dental". The Google display name "Dental Implants Clinic" and the advertiser "Passion Dental Group" were not searched on Meta.'},
   'google':{'status':'advertiser_uncertain',**grec('bond','dentalimplantsclinic.ca'),'advertiser':'Passion Dental Group Inc (Verified)','why_uncertain':'The ads point to the domain under study and show "Bond Street Dental" location assets, but the website could not be read, so the clinic identity behind the domain is unverified. Becomes relevant_ads_observed once the site confirms Bond Street Dental.',
     'any_time_count':31,'window_count':26,'all_window_creatives_opened':True,'list_source':json.load(open(f'{EV}/bond_google_links.json'))['list_url'],
     'creatives':[{**{k:c[k] for k in ('url','checked_utc','last_shown','format','variations')},'headline_or_asset':BT[c['n']],'implant':'yes' if c['n'] in IMPL else 'no','screenshot':c['shot'] if c['shot'].startswith('/') else f'{EV}/'+c['shot']} for c in bondcr],
     'implant_creatives':'3 of 26: Advanced Dental Implants; Dental Implants Clinic with All On 4 sitelink; Dental Implant At $1,599. The $1,599 headline has no conditions visible in the creative. The cached lead said "$1,799 surgical phase only"; neither figure is verified on the website.',
     'limit':'Only the first variation of each creative was read (several show "1 of N variations").'}}}
doc['ads']=ads
doc['ads_summary']=[{'clinic':a,'platform':p,'status':ads[a][p]['status']} for a in ads for p in ('meta','google')]

# 5. preview
pr=json.load(open(f'{EV}/preview_results.json'))
doc['preview_verification']={'url':'https://helpmemarketing-3kwy4etrg-ankit-kumars-projects-a328efd6.vercel.app/dental-index (share link, deployment dpl_AZXWnTSM1LXB9pXuR46UDEiBsEEy, commit 766f800)','checked_utc':[pr['started_utc'],pr['finished_utc']],'viewports':['1280x900 desktop','390x844 mobile (touch)'],'themes':['light','dark'],
 'passed':['HTTP 200 all four runs; one H1; robots "noindex, nofollow"; canonical https://helpmemarketing.com/dental-index','No horizontal overflow at 1280 or 390; no style attributes; no images without alt','All 9 in-page anchors resolve and land the target at the top of the viewport (rechecked after smooth scroll settled)','Mobile menu opens (aria-expanded true), lists 6 links, closes on Escape','Comparison: table on desktop, five cards on mobile','45 source links; CSV link returns 200 (39 lines = header + 38 rows); /dental-index.html 308 to /dental-index; kit README 404; sitemap has no dental entry','Exactly 3 tests (#dx-test-1..3); 12 "What this means for your clinic" takeaways, 2 labelled pending (Dundas, Bond)','Keyboard: 70 Tab stops on desktop, each with a visible outline; all 6 summaries open on Enter and close on a second Enter','Light theme: 449 text elements checked, 0 below WCAG AA','Both CTAs link to /contact?intent=review&entry=research_dental#contact-form; clicking lands on /contact in review mode and pushes contact_view with entry_point research_dental and contact_intent review; form not submitted','Contact form fields all labelled (checkbox wrapped in its label; honeypot labelled off-screen)'],
 'observed_problems':[{'severity':'fix before release','where':'Dark theme, hero button "See the five clinics" (a.btn.btn-primary, href #dx-compare)','what':'Text rgb(153,153,153) on Signal Orange rgb(255,92,26), contrast 1.08:1 (needs 4.5:1). The rule ".msi.msi a { color: var(--text-muted) }" overrides "body.redesign-prototype .btn-primary { color: var(--bg) }". Light theme is unaffected (14,14,14 on orange).','screenshot':shot('preview-desktop-dark-hero.png'),'scope_note':'The rule is shared Index CSS; other Index pages with a .btn-primary inside .msi were not checked.'}],
 'design_preferences':['Source links in the comparison show raw URL paths as link text (accessible, but long on phones). Preference only.'],
 'not_checked':['Real phones and Safari; screen readers; reduced-motion; the founder\'s Chrome'],
 'screenshots':sorted(f'{EV}/shots/'+f for f in os.listdir(f'{EV}/shots') if f.startswith('preview-'))}

# 6. gaps
doc['unresolved_gaps']=[
 'Dundas East Dental website: blocked to this container ("VPN or Proxy Detected"). Needs a normal browser on an ordinary connection: name, address, phone, implant and full-arch URLs, consultation, cost, financing, form fields, next step, Instagram link.',
 'Bond Street Dental website: Cloudflare challenge. Same fields, plus confirmation on the site itself that dentalimplantsclinic.ca is Bond Street Dental, and the conditions behind any implant price ($1,599 in Google ads; $1,799 surgical phase in the cached lead).',
 'Instagram handles for Dundas and Bond: unverified until their websites are read.',
 '@gajjardentistry posts: refused (HTTP 429). Needs a manual read or an authorised collector.',
 'Instagram coverage for Studio B and NYSC is probable, not complete (logged-out grid of 12; plays missing; videos not watched; collaborator-owned posts on other accounts not searched).',
 'Studio B price conflict: Meta ad "$17,990 PER ARCH" plus "$8,900" final bridge vs website "from $17,900". Recorded, not reconciled.',
 'Gajjar Google: 11 of 15 any-time creatives not opened (none were in the window).',
 'Bond Meta: not searched under "Dental Implants Clinic" or "Passion Dental Group".',
 'Phones for Studio B, NYSC and Gajjar are not recorded in the website observations.',
 'Dark-theme hero button contrast defect on the preview.',
 'Release blockers unchanged: Apps Script redeploy with research_dental, founder review.']
doc['files']={'load_log':f'{EV}/load_log.jsonl','meta_parsed':f'{EV}/meta_parsed.json','google_creatives':f'{EV}/google_creatives.jsonl','google_window':f'{EV}/google_window.jsonl','bond_google_creatives':f'{EV}/bond_google_creatives.json','ig_posts':f'{EV}/ig_posts.jsonl','ig_grid':f'{EV}/ig_grid.json','preview_results':f'{EV}/preview_results.json','page_text':f'{EV}/pages/'}
json.dump(doc,open(f'{EV}/out/dental_evidence_001_2026-10-16.json','w'),indent=1,ensure_ascii=False)
print('written', len(posts),'posts', [ (x['clinic'],x['platform'],x['status']) for x in doc['ads_summary']])
