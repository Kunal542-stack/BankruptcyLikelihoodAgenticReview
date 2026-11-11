import pandas as pd
pd.set_option('display.width',250); pd.set_option('display.max_columns',30); pd.set_option('display.max_rows',200)
df=pd.read_csv('shared/financials.csv',dtype={'adsh':str})
df=df[df.filed<=20231013]
df['sic2']=(df.sic//100).astype('Int64')
p=df[(df.sic2==30)&(df.cik!=1008654)&(df.ddate>=20220601)&(df.ddate<=20230630)]
p=p.sort_values('filed').groupby('cik').tail(1)
num=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
print(len(p)); print((p[['name','form','ddate']+num].set_index('name').assign(**{k:p.set_index('name')[k]/1e6 for k in num})).round(1))
t=df[df.adsh=='0001008654-23-000079'].iloc[0]
r=pd.DataFrame({'tup':t[num].astype(float)/1e6,'peer_median':p[num].median()/1e6,
 'pct_rank':[ (p[k]<t[k]).mean() for k in num]})
print(r.round(2))
def ratios(x):
    return pd.DataFrame({'liab/assets':x.total_liabilities/x.total_assets,'cur_ratio':x.current_assets/x.current_liabilities,
     'ni/assets':x.net_income/x.total_assets,'ni/rev':x.net_income/x.revenue,'oi/rev':x.operating_income/x.revenue,'ocf/assets':x.operating_cash_flow/x.total_assets,'rev/assets':x.revenue/x.total_assets})
pr=ratios(p); tr=ratios(df[df.adsh=='0001008654-23-000079']).iloc[0]
print(pd.DataFrame({'tup':tr,'peer_median':pr.median(),'pct_rank_below':[(pr[k]<tr[k]).mean() for k in pr]}).round(3))
p.to_csv('final_cases/0001008654-23-000079/scripts/peers_used.csv',index=False)
