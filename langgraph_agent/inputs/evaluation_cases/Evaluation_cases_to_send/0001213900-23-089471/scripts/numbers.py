"""Company history and peer comparison for the 8 model inputs. Drops every row filed after 20231122."""
import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 30)
CUT = 20231122
CIK = 1841800
COLS = ["total_assets", "current_assets", "current_liabilities", "total_liabilities",
        "revenue", "net_income", "operating_income", "operating_cash_flow"]

df = pd.read_csv("shared/financials.csv")
df = df[df["filed"] <= CUT].copy()

co = df[df["cik"] == CIK].sort_values("filed")
print(co[["adsh", "form", "fp", "ddate", "filed"] + COLS].to_string())
sic = co["sic"].iloc[0]
print("sic", sic)
me = co[co["adsh"] == "0001213900-23-089471"].iloc[0]
print("missing:", [c for c in COLS if pd.isna(me[c])])

# ratios for the company over time
r = co.copy()
r["liab/assets"] = r.total_liabilities / r.total_assets
r["current_ratio"] = r.current_assets / r.current_liabilities
r["ni/assets"] = r.net_income / r.total_assets
r["ni/revenue"] = r.net_income / r.revenue
r["ocf/assets"] = r.operating_cash_flow / r.total_assets
print(r[["form", "ddate", "filed", "liab/assets", "current_ratio", "ni/assets", "ni/revenue", "ocf/assets"]].round(3).to_string())

# peers: same 2-digit sic, period ending within +-3 months of 20230930, not the company; latest report per peer
sic2 = str(int(sic))[:2]
df["sic2"] = df["sic"].fillna(0).astype(int).astype(str).str[:2]
dd = pd.to_datetime(df["ddate"].astype(str), format="%Y%m%d")
peers = df[(df.sic2 == sic2) & (df.cik != CIK) & (dd >= "2023-06-30") & (dd <= "2023-12-31")]
peers = peers.sort_values("filed").groupby("cik").tail(1).copy()
print("peers n =", len(peers))
peers["liab/assets"] = peers.total_liabilities / peers.total_assets
peers["current_ratio"] = peers.current_assets / peers.current_liabilities
peers["ni/assets"] = peers.net_income / peers.total_assets
peers["ni/revenue"] = peers.net_income / peers.revenue
peers["ocf/assets"] = peers.operating_cash_flow / peers.total_assets
peers["rev/assets"] = peers.revenue / peers.total_assets
mer = r[r.adsh == "0001213900-23-089471"].iloc[0].copy()
mer["rev/assets"] = mer.revenue / mer.total_assets
rows = []
for c in COLS + ["liab/assets", "current_ratio", "ni/assets", "ni/revenue", "ocf/assets", "rev/assets"]:
    s = peers[c].dropna()
    v = mer[c]
    pct = (s < v).mean() * 100 if pd.notna(v) else float("nan")
    rows.append([c, v, s.median(), len(s), round(pct)])
out = pd.DataFrame(rows, columns=["metric", "nogin", "peer_median", "n", "nogin_percentile"])
print(out.to_string())
peers.to_csv("final_cases-1/0001213900-23-089471/scripts/peers.csv", index=False)
