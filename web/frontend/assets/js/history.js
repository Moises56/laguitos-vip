/**
 * Laguitos · History
 *
 * Tabs + paginación + render del historial. Usa Animations.switchTabFlip
 * para el cambio entre "Mis laguitos" y "Compartidos conmigo".
 *
 * Expuesto en window.Laguitos.History.
 */
window.Laguitos = window.Laguitos || {};
window.Laguitos.History = (() => {
  'use strict';

  const PAGE_SIZE = 20;

  const state = {
    scope: 'own',
    page: 1,
    total: 0,
    items: [],
    loading: false,
  };

  let els = {};
  const cacheEls = () => {
    els = {
      list: document.getElementById('history-list'),
      empty: document.getElementById('history-empty'),
      tabs: Array.from(document.querySelectorAll('.tab[data-tab]')),
      tabIndicator: document.querySelector('.tab-indicator'),
      tabCountOwn: document.getElementById('tab-count-own'),
      tabCountShared: document.getElementById('tab-count-shared'),
      pagination: document.getElementById('history-pagination'),
      paginationInfo: document.getElementById('pagination-info'),
      prevBtn: document.querySelector('[data-action="prev-page"]'),
      nextBtn: document.querySelector('[data-action="next-page"]'),
    };
  };

  // ─── Formatters ──────────────────────────────────────────────────────
  const fmtBytes = (n) => {
    if (n == null) return '';
    const u = ['B', 'KB', 'MB', 'GB', 'TB'];
    let i = 0;
    let v = n;
    while (v >= 1024 && i < u.length - 1) { v /= 1024; i++; }
    return `${v.toFixed(v >= 10 || i === 0 ? 0 : 1)} ${u[i]}`;
  };

  const MONTHS_ES = [
    'ene', 'feb', 'mar', 'abr', 'may', 'jun',
    'jul', 'ago', 'sep', 'oct', 'nov', 'dic',
  ];

  const fmtRelativeTime = (iso) => {
    if (!iso) return '';
    const date = new Date(iso);
    if (Number.isNaN(date.getTime())) return '';
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    const isSameDay =
      date.getFullYear() === now.getFullYear() &&
      date.getMonth() === now.getMonth() &&
      date.getDate() === now.getDate();
    if (isSameDay) return 'hoy';

    const yesterday = new Date(now);
    yesterday.setDate(now.getDate() - 1);
    if (
      date.getFullYear() === yesterday.getFullYear() &&
      date.getMonth() === yesterday.getMonth() &&
      date.getDate() === yesterday.getDate()
    ) return 'ayer';

    if (diffDays > 0 && diffDays < 7) return `hace ${diffDays} días`;

    const d = date.getDate();
    const m = MONTHS_ES[date.getMonth()];
    const y = date.getFullYear();
    return `el ${d} ${m} ${y}`;
  };

  const escapeHtml = (s) => {
    const div = document.createElement('div');
    div.textContent = s == null ? '' : String(s);
    return div.innerHTML;
  };

  const statusBadge = (status) => {
    const cls = {
      completed: 'status-badge--completed',
      running: 'status-badge--running',
      pending: 'status-badge--pending',
      failed: 'status-badge--failed',
      cancelled: 'status-badge--cancelled',
    }[status] || 'status-badge--pending';
    const label = {
      completed: 'Listo',
      running: 'Descargando',
      pending: 'En cola',
      failed: 'Falló',
      cancelled: 'Cancelada',
    }[status] || status || '';
    return `<span class="status-badge ${cls}">${escapeHtml(label)}</span>`;
  };

  // ─── Render ──────────────────────────────────────────────────────────
  const renderItem = (dl) => {
    const icon = dl.mode === 'audio' ? '♪' : '▷';
    const sizeTxt = dl.file_size_bytes ? fmtBytes(dl.file_size_bytes) : '';
    const platform = dl.platform || '';
    const metaBits = [platform, sizeTxt, fmtRelativeTime(dl.created_at)]
      .filter(Boolean)
      .join(' · ');

    const sharedPill =
      dl.is_mine && dl.shared_with && dl.shared_with.length > 0
        ? `<div class="history-item-shared">Compartido con ♦${dl.shared_with.length}</div>`
        : '';

    const ownerChip = !dl.is_mine && dl.owner
      ? `<span class="history-item-shared">De ${escapeHtml(dl.owner.name)}</span>`
      : '';

    const actions = [];
    if (dl.is_mine) {
      actions.push(
        `<button class="history-item-btn" data-action="share" title="Compartir">⇄</button>`
      );
    }
    if (dl.status === 'completed') {
      actions.push(
        `<button class="history-item-btn" data-action="download" title="Descargar">↓</button>`
      );
    }
    if (dl.is_mine) {
      actions.push(
        `<button class="history-item-btn" data-action="delete" title="Eliminar">✕</button>`
      );
    }

    const wrapper = document.createElement('div');
    wrapper.className = 'history-item';
    wrapper.dataset.id = dl.id;
    wrapper.innerHTML = `
      <div class="history-item-icon" aria-hidden="true">${icon}</div>
      <div class="history-item-body">
        <div class="history-item-title">${escapeHtml(dl.title || 'Sin título')}</div>
        <div class="history-item-meta">
          ${statusBadge(dl.status)}
          <span>${escapeHtml(metaBits)}</span>
        </div>
        ${sharedPill}
        ${ownerChip}
      </div>
      <div class="history-item-actions">${actions.join('')}</div>
    `;
    attachItemActions(wrapper, dl);
    return wrapper;
  };

  const render = (items) => {
    if (!els.list) return;
    if (!items || items.length === 0) {
      els.list.replaceChildren();
      if (els.empty) els.empty.style.display = 'block';
      if (els.pagination) els.pagination.style.display = 'none';
      return;
    }
    if (els.empty) els.empty.style.display = 'none';

    const frag = document.createDocumentFragment();
    items.forEach((dl) => frag.appendChild(renderItem(dl)));
    // Swap atómico: sin frames vacíos entre el clear y el append.
    els.list.replaceChildren(frag);

    renderPagination();

    const { Animations } = window.Laguitos;
    if (Animations && Animations.setupHistoryScroll) {
      try { Animations.setupHistoryScroll(); } catch (_) { /* noop */ }
    }
  };

  const renderPagination = () => {
    if (!els.pagination) return;
    const totalPages = Math.max(1, Math.ceil(state.total / PAGE_SIZE));
    if (state.total <= PAGE_SIZE) {
      els.pagination.style.display = 'none';
      return;
    }
    els.pagination.style.display = 'flex';
    if (els.paginationInfo) {
      els.paginationInfo.textContent = `Página ${state.page} de ${totalPages}`;
    }
    if (els.prevBtn) els.prevBtn.disabled = state.page <= 1;
    if (els.nextBtn) els.nextBtn.disabled = state.page >= totalPages;
  };

  const updateTabUI = () => {
    els.tabs.forEach((tab) => {
      const active = tab.dataset.tab === state.scope;
      tab.classList.toggle('tab--active', active);
      tab.setAttribute('aria-selected', active ? 'true' : 'false');
    });
    moveTabIndicator();
  };

  const moveTabIndicator = () => {
    if (!els.tabIndicator) return;
    const active = els.tabs.find((t) => t.classList.contains('tab--active'));
    if (!active) return;
    const parentRect = active.parentElement.getBoundingClientRect();
    const rect = active.getBoundingClientRect();
    els.tabIndicator.style.left = `${rect.left - parentRect.left}px`;
    els.tabIndicator.style.width = `${rect.width}px`;
  };

  const updateTabCount = (scope, count) => {
    if (scope === 'own' && els.tabCountOwn) {
      els.tabCountOwn.textContent = count != null ? `(${count})` : '';
    } else if (scope === 'shared' && els.tabCountShared) {
      els.tabCountShared.textContent = count != null ? `(${count})` : '';
    }
  };

  // ─── Item actions ────────────────────────────────────────────────────
  const attachItemActions = (itemEl, dl) => {
    const { API, Sharing } = window.Laguitos;

    itemEl.addEventListener('click', async (ev) => {
      const btn = ev.target.closest('[data-action]');
      if (!btn || !itemEl.contains(btn)) return;
      const action = btn.dataset.action;

      if (action === 'share') {
        if (Sharing && typeof Sharing.openShareDialog === 'function') {
          Sharing.openShareDialog(dl.id, btn);
        }
        return;
      }

      if (action === 'download') {
        window.open(API.getFileUrl(dl.id), '_blank');
        return;
      }

      if (action === 'delete') {
        const confirmed = window.confirm('¿Eliminar este laguito? No se puede deshacer.');
        if (!confirmed) return;
        try {
          await API.deleteDownload(dl.id);
          removeItem(dl.id);
        } catch (e) {
          console.error('[History] delete failed', e);
          window.alert(e.detail || 'No se pudo eliminar.');
        }
      }
    });
  };

  // ─── Load ────────────────────────────────────────────────────────────
  const load = async (scope = state.scope, page = 1) => {
    if (!els.list) cacheEls();
    state.loading = true;
    state.scope = scope;
    state.page = page;
    try {
      const res = await window.Laguitos.API.listDownloads({
        scope,
        page,
        pageSize: PAGE_SIZE,
      });
      state.items = res.items || [];
      state.total = res.total || 0;
      updateTabCount(scope, state.total);
      render(state.items);
    } catch (e) {
      console.error('[History] load failed', e);
      if (els.list) {
        els.list.innerHTML =
          '<p style="text-align:center;color:#c23;padding:1rem;">No pudimos cargar el historial.</p>';
      }
    } finally {
      state.loading = false;
    }
  };

  const switchTab = (scope) => {
    if (scope === state.scope || state.loading) return;
    const { Animations } = window.Laguitos;

    const doSwap = () => {
      state.scope = scope;
      state.page = 1;
      if (els.list) els.list.replaceChildren();
    };

    if (Animations && Animations.switchTabFlip) {
      Animations.switchTabFlip(doSwap);
    } else {
      doSwap();
    }

    updateTabUI();
    load(scope, 1);
  };

  const refresh = () => load(state.scope, state.page);

  // Animación suave de salida + remoción del DOM sin re-fetch.
  const removeItem = (downloadId) => {
    if (!els.list) cacheEls();
    const itemEl = els.list.querySelector(
      `.history-item[data-id="${downloadId}"]`,
    );
    if (!itemEl) {
      console.warn('[History] removeItem: item not found in DOM');
      return;
    }

    state.items = state.items.filter((it) => it.id !== downloadId);
    state.total = Math.max(0, state.total - 1);

    const done = () => {
      itemEl.remove();
      updateTabCount(state.scope, state.total);
      if (els.list.children.length === 0 && els.empty) {
        els.empty.style.display = 'block';
      }
      renderPagination();
    };

    const g = window.gsap;
    if (!g) { done(); return; }
    g.to(itemEl, {
      opacity: 0,
      x: -30,
      height: 0,
      marginBottom: 0,
      paddingTop: 0,
      paddingBottom: 0,
      duration: 0.35,
      ease: 'power2.in',
      onComplete: done,
    });
  };

  // Insertar un download recién completado arriba de todo, animado.
  const addItemAtTop = (download) => {
    if (!download || !download.id) return;
    if (state.scope !== 'own' && state.scope !== 'all') return;
    // Evita duplicar si ya está en el DOM (p.ej. por un refresh concurrente).
    if (els.list && els.list.querySelector(`.history-item[data-id="${download.id}"]`)) return;
    if (!els.list) cacheEls();

    state.items = [download, ...state.items];
    state.total += 1;

    if (els.empty) els.empty.style.display = 'none';
    const itemEl = renderItem(download);
    els.list.insertBefore(itemEl, els.list.firstChild);

    const g = window.gsap;
    if (g) {
      g.set(itemEl, { opacity: 0, y: -20, scale: 0.97 });
      g.to(itemEl, {
        opacity: 1,
        y: 0,
        scale: 1,
        duration: 0.5,
        ease: 'back.out(1.4)',
      });
    }

    updateTabCount(state.scope, state.total);
    renderPagination();
  };

  const clear = () => {
    if (els.list) els.list.replaceChildren();
    if (els.empty) els.empty.style.display = 'block';
    if (els.pagination) els.pagination.style.display = 'none';
    state.items = [];
    state.total = 0;
    updateTabCount('own', null);
    updateTabCount('shared', null);
  };

  // ─── Init ────────────────────────────────────────────────────────────
  const init = () => {
    const root = document.getElementById('section-history');
    if (root && root.dataset.wired === '1') return;
    if (root) root.dataset.wired = '1';

    cacheEls();

    els.tabs.forEach((tab) => {
      tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });

    if (els.prevBtn) {
      els.prevBtn.addEventListener('click', () => {
        if (state.page > 1) load(state.scope, state.page - 1);
      });
    }
    if (els.nextBtn) {
      els.nextBtn.addEventListener('click', () => {
        const totalPages = Math.max(1, Math.ceil(state.total / PAGE_SIZE));
        if (state.page < totalPages) load(state.scope, state.page + 1);
      });
    }

    window.addEventListener('resize', moveTabIndicator);
    updateTabUI();
  };

  return {
    init,
    load,
    switchTab,
    refresh,
    clear,
    render,
    removeItem,
    addItemAtTop,
  };
})();
