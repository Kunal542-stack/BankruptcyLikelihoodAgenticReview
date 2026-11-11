import pandas as pd
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
df=pd.read_csv('../../shared/financials.csv')
df=df[df.filed<=20240814]
c=df[df.cik==1750153].sort_values('filed')
cols=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
print(c[['adsh','form','fp','ddate','filed']+cols].to_string())
print(c.sic.unique())
