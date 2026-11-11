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
 *   index-download       Index downloads       /gta-medspa-index, /hair-loss-index, /realestate-index (emails the CSV since 2026-11-03)
 *   growth-os-download   Growth OS downloads   /seo-growth-os (emails the visual guide PDF), /meta-growth-os
 *   subscribe            Subscribers           /blog newsletter, the audit's "Subscribe to updates"
 *   research-code        Research unlocks      /business-spend-index, /realestate-index, "Read the full case study" (emails a 6-digit code)
 *   research-verify      Research unlocks      the same form, second step (checks the code; marks the row Verified)
 *   (anything that fails a check)  Spam
 *
 * Leads keeps the exact 13 columns and order of the old contact script, so nothing shifts. The
 * Source column now says "contact form" or "marketing audit".
 *
 * Nothing is thrown away. A filled honeypot, a bad email, a failed Turnstile check, too many
 * requests from one address, or an unknown payload is written to the Spam tab with the reason.
 * Since 2026-10-11 every reply says what happened: { result: 'ok', saved: 'lead' }, { result: 'ok',
 * saved: 'spam', reason } or { result: 'error' }. /contact reads it and shows its thank-you only for a
 * saved lead. Accepted free review requests get an automatic confirmation email.
 *
 * SET-UP (keeps the same /exec URL, so /contact keeps working the whole time):
 *   1. In the "HMM | Contact Us" sheet: Extensions → Apps Script.
 *   2. Select all in Code.gs, delete, paste this whole file. Save.
 *   3. Pick `setup` in the function menu and press Run. Approve the permissions Google asks for
 *      (Sheets, sending email as you, reading the Growth OS zip in Drive, and calling Cloudflare).
 *      It creates the five new tabs with header rows and leaves Leads as it is.
 *   4. Run `testRouting`. It writes one test row to each tab (emails are skipped) and logs where
 *      each went. Check the tabs, then delete the rows marked TEST.
 *   5. Run `testEmails`. It sends the SEO Growth OS Visual Guide twice (not opted in, then opted in, so
 *      you can check both footers) and a sample audit plan to your own address. Check all three arrived.
 *   6. Deploy → Manage deployments → edit the EXISTING deployment (pencil) → Version: New
 *      version → Deploy. Do not pick "New deployment": that makes a new URL.
 *   7. Tell Claude it is live. The site's other forms are then switched to this URL.
 *   8. Optional, once: run `importGrowthOsHistory` to copy past Growth OS downloads across, and
 *      `importIndexHistory` (fill in its sheet ID first) for past Index downloads.
 *
 * Research unlocks (added 2026-11-02): after pasting this version, run `setup` once (it creates the Research unlocks
 * tab and asks for the script cache permission), then `testResearchUnlock` and `testResearchVerify`, then redeploy
 * the existing deployment as in step 6. Do this BEFORE the gated /business-spend-index goes live: until then the
 * old script files research-code requests as "Unknown form" and no visitor can unlock the page.
 * CSV by email (added 2026-11-03): /realestate-index sends form=index-download and this script emails the CSV published at
 * /assets/index/real-estate/data/realestate-index-postlog.csv (fetched at send time). Run `testIndexCsv` once after pasting
 * (it asks for permission to fetch the file), then redeploy the existing deployment before the page change goes live.
 * The same applies to /realestate-index (gate added 2026-11-03): paste this version and redeploy before it goes live,
 * or its code requests come back "Unknown research".
 *
 * Turnstile stays off until you add the script property TURNSTILE_SECRET (Project Settings →
 * Script properties). Put the site key on the page first, then the secret. Checked on the two lead
 * forms and the research code request, each with its own action: contact (/contact), audit_help (the audit)
 * and research_unlock (the case study's "Send my code"). Setup order and details: see the Cloudflare notes at the bottom of this file.
 */

var SHEET_NAME = 'Leads';        // kept from the old script
var TABS = {
  Leads: ['Timestamp', 'Name', 'Email', 'Phone', 'Company / Business', 'Website',
          'What do you need help with?', 'Anything we should know?', 'Currently marketing',
          'Monthly investment', 'Desired outcome', 'Timeline', 'Source'],
  'Audit': ['Received', 'Type', 'Email', 'Priority', 'Path', 'Plan title', 'Answer', 'Plan link', 'Email sent'],
  'Index downloads': ['Received', 'Email', 'Report', 'Cycle', 'Source tag', 'CSV email'],
  'Growth OS downloads': ['Received', 'Email', 'Product', 'Marketing consent', 'Consent timestamp', 'Bundle email', 'Referrer', 'User agent'],
  'Subscribers': ['Received', 'Email', 'Source', 'Consent'],
  'Research unlocks': ['Last code sent', 'Email', 'Research', 'Status', 'Verified at', 'Codes sent', 'Source'],
  'Spam': ['Received', 'Form', 'Name', 'Email', 'Reason', 'Details']
};

var SITE_URL = 'https://helpmemarketing.com';
var CONTACT_URL = SITE_URL + '/contact';
var AUDIT_URL = SITE_URL + '/tools/marketing-audit';
var FROM_NAME = 'HelpMeMarketing';
var REPLY_TO = 'hello@helpmemarketing.com';
var SENDER_POSTAL = 'Help Me Marketing, Halton Hills, Ontario, Canada';
// The SEO Growth OS visual guide PDF in Drive (2026-11-11: replaces the bundle zip, which is no longer sent publicly).
// Upload docs/growth-os-checklist/HMM-SEO-Growth-OS-Visual-Guide.pdf to Drive and paste its file ID here before deploying.
var SEO_CHECKLIST_FILE_ID = '1itZqQlmPA9YcpAsuvaEwT21FefoyZxLB';   // HMM-SEO-Growth-OS-Visual-Guide.pdf, uploaded 2026-11-11 (approved build 2a9ba42)
var SEO_CHECKLIST_FILENAME = 'HMM-SEO-Growth-OS-Visual-Guide.pdf';
var RATE_LIMITS = { 'audit-plan': 5, 'growth-os-download': 3, 'index-download': 3 };  // per email address, per 24 hours
var DAY_MS = 24 * 60 * 60 * 1000;
var INDEX_REPORTS = { 'gta-medspa': 'GTA MedSpa Index', 'hair-loss': 'Hair Loss Index', 'instagram': 'Real Estate Index (Instagram)', 'realestate-index': 'Real Estate Index' };
// Index CSVs sent by email instead of downloading on the page (added 2026-11-03). The file is the published copy on the site.
var INDEX_CSV = { 'realestate-index': { url: SITE_URL + '/assets/index/real-estate/data/realestate-index-postlog.csv',
  name: 'realestate-index-postlog.csv', title: 'How Canadian Real Estate Investment Firms Market to Investors', path: '/realestate-index' } };
// Turnstile action per protected form. 'contact' is also accepted from the audit form until its page
// change (action 'audit_help') is live; it can be removed after that.
var TURNSTILE_ACTIONS = { 'contact': ['contact'], 'audit-help': ['audit_help', 'contact'], 'research-code': ['research_unlock'],
  'growth-os-download': ['growth_os_download'] };   // SEO checklist only (was the bundle until 2026-11-11; d2, 2026-11-10); see spamReason_
var TURNSTILE_HOSTS = ['helpmemarketing.com', 'www.helpmemarketing.com'];   // production only, never localhost
var DRY_RUN = false;             // true only inside testRouting: rows are written, no email is sent

/* ============================ entry points ============================ */

// Replies with what happened so the page only says "sent" when the row is saved:
// { result: 'ok', saved: 'lead' } for a filed form, { result: 'ok', saved: 'spam', reason } when it went to the Spam tab,
// { result: 'error' } when nothing could be written (the page then keeps the visitor's text and offers email).
function doPost(e) {
  var data = {}, saved = 'error', why = '', emailStatus = '';
  try {
    data = parseIncoming_(e);
    var form = formOf_(data);

    // Checks that need the network run before the lock, so one slow call never blocks other forms.
    var reason = spamReason_(form, data);

    // Research unlocks (2026-11-02) reply with their own shape: the page needs to know whether a code went out
    // and whether the code matched, not only whether a row was saved.
    if (form === 'research-code' || form === 'research-verify') {
      var rlock = LockService.getScriptLock();
      rlock.waitLock(20000);
      try {
        if (reason) { spam_(form, data, reason); return jsonOut_({ result: 'ok', saved: 'spam', reason: String(reason).slice(0, 80) }); }
        return jsonOut_(form === 'research-code' ? researchCode_(data) : researchVerify_(data));
      } finally {
        rlock.releaseLock();
      }
    }

    var lock = LockService.getScriptLock();
    lock.waitLock(20000);
    try {
      if (reason) { spam_(form, data, reason); saved = 'spam'; why = reason; }
      else {
        var filed = route_(form, data);
        saved = filed === 'spam' ? 'spam' : 'lead';
        // Checklist requests (2026-11-11) also report whether the email went out, so the page only says
        // "check your inbox" when the mail service accepted it.
        if (filed === 'lead_email_sent' || filed === 'lead_email_failed') emailStatus = filed === 'lead_email_sent' ? 'sent' : 'failed';
      }
    } finally {
      lock.releaseLock();
    }
  } catch (err) {
    console.error('Form handling failed: ' + err + ' | ' + JSON.stringify(data).slice(0, 500));
    try { spam_(data.form || 'unknown', data, 'Script error: ' + String(err).slice(0, 200)); saved = 'spam'; why = 'Script error'; } catch (ignore) { saved = 'error'; }
  }
  if (saved === 'error') return jsonOut_({ result: 'error' });
  if (saved === 'spam') return jsonOut_({ result: 'ok', saved: 'spam', reason: String(why).slice(0, 80) });
  return jsonOut_(emailStatus ? { result: 'ok', saved: 'lead', email: emailStatus } : { result: 'ok', saved: 'lead' });
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
  if (/^(gta-medspa|hair-loss|instagram|realestate-index)/.test(src)) return 'index-download';
  if (/growth-os/.test(src)) return 'growth-os-download';
  var help = joinMulti_(d['help_with[]'] || d.help_with);
  if (help.indexOf('[From the marketing audit]') === 0) return 'audit-help';
  if (d.name || help) return 'contact';
  return 'unknown';
}

// Returns why a submission is spam, or '' when it may go to its tab.
// A page's own bot check tripped. The page still sends the submission so a real person caught by
// mistake (for example by phone autofill) is kept, not lost.
var CLIENT_FLAGS = {
  'trap': 'Hidden trap field was filled',
  'fast': 'Sent less than 3 seconds after the page opened',
  'no-input': 'No typing or tapping before sending'
};

function spamReason_(form, d) {
  if (d.client_flag) return 'Page bot check: ' + (CLIENT_FLAGS[d.client_flag] || String(d.client_flag).slice(0, 40)) +
    (d.trap_value ? ' (trap held: ' + String(d.trap_value).slice(0, 60) + ')' : '');
  if (d.company_url_secondary && String(d.company_url_secondary).trim() !== '') return 'Honeypot filled';
  if (form === 'unknown') return 'Unknown form';
  if (form === 'audit-feedback') return '';                       // no email address in it
  if (!isEmail_(pick_(d, 'email'))) return 'Invalid email';
  if (form === 'research-code' || form === 'research-verify') {
    if (!RESEARCH[pick_(d, 'research')]) return 'Unknown research';
    if (form === 'research-code' && isDisposable_(pick_(d, 'email'))) return 'Disposable email domain';
  }
  // The Meta Growth OS page downloads on the page, sends no email and carries no Turnstile widget, so only the
  // SEO checklist, which is emailed, needs a token (d2, 2026-11-10).
  if (form === 'growth-os-download' && growthOsProduct_(d) !== 'SEO Growth OS') return '';
  if (TURNSTILE_ACTIONS[form]) return turnstileReason_(form, d);
  return '';
}

function route_(form, d) {
  var email = pick_(d, 'email').toLowerCase();
  if (RATE_LIMITS[form]) {
    var tab = form === 'audit-plan' ? 'Audit' : form === 'index-download' ? 'Index downloads' : 'Growth OS downloads';
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
  return spam_(form, d, 'Unknown form');
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
    leadSource_(form, d)
  ]);
  if (form === 'contact' && pick_(d, 'contact_intent') === 'review') sendReviewConfirmation_(d);
}

