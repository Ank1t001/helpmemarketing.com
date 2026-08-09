/**
 * HelpMeMarketing — Schedule a Call (backend Apps Script)
 *
 * Receives the three-step qualifying form from /schedule-a-call, appends a row
 * to the "call_requests" tab in the "HMM Schedule Call" workbook, emails Ankit
 * a pre-call brief, and sends the prospect a confirmation.
 *
 * Third Apps Script on the site, alongside the contact form and the marketing
 * audit. Its own workbook, its own deployment.
 *
 * CASL note: this is a requested reply to an enquiry, so it runs on implied
 * consent. There is deliberately no marketing opt-in here and these addresses
 * must NOT be added to any list. Someone booking a call has not agreed to be
 * marketed to.
 *
 * Deployment:
 *   1. Paste this file into the "HMM Schedule Call" Apps Script project,
 *      overwriting the previous version. Do not paste it over the Growth OS
 *      gate project; they are separate deployments.
 *   2. Run setupSheet() once to create the call_requests tab and header row.
 *      Until this runs, every submission throws "Sheet tab not found".
 *   3. Run testNotify() to send yourself a sample brief and check it reads well.
 *   4. Deploy -> New deployment -> Web app, Execute as: Me, Who has access: Anyone.
 *   5. Confirm the /exec URL returns the doGet JSON in a private window, then
 *      share it back to be wired into SCHED_URL in schedule-a-call.html.
 *   6. Authorize MailApp and SpreadsheetApp on first run.
 *
 * Re-deploying: editing code does NOT update the live web app. Deploy ->
 * Manage deployments -> edit -> New version, every time.
 */

// ============================================================
// CONFIGURATION
// ============================================================

// The dedicated "HMM Schedule Call" workbook. One workbook per funnel, matching
// how the Growth OS gate writes to "Growth Seo". The shared "Help Me Marketing
// Data" file (1RMYcfgl2DK4WvRNZFr1lu6_odGMwYX-EJBkZv-tSCds) keeps contact-form
// and audit leads only.
const SHEET_ID = '1DvloD5Qp9GSe-pqJh8NsAuVlhXJYleGV6oNV1JdD3l8';
const SHEET_NAME = 'call_requests';

const FROM_NAME = 'HelpMeMarketing';
const FROM_ADDRESS = 'Hello@helpmemarketing.com';
const NOTIFY_TO = 'Hello@helpmemarketing.com';   // where the pre-call brief lands
const SITE_URL = 'https://helpmemarketing.com';

// Max submissions per email per rolling window.
const RATE_LIMIT_MAX = 3;
const RATE_LIMIT_WINDOW_MS = 24 * 60 * 60 * 1000;

// Field order drives both the sheet columns and the brief. Keep them in sync:
// add a field here and it appears in the row and the email automatically.
const FIELDS = [
  ['name',           'Name'],
  ['email',          'Email'],
  ['company',        'Company'],
  ['website',        'Website'],
  ['businessType',   'What they sell'],
  ['market',         'Market'],
  ['dealValue',      'Value of a won customer'],
  ['platform',       'Platform'],
  ['whoShips',       'Who ships site changes'],
  ['whoWrites',      'Who writes content'],
  ['organicTraffic', 'Organic traffic'],
  ['trafficDrop',    'Traffic drop'],
  ['alreadyTried',   'Already tried'],
  ['timeSinks',      'Time sinks'],
  ['toolStack',      'Tool stack'],
  ['budget',         'Budget'],
  ['timeline',       'Timeline'],
  ['decisionMaker',  'Decision maker'],
  ['theDecision',    'The decision they want made']
];

const HEADER_ROW = ['Timestamp'].concat(FIELDS.map(function (f) { return f[1]; }))
                                .concat(['Source', 'Referrer', 'User agent']);

// ============================================================
// MAIN ENTRY POINT
// ============================================================

