import sys,glob,os,re
from bs4 import BeautifulSoup
src,dst=sys.argv[1],sys.argv[2]; os.makedirs(dst,exist_ok=True)
for f in glob.glob(os.path.join(src,'*.htm')):
    s=BeautifulSoup(open(f,encoding='utf-8',errors='ignore').read(),'html.parser')
    for t in s.find_all(['ix:header','script','style']): t.decompose()
    for d in s.find_all(style=re.compile(r'display:\s*none')): d.decompose()
    for tr in s.find_all('tr'):
        cells=[c.get_text(' ',strip=True) for c in tr.find_all(['td','th'])]
        tr.replace_with(' | '.join(x for x in cells if x)+'\n')
    txt=s.get_text('\n')
    txt=re.sub(r'[ \t\xa0]+',' ',txt); txt=re.sub(r'\n\s*\n+','\n',txt)
    open(os.path.join(dst,os.path.basename(f)[:-4]+'.txt'),'w').write(txt)
