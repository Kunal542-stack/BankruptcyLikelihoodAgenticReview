"""Company history and peer comparison from shared/financials.csv, as of 20250807."""
import pandas as pd

CUT, CIK, ADSH = 20250807, 1001233, "0001628280-25-038860"
df = pd.read_csv("shared/financials.csv")
df = df[df["filed"] <= CUT]  # drop everything filed after the report date
cols = ["total_assets", "current_assets", "current_liabilities", "total_liabilities",
        "revenue", "net_income", "operating_income", "operating_cash_flow"]

co = df[df.cik == CIK].sort_values("filed")
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 30)
print(co[["adsh", "form", "fp", "ddate", "filed"] + cols].to_string())
me = co[co.adsh == ADSH].iloc[0]
print("\nmissing:", [c for c in cols if pd.isna(me[c])])

sic2 = int(str(int(me.sic))[:2])
print("sic", me.sic, "sic2", sic2)
df["sic2"] = (df.sic // 100).astype("Int64")
import sys
MODE = sys.argv[1] if len(sys.argv) > 1 else "sic2"
peers = df[((df.sic2 == sic2) if MODE == "sic2" else (df.sic == me.sic)) & (df.cik != CIK)]
print("peer mode", MODE)
# peers at about the same date: period end within +-92 days, latest report per company
d = pd.to_datetime(peers.ddate.astype(str))
me_d = pd.to_datetime(str(me.ddate))
peers = peers[(d - me_d).abs().dt.days <= 92].sort_values("filed").groupby("cik").tail(1)
print("peers:", len(peers))


def dv(a, b):
    return a / b if pd.notna(a) and pd.notna(b) and b != 0 else float("nan")


def ratios(r):
    return pd.Series({
        "ni_to_assets": dv(r.net_income, r.total_assets),
        "ocf_to_assets": dv(r.operating_cash_flow, r.total_assets),
        "liab_to_assets": dv(r.total_liabilities, r.total_assets),
        "current_ratio": dv(r.current_assets, r.current_liabilities),
        "ni_to_revenue": dv(r.net_income, r.revenue),
    })


pr = peers.apply(ratios, axis=1)
mr = ratios(me)
out = []
for c in cols:
    s = peers[c].dropna()
    out.append([c, me[c], s.median(), (s < me[c]).mean() * 100, len(s)])
for c in pr.columns:
    s = pr[c].dropna()
    s = s[abs(s) < 1e6]
    out.append([c, mr[c], s.median(), (s < mr[c]).mean() * 100, len(s)])
print(pd.DataFrame(out, columns=["item", "sangamo", "peer_median", "pct_peers_below", "n"]).to_string())

peers.to_csv(f"final_cases-1/0001628280-25-038860/scripts/peers_{MODE}.csv", index=False)
co.to_csv("final_cases-1/0001628280-25-038860/scripts/company.csv", index=False)
