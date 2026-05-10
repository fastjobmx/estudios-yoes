# Conciencia Revolucionaria — Guía de Administración V1

> Versión congelada: Mayo 2026  
> Estado: Producción lista. 97/97 checks OK.

---

## 1. Estructura final de carpetas

```
ESTUDIOS YOES/
│
├── index.html              ← Landing principal
├── conferencias.html       ← Catálogo / biblioteca
├── conferencia.html        ← Lector individual
├── cr-styles.css           ← Estilos globales del sitio
├── tailwind-config.js      ← Paleta de colores y fuentes (Tailwind)
├── app.js                  ← Helpers JS (referencia, no se importa directamente)
├── generate_json.py        ← Herramienta: regenerar conferencias.json desde PDFs
├── README.md               ← Instrucciones técnicas para desarrolladores
├── GUIA-V1.md              ← Esta guía
│
├── data/
│   ├── conferencias.json   ← 74 conferencias estructuradas (Fase A + Fase B)
│   └── yoes.json           ← 6 Estudios de los Yoes
│
├── assets/
│   ├── logo.png            ← Logo principal (también favicon)
│   ├── logo1.svg           ← Logo alternativo SVG
│   ├── og-image.svg        ← Imagen para compartir en redes sociales
│   ├── Conferencias Fase A.pdf  ← Fuente original Fase A
│   ├── FASE B 2010.pdf          ← Fuente original Fase B
│   └── [PDFs de Yoes]           ← Fuentes de los estudios de los Yoes
│
└── _deprecated/            ← Archivos del sistema anterior — NO ejecutar
    ├── build_html.py       ← ⚠️ PELIGRO: puede sobreescribir index.html
    ├── script.js
    ├── styles.css
    └── [scripts de QA]
```

---

## 2. Qué hace cada archivo

| Archivo | Función |
|---------|---------|
| `index.html` | Landing cinematográfica. Hero, pilares, método, sección Yoes con 6 tarjetas, CTA biblioteca, footer. Todo el JS está inline al final del archivo. |
| `conferencias.html` | Catálogo con buscador en tiempo real, filtros por Fase A / Fase B / Yoes, vista grid y lista, indicadores de "leída", skeleton de carga. Carga `data/conferencias.json` + `data/yoes.json` via `fetch()`. |
| `conferencia.html` | Lector individual. Recibe `?id=fase-a-01` en la URL. Genera TOC automático, muestra tiempo de lectura, prev/next dentro de la misma colección, conferencias relacionadas, modo foco, barra de progreso. Marca como "leída" al llegar al 85% de la página. |
| `cr-styles.css` | Sistema de diseño compartido: variables de color, navbar, tarjetas, skeleton, TOC, prose-reader, animaciones (halo, fade, backToTop, hover radial). |
| `tailwind-config.js` | Define los colores y fuentes personalizadas de Tailwind. **Debe cargarse antes del CDN de Tailwind** en cada HTML. |
| `generate_json.py` | Script Python que extrae texto de los PDFs y genera `data/conferencias.json`. Solo necesario si se actualizan los PDFs. |
| `data/conferencias.json` | Base de datos de 74 conferencias en formato JSON. Cada entrada tiene: `id`, `phase`, `number`, `title`, `page`, `summary`, `tags[]`, `content[]`. |
| `data/yoes.json` | Base de datos de 6 estudios de los Yoes. Misma estructura que conferencias pero con `collection: "yoes"` en lugar de `phase`. |

---

## 3. Cómo editar una conferencia existente

Abrir `data/conferencias.json` y localizar la conferencia por su `id`.

```json
{
  "id": "fase-a-15",
  "phase": "A",
  "number": "15",
  "title": "Ego, personalidad y esencia",
  "page": "87",
  "summary": "Texto del resumen que aparece en la tarjeta del catálogo.",
  "tags": ["ego", "personalidad", "esencia"],
  "content": [
    { "type": "heading", "level": 2, "text": "Título de sección" },
    { "type": "paragraph", "text": "Párrafo de contenido." },
    { "type": "list", "items": ["Punto uno", "Punto dos"] }
  ]
}
```

