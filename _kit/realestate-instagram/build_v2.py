#!/usr/bin/env python3
"""Instagram-only, portable build-kit migration. No deployment or network writes."""
import argparse
import csv
import hashlib
import html
import io
import json
import re
import statistics as st
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
import reindex_data as data
from ig_body import BASE, render, split_shell, snapshot, long_date

def normalise(value):
    return re.sub(r'[\u2013\u2014]', lambda m: ' to ' if
        m.start() > 0 and m.end() < len(value) and value[m.start()-1].isdigit()
        and value[m.end()].isdigit() else ', ', str(value))

def fingerprint():
    payload = {'IG': data.IG, 'IG_BRANDS': data.IG_BRANDS,
               'IG_PEAK_90D': data.IG_PEAK_90D, 'IG_REF': data.IG_REF,
               'postlog': json.loads((BASE/'ig_postlog.json').read_text()),
               'captions': json.loads((BASE/'ig_caps.json').read_text())}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=True).encode()).hexdigest()

def percentile(value, pool):
    if len(pool)<2: return 50.0
    return (sum(x<value for x in pool)+sum(x==value for x in pool)/2)/len(pool)*100

def intent(cl):
    if cl<=0: return 0
    if cl<1.5: return cl/1.5*70
    if cl<=5: return 70+(cl-1.5)/3.5*30
    return max(40,100-(cl-5)*10)

def metrics():
    out={}
    for brand, meta in data.IG_BRANDS.items():
        posts=[p for p in data.IG if p[0]==brand]
        followers=meta['ig_foll']
        if not followers: raise ValueError('Missing followers: '+brand)
        likes=[p[2] for p in posts]; comments=[p[3] for p in posts]
        videos=[p for p in posts if p[5]]
        out[brand]={'n':len(posts),'followers':followers,'median_likes':st.median(likes) if likes else 0,
            'median_comments':st.median(comments) if comments else 0,'er':(st.median(likes) if likes else 0)/followers*100,
            'cl':sum(comments)/sum(likes)*100 if sum(likes) else 0,
            'lv':st.median(p[2]/p[5]*100 for p in videos) if videos else None,
            'peak':max(p[5] for p in videos)/followers if videos else 0,
            'has_video':bool(videos)}
    eligible=[v for v in out.values() if v['n']>=5]
    for brand, m in out.items():
        m['score']=round(.45*percentile(m['er'],[v['er'] for v in eligible])+
            .30*intent(m['cl'])+.25*percentile(-m['peak'],[-v['peak'] for v in eligible]))
        if m['n']<5: m['score']=min(m['score'],30)
        peak90=data.IG_PEAK_90D.get(brand,{}).get('plays',0)/m['followers']
        m['flag']='LOW CADENCE' if m['n']<5 else f'BOOST {peak90:.0f}x' if peak90>=50 else f"PUSH {m['peak']:.0f}x" if m['peak']>=10 else 'ORGANIC'
    for rank,(brand,m) in enumerate(sorted(out.items(),key=lambda p:(-p[1]['score'],-p[1]['er'])),1): m['rank']=rank
    return out

def read_csv(path):
    return list(csv.DictReader(io.StringIO(path.read_text(encoding='utf-8-sig'))))

def verify_scores(actual, path):
    expected=read_csv(path); report=[]
    if {r['brand'] for r in expected} != set(actual): raise ValueError('Scoreboard roster mismatch')
    for row in expected:
        brand=row['brand']; m=actual[brand]; score=int(row.get('ig_score') or row.get('score'))
        rank=int(row['rank']); ok=(m['score']==score and m['rank']==rank)
        report.append({'brand':brand,'expected_score':score,'calculated_score':m['score'],
                       'expected_rank':rank,'calculated_rank':m['rank'],'passed':ok})
    if not all(r['passed'] for r in report): raise ValueError('Published score/rank reproduction failed: '+json.dumps(report))
    return report

