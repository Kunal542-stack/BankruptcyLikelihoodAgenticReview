import pandas as pd
df=pd.read_csv('shared/financials.csv',dtype={'adsh':str})
df=df[df.filed<=20250312]
c=df[df.cik==1159167].sort_values('filed')
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
cols=['form','fp','ddate','filed','total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
print((c[cols].set_index(['form','fp','ddate','filed'])/1e6).round(1).tail(16))
print(c.sic.unique())
