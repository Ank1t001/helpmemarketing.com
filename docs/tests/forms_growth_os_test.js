// Runs the real forms script (docs/HMM_Forms_AppsScript.gs) in Node with stand-ins for the Apps Script services,
// and checks the SEO Growth OS download bot checks (d2, 2026-11-10).
// Usage: node docs/tests/forms_growth_os_test.js   (exits 1 on any failure)
const fs = require('fs'), path = require('path'), vm = require('vm'), assert = require('assert'), crypto = require('crypto');

function load(opts) {
  const sheets = {}, mails = [], fetches = [], attachments = [], messages = [], props = {};
  const sheet = name => sheets[name] || (sheets[name] = {
    rows: [],
    getLastRow() { return this.rows.length; },
    appendRow(r) { this.rows.push(r); },
    getRange(r, c, nr, nc) { const rows = this.rows; return {
      setFontWeight() {}, getValues() { return rows.slice(r - 1, r - 1 + nr).map(x => x.slice(c - 1, c - 1 + nc)); } }; },
    setFrozenRows() {},
    deleteRow(n) { this.rows.splice(n - 1, 1); }
  });
  const ctx = {
    console: { log() {}, error() {}, warn() {} }, JSON, Date, Math, String, Object, Array,
    PropertiesService: { getScriptProperties: () => ({ getProperty: k => (k === 'TURNSTILE_SECRET' ? opts.secret : props[k] || null), setProperty: (k, v) => { props[k] = v; } }) },
    HtmlService: { createHtmlOutput: h => ({ html: h, setTitle() { return this; } }) },
    UrlFetchApp: { fetch: (url, o) => { fetches.push(url); const r = opts.siteverify(o.payload.response);
      return { getResponseCode: () => 200, getContentText: () => JSON.stringify(r) }; } },
    SpreadsheetApp: { getActiveSpreadsheet: () => ({ getSheetByName: n => sheets[n] || null, insertSheet: n => sheet(n) }) },
    LockService: { getScriptLock: () => ({ waitLock() {}, releaseLock() {} }) },
    ContentService: { MimeType: { JSON: 'json' }, createTextOutput: t => ({ text: t, setMimeType() { return this; } }) },
    MailApp: { sendEmail: m => { if (opts.mailThrows) throw new Error('Service invoked too many times'); mails.push(m.to); attachments.push(m.attachments); messages.push(m); }, getRemainingDailyQuota: () => 100 },
    DriveApp: { getFileById: id => {
      if (opts.fileMissing) throw new Error('No item with the given ID could be found: ' + id);
      const mime = opts.mime || 'application/pdf';
      return { getMimeType: () => mime, getBlob: () => ({ name: '', getContentType: () => opts.blobType || mime, setName(n) { this.name = n; return this; } }) };
    } },
    Logger: { log() {} }, CacheService: { getScriptCache: () => ({ get() { return null; }, put() {}, remove() {} }) },
    Utilities: { getUuid: () => crypto.randomUUID(), computeHmacSha256Signature: (v, k) => [...crypto.createHmac('sha256', k).update(v).digest()],
      base64EncodeWebSafe: b => Buffer.from(b).toString('base64').replace(/\+/g, '-').replace(/\//g, '_') }, Session: { getActiveUser: () => ({ getEmail: () => '' }) }
  };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(__dirname, '..', 'HMM_Forms_AppsScript.gs'), 'utf8'), ctx);
  if (opts.fileId !== undefined) vm.runInContext('SEO_CHECKLIST_FILE_ID = ' + JSON.stringify(opts.fileId) + ';', ctx);
  else vm.runInContext("SEO_CHECKLIST_FILE_ID = 'test-checklist-id';", ctx);
  const post = body => JSON.parse(ctx.doPost({ postData: { contents: JSON.stringify(body) } }).text);
  return { post, sheets, mails, fetches, attachments, messages, ctx, get: q => ctx.doGet({ parameter: q }), confirm: q => ctx.doPost({ parameter: q }) };
}

