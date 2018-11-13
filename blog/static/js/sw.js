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

importScripts("https://storage.googleapis.com/workbox-cdn/releases/3.6.3/workbox-sw.js");

workbox.skipWaiting();
workbox.clientsClaim();

/**
 * The workboxSW.precacheAndRoute() method efficiently caches and responds to
 * requests for URLs in the manifest.
 * See https://goo.gl/S9QRab
 */
self.__precacheManifest = [
  {
    "url": "static/js/prod/app.min.js",
    "revision": "9985112238110b8092d71fc8f1faf2ed"
  },
  {
    "url": "static/js/prod/general.min.js",
    "revision": "27607804f5f0f7b9df50ccde5f62cd17"
  }
].concat(self.__precacheManifest || []);
workbox.precaching.suppressWarnings();
workbox.precaching.precacheAndRoute(self.__precacheManifest, {});

workbox.routing.registerRoute("/api/posts", workbox.strategies.networkFirst({ "cacheName":"my-api-cache","networkTimeoutSeconds":10,"fetchOptions":{"mode":"no-cors"},"matchOptions":{"ignoreSearch":true}, plugins: [new workbox.expiration.Plugin({"maxEntries":5,"maxAgeSeconds":60,"purgeOnQuotaError":false}), new workbox.backgroundSync.Plugin("my-queue-name", {"maxRetentionTime":3600}), new workbox.cacheableResponse.Plugin({"statuses":[0,200],"headers":{"x-test":"true"}}), new workbox.broadcastUpdate.Plugin("my-update-channel")] }), 'GET');
