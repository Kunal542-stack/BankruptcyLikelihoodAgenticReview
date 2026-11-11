import re, glob, csv
D='/Users/pramukhvenkateshkoushik/Desktop/Data_cap/investigator/final_cases-1/0001641172-25-023889/'
rep=open(D+'report.md').read()
norm=lambda s: re.sub(r'\s+',' ',s.replace('’',"'").replace('“','"').replace('”','"')).replace('$ ','$').strip()
texts={f.split('/')[-1][:20]:norm(open(f).read()) for f in glob.glob(D+'text/*.txt')}
quotes=re.findall(r"\"([^\"\n]{10,}?)\"",rep.replace('“','"').replace('”','"'))
ok=True
for q in quotes:
    hits=[k for k,t in texts.items() if norm(q) in t]
    print(('OK  ' if hits else 'MISS'),q[:70],hits[:2]); ok&=bool(hits)
# words
body=re.sub(r'^\[[^\]]+\]: \S+$','',rep,flags=re.M); body=re.sub(r'!\[[^\]]*\]\([^)]*\)','',body)
print('words',len(re.findall(r"[A-Za-z0-9$%.,'’\-–/]+",body)))
# links: every EDGAR link must be a filing dated <= 20250814
dates={r['adsh'].replace('-',''):r['date'] for r in csv.DictReader(open(D+'scripts/filings_list.csv'))}
for u in set(re.findall(r'https://www.sec.gov/\S+',rep)):
    a=u.split('/')[7]; d=dates.get(a); print('link',a,d,'OK' if d and d.replace('-','')<='20250814' else 'BAD'); ok&=bool(d and d.replace('-','')<='20250814')
used=set(re.findall(r'\[([^\]]+)\]',rep)); defs=set(re.findall(r'^\[([^\]]+)\]:',rep,flags=re.M))
print('undefined refs',[u for u in used if u not in defs and not u.startswith(('Revenue','Liquidity','Peers'))])
# numbers recomputed
nums={'cash':109692,'9M rev':6696901,'q3 rev':1285262,'q3 rev yago':4350570}
assert round(1285262/4350570-1,2)==-0.70; assert round(271245/1285262,2)==0.21
assert round(30001841/3364896,1)==8.9; assert round(1843164/25235127,2)==0.07
assert round(-16238313/3364896,1)==-4.8; assert 3364896-30001841==-26636945
assert 889000+2000000+286326+1175000+82427+361800+1000476+268035+827825==6890889
assert 2500000+3000000+2000000==7500000 and round(11244549/1e6,1)==11.2
assert round(9438530/6250106-1,2)==0.51 and round(4137485/1e6,1)==4.1
assert round(4230300/9)==470033 and round((4230300-3233491)/3)==332270
print('numbers OK; all quotes/links OK' if ok else 'PROBLEMS')
