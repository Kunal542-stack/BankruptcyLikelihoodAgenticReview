import pandas as pd, numpy as np
df = pd.read_csv("../../shared/financials.csv")
df = df[df.filed <= 20230810]
cols = ["total_assets","current_assets","current_liabilities","total_liabilities","revenue","net_income","operating_income","operating_cash_flow"]
me = df[df.adsh == "0001113148-23-000009"].iloc[0]
p = df[(df.sic // 100 == 28) & (df.cik != 1113148) & (df.ddate == 20230630)]
p = p.sort_values("filed").groupby("cik").tail(1)
print("peers:", len(p), " pharma 2834 among them:", (p.sic == 2834).sum())
rows = []
for c in cols:
    s = p[c].dropna()
    rows.append([c, me[c], s.median(), (s < me[c]).mean() * 100, p[c].isna().sum()])
print(pd.DataFrame(rows, columns=["item", "INFI", "peer_median", "pct_rank_INFI", "peers_missing"]).to_string())
# ratios
def r(d):
    o = pd.DataFrame(index=d.index)
    o["liab_to_assets"] = d.total_liabilities / d.total_assets
    o["current_ratio"] = d.current_assets / d.current_liabilities
    o["ni_to_assets"] = d.net_income / d.total_assets
    o["ocf_to_assets"] = d.operating_cash_flow / d.total_assets
    o["ni_to_rev"] = d.net_income / d.revenue
    return o
rp = r(p); rm = r(me.to_frame().T.astype({c: float for c in cols}))
for c in rp:
    v = float(rm[c].iloc[0]); s = rp[c].replace([np.inf, -np.inf], np.nan).dropna()
    print(f"{c:16s} INFI {v:8.2f}  peer median {s.median():8.2f}  INFI pct rank {(s < v).mean()*100:5.1f}")
print("share of peers with liabilities > assets:", (rp.liab_to_assets > 1).mean())
print("peers with TA < 30M:", (p.total_assets < 30e6).sum())
small = p[(p.total_assets < 50e6)]
print("small peers (<50M TA) n=", len(small), "median liab/assets", r(small).liab_to_assets.median(), "median NI/TA", r(small).ni_to_assets.median())
