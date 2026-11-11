// Renders seo-growth-os-checklist.html to the PDF that the forms script emails (upload the PDF to Drive).
// Usage: NODE_PATH=$(npm root -g) node docs/growth-os-checklist/build_pdf.mjs
import {createRequire} from 'module'; import path from 'path'; import {fileURLToPath} from 'url';
const pw=createRequire(import.meta.url)('playwright'); const dir=path.dirname(fileURLToPath(import.meta.url));
const b=await pw.chromium.launch(); const p=await b.newPage();
await p.goto('file://'+path.join(dir,'seo-growth-os-checklist.html'));
// Page numbers in the footer; sections are kept whole by .blk/.closing (break-inside: avoid) in the HTML.
const footer = '<div style="width:100%;font-family:Arial,sans-serif;font-size:8px;color:#6b6b6b;padding:0 0.6in;display:flex;justify-content:space-between">'
  + '<span>SEO Growth OS checklist &middot; HelpMeMarketing</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>';
await p.pdf({path:path.join(dir,'HMM-SEO-Growth-OS-Checklist.pdf'),format:'Letter',margin:{top:'0.55in',bottom:'0.7in',left:'0.6in',right:'0.6in'},
  printBackground:true,displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:footer});
await b.close(); console.log('wrote HMM-SEO-Growth-OS-Checklist.pdf');
