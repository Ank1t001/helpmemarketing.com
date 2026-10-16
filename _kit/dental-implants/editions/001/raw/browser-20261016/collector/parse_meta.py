import json,re,sys,glob
out={}
for f in sorted(glob.glob('pages/meta-*.txt')):
    tag=f.split('/')[-1][:-4]; t=open(f).read().replace('​','')
    m=re.search(r'~?(\d+) results?',t); n=m.group(0) if m else ('No ads match your search criteria' if 'No ads match' in t else None)
    parts=re.split(r'\n(Active|Inactive)\nLibrary ID: (\d+)\n',t)
    ads=[]
    for i in range(1,len(parts)-1,3):
        status,lid,body=parts[i],parts[i+1],parts[i+2]
        lines=[l for l in body.split('\n')]
        dates=lines[0].strip()
        try: sp=lines.index('Sponsored')
        except ValueError: sp=None
        adv=lines[sp-1].strip() if sp else None
        multi=next((l for l in lines[:sp] if 'ads use this' in l),None) if sp else None
        txt='\n'.join(lines[sp+1:]).strip() if sp else body
        txt=re.split(r'\n(?:Active|Inactive)\n',txt)[0]
        caps=re.findall(r'\n([A-Z0-9.\-]+\.[A-Z]{2,})\n',txt)
        ads.append(dict(status=status,library_id=lid,library_url=f'https://www.facebook.com/ads/library/?id={lid}',dates=dates,advertiser=adv,variants=multi,display_domain=caps,first_line=txt.split('\n')[0][:140],text=txt[:1200]))
    out[tag]=dict(result_line=n,ads=ads)
json.dump(out,open('meta_parsed.json','w'),indent=1,ensure_ascii=False)
for k,v in out.items():
    print('\n##',k,v['result_line'],len(v['ads']))
    for a in v['ads']: print(' ',a['status'],a['library_id'],a['dates'],'|',a['advertiser'],'|',a['display_domain'],'|',a['first_line'][:90])
