
    document.documentElement.classList.add('js');
    (function () {
      fetch('assets/app_url.json').then(function (r) { return r.json(); }).then(function (j) {
        if (!j || !j.url) return;
        document.querySelectorAll('[data-app-url]').forEach(function (a) {
          var key = a.getAttribute('data-app-url');
          if (j[key]) a.setAttribute('href', j[key]);
        });
      }).catch(function () {});
    })();
    (function () {
      var btn = document.getElementById('hamburger'); var nav = document.getElementById('siteNav');
      if (!btn || !nav) return;
      btn.addEventListener('click', function () { var open = nav.classList.toggle('open'); btn.setAttribute('aria-expanded', open ? 'true' : 'false'); btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu'); });
      nav.addEventListener('click', function (e) { if (e.target.tagName === 'A') { nav.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); } });
      document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { nav.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); } });
    })();
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('is-visible'); io.unobserve(e.target); } }); }, { threshold: 0.12 });
      document.querySelectorAll('.reveal').forEach(function (el) { io.observe(el); });
    } else { document.querySelectorAll('.reveal').forEach(function (el) { el.classList.add('is-visible'); }); }
    // Scroll/resize sweep — fail-safe so in-view content never stays hidden
    (function () {
      function sweep() {
        document.querySelectorAll('.reveal:not(.is-visible)').forEach(function (el) {
          var r = el.getBoundingClientRect();
          if (r.top < window.innerHeight && r.bottom > 0) el.classList.add('is-visible');
        });
      }
      window.addEventListener('scroll', sweep, { passive: true });
      window.addEventListener('resize', sweep);
      setTimeout(sweep, 600);
    })();
    (function () { var el = document.getElementById('yr'); if (el) el.textContent = new Date().getFullYear(); })();
    if ('serviceWorker' in navigator) { navigator.serviceWorker.register('/sw.js').catch(function () {}); }
    (function () {
      var es = {
        'Simple, honest pricing': 'Precios simples y honestos',
        'Founding Professional': 'Profesional Fundador',
        'City License': 'Licencia Municipal',
        'How Restaurant Radar Compares to National Ad & Reservation Platforms': 'Cómo Se Compara Restaurant Radar en la Economía Actual',
        'Asked before subscribing': 'Preguntas frecuentes antes de suscribirse'
      };
      var rev = {}; Object.keys(es).forEach(function (k) { rev[es[k]] = k; });
      var bEn = document.getElementById('langEn'); var bEs = document.getElementById('langEs');
      if (!bEn || !bEs) return;
      function setLang(l) {
        var d = l === 'es' ? es : rev;
        document.querySelectorAll('h1,h2,h3,a').forEach(function (el) {
          if (el.children.length === 0) { var t = (el.textContent || '').trim(); if (d[t]) el.textContent = d[t]; }
        });
        bEn.classList.toggle('active', l !== 'es');
        bEs.classList.toggle('active', l === 'es');
      }
      bEn.onclick = function () { setLang('en'); }; bEs.onclick = function () { setLang('es'); };
      if (new URLSearchParams(location.search).get('lang') === 'es') setLang('es');
    })();
  