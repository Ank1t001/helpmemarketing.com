// Renders seo-growth-os-checklist.html to the PDF that the forms script emails (upload the PDF to Drive).
// Usage: NODE_PATH=$(npm root -g) node docs/growth-os-checklist/build_pdf.mjs
import {createRequire} from 'module'; import path from 'path'; import {fileURLToPath} from 'url';
const pw=createRequire(import.meta.url)('playwright'); const dir=path.dirname(fileURLToPath(import.meta.url));
const b=await pw.chromium.launch(); const p=await b.newPage();
await p.goto('file://'+path.join(dir,'seo-growth-os-checklist.html'));
await p.pdf({path:path.join(dir,'HMM-SEO-Growth-OS-Checklist.pdf'),format:'Letter',margin:{top:'0.55in',bottom:'0.55in',left:'0.6in',right:'0.6in'},printBackground:true});
await b.close(); console.log('wrote HMM-SEO-Growth-OS-Checklist.pdf');