function doPost(e) {
  try {
    const data = getRequestData(e);

    // Honeypot: silent success so the bot cannot tell it failed.
    if (data.company_url_secondary && String(data.company_url_secondary).trim().length > 0) {
      return jsonResponse({ status: 'success' });
    }

    const email = String(data.email || '').trim();
    if (!isValidEmail(email)) {
      return jsonResponse({ status: 'success' });
    }

    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(SHEET_NAME);
    if (!sheet) throw new Error('Sheet tab not found: ' + SHEET_NAME);

    if (!checkRateLimit(email, sheet)) {
      return jsonResponse({ status: 'success' });
    }

    appendRow(sheet, data);
    notifyTeam(data);
    confirmToProspect(data);

    return jsonResponse({ status: 'success' });
  } catch (err) {
    console.error('Schedule-call handler failed: ' + err);
    return jsonResponse({ status: 'error', message: String(err) });
  }
}

function doGet() {
  return jsonResponse({ status: 'ok', service: 'HMM Schedule Call' });
}

// ============================================================
// HELPERS
// ============================================================

function getRequestData(e) {
  if (e && e.postData && e.postData.contents) {
    try { return JSON.parse(e.postData.contents); } catch (err) { /* fall through */ }
  }
  return (e && e.parameter) ? e.parameter : {};
}

