const CACHE_NAME = 'jeremi-v1';
const urlsToCache = [
  '/',
  '/static/manifest.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(names =>
      Promise.all(names.filter(n => n !== CACHE_NAME).map(n => caches.delete(n)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  // Network-first for socket.io and dynamic content, cache-first for static
  if (event.request.url.includes('/socket.io/')) {
    return; // Don't cache websocket traffic
  }
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
