/**
 * HelpMeMarketing — SEO Growth OS download gate (backend Apps Script)
 *
 * Receives a JSON POST from the modal on /seo-growth-os, validates spam
 * protection, appends a row to the "growth_os_downloads" tab, and emails the
 * visitor the SEO Growth OS bundle as an attachment.
 *
 * Separate from the contact-form and marketing-audit Apps Scripts: different
 * tab, different deployment, different purpose.
 *
 * CASL note (this is why the consent columns exist):
 *   Sending the file itself runs on implied consent, because the visitor
 *   asked for it. Emailing them ANYTHING ELSE later requires express consent,
 *   which is what the unticked checkbox captures. Columns 3 and 4 record
 *   whether they ticked it and when, which is the record you would need to
 *   produce if a complaint is ever filed. Do not pre-tick that box, and do
 *   not market to rows where consent is FALSE.
 *
 * Deployment:
 *   1. Upload seo-growth-os.zip (the 32-skill bundle) to Drive, then copy its
 *      file ID from the share URL and paste it into ZIP_FILE_ID below.
 *   2. In the "Help Me Marketing Data" workbook, create a tab named
 *      growth_os_downloads and paste the 7-column header row from
 *      HEADER_ROW below into row 1.
 *   3. Open script.google.com -> New project -> name it "HMM Growth OS Gate".
 *   4. Paste this entire file into Code.gs, overwriting the default content.
 *   5. Save, then Deploy -> New deployment -> type: Web app
 *      - Description: "Growth OS download gate v1.0"
 *      - Execute as: Me
 *      - Who has access: Anyone (anonymous is required for an unauthenticated POST)
 *   6. Copy the /exec URL and share it back so it can be wired into
 *      seo-growth-os.html (the GATE_URL constant near the bottom of the page).
 *   7. On first run, authorize: MailApp, SpreadsheetApp, DriveApp.
 *   8. Send yourself a test through the live form and confirm the attachment
 *      arrives and opens.
 *
 * Quota: MailApp allows 100 recipients/day on consumer Gmail and 1500/day on
 * Workspace. Each download costs one. If the page ever spikes past that, move
 * to a hosted link instead of an attachment.
 */

// ============================================================
// CONFIGURATION — fill these before deployment
// ============================================================

// Same workbook as the contact form and the audit; separate tab.
const SHEET_ID = '1RMYcfgl2DK4WvRNZFr1lu6_odGMwYX-EJBkZv-tSCds';
const SHEET_NAME = 'growth_os_downloads';

// Drive file ID of the 32-skill bundle that gets attached to every delivery.
const ZIP_FILE_ID = 'PASTE_DRIVE_FILE_ID_HERE';
const ZIP_FILENAME = 'seo-growth-os.zip';

// Sender identity. FROM_ADDRESS must be an alias on the Workspace account.
const FROM_NAME = 'HelpMeMarketing';
const FROM_ADDRESS = 'Hello@helpmemarketing.com';
const SITE_URL = 'https://helpmemarketing.com';
const CONTACT_URL = SITE_URL + '/contact';

// CASL requires a real mailing address in any commercial electronic message.
const SENDER_POSTAL = 'Help Me Marketing, Burlington, Ontario, Canada';

// Rate limit: max deliveries per email address per rolling window.
const RATE_LIMIT_MAX = 3;
const RATE_LIMIT_WINDOW_MS = 24 * 60 * 60 * 1000;

// Paste this into row 1 of the growth_os_downloads tab:
// Timestamp | Email | Marketing consent | Consent timestamp | Source | Referrer | User agent
const HEADER_ROW = ['Timestamp', 'Email', 'Marketing consent', 'Consent timestamp',
                    'Source', 'Referrer', 'User agent'];

// ============================================================
// MAIN ENTRY POINT
// ============================================================

