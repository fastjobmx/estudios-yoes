"""
map_images.py
=============
1. Lee el PDF de Fase A y detecta en qué página empieza cada conferencia.
2. Asigna pageStart / pageEnd a cada conferencia en conferencias.json.
3. Inserta bloques `image` en el content[] de cada conferencia
   para las imágenes que caen dentro de su rango de páginas.
4. Actualiza images-manifest.json con relatedLectureIds y caption vacío.

Requiere: PyMuPDF  →  pip install pymupdf
"""

import re, json
from pathlib import Path
import fitz  # PyMuPDF

ROOT   = Path(__file__).parent.parent
DATA   = ROOT / "data"
ASSETS = ROOT / "assets" / "conferencias"

PDF_A = ROOT / "assets" / "Conferencias Fase A.pdf"
PDF_B = ROOT / "assets" / "FASE B 2010.pdf"

CONF_JSON     = DATA / "conferencias.json"
MANIFEST_JSON = DATA / "images-manifest.json"

# ── Patrones que marcan el inicio de una conferencia ──
# Fase A: "Conf. 01 EL CONOCIMIENTO"
CONF_A_RE = re.compile(
    r'conf\.?\s+(\d{1,2})\s+[A-Z\u00c1\u00c9\u00cd\u00d3\u00da\u00d1]',
    re.IGNORECASE
)
# Fase B: "Conferencia Nro. 1 - Fase "B""
CONF_B_RE = re.compile(
    r'conferencia\s+nro\.?\s*(\d{1,2})\s*[-\u2013]\s*fase',
    re.IGNORECASE
)

def extract_page_map(pdf_path, phase_letter):
    """Devuelve dict: conf_number -> (page_start, page_end) (1-indexed)."""
    doc = fitz.open(str(pdf_path))
    num_pages = len(doc)
    
    pattern = CONF_A_RE if phase_letter.upper() == "A" else CONF_B_RE
    page_to_conf = {}  # page_num (1-indexed) -> conf_number
    
    for page_idx in range(num_pages):
        page = doc[page_idx]
        text = page.get_text("text")
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        for line in lines[:10]:  # primeras 10 líneas
            m = pattern.search(line)
            if m:
                num = int(m.group(1))
                if 1 <= num <= 75:
                    # Solo registrar si es la primera vez que aparece este número
                    if num not in [v for v in page_to_conf.values()]:
                        page_to_conf[page_idx + 1] = num
                    break
    
    doc.close()
    
    # Construir rangos: conf_number -> (start_page, end_page)
    if not page_to_conf:
        print(f"  [!] No se detectaron conferencias en {pdf_path.name}")
        return {}
    
    sorted_pages = sorted(page_to_conf.items())  # [(page, conf_num), ...]
    ranges = {}
    
    for i, (page, conf_num) in enumerate(sorted_pages):
        if i + 1 < len(sorted_pages):
            end_page = sorted_pages[i + 1][0] - 1
        else:
            end_page = num_pages
        ranges[conf_num] = (page, end_page)
    
    return ranges

def assign_pages_and_images():
    data     = json.load(open(CONF_JSON, encoding="utf-8"))
    manifest = json.load(open(MANIFEST_JSON, encoding="utf-8"))
    
    # ── Paso 1: mapear páginas por fase ──
    print("Analizando PDF Fase A...")
    ranges_a = extract_page_map(PDF_A, "A")
    print(f"  {len(ranges_a)} conferencias detectadas en Fase A")
    for num, (s, e) in sorted(ranges_a.items()):
        print(f"    Conf {num:02d}: páginas {s}–{e}")
    
    print()
    print("Analizando PDF Fase B...")
    ranges_b = extract_page_map(PDF_B, "B")
    print(f"  {len(ranges_b)} conferencias detectadas en Fase B")
    for num, (s, e) in sorted(ranges_b.items()):
        print(f"    Conf {num:02d}: páginas {s}–{e}")
    
    # ── Paso 2: asignar pageStart / pageEnd a cada conferencia ──
    updated_confs = 0
    for conf in data:
        if conf.get("collection") == "yoes":
            continue
        
        phase  = conf.get("phase", "").upper()
        num    = conf.get("number")
        if not num:
            continue
        num_int = int(num)
        ranges = ranges_a if phase == "A" else ranges_b
        
        if num_int in ranges:
            ps, pe = ranges[num_int]
            conf["pageStart"] = ps
            conf["pageEnd"]   = pe
            updated_confs += 1
    
    print(f"\n  pageStart/End asignados a {updated_confs} conferencias")
    
    # ── Paso 3: construir índice imagen → conferencia ──
    # Mapa: src -> item del manifest
    img_by_src = {img["src"]: img for img in manifest if img.get("src")}
    
    # Agrupar imágenes del manifest por (phase, page)
    # Nombre: fase-a-p005-img01.jpeg → phase=A, page=5
    IMG_NAME_RE = re.compile(r'fase-([ab])-p(\d+)-img(\d+)')
    
    img_by_phase_page = {}  # (phase_upper, page_int) -> [img_item, ...]
    for img in manifest:
        src = img.get("src", "")
        m   = IMG_NAME_RE.search(Path(src).name)
        if m:
            ph = m.group(1).upper()
            pg = int(m.group(2))
            key = (ph, pg)
            img_by_phase_page.setdefault(key, []).append(img)
    
    # ── Paso 4: insertar bloques image en el content[] de cada conferencia ──
    images_placed = 0
    for conf in data:
        if conf.get("collection") == "yoes":
            continue
        
        phase = conf.get("phase", "").upper()
        ps    = conf.get("pageStart")
        pe    = conf.get("pageEnd")
        
        if not ps or not pe:
            continue
        
        # Recolectar imágenes que caen en el rango de páginas
        imgs_for_conf = []
        for pg in range(ps, pe + 1):
            key = (phase, pg)
            if key in img_by_phase_page:
                for img in img_by_phase_page[key]:
                    imgs_for_conf.append(img)
        
        if not imgs_for_conf:
            continue
        
        # Marcar en el manifest
        for img in imgs_for_conf:
            img["relatedLectureIds"] = [conf["id"]]
            img["needsManualPlacement"] = False
        
        # Insertar bloques image al final del content (antes del último párrafo si existe)
        existing_content = conf.get("content", [])
        
        # Evitar duplicados: si ya hay bloques image, no agregar de nuevo
        existing_srcs = {b.get("src") for b in existing_content if b.get("type") == "image"}
        
        new_image_blocks = []
        for img in imgs_for_conf:
            if img["src"] not in existing_srcs:
                new_image_blocks.append({
                    "type":    "image",
                    "src":     img["src"],
                    "alt":     img.get("alt", "Imagen de la conferencia"),
                    "caption": img.get("caption", "")
                })
        
        if new_image_blocks:
            # Insertar antes del último párrafo para no romper el cierre
            if existing_content and existing_content[-1].get("type") == "paragraph":
                insert_at = len(existing_content) - 1
                conf["content"] = (
                    existing_content[:insert_at] +
                    new_image_blocks +
                    [existing_content[-1]]
                )
            else:
                conf["content"] = existing_content + new_image_blocks
            
            images_placed += len(new_image_blocks)
            print(f"  {conf['id']}: {len(new_image_blocks)} imagen(es) insertada(s)")
    
    print(f"\nTotal imágenes insertadas: {images_placed}")
    
    # ── Guardar ──
    json.dump(data,     open(CONF_JSON,     "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(manifest, open(MANIFEST_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("\narchivos guardados.")

if __name__ == "__main__":
    assign_pages_and_images()
