/**
 * Laguitos · Animations
 *
 * 10 timelines con GSAP core + ScrollTrigger + Flip + CustomEase.
 * Sin dependencias premium (SplitText casero).
 * Respeta prefers-reduced-motion.
 *
 * Expuesto en window.Laguitos.Animations.
 */
window.Laguitos = window.Laguitos || {};
window.Laguitos.Animations = (() => {
  'use strict';

  const g = window.gsap;
  const ST = window.ScrollTrigger;
  const Flip = window.Flip;
  const CustomEase = window.CustomEase;

  if (!g || !ST || !Flip || !CustomEase) {
    console.error('[Animations] GSAP o plugins faltantes');
    return {};
  }

  g.registerPlugin(ST, Flip, CustomEase);

  // ─── Easings ─────────────────────────────────────────────────────
  CustomEase.create('fluid', 'M0,0 C0.25,0.1 0.25,1 1,1');
  CustomEase.create('soft',  'M0,0 C0.16,1 0.3,1 1,1');
  CustomEase.create('drip',  'M0,0 C0.55,0 0.2,0.95 1,1');

  // ─── Reduced motion guard ────────────────────────────────────────
  const reducedMQ = window.matchMedia('(prefers-reduced-motion: reduce)');
  const prefersReducedMotion = () => reducedMQ.matches;
  if (prefersReducedMotion()) {
    g.globalTimeline.timeScale(100);
  }

  // ─── Helpers ─────────────────────────────────────────────────────

  /**
   * Split by words preservando <br>. Envuelve cada palabra en:
   *   <span class="word" style="display:inline-block;overflow:hidden">
   *     <span class="word-inner" style="display:inline-block">palabra</span>
   *   </span>
   * Devuelve array de .word-inner para animar.
   */
  const splitByWords = (el) => {
    if (!el || el.dataset.splitted === '1') {
      return Array.from(el.querySelectorAll('.word-inner'));
    }
    const inners = [];
    const children = Array.from(el.childNodes);

    children.forEach((node) => {
      if (node.nodeType === Node.TEXT_NODE) {
        const text = node.textContent;
        const words = text.split(/(\s+)/);
        const frag = document.createDocumentFragment();
        words.forEach((chunk) => {
          if (!chunk) return;
          if (/^\s+$/.test(chunk)) {
            frag.appendChild(document.createTextNode(chunk));
            return;
          }
          const wordSpan = document.createElement('span');
          wordSpan.className = 'word';
          wordSpan.style.cssText =
            'display:inline-block;overflow:hidden;vertical-align:bottom;line-height:inherit;';
          const inner = document.createElement('span');
          inner.className = 'word-inner';
          inner.style.cssText = 'display:inline-block;will-change:transform;';
          inner.textContent = chunk;
          wordSpan.appendChild(inner);
          frag.appendChild(wordSpan);
          inners.push(inner);
        });
        node.parentNode.replaceChild(frag, node);
      }
    });

    el.dataset.splitted = '1';
    return inners;
  };

  const waitFonts = () =>
    document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();

  const randomBetween = (min, max) => Math.random() * (max - min) + min;

  // ══════════════════════════════════════════════════════════════════
  // Timeline 1 · Loader cinemático
  // ══════════════════════════════════════════════════════════════════
  const playLoader = () => new Promise((resolve) => {
    const loader = document.getElementById('laguitos-loader');
    if (!loader) return resolve();

    if (prefersReducedMotion()) {
      loader.style.opacity = '0';
      setTimeout(() => { loader.remove(); resolve(); }, 100);
      return;
    }

    const drop = loader.querySelector('.loader-drop');
    const ripples = loader.querySelectorAll('.loader-ripple');
    const words = loader.querySelectorAll('.loader-word');
    const text = loader.querySelector('.loader-text');

    g.set(drop, { y: -100, scale: 0, opacity: 0, transformOrigin: '50% 50%' });
    g.set(ripples, { scale: 0, opacity: 0, transformOrigin: '50% 50%' });
    g.set(words, { y: 20, opacity: 0 });
    if (text) g.set(text, { opacity: 1 });

    const tl = g.timeline({
      onComplete: () => { loader.remove(); resolve(); }
    });

    tl.to(drop, { y: 0, scale: 1, opacity: 1, duration: 0.9, ease: 'drip' })
      .to(drop, { scaleY: 0.6, scaleX: 1.3, duration: 0.1, ease: 'power2.out' })
      .to(drop, { scaleY: 1, scaleX: 1, duration: 0.4, ease: 'back.out(2)' })
      .to(ripples, {
        scale: 4,
        opacity: 0.5,
        duration: 1.2,
        stagger: 0.2,
        ease: 'fluid',
      }, '-=0.3')
      .to(ripples, { opacity: 0, duration: 0.6, ease: 'fluid' }, '-=0.8')
      .to(words, {
        y: 0,
        opacity: 1,
        duration: 0.6,
        stagger: 0.12,
        ease: 'soft',
      }, '-=1.0')
      .to({}, { duration: 1 })
      .to(loader, { opacity: 0, duration: 0.7, ease: 'fluid' });
  });

  // ══════════════════════════════════════════════════════════════════
  // Timeline 2 · Page load orquestado
  // ══════════════════════════════════════════════════════════════════
  const playPageLoad = async () => {
    await waitFonts();

    const header = document.querySelector('.header');
    const eyebrow = document.querySelector('.hero-eyebrow');
    const title = document.querySelector('.hero-title');
    const sub = document.querySelector('.hero-sub');
    const card = document.querySelector('.card-download');
    const orbs = document.querySelectorAll('.bg-mesh .orb');

    const titleInners = title ? splitByWords(title) : [];

    if (prefersReducedMotion()) {
      [header, eyebrow, title, sub, card].forEach((el) => {
        if (el) g.set(el, { clearProps: 'all', opacity: 1 });
      });
      return;
    }

    g.set([header, eyebrow, sub, card], { opacity: 0 });
    g.set(header, { y: -40 });
    g.set(eyebrow, { x: -20 });
    g.set(titleInners, { yPercent: 110, opacity: 0 });
    g.set(sub, { y: 20 });
    g.set(card, { y: 60, scale: 0.97 });
    g.set(orbs, { scale: 0, opacity: 0, transformOrigin: '50% 50%' });

    return new Promise((resolve) => {
      const tl = g.timeline({ onComplete: resolve });

      tl.to(header, { y: 0, opacity: 1, duration: 0.7, ease: 'soft' })
        .to(eyebrow, { x: 0, opacity: 1, duration: 0.5, ease: 'fluid' }, '-=0.3')
        .to(titleInners, {
          yPercent: 0,
          opacity: 1,
          duration: 0.9,
          stagger: 0.06,
          ease: 'soft',
        }, '-=0.2')
        .to(sub, { y: 0, opacity: 1, duration: 0.6, ease: 'fluid' }, '-=0.5')
        .to(card, {
          y: 0,
          scale: 1,
          opacity: 1,
          duration: 0.8,
          ease: 'soft',
        }, '-=0.4')
        .to(orbs, {
          scale: 1,
          opacity: 1,
          duration: 1.6,
          stagger: 0.2,
          ease: 'fluid',
        }, '-=1.2');
    });
  };

  // ══════════════════════════════════════════════════════════════════
  // Timeline 3 · Parallax multi-capa
  // ══════════════════════════════════════════════════════════════════
  const setupParallax = () => {
    if (prefersReducedMotion()) return;

    const pairs = [
      { sel: '.orb--violet',   y: -150 },
      { sel: '.orb--rose',     y:  -80 },
      { sel: '.orb--gold',     y: -200 },
      { sel: '.orb--lavender', y: -120 },
      { sel: '.hero-title',    y:  -50 },
    ];

    pairs.forEach(({ sel, y }) => {
      const el = document.querySelector(sel);
      if (!el) return;
      g.to(el, {
        y,
        ease: 'none',
        scrollTrigger: {
          trigger: 'body',
          start: 'top top',
          end: 'bottom top',
          scrub: true,
        },
      });
    });

    const sub = document.querySelector('.hero-sub');
    if (sub) {
      g.to(sub, {
        y: -30,
        opacity: 0.3,
        ease: 'none',
        scrollTrigger: {
          trigger: 'body',
          start: 'top top',
          end: 'bottom top',
          scrub: true,
        },
      });
    }
  };

  // ══════════════════════════════════════════════════════════════════
  // startOrbFloat · loop idle suave (complemento del parallax)
  // ══════════════════════════════════════════════════════════════════
  const startOrbFloat = () => {
    if (prefersReducedMotion()) return;
    document.querySelectorAll('.bg-mesh .orb').forEach((orb, i) => {
      g.to(orb, {
        x: `+=${randomBetween(-30, 30)}`,
        y: `+=${randomBetween(-20, 20)}`,
        duration: randomBetween(6, 10),
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut',
        delay: i * 0.3,
      });
    });
  };

  // ══════════════════════════════════════════════════════════════════
  // Timeline 4 · Login modal entrance / exit
  // ══════════════════════════════════════════════════════════════════
  const playLoginModal = () => new Promise((resolve) => {
    const backdrop = document.getElementById('modal-login');
    if (!backdrop) return resolve();

    // Resetear el display inline para que el CSS (display:grid + place-items:center)
    // centre el modal correctamente. Usar flex rompe el centrado horizontal.
    backdrop.style.display = '';
    const modal = backdrop.querySelector('.modal');
    const children = modal ? modal.children : [];

    if (prefersReducedMotion()) {
      g.set(backdrop, { opacity: 1 });
      g.set(modal, { opacity: 1, x: 0, y: 0, scale: 1 });
      resolve();
      return;
    }

    g.set(backdrop, { opacity: 0 });
    g.set(modal, { opacity: 0, x: 0, y: 50, scale: 0.95 });
    g.set(children, { opacity: 0, y: 12 });

    const tl = g.timeline({ onComplete: resolve });
    tl.to(backdrop, { opacity: 1, duration: 0.5, ease: 'fluid' })
      .to(modal, {
        opacity: 1,
        y: 0,
        scale: 1,
        duration: 0.7,
        ease: 'back.out(1.5)',
      }, '-=0.3')
      .to(children, {
        opacity: 1,
        y: 0,
        duration: 0.4,
        stagger: 0.06,
        ease: 'soft',
      }, '-=0.3');
  });

  const hideLoginModal = () => new Promise((resolve) => {
    const backdrop = document.getElementById('modal-login');
    if (!backdrop) return resolve();
    const modal = backdrop.querySelector('.modal');

    if (prefersReducedMotion()) {
      backdrop.style.display = 'none';
      resolve();
      return;
    }

    g.timeline({
      onComplete: () => { backdrop.style.display = 'none'; resolve(); },
    })
      .to(modal, { y: 20, scale: 0.97, opacity: 0, duration: 0.35, ease: 'fluid' })
      .to(backdrop, { opacity: 0, duration: 0.3, ease: 'fluid' }, '-=0.2');
  });

  // ══════════════════════════════════════════════════════════════════
  // Timeline 5 · Progress bar
  // ══════════════════════════════════════════════════════════════════
  const _progressProxy = { pct: 0 };

  const updateProgress = (pct) => {
    const fill = document.getElementById('progress-fill');
    const label = document.getElementById('progress-percent');
    if (!fill) return;

    const clamped = Math.max(0, Math.min(100, Number(pct) || 0));

    g.to(fill, {
      width: `${clamped}%`,
      duration: 0.5,
      ease: 'power2.out',
      overwrite: 'auto',
    });

    g.to(_progressProxy, {
      pct: clamped,
      duration: 0.5,
      ease: 'power2.out',
      snap: { pct: 0.1 },
      overwrite: 'auto',
      onUpdate: () => {
        if (label) label.textContent = `${_progressProxy.pct.toFixed(1)}%`;
      },
    });
  };

  // ══════════════════════════════════════════════════════════════════
  // Timeline 6 · Celebración (pétalos + glow)
  // ══════════════════════════════════════════════════════════════════
  const PETAL_COLORS = ['#ab8be2', '#e8a5bf', '#c9b2f0', '#e8c976'];

  const celebrate = (cardEl) => new Promise((resolve) => {
    const progress = document.getElementById('progress-panel');
    const success = document.getElementById('status-success');
    const link = document.getElementById('download-link');

    if (prefersReducedMotion()) {
      if (progress) progress.style.display = 'none';
      if (success) success.style.display = 'block';
      resolve();
      return;
    }

    const master = g.timeline({ onComplete: resolve });

    if (progress) {
      master.to(progress, { opacity: 0, y: -10, duration: 0.4, ease: 'fluid' });
    }

    // Spawn pétalos
    const origin = (cardEl || success || document.body).getBoundingClientRect();
    const cx = origin.left + origin.width / 2;
    const cy = origin.top + origin.height / 2;

    const petals = [];
    const count = 26;
    for (let i = 0; i < count; i++) {
      const p = document.createElement('div');
      const size = randomBetween(8, 16);
      p.style.cssText = `
        position:fixed;
        left:${cx}px;
        top:${cy}px;
        width:${size}px;
        height:${size * 1.6}px;
        background:${PETAL_COLORS[i % PETAL_COLORS.length]};
        border-radius:60% 40% 50% 70% / 70% 50% 70% 40%;
        pointer-events:none;
        z-index:9999;
        opacity:0.9;
        transform:translate(-50%,-50%);
      `;
      document.body.appendChild(p);
      petals.push(p);
    }

    master.add(() => {
      petals.forEach((p) => {
        g.to(p, {
          x: randomBetween(-260, 260),
          y: randomBetween(-80, 260),
          rotation: randomBetween(-360, 360),
          opacity: 0,
          duration: randomBetween(1.5, 2.5),
          ease: 'power2.out',
          onComplete: () => p.remove(),
        });
      });
    });

    if (success) {
      master.add(() => { success.style.display = 'block'; })
        .fromTo(success,
          { opacity: 0, y: 15 },
          { opacity: 1, y: 0, duration: 0.6, ease: 'soft' });
    }

    if (link) {
      master.fromTo(link,
        { opacity: 0, y: 15 },
        { opacity: 1, y: 0, duration: 0.5, ease: 'soft' }, '-=0.3')
        .to(link, {
          boxShadow: '0 12px 40px rgba(171, 139, 226, 0.55)',
          duration: 0.5,
          yoyo: true,
          repeat: 1,
          ease: 'sine.inOut',
        });
    }
  });

  // ══════════════════════════════════════════════════════════════════
  // Hide success card (dismiss animado)
  // ══════════════════════════════════════════════════════════════════
  const hideSuccess = (successEl) => new Promise((resolve) => {
    if (!successEl) { resolve(); return; }
    if (prefersReducedMotion()) {
      successEl.style.display = 'none';
      resolve();
      return;
    }
    g.to(successEl, {
      opacity: 0,
      y: -20,
      scale: 0.97,
      duration: 0.5,
      ease: 'power2.in',
      onComplete: () => {
        // Limpiamos solo las props animadas; display lo seteamos después.
        g.set(successEl, { clearProps: 'opacity,transform,y,scale' });
        successEl.style.display = 'none';
        resolve();
      },
    });
  });

  // ══════════════════════════════════════════════════════════════════
  // Timeline 7 · ScrollTrigger reveal del historial
  // ══════════════════════════════════════════════════════════════════
  const setupHistoryScroll = () => {
    if (prefersReducedMotion()) return;

    ST.batch('.history-item', {
      start: 'top 85%',
      onEnter: (batch) => {
        g.fromTo(batch,
          { x: -30, opacity: 0 },
          { x: 0, opacity: 1, duration: 0.7, stagger: 0.08, ease: 'fluid', overwrite: true }
        );
      },
      onLeaveBack: (batch) => {
        g.to(batch, { x: -30, opacity: 0, duration: 0.3, ease: 'fluid', overwrite: true });
      },
    });
  };

  // ══════════════════════════════════════════════════════════════════
  // Timeline 8 · Flip entre tabs del historial
  // ══════════════════════════════════════════════════════════════════
  /**
   * @param {Function} mutateCallback  sync function que cambia el DOM
   *   (ej. history.js hace el swap de items)
   */
  const switchTabFlip = (mutateCallback) => {
    const items = document.querySelectorAll('.history-item');
    const state = Flip.getState(items, { props: 'opacity' });

    try { mutateCallback(); } catch (e) { console.error('[switchTabFlip] mutate error', e); }

    Flip.from(state, {
      duration: prefersReducedMotion() ? 0 : 0.7,
      ease: 'fluid',
      absolute: true,
      scale: true,
      onEnter: (els) => g.fromTo(els,
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.5, stagger: 0.05, ease: 'soft' }),
      onLeave: (els) => g.to(els,
        { opacity: 0, y: -10, duration: 0.3, ease: 'fluid' }),
    });
  };

  // ══════════════════════════════════════════════════════════════════
  // Timeline 9 · Share modal con Flip desde el trigger
  // ══════════════════════════════════════════════════════════════════
  const openShareModalFlip = (triggerEl) => {
    const modalBackdrop = document.getElementById('modal-share');
    if (!modalBackdrop) return;
    const modal = modalBackdrop.querySelector('.modal');

    if (prefersReducedMotion() || !triggerEl) {
      modalBackdrop.style.display = '';
      g.set(modalBackdrop, { opacity: 1 });
      return;
    }

    const state = Flip.getState(triggerEl);
    modalBackdrop.style.display = '';
    g.set(modalBackdrop, { opacity: 0 });
    g.to(modalBackdrop, { opacity: 1, duration: 0.4, ease: 'fluid' });

    Flip.from(state, {
      targets: modal,
      duration: 0.7,
      ease: 'fluid',
      absolute: true,
      scale: true,
    });
  };

  // ══════════════════════════════════════════════════════════════════
  // Timeline 10 · Cursor custom (desktop only)
  // ══════════════════════════════════════════════════════════════════
  const initCustomCursor = () => {
    const canHover = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    if (!canHover || prefersReducedMotion()) return;

    const dot = document.createElement('div');
    dot.className = 'laguitos-cursor-dot';
    dot.style.cssText = `
      position:fixed; top:0; left:0;
      width:8px; height:8px;
      background:#8b6dd1;
      border-radius:50%;
      pointer-events:none;
      z-index:10000;
      transform:translate(-50%,-50%);
    `;

    const ring = document.createElement('div');
    ring.className = 'laguitos-cursor-ring';
    ring.style.cssText = `
      position:fixed; top:0; left:0;
      width:36px; height:36px;
      border:1.5px solid rgba(139, 109, 209, 0.55);
      border-radius:50%;
      pointer-events:none;
      z-index:9999;
      transform:translate(-50%,-50%);
      box-shadow:0 0 20px rgba(171, 139, 226, 0.35);
      backdrop-filter:blur(2px);
      transition:background 0.2s;
    `;

    document.body.appendChild(ring);
    document.body.appendChild(dot);
    document.body.style.cursor = 'none';

    const setDotX = g.quickTo(dot, 'x', { duration: 0.15, ease: 'power3.out' });
    const setDotY = g.quickTo(dot, 'y', { duration: 0.15, ease: 'power3.out' });
    const setRingX = g.quickTo(ring, 'x', { duration: 0.4, ease: 'power3.out' });
    const setRingY = g.quickTo(ring, 'y', { duration: 0.4, ease: 'power3.out' });

    window.addEventListener('mousemove', (e) => {
      setDotX(e.clientX); setDotY(e.clientY);
      setRingX(e.clientX); setRingY(e.clientY);
    });

    const interactiveSel = 'a, button, [role="button"], input, select, textarea, [data-cursor="link"]';
    document.addEventListener('mouseover', (e) => {
      if (e.target.closest && e.target.closest(interactiveSel)) {
        g.to(ring, {
          scale: 1.3,
          duration: 0.3,
          ease: 'soft',
          borderColor: 'rgba(139, 109, 209, 0.7)',
          boxShadow: '0 0 8px rgba(171, 139, 226, 0.25)',
        });
      }
    });
    document.addEventListener('mouseout', (e) => {
      if (e.target.closest && e.target.closest(interactiveSel)) {
        g.to(ring, {
          scale: 1,
          duration: 0.3,
          ease: 'soft',
          borderColor: 'rgba(139, 109, 209, 0.55)',
          boxShadow: '0 0 20px rgba(171, 139, 226, 0.35)',
        });
      }
    });
  };

  // ══════════════════════════════════════════════════════════════════
  // API pública
  // ══════════════════════════════════════════════════════════════════
  return {
    playLoader,
    playPageLoad,
    playLoginModal,
    hideLoginModal,
    updateProgress,
    celebrate,
    hideSuccess,
    setupParallax,
    setupHistoryScroll,
    switchTabFlip,
    openShareModalFlip,
    startOrbFloat,
    initCustomCursor,
    prefersReducedMotion,
  };
})();
