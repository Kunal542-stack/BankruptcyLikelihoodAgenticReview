import glob,re,os,pandas as pd
C='final_cases/0001083301-25-000061/'
def norm(s):
    s=s.replace('’',"'").replace('“','"').replace('”','"')
    s=re.sub(r'\s+',' ',s); s=re.sub(r'\$ (?=[\d(])','$',s); s=s.replace('( ','(').replace(' )',')')
    return s
T={os.path.basename(f).split('_')[0]:norm(open(f).read()) for f in glob.glob(C+'filings/text/*.txt')+glob.glob(C+'filings/older/text/*.txt')}
rep=norm(open(C+'report.md').read())
Q=[('0001083301-25-000061','increased stock-based compensation of $28.2 million'),
 ('0001083301-25-000061','As of June 30, 2025, the Company had cash and cash equivalents of $90.0 million, a working capital balance of $(52.2) million'),
 ('0001083301-25-000061','The 2030 Convertible Notes mature on February 1, 2030'),
 ('0001083301-25-000061','ITEM 3. Defaults Upon Senior Securities. None'),
 ('0001083301-25-000061',"the Company received $90.0 million in prepaid rent from the Company's HPC customer ahead of lease commencement"),
 ('0001083301-25-000061','the remaining capacity of the ATM Program to offer and sell shares of Common Stock is $200.0 million'),
 ('0001083301-25-000061','In July 2025, the CB-1 Earnout Milestone was achieved'),
 ('0001083301-25-000061','remains on track to deliver 72.5 MW of HPC colocation capacity'),
 ('0001558370-23-005301',"there is no longer substantial doubt about the Company's ability to continue as a going concern"),
 ('0001083301-24-000112','paid off in full'),
 ('0001083301-25-000018','present fairly, in all material respects')]
ok=True
for a,q in Q:
    f=q in T[a]; r=(q.split('ITEM 3. ')[-1].split(' None')[0] if 'ITEM 3' in q else q) in rep
    print('OK ' if f else 'MISSING','| in report' if r else '| (not quoted in report)',a,q[:70]); ok&=f
q10=T['0001083301-25-000061']; q1=T['0001083301-25-000038']
for src,s in [(q10,'Net loss | $ | (18,370) | $ | (10,876) | $ | (79,788)'),(q10,'Stock-based compensation expense | 39,978'),(q10,'Depreciation | 34,360'),
 (q10,'Purchase of and deposits on plant and equipment | (213,629)'),(q10,'Cash, cash equivalents and restricted cash at end of period | $ | 91,418'),
 (q10,'Total current liabilities | 151,304'),(q10,'Current portion of deferred rent liability | 47,716'),(q10,'Contingent consideration liabilities | 30,000'),
 (q10,'Purchase of treasury stock | (33,292)'),(q10,'Payments of tax withholding related to net share settlements of stock-based compensation awards | (18,936)'),
 (q10,'Proceeds from sale of digital currency | 82,382'),(q10,'Net cash provided by operating activities | 1,677'),(q10,'Total stockholders\' equity | 174,332'),
 (q1,'Stock-based compensation expense | 38,674'),(q1,'Net cash provided by operating activities | 56,487'),(q1,'Purchase of and deposits on plant and equipment | (93,687)'),
 (q1,'Cash and cash equivalents at end of period | $ | 218,162'),(q1,'Net loss | $ | (61,418)'),(q1,'Proceeds from sale of digital currency | 32,623'),
 (T['0001083301-25-000018'],'Net loss | $ | (72,418) | $ | (73,421)')]:
    print('OK ' if s in src else 'MISSING', s); ok&=s in src
print('Q2 NI ann',(-79788+61418)*4/1e3,'| Q2 capex',(213629-93687)/1e3,'| Q2 econ OCF',(1677-56487+82382-32623)/1e3,
 '| Q2 burn/mo',round((1677-56487+82382-32623-(213629-93687))/3/1e3,1),'| months',round(89993/((213629-93687)-(1677-56487+82382-32623))*3,1))
print('CR',round(99115/151304,2),'CR ex',round(99115/(151304-47716-30000),2),'lev',round(695076/869408,2),'coupon',500000*0.0275/2/1e3)
df=pd.read_csv('shared/financials.csv'); df=df[df.filed<=20250808]; print('max filed in data used',df.filed.max())
fl=os.popen('/opt/anaconda3/bin/python sec_tools.py filings 1083301 20250808').read()
for a in T:
    l=[x for x in fl.splitlines() if a in x]; d=l[0].split(',')[0] if l else ('2025-08-08 target' if a.endswith('25-000061') else 'NOT LISTED')
    print(a,d, 'LATE!' if d.replace('-','')[:8]>'20250808' else '')
w=len(re.findall(r'\S+',open(C+'report.md').read())); print('words',w)
print('ALL OK' if ok and w<=1200 else 'PROBLEM')
