import pandas as pd, numpy as np
df = pd.read_csv('shared/financials.csv')
df = df[df.filed <= 20230809]
co = df[df.cik==1078207].sort_values('filed')
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
cols=['form','fp','ddate','filed','total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
print((co[cols].tail(14).set_index(['form','fp','ddate','filed'])/1e6).round(1))
