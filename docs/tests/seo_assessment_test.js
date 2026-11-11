// Decision rules of the SEO and AI visibility assessment on /ai-seo-agency (tools/seo-assessment.js).
// Usage: node docs/tests/seo_assessment_test.js   (exits 1 on any failure)
const assert = require('assert'), path = require('path');
const A = require(path.join(__dirname, '..', '..', 'tools', 'seo-assessment.js'));
let failed = 0;
function t(name, fn) { try { fn(); console.log('ok   ' + name); } catch (e) { failed++; console.log('FAIL ' + name + '\n     ' + e.message); } }
const base = { goal: 'find', traffic: 'enquiries', action: 'calls', data: ['gsc'] };
const d = o => A.decide(Object.assign({}, base, o));

t('1. no reliable figures and no usable source -> baseline', () => assert.strictEqual(d({ traffic: 'unknown', data: ['none'] }).key, 'baseline'));
t('1. only earlier AI checks is not a usable search source -> baseline', () => assert.strictEqual(d({ traffic: 'unknown', data: ['ai_checks'] }).key, 'baseline'));
t('1. baseline wins over every goal (precedence)', () => ['find', 'enquire', 'ai', 'understand', 'unsure'].forEach(g => assert.strictEqual(d({ goal: g, traffic: 'unknown', data: ['none'] }).key, 'baseline')));
t('1. no reliable figures but analytics available -> not baseline', () => assert.notStrictEqual(d({ traffic: 'unknown', data: ['analytics'] }).key, 'baseline'));
t('2. visits but few enquiries -> enquiry_path, no conflict', () => { const r = d({ traffic: 'visits' }); assert.strictEqual(r.key, 'enquiry_path'); assert.strictEqual(r.conflict, ''); });
t('2. goal enquiries with search enquiries -> enquiry_path, no conflict', () => { const r = d({ goal: 'enquire', traffic: 'enquiries' }); assert.strictEqual(r.key, 'enquiry_path'); assert.strictEqual(r.conflict, ''); });
t('2. goal enquiries but very few search visits -> enquiry_path with conflict', () => { const r = d({ goal: 'enquire', traffic: 'few' }); assert.strictEqual(r.key, 'enquiry_path'); assert.ok(/Confirm how many relevant search visits/.test(r.conflict)); });
t('2. goal enquiries, no reliable figures but records exist -> enquiry_path with conflict', () => { const r = d({ goal: 'enquire', traffic: 'unknown', data: ['records'] }); assert.strictEqual(r.key, 'enquiry_path'); assert.ok(r.conflict.length > 0); });
t('2. enquiry path wins over the AI goal when visits do not convert', () => assert.strictEqual(d({ goal: 'ai', traffic: 'visits' }).key, 'enquiry_path'));
t('3. AI goal -> ai_answers', () => assert.strictEqual(d({ goal: 'ai', traffic: 'few' }).key, 'ai_answers'));
t('4. otherwise -> service_pages', () => ['find', 'understand', 'unsure'].forEach(g => assert.strictEqual(d({ goal: g, traffic: 'few' }).key, 'service_pages')));
t('every result explains the answers that led to it', () => [{ traffic: 'unknown', data: ['none'] }, { traffic: 'visits' }, { goal: 'ai' }, {}].forEach(o => assert.ok(d(o).reasons.length >= 1)));
t('every result has all required parts and two follow-ups', () => ['baseline', 'enquiry_path', 'ai_answers', 'service_pages'].forEach(k => {
  const c = A.content(k, 'calls'); ['title', 'check', 'first', 'monitor', 'note'].forEach(f => assert.ok(c[f], k + ' ' + f));
  assert.strictEqual(c.follow.length, 2); assert.ok(c.cannot.length >= 1); }));
t('customer action wording follows question 3', () => {
  assert.ok(/real bookings/.test(A.content('baseline', 'bookings').first));
  assert.ok(/purchases/.test(A.content('enquiry_path', 'purchases').monitor));
  assert.ok(/calls and enquiries/.test(A.content('baseline', 'calls').first));
  assert.ok(/customer actions/.test(A.content('service_pages', 'other').monitor)); });
t('missing data is never read as zero traffic', () => assert.ok(/not the same as no search traffic/.test(A.content('baseline', 'calls').note)));
t('no score, metric or promise in any result text', () => ['baseline', 'enquiry_path', 'ai_answers', 'service_pages'].forEach(k => {
  const txt = JSON.stringify(A.content(k, 'other')); assert.ok(!/\d+\s*%|score|guarantee|will (rank|increase|improve)/i.test(txt), k); }));
t('no em dashes in questions or results', () => { assert.ok(!/—/.test(JSON.stringify(A.QUESTIONS))); ['baseline', 'enquiry_path', 'ai_answers', 'service_pages'].forEach(k => assert.ok(!/—/.test(JSON.stringify(A.content(k, 'calls'))))); });
t('summary carries priority and answers, no URL-encoded state', () => {
  const a = Object.assign({}, base, { traffic: 'visits' }), r = A.decide(a), s = A.summary(a, r, A.content(r.key, a.action));
  assert.ok(/Starting priority: Review the path/.test(s)); assert.ok(/Search Console information/.test(s)); });
if (failed) { console.log(failed + ' failed'); process.exit(1); } else console.log('all passed');
