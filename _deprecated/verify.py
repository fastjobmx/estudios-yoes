with open(r'C:\Users\Walter Losada\Desktop\ESTUDIOS YOES\index.html', encoding='utf-8') as f:
    html = f.read()

checks = [
    ('Hero section',        'id="hero"'),
    ('Logo PNG',            'assets/logo.png'),
    ('Pilares section',     'id="pilares"'),
    ('Factores section',    'id="factores"'),
    ('Yoes section',        'id="yoes"'),
    ('Biblioteca section',  'id="biblioteca"'),
    ('Fase A tab',          'id="fase-a"'),
    ('Fase B tab',          'id="fase-b"'),
    ('Accordion items',     'accordion-item'),
    ('Yo cards',            'yo-card-full'),
    ('script.js',           'script.js'),
    ('Conf A 01',           'El Conocimiento de'),
    ('Conf A 50',           'El Origen del Ego'),
    ('Conf B 01',           'Concentraci'),
    ('Conf B 25',           'ntesis'),
    ('Yo depresion',        'Abatimiento'),
    ('Yo miedo',            'Miedo'),
    ('Yo toxica',           'xica'),
    ('Footer frase',        'La muerte es la puerta'),
]

all_ok = True
for name, needle in checks:
    ok = needle in html
    status = 'OK     ' if ok else 'MISSING'
    if not ok:
        all_ok = False
    print(status, '-', name)

print()
print('Total HTML size:', f'{len(html):,}', 'chars')
print('Accordion items:', html.count('class="accordion-item"'))
print('Yo cards:       ', html.count('yo-card-full'))
print()
print('ALL OK' if all_ok else 'SOME CHECKS FAILED')
