/**
 * HelpMeMarketing — Marketing Maturity Audit (backend Apps Script)
 *
 * Receives JSON POST from /tools/marketing-audit.html, validates spam protection,
 * appends a row to the "Marketing-Audit-Leads" sheet, and sends a confirmation
 * email with the visitor's tier-specific results.
 *
 * Separate from the contact-form Apps Script — different sheet, different
 * deployment, different lead qualification.
 *
 * V2.1 em-dash compliance: tier content embedded below has em-dashes purged
 * to match marketing-audit-content.js v1.0 (May 11, 2026). If you update the
 * audit content in the website JS file, sync the strings here.
 *
 * Deployment:
 *   1. Confirm the "audit_submissions" tab exists in the "Help Me Marketing
 *      Data" workbook (alongside main_submissions, rejected_submissions).
 *      Paste the 15-column header row from the CP4 spec into row 1.
 *   2. Open script.google.com -> New project -> name it "HMM Marketing Audit"
 *      (separate Apps Script from the existing contact-form project).
 *   3. Paste this entire file into Code.gs (overwriting the default content).
 *   4. SHEET_ID and SHEET_NAME are already wired below; verify they match
 *      your workbook and tab names.
 *   5. Save the project.
 *   6. Deploy -> New deployment -> type: Web app
 *      - Description: "Marketing Maturity Audit v1.0"
 *      - Execute as: Me (your Google account)
 *      - Who has access: Anyone (anonymous required for unauthenticated POST)
 *   7. Copy the /exec URL. Either share it back so we wire it into
 *      tools/marketing-audit.js, or run the one-line node replace yourself.
 *   8. On first run, authorize: MailApp, SpreadsheetApp.
 *
 * Multi-tab safety: rate-limit logic uses the audit_submissions tab only.
 * SpreadsheetApp.openById(SHEET_ID).getSheetByName(SHEET_NAME) scopes the
 * lookup so it never scans main_submissions or rejected_submissions rows.
 */

// ============================================================
// CONFIGURATION — fill these before deployment
// ============================================================

// Existing "Help Me Marketing Data" workbook — shared with contact-form leads
// but each Apps Script writes to its own tab. The audit writes to
// audit_submissions; the contact-form Apps Script writes to main_submissions
// and rejected_submissions. Rate limit (checkRateLimit below) reads
// getDataRange() on the scoped sheet only, so audit rate-limit checks are
// isolated from contact-form rows.
const SHEET_ID = '1RMYcfgl2DK4WvRNZFr1lu6_odGMwYX-EJBkZv-tSCds';
const SHEET_NAME = 'audit_submissions';

// Notification settings
const FROM_NAME = 'HelpMeMarketing';
const FROM_ADDRESS = 'Hello@helpmemarketing.com';   // must be an alias on your Google Workspace
const SITE_URL = 'https://helpmemarketing.com';
const CONTACT_URL = SITE_URL + '/contact';

// Rate limit: max submissions per email per rolling window
const RATE_LIMIT_MAX = 5;
const RATE_LIMIT_WINDOW_MS = 24 * 60 * 60 * 1000;  // 24 hours

// ============================================================
// MAIN ENTRY POINT
// ============================================================

function doPost(e) {
  try {
    const data = getRequestData(e);

    // Check 1: Honeypot (bot detection). Silent reject — no row, no email.
    if (data.company_url_secondary && String(data.company_url_secondary).trim().length > 0) {
      return jsonResponse({ status: 'success' });  // bot can't tell it failed
    }

    // Check 2: Email format (belt-and-braces; client already validates)
    const email = String(data.email || '').trim();
    if (!isValidEmail(email)) {
      return jsonResponse({ status: 'success' });  // silent
    }

    // Check 3: Tier sanity
    const tier = String(data.tier || '').trim();
    if (!CONTENT[tier]) {
      return jsonResponse({ status: 'success' });  // silent — malformed payload
    }

    // Check 4: Score sanity
    const scaledScore = parseInt(data.scaledScore, 10);
    if (Number.isNaN(scaledScore) || scaledScore < 0 || scaledScore > 100) {
      return jsonResponse({ status: 'success' });  // silent
    }

    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(SHEET_NAME);
    if (!sheet) {
      throw new Error('Sheet "' + SHEET_NAME + '" not found in spreadsheet ' + SHEET_ID);
    }

    // Check 5: Rate limit
    if (!checkRateLimit(email, sheet)) {
      return jsonResponse({ status: 'success' });  // silent — looks like success to repeat submitter
    }

    // Append row + send email
    appendRow(sheet, data);
    sendConfirmationEmail(data);

    return jsonResponse({ status: 'success' });
  } catch (err) {
    // Don't leak details. Return success so spam bots can't probe.
    // Log for our own visibility.
    console.error('doPost error: ' + err.toString());
    return jsonResponse({ status: 'success' });
  }
}

// ============================================================
// REQUEST PARSING
// ============================================================

