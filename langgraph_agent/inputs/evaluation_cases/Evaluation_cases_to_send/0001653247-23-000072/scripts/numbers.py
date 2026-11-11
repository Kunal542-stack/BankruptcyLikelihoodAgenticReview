"""Company history and peer comparison from shared/financials.csv (rows filed after 20231113 dropped)."""
import pandas as pd
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
CSV = "/Users/pramukhvenkateshkoushik/Desktop/Data_cap/investigator/shared/financials.csv"
df = pd.read_csv(CSV, dtype={"adsh": str})
df = df[df["filed"] <= 20231113]          # drop later rows immediately
COLS = ["total_assets", "current_assets", "current_liabilities", "total_liabilities",
        "revenue", "net_income", "operating_income", "operating_cash_flow"]
co = df[df["cik"] == 1653247].sort_values("filed")
print(co[["adsh", "form", "fp", "ddate", "filed"] + COLS].to_string())
me = co[co["adsh"] == "0001653247-23-000072"].iloc[0]
sic2 = str(int(me["sic"]))[:2]
print("sic", me["sic"], "missing:", [c for c in COLS if pd.isna(me[c])])

# peers: same 2-digit SIC, period end within +/- 6 months of 20230930, latest report each, excl. company
d = pd.to_datetime(df["ddate"].astype(str))
peers = df[(df["sic"].astype("Int64").astype(str).str[:2] == sic2) & (df["cik"] != 1653247)
           & (d.between("2023-04-01", "2023-12-31"))]
peers = peers.sort_values("filed").groupby("cik").tail(1)
print("peers:", len(peers))

def ratios(x):
    r = pd.DataFrame(index=x.index)
    for c in COLS:
        r[c] = x[c]
    r["liab/assets"] = x["total_liabilities"] / x["total_assets"]
    r["current_ratio"] = x["current_assets"] / x["current_liabilities"]
    r["ni/assets"] = x["net_income"] / x["total_assets"]
    r["ni/revenue"] = x["net_income"] / x["revenue"]
    r["oi/revenue"] = x["operating_income"] / x["revenue"]
    r["ocf/assets"] = x["operating_cash_flow"] / x["total_assets"]
    r["rev/assets"] = x["revenue"] / x["total_assets"]
    return r

pr = ratios(peers); mr = ratios(me.to_frame().T.astype({c: float for c in COLS}))
out = []
for c in pr.columns:
    v = float(mr[c].iloc[0]); s = pr[c].dropna()
    out.append([c, v, s.median(), (s < v).mean() * 100, len(s)])
print(pd.DataFrame(out, columns=["metric", "waitr", "peer_median", "pct_peers_below", "n"]).to_string())
co_r = ratios(co.set_index("filed"))
print(co_r[["liab/assets", "current_ratio", "ni/assets", "ni/revenue", "ocf/assets", "rev/assets"]].round(3).to_string())
peers.to_csv("/Users/pramukhvenkateshkoushik/Desktop/Data_cap/investigator/final_cases-1/0001653247-23-000072/scripts/peers.csv", index=False)
