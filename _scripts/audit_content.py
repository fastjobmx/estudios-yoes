"""
audit_content.py — Auditoría de fidelidad de data/conferencias.json y data/yoes.json
Genera _reports/content-audit.md
"""
import json, os, re
from datetime import datetime

ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONF_F  = os.path.join(ROOT, 'data', 'conferencias.json')
YOES_F  = os.path.join(ROOT, 'data', 'yoes.json')
OUT_F   = os.path.join(ROOT, '_reports', 'content-audit.md')

PLACEHOLDER_RE = re.compile(
    r'\b(placeholder|lorem|ipsum|aqui va|aquí va|pendiente|falta|TODO|TBD|xxx)\b',
    re.IGNORECASE
)

EXPECTED_A_IDS = ['fase-a-' + str(i).zfill(2) for i in range(1, 51)]
EXPECTED_B_IDS = ['fase-b-' + str(i).zfill(2) for i in range(1, 26)]
EXPECTED_YO_IDS = [
    'yo-abatimiento', 'yo-conquistador', 'yo-machista',
    'yo-miedo', 'yo-relacion-toxica', 'yo-meditacion-500'
]

# ── Carga ─────────────────────────────────────────────────────────────────
with open(CONF_F, encoding='utf-8') as f:
    confs = json.load(f)
with open(YOES_F, encoding='utf-8') as f:
    yoes = json.load(f)

all_items = confs + yoes
ids_all = [x['id'] for x in all_items]

# ── Helpers ───────────────────────────────────────────────────────────────
def word_count(content):
    total = 0
    for b in (content or []):
        txt = b.get('text','') or ' '.join(b.get('items', b.get('steps', [])))
        total += len(txt.split())
    return total

def has_placeholder(content):
    for b in (content or []):
        txt = b.get('text','') or ''
        if PLACEHOLDER_RE.search(txt):
            return True
    return False

def required_fields_missing(obj, fields):
    return [f for f in fields if f not in obj or not obj[f]]

# ── Análisis conferencias ─────────────────────────────────────────────────
fa = [x for x in confs if x.get('phase') == 'A']
fb = [x for x in confs if x.get('phase') == 'B']
fa_ids = [x['id'] for x in fa]
fb_ids = [x['id'] for x in fb]

missing_a      = [i for i in EXPECTED_A_IDS if i not in fa_ids]
missing_b      = [i for i in EXPECTED_B_IDS if i not in fb_ids]
duplicate_ids  = [i for i in ids_all if ids_all.count(i) > 1]
duplicate_ids  = list(set(duplicate_ids))

CONF_REQUIRED = ['id','phase','number','title','page','summary','tags','content']

incomplete     = []  # Faltan campos obligatorios
short          = []  # < 300 palabras (sospechosamente corto)
very_short     = []  # < 150 palabras (crítico)
placeholder_c  = []  # Texto placeholder detectado
no_images      = []  # Sin bloques de imagen
with_images    = []  # Con bloques de imagen

for c in confs:
    missing_f = required_fields_missing(c, CONF_REQUIRED)
    wc = word_count(c.get('content', []))
    ph = has_placeholder(c.get('content', []))
    imgs = [b for b in c.get('content',[]) if b.get('type') == 'image']

    if missing_f:
        incomplete.append({'id': c['id'], 'missing': missing_f})
    if wc < 150:
        very_short.append({'id': c['id'], 'words': wc, 'title': c.get('title','')[:50]})
    elif wc < 300:
        short.append({'id': c['id'], 'words': wc, 'title': c.get('title','')[:50]})
    if ph:
        placeholder_c.append(c['id'])
    if imgs:
        with_images.append(c['id'])
    else:
        no_images.append(c['id'])

# Títulos duplicados sospechosos
titles = [c.get('title','').strip() for c in confs]
dup_titles = list(set(t for t in titles if titles.count(t) > 1))

# Saltos de numeración Fase A
fa_nums = sorted([int(x['number']) for x in fa if x.get('number','').isdigit()])
gaps_a = [fa_nums[i]+1 for i in range(len(fa_nums)-1) if fa_nums[i+1] - fa_nums[i] > 1]

# ── Análisis Yoes ──────────────────────────────────────────────────────────
yo_ids = [y['id'] for y in yoes]
missing_yo = [i for i in EXPECTED_YO_IDS if i not in yo_ids]
YO_REQUIRED = ['id','collection','title','summary','tags','content']

