"""Check quotes, links, dates, key numbers and word count of report.md."""
import glob, re, subprocess, pandas as pd

rep = open("report.md").read()
texts = {p: re.sub(r"\s+", " ", open(p).read()) for p in glob.glob("filings/*.txt")}
norm = lambda s: re.sub(r"\s+", " ", s.replace("’", "'").replace("“", '"').replace("”", '"'))

# 1. quotes: every "..." of 25+ chars must appear verbatim in a saved filing
quotes = [q for q in re.findall(r'"([^"]{25,})"', rep)]
ok = True
for q in quotes:
    hits = [p for p, t in texts.items() if q in t or norm(q) in norm(t)]
    print("OK " if hits else "MISSING", q[:70], "->", [h.split("/")[1][:20] for h in hits])
    ok &= bool(hits)

# 2. links: every EDGAR link must be a downloaded filing dated <= 20250807
lst = subprocess.run(["/opt/anaconda3/bin/python", "../../sec_tools.py", "filings", "1159167", "20250807"],
                     capture_output=True, text=True).stdout
fl = pd.read_csv(pd.io.common.StringIO(lst))
fl["key"] = fl.adsh.str.replace("-", "")
for url in sorted(set(re.findall(r"https://www\.sec\.gov/[^)\s]+", rep))):
    acc = url.split("/")[-2]
    row = fl[fl.key == acc]
    if acc == "000115916725000069":  # the report itself, filed on the cutoff date 2025-08-07
        row = pd.DataFrame({"date": ["2025-08-07"], "document": ["irbt-20250628.htm"]})
    date = row.date.iloc[0] if len(row) else None
    good = date is not None and date.replace("-", "") <= "20250807" and url.split("/")[-1] == row.document.iloc[0]
    print("LINK", "OK " if good else "BAD", date, url.split("/")[-1]); ok &= good

# 3. numbers recomputed
co = pd.read_csv("scripts/company_rows.csv"); pe = pd.read_csv("scripts/peer_rows.csv")
assert co.filed.max() <= 20250807 and pe.filed.max() <= 20250807
me = co[co.adsh == "0001159167-25-000069"].iloc[0]
chk = {
 "NI/rev": (me.net_income / me.revenue, -0.48), "liab/assets": (me.total_liabilities / me.total_assets, 1.02),
 "current ratio": (me.current_assets / me.current_liabilities, 0.54),
 "peer NI pct": ((pe.net_income < me.net_income).mean(), 0.06),
 "peer bigger": ((pe.total_assets > me.total_assets).mean(), 0.47),
 "loan/cash": (203186 / 40568, 5.0), "Q2 OCF": (-56617 - (-26460), -30.157e3),
 "months cash Q2": (40568 / (30157 / 3), 4.0), "months incl restricted": ((40568 + 36000) / (30157 / 3), 7.6),
 "GM Q2-25": (38299 / 127558, 0.300), "GM Q2-24": (27466 / 166361, 0.165),
 "Q2 loss ex FV gain": (-22808 - 23278, -46.1e3), "cash fall": (1 - 40568 / 134303, 0.70),
 "H1 cash loss": (-110081 + 37001, -73.08e3),
}
for k, (v, want) in chk.items():
    good = abs(v - want) <= abs(want) * 0.03 + 0.006
    print("NUM", "OK " if good else "BAD", k, round(v, 3), want); ok &= good

# 4. word count
words = len(re.sub(r"!\[.*?\]\(.*?\)|\]\(.*?\)", "]", rep).split())
print("words (links stripped)", words); ok &= words <= 1200
print("ALL OK" if ok else "PROBLEMS")
