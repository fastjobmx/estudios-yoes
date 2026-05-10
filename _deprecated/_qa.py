"""QA completo del proyecto Conciencia Revolucionaria."""
import json, os, re

ROOT = r'C:\Users\Walter Losada\Desktop\ESTUDIOS YOES'

# ── 1. JSON validity + data integrity ─────────────────────────────────────
print("=" * 60)
print("1. DATOS JSON")
print("=" * 60)

with open(os.path.join(ROOT, 'data', 'conferencias.json'), encoding='utf-8') as f:
    confs = json.load(f)
with open(os.path.join(ROOT, 'data', 'yoes.json'), encoding='utf-8') as f:
    yoes = json.load(f)

all_items = confs + yoes

# IDs duplicados
ids = [x['id'] for x in all_items]
dupes = [id for id in ids if ids.count(id) > 1]
print("IDs duplicados:", dupes or "ninguno")

# IDs vacíos
empties = [x.get('id','') for x in all_items if not x.get('id')]
print("IDs vacíos:", empties or "ninguno")

# Content vacío
no_content = [x['id'] for x in all_items if not x.get('content')]
print("Sin content:", no_content or "ninguno")

# Verificar Fase A: 01..50
fa_ids = sorted([x['id'] for x in confs if x.get('phase') == 'A'])
expected_a = ['fase-a-' + str(i).zfill(2) for i in range(1, 51)]
missing_a = [e for e in expected_a if e not in fa_ids]
print("Fase A faltantes:", missing_a or "ninguno")

# Verificar Fase B: 01..25
fb_ids = sorted([x['id'] for x in confs if x.get('phase') == 'B'])
expected_b = ['fase-b-' + str(i).zfill(2) for i in range(1, 26)]
missing_b = [e for e in expected_b if e not in fb_ids]
print("Fase B faltantes:", missing_b or "ninguno")

# Yoes esperados
expected_yoes = ['yo-abatimiento','yo-conquistador','yo-machista','yo-miedo','yo-relacion-toxica','yo-meditacion-500']
yo_ids = [x['id'] for x in yoes]
missing_yoes = [e for e in expected_yoes if e not in yo_ids]
print("Yoes faltantes:", missing_yoes or "ninguno")

# fase-a-05 y 06
a05 = next((x for x in confs if x['id'] == 'fase-a-05'), None)
a06 = next((x for x in confs if x['id'] == 'fase-a-06'), None)
print("\nfase-a-05 title:", a05['title'][:60] if a05 else "FALTA")
print("fase-a-06 title:", a06['title'][:60] if a06 else "FALTA")
print("fase-a-06 note:", a06.get('note','(sin note)')[:80] if a06 else "N/A")

# ── 2. Links en index.html ─────────────────────────────────────────────────
print("\n" + "=" * 60)
print("2. LINKS EN index.html")
print("=" * 60)

with open(os.path.join(ROOT, 'index.html'), encoding='utf-8') as f:
    idx_html = f.read()

# Buscar todos los ?id= usados
id_refs = re.findall(r'conferencia\.html\?id=([\w-]+)', idx_html)
broken = [r for r in id_refs if r not in ids]
print("IDs referenciados:", id_refs)
print("Links rotos:", broken or "ninguno")

# ── 3. Archivos existentes ─────────────────────────────────────────────────
print("\n" + "=" * 60)
print("3. ARCHIVOS DEL PROYECTO")
print("=" * 60)

check_files = {
    'index.html': True,
    'conferencias.html': True,
    'conferencia.html': True,
    'cr-styles.css': True,
    'tailwind-config.js': True,
    'app.js': False,
    'README.md': True,
    'generate_json.py': False,
    'styles.css': False,          # debe estar en _deprecated
    'script.js': False,           # debe estar en _deprecated
    'build_html.py': False,       # debe estar en _deprecated
    'verify.py': False,
    'verify2.py': False,
    'verify3.py': False,
    '_deprecated/build_html.py': False,
    '_deprecated/script.js': False,
    '_deprecated/styles.css': False,
    'data/conferencias.json': True,
    'data/yoes.json': True,
}

for fname, required in check_files.items():
    exists = os.path.exists(os.path.join(ROOT, fname))
    status = "OK" if exists else ("FALTA" if required else "ausente")
    print(f"  {'[OK]' if exists else '[--]'} {fname} {'(requerido)' if required else ''}")

# ── 4. tailwind-config cargado antes del CDN ──────────────────────────────
print("\n" + "=" * 60)
print("4. ORDEN DE SCRIPTS (tailwind-config antes CDN)")
print("=" * 60)
for fname in ['index.html', 'conferencias.html', 'conferencia.html']:
    with open(os.path.join(ROOT, fname), encoding='utf-8') as f:
        html = f.read()
    pos_cfg = html.find('tailwind-config.js')
    pos_cdn = html.find('cdn.tailwindcss.com')
    if pos_cfg == -1:
        print(f"  {fname}: SIN tailwind-config.js — PROBLEMA")
    elif pos_cdn == -1:
        print(f"  {fname}: SIN CDN tailwind — PROBLEMA")
    elif pos_cfg < pos_cdn:
        print(f"  {fname}: orden OK (config={pos_cfg}, cdn={pos_cdn})")
    else:
        print(f"  {fname}: ORDEN INCORRECTO — config DESPUÉS del CDN")

# ── 5. OG/meta en cada HTML ───────────────────────────────────────────────
print("\n" + "=" * 60)
print("5. META / OG")
print("=" * 60)
for fname in ['index.html', 'conferencias.html', 'conferencia.html']:
    with open(os.path.join(ROOT, fname), encoding='utf-8') as f:
        html = f.read()
    has_og_title  = 'og:title'       in html
    has_og_desc   = 'og:description' in html
    has_og_img    = 'og:image'       in html
    has_tw_card   = 'twitter:card'   in html
    has_desc      = 'meta name="description"' in html
    placeholder   = 'og-image.jpg' in html  # placeholder, no real image
    print(f"  {fname}: og:title={has_og_title} og:desc={has_og_desc} og:img={has_og_img} tw:card={has_tw_card} meta-desc={has_desc} [img-placeholder={placeholder}]")

# ── 6. fetch yoes.json en conferencias y conferencia ──────────────────────
print("\n" + "=" * 60)
print("6. FETCH yoes.json")
print("=" * 60)
for fname in ['conferencias.html', 'conferencia.html']:
    with open(os.path.join(ROOT, fname), encoding='utf-8') as f:
        html = f.read()
    print(f"  {fname}: fetch yoes.json = {'SI' if 'yoes.json' in html else 'NO'}")

# ── 7. Modo foco ──────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("7. MODO FOCO")
print("=" * 60)
with open(os.path.join(ROOT, 'conferencia.html'), encoding='utf-8') as f:
    conf_html = f.read()
print("  focus-mode CSS oculta readerToolbar:", "readerToolbar" in conf_html and "focus-mode" in conf_html)
print("  exitFocusBtn existe:", "exitFocusBtn" in conf_html)
print("  btnFocus existe:", "btnFocus" in conf_html)

# ── 8. TOC buildTOC ──────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("8. TOC")
print("=" * 60)
print("  buildTOC definida:", "function buildTOC" in conf_html)
print("  secciones auto (Inicio/Desarrollo):", "'Inicio'" in conf_html or '"Inicio"' in conf_html)

print("\n" + "=" * 60)
print("QA COMPLETO")
print("=" * 60)