const GOOD = { success: true, action: 'growth_os_download', hostname: 'helpmemarketing.com' };
const siteverify = t => (t === 'good-token' ? GOOD : { success: false, 'error-codes': ['invalid-input-response'] });
const base = { form: 'growth-os-download', product: 'seo', marketingConsent: true, source: '/seo-growth-os', referrer: '', userAgent: 'test' };
const rows = (env, tab) => (env.sheets[tab] ? env.sheets[tab].rows.slice(1) : []);
let failed = 0;
function test(name, fn) { try { fn(); console.log('ok   ' + name); } catch (e) { failed++; console.log('FAIL ' + name + '\n     ' + e.message); } }

test('trap field filled: rejected, Spam row with the /contact reason, no email, no Subscribers row', () => {
  const env = load({ secret: 'x', siteverify });
  const r = env.post({ ...base, email: 'a@example.com', company_url_secondary: 'http://bot', client_flag: 'trap', trap_value: 'http://bot', 'cf-turnstile-response': 'good-token' });
  assert.deepStrictEqual([r.result, r.saved], ['ok', 'spam']);
  assert.strictEqual(rows(env, 'Spam')[0][4], 'Page bot check: Hidden trap field was filled (trap held: http://bot)');
  assert.strictEqual(env.mails.length, 0); assert.strictEqual(rows(env, 'Subscribers').length, 0); assert.strictEqual(rows(env, 'Growth OS downloads').length, 0);
});

test('trap filled with no client flag (direct post): rejected as Honeypot filled', () => {
  const env = load({ secret: 'x', siteverify });
  const r = env.post({ ...base, email: 'b@example.com', company_url_secondary: 'x', 'cf-turnstile-response': 'good-token' });
  assert.strictEqual(r.saved, 'spam'); assert.strictEqual(rows(env, 'Spam')[0][4], 'Honeypot filled'); assert.strictEqual(env.mails.length, 0);
});

test('no Turnstile token: rejected, Spam row "No Turnstile token", no email, no Subscribers row', () => {
  const env = load({ secret: 'x', siteverify });
  const r = env.post({ ...base, email: 'c@example.com' });
  assert.strictEqual(r.saved, 'spam'); assert.strictEqual(rows(env, 'Spam')[0][4], 'No Turnstile token');
  assert.strictEqual(env.mails.length, 0); assert.strictEqual(rows(env, 'Subscribers').length, 0);
});

test('token that fails verification: rejected with the /contact reason text', () => {
  const env = load({ secret: 'x', siteverify });
  const r = env.post({ ...base, email: 'd@example.com', 'cf-turnstile-response': 'bad-token' });
  assert.strictEqual(r.saved, 'spam'); assert.strictEqual(rows(env, 'Spam')[0][4], 'Turnstile token did not verify (invalid-input-response)');
  assert.strictEqual(env.mails.length, 0);
});

test('normal submission with a valid token: saved, checklist PDF emailed, reply says email sent', () => {
  const env = load({ secret: 'x', siteverify });
  const r = env.post({ ...base, email: 'e@example.com', 'cf-turnstile-response': 'good-token' });
  assert.deepStrictEqual([r.result, r.saved, r.email], ['ok', 'lead', 'sent']);
  assert.strictEqual(env.attachments[0][0].name, 'HMM-SEO-Growth-OS-PDF-Overview.pdf');
  assert.strictEqual(rows(env, 'Growth OS downloads')[0][5], 'Sent');
  assert.deepStrictEqual(env.mails, ['e@example.com']);
  assert.strictEqual(rows(env, 'Growth OS downloads').length, 1); assert.strictEqual(rows(env, 'Subscribers').length, 1); assert.strictEqual(rows(env, 'Spam').length, 0);
});

