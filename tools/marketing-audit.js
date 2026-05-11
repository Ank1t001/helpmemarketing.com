/* HelpMeMarketing — Marketing Maturity Audit behaviour
 *
 * One-question-at-a-time wizard with sticky progress bar + Previous/Next nav.
 * Question state, scoring, tier matching, email capture, results rendering.
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

  // Deployed Apps Script /exec URL for audit submissions.
  const APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbxei2sZjxF410RIcu4ynzA29cqAHtXI3sql90h57qEYFvDjJAWhZUAxi1Xy16a60RWM/exec';

  // Tier thresholds — first match wins, evaluated in order: <=30, <=55, <=80, else Advanced.
  const TIER_THRESHOLDS = [
    { max: 30,  key: 'foundational' },
    { max: 55,  key: 'growing' },
    { max: 80,  key: 'scaling' },
    { max: 100, key: 'advanced' }
  ];

  // Wizard transition timing. Must match CSS .audit-question opacity transition (0.3s).
  const TRANSITION_DURATION_MS = 300;

  // Wizard question order. Matches data-question attributes on fieldsets.
  const QUESTION_IDS = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8'];

  // ============================================================
  // STATE (closure-local, not persisted)
  // ============================================================

  const answers = {};            // { q1: 5, q2: 8, ... } — last selected score per question
  let currentTier = null;
  let currentRawScore = 0;
  let currentScaledScore = 0;
  let submitting = false;        // prevents double-submit on email form

  // Wizard state
  let currentQuestionIndex = 0;  // 0-based; 0 = q1
  let transitioning = false;     // race guard for rapid Next/Prev clicks (Finding 5)

  // ============================================================
  // INIT
  // ============================================================

  function init() {
    setupQuestionTracking();
    setupWizardNavigation();
    setupEmailForm();
    setupNavHamburger();

    // Initialize wizard UI (progress fill, counter, dimension label, button states)
    updateProgress();
    updateNavButtons();
  }

  // ============================================================
  // QUESTION TRACKING (radio change -> answer state)
  // ============================================================

  function setupQuestionTracking() {
    const form = document.getElementById('audit-form');
    if (!form) return;

    // Single delegated listener handles all 8 questions x 37 radio options.
    form.addEventListener('change', function (e) {
      const target = e.target;
      if (!target || target.type !== 'radio' || !target.name) return;
      if (!/^q[1-8]$/.test(target.name)) return;
      const score = parseInt(target.dataset.score, 10);
      if (Number.isNaN(score)) return;
      answers[target.name] = score;
      updateNavButtons();
    });
  }

  function getAnsweredCount() {
    return Object.keys(answers).length;
  }

  // ============================================================
  // WIZARD HELPERS
  // ============================================================

  function getCurrentQuestionId() {
    return QUESTION_IDS[currentQuestionIndex];
  }

  // Reads dimension from the current fieldset's .audit-dimension span
  // (single source of truth — no duplicate data-dimension attribute needed).
  function getCurrentDimension() {
    const id = getCurrentQuestionId();
    const fieldset = document.querySelector('[data-question="' + id + '"]');
    if (!fieldset) return '';
    const dimSpan = fieldset.querySelector('.audit-dimension');
    return dimSpan ? dimSpan.textContent.trim() : '';
  }

  function isCurrentQuestionAnswered() {
    return Object.prototype.hasOwnProperty.call(answers, getCurrentQuestionId());
  }

  // ============================================================
  // WIZARD UI UPDATES
  // ============================================================

  function updateProgress() {
    const total = QUESTION_IDS.length;
    const current = currentQuestionIndex + 1;
    const fill = document.getElementById('audit-progress-fill');
    const counter = document.getElementById('audit-progress-counter');
    const dimension = document.getElementById('audit-progress-dimension');

    if (fill) fill.style.width = ((current / total) * 100) + '%';
    if (counter) counter.textContent = 'Question ' + current + ' of ' + total;
    if (dimension) dimension.textContent = getCurrentDimension();
  }

  function updateNavButtons() {
    const prevBtn = document.getElementById('audit-prev');
    const nextBtn = document.getElementById('audit-next');
    if (!prevBtn || !nextBtn) return;

    prevBtn.disabled = (currentQuestionIndex === 0);
    nextBtn.disabled = !isCurrentQuestionAnswered();

    // Final question: transform Next into "See my results" (gold variant)
    if (currentQuestionIndex === QUESTION_IDS.length - 1) {
      nextBtn.classList.add('audit-nav-btn--final');
      nextBtn.innerHTML = 'See my results';
      nextBtn.setAttribute('aria-label', 'See my results');
    } else {
      nextBtn.classList.remove('audit-nav-btn--final');
      nextBtn.innerHTML = 'Next <span aria-hidden="true">&rarr;</span>';
      nextBtn.setAttribute('aria-label', 'Next question');
    }
  }

  // ============================================================
  // QUESTION TRANSITION (fade out -> swap -> fade in)
  // Locked by `transitioning` flag for full ~600ms cycle to prevent
  // rapid-click race conditions (Finding 5).
  // ============================================================

  function showQuestion(index, direction) {
    if (transitioning) return;
    transitioning = true;

    const currentFieldset = document.querySelector('.audit-question--active');
    const targetId = QUESTION_IDS[index];
    const targetFieldset = document.querySelector('[data-question="' + targetId + '"]');

    if (!targetFieldset) {
      transitioning = false;
      return;
    }

    // Fade out current: --active -> --fading (display:block kept, opacity 1 -> 0)
    if (currentFieldset) {
      currentFieldset.classList.add('audit-question--fading');
      currentFieldset.classList.remove('audit-question--active');
    }

    window.setTimeout(function () {
      // Hide previous fully (remove --fading, base display:none kicks in)
      if (currentFieldset) {
        currentFieldset.classList.remove('audit-question--fading');
        currentFieldset.hidden = true;
      }

      // Reveal target at opacity 0 (--fading: display:block, opacity:0)
      targetFieldset.hidden = false;
      targetFieldset.classList.add('audit-question--fading');

      // Force layout so the transparent state paints before the transition starts
      // (otherwise some browsers batch class changes and skip the animation).
      void targetFieldset.offsetHeight;

      // Trigger fade-in: --fading -> --active (opacity 0 -> 1 transitions over 300ms)
      window.requestAnimationFrame(function () {
        targetFieldset.classList.remove('audit-question--fading');
        targetFieldset.classList.add('audit-question--active');
      });

      currentQuestionIndex = index;
      updateProgress();
      updateNavButtons();

      // Scroll to question. CSS scroll-margin-top: 80px (Finding 4) keeps the
      // heading below the sticky progress bar + nav.
      targetFieldset.scrollIntoView({ behavior: 'smooth', block: 'start' });

      // Focus the previously-selected radio (or first if none) on desktop only.
      // Skip on mobile to avoid spawning the on-screen keyboard.
      if (window.innerWidth > 768) {
        const selected = targetFieldset.querySelector('input[type="radio"]:checked');
        const focusTarget = selected || targetFieldset.querySelector('input[type="radio"]');
        if (focusTarget) {
          try { focusTarget.focus({ preventScroll: true }); }
          catch (_) { focusTarget.focus(); }
        }
      }

      // Release transition lock only after the fade-in also completes,
      // so a second rapid click can't overlap two opacity transitions.
      window.setTimeout(function () {
        transitioning = false;
      }, TRANSITION_DURATION_MS);
    }, TRANSITION_DURATION_MS);
  }

  function goToNext() {
    if (transitioning) return;
    if (!isCurrentQuestionAnswered()) return;

    if (currentQuestionIndex === QUESTION_IDS.length - 1) {
      handleSubmit();
      return;
    }
    showQuestion(currentQuestionIndex + 1, 'forward');
  }

  function goToPrevious() {
    if (transitioning) return;
    if (currentQuestionIndex === 0) return;
    showQuestion(currentQuestionIndex - 1, 'backward');
  }

  // ============================================================
  // WIZARD WIRING (clicks + Enter + arrow keys)
  // ============================================================

  function setupWizardNavigation() {
    const form = document.getElementById('audit-form');
    const prevBtn = document.getElementById('audit-prev');
    const nextBtn = document.getElementById('audit-next');

    if (prevBtn) prevBtn.addEventListener('click', goToPrevious);
    if (nextBtn) nextBtn.addEventListener('click', goToNext);

    // Enter on a focused radio submits the form by HTML default. Route through
    // goToNext for wizard-consistent behavior, including Q8 -> handleSubmit (Finding 6).
    if (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        goToNext();
      });
    }

    // Arrow keys advance/retreat — but ONLY when focus is outside a form input.
    // Native radio groups use arrow keys to step between options; let that win
    // when the user is interacting with a question (Finding 3).
    document.addEventListener('keydown', function (e) {
      const tag = e.target && e.target.tagName;
      if (tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') return;

      // Suppress wizard nav when past the audit (email gate or results visible)
      const gate = document.getElementById('audit-email-gate');
      const results = document.getElementById('audit-results');
      if ((gate && !gate.hidden) || (results && !results.hidden)) return;

      if (e.key === 'ArrowRight') {
        if (nextBtn && !nextBtn.disabled) {
          e.preventDefault();
          goToNext();
        }
      } else if (e.key === 'ArrowLeft') {
        if (prevBtn && !prevBtn.disabled) {
          e.preventDefault();
          goToPrevious();
        }
      }
    });
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
  // SUBMIT (final question -> email gate)
  // ============================================================

  function handleSubmit() {
    // Defensive guard: should never trigger with <8 answers because goToNext
    // checks isCurrentQuestionAnswered first. But cheap to verify.
    if (getAnsweredCount() < 8) return;

    currentRawScore = calculateRawScore();
    currentScaledScore = Math.round(currentRawScore * 1.25);
    currentTier = getTier(currentScaledScore);

    // Hide wizard chrome — the email gate takes over from here.
    const nav = document.querySelector('.audit-wizard-nav');
    const progress = document.getElementById('audit-progress');
    if (nav) nav.style.display = 'none';
    if (progress) progress.style.display = 'none';

    revealEmailGate();
  }

  function revealEmailGate() {
    const gate = document.getElementById('audit-email-gate');
    const preview = document.getElementById('audit-tier-preview');
    if (!gate || !preview) return;

    const tierData = getTierData(currentTier);
    const tierName = tierData ? tierData.name : currentTier;

    preview.innerHTML =
      'Your tier: <strong>' + escapeHtml(tierName) + '</strong> ' +
      '<span class="audit-tier-score">' + currentScaledScore + '/100</span>';

    gate.hidden = false;

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
      company_url_secondary: ''
    };
  }

  function submitToBackend(payload) {
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
  // NAV HAMBURGER (sitewide chrome — kept here so this page
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
