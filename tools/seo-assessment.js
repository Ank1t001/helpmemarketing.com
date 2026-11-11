/* SEO and AI visibility assessment on /ai-seo-agency (2026-11-11).
   A deterministic, answer-based guide: no scan, no AI call, nothing sent. The rules live in decide() so they can be
   tested in Node (docs/tests/seo_assessment_test.js). The visual parts reuse the marketing audit's .ma-* styles. */
(function (root) {
  'use strict';

  var QUESTIONS = [
    { id: 'goal', q: 'What would you most like to improve?', opts: [
      { v: 'find', label: 'Help more people find my business.' },
      { v: 'enquire', label: 'Get more enquiries from existing website visits.' },
      { v: 'ai', label: 'Understand how my business appears in AI answers.' },
      { v: 'understand', label: 'Understand what search is bringing to my business.' },
      { v: 'unsure', label: 'I’m not sure where to start.' }] },
    { id: 'traffic', q: 'What best describes your website’s search traffic?', opts: [
      { v: 'few', label: 'Very few people arrive through search.' },
      { v: 'visits', label: 'People arrive through search, but few enquire.' },
      { v: 'enquiries', label: 'Search already brings enquiries.' },
      { v: 'unknown', label: 'I don’t have reliable figures.' }] },
    { id: 'action', q: 'What kind of customer action matters most?', opts: [
      { v: 'calls', label: 'Calls or quote requests.' },
      { v: 'bookings', label: 'Bookings or appointments.' },
      { v: 'purchases', label: 'Online purchases.' },
      { v: 'other', label: 'Something else.' }] },
    { id: 'data', q: 'What information can you currently use?', multi: true, hint: 'Choose all that apply.', opts: [
      { v: 'gsc', label: 'Search Console information about searches and pages.' },
      { v: 'analytics', label: 'Website analytics.' },
      { v: 'records', label: 'A record of enquiries, bookings or sales.' },
      { v: 'ai_checks', label: 'Previous checks of AI answers about my business.' },
      { v: 'none', label: 'I’m not sure / none of these.', exclusive: true }] }
  ];

  // Wording for the customer action chosen in question 3.
  var ACTION = { calls: 'calls and enquiries', bookings: 'bookings', purchases: 'purchases', other: 'customer actions' };
  // Sources that can show search figures or customer actions. Earlier AI answer checks are useful, but they are not
  // a measure of search traffic, so they do not count here.
  var USABLE = ['gsc', 'analytics', 'records'];

  function label(qid, v) {
    for (var i = 0; i < QUESTIONS.length; i++) if (QUESTIONS[i].id === qid)
      for (var j = 0; j < QUESTIONS[i].opts.length; j++) if (QUESTIONS[i].opts[j].v === v) return QUESTIONS[i].opts[j].label;
    return '';
  }
  function quote(qid, v) { return '“' + label(qid, v).replace(/\.$/, '') + '”'; }

  /* The decision rules, in order of precedence:
     1. No reliable search figures and no usable source (Search Console, analytics or customer-action records)
        -> baseline: establish the search starting point.
     2. Otherwise, visits without enquiries, or "more enquiries" as the main goal -> enquiry_path.
        If the traffic answer is "very few" or "no reliable figures", traffic must be confirmed first (conflict).
     3. Otherwise, "understand AI answers" as the main goal -> ai_answers.
     4. Otherwise -> service_pages. */
  function decide(a) {
    var data = a.data || [];
    var usable = data.filter(function (d) { return USABLE.indexOf(d) > -1; });
    var reasons = [], conflict = '';
    if (a.traffic === 'unknown' && usable.length === 0) {
      reasons.push('You said ' + quote('traffic', 'unknown') + '.');
      reasons.push(data.indexOf('none') > -1 || !data.length
        ? 'You said you are not sure which information you can use, or have none of the listed sources.'
        : 'You did not choose Search Console, website analytics or a record of ' + ACTION[a.action] + '.');
      return { key: 'baseline', reasons: reasons, conflict: conflict };
    }
    if (a.traffic === 'visits' || a.goal === 'enquire') {
      if (a.traffic === 'visits') reasons.push('You said ' + quote('traffic', 'visits') + '.');
      if (a.goal === 'enquire') reasons.push('Your main goal is ' + quote('goal', 'enquire') + '.');
      if (a.goal === 'enquire' && (a.traffic === 'few' || a.traffic === 'unknown')) {
        conflict = a.traffic === 'few'
          ? 'You also said very few people arrive through search. Confirm how many relevant search visits reach your site first: if there are very few, the path to an enquiry has little to work with, and helping people find you may matter more.'
          : 'You also said you don’t have reliable figures. Confirm how many relevant search visits arrive, using the sources you have, before deciding the path to an enquiry is the main gap.';
      }
      return { key: 'enquiry_path', reasons: reasons, conflict: conflict };
    }
    if (a.goal === 'ai') {
      reasons.push('Your main goal is ' + quote('goal', 'ai') + '.');
      if (data.indexOf('ai_checks') === -1) reasons.push('You haven’t indicated whether earlier AI visibility checks are available. Check for an existing record before creating your baseline.');
      return { key: 'ai_answers', reasons: reasons, conflict: conflict };
    }
    reasons.push('Your main goal is ' + quote('goal', a.goal) + '.');
    reasons.push('You said ' + quote('traffic', a.traffic) + '.');
    return { key: 'service_pages', reasons: reasons, conflict: conflict };
  }

  function content(key, action) {
    var act = ACTION[action] || ACTION.other;
    var R = {
      baseline: {
        title: 'Establish your search starting point',
        check: 'Whether Search Console and website analytics are available, and whether genuine ' + act + ' are recorded.',
        first: 'Create a dated baseline of search visits and real ' + act + ' using the information available.',
        follow: ['Identify the pages people arrive on from search.', 'Separate test activity from genuine ' + act + '.'],
        monitor: 'Whether search visits and ' + act + ' are being recorded consistently.',
        note: 'Missing figures are not the same as no search traffic or no demand. They only mean the starting point isn’t measured yet.'
      },
      enquiry_path: {
        title: 'Review the path from a search visit to an enquiry',
        check: 'Whether relevant visitors are reaching the right pages, and whether ' + act + ' can be completed.',
        first: 'Review one important landing page and its next step from the customer’s perspective.',
        follow: ['Clarify the service, evidence and next action where needed.', 'Verify that genuine ' + act + ' are recorded correctly.'],
        monitor: 'Relevant search visits and completed ' + act + ' over comparable periods.',
        note: 'This doesn’t mean your website converts poorly. That needs real figures for visits and ' + act + '.'
      },
      ai_answers: {
        title: 'Check how AI answers describe your business',
        check: 'Which real questions customers ask when researching the service.',
        first: 'Choose a small, relevant set of questions and record dated answers, mentions and cited sources.',
        follow: ['Compare those answers with your actual services and location.', 'Review unclear or inconsistent information on relevant pages and business profiles.'],
        monitor: 'Changes across repeated checks, plus identifiable referral visits and ' + act + ' where available.',
        note: 'AI answers vary by tool, question and timing. A single missing mention doesn’t show a site-wide visibility problem.'
      },
      service_pages: {
        title: 'Review how customers find your main services',
        check: 'Which service pages appear in search and which customer questions they answer.',
        first: 'Choose one commercially important service page and review its search evidence and usefulness.',
        follow: ['Add missing service details or answers to customer questions, using real business information.', 'Check that relevant existing pages link to it clearly.'],
        monitor: 'Page-level search impressions, clicks, relevant queries and genuine ' + act + ' over comparable periods.',
        note: 'This doesn’t assume indexing problems, missing links or content gaps. Each of those needs to be checked on the page itself.'
      }
    };
    var r = R[key];
    r.cannot = ['Whether your answers match what Search Console, analytics or your records actually show.',
      'Anything on your website: this assessment doesn’t scan pages, links or technical set-up.',
      'Your rankings, or how AI tools currently describe your business.'];
    return r;
  }

  function summary(a, d, r) {
    var lines = ['SEO and AI visibility assessment (helpmemarketing.com/ai-seo-agency)', '',
      'Starting priority: ' + r.title, '', 'My answers:',
      '- What I would most like to improve: ' + label('goal', a.goal),
      '- My website’s search traffic: ' + label('traffic', a.traffic),
      '- Customer action that matters most: ' + label('action', a.action),
      '- Information I can use: ' + (a.data || []).map(function (v) { return label('data', v).replace(/\.$/, ''); }).join('; ')];
    if (d.conflict) lines.push('', 'Note: ' + d.conflict);
    lines.push('', 'Anything else you should know:', '');
    return lines.join('\n');
  }

  var api = { QUESTIONS: QUESTIONS, decide: decide, content: content, summary: summary, label: label };
  if (typeof module !== 'undefined' && module.exports) { module.exports = api; return; }
  root.HMM_SEOA = api;

  /* ---------- page behaviour ---------- */
  function init() {
    var box = document.getElementById('seoa'); if (!box) return;
    var $ = function (id) { return document.getElementById(id); };
    var startBox = $('seoa-start-box'), startBtn = $('seoa-start'), wizard = $('seoa-wizard'), form = $('seoa-form');
    var stepHost = $('seoa-step'), count = $('seoa-count'), fill = $('seoa-fill'), err = $('seoa-err');
    var backBtn = $('seoa-back'), nextBtn = $('seoa-next'), out = $('seoa-result'), live = $('seoa-live');
    var answers = {}, idx = 0, started = false, last = null, helpSent = false;
    function hide(el, on) { el.classList.toggle('is-hidden', on); }
    function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
    function track(ev, data) { try { window.dataLayer = window.dataLayer || []; var o = { event: ev }; for (var k in data || {}) o[k] = data[k]; window.dataLayer.push(o); } catch (e) {} }
    function focusTop(el) { el.focus({ preventScroll: true }); var r = el.getBoundingClientRect(); if (r.top < 72 || r.top > window.innerHeight * 0.6) el.scrollIntoView({ block: 'start' }); }

    startBox.hidden = false;
    startBtn.addEventListener('click', function () {
      if (!started) { started = true; track('seo_assess_start'); }
      hide(startBox, true); startBox.hidden = true; hide(wizard, false); idx = 0; render(true);
    });

    function render(focus) {
      var q = QUESTIONS[idx], n = QUESTIONS.length, multi = !!q.multi, cur = answers[q.id];
      fill.style.width = Math.max(4, Math.round((idx / n) * 100)) + '%';
      count.textContent = 'Question ' + (idx + 1) + ' of ' + n;
      var h = '<fieldset class="ma-q"><legend class="ma-q-legend"><span class="ma-q-text" tabindex="-1">' + esc(q.q) + '</span></legend>' +
        (q.hint ? '<p class="ma-q-hint">' + esc(q.hint) + '</p>' : '') + '<div class="ma-opts">';
      q.opts.forEach(function (o) {
        var on = multi ? (cur || []).indexOf(o.v) > -1 : cur === o.v;
        h += '<label class="ma-opt' + (o.exclusive ? ' ma-opt--unsure' : '') + (multi ? ' seoa-multi' : '') + '"><input type="' + (multi ? 'checkbox' : 'radio') +
          '" name="seoa-' + q.id + '" value="' + esc(o.v) + '"' + (on ? ' checked' : '') + '><span>' + esc(o.label) + '</span></label>';
      });
      stepHost.innerHTML = h + '</div></fieldset>';
      hide(err, true); err.textContent = '';
      backBtn.classList.toggle('is-invisible', idx === 0); backBtn.disabled = idx === 0;
      nextBtn.textContent = idx === n - 1 ? 'See my starting point' : 'Next';
      if (focus) focusTop(stepHost.querySelector('.ma-q-text'));
    }
    stepHost.addEventListener('change', function (e) {
      var t = e.target, q = QUESTIONS[idx]; if (!t || t.name !== 'seoa-' + q.id) return;
      if (!q.multi) { answers[q.id] = t.value; }
      else {
        var excl = q.opts.filter(function (o) { return o.exclusive; }).map(function (o) { return o.v; });
        if (t.checked && excl.indexOf(t.value) > -1) stepHost.querySelectorAll('input').forEach(function (i) { if (i !== t) i.checked = false; });
        else if (t.checked) stepHost.querySelectorAll('input').forEach(function (i) { if (excl.indexOf(i.value) > -1) i.checked = false; });
        answers[q.id] = Array.prototype.filter.call(stepHost.querySelectorAll('input'), function (i) { return i.checked; }).map(function (i) { return i.value; });
      }
      hide(err, true);
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var q = QUESTIONS[idx], a = answers[q.id];
      if (!a || (q.multi && !a.length)) {
        err.textContent = q.multi ? 'Choose at least one option to continue.' : 'Choose an answer to continue.';
        hide(err, false); var first = stepHost.querySelector('input'); if (first) first.focus(); return;
      }
      if (idx < QUESTIONS.length - 1) { idx++; render(true); } else finish();
    });
    backBtn.addEventListener('click', function () { if (idx > 0) { idx--; render(true); } });

    function finish() {
      var d = decide(answers), r = content(d.key, answers.action);
      last = { d: d, r: r }; helpSent = false;
      var h = '<p class="ind2-k">Your answers suggest starting here</p>' +
        '<h3 class="seoa-title" tabindex="-1">' + esc(r.title) + '</h3>' +
        '<div class="seoa-block"><p class="seoa-h">Why this comes first</p><ul class="pm-list">' +
        d.reasons.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>' +
        (d.conflict ? '<p class="seoa-conflict">' + esc(d.conflict) + '</p>' : '') + '</div>' +
        '<div class="seoa-grid">' +
        '<div class="seoa-block"><p class="seoa-h">What to check before making changes</p><p>' + esc(r.check) + '</p></div>' +
        '<div class="seoa-block"><p class="seoa-h">Your first action</p><p>' + esc(r.first) + '</p></div>' +
        '<div class="seoa-block"><p class="seoa-h">Then</p><ol class="pm-list">' + r.follow.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ol></div>' +
        '<div class="seoa-block"><p class="seoa-h">What to monitor</p><p>' + esc(r.monitor) + '</p></div></div>' +
        '<p class="pm-note seoa-small">' + esc(r.note) + '</p>' +
        '<div class="seoa-block"><p class="seoa-h">What this assessment could not verify</p><ul class="pm-list">' + r.cannot.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div>' +
        '<div class="seoa-actions"><button type="button" class="btn btn-primary" id="seoa-help">Get help with this</button>' +
        '<a class="ma-btn" href="/seo-growth-os" data-seoa-gos="result">Explore SEO Growth OS</a></div>' +
        '<div class="seoa-edit"><button type="button" class="ma-textbtn" id="seoa-edit">Edit my answers</button><button type="button" class="ma-textbtn" id="seoa-restart">Start again</button></div>' +
        '<div class="seoa-help is-hidden" id="seoa-help-box"><p class="seoa-h">Send this to me</p>' +
        '<p class="ma-note">Nothing has been sent. Edit the summary if you like, copy it, then paste it into the contact form. I only see it if you send that form.</p>' +
        '<label class="sr-only" for="seoa-summary">Your summary</label><textarea class="form-textarea seoa-summary" id="seoa-summary" rows="11"></textarea>' +
        '<div class="seoa-actions"><button type="button" class="ma-btn ma-btn--solid" id="seoa-copy">Copy my summary</button>' +
        '<a class="btn btn-primary" href="/contact#contact-form">Open the contact form &rarr;</a></div><p class="ma-small" id="seoa-copy-msg" aria-live="polite"></p></div>';
      out.innerHTML = h;
      hide(wizard, true); hide(out, false);
      live.textContent = 'Your starting point: ' + r.title + '.';
      track('seo_assess_complete', { seo_assess_result: d.key, seo_assess_conflict: !!d.conflict });
      focusTop(out.querySelector('.seoa-title'));
    }
    out.addEventListener('click', function (e) {
      var t = e.target.closest('button'); if (!t || !last) return;
      if (t.id === 'seoa-help') {
        var hb = $('seoa-help-box'), ta = $('seoa-summary');
        if (hb.classList.contains('is-hidden')) { ta.value = summary(answers, last.d, last.r); hide(hb, false); }
        if (!helpSent) { helpSent = true; track('seo_assess_help_click', { seo_assess_result: last.d.key }); }
        ta.focus();
      } else if (t.id === 'seoa-copy') {
        var ta2 = $('seoa-summary'), msg = $('seoa-copy-msg');
        var done = function () { msg.textContent = 'Copied. Paste it into the contact form’s message box.'; track('seo_assess_summary_copy', { seo_assess_result: last.d.key }); };
        var manual = function () { ta2.focus(); ta2.select(); msg.textContent = 'Your browser blocked copying. The summary is selected: press Ctrl+C or Cmd+C.'; };
        if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(ta2.value).then(done, manual); else manual();
      } else if (t.id === 'seoa-edit') {
        hide(out, true); hide(wizard, false); idx = 0; render(true);
      } else if (t.id === 'seoa-restart') {
        answers = {}; last = null; hide(out, true); hide(wizard, false); idx = 0; render(true);
      }
    });
    document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[data-seoa-gos]');
      if (a) track('seo_assess_growth_os_click', { location: a.getAttribute('data-seoa-gos') });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})(this);
