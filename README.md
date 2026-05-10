# Conciencia Revolucionaria — Sitio Web

Sitio multi-página estático de la escuela de Auto-Conocimiento Conciencia Revolucionaria.

---

## Estructura de archivos

```
ESTUDIOS YOES/
├── index.html              ← Landing cinematográfica (hero, pilares, método, yoes, CTA)
├── conferencias.html       ← Catálogo con buscador, filtros, vista grid/lista
├── conferencia.html        ← Lector individual (?id=fase-a-01)
├── cr-styles.css           ← Sistema de diseño compartido
├── tailwind-config.js      ← Configuración Tailwind unificada (cargar ANTES del CDN)
├── app.js                  ← Helpers compartidos (referencia, no importado directamente)
├── generate_json.py        ← Regenera data/conferencias.json desde los PDFs
├── README.md               ← Este archivo
│
├── data/
│   ├── conferencias.json   ← 75 conferencias (Fase A: 50, Fase B: 25)
│   └── yoes.json           ← 6 Estudios de los Yoes
│
├── assets/
│   ├── logo.png            ← Logo (también usado como favicon)
│   ├── logo1.svg           ← Logo alternativo SVG
│   ├── og-image.svg        ← Imagen Open Graph para redes sociales
│   ├── Conferencias Fase A.pdf
│   ├── FASE B 2010.pdf
│   └── [PDFs de Yoes]      ← Fuente de los estudios de los Yoes
│
└── _deprecated/            ← Archivos del sistema anterior (NO usar)
    ├── build_html.py       ← PELIGRO: puede sobreescribir index.html si se ejecuta
    ├── script.js
    ├── styles.css
    └── [scripts de QA]
```

---

## ⚠️ IMPORTANTE: Servidor local obligatorio

`conferencias.html` y `conferencia.html` cargan JSON con `fetch()`.  
**Esto NO funciona abriendo los archivos con `file://`** por política CORS del navegador.

### Iniciar servidor local

```bash
python -m http.server 8000
```

Luego abrir en el navegador:

```
http://localhost:8000
```

---

## URLs de prueba

| URL | Descripción |
|-----|-------------|
| `http://localhost:8000` | Landing |
| `http://localhost:8000/conferencias.html` | Catálogo completo |
| `http://localhost:8000/conferencia.html?id=fase-a-01` | Primera conferencia |
| `http://localhost:8000/conferencia.html?id=fase-b-01` | Primera de Fase B |
| `http://localhost:8000/conferencia.html?id=yo-abatimiento` | Estudio Yo 1 |
| `http://localhost:8000/conferencia.html?id=yo-miedo` | Estudio Yo 4 |
| `http://localhost:8000/conferencia.html?id=no-existe` | Debe mostrar 404 elegante |
| `http://localhost:8000/conferencias.html?phase=Y` | Filtro Yoes directo |

---

## IDs de las conferencias

| Colección | Formato | Rango | Nota |
|-----------|---------|-------|------|
| Fase A | `fase-a-NN` | 01–50 | **`fase-a-07` no existe** — el PDF original une 05 y 06 en una sola conferencia doble |
| Fase B | `fase-b-NN` | 01–25 | — |
| Yoes | `yo-NOMBRE` | 6 estudios | Ver tabla abajo |

### IDs de Yoes

| ID | Título |
|----|--------|
| `yo-abatimiento` | El Yo del Abatimiento por Pérdida Afectiva |
| `yo-conquistador` | El Yo Conquistador |
| `yo-machista` | El Yo Machista |
| `yo-miedo` | El Yo del Miedo |
| `yo-relacion-toxica` | El Yo de la Relación Tóxica |
| `yo-meditacion-500` | 500 Preguntas para Meditación Reflexiva |

---

## Regenerar conferencias.json desde PDFs

```bash
python generate_json.py
```

Requiere: `pip install pdfplumber` (o `pypdf2` según la versión del script).  
Los PDFs deben estar en `assets/`.

---

## Publicación

### Netlify (recomendado)

1. Subir la carpeta completa a un repositorio GitHub/GitLab.
2. En Netlify → **New site from Git** → seleccionar el repo.
3. **Build command:** dejar vacío (sitio estático).
4. **Publish directory:** `/` (o la raíz del repo).
5. Deploy. El sitio queda en una URL `.netlify.app`.

### Vercel

```bash
npm i -g vercel
vercel --cwd "C:\Users\Walter Losada\Desktop\ESTUDIOS YOES"
```

Seleccionar "Other" como framework. Publish directory: `./`.

### GitHub Pages

1. Subir todo a un repositorio público en GitHub.
2. En el repo → **Settings → Pages → Source: Deploy from branch → main → / (root)**.
3. El sitio queda en `https://USUARIO.github.io/REPO/`.

> **Nota GitHub Pages:** los paths relativos funcionan correctamente.  
> Si el repo se llama `cr-sitio`, las URLs serán `https://usuario.github.io/cr-sitio/conferencias.html`.

---

## Qué revisar en la consola del navegador

Abrir DevTools (F12) → pestaña **Console**. No debe haber:

- `Failed to fetch` → indica que se abrió con `file://` en vez de un servidor local.
- `404 (Not Found)` para `conferencias.json` o `yoes.json` → verificar que los archivos existen en `data/`.
- `Uncaught SyntaxError` → indica un problema en el JS inline.
- `tailwind is not defined` → verificar que `tailwind-config.js` carga ANTES del CDN de Tailwind.

---

## Redes sociales

| Red | URL |
|-----|-----|
| WhatsApp | https://chat.whatsapp.com/KWamxv5ZAsK2JobCfTkkzF |
| YouTube | https://www.youtube.com/@concienciarevolucionaria |
| Instagram | https://www.instagram.com/concienciarevolucionaria18/ |
| TikTok | https://www.tiktok.com/@concienciarevolucionaria |
| Facebook | https://www.facebook.com/profile.php?id=61550522941805 |
