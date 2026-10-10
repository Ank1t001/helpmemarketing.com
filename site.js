/*
 * HelpMeMarketing shared page behaviour, loaded on every page via
 * <script src="/site.js" defer>. Replaces the inline onclick that the nav
 * hamburger carried on every page until 2026-09-18. Keep this file to
 * sitewide chrome only; page features live in their own scripts.
 */
(function () {
  'use strict';

  function initNav() {
    var btn = document.querySelector('.nav-hamburger');
    var menu = document.querySelector('.nav-mobile-menu');
    if (!btn || !menu) return;

    function setOpen(open) {
      menu.classList.toggle('open', open);
      btn.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    }

    btn.addEventListener('click', function () {
      setOpen(!menu.classList.contains('open'));
    });
    // A tap on a menu link (including a same-page anchor) closes the menu.
    menu.addEventListener('click', function (e) {
      if (e.target.closest('a')) setOpen(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menu.classList.contains('open')) { setOpen(false); btn.focus(); }
    });
    document.addEventListener('click', function (e) {
      if (!menu.classList.contains('open')) return;
      if (menu.contains(e.target) || btn.contains(e.target)) return;
      setOpen(false);
    });
  }

  // Light/dark switch, on pages that carry [data-theme-toggle] buttons (homepage footer and phone menu since 2026-10-09).
  // The inline head script has already set html[data-theme]: the saved choice, else dark (the default).
  function initTheme() {
    var btns = document.querySelectorAll('[data-theme-toggle]');
    if (!btns.length) return;
    var root = document.documentElement, meta = document.querySelector('meta[name="theme-color"]');
    function apply(t) {
      root.setAttribute('data-theme', t);
      btns.forEach(function (b) {
        b.setAttribute('aria-label', t === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
        b.setAttribute('aria-pressed', t === 'dark' ? 'true' : 'false');
        var lbl = b.querySelector('[data-theme-label]');
        if (lbl) lbl.textContent = t === 'dark' ? 'Light mode' : 'Dark mode';
      });
      if (meta) meta.setAttribute('content', t === 'dark' ? '#0E0E0E' : '#FFFFFF');
    }
    apply(root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light');
    btns.forEach(function (b) {
      b.addEventListener('click', function () {
        var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        try { localStorage.setItem('hmm_theme', next); } catch (e) {}
        apply(next);
      });
    });
  }

  function init() { initNav(); initTheme(); }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
