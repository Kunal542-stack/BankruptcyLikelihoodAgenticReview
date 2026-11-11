import pandas as pd
df = pd.read_csv('../../shared/financials.csv')
df = df[df.filed <= 20250807]
c = df[df.cik==1001233].sort_values('ddate')
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
cols=['form','ddate','filed','total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
print(c[cols].tail(14).to_string())
print(c.sic.unique())
