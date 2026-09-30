/**
 * HMM forms → the "HMM | Contact Us" Google Sheet (one script for every form on the site).
 * Version 2026-09-29. Replaces the contact-only script that lived here, and takes over from the
 * separate Growth OS, Index and marketing audit scripts.
 *
 * Every form posts to this script's one /exec URL with a `form` label, and each lands on its tab:
 *
 *   form                 tab                   from
 *   contact              Leads                 /contact
 *   audit-help           Leads                 /tools/marketing-audit, "Get help with this"
 *   audit-plan           Audit                 /tools/marketing-audit, "Email my plan" (emails the plan)
 *   audit-feedback       Audit                 /tools/marketing-audit, "Do you know what to do next?"
 *   index-download       Index downloads       /gta-medspa-index, /hair-loss-index, /instagram-reindex
 *   growth-os-download   Growth OS downloads   /seo-growth-os (emails the bundle), /meta-growth-os
 *   subscribe            Subscribers           /blog newsletter, the audit's "Subscribe to updates"
 *   (anything that fails a check)  Spam
 *
 * Leads keeps the exact 13 columns and order of the old contact script, so nothing shifts. The
 * Source column now says "contact form" or "marketing audit".
 *
 * Nothing is thrown away. A filled honeypot, a bad email, a failed Turnstile check, too many
 * requests from one address, or an unknown payload is written to the Spam tab with the reason.
 * The page cannot read replies (it posts with no-cors), so every request gets the same "ok".
 *
 * SET-UP (keeps the same /exec URL, so /contact keeps working the whole time):
 *   1. In the "HMM | Contact Us" sheet: Extensions → Apps Script.
 *   2. Select all in Code.gs, delete, paste this whole file. Save.
 *   3. Pick `setup` in the function menu and press Run. Approve the permissions Google asks for
 *      (Sheets, sending email as you, reading the Growth OS zip in Drive, and calling Cloudflare).
 *      It creates the five new tabs with header rows and leaves Leads as it is.
 *   4. Run `testRouting`. It writes one test row to each tab (emails are skipped) and logs where
 *      each went. Check the tabs, then delete the rows marked TEST.
 *   5. Run `testEmails`. It sends the SEO Growth OS bundle and a sample audit plan to your own
 *      address. Check both arrived.
 *   6. Deploy → Manage deployments → edit the EXISTING deployment (pencil) → Version: New
 *      version → Deploy. Do not pick "New deployment": that makes a new URL.
 *   7. Tell Claude it is live. The site's other forms are then switched to this URL.
 *   8. Optional, once: run `importGrowthOsHistory` to copy past Growth OS downloads across, and
 *      `importIndexHistory` (fill in its sheet ID first) for past Index downloads.
 *
 * Turnstile stays off until you add the script property TURNSTILE_SECRET (Project Settings →
 * Script properties). Put the site key on the page first, then the secret. Checked only on the
 * two lead forms, each with its own action: contact (/contact) and audit_help (the audit). Setup order and details: see the Cloudflare notes at the bottom of this file.
 */

var SHEET_NAME = 'Leads';        // kept from the old script
var TABS = {
  Leads: ['Timestamp', 'Name', 'Email', 'Phone', 'Company / Business', 'Website',
          'What do you need help with?', 'Anything we should know?', 'Currently marketing',
          'Monthly investment', 'Desired outcome', 'Timeline', 'Source'],
  'Audit': ['Received', 'Type', 'Email', 'Priority', 'Path', 'Plan title', 'Answer', 'Plan link', 'Email sent'],
  'Index downloads': ['Received', 'Email', 'Report', 'Cycle', 'Source tag'],
  'Growth OS downloads': ['Received', 'Email', 'Product', 'Marketing consent', 'Consent timestamp', 'Bundle email', 'Referrer', 'User agent'],
  'Subscribers': ['Received', 'Email', 'Source', 'Consent'],
  'Spam': ['Received', 'Form', 'Name', 'Email', 'Reason', 'Details']
};

