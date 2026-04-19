/**
 * Laguitos · Orquestador principal.
 *
 * Fase 1 — loader (una vez por sesión)
 * Fase 2 — page load + parallax + cursor
 * Fase 3 — auth check (login modal si no hay token o si /auth/me devuelve 401)
 * Fase 4 — cablear Downloads / History / Sharing
 * Fase 5 — cargar historial inicial (scope=own)
 * Fase 6 — suscribirse a cambios de auth (logout)
 */
window.Laguitos = window.Laguitos || {};
window.Laguitos.App = (() => {
  'use strict';

  const LOADER_KEY = 'laguitos.loader.shown';

  // Guard: la orquestación debe correr UNA sola vez por carga de página,
  // aunque algún mecanismo externo (HMR, extensión del browser, test
  // manual con App.init()) intente re-invocarla.
  let initStarted = false;

  const shouldPlayLoader = () => !sessionStorage.getItem(LOADER_KEY);

  const skipLoader = () => {
    const loader = document.getElementById('laguitos-loader');
    if (loader) loader.remove();
  };

  // ─── Login modal wiring ──────────────────────────────────────────────
  // Listener único; cada waitForLogin() registra su propio resolver y se
  // desencadena al próximo login exitoso.
  let _pendingLoginResolvers = [];

  const setupLoginForm = () => {
    const form = document.querySelector('[data-form="login"]');
    if (!form || form.dataset.wired === '1') return;
    form.dataset.wired = '1';

    const emailEl = document.getElementById('login-email');
    const passEl = document.getElementById('login-password');
    const errEl = document.getElementById('login-error');
    const submitBtn = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (errEl) errEl.textContent = '';
      const email = (emailEl && emailEl.value || '').trim();
      const password = (passEl && passEl.value) || '';
      if (!email || !password) {
        if (errEl) errEl.textContent = 'Completá correo y contraseña.';
        return;
      }
      if (submitBtn) submitBtn.disabled = true;
      try {
        await window.Laguitos.Auth.login(email, password);
        const { Animations } = window.Laguitos;
        if (Animations && Animations.hideLoginModal) {
          await Animations.hideLoginModal();
        } else {
          const backdrop = document.getElementById('modal-login');
          if (backdrop) backdrop.style.display = 'none';
        }
        if (passEl) passEl.value = '';
        const resolvers = _pendingLoginResolvers;
        _pendingLoginResolvers = [];
        resolvers.forEach((r) => r());
      } catch (err) {
        if (errEl) {
          errEl.textContent = err.detail || 'No se pudo iniciar sesión.';
        }
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  };

  const waitForLogin = () => new Promise((resolve) => {
    setupLoginForm();
    _pendingLoginResolvers.push(resolve);
  });

  // ─── Header nav ──────────────────────────────────────────────────────
  const updateHeaderForUser = (user) => {
    const nav = document.getElementById('header-nav');
    const userSpan = document.getElementById('header-user');
    if (!nav) return;
    if (user) {
      nav.style.display = 'flex';
      if (userSpan) userSpan.textContent = user.name || user.email || '';
    } else {
      nav.style.display = 'none';
      if (userSpan) userSpan.textContent = '';
    }
  };

  const wireLogout = () => {
    const btn = document.querySelector('[data-action="logout"]');
    if (!btn || btn.dataset.wired === '1') return;
    btn.dataset.wired = '1';
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      window.Laguitos.Auth.logout();
    });
  };

  const showLoginModal = async (Animations) => {
    if (Animations && Animations.playLoginModal) {
      await Animations.playLoginModal();
    } else {
      const backdrop = document.getElementById('modal-login');
      if (backdrop) backdrop.style.display = '';
    }
  };

  const checkAuth = async (Auth, API) => {
    if (!Auth.isLoggedIn()) return null;
    try {
      return await API.me();
    } catch (e) {
      if (e.status === 401) {
        Auth.logout();
        return null;
      }
      console.warn('[App] /auth/me falló (no 401)', e);
      return Auth.getUser();
    }
  };

  // ─── Init ────────────────────────────────────────────────────────────
  const init = async () => {
    if (initStarted) return;
    initStarted = true;
    const { API, Auth, Animations, Downloads, History, Sharing } = window.Laguitos;

    // Fase 1 — Loader (una sola vez por sesión)
    if (Animations && Animations.playLoader) {
      if (shouldPlayLoader()) {
        await Animations.playLoader();
        sessionStorage.setItem(LOADER_KEY, '1');
      } else {
        skipLoader();
      }
    } else {
      skipLoader();
    }

    // Fase 2 — Auth TEMPRANO: el contenido sigue oculto (body.is-auth-gated)
    // hasta que el login se complete.
    let currentUser = await checkAuth(Auth, API);
    if (!currentUser) {
      await showLoginModal(Animations);
      await waitForLogin();
      currentUser = Auth.getUser();
    }
    document.body.classList.remove('is-auth-gated');

    // Fase 3 — Page load del contenido principal (ahora visible).
    if (Animations) {
      if (Animations.playPageLoad) await Animations.playPageLoad();
      if (Animations.setupParallax) Animations.setupParallax();
      if (Animations.startOrbFloat) Animations.startOrbFloat();
      if (Animations.initCustomCursor) Animations.initCustomCursor();
    }

    // Fase 4 — Header + módulos
    updateHeaderForUser(currentUser);
    wireLogout();
    if (Downloads && Downloads.init) Downloads.init();
    if (History && History.init) History.init();
    if (Sharing && Sharing.init) Sharing.init();

    // Fase 5 — Historial inicial
    if (History && History.load) {
      try { await History.load('own', 1); } catch (_) { /* noop */ }
    }

    // Fase 6 — Reaccionar a logout / 401 (re-gatear y pedir login otra vez).
    Auth.onAuthChange(async (snap) => {
      updateHeaderForUser(snap.user);
      if (!snap.loggedIn) {
        if (History && History.clear) History.clear();
        if (Sharing && Sharing.closeDialog) Sharing.closeDialog();
        document.body.classList.add('is-auth-gated');
        await showLoginModal(Animations);
        await waitForLogin();
        document.body.classList.remove('is-auth-gated');
        const u = Auth.getUser();
        updateHeaderForUser(u);
        if (History && History.load) History.load('own', 1);
      }
    });
  };

  document.addEventListener('DOMContentLoaded', init);

  return { init };
})();
