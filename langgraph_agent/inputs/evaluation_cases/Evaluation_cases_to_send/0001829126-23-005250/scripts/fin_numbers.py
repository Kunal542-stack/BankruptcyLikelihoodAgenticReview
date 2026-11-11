"""Company history and peer comparison from shared/financials.csv, as of 20230809."""
import pandas as pd
CUT = 20230809
df = pd.read_csv("shared/financials.csv")
df = df[df["filed"] <= CUT]          # drop everything filed after the report date
cols = ["total_assets", "current_assets", "current_liabilities", "total_liabilities", "revenue",
        "net_income", "operating_income", "operating_cash_flow"]
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
co = df[df.cik == 1823882].sort_values("filed")
print(co[["adsh", "form", "fp", "ddate", "filed", "sic"] + cols].to_string())
me = co[co.adsh == "0001829126-23-005250"].iloc[0]
sic2 = str(int(me.sic))[:2]
print("sic", me.sic, "sic2", sic2)
peers = df[(df.sic.fillna(0).astype(int).astype(str).str[:2] == sic2) & (df.cik != 1823882)]
peers = peers[(peers.ddate >= 20230101) & (peers.ddate <= 20231231)]
peers = peers.sort_values("filed").groupby("cik").tail(1)   # latest report per peer, ddate in 2023
print("peers", len(peers))
r = {}
for c in cols:
    s = peers[c].dropna()
    r[c] = dict(value=me[c], peer_median=s.median(), pct_rank=(s < me[c]).mean() * 100, n=len(s))
for c in cols:
    if c != "total_assets":
        s = (peers[c] / peers.total_assets).replace([float("inf"), -float("inf")], pd.NA).dropna()
        r[c]["share_of_assets"] = me[c] / me.total_assets
        r[c]["peer_median_share"] = s.median()
        r[c]["pct_rank_share"] = (s < me[c] / me.total_assets).mean() * 100
print(pd.DataFrame(r).T.to_string())
# ratios
for _, x in co.iterrows():
    print(x.form, x.ddate, "lev(TL/TA)=%.2f cur=%.2f equity=%.1fM NI/rev=%.2f" % (
        x.total_liabilities / x.total_assets, x.current_assets / x.current_liabilities,
        (x.total_assets - x.total_liabilities) / 1e6, x.net_income / x.revenue))
pl = peers.assign(lev=peers.total_liabilities / peers.total_assets, cr=peers.current_assets / peers.current_liabilities,
                  nm=peers.net_income / peers.revenue)
print("peer median lev %.2f, cr %.2f, NI/rev %.2f" % (pl.lev.median(), pl.cr.median(), pl.nm.median()))
print("share of peers with lev>%.2f: %.0f%%" % (me.total_liabilities / me.total_assets,
      (pl.lev > me.total_liabilities / me.total_assets).mean() * 100))
peers.to_csv("final_cases-1/0001829126-23-005250/scripts/peers.csv", index=False)
