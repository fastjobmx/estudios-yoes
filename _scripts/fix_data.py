"""
fix_data.py — Correcciones de datos V1.1
1. Crea fase-a-07 (alias de fase-a-06, misma conferencia doble del PDF)
2. Extrae texto completo de conferencias críticas (<150 palabras) desde PDF
3. Extrae contenido de los PDFs de Yoes y actualiza yoes.json
4. Agrega campos adicionales (collection, sourcePdf, pageStart, pageEnd, related, images)
"""
import fitz, json, os, re
from pathlib import Path

ROOT   = Path(__file__).parent.parent
CONF_F = ROOT / 'data' / 'conferencias.json'
YOES_F = ROOT / 'data' / 'yoes.json'
PDF_A  = ROOT / 'assets' / 'Conferencias Fase A.pdf'
PDF_B  = ROOT / 'assets' / 'FASE B 2010.pdf'

# ── Helpers ────────────────────────────────────────────────────────────────
def clean_text(t):
    t = re.sub(r'\s+', ' ', t).strip()
    t = re.sub(r'[^\S\n]+', ' ', t)
    return t

def word_count(content):
    total = 0
    for b in (content or []):
        txt = b.get('text','') or ' '.join(b.get('items', b.get('steps', [])))
        total += len(txt.split())
    return total

def extract_page_range_text(pdf_path, start_page, end_page):
    """Extrae texto de páginas start_page..end_page (1-based inclusive)."""
    doc = fitz.open(str(pdf_path))
    blocks = []
    for p in range(start_page - 1, min(end_page, len(doc))):
        page = doc[p]
        text = page.get_text("text")
        for line in text.split('\n'):
            line = clean_text(line)
            if len(line) > 20:
                blocks.append(line)
    doc.close()
    return blocks

def lines_to_content(lines):
    """Convierte líneas de texto a bloques JSON estructurados."""
    content = []
    for line in lines:
        if len(line) < 5:
            continue
        # Detectar headings: líneas cortas, en mayúsculas o con patrón de título
        if line.isupper() and len(line) < 100:
            content.append({"type": "heading", "level": 2, "text": line.title()})
        elif re.match(r'^[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{5,60}$', line):
            content.append({"type": "heading", "level": 3, "text": line.title()})
        else:
            # Párrafo normal
            if content and content[-1]['type'] == 'paragraph':
                # Unir con el párrafo anterior si no termina en punto
                prev = content[-1]['text']
                if prev and not prev[-1] in '.!?:':
                    content[-1]['text'] = prev + ' ' + line
                    continue
            content.append({"type": "paragraph", "text": line})
    return content

def extract_yo_from_pdf(pdf_path):
    """Extrae contenido completo de un PDF de Yo."""
    doc = fitz.open(str(pdf_path))
    all_lines = []
    for page in doc:
        text = page.get_text("text")
        for line in text.split('\n'):
            line = clean_text(line)
            if len(line) > 15:
                all_lines.append(line)
    doc.close()
    return lines_to_content(all_lines)

# ── Cargar JSONs ───────────────────────────────────────────────────────────
with open(CONF_F, encoding='utf-8') as f:
    confs = json.load(f)
with open(YOES_F, encoding='utf-8') as f:
    yoes = json.load(f)

conf_by_id = {c['id']: c for c in confs}

# ── 1. Crear fase-a-07 ─────────────────────────────────────────────────────
if 'fase-a-07' not in conf_by_id:
    a06 = conf_by_id.get('fase-a-06')
    if a06:
        a07 = {
            "id":       "fase-a-07",
            "phase":    "A",
            "number":   "07",
            "title":    "Las dimensiones y dónde están en nosotros (parte III)",
            "page":     a06.get('page', ''),
            "summary":  "Continuación del estudio sobre las dimensiones del cosmos y su ubicación en el ser humano. "
                        "Complemento directo de las conferencias 05 y 06, que en el PDF original conforman un bloque doble.",
            "tags":     a06.get('tags', []),
            "content":  [
                {
                    "type": "heading",
                    "level": 2,
                    "text": "Nota editorial"
                },
                {
                    "type": "paragraph",
                    "text": "En el documento fuente original, las conferencias 05, 06 y 07 aparecen unidas como un "
                            "bloque doble titulado \"Conf. 05 y 06 — Las dimensiones y dónde están en nosotros\". "
                            "Este ID ha sido creado para mantener la secuencia de navegación completa del 01 al 50. "
                            "El contenido íntegro de esta conferencia se encuentra en fase-a-05 y fase-a-06."
                }
            ],
            "note": "Conferencia complementaria. El PDF fuente une 05 y 06 en un solo bloque. "
                    "Este ID mantiene la secuencia navegable.",
            "sourcePdf": "Conferencias Fase A.pdf",
            "collection": "conferencias"
        }
        # Insertar después de fase-a-06
        idx_a06 = next(i for i,c in enumerate(confs) if c['id'] == 'fase-a-06')
        confs.insert(idx_a06 + 1, a07)
        conf_by_id['fase-a-07'] = a07
        print("✓ Creado: fase-a-07")
    else:
        print("✗ No se encontró fase-a-06 para basar fase-a-07")
else:
    print("→ fase-a-07 ya existe")

# ── 2. Agregar campo collection a conferencias ─────────────────────────────
for c in confs:
    if 'collection' not in c:
        c['collection'] = 'conferencias'

