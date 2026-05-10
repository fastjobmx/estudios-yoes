"""
extract_pdf_images.py
Extrae imágenes de los PDFs de conferencias usando PyMuPDF.
Guarda en assets/conferencias/fase-a/ y assets/conferencias/fase-b/
Genera data/images-manifest.json
"""
import fitz  # PyMuPDF
import os, json, hashlib
from pathlib import Path

ROOT     = Path(__file__).parent.parent
ASSETS_A = ROOT / 'assets' / 'conferencias' / 'fase-a'
ASSETS_B = ROOT / 'assets' / 'conferencias' / 'fase-b'
MANIFEST = ROOT / 'data' / 'images-manifest.json'

ASSETS_A.mkdir(parents=True, exist_ok=True)
ASSETS_B.mkdir(parents=True, exist_ok=True)

PDFS = [
    {
        'path': ROOT / 'assets' / 'Conferencias Fase A.pdf',
        'phase': 'A',
        'prefix': 'fase-a',
        'out_dir': ASSETS_A,
    },
    {
        'path': ROOT / 'assets' / 'FASE B 2010.pdf',
        'phase': 'B',
        'prefix': 'fase-b',
        'out_dir': ASSETS_B,
    },
]

# Tamaño mínimo: ignorar imágenes de <4KB (logos, decoraciones, ruido OCR)
MIN_SIZE_BYTES = 4000
# Dimensiones mínimas en píxeles
MIN_W, MIN_H = 80, 80

manifest = []
seen_hashes = set()
total_extracted = 0
total_skipped   = 0

for pdf_info in PDFS:
    pdf_path = pdf_info['path']
    if not pdf_path.exists():
        print(f"[SKIP] No encontrado: {pdf_path}")
        continue

    print(f"\nProcesando: {pdf_path.name}")
    doc = fitz.open(str(pdf_path))
    phase   = pdf_info['phase']
    prefix  = pdf_info['prefix']
    out_dir = pdf_info['out_dir']

    img_counter_per_page = {}

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_label = page_num + 1  # 1-based

        image_list = page.get_images(full=True)
        if not image_list:
            continue

        img_idx_on_page = 0

        for img_info in image_list:
            xref = img_info[0]
            try:
                base_image = doc.extract_image(xref)
            except Exception:
                continue

            img_bytes  = base_image['image']
            img_ext    = base_image['ext']          # jpeg, png, etc.
            img_width  = base_image['width']
            img_height = base_image['height']

            # Filtros de calidad
            if len(img_bytes) < MIN_SIZE_BYTES:
                total_skipped += 1
                continue
            if img_width < MIN_W or img_height < MIN_H:
                total_skipped += 1
                continue

            # Evitar duplicados por hash
            img_hash = hashlib.md5(img_bytes).hexdigest()
            if img_hash in seen_hashes:
                total_skipped += 1
                continue
            seen_hashes.add(img_hash)

            img_idx_on_page += 1
            filename = f"{prefix}-p{page_label:03d}-img{img_idx_on_page:02d}.{img_ext}"
            out_path = out_dir / filename

            with open(out_path, 'wb') as f:
                f.write(img_bytes)

            # Intentar convertir a PNG si es un formato raro
            rel_src = f"assets/conferencias/{prefix}/{filename}"
            img_id  = filename.rsplit('.', 1)[0]

            entry = {
                "id":                  img_id,
                "phase":               phase,
                "page":                page_label,
                "src":                 rel_src,
                "width":               img_width,
                "height":              img_height,
                "sizeKB":              round(len(img_bytes) / 1024, 1),
                "alt":                 f"Imagen de la conferencia Fase {phase}, página {page_label}",
                "caption":             "",
                "relatedLectureIds":   [],
                "needsManualPlacement": True
            }
            manifest.append(entry)
            total_extracted += 1

            print(f"  [{phase} p.{page_label}] {filename} ({img_width}x{img_height}, {round(len(img_bytes)/1024,1)}KB)")

    doc.close()

# Guardar manifiesto
with open(MANIFEST, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print(f"\n{'='*50}")
print(f"Imágenes extraídas: {total_extracted}")
print(f"Imágenes omitidas (pequeñas/duplicadas): {total_skipped}")
print(f"Manifiesto guardado: {MANIFEST}")