// Automatic receipt for an accepted free review request, sent straight after the row is saved. It is proof the
// request arrived, not the personal reply promised within 1 to 2 business days. A mail failure never loses the lead.
function sendReviewConfirmation_(d) {
  var email = pick_(d, 'email');
  if (!isEmail_(email)) return;
  var first = (pick_(d, 'name').split(/\s+/)[0] || 'there').slice(0, 40);
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var text = 'Hi ' + first + ',\n\nThanks for sharing your website!\n\nI\'ve received your request for a free marketing review.\n\n' +
    'Here\'s what happens next:\n\n' +
    '- Within 1 to 2 business days: I\'ll personally reply to confirm the next steps.\n' +
    '- Within 5 to 7 business days: You\'ll receive your written marketing review covering what\'s working, what needs attention and what I\'d recommend fixing first.\n\n' +
    'If I need any more information, I\'ll let you know.\n\nThanks,\nAnkit\nHelp Me Marketing';
  var html = '<p>Hi ' + esc(first) + ',</p><p>Thanks for sharing your website!</p><p>I&rsquo;ve received your request for a free marketing review.</p>' +
    '<p><strong>Here&rsquo;s what happens next:</strong></p><ul>' +
    '<li><strong>Within 1 to 2 business days:</strong> I&rsquo;ll personally reply to confirm the next steps.</li>' +
    '<li><strong>Within 5 to 7 business days:</strong> You&rsquo;ll receive your written marketing review covering what&rsquo;s working, what needs attention and what I&rsquo;d recommend fixing first.</li></ul>' +
    '<p>If I need any more information, I&rsquo;ll let you know.</p><p>Thanks,<br>Ankit<br>Help Me Marketing</p>';
  send_(function () {
    MailApp.sendEmail({ to: email, replyTo: REPLY_TO, name: FROM_NAME, subject: 'Your free marketing review request is in', body: text, htmlBody: html });
  });
}

