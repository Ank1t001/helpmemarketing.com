"""Bounded server fetch of public provider pages for the Business Cards & Spend Management Index (the edition 001 collector).
The output directory is private storage: never inside the repository or the deployment.
Usage: python3 -I collect.py OUTDIR PLATFORM ROLE URL [URL ...]
Saves raw HTML (gz), visible text and links; appends one JSON line per fetch to OUTDIR/fetch_log.jsonl.
Method recorded as server fetch (curl), no JavaScript rendering, no cookies, no login."""
import sys, os, json, gzip, hashlib, subprocess, datetime, re
from html.parser import HTMLParser
from zoneinfo import ZoneInfo
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True); s.skip=0; s.out=[]; s.links=[]; s.a=None; s.title=''; s.intitle=False
    def handle_starttag(s,t,a):
        if t in ('script','style','noscript','svg','template'): s.skip+=1
        if t=='title': s.intitle=True
        if t=='a': s.a=[dict(a).get('href') or '', []]
        if t in ('p','div','li','h1','h2','h3','h4','h5','h6','br','tr','section','article','td','th','dt','dd'): s.out.append('\n')
    def handle_endtag(s,t):
        if t in ('script','style','noscript','svg','template') and s.skip: s.skip-=1
        if t=='title': s.intitle=False
        if t=='a' and s.a is not None:
            s.links.append((s.a[0], ' '.join(''.join(s.a[1]).split()))); s.a=None
    def handle_data(s,d):
        if s.intitle: s.title+=d
        if s.skip: return
        s.out.append(d)
        if s.a is not None: s.a[1].append(d)
def slug(u): return re.sub(r'[^a-z0-9]+','-',u.lower().split('://',1)[-1]).strip('-')[:90]
def main():
    out, plat, role, urls = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
    os.makedirs(out, exist_ok=True)
    for u in urls:
        t0 = datetime.datetime.now(ZoneInfo('America/Toronto')).isoformat(timespec='seconds')
        r = subprocess.run(['curl','-sS','-L','--max-time','40','--compressed','-A',UA,'-H','Accept-Language: en-CA,en;q=0.9','-o','-','-w','\n__META__%{http_code} %{url_effective} %{content_type}',u], capture_output=True)
        body, _, meta = r.stdout.rpartition(b'\n__META__')
        code, final, ctype = (meta.decode(errors='replace').split(' ',2)+['',''])[:3]
        h = hashlib.sha256(body).hexdigest(); sl = slug(final or u)
        rec = {'platform':plat,'role':role,'requested_url':u,'final_url':final,'http_status':int(code or 0),'content_type':ctype,'bytes':len(body),'sha256':h,'fetched_at':t0,'method':'server fetch (curl), no JavaScript, no cookies','file':sl,'error':r.stderr.decode(errors='replace').strip()[:200]}
        if body and 'html' in ctype:
            with gzip.open(f'{out}/{sl}.html.gz','wb') as f: f.write(body)
            p = P(); p.feed(body.decode('utf-8','replace'))
            txt = re.sub(r'\n\s*\n+','\n', re.sub(r'[ \t\xa0]+',' ',''.join(p.out)))
            open(f'{out}/{sl}.txt','w').write(txt.strip()+'\n')
            json.dump({'title':p.title.strip(),'links':p.links}, open(f'{out}/{sl}.links.json','w'))
            rec['title']=p.title.strip(); rec['text_chars']=len(txt)
        open(f'{out}/fetch_log.jsonl','a').write(json.dumps(rec)+'\n')
        print(rec['http_status'], plat, role, final, rec.get('text_chars'), rec.get('title','')[:70])
main()