var SITE_URL = 'https://helpmemarketing.com';
var CONTACT_URL = SITE_URL + '/contact';
var AUDIT_URL = SITE_URL + '/tools/marketing-audit';
var FROM_NAME = 'HelpMeMarketing';
var REPLY_TO = 'hello@helpmemarketing.com';
var SENDER_POSTAL = 'Help Me Marketing, Burlington, Ontario, Canada';
var SEO_ZIP_FILE_ID = '1-ctzBnCzEve1LEpl0wpS_TTgCKOzD02X';   // the SEO Growth OS bundle in Drive
var SEO_ZIP_FILENAME = 'seo-growth-os.zip';
var RATE_LIMITS = { 'audit-plan': 5, 'growth-os-download': 3 };  // per email address, per 24 hours
var DAY_MS = 24 * 60 * 60 * 1000;
var INDEX_REPORTS = { 'gta-medspa': 'GTA MedSpa Index', 'hair-loss': 'Hair Loss Index', 'instagram': 'Real Estate Index (Instagram)' };
// Turnstile action per protected form. 'contact' is also accepted from the audit form until its page
// change (action 'audit_help') is live; it can be removed after that.
var TURNSTILE_ACTIONS = { 'contact': ['contact'], 'audit-help': ['audit_help', 'contact'] };
var TURNSTILE_HOSTS = ['helpmemarketing.com', 'www.helpmemarketing.com'];   // production only, never localhost
var DRY_RUN = false;             // true only inside testRouting: rows are written, no email is sent

/* ============================ entry points ============================ */

function doPost(e) {
  var data = {};
  try {
    data = parseIncoming_(e);
    var form = formOf_(data);

    // Checks that need the network run before the lock, so one slow call never blocks other forms.
    var reason = spamReason_(form, data);

    var lock = LockService.getScriptLock();
    lock.waitLock(20000);
    try {
      if (reason) spam_(form, data, reason);
      else route_(form, data);
    } finally {
      lock.releaseLock();
    }
  } catch (err) {
    console.error('Form handling failed: ' + err + ' | ' + JSON.stringify(data).slice(0, 500));
    try { spam_(data.form || 'unknown', data, 'Script error: ' + String(err).slice(0, 200)); } catch (ignore) {}
  }
  return jsonOut_({ result: 'ok' });
}

// Open the /exec URL in a browser to confirm the deployment is live.
function doGet() {
  return jsonOut_({ result: 'ok', message: 'HMM forms endpoint is live.' });
}

/* ============================ routing ============================ */

// Which form sent this. Pages send `form`; the fallbacks cover pages still cached with the old payloads.
function formOf_(d) {
  if (d.form) return String(d.form);
  if (d.action === 'plan') return 'audit-plan';
  if (d.action === 'feedback') return 'audit-feedback';
  if (d.action === 'subscribe') return 'subscribe';
  var src = String(d.source || '');
  if (/^(gta-medspa|hair-loss|instagram)/.test(src)) return 'index-download';
  if (/growth-os/.test(src)) return 'growth-os-download';
  var help = joinMulti_(d['help_with[]'] || d.help_with);
  if (help.indexOf('[From the marketing audit]') === 0) return 'audit-help';
  if (d.name || help) return 'contact';
  return 'unknown';
}

// Returns why a submission is spam, or '' when it may go to its tab.
function spamReason_(form, d) {
  if (d.company_url_secondary && String(d.company_url_secondary).trim() !== '') return 'Honeypot filled';
  if (form === 'unknown') return 'Unknown form';
  if (form === 'audit-feedback') return '';                       // no email address in it
  if (!isEmail_(pick_(d, 'email'))) return 'Invalid email';
  if (TURNSTILE_ACTIONS[form]) return turnstileReason_(form, d);
  return '';
}

