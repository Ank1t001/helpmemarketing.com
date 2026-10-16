import { createRequire } from 'module'; const { chromium } = createRequire(import.meta.url)('/opt/node22/lib/node_modules/playwright');
import fs from 'fs';
const OUT = process.argv[2];
const SHARE = 'https://helpmemarketing-3kwy4etrg-ankit-kumars-projects-a328efd6.vercel.app/dental-index?_vercel_share=REDACTED';
const BASE = 'https://helpmemarketing-3kwy4etrg-ankit-kumars-projects-a328efd6.vercel.app';
const res = { started_utc: new Date().toISOString(), runs: [] };
const b = await chromium.launch();
for (const [name, vp, mobile] of [['desktop',{width:1280,height:900},false],['mobile',{width:390,height:844},true]]) {
 for (const theme of ['light','dark']) {
  const ctx = await b.newContext({ viewport: vp, isMobile: mobile, hasTouch: mobile, deviceScaleFactor: 1 });
  if (theme==='dark') await ctx.addInitScript(()=>{try{localStorage.setItem('hmm_theme','dark')}catch(e){}});
  const p = await ctx.newPage();
  const r = { device: name, theme, checked_utc: new Date().toISOString() };
  const resp = await p.goto(SHARE, { waitUntil: 'networkidle' });
  r.status = resp.status(); r.url = p.url();
  r.dom = await p.evaluate(() => {
    const q=s=>[...document.querySelectorAll(s)];
    const anchors = q('a[href^="#"]').map(a=>({href:a.getAttribute('href'), text:a.textContent.trim().slice(0,60), target_exists: !!document.getElementById(a.getAttribute('href').slice(1))}));
    const navLinks = q('nav.nav a, #nav-mobile-menu a').map(a=>a.getAttribute('href'));
    const srcLinks = q('.dx-src a').map(a=>({href:a.href, aria:a.getAttribute('aria-label'), text:a.textContent.trim()}));
    const csv = q('a[href$=".csv"]').map(a=>a.getAttribute('href'));
    const tests = q('#dx-tests [id^="dx-test-"]').length;
    const takeaways = q('.note.take').map(n=>({pending:n.classList.contains('dx-pending'), lbl:(n.querySelector('.lbl')||{}).textContent, text:n.textContent.trim().slice(0,200)}));
    const placeholders = q('.dx-ph, .dx-pending, .dx-miss').map(e=>({cls:e.className, text:e.textContent.trim().replace(/\s+/g,' ').slice(0,160)}));
    const cmpTable = document.querySelector('#dx-compare table');
    const cmpVisible = cmpTable ? getComputedStyle(cmpTable).display : null;
    const cmpCards = q('#dx-compare .card, #dx-compare [class*="card"]').filter(e=>e.offsetParent).length;
    const cmpRows = cmpTable ? q('#dx-compare tbody tr').map(tr=>[...tr.children].map(c=>c.textContent.trim().replace(/\s+/g,' ').slice(0,80))) : [];
    const details = q('details').map(d=>({summary:d.querySelector('summary')?.textContent.trim().slice(0,80), open:d.open}));
    const cta = q('[data-review-cta]').map(a=>({href:a.getAttribute('href'), entry:a.getAttribute('data-review-cta'), text:a.textContent.trim()}));
    const robots = q('meta[name="robots"]').map(m=>m.content);
    const canonical = document.querySelector('link[rel=canonical]')?.href;
    const h1 = q('h1').map(h=>h.textContent.trim());
    const overflowX = document.documentElement.scrollWidth > window.innerWidth;
    const inline = q('[style]').filter(e=>!e.closest('#hmm-consent, .hmm-consent')).map(e=>e.tagName+'.'+e.className).slice(0,10);
    const formsOnPage = q('form, input, select, textarea').length;
    const imgsNoAlt = q('img:not([alt])').length;
    return {anchors, navLinks, srcLinks, csv, tests, takeaways, placeholders, cmpVisible, cmpCards, cmpRows, details, cta, robots, canonical, h1, overflowX, inline, formsOnPage, imgsNoAlt, docW: document.documentElement.scrollWidth, winW: innerWidth};
  });
  // contrast audit on visible text in main
  r.contrast = await p.evaluate(() => {
    function parse(c){const m=c.match(/rgba?\(([^)]+)\)/);if(!m)return null;const a=m[1].split(/[ ,\/]+/).filter(Boolean).map(Number);return {r:a[0],g:a[1],b:a[2],a:a.length>3?a[3]:1};}
    function lum({r,g,b}){return [r,g,b].map(v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)}).reduce((s,v,i)=>s+v*[0.2126,0.7152,0.0722][i],0);}
    function bg(el){const stack=[];for(let e=el;e;e=e.parentElement){const c=parse(getComputedStyle(e).backgroundColor);if(c&&c.a>0)stack.push(c);if(c&&c.a>=1)break;}
      let base={r:255,g:255,b:255};if(stack.length&&stack[stack.length-1].a>=1){base=stack.pop();}else{base=parse(getComputedStyle(document.body).backgroundColor)||base;}
      while(stack.length){const c=stack.pop();base={r:c.r*c.a+base.r*(1-c.a),g:c.g*c.a+base.g*(1-c.a),b:c.b*c.a+base.b*(1-c.a)};}return base;}
    const fails=[];let n=0;
    const walker=document.createTreeWalker(document.querySelector('.msi')||document.body,NodeFilter.SHOW_TEXT);
    const seen=new Set();
    while(walker.nextNode()){const t=walker.currentNode;if(!t.textContent.trim())continue;const el=t.parentElement;if(seen.has(el)||!el.offsetParent)continue;seen.add(el);
      const cs=getComputedStyle(el);if(cs.visibility==='hidden'||+cs.opacity===0)continue;let fg=parse(cs.color);if(!fg)continue;const b=bg(el);
      if(fg.a<1)fg={r:fg.r*fg.a+b.r*(1-fg.a),g:fg.g*fg.a+b.g*(1-fg.a),b:fg.b*fg.a+b.b*(1-fg.a)};
      const L1=lum(fg),L2=lum(b);const cr=(Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);n++;
      const size=parseFloat(cs.fontSize),bold=+cs.fontWeight>=700;const large=size>=24||(size>=18.66&&bold);const need=large?3:4.5;
      if(cr<need)fails.push({text:el.textContent.trim().slice(0,50),tag:el.tagName,cls:el.className,ratio:+cr.toFixed(2),need,size});}
    return {checked:n,fails:fails.slice(0,25),fail_count:fails.length};
  });
  // keyboard: tab through first 60 stops and record focus visibility
  if (!mobile) {
    await p.evaluate(()=>window.scrollTo(0,0));
    await p.locator('body').click({position:{x:5,y:5}}).catch(()=>{});
    const stops=[];
    for (let i=0;i<70;i++){ await p.keyboard.press('Tab'); const s=await p.evaluate(()=>{const e=document.activeElement;if(!e||e===document.body)return null;const cs=getComputedStyle(e);return {tag:e.tagName,text:(e.getAttribute('aria-label')||e.textContent||'').trim().replace(/\s+/g,' ').slice(0,50),href:e.getAttribute('href'),outline:cs.outlineStyle+' '+cs.outlineWidth,boxShadow:cs.boxShadow!=='none'};}); stops.push(s); }
    r.tab_stops = stops;
    r.tab_no_visible_focus = stops.filter(s=>s && s.outline.startsWith('none') && !s.boxShadow).map(s=>s.tag+' '+s.text);
    // summaries: focus and Enter
    const sums = await p.locator('details > summary').count(); r.summary_keyboard=[];
    for (let i=0;i<sums;i++){ const s=p.locator('details > summary').nth(i); await s.focus(); const before=await s.evaluate(e=>e.parentElement.open); await p.keyboard.press('Enter'); const after=await s.evaluate(e=>e.parentElement.open); await p.keyboard.press('Enter'); const back=await s.evaluate(e=>e.parentElement.open); r.summary_keyboard.push({text:(await s.textContent()).trim().slice(0,70),before,after_enter:after,after_second_enter:back}); }
    // anchor click test
    r.anchor_scroll=[];
    for (const id of ['dx-compare','dx-tests','dx-method']) { await p.evaluate(()=>window.scrollTo(0,0)); const a=p.locator(`a[href="#${id}"]`).first(); if(await a.count()){ await a.click(); await p.waitForTimeout(600); const top=await p.evaluate(i=>Math.round(document.getElementById(i).getBoundingClientRect().top),id); r.anchor_scroll.push({id,top_after_click:top,hash:await p.evaluate(()=>location.hash)}); } }
  }
  // mobile: menu
  if (mobile) {
    const hb=p.locator('.nav-hamburger'); r.menu={exists:await hb.count()};
    if (r.menu.exists){ await hb.click(); await p.waitForTimeout(300); r.menu.expanded=await hb.getAttribute('aria-expanded'); r.menu.links=await p.locator('#nav-mobile-menu a').evaluateAll(as=>as.filter(a=>a.offsetParent).map(a=>a.getAttribute('href'))); await p.keyboard.press('Escape'); r.menu.after_escape=await hb.getAttribute('aria-expanded'); }
  }
  if (theme==='light') {
    for (const id of ['top','dx-answer','dx-findings','dx-compare','dx-examples','dx-accounts','dx-patterns','dx-tests','dx-method','dx-help']) {
      const f=`${OUT}/shots/preview-${name}-${id}.png`;
      if (id==='top') { await p.evaluate(()=>window.scrollTo(0,0)); await p.screenshot({path:f}); }
      else { const el=p.locator('#'+id); if(await el.count()){ await el.scrollIntoViewIfNeeded(); await p.waitForTimeout(200); await el.screenshot({path:f}).catch(e=>r['shot_err_'+id]=String(e).slice(0,100)); } }
    }
    // CTA click: no submit
    const cta=p.locator('[data-review-cta="research_dental"]').first();
    if (await cta.count()) {
      await p.evaluate(()=>{window.__dl=[];const o=window.dataLayer||(window.dataLayer=[]);const push=o.push.bind(o);o.push=function(x){window.__dl.push(x);return push(x)};});
      await cta.scrollIntoViewIfNeeded();
      const [nav] = await Promise.all([p.waitForNavigation({waitUntil:'networkidle'}), cta.click()]);
      r.cta_click = { landed: p.url(), status: nav && nav.status() };
      r.cta_contact = await p.evaluate(()=>({intentClass:document.documentElement.classList.contains('intent-review'), dl:(window.dataLayer||[]).filter(x=>x&&x.event).map(x=>({event:x.event,entry_point:x.entry_point,contact_intent:x.contact_intent})), formExists:!!document.querySelector('form'), labels:[...document.querySelectorAll('form input:not([type=hidden]):not([tabindex="-1"]), form textarea, form select')].filter(e=>e.offsetParent).map(e=>({name:e.name, label: (e.id && document.querySelector(`label[for="${e.id}"]`)?.textContent.trim().slice(0,60)) || e.getAttribute('aria-label') || null}))}));
      await p.screenshot({path:`${OUT}/shots/preview-${name}-cta-contact.png`});
    }
  }
  res.runs.push(r); await ctx.close();
 }
}
// CSV and other URLs
const ctx = await b.newContext(); const p = await ctx.newPage(); await p.goto(SHARE);
res.http = {};
for (const path of ['/assets/index/dental/dental-index-edition-001-observations.csv','/dental-index.html','/_kit/dental-implants/README.md','/sitemap.xml']) {
  const r = await p.request.get(BASE+path, {maxRedirects:0}); const body = r.status()===200 ? await r.text() : '';
  res.http[path] = { status: r.status(), location: r.headers()['location']||null, bytes: body.length, lines: body ? body.trim().split('\n').length : null, mentions_dental: path==='/sitemap.xml' ? body.includes('dental-index') : undefined };
}
res.finished_utc = new Date().toISOString();
fs.writeFileSync(`${OUT}/preview_results.json`, JSON.stringify(res, null, 1));
await b.close();
console.log('done');
