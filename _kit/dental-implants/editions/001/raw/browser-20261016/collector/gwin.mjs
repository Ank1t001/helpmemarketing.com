import { createRequire } from 'module'; const { chromium } = createRequire(import.meta.url)('/opt/node22/lib/node_modules/playwright');
import fs from 'fs';
const b=await chromium.launch(); const ctx=await b.newContext({viewport:{width:1280,height:1000},locale:'en-CA',timezoneId:'America/Toronto'});
for (const [a,d] of [['studiob','studiobdental.ca'],['nysc','smile-by-design.ca'],['gajjar','drgajjar.com'],['dundas','dundaseastdental.com'],['bond','dentalimplantsclinic.ca']]) {
 const p=await ctx.newPage(); const u='https://adstransparency.google.com/?region=CA&domain='+d+'&start-date=2026-09-16&end-date=2026-10-15'; const t0=new Date().toISOString();
 await p.goto(u,{waitUntil:'domcontentloaded'}); await p.waitForTimeout(9000);
 for(let i=0;i<3;i++){await p.mouse.wheel(0,3000);await p.waitForTimeout(1200);}
 const txt=(await p.evaluate(()=>document.body.innerText)).split('\n').filter(x=>x.trim());
 const i=txt.findIndex(x=>/^\d+ ads?$/.test(x)); const rec={alias:a,url:u,final_url:p.url(),checked_utc:t0,count_line:txt[i],date_label:txt[i+2],advertisers:[...new Set(txt.slice(i,i+80).filter((x,k,arr)=>arr[k+1]==='Verified'))],creatives:[...new Set(await p.evaluate(()=>[...document.querySelectorAll('a[href*="/creative/"]').values()].map(a=>a.href)))]};
 await p.screenshot({path:'shots/google-'+a+'-window.png',fullPage:true}); fs.appendFileSync('google_window.jsonl',JSON.stringify(rec)+'\n'); console.log(JSON.stringify(rec)); await p.close(); }
await b.close();
