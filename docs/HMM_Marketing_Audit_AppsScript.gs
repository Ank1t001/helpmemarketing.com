/**
 * HelpMeMarketing marketing audit: backend Apps Script, v2 (2026-09-29).
 *
 * v2 replaces the v1 maturity-score script (tier content, 0 to 100 score, email gate). The
 * new audit on /tools/marketing-audit shows the whole plan on screen with no email, so this
 * script only handles the three things a visitor can choose to send:
 *
 *   action "plan"       Email my plan. Emails the visitor the plan text the page built, plus a
 *                       link that reopens the same plan. Logged on the plan_requests tab.
 *   action "subscribe"  Subscribe to updates. A separate, optional choice. Logged on the
 *                       subscribers tab. This script does not send newsletters; export the tab
 *                       to whatever tool sends them.
 *   action "feedback"   The optional "Do you know what to do next?" answer. Logged on the
 *                       feedback tab. No email address is sent with it.
 *
 * "Contact HMM" does NOT come here. The audit's contact form posts to the contact form's own
 * Apps Script (the "HMM | Contact Us" sheet), with the audit summary in the
 * "What do you need help with?" column, starting "[From the marketing audit]".
 *
 * The page sends JSON as text/plain with mode no-cors, so it never reads the reply. Every
 * rejection therefore returns the same "ok", and a bot learns nothing.
 *
 * SET-UP (keeps the same /exec URL as v1):
 *
 *   1. Open the existing "HMM Marketing Audit" Apps Script project (the one behind v1).
 *   2. Replace everything in Code.gs with this file. Save.
 *   3. Deploy > Manage deployments > edit (pencil) the existing deployment > Version: New
 *      version > Deploy. Editing keeps the same /exec URL:
 *        https://script.google.com/macros/s/AKfycbxei2sZjxF410RIcu4ynzA29cqAHtXI3sql90h57qEYFvDjJAWhZUAxi1Xy16a60RWM/exec
 *   4. Approve MailApp and SpreadsheetApp if Google asks.
 *   5. Run testPlanEmail() once from the editor with your own address to see the email.
 *   6. Tell Claude it is live. The page switches on when that URL goes in the
 *      data-plan-endpoint attribute on <div id="ma"> in tools/marketing-audit.html. Until then
 *      "Email my plan" opens the visitor's own email app with the plan filled in, and
 *      "Subscribe to updates" stays hidden.
 *
 * The three tabs are created on first use, with a bold header row.
 */

const SHEET_ID = '1RMYcfgl2DK4WvRNZFr1lu6_odGMwYX-EJBkZv-tSCds';
const FROM_NAME = 'HelpMeMarketing';
const REPLY_TO = 'hello@helpmemarketing.com';
const PAGE_URL = 'https://helpmemarketing.com/tools/marketing-audit';
const RATE_LIMIT_MAX = 5;                              // per email address, per action
const RATE_LIMIT_WINDOW_MS = 24 * 60 * 60 * 1000;      // rolling 24 hours
const MAX_PLAN_CHARS = 12000;

const TABS = {
  plan: { name: 'plan_requests', head: ['Received', 'Email', 'Priority', 'Path', 'Plan title', 'Plan link'] },
  subscribe: { name: 'subscribers', head: ['Received', 'Email', 'Source'] },
  feedback: { name: 'feedback', head: ['Received', 'Answer', 'Priority', 'Path'] }
};

function doPost(e) {
  try {
    const d = readBody_(e);
    if (d.company_url_secondary) return ok_();                 // honeypot, if a client ever sends it
    const action = String(d.action || '');
    if (action === 'plan') return handlePlan_(d);
    if (action === 'subscribe') return handleSubscribe_(d);
    if (action === 'feedback') return handleFeedback_(d);
  } catch (err) {
    console.error(err);
  }
  return ok_();
}

function handlePlan_(d) {
  const email = clean_(d.email, 160).toLowerCase();
  const text = clean_(d.plan_text, MAX_PLAN_CHARS);
  const url = clean_(d.plan_url, 600);
  if (!isEmail_(email) || !text || url.indexOf(PAGE_URL + '#plan=') !== 0) return ok_();
  const sh = tab_('plan');
  if (rateLimited_(sh, email)) return ok_();
  const title = clean_(d.plan_title, 120) || 'Your marketing plan';
  sh.appendRow([new Date(), email, clean_(d.priority, 40), clean_(d.path, 40), title, url]);
  MailApp.sendEmail({
    to: email,
    replyTo: REPLY_TO,
    name: FROM_NAME,
    subject: 'Your marketing plan: ' + title,
    body: text + '\n\n' + footer_(),
    htmlBody: planHtml_(text, url)
  });
  return ok_();
}

