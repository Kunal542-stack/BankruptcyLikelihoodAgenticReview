import re, glob, os, pandas as pd
B='final_cases/0001213900-23-087187/'
def norm(s): return re.sub(r'\s+',' ',s.replace('\xa0',' ')).strip()
T={os.path.basename(f)[:20]:norm(open(f).read()) for f in glob.glob(B+'filings/text/*.txt')}
Q=[('0001213900-23-087187',"its cash position may not be sufficient to support its daily operations."),
('0001213900-23-087187',"As of September 30, 2023, the Company is in default on $2,265,447 in principal on senior secured notes from The July 2022 Convertible Note Offering."),
('0001213900-23-087187',"the lender may require immediate payment of all amounts owed under the Loan or file suit and obtain judgment."),
('0001213900-23-087187',"This increase is primarily attributable to a reduction in cash and an increase in accounts payable and accrued liabilities."),
('0001213900-23-030833',"raise substantial doubt about its ability to continue as a going concern"),
('0001213900-23-087187',"These factors raise substantial doubt about the Company’s ability to continue as a going concern for a period of one year from the issuance of these financial statements."),
('0001213900-22-054149',"has determined to delist the Company’s common stock from the Exchange"),
('0001213900-23-082227',"extend the maturity dates for the Debentures, which have a cumulative remaining balance of $2,485,000,"),
('0001213900-23-087187',"were predominantly financed by proceeds from the continued exercise of warrants, the issuance of both convertible notes and promissory notes, and the sale of common stock."),
('0001213900-23-087187',"in default")]
for a,q in Q: print('OK ' if norm(q) in T[a] else 'MISSING',a,q[:60])
# dates
fl=open('/dev/stdin').read() if False else None
d=pd.read_csv('shared/financials.csv',dtype={'adsh':str}); d=d[d.cik==1357671]
used=[os.path.basename(f)[:20] for f in glob.glob(B+'filings/*.htm')]
print('csv filed dates for used adsh:',sorted(d[d.adsh.isin(used)].filed.tolist()))
r=open(B+'report.md').read()
print('words',len(re.sub(r'[|\-#*!\[\]()]',' ',r).split()))
# numbers
print('loss/TA',31033996/2892000,'cashloss chg',(10238822/16971249-1)*100,'notes total',1708863+6096192,'NI attrib check',23275497*4/3)