function getRequestData(e) {
  // Primary: JSON in e.postData.contents (matches /contact.html and audit page pattern;
  // body is JSON.stringify(payload) with Content-Type: text/plain to avoid CORS preflight).
  if (e && e.postData && e.postData.contents) {
    try {
      return JSON.parse(e.postData.contents);
    } catch (err) {
      // fall through
    }
  }
  // Defensive fallback: form-urlencoded params
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
  if (values.length <= 1) return true;  // header row only
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

function appendRow(sheet, data) {
  const scores = data.scores || {};
  sheet.appendRow([
    new Date(),                                // 1. Timestamp
    String(data.email || ''),                  // 2. Email
    String(data.tierName || data.tier || ''),  // 3. Tier name
    parseInt(data.scaledScore, 10) || 0,       // 4. Scaled score (0-100)
    parseInt(data.rawScore, 10) || 0,          // 5. Raw score (0-80)
    parseInt(scores.q1, 10) || 0,              // 6. Q1
    parseInt(scores.q2, 10) || 0,              // 7. Q2
    parseInt(scores.q3, 10) || 0,              // 8. Q3
    parseInt(scores.q4, 10) || 0,              // 9. Q4
    parseInt(scores.q5, 10) || 0,              // 10. Q5
    parseInt(scores.q6, 10) || 0,              // 11. Q6 (Retention — signal dimension)
    parseInt(scores.q7, 10) || 0,              // 12. Q7
    parseInt(scores.q8, 10) || 0,              // 13. Q8
    String(data.userAgent || ''),              // 14. User agent
    String(data.referrer || '')                // 15. Referrer
  ]);
}

// ============================================================
// CONFIRMATION EMAIL
// ============================================================

function sendConfirmationEmail(data) {
  const tier = CONTENT[data.tier];
  if (!tier) return;

  const scaledScore = parseInt(data.scaledScore, 10) || 0;
  const subject = 'Your Marketing Maturity Audit results: ' + tier.name + ' (' + scaledScore + '/100)';
  const htmlBody = buildEmailHtml(tier, scaledScore);
  const textBody = buildEmailText(tier, scaledScore);

  MailApp.sendEmail({
    to: data.email,
    from: FROM_ADDRESS,
    name: FROM_NAME,
    replyTo: FROM_ADDRESS,
    subject: subject,
    htmlBody: htmlBody,
    body: textBody  // plain-text fallback for clients that strip HTML
  });
}

function buildEmailHtml(tier, scaledScore) {
  const headerFontFamily = 'Arial,Helvetica,sans-serif';
  const navy = '#0A1628';
  const gold = '#C9A96E';
  const ivory = '#FAF9F6';
  const border = '#E8E4DC';
  const text = '#1A1A1A';
  const muted = '#888';

  return (
'<!DOCTYPE html>' +
'<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">' +
'<title>Your Marketing Maturity Audit results</title>' +
'<style>@media only screen and (max-width:620px){.audit-content{padding:18px !important;}.audit-h2{font-size:15px !important;}}</style>' +
'</head><body style="margin:0;padding:0;background:' + ivory + ';font-family:' + headerFontFamily + ';">' +
'<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:' + ivory + ';"><tr><td align="center">' +
'<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="600" style="max-width:600px;background:#fff;border:0.5px solid ' + border + ';margin:24px auto;">' +
// Header
'<tr><td style="padding:22px 28px;background:' + navy + ';border-bottom:3px solid ' + gold + ';">' +
'<h1 style="margin:0;color:' + ivory + ';font-family:' + headerFontFamily + ';font-size:20px;font-weight:500;letter-spacing:-0.01em;">HelpMeMarketing</h1>' +
'</td></tr>' +
// Body content
'<tr><td class="audit-content" style="padding:32px 28px;color:' + text + ';font-family:' + headerFontFamily + ';font-size:15px;line-height:1.65;">' +
'<p style="margin:0 0 14px;">Hi there,</p>' +
'<p style="margin:0 0 22px;">Thanks for taking the Marketing Maturity Audit. Your results are below.</p>' +
// Tier badge
'<div style="display:inline-block;padding:12px 22px;background:' + gold + ';color:' + navy + ';border-radius:999px;font-weight:600;font-size:17px;letter-spacing:-0.01em;margin-bottom:24px;">' +
escapeHtml(tier.name) + ' &middot; ' + scaledScore + '/100' +
'</div>' +
// Where you are
'<h2 class="audit-h2" style="font-family:' + headerFontFamily + ';color:' + navy + ';font-size:16px;font-weight:600;margin:28px 0 10px;padding-bottom:6px;border-bottom:2px solid ' + gold + ';display:inline-block;">Where you are</h2>' +
'<div>' + tier.descriptionHTML + '</div>' +
// What to do
'<h2 class="audit-h2" style="font-family:' + headerFontFamily + ';color:' + navy + ';font-size:16px;font-weight:600;margin:32px 0 10px;padding-bottom:6px;border-bottom:2px solid ' + gold + ';display:inline-block;">What to do</h2>' +
'<div>' + tier.recommendationsHTML + '</div>' +
// What good help looks like
'<h2 class="audit-h2" style="font-family:' + headerFontFamily + ';color:' + navy + ';font-size:16px;font-weight:600;margin:32px 0 10px;padding-bottom:6px;border-bottom:2px solid ' + gold + ';display:inline-block;">What good help looks like</h2>' +
'<div>' + tier.serviceMappingHTML + '</div>' +
// A note from us
'<h2 class="audit-h2" style="font-family:' + headerFontFamily + ';color:' + navy + ';font-size:16px;font-weight:600;margin:36px 0 10px;padding-bottom:6px;border-bottom:2px solid ' + gold + ';display:inline-block;">A note from us</h2>' +
'<p style="margin:0 0 16px;">The audit is designed to be useful even if you never hire us. If anything here resonates and you want to talk about what an engagement would look like, the easiest next step is a 30-minute conversation. No pitch, no follow-up sequence.</p>' +
// CTA
'<p style="text-align:center;margin:28px 0 8px;">' +
'<a href="' + CONTACT_URL + '" style="display:inline-block;padding:14px 28px;background:' + navy + ';color:' + ivory + ';text-decoration:none;border-radius:8px;font-family:' + headerFontFamily + ';font-weight:500;font-size:15px;">Start a conversation</a>' +
'</p>' +
'</td></tr>' +
// Footer
'<tr><td style="padding:20px 28px;background:' + ivory + ';border-top:1px solid ' + border + ';font-family:' + headerFontFamily + ';font-size:12px;line-height:1.55;color:' + muted + ';">' +
'You are receiving this because you completed the Marketing Maturity Audit at helpmemarketing.com. We will not send you anything else unless you reach out.' +
'<br><br>' +
'<span style="color:' + text + ';font-weight:600;">Ankit Kumar</span><br>' +
'Founder, HelpMeMarketing<br>' +
'<a href="mailto:' + FROM_ADDRESS + '" style="color:' + navy + ';">' + FROM_ADDRESS + '</a>' +
'</td></tr>' +
'</table>' +
'</td></tr></table></body></html>'
  );
}

function buildEmailText(tier, scaledScore) {
  return (
    'Hi there,\n\n' +
    'Thanks for taking the Marketing Maturity Audit. Your results are below.\n\n' +
    '== ' + tier.name.toUpperCase() + ' / ' + scaledScore + ' of 100 ==\n\n' +
    'WHERE YOU ARE\n' +
    stripHtmlToText(tier.descriptionHTML) + '\n\n' +
    'WHAT TO DO\n' +
    stripHtmlToText(tier.recommendationsHTML) + '\n\n' +
    'WHAT GOOD HELP LOOKS LIKE\n' +
    stripHtmlToText(tier.serviceMappingHTML) + '\n\n' +
    'A NOTE FROM US\n' +
    'The audit is designed to be useful even if you never hire us. If anything here resonates and you want to talk about what an engagement would look like, the easiest next step is a 30-minute conversation. No pitch, no follow-up sequence.\n\n' +
    'START A CONVERSATION: ' + CONTACT_URL + '\n\n' +
    '-- \n' +
    'Ankit Kumar\n' +
    'Founder, HelpMeMarketing\n' +
    FROM_ADDRESS + '\n\n' +
    'You are receiving this because you completed the Marketing Maturity Audit at helpmemarketing.com. We will not send you anything else unless you reach out.'
  );
}

// ============================================================
// UTILITIES
// ============================================================

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// Naive HTML-to-text for the plain-text fallback. Good enough for our tier content shape.
function stripHtmlToText(html) {
  return String(html)
    .replace(/<\/h4[^>]*>/gi, '\n')
    .replace(/<h4[^>]*>/gi, '\n## ')
    .replace(/<\/p>/gi, '\n\n')
    .replace(/<p[^>]*>/gi, '')
    .replace(/<\/li>/gi, '')
    .replace(/<li[^>]*>/gi, '  - ')
    .replace(/<\/?(ol|ul|div|aside|section)[^>]*>/gi, '\n')
    .replace(/<br[^>]*>/gi, '\n')
    .replace(/<\/?(em|strong|span|a)[^>]*>/gi, '')
    .replace(/<[^>]+>/g, '')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, ' ')
    .replace(/[ \t]+/g, ' ')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

// ============================================================
// TIER CONTENT
// ============================================================
// Verbatim copy of marketing-audit-content.js v1.0 (May 11, 2026)
// with V2.1 em-dash purge applied. Keep in sync when content updates.
// ============================================================

const CONTENT = {
  foundational: {
    name: 'Foundational',
    range: '0-30',
    descriptionHTML:
      '<p style="margin:0 0 14px;"><strong>You are running marketing on intuition, not infrastructure. Most of what is happening is reactive.</strong></p>' +
      '<p style="padding:14px 18px;border-left:3px solid #C9A96E;background:rgba(201,169,110,0.08);font-style:italic;font-family:Georgia,serif;color:#0A1628;margin:0 0 18px;">Leads come in some months and not others, and you are not sure why. You spend on ads when business is slow and pull back when it is busy. You haven&#39;t really written down who your customer is. You&#39;d know them when you see them.</p>' +
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:18px 0 8px;">What is typical at this tier</h4>' +
      '<p style="margin:0 0 14px;">Most businesses we see start here, and most stay longer than they should. There is usually one channel that is quietly working (referrals, one ad campaign, an old SEO win) and a lot of guessing around it. Spend is reactive. Attribution is "how did you hear about us?" if it exists at all. The business is running, but the marketing isn&#39;t a system. It is a series of decisions made under pressure.</p>' +
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:18px 0 8px;">The biggest gap</h4>' +
      '<p style="margin:0 0 14px;">You don&#39;t have a written ICP, a defined funnel, or measurement that drives decisions. Until those three exist, every channel will underperform because there is no way to tell what is working.</p>' +
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:18px 0 8px;">What success looks like</h4>' +
      '<p style="margin:0 0 14px;">Moving to Growing isn&#39;t about more spend or more channels. It is about getting one channel working well enough that you can measure it, learn from it, and decide what to do next.</p>',
    recommendationsHTML:
      '<h4 style="font-size:11px;text-transform:uppercase;letter-spacing:1.2px;color:#C9A96E;margin:0 0 10px;">If you do nothing else</h4>' +
      '<div style="background:#FAF9F6;border-left:3px solid #C9A96E;padding:16px 20px;margin:0 0 22px;">' +
        '<p style="margin:0 0 10px;"><strong>Write a 1-page ICP doc this week.</strong> Four sections: who they are (industry, role, business stage), what triggers them to look for what you sell, what they buy instead today, and where they spend time online. One page. No template, no consultant. Just write it from your last five customers. This unlocks every other marketing decision you will make for the next year. Without it, channel selection, ad copy, and landing pages are all guesswork.</p>' +
        '<p style="margin:0;font-size:13px;color:#888;font-style:italic;">Timeline: 2-3 hours of focused work this week.</p>' +
      '</div>' +
      '<h4 style="font-size:11px;text-transform:uppercase;letter-spacing:1.2px;color:#C9A96E;margin:22px 0 10px;">The 3 supporting actions</h4>' +
      '<p style="margin:0 0 8px;"><strong>1. Pick one channel and commit for 90 days.</strong> Stop testing. Stop adding. Pick the channel where you have evidence your customers actually are (your existing customers; ask them). Run it consistently for 90 days. You can&#39;t diagnose what is working when you change the inputs every week.</p>' +
      '<p style="margin:0 0 14px;font-size:13px;color:#888;font-style:italic;">Why it matters: Foundational businesses lose more to channel-switching than to running the wrong channel. 90 days is the minimum window to learn anything real.</p>' +
      '<p style="margin:0 0 8px;"><strong>2. Send paid traffic to a dedicated landing page, not your homepage.</strong> If you are running any paid ads, build one landing page for the campaign. Doesn&#39;t have to be fancy. Carrd, Webflow, or even a single page on your existing site works. One headline that matches the ad, three benefits, social proof, one form. Sending paid traffic to a homepage is the most expensive mistake at this tier.</p>' +
      '<p style="margin:0 0 14px;font-size:13px;color:#888;font-style:italic;">Why it matters: Homepages are designed for branded traffic that already knows you. Paid traffic doesn&#39;t. The conversion gap is usually 3-5x.</p>' +
      '<p style="margin:0 0 8px;"><strong>3. Set up GA4 properly and check it weekly, even briefly.</strong> If you don&#39;t have GA4, install it this week. If you have it but never look at it, set a recurring 15-minute weekly check on your calendar. You are not doing analysis. You are building the muscle of <em>looking</em>. The infrastructure is free; the habit is what is missing.</p>' +
      '<p style="margin:0 0 14px;font-size:13px;color:#888;font-style:italic;">Why it matters: Every higher tier requires data fluency. You can&#39;t build that muscle later. You build it now by looking, even when you don&#39;t fully understand what you are seeing.</p>',
    serviceMappingHTML:
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:0 0 10px;">What good help looks like at this tier</h4>' +
      '<p style="margin:0 0 14px;"><strong>Recommended service: Performance Marketing.</strong> Single channel, 90-day engagement.</p>' +
      '<p style="margin:0 0 14px;">At Foundational tier, the highest-leverage outside help is getting <em>one paid channel</em> set up and run properly while you build the operational muscles. Not a multi-channel program. Not a brand overhaul. One channel, usually Google Search or Meta, with the goals, tracking, and reporting cadence done right from day one.</p>' +
      '<p style="margin:0 0 14px;"><strong>Engagement shape:</strong> 90-day initial sprint focused on a single channel. Strategy + setup + the first 60 days of active management. After 90 days, you decide whether to extend, switch the engagement model, or take it in-house.</p>' +
      '<p style="margin:0 0 6px;"><strong>Why this scope at this tier:</strong></p>' +
      '<ul style="margin:0 0 16px;padding-left:22px;">' +
        '<li style="margin-bottom:6px;">A Foundational business doesn&#39;t need ten things done. It needs one thing done well enough to learn from. Trying to do more usually means doing nothing well.</li>' +
        '<li style="margin-bottom:6px;">90 days is the minimum window to learn anything real from a paid channel. Shorter engagements end before the data is interpretable.</li>' +
        '<li style="margin-bottom:6px;">Single-channel focus means clean attribution. When everything is running through one channel, "what is working" is answerable.</li>' +
      '</ul>' +
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:18px 0 8px;">In-house vs. partner: the honest contrast</h4>' +
      '<p style="margin:0 0 12px;"><strong>In-house works if you have:</strong> A team member with real paid acquisition experience (not "they ran some Facebook ads once", actual time managing budgets and reading data), and at least 8-10 hours/week to dedicate to the channel.</p>' +
      '<p style="margin:0 0 14px;"><strong>Partner works if you have:</strong> Budget for the channel but no internal expertise, no time to learn while running the business, or you have tried in-house and hit a ceiling you can&#39;t get past. Most Foundational businesses we work with are in this second category. They have the customer demand and the marketing budget but lack the operational time to build the function.</p>' +
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:18px 0 8px;">What to avoid at this tier</h4>' +
      '<p style="margin:0 0 14px;"><strong>Don&#39;t hire multiple specialists at once.</strong> A common Foundational mistake is hiring an SEO agency, a paid ads agency, and a content writer simultaneously, because everyone needs everything. Three uncoordinated engagements at this tier produce three half-finished programs, none of which generate enough signal to learn from. Pick one channel, get it right, then expand.</p>' +
      '<p style="margin:0 0 14px;"><strong>Don&#39;t commit to long contracts.</strong> 12-month retainers at Foundational tier are a red flag. The agency benefits from the lock-in; you benefit from being able to walk away after 90 days if it isn&#39;t working. Insist on shorter terms or month-to-month after the initial sprint.</p>'
  },

  growing: {
    name: 'Growing',
    range: '31-55',
    descriptionHTML:
      '<p style="margin:0 0 14px;"><strong>You have built some marketing infrastructure, but it is working in pieces, not as a system.</strong></p>' +
      '<p style="padding:14px 18px;border-left:3px solid #C9A96E;background:rgba(201,169,110,0.08);font-style:italic;font-family:Georgia,serif;color:#0A1628;margin:0 0 18px;">You have a written ICP, you are running on a couple of channels, and you check GA4 about once a month. You can roughly tell which channel works best, but when you try to explain why, the answer gets fuzzy. You know you should test more, measure more, follow up more. There is just never time.</p>' +
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:18px 0 8px;">What is typical at this tier</h4>' +
      '<p style="margin:0 0 14px;">This is where most businesses with real marketing budgets land. There is a contact form, a basic email sequence, ads running on at least one platform. The pieces exist. What is missing is the connective tissue. The funnel isn&#39;t measured stage-by-stage, attribution stops at the channel level, and decisions still happen on instinct as often as on data. The business is past winging it, but not yet running a marketing operation.</p>' +
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:18px 0 8px;">The biggest gap</h4>' +
      '<p style="margin:0 0 14px;">You are collecting data you don&#39;t act on. The infrastructure exists; the operating cadence doesn&#39;t. Until weekly review with real adjustments becomes routine, the next tier stays out of reach.</p>' +
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:18px 0 8px;">What success looks like</h4>' +
      '<p style="margin:0 0 14px;">Moving to Scaling isn&#39;t about adding more channels or tools. It is about making the channels you already have measurable enough that you can confidently say which one to double down on, and which to cut.</p>',
    recommendationsHTML:
      '<h4 style="font-size:11px;text-transform:uppercase;letter-spacing:1.2px;color:#C9A96E;margin:0 0 10px;">If you do nothing else</h4>' +
      '<div style="background:#FAF9F6;border-left:3px solid #C9A96E;padding:16px 20px;margin:0 0 22px;">' +
        '<p style="margin:0 0 10px;"><strong>Install a weekly marketing review and never skip it.</strong> 60 minutes, same time every week, with one rule: every metric you look at has to produce a decision. Not "let&#39;s keep an eye on it"; an actual change to spend, creative, targeting, or process. If a metric never drives a decision in 8 weeks, remove it from the review. The infrastructure you have built doesn&#39;t compound until you build the cadence to act on it. This is the muscle that separates Growing from Scaling, and it costs nothing but discipline.</p>' +
        '<p style="margin:0;font-size:13px;color:#888;font-style:italic;">Timeline: First review scheduled this week. The muscle takes 90 days to feel natural.</p>' +
      '</div>' +
      '<h4 style="font-size:11px;text-transform:uppercase;letter-spacing:1.2px;color:#C9A96E;margin:22px 0 10px;">The 3 supporting actions</h4>' +
      '<p style="margin:0 0 8px;"><strong>1. Tag every campaign with UTMs and audit your attribution gaps.</strong> Use Google&#39;s free Campaign URL Builder. Every paid campaign, every email, every social post that drives traffic: UTM tagged at the source. Then spend one hour in GA4 looking at where "(direct)" or "unassigned" traffic is coming from. That is your attribution gap, and it is almost always bigger than you think. You can&#39;t act on what you can&#39;t see.</p>' +
      '<p style="margin:0 0 14px;font-size:13px;color:#888;font-style:italic;">Why it matters: At Growing tier, your channel-level attribution is probably 70-80% accurate. The missing 20-30% is where over- or under-spending decisions hide.</p>' +
      '<p style="margin:0 0 8px;"><strong>2. Build a basic conversion funnel and find your weakest stage.</strong> Map the actual stages: ad impression &rarr; click &rarr; landing page &rarr; form &rarr; qualified lead &rarr; customer. Get a real number on each stage&#39;s conversion rate. Most Growing businesses have one stage that is 3-5x worse than the others. That is the bottleneck, not the channel. Fix the bottleneck before adding spend or testing new channels.</p>' +
      '<p style="margin:0 0 14px;font-size:13px;color:#888;font-style:italic;">Why it matters: Growing businesses spend on what is easiest to measure (top of funnel) instead of what is broken (middle of funnel). The bottleneck is usually a landing page or a form.</p>' +
      '<p style="margin:0 0 8px;"><strong>3. Pick one experiment per month and run it through completion.</strong> Not three experiments in parallel. One, run to statistical sufficiency or 4 weeks, whichever comes first. Document what you tested, what changed, what you learned. The experimentation muscle is what compounds; the individual experiment results matter less than building the habit of testing systematically.</p>' +
      '<p style="margin:0 0 14px;font-size:13px;color:#888;font-style:italic;">Why it matters: Growing businesses test sporadically and learn nothing because they never let an experiment run long enough or document what happened.</p>',
    serviceMappingHTML:
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:0 0 10px;">What good help looks like at this tier</h4>' +
      '<p style="margin:0 0 14px;"><strong>Recommended services: Performance Marketing + Analytics/Attribution.</strong> Typically running in parallel.</p>' +
      '<p style="margin:0 0 14px;">At Growing tier, the gap isn&#39;t "we don&#39;t have marketing"; it is "we have marketing but it&#39;s not measurable enough to act on." The two services that address this directly are paid channel management (the inputs) and the analytics layer that makes spend decisions defensible (the visibility). Most Growing engagements at HMM run both in parallel because separating them at this tier leads to the same gap that brought the business to the audit: channels running without enough measurement to optimize them.</p>' +
      '<p style="margin:0 0 14px;"><strong>Engagement shape (Performance Marketing):</strong> 90-day initial sprint expanding to ongoing management. At Growing, scope often includes 2-3 channels (not just one) because the business has signal across multiple platforms already. Monthly review cadence with quarterly strategic resets.</p>' +
      '<p style="margin:0 0 14px;"><strong>Engagement shape (Analytics/Attribution):</strong> Project-based initial setup (4-6 weeks), then a lighter monthly retainer for dashboard maintenance and quarterly attribution audits. UTM hygiene, GA4 configuration, cross-platform reconciliation, and a single source-of-truth dashboard.</p>' +
      '<p style="margin:0 0 6px;"><strong>Why this pairing at this tier:</strong></p>' +
      '<ul style="margin:0 0 16px;padding-left:22px;">' +
        '<li style="margin-bottom:6px;">Running paid acquisition without proper attribution at Growing tier is the most common cause of plateau. Every Growing business we have worked with has had measurement gaps wider than they realized.</li>' +
        '<li style="margin-bottom:6px;">Project-based analytics setup with lighter ongoing retainer keeps cost realistic. Analytics work compounds: you build the foundation once and maintain it cheaply.</li>' +
        '<li style="margin-bottom:6px;">The two services compound. Better attribution drives smarter paid spend; smarter paid spend produces cleaner data to attribute.</li>' +
      '</ul>' +
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:18px 0 8px;">In-house vs. partner: the honest contrast</h4>' +
      '<p style="margin:0 0 12px;"><strong>In-house works if you have:</strong> A marketing lead with 2-3 years of paid acquisition experience, a designated analyst (full or part-time) who actually opens GA4 weekly, and at least 15-20 hours/week of combined team time on marketing operations.</p>' +
      '<p style="margin:0 0 14px;"><strong>Partner works if you have:</strong> A marketing budget growing faster than your ability to hire senior talent, or a generalist marketing lead who is strong on strategy but doesn&#39;t have the analytics depth to build the measurement layer. The most common Growing-tier engagement we run is "your marketing lead + our analytics + our paid management" as a hybrid model. The internal lead keeps strategic ownership; we handle the operational depth.</p>' +
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:18px 0 8px;">What to avoid at this tier</h4>' +
      '<p style="margin:0 0 14px;"><strong>Don&#39;t hire three specialists who don&#39;t talk to each other.</strong> A Growing business with a paid ads agency, an SEO agency, and an email vendor running independently produces uncoordinated work and conflicting attribution claims. If you work with multiple partners, they need a coordination layer: either a senior internal marketing lead, or a single accountable partner that runs the program holistically.</p>' +
      '<p style="margin:0 0 14px;"><strong>Don&#39;t ignore retention because no one is selling you a retention service.</strong> Most agencies (including ours, currently) lead with acquisition because that is where the obvious budget is. But at Growing tier, you have enough customer volume that retention math starts mattering. Build a basic lifecycle program in-house: welcome sequence, win-back, basic segmentation. It doesn&#39;t need an agency yet; it needs an owner. Most growing businesses can run a 3x improvement in retention value with one focused team member and Klaviyo or HubSpot. This is the work that compounds quietly while acquisition gets all the attention.</p>'
  },

  scaling: {
    name: 'Scaling',
    range: '56-80',
    // Body matches marketing-audit-content.js (em-dashes purged, inline-styled for email)
    descriptionHTML:
      '<p style="margin:0 0 14px;"><strong>You are running a measurable marketing operation. The question now is which parts to scale and which to rebuild.</strong></p>' +
      '<p style="padding:14px 18px;border-left:3px solid #C9A96E;background:rgba(201,169,110,0.08);font-style:italic;font-family:Georgia,serif;color:#0A1628;margin:0 0 18px;">You know your CAC by channel. UTM tags are on every campaign. Someone reviews performance weekly and changes get made. You have started running A/B tests, but only on the things that are easy to test. The ceiling you are hitting isn&#39;t a budget problem or a channel problem. It is that the next level of growth needs different muscles than the ones that got you here.</p>' +
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:18px 0 8px;">What is typical at this tier</h4>' +
      '<p style="margin:0 0 14px;">Businesses at Scaling have figured out attribution at the channel level, built landing pages that convert, and run paid acquisition with discipline. The funnel is measured, the dashboards exist, the operating cadence is real. What is missing isn&#39;t infrastructure. It is experimentation muscle and cross-channel integration. Most businesses at this tier are running parallel programs that don&#39;t talk to each other: paid ads optimizing for last-click, SEO building authority, email sending offers. Each works. Together, they don&#39;t compound.</p>' +
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:18px 0 8px;">The biggest gap</h4>' +
      '<p style="margin:0 0 14px;">You are optimizing within channels but not across them. The next tier requires treating the marketing program as one system, not five, and running real experiments on the parts that matter, not the parts that are easy to measure.</p>' +
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:18px 0 8px;">What success looks like</h4>' +
      '<p style="margin:0 0 14px;">Moving to Advanced isn&#39;t about more sophistication. It is about integration: making channels reinforce each other, attribution see across them, and decisions weigh the whole system instead of one platform&#39;s report.</p>',
    recommendationsHTML:
      '<h4 style="font-size:11px;text-transform:uppercase;letter-spacing:1.2px;color:#C9A96E;margin:0 0 10px;">If you do nothing else</h4>' +
      '<div style="background:#FAF9F6;border-left:3px solid #C9A96E;padding:16px 20px;margin:0 0 22px;">' +
        '<p style="margin:0 0 10px;"><strong>Run a cross-channel attribution audit and name what you are double-counting.</strong> Pull the last 90 days of conversion data from each platform: Google Ads, Meta, GA4, your CRM. Add up the "conversions attributed to me" claims from each platform. The total is almost always 20-40% higher than your actual customer count. That is the double-counting problem. Sit down with your team and name which channels are getting credit they don&#39;t deserve, and which assist channels are getting none. Until you can see the system, you can&#39;t optimize the system.</p>' +
        '<p style="margin:0;font-size:13px;color:#888;font-style:italic;">Timeline: 1 week to pull and reconcile. The conversation it triggers takes longer, but it has to happen.</p>' +
      '</div>' +
      '<h4 style="font-size:11px;text-transform:uppercase;letter-spacing:1.2px;color:#C9A96E;margin:22px 0 10px;">The 3 supporting actions</h4>' +
      '<p style="margin:0 0 8px;"><strong>1. Build a single source of truth dashboard outside any one ad platform.</strong> GA4 alone isn&#39;t enough. Looker Studio (free) or a paid tool like Funnel.io or Whatagraph. Pick one, build a dashboard that reports on the <em>business</em> not the <em>platforms</em>. Customer acquisition cost, lifetime value, revenue by channel, blended ROAS. The dashboard should answer "what should we do this week?" not "what did Google Ads say happened last week?" Most Scaling businesses have 5+ dashboards that contradict each other. One source of truth is non-negotiable.</p>' +
      '<p style="margin:0 0 14px;font-size:13px;color:#888;font-style:italic;">Why it matters: Cross-channel decisions require cross-channel data. As long as the highest-fidelity dashboard lives inside a single ad platform, you will keep over-investing in that platform.</p>' +
      '<p style="margin:0 0 8px;"><strong>2. Stop optimizing within channels and start optimizing across them.</strong> The Scaling failure pattern is paid teams optimizing CPL, SEO teams optimizing rankings, email teams optimizing open rates: none of them talking, all of them claiming credit. Pick one cross-channel motion to test this quarter: a retargeting program that uses email engagement to filter Meta audiences, an SEO content piece that powers a paid landing page, an email re-engagement campaign that follows up paid-ads non-converters. The point isn&#39;t the specific tactic. It is building the habit of asking "how do these channels reinforce each other?"</p>' +
      '<p style="margin:0 0 14px;font-size:13px;color:#888;font-style:italic;">Why it matters: Within-channel optimization has diminishing returns at Scaling. Cross-channel multiplication is where the next 30-50% of efficiency lives.</p>' +
      '<p style="margin:0 0 8px;"><strong>3. Run a quarterly portfolio review on your full marketing mix.</strong> Once a quarter, sit with the question: "If I had to cut 20% of marketing spend tomorrow, what would go and why?" The answer should be defensible without referring to platform reports. The exercise forces clarity on which programs are doing the work and which are running because no one has questioned them. Most Scaling businesses have 1-2 zombie programs eating budget without contributing. The portfolio review surfaces them.</p>' +
      '<p style="margin:0 0 14px;font-size:13px;color:#888;font-style:italic;">Why it matters: At Scaling, the constraint shifts from "are we spending enough?" to "is every dollar earning its place?" The portfolio review is how you maintain spend discipline as the operation grows.</p>',
    serviceMappingHTML:
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:0 0 10px;">What good help looks like at this tier</h4>' +
      '<p style="margin:0 0 14px;"><strong>Recommended services: Performance Marketing + Analytics/Attribution + Custom Dashboards.</strong> Typically running as an integrated program.</p>' +
      '<p style="margin:0 0 14px;">At Scaling tier, the engagement model shifts from "we do this for you" to "we run this layer of your marketing operation." The three services above aren&#39;t a bundle. They are the operational stack that makes cross-channel decisions possible. Most Scaling engagements at HMM run all three because the gaps that brought a Scaling business to the audit (cross-channel attribution, parallel programs that don&#39;t compound, dashboards that contradict each other) require integrated work, not separate engagements.</p>' +
      '<p style="margin:0 0 14px;"><strong>Engagement shape (Performance Marketing):</strong> Ongoing channel management across 3-5 platforms (Google, Meta, LinkedIn, programmatic, etc.). Weekly optimization, monthly strategic reviews, quarterly portfolio resets. At Scaling, the deliverable isn&#39;t "ads running". It is "spend allocation defended with cross-channel data."</p>' +
      '<p style="margin:0 0 14px;"><strong>Engagement shape (Analytics/Attribution):</strong> Continuous attribution work, not project-based. UTM governance, cross-platform reconciliation, regular audits of where attribution is breaking, and infrastructure work to close the gaps. This is the layer that makes the rest of the program defensible.</p>' +
      '<p style="margin:0 0 14px;"><strong>Engagement shape (Custom Dashboards):</strong> Initial build (6-8 weeks for a real Scaling-tier dashboard), then ongoing iteration as the business evolves. Looker Studio for most, paid platforms (Funnel.io, Looker, Tableau) when the data volume or stakeholder count justifies it. The dashboard is the single source of truth: not a reporting deliverable, but the decision-making infrastructure.</p>' +
      '<p style="margin:0 0 6px;"><strong>Why this stack at this tier:</strong></p>' +
      '<ul style="margin:0 0 16px;padding-left:22px;">' +
        '<li style="margin-bottom:6px;">Cross-channel optimization is impossible without all three layers working together.</li>' +
        '<li style="margin-bottom:6px;">An integrated provider running all three eliminates the "whose data is right?" problem.</li>' +
        '<li style="margin-bottom:6px;">The three services share strategic context. Decisions in one inform the others in real time.</li>' +
      '</ul>' +
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:18px 0 8px;">In-house vs. partner: the honest contrast</h4>' +
      '<p style="margin:0 0 12px;"><strong>In-house works if you have:</strong> A senior marketing leader (VP-level or strong director) who owns strategy, plus dedicated specialists for at least two of the three layers, plus 30+ hours/week of combined team time on marketing operations. At Scaling, in-house is genuinely viable, but it usually requires more senior talent than businesses realize.</p>' +
      '<p style="margin:0 0 14px;"><strong>Partner works if you have:</strong> Senior strategic ownership internally but operational depth gaps in one or more layers, or you have outgrown the "one agency per channel" model and need integration. The most common Scaling engagement at HMM is a partnership with an internal marketing leader who treats us as their operations and measurement team.</p>' +
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:18px 0 8px;">What to avoid at this tier</h4>' +
      '<p style="margin:0 0 14px;"><strong>Don&#39;t hire a specialist agency per channel without an integration layer.</strong> The Scaling failure pattern is one agency for Google, one for Meta, one for SEO, one for email: all running independently, all claiming credit for the same customers, all reporting in their own format.</p>' +
      '<p style="margin:0 0 14px;"><strong>Don&#39;t outsource the dashboard layer to whichever agency you happen to like best.</strong> The dashboard is the decision-making infrastructure for the entire program. It shouldn&#39;t live inside a channel agency&#39;s reporting tool.</p>' +
      '<p style="margin:0 0 14px;"><strong>Don&#39;t ignore retention yet again.</strong> At Scaling tier, retention isn&#39;t optional. The unit economics depend on it. We still don&#39;t currently offer a dedicated lifecycle service, but at Scaling the gap is bigger because the math matters more.</p>'
  },

  advanced: {
    name: 'Advanced',
    range: '81-100',
    descriptionHTML:
      '<p style="margin:0 0 14px;"><strong>You have built an integrated marketing program. The work now is compounding it, not adding to it.</strong></p>' +
      '<p style="padding:14px 18px;border-left:3px solid #C9A96E;background:rgba(201,169,110,0.08);font-style:italic;font-family:Georgia,serif;color:#0A1628;margin:0 0 18px;">You can answer where any customer came from, what they did before buying, and how the channels worked together to get them there. Your team runs experiments on the things that move revenue, not the things that are easy to test. You have stopped adding tools and started removing them. The questions you are trying to answer now aren&#39;t "is marketing working". They are "where is the next 20% coming from."</p>' +
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:18px 0 8px;">What is typical at this tier</h4>' +
      '<p style="margin:0 0 14px;">Businesses at Advanced are rare. Marketing operates as a system: paid acquisition, organic, lifecycle, and brand reinforce each other; attribution sees across channels; the operating cadence is tight enough that decisions happen in days, not quarters. The team is past collecting data and past acting on it. They are now compounding it. What separates Advanced from "very good" is that the program isn&#39;t just measured, it is predictive. You can model what a budget shift will do before you make it.</p>' +
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:18px 0 8px;">The biggest gap</h4>' +
      '<p style="margin:0 0 14px;">The frontier at this tier isn&#39;t infrastructure or discipline. It is category position. The next ceiling is brand pull: turning marketing efficiency into market leadership, where customers find you before they search.</p>' +
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:18px 0 8px;">What success looks like</h4>' +
      '<p style="margin:0 0 14px;">There is no clean tier above 81-100 in this audit, but there is a real one in the market. It is the businesses that don&#39;t just acquire customers efficiently. They are the default choice in their category before anyone clicks an ad.</p>',
    recommendationsHTML:
      '<h4 style="font-size:11px;text-transform:uppercase;letter-spacing:1.2px;color:#C9A96E;margin:0 0 10px;">If you do nothing else</h4>' +
      '<div style="background:#FAF9F6;border-left:3px solid #C9A96E;padding:16px 20px;margin:0 0 22px;">' +
        '<p style="margin:0 0 10px;"><strong>Build a 12-month brand investment plan separate from your performance marketing budget.</strong> Performance marketing has plateaued for you by definition; you have optimized it. The next 20% of growth lives in brand pull: customers arriving with intent because they already know you, not because they clicked an ad. Allocate 15-25% of total marketing spend to brand work that won&#39;t show up in last-click attribution: thought leadership, category-defining content, podcast and partnership presence, owned audience growth. Measure it by branded search volume and direct traffic, not by ROAS. Most Advanced businesses won&#39;t do this because the discomfort of un-attributable spend is real. The ones who do, compound past their competition.</p>' +
        '<p style="margin:0;font-size:13px;color:#888;font-style:italic;">Timeline: Plan built this quarter. Investment runs 12 months minimum before signal appears.</p>' +
      '</div>' +
      '<h4 style="font-size:11px;text-transform:uppercase;letter-spacing:1.2px;color:#C9A96E;margin:22px 0 10px;">The 3 supporting actions</h4>' +
      '<p style="margin:0 0 8px;"><strong>1. Move from descriptive measurement to predictive modeling.</strong> Your dashboards tell you what happened. The next layer tells you what will happen. Build a media mix model (or buy one: Recast, Mixpanel, or in-house with a data scientist) that lets you simulate budget shifts before you make them.</p>' +
      '<p style="margin:0 0 14px;font-size:13px;color:#888;font-style:italic;">Why it matters: Advanced operations make budget decisions weekly. The ones who simulate first outperform the ones who learn through doing.</p>' +
      '<p style="margin:0 0 8px;"><strong>2. Audit your stack and remove what isn&#39;t compounding.</strong> Advanced marketing operations accumulate tools: every ICP iteration added a platform, every team change brought new preferences. Most Advanced stacks can lose 20-30% of their tools with no impact on results. The signal of operational maturity at this tier isn&#39;t what you add. It is what you remove.</p>' +
      '<p style="margin:0 0 14px;font-size:13px;color:#888;font-style:italic;">Why it matters: Tool sprawl is the silent tax on Advanced operations.</p>' +
      '<p style="margin:0 0 8px;"><strong>3. Invest in the team layer, not the tool layer.</strong> At Advanced, the binding constraint is rarely budget or technology. It is the depth and seniority of the people running the program. Hire one strategist-level marketer who can think about the whole system, not three coordinators who can execute pieces of it.</p>' +
      '<p style="margin:0 0 14px;font-size:13px;color:#888;font-style:italic;">Why it matters: Tools and tactics commoditize. Strategic judgment doesn&#39;t.</p>',
    serviceMappingHTML:
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:0 0 10px;">What good help looks like at this tier</h4>' +
      '<p style="margin:0 0 14px;"><strong>Recommended services: selective engagement across Custom Dashboards + Analytics/Attribution + Custom Apps.</strong> Typically as specialized capability supplements, not full-function partnership.</p>' +
      '<p style="margin:0 0 14px;">At Advanced tier, the engagement model shifts again, from "we run this layer of your operation" to "we build specific things your internal team needs but doesn&#39;t have capacity or specialized depth for." Most Advanced engagements at HMM aren&#39;t comprehensive program management. They are project-shaped: purpose-built dashboards for specific business questions, attribution infrastructure rebuilds, internal marketing tools or custom apps that off-the-shelf platforms don&#39;t cover.</p>' +
      '<p style="margin:0 0 14px;"><strong>Engagement shape (Custom Dashboards):</strong> Project-based builds for specific decision-making needs. Typically 4-8 week builds with ongoing iteration as the business evolves.</p>' +
      '<p style="margin:0 0 14px;"><strong>Engagement shape (Analytics/Attribution):</strong> Specialized work: server-side tracking implementation, MMM builds, attribution rebuilds when platform changes break existing infrastructure. Project-based with retainer support.</p>' +
      '<p style="margin:0 0 14px;"><strong>Engagement shape (Custom Apps):</strong> Internal tools that bridge gaps between platforms. 6-12 week build cycles. This is the service Advanced businesses underuse because they don&#39;t realize it is an option.</p>' +
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:18px 0 8px;">In-house vs. partner: the honest contrast</h4>' +
      '<p style="margin:0 0 12px;"><strong>In-house works if you have:</strong> A marketing operations function with dedicated engineering, data, and analytics resources, plus the senior strategic leadership to direct them. At Advanced, in-house is the default.</p>' +
      '<p style="margin:0 0 14px;"><strong>Partner works if you have:</strong> Specific capability gaps that internal hiring can&#39;t close fast enough, or one-off builds that don&#39;t justify dedicated headcount. The most common Advanced engagement at HMM is "internal team owns the program; we deliver specialized infrastructure projects on cycle."</p>' +
      '<h4 style="font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#0A1628;margin:18px 0 8px;">What the audit doesn&#39;t address well at this tier</h4>' +
      '<p style="margin:0 0 14px;"><strong>Category position and brand pull.</strong> The primary recommendation above is the right strategic move, but it is not an audit-shaped problem and it is not a HMM service. Hire a brand strategist or a category-design consultant.</p>' +
      '<p style="margin:0 0 14px;"><strong>Retention and lifecycle infrastructure.</strong> Same admission as Growing and Scaling: HMM doesn&#39;t currently offer dedicated lifecycle services. At Advanced, this is the most acute gap in our service map: your unit economics depend on it, your CAC is climbing.</p>' +
      '<p style="margin:0 0 14px;"><strong>AI and automation infrastructure.</strong> Marketing AI tooling is changing faster than any agency can stay current. HMM can build specific custom apps but we are not your AI strategy partner.</p>'
  }
};
