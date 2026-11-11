import sys, os, re, glob
from bs4 import BeautifulSoup
src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
for f in glob.glob(src+'/*.htm'):
    s = BeautifulSoup(open(f,'rb').read(), 'lxml')
    for t in s(['script','style']): t.decompose()
    for t in s.find_all(lambda x: x.name and x.name.lower() in ('ix:header',)): t.decompose()
    for d in s.find_all(style=re.compile(r'display:\s*none')): d.decompose()
    for tr in s.find_all('tr'):
        cells = [c.get_text(' ', strip=True) for c in tr.find_all(['td','th'])]
        tr.replace_with(' | '.join(c for c in cells if c) + '\n')
    txt = s.get_text('\n')
    txt = re.sub(r'[ \xa0\t]+', ' ', txt); txt = re.sub(r'\n\s*\n+', '\n', txt)
    open(os.path.join(dst, os.path.basename(f).replace('.htm','.txt')),'w').write(txt)
