/**
 * Laguitos · Sharing
 *
 * Modal de compartir. Usa #modal-share (ya en index.html) y
 * Animations.openShareModalFlip para la entrada desde el botón trigger.
 *
 * Expuesto en window.Laguitos.Sharing.
 */
window.Laguitos = window.Laguitos || {};
window.Laguitos.Sharing = (() => {
  'use strict';

  const state = {
    currentDownloadId: null,
    allUsers: [],
    sharedUserIds: new Set(),
    busy: false,
  };

  let els = {};
  const cacheEls = () => {
    els = {
      backdrop: document.getElementById('modal-share'),
      usersList: document.getElementById('share-users'),
      currentList: document.getElementById('share-current'),
      closeBtn: document.querySelector('[data-action="close-share"]'),
    };
  };

  const escapeHtml = (s) => {
    const d = document.createElement('div');
    d.textContent = s == null ? '' : String(s);
    return d.innerHTML;
  };

  const initials = (name) => {
    if (!name) return '?';
    const parts = String(name).trim().split(/\s+/);
    const first = parts[0] ? parts[0][0] : '';
    const second = parts[1] ? parts[1][0] : '';
    return (first + second).toUpperCase() || '?';
  };

  // ─── Render ──────────────────────────────────────────────────────────
  const renderUsers = () => {
    if (!els.usersList) return;

    if (!state.allUsers.length) {
      els.usersList.innerHTML =
        '<p style="padding:1rem;color:var(--ink-300);font-size:13px;">No hay otros usuarios con quien compartir.</p>';
      return;
    }

    const rows = state.allUsers.map((u) => {
      const isShared = state.sharedUserIds.has(u.id);
      return `
        <div class="share-user-row ${isShared ? 'share-user-row--shared' : ''}"
             data-user-id="${u.id}"
             role="button"
             tabindex="0"
             aria-pressed="${isShared ? 'true' : 'false'}">
          <div class="share-user-name">
            <span class="share-user-avatar">${escapeHtml(initials(u.name))}</span>
            <span>${escapeHtml(u.name)}</span>
          </div>
          <span class="share-check" aria-hidden="true">✓</span>
        </div>
      `;
    }).join('');

    els.usersList.innerHTML = rows;

    els.usersList.querySelectorAll('.share-user-row').forEach((row) => {
      row.addEventListener('click', () => handleToggle(row));
      row.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handleToggle(row);
        }
      });
    });
  };

  const renderCurrent = () => {
    if (!els.currentList) return;
    if (state.sharedUserIds.size === 0) {
      els.currentList.innerHTML = '';
      return;
    }
    const names = state.allUsers
      .filter((u) => state.sharedUserIds.has(u.id))
      .map((u) => u.name);
    els.currentList.innerHTML = `
      <div class="share-current-label">Ya compartido con</div>
      ${names.map((n) =>
        `<div class="share-current-item"><span>♦ ${escapeHtml(n)}</span></div>`,
      ).join('')}
    `;
  };

  // ─── Toggle ──────────────────────────────────────────────────────────
  const handleToggle = async (rowEl) => {
    if (state.busy) return;
    const userId = Number(rowEl.dataset.userId);
    if (!userId || !state.currentDownloadId) return;

    const wasShared = state.sharedUserIds.has(userId);
    state.busy = true;
    rowEl.style.opacity = '0.5';

    try {
      if (wasShared) {
        await window.Laguitos.API.unshareDownload(state.currentDownloadId, userId);
        state.sharedUserIds.delete(userId);
      } else {
        await window.Laguitos.API.shareDownload(state.currentDownloadId, userId);
        state.sharedUserIds.add(userId);
      }
      rowEl.classList.toggle('share-user-row--shared');
      rowEl.setAttribute(
        'aria-pressed',
        state.sharedUserIds.has(userId) ? 'true' : 'false',
      );
      renderCurrent();

      const { History } = window.Laguitos;
      if (History && typeof History.refresh === 'function') {
        try { await History.refresh(); } catch (_) { /* noop */ }
      }
    } catch (e) {
      console.error('[Sharing] toggle failed', e);
      window.alert(e.detail || 'No se pudo actualizar el compartir.');
    } finally {
      rowEl.style.opacity = '';
      state.busy = false;
    }
  };

  // ─── Load users + existing shares ────────────────────────────────────
  const loadUsersList = async (downloadId) => {
    const { API } = window.Laguitos;
    if (els.usersList) {
      els.usersList.innerHTML =
        '<p style="padding:1rem;color:var(--ink-300);font-size:13px;">Cargando…</p>';
    }

    try {
      const [usersRes, sharesRes] = await Promise.all([
        API.listUsers(),
        API.listShares(downloadId),
      ]);
      state.allUsers = (usersRes && usersRes.items) || [];
      state.sharedUserIds = new Set(
        ((sharesRes && sharesRes.items) || []).map((s) => s.user_id),
      );
      renderUsers();
      renderCurrent();
    } catch (e) {
      console.error('[Sharing] load failed', e);
      if (els.usersList) {
        els.usersList.innerHTML =
          '<p style="padding:1rem;color:#c23;font-size:13px;">No se pudo cargar la lista de usuarios.</p>';
      }
    }
  };

  // ─── Open / close ────────────────────────────────────────────────────
  const openShareDialog = (downloadId, triggerEl) => {
    if (!els.backdrop) return;
    state.currentDownloadId = downloadId;
    state.allUsers = [];
    state.sharedUserIds = new Set();

    const { Animations } = window.Laguitos;
    if (Animations && Animations.openShareModalFlip) {
      Animations.openShareModalFlip(triggerEl);
    } else {
      els.backdrop.style.display = '';
      els.backdrop.style.opacity = '1';
    }

    loadUsersList(downloadId);
  };

  const closeDialog = () => {
    if (!els.backdrop) return;
    els.backdrop.style.display = 'none';
    state.currentDownloadId = null;
    if (els.usersList) els.usersList.innerHTML = '';
    if (els.currentList) els.currentList.innerHTML = '';
  };

  // ─── Init ────────────────────────────────────────────────────────────
  const init = () => {
    const root = document.getElementById('modal-share');
    if (root && root.dataset.sharingWired === '1') return;
    if (root) root.dataset.sharingWired = '1';

    cacheEls();

    if (els.closeBtn) {
      els.closeBtn.addEventListener('click', (e) => {
        e.preventDefault();
        closeDialog();
      });
    }

    if (els.backdrop) {
      els.backdrop.addEventListener('click', (e) => {
        if (e.target === els.backdrop) closeDialog();
      });
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && els.backdrop && els.backdrop.style.display === 'flex') {
        closeDialog();
      }
    });
  };

  return {
    init,
    openShareDialog,
    closeDialog,
    loadUsersList,
  };
})();
