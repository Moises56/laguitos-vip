/**
 * Laguitos · Downloads
 *
 * Orquesta el form de descarga, WS de progreso (con fallback a polling)
 * y la celebración de éxito. Depende de API, Animations e History.
 *
 * Expuesto en window.Laguitos.Downloads.
 */
window.Laguitos = window.Laguitos || {};
window.Laguitos.Downloads = (() => {
  'use strict';

  const URL_RE = /^https?:\/\/\S+$/i;
  const WS_BACKOFFS = [1000, 2000, 4000, 8000];
  const POLL_INTERVAL_MS = 2000;
  const POLL_TIMEOUT_MS = 5 * 60 * 1000;
  // Progress bar visible al menos este tiempo para que el usuario
  // alcance a ver el shimmer aunque el backend termine enseguida.
  const MIN_VISIBLE_MS = 800;
  // Auto-dismiss del success card tras celebrar.
  const SUCCESS_AUTO_DISMISS_MS = 8000;

  const state = {
    mode: 'video',
    quality: 'mejor',
    currentJobId: null,
    ws: null,
    wsAttempts: 0,
    wsReconnectTimer: null,
    pollTimer: null,
    pollStartedAt: 0,
    progressShownAt: 0,
    successTimerId: null,
    cancelled: false,
    completed: false,
  };

  // ─── DOM refs ────────────────────────────────────────────────────────
  const $ = (sel) => document.querySelector(sel);

  let els = {};
  const cacheEls = () => {
    els = {
      urlInput: $('#input-url'),
      pasteBtn: $('[data-action="paste"]'),
      submitBtn: $('[data-action="submit"]'),
      formatOptions: document.querySelectorAll('.format-option'),
      qualitySelect: $('#select-quality'),
      cardDownload: $('.card-download'),
      progressPanel: $('#progress-panel'),
      progressTitle: $('#progress-title'),
      progressMeta: $('#progress-meta'),
      progressFill: $('#progress-fill'),
      progressPercent: $('#progress-percent'),
      progressSpeed: $('#progress-speed'),
      progressEta: $('#progress-eta'),
      cancelBtn: $('[data-action="cancel-download"]'),
      success: $('#status-success'),
      successTitle: $('#success-title'),
      successMeta: $('#success-meta'),
      downloadLink: $('#download-link'),
    };
  };

  // ─── Helpers ─────────────────────────────────────────────────────────
  const fmtBytes = (n) => {
    if (!n || n < 0) return '';
    const u = ['B', 'KB', 'MB', 'GB', 'TB'];
    let i = 0;
    let v = n;
    while (v >= 1024 && i < u.length - 1) { v /= 1024; i++; }
    return `${v.toFixed(v >= 10 || i === 0 ? 0 : 1)} ${u[i]}`;
  };

  const fmtSpeed = (bps) => {
    if (!bps || bps <= 0) return '';
    return `${fmtBytes(bps)}/s`;
  };

  const fmtEta = (seconds) => {
    if (!seconds || seconds <= 0) return '';
    const s = Math.round(seconds);
    if (s < 60) return `${s}s`;
    const m = Math.floor(s / 60);
    const r = s % 60;
    if (m < 60) return `${m}m ${r}s`;
    const h = Math.floor(m / 60);
    return `${h}h ${m % 60}m`;
  };

  const isValidUrl = (v) => URL_RE.test((v || '').trim());

  const toastError = (msg) => {
    const meta = els.progressMeta || els.successMeta;
    if (meta) meta.textContent = msg;
    else alert(msg);
    console.warn('[Downloads]', msg);
  };

  // ─── UI state ────────────────────────────────────────────────────────
  const resetProgressVisual = () => {
    if (els.progressFill) els.progressFill.style.width = '0%';
    if (els.progressPercent) els.progressPercent.textContent = '0.0%';
    if (els.progressTitle) els.progressTitle.textContent = 'Preparando descarga…';
    if (els.progressMeta) els.progressMeta.textContent = '';
    if (els.progressSpeed) els.progressSpeed.textContent = '';
    if (els.progressEta) els.progressEta.textContent = '';
    // Limpiar override de opacity que celebrate() deja inline.
    if (els.progressPanel) {
      els.progressPanel.style.opacity = '';
      els.progressPanel.style.transform = '';
    }
  };

  const showForm = () => {
    if (els.progressPanel) els.progressPanel.classList.remove('is-active');
    if (els.success) els.success.style.display = 'none';
  };

  const showProgress = () => {
    resetProgressVisual();
    if (els.success) els.success.style.display = 'none';
    if (els.progressPanel) els.progressPanel.classList.add('is-active');
    state.progressShownAt = Date.now();
  };

  const hideProgress = () => {
    if (els.progressPanel) els.progressPanel.classList.remove('is-active');
    // Después de la transición (max-height 0.4s), resetear la barra.
    setTimeout(resetProgressVisual, 450);
  };

  const clearAutoDismissSuccess = () => {
    if (state.successTimerId) {
      clearTimeout(state.successTimerId);
      state.successTimerId = null;
    }
  };

  const isSuccessVisible = () => {
    if (!els.success) return false;
    if (els.success.style.display === 'none') return false;
    return getComputedStyle(els.success).display !== 'none';
  };

  const dismissSuccess = async () => {
    clearAutoDismissSuccess();
    if (!isSuccessVisible()) return;
    const { Animations } = window.Laguitos;
    if (Animations && Animations.hideSuccess) {
      await Animations.hideSuccess(els.success);
    } else if (els.success) {
      els.success.style.display = 'none';
    }
  };

  const scheduleAutoDismissSuccess = () => {
    clearAutoDismissSuccess();
    state.successTimerId = setTimeout(() => {
      dismissSuccess();
    }, SUCCESS_AUTO_DISMISS_MS);
  };

  const updateSubmitEnabled = () => {
    if (!els.submitBtn || !els.urlInput) return;
    const ok = isValidUrl(els.urlInput.value);
    els.submitBtn.disabled = !ok;
  };

  // ─── WebSocket ───────────────────────────────────────────────────────
  const closeWs = () => {
    if (state.wsReconnectTimer) {
      clearTimeout(state.wsReconnectTimer);
      state.wsReconnectTimer = null;
    }
    if (state.ws) {
      try { state.ws.close(); } catch (_) { /* noop */ }
      state.ws = null;
    }
  };

  const openWs = (jobId) => {
    const { API } = window.Laguitos;
    const wsUrl = API.getWsUrl(jobId);
    let ws;
    try {
      ws = new WebSocket(wsUrl);
    } catch (e) {
      console.error('[Downloads] WS constructor failed', e);
      startPolling(jobId);
      return;
    }
    state.ws = ws;

    ws.onopen = () => {
      state.wsAttempts = 0;
    };

    ws.onmessage = (ev) => {
      let data;
      try { data = JSON.parse(ev.data); } catch { return; }
      if (!data || data.type === 'ping') return;
      handleProgressUpdate(data);
    };

    ws.onerror = () => { /* se maneja en onclose */ };

    ws.onclose = (ev) => {
      if (state.completed || state.cancelled) return;
      state.ws = null;
      if (state.wsAttempts < WS_BACKOFFS.length) {
        const delay = WS_BACKOFFS[state.wsAttempts];
        state.wsAttempts += 1;
        state.wsReconnectTimer = setTimeout(() => {
          if (state.currentJobId === jobId && !state.completed && !state.cancelled) {
            openWs(jobId);
          }
        }, delay);
      } else {
        console.warn('[Downloads] WS agotó reintentos, cambiando a polling', ev && ev.code);
        startPolling(jobId);
      }
    };
  };

  // ─── Polling fallback ────────────────────────────────────────────────
  const stopPolling = () => {
    if (state.pollTimer) {
      clearTimeout(state.pollTimer);
      state.pollTimer = null;
    }
  };

  const startPolling = (jobId) => {
    if (state.pollTimer) return;
    state.pollStartedAt = Date.now();
    const tick = async () => {
      if (state.currentJobId !== jobId || state.completed || state.cancelled) return;
      if (Date.now() - state.pollStartedAt > POLL_TIMEOUT_MS) {
        toastError('La descarga tardó demasiado. Intentalo de nuevo.');
        finalize({ ok: false });
        return;
      }
      try {
        const dl = await window.Laguitos.API.getDownload(jobId);
        handleProgressUpdate({
          job_id: jobId,
          status: dl.status,
          percent: dl.progress_percent || 0,
          message: dl.error_message || null,
          title: dl.title,
          platform: dl.platform,
          file_size_bytes: dl.file_size_bytes,
        });
      } catch (e) {
        if (e.status === 404) {
          toastError('La descarga desapareció.');
          finalize({ ok: false });
          return;
        }
        // network hiccup — sigue intentando
      }
      state.pollTimer = setTimeout(tick, POLL_INTERVAL_MS);
    };
    state.pollTimer = setTimeout(tick, POLL_INTERVAL_MS);
  };

  // ─── Progress update handler ─────────────────────────────────────────
  const handleProgressUpdate = (data) => {
    const { Animations } = window.Laguitos;
    const pct = Number(data.percent) || 0;

    if (data.status === 'running' || data.status === 'pending') {
      if (els.progressTitle) {
        els.progressTitle.textContent =
          data.status === 'pending' ? 'Encolando descarga…' : 'Descargando…';
      }
      if (els.progressMeta && data.message) {
        els.progressMeta.textContent = data.message;
      }
      if (els.progressSpeed) {
        els.progressSpeed.textContent = fmtSpeed(data.speed_bytes_per_sec);
      }
      if (els.progressEta) {
        els.progressEta.textContent = fmtEta(data.eta_seconds);
      }
      if (Animations && Animations.updateProgress) {
        Animations.updateProgress(pct);
      }
      return;
    }

    if (data.status === 'completed') {
      finalize({ ok: true, data });
      return;
    }

    if (data.status === 'failed' || data.status === 'cancelled') {
      finalize({ ok: false, data });
    }
  };

  // ─── Finalize (completed / failed / cancelled) ───────────────────────
  const finalize = async ({ ok, data }) => {
    if (state.completed || state.cancelled) return;
    state.completed = ok === true;
    state.cancelled = data && data.status === 'cancelled';

    closeWs();
    stopPolling();

    const { API, Animations, History } = window.Laguitos;
    const jobId = state.currentJobId;
    let detail = data;

    if (ok) {
      try {
        detail = await API.getDownload(jobId);
      } catch (_) { /* usamos lo que teníamos */ }

      if (els.downloadLink) {
        els.downloadLink.href = API.getFileUrl(jobId);
      }
      if (els.successTitle) {
        els.successTitle.textContent = '¡Guardado!';
      }
      if (els.successMeta) {
        const title = (detail && detail.title) || 'Tu laguito';
        const size = detail && detail.file_size_bytes
          ? ` · ${fmtBytes(detail.file_size_bytes)}`
          : '';
        els.successMeta.textContent = `${title}${size}`;
      }

      // Garantizar un mínimo de visibilidad del progress panel para
      // que el shimmer se alcance a ver aunque el backend haya terminado
      // casi instantáneamente.
      const elapsed = Date.now() - (state.progressShownAt || 0);
      if (elapsed < MIN_VISIBLE_MS) {
        await new Promise((r) => setTimeout(r, MIN_VISIBLE_MS - elapsed));
      }

      if (Animations && Animations.celebrate) {
        await Animations.celebrate(els.cardDownload || els.success);
        hideProgress();
      } else if (els.success) {
        els.success.style.display = 'block';
        hideProgress();
      }
    } else {
      const reason =
        (data && (data.message || data.error_message)) ||
        (state.cancelled ? 'Descarga cancelada' : 'La descarga falló');
      if (els.progressTitle) els.progressTitle.textContent = reason;
      if (els.progressMeta) els.progressMeta.textContent = '';
      if (els.progressSpeed) els.progressSpeed.textContent = '';
      if (els.progressEta) els.progressEta.textContent = '';
    }

    if (History) {
      if (ok && detail && typeof History.addItemAtTop === 'function') {
        try { History.addItemAtTop(detail); } catch (e) { console.warn(e); }
      } else if (typeof History.refresh === 'function') {
        try { await History.refresh(); } catch (_) { /* noop */ }
      }
    }

    if (ok) scheduleAutoDismissSuccess();
  };

  // ─── Submit ──────────────────────────────────────────────────────────
  const submitDownload = async () => {
    if (!els.urlInput) return;
    const url = els.urlInput.value.trim();
    if (!isValidUrl(url)) {
      els.urlInput.focus();
      return;
    }
    const { API } = window.Laguitos;

    // Cerrar success card de la descarga anterior (si sigue visible).
    if (isSuccessVisible()) {
      await dismissSuccess();
    }

    state.currentJobId = null;
    state.wsAttempts = 0;
    state.cancelled = false;
    state.completed = false;
    closeWs();
    stopPolling();

    showProgress();
    if (els.submitBtn) els.submitBtn.disabled = true;

    let created;
    try {
      created = await API.createDownload({
        url,
        mode: state.mode,
        quality: state.quality,
      });
    } catch (e) {
      toastError(e.detail || 'No se pudo crear la descarga');
      if (els.progressPanel) els.progressPanel.style.display = 'none';
      if (els.submitBtn) els.submitBtn.disabled = !isValidUrl(url);
      return;
    }

    state.currentJobId = created.job_id;
    openWs(created.job_id);

    if (els.submitBtn) els.submitBtn.disabled = !isValidUrl(url);
  };

  // ─── Cancel ──────────────────────────────────────────────────────────
  const cancelCurrent = async () => {
    if (!state.currentJobId) return;
    const { API } = window.Laguitos;
    try {
      await API.cancelDownload(state.currentJobId);
    } catch (e) {
      if (e.status !== 400) {
        toastError(e.detail || 'No se pudo cancelar');
      }
    }
    finalize({ ok: false, data: { status: 'cancelled', message: 'Cancelada' } });
  };

  // ─── Reset ───────────────────────────────────────────────────────────
  const resetForm = () => {
    closeWs();
    stopPolling();
    state.currentJobId = null;
    state.cancelled = false;
    state.completed = false;
    state.wsAttempts = 0;
    showForm();
    if (els.urlInput) els.urlInput.value = '';
    updateSubmitEnabled();
  };

  // ─── Init / wiring ───────────────────────────────────────────────────
  const init = () => {
    const root = document.getElementById('section-download');
    if (root && root.dataset.wired === '1') return;
    if (root) root.dataset.wired = '1';

    cacheEls();

    if (els.urlInput) {
      els.urlInput.addEventListener('input', updateSubmitEnabled);
      els.urlInput.addEventListener('focus', () => {
        if (state.completed) resetForm();
      });
    }
    updateSubmitEnabled();

    if (els.pasteBtn) {
      els.pasteBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        if (!navigator.clipboard || !navigator.clipboard.readText) {
          toastError('Tu navegador no permite leer el portapapeles automáticamente.');
          return;
        }
        try {
          const text = await navigator.clipboard.readText();
          if (text && els.urlInput) {
            els.urlInput.value = text.trim();
            updateSubmitEnabled();
          }
        } catch {
          toastError('No se pudo leer el portapapeles.');
        }
      });
    }

    els.formatOptions.forEach((btn) => {
      btn.addEventListener('click', () => {
        els.formatOptions.forEach((b) => {
          b.classList.remove('format-option--active');
          b.setAttribute('aria-pressed', 'false');
        });
        btn.classList.add('format-option--active');
        btn.setAttribute('aria-pressed', 'true');
        state.mode = btn.dataset.value || 'video';
      });
    });

    if (els.qualitySelect) {
      state.quality = els.qualitySelect.value || 'mejor';
      els.qualitySelect.addEventListener('change', () => {
        state.quality = els.qualitySelect.value;
      });
    }

    if (els.submitBtn) {
      els.submitBtn.addEventListener('click', (e) => {
        e.preventDefault();
        submitDownload();
      });
    }

    if (els.cancelBtn) {
      els.cancelBtn.addEventListener('click', (e) => {
        e.preventDefault();
        cancelCurrent();
      });
    }

    // Close manual del success card (botón ×).
    if (els.success) {
      els.success.addEventListener('click', (e) => {
        const btn = e.target.closest('[data-action="close-success"]');
        if (!btn) return;
        e.preventDefault();
        dismissSuccess();
      });
    }
  };

  return {
    init,
    submitDownload,
    cancelCurrent,
    resetForm,
  };
})();
