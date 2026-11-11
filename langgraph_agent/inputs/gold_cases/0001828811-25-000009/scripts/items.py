import sys,re
for f in sys.argv[1:]:
    t=open(f).read(); t=re.sub(r'\s*\n\s*',' ',t)
    i=t.find('Item 1.01') if 'Item 1.01' in t else t.find('Item ')
    m=re.search(r'Item\s+\d\.\d\d',t[1500:]); s=1500+m.start() if m else 0
    e=t.find('Item 9.01',s); e=e if e>0 else s+3000
    print('########',f[:20]); print(t[s:min(e,s+2500)]); print()
