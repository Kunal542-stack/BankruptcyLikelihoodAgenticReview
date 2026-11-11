import sys,glob,os,re
from bs4 import BeautifulSoup
d=sys.argv[1]
for f in glob.glob(os.path.join(d,'*.htm')):
    soup=BeautifulSoup(open(f,'rb').read(),'html.parser')
    for t in soup.find_all(['script','style']): t.decompose()
    for t in soup.find_all(lambda x: x.name and x.name.lower() in ('ix:header',)): t.decompose()
    for div in soup.find_all(style=re.compile(r'display:\s*none')): div.decompose()
    for tr in soup.find_all('tr'):
        cells=[c.get_text(' ',strip=True) for c in tr.find_all(['td','th'])]
        tr.replace_with(' | '.join(c for c in cells if c)+'\n')
    txt=soup.get_text('\n')
    txt=re.sub(r'\xa0',' ',txt); txt=re.sub(r'[ \t]+',' ',txt); txt=re.sub(r'\n\s*\n+','\n',txt)
    open(f[:-4]+'.txt','w').write(txt)
    print(f, len(txt))
