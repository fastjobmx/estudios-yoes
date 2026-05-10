import PyPDF2, re, json

BASE = r'C:\Users\Walter Losada\Desktop\ESTUDIOS YOES\assets'

def safe_text(path, s, e, mx=3000):
    try:
        r = PyPDF2.PdfReader(path)
        out = []
        for i in range(s-1, min(e, len(r.pages))):
            try:
                t = r.pages[i].extract_text()
                if t:
                    t = re.sub(r'www\.conocimientodesimismo\.co[^\n]*', '', t)
                    t = re.sub(r'Conferencia de Fase [AB]\.\s*\d+ de \d+\.?\s*', '', t)
                    t = re.sub(r'\s{2,}', ' ', t)
                    out.append(t.strip())
            except:
                pass
        full = re.sub(r'\s+', ' ', ' '.join(out)).strip()
        return full[:mx]
    except Exception as ex:
        return 'Error: ' + str(ex)

def yo_full(path, mx=4000):
    try:
        r = PyPDF2.PdfReader(path)
        out = []
        for p in r.pages:
            try:
                t = p.extract_text()
                if t:
                    t = re.sub(r'\s{2,}', ' ', t)
                    out.append(t.strip())
            except:
                pass
        full = re.sub(r'\s+', ' ', ' '.join(out)).strip()
        return full[:mx]
    except Exception as ex:
        return 'Error: ' + str(ex)

# ── FASE A ──
fa = BASE + r'\Conferencias Fase A.pdf'
conf_a_map = [
    (1,  5,  8,  'El Conocimiento de Sí Mismo y Objetivos'),
    (2,  9,  11, 'Qué es la Muerte. Lo que Muere y lo que No Muere'),
    (3,  12, 13, 'El Desdoblamiento Astral'),
    (4,  14, 18, 'Los Siete Centros de la Máquina Humana'),
    (5,  19, 22, 'Las Dimensiones y Dónde Están en Nosotros'),
    (7,  23, 24, 'Las Conjuraciones: Belilín, Círculo Mágico, Júpiter, Pentalfa'),
    (8,  25, 28, 'Evolución, Involución y Revolución'),
    (9,  29, 31, 'Las Infradimensiones'),
    (10, 32, 35, 'Los Siete Cuerpos'),
    (11, 36, 39, 'Cómo se Fabrica Alma y Espíritu'),
    (12, 40, 41, 'Retorno y Recurrencia'),
    (13, 42, 45, 'Leyes de Karma y Dharma'),
    (14, 46, 51, 'Drogas y Alcoholismo'),
    (15, 52, 54, 'Ego, Personalidad y Esencia'),
    (16, 55, 57, 'Observación de Sí Mismo — La Auto-Observación'),
    (17, 58, 61, 'Los Tres Factores de la Revolución de la Conciencia'),
    (18, 62, 65, 'La Charla Interior y la Canción Psicológica'),
    (19, 66, 71, 'Estados y Eventos'),
    (20, 72, 73, 'El País Psicológico'),
    (21, 74, 76, 'Concentración y Relajación'),
    (22, 77, 78, 'La Meditación'),
    (23, 79, 82, 'Fanatismo y Mitomanía'),
    (24, 83, 88, 'La Vida y el Nivel del Ser'),
    (25, 89, 91, 'Exoterismo, Pseudo-Esoterismo y Esoterismo'),
    (26, 92, 93, 'El Mundo de Relaciones'),
    (27, 94, 95, 'Técnica para Disolver el Yo. Los Detalles'),
    (28, 96, 98, 'El Cristo Universal e Individual'),
    (29, 99, 104, 'La Ley del Péndulo'),
    (30, 105, 106, 'Método para Despertar la Conciencia'),
    (31, 107, 108, 'Criaturas Mecánicas'),
    (32, 109, 110, 'El Cambio Radical'),
    (33, 111, 114, 'Ley de Octavas y Ley de Entropía'),
    (34, 115, 118, 'El Centro de Gravedad Permanente'),
    (35, 119, 122, 'Explicaciones sobre la Familia y los Apegos'),
    (36, 123, 124, 'Meditación y Koanes'),
    (37, 125, 125, 'Práctica para el Desdoblamiento Astral. El Saltico'),
    (38, 126, 129, 'El Difícil Camino y el Trabajo Crístico'),
    (39, 130, 132, 'La No-Identificación con las Cosas del Diario Vivir'),
    (40, 133, 136, 'Sacrificio por la Humanidad'),
    (41, 137, 140, 'La Danza de los Derviches y la Transmutación'),
    (42, 141, 142, 'Dos Clases de Conocimiento: Objetivo y Subjetivo'),
    (43, 143, 145, 'Diversos Tipos de Yoes Lujuriosos'),
    (44, 146, 149, 'El Yo de la Traición'),
    (45, 150, 152, 'Qué Debemos Hacer para que las Prácticas den Resultados'),
    (46, 153, 156, 'Cómo Controlar Poluciones Nocturnas y Caídas Sexuales'),
    (47, 157, 160, 'El Yo de la Brujería'),
    (48, 161, 161, 'Pronunciación de Mantrams para el Desdoblamiento Astral'),
    (49, 162, 168, 'La Dualidad'),
    (50, 169, 170, 'El Origen del Ego'),
]

fase_a = {}
for num, s, e, title in conf_a_map:
    txt = safe_text(fa, s, e)
    fase_a[str(num).zfill(2)] = {'num': num, 'title': title, 'text': txt}

print(f'Fase A: {len(fase_a)} conferencias extraidas')

# ── FASE B ──
fb = BASE + r'\FASE B 2010.pdf'
rb = PyPDF2.PdfReader(fb)
print(f'Fase B total paginas: {len(rb.pages)}')

# Scan for lesson boundaries
for i in range(len(rb.pages)):
    try:
        t = rb.pages[i].extract_text()
        if t and ('Lección' in t or 'LECCION' in t.upper() or 'Leccion' in t):
            print(f'  PAG {i+1}: {t.strip()[:120]}')
    except:
        pass