function jsonResponse(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function isValidEmail(email) {
  if (!email || email.length < 5 || email.length > 254) return false;
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function checkRateLimit(email, sheet) {
  const values = sheet.getDataRange().getValues();
  if (values.length <= 1) return true;
  const cutoff = new Date(Date.now() - RATE_LIMIT_WINDOW_MS);
  const target = email.toLowerCase();
  let count = 0;
  for (let i = 1; i < values.length; i++) {
    const rowDate = new Date(values[i][0]);
    const rowEmail = String(values[i][2] || '').toLowerCase();  // col 3 = Email
    if (rowDate >= cutoff && rowEmail === target) {
      count++;
      if (count >= RATE_LIMIT_MAX) return false;
    }
  }
  return true;
}

/** timeSinks arrives as an array of slugs; everything else is a string. */
function readField(data, key) {
  const v = data[key];
  if (Array.isArray(v)) return v.join(', ');
  return v === undefined || v === null ? '' : String(v).trim();
}

// ============================================================
// SHEET WRITE
// ============================================================

function appendRow(sheet, data) {
  const row = [new Date()];
  FIELDS.forEach(function (f) { row.push(readField(data, f[0])); });
  row.push(String(data.source || '/schedule-a-call'));
  row.push(String(data.referrer || ''));
  row.push(String(data.userAgent || ''));
  sheet.appendRow(row);
}

// ============================================================
// EMAILS
// ============================================================

/** The pre-call brief. Everything answered, in the order it was asked. */
function notifyTeam(data) {
  const name = readField(data, 'name') || 'Someone';
  const company = readField(data, 'company') || 'unknown company';
  const budget = readField(data, 'budget') || 'no budget given';
  const timeline = readField(data, 'timeline') || 'no timeline given';

  const subject = 'Call request: ' + company + ' (' + budget + ', ' + timeline + ')';

  let rows = '';
  let text = [];
  FIELDS.forEach(function (f) {
    const v = readField(data, f[0]);
    if (!v) return;   // skip blanks so the brief stays scannable
    rows +=
      '<tr>' +
      '<td style="padding:7px 14px 7px 0;color:#888;font-size:13px;vertical-align:top;white-space:nowrap">' + f[1] + '</td>' +
      '<td style="padding:7px 0;color:#111;font-size:14px;vertical-align:top">' + escapeHtml(v) + '</td>' +
      '</tr>';
    text.push(f[1] + ': ' + v);
  });

  const html =
    '<div style="font-family:Arial,Helvetica,sans-serif;max-width:640px">' +
    '<p style="font-size:15px;color:#111;margin:0 0 4px"><b>' + escapeHtml(name) + '</b> from <b>' + escapeHtml(company) + '</b> wants a call.</p>' +
    '<p style="font-size:13px;color:#888;margin:0 0 18px">Submitted from ' + escapeHtml(String(data.source || '/schedule-a-call')) +
    (data.referrer ? ' &middot; came from ' + escapeHtml(String(data.referrer)) : '') + '</p>' +
    '<table cellpadding="0" cellspacing="0" style="border-top:1px solid #e5e5e5;width:100%">' + rows + '</table>' +
    '</div>';

  MailApp.sendEmail({
    to: NOTIFY_TO,
    from: FROM_ADDRESS,
    name: FROM_NAME,
    replyTo: readField(data, 'email') || FROM_ADDRESS,   // reply goes to the prospect
    subject: subject,
    htmlBody: html,
    body: name + ' from ' + company + ' wants a call.\n\n' + text.join('\n')
  });
}

/** Short confirmation so they know it landed. No marketing, no list. */
function confirmToProspect(data) {
  const email = readField(data, 'email');
  if (!isValidEmail(email)) return;
  const first = (readField(data, 'name').split(' ')[0]) || 'there';

  const html =
    '<div style="font-family:Arial,Helvetica,sans-serif;max-width:560px;font-size:15px;line-height:1.6;color:#111">' +
    '<p>Hi ' + escapeHtml(first) + ',</p>' +
    '<p>Thanks for the detail. It means we can open the call with what we would actually do, rather than spending the first twenty minutes on background.</p>' +
    '<p>If you have not already picked a slot, reply to this email and we will send times that work.</p>' +
    '<p style="color:#888;font-size:13px;margin-top:24px">Ankit Kumar &middot; Help Me Marketing<br>' +
    '<a href="' + SITE_URL + '" style="color:#FF5C1A">helpmemarketing.com</a></p>' +
    '</div>';

  MailApp.sendEmail({
    to: email,
    from: FROM_ADDRESS,
    name: FROM_NAME,
    replyTo: FROM_ADDRESS,
    subject: 'We got your details',
    htmlBody: html,
    body: 'Hi ' + first + ',\n\nThanks for the detail. It means we can open the call with what we ' +
          'would actually do, rather than spending the first twenty minutes on background.\n\n' +
          'If you have not already picked a slot, reply to this email and we will send times ' +
          'that work.\n\nAnkit Kumar, Help Me Marketing\n' + SITE_URL
  });
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// ============================================================
// ONE-TIME SETUP AND TEST
// ============================================================

/** Creates the call_requests tab and header row. Safe to re-run. */
function setupSheet() {
  const ss = SpreadsheetApp.openById(SHEET_ID);
  let sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) sheet = ss.insertSheet(SHEET_NAME);
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADER_ROW);
    sheet.getRange(1, 1, 1, HEADER_ROW.length).setFontWeight('bold');
    sheet.setFrozenRows(1);
  }
  Logger.log('Ready: tab "' + SHEET_NAME + '" with ' + HEADER_ROW.length + ' columns.');
}

/** Sends a sample brief so the formatting can be checked before it matters. */
function testNotify() {
  notifyTeam({
    name: 'Jamie Chen', email: 'jamie@example.com', company: 'Acme Supply',
    website: 'acme.example', businessType: 'SaaS or B2B software', market: 'Canada',
    dealValue: '$2,000 to $10,000', platform: 'WordPress',
    whoShips: 'An agency or contractor', whoWrites: 'Freelance writer',
    organicTraffic: '5,000 to 25,000', trafficDrop: 'Yes, after a Google update',
    alreadyTried: 'Two agencies, neither shipped anything technical.',
    timeSinks: ['reporting', 'content'], toolStack: 'HubSpot, GA4',
    budget: '$2,500 to $5,000', timeline: 'Within the next month',
    decisionMaker: 'Me, I can decide',
    theDecision: 'Whether to rebuild or fix what we have.',
    source: '/schedule-a-call', referrer: SITE_URL + '/seo-growth-os'
  });
  Logger.log('Sample brief sent to ' + NOTIFY_TO);
}