function route_(form, d) {
  var email = pick_(d, 'email').toLowerCase();
  if (RATE_LIMITS[form]) {
    var tab = form === 'audit-plan' ? 'Audit' : 'Growth OS downloads';
    var col = form === 'audit-plan' ? 3 : 2;
    if (countRecent_(tab, col, email) >= RATE_LIMITS[form]) return spam_(form, d, 'Too many requests from this email today');
  }
  switch (form) {
    case 'contact':
    case 'audit-help': return addLead_(form, d);
    case 'audit-plan': return addPlan_(d, email);
    case 'audit-feedback': return addFeedback_(d);
    case 'index-download': return addIndex_(d, email);
    case 'growth-os-download': return addGrowthOs_(d, email);
    case 'subscribe': return addSubscriber_(email, pick_(d, 'source') || 'website', 'Yes, subscribe form');
  }
  spam_(form, d, 'Unknown form');
}

/* ============================ one handler per tab ============================ */

function addLead_(form, d) {
  var help = joinMulti_(d['help_with[]'] || d.help_with).replace(/^\[From the marketing audit\]\s*/, '');
  tab_('Leads').appendRow([
    new Date(),
    pick_(d, 'name'),
    pick_(d, 'email'),
    pick_(d, 'phone'),
    pick_(d, 'company'),
    pick_(d, 'website'),
    help,
    pick_(d, 'biggest_challenge'),
    joinMulti_(d['current_marketing[]'] || d.current_marketing),
    pick_(d, 'monthly_investment'),
    pick_(d, 'desired_outcome'),
    pick_(d, 'timeline'),
    form === 'audit-help' ? 'marketing audit' : 'contact form'
  ]);
}

function addPlan_(d, email) {
  var text = pick_(d, 'plan_text').slice(0, 12000);
  var url = pick_(d, 'plan_url').slice(0, 600);
  var title = pick_(d, 'plan_title').slice(0, 120) || 'Your marketing plan';
  if (!text || url.indexOf(AUDIT_URL + '#plan=') !== 0) return spam_('audit-plan', d, 'Plan text or link missing');
  var sent = send_(function () {
    MailApp.sendEmail({ to: email, replyTo: REPLY_TO, name: FROM_NAME, subject: 'Your marketing plan: ' + title,
      body: text + '\n\n' + planFooter_(), htmlBody: planHtml_(text, url) });
  });
  tab_('Audit').appendRow([new Date(), 'Plan emailed', email, pick_(d, 'priority'), pick_(d, 'path'), title, '', url, sent]);
}

function addFeedback_(d) {
  var answer = pick_(d, 'answer');
  if (['Yes', 'Partly', 'No'].indexOf(answer) === -1) return spam_('audit-feedback', d, 'Unexpected feedback answer');
  tab_('Audit').appendRow([new Date(), 'Feedback', '', pick_(d, 'priority'), pick_(d, 'path'), '', answer, '', '']);
}

function addIndex_(d, email) {
  var src = pick_(d, 'source');
  var key = Object.keys(INDEX_REPORTS).filter(function (k) { return src.indexOf(k) === 0; })[0];
  var cycle = (src.match(/cycle-(\d+)/) || [])[1] || '';
  tab_('Index downloads').appendRow([new Date(), email, key ? INDEX_REPORTS[key] : src, cycle, src]);
}

function addGrowthOs_(d, email) {
  var src = pick_(d, 'source');
  var product = (pick_(d, 'product') === 'meta' || /meta/.test(src)) ? 'Meta Growth OS' : 'SEO Growth OS';
  var consent = d.marketingConsent === true || d.marketingConsent === 'true';
  // The SEO bundle is emailed as an attachment; the Meta bundle downloads on the page, so it gets no email.
  var sent = product === 'SEO Growth OS' ? send_(function () { sendSeoBundle_(email); }) : 'Not needed (downloads on the page)';
  tab_('Growth OS downloads').appendRow([new Date(), email, product, consent ? 'TRUE' : 'FALSE', consent ? new Date() : '',
    sent, pick_(d, 'referrer').slice(0, 300), pick_(d, 'userAgent').slice(0, 300)]);
  if (consent) addSubscriber_(email, product + ' download', 'Yes, ticked the box');
}

