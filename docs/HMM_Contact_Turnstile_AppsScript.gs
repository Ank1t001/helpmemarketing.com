/**
 * Cloudflare Turnstile check for the /contact form's Apps Script (added 2026-09-28).
 *
 * The contact form's own Apps Script is not in this repo, so this file is the piece to paste
 * into it. It adds one check at the top of doPost: a submission whose Turnstile token does not
 * verify is written to a "Spam" tab instead of the main tab. Nothing is ever discarded, so a
 * real person Turnstile got wrong can still be found and answered.
 *
 * The browser side is already on the page (contact.html). It is switched on by putting the
 * public site key in the form's data-turnstile-sitekey attribute. While that attribute is empty
 * the page sends no token and behaves exactly as before.
 *
 * SET-UP, IN THIS ORDER (the order matters):
 *
 *   1. Cloudflare dashboard > Turnstile > Add widget.
 *      Name: HMM contact. Hostname: helpmemarketing.com. Widget mode: Managed.
 *      Pre-clearance: No. Copy the Site Key and the Secret Key.
 *
 *   2. Put the SITE key live on the page first (data-turnstile-sitekey on the contact form).
 *      The site key is public; it is safe in the page and in chat. From this moment the form
 *      sends a token with every lead. Your sheet script ignores it until step 4.
 *      The marketing audit's "help applying this" form (#ma-cform in tools/marketing-audit.html,
 *      added 2026-09-29) posts to this same script, so put the same site key on it too, or its
 *      leads will land on the Spam tab once step 4 is done.
 *
 *   3. Paste everything below the line into the contact form's Apps Script, and add the three
 *      marked lines to the very top of its existing doPost (shown at the bottom of this file).
 *      Pasting the code changes nothing yet: the check only runs once the secret exists.
 *
 *   4. Apps Script > Project Settings > Script properties > Add script property:
 *        Property: TURNSTILE_SECRET    Value: the Secret Key from step 1
 *      Never put the secret in the page, the repo or a chat.
 *
 *   5. Deploy > Manage deployments > edit (pencil) the EXISTING deployment > Version: New version
 *      > Deploy. Editing keeps the same /exec URL. "New deployment" would create a different URL
 *      and the form would keep posting to the old code.
 *
 *   6. Send one real test from your phone. It should land on the main tab, not on Spam.
 *
 * If step 4 happens before step 2, every lead has no token and lands on the Spam tab until the
 * site key is live. Nothing is lost, but the main tab goes quiet.
 *
 * If your existing script builds its columns from every parameter it receives, add
 * 'cf-turnstile-response' to whatever it skips, or a token column will appear in the main tab.
 */

// ---------------------------------------------------------------------------------------------

const TURNSTILE_ACTION = 'contact';          // matches action:'contact' in contact.html
const TURNSTILE_ALLOWED_HOSTS = ['helpmemarketing.com', 'www.helpmemarketing.com'];
const CONTACT_SPAM_TAB = 'Spam';

/** True when the submission may go to the main tab. */
function contactPassesTurnstile_(p) {
  const secret = PropertiesService.getScriptProperties().getProperty('TURNSTILE_SECRET');
  if (!secret) return true;                 // not switched on yet: behave exactly as before
  const token = p['cf-turnstile-response'];
  if (!token) return false;                 // direct POSTs to this URL and blocked widgets
  try {
    const res = UrlFetchApp.fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method: 'post',
      payload: { secret: secret, response: token },
      muteHttpExceptions: true
    });
    const d = JSON.parse(res.getContentText());
    if (d.success !== true) return false;   // invalid, expired or already used token
    if (d.action && d.action !== TURNSTILE_ACTION) return false;
    if (d.hostname && TURNSTILE_ALLOWED_HOSTS.indexOf(d.hostname) === -1) return false;
    return true;
  } catch (err) {
    return false;                           // Cloudflare unreachable: file it, do not lose it
  }
}

/** Writes a failed submission to the Spam tab, creating the tab on first use. */
function logContactSpam_(ss, p) {
  let sh = ss.getSheetByName(CONTACT_SPAM_TAB);
  if (!sh) {
    sh = ss.insertSheet(CONTACT_SPAM_TAB);
    sh.appendRow(['Received', 'Name', 'Email', 'Phone', 'Website',
                  'What do you need help with?', 'Anything we should know?', 'Reason']);
    sh.getRange(1, 1, 1, 8).setFontWeight('bold');
  }
  sh.appendRow([
    new Date(),
    p.name || '', p.email || '', p.phone || '', p.website || '',
    p['help_with[]'] || '', p.biggest_challenge || '',
    p['cf-turnstile-response'] ? 'Token did not verify' : 'No token'
  ]);
}

// ---------------------------------------------------------------------------------------------
// The three lines to add at the very top of your EXISTING doPost. Leave the rest of it as it is.
//
// function doPost(e) {
//   const p = (e && e.parameter) || {};                                        // add
//   if (!contactPassesTurnstile_(p)) {                                          // add
//     logContactSpam_(SpreadsheetApp.getActiveSpreadsheet(), p);                // add (see note)
//     return ContentService.createTextOutput('ok');                             // add
//   }                                                                           // add
//   ...your existing code, unchanged...
// }
//
// Note: getActiveSpreadsheet() works when the script was created from inside the sheet
// (Extensions > Apps Script). If your script opens the sheet with SpreadsheetApp.openById(...),
// pass that same spreadsheet here instead.
