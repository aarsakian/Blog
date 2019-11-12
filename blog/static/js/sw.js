/**
 * Welcome to your Workbox-powered service worker!
 *
 * You'll need to register this file in your web app and you should
 * disable HTTP caching for this file too.
 * See https://goo.gl/nhQhGp
 *
 * The rest of the code is auto-generated. Please don't update this file
 * directly; instead, make changes to your Workbox build configuration
 * and re-run your build process.
 * See https://goo.gl/2aRDsh
 */

importScripts("https://storage.googleapis.com/workbox-cdn/releases/4.3.1/workbox-sw.js");

workbox.core.skipWaiting();

workbox.core.clientsClaim();

/**
 * The workboxSW.precacheAndRoute() method efficiently caches and responds to
 * requests for URLs in the manifest.
 * See https://goo.gl/S9QRab
 */
self.__precacheManifest = [
  {
    "url": "prod/app.min.js",
    "revision": "f3f543a3177a6ba54e2ee88af58c4ed8"
  },
  {
    "url": "prod/general.min.js",
    "revision": "20b5044ed7c1150b3d728fb9cd283cef"
  },
  {
    "url": "/",
    "revision": "9a1bef2cc49fce5d1274b3eed48326c2"
  }
].concat(self.__precacheManifest || []);
workbox.precaching.precacheAndRoute(self.__precacheManifest, {});

workbox.routing.registerRoute("/api/*", new workbox.strategies.NetworkFirst({ "cacheName":"my-api-cache","networkTimeoutSeconds":10,"fetchOptions":{"mode":"no-cors"},"matchOptions":{"ignoreSearch":true}, plugins: [new workbox.expiration.Plugin({ maxEntries: 5, maxAgeSeconds: 60, purgeOnQuotaError: false }), new workbox.backgroundSync.Plugin("my-queue-name", { maxRetentionTime: 3600 }), new workbox.cacheableResponse.Plugin({ statuses: [ 0, 200 ], headers: { 'x-test': 'true' } }), new workbox.broadcastUpdate.Plugin({ channelName: 'my-update-channel' })] }), 'GET');