// Source column for a lead. Contact leads add the intent (free review or general), the site CTA that sent them,
// any UTM tags and the landing page, each checked against a pattern here: URL parameters are never trusted as sent.
// Kept in the existing Source column so the Leads columns and order stay unchanged.
function leadSource_(form, d) {
  if (form === 'audit-help') return /^fast$/.test(pick_(d, 'client_signal')) ? 'marketing audit | signal fast' : 'marketing audit';
  var parts = ['contact form', pick_(d, 'contact_intent') === 'review' ? 'free review' : 'general'];
  var entry = pick_(d, 'entry_point');
  if (/^(home_hero|home_final|home_journey|work_final|industry_(healthcare|finance|dtc|saas)_(hero|final)|research_(hub|gta_medspa|gta_medspa_help|business_spend)|seo_automation|ai_seo_setup|direct)$/.test(entry)) parts.push('entry ' + entry);
  ['utm_source', 'utm_medium', 'utm_campaign'].forEach(function (k) {
    var v = pick_(d, k).replace(/[^\w.\-]/g, '').slice(0, 60);
    if (v) parts.push(k.replace('utm_', '') + ' ' + v);
  });
  var sig = pick_(d, 'client_signal');
  if (/^fast$/.test(sig)) parts.push('signal fast');
  var lp = pick_(d, 'landing_page').replace(/[^\w\/.\-?=&]/g, '').slice(0, 160);
  if (lp) parts.push('landing ' + lp);
  return parts.join(' | ');
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
  var c = key && INDEX_CSV[key], sent = c ? send_(function () { sendIndexCsv_(email, c, cycle); }) : 'Not needed (downloads on the page)';
  tab_('Index downloads').appendRow([new Date(), email, key ? INDEX_REPORTS[key] : src, cycle, src, sent]);
}

