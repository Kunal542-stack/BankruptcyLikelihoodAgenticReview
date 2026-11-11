"""Company history, peer comparison and ratios. Usage: python -I numbers.py <financials.csv>"""
import sys

import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 30)
CUT = 20231114
ADSH = "0001078207-23-000136"
COLS = ["total_assets", "current_assets", "current_liabilities", "total_liabilities",
        "revenue", "net_income", "operating_income", "operating_cash_flow"]

df = pd.read_csv(sys.argv[1])
df = df[df["filed"] <= CUT].copy()          # drop every row filed after the report date
co = df[df["cik"] == 1078207].sort_values("filed")
print("== company history ($m) ==")
show = co[["adsh", "form", "fp", "ddate", "filed"] + COLS].copy()
show[COLS] = (show[COLS] / 1e6).round(1)
print(show.to_string(index=False))

me = co[co["adsh"] == ADSH].iloc[0]
sic2 = str(int(me["sic"]))[:2]
print("\nsic", me["sic"], "sic2", sic2)

# missing values
print("missing:", [c for c in COLS if pd.isna(me[c])])

# ratios for the company over time
r = co.copy()
r["leverage_TL_TA"] = r.total_liabilities / r.total_assets
r["current_ratio"] = r.current_assets / r.current_liabilities
r["NI_TA"] = r.net_income / r.total_assets
r["NI_rev"] = r.net_income / r.revenue
r["OCF_TA"] = r.operating_cash_flow / r.total_assets
r["equity"] = (r.total_assets - r.total_liabilities) / 1e6
print("\n== company ratios ==")
print(r[["form", "fp", "ddate", "filed", "leverage_TL_TA", "current_ratio", "NI_TA", "NI_rev", "OCF_TA", "equity"]]
      .round(3).to_string(index=False))

# peers: same 2-digit sic, latest report per company with period end within +-120 days of 2023-09-30, not the company
peers = df[(df["sic"].fillna(0).astype(int).astype(str).str[:2] == sic2) & (df["cik"] != 1078207)].copy()
peers["dd"] = pd.to_datetime(peers["ddate"].astype(int).astype(str))
peers = peers[(peers.dd >= "2023-06-01") & (peers.dd <= "2023-12-31")]
peers = peers.sort_values("filed").groupby("cik").tail(1)
print("\npeers n =", len(peers))
for c in COLS:
    peers[c + "_pct"] = peers[c] / (peers.total_assets if c not in ("net_income", "operating_income", "operating_cash_flow") or c == "revenue" else peers.total_assets)
ranks = []
for c in COLS:
    v = peers[c].dropna()
    pct_rank = (v < me[c]).mean() * 100 if pd.notna(me[c]) else None
    ratio_me = me[c] / me.total_assets
    ratio_peers = (peers[c] / peers.total_assets).dropna()
    rk2 = (ratio_peers < ratio_me).mean() * 100
    ranks.append([c, me[c] / 1e6, v.median() / 1e6, round(pct_rank, 0), round(ratio_me, 3),
                  round(ratio_peers.median(), 3), round(rk2, 0), len(v)])
print(pd.DataFrame(ranks, columns=["item", "bfx_$m", "peer_median_$m", "bfx_pctile_$", "bfx_/TA",
                                   "peer_med_/TA", "bfx_pctile_/TA", "n"]).round(3).to_string(index=False))
# also net income / revenue
p_nim = (peers.net_income / peers.revenue).replace([float("inf"), -float("inf")], pd.NA).dropna()
print("NI/rev bfx", round(me.net_income / me.revenue, 3), "peer median", round(p_nim.median(), 3),
      "pctile", round((p_nim < me.net_income / me.revenue).mean() * 100))
p_lev = (peers.total_liabilities / peers.total_assets).dropna()
p_cr = (peers.current_assets / peers.current_liabilities).dropna()
print("leverage bfx", round(me.total_liabilities / me.total_assets, 3), "peer med", round(p_lev.median(), 3),
      "pctile", round((p_lev < me.total_liabilities / me.total_assets).mean() * 100))
print("current ratio bfx", round(me.current_assets / me.current_liabilities, 3), "peer med", round(p_cr.median(), 3),
      "pctile", round((p_cr < me.current_assets / me.current_liabilities).mean() * 100))
print("peer names sample:", peers.sort_values("total_assets", ascending=False)[["name", "sic"]].head(15).to_string(index=False))
peers.to_csv("scripts/peers_used.csv", index=False)
