import pandas as pd
p=pd.read_csv('final_cases/0001008654-23-000079/scripts/peers_used.csv')
t=dict(total_assets=743.6e6,current_assets=431.6e6,current_liabilities=1001.9e6,total_liabilities=1173.4e6,revenue=1304.0e6,net_income=-232.5e6,operating_income=23.6e6,operating_cash_flow=-34.0e6)
for k,v in t.items():
    s=p[k].dropna(); print(k,'n=',len(s),'peers below:',int((s<v).sum()),'median $m',round(s.median()/1e6,1),'tup/assets',round(v/743.6e6,3),'peer median /assets',round((s/p.loc[s.index,'total_assets']).median(),3))
print('peer dates',p.ddate.min(),p.ddate.max(), 'filed max',p.filed.max())
