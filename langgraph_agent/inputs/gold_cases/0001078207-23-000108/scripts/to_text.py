import sys, os, re
from bs4 import BeautifulSoup
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
for f in sorted(os.listdir(src)):
    if not f.endswith('.htm'): continue
    soup = BeautifulSoup(open(os.path.join(src,f), encoding='utf-8', errors='ignore').read(), 'html.parser')
    for t in soup(['script','style']): t.decompose()
    for t in soup.find_all(lambda x: x.name and x.name.lower() in ('ix:header',)): t.decompose()
    for d in soup.find_all(style=re.compile(r'display:\s*none')): d.decompose()
    for tr in soup.find_all('tr'):
        cells = [c.get_text(' ', strip=True) for c in tr.find_all(['td','th'])]
        cells = [c for c in cells if c]
        tr.replace_with(soup.new_string('\n' + ' | '.join(cells) + '\n'))
    txt = soup.get_text('\n')
    txt = re.sub(r'[ \t\xa0]+', ' ', txt)
    txt = re.sub(r'\n\s*\n+', '\n', txt)
    open(os.path.join(out, f.replace('.htm','.txt')), 'w').write(txt)
    print(f, len(txt))
