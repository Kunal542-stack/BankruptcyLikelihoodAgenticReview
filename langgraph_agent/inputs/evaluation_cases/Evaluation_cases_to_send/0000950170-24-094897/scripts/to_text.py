import sys, glob, os, re
from bs4 import BeautifulSoup
folder = sys.argv[1]
for p in glob.glob(f"{folder}/*.htm"):
    soup = BeautifulSoup(open(p, 'rb').read(), 'lxml')
    for t in soup.find_all(['ix:header', 'script', 'style']):
        t.decompose()
    for d in soup.find_all(style=re.compile(r'display:\s*none')):
        d.decompose()
    for tr in soup.find_all('tr'):
        cells = [c.get_text(' ', strip=True) for c in tr.find_all(['td', 'th'])]
        tr.replace_with(soup.new_string('\n' + ' | '.join(c for c in cells if c) + '\n'))
    txt = soup.get_text('\n')
    txt = re.sub(r'[ \t\xa0]+', ' ', txt)
    txt = re.sub(r'\n\s*\n+', '\n', txt)
    open(p[:-4] + '.txt', 'w').write(txt)
    print(p, len(txt))
