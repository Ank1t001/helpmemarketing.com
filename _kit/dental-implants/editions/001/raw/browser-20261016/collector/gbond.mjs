import { createRequire } from 'module'; const { chromium } = createRequire(import.meta.url)('/opt/node22/lib/node_modules/playwright');
import fs from 'fs';
const b=await chromium.launch(); const ctx=await b.newContext({viewport:{width:1280,height:1000},locale:'en-CA',timezoneId:'America/Toronto'});
const p=await ctx.newPage(); await p.goto('https://adstransparency.google.com/?region=CA&domain=dentalimplantsclinic.ca&start-date=2026-09-16&end-date=2026-10-15',{waitUntil:'domcontentloaded'}); await p.waitForTimeout(8000);
await p.getByText('See all ads').first().click(); await p.waitForTimeout(6000);
for(let i=0;i<8;i++){await p.mouse.wheel(0,4000);await p.waitForTimeout(1500);}
const links=[...new Set(await p.evaluate(()=>[...document.querySelectorAll('a[href*="/creative/"]')].map(a=>a.href)))];
fs.writeFileSync('bond_google_links.json',JSON.stringify({listed_utc:new Date().toISOString(),list_url:p.url(),count:links.length,links},null,1));
console.log(p.url(),links.length);
const out=[];
for (const [i,u] of links.entries()){ const q=await ctx.newPage(); const t0=new Date().toISOString(); await q.goto(u,{waitUntil:'domcontentloaded'}); await q.waitForTimeout(7000);
 const t=(await q.evaluate(()=>document.body.innerText)); const ls=(t.match(/Last shown: ([^\n]+)/)||[])[1]; const fm=(t.match(/Format: ([^\n]+)/)||[])[1]; const vr=(t.match(/(\d+ of \d+ variations)/)||[])[1]||null;
 const f='shots/bond-google/cr'+String(i+1).padStart(2,'0')+'.png'; await q.screenshot({path:f,clip:{x:0,y:100,width:1280,height:700}});
 out.push({n:i+1,url:u,checked_utc:t0,advertiser:(t.match(/Ad details\n([^\n]+)/)||[])[1],last_shown:ls,format:fm,variations:vr,shot:f}); await q.close(); }
fs.writeFileSync('bond_google_creatives.json',JSON.stringify(out,null,1)); console.log(out.map(o=>o.n+' '+o.last_shown+' '+o.format+' '+o.variations).join('\n')); await b.close();
