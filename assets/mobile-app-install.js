(function() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
      navigator.serviceWorker.register('/sw.js').catch(function() {});
    });
  }
  var isStandalone = (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches)
    || window.navigator.standalone === true
    || /ShebaNativeAndroid/i.test(navigator.userAgent || '');
  if (isStandalone) return;
  if (sessionStorage.getItem('sheba_app_bar_dismissed_restaurantradar') === '1') return;

  var deferredPrompt = null;
  window.addEventListener('beforeinstallprompt', function(e) {
    e.preventDefault();
    deferredPrompt = e;
  });

  function injectBar() {
    if (document.getElementById('sheba-mobile-app-bar')) return;
    var bar = document.createElement('div');
    bar.id = 'sheba-mobile-app-bar';
    bar.style.cssText = 'position:fixed;bottom:16px;left:16px;z-index:9998;display:flex;align-items:center;gap:8px;background:#fff7e6;color:#1c1917;border:1px solid #f0c98a;border-radius:999px;padding:8px 12px;box-shadow:0 10px 28px rgba(28,25,23,0.18);font-family:system-ui,-apple-system,sans-serif;font-size:12.5px;line-height:1.2;max-width:calc(100vw - 32px);';
    var isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent || '') && !window.MSStream;

    var installBtn = document.createElement('button');
    installBtn.type = 'button';
    installBtn.textContent = isIOS ? '📱 Install iOS App' : '📱 Install App';
    installBtn.style.cssText = 'background:#9a3412;color:#fff;border:none;border-radius:999px;padding:11px 14px;min-height:44px;font-weight:700;font-size:12.5px;cursor:pointer;white-space:nowrap;';
    installBtn.onclick = function() {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.finally(function() { deferredPrompt = null; });
      } else if (isIOS) {
        alert('To install Restaurant Radar on iPhone/iPad:\n\n1. Tap the Share button (⬆️) at the bottom of Safari.\n2. Scroll down and tap "Add to Home Screen" (➕).');
      } else {
        window.location.href = '/downloads/restaurantradar.apk';
      }
    };

    var apkLink = document.createElement('a');
    apkLink.href = '/downloads/restaurantradar.apk';
    apkLink.setAttribute('download', 'restaurantradar.apk');
    apkLink.textContent = '⬇ Android APK';
    apkLink.style.cssText = 'color:#7c2d12;text-decoration:none;font-weight:600;font-size:12px;padding:11px 12px;min-height:44px;display:inline-flex;align-items:center;border-radius:999px;border:1px solid #e2c9a0;white-space:nowrap;';

    var closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.setAttribute('aria-label', 'Dismiss mobile app bar');
    closeBtn.textContent = '✕';
    closeBtn.style.cssText = 'background:transparent;color:#57534e;border:none;font-size:15px;cursor:pointer;padding:12px;min-width:44px;min-height:44px;line-height:1;';
    closeBtn.onclick = function() {
      sessionStorage.setItem('sheba_app_bar_dismissed_restaurantradar', '1');
      bar.remove();
    };

    bar.appendChild(installBtn);
    bar.appendChild(apkLink);
    bar.appendChild(closeBtn);
    document.body.appendChild(bar);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectBar);
  } else {
    injectBar();
  }
})();