test('Meta Growth OS request without a token: rejected like SEO, no email', () => {
  const env = load({ secret: 'x', siteverify });
  const r = env.post({ ...base, product: 'meta', source: '/meta-growth-os', email: 'f@example.com' });
  assert.strictEqual(r.saved, 'spam'); assert.strictEqual(rows(env, 'Spam')[0][4], 'No Turnstile token'); assert.strictEqual(env.mails.length, 0);
});

test('Meta Growth OS request with a valid token: Meta PDF emailed, joins Subscribers, reply says sent', () => {
  const env = load({ secret: 'x', siteverify });
  const r = env.post({ ...base, product: 'meta', source: '/meta-growth-os', marketingConsent: false, email: 'm@example.com', 'cf-turnstile-response': 'good-token' });
  assert.deepStrictEqual([r.result, r.saved, r.email], ['ok', 'lead', 'sent']);
  assert.strictEqual(env.attachments[0][0].name, 'HMM-Meta-Growth-OS-PDF-Overview.pdf');
  const m = env.messages[0];
  assert.strictEqual(m.subject, 'Your Meta Growth OS PDF overview');
  for (const x of [m.htmlBody, m.body]) {
    assert.ok(x.includes('Thanks for your interest in Meta Growth OS. Your PDF overview is attached.'));
    assert.ok(x.includes('/contact?entry=meta_automation#contact-form') && x.includes('Enquire about Meta ads automation'));
    assert.ok(x.includes('occasional marketing notes and updates') && x.includes('action=unsubscribe&e=m%40example.com&t='));
    assert.ok(!/SEO/.test(x), 'no SEO wording in the Meta email');
  }
  assert.strictEqual(rows(env, 'Growth OS downloads')[0][2], 'Meta Growth OS');
  assert.strictEqual(rows(env, 'Subscribers')[0][2], 'Meta Growth OS PDF overview');
});

test('/contact unchanged: no token still rejected the same way', () => {
  const env = load({ secret: 'x', siteverify });
  const r = env.post({ form: 'contact', name: 'T', email: 'g@example.com', 'help_with[]': 'x' });
  assert.strictEqual(r.saved, 'spam'); assert.strictEqual(rows(env, 'Spam')[0][4], 'No Turnstile token');
});

const failCase = (name, opts, reasonRe) => test(name, () => {
  const env = load({ secret: 'x', siteverify, ...opts });
  const r = env.post({ ...base, email: 'h@example.com', marketingConsent: true, 'cf-turnstile-response': 'good-token' });
  assert.deepStrictEqual([r.result, r.saved, r.email], ['ok', 'lead', 'failed']);
  assert.strictEqual(env.mails.length, 0);
  const row = rows(env, 'Growth OS downloads')[0];
  assert.ok(row, 'request row kept'); assert.ok(reasonRe.test(row[5]), 'status column: ' + row[5]);
  assert.strictEqual(rows(env, 'Subscribers').length, 1, 'consent still recorded');
});
failCase('checklist file ID still the placeholder: request kept, reply says email failed', { fileId: 'PASTE_CHECKLIST_PDF_FILE_ID_HERE' }, /Failed: .*file ID is not set/);
failCase('checklist file missing or not shared: request kept, reply says email failed', { fileMissing: true }, /Failed: .*No item/);
failCase('configured file is not a PDF (renamed zip): request kept, reply says email failed', { mime: 'application/zip' }, /Failed: .*not a PDF/);
failCase('file says PDF but content is not: request kept, reply says email failed', { blobType: 'application/octet-stream' }, /Failed: .*content is not a PDF/);
failCase('mail service refuses the email: request kept, reply says email failed', { mailThrows: true }, /Failed: .*too many times/);

