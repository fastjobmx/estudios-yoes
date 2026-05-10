import json

with open(r'C:\Users\Walter Losada\Desktop\ESTUDIOS YOES\data\conferencias.json', encoding='utf-8') as f:
    data = json.load(f)

print('=== Fase A (primeras 6) ===')
for c in data[:6]:
    first = c['content'][0] if c['content'] else {}
    preview = first.get('text','')[:75] if first.get('type')=='paragraph' else repr(first)[:75]
    print(f"  {c['id']:16} | {len(c['content']):2}bl | tags={c['tags'][:3]}")
    print(f"    {preview}")

print()
print('=== Fase B (todas) ===')
for c in [x for x in data if x['phase'] == 'B']:
    print(f"  {c['id']:16} | {len(c['content']):2}bl | {c['summary'][:60]}")

total_chars = sum(
    sum(len(b.get('text','')) for b in c['content'] if b.get('type') == 'paragraph')
    for c in data
)
print(f"\nTotal caracteres de prosa: {total_chars:,}")
print(f"Total conferencias: {len(data)}")
