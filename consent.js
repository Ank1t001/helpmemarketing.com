/*
 * HelpMeMarketing consent, shared sitewide via <script src="/consent.js" defer>.
 * Self-contained: injects its own markup and styles (tokens with hex fallbacks),
 * no inline style attributes on page HTML. Spec: /docs/HMM_Design_System.md,
 * "Consent and privacy choices".
 *
 * Who is asked (decided by /api/region from Vercel's country and region headers):
 *   restricted (Quebec, EU and EEA, UK, Switzerland): analytics off until the visitor
 *     accepts; the banner is shown.
 *   everywhere else: analytics on by default, no banner; the footer "Privacy choices"
 *     link opens the panel to opt out.
 *   region unknown or lookup fails: treated as restricted (banner).
 *   Global Privacy Control signal: treated as an opt-out (denied, no banner).
 *   a saved choice always wins and skips the lookup.
 *
 * Session recordings (Hotjar, Microsoft Clarity) are opt-in everywhere: GTM fires those
 * tags only on the "hmm_replay_consent" dataLayer event, which is pushed only when the
 * visitor has explicitly allowed recordings. Ad signals follow an explicit Accept only.
 *
 * Signals sent: Google Consent Mode "update" plus a "hmm_consent_update" dataLayer
 * event (hmm_consent, hmm_replay, hmm_region, hmm_consent_source). The inline
 * consent "default" (denied, wait_for_update) sits in every page head above the GTM loader.
 */
