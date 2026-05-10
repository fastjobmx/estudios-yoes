"""
Generates index.html with all real content from content.json
"""
import json, re, os

BASE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE, 'assets', 'content.json'), encoding='utf-8') as f:
    d = json.load(f)

def esc(s):
    return (str(s)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))

def paras_html(raw, max_chars=2800):
    raw = re.sub(r'\s+', ' ', str(raw)).strip()[:max_chars]
    # Split on sentence endings
    parts = re.split(r'(?<=[\.!?])\s+', raw)
    paras, cur = [], []
    for p in parts:
        cur.append(p)
        if len(' '.join(cur)) > 300:
            paras.append(' '.join(cur))
            cur = []
    if cur:
        paras.append(' '.join(cur))
    result = ''
    for p in paras:
        if p.strip():
            result += '<p>' + esc(p) + '</p>\n              '
    return result

def tags_from_title(title):
    keywords = {
        'muerte': 'Muerte', 'ego': 'Ego', 'conciencia': 'Conciencia',
        'meditac': 'Meditación', 'karma': 'Karma', 'yo': 'Yoes',
        'astral': 'Astral', 'cuerpo': 'Cuerpos', 'dimensi': 'Dimensiones',
        'fuego': 'Fuego Sagrado', 'chakra': 'Chakras', 'iglesia': 'Iglesias',
        'sexo': 'Magia Sexual', 'sexual': 'Magia Sexual', 'traici': 'Traición',
        'miedo': 'Miedo', 'bruj': 'Brujería', 'pendulo': 'Ley del Péndulo',
        'factor': 'Tres Factores', 'sacrif': 'Sacrificio', 'origen': 'Origen del Ego',
        'dualidad': 'Dualidad', 'karma': 'Karma', 'dharma': 'Dharma',
        'retorno': 'Retorno', 'recurrencia': 'Recurrencia',
        'alma': 'Alma y Espíritu', 'esencia': 'Esencia',
        'fanatismo': 'Fanatismo', 'exoterismo': 'Esoterismo',
        'concentraci': 'Concentración', 'relajaci': 'Relajación',
        'conjuraci': 'Conjuraciones', 'droga': 'Drogas',
        'alcohol': 'Alcoholismo', 'observaci': 'Auto-Observación',
        'familia': 'Familia', 'apego': 'Apegos',
    }
    t = title.lower()
    tags = []
    for k, v in keywords.items():
        if k in t and v not in tags:
            tags.append(v)
    return tags[:3]

# ─────────────────────────────────────────
# Build Fase A accordion items
# ─────────────────────────────────────────
def accordion_item(num_str, title, text, stagger_idx, prefix=''):
    stagger = (stagger_idx % 6) + 1
    tags = tags_from_title(title)
    tag_html = ''
    for tg in tags:
        tag_html += '<span class="lecture-tag">' + esc(tg) + '</span>'
    content_html = paras_html(text)
    num_display = prefix + str(num_str).zfill(2) if not prefix else prefix + str(num_str).zfill(2)

    return f'''
        <div class="accordion-item fade-up stagger-{stagger}">
          <div class="accordion-header">
            <span class="accordion-num">{esc(num_display)}</span>
            <span class="accordion-title">{esc(title)}</span>
            <span class="accordion-icon"></span>
          </div>
          <div class="accordion-body">
            <div class="accordion-content">
              {content_html}
              <div class="lecture-tags">{tag_html}</div>
            </div>
          </div>
        </div>'''

fase_a_html = ''
for i, c in enumerate(d['fase_a']):
    fase_a_html += accordion_item(c['num'], c['title'], c['text'], i, prefix='')

fase_b_html = ''
for i, c in enumerate(d['fase_b']):
    fase_b_html += accordion_item(c['num'], c['title'], c['text'], i, prefix='B-')

