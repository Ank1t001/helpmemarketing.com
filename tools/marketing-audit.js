/* HelpMeMarketing — Marketing Maturity Audit behaviour
 *
 * Question state tracking, scoring, tier matching, email capture, results rendering.
 * Content data comes from window.MARKETING_AUDIT_CONTENT (loaded by marketing-audit-content.js).
 *
 * Storage policy: NONE. No localStorage, no sessionStorage, no cookies.
 * Page reload resets the audit. Closure state holds answers in memory only.
 *
 * Cloudflare compatibility: all listeners via addEventListener inside IIFE.
 * No inline onclick handlers anywhere on the page.
 */
(function () {
  'use strict';

  // ============================================================
  // CONFIGURATION
  // ============================================================

  // CP4 wiring target: replace with the deployed Apps Script /exec URL.
  // Pattern follows /contact.html SHEET_URL convention.
  const APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbxei2sZjxF410RIcu4ynzA29cqAHtXI3sql90h57qEYFvDjJAWhZUAxi1Xy16a60RWM/exec';

  // Tier thresholds — matches PART 2 of HMM_Marketing_Audit_Content.md.
  // First match wins, evaluated in order: ≤30, ≤55, ≤80, else Advanced.
  const TIER_THRESHOLDS = [
    { max: 30,  key: 'foundational' },
    { max: 55,  key: 'growing' },
    { max: 80,  key: 'scaling' },
    { max: 100, key: 'advanced' }
  ];

  // ============================================================
  // STATE (closure-local, not persisted)
  // ============================================================

  const answers = {};            // { q1: 5, q2: 8, ... } — last selected score per question
  let currentTier = null;
  let currentRawScore = 0;
  let currentScaledScore = 0;
  let submitting = false;        // prevents double-submit on email form

  // ============================================================
  // INIT
  // ============================================================

  function init() {
    setupQuestionTracking();
    setupAuditSubmit();
    setupEmailForm();
    setupNavHamburger();
  }

  // ============================================================
  // QUESTION TRACKING
  // ============================================================

  function setupQuestionTracking() {
    const form = document.getElementById('audit-form');
    if (!form) return;

    // Single delegated listener handles all 8 questions × 37 radio options.
    form.addEventListener('change', function (e) {
      const target = e.target;
      if (!target || target.type !== 'radio' || !target.name) return;
      if (!/^q[1-8]$/.test(target.name)) return;
      const score = parseInt(target.dataset.score, 10);
      if (Number.isNaN(score)) return;
      answers[target.name] = score;
      updateSubmitState();
    });
  }

  function getAnsweredCount() {
    return Object.keys(answers).length;
  }

  function updateSubmitState() {
    const submit = document.getElementById('audit-submit');
    const progress = document.getElementById('audit-progress');
    if (!submit) return;

    const count = getAnsweredCount();
    submit.disabled = count < 8;

    if (progress) {
      progress.textContent = count < 8
        ? count + ' of 8 answered'
        : 'Ready';
    }
  }

  // ============================================================
  // SCORING + TIER MATCHING
  // ============================================================

  function calculateRawScore() {
    let sum = 0;
    for (const k in answers) {
      if (Object.prototype.hasOwnProperty.call(answers, k)) {
        sum += answers[k];
      }
    }
    return sum;
  }

  function getTier(scaledScore) {
    for (let i = 0; i < TIER_THRESHOLDS.length; i++) {
      if (scaledScore <= TIER_THRESHOLDS[i].max) {
        return TIER_THRESHOLDS[i].key;
      }
    }
    return 'advanced'; // safety net
  }

  // ============================================================
  // AUDIT SUBMIT — reveal email gate with tier preview
  // ============================================================

  function setupAuditSubmit() {
    const form = document.getElementById('audit-form');
    if (!form) return;

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (getAnsweredCount() < 8) return;

      currentRawScore = calculateRawScore();
      currentScaledScore = Math.round(currentRawScore * 1.25);
      currentTier = getTier(currentScaledScore);

      revealEmailGate();
    });
  }

  function revealEmailGate() {
    const gate = document.getElementById('audit-email-gate');
    const preview = document.getElementById('audit-tier-preview');
    const submit = document.getElementById('audit-submit');
    if (!gate || !preview) return;

    const tierData = getTierData(currentTier);
    const tierName = tierData ? tierData.name : currentTier;

    preview.innerHTML =
      'Your tier: <strong>' + escapeHtml(tierName) + '</strong> ' +
      '<span class="audit-tier-score">' + currentScaledScore + '/100</span>';

    gate.hidden = false;

    // Hide submit button (audit flow has moved past it)
    if (submit) submit.style.display = 'none';

    // Smooth-scroll + focus email input
    window.setTimeout(function () {
      gate.scrollIntoView({ behavior: 'smooth', block: 'start' });
      const emailInput = document.getElementById('audit-email-input');
      if (emailInput) {
        try { emailInput.focus({ preventScroll: true }); }
        catch (_) { emailInput.focus(); }
      }
    }, 100);
  }

  // ============================================================
  // EMAIL FORM — validation, honeypot, POST to backend
  // ============================================================

  function setupEmailForm() {
    const form = document.getElementById('audit-email-form');
    if (!form) return;

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (submitting) return;

      const emailInput = document.getElementById('audit-email-input');
      const honeypot = document.getElementById('audit-hp');
      const errorEl = document.getElementById('audit-email-error');

      // Honeypot check — silent reject (treat as no-op, don't reveal results).
      // A real user won't have this filled; a bot will.
      if (honeypot && honeypot.value && honeypot.value.trim().length > 0) {
        return;
      }

      const email = (emailInput && emailInput.value || '').trim();
      if (!isValidEmail(email)) {
        showError(errorEl, 'Please enter a valid email address.');
        return;
      }

      hideError(errorEl);
      lockSubmit(form, true);

      const payload = buildPayload(email);

      submitToBackend(payload)
        .then(function () {
          renderResults();
        })
        .catch(function () {
          lockSubmit(form, false);
          showError(errorEl,
            'Something went wrong sending your results. ' +
            'Please try again or email hello@helpmemarketing.com.');
        });
    });
  }

  function lockSubmit(form, lock) {
    submitting = lock;
    const btn = form.querySelector('.audit-email-submit');
    if (!btn) return;
    btn.disabled = lock;
    btn.textContent = lock ? 'Sending…' : 'Show my results';
  }

  function isValidEmail(email) {
    if (!email || email.length < 5 || email.length > 254) return false;
    // Lightweight format check: token@token.tld
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  function showError(el, message) {
    if (!el) return;
    el.textContent = message;
    el.hidden = false;
  }
  function hideError(el) {
    if (!el) return;
    el.textContent = '';
    el.hidden = true;
  }

  function buildPayload(email) {
    return {
      email: email,
      tier: currentTier,
      tierName: getTierName(currentTier),
      scaledScore: currentScaledScore,
      rawScore: currentRawScore,
      scores: {
        q1: answers.q1 || 0,
        q2: answers.q2 || 0,
        q3: answers.q3 || 0,
        q4: answers.q4 || 0,
        q5: answers.q5 || 0,
        q6: answers.q6 || 0,
        q7: answers.q7 || 0,
        q8: answers.q8 || 0
      },
      userAgent: navigator.userAgent || '',
      referrer: document.referrer || '',
      submittedAt: new Date().toISOString(),
      // Honeypot value — intentionally empty here; Apps Script side enforces.
      company_url_secondary: ''
    };
  }

  function submitToBackend(payload) {
    // no-cors POST follows the /contact.html pattern — Apps Script receives
    // text/plain body and parses e.postData.contents. Response is opaque
    // (browser can't read it) so we treat fetch resolution as success.
    return fetch(APPS_SCRIPT_URL, {
      method: 'POST',
      mode: 'no-cors',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify(payload)
    });
  }

  // ============================================================
  // RESULTS RENDERING
  // ============================================================

  function renderResults() {
    const results = document.getElementById('audit-results');
    const gate = document.getElementById('audit-email-gate');
    if (!results) return;

    const tierData = getTierData(currentTier);
    if (!tierData) {
      showError(
        document.getElementById('audit-email-error'),
        'Could not load results. Please refresh and try again.'
      );
      return;
    }

    const linksHTML = (tierData.internalLinks || []).map(function (l) {
      return '<li><a href="' + escapeAttr(l.href) + '">' + escapeHtml(l.text) + '</a></li>';
    }).join('');

    const internalLinksBlock = linksHTML
      ? '<aside class="audit-internal-links">' +
          '<h4>Related reading and next steps</h4>' +
          '<ul>' + linksHTML + '</ul>' +
        '</aside>'
      : '';

    results.innerHTML =
      '<div class="audit-tier-badge">' +
        '<span>' + escapeHtml(tierData.name) + '</span>' +
        '<span class="audit-tier-score">' + currentScaledScore + '/100</span>' +
      '</div>' +
      '<section class="audit-tier-description">' + tierData.descriptionHTML + '</section>' +
      '<section class="audit-recommendations">' + tierData.recommendationsHTML + '</section>' +
      '<section class="audit-service-mapping">' + tierData.serviceMappingHTML + '</section>' +
      internalLinksBlock +
      '<a class="audit-final-cta" href="/contact">' +
        '<span class="audit-final-cta-label">Free · 30 min</span>' +
        '<span class="audit-final-cta-text">Start a conversation</span>' +
      '</a>';

    // Swap: hide email gate, show results
    if (gate) gate.hidden = true;
    results.hidden = false;

    window.setTimeout(function () {
      results.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
  }

  // ============================================================
  // CONTENT LOOKUP HELPERS
  // ============================================================

  function getTierData(tierKey) {
    const content = window.MARKETING_AUDIT_CONTENT;
    if (!content || !content.tiers) return null;
    return content.tiers[tierKey] || null;
  }
  function getTierName(tierKey) {
    const t = getTierData(tierKey);
    return t ? t.name : (tierKey || '');
  }

  // ============================================================
  // NAV HAMBURGER (sitewide chrome — handled here so this page
  // is fully Cloudflare-safe with no inline onclick handlers)
  // ============================================================

  function setupNavHamburger() {
    const btn = document.getElementById('audit-nav-ham');
    const menu = document.querySelector('.nav-mobile-menu');
    if (!btn || !menu) return;

    btn.addEventListener('click', function () {
      const isOpen = menu.classList.toggle('open');
      btn.classList.toggle('open', isOpen);
      btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    // Close on click outside
    document.addEventListener('click', function (e) {
      if (!menu.classList.contains('open')) return;
      if (menu.contains(e.target) || btn.contains(e.target)) return;
      menu.classList.remove('open');
      btn.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
    });
  }

  // ============================================================
  // ESCAPING UTILITIES
  // ============================================================

  const HTML_ESCAPES = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  };
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) { return HTML_ESCAPES[c]; });
  }
  function escapeAttr(s) {
    return escapeHtml(s);
  }

  // ============================================================
  // BOOTSTRAP
  // ============================================================

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
