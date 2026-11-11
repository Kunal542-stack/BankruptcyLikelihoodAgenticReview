import re,glob,pandas as pd
norm=lambda s:re.sub(r'\s+',' ',s).strip()
txt=norm(' '.join(open(f).read() for f in glob.glob('filings/*.txt')))
rep=open('report.md').read()
quotes=re.findall(r'[*"]\*?"([^"]{12,})"',rep)+re.findall(r'\*"([^*]+)"\*',rep)
for q in sorted(set(quotes)):
    print('OK ' if norm(q) in txt else 'MISSING', q[:90])
for extra in ['to be tested monthly','may assign limited or no value']:
    print('OK ' if extra in txt else 'MISSING',extra)
# numbers
df=pd.read_csv('../../shared/financials.csv',dtype={'adsh':str}); df=df[df.filed<=20250331]
me=df[df.adsh=='0001828811-25-000009'].iloc[0]
assert round(me.net_income/1e6,1)==-137.7 and round(me.operating_cash_flow/1e6,1)==-106.4 and round(me.revenue/1e6,1)==28.0
assert abs(me.net_income/me.revenue+4.92)<0.01
for n in ['22.6','9.3','17.3','89.7','43.0','105.1','58.9','54.0','102.5','117.9','363.1','173.0','16.4','58.6','10.0']: assert n in txt, n
print('numbers OK')
# dates: filings used
fl=open('/dev/stdin').read() if False else None
print('words',len(re.findall(r'\S+',rep)))
