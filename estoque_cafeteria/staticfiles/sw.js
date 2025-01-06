const CACHE_NAME = 'estoque-cache-v4';
const urlsToCache = [
    '/login/',
    '/static/css/global.css',
    '/static/images/logo192.png',
    '/templates/offline.html'
];

// Instala e armazena no cache
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Cache aberto');
                return cache.addAll(urlsToCache)
                    .catch((err) => {
                        console.error('Erro ao adicionar ao cache:', err);
                    });
            })
    );
});

// Intercepta requisições
self.addEventListener('fetch', (event) => {
    event.respondWith(
        fetch(event.request).catch(() => {
            return caches.match(event.request).then((response) => {
                return response || caches.match('/templates/offline.html');
            });
        })
    );
});
