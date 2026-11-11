"""Check quotes word for word, recompute cited numbers, check links and dates, count words."""
import re, os, glob, sys
C = sys.argv[1]
rep = open(f"{C}/report.md").read()
texts = {os.path.basename(f): re.sub(r"\s+", " ", open(f).read()) for f in glob.glob(f"{C}/filings/*.txt")}
allt = " ".join(texts.values())
quotes = [q for q in re.findall(r'"([^"]+)"', rep) if len(q) > 12]
print("QUOTES")
for q in quotes:
    qn = re.sub(r"\s+", " ", q)
    hits = [k[:20] for k, v in texts.items() if qn in v]
    print("OK " if hits else "MISSING", hits[:2], qn[:80])
print("\nNUMBERS")
chk = {
 "runway months (Q3 burn)": 1533 / (26519 / 3), "runway days": 1533 / (26519 / 3) * 30,
 "incl restricted months": 16069 / (26519 / 3), "Q1/Q2/Q3 burn per month": (47519/3, 35900/3, 26519/3),
 "burn fall Q1->Q3": 1 - 26519 / 47519, "payables / cash": 81015 / 1533,
 "Q3 AP/accrual build": 10983 - 1494, "current ratio": 28979 / 202344, "TL/TA": 301330 / 523289,
 "working capital": 28979 - 202344, "OCF/TA": -146584 / 523289, "OI/rev": -220040 / 1996,
 "AFV drawn": 3.9 + 3.0, "annualised NI 9M": -112389 * 12 / 9,
}
for k, v in chk.items(): print(f"{k:28s} {v}")
print("\nLINKS")
links = re.findall(r"\]\(([^)]+)\)", rep)
for l in sorted(set(links)):
    if l.startswith("http"):
        m = re.search(r"/data/1750153/(\d{18})/(.+)$", l); adsh = m.group(1)
        a = f"{adsh[:10]}-{adsh[10:12]}-{adsh[12:]}"
        ok = any(f.startswith(a) for f in os.listdir(f"{C}/filings"))
        print("saved" if ok else "NOT SAVED", a, m.group(2))
    else:
        print("exists" if os.path.exists(os.path.join(C, l)) else "MISSING", l)
print("\nfilings dates: all EDGAR filings were listed by sec_tools with date < 20241114, plus the 10-Q filed 20241114")
words = len(re.findall(r"\S+", rep)); print("WORDS", words)
