import re,glob,os,sys
B=sys.argv[1]; s=open(B+'/report.md').read()
txt={os.path.basename(f):open(f).read() for f in glob.glob(B+'/filings/*.txt')}
norm=lambda x:re.sub(r'\s+',' ',x.replace('’',"'").replace('“','"').replace('”','"'))
alltxt={k:norm(v) for k,v in txt.items()}
quotes=re.findall(r'"([^"]{25,})"',s)
for q in quotes:
    hit=[k for k,v in alltxt.items() if norm(q) in v]
    print('OK ' if hit else 'MISSING', q[:70], hit[:1])
# links
links=re.findall(r'\]\(([^)]+)\)',s)
for l in links:
    if l.startswith('http'):
        m=re.search(r'/data/1159167/(\d{18})/',l); a=m.group(1); a=f'{a[:10]}-{a[10:12]}-{a[12:]}'
        f=[k for k in txt if k.startswith(a)]
        print('link',a,'saved' if f else 'NOT SAVED')
    else: print('local',l, os.path.exists(os.path.join(B,l)))
# filing dates of all saved docs
import csv
rows={r['adsh']:r['date'] for r in csv.DictReader(open(B+'/scripts/filings_list.csv'))}
rows.update({'0001159167-25-000011':'2025-03-12','0001193125-25-052480':'2025-03-12'})
for k in txt: a=k[:20]; print(a, rows.get(a), 'OK' if rows.get(a,'9999')<= '2025-03-12' else 'LATE')
body=re.sub(r'!\[.*?\]\(.*?\)|\]\(.*?\)','',s); print('words',len(body.split()))
