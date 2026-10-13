const CACHE = 'radar-v2';
const SHELL = [
  '/',
  '/index.html',
  '/pricing.html',
  '/city-license.html',
  '/privacy.html',
  '/assets/site.css',
  '/assets/icon.svg',
  '/assets/img/product-map.png',
  '/assets/img/og-image.png',
  '/manifest.json'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE).then(function(cache) {
      return cache.addAll(SHELL);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(
        keys.filter(function(k) { return k !== CACHE; }).map(function(k) {
          return caches.delete(k);
        })
      );
    }).then(function() { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function(event) {
  var url = new URL(event.request.url);
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request).catch(function() {
        return caches.match(event.request);
      })
    );
    return;
  }
  event.respondWith(
    caches.match(event.request).then(function(cached) {
      if (cached) return cached;
      return fetch(event.request).then(function(response) {
        caches.open(CACHE).then(function(cache) {
          cache.put(event.request, response.clone());
        });
        return response;
      });
    })
  );
});