import { createRequire } from 'module'; const { chromium } = createRequire(import.meta.url)('/opt/node22/lib/node_modules/playwright');
import fs from 'fs';
const urls=JSON.parse(process.argv[2]); const b=await chromium.launch(); const ctx=await b.newContext({viewport:{width:1280,height:1000},locale:'en-CA',timezoneId:'America/Toronto'});
const out=[];
for (const [tag,u] of urls){ const p=await ctx.newPage(); const rec={tag,url:u,started_utc:new Date().toISOString()};
 try{const r=await p.goto(u,{waitUntil:'domcontentloaded',timeout:45000});rec.status=r.status();}catch(e){rec.error=String(e).slice(0,150);}
 await p.waitForTimeout(9000);
 rec.main=(await p.evaluate(()=>document.body.innerText)).split('\n').filter(x=>x.trim()).filter(x=>!/^(arrow_|check|search|calendar_today)/.test(x)).slice(0,60).join(' | ');
 rec.frames=[]; for (const f of p.frames()){ if(f===p.mainFrame())continue; try{const t=(await f.evaluate(()=>document.body?document.body.innerText:'')).trim(); if(t) rec.frames.push(t.replace(/\s+/g,' ').slice(0,600)); const links=await f.evaluate(()=>[...document.querySelectorAll('a[href]')].map(a=>a.href).slice(0,5)); if(links.length) rec.frame_links=(rec.frame_links||[]).concat(links);}catch(e){} }
 await p.screenshot({path:'shots/'+tag+'.png'}); rec.finished_utc=new Date().toISOString(); out.push(rec); fs.appendFileSync('google_creatives.jsonl',JSON.stringify(rec)+'\n'); await p.close(); }
await b.close(); console.log(out.length);
