import { createRequire } from 'module'; const { chromium } = createRequire(import.meta.url)('/opt/node22/lib/node_modules/playwright');
const SHARE='https://helpmemarketing-3kwy4etrg-ankit-kumars-projects-a328efd6.vercel.app/dental-index?_vercel_share=REDACTED';
const b=await chromium.launch(); const out={};
for (const theme of ['light','dark']) for (const [dev,vp] of [['desktop',{width:1280,height:900}],['mobile',{width:390,height:844}]]) {
 const ctx=await b.newContext({viewport:vp}); if(theme==='dark') await ctx.addInitScript(()=>{try{localStorage.setItem('hmm_theme','dark')}catch(e){}});
 const p=await ctx.newPage(); await p.goto(SHARE,{waitUntil:'networkidle'}); const k=theme+'-'+dev; out[k]={};
 out[k].btn=await p.evaluate(()=>{const a=[...document.querySelectorAll('header .btn')].map(a=>{const c=getComputedStyle(a);return {t:a.textContent.trim(),color:c.color,bg:c.backgroundColor,bgimg:c.backgroundImage.slice(0,60),border:c.borderColor}});return a;});
 out[k].anchors=[];
 for (const a of await p.locator('a[href^="#dx-"]').evaluateAll(as=>as.map(a=>a.getAttribute('href')))) {
   await p.evaluate(()=>window.scrollTo({top:0,behavior:'instant'})); await p.waitForTimeout(200);
   await p.locator('a[href="'+a+'"]').first().click(); let top; for(let i=0;i<10;i++){await p.waitForTimeout(300); top=await p.evaluate(id=>Math.round(document.getElementById(id).getBoundingClientRect().top),a.slice(1));}
   out[k].anchors.push([a,top]);
 }
 if(dev==='desktop'){ await p.evaluate(()=>scrollTo(0,0)); await p.locator('header').screenshot({path:'shots/preview-desktop-'+theme+'-hero.png'}); }
 await ctx.close();
}
const ctx=await b.newContext(); const p=await ctx.newPage(); await p.goto(SHARE); await p.goto(SHARE.replace('/dental-index','/contact?intent=review&entry=research_dental')+'#contact-form');
out.contact_unlabelled=await p.evaluate(()=>[...document.querySelectorAll('form input, form textarea, form select')].filter(e=>e.offsetParent&&e.type!=='hidden').map(e=>({tag:e.tagName,type:e.type,id:e.id,name:e.name,wrapped:!!e.closest('label'),forLabel:!!(e.id&&document.querySelector('label[for="'+e.id+'"]')),aria:e.getAttribute('aria-label')||e.getAttribute('aria-labelledby')})));
console.log(JSON.stringify(out,null,1)); await b.close();
