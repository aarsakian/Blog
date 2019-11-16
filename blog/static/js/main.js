var App = require('./app');

function initServiceWorker() {
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
          navigator.serviceWorker.register('/static/js/sw.js').then(registration => {
          }).catch(registrationError => {
            console.log('SW registration failed: ', registrationError);
          });
        });
      }

}

initServiceWorker();

App.start();