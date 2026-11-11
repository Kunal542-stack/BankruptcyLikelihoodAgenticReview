import sys,os,re,glob
from bs4 import BeautifulSoup
d=sys.argv[1]; out=os.path.join(d,'text'); os.makedirs(out,exist_ok=True)
for f in glob.glob(os.path.join(d,'*.htm')):
    s=BeautifulSoup(open(f,encoding='utf-8',errors='ignore').read(),'lxml')
    for t in s(['script','style']): t.decompose()
    for t in s.find_all(lambda x: x.name and x.name.lower() in ('ix:header',)): t.decompose()
    for div in s.find_all(style=re.compile(r'display:\s*none')): div.decompose()
    for tr in s.find_all('tr'):
        cells=[c.get_text(' ',strip=True) for c in tr.find_all(['td','th'])]
        cells=[c for c in cells if c]
        tr.replace_with(s.new_string('\n'+' | '.join(cells)+'\n'))
    txt=s.get_text('\n')
    txt=re.sub(r'[ \t\xa0]+',' ',txt); txt=re.sub(r'\n\s*\n+','\n',txt)
    open(os.path.join(out,os.path.basename(f).replace('.htm','.txt')),'w').write(txt)
    print(f, len(txt))