# ── 3. Extraer texto de conferencias críticas desde PDF ────────────────────
# Mapeo manual de ID → páginas en el PDF (verificado por numeración del PDF)
PAGE_MAP_A = {
    'fase-a-03': (14, 17),   # El desdoblamiento astral — 301 palabras, extraer más
    'fase-a-06': (27, 30),   # Continuación dimensiones — 312 palabras
    'fase-a-37': (145, 148), # Práctica desdoblamiento — 115 palabras CRÍTICO
    'fase-a-48': (186, 189), # Pronunciación mantrams — 131 palabras CRÍTICO
}
PAGE_MAP_B = {
    'fase-b-02': (8, 11),    # 158 palabras
    'fase-b-03': (12, 15),   # 130 palabras CRÍTICO
}

def enrich_from_pdf(conf_id, pdf_path, start_p, end_p):
    c = conf_by_id.get(conf_id)
    if not c:
        print(f"  ✗ No encontrado: {conf_id}")
        return
    current_wc = word_count(c.get('content', []))
    lines = extract_page_range_text(pdf_path, start_p, end_p)
    if not lines:
        print(f"  ✗ Sin texto extraído para {conf_id} (pp.{start_p}-{end_p})")
        return
    new_content = lines_to_content(lines)
    new_wc = word_count(new_content)
    if new_wc > current_wc:
        # Conservar el content existente si tiene headings estructurados
        has_headings = any(b.get('type') == 'heading' for b in c.get('content', []))
        if has_headings and current_wc > 100:
            # Adjuntar nuevo contenido al final en lugar de reemplazar
            c['content'] = c['content'] + [{"type":"heading","level":2,"text":"Contenido extraído del PDF"}] + new_content
        else:
            c['content'] = new_content
        c['sourcePdf'] = pdf_path.name
        c['pageStart'] = start_p
        c['pageEnd']   = end_p
        print(f"  ✓ {conf_id}: {current_wc} → {word_count(c['content'])} palabras")
    else:
        print(f"  → {conf_id}: extracción no mejoró ({current_wc} → {new_wc} palabras), conservando original")

print("\nExtrayendo conferencias críticas desde PDFs...")
for cid, (s, e) in PAGE_MAP_A.items():
    enrich_from_pdf(cid, PDF_A, s, e)
for cid, (s, e) in PAGE_MAP_B.items():
    enrich_from_pdf(cid, PDF_B, s, e)

# ── 4. Agregar campos sourcePdf y pageStart/pageEnd a los que faltan ──────
for c in confs:
    if 'sourcePdf' not in c:
        if c.get('phase') == 'A':
            c['sourcePdf'] = 'Conferencias Fase A.pdf'
        elif c.get('phase') == 'B':
            c['sourcePdf'] = 'FASE B 2010.pdf'
    if 'related' not in c:
        c['related'] = []
    if 'images' not in c:
        c['images'] = []

# ── 5. Extraer contenido de PDFs de Yoes ──────────────────────────────────
YO_PDF_MAP = {
    'yo-abatimiento':      ROOT / 'assets' / 'YO_DEPRESION_abatimiento_perdida_duelo.pdf',
    'yo-conquistador':     ROOT / 'assets' / 'Yo_Conquistador.pdf',
    'yo-machista':         ROOT / 'assets' / 'Yo_machista_trabajo_interior.pdf',
    'yo-miedo':            ROOT / 'assets' / 'elmiedo.pdf',
    'yo-relacion-toxica':  ROOT / 'assets' / 'estudio_relacion_toxica.pdf',
    'yo-meditacion-500':   ROOT / 'assets' / 'PREGUNTAS MEDITACIÓN 500 (1).pdf',
}

print("\nExtrayendo contenido de PDFs de Yoes...")
yo_by_id = {y['id']: y for y in yoes}

for yo_id, pdf_path in YO_PDF_MAP.items():
    yo = yo_by_id.get(yo_id)
    if not yo:
        print(f"  ✗ Yo no encontrado en JSON: {yo_id}")
        continue
    if not pdf_path.exists():
        print(f"  ✗ PDF no encontrado: {pdf_path.name}")
        yo['status'] = 'incompleto'
        yo['missingSource'] = True
        continue

    current_wc = word_count(yo.get('content', []))
    new_content = extract_yo_from_pdf(pdf_path)
    new_wc = word_count(new_content)

    print(f"  {yo_id}: {current_wc} → {new_wc} palabras (desde {pdf_path.name})")

    if new_wc > current_wc:
        yo['content'] = new_content
        yo['status']  = 'completo'
        yo['source']  = pdf_path.name
        yo['missingSource'] = False
    else:
        yo['status'] = 'incompleto' if new_wc < 200 else 'completo'
        yo['source'] = pdf_path.name

    # Campos adicionales
    if 'related' not in yo:
        yo['related'] = []
    if 'subtitle' not in yo:
        yo['subtitle'] = ''

# ── 6. Guardar JSONs ───────────────────────────────────────────────────────
with open(CONF_F, 'w', encoding='utf-8') as f:
    json.dump(confs, f, ensure_ascii=False, indent=2)
print(f"\n✓ Guardado: {CONF_F} ({len(confs)} conferencias)")

with open(YOES_F, 'w', encoding='utf-8') as f:
    json.dump(yoes, f, ensure_ascii=False, indent=2)
print(f"✓ Guardado: {YOES_F} ({len(yoes)} yoes)")

# ── Resumen ────────────────────────────────────────────────────────────────
fa = [c for c in confs if c.get('phase') == 'A']
fb = [c for c in confs if c.get('phase') == 'B']
print(f"\nResumen final:")
print(f"  Conferencias: {len(confs)} | Fase A: {len(fa)}/50 | Fase B: {len(fb)}/25")
print(f"  Yoes: {len(yoes)}")
print(f"  fase-a-07 presente: {'fase-a-07' in [c['id'] for c in confs]}")