yo_incomplete = []
yo_short = []
yo_status = {}

for y in yoes:
    mf = required_fields_missing(y, YO_REQUIRED)
    wc = word_count(y.get('content', []))
    status = y.get('status', 'ok')
    yo_status[y['id']] = {'words': wc, 'status': status}
    if mf:
        yo_incomplete.append({'id': y['id'], 'missing': mf})
    if wc < 400:
        yo_short.append({'id': y['id'], 'words': wc, 'title': y.get('title','')[:50]})

# ── Generar reporte ────────────────────────────────────────────────────────
lines = []
L = lines.append

L(f"# Auditoría de Contenido — Conciencia Revolucionaria")
L(f"**Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
L("")
L("---")
L("")

# Resumen ejecutivo
total_ok = len(confs) + len(yoes)
L("## Resumen ejecutivo")
L("")
L(f"| Métrica | Valor |")
L(f"|---------|-------|")
L(f"| Conferencias esperadas (A+B) | 75 (50 Fase A + 25 Fase B) |")
L(f"| Conferencias encontradas     | {len(confs)} |")
L(f"| Fase A encontradas           | {len(fa)}/50 |")
L(f"| Fase B encontradas           | {len(fb)}/25 |")
L(f"| Estudios de Yoes esperados   | {len(EXPECTED_YO_IDS)} |")
L(f"| Estudios de Yoes encontrados | {len(yoes)} |")
L(f"| IDs duplicados               | {len(duplicate_ids)} |")
L(f"| Conferencias incompletas (campos) | {len(incomplete)} |")
L(f"| Conferencias críticas (<150 palabras) | {len(very_short)} |")
L(f"| Conferencias cortas (150-300 palabras) | {len(short)} |")
L(f"| Conferencias con imágenes    | {len(with_images)} |")
L(f"| Conferencias sin imágenes    | {len(no_images)} |")
L("")
L("---")
L("")

# Fase A faltantes
L("## 1. Conferencias faltantes")
L("")
if missing_a:
    L(f"### Fase A — Faltantes ({len(missing_a)})")
    for m in missing_a:
        L(f"- `{m}`")
    L("")
    if 'fase-a-07' in missing_a:
        L("> **Nota sobre `fase-a-07`:** En el PDF original, las conferencias 05 y 06 aparecen")
        L("> unidas en un bloque doble. Se requiere crear `fase-a-07` con contenido propio")
        L("> o duplicar el bloque 05/06 para mantener la secuencia navegable 01→50.")
        L("")
else:
    L("### Fase A — Ninguna faltante ✓")
    L("")

if missing_b:
    L(f"### Fase B — Faltantes ({len(missing_b)})")
    for m in missing_b:
        L(f"- `{m}`")
    L("")
else:
    L("### Fase B — Ninguna faltante ✓")
    L("")
L("---")
L("")

# Duplicados
L("## 2. IDs y títulos duplicados")
L("")
if duplicate_ids:
    L(f"**IDs duplicados:** {duplicate_ids}")
else:
    L("**IDs duplicados:** ninguno ✓")
L("")
if dup_titles:
    L(f"**Títulos duplicados sospechosos:**")
    for t in dup_titles:
        L(f"- \"{t}\"")
else:
    L("**Títulos duplicados:** ninguno ✓")
L("")
L("---")
L("")

# Incompletas por campos
L("## 3. Conferencias con campos obligatorios faltantes")
L("")
if incomplete:
    for item in incomplete:
        L(f"- `{item['id']}` — falta: {', '.join(item['missing'])}")
else:
    L("Ninguna ✓")
L("")
L("---")
L("")

# Críticas por longitud
L("## 4. Conferencias sospechosamente cortas")
L("")
if very_short:
    L("### Críticas (< 150 palabras) — posiblemente incompletas")
    L("")
    L("| ID | Palabras | Título |")
    L("|---|---|---|")
    for item in very_short:
        L(f"| `{item['id']}` | {item['words']} | {item['title']} |")
    L("")
else:
    L("### Ninguna crítica ✓")
    L("")

if short:
    L("### Cortas (150–300 palabras) — revisar si están completas")
    L("")
    L("| ID | Palabras | Título |")
    L("|---|---|---|")
    for item in short:
        L(f"| `{item['id']}` | {item['words']} | {item['title']} |")
    L("")
L("---")
L("")

# Placeholder
L("## 5. Texto placeholder detectado")
L("")
if placeholder_c:
    for p in placeholder_c:
        L(f"- `{p}`")
else:
    L("Ninguno ✓")
L("")
L("---")
L("")

# Saltos de numeración
L("## 6. Saltos de numeración")
L("")
if gaps_a:
    L(f"**Fase A — Saltos detectados en:** {gaps_a}")
    L("")
    if 7 in gaps_a:
        L("> El salto en 07 es intencional: el PDF une las conferencias 05 y 06.")
        L("> **Acción requerida:** Crear `fase-a-07` para que la navegación sea completa.")
else:
    L("Ningún salto inesperado ✓")
L("")
L("---")
L("")

# Imágenes
L("## 7. Estado de imágenes")
L("")
L(f"- Conferencias **con** bloques de imagen: {len(with_images)}")
if with_images:
    for i in with_images: L(f"  - `{i}`")
L("")
L(f"- Conferencias **sin** imágenes ({len(no_images)} de {len(confs)}):")
L(f"  *(Ver script `_scripts/extract_pdf_images.py` para extraer imágenes de los PDFs)*")
L("")
L("---")
L("")

# Yoes
L("## 8. Auditoría Estudios de los Yoes")
L("")
L(f"| ID | Palabras | Status |")
L(f"|---|---|---|")
for y in yoes:
    d = yo_status.get(y['id'], {})
    st = d.get('status', 'ok')
    L(f"| `{y['id']}` | {d.get('words',0)} | {st} |")
L("")

if missing_yo:
    L(f"**IDs esperados faltantes:** {missing_yo}")
    L("")

if yo_incomplete:
    L("**Campos faltantes:**")
    for item in yo_incomplete:
        L(f"- `{item['id']}` — falta: {', '.join(item['missing'])}")
    L("")

if yo_short:
    L("**Yoes cortos (< 400 palabras):**")
    for item in yo_short:
        L(f"- `{item['id']}` — {item['words']} palabras — {item['title']}")
    L("")
L("---")
L("")

# Acciones
L("## 9. Acciones recomendadas")
L("")
actions = []
if missing_a:
    for m in missing_a:
        if m == 'fase-a-07':
            actions.append("**CRÍTICO:** Crear `fase-a-07` — el salto 06→08 rompe la navegación secuencial. Duplicar contenido de fase-a-06 con nota editorial o extraer desde PDF.")
        else:
            actions.append(f"**CRÍTICO:** Crear `{m}` — conferencia faltante.")
if missing_b:
    for m in missing_b:
        actions.append(f"**CRÍTICO:** Crear `{m}` — conferencia faltante.")
if very_short:
    for item in very_short:
        actions.append(f"**REVISAR:** `{item['id']}` tiene solo {item['words']} palabras. Extraer texto completo del PDF.")
if short:
    for item in short:
        actions.append(f"**REVISAR:** `{item['id']}` tiene {item['words']} palabras. Puede estar incompleta.")
if duplicate_ids:
    actions.append(f"**CORREGIR:** IDs duplicados: {duplicate_ids}")
if yo_short:
    for item in yo_short:
        actions.append(f"**COMPLETAR YO:** `{item['id']}` tiene {item['words']} palabras. Extraer de PDF fuente.")
if len(no_images) == len(confs):
    actions.append("**IMÁGENES:** Ninguna conferencia tiene imágenes. Ejecutar `_scripts/extract_pdf_images.py`.")

for i, a in enumerate(actions, 1):
    L(f"{i}. {a}")

if not actions:
    L("✓ Sin acciones críticas pendientes.")
L("")
L("---")
L("")
L(f"*Generado automáticamente por `_scripts/audit_content.py`*")

os.makedirs(os.path.dirname(OUT_F), exist_ok=True)
with open(OUT_F, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f"Reporte generado: {OUT_F}")
print(f"Conferencias: {len(confs)} | Fase A: {len(fa)}/50 | Fase B: {len(fb)}/25")
print(f"Faltantes A: {missing_a}")
print(f"Faltantes B: {missing_b}")
print(f"Críticas (<150 palabras): {[x['id']+':'+str(x['words']) for x in very_short]}")
print(f"Cortas (150-300): {[x['id']+':'+str(x['words']) for x in short]}")
