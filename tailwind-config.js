/* ============================================================
   CONCIENCIA REVOLUCIONARIA — Tailwind Config Unificada
   Cargar ANTES del CDN de Tailwind en todas las páginas:
     <script src="tailwind-config.js"></script>
     <script src="https://cdn.tailwindcss.com"></script>
   ============================================================ */
window.tailwind = window.tailwind || {};
window.tailwind.config = {
  theme: {
    extend: {
      colors: {
        void:    '#050505',
        ink:     '#0B0B0C',
        obsidian:'#111113',
        ash:     '#B6B0A8',
        bone:    '#F6F0E7',
        gold:    '#C6A15B',
        gold2:   '#F0D58C',
        ember:   '#7A3F22'
      },
      fontFamily: {
        sans:  ['Inter', 'Montserrat', 'system-ui', 'sans-serif'],
        serif: ['Cormorant Garamond', 'Georgia', 'serif']
      }
    }
  }
};
