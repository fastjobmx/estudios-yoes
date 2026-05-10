import re
with open(r'C:\Users\Walter Losada\Desktop\ESTUDIOS YOES\index.html', encoding='utf-8') as f:
    html = f.read()

acc = html.count('accordion-item')
hdr = html.count('accordion-header')
yo  = html.count('yo-card-full')
print('accordion-item occurrences:', acc)
print('accordion-header occurrences:', hdr)
print('yo-card-full occurrences:', yo)

# Show first accordion item
idx = html.find('accordion-item')
print('\nFirst accordion context:')
print(html[idx-30:idx+120])
