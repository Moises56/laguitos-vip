/**
 * Laguitos API client.
 *
 * Wrapper puro de fetch. No toca DOM ni modales.
 * - Inyecta Authorization: Bearer <token> si Auth tiene sesión
 * - Interceptor 401: avisa a Auth para que limpie estado y dispare onAuthChange
 * - Errores: lanza { status, detail } siempre que la respuesta no sea ok
 *
 * Expuesto en window.Laguitos.API.
 */
window.Laguitos = window.Laguitos || {};
window.Laguitos.API = (() => {
  'use strict';

  const _detectBaseUrl = () => {
    const origin = window.location.origin;
    // Same-origin cuando el frontend se sirve desde el backend FastAPI
    // (dev con StaticFiles o prod con nginx → mismo origin).
    if (origin.includes('localhost:8000') || origin.includes('127.0.0.1:8000')) {
      return '';
    }
    // Fallback para casos raros (file://, static server externo).
    return 'http://localhost:8000';
  };

  let _baseUrl = _detectBaseUrl();

  /**
   * Override manual. El auto-detect ya cubre :5500/:3000/:8080/file:// → :8000,
   * y same-origin para :8000 y producción. Usá esto solo si tu dev setup
   * corre en otro puerto.
   */
  const configure = ({ baseUrl } = {}) => {
    if (typeof baseUrl === 'string') {
      _baseUrl = baseUrl.replace(/\/+$/, '');
    }
  };

  const _getToken = () => {
    const Auth = window.Laguitos && window.Laguitos.Auth;
    return Auth && typeof Auth.getToken === 'function' ? Auth.getToken() : null;
  };

  const _notify401 = () => {
    const Auth = window.Laguitos && window.Laguitos.Auth;
    if (Auth && typeof Auth._handle401 === 'function') {
      Auth._handle401();
    }
  };

  /**
   * Core request. Devuelve el JSON parseado en éxito.
   * En error lanza un Error con .status y .detail.
   */
  const request = async (path, { method = 'GET', body, headers = {}, skipAuth = false } = {}) => {
    const url = `${_baseUrl}${path}`;
    const finalHeaders = { Accept: 'application/json', ...headers };

    let finalBody = body;
    if (body !== undefined && body !== null && !(body instanceof FormData)) {
      finalHeaders['Content-Type'] = 'application/json';
      finalBody = typeof body === 'string' ? body : JSON.stringify(body);
    }

    if (!skipAuth) {
      const token = _getToken();
      if (token) finalHeaders['Authorization'] = `Bearer ${token}`;
    }

    let response;
    try {
      response = await fetch(url, { method, headers: finalHeaders, body: finalBody });
    } catch (networkErr) {
      const err = new Error('No se pudo conectar con el servidor');
      err.status = 0;
      err.detail = networkErr.message || 'network error';
      throw err;
    }

    if (response.status === 401) {
      _notify401();
    }

    const text = await response.text();
    const data = text ? _safeParse(text) : null;

    if (!response.ok) {
      const err = new Error(_extractDetail(data) || `HTTP ${response.status}`);
      err.status = response.status;
      err.detail = _extractDetail(data);
      err.data = data;
      throw err;
    }

    return data;
  };

  const _safeParse = (text) => {
    try { return JSON.parse(text); } catch { return text; }
  };

  const _extractDetail = (data) => {
    if (!data) return null;
    if (typeof data === 'string') return data;
    if (typeof data.detail === 'string') return data.detail;
    if (Array.isArray(data.detail)) {
      return data.detail.map((d) => d.msg || JSON.stringify(d)).join('; ');
    }
    return null;
  };

  // ─── Auth ────────────────────────────────────────────────────────────
  const login = (email, password) =>
    request('/api/auth/login', {
      method: 'POST',
      body: { email, password },
      skipAuth: true,
    });

  const me = () => request('/api/auth/me');

  const listUsers = () => request('/api/auth/users');

  // ─── Downloads ───────────────────────────────────────────────────────
  const createDownload = ({ url, mode, quality }) =>
    request('/api/downloads', {
      method: 'POST',
      body: { url, mode, quality },
    });

  const listDownloads = ({ scope = 'own', page = 1, pageSize = 20 } = {}) => {
    const qs = new URLSearchParams({
      scope,
      page: String(page),
      page_size: String(pageSize),
    }).toString();
    return request(`/api/downloads?${qs}`);
  };

  const getDownload = (id) => request(`/api/downloads/${encodeURIComponent(id)}`);

  const cancelDownload = (id) =>
    request(`/api/downloads/${encodeURIComponent(id)}/cancel`, { method: 'POST' });

  const deleteDownload = (id) =>
    request(`/api/downloads/${encodeURIComponent(id)}`, { method: 'DELETE' });

  /**
   * Devuelve la URL absoluta del archivo listo para descargar,
   * con el token como query param (endpoint lo acepta así).
   */
  const getFileUrl = (id) => {
    const token = _getToken();
    const base = _baseUrl || window.location.origin;
    const qs = new URLSearchParams({ token: token || '' }).toString();
    return `${base}/api/downloads/${encodeURIComponent(id)}/file?${qs}`;
  };

  /**
   * Devuelve la URL WebSocket con el token ya incluido como query.
   * Convierte http(s) → ws(s).
   */
  const getWsUrl = (id) => {
    const token = _getToken();
    const http = _baseUrl || window.location.origin;
    const ws = http.replace(/^http/i, 'ws');
    const qs = new URLSearchParams({ token: token || '' }).toString();
    return `${ws}/ws/downloads/${encodeURIComponent(id)}?${qs}`;
  };

  // ─── Sharing ─────────────────────────────────────────────────────────
  const shareDownload = (id, userId) =>
    request(`/api/downloads/${encodeURIComponent(id)}/share`, {
      method: 'POST',
      body: { user_id: userId },
    });

  const unshareDownload = (id, userId) =>
    request(
      `/api/downloads/${encodeURIComponent(id)}/share/${encodeURIComponent(userId)}`,
      { method: 'DELETE' },
    );

  const listShares = (id) =>
    request(`/api/downloads/${encodeURIComponent(id)}/shares`);

  return {
    configure,
    request,
    get baseUrl() { return _baseUrl; },
    login,
    me,
    listUsers,
    createDownload,
    listDownloads,
    getDownload,
    cancelDownload,
    deleteDownload,
    getFileUrl,
    getWsUrl,
    shareDownload,
    unshareDownload,
    listShares,
  };
})();
