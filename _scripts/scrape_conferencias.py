"""
scrape_conferencias.py
======================
Extrae el texto limpio de cada conferencia del sitio oficial
https://conocimientodesimismo.co y lo estructura en bloques JSON.

Uso: python _scripts/scrape_conferencias.py
     python _scripts/scrape_conferencias.py --id fase-a-01   (solo una)
     python _scripts/scrape_conferencias.py --fase A          (solo Fase A)
     python _scripts/scrape_conferencias.py --dry-run         (muestra sin guardar)

Requiere: pip install requests beautifulsoup4
"""

import re, json, time, argparse
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Instala dependencias: pip install requests beautifulsoup4")
    raise

ROOT      = Path(__file__).parent.parent
DATA      = ROOT / "data"
CONF_JSON = DATA / "conferencias.json"

BASE_URL  = "https://conocimientodesimismo.co/conferencia/"

# Mapa: id JSON → slug del sitio oficial
SLUG_MAP = {
    "fase-a-01": "conocimiento-de-si-mismo-y-objetivos",
    "fase-a-02": "que-es-la-muerte-lo-que-muere-y-lo-que-no-muere",
    "fase-a-03": "el-desdoblamiento-astral",
    "fase-a-04": "los-siete-centros-de-la-maquina-humana",
    "fase-a-05": "conferencia-5-y-6-las-dimensiones-y-donde-estan-en",
    "fase-a-06": "conferencia-5-y-6-las-dimensiones-y-donde-estan-en",
    "fase-a-07": "conferencia-7-las-conjuraciones-belilin-circulo-ma",
    "fase-a-08": "conferencia-8-evolucion-involucion-revolucion",
    "fase-a-09": "conferencia-9-las-infradimensiones",
    "fase-a-10": "conferencia-10-los-siete-cuerpos",
    "fase-a-11": "conferencia-11-como-se-fabrica-alma-y-espiritu",
    "fase-a-12": "conferencia-12-retorno-y-recurrencia",
    "fase-a-13": "conferencia-13-leyes-de-karma-y-dharma",
    "fase-a-14": "conferencia-14-drogas-y-alcoholismo",
    "fase-a-15": "conferencia-15-ego-personalidad-y-esencia",
    "fase-a-16": "conferencia-16-la-observacion-de-si-mismo",
    "fase-a-17": "conferencia-17-los-tres-factores-de-la-revolucion-",
    "fase-a-18": "conferencia-18-la-charla-interior-y-la-cancion-psi",
    "fase-a-19": "conferencia-19-estados-y-eventos",
    "fase-a-20": "conferencia-20-el-pais-psicologico",
    "fase-a-21": "conferencia-21-concentracion-y-relajacion",
    "fase-a-22": "conferencia-22-la-meditacion",
    "fase-a-23": "conferencia-23-fanatismo-y-mitomania",
    "fase-a-24": "conferencia-24-la-vida-y-el-nivel-del-ser",
    "fase-a-25": "conferencia-25-exoterismo-pseudo-esoterismo-y-esot",
    "fase-a-26": "el-mundo-de-las-relaciones",
    "fase-a-27": "conferencia-27-tecnica-para-disolver-el-yo-los-det",
    "fase-a-28": "conferencia-28-el-cristo-universal-e-individual",
    "fase-a-29": "conferencia-29-la-ley-del-pendulo",
    "fase-a-30": "conferencia-30-metodo-para-despertar-la-conciencia",
    "fase-a-31": "conferencia-31-criaturas-mecanicas",
    "fase-a-32": "conferencia-32-el-cambio-radical",
    "fase-a-33": "conferencia-33-ley-de-octavas-y-ley-de-entropia",
    "fase-a-34": "conferencia-34-el-centro-de-gravedad-permanente",
    "fase-a-35": "conferencia-35-explicaciones-sobre-la-familia-y-lo",
    "fase-a-36": "conferencia-36-meditacion-y-koanes",
    "fase-a-37": "conferencia-37",
    "fase-a-38": "conferencia-38-el-dificil-camino-y-el-trabajo-cris",
    "fase-a-39": "conferencia-39-la-no-identificacion-con-las-cosas-",
    "fase-a-40": "conferencia-40-el-sacrificio-por-la-humanidad",
    "fase-a-41": "conferencia-41-la-danza-de-los-derviches-y-la-tran",
    "fase-a-42": "conferencia-42-dos-clases-de-conocimiento-objetivo",
    "fase-a-43": "conferencia-43-diversos-tipos-de-yoes-lujuriosos",
    "fase-a-44": "conferencia-44-el-yo-de-la-traicion",
    "fase-a-45": "conferencia-45-que-debemos-hacer-para-que-las-prac",
    "fase-a-46": "conferencia-46-como-controlar-poluciones-nocturnas",
    "fase-a-47": "conferencia-47-el-yo-de-la-brujeria",
    "fase-a-48": "conferencia-48-pronunciacion-de-mantrams-para-el-d",
    "fase-a-49": "conferencia-49-la-dualidad",
    "fase-a-50": "conferencia-50-el-origen-del-ego",
}

