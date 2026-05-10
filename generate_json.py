"""
Genera data/conferencias.json con contenido completo extraido de los PDFs.
"""
import PyPDF2, re, json, os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

FA = os.path.join(BASE, 'assets', 'Conferencias Fase A.pdf')
FB = os.path.join(BASE, 'assets', 'FASE B 2010.pdf')

def clean(t):
    t = re.sub(r'www\.conocimientodesimismo\.co[^\n]*', '', t)
    t = re.sub(r'Conocimiento de Si Mismo\s*\n?\s*Fase [AB]\s*[Pp][aá]gina \d+\s*', '', t)
    t = re.sub(r'Conferencia de Fase [AB]\.\s*\d+ de \d+\.?\s*', '', t)
    t = re.sub(r'\n{3,}', '\n\n', t)
    t = re.sub(r'[ \t]{2,}', ' ', t)
    return t.strip()

def get_pages(path, start, end):
    r = PyPDF2.PdfReader(path)
    pages = []
    for i in range(start - 1, min(end, len(r.pages))):
        try:
            t = r.pages[i].extract_text()
            if t:
                pages.append(clean(t))
        except:
            pass
    return '\n\n'.join(pages)

def text_to_content(raw):
    """Convert raw text to structured content blocks."""
    blocks = []
    # First pass: join lines that are clearly OCR-split mid-sentence
    lines = raw.split('\n')
    joined = []
    buf = ''
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if buf:
                joined.append(buf)
                buf = ''
            joined.append('')
            continue
        # If previous buffer ends mid-word (no ending punct, no heading start)
        if buf and not re.search(r'[\.!?:–—]\s*$', buf) and not re.match(r'^\d+\.?\s', stripped):
            buf = buf + ' ' + stripped
        else:
            if buf:
                joined.append(buf)
            buf = stripped
    if buf:
        joined.append(buf)
    raw = '\n'.join(joined)

    raw = re.sub(r'\n{3,}', '\n\n', raw).strip()
    paragraphs = raw.split('\n\n')

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        para_lines = para.split('\n')

        # Check if it's a heading (short, uppercase or title-style, no period at end)
        if len(para_lines) == 1:
            line = para_lines[0].strip()
            if (len(line) < 100 and
                (line.isupper() or
                 re.match(r'^(Conf\.|Conferencia|CONF|LOS |LAS |EL |LA |QUÉ |CÓMO |POR QUÉ |QUE |COMO |PARA )', line, re.I)) and
                not line.endswith('.')):
                level = 2 if line.isupper() else 3
                blocks.append({"type": "heading", "level": level, "text": line})
                continue

        # Check if it's a bullet/numbered list
        bullet_lines = [l for l in para_lines if re.match(r'^\s*[•\-\*·➤►▸◆✦]\s+', l)]
        numbered_lines = [l for l in para_lines if re.match(r'^\s*\d+[\.\)]\s+', l)]

        if len(bullet_lines) >= 2 or len(numbered_lines) >= 2:
            items = []
            for l in para_lines:
                l = l.strip()
                l = re.sub(r'^[•\-\*·➤►▸◆✦]\s+', '', l)
                l = re.sub(r'^\d+[\.\)]\s+', '', l)
                if l:
                    items.append(l)
            # If items look like long text, treat as paragraphs
            avg_len = sum(len(i) for i in items) / max(len(items),1)
            if avg_len > 120:
                for item in items:
                    blocks.append({"type": "paragraph", "text": item})
            elif items:
                blocks.append({"type": "list", "items": items})
            continue

        # Regular paragraph — join lines
        text = ' '.join(l.strip() for l in para_lines if l.strip())
        if len(text) > 20:
            blocks.append({"type": "paragraph", "text": text})

    return blocks

