import re, glob, pandas as pd, numpy as np
rep = open("report.md").read()
norm = lambda s: re.sub(r"\s+", " ", s.replace("’", "'").replace("“", '"').replace("”", '"'))
texts = {p: norm(open(p).read()) for p in glob.glob("filings/*.txt")}
quotes = [q for line in rep.replace("“", '"').replace("”", '"').splitlines() for q in re.findall(r'"([^"]{12,}?)"', line)]
bad = 0
for q in quotes:
    hits = [p.split("/")[-1][:20] for p, t in texts.items() if norm(q) in t]
    print("OK " if hits else "MISSING", q[:70], hits[:2]); bad += not hits
print("quotes:", len(quotes), "missing:", bad)
# numbers
df = pd.read_csv("../../shared/financials.csv"); df = df[df.filed <= 20230810]
me = df[df.adsh == "0001113148-23-000009"].iloc[0]
p = df[(df.sic // 100 == 28) & (df.cik != 1113148) & (df.ddate == 20230630)].sort_values("filed").groupby("cik").tail(1)
assert len(p) == 567
chk = {"NI/TA": round(me.net_income / me.total_assets, 2), "TL/TA": round(me.total_liabilities / me.total_assets, 2),
       "CR": round(me.current_assets / me.current_liabilities, 2), "peer median NI $M": round(p.net_income.median() / 1e6),
       "peer median TL/TA": round((p.total_liabilities / p.total_assets).median(), 2),
       "pct peers worse NI/TA": round(((p.net_income / p.total_assets) < me.net_income / me.total_assets).mean() * 100),
       "pct peers lower TL/TA": round(((p.total_liabilities / p.total_assets) < me.total_liabilities / me.total_assets).mean() * 100),
       "royalty share TL": round(47826 / 58638 * 100), "TL ex royalty / TA": round(10812 / 21232, 2),
       "months Q2 burn": round(17746 / ((20583 - 12576) / 3), 1), "months H1": round(17746 / (20583 / 6), 1),
       "cash drop %": round((80.726 - 17.746) / 80.726 * 100), "equity": 21232 - 58638}
for c in ["total_assets","current_assets","current_liabilities","total_liabilities","revenue","net_income","operating_income","operating_cash_flow"]:
    chk["pct " + c] = round((p[c].dropna() < me[c]).mean() * 100)
for k, v in chk.items(): print(f"{k:28s} {v}")
# filing values cross-check vs csv
q2 = texts["filings/0001113148-23-000009_infi-20230630.txt"]
for s in ["Total liabilities | 58,638", "Total assets | $ | 21,232", "Net loss | $ | (9,956) | $ | (11,986) | $ | (21,001)", "Cash and cash equivalents | $ | 17,746",
          "Net cash used in operating activities | (20,583)", "Total stockholders' deficit | (37,406)", "Liabilities related to sale of future royalties, net, current portion | 1,252"]:
    print("in filing:", norm(s) in q2, s)
# links and dates
links = re.findall(r"\]\(([^)]+)\)", rep); acc = set()
lst = pd.read_csv("scripts/filings_list.csv")
for l in links:
    m = re.search(r"/data/1113148/(\d{18})/", l)
    if m:
        a = m.group(1); a = f"{a[:10]}-{a[10:12]}-{a[12:]}"; acc.add(a)
dates = {a: (lst.loc[lst.adsh == a, "date"].iloc[0] if a in set(lst.adsh) else "2023-08-10 (this report)") for a in acc}
for a, d in sorted(dates.items(), key=lambda x: x[1]): print(a, d)
print("all sources <= 2023-08-10:", all(d[:10] <= "2023-08-10" for d in dates.values()))
print("local files exist for all links:", all(glob.glob(f"filings/{a}_*.htm") for a in acc))
print("links:", len(links), "word count:", len(re.findall(r"\S+", rep)))
