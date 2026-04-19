/**
 * Laguitos Auth state manager.
 *
 * Módulo puro: persiste sesión en localStorage y publica cambios
 * a suscriptores. No toca DOM ni modales.
 *
 * Expuesto en window.Laguitos.Auth.
 */
window.Laguitos = window.Laguitos || {};
window.Laguitos.Auth = (() => {
  'use strict';

  const TOKEN_KEY = 'laguitos.token';
  const USER_KEY = 'laguitos.user';

  const _listeners = new Set();

  const _readUser = () => {
    try {
      const raw = localStorage.getItem(USER_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  };

  const _emit = () => {
    const snapshot = { user: getUser(), token: getToken(), loggedIn: isLoggedIn() };
    _listeners.forEach((cb) => {
      try { cb(snapshot); } catch (e) { console.error('[Auth] listener error', e); }
    });
  };

  const getToken = () => localStorage.getItem(TOKEN_KEY);

  const getUser = () => _readUser();

  const isLoggedIn = () => !!getToken();

  /**
   * Intenta autenticar contra el backend y persiste sesión.
   * Propaga errores del API (ej. 401 con detail "Email o contraseña incorrectos").
   */
  const login = async (email, password) => {
    const API = window.Laguitos.API;
    const data = await API.login(email, password);

    if (!data || !data.access_token || !data.user) {
      const err = new Error('Respuesta de login inválida');
      err.status = 500;
      throw err;
    }

    localStorage.setItem(TOKEN_KEY, data.access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(data.user));
    _emit();
    return data.user;
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    _emit();
  };

  /**
   * Suscribe un callback a cambios de sesión.
   * Devuelve la función para desuscribir.
   * El callback recibe { user, token, loggedIn }.
   */
  const onAuthChange = (callback) => {
    if (typeof callback !== 'function') return () => {};
    _listeners.add(callback);
    return () => _listeners.delete(callback);
  };

  /**
   * Llamado por API cuando una respuesta devuelve 401.
   * Limpia credenciales y notifica a suscriptores.
   */
  const _handle401 = () => {
    if (!isLoggedIn()) return;
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    _emit();
  };

  return {
    login,
    logout,
    getToken,
    getUser,
    isLoggedIn,
    onAuthChange,
    _handle401,
  };
})();