// One row per address: a repeat sign-up is ignored, not duplicated.
function addSubscriber_(email, source, consent) {
  var sh = tab_('Subscribers');
  var last = sh.getLastRow();
  if (last > 1) {
    var emails = sh.getRange(2, 2, last - 1, 1).getValues();
    for (var i = 0; i < emails.length; i++) if (String(emails[i][0]).toLowerCase() === email) return;
  }
  sh.appendRow([new Date(), email, source, consent]);
}

function spam_(form, d, reason) {
  var copy = {};
  Object.keys(d || {}).forEach(function (k) { if (k !== 'cf-turnstile-response' && k !== 'plan_text') copy[k] = d[k]; });
  tab_('Spam').appendRow([new Date(), form, pick_(d, 'name'), pick_(d, 'email'), reason, JSON.stringify(copy).slice(0, 2000)]);
}

/* ============================ Turnstile ============================ */

// Cloudflare's standard server check: a present token of sane length, a 200 reply from siteverify,
// success true, the form's own action and one of our hostnames. Anything else goes to Spam with the
// reason and Cloudflare's error codes (for example timeout-or-duplicate for a reused token).
function turnstileReason_(form, d) {
  var secret = PropertiesService.getScriptProperties().getProperty('TURNSTILE_SECRET');
  if (!secret) return '';                                   // not switched on yet
  var token = d['cf-turnstile-response'];
  if (typeof token !== 'string' || token.length === 0) return 'No Turnstile token';
  if (token.length > 2048) return 'Turnstile token too long';
  var r;
  try {
    var res = UrlFetchApp.fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method: 'post', payload: { secret: secret, response: token }, muteHttpExceptions: true });
    if (res.getResponseCode() !== 200) return 'Cloudflare replied ' + res.getResponseCode();
    r = JSON.parse(res.getContentText());
  } catch (err) {
    return 'Cloudflare unreachable';                        // filed on Spam, not lost
  }
  if (r.success !== true) return 'Turnstile token did not verify (' + (r['error-codes'] || []).join(', ') + ')';
  if (TURNSTILE_ACTIONS[form].indexOf(r.action) === -1) return 'Turnstile action mismatch (' + r.action + ')';
  if (TURNSTILE_HOSTS.indexOf(r.hostname) === -1) return 'Turnstile hostname mismatch (' + r.hostname + ')';
  return '';
}

/* ============================ email ============================ */

// Runs a send and reports what happened, so a failed email never loses the row.
function send_(fn) {
  if (DRY_RUN) return 'Skipped (test)';
  try { fn(); return 'Sent'; } catch (err) { console.error(err); return 'Failed: ' + String(err).slice(0, 120); }
}

function planFooter_() {
  return 'You asked for this plan on helpmemarketing.com. This email does not sign you up for anything.\n' +
    'Want help with it? Reply to this email and Ankit will get back to you within 1 to 2 business days.';
}