// The CSV is fetched from the site at send time, so the email always carries the published edition.
function sendIndexCsv_(email, c, cycle) {
  var res = UrlFetchApp.fetch(c.url, { muteHttpExceptions: true, followRedirects: true });
  if (res.getResponseCode() !== 200) throw new Error('CSV fetch returned ' + res.getResponseCode());
  var blob = Utilities.newBlob(res.getContentText('UTF-8'), 'text/csv', c.name);
  var ed = cycle ? ' (edition ' + cycle + ')' : '';
  MailApp.sendEmail({ to: email, name: FROM_NAME, replyTo: REPLY_TO, subject: 'Your CSV: ' + c.title, attachments: [blob],
    body: 'The CSV for "' + c.title + '"' + ed + ' is attached: every post in the comparison with its recorded metrics and source link.\n\n' +
      'Read the case study: ' + SITE_URL + c.path + '\n\n' +
      'You asked for this file at ' + SITE_URL + c.path + '. I will email you when a new edition is published. Reply to this email if you have a question about the data.\n\nAnkit Kumar, HelpMeMarketing',
    htmlBody: '<div style="font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.6;color:#1a1a1a;max-width:560px">' +
      '<p style="margin:0 0 12px">The CSV for &ldquo;' + esc_(c.title) + '&rdquo;' + esc_(ed) + ' is attached: every post in the comparison with its recorded metrics and source link.</p>' +
      '<p style="margin:0 0 12px"><a href="' + SITE_URL + c.path + '" style="color:#c2410c">Read the case study</a></p>' +
      '<p style="margin:0 0 12px;color:#666;font-size:13px">You asked for this file at ' + SITE_URL.replace('https://', '') + c.path + '. I will email you when a new edition is published. Reply to this email if you have a question about the data.</p>' +
      '<p style="margin:0">Ankit Kumar, HelpMeMarketing</p></div>' });
}

function growthOsProduct_(d) {
  return (pick_(d, 'product') === 'meta' || /meta/.test(pick_(d, 'source'))) ? 'Meta Growth OS' : 'SEO Growth OS';
}

function addGrowthOs_(d, email) {
  var product = growthOsProduct_(d);
  var consent = d.marketingConsent === true || d.marketingConsent === 'true';
  // The SEO checklist is emailed as an attachment; the Meta bundle downloads on the page, so it gets no email.
  var sent = product === 'SEO Growth OS' ? send_(function () { sendSeoChecklist_(email, consent); }) : 'Not needed (downloads on the page)';
  tab_('Growth OS downloads').appendRow([new Date(), email, product, consent ? 'TRUE' : 'FALSE', consent ? new Date() : '',
    sent, pick_(d, 'referrer').slice(0, 300), pick_(d, 'userAgent').slice(0, 300)]);
  if (consent) addSubscriber_(email, product + (product === 'SEO Growth OS' ? ' visual guide' : ' download'), 'Yes, ticked the box');
  // The row is kept either way; the reply tells the page whether the checklist email was accepted.
  if (product === 'SEO Growth OS') return sent === 'Sent' || sent === 'Skipped (test)' ? 'lead_email_sent' : 'lead_email_failed';
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
  return 'spam';
}

/* ============================ research unlocks ============================ */

// Gated sections of a research page open only after the visitor proves the email is theirs (founder, 2026-11-02):
// research-code emails a 6-digit code, research-verify checks it. The code is never stored, only its salted SHA-256,
// in the script cache for 15 minutes; five wrong tries end it. One row per address and research on Research unlocks.
var RESEARCH = {
  'business-spend-index': { label: 'How Six Business Finance Brands Market Their Products', path: '/business-spend-index' },
  'realestate-index': { label: 'How Canadian Real Estate Investment Firms Market to Investors', path: '/realestate-index' }
};
var CODE_TTL_S = 15 * 60;
var CODE_MAX_TRIES = 5;
var CODES_PER_EMAIL_HOUR = 3;
var CODES_PER_DAY = 300;          // keeps MailApp quota for the other forms
// Common throwaway inbox services. A short list on purpose: the code itself is the real check.
var DISPOSABLE = ['mailinator.com', 'guerrillamail.com', 'guerrillamail.net', 'guerrillamail.org', 'sharklasers.com', 'grr.la', 'guerrillamailblock.com',
  '10minutemail.com', '10minutemail.net', 'temp-mail.org', 'tempmail.com', 'tempmail.net', 'tempmailo.com', 'temp-mail.io', 'tempail.com',
  'throwawaymail.com', 'yopmail.com', 'yopmail.net', 'yopmail.fr', 'getnada.com', 'nada.email', 'trashmail.com', 'trashmail.de', 'trashmail.net',
  'dispostable.com', 'maildrop.cc', 'mailnesia.com', 'mintemail.com', 'mohmal.com', 'fakeinbox.com', 'fakemail.net', 'emailondeck.com',
  'spamgourmet.com', 'mailcatch.com', 'mytemp.email', 'tempinbox.com', 'burnermail.io', 'moakt.com', 'tmail.ws', 'tmpmail.org', 'tmpmail.net',
  'inboxkitten.com', 'emailfake.com', 'luxusmail.org', 'mail.tm', 'mail.gw', 'dropmail.me', '1secmail.com', '1secmail.org', '1secmail.net',
  'mailpoof.com', 'spambox.us', 'discard.email', 'harakirimail.com', 'mailsac.com', 'tempr.email', 'linshiyouxiang.net', 'byom.de', 'trbvm.com',
  'example.com', 'example.org', 'example.net', 'test.com'];

