"""
scrape_with_images.py
=====================
Re-scrapea todas las conferencias de Fase A incluyendo imágenes inline,
descarga las imágenes del sitio oficial y actualiza conferencias.json
con bloques image posicionados exactamente donde aparecen en el texto.

Uso: python _scripts/scrape_with_images.py
     python _scripts/scrape_with_images.py --id fase-a-41

Requiere: pip install requests beautifulsoup4
"""

import re, json, time, argparse
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT      = Path(__file__).parent.parent
DATA      = ROOT / "data"
CONF_JSON = DATA / "conferencias.json"
IMG_DIR   = ROOT / "assets" / "conferencias" / "fase-a" / "web"
IMG_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://conocimientodesimismo.co"

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

META_RE = re.compile(
    r"^(share!?|\d{1,2}\s+de\s+\w+|\s*fin\s+conferencia|www\.|https?://)",
    re.IGNORECASE,
)

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; educational-scraper/1.0)"}


def is_caps_heading(text: str) -> bool:
    clean = re.sub(r"\s+", " ", text).strip().rstrip(":. ")
    letters = [c for c in clean if c.isalpha()]
    if not letters or len(clean) < 4:
        return False
    uppers = [c for c in letters if c.isupper()]
    return len(uppers) / len(letters) >= 0.75


def normalize_caps(text: str) -> str:
    # Elimina espacios OCR solo entre letras MAYUSCULAS SOLAS (ej: "C I ENC I A" -> "CIENCIA")
    # pero respeta espacios entre palabras reales (ej: "LA DANZA DE LOS DERVICHES")
    # Patron: espacio entre dos letras individuales (rodeadas de no-letras o inicio/fin)
    cleaned = re.sub(r"(?<!\w)([A-Z\u00C0-\u00DC])\s(?=[A-Z\u00C0-\u00DC])(?!\w\w)", r"\1", text)
    cleaned = cleaned.strip().rstrip(":. ")
    # Title case preservando acentos
    words = cleaned.split()
    result = []
    for w in words:
        if w:
            result.append(w[0].upper() + w[1:].lower())
    return " ".join(result)


def download_image(img_url: str) -> str | None:
    """Descarga la imagen y devuelve la ruta local relativa."""
    filename = img_url.split("/")[-1].split("?")[0]
    local_path = IMG_DIR / filename
    if local_path.exists():
        return "assets/conferencias/fase-a/web/" + filename
    try:
        r = requests.get(img_url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            local_path.write_bytes(r.content)
            return "assets/conferencias/fase-a/web/" + filename
    except Exception as e:
        print(f"    [!] Error descargando {img_url}: {e}")
    return None


def parse_element(el, conf_id: str) -> list[dict]:
    """
    Convierte un elemento HTML en uno o más bloques JSON.
    Maneja el caso imagen+texto inline del sitio oficial.
    """
    tag  = el.name
    blocks = []

    # ── Listas ──
    if tag in ("ul", "ol"):
        items = [li.get_text(" ", strip=True) for li in el.find_all("li")]
        items = [i for i in items if i and not META_RE.match(i)]
        if items:
            blocks.append({"type": "list", "items": items})
        return blocks

    # ── Headings HTML ──
    if tag in ("h2", "h3", "h4"):
        text = el.get_text(" ", strip=True)
        if text:
            blocks.append({"type": "heading", "level": int(tag[1]), "text": text})
        return blocks

    if tag == "h1":
        return []

    # ── Blockquote ──
    if tag == "blockquote":
        text = el.get_text(" ", strip=True)
        if text:
            blocks.append({"type": "quote", "text": text})
        return blocks

    # ── Párrafos (pueden contener imagen inline) ──
    if tag == "p":
        img_tags = el.find_all("img")
        img_tags = [i for i in img_tags if "media_files" in i.get("src", "")]

        if img_tags:
            # Extraer imagenes y capturar el texto restante como caption
            for img in img_tags:
                img.extract()
            text = el.get_text(" ", strip=True).strip()
            # Descargar y registrar cada imagen
            for img_tag in img_tags:
                raw_src = img_tag.get("src", "")
                img_url = urljoin(BASE_URL, raw_src)
                local_src = download_image(img_url)
                if local_src:
                    filename = local_src.split("/")[-1]
                    alt = img_tag.get("alt", "").strip() or filename
                    block = {
                        "type":   "image",
                        "src":    local_src,
                        "alt":    alt,
                        "caption": text if text else "",
                    }
                    blocks.append(block)
                    print(f"      ↓ {filename}" + (f" | caption: {text[:40]}" if text else ""))
        else:
            # Párrafo puro
            text = el.get_text(" ", strip=True).strip()
            if not text or META_RE.match(text):
                return []
            # Detectar subtítulo CAPS
            if is_caps_heading(text):
                title = normalize_caps(text)
                level = 3 if len(title) < 25 else 2
                blocks.append({"type": "heading", "level": level, "text": title})
                return blocks
            # Detectar cita
            starts_q = text.startswith('"') or text.startswith("\u201c")
            ends_q   = text.endswith('"') or text.endswith("\u201d")
            if starts_q and ends_q:
                blocks.append({"type": "quote", "text": text.strip('"\u201c\u201d')})
                return blocks
            blocks.append({"type": "paragraph", "text": text})

    return blocks


def scrape_conference(conf_id: str, slug: str) -> list[dict] | None:
    url  = BASE_URL + "/conferencia/" + slug + "/"
    print(f"  [{conf_id}] {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
    except Exception as e:
        print(f"    Error: {e}")
        return None
    if r.status_code != 200:
        print(f"    HTTP {r.status_code}")
        return None

    soup     = BeautifulSoup(r.text, "html.parser")
    body     = soup.find("div", class_="post-open-content-body")
    if not body:
        return None

    blocks = []
    for el in body.children:
        if not hasattr(el, "name") or not el.name:
            continue
        tag = el.name
        # Saltar el div del video/título
        if tag == "div":
            cls = " ".join(el.get("class", []))
            if "video-box" in cls:
                continue
            # Procesar contenido dentro de divs genéricos
            for sub in el.find_all(["p", "ul", "ol", "h2", "h3", "blockquote"], recursive=False):
                blocks.extend(parse_element(sub, conf_id))
            continue
        blocks.extend(parse_element(el, conf_id))

    # Filtrar bloques vacíos
    blocks = [b for b in blocks if b]
    return blocks if blocks else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", help="Procesar solo esta conferencia")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = json.load(open(CONF_JSON, encoding="utf-8"))

    ids_to_process = [args.id] if args.id else list(SLUG_MAP.keys())

    updated = 0
    errors  = 0

    for conf_id in ids_to_process:
        slug = SLUG_MAP.get(conf_id)
        if not slug:
            continue

        blocks = scrape_conference(conf_id, slug)
        if not blocks:
            errors += 1
            continue

        img_count = sum(1 for b in blocks if b.get("type") == "image")
        print(f"    -> {len(blocks)} bloques, {img_count} imagenes")

        if not args.dry_run:
            for conf in data:
                if conf["id"] == conf_id:
                    conf["content"] = blocks
                    updated += 1
                    break

        time.sleep(0.7)

    if not args.dry_run and updated > 0:
        json.dump(data, open(CONF_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"\nGuardado. Actualizadas: {updated} | Errores: {errors}")
    else:
        print(f"\nDry-run. Procesadas: {len(ids_to_process)}")


if __name__ == "__main__":
    main()