// The page's plan text uses UPPER CASE lines as headings; this turns them into bold headings.
function planHtml_(text, url) {
  var html = '';
  text.split('\n').forEach(function (l) {
    if (!l.trim()) { html += '<div style="height:10px"></div>'; return; }
    var heading = /^[A-Z0-9 ,.'=:\-]+$/.test(l) && /[A-Z]{3}/.test(l);
    html += heading
      ? '<p style="margin:14px 0 4px;font:600 13px/1.4 Arial,sans-serif;letter-spacing:.08em;color:#FF5C1A">' + esc_(l.replace(/=+/g, '').trim()) + '</p>'
      : '<p style="margin:0 0 4px;font:15px/1.55 Arial,sans-serif;color:#1A1A1A">' + esc_(l) + '</p>';
  });
  return '<div style="max-width:620px;margin:0 auto;padding:24px">' +
    '<p style="margin:0 0 16px"><a href="' + esc_(url) + '" style="display:inline-block;padding:10px 18px;background:#FF5C1A;color:#0E0E0E;border-radius:8px;font:600 14px Arial,sans-serif;text-decoration:none">Open your plan</a></p>' +
    html + '<p style="margin:24px 0 0;font:13px/1.5 Arial,sans-serif;color:#666">' + esc_(planFooter_()).replace(/\n/g, '<br>') + '</p></div>';
}

function sendSeoBundle_(email) {
  var blob = DriveApp.getFileById(SEO_ZIP_FILE_ID).getBlob().setName(SEO_ZIP_FILENAME);
  MailApp.sendEmail({ to: email, name: FROM_NAME, replyTo: REPLY_TO, subject: 'Your SEO Growth OS download',
    htmlBody: seoBundleHtml_(), body: seoBundleText_(), attachments: [blob] });
}

// Same email as the old Growth OS script, word for word.
function seoBundleHtml_() {
  var font = 'Arial,Helvetica,sans-serif', bg = '#0E0E0E', card = '#1A1A1A', text = '#FFFFFF', muted = '#999999',
    cta = '#FF5C1A', mint = '#00D4AA', border = 'rgba(255,255,255,0.10)';
  return (
'<!DOCTYPE html>' +
'<html lang="en"><head><meta charset="UTF-8">' +
'<meta name="viewport" content="width=device-width,initial-scale=1"></head>' +
'<body style="margin:0;padding:0;background:' + bg + ';">' +
'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:' + bg + ';padding:32px 16px;">' +
'<tr><td align="center">' +
'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:' + card + ';border:1px solid ' + border + ';border-radius:14px;padding:32px;">' +
'<tr><td style="font-family:' + font + ';font-size:11px;letter-spacing:2px;text-transform:uppercase;color:' + mint + ';font-weight:bold;padding-bottom:12px;">' +
'HMM &middot; Search Growth, Engineered</td></tr>' +
'<tr><td style="font-family:' + font + ';font-size:26px;line-height:1.25;color:' + text + ';font-weight:bold;padding-bottom:16px;">' +
'Your SEO Growth OS is attached.</td></tr>' +
'<tr><td style="font-family:' + font + ';font-size:15px;line-height:1.6;color:' + muted + ';padding-bottom:20px;">' +
'The bundle is the zip on this email: 32 skills, a README, and a SETUP file. ' +
'Unzip it, open SETUP.md, and it will walk you through installing the skills and running the first audit. ' +
'It runs on your own machine. Nothing is sent to us.</td></tr>' +
'<tr><td style="font-family:' + font + ';font-size:15px;line-height:1.6;color:' + muted + ';padding-bottom:24px;">' +
'Start with the six-node command in the README. Point it at your own site, and it will produce a health score, ' +
'a root-cause gap inventory, and a ranked roadmap before it touches anything.</td></tr>' +
'<tr><td style="padding-bottom:26px;">' +
'<a href="' + CONTACT_URL + '" style="display:inline-block;font-family:' + font + ';font-size:15px;font-weight:bold;color:#ffffff;background:' + cta + ';border-radius:8px;padding:14px 24px;text-decoration:none;">' +
'Need help with setup? Book a call</a></td></tr>' +
'<tr><td style="border-top:1px solid ' + border + ';padding-top:18px;font-family:' + font + ';font-size:12px;line-height:1.6;color:#8A8A8A;">' +
'You are getting this because you asked for the SEO Growth OS download at ' + SITE_URL + '/seo-growth-os.<br>' +
SENDER_POSTAL + '<br>' +
'Prefer not to hear from us again? Reply with "unsubscribe" and you are off the list.' +
'</td></tr>' +
'</table></td></tr></table></body></html>'
  );
}

function seoBundleText_() {
  return [
    'Your SEO Growth OS is attached.', '',
    'The bundle is the zip on this email: 32 skills, a README, and a SETUP file.',
    'Unzip it, open SETUP.md, and it will walk you through installing the skills',
    'and running the first audit. It runs on your own machine. Nothing is sent to us.', '',
    'Start with the six-node command in the README. Point it at your own site, and',
    'it will produce a health score, a root-cause gap inventory, and a ranked',
    'roadmap before it touches anything.', '',
    'Need help with setup? Book a call: ' + CONTACT_URL, '', '---',
    'You are getting this because you asked for the SEO Growth OS download at',
    SITE_URL + '/seo-growth-os.', SENDER_POSTAL,
    'Prefer not to hear from us again? Reply with "unsubscribe" and you are off the list.'
  ].join('\n');
}

/* ============================ helpers ============================ */

// Parses every body format Apps Script can receive: FormData or urlencoded (e.parameters),
// a JSON body, or urlencoded raw text. Kept from the old contact script.
function parseIncoming_(e) {
  var out = {};
  if (e && e.parameters) {
    Object.keys(e.parameters).forEach(function (k) {
      var v = e.parameters[k];
      out[k] = (v && v.length > 1) ? v : (v ? v[0] : '');
    });
  }
  if (e && e.postData && e.postData.contents) {
    var raw = e.postData.contents;
    try {
      var j = JSON.parse(raw);
      if (j && typeof j === 'object') {
        Object.keys(j).forEach(function (k) { out[k] = j[k]; });
        return out;
      }
    } catch (ignore) {}
    if (Object.keys(out).length === 0 && raw.indexOf('=') !== -1) {
      raw.split('&').forEach(function (pair) {
        var kv = pair.split('=');
        if (kv.length >= 1 && kv[0]) {
          var key = decodeURIComponent(kv[0].replace(/\+/g, ' '));
          var val = decodeURIComponent((kv[1] || '').replace(/\+/g, ' '));
          if (out[key] === undefined) out[key] = val;
          else if (Array.isArray(out[key])) out[key].push(val);
          else out[key] = [out[key], val];
        }
      });
    }
  }
  return out;
}

// Returns the tab, creating it with a bold, frozen header row the first time.
function tab_(name) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(name);
  if (!sh) sh = ss.insertSheet(name);
  if (sh.getLastRow() === 0) {
    sh.appendRow(TABS[name]);
    sh.getRange(1, 1, 1, TABS[name].length).setFontWeight('bold');
    sh.setFrozenRows(1);
  }
  return sh;
}

