import { createRequire } from 'module'; const { chromium } = createRequire(import.meta.url)('/opt/node22/lib/node_modules/playwright');
import fs from 'fs';
const rows=JSON.parse(fs.readFileSync('ig_grid.json')).filter(r=>r.derived_in_window);
const b=await chromium.launch(); const ctx=await b.newContext({viewport:{width:1280,height:1000},locale:'en-CA',timezoneId:'America/Toronto'});
for (const r of rows){ const p=await ctx.newPage(); const rec={url:r.url,shortcode:r.shortcode,handle:r.handle,checked_utc:new Date().toISOString()};
 const resp=await p.goto(r.url,{waitUntil:'domcontentloaded',timeout:45000}).catch(e=>null); rec.status=resp?resp.status():null; await p.waitForTimeout(6000); rec.final_url=p.url();
 Object.assign(rec, await p.evaluate(()=>{const m=n=>document.querySelector('meta[property="'+n+'"],meta[name="'+n+'"]')?.content||null; const t=[...document.querySelectorAll('time[datetime]')].map(x=>({dt:x.getAttribute('datetime'),title:x.getAttribute('title'),text:x.textContent})); return {og_title:m('og:title'),og_desc:m('og:description'),description:m('description'),og_type:m('og:type'),times:t.slice(0,3),text:document.body.innerText.slice(0,1500)};}).catch(()=>({})));
 await p.screenshot({path:'shots/ig/'+r.shortcode+'.png'}); fs.appendFileSync('ig_posts.jsonl',JSON.stringify(rec)+'\n'); console.log(rec.handle,rec.shortcode,rec.status,rec.final_url.slice(0,60),(rec.og_desc||'').slice(0,120));
 await p.close(); if(rec.status===429||/accounts\/login/.test(rec.final_url)){console.log('STOP: refused');break;} await new Promise(s=>setTimeout(s,4000)); }
await b.close();
