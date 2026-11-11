import sys,glob,os,re
from bs4 import BeautifulSoup
d=sys.argv[1]
for f in glob.glob(d+'/*.htm'):
    s=BeautifulSoup(open(f,encoding='utf-8',errors='ignore'),'lxml')
    for t in s.find_all(style=re.compile(r'display:\s*none')): t.decompose()
    for t in s.find_all(['ix:header']): t.decompose()
    for tr in s.find_all('tr'):
        cells=[c.get_text(' ',strip=True) for c in tr.find_all(['td','th'])]
        tr.replace_with(' | '.join(c for c in cells if c)+'\n')
    txt=s.get_text('\n')
    txt=re.sub(r'[ \xa0\t]+',' ',txt); txt=re.sub(r'\n\s*\n+','\n',txt)
    open(f[:-4]+'.txt','w').write(txt)