# ─────────────────────────────────────────
# Build Yoes cards
# ─────────────────────────────────────────
def yo_card(i, yo):
    stagger = (i % 6) + 1
    title = yo['title']
    text = yo['text']
    preview = re.sub(r'\s+', ' ', text)[:320].strip()
    # Full content in accordion-style expandable
    full_paras = paras_html(text, max_chars=5000)
    num_display = str(i + 1).zfill(2)

    return f'''
      <div class="yo-card yo-card-full fade-up stagger-{stagger}">
        <span class="yo-tag">Estudio {num_display}</span>
        <h3 class="yo-title">{esc(title)}</h3>
        <p class="yo-desc yo-preview">{esc(preview)}...</p>
        <div class="yo-full-content" style="display:none;">
          {full_paras}
        </div>
        <button class="yo-link yo-toggle" type="button">Leer el estudio completo</button>
      </div>'''

yoes_html = ''
for i, yo in enumerate(d['yoes']):
    yoes_html += yo_card(i, yo)

# ─────────────────────────────────────────
# HTML TEMPLATE
# ─────────────────────────────────────────
html = '''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="Conciencia Revolucionaria — Un camino hacia la Auto-Realización Íntima a través de los Tres Factores de la Revolución de la Conciencia." />
  <title>Conciencia Revolucionaria</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            bg: "#0A0A0A", surface: "#111111",
            gold: "#C5A059", "gold-light": "#E8C97A", "text-muted": "#9A9A9A"
          },
          fontFamily: {
            sans: ["Montserrat","sans-serif"],
            serif: ["Cormorant Garamond","serif"]
          }
        }
      }
    }
  </script>
  <link rel="stylesheet" href="styles.css" />
</head>
<body class="bg-bg text-[#F5F5F5]">

  <div class="reading-progress"></div>

  <!-- ── NAVIGATION ── -->
  <nav id="navbar" aria-label="Navegación principal">
    <a href="#hero" class="nav-logo">
      <img src="assets/logo.png" alt="Conciencia Revolucionaria Logo" onerror="this.onerror=null;this.src=\'assets/logo1.svg\';" />
      <span class="nav-logo-text">Conciencia Revolucionaria</span>
    </a>
    <ul class="nav-links">
      <li><a href="#pilares">Pilares</a></li>
      <li><a href="#yoes">Estudios</a></li>
      <li><a href="#factores">Los 3 Factores</a></li>
      <li><a href="#biblioteca">Biblioteca</a></li>
    </ul>
    <div class="hamburger" role="button" aria-label="Menú" tabindex="0">
      <span></span><span></span><span></span>
    </div>
  </nav>

  <div class="mobile-menu" role="dialog" aria-modal="true">
    <a href="#pilares">Pilares</a>
    <a href="#yoes">Estudios de los Yoes</a>
    <a href="#factores">Los 3 Factores</a>
    <a href="#biblioteca">Biblioteca</a>
  </div>

  <!-- ── HERO ── -->
  <section id="hero" aria-label="Hero">
    <div class="hero-radial"></div>
    <img src="assets/logo.png" alt="Logo Conciencia Revolucionaria"
         class="hero-logo fade-in"
         onerror="this.onerror=null;this.src=\'assets/logo1.svg\';" />
    <p class="hero-eyebrow fade-up stagger-1">Escuela de Auto-Conocimiento</p>
    <h1 class="hero-title fade-up stagger-2">
      Conocimiento de Sí Mismo:<br/>
      <span>La Revolución de la Dialéctica</span>
    </h1>
    <p class="hero-subtitle fade-up stagger-3">
      Un camino hacia la Auto-Realización Íntima a través de los
      Tres Factores de la Revolución de la Conciencia.
    </p>
    <a href="#biblioteca" class="btn-primary fade-up stagger-4">Iniciar el Trabajo</a>
    <div class="hero-scroll fade-in stagger-5" aria-hidden="true">
      <span>Descender</span>
      <div class="scroll-line"></div>
    </div>
  </section>

  <!-- ── 4 PILARES ── -->
  <section id="pilares" aria-label="Los 4 Pilares de la Sabiduría">
    <div class="max-w-6xl mx-auto text-center">
      <p class="section-label fade-up">Fundamentos</p>
      <div class="divider divider-center fade-up stagger-1"></div>
      <h2 class="section-title fade-up stagger-2">Los Cuatro Pilares<br/>de la Sabiduría</h2>
      <p class="mt-4 text-[0.82rem] text-[#9A9A9A] max-w-xl mx-auto leading-relaxed fade-up stagger-3">
        La sabiduría integral no puede edificarse sobre un solo ángulo de comprensión.
        Ciencia, Arte, Psicología y Filosofía son los cuatro vértices del templo interior.
      </p>
    </div>
    <div class="pilares-grid fade-up stagger-2">
      <div class="pilar-card">
        <p class="pilar-number">01</p>
        <svg class="pilar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m0 0h10a2 2 0 0 0 2-2V9M9 21H5a2 2 0 0 1-2-2V9m0 0h18"/></svg>
        <h3 class="pilar-title">Ciencia</h3>
        <p class="pilar-desc">La ciencia sagrada investiga las leyes que gobiernan la existencia con rigor y precisión. No para acumular datos, sino para disolver la ignorancia fundamental que nos mantiene dormidos ante la realidad de nuestra propia naturaleza interior.</p>
      </div>
      <div class="pilar-card">
        <p class="pilar-number">02</p>
        <svg class="pilar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 12s1.5-2 4-2 4 2 4 2"/><path d="M9 9h.01M15 9h.01"/></svg>
        <h3 class="pilar-title">Arte</h3>
        <p class="pilar-desc">El Arte es el lenguaje del alma. A través de sus formas, colores y símbolos, la conciencia se expresa más allá de las limitaciones del intelecto ordinario. El arte genuino eleva, despierta y señala hacia lo eterno que habita en cada ser humano.</p>
      </div>
      <div class="pilar-card">
        <p class="pilar-number">03</p>
        <svg class="pilar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
        <h3 class="pilar-title">Psicología</h3>
        <p class="pilar-desc">La Psicología Revolucionaria estudia el "Ego" o conjunto de agregados psicológicos que fragmentan la conciencia. Conocer el funcionamiento mecánico de los "Yoes" internos es el primer y más honesto paso hacia la transformación radical del ser.</p>
      </div>
      <div class="pilar-card">
        <p class="pilar-number">04</p>
        <svg class="pilar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
        <h3 class="pilar-title">Filosofía</h3>
        <p class="pilar-desc">La Filosofía Perenne nos invita a cuestionar lo que consideramos verdadero, a trascender el pensamiento superficial y a indagar en las preguntas esenciales del ser. No como ejercicio intelectual, sino como herramienta viva de auto-investigación radical.</p>
      </div>
    </div>
  </section>

  <!-- ── LOS 3 FACTORES ── -->
  <section id="factores" aria-label="Los Tres Factores">
    <div class="max-w-6xl mx-auto text-center">
      <p class="section-label fade-up">El Camino</p>
      <div class="divider divider-center fade-up stagger-1"></div>
      <h2 class="section-title fade-up stagger-2">Los Tres Factores de la<br/><span class="gold">Revolución de la Conciencia</span></h2>
      <p class="mt-4 text-[0.82rem] text-[#9A9A9A] max-w-xl mx-auto leading-relaxed fade-up stagger-3">
        Tres operaciones simultáneas e inseparables que constituyen el método integral del trabajo interno sobre sí mismo.
      </p>
    </div>
    <div class="factores-grid fade-up stagger-3">
      <div class="factor-card">
        <p class="factor-roman">I</p>
        <h3 class="factor-title">Nacer</h3>
        <p class="factor-desc">La creación del Cuerpo Solar del Hombre, la cristalización de los vehículos superiores del ser a través de la Magia Sexual. El Fuego Sagrado como principio creativo y transformador.</p>
      </div>
      <div class="factor-card">
        <p class="factor-roman">II</p>
        <h3 class="factor-title">Morir</h3>
        <p class="factor-desc">La disolución psicológica del Ego. La muerte interior de los agregados, defectos y "Yoes" que fragmentan la conciencia y producen el sufrimiento. Morir en vida para verdaderamente vivir.</p>
      </div>
      <div class="factor-card">
        <p class="factor-roman">III</p>
        <h3 class="factor-title">Sacrificio</h3>
        <p class="factor-desc">El servicio a la humanidad doliente como expresión del amor consciente. Trabajar en el despertar de los demás, sin esperar recompensa ni reconocimiento. El sacrificio como la máxima nobleza del espíritu.</p>
      </div>
    </div>
  </section>

  <!-- ── HUB YOES ── -->
  <section id="yoes" aria-label="Estudios de los Yoes">
    <div class="max-w-6xl mx-auto text-center">
      <p class="section-label fade-up">Agregados Psicológicos</p>
      <div class="divider divider-center fade-up stagger-1"></div>
      <h2 class="section-title fade-up stagger-2">Hub de Estudios<br/>de los Yoes</h2>
      <p class="mt-4 text-[0.82rem] text-[#9A9A9A] max-w-xl mx-auto leading-relaxed fade-up stagger-3">
        Cada "Yo" interno es un fragmento de conciencia atrapado en un defecto.
        Conocerlos, comprenderlos y disolverlos es la tarea más urgente del buscador.
      </p>
    </div>
    <div class="yoes-grid">
      ''' + yoes_html + '''
    </div>
  </section>

  <!-- ── BIBLIOTECA ── -->
  <section id="biblioteca" aria-label="Biblioteca Doctrinal">
    <div class="max-w-4xl mx-auto text-center">
      <p class="section-label fade-up">Biblioteca Doctrinal</p>
      <div class="divider divider-center fade-up stagger-1"></div>
      <h2 class="section-title fade-up stagger-2">Conferencias &amp; Lecciones</h2>
      <p class="mt-4 text-[0.82rem] text-[#9A9A9A] max-w-xl mx-auto leading-relaxed fade-up stagger-3">
        Dos fases de estudio sistemático. Cada texto es una herramienta viva para la comprensión y la práctica. Lee despacio. Lee con presencia.
      </p>
    </div>

    <div class="biblioteca-tabs fade-up stagger-3">
      <button class="tab-btn active" data-tab="fase-a">Fase A — 50 Conferencias</button>
      <button class="tab-btn" data-tab="fase-b">Fase B — 25 Lecciones</button>
    </div>

    <div id="fase-a" class="tab-panel active">
      <div class="accordion-container">
        ''' + fase_a_html + '''
      </div>
    </div>

    <div id="fase-b" class="tab-panel">
      <div class="accordion-container">
        ''' + fase_b_html + '''
      </div>
    </div>
  </section>

  <!-- ── FOOTER ── -->
  <footer>
    <img src="assets/logo.png" alt="Logo" class="footer-logo"
         onerror="this.onerror=null;this.src=\'assets/logo1.svg\';" />
    <p class="footer-phrase">"La muerte es la puerta a <span>la vida</span>"</p>
    <nav class="social-links" aria-label="Redes sociales">
      <a href="#" aria-label="YouTube">YouTube</a>
      <a href="#" aria-label="Telegram">Telegram</a>
      <a href="#" aria-label="Facebook">Facebook</a>
      <a href="#" aria-label="Instagram">Instagram</a>
    </nav>
    <p class="footer-copy">&copy; <span id="year"></span> Conciencia Revolucionaria &nbsp;&middot;&nbsp; Todos los derechos reservados</p>
  </footer>

  <script src="script.js"></script>
  <script>
    document.getElementById("year").textContent = new Date().getFullYear();
  </script>
</body>
</html>'''

out_path = os.path.join(BASE, 'index.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

size = os.path.getsize(out_path)
print(f'index.html generado: {size:,} bytes')
print(f'Fase A: {len(d["fase_a"])} conferencias')
print(f'Fase B: {len(d["fase_b"])} lecciones')
print(f'Yoes:   {len(d["yoes"])} estudios')