// Rows in the last 24 hours on `name` whose column `col` (1-based) holds this email.
function countRecent_(name, col, email) {
  var sh = tab_(name), last = sh.getLastRow();
  if (last < 2) return 0;
  var rows = sh.getRange(2, 1, last - 1, col).getValues(), since = Date.now() - DAY_MS, n = 0;
  for (var i = rows.length - 1; i >= 0; i--) {
    var t = rows[i][0] instanceof Date ? rows[i][0].getTime() : 0;
    if (t < since) break;                                   // rows are added in time order
    if (String(rows[i][col - 1]).toLowerCase() === email) n++;
  }
  return n;
}

function pick_(data, key) {
  var v = data[key];
  if (v === undefined || v === null) return '';
  return Array.isArray(v) ? v.join(', ') : String(v).trim();
}

function joinMulti_(v) {
  if (v === undefined || v === null) return '';
  return Array.isArray(v) ? v.join(', ') : String(v);
}

function isEmail_(v) { return v.length <= 254 && /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v); }

function esc_(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }

function jsonOut_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

/* ============================ run these from the editor ============================ */

// Step 3. Creates the tabs and asks for every permission the script needs, in one go.
function setup() {
  Object.keys(TABS).forEach(function (name) { tab_(name); });
  MailApp.getRemainingDailyQuota();
  DriveApp.getFileById(SEO_ZIP_FILE_ID).getName();
  checkTurnstileSecret();
  Logger.log('Ready. Tabs: ' + Object.keys(TABS).join(', '));
}

