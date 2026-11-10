// Runs the real forms script (docs/HMM_Forms_AppsScript.gs) in Node with stand-ins for the Apps Script services,
// and checks the SEO Growth OS download bot checks (d2, 2026-11-10).
// Usage: node docs/tests/forms_growth_os_test.js   (exits 1 on any failure)
const fs = require('fs'), path = require('path'), vm = require('vm'), assert = require('assert');

function load(opts) {
  const sheets = {}, mails = [], fetches = [];
  const sheet = name => sheets[name] || (sheets[name] = {
    rows: [],
    getLastRow() { return this.rows.length; },
    appendRow(r) { this.rows.push(r); },
    getRange(r, c, nr, nc) { const rows = this.rows; return {
      setFontWeight() {}, getValues() { return rows.slice(r - 1, r - 1 + nr).map(x => x.slice(c - 1, c - 1 + nc)); } }; },
    setFrozenRows() {}
  });
  const ctx = {
    console, JSON, Date, Math, String, Object, Array,
    PropertiesService: { getScriptProperties: () => ({ getProperty: k => (k === 'TURNSTILE_SECRET' ? opts.secret : null) }) },
    UrlFetchApp: { fetch: (url, o) => { fetches.push(url); const r = opts.siteverify(o.payload.response);
      return { getResponseCode: () => 200, getContentText: () => JSON.stringify(r) }; } },
    SpreadsheetApp: { getActiveSpreadsheet: () => ({ getSheetByName: n => sheets[n] || null, insertSheet: n => sheet(n) }) },
    LockService: { getScriptLock: () => ({ waitLock() {}, releaseLock() {} }) },
    ContentService: { MimeType: { JSON: 'json' }, createTextOutput: t => ({ text: t, setMimeType() { return this; } }) },
    MailApp: { sendEmail: m => mails.push(m.to), getRemainingDailyQuota: () => 100 },
    DriveApp: { getFileById: () => ({ getBlob: () => ({ setName() { return this; } }) }) },
    Logger: { log() {} }, CacheService: { getScriptCache: () => ({ get() { return null; }, put() {}, remove() {} }) },
    Utilities: {}, Session: { getActiveUser: () => ({ getEmail: () => '' }) }
  };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(__dirname, '..', 'HMM_Forms_AppsScript.gs'), 'utf8'), ctx);
  const post = body => JSON.parse(ctx.doPost({ postData: { contents: JSON.stringify(body) } }).text);
  return { post, sheets, mails, fetches };
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

test('normal submission with a valid token: saved, bundle emailed, download and Subscribers rows written', () => {
  const env = load({ secret: 'x', siteverify });
  const r = env.post({ ...base, email: 'e@example.com', 'cf-turnstile-response': 'good-token' });
  assert.deepStrictEqual([r.result, r.saved], ['ok', 'lead']);
  assert.deepStrictEqual(env.mails, ['e@example.com']);
  assert.strictEqual(rows(env, 'Growth OS downloads').length, 1); assert.strictEqual(rows(env, 'Subscribers').length, 1); assert.strictEqual(rows(env, 'Spam').length, 0);
});

test('Meta Growth OS download (no widget on that page): still saved without a token, no email', () => {
  const env = load({ secret: 'x', siteverify });
  const r = env.post({ ...base, product: 'meta', source: '/meta-growth-os', email: 'f@example.com' });
  assert.strictEqual(r.saved, 'lead'); assert.strictEqual(env.mails.length, 0); assert.strictEqual(env.fetches.length, 0);
});

test('/contact unchanged: no token still rejected the same way', () => {
  const env = load({ secret: 'x', siteverify });
  const r = env.post({ form: 'contact', name: 'T', email: 'g@example.com', 'help_with[]': 'x' });
  assert.strictEqual(r.saved, 'spam'); assert.strictEqual(rows(env, 'Spam')[0][4], 'No Turnstile token');
});

if (failed) { console.log(failed + ' failed'); process.exit(1); } else console.log('all passed');