test('guide email: approved copy, enquiry link, logo, footer with subscription line, Unsubscribe and Privacy links', () => {
  const env = load({ secret: 'x', siteverify });
  env.post({ ...base, marketingConsent: false, email: 'g@example.com', 'cf-turnstile-response': 'good-token' });
  const m = env.messages[0];
  assert.strictEqual(m.subject, 'Your SEO Growth OS PDF overview');
  for (const t of [m.htmlBody, m.body]) {
    assert.ok(t.includes('Your PDF overview is attached.') && t.includes('Your PDF overview') && t.includes('Hello,'));
    assert.ok(t.includes('page 1'));
    assert.ok(t.includes('/contact?entry=seo_automation#contact-form'));
    assert.ok(t.includes('/privacy'));
    assert.ok(t.includes('will receive occasional SEO notes and updates'));
    assert.ok(t.includes('Unsubscribe') && t.includes('action=unsubscribe&e=g%40example.com&t='));
    assert.ok(!t.includes('Help Me Marketing'));
  }
  assert.ok(m.htmlBody.includes('/assets/brand/email/hmm-logo-email.png') && m.htmlBody.includes('alt="HelpMeMarketing"'));
  assert.strictEqual((m.htmlBody.match(/<a href="[^"]*contact/g) || []).length, 1);
});

test('every SEO guide request joins Subscribers, even when the page sends no consent flag', () => {
  const env = load({ secret: 'x', siteverify });
  env.post({ ...base, marketingConsent: false, email: 'h@example.com', 'cf-turnstile-response': 'good-token' });
  const sub = rows(env, 'Subscribers');
  assert.strictEqual(sub.length, 1); assert.strictEqual(sub[0][1], 'h@example.com');
  assert.strictEqual(sub[0][3], 'Guide request (notice on the form)');
});

test('unsubscribe link: opening it only shows a confirmation page; confirming removes, logs and notifies', () => {
  const env = load({ secret: 'x', siteverify });
  env.post({ ...base, email: 'u@example.com', 'cf-turnstile-response': 'good-token' });
  const link = new URL(env.messages[0].body.match(/Unsubscribe: (\S+)/)[1]);
  const q = Object.fromEntries(link.searchParams);
  const page = env.get(q);
  assert.ok(page.html.includes('Unsubscribe?') && page.html.includes('unsubscribe-confirm'));
  assert.strictEqual(rows(env, 'Subscribers').length, 1);          // a link scanner opening the URL changes nothing
  const done = env.confirm({ action: 'unsubscribe-confirm', e: q.e, t: q.t });
  assert.ok(done.html.includes('You are unsubscribed'));
  assert.strictEqual(rows(env, 'Subscribers').length, 0);
  const un = rows(env, 'Unsubscribes');
  assert.strictEqual(un.length, 1); assert.deepStrictEqual([un[0][1], un[0][2]], ['u@example.com', 'Yes']);
  const notice = env.messages[env.messages.length - 1];
  assert.strictEqual(notice.to, 'hello@helpmemarketing.com'); assert.strictEqual(notice.subject, 'Unsubscribe: u@example.com');
});

test('unsubscribe link with a wrong token is refused and changes nothing', () => {
  const env = load({ secret: 'x', siteverify });
  env.post({ ...base, email: 'v@example.com', 'cf-turnstile-response': 'good-token' });
  const done = env.confirm({ action: 'unsubscribe-confirm', e: 'v@example.com', t: 'forged' });
  assert.ok(done.html.includes('not valid'));
  assert.strictEqual(rows(env, 'Subscribers').length, 1); assert.strictEqual(rows(env, 'Unsubscribes').length, 0);
});

test('someone who unsubscribed is not added back by a later guide request', () => {
  const env = load({ secret: 'x', siteverify });
  env.post({ ...base, email: 'w@example.com', 'cf-turnstile-response': 'good-token' });
  const q = Object.fromEntries(new URL(env.messages[0].body.match(/Unsubscribe: (\S+)/)[1]).searchParams);
  env.confirm({ action: 'unsubscribe-confirm', e: q.e, t: q.t });
  env.post({ ...base, email: 'w@example.com', 'cf-turnstile-response': 'good-token' });
  assert.strictEqual(rows(env, 'Subscribers').length, 0);
});

if (failed) { console.log(failed + ' failed'); process.exit(1); } else console.log('all passed');
