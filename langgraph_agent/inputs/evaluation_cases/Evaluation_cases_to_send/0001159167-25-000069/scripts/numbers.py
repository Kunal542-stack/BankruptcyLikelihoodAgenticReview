"""Company history, peer comparison and ratios from shared/financials.csv (rows filed <= 20250807 only)."""
import pandas as pd
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)

CSV = "/Users/pramukhvenkateshkoushik/Desktop/Data_cap/investigator/shared/financials.csv"
CUTOFF = 20250807
CIK = 1159167
COLS = ["total_assets", "current_assets", "current_liabilities", "total_liabilities",
        "revenue", "net_income", "operating_income", "operating_cash_flow"]

df = pd.read_csv(CSV)
df = df[df["filed"] <= CUTOFF].copy()          # drop everything filed after the report date
co = df[df["cik"] == CIK].sort_values("filed")
print(co[["adsh", "form", "fp", "ddate", "filed"] + COLS].to_string())

me = co[co["adsh"] == "0001159167-25-000069"].iloc[0]
print("\nSIC", me["sic"])
sic2 = str(int(me["sic"]))[:2]

# peers: same 2-digit SIC, report period within +-6 months of 20250630, latest report per company, not iRobot
df["sic2"] = df["sic"].dropna().astype(int).astype(str).str[:2]
dd = pd.to_datetime(df["ddate"].astype(str))
peers = df[(df["sic2"] == sic2) & (df["cik"] != CIK) &
           (dd.between("2025-01-01", "2025-06-30"))]
peers = peers.sort_values("ddate").groupby("cik").tail(1)
print("peers:", len(peers))

def ratios(x):
    r = {}
    r["liab/assets"] = x["total_liabilities"] / x["total_assets"]
    r["current_ratio"] = x["current_assets"] / x["current_liabilities"]
    r["NI/assets"] = x["net_income"] / x["total_assets"]
    r["NI/revenue"] = x["net_income"] / x["revenue"]
    r["OI/revenue"] = x["operating_income"] / x["revenue"]
    r["OCF/assets"] = x["operating_cash_flow"] / x["total_assets"]
    r["rev/assets"] = x["revenue"] / x["total_assets"]
    return pd.Series(r) if isinstance(x, pd.Series) and x.ndim == 1 else pd.DataFrame(r)

rows = []
for c in COLS:
    v = me[c]; s = peers[c].dropna()
    rows.append([c, v, s.median(), (s < v).mean() * 100, s.notna().sum()])
pr = ratios(peers); mr = ratios(me)
for c in pr.columns:
    v = mr[c]; s = pr[c].replace([float("inf"), -float("inf")], pd.NA).dropna()
    rows.append([c, v, s.median(), (s < v).mean() * 100, len(s)])
out = pd.DataFrame(rows, columns=["metric", "iRobot", "peer_median", "pct_peers_below", "n"])
print(out.to_string())

print("\nCompany ratios over time")
r = ratios(co.set_index("filed")[COLS]); print(r.round(3).to_string())
co.to_csv("scripts/company_rows.csv", index=False)
peers.to_csv("scripts/peer_rows.csv", index=False)
