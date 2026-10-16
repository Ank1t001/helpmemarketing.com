import { createRequire } from 'module'; const { chromium } = createRequire(import.meta.url)('/opt/node22/lib/node_modules/playwright');
import fs from 'fs'; import crypto from 'crypto';
const [,, tag, url, wait='6000', vw='1280'] = process.argv;
const b=await chromium.launch(); const ctx=await b.newContext({viewport:{width:+vw,height:900}, locale:'en-CA', timezoneId:'America/Toronto'});
const p=await ctx.newPage(); const rec={tag,requested_url:url,started_utc:new Date().toISOString()};
try { const r=await p.goto(url,{waitUntil:'domcontentloaded',timeout:45000}); rec.status=r?r.status():null; rec.headers_server=r?r.headers()['server']:null; }
catch(e){ rec.error=String(e).slice(0,200); }
await p.waitForTimeout(+wait);
for(let i=0;i<(+process.env.SCROLLS||0);i++){await p.mouse.wheel(0,4000);await p.waitForTimeout(1500);}
rec.links=await p.evaluate(()=>[...document.querySelectorAll('a[href]')].map(a=>a.href).filter(h=>!/facebook\.com\/(policies|privacy|help|legal)|metastatus|about\.meta/.test(h))).catch(()=>[]);
rec.final_url=p.url(); rec.title=await p.title().catch(()=>null);
const html=await p.content().catch(()=>''); const text=await p.evaluate(()=>document.body?document.body.innerText:'').catch(()=>'');
rec.html_sha256=crypto.createHash('sha256').update(html).digest('hex'); rec.html_bytes=html.length; rec.text_chars=text.length;
rec.challenge=/Just a moment|cf-chl|challenge-platform|Verify you are human|Checking your browser|captcha/i.test(html+text);
rec.login_wall=/Log in to Facebook|You must log in|Log into Facebook/i.test(text);
 fs.writeFileSync('pages/'+tag+'.txt',text);
await p.screenshot({path:'shots/'+tag+'.png',fullPage:!!process.env.FULL}).catch(()=>{});
rec.finished_utc=new Date().toISOString(); fs.appendFileSync('load_log.jsonl',JSON.stringify(rec)+'\n'); const {links,...short}=rec;console.log(JSON.stringify(short)); await b.close();