function isDisposable_(email) {
  var dom = String(email).toLowerCase().split('@').pop();
  return DISPOSABLE.some(function (x) { return dom === x || dom.slice(-(x.length + 1)) === '.' + x; });
}

function sha256_(s) {
  return Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, s, Utilities.Charset.UTF_8)
    .map(function (b) { return ('0' + (b & 255).toString(16)).slice(-2); }).join('');
}

function codeKey_(email, research) { return 'rc_' + sha256_(email + '|' + research).slice(0, 40); }

// Six digits from Apps Script's random UUID (Math.random is not meant for secrets).
function newCode_() {
  var hex = Utilities.getUuid().replace(/-/g, '');
  return ('000000' + (parseInt(hex.slice(0, 12), 16) % 1000000)).slice(-6);
}

// Source column: the page, then its landing page and UTM tags, each checked against a pattern.
function researchSource_(d) {
  var parts = ['page ' + RESEARCH[pick_(d, 'research')].path];
  ['utm_source', 'utm_medium', 'utm_campaign'].forEach(function (k) {
    var v = pick_(d, k).replace(/[^\w.\-]/g, '').slice(0, 60);
    if (v) parts.push(k.replace('utm_', '') + ' ' + v);
  });
  var lp = pick_(d, 'landing_page').replace(/[^\w\/.\-?=&]/g, '').slice(0, 160);
  if (lp) parts.push('landing ' + lp);
  return parts.join(' | ');
}

// The row for this address and research, or 0.
function researchRow_(sh, email, label) {
  var last = sh.getLastRow();
  if (last < 2) return 0;
  var rows = sh.getRange(2, 2, last - 1, 2).getValues();
  for (var i = rows.length - 1; i >= 0; i--) if (String(rows[i][0]).toLowerCase() === email && rows[i][1] === label) return i + 2;
  return 0;
}

function researchCode_(d) {
  var email = pick_(d, 'email').toLowerCase(), key = pick_(d, 'research'), r = RESEARCH[key];
  var cache = CacheService.getScriptCache(), props = PropertiesService.getScriptProperties();
  var hourKey = 'rcn_' + sha256_(email).slice(0, 40), sentHour = parseInt(cache.get(hourKey) || '0', 10);
  if (sentHour >= CODES_PER_EMAIL_HOUR) { spam_('research-code', d, 'Too many codes for this email in an hour'); return { result: 'ok', saved: 'limit' }; }
  var today = Utilities.formatDate(new Date(), 'America/Toronto', 'yyyy-MM-dd'), day = (props.getProperty('rc_day') || '').split(':');
  var sentDay = day[0] === today ? parseInt(day[1] || '0', 10) : 0;
  if (sentDay >= CODES_PER_DAY) { spam_('research-code', d, 'Daily code limit reached'); return { result: 'ok', saved: 'limit' }; }

  var code = newCode_(), salt = Utilities.getUuid();
  var sent = send_(function () {
    MailApp.sendEmail({ to: email, replyTo: REPLY_TO, name: FROM_NAME, subject: code + ' is your code for the HelpMeMarketing case study',
      body: researchCodeText_(code, r), htmlBody: researchCodeHtml_(code, r) });
  });
  if (sent.indexOf('Failed') === 0) return { result: 'error' };
  cache.put(codeKey_(email, key), JSON.stringify({ h: sha256_(salt + code), s: salt, n: 0, exp: Date.now() + CODE_TTL_S * 1000 }), CODE_TTL_S);
  cache.put(hourKey, String(sentHour + 1), 3600);
  props.setProperty('rc_day', today + ':' + (sentDay + 1));

  var sh = tab_('Research unlocks'), row = researchRow_(sh, email, r.label);
  if (row) {
    var n = parseInt(sh.getRange(row, 6).getValue(), 10) || 0;
    sh.getRange(row, 1).setValue(new Date());
    sh.getRange(row, 6).setValue(n + 1);
  } else {
    sh.appendRow([new Date(), email, r.label, 'Code sent', '', 1, researchSource_(d)]);
  }
  return { result: 'ok', saved: 'code_sent' };
}

