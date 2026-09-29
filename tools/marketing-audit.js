/* HelpMeMarketing marketing check-up: behaviour (v2, 2026-09-29).
 * Content comes from window.HMM_AUDIT (/tools/marketing-audit-content.js).
 * Flow: 3 shared questions, one path of 4 to 6 questions, the capability question, then the plan.
 * Nothing leaves the browser until the visitor presses a send button. The plan lives in the URL
 * hash (#plan=...), so a reload, a copied link or an emailed link reopens the same plan.
 */
(function () {
  'use strict';

  var CONTACT_URL = 'https://script.google.com/macros/s/AKfycbzeefYKM_xZuJHIg9pjl0hTLo57v87Qfpb5DzwvikeyVY3_QdYHFd18zpzlfBsbALSp/exec';
  var TS_SRC = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
  var PAGE_URL = 'https://helpmemarketing.com/tools/marketing-audit';
  var MIN_MS = 3000, TS_WAIT_MS = 10000;

  var C, root, stepHost, fill, count, backBtn, nextBtn, doneBtn, wizard, results, body;
  var answers = {}, idx = 0, started = false, pointerPick = false, current = null;

  /* ---------- helpers ---------- */
  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function track(ev, data) {
    try { window.dataLayer = window.dataLayer || []; var o = { event: ev }; for (var k in data || {}) o[k] = data[k]; window.dataLayer.push(o); } catch (e) {}
  }
  function hide(el, on) { if (el) el.classList.toggle('is-hidden', on); }
  function opt(q, v) { for (var i = 0; i < q.opts.length; i++) if (q.opts[i].v === v) return q.opts[i]; return null; }
  function lower1(s) { return s.charAt(0).toLowerCase() + s.slice(1); }

  /* ---------- steps ---------- */
  function pathKey() { return (answers.buy && answers.goal && answers.stage) ? C.pathFor(answers) : null; }
  function pathQs(pk) {
    return C.paths[pk].qs.filter(function (q) { return !q.when || q.when(answers); });
  }
  function steps() {
    var list = C.shared.map(function (q) { return { q: q, tag: 'About your business' }; });
    var pk = pathKey();
    if (pk) {
      pathQs(pk).forEach(function (q, i) { list.push({ q: q, tag: C.paths[pk].name, intro: i === 0 ? C.paths[pk].intro : '' }); });
      list.push({ q: C.capability, tag: 'Last question' });
    }
    return list;
  }
  function allAnswered() {
    if (!pathKey()) return false;
    return steps().every(function (s) { return !!answers[s.q.id]; });
  }
  function findQ(id) {
    var all = C.shared.concat([C.capability]);
    for (var k in C.paths) all = all.concat(C.paths[k].qs);
    for (var i = 0; i < all.length; i++) if (all[i].id === id) return all[i];
    return null;
  }

  function renderStep(focus) {
    var list = steps(), s = list[idx];
    current = s.q;
    var total = pathKey() ? list.length : 9;
    fill.style.width = Math.round((idx / total) * 100) + '%';
    count.textContent = 'Question ' + (idx + 1) + ' of ' + (pathKey() ? total : 'about ' + total);
    var h = '<fieldset class="ma-q"><legend class="ma-q-legend">' +
      '<span class="ma-q-tag">' + esc(s.tag) + '</span>' +
      (s.intro ? '<span class="ma-q-intro">' + esc(s.intro) + '</span>' : '') +
      '<span class="ma-q-text" tabindex="-1">' + esc(s.q.q) + '</span></legend>' +
      (s.q.hint ? '<p class="ma-q-hint">' + esc(s.q.hint) + '</p>' : '') +
      '<div class="ma-opts">';
    s.q.opts.forEach(function (o) {
      h += '<label class="ma-opt"><input type="radio" name="ma-' + s.q.id + '" value="' + esc(o.v) + '"' +
        (answers[s.q.id] === o.v ? ' checked' : '') + '><span>' + esc(o.label) + '</span></label>';
    });
    h += '</div></fieldset>';
    stepHost.innerHTML = h;
    backBtn.disabled = idx === 0;
    syncNav();
    if (focus) { var t = stepHost.querySelector('.ma-q-text'); if (t) t.focus({ preventScroll: true }); keepInView(); }
  }
  function keepInView() {
    var r = wizard.getBoundingClientRect();
    if (r.top < 72 || r.top > window.innerHeight * 0.4) wizard.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  function syncNav() {
    var list = steps(), last = idx === list.length - 1 && !!pathKey();
    var answered = !!answers[current.id];
    nextBtn.disabled = !answered;
    nextBtn.textContent = last ? 'See my plan' : 'Next';
    /* After a "Change" from the plan, every answer is already there: offer the shortcut back. */
    hide(doneBtn, last || !allAnswered());
  }

  function choose(v) {
    if (!started) { started = true; track('audit_start'); }
    var before = pathKey();
    answers[current.id] = v;
    var after = pathKey();
    if (after && after !== before) track('audit_path_set', { audit_path: after });
    syncNav();
  }
  function next() {
    if (!answers[current.id]) return;
    var list = steps();
    if (idx >= list.length - 1 && pathKey()) return finish();
    idx++; renderStep(true);
  }
  function back() { if (idx > 0) { idx--; renderStep(true); } }

  /* ---------- diagnosis ---------- */
  function diagnose() {
    var pk = pathKey(), P = C.paths[pk], qs = pathQs(pk);
    var sev = {}, trig = {};
    qs.forEach(function (q) {
      var o = opt(q, answers[q.id]);
      if (o && o.p) for (var k in o.p) { sev[k] = (sev[k] || 0) + o.p[k]; (trig[k] = trig[k] || []).push(q); }
    });
    var unsureKey = P.key.map(function (id) { return qs.filter(function (q) { return q.id === id; })[0]; })
      .filter(function (q) { var o = q && opt(q, answers[q.id]); return o && o.unsure; });
    var max = 0; for (var k in sev) max = Math.max(max, sev[k]);
    var boost = P.boost[answers.goal] || [], pid, mode;
    if (max === 0) { pid = unsureKey.length ? P.find : P.fallback; mode = unsureKey.length ? 'find' : 'healthy'; }
    else if (max < 2 && unsureKey.length >= 2) { pid = P.find; mode = 'find'; }
    else {
      var best = -1;
      Object.keys(sev).forEach(function (id) {
        var sc = sev[id] + (boost.indexOf(id) > -1 ? 0.5 : 0), ord = P.order.indexOf(id); if (ord < 0) ord = 99;
        var bOrd = P.order.indexOf(pid); if (bOrd < 0) bOrd = 99;
        if (sc > best || (sc === best && ord < bOrd)) { best = sc; pid = id; }
      });
      mode = 'problem';
    }
    var pr = C.priorities[pid];
    var reasons = [];
    var src = mode === 'problem' ? trig[pid] : mode === 'find' ? unsureKey : [];
    (src || []).forEach(function (q) { reasons.push({ q: q.q, a: opt(q, answers[q.id]).label }); });
    if (mode === 'healthy') qs.slice(0, 3).forEach(function (q) { reasons.push({ q: q.q, a: opt(q, answers[q.id]).label }); });
    var goalBoost = mode === 'problem' && boost.indexOf(pid) > -1;
    var verify = [];
    qs.forEach(function (q) {
      var o = opt(q, answers[q.id]);
      if (o && o.unsure && q.verify && !(mode === 'find' && unsureKey.indexOf(q) > -1)) verify.push(q.verify);
    });
    verify.push('Before you change anything, write down where you are today. ' + pr.measure);
    var actions = typeof pr.actions === 'function' ? pr.actions(answers) : pr.actions;
    return { pk: pk, path: P, pid: pid, pr: pr, mode: mode, reasons: reasons, goalBoost: goalBoost, verify: verify,
      actions: actions, res: C.resources[pr.resource], who: answers.who,
      because: mode === 'healthy' && pr.healthy ? pr.healthy : pr.because };
  }

  /* ---------- plan link ---------- */
  function encode() {
    return steps().map(function (s) { return s.q.id + '.' + answers[s.q.id]; }).join('~');
  }
  function planUrl() { return PAGE_URL + '#plan=' + encode(); }
  function decode(str) {
    var a = {};
    str.split('~').forEach(function (pair) {
      var i = pair.indexOf('.'); if (i < 1) return;
      var id = pair.slice(0, i), v = pair.slice(i + 1), q = findQ(id);
      if (q && opt(q, v)) a[id] = v;
    });
    return a;
  }

  /* ---------- text versions (download, copy, email, contact) ---------- */
  function situationRows() {
    return C.shared.concat([C.capability]).map(function (q) { return { q: q, o: opt(q, answers[q.id]) }; });
  }
  function actionText(a, n, d) {
    var t = n + '. ' + a.do + '\n   How: ' + a.how;
    if (d.who === 'team') t += '\n   Suggested owner: ' + a.owner;
    return t;
  }
  function planText(d, withResource) {
    var L = [];
    L.push('YOUR MARKETING PLAN', 'From the HelpMeMarketing marketing audit', 'Open it again: ' + planUrl(), '');
    L.push('YOUR SITUATION');
    situationRows().forEach(function (r) { L.push('- ' + r.q.short + ': ' + r.o.sum); });
    L.push('', 'YOUR FIRST PRIORITY', d.pr.title, d.pr.plain, '');
    L.push('WHY WE PICKED THIS');
    d.reasons.forEach(function (r) { L.push('- ' + r.q + ' You said: ' + r.a); });
    L.push(d.because, '');
    L.push('WHAT TO CHECK FIRST');
    d.verify.forEach(function (v) { L.push('- ' + v); });
    L.push('', 'YOUR FIRST ACTION', actionText(d.actions[0], 1, d), '');
    L.push('YOUR NEXT TWO ACTIONS', actionText(d.actions[1], 2, d), actionText(d.actions[2], 3, d), '');
    L.push('HOW TO KNOW IT IS WORKING', 'Measure: ' + d.pr.measure, 'Check again ' + d.pr.review + '.');
    if (d.who === 'team') { L.push('', 'TEAM REVIEW CHECKLIST'); d.pr.review_list.forEach(function (x) { L.push('[ ] ' + x); }); }
    if (d.who === 'agency') {
      L.push('', 'QUESTIONS TO SEND YOUR AGENCY OR FREELANCER'); d.pr.agency.forEach(function (x) { L.push('- ' + x); });
      L.push('', 'EVIDENCE TO ASK FOR'); d.pr.evidence.forEach(function (x) { L.push('- ' + x); });
    }
    if (d.who === 'help') L.push('', 'THE KIND OF HELP THAT FITS', d.pr.help);
    if (withResource) {
      L.push('', '', '==== ' + d.res.name.toUpperCase() + ' ====', '');
      d.res.body.forEach(function (sec) { L.push(sec[0].toUpperCase()); sec[1].forEach(function (x) { L.push(x); }); L.push(''); });
      if (d.res.csv) L.push('The tracker is a separate spreadsheet file. Download it from your plan page.');
    }
    return L.join('\n');
  }
  function teamText(d) {
    var L = ['Marketing audit summary', ''];
    L.push('How we sell: ' + opt(C.shared[0], answers.buy).sum);
    L.push('Goal: ' + opt(C.shared[1], answers.goal).sum);
    L.push('First priority: ' + d.pr.title);
    L.push('Why: ' + d.because);
    L.push('First action: ' + d.actions[0].do);
    L.push('Then: ' + d.actions[1].do + ' ' + d.actions[2].do);
    L.push('How we will know: ' + d.pr.measure + ' Check again ' + d.pr.review + '.');
    L.push('', 'Questions to talk about:');
    d.pr.agency.forEach(function (x) { L.push('- ' + x); });
    L.push('', 'Full plan: ' + planUrl());
    return L.join('\n');
  }
  function contactSummary(d) {
    return [
      'How customers buy: ' + opt(C.shared[0], answers.buy).label,
      'Goal: ' + opt(C.shared[1], answers.goal).label,
      'Where the business is: ' + opt(C.shared[2], answers.stage).label,
      'First priority: ' + d.pr.title,
      'Who makes changes: ' + opt(C.capability, answers.who).label,
      'Help I would like: ' + d.pr.topic.replace(/\byour\b/g, 'our').replace(/\byou\b/g, 'we'),
      'Plan: ' + planUrl()
    ].join('\n');
  }

  /* ---------- results ---------- */
  function actionHTML(a, n, d) {
    return '<li class="ma-act"><span class="ma-act-n" aria-hidden="true">' + n + '</span><div><p class="ma-act-do">' + esc(a.do) + '</p>' +
      '<p class="ma-act-how">' + esc(a.how) + '</p>' +
      (d.who === 'team' ? '<p class="ma-act-owner">Suggested owner: ' + esc(a.owner) + '</p>' : '') + '</div></li>';
  }
  function list(items) { return '<ul class="ma-list">' + items.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>'; }

  function renderResults(d) {
    var pr = d.pr, h = '';
    var rows = situationRows();
    h += '<div class="ma-block ma-situation"><h3 class="ma-h">Your situation</h3><dl class="ma-sit">';
    rows.forEach(function (r) {
      h += '<div class="ma-sit-row"><dt>' + esc(r.q.short) + '</dt><dd>' + esc(r.o.sum) +
        ' <button type="button" class="ma-link" data-edit="' + r.q.id + '">Change<span class="sr-only"> ' + esc(lower1(r.q.short)) + '</span></button></dd></div>';
    });
    h += '</dl><details class="ma-more"><summary>Your other answers (' + pathQs(d.pk).length + ')</summary><dl class="ma-sit">';
    pathQs(d.pk).forEach(function (q) {
      h += '<div class="ma-sit-row"><dt>' + esc(q.short) + '</dt><dd>' + esc(opt(q, answers[q.id]).label) +
        ' <button type="button" class="ma-link" data-edit="' + q.id + '">Change<span class="sr-only"> ' + esc(lower1(q.short)) + '</span></button></dd></div>';
    });
    h += '</dl></details></div>';

    h += '<div class="ma-block ma-priority"><p class="ma-eyebrow">Your first priority</p><h2 class="ma-title" id="ma-title" tabindex="-1">' + esc(pr.title) + '</h2><p class="ma-plain">' + esc(pr.plain) + '</p></div>';

    h += '<div class="ma-block"><h3 class="ma-h">Why we picked this</h3>';
    if (d.reasons.length) {
      h += '<ul class="ma-list ma-reasons">' + d.reasons.map(function (r) { return '<li><span class="ma-rq">' + esc(r.q) + '</span> You said: <strong>' + esc(r.a) + '</strong></li>'; }).join('') + '</ul>';
    }
    h += '<p class="ma-p">' + esc(d.because) + (d.goalBoost ? ' It also matches what you said you want most: ' + esc(lower1(opt(C.shared[1], answers.goal).sum)) + '.' : '') + '</p></div>';

    h += '<div class="ma-block"><h3 class="ma-h">What to check first</h3>' +
      (d.mode === 'find' ? '<p class="ma-p">We can&rsquo;t be sure yet, so your first action below is to find out. That is a normal and useful first step.</p>' : '') +
      list(d.verify) + '</div>';

    h += '<div class="ma-block"><h3 class="ma-h">Your first action</h3><ol class="ma-acts">' + actionHTML(d.actions[0], 1, d) + '</ol>' +
      '<p class="ma-small">' + ({ team: 'Your team can start this today.', agency: 'You can start this today, or ask your agency or freelancer to.' }[d.who] || 'You can start this today, without talking to anyone.') + '</p></div>';
    h += '<div class="ma-block"><h3 class="ma-h">Your next two actions</h3><ol class="ma-acts">' + actionHTML(d.actions[1], 2, d) + actionHTML(d.actions[2], 3, d) + '</ol></div>';

    h += '<div class="ma-block"><h3 class="ma-h">How to know it&rsquo;s working</h3><p class="ma-p"><strong>Measure:</strong> ' + esc(pr.measure) + '</p>' +
      '<p class="ma-p"><strong>Check again</strong> ' + esc(pr.review) + '.</p>';
    if (d.who === 'team') h += '<p class="ma-sub">Team review checklist</p>' + list(pr.review_list.map(function (x) { return x; }));
    h += '</div>';

    if (d.who === 'agency') {
      h += '<div class="ma-block ma-agency"><h3 class="ma-h">For your agency or freelancer</h3><p class="ma-sub">Questions to send</p>' + list(pr.agency) +
        '<p class="ma-sub">Evidence to ask for</p>' + list(pr.evidence) +
        '<button type="button" class="ma-btn" data-copy="agency">Copy these questions</button></div>';
    }
    if (d.who === 'help') {
      h += '<div class="ma-block ma-agency"><h3 class="ma-h">The kind of help that fits</h3><p class="ma-p">' + esc(pr.help) + '</p>' +
        '<p class="ma-small">You can take this plan to anyone you trust. Nobody will contact you unless you ask.</p></div>';
    }

    h += '<div class="ma-block ma-resource"><h3 class="ma-h">Your free resource</h3><p class="ma-eyebrow">' + esc(d.res.kind) + '</p>' +
      '<p class="ma-res-name">' + esc(d.res.name) + '</p><p class="ma-p">' + esc(d.res.blurb) + '</p><div class="ma-btns">' +
      '<button type="button" class="ma-btn ma-btn--main" data-dl="plan">Download plan and ' + esc(d.res.kind.toLowerCase()) + '</button>' +
      (d.res.csv ? '<button type="button" class="ma-btn" data-dl="csv">Download the spreadsheet</button>' : '') + '</div></div>';

    body.innerHTML = h;

    /* Next steps: text that depends on the result. */
    $('ma-next-team-h').textContent = d.who === 'agency' ? 'I want to share this with my agency' : 'I want to discuss this with my team';
    $('ma-next-help-p').textContent = 'Talk with Ankit about ' + d.pr.topic + '. Your answers come with you, so you won’t need to explain again.';
    $('ma-contact-h').textContent = 'Get help with ' + lower1(d.pr.area);
    $('ma-sum').value = contactSummary(d);
    resetContact();
  }

  var last = null;
  function finish(fromLink) {
    var d = diagnose(); last = d;
    renderResults(d);
    hide(wizard, true); hide(results, false);
    try { history.replaceState(null, '', '#plan=' + encode()); } catch (e) {}
    refreshMailto();
    track('audit_complete', { audit_path: d.pk, audit_priority: d.pid, audit_capability: d.who, audit_mode: d.mode, audit_from_link: !!fromLink });
    var t = $('ma-title');
    results.scrollIntoView({ behavior: fromLink ? 'auto' : 'smooth', block: 'start' });
    if (t && !fromLink) t.focus({ preventScroll: true });
  }
  function edit(id) {
    var list = steps();
    for (var i = 0; i < list.length; i++) if (list[i].q.id === id) { idx = i; break; }
    track('audit_edit', { question: id });
    hide(results, true); hide(wizard, false);
    try { history.replaceState(null, '', location.pathname); } catch (e) {}
    renderStep(true);
  }
  function restart() {
    answers = {}; idx = 0; last = null;
    hide(results, true); hide(wizard, false);
    try { history.replaceState(null, '', location.pathname); } catch (e) {}
    renderStep(true);
  }

  /* ---------- saving and sharing ---------- */
  function download(name, text, type) {
    var blob = new Blob([text], { type: type }), url = URL.createObjectURL(blob), a = document.createElement('a');
    a.href = url; a.download = name; document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(url); a.remove(); }, 500);
  }
  function csvText(cols) { return '﻿' + cols.map(function (c) { return '"' + c.replace(/"/g, '""') + '"'; }).join(',') + '\r\n'; }
  function slug(s) { return s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''); }
  function copy(text, btn) {
    function ok() { if (!btn) return; var t = btn.textContent; btn.textContent = 'Copied'; btn.classList.add('is-done'); setTimeout(function () { btn.textContent = t; btn.classList.remove('is-done'); }, 2000); }
    function fallback() { var ta = document.createElement('textarea'); ta.value = text; ta.setAttribute('readonly', ''); ta.className = 'ma-offscreen'; document.body.appendChild(ta); ta.select(); try { document.execCommand('copy'); ok(); } catch (e) {} ta.remove(); }
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(ok, fallback); else fallback();
  }

  function onResultsClick(e) {
    var t = e.target.closest('button,a'); if (!t || !last) return;
    var d = last;
    if (t.hasAttribute('data-edit')) return edit(t.getAttribute('data-edit'));
    var dl = t.getAttribute('data-dl');
    if (dl === 'plan') { download('hmm-plan-' + slug(d.pr.title) + '.txt', planText(d, true), 'text/plain;charset=utf-8'); track('audit_download', { file: 'plan', audit_priority: d.pid }); track('audit_next_step', { choice: 'self_download' }); return; }
    if (dl === 'csv') { download('hmm-' + slug(d.res.name) + '.csv', csvText(d.res.columns), 'text/csv;charset=utf-8'); track('audit_download', { file: 'csv', audit_priority: d.pid }); return; }
    var cp = t.getAttribute('data-copy');
    if (cp === 'plan') { copy(planText(d, true), t); track('audit_copy', { what: 'plan' }); track('audit_next_step', { choice: 'self_copy' }); return; }
    if (cp === 'team') { copy(teamText(d), t); track('audit_copy', { what: 'team' }); track('audit_next_step', { choice: 'team' }); return; }
    if (cp === 'agency') { copy(d.pr.agency.map(function (x, i) { return (i + 1) + '. ' + x; }).join('\n') + '\n\nEvidence I would like to see:\n' + d.pr.evidence.map(function (x) { return '- ' + x; }).join('\n'), t); track('audit_copy', { what: 'agency' }); return; }
    if (cp === 'link') { copy(planUrl(), t); track('audit_copy', { what: 'link' }); return; }
    if (t.id === 'ma-open-contact') { openContact(); return; }
    if (t.id === 'ma-mailto') { track('audit_email_plan', { method: 'mailto' }); return; }
    if (t.id === 'ma-restart') { restart(); return; }
    var fb = t.getAttribute('data-feedback');
    if (fb) { sendFeedback(fb); return; }
  }

  function endpoint() { return (root.getAttribute('data-plan-endpoint') || '').trim(); }
  function setupSave() {
    var ep = endpoint();
    hide($('ma-email-form'), !ep); hide($('ma-mailto'), !!ep); hide($('ma-sub-wrap'), !ep);
  }
  function refreshMailto() {
    if (!last) return;
    var body = teamText(last).replace(/^Marketing audit summary/, 'My marketing plan');
    $('ma-mailto').href = 'mailto:?subject=' + encodeURIComponent('My marketing plan: ' + last.pr.title) + '&body=' + encodeURIComponent(body);
  }
  function postJSON(payload) {
    return fetch(endpoint(), { method: 'POST', mode: 'no-cors', headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: JSON.stringify(payload) });
  }
  function validEmail(v) { return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v); }
  function setupEmailForms() {
    var ef = $('ma-email-form'), sf = $('ma-sub-form');
    ef.addEventListener('submit', function (e) {
      e.preventDefault(); if (!last) return;
      var inp = $('ma-email'), msg = $('ma-email-msg'), v = inp.value.trim();
      if (!validEmail(v)) { msg.textContent = 'Please enter a valid email address.'; inp.setAttribute('aria-invalid', 'true'); inp.focus(); return; }
      inp.removeAttribute('aria-invalid');
      if ($('ma-email-hp').value) { msg.textContent = 'Sent. Check your inbox in a few minutes.'; return; }
      msg.textContent = 'Sending…';
      postJSON({ action: 'plan', email: v, plan_title: last.pr.title, plan_text: planText(last, true), plan_url: planUrl(), path: last.pk, priority: last.pid })
        .then(function () { msg.textContent = 'Sent. Check your inbox in a few minutes.'; ef.reset(); track('audit_email_plan', { method: 'server' }); },
          function () { msg.textContent = 'That did not work. Please use Download or Copy instead.'; });
    });
    sf.addEventListener('submit', function (e) {
      e.preventDefault();
      var inp = $('ma-sub-email'), msg = $('ma-sub-msg'), v = inp.value.trim();
      if (!validEmail(v)) { msg.textContent = 'Please enter a valid email address.'; inp.setAttribute('aria-invalid', 'true'); inp.focus(); return; }
      inp.removeAttribute('aria-invalid');
      if ($('ma-sub-hp').value) { msg.textContent = 'You’re subscribed. Thank you.'; return; }
      msg.textContent = 'Sending…';
      postJSON({ action: 'subscribe', email: v, source: 'marketing-audit' })
        .then(function () { msg.textContent = 'You’re subscribed. Thank you.'; sf.reset(); track('audit_subscribe'); },
          function () { msg.textContent = 'That did not work. Please try again later.'; });
    });
  }
  function sendFeedback(v) {
    var labels = { yes: 'Yes', partly: 'Partly', no: 'No' };
    $('ma-fb-btns').classList.add('is-hidden');
    $('ma-fb-thanks').textContent = v === 'no'
      ? 'Thanks for telling us. Try the first action anyway, or change an answer above if something did not fit.'
      : 'Thanks for telling us.';
    track('audit_feedback', { answer: labels[v], audit_priority: last && last.pid });
    if (endpoint() && last) postJSON({ action: 'feedback', answer: labels[v], path: last.pk, priority: last.pid }).catch(function () {});
  }

  /* ---------- contact (carries the plan forward) ---------- */
  var cf, human = false, t0 = Date.now(), sending = false;
  var ts = { key: '', started: false, token: '', interactive: false, failed: false };
  function loadTurnstile() {
    ts.key = (cf.getAttribute('data-turnstile-sitekey') || '').trim();
    if (!ts.key || ts.started) return; ts.started = true;
    var sc = document.createElement('script'); sc.src = TS_SRC; sc.async = true;
    sc.addEventListener('error', function () { ts.failed = true; });
    sc.addEventListener('load', function () {
      if (!window.turnstile) { ts.failed = true; return; }
      try {
        window.turnstile.render('#ma-turnstile', {
          sitekey: ts.key, action: 'contact', theme: 'dark', size: 'flexible', appearance: 'interaction-only',
          callback: function (t) { ts.token = t; ts.failed = false; ts.interactive = false; },
          'expired-callback': function () { ts.token = ''; },
          'error-callback': function () { ts.failed = true; },
          'before-interactive-callback': function () { ts.interactive = true; },
          'after-interactive-callback': function () { ts.interactive = false; }
        });
      } catch (e) { ts.failed = true; }
    });
    document.head.appendChild(sc);
  }
  function waitForToken() {
    return new Promise(function (res) { var s = Date.now(); (function poll() { if (ts.token || ts.failed || ts.interactive || Date.now() - s > TS_WAIT_MS) return res(); setTimeout(poll, 150); })(); });
  }
  function resetContact() {
    hide($('ma-contact'), true); hide(cf, false); hide($('ma-thanks'), true); hide($('ma-cerr'), true);
  }
  function openContact() {
    var box = $('ma-contact');
    hide(box, false);
    track('audit_next_step', { choice: 'contact' });
    track('audit_contact_open', { audit_priority: last && last.pid });
    box.scrollIntoView({ behavior: 'smooth', block: 'start' });
    setTimeout(function () { $('ma-sum').focus({ preventScroll: true }); }, 400);
  }
  function setupContact() {
    cf = $('ma-cform'); if (!cf) return;
    ['pointerdown', 'keydown', 'touchstart', 'input'].forEach(function (t) { cf.addEventListener(t, function () { human = true; }, { passive: true }); });
    cf.addEventListener('focusin', loadTurnstile);
    cf.addEventListener('pointerdown', loadTurnstile);
    var err = $('ma-cerr'), btn = $('ma-csend');
    function show(msg, el) { err.textContent = msg; hide(err, false); if (el) { el.setAttribute('aria-invalid', 'true'); el.focus(); } }
    function clear() { hide(err, true); cf.querySelectorAll('[aria-invalid]').forEach(function (el) { el.removeAttribute('aria-invalid'); }); }
    function busy(on) { sending = on; btn.disabled = on; btn.textContent = on ? 'Sending…' : 'Send to Ankit'; }
    function done(first) {
      $('ma-thanks-name').textContent = first ? ', ' + first : '';
      hide(cf, true); var th = $('ma-thanks'); hide(th, false); th.focus({ preventScroll: true });
      th.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    cf.addEventListener('submit', function (e) {
      e.preventDefault(); if (sending) return; clear();
      var sum = $('ma-sum').value.trim(), name = $('ma-name').value.trim(), email = $('ma-cemail').value.trim();
      var site = $('ma-site').value.trim(), notes = $('ma-notes').value.trim();
      if (site && !/^https?:\/\//i.test(site)) site = 'https://' + site;
      if (!name) return show('Please tell us your name.', $('ma-name'));
      if (!validEmail(email)) return show('Please enter a valid email address.', $('ma-cemail'));
      if (site && !/^https?:\/\/[^\s\/.]+\.[^\s]{2,}$/i.test(site)) return show('Please check your website, for example yourbusiness.com, or leave it blank.', $('ma-site'));
      if (!sum) return show('Please keep a short summary so Ankit knows what you need.', $('ma-sum'));
      var first = name.split(/\s+/)[0];
      /* Bot guard, same as /contact: honeypot, three-second minimum, a real key, pointer, touch or input event. */
      if ($('ma-chp').value || Date.now() - t0 < MIN_MS || !human) { done(first); return; }
      busy(true); loadTurnstile();
      (ts.key ? waitForToken() : Promise.resolve()).then(function () {
        if (ts.key && !ts.token && ts.interactive) { busy(false); show('Please complete the quick security check just above the button.'); return; }
        var fd = new FormData();
        fd.append('name', name); fd.append('email', email); fd.append('phone', '');
        fd.append('website', site || 'Not given');
        fd.append('help_with[]', '[From the marketing audit]\n' + sum);
        fd.append('biggest_challenge', notes);
        if (ts.key) fd.append('cf-turnstile-response', ts.token);
        return fetch(CONTACT_URL, { method: 'POST', mode: 'no-cors', body: fd }).then(function () {
          track('audit_contact_submit', { audit_priority: last && last.pid, audit_path: last && last.pk });
          done(first);
        });
      }).catch(function () {
        busy(false);
        show('Something went wrong. Please email Hello@helpmemarketing.com and we will reply right away.');
      });
    });
  }

  /* ---------- start ---------- */
  function init() {
    C = window.HMM_AUDIT; root = $('ma'); if (!C || !root) return;
    wizard = $('ma-wizard'); results = $('ma-results'); body = $('ma-results-body');
    stepHost = $('ma-step'); fill = $('ma-fill'); count = $('ma-count');
    backBtn = $('ma-back'); nextBtn = $('ma-next'); doneBtn = $('ma-done');
    root.classList.add('is-ready');

    stepHost.addEventListener('pointerdown', function () { pointerPick = true; });
    stepHost.addEventListener('keydown', function () { pointerPick = false; });
    stepHost.addEventListener('change', function (e) {
      if (e.target.type !== 'radio') return;
      choose(e.target.value);
      /* A tap or click moves on by itself; arrow keys only select, so keyboard users are never pushed along. */
      if (pointerPick) { pointerPick = false; var at = idx; setTimeout(function () { if (idx === at) next(); }, 260); }
    });
    nextBtn.addEventListener('click', next);
    backBtn.addEventListener('click', back);
    doneBtn.addEventListener('click', function () { if (allAnswered()) finish(); });
    results.addEventListener('click', onResultsClick);

    setupSave(); setupEmailForms(); setupContact();

    var m = /[#&]plan=([^&]+)/.exec(location.hash);
    if (m) {
      answers = decode(decodeURIComponent(m[1]));
      if (allAnswered()) { idx = steps().length - 1; renderStep(false); finish(true); return; }
      answers = {};
    }
    renderStep(false);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
