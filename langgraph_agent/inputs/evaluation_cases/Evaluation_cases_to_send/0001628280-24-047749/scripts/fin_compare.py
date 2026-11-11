import pandas as pd
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
CUT = 20241114
df = pd.read_csv("shared/financials.csv")
df = df[df["filed"] <= CUT].copy()          # drop anything filed after the report date
cols = ["total_assets","current_assets","current_liabilities","total_liabilities","revenue","net_income","operating_income","operating_cash_flow"]
me = df[df.cik == 1750153].sort_values("filed")
print(me[["adsh","form","fp","ddate","filed"]+cols].to_string())
row = me[me.adsh == "0001628280-24-047749"].iloc[0]
sic2 = str(int(row.sic))[:2]; print("sic", row.sic)
peers = df[(df.sic.astype("Int64").astype(str).str[:2] == sic2) & (df.cik != 1750153)]
peers = peers[(peers.ddate >= 20240630) & (peers.ddate <= 20241231)].sort_values("filed").groupby("cik").tail(1)
print("peers n =", len(peers))
def pct(col, val, base=None):
    s = peers[col] if base is None else peers[col] / peers[base]
    s = s.replace([float("inf"), -float("inf")], pd.NA).dropna()
    return (s < val).mean() * 100, s.median(), len(s)
for c in cols:
    p, m, n = pct(c, row[c]); print(f"{c:22s} {row[c]/1e6:10.1f}M  pctile {p:5.1f}  peer median {m/1e6:10.1f}M n={n}")
for c in cols[1:]:
    p, m, n = pct(c, row[c]/row.total_assets, "total_assets"); print(f"{c+'/TA':26s} {row[c]/row.total_assets:8.3f} pctile {p:5.1f} peer median {m:8.3f} n={n}")
for c in ["net_income","operating_income","operating_cash_flow"]:
    p, m, n = pct(c, row[c]/row.revenue, "revenue"); print(f"{c+'/rev':26s} {row[c]/row.revenue:8.2f} pctile {p:5.1f} peer median {m:8.3f} n={n}")
print("leverage TL/TA", row.total_liabilities/row.total_assets, "current ratio", row.current_assets/row.current_liabilities,
      "equity", (row.total_assets-row.total_liabilities)/1e6)
pl = peers.total_liabilities/peers.total_assets; print("peer TL/TA median", pl.median(), "pctile", (pl < row.total_liabilities/row.total_assets).mean()*100)
pc = peers.current_assets/peers.current_liabilities; print("peer CR median", pc.median(), "pctile", (pc < row.current_assets/row.current_liabilities).mean()*100)
print(peers.sort_values("total_assets")[["name","ddate","total_assets","revenue","net_income"]].head(15).to_string())