function researchVerify_(d) {
  var email = pick_(d, 'email').toLowerCase(), key = pick_(d, 'research'), r = RESEARCH[key];
  var code = pick_(d, 'code').replace(/\D/g, '');
  var cache = CacheService.getScriptCache(), ck = codeKey_(email, key), raw = cache.get(ck);
  if (!raw) return { result: 'ok', verified: false, reason: 'expired' };
  var e = JSON.parse(raw);
  if (code.length !== 6 || sha256_(e.s + code) !== e.h) {
    e.n += 1;
    var left = Math.floor((e.exp - Date.now()) / 1000);
    if (e.n >= CODE_MAX_TRIES || left < 1) { cache.remove(ck); return { result: 'ok', verified: false, reason: 'too_many' }; }
    cache.put(ck, JSON.stringify(e), left);
    return { result: 'ok', verified: false, reason: 'wrong' };
  }
  cache.remove(ck);
  var sh = tab_('Research unlocks'), row = researchRow_(sh, email, r.label);
  if (row) { sh.getRange(row, 4).setValue('Verified'); sh.getRange(row, 5).setValue(new Date()); }
  else sh.appendRow([new Date(), email, r.label, 'Verified', new Date(), 1, researchSource_(d)]);
  return { result: 'ok', verified: true };
}

function researchCodeText_(code, r) {
  return 'Your code: ' + code + '\n\nEnter it on the page to read the full case study "' + r.label + '". It works for 15 minutes.\n\n' +
    'You asked for this code at ' + SITE_URL + r.path + '. If you did not, you can ignore this email; nothing happens without the code.\n\n' +
    'Ankit Kumar\nHelpMeMarketing\n' + SENDER_POSTAL;
}

