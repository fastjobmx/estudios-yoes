/* ============================================================
   CONCIENCIA REVOLUCIONARIA — Main Script
   ============================================================ */

(function () {
  'use strict';

  /* ── Reading Progress Bar ── */
  const progressBar = document.querySelector('.reading-progress');
  function updateProgress() {
    const total = document.body.scrollHeight - window.innerHeight;
    const pct = total > 0 ? (window.scrollY / total) * 100 : 0;
    if (progressBar) progressBar.style.width = pct + '%';
  }

  /* ── Navbar scroll state ── */
  const navbar = document.getElementById('navbar');
  function handleNavbar() {
    if (!navbar) return;
    if (window.scrollY > 60) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  }

  /* ── Intersection Observer for fade animations ── */
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  function initAnimations() {
    document.querySelectorAll('.fade-up, .fade-in').forEach(el => observer.observe(el));
  }

  /* ── Hamburger Menu ── */
  const hamburger = document.querySelector('.hamburger');
  const mobileMenu = document.querySelector('.mobile-menu');

  function toggleMobileMenu() {
    if (!hamburger || !mobileMenu) return;
    hamburger.classList.toggle('open');
    mobileMenu.classList.toggle('open');
    document.body.style.overflow = mobileMenu.classList.contains('open') ? 'hidden' : '';
  }

  if (hamburger) hamburger.addEventListener('click', toggleMobileMenu);

  if (mobileMenu) {
    mobileMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        hamburger.classList.remove('open');
        mobileMenu.classList.remove('open');
        document.body.style.overflow = '';
      });
    });
  }

  /* ── Tab System (Biblioteca) ── */
  function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.dataset.tab;

        tabBtns.forEach(b => b.classList.remove('active'));
        tabPanels.forEach(p => p.classList.remove('active'));

        btn.classList.add('active');
        const panel = document.getElementById(target);
        if (panel) {
          panel.classList.add('active');
          // Re-observe newly visible fade elements
          panel.querySelectorAll('.fade-up, .fade-in').forEach(el => {
            if (!el.classList.contains('visible')) observer.observe(el);
          });
        }
      });
    });
  }

  /* ── Accordion System ── */
  function initAccordions() {
    document.querySelectorAll('.accordion-header').forEach(header => {
      header.addEventListener('click', () => {
        const item = header.closest('.accordion-item');
        const body = item.querySelector('.accordion-body');
        const isOpen = item.classList.contains('open');

        // Close all in same container
        const siblings = item.closest('.accordion-container')
          ? item.closest('.accordion-container').querySelectorAll('.accordion-item')
          : [];

        siblings.forEach(sib => {
          if (sib !== item) {
            sib.classList.remove('open');
            const sibBody = sib.querySelector('.accordion-body');
            if (sibBody) sibBody.classList.remove('open');
          }
        });

        // Toggle current
        item.classList.toggle('open', !isOpen);
        if (body) body.classList.toggle('open', !isOpen);
      });
    });
  }

  /* ── Smooth scroll for anchor links ── */
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', (e) => {
        const href = anchor.getAttribute('href');
        if (href === '#') return;
        const target = document.querySelector(href);
        if (target) {
          e.preventDefault();
          const offset = 80;
          const top = target.getBoundingClientRect().top + window.scrollY - offset;
          window.scrollTo({ top, behavior: 'smooth' });
        }
      });
    });
  }

  /* ── Scroll events ── */
  window.addEventListener('scroll', () => {
    updateProgress();
    handleNavbar();
  }, { passive: true });

  /* ── Yo Cards expand/collapse ── */
  function initYoCards() {
    document.querySelectorAll('.yo-toggle').forEach(btn => {
      btn.addEventListener('click', () => {
        const card = btn.closest('.yo-card-full');
        if (!card) return;
        const preview = card.querySelector('.yo-preview');
        const full = card.querySelector('.yo-full-content');
        const isOpen = card.classList.contains('expanded');

        if (!isOpen) {
          card.classList.add('expanded');
          if (full) full.style.display = 'block';
          if (preview) preview.style.display = 'none';
          btn.textContent = 'Cerrar estudio';
          btn.style.cssText = '';
          // Scroll card into view
          setTimeout(() => {
            card.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }, 50);
        } else {
          card.classList.remove('expanded');
          if (full) full.style.display = 'none';
          if (preview) preview.style.display = 'block';
          btn.textContent = 'Leer el estudio completo';
        }
      });
    });
  }

  /* ── Init ── */
  document.addEventListener('DOMContentLoaded', () => {
    handleNavbar();
    updateProgress();
    initAnimations();
    initTabs();
    initAccordions();
    initSmoothScroll();
    initYoCards();

    // Hero elements: trigger immediately
    document.querySelectorAll('#hero .fade-up, #hero .fade-in').forEach((el, i) => {
      setTimeout(() => el.classList.add('visible'), i * 180);
    });
  });
})();