def make_tags(title, content_text):
    keyword_map = {
        'muerte': 'muerte psicológica', 'ego': 'ego', 'conciencia': 'conciencia',
        'meditac': 'meditación', 'karma': 'karma', 'dharma': 'dharma',
        'astral': 'astral', 'cuerpo': 'cuerpos', 'dimensi': 'dimensiones',
        'fuego': 'fuego sagrado', 'chakra': 'chakras', 'iglesia': 'chakras',
        'sexual': 'magia sexual', 'sexo': 'magia sexual', 'traici': 'traición',
        'miedo': 'miedo', 'bruj': 'brujería', 'péndulo': 'ley del péndulo',
        'pendulo': 'ley del péndulo', 'factor': 'tres factores', 'sacrif': 'sacrificio',
        'origen': 'ego', 'dualidad': 'dualidad', 'retorno': 'retorno',
        'recurrencia': 'recurrencia', 'alma': 'alma y espíritu', 'esencia': 'esencia',
        'fanatismo': 'fanatismo', 'exoter': 'esoterismo', 'esot': 'esoterismo',
        'concentraci': 'concentración', 'relajaci': 'relajación',
        'conjuraci': 'conjuraciones', 'droga': 'drogas', 'alcohol': 'alcoholismo',
        'observaci': 'auto-observación', 'familia': 'familia', 'apego': 'apegos',
        'koan': 'meditación', 'dervich': 'práctica', 'mantram': 'mantrams',
        'involuc': 'evolución', 'evoluc': 'evolución', 'infradim': 'infradimensiones',
        'octava': 'leyes cósmicas', 'entrop': 'leyes cósmicas', 'gravedad': 'trabajo interior',
        'psicol': 'psicología', 'charla': 'mente', 'interior': 'trabajo interior',
        'práctica': 'práctica', 'practica': 'práctica', 'lujuri': 'lujuria',
        'iniciaci': 'iniciación', 'bautismo': 'esoterismo', 'logia': 'discernimiento',
        'templo': 'discernimiento', 'hannasmuss': 'discernimiento', 'tantris': 'magia sexual',
        'rayo': 'cosmología', 'dant': 'infradimensiones', 'teosofia': 'discernimiento',
        'lucifer': 'discernimiento', 'intuici': 'despertar', 'cristo': 'cristo',
        'águila': 'símbolo', 'agui': 'símbolo', 'cruz': 'símbolo',
        'personalidad': 'ego', 'ser ': 'ser', 'país psic': 'psicología',
        'cambio radical': 'trabajo interior', 'no-identi': 'trabajo interior',
        'sacrificio': 'sacrificio',
    }
    t_lower = (title + ' ' + content_text[:500]).lower()
    tags = []
    seen = set()
    for k, v in keyword_map.items():
        if k in t_lower and v not in seen:
            tags.append(v)
            seen.add(v)
    # Add phase-generic tags
    if 'práctica' in title.lower() or 'práctica' in t_lower[:200]:
        if 'práctica' not in seen:
            tags.append('práctica')
    return tags[:6]

def make_summary(title, content_text, max_chars=180):
    """Extract first meaningful sentence as summary."""
    text = re.sub(r'\s+', ' ', content_text).strip()
    # Remove heading repetition at start
    title_clean = re.sub(r'Conf\. \d+ ', '', title)
    text = re.sub(re.escape(title_clean), '', text, flags=re.I).strip()
    # Take first 2 sentences
    sentences = re.split(r'(?<=[\.!?])\s+', text)
    summary = ''
    for s in sentences:
        if len(summary) + len(s) < max_chars:
            summary += s + ' '
        else:
            break
    return summary.strip() or text[:max_chars]

# ─── FASE A MAP ───
conf_a_map = [
    ('01', 5,  8,  'El conocimiento de sí mismo y objetivos'),
    ('02', 9,  11, 'Qué es la muerte. Lo que muere y lo que no muere'),
    ('03', 12, 13, 'El desdoblamiento astral'),
    ('04', 14, 18, 'Los siete centros de la máquina humana'),
    ('05', 19, 22, 'Las dimensiones y dónde están en nosotros'),
    ('07', 23, 24, 'Las conjuraciones: Belilín, Círculo Mágico, Júpiter, Pentalfa'),
    ('08', 25, 28, 'Evolución, involución y revolución'),
    ('09', 29, 31, 'Las infradimensiones'),
    ('10', 32, 35, 'Los siete cuerpos'),
    ('11', 36, 39, 'Cómo se fabrica alma y espíritu'),
    ('12', 40, 41, 'Retorno y recurrencia'),
    ('13', 42, 45, 'Leyes de karma y dharma'),
    ('14', 46, 51, 'Drogas y alcoholismo'),
    ('15', 52, 54, 'Ego, personalidad y esencia'),
    ('16', 55, 57, 'Observación de sí mismo. La auto-observación'),
    ('17', 58, 61, 'Los tres factores de la revolución de la conciencia'),
    ('18', 62, 65, 'La charla interior y la canción psicológica'),
    ('19', 66, 71, 'Estados y eventos'),
    ('20', 72, 73, 'El país psicológico'),
    ('21', 74, 76, 'Concentración y relajación'),
    ('22', 77, 78, 'La meditación'),
    ('23', 79, 82, 'Fanatismo y mitomanía'),
    ('24', 83, 88, 'La vida y el nivel del ser'),
    ('25', 89, 91, 'Exoterismo, pseudo-esoterismo y esoterismo'),
    ('26', 92, 93, 'El mundo de relaciones'),
    ('27', 94, 95, 'Técnica para disolver el yo. Los detalles'),
    ('28', 96, 98, 'El Cristo universal e individual'),
    ('29', 99, 104, 'La ley del péndulo'),
    ('30', 105, 106, 'Método para despertar la conciencia. Las dos conciencias: objetiva y subjetiva'),
    ('31', 107, 108, 'Criaturas mecánicas'),
    ('32', 109, 110, 'El cambio radical'),
    ('33', 111, 114, 'Ley de octavas y ley de entropía'),
    ('34', 115, 118, 'El centro de gravedad permanente'),
    ('35', 119, 122, 'Explicaciones sobre la familia y los apegos'),
    ('36', 123, 124, 'Meditación y koanes'),
    ('37', 125, 125, 'Práctica para el desdoblamiento astral. El saltico'),
    ('38', 126, 129, 'El difícil camino y el trabajo crístico'),
    ('39', 130, 132, 'La no-identificación con las cosas del diario vivir y por qué juzgamos a los demás'),
    ('40', 133, 136, 'Sacrificio por la humanidad'),
    ('41', 137, 140, 'La danza de los derviches y la transmutación de las fuerzas cósmicas'),
    ('42', 141, 142, 'Dos clases de conocimiento: objetivo y subjetivo'),
    ('43', 143, 145, 'Diversos tipos de yoes lujuriosos'),
    ('44', 146, 149, 'El yo de la traición'),
    ('45', 150, 152, 'Qué debemos hacer para que las prácticas den resultados positivos'),
    ('46', 153, 156, 'Cómo controlar poluciones nocturnas y caídas sexuales'),
    ('47', 157, 160, 'El yo de la brujería'),
    ('48', 161, 161, 'Pronunciación de mantrams para el desdoblamiento astral'),
    ('49', 162, 168, 'La dualidad'),
    ('50', 169, 170, 'El origen del ego'),
]

