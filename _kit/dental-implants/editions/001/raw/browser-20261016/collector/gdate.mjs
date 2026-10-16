import { createRequire } from 'module'; const { chromium } = createRequire(import.meta.url)('/opt/node22/lib/node_modules/playwright');
const b=await chromium.launch(); const ctx=await b.newContext({viewport:{width:1280,height:1000},locale:'en-CA',timezoneId:'America/Toronto'});
const p=await ctx.newPage(); await p.goto('https://adstransparency.google.com/?region=CA&domain=drgajjar.com',{waitUntil:'domcontentloaded'}); await p.waitForTimeout(8000);
await p.getByText('Any time').first().click(); await p.waitForTimeout(1500);
console.log((await p.evaluate(()=>document.body.innerText)).split('\n').filter(x=>x.trim()).slice(0,80).join(' | '));
await p.screenshot({path:'shots/google-gajjar-datefilter.png'}); await b.close();
