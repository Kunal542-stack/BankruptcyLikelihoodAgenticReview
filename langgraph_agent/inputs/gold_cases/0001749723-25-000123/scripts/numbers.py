import pandas as pd
df=pd.read_csv('../../shared/financials.csv')
df=df[df.filed<=20250905]
c=df[df.cik==1749723].sort_values('filed')
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
cols=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
print(c[['adsh','form','fp','ddate','filed']+cols].assign(**{k:c[k]/1e6 for k in cols}).round(0).to_string())
print(c.sic.unique())
