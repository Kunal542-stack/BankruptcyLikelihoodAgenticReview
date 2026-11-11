import sys, glob, os, re
from bs4 import BeautifulSoup
src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
BLOCK = ['p', 'div', 'br', 'li', 'h1', 'h2', 'h3', 'h4', 'table']
for p in glob.glob(f"{src}/*.htm"):
    soup = BeautifulSoup(open(p, 'rb').read(), 'html.parser')
    for t in soup.find_all(['ix:header', 'script', 'style']): t.decompose()
    for d in soup.find_all(style=re.compile(r'display:\s*none')): d.decompose()
    for tr in soup.find_all('tr'):
        cells = [re.sub(r'\s+', ' ', c.get_text('', strip=False)).strip() for c in tr.find_all(['td', 'th'])]
        tr.replace_with(soup.new_string('\n' + ' | '.join(c for c in cells if c) + '\n'))
    for b in soup.find_all(BLOCK):
        b.insert_before('\n'); b.insert_after('\n')
    txt = soup.get_text('')
    txt = txt.replace('\xa0', ' ')
    txt = re.sub(r'[ \t]+', ' ', txt)
    txt = re.sub(r'\n\s*\n*', '\n', txt)
    open(f"{dst}/{os.path.basename(p)[:-4]}.txt", 'w').write(txt)