function researchCodeHtml_(code, r) {
  return '<div style="max-width:560px;margin:0 auto;padding:24px;font:15px/1.6 Arial,sans-serif;color:#1A1A1A">' +
    '<p style="margin:0 0 8px">Your code:</p>' +
    '<p style="margin:0 0 20px;font:700 32px/1.2 Arial,sans-serif;letter-spacing:6px">' + esc_(code) + '</p>' +
    '<p style="margin:0 0 12px">Enter it on the page to read the full case study &ldquo;' + esc_(r.label) + '&rdquo;. It works for 15 minutes.</p>' +
    '<p style="margin:0 0 20px;color:#666;font-size:13px">You asked for this code at <a href="' + SITE_URL + r.path + '" style="color:#666">' + SITE_URL.replace('https://', '') + r.path + '</a>. ' +
    'If you did not, you can ignore this email; nothing happens without the code.</p>' +
    '<p style="margin:0;color:#666;font-size:13px">Ankit Kumar<br>HelpMeMarketing<br>' + esc_(SENDER_POSTAL) + '</p></div>';
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

// Throws (so send_ records "Failed" and the page shows the recovery message) when the file ID is still the
// placeholder, the file is missing or not shared with the script, or it is not actually a PDF.
function checklistBlob_() {
  if (!SEO_CHECKLIST_FILE_ID || /PASTE/.test(SEO_CHECKLIST_FILE_ID)) throw new Error('Checklist file ID is not set');
  var file = DriveApp.getFileById(SEO_CHECKLIST_FILE_ID);
  if (file.getMimeType() !== 'application/pdf') throw new Error('Checklist file is not a PDF (' + file.getMimeType() + ')');
  var blob = file.getBlob();
  if (blob.getContentType() !== 'application/pdf') throw new Error('Checklist file content is not a PDF');
  return blob.setName(SEO_CHECKLIST_FILENAME);
}

function sendSeoChecklist_(email, optedIn) {
  var blob = checklistBlob_();
  MailApp.sendEmail({ to: email, name: FROM_NAME, replyTo: REPLY_TO, subject: 'Your SEO Growth OS Visual Guide',
    htmlBody: seoChecklistHtml_(optedIn), body: seoChecklistText_(optedIn), attachments: [blob] });
}

// Visual Guide email (founder copy and layout, 2026-11-11): light grey frame, white logo header, Obsidian banner,
// white body, Warm Ivory setup block with one orange button, compact footer. All text is live text; the only image
// is the logo (PNG, because Gmail and Outlook block SVG), with an alt text that reads as the brand name when images
// are off. The footer matches the visitor's newsletter choice; a request on its own never subscribes anyone.
var SEO_GUIDE_ENQUIRY_URL = SITE_URL + '/contact?entry=seo_automation#contact-form';
var SEO_GUIDE_LOGO_URL = SITE_URL + '/assets/brand/email/hmm-logo-email.png';
function seoGuideFooter_(optedIn) {
  return ['You requested this guide at helpmemarketing.com.',
    optedIn ? 'You also opted in to occasional SEO notes and updates. To unsubscribe, reply to this email with “unsubscribe”.'
            : 'This request does not subscribe you to marketing updates.',
    'HelpMeMarketing, Halton Hills, Ontario, Canada'];
}
function seoChecklistHtml_(optedIn) {
  var font = 'Arial,Helvetica,sans-serif', serif = 'Georgia,\'Times New Roman\',serif',
    outer = '#EEEDEA', white = '#FFFFFF', obsidian = '#0E0E0E', ivory = '#F7F6F2', text = '#0E0E0E', body = '#3A3A3A',
    muted = '#6B6B6B', cta = '#FF5C1A', line = '#E4E1DA';
  var p = function (html, pad) {
    return '<tr><td class="px" style="font-family:' + font + ';font-size:17px;line-height:1.65;color:' + body + ';padding:0 30px ' + (pad === undefined ? 18 : pad) + 'px 30px;">' + html + '</td></tr>';
  };
  var foot = seoGuideFooter_(optedIn);
  return (
'<!DOCTYPE html>' +
'<html lang="en"><head><meta charset="UTF-8">' +
'<meta name="viewport" content="width=device-width,initial-scale=1">' +
'<meta name="color-scheme" content="light"><meta name="supported-color-schemes" content="light">' +
'<title>Your SEO Growth OS Visual Guide</title>' +
'<style>@media only screen and (max-width:600px){.px{padding-left:22px!important;padding-right:22px!important}' +
'.ban{font-size:24px!important}.wrap{padding:12px 0!important}}</style></head>' +
'<body style="margin:0;padding:0;background:' + outer + ';">' +
'<div style="display:none;max-height:0;overflow:hidden;opacity:0;color:' + outer + ';">' +
'Your five-page guide is attached. Start with the challenge closest to yours.</div>' +
'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:' + outer + ';">' +
'<tr><td class="wrap" align="center" style="padding:32px 12px;">' +
'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:640px;background:' + white + ';">' +
// 1. White header with the logo
'<tr><td align="center" style="padding:28px 30px 24px 30px;background:' + white + ';">' +
'<img src="' + SEO_GUIDE_LOGO_URL + '" width="140" height="64" alt="HelpMeMarketing" ' +
'style="display:block;width:140px;height:auto;border:0;font-family:' + font + ';font-size:15px;line-height:20px;font-weight:bold;color:' + text + ';text-align:center;"></td></tr>' +
// 2. Obsidian banner
'<tr><td class="px" style="background:' + obsidian + ';padding:28px 30px;">' +
'<div style="font-family:' + font + ';font-size:12px;letter-spacing:2px;text-transform:uppercase;font-weight:bold;color:' + cta + ';padding-bottom:8px;">SEO Growth OS</div>' +
'<div class="ban" style="font-family:' + serif + ';font-size:28px;line-height:1.25;color:' + white + ';">Your visual guide <span style="color:' + cta + ';font-style:italic;">is attached.</span></div>' +
'</td></tr>' +
// 3. White body with the approved copy
'<tr><td style="height:30px;line-height:30px;font-size:0;">&nbsp;</td></tr>' +
p('Hello,') +
p('Thanks for your interest in SEO Growth OS. Your guide is attached.') +
p('See how it brings together SEO audits, automation and growth planning, from finding issues to prioritising improvements and tracking progress.') +
p('Start on page 1 with the challenge closest to yours, then explore what can be automated and what you receive.', 30) +
// 4. Warm Ivory setup block
'<tr><td class="px" align="center" style="background:' + ivory + ';padding:30px;border-top:1px solid ' + line + ';border-bottom:1px solid ' + line + ';">' +
'<div style="font-family:' + serif + ';font-size:22px;line-height:1.3;color:' + text + ';padding-bottom:20px;">Want help setting it up for your business?</div>' +
'<table role="presentation" cellpadding="0" cellspacing="0" align="center"><tr><td style="border-radius:8px;background:' + cta + ';">' +
'<a href="' + SEO_GUIDE_ENQUIRY_URL + '" style="display:inline-block;font-family:' + font + ';font-size:16px;font-weight:bold;color:' + obsidian + ';background:' + cta + ';border-radius:8px;padding:15px 28px;text-decoration:none;">' +
'Enquire about SEO automation</a></td></tr></table></td></tr>' +
// Signature
'<tr><td style="height:30px;line-height:30px;font-size:0;">&nbsp;</td></tr>' +
p('Ankit Kumar<br><span style="color:' + muted + ';">HelpMeMarketing</span>', 30) +
'</table>' +
// 5. Compact footer
'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:640px;">' +
'<tr><td class="px" style="padding:20px 30px 8px 30px;font-family:' + font + ';font-size:12px;line-height:1.6;color:' + muted + ';text-align:center;">' +
foot.join('<br>') + '<br>' +
'<a href="' + SITE_URL + '/privacy" style="color:' + muted + ';text-decoration:underline;">Privacy policy</a>' +
'</td></tr></table>' +
'</td></tr></table></body></html>'
  );
}

function seoChecklistText_(optedIn) {
  return ['SEO GROWTH OS', 'Your visual guide is attached.', '',
    'Hello,', '',
    'Thanks for your interest in SEO Growth OS. Your guide is attached.', '',
    'See how it brings together SEO audits, automation and growth planning, from finding issues to prioritising improvements and tracking progress.', '',
    'Start on page 1 with the challenge closest to yours, then explore what can be automated and what you receive.', '',
    'Want help setting it up for your business?',
    'Enquire about SEO automation: ' + SEO_GUIDE_ENQUIRY_URL, '',
    'Ankit Kumar', 'HelpMeMarketing', '', '---'
  ].concat(seoGuideFooter_(optedIn), ['Privacy policy: ' + SITE_URL + '/privacy']).join('\n');
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
  CacheService.getScriptCache().put('setup_check', '1', 60);
  checklistBlob_();   // fails until the checklist file ID is set and points at a real PDF
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
    { parameters: { form: ['contact'], name: ['TEST review'], email: [me], phone: [''], website: ['https://example.com'], 'help_with[]': ['Free marketing review'], biggest_challenge: [''], contact_intent: ['review'], entry_point: ['home_hero'], utm_source: ['test'] } },
    { parameters: { form: ['audit-help'], name: ['TEST audit lead'], email: [me], phone: [''], website: ['Not given'], 'help_with[]': ['TEST summary'], biggest_challenge: [''] } },
    { json: { form: 'audit-plan', email: me, plan_title: 'TEST plan', plan_text: 'YOUR MARKETING PLAN\nTEST', plan_url: AUDIT_URL + '#plan=test', path: 'online', priority: 'P_TEST' } },
    { json: { form: 'audit-feedback', answer: 'Yes', path: 'online', priority: 'P_TEST' } },
    { parameters: { form: ['index-download'], email: [me], source: ['gta-medspa-cycle-001'] } },
    { json: { form: 'growth-os-download', product: 'seo', email: me, marketingConsent: false, source: '/seo-growth-os' } },
    { json: { form: 'subscribe', email: me, source: 'blog' } },
    { parameters: { form: ['research-code'], email: ['test@mailinator.com'], research: ['business-spend-index'] } },
    { parameters: { form: ['contact'], name: ['TEST bot'], email: [me], company_url_secondary: ['http://spam.example'] } }
  ];
  cases.forEach(function (c) {
    var e = c.json ? { parameters: {}, postData: { contents: JSON.stringify(c.json) } } : { parameters: c.parameters };
    doPost(e);
  });
  Logger.log('Wrote ' + cases.length + ' TEST rows: Leads 3 (one a free review, Source should read contact form | free review | entry home_hero | source test), Audit 2, Index downloads 1, Growth OS downloads 1, Subscribers 1, Spam 2 (one a disposable research email). Delete them when checked. Run testResearchUnlock for the code flow.');
}