// Run any time: tells you whether TURNSTILE_SECRET is set and whether Cloudflare accepts it. A dummy
// token must fail as invalid-input-response (secret good), not invalid-input-secret (secret wrong).
function checkTurnstileSecret() {
  var secret = PropertiesService.getScriptProperties().getProperty('TURNSTILE_SECRET');
  if (!secret) return Logger.log('TURNSTILE_SECRET is not set, so Turnstile checking is off.');
  var r = JSON.parse(UrlFetchApp.fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
    method: 'post', payload: { secret: secret, response: 'XXXX.DUMMY.TOKEN.XXXX' }, muteHttpExceptions: true }).getContentText());
  var codes = r['error-codes'] || [];
  Logger.log(codes.indexOf('invalid-input-secret') > -1 ? 'TURNSTILE_SECRET is WRONG: Cloudflare rejected it. Re-copy the secret key from the widget.'
    : codes.indexOf('invalid-input-response') > -1 ? 'TURNSTILE_SECRET is valid.' : 'Unexpected reply from Cloudflare: ' + JSON.stringify(codes));
}

// Step 4. One test row per tab, the way each page sends it. Emails are skipped.
function testRouting() {
  DRY_RUN = true;
  var me = 'test@example.com';
  var cases = [
    { parameters: { form: ['contact'], name: ['TEST contact'], email: [me], phone: [''], website: ['https://example.com'], 'help_with[]': ['TEST need'], biggest_challenge: [''] } },
    { parameters: { form: ['audit-help'], name: ['TEST audit lead'], email: [me], phone: [''], website: ['Not given'], 'help_with[]': ['TEST summary'], biggest_challenge: [''] } },
    { json: { form: 'audit-plan', email: me, plan_title: 'TEST plan', plan_text: 'YOUR MARKETING PLAN\nTEST', plan_url: AUDIT_URL + '#plan=test', path: 'online', priority: 'P_TEST' } },
    { json: { form: 'audit-feedback', answer: 'Yes', path: 'online', priority: 'P_TEST' } },
    { parameters: { form: ['index-download'], email: [me], source: ['gta-medspa-cycle-001'] } },
    { json: { form: 'growth-os-download', product: 'seo', email: me, marketingConsent: false, source: '/seo-growth-os' } },
    { json: { form: 'subscribe', email: me, source: 'blog' } },
    { parameters: { form: ['contact'], name: ['TEST bot'], email: [me], company_url_secondary: ['http://spam.example'] } }
  ];
  cases.forEach(function (c) {
    var e = c.json ? { parameters: {}, postData: { contents: JSON.stringify(c.json) } } : { parameters: c.parameters };
    doPost(e);
  });
  Logger.log('Wrote ' + cases.length + ' TEST rows: Leads 2, Audit 2, Index downloads 1, Growth OS downloads 1, Subscribers 1, Spam 1. Delete them when checked.');
}

// Step 5. Sends the SEO bundle and a sample plan to your own address.
function testEmails() {
  var me = Session.getActiveUser().getEmail();
  sendSeoBundle_(me);
  MailApp.sendEmail({ to: me, replyTo: REPLY_TO, name: FROM_NAME, subject: 'Your marketing plan: Cut missed appointments (test)',
    body: 'YOUR MARKETING PLAN\nTest', htmlBody: planHtml_('YOUR MARKETING PLAN\nFrom the HelpMeMarketing marketing audit\n\nYOUR FIRST PRIORITY\nCut missed appointments\n\nYOUR FIRST ACTION\n1. Send a confirmation right after every booking.', AUDIT_URL + '#plan=buy.appointment~goal.convert~stage.active~a_fit.most~a_wait.week~a_how.online~a_finish.most~a_remind.none~a_noshow.some~who.self') });
  Logger.log('Sent the SEO bundle and a sample plan to ' + me);
}