(function () {
  'use strict';

  var KEY = 'hmm_consent2';          // JSON {a, r, ads}: analytics, recordings, ad signals
  var LEGACY_KEY = 'hmm_consent';    // 'granted' | 'denied' from the earlier banner
  var REGION_KEY = 'hmm_region';     // sessionStorage: 'open' | 'restricted'
  var REGION_TIMEOUT_MS = 2000;
  // Recordings default for visitors in open regions. Flip to true only with the founder's say-so.
  var REPLAY_DEFAULT_OPEN = false;

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }

  var current = { a: 'denied', r: 'denied', ads: 'denied' };
  var regionClass = 'unknown';
  var replayPushed = false;
  var explicit = false;              // true once the visitor (or a saved choice) has decided

  /* ---------- storage ---------- */
  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function ssGet(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } }
  function ssSet(k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} }
  function ok(v) { return v === 'granted' || v === 'denied'; }

  function readChoice() {
    var raw = lsGet(KEY), c = null;
    if (raw) {
      try { c = JSON.parse(raw); } catch (e) { c = null; }
      if (c && ok(c.a) && ok(c.r) && ok(c.ads)) return c;
    }
    var old = lsGet(LEGACY_KEY);       // accepted under the old banner: analytics and ad signals, never recordings
    if (old === 'granted') return { a: 'granted', r: 'denied', ads: 'granted' };
    if (old === 'denied') return { a: 'denied', r: 'denied', ads: 'denied' };
    return null;
  }

  /* ---------- signals ---------- */
  // Recordings and ad signals depend on analytics: with analytics off they are off too.
  function norm(c) {
    return c.a === 'granted' ? c : { a: 'denied', r: 'denied', ads: 'denied' };
  }

  function signals(c) {
    c = norm(c);
    current = c;
    var ads = c.a === 'granted' && c.ads === 'granted' ? 'granted' : 'denied';
    gtag('consent', 'update', { analytics_storage: c.a, ad_storage: ads, ad_user_data: ads, ad_personalization: ads });
  }

  function announce(source) {
    window.dataLayer.push({ event: 'hmm_consent_update', hmm_consent: current.a, hmm_replay: current.r, hmm_region: regionClass, hmm_consent_source: source });
    if (current.r === 'granted' && !replayPushed) {
      replayPushed = true;
      window.dataLayer.push({ event: 'hmm_replay_consent' });
    }
  }

  function decide(c, source) { signals(c); announce(source); }

  function save(c, source) {
    c = norm(c);
    explicit = true;
    lsSet(KEY, JSON.stringify(c));
    decide(c, source);
    removeBanner();
  }

  /* ---------- region ---------- */
  function lookupRegion() {
    var cached = ssGet(REGION_KEY);
    if (cached === 'open' || cached === 'restricted') return Promise.resolve(cached);
    if (!window.fetch) return Promise.resolve('restricted');
    return new Promise(function (resolve) {
      var done = false;
      function finish(v, cache) { if (done) return; done = true; if (cache) ssSet(REGION_KEY, v); resolve(v); }
      var timer = setTimeout(function () { finish('restricted', false); }, REGION_TIMEOUT_MS);
      fetch('/api/region', { cache: 'no-store', credentials: 'omit' })
        .then(function (r) { if (!r.ok) throw new Error('region ' + r.status); return r.json(); })
        .then(function (j) { clearTimeout(timer); finish(j && j.restricted === false ? 'open' : 'restricted', true); })
        .catch(function () { clearTimeout(timer); finish('restricted', false); });   // fail closed: ask
    });
  }

  /* ---------- styles ---------- */
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
      '.hmm-consent button,.hmm-pc button{font:inherit;font-weight:600;cursor:pointer;border-radius:8px;padding:9px 18px;border:1px solid transparent;}' +
      '.hmm-consent .hmm-accept,.hmm-pc .hmm-save{background:var(--cta,#FF5C1A);color:var(--bg,#0E0E0E);}' +
      '.hmm-consent .hmm-accept:hover,.hmm-pc .hmm-save:hover{background:var(--cta-hover,#FF7038);}' +
      '.hmm-consent .hmm-decline,.hmm-pc .hmm-close{background:transparent;color:var(--text,#FFFFFF);border-color:rgba(255,255,255,0.2);}' +
      '.hmm-consent .hmm-decline:hover,.hmm-pc .hmm-close:hover{border-color:rgba(255,255,255,0.45);}' +
      '.hmm-consent button:focus-visible,.hmm-pc button:focus-visible,.hmm-pc input:focus-visible{outline:2px solid #f78b4e;outline-offset:2px;}' +
      '.hmm-pc{position:fixed;inset:0;z-index:2147483001;display:flex;align-items:center;justify-content:center;padding:16px;background:rgba(0,0,0,.6);' +
      'font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;font-size:14px;line-height:1.55;color:var(--text,#FFFFFF);}' +
      '.hmm-pc-box{width:100%;max-width:480px;max-height:calc(100vh - 32px);overflow:auto;background:var(--bg-elevated,#1A1A1A);' +
      'border:1px solid var(--border,rgba(255,255,255,0.08));border-radius:14px;padding:22px 22px 18px;box-shadow:0 10px 40px rgba(0,0,0,.5);}' +
      '.hmm-pc h2{margin:0 0 6px;font-size:18px;font-weight:600;line-height:1.3;}' +
      '.hmm-pc p{margin:0 0 14px;color:var(--text-muted,#999999);}' +
      '.hmm-pc a{color:var(--cta,#FF5C1A);text-decoration:underline;}' +
      '.hmm-pc-row{display:flex;gap:12px;align-items:flex-start;padding:12px 0;border-top:1px solid var(--border,rgba(255,255,255,0.08));cursor:pointer;}' +
      '.hmm-pc-row input{flex:none;width:20px;height:20px;margin:2px 0 0;accent-color:var(--cta,#FF5C1A);cursor:pointer;}' +
      '.hmm-pc-row strong{display:block;color:var(--text,#FFFFFF);font-weight:600;}' +
      '.hmm-pc-row span{color:var(--text-muted,#999999);}' +
      '.hmm-pc-note{margin:2px 0 12px;padding:10px 12px;border:1px solid var(--border,rgba(255,255,255,0.08));border-radius:8px;font-size:13px;}' +
      '.hmm-pc-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:6px;}' +
      '.hmm-pc-status{min-height:20px;margin:10px 0 0;font-size:13px;color:var(--mint,#00D4AA);}' +
      '@media (prefers-reduced-motion:reduce){.hmm-consent{transition:none;}}' +
      '@media (max-width:720px){.hmm-consent{left:12px;right:12px;bottom:calc(12px + var(--hmm-consent-offset,0px));padding:14px 16px;font-size:13px;line-height:1.5;}' +
      '.hmm-consent p{margin:0 0 10px;}.hmm-consent button,.hmm-pc button{padding:8px 14px;}' +
      '.hmm-pc{align-items:flex-end;padding:0;}.hmm-pc-box{max-width:none;border-radius:14px 14px 0 0;max-height:90vh;padding:18px 16px 16px;}}';
    var s = document.createElement('style');
    s.id = 'hmm-consent-style';
    s.textContent = css;
    document.head.appendChild(s);
  }

  /* ---------- banner (restricted regions) ---------- */
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
      'Accept analytics cookies and session recordings, or decline and we will only keep what the site needs to work. ' +
      'See our <a href="/privacy">Privacy Policy</a>.</p>' +
      '<div class="hmm-consent-actions">' +
      '<button type="button" class="hmm-accept">Accept</button>' +
      '<button type="button" class="hmm-decline">Decline</button>' +
      '</div>';
    document.body.appendChild(el);
    watchFixed(el, placeAboveFixed(el));
    el.querySelector('.hmm-accept').addEventListener('click', function () { save({ a: 'granted', r: 'granted', ads: 'granted' }, 'banner'); });
    el.querySelector('.hmm-decline').addEventListener('click', function () { save({ a: 'denied', r: 'denied', ads: 'denied' }, 'banner'); });
    requestAnimationFrame(function () { el.classList.add('hmm-show'); });
  }

  /* ---------- Privacy choices panel ---------- */
  var lastFocus = null;

  function closePanel() {
    var p = document.getElementById('hmm-pc');
    if (p && p.parentNode) p.parentNode.removeChild(p);
    document.removeEventListener('keydown', panelKeys, true);
    if (lastFocus && lastFocus.focus) lastFocus.focus();
    lastFocus = null;
  }

  function panelKeys(ev) {
    var p = document.getElementById('hmm-pc');
    if (!p) return;
    if (ev.key === 'Escape') { ev.preventDefault(); closePanel(); return; }
    if (ev.key !== 'Tab') return;
    var f = p.querySelectorAll('button,input,a[href]');
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (ev.shiftKey && document.activeElement === first) { ev.preventDefault(); last.focus(); }
    else if (!ev.shiftKey && document.activeElement === last) { ev.preventDefault(); first.focus(); }
  }

  function openPanel() {
    if (document.getElementById('hmm-pc')) return;
    injectStyles();
    lastFocus = document.activeElement;
    var gpc = navigator.globalPrivacyControl === true;
    var wrap = document.createElement('div');
    wrap.className = 'hmm-pc';
    wrap.id = 'hmm-pc';
    wrap.innerHTML =
      '<div class="hmm-pc-box" role="dialog" aria-modal="true" aria-labelledby="hmm-pc-title">' +
      '<h2 id="hmm-pc-title">Privacy choices</h2>' +
      '<p>Choose what we may use to understand how this site is used. Our forms and security checks work either way. ' +
      'See our <a href="/privacy#sec-cookies">Privacy Policy</a>.</p>' +
      (gpc && !explicit ? '<p class="hmm-pc-note">Your browser sends a Global Privacy Control signal, so these are off until you turn them on here.</p>' : '') +
      '<label class="hmm-pc-row"><input type="checkbox" id="hmm-pc-a"><span><strong>Analytics</strong>' +
      'Google Analytics counts visits and enquiries so we can improve the site.</span></label>' +
      '<label class="hmm-pc-row"><input type="checkbox" id="hmm-pc-r"><span><strong>Session recordings</strong>' +
      'Hotjar and Microsoft Clarity record how pages are used so we can fix confusing ones. Off unless you turn it on, and ' +
      'it needs Analytics to be on. Turning it off takes effect on the next page you open.</span></label>' +
      '<div class="hmm-pc-actions"><button type="button" class="hmm-save">Save choices</button>' +
      '<button type="button" class="hmm-close">Close</button></div>' +
      '<p class="hmm-pc-status" role="status" aria-live="polite"></p>' +
      '</div>';
    document.body.appendChild(wrap);
    var a = wrap.querySelector('#hmm-pc-a'), r = wrap.querySelector('#hmm-pc-r');
    a.checked = current.a === 'granted';
    r.checked = current.r === 'granted';
    r.disabled = !a.checked;
    a.addEventListener('change', function () { r.disabled = !a.checked; if (!a.checked) r.checked = false; });
    wrap.querySelector('.hmm-close').addEventListener('click', closePanel);
    wrap.addEventListener('click', function (ev) { if (ev.target === wrap) closePanel(); });
    wrap.querySelector('.hmm-save').addEventListener('click', function () {
      var an = a.checked ? 'granted' : 'denied';
      save({ a: an, r: r.checked ? 'granted' : 'denied', ads: an === 'granted' && current.ads === 'granted' ? 'granted' : 'denied' }, 'panel');
      wrap.querySelector('.hmm-pc-status').textContent = 'Saved.';
      setTimeout(closePanel, 900);
    });
    document.addEventListener('keydown', panelKeys, true);
    a.focus();
  }

  /* ---------- start ---------- */
  function init() {
    // Footer "Privacy choices" and the /privacy "Manage cookie preferences" link both open the panel.
    document.addEventListener('click', function (ev) {
      var t = ev.target && ev.target.closest ? ev.target.closest('#hmm-privacy-choices,#hmm-cookie-settings') : null;
      if (!t) return;
      ev.preventDefault();
      openPanel();
    });

    var prior = readChoice();
    if (prior) {                               // a saved choice wins; no lookup
      explicit = true;
      regionClass = ssGet(REGION_KEY) || 'unknown';
      decide(prior, 'saved');
      return;
    }

    if (navigator.globalPrivacyControl === true) {
      regionClass = ssGet(REGION_KEY) || 'unknown';
      decide({ a: 'denied', r: 'denied', ads: 'denied' }, 'gpc');   // an opt-out signal: no banner
      return;
    }

    signals({ a: 'denied', r: 'denied', ads: 'denied' });  // safe until we know who this is
    lookupRegion().then(function (region) {
      regionClass = region;
      if (explicit) return;                    // the visitor chose while we were asking
      if (region === 'open') {
        decide({ a: 'granted', r: REPLAY_DEFAULT_OPEN ? 'granted' : 'denied', ads: 'denied' }, 'region_default');
      } else {
        announce('pending');
        showBanner();
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