# ── Detección de subtítulos en CAPS ──
# Ejemplos: "TODOS ESTAMOS CONSTITUIDOS POR TRES PARTES:"
#           "CIENCIA:", "ARTE:", "MÍSTICA:", "OBJETIVOS DEL CONOCIMIENTO..."
CAPS_TITLE_RE = re.compile(r'^([A-ZÁÉÍÓÚÑÜ\s\-–]{4,}[\.:])$')

# Patrones de metadata a eliminar
META_RE = re.compile(
    r'^(share!?|conferencia\s+\d+\s+de\s+fase|fin\s+conferencia|www\.|https?://)',
    re.IGNORECASE
)


def fetch_page(url: str) -> BeautifulSoup | None:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; educational-scraper/1.0)"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            return BeautifulSoup(r.text, "html.parser")
        print(f"  HTTP {r.status_code}: {url}")
        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None


def is_caps_heading(text: str) -> bool:
    """Detecta si un texto es un subtítulo en mayúsculas del documento original."""
    clean = text.strip()
    if not clean or len(clean) < 3 or len(clean) > 100:
        return False
    # Quitar espacios OCR internos y signos al final
    normalized = re.sub(r'\s+', ' ', clean).rstrip(':. ')
    # Debe tener al menos 60% de letras mayúsculas (ignora números y tildes)
    letters = [c for c in normalized if c.isalpha()]
    if not letters:
        return False
    uppers = [c for c in letters if c.isupper()]
    ratio  = len(uppers) / len(letters)
    return ratio >= 0.75 and len(normalized) >= 4


def normalize_caps_title(text: str) -> str:
    """Convierte 'C I ENC I A' -> 'Ciencia', elimina espacios OCR en CAPS."""
    # Quitar espacios extra dentro de palabras: 'C I ENC I A' -> 'CIENCIA'
    cleaned = re.sub(r'(?<=[A-Z\u00c0-\u00dc])\s(?=[A-Z\u00c0-\u00dc])', '', text)
    cleaned = cleaned.strip().rstrip(':. ')
    # Title case
    return cleaned.title()


def parse_content(soup: BeautifulSoup) -> list[dict]:
    """
    Extrae los bloques de contenido del HTML de una página de conferencia.
    Usa el contenedor real del sitio conocimientodesimismo.co
    """
    # Contenedor real del sitio
    content_el = (
        soup.find("div", class_="post-open-content-body") or
        soup.find("div", class_="entry-content") or
        soup.find("div", class_="post-content")
    )
    if not content_el:
        return []

    blocks = []

    for el in content_el.children:
        if not hasattr(el, 'name') or not el.name:
            continue

        tag  = el.name
        text = el.get_text(" ", strip=True)

        # Saltar el div del video/título al inicio
        if tag == "div":
            cls = el.get("class", [])
            if "video-box" in cls or "video" in " ".join(cls):
                continue
            # Procesar divs genéricos recursivamente
            for sub in el.find_all(["p", "ul", "ol", "blockquote", "h2", "h3"]):
                sub_text = sub.get_text(" ", strip=True)
                if sub_text:
                    blocks.append({"type": "paragraph", "text": sub_text})
            continue

        if not text:
            continue
        if META_RE.match(text):
            continue

        # ── Headings HTML explícitos ──
        if tag in ("h2", "h3", "h4"):
            blocks.append({"type": "heading", "level": int(tag[1]), "text": text})
            continue

        # H1 = título de página, omitir
        if tag == "h1":
            continue

        # ── Listas ──
        if tag in ("ul", "ol"):
            items = [li.get_text(" ", strip=True) for li in el.find_all("li")]
            items = [i for i in items if i and not META_RE.match(i)]
            if items:
                blocks.append({"type": "list", "items": items})
            continue

        # ── Blockquote ──
        if tag == "blockquote":
            blocks.append({"type": "quote", "text": text})
            continue

        # ── Párrafos ──
        if tag == "p":
            clean = text.strip()
            if not clean:
                continue

            # Detectar subtítulo en CAPS
            if is_caps_heading(clean):
                title = normalize_caps_title(clean)
                level = 3 if len(title) < 25 else 2
                blocks.append({"type": "heading", "level": level, "text": title})
                continue

            # Detectar cita: empieza y termina con comillas tipográficas
            starts_quote = clean.startswith('"') or clean.startswith('\u201c')
            ends_quote   = clean.endswith('"') or clean.endswith('\u201d')
            if starts_quote and ends_quote:
                blocks.append({"type": "quote", "text": clean.strip('"' + '\u201c' + '\u201d')})
                continue

            blocks.append({"type": "paragraph", "text": clean})

    return blocks


