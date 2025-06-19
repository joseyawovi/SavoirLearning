// Service Worker for Progressive Web App functionality
const CACHE_NAME = 'savoir-lms-v1';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/css/enhanced-styles.css',
    '/static/js/quiz.js',
    '/static/js/dashboard-enhancements.js',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
    'https://cdn.tailwindcss.com'
];

// Install Service Worker
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch events
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Return cached version or fetch from network
                return response || fetch(event.request);
            })
    );
});

// Activate Service Worker
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Background sync for offline functionality
self.addEventListener('sync', event => {
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

function doBackgroundSync() {
    // Sync user progress when back online
    return fetch('/api/sync-progress/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            syncData: getStoredProgress()
        })
    });
}

function getStoredProgress() {
    // Get offline stored progress data
    const progress = localStorage.getItem('offlineProgress');
    return progress ? JSON.parse(progress) : {};
}