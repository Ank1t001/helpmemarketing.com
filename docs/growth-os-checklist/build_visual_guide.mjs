// Renders a Growth OS guide (5 fixed US Letter pages, HMM brand) to a PDF.
// Usage: NODE_PATH=$(npm root -g) node docs/growth-os-checklist/build_visual_guide.mjs [seo|meta]
// seo (default): seo-growth-os-visual-guide.html -> HMM-SEO-Growth-OS-Visual-Guide.pdf
// meta: meta-growth-os-overview.html -> HMM-Meta-Growth-OS-PDF-Overview.pdf
import {createRequire} from 'module'; import path from 'path'; import {fileURLToPath} from 'url';
const pw=createRequire(import.meta.url)('playwright'); const dir=path.dirname(fileURLToPath(import.meta.url));
const JOBS={seo:['seo-growth-os-visual-guide.html','HMM-SEO-Growth-OS-Visual-Guide.pdf'],meta:['meta-growth-os-overview.html','HMM-Meta-Growth-OS-PDF-Overview.pdf']};
const [SRC,OUT]=JOBS[process.argv[2]||'seo']||(()=>{throw new Error('use seo or meta')})();
const b=await pw.chromium.launch(); const p=await b.newPage();
await p.goto('file://'+path.join(dir,SRC));
await p.evaluate(() => document.fonts.ready);
// Report any page whose content runs past its fixed height, so nothing is clipped silently.
const over = await p.evaluate(() => [...document.querySelectorAll('.page')].map((s,i)=>{
  const f=s.querySelector('.pf'); const lim=f?f.getBoundingClientRect().top:s.getBoundingClientRect().bottom;
  const kids=[...s.children].filter(c=>!c.matches('.pf'));
  const bottom=Math.max(...kids.map(c=>c.getBoundingClientRect().bottom));
  return bottom>lim-6 ? `page ${i+1} overflows by ${Math.round(bottom-lim+6)}px` : null; }).filter(Boolean));
if (over.length) console.log('WARNING', over.join('; '));
await p.pdf({path:path.join(dir,OUT),width:'8.5in',height:'11in',printBackground:true,preferCSSPageSize:true});
await b.close(); console.log('wrote '+OUT);