class Tables(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.tables=[]; self.depth=0; self.cell=None
    def handle_starttag(self, tag, attrs):
        if tag=='table':
            self.depth+=1
            if self.depth==1: self.current=[]
        if self.depth==1 and tag=='tr': self.row=[]
        if self.depth==1 and tag in ('th','td'): self.cell=[]
    def handle_data(self, text):
        if self.cell is not None: self.cell.append(text)
    def handle_endtag(self, tag):
        if self.depth==1 and tag in ('th','td') and self.cell is not None:
            self.row.append(' '.join(' '.join(self.cell).split())); self.cell=None
        if self.depth==1 and tag=='tr': self.current.append(self.row)
        if tag=='table':
            if self.depth==1: self.tables.append(self.current)
            self.depth-=1

def validate(source, actual, rows, config):
    _,body,_=split_shell(source)
    if '\u2013' in source or '\u2014' in source: raise ValueError('Dash normalisation failed')
    if 'linkedin.com/posts/' in body: raise ValueError('Other-platform research output found')
    if re.search(r'\b(?:Reach|Impressions)\s*</th>',body,re.I): raise ValueError('Private metric column')
    for src in re.findall(r'<img\b[^>]*\bsrc="([^"]+)"',body):
        if not src.startswith('/assets/index/real-estate/frames/'): raise ValueError('Invalid report frame path: '+src)
    if 'api.apify.com' in source: raise ValueError('Signed image URL found')
    # Gate transport is copied from the current repository page, never rebuilt from the old kit.
    shell=(BASE/'site_shell.html').read_text()
    for name in ('GATE_ENDPOINT',):
        pattern=r'var '+name+r'=("[^"\n]+")'
        if re.search(pattern,source).group(1)!=re.search(pattern,shell).group(1): raise ValueError('Gate endpoint changed')
    if "form:'index-download'" not in source: raise ValueError('Current gate payload missing')
    ids=['ri-overview','ri-rankings','ri-creative','ri-insights','ri-test','ri-advanced','ri-data']
    positions=[body.find('id="'+x+'"') for x in ids]
    if -1 in positions or positions!=sorted(positions): raise ValueError('Reading-level section contract failed')
    # Authorship and citation (2026-10-13): byline linked to /about, researcher profile, cite block and edition history.
    cyc,when=config['cycle'],long_date(config['scraped_at'])
    need={'linked byline':'Research and analysis by <b><a href="/about">Ankit Kumar</a></b>',
          'researcher profile':'<h4>About the researcher</h4>','profile links':'<a href="/about">About Ankit</a> &middot; <a href="/work">Explore HMM&rsquo;s work</a>',
          'cite block':f'Edition {cyc}. Data collected {when}.','snapshot link':f'href="/realestate-index/edition-{cyc}"',
          'edition history':'id="ri-editions"','methodology':'<summary>How this research was produced</summary>'}
    for label,text in need.items():
        if text not in body: raise ValueError('Missing '+label)
    # Founder-approved structure, wording and layout (2026-10-13). See EDITORIAL_RULES.md.
    order=['ri-overview','ri-rankings','ri-creative','ri-insights','ri-test','ri-download','ri-advanced','ri-editions','ri-data']
    pos=[body.find('id="'+x+'"') for x in order]
    if -1 in pos or pos!=sorted(pos): raise ValueError('Section order must be '+', '.join(order))
    text=re.sub(r'<script.*?</script>','',body,flags=re.S)
    text=re.sub(r'<table id="postlog">.*?</table>','',text,flags=re.S)   # caption excerpts are quoted evidence
    text=re.sub(r'<[^>]+>',' ',text)
    banned={r'\bBOOST\b':'BOOST flag',r'\bPUSH\b':'PUSH flag',r'\bORGANIC\b':'ORGANIC flag',r'\bWORKING\b':'WORKING status',
            r'\bLANDED\b|NOT LANDING':'landing status',r'best[- ]performing|\bwinning\b':'best-performing or winning',
            r'\d percent\b':'"percent" (use %)',r'\bcycle\b':'"cycle" in visible text (use edition)',r'Advanced research':'old Research heading',
            r'media buy|honest end|PAID PUSH|reach beyond the base':'loaded distribution wording',r'whole category':'"whole category"',
            r'\bverbatim\b':'"verbatim"',r'Your takeaway':'old takeaway label',r'pooled median':'"pooled median"',r'thirty days':'"thirty days"',
            r'\bhealthy band\b':'"healthy band" (use index target band)'}
    for pat,label in banned.items():
        m=re.search(pat,text)
        if m: raise ValueError('Retired wording: '+label+' near "'+' '.join(text[max(0,m.start()-40):m.end()+20].split())+'"')
    if re.search(r'class="flag (?!neutral)',body): raise ValueError('Flags must use the neutral style')
    board_rows=re.search(r'<section id="ri-rankings">.*?<tbody>(.*?)</tbody>',body,re.S)
    if not board_rows or board_rows.group(1).count('data-note="')!=board_rows.group(1).count('<tr'): raise ValueError('Every scoreboard row needs a data-note for the firm panel')
    for label,needle in {'metrics note':'Tap or hover over underlined metrics for a definition.','download heading':'<h2>Download the dataset</h2>',
                         'email label':'<label class="gate-label" for="gate-email">Email address</label>','status live region':'id="gate-msg" role="status" aria-live="polite"',
                         'current edition history row':f'<b>{cyc}</b> (this page)','post log expander':'<summary>Open the post log</summary>'}.items():
        if needle not in body: raise ValueError('Missing '+label)
    shell_css=(BASE/'site_shell.html').read_text()
    for marker in ('Expandables, one pattern','UX spacing pass 2','minmax(min(320px,100%),1fr)','.flag.neutral'):
        if marker not in shell_css or marker not in source: raise ValueError('Layout rules missing from the shell: '+marker)
    head=source.split('</head>')[0]
    if '"@id":"https://helpmemarketing.com/about#ankit-kumar"' not in head or '"@id":"https://helpmemarketing.com/#organization"' not in head: raise ValueError('Article author/publisher not linked')
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>',source,re.S): json.loads(blk)
    parser=Tables(); parser.feed(body)
    headings=['Account','Score','Followers','Posts','Mix','Median likes','Med comm','Like/play','Peak','Flag','Top post']
    board=next((t for t in parser.tables if t and t[0]==headings),None)
    if not board or len(board)-1!=len(actual): raise ValueError('Scoreboard headings or row count changed')
    for row,(brand,m) in zip(board[1:],sorted(actual.items(),key=lambda p:p[1]['rank'])):
        if not row[0].startswith(brand) or int(row[1].split()[0])!=m['score']: raise ValueError('Body score mismatch: '+brand)
        if int(row[2].replace(',',''))!=m['followers'] or int(row[3])!=m['n']: raise ValueError('Body sample mismatch: '+brand)
        if not m['has_video'] and (row[7]!='no video' or row[8]!='no video'): raise ValueError('No-video display mismatch')
    parsed=json.loads(re.search(r'var GATED_CSV=("(?:\\.|[^"\\])*");',body).group(1))
    embedded=list(csv.DictReader(io.StringIO(parsed)))
    if embedded!=rows: raise ValueError('Embedded CSV mismatch')
    if any(r['platform']!='Instagram' for r in embedded): raise ValueError('CSV platform mismatch')
    if any(r['cycle']!=config['cycle'] or r['scraped_at']!=config['scraped_at'] for r in rows): raise ValueError('CSV freshness mismatch')
    return {'scoreboard_contract':True,'reading_level_ids':True,'gate_transport_preserved':True,
            'instagram_only':True,'csv_rows':len(rows),'dash_normalisation':True}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--verify-baseline',action='store_true',help='Historical local QA only; never ready for publication')
    parser.add_argument('--as-of',type=date.fromisoformat,default=date.today())
    args=parser.parse_args()
    config=json.loads((BASE/'ig_cycle.json').read_text())
    review=json.loads((BASE/'body_review.json').read_text())
    if review['cycle']!=config['cycle'] or review['dataset_sha256']!=fingerprint(): raise ValueError('Editorial review belongs to a different dataset')
    body=(BASE/'report_body.html').read_bytes()
    if review['body_sha256']!=hashlib.sha256(body).hexdigest(): raise ValueError('Body changed since review; recheck and record its hash')
    scraped=date.fromisoformat(config['scraped_at']); window=tuple(map(date.fromisoformat,config['window']))
    if window[1]!=scraped or (window[1]-window[0]).days!=30: raise ValueError('Expected explicit 30-day window ending at scrape date')
    if any(not window[0] <= date.fromisoformat(p[1]) <= window[1] for p in data.IG): raise ValueError('Out-of-window post')
    for b,p in data.IG_PEAK_90D.items():
        if not 0 <= (scraped-date.fromisoformat(p['date'])).days <= 90: raise ValueError('Out-of-window peak: '+b)
    if not args.verify_baseline:
        if config['status']!='fresh' or scraped!=args.as_of: raise ValueError('Historical inputs: use --verify-baseline for QA, or supply a fresh complete cycle')
        caps=json.loads((BASE/'ig_caps.json').read_text())
        missing=[p[7] for p in data.IG if p[7] not in caps or not caps[p[7]].get('cap')]
        if missing: raise ValueError('Missing current full captions: '+str(len(missing)))
        if review.get('publication_review')!='complete': raise ValueError('Fresh cycle editorial/creative/advertising review incomplete')
    actual=metrics()
    scores=verify_scores(actual,BASE/config['expected_scoreboard']) if args.verify_baseline else None
    if not args.verify_baseline:
        prior=json.loads((BASE/config['prior_verification']).read_text())
        if prior.get('status') not in ('verified','exception_approved') or prior.get('cycle')!=config['prior_cycle']: raise ValueError('Prior-cycle verification blocked')
        if prior['status']=='exception_approved' and not (prior.get('approved_by') and prior.get('approved_on')): raise ValueError('Baseline exception lacks a recorded approver and date')
    csv_text=normalise((BASE/config['postlog_csv']).read_text())
    rows=list(csv.DictReader(io.StringIO(csv_text)))
    ranked=[r for r in rows if r['cohort']!='REFERENCE']
    if len(ranked)!=len(data.IG): raise ValueError('Postlog does not match ranked dataset')
    bycode={p[7]:p for p in data.IG}
    for row in ranked:
        code=row['url'].rstrip('/').split('/')[-1]; p=bycode.get(code)
        if p is None or row['brand']!=p[0] or int(row['likes'])!=p[2] or int(row['comments'])!=p[3]: raise ValueError('Postlog metric mismatch')
    next_date=date.fromisoformat(config['next_scheduled_refresh'])
    if next_date.day!=14 or next_date<=scraped: raise ValueError('Next scheduled refresh must be a future monthly 14th')
    source=normalise(render(csv_text,config['cycle'],config['scraped_at'],next_date.isoformat(),args.as_of.isoformat(),config.get('modified_at')))
    checks=validate(source,actual,rows,config)
    output=BASE/'output'; output.mkdir(exist_ok=True)
    name='HISTORICAL_QA_cycle003.html' if args.verify_baseline else 'Re Index Instagram v8.html'
    (output/name).write_text(source,encoding='utf-8')
    if not args.verify_baseline:
        snap=snapshot(source,config['cycle'],config['scraped_at'])
        if re.findall(r'<meta name="robots"[^>]*>',snap)!=['<meta name="robots" content="noindex, follow">']: raise ValueError('Snapshot must carry exactly one robots tag: noindex, follow')
        if '"datePublished"' in source: raise ValueError('datePublished must stay absent until first publication is substantiated')
        if f'"dateModified":"{config["modified_at"]}"' not in source or f'"dateModified":"{config["modified_at"]}"' not in snap: raise ValueError('dateModified must equal the recorded modified_at')
        if '"image":{"@type":"ImageObject","url":"https://helpmemarketing.com/assets/index/real-estate/og.jpg"' not in source: raise ValueError('Article image missing')
        (output/f"edition-{config['cycle']}.html").write_text(snap,encoding='utf-8')
    (output/'cycle_metrics.json').write_text(json.dumps(actual,indent=2))
    result={'cycle':config['cycle'],'scraped_at':config['scraped_at'],
            'status':'historical_qa_only' if args.verify_baseline else 'review_candidate',
            'production_ready':False,'checks':checks,'score_reproduction':scores,
            'prior_cycle_verification':json.loads((BASE/config['prior_verification']).read_text())}
    (output/'validation.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
