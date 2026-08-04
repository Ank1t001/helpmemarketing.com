/*
 * HelpMeMarketing cookie consent banner (shared, sitewide).
 * Referenced once per page as <script src="/consent.js" defer>.
 *
 * Scope note: this is a self-contained JS component that injects its own
 * markup and styles. It is theme-independent so it renders consistently on
 * both legacy (light) and prototype (dark) pages. It does not use the
 * prototype CSS tokens and adds no inline style="" attributes to page HTML,
 * so it stays within the prototype no-inline convention.
 *
 * What it does (PIPEDA-appropriate foundation):
 *  - Shows a banner until the visitor makes a choice.
 *  - Stores the choice in localStorage ("hmm_consent" = granted | denied).
 *  - Emits the choice as a Google Consent Mode update AND a dataLayer event
 *    ("hmm_consent_update"), so GTM tags can be gated on it.
 *
 * IMPORTANT: this emits the consent SIGNAL. It does not by itself block any
 * GTM tag. To actually gate tags you must either (a) enable Consent Mode /
 * "Require additional consent" on your GA4 and ads tags in the GTM UI, or
 * (b) trigger those tags on the "hmm_consent_update" event with a condition
 * of consent == granted. Full default-denied-before-GTM gating also needs a
 * small Consent Mode default snippet in <head> above the GTM tag; ask to add
 * it when you want hard gating.
 */
(function () {
  'use strict';

  var KEY = 'hmm_consent';
  var SIGNALS = ['analytics_storage', 'ad_storage', 'ad_user_data', 'ad_personalization'];

  // gtag shim so consent calls are safe whether or not GTM/gtag is present.
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }

  function applyConsent(state) {
    var value = state === 'granted' ? 'granted' : 'denied';
    var consent = {};
    for (var i = 0; i < SIGNALS.length; i++) consent[SIGNALS[i]] = value;
    gtag('consent', 'update', consent);
    window.dataLayer.push({ event: 'hmm_consent_update', hmm_consent: value });
  }

  function store(state) {
    try { localStorage.setItem(KEY, state); } catch (e) {}
  }

  function read() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function injectStyles() {
    if (document.getElementById('hmm-consent-style')) return;
    var css =
      '.hmm-consent{position:fixed;left:16px;right:16px;bottom:16px;z-index:2147483000;' +
      'max-width:560px;margin:0 auto;background:#14181f;color:#e8eaed;border:1px solid #2a2f3a;' +
      'border-radius:12px;padding:18px 20px;box-shadow:0 10px 40px rgba(0,0,0,.45);' +
      'font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;font-size:14px;line-height:1.55;' +
      'opacity:0;transform:translateY(12px);transition:opacity .25s ease,transform .25s ease;}' +
      '.hmm-consent.hmm-show{opacity:1;transform:translateY(0);}' +
      '.hmm-consent p{margin:0 0 14px;}' +
      '.hmm-consent a{color:#f78b4e;text-decoration:underline;}' +
      '.hmm-consent-actions{display:flex;gap:10px;flex-wrap:wrap;}' +
      '.hmm-consent button{font:inherit;font-weight:600;cursor:pointer;border-radius:8px;' +
      'padding:9px 18px;border:1px solid transparent;}' +
      '.hmm-consent .hmm-accept{background:#F26A21;color:#fff;}' +
      '.hmm-consent .hmm-accept:hover{background:#e05d17;}' +
      '.hmm-consent .hmm-decline{background:transparent;color:#e8eaed;border-color:#3a4150;}' +
      '.hmm-consent .hmm-decline:hover{border-color:#5a6472;}' +
      '.hmm-consent button:focus-visible{outline:2px solid #f78b4e;outline-offset:2px;}' +
      '@media (prefers-reduced-motion:reduce){.hmm-consent{transition:none;}}';
    var s = document.createElement('style');
    s.id = 'hmm-consent-style';
    s.textContent = css;
    document.head.appendChild(s);
  }

  function removeBanner() {
    var el = document.getElementById('hmm-consent');
    if (!el) return;
    el.classList.remove('hmm-show');
    setTimeout(function () { if (el.parentNode) el.parentNode.removeChild(el); }, 260);
  }

  function choose(state) {
    store(state);
    applyConsent(state);
    removeBanner();
  }

  function showBanner() {
    if (document.getElementById('hmm-consent')) return;
    injectStyles();
    var el = document.createElement('div');
    el.className = 'hmm-consent';
    el.id = 'hmm-consent';
    el.setAttribute('role', 'dialog');
    el.setAttribute('aria-live', 'polite');
    el.setAttribute('aria-label', 'Cookie consent');
    el.innerHTML =
      '<p>We use cookies to see how this site is used and to improve it. ' +
      'Accept analytics cookies, or decline and we will only keep what the site needs to work. ' +
      'See our <a href="/privacy">Privacy Policy</a>.</p>' +
      '<div class="hmm-consent-actions">' +
      '<button type="button" class="hmm-accept">Accept</button>' +
      '<button type="button" class="hmm-decline">Decline</button>' +
      '</div>';
    document.body.appendChild(el);
    el.querySelector('.hmm-accept').addEventListener('click', function () { choose('granted'); });
    el.querySelector('.hmm-decline').addEventListener('click', function () { choose('denied'); });
    requestAnimationFrame(function () { el.classList.add('hmm-show'); });
  }

  function init() {
    var prior = read();
    if (prior === 'granted' || prior === 'denied') {
      applyConsent(prior); // re-assert the stored choice on every page load
    } else {
      applyConsent('denied'); // safe default until the visitor chooses
      showBanner();
    }
    // Optional "Manage cookie preferences" link (e.g. on the privacy page):
    // clicking it clears the stored choice and reopens the banner.
    var reset = document.getElementById('hmm-cookie-settings');
    if (reset) {
      reset.addEventListener('click', function (ev) {
        ev.preventDefault();
        try { localStorage.removeItem(KEY); } catch (e) {}
        showBanner();
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
