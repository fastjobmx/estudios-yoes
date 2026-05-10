/* ============================================================
   CONCIENCIA REVOLUCIONARIA — Shared App Logic
   ============================================================ */

'use strict';

/* ── Reveal on scroll ── */
export function initReveal() {
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -48px 0px' });
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));
  return io;
}

/* ── Navbar scroll ── */
export function initNavbar(id = 'navbar') {
  const nav = document.getElementById(id);
  if (!nav) return;
  const onScroll = () => nav.classList.toggle('is-scrolled', window.scrollY > 24);
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

/* ── Progress bar ── */
export function initProgress(id = 'progressBar') {
  const bar = document.getElementById(id);
  if (!bar) return;
  window.addEventListener('scroll', () => {
    const h = document.documentElement.scrollHeight - innerHeight;
    if (h > 0) bar.style.width = Math.min(100, (scrollY / h) * 100) + '%';
  }, { passive: true });
}

/* ── Mobile menu ── */
export function initMobileMenu(btnId = 'menuBtn', menuId = 'mobileMenu') {
  const btn = document.getElementById(btnId);
  const menu = document.getElementById(menuId);
  if (!btn || !menu) return;
  btn.addEventListener('click', () => {
    const open = menu.classList.toggle('hidden') === false;
    btn.setAttribute('aria-expanded', String(open));
  });
  menu.querySelectorAll('a').forEach(a =>
    a.addEventListener('click', () => menu.classList.add('hidden'))
  );
}

/* ── Cursor glow ── */
export function initCursorGlow(id = 'cursorGlow') {
  const glow = document.getElementById(id);
  if (!glow || window.matchMedia('(pointer: coarse)').matches) return;
  window.addEventListener('mousemove', e => {
    glow.style.left = e.clientX + 'px';
    glow.style.top  = e.clientY + 'px';
  }, { passive: true });
}

/* ── Magnetic cards ── */
export function initMagneticCards(selector = '.magnetic-card') {
  document.querySelectorAll(selector).forEach(card => {
    card.addEventListener('mousemove', e => {
      const r = card.getBoundingClientRect();
      const rx = ((e.clientY - r.top)  / r.height - 0.5) * -6;
      const ry = ((e.clientX - r.left) / r.width  - 0.5) *  6;
      card.style.transform = `perspective(900px) rotateX(${rx}deg) rotateY(${ry}deg) translateY(-4px)`;
    });
    card.addEventListener('mouseleave', () => { card.style.transform = ''; });
  });
}

/* ── Normalize string for search ── */
export function normalize(str) {
  return String(str).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

/* ── Fetch JSON with error handling ── */
export async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