**Campos editables:**
- `title` — Título visible en tarjeta y lector
- `summary` — Resumen corto (máx. 2-3 líneas) visible en la tarjeta
- `tags` — Array de etiquetas para filtrar (usar minúsculas, sin acentos preferiblemente)
- `content` — Array de bloques de texto del lector

**Tipos de bloque en `content`:**

| `type` | Campos requeridos | Resultado |
|--------|-------------------|-----------|
| `heading` | `level` (2 o 3), `text` | Subtítulo en el lector + entrada en el TOC |
| `paragraph` | `text` | Párrafo de prosa |
| `list` | `items` (array de strings) | Lista con viñetas |

---

## 4. Cómo agregar una nueva conferencia

1. Abrir `data/conferencias.json`.
2. Agregar un nuevo objeto al array, siguiendo el formato del punto anterior.
3. Elegir el `id` correcto:
   - Fase A: `fase-a-NN` (ej. `fase-a-51` si hay una nueva)
   - Fase B: `fase-b-NN` (ej. `fase-b-26`)
4. **Verificar que el JSON sigue siendo válido** antes de guardar. Usar un validador online como [jsonlint.com](https://jsonlint.com) o correr en terminal:
   ```bash
   python -c "import json; json.load(open('data/conferencias.json', encoding='utf-8')); print('OK')"
   ```
5. No se necesita tocar ningún HTML. El catálogo y el lector la detectan automáticamente.

> **Nota sobre `fase-a-07`:** este ID no existe intencionalmente. El PDF original une las conferencias 05 y 06 en un solo documento doble. El salto de 06 a 08 es correcto.

---

## 5. Cómo agregar un nuevo estudio de Yo

1. Abrir `data/yoes.json`.
2. Agregar un nuevo objeto al array:

```json
{
  "id": "yo-nuevo-nombre",
  "collection": "yoes",
  "title": "El Yo del Nuevo Defecto",
  "summary": "Descripción breve del estudio para la tarjeta.",
  "tags": ["etiqueta1", "etiqueta2"],
  "content": [
    { "type": "heading", "level": 2, "text": "Introducción" },
    { "type": "paragraph", "text": "Contenido del estudio..." }
  ]
}
```

3. **Importante:** el campo `"collection": "yoes"` es obligatorio. Sin él, el filtro "Yoes" no lo mostrará.
4. Si quieres que aparezca en la sección Yoes de `index.html`, agregar una tarjeta nueva en esa sección (en el bloque `<!-- ══ YOES ══ -->`), siguiendo el patrón de las 6 existentes, y apuntando al nuevo ID.

---

## 6. Cómo cambiar el logo

El logo se usa en tres lugares:

1. **Navbar** (en los 3 HTMLs):
   ```html
   <img src="assets/logo.png" alt="Logo" ...
        onerror="this.onerror=null;this.src='assets/logo.svg';" />
   ```
2. **Footer** de `index.html` — mismo patrón.
3. **Favicon** (en los 3 HTMLs):
   ```html
   <link rel="icon" href="assets/logo.png" type="image/png" />
   ```

**Para cambiar el logo:**
- Reemplazar `assets/logo.png` con la nueva imagen (mismo nombre).
- Si el nuevo logo es SVG, reemplazar también `assets/logo1.svg` y cambiar el `onerror` fallback.
- Si cambias el nombre del archivo, actualizar las 3 referencias en cada HTML (buscar `logo.png`).

---

## 7. Cómo cambiar colores

Los colores se definen en **dos lugares** que deben mantenerse sincronizados:

### `tailwind-config.js` (clases Tailwind utilitarias)

```js
tailwind.config = {
  theme: {
    extend: {
      colors: {
        void:     '#050505',  // Negro obsidiana — fondo principal
        gold:     '#C6A15B',  // Dorado envejecido — acentos
        gold2:    '#F0D58C',  // Dorado claro — textos dorados, labels
        ember:    '#7A3F22',  // Óxido — acentos cálidos secundarios
        bone:     '#F6F0E7',  // Marfil — texto principal
      }
    }
  }
}
```

### `cr-styles.css` (variables CSS para animaciones y componentes)

```css
:root {
  --gold:  #C6A15B;
  --gold2: #F0D58C;
  --void:  #050505;
  --bone:  #F6F0E7;
  --ember: #7A3F22;
}
```

**Cambiar un color:** editar el mismo valor en ambos archivos. Si solo se cambia en uno, los colores quedan inconsistentes entre las clases Tailwind y los componentes CSS puros.

---

## 8. Cómo cambiar textos de la landing

Abrir `index.html`. Los textos editables están en estas secciones:

| Sección | Buscador sugerido | Qué encontrarás |
|---------|-------------------|-----------------|
| Hero | `<!-- ══ HERO ══ -->` | Título principal, subtítulo poético, chips de stats |
| Pilares | `<!-- ══ PILARES ══ -->` | Títulos y descripciones de los 3 pilares |
| Método | `<!-- ══ MÉTODO ══ -->` | Pasos del método, citas |
| Yoes | `<!-- ══ YOES ══ -->` | Títulos, descripciones y links de los 6 Yoes |
| Biblioteca CTA | `<!-- ══ BIBLIOTECA CTA ══ -->` | Frase de llamada a acción |
| Footer | `<footer` | Texto del pie de página, links de redes |

**Regla:** no tocar las clases CSS ni los `id=` al editar texto. Solo modificar el contenido entre las etiquetas HTML.

---

## 9. Cómo probar localmente

**Paso 1** — Abrir terminal en la carpeta del proyecto:
```bash
cd "C:\Users\Walter Losada\Desktop\ESTUDIOS YOES"
```

**Paso 2** — Iniciar servidor:
```bash
python -m http.server 8000
```

**Paso 3** — Abrir en el navegador:
```
http://localhost:8000
```

> ⚠️ **No abrir los archivos con doble clic** (protocolo `file://`). El `fetch()` que carga los JSON falla silenciosamente con CORS. Siempre usar el servidor local.

**URLs de prueba clave:**

| URL | Qué verificar |
|-----|---------------|
| `http://localhost:8000` | Landing completa, links, animaciones |
| `http://localhost:8000/conferencias.html` | Skeleton → tarjetas, búsqueda, filtros |
| `http://localhost:8000/conferencia.html?id=fase-a-01` | TOC, prev/next, modo foco |
| `http://localhost:8000/conferencia.html?id=yo-miedo` | Yoes carga bien, prev/next entre Yoes |
| `http://localhost:8000/conferencia.html?id=no-existe` | Debe mostrar 404 elegante |
| `http://localhost:8000/conferencias.html?phase=Y` | Llega filtrado a Yoes |

---

## 10. Cómo publicar

### Netlify (recomendado — gratis, sin configuración)

1. Crear cuenta en [netlify.com](https://netlify.com)
2. Arrastrar la carpeta completa al área de deploy en el dashboard, **o bien:**
3. Subir a GitHub → Netlify → **Add new site → Import an existing project** → seleccionar repo → Build command: vacío → Publish directory: `.` → **Deploy**.
4. El sitio queda en una URL como `https://nombre-aleatorio.netlify.app`.
5. Para dominio personalizado: **Domain management → Add custom domain**.

### Vercel

```bash
npm i -g vercel
vercel "C:\Users\Walter Losada\Desktop\ESTUDIOS YOES"
```
Seleccionar framework: **Other**. Publish directory: `./`.

### GitHub Pages (requiere repositorio público)

1. Subir la carpeta a un repositorio en GitHub.
2. En el repo: **Settings → Pages → Source: Deploy from branch → main → / (root) → Save**.
3. El sitio queda en `https://USUARIO.github.io/NOMBRE-REPO/`.

> **Nota:** en GitHub Pages, si el repo no está en la raíz del dominio, los paths relativos siguen funcionando correctamente porque todos los links son relativos (`conferencias.html`, `assets/logo.png`, etc.).

---

## 11. Checklist antes de publicar

Ejecutar con el servidor local activo:

### Navegación
- [ ] `index.html` abre correctamente en el navegador
- [ ] El link "Biblioteca" lleva a `conferencias.html`
- [ ] Los 6 links de Yoes en la sección Yoes abren el lector correctamente
- [ ] El link "Conf. 40 — Sacrificio" del pilar Sacrificio abre bien
- [ ] En `conferencias.html`, al hacer clic en una tarjeta se abre el lector
- [ ] En el lector, el botón "← Biblioteca" regresa al catálogo
- [ ] Los botones Anterior / Siguiente navegan entre conferencias de la misma fase
- [ ] El menú móvil (ícono hamburguesa) funciona y se cierra al hacer clic en un link

### Datos
- [ ] El catálogo muestra 74 conferencias + 6 Yoes = 80 items en "Todo"
- [ ] El filtro "Fase A" muestra 49 items
- [ ] El filtro "Fase B" muestra 25 items
- [ ] El filtro "Yoes" muestra 6 items
- [ ] La búsqueda filtra por título, tags y resumen
- [ ] `conferencia.html?id=no-existe` muestra el 404 elegante

### Lector
- [ ] El TOC aparece en la barra lateral (desktop)
- [ ] La barra de progreso sube al hacer scroll
- [ ] El porcentaje "X% leído" se actualiza
- [ ] El modo Foco oculta el sidebar y muestra el botón "Salir del modo foco"
- [ ] Los botones A− y A+ cambian el tamaño de fuente
- [ ] El botón "Copiar enlace" funciona
- [ ] Al llegar al 85% de una conferencia, aparece el badge "Leída"
- [ ] Al volver al catálogo, la tarjeta de esa conferencia muestra el badge "Leída"

### Visual (revisar en Chrome, Firefox y móvil)
- [ ] El favicon (logo) aparece en la pestaña del navegador
- [ ] Las fuentes cargan (Cormorant Garamond para títulos, Inter para cuerpo)
- [ ] Las tarjetas tienen efecto hover suave (inclinación 3D)
- [ ] El botón "volver arriba" aparece al bajar más de 500px
- [ ] La transición de página (fade) funciona al navegar entre páginas

### Consola (F12 → Console)
- [ ] Sin errores rojos
- [ ] Sin advertencias de `Failed to fetch`
- [ ] Sin `tailwind is not defined`

---

## 12. Recomendaciones para V2

Estas mejoras están fuera del alcance de V1 pero son las más valiosas para el futuro.

### Contenido
- **Audio por conferencia** — Agregar campo `audio_url` en el JSON y un reproductor inline en el lector. Ideal si hay grabaciones.
- **Notas personales** — Campo de texto por conferencia guardado en `localStorage`. El lector ya tiene la infraestructura.
- **Exportar a PDF** — Botón "Imprimir conferencia" con CSS `@media print` que oculta la navegación.

### Datos
- **Buscador global con índice** — Construir un índice de búsqueda en memoria al cargar (Fuse.js o similar) para búsqueda difusa más tolerante a errores tipográficos.
- **Paginación o scroll infinito** — Si el catálogo crece a 150+ items, el render inicial puede ser lento. Virtualizar la lista.
- **Timestamp de última edición** — Agregar campo `updated_at` en el JSON para mostrar "Actualizado el…" en el lector.

### Técnico
- **Service Worker (PWA)** — Cachear los JSON y los assets para que el sitio funcione offline. Solo requiere un `sw.js` de ~30 líneas.
- **`netlify.toml` o `vercel.json`** — Configurar redirects para que `yourdomain.com/conferencia/fase-a-01` funcione como URL limpia en lugar de `?id=fase-a-01`.
- **Og:image dinámica** — Generar una imagen OG por conferencia con el título renderizado. Requiere un servidor (Netlify Edge Functions o similar).
- **Analytics mínimos** — Plausible o Fathom (privacidad-first, sin cookies) para saber qué conferencias se leen más.

### UX
- **Modo claro** — Toggle light/dark. La paleta oscura es la identidad, pero el modo claro ayuda a lectores de día.
- **Progreso sincronizado** — Si el usuario lee en dos dispositivos, sincronizar el progreso via un backend mínimo (Supabase free tier).
- **Índice general de Yoes** — Página dedicada `/yoes.html` con todos los estudios en profundidad, separada del catálogo general.

---

*Versión V1 — Mayo 2026 — Proyecto listo para producción.*