// Step 8, optional and once. Copies past rows from the old Growth OS sheet; opt-ins also go to Subscribers.
function importGrowthOsHistory() {
  var props = PropertiesService.getScriptProperties();
  if (props.getProperty('imported_growth_os')) return Logger.log('Already imported once. Nothing done.');
  var src = SpreadsheetApp.openById('1cGinedEOETdJ_FFB1TPL9lRKccT-KGxrEQAD8hoNmuk').getSheetByName('growth_os_downloads');
  var rows = src.getDataRange().getValues().slice(1), sh = tab_('Growth OS downloads');
  rows.forEach(function (r) {   // old columns: Timestamp, Email, Consent, Consent time, Source, Referrer, User agent
    var product = /meta/.test(String(r[4])) ? 'Meta Growth OS' : 'SEO Growth OS';
    sh.appendRow([r[0], r[1], product, r[2], r[3], 'Imported', r[5], r[6]]);
    if (String(r[2]).toUpperCase() === 'TRUE') addSubscriber_(String(r[1]).toLowerCase(), product + ' download (imported)', 'Yes, ticked the box');
  });
  props.setProperty('imported_growth_os', new Date().toISOString());
  Logger.log('Imported ' + rows.length + ' Growth OS rows.');
}

// Step 8, optional and once. Fill in the old Index sheet's ID and tab (open the old Index Apps
// Script and look for its sheet). Columns are found by their headers: a date, an email and a source.
function importIndexHistory() {
  var OLD_SHEET_ID = 'PASTE_THE_OLD_INDEX_SHEET_ID';
  var OLD_TAB = 'PASTE_THE_TAB_NAME';
  if (OLD_SHEET_ID.indexOf('PASTE_') === 0) return Logger.log('Fill in OLD_SHEET_ID and OLD_TAB first.');
  var props = PropertiesService.getScriptProperties();
  if (props.getProperty('imported_index')) return Logger.log('Already imported once. Nothing done.');
  var all = SpreadsheetApp.openById(OLD_SHEET_ID).getSheetByName(OLD_TAB).getDataRange().getValues();
  var head = all[0].map(function (h) { return String(h).toLowerCase(); });
  var find = function (re) { for (var i = 0; i < head.length; i++) if (re.test(head[i])) return i; return -1; };
  var ti = find(/time|date/), ei = find(/mail/), si = find(/source/);
  if (ei < 0) return Logger.log('No email column found in ' + OLD_TAB + '.');
  var sh = tab_('Index downloads');
  all.slice(1).forEach(function (r) {
    var src = si > -1 ? String(r[si]) : '';
    var key = Object.keys(INDEX_REPORTS).filter(function (k) { return src.indexOf(k) === 0; })[0];
    sh.appendRow([ti > -1 ? r[ti] : '', String(r[ei]).toLowerCase(), key ? INDEX_REPORTS[key] : src, (src.match(/cycle-(\d+)/) || [])[1] || '', src || 'Imported']);
  });
  props.setProperty('imported_index', new Date().toISOString());
  Logger.log('Imported ' + (all.length - 1) + ' Index rows.');
}

/* ============================ Cloudflare Turnstile notes ============================
 * 1. Cloudflare → Turnstile → Add widget. Hostname helpmemarketing.com, mode Managed,
 *    pre-clearance No. Copy the site key and the secret key.
 * 2. Site key first: it goes in data-turnstile-sitekey on BOTH lead forms (contact.html and
 *    #ma-cform in tools/marketing-audit.html). It is public; share it with Claude.
 * 3. Then the secret: Project Settings → Script properties → TURNSTILE_SECRET. Never in the page,
 *    the repo or a chat. From then on, lead submissions without a valid token go to Spam.
 * If the secret goes in before the site key is live, every lead lands on Spam until it is.
 */
