"""Company history and peer comparison from shared/financials.csv, as of 20231108."""
import pandas as pd
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)

CUT = 20231108
df = pd.read_csv("../../shared/financials.csv")
df = df[df["filed"] <= CUT]  # drop everything filed after the report date
COLS = ["total_assets", "current_assets", "current_liabilities", "total_liabilities",
        "revenue", "net_income", "operating_income", "operating_cash_flow"]

co = df[df["cik"] == 1823882].sort_values("filed")
print(co[["adsh", "form", "fp", "ddate", "filed"] + COLS].to_string())
r = co[co["adsh"] == "0001829126-23-007197"].iloc[0]
sic2 = str(int(r["sic"]))[:2]
print("sic", r["sic"], "sic2", sic2)

# peers: same 2-digit SIC, latest report per company with period end within +-6 months of 20230930
peers = df[(df["sic"].fillna(0).astype(int).astype(str).str[:2] == sic2) & (df["cik"] != 1823882)]
peers = peers[(peers["ddate"] >= 20230331) & (peers["ddate"] <= 20231231)]
peers = peers.sort_values("filed").groupby("cik").tail(1)
print("peers:", len(peers))

def rank(col, val, base):
    s = base[col].dropna()
    return f"{(s < val).mean()*100:.0f}th pct (n={len(s)}, median={s.median():,.0f})"

out = []
for c in COLS:
    out.append([c, r[c], rank(c, r[c], peers)])
for c in ["net_income", "operating_income", "operating_cash_flow", "total_liabilities", "current_liabilities"]:
    pr = peers.assign(x=peers[c] / peers["total_assets"])
    out.append([c + "/assets", r[c] / r["total_assets"], rank("x", r[c] / r["total_assets"], pr)])
for c in ["net_income", "operating_income", "operating_cash_flow"]:
    pr = peers[peers["revenue"] > 0].assign(x=lambda p: p[c] / p["revenue"])
    out.append([c + "/revenue", r[c] / r["revenue"], rank("x", r[c] / r["revenue"], pr)])
pr = peers.assign(x=peers["current_assets"] / peers["current_liabilities"])
out.append(["current_ratio", r["current_assets"] / r["current_liabilities"], rank("x", r["current_assets"] / r["current_liabilities"], pr)])
print(pd.DataFrame(out, columns=["metric", "value", "peer rank"]).to_string())
peers.to_csv("scripts/peers.csv", index=False)
