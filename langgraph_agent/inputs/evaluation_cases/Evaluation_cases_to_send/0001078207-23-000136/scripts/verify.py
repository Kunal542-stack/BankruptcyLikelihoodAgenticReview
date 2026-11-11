"""Checks: quotes word for word in saved filings, links map to saved filings dated <= 20231114,
recomputed numbers, word count. Usage: python -I verify.py <case_dir> <financials.csv>"""
import os
import re
import sys

import pandas as pd

case, csv = sys.argv[1], sys.argv[2]
report = open(f"{case}/report.md").read()
texts = {f.split("_")[0]: open(f"{case}/filings/text/{f}").read() for f in os.listdir(f"{case}/filings/text")}
FILED = {  # filing dates from `sec_tools.py filings 1078207 20231114` (+ this report, 2023-11-14)
    "0001078207-23-000136": 20231114, "0001078207-23-000108": 20230809, "0001078207-23-000055": 20230601,
    "0001078207-22-000201": 20221109, "0001078207-22-000114": 20220603, "0001078207-22-000206": 20221201,
    "0001078207-23-000022": 20230502, "0001193125-23-168081": 20230615, "0001078207-23-000095": 20230710,
    "0001078207-23-000123": 20230927, "0001078207-22-000093": 20220519, "0001839882-22-013387": 20220621,
    "0001078207-22-000132": 20220715}

norm = lambda s: re.sub(r"\s+", " ", s.replace("’", "'").replace("“", '"').replace("”", '"')).strip()
quotes = re.findall(r'\*"(.+?)"\*', report)
ok = True
for q in quotes:
    hits = [a for a, t in texts.items() if norm(q) in norm(t)]
    print("QUOTE", "OK " if hits else "MISSING", hits[:2], q[:70])
    ok &= bool(hits)

links = set(re.findall(r"https://www\.sec\.gov/Archives/edgar/data/(\d+)/(\d{18})/([\w\-\.]+)", report))
for cik, acc, doc in sorted(links):
    adsh = f"{acc[:10]}-{acc[10:12]}-{acc[12:]}"
    saved = os.path.exists(f"{case}/filings/{adsh}_{doc}")
    date = FILED.get(adsh)
    good = saved and cik == "1078207" and date is not None and date <= 20231114
    print("LINK", "OK " if good else "BAD", adsh, doc, date)
    ok &= good

# recompute cited numbers from the CSV (rows filed <= cut-off) and from statement figures ($k)
df = pd.read_csv(csv); df = df[df.filed <= 20231114]
me = df[df.adsh == "0001078207-23-000136"].iloc[0]
chk = {
    "NI annual -34.9": (me.net_income / 1e6, -34.9), "NI/TA -0.21": (me.net_income / me.total_assets, -0.208),
    "CL/TA 0.51": (me.current_liabilities / me.total_assets, 0.508), "lev 0.72": (me.total_liabilities / me.total_assets, 0.719),
    "lev Sep-22 0.60": (134894 / 226513, 0.596), "CR 1.38": (me.current_assets / me.current_liabilities, 1.379),
    "CR Sep-22 2.32": (155292 / 66906, 2.321), "payables share 0.74": (63235 / 85243, 0.742),
    "Q2 cash loss 8.9": (-((-17467 - -4924) + (6256 - 3150) + (1941 - 1015) + (114 + 182) + 0 + (582 - 1252)) / 1000, 8.9),
    "H1 cash loss annual 35.2": (-(-17467 + 6256 + 1941 + 114 - 9021 + 582) * 2 / 1000, 35.2),
    "cash drop Q2 8.0": ((18280 - 10292) / 1000, 7.99), "liquidity 39.3": ((10292 + 29000) / 1000, 39.3),
    "months 11": ((10292 + 29000 - 7000) / 2957, 10.9), "floor liquidity 32.3": ((10292 + 29000 - 7000) / 1000, 32.3), "H2 implied 125-150": ((215000 - 90409) / 1000, 124.6),
    "H2 FY23 166": ((286773 - 120275) / 1000, 166.5), "payables WC +34.8": (34757 / 1000, 34.8),
    "debt drop": (47.3 - 17.2, 30.1),
}
for k, (got, want) in chk.items():
    print("NUM", "OK " if abs(got - want) < 0.06 * max(1, abs(want)) else "DIFF", k, round(got, 3))
words = len(re.sub(r"!\[.*?\]\(.*?\)|\(https?://\S+?\)", "", report).split())
print("WORDS", words)
print("ALL QUOTES AND LINKS OK" if ok else "PROBLEMS FOUND")
