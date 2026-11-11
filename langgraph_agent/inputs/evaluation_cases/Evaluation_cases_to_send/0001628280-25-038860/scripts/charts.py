"""Charts for the Sangamo case. Run from the investigator folder with python -I."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

C = "final_cases-1/0001628280-25-038860"

# 1. quarterly operating cash flow, partner receipts marked
q = pd.read_csv(f"{C}/scripts/quarterly_ocf.csv", index_col=0).iloc[:, 0]
fig, ax = plt.subplots(figsize=(8, 4))
colors = ["tab:red" if v < 0 else "tab:green" for v in q.values]
ax.bar(q.index, q.values, color=colors)
ax.axhline(0, color="black", lw=0.8)
notes = {"2024Q3": "Genentech\n\\$40m", "2024Q4": "Genentech \\$10m\n+ Astellas \\$20m",
         "2025Q2": "Lilly\n\\$18m"}
for k, t in notes.items():
    i = list(q.index).index(k)
    ax.text(i, {"2024Q3": 26, "2024Q4": 12, "2025Q2": 20}[k], t, ha="center", va="center", fontsize=7)
    ax.text(i, max(q[k], 0) + 2, f"{q[k]:.1f}", ha="center", fontsize=8)
ax.set_ylim(-80, 32)
ax.set_ylabel("$ millions per quarter")
ax.set_title("Quarterly operating cash flow: burn looks small only when partner fees arrive\n(labels = partner cash received; ex-fees burn was \\$28-36m in each of those quarters)", fontsize=10)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{C}/charts/1_quarterly_ocf.png", dpi=130)

# 2. management's own runway at each annual/quarterly filing (months from filing date to start of the named period)
r = pd.DataFrame({
    "filing": ["10-K\n13 Mar 2024", "10-K\n17 Mar 2025", "10-Q\n12 May 2025", "10-Q\n7 Aug 2025"],
    "filed": pd.to_datetime(["2024-03-13", "2025-03-17", "2025-05-12", "2025-08-07"]),
    "until": pd.to_datetime(["2024-07-01", "2025-05-15", "2025-07-01", "2025-10-01"]),
    "text": ["'into Q3 2024'", "'into the middle of Q2 2025'", "'early into Q3 2025'", "'into Q4 2025'"]})
r["months"] = (r["until"] - r["filed"]).dt.days / 30.4
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(r.filing, r.months, color="tab:orange")
for i, (m, t) in enumerate(zip(r.months, r.text)):
    ax.text(i, m + 0.1, f"{t}\n~{m:.1f} months", ha="center", fontsize=8)
ax.axhline(12, color="grey", ls="--", lw=0.8)
ax.text(3.4, 11.6, "12 months", ha="right", fontsize=8, color="grey")
ax.set_ylim(0, 13)
ax.set_ylabel("months of cash management stated\n(filing date to start of named period)")
ax.set_title("Management's stated cash runway has stayed under 4 months since early 2024")
plt.tight_layout()
plt.savefig(f"{C}/charts/2_stated_runway.png", dpi=130)

# 3. percentile among SIC 28 peers (higher = better for every bar)
peers = pd.read_csv(f"{C}/scripts/peers_sic2.csv")
me = dict(total_assets=97_558e3, ni=-101_166e3, ocf=-88_614e3, ca=49_893e3, cl=47_659e3, tl=77_956e3)
def pct(series, value, higher_better=True):
    s = series.replace([float("inf"), -float("inf")], pd.NA).dropna()
    return ((s < value).mean() if higher_better else (s > value).mean()) * 100
ta = peers.total_assets.where(peers.total_assets > 0)
vals = {
    "Total assets (size)": pct(peers.total_assets, me["total_assets"]),
    "Net income / assets": pct(peers.net_income / ta, me["ni"] / me["total_assets"]),
    "Op. cash flow / assets": pct(peers.operating_cash_flow / ta, me["ocf"] / me["total_assets"]),
    "Current ratio": pct(peers.current_assets / peers.current_liabilities.where(peers.current_liabilities > 0),
                         me["ca"] / me["cl"]),
    "Liabilities / assets\n(lower is better)": pct(peers.total_liabilities / ta, me["tl"] / me["total_assets"], False),
}
fig, ax = plt.subplots(figsize=(8, 4))
ax.barh(list(vals), list(vals.values()), color=["tab:blue"] + ["tab:red"] * 4)
ax.axvline(50, color="grey", ls="--", lw=0.8)
for i, v in enumerate(vals.values()):
    ax.text(v + 1, i, f"{v:.0f}th", va="center", fontsize=9)
ax.set_xlim(0, 100)
ax.set_xlabel(f"percentile among {len(peers)} SIC 28 peers, period ending within 92 days of 30 Jun 2025 (100 = best)")
ax.set_title("Mid-sized for its peer group, but in the bottom quarter on losses and liquidity")
ax.invert_yaxis()
plt.tight_layout()
plt.savefig(f"{C}/charts/3_peer_percentiles.png", dpi=130)
print(vals)

# 4. reported loss vs loss after adding back non-cash items vs operating cash flow
a = pd.read_csv(f"{C}/scripts/adjusted_loss.csv")
fig, ax = plt.subplots(figsize=(8, 4.2))
x = list(range(len(a)))
w = 0.27
for off, col, lab, colr in [(-w, "net_loss", "reported net loss", "tab:grey"),
                            (0, "cash_loss", "net loss + non-cash expenses added back", "tab:red"),
                            (w, "ocf", "actual operating cash outflow", "black")]:
    ax.bar([i + off for i in x], -a[col], width=w, label=lab, color=colr)
    for i, v in zip(x, -a[col]):
        ax.text(i + off, v + 3, f"{v:.0f}", ha="center", fontsize=8)
ax.set_xticks(x)
ax.set_xticklabels(["FY2023\n(12 months)", "FY2024\n(12 months)", "H1 2024\n(6 months)", "H1 2025\n(6 months)"])
ax.set_ylabel("\\$ millions (shown as positive)")
ax.set_title("Since 2024 the loss is mostly cash. FY2023 had \\$155m of write-downs, but its cash\n"
             "outflow was still \\$225m because \\$161m of revenue came from old deferred revenue", fontsize=10)
ax.legend(fontsize=8)
plt.tight_layout()
plt.savefig(f"{C}/charts/4_cash_vs_reported_loss.png", dpi=130)