function doPost(e) {
  try {
    const data = getRequestData(e);

    // Check 1: Honeypot. Silent success so the bot cannot tell it failed.
    if (data.company_url_secondary && String(data.company_url_secondary).trim().length > 0) {
      return jsonResponse({ status: 'success' });
    }

    // Check 2: Email format. Client validates too; this is belt and braces.
    const email = String(data.email || '').trim();
    if (!isValidEmail(email)) {
      return jsonResponse({ status: 'success' });
    }

    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(SHEET_NAME);
    if (!sheet) throw new Error('Sheet tab not found: ' + SHEET_NAME);

    // Check 3: Rate limit, scoped to this tab only.
    if (!checkRateLimit(email, sheet)) {
      return jsonResponse({ status: 'success' });
    }

    const consent = data.marketingConsent === true || data.marketingConsent === 'true';

    appendRow(sheet, {
      email: email,
      consent: consent,
      source: String(data.source || '/seo-growth-os'),
      referrer: String(data.referrer || ''),
      userAgent: String(data.userAgent || '')
    });

    sendBundle(email);

    return jsonResponse({ status: 'success' });
  } catch (err) {
    console.error('Growth OS gate failed: ' + err);
    return jsonResponse({ status: 'error', message: String(err) });
  }
}

function doGet() {
  return jsonResponse({ status: 'ok', service: 'HMM Growth OS gate' });
}

// ============================================================
// REQUEST / RESPONSE HELPERS
// ============================================================

function getRequestData(e) {
  // Body is JSON.stringify(payload) sent as text/plain to avoid a CORS preflight,
  // matching /contact.html and /tools/marketing-audit.
  if (e && e.postData && e.postData.contents) {
    try {
      return JSON.parse(e.postData.contents);
    } catch (err) {
      // fall through to the form-urlencoded fallback
    }
  }
  return (e && e.parameter) ? e.parameter : {};
}

function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

// ============================================================
// VALIDATION HELPERS
// ============================================================

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
    const rowEmail = String(values[i][1] || '').toLowerCase();
    if (rowDate >= cutoff && rowEmail === target) {
      count++;
      if (count >= RATE_LIMIT_MAX) return false;
    }
  }
  return true;
}

// ============================================================
// SHEET WRITE
// ============================================================

function appendRow(sheet, d) {
  sheet.appendRow([
    new Date(),                        // 1. Timestamp
    d.email,                           // 2. Email
    d.consent ? 'TRUE' : 'FALSE',      // 3. Marketing consent (express, CASL)
    d.consent ? new Date() : '',       // 4. Consent timestamp (proof of when)
    d.source,                          // 5. Source page
    d.referrer,                        // 6. Referrer
    d.userAgent                        // 7. User agent
  ]);
}

// ============================================================
// DELIVERY
// ============================================================

function sendBundle(email) {
  const file = DriveApp.getFileById(ZIP_FILE_ID);
  const blob = file.getBlob().setName(ZIP_FILENAME);

  MailApp.sendEmail({
    to: email,
    from: FROM_ADDRESS,
    name: FROM_NAME,
    replyTo: FROM_ADDRESS,
    subject: 'Your SEO Growth OS download',
    htmlBody: buildEmailHtml(),
    body: buildEmailText(),
    attachments: [blob]
  });
}

function buildEmailHtml() {
  const font = 'Arial,Helvetica,sans-serif';
  const bg = '#0E0E0E';
  const card = '#1A1A1A';
  const text = '#FFFFFF';
  const muted = '#999999';
  const cta = '#FF5C1A';
  const mint = '#00D4AA';
  const border = 'rgba(255,255,255,0.10)';

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

function buildEmailText() {
  return [
    'Your SEO Growth OS is attached.',
    '',
    'The bundle is the zip on this email: 32 skills, a README, and a SETUP file.',
    'Unzip it, open SETUP.md, and it will walk you through installing the skills',
    'and running the first audit. It runs on your own machine. Nothing is sent to us.',
    '',
    'Start with the six-node command in the README. Point it at your own site, and',
    'it will produce a health score, a root-cause gap inventory, and a ranked',
    'roadmap before it touches anything.',
    '',
    'Need help with setup? Book a call: ' + CONTACT_URL,
    '',
    '---',
    'You are getting this because you asked for the SEO Growth OS download at',
    SITE_URL + '/seo-growth-os.',
    SENDER_POSTAL,
    'Prefer not to hear from us again? Reply with "unsubscribe" and you are off the list.'
  ].join('\n');
}

// ============================================================
// ONE-TIME SETUP HELPER
// ============================================================

/**
 * Run this once from the Apps Script editor to create the tab and header row.
 * Safe to re-run: it will not duplicate an existing tab.
 */
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

/**
 * Run this once after pasting ZIP_FILE_ID to confirm the attachment resolves
 * and the email renders, without going through the live form.
 */
function testDelivery() {
  sendBundle(FROM_ADDRESS);
  Logger.log('Test bundle sent to ' + FROM_ADDRESS);
}
