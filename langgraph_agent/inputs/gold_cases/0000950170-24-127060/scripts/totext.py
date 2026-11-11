import sys,glob,os,re
from bs4 import BeautifulSoup
d=sys.argv[1]
for f in glob.glob(d+'/*.htm'):
    out=f[:-4]+'.txt'
    soup=BeautifulSoup(open(f,encoding='utf-8',errors='ignore').read(),'html.parser')
    for t in soup.find_all(['ix:header','script','style']): t.decompose()
    for div in soup.find_all(style=re.compile(r'display:\s*none')): div.decompose()
    for tr in soup.find_all('tr'):
        cells=[c.get_text(' ',strip=True) for c in tr.find_all(['td','th'])]
        tr.replace_with(soup.new_string('\n'+' | '.join(x for x in cells if x)+'\n'))
    txt=soup.get_text('\n')
    txt=re.sub(r'[ \xa0\t]+',' ',txt); txt=re.sub(r'\n\s*\n+','\n',txt)
    open(out,'w').write(txt)
    print(out,len(txt))
