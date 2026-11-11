import pandas as pd
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
df=pd.read_csv('shared/financials.csv',dtype={'adsh':str})
df=df[df.filed<=20231013]
c=df[df.cik==1008654].sort_values('filed')
cols=['form','fp','ddate','filed','total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
print((c[cols].set_index(['form','fp','ddate','filed'])/1e6).round(1))
print(c.sic.unique())