// Runs the research unlock flow against your own address: sends a real code email, then checks a wrong code
// and the real one. Writes one Research unlocks row (delete it after). Run after setup, before redeploying.
function testResearchUnlock() {
  var me = Session.getActiveUser().getEmail().toLowerCase(), d = { email: me, research: 'business-spend-index' };
  Logger.log('code request -> ' + JSON.stringify(researchCode_(d)));
  Logger.log('wrong code -> ' + JSON.stringify(researchVerify_({ email: me, research: 'business-spend-index', code: '000000' })));
  Logger.log('Now open the email, then run testResearchVerify after typing the code into RESEARCH_TEST_CODE below.');
}
// Sends the Real Estate Index CSV to you (the account running the script) and adds a row to Index downloads.
function testIndexCsv() {
  var me = Session.getActiveUser().getEmail().toLowerCase();
  Logger.log('index csv -> ' + JSON.stringify(route_('index-download', { form: 'index-download', email: me, source: 'realestate-index-cycle-005' })));
  Logger.log('Check your inbox for the CSV.');
}

var RESEARCH_TEST_CODE = '';
function testResearchVerify() {
  var me = Session.getActiveUser().getEmail().toLowerCase();
  Logger.log('real code -> ' + JSON.stringify(researchVerify_({ email: me, research: 'business-spend-index', code: RESEARCH_TEST_CODE })));
}

// Logs the Source text each review link would produce. Writes no row, sends no email and skips Turnstile,
// so it is safe to run on the production script at any time. An unknown entry must show no "entry" part.
function testLeadSources() {
  ['research_hub', 'research_gta_medspa', 'research_gta_medspa_help', 'research_business_spend', 'home_hero', 'direct', 'not_a_real_entry'].forEach(function (entry) {
    Logger.log(entry + ' -> ' + leadSource_('contact', { contact_intent: 'review', entry_point: entry }));
  });
}

// Step 5. Sends the SEO visual guide and a sample plan to your own address.
function testEmails() {
  var me = Session.getActiveUser().getEmail();
  sendSeoChecklist_(me, false);   // not opted in: footer says the request does not subscribe you
  sendSeoChecklist_(me, true);    // opted in: footer explains how to unsubscribe
  MailApp.sendEmail({ to: me, replyTo: REPLY_TO, name: FROM_NAME, subject: 'Your marketing plan: Cut missed appointments (test)',
    body: 'YOUR MARKETING PLAN\nTest', htmlBody: planHtml_('YOUR MARKETING PLAN\nFrom the HelpMeMarketing marketing audit\n\nYOUR FIRST PRIORITY\nCut missed appointments\n\nYOUR FIRST ACTION\n1. Send a confirmation right after every booking.', AUDIT_URL + '#plan=buy.appointment~goal.convert~stage.active~a_fit.most~a_wait.week~a_how.online~a_finish.most~a_remind.none~a_noshow.some~who.self') });
  Logger.log('Sent the SEO visual guide (both footer versions) and a sample plan to ' + me);
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
