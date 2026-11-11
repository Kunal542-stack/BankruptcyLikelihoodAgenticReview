import sys, os, re
from bs4 import BeautifulSoup
src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
for f in sorted(os.listdir(src)):
    if not f.endswith('.htm'):
        continue
    soup = BeautifulSoup(open(os.path.join(src, f), encoding='utf-8', errors='ignore'), 'html.parser')
    for t in soup.find_all(['ix:header', 'script', 'style']):
        t.decompose()
    for d in soup.find_all(style=re.compile(r'display:\s*none')):
        d.decompose()
    for tr in soup.find_all('tr'):
        cells = [c.get_text(' ', strip=True) for c in tr.find_all(['td', 'th'])]
        cells = [c for c in cells if c and c not in ('$', ')', '%')]
        tr.replace_with(soup.new_string('\n' + ' | '.join(cells) + '\n'))
    for b in soup.find_all(['p', 'div', 'br', 'li', 'h1', 'h2', 'h3', 'h4']):
        b.insert_after(soup.new_string('\n'))
    txt = soup.get_text()
    txt = txt.replace('\xa0', ' ')
    txt = re.sub(r'[ \t]+', ' ', txt)
    txt = re.sub(r'\n\s*\n+', '\n', txt)
    open(os.path.join(dst, f.replace('.htm', '.txt')), 'w').write(txt)
    print(f, len(txt))
