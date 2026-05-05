/* HelpMeMarketing — Blog Template V2 (D-hybrid)
 * Auto-generates TOC, drives active-section highlighting via
 * IntersectionObserver, handles mobile collapsible TOC, and wires
 * up share-icon click handlers. Single source of truth for all
 * blog pages using the V2 template.
 */
(function () {
  'use strict';

  function init() {
    var headings = document.querySelectorAll('.blog-content h2[id]');
    if (headings.length === 0) return;

    var tocList = document.querySelector('.toc-list');
    var tocListMobile = document.querySelector('.toc-list-mobile');

    // Build desktop TOC
    if (tocList) {
      headings.forEach(function (h) {
        var li = document.createElement('li');
        li.className = 'toc-item';
        li.dataset.target = h.id;
        li.textContent = h.textContent;
        li.setAttribute('role', 'link');
        li.setAttribute('tabindex', '0');
        li.addEventListener('click', function () {
          scrollToHeading(h.id);
        });
        li.addEventListener('keydown', function (e) {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            scrollToHeading(h.id);
          }
        });
        tocList.appendChild(li);
      });
    }

    // Build mobile TOC (mirror desktop)
    if (tocListMobile) {
      headings.forEach(function (h) {
        var li = document.createElement('li');
        li.dataset.target = h.id;
        li.textContent = h.textContent;
        li.setAttribute('role', 'link');
        li.setAttribute('tabindex', '0');
        li.addEventListener('click', function () {
          scrollToHeading(h.id);
          closeMobilePanel();
        });
        li.addEventListener('keydown', function (e) {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            scrollToHeading(h.id);
            closeMobilePanel();
          }
        });
        tocListMobile.appendChild(li);
      });
    }

    function scrollToHeading(id) {
      var target = document.getElementById(id);
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }

    function closeMobilePanel() {
      var panel = document.querySelector('.toc-mobile-panel');
      var toggle = document.querySelector('.toc-mobile-toggle');
      if (panel && toggle) {
        panel.classList.remove('open');
        toggle.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    }

    // Active section highlighting
    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              var id = entry.target.id;
              document.querySelectorAll('.toc-item').forEach(function (i) {
                i.classList.remove('active');
              });
              var activeItem = document.querySelector(
                '.toc-item[data-target="' + id + '"]'
              );
              if (activeItem) activeItem.classList.add('active');
            }
          });
        },
        {
          rootMargin: '-80px 0px -60% 0px',
          threshold: 0
        }
      );
      headings.forEach(function (h) {
        observer.observe(h);
      });
    }

    // Mobile collapsible TOC toggle
    var mobileToggle = document.querySelector('.toc-mobile-toggle');
    var mobilePanel = document.querySelector('.toc-mobile-panel');
    if (mobileToggle && mobilePanel) {
      mobileToggle.addEventListener('click', function () {
        var isOpen = mobilePanel.classList.toggle('open');
        mobileToggle.classList.toggle('open', isOpen);
        mobileToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      });
    }

    // Share icon handlers
    var shareIcons = document.querySelectorAll('.share-icon[data-network]');
    shareIcons.forEach(function (icon) {
      icon.addEventListener('click', function (e) {
        e.preventDefault();
        var network = icon.dataset.network;
        var pageUrl = window.location.href;
        var pageTitle = document.title;
        var shareUrl = '';

        if (network === 'linkedin') {
          shareUrl =
            'https://www.linkedin.com/sharing/share-offsite/?url=' +
            encodeURIComponent(pageUrl);
        } else if (network === 'x') {
          shareUrl =
            'https://twitter.com/intent/tweet?url=' +
            encodeURIComponent(pageUrl) +
            '&text=' +
            encodeURIComponent(pageTitle);
        } else if (network === 'facebook') {
          shareUrl =
            'https://www.facebook.com/sharer/sharer.php?u=' +
            encodeURIComponent(pageUrl);
        } else if (network === 'copy') {
          copyToClipboard(pageUrl, icon);
          return;
        }

        if (shareUrl) {
          window.open(shareUrl, '_blank', 'noopener,noreferrer');
        }
      });
    });

    function copyToClipboard(text, icon) {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(
          function () {
            showCopiedFeedback(icon);
          },
          function () {
            fallbackCopy(text, icon);
          }
        );
      } else {
        fallbackCopy(text, icon);
      }
    }

    function fallbackCopy(text, icon) {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      ta.setAttribute('readonly', '');
      document.body.appendChild(ta);
      ta.select();
      try {
        document.execCommand('copy');
        showCopiedFeedback(icon);
      } catch (e) {
        /* silent */
      }
      document.body.removeChild(ta);
    }

    function showCopiedFeedback(icon) {
      // Remove any existing tooltip first
      var existing = icon.querySelector('.share-icon-tooltip');
      if (existing) icon.removeChild(existing);

      var tooltip = document.createElement('span');
      tooltip.className = 'share-icon-tooltip';
      tooltip.textContent = 'Copied!';
      icon.appendChild(tooltip);

      setTimeout(function () {
        if (tooltip.parentNode === icon) {
          icon.removeChild(tooltip);
        }
      }, 2000);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
