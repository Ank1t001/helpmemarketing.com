/*
 * HelpMeMarketing cookie consent banner, shared sitewide via
 * <script src="/consent.js" defer>. Self-contained: injects its own markup
 * and styles (tokens with hex fallbacks), no inline style attributes on
 * page HTML. Stores the choice in localStorage ("hmm_consent"), emits it as a
 * Google Consent Mode update plus a "hmm_consent_update" dataLayer event.
 * Emits the signal only; tag gating is configured in GTM. See
 * /docs/HMM_Design_System.md, "Consent banner".
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
      '.hmm-consent{position:fixed;left:16px;right:16px;bottom:calc(16px + var(--hmm-consent-offset,0px));z-index:2147483000;' +
      'max-width:560px;margin:0 auto;background:var(--bg-elevated,#1A1A1A);color:var(--text,#FFFFFF);border:1px solid var(--border,rgba(255,255,255,0.08));' +
      'border-radius:12px;padding:18px 20px;box-shadow:0 10px 40px rgba(0,0,0,.45);' +
      'font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;font-size:14px;line-height:1.55;' +
      'opacity:0;transform:translateY(12px);transition:opacity .25s ease,transform .25s ease;}' +
      '.hmm-consent.hmm-show{opacity:1;transform:translateY(0);}' +
      '.hmm-consent p{margin:0 0 14px;}' +
      '.hmm-consent a{color:var(--cta,#FF5C1A);text-decoration:underline;}' +
      '.hmm-consent-actions{display:flex;gap:10px;flex-wrap:wrap;}' +
      '.hmm-consent button{font:inherit;font-weight:600;cursor:pointer;border-radius:8px;' +
      'padding:9px 18px;border:1px solid transparent;}' +
      '.hmm-consent .hmm-accept{background:var(--cta,#FF5C1A);color:var(--bg,#0E0E0E);}' +
      '.hmm-consent .hmm-accept:hover{background:var(--cta-hover,#FF7038);}' +
      '.hmm-consent .hmm-decline{background:transparent;color:var(--text,#FFFFFF);border-color:rgba(255,255,255,0.2);}' +
      '.hmm-consent .hmm-decline:hover{border-color:rgba(255,255,255,0.45);}' +
      '.hmm-consent button:focus-visible{outline:2px solid #f78b4e;outline-offset:2px;}' +
      '@media (prefers-reduced-motion:reduce){.hmm-consent{transition:none;}}' +
      '@media (max-width:720px){.hmm-consent{left:12px;right:12px;bottom:calc(12px + var(--hmm-consent-offset,0px));padding:14px 16px;font-size:13px;line-height:1.5;}' +
      '.hmm-consent p{margin:0 0 10px;}.hmm-consent button{padding:8px 14px;}}';
    var s = document.createElement('style');
    s.id = 'hmm-consent-style';
    s.textContent = css;
    document.head.appendChild(s);
  }

  // Keep the banner clear of a control the page pins to the bottom edge
  // (marked data-consent-avoid, e.g. the audit wizard's mobile nav).
  function placeAboveFixed(el) {
    var avoid = document.querySelector('[data-consent-avoid]');
    var offset = 0;
    if (avoid) {
      var r = avoid.getBoundingClientRect();
      var pinned = getComputedStyle(avoid).position === 'fixed' && r.height > 0 &&
        Math.abs(window.innerHeight - r.bottom) < 2;
      if (pinned) offset = Math.round(r.height);
    }
    el.style.setProperty('--hmm-consent-offset', offset + 'px');
    return avoid;
  }

  function watchFixed(el, avoid) {
    var update = function () { if (el.parentNode) placeAboveFixed(el); };
    window.addEventListener('resize', update);
    // Re-measure once the .page-enter slide (350ms) has released its transform.
    setTimeout(update, 450);
    setTimeout(update, 1200);
    if (avoid && 'ResizeObserver' in window) {
      new ResizeObserver(update).observe(avoid);
    }
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
    watchFixed(el, placeAboveFixed(el));
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
    // "Manage cookie preferences" link on /privacy: clear the choice, reopen.
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