# ─── FASE B MAP ───
conf_b_map = [
    ('01', 4,  6,  'Concentración y Relajación'),
    ('02', 7,  7,  'Práctica de Meditación Reflexiva'),
    ('03', 8,  8,  'Práctica de Desdoblamiento Astral'),
    ('04', 9,  9,  'El Desdoblamiento Mental'),
    ('05', 10, 13, 'El Equilibrio de los Centros y la Fabricación de los Mercurios'),
    ('06', 14, 17, 'Las Siete Iglesias y los Siete Chacras'),
    ('07', 18, 20, 'La Iniciación y las Pruebas'),
    ('08', 21, 22, 'El Fuego Sagrado'),
    ('09', 23, 24, 'Cuál es el Verdadero Bautismo'),
    ('10', 25, 26, 'La Primera Montaña'),
    ('11', 27, 27, 'La Segunda Montaña'),
    ('12', 28, 29, 'La Tercera Montaña'),
    ('13', 30, 30, 'Cuatro Clases de Hannasmussen'),
    ('14', 31, 32, 'Tres Clases de Tantrismo'),
    ('15', 33, 34, 'El Rayo de la Creación'),
    ('16', 35, 37, 'Círculos Dantescos 1, 2, 3, 4 y 5'),
    ('17', 38, 40, 'Círculos Dantescos 6, 7, 8 y 9'),
    ('18', 41, 42, 'Teosofía, Espiritismo y Médium'),
    ('19', 43, 44, 'Lucifer, Diablo y Satán'),
    ('20', 45, 45, 'La Intuición'),
    ('21', 46, 47, 'El Cristo Íntimo y la muerte de los Yoes Causa'),
    ('22', 48, 49, 'La Vida Íntima de cada uno'),
    ('23', 50, 51, 'El Símbolo del Águila tragándose la Serpiente'),
    ('24', 52, 52, 'La práctica de la Cruz y qué simboliza la Cruz'),
    ('25', 53, 58, 'Cómo diferenciar un Templo de Magia Blanca de uno de Magia Negra'),
]

conferences = []

print('Extrayendo Fase A...')
for num, s, e, title in conf_a_map:
    raw = get_pages(FA, s, e)
    content = text_to_content(raw)
    conf_text = ' '.join(
        b['text'] for b in content if b.get('type') == 'paragraph'
    )
    entry = {
        'id': f'fase-a-{num}',
        'phase': 'A',
        'number': num,
        'title': title,
        'page': s,
        'summary': make_summary(title, conf_text),
        'tags': make_tags(title, conf_text),
        'content': content,
    }
    conferences.append(entry)
    print(f'  A-{num}: {len(content)} bloques')

print('Extrayendo Fase B...')
for num, s, e, title in conf_b_map:
    raw = get_pages(FB, s, e)
    content = text_to_content(raw)
    conf_text = ' '.join(
        b['text'] for b in content if b.get('type') == 'paragraph'
    )
    entry = {
        'id': f'fase-b-{num}',
        'phase': 'B',
        'number': num,
        'title': title,
        'page': s,
        'summary': make_summary(title, conf_text),
        'tags': make_tags(title, conf_text),
        'content': content,
    }
    conferences.append(entry)
    print(f'  B-{num}: {len(content)} bloques')

out = os.path.join(DATA_DIR, 'conferencias.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(conferences, f, ensure_ascii=False, indent=2)

size = os.path.getsize(out)
print(f'\nOK: {len(conferences)} conferencias → data/conferencias.json ({size:,} bytes)')
