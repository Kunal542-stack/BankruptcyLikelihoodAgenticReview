import pandas as pd
df = pd.read_csv("../../shared/financials.csv")
df = df[df.filed <= 20230810]
co = df[df.cik == 1113148].sort_values("filed")
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
print(co.drop(columns=["name","cik","adsh"]).to_string())
