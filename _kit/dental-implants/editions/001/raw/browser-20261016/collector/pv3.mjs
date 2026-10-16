import { createRequire } from 'module'; const { chromium } = createRequire(import.meta.url)('/opt/node22/lib/node_modules/playwright');
const SHARE='https://helpmemarketing-3kwy4etrg-ankit-kumars-projects-a328efd6.vercel.app/dental-index?_vercel_share=REDACTED';
const b=await chromium.launch(); const ctx=await b.newContext({viewport:{width:1280,height:900}}); await ctx.addInitScript(()=>{try{localStorage.setItem('hmm_theme','dark')}catch(e){}});
const p=await ctx.newPage(); await p.goto(SHARE,{waitUntil:'networkidle'});
const cdp=await ctx.newCDPSession(p); await cdp.send('DOM.enable'); await cdp.send('CSS.enable');
const {root}=await cdp.send('DOM.getDocument'); const {nodeId}=await cdp.send('DOM.querySelector',{nodeId:root.nodeId,selector:'header .btn-primary'});
const m=await cdp.send('CSS.getMatchedStylesForNode',{nodeId});
for (const r of m.matchedCSSRules) { const c=r.rule.style.cssProperties.filter(x=>x.name==='color'&&x.value); if(c.length) console.log(r.rule.selectorList.text.slice(0,160),'=>',c.map(x=>x.value+(x.important?' !important':'')).join(',')); }
await b.close();
