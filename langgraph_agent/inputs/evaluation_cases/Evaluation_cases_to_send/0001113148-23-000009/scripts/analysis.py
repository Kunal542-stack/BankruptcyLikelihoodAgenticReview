import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
df = pd.read_csv("../../shared/financials.csv"); df = df[df.filed <= 20230810]
me = df[df.adsh == "0001113148-23-000009"].iloc[0]
# figures from filings ($k): Q2-2023 10-Q, Q2-2022 10-Q, FY2022 10-K
cash = 17746; ocf_h1 = -20583; ocf_q1 = -12576; ocf_q2 = ocf_h1 - ocf_q1
cl = 12064; royalty_cur = 1252; royalty_nc = 46574; tl = 58638; ta = 21232; ca = 19908
print("Q2 OCF", ocf_q2, " months cash (Q2 burn)", round(cash / (-ocf_q2 / 3), 1), " months (H1 avg)", round(cash / (-ocf_h1 / 6), 1))
print("after 3.4M severance, months at Q2 burn", round((cash - 3400) / (-ocf_q2 / 3), 1))
print("TL/TA", round(tl / ta, 2), " royalty liab total", royalty_cur + royalty_nc, " share of TL", round((royalty_cur + royalty_nc) / tl, 3))
other = tl - royalty_cur - royalty_nc; print("other liabilities", other, " /TA", round(other / ta, 2))
print("current ratio", round(ca / cl, 2), " cash/(CL ex royalty)", round(cash / (cl - royalty_cur), 2), " cash - CL ex royalty", cash - (cl - royalty_cur))
print("equity", ta - tl)
adj = {"FY2021": (-45262, 480, 2695, -984, 180, 59), "FY2022": (-44369, 458, 3621, -1373, 180, 91),
       "H1 2022": (-24422, 241, 1682, -708, 90, 66), "H1 2023": (-21001, 211, 2630, -695, 90, -220)}
for k, v in adj.items():
    print(k, "net loss", v[0], " cash-flow non-cash items", sum(v[1:]), " adjusted loss", sum(v), " non-cash share", round(sum(v[1:]) / -v[0], 3))
prior = dict(total_assets=61857e3, current_assets=59610e3, current_liabilities=14339e3, total_liabilities=62964e3,
             revenue=1338e3*2, net_income=-24422e3*2, operating_income=-24425e3*2, operating_cash_flow=-24130e3*2)
for k, v in prior.items(): print(f"{k:20s} now {me[k]/1e6:8.2f}  yr-before {v/1e6:8.2f}  chg {(me[k]-v)/abs(v)*100:6.1f}%")
# charts
q = pd.DataFrame({"date": ["2021-12-31","2022-06-30","2022-09-30","2022-12-31","2023-03-31","2023-06-30"],
                  "cash": [80.726, 56.575, 47.182, 38.313, 25.737, 17.746]}); q["date"] = pd.to_datetime(q.date)
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(q.date, q.cash, "o-", color="tab:blue")
for d, c in zip(q.date, q.cash): ax.annotate(f"${c:.1f}M", (d, c), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=8)
ax.axvline(pd.Timestamp("2023-07-23"), color="red", ls="--"); ax.text(pd.Timestamp("2023-07-15"), 70, "MEI merger\nterminated\n23 Jul 2023 ", color="red", fontsize=8, ha="right")
import matplotlib.dates as mdates; ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y")); ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1,7])); ax.set_ylim(0, 95); ax.set_ylabel("Cash, equivalents & AFS securities ($M)")
ax.set_title("Cash fell 78% in 18 months with no new equity raised\n(source: 10-K FY22, 10-Qs Q2'22, Q3'22, Q1'23, Q2'23)", fontsize=9)
fig.tight_layout(); fig.savefig("charts/1_cash_trend.png", dpi=130)
fig, ax = plt.subplots(figsize=(7, 4))
parts = [("Royalty-sale liabilities\n(non-recourse, non-cash)", royalty_cur + royalty_nc, "tab:gray"), ("Payables & accrued\n(cash-settled)", other, "tab:red")]
b = 0
for lab, v, c in parts: ax.bar("Liabilities", v / 1e3, bottom=b / 1e3, color=c, label=lab); b += v
ax.bar("Total assets", ta / 1e3, color="tab:blue", label="Total assets"); ax.bar("Cash", cash / 1e3, color="tab:green", label="Cash")
ax.set_ylabel("$M at 30 Jun 2023"); ax.legend(fontsize=8)
ax.set_title("Negative equity is mostly royalty-sale accounting; the real\npressure is cash vs. ~$10.8M of payables plus burn (Q2'23 10-Q)", fontsize=9)
fig.tight_layout(); fig.savefig("charts/2_liabilities.png", dpi=130)
p = df[(df.sic // 100 == 28) & (df.cik != 1113148) & (df.ddate == 20230630)].sort_values("filed").groupby("cik").tail(1)
r = (p.net_income / p.total_assets).replace([np.inf, -np.inf], np.nan).dropna().clip(-3, 1)
fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(r, bins=40, color="lightgray", edgecolor="gray"); v = me.net_income / me.total_assets
ax.axvline(v, color="red"); ax.text(v + 0.03, ax.get_ylim()[1] * 0.8, f"Infinity {v:.2f}\n(worse than {(r > v).mean()*100:.0f}% of peers)", color="red", fontsize=8)
ax.set_xlabel("Annualized net income / total assets (values beyond -3 and 1 are piled into the end bins)"); ax.set_ylabel("SIC 28 peers, period 30 Jun 2023")
ax.set_title(f"Loss is ordinary in dollars (peer median -${-p.net_income.median()/1e6:.0f}M) but huge vs. assets", fontsize=9)
fig.tight_layout(); fig.savefig("charts/3_peer_loss_to_assets.png", dpi=130)
print("peers n", len(p), "share peers worse NI/TA", ((p.net_income / p.total_assets) < v).mean())
