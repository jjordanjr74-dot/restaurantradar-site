/* Safe-Stop filter wiring.
 *
 * The six .safe-filter buttons rendered on the live page had data-filter attributes but no
 * handler at all, so clicking "Wheelchair / ADA" or "Fenced Dog Run" changed nothing — a dead
 * control on the main conversion surface. This module owns that behaviour: it toggles the
 * pressed state, filters the stop cards by the badges they already carry, announces the new
 * count to screen readers, and shows an honest empty state when a filter matches nothing.
 */
(function () {
  'use strict';

  var LABELS = {
    lit: /(🌙|well-lit|high-lumen|security)/i,
    bath: /(🚻|restroom|family bathroom)/i,
    dog: /(🐕|dog run|pet exercise)/i,
    ada: /(♿|ada|zero-step)/i,
    food: /(🍖|kitchen open|open 24\/7)/i
  };

  function cards() {
    var grid = document.getElementById('stopCardsGrid');
    if (!grid) return [];
    return Array.prototype.slice.call(grid.children).filter(function (el) {
      return el.nodeType === 1 && el.classList.contains('feature-card');
    });
  }

  function emptyState(grid, show, activeKey) {
    var note = document.getElementById('safeFilterEmpty');
    if (!show) {
      if (note) note.hidden = true;
      return;
    }
    if (!note) {
      note = document.createElement('p');
      note.id = 'safeFilterEmpty';
      note.setAttribute('role', 'status');
      note.style.cssText = 'margin:18px 0;padding:14px 16px;border-radius:10px;' +
        'border:1px solid #10b981;background:rgba(16,185,129,0.08);color:#0f172a;font-weight:600';
      grid.parentNode.insertBefore(note, grid.nextSibling);
    }
    var btn = document.querySelector('.safe-filter[data-filter="' + activeKey + '"]');
    var label = btn ? btn.textContent.replace(/^\W+\s*/, '').trim() : activeKey;
    note.textContent = 'No corridor stop in this list is tagged "' + label +
      '" yet. Try another filter, or call ahead to confirm before you pull off the highway.';
    note.hidden = false;
  }

  function apply(key) {
    var all = cards();
    var count = 0;
    var matcher = LABELS[key];
    all.forEach(function (card) {
      var keep = key === 'all' || !matcher ? true : matcher.test(card.textContent || '');
      card.hidden = !keep;
      if (keep) count += 1;
    });
    var grid = document.getElementById('stopCardsGrid');
    if (grid) {
      emptyState(grid, count === 0 && key !== 'all', key);
      var live = document.getElementById('safeFilterCount');
      if (!live) {
        live = document.createElement('p');
        live.id = 'safeFilterCount';
        live.setAttribute('aria-live', 'polite');
        live.style.cssText = 'margin:-14px 0 18px;font-size:13px;font-weight:600;color:#334155';
        grid.parentNode.insertBefore(live, grid);
      }
      live.textContent = key === 'all'
        ? 'Showing all ' + count + ' corridor stops.'
        : 'Showing ' + count + ' of ' + all.length + ' corridor stops matching this filter.';
    }
  }

  function setActive(btn) {
    var bar = btn.closest('.safe-filter-bar') || document;
    Array.prototype.forEach.call(bar.querySelectorAll('.safe-filter'), function (b) {
      var on = b === btn;
      b.classList.toggle('is-active', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  }

  function boot() {
    var filters = document.querySelectorAll('.safe-filter[data-filter]');
    if (!filters.length) return;
    Array.prototype.forEach.call(filters, function (btn) {
      btn.setAttribute('aria-pressed', btn.classList.contains('is-active') ? 'true' : 'false');
    });
    document.addEventListener('click', function (ev) {
      var btn = ev.target.closest && ev.target.closest('.safe-filter[data-filter]');
      if (!btn) return;
      ev.preventDefault();
      setActive(btn);
      apply(btn.getAttribute('data-filter'));
    });
    apply('all');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();