function handleSubscribe_(d) {
  const email = clean_(d.email, 160).toLowerCase();
  if (!isEmail_(email)) return ok_();
  const sh = tab_('subscribe');
  if (rateLimited_(sh, email)) return ok_();
  const rows = sh.getDataRange().getValues();
  for (let i = 1; i < rows.length; i++) if (String(rows[i][1]).toLowerCase() === email) return ok_();  // already on the list
  sh.appendRow([new Date(), email, clean_(d.source, 40)]);
  return ok_();
}

function handleFeedback_(d) {
  const answer = clean_(d.answer, 10);
  if (['Yes', 'Partly', 'No'].indexOf(answer) === -1) return ok_();
  tab_('feedback').appendRow([new Date(), answer, clean_(d.priority, 40), clean_(d.path, 40)]);
  return ok_();
}

/* ---------- helpers ---------- */

function readBody_(e) {
  if (e && e.postData && e.postData.contents) {
    try { return JSON.parse(e.postData.contents); } catch (err) { /* fall through */ }
  }
  return (e && e.parameter) || {};
}

function ok_() { return ContentService.createTextOutput('ok'); }

function clean_(v, max) { return String(v == null ? '' : v).replace(/\r/g, '').trim().slice(0, max); }

function isEmail_(v) { return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v); }

function tab_(key) {
  const ss = SpreadsheetApp.openById(SHEET_ID);
  let sh = ss.getSheetByName(TABS[key].name);
  if (!sh) {
    sh = ss.insertSheet(TABS[key].name);
    sh.appendRow(TABS[key].head);
    sh.getRange(1, 1, 1, TABS[key].head.length).setFontWeight('bold');
    sh.setFrozenRows(1);
  }
  return sh;
}

function rateLimited_(sh, email) {
  const since = Date.now() - RATE_LIMIT_WINDOW_MS;
  const rows = sh.getDataRange().getValues();
  let n = 0;
  for (let i = rows.length - 1; i >= 1; i--) {
    const t = rows[i][0] instanceof Date ? rows[i][0].getTime() : 0;
    if (t < since) break;                                   // rows are appended in time order
    if (String(rows[i][1]).toLowerCase() === email) n++;
  }
  return n >= RATE_LIMIT_MAX;
}

function footer_() {
  return 'You asked for this plan on helpmemarketing.com. This email does not sign you up for anything.\n' +
    'Want help with it? Reply to this email and Ankit will get back to you within 1 to 2 business days.';
}

function esc_(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/* The page's plan text uses UPPER CASE lines as headings. Turn those into bold headings and keep
   everything else as plain lines, so the email reads like the page without any page code. */
function planHtml_(text, url) {
  const lines = text.split('\n');
  let html = '';
  lines.forEach(function (l) {
    if (!l.trim()) { html += '<div style="height:10px"></div>'; return; }
    const heading = /^[A-Z0-9 ,.'=:\-]+$/.test(l) && /[A-Z]{3}/.test(l);
    html += heading
      ? '<p style="margin:14px 0 4px;font:600 13px/1.4 Arial,sans-serif;letter-spacing:.08em;color:#FF5C1A">' + esc_(l.replace(/=+/g, '').trim()) + '</p>'
      : '<p style="margin:0 0 4px;font:15px/1.55 Arial,sans-serif;color:#1A1A1A">' + esc_(l) + '</p>';
  });
  return '<div style="max-width:620px;margin:0 auto;padding:24px">' +
    '<p style="margin:0 0 16px"><a href="' + esc_(url) + '" style="display:inline-block;padding:10px 18px;background:#FF5C1A;color:#0E0E0E;border-radius:8px;font:600 14px Arial,sans-serif;text-decoration:none">Open your plan</a></p>' +
    html +
    '<p style="margin:24px 0 0;font:13px/1.5 Arial,sans-serif;color:#666">' + esc_(footer_()).replace(/\n/g, '<br>') + '</p></div>';
}

/* Run once from the editor: sends a sample plan to your own Google account address. */
function testPlanEmail() {
  const to = Session.getActiveUser().getEmail();
  handlePlan_({
    email: to,
    plan_title: 'Cut missed appointments',
    plan_url: PAGE_URL + '#plan=buy.appointment~goal.convert~stage.active~a_fit.most~a_wait.week~a_how.online~a_finish.most~a_remind.none~a_noshow.some~who.self',
    plan_text: 'YOUR MARKETING PLAN\nFrom the HelpMeMarketing marketing audit\n\nYOUR FIRST PRIORITY\nCut missed appointments\nPeople book but do not show up.\n\nYOUR FIRST ACTION\n1. Send a confirmation right after every booking.'
  });
}
