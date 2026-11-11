import re,glob,os,subprocess
B='final_cases/0000950170-24-127060/'
norm=lambda s: re.sub(r'\s+',' ',s.replace('’',"'").replace('“','"').replace('”','"')).strip()
texts={os.path.basename(f).split('_')[0]:norm(open(f).read()) for f in glob.glob(B+'filings/*.txt')}
rep=open(B+'report.md').read()
quotes=[q for q in re.findall(r'"([^"\n]+)"',rep)]
src={'in its sole discretion':'0001193125-24-198866','aggregate gross sales':'0001193125-24-172679','raise substantial doubt':'0000950170-24-039423','None.':'0000950170-24-127060'}
for q in quotes:
    a=next((v for k,v in src.items() if q.startswith(k)),'0000950170-24-127060')
    print('OK ' if norm(q) in texts[a] else 'MISSING', a, q[:70])
lst=subprocess.run(['/opt/anaconda3/bin/python','sec_tools.py','filings','1580063','20241114'],capture_output=True,text=True).stdout
dates={l.split(',')[2]:l.split(',')[0] for l in lst.splitlines()[1:] if l.count(',')>=2}
for a in sorted(texts): print(a, dates.get(a,'(target, filed 2024-11-14)'))
print('max listed date',max(dates.values()),'| words',len(rep.split()))
