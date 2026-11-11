import sys,glob,os,re
from bs4 import BeautifulSoup
for f in glob.glob(sys.argv[1]+'/*.htm'):
    s=BeautifulSoup(open(f,'rb').read(),'lxml')
    for t in s.find_all(['ix:header']): t.decompose()
    for t in s.find_all(style=re.compile(r'display:\s*none')): t.decompose()
    for tr in s.find_all('tr'):
        cells=[c.get_text(' ',strip=True) for c in tr.find_all(['td','th'])]
        tr.replace_with(' | '.join(c for c in cells if c)+'\n')
    txt=s.get_text('\n')
    txt=re.sub(r'[ \t\xa0]+',' ',txt); txt=re.sub(r'\n\s*\n+','\n',txt)
    open(f[:-4]+'.txt','w').write(txt)
    print(f, len(txt))