def clean_blocks(blocks: list[dict]) -> list[dict]:
    """
    Post-proceso: elimina duplicados consecutivos, bloques vacíos,
    y junta párrafos de una sola línea muy corta con el siguiente.
    """
    out = []
    for b in blocks:
        if not b:
            continue
        t = b.get("type")
        # Skip listas vacías
        if t == "list" and not b.get("items"):
            continue
        # Skip párrafos vacíos o de metadata
        if t == "paragraph":
            txt = b.get("text", "").strip()
            if not txt or META_RE.match(txt):
                continue
            b["text"] = txt
        out.append(b)
    return out


def scrape_conference(conf_id: str, slug: str, dry_run: bool = False) -> list[dict] | None:
    if slug is None:
        print(f"  [{conf_id}] Sin slug (nota editorial) — omitido")
        return None

    url  = BASE_URL + slug + "/"
    print(f"  [{conf_id}] {url}")

    soup = fetch_page(url)
    if not soup:
        return None

    blocks = parse_content(soup)
    blocks = clean_blocks(blocks)

    if dry_run:
        print(f"    → {len(blocks)} bloques")
        for b in blocks[:6]:
            t = b.get("type")
            if t == "heading":
                print(f"      H{b['level']}: {b['text'][:60]}")
            elif t == "paragraph":
                print(f"      P: {b['text'][:65]}...")
            elif t == "list":
                print(f"      LIST ({len(b['items'])} items): {b['items'][0][:45]}")
            elif t == "quote":
                print(f"      QUOTE: {b['text'][:60]}")
        if len(blocks) > 6:
            print(f"      ... ({len(blocks) - 6} más)")

    return blocks if blocks else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id",      help="Procesar solo esta conferencia (ej: fase-a-01)")
    parser.add_argument("--fase",    help="Procesar solo esta fase (A o B)")
    parser.add_argument("--dry-run", action="store_true", help="No guardar, solo mostrar")
    args = parser.parse_args()

    data = json.load(open(CONF_JSON, encoding="utf-8"))

    # Filtrar qué IDs procesar
    ids_to_process = list(SLUG_MAP.keys())
    if args.id:
        ids_to_process = [args.id]
    elif args.fase:
        ids_to_process = [k for k in SLUG_MAP if f"fase-{args.fase.lower()}" in k]

    updated = 0
    skipped = 0
    errors  = 0

    for conf_id in ids_to_process:
        slug = SLUG_MAP.get(conf_id)
        if slug is None and conf_id != "fase-a-07":
            print(f"  [{conf_id}] Sin slug mapeado — omitido")
            skipped += 1
            continue

        blocks = scrape_conference(conf_id, slug, dry_run=args.dry_run)

        if blocks is None:
            errors += 1
            continue

        if not args.dry_run:
            # Buscar la conferencia en el JSON y actualizar su content
            for conf in data:
                if conf["id"] == conf_id:
                    # Preservar bloques image que ya estaban
                    existing_images = [b for b in conf.get("content", []) if b.get("type") == "image"]
                    # Insertar imágenes antes del último párrafo
                    if existing_images:
                        if blocks and blocks[-1].get("type") == "paragraph":
                            blocks = blocks[:-1] + existing_images + [blocks[-1]]
                        else:
                            blocks = blocks + existing_images
                    conf["content"] = blocks
                    updated += 1
                    print(f"    ✓ {conf_id}: {len(blocks)} bloques guardados")
                    break

        time.sleep(0.8)  # respetar el servidor

    if not args.dry_run and updated > 0:
        json.dump(data, open(CONF_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"\nGuardado. Actualizadas: {updated} | Errores: {errors} | Omitidas: {skipped}")
    else:
        print(f"\nDry-run. Procesadas: {len(ids_to_process)} | Errores: {errors}")


if __name__ == "__main__":
    main()
