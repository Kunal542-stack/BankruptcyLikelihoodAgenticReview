"""Check quotes are verbatim in saved filings, links point to saved filings dated <= 20230809, recompute key numbers, word count."""
import re, os, glob, pandas as pd
B = "final_cases-1/0001829126-23-005250"
rep = open(f"{B}/report.md").read()
norm = lambda s: re.sub(r"\s+", " ", s.replace(" ", " ")).strip()
texts = {os.path.basename(f): norm(open(f).read()) for f in glob.glob(f"{B}/filings/text/*.txt")}
alltext = " ".join(texts.values())

quotes = [q for q in re.findall(r"\"([^\"\n]*)\"", rep) if len(q) >= 15]
bad = 0
for q in quotes:
    hits = [k[:20] for k, t in texts.items() if norm(q) in t]
    print("OK " if hits else "MISSING", q[:70], hits[:2]); bad += not hits
print("quotes:", len(quotes), "missing:", bad)

# links: accession in URL must be a saved filing, dated before cutoff
listing = {"000182912623005250": "2023-08-09"}
saved = {os.path.basename(f).split("_")[0].replace("-", ""): f for f in glob.glob(f"{B}/filings/*.htm")}
import subprocess, io
csv = subprocess.run(["/opt/anaconda3/bin/python", "sec_tools.py", "filings", "1823882", "20230809"], capture_output=True, text=True).stdout
fl = pd.read_csv(io.StringIO(csv))
for _, r in fl.iterrows(): listing[r.adsh.replace("-", "")] = r.date
for url in sorted(set(re.findall(r"https://www\.sec\.gov/Archives/edgar/data/1823882/(\d{18})/([^)\s]+)", rep))):
    acc, doc = url
    date = listing.get(acc, "??")
    ok = acc in saved and saved[acc].endswith(doc) and date.replace("-", "") <= "20230809"
    print("LINK", "OK " if ok else "BAD", acc, doc, date)

# numbers
df = pd.read_csv("shared/financials.csv"); df = df[df.filed <= 20230809]
m = df[df.adsh == "0001829126-23-005250"].iloc[0]
assert df.filed.max() <= 20230809
print("max filed date used:", df.filed.max())
chk = {"TL/TA 2.20": round(m.total_liabilities / m.total_assets, 2) == 2.20,
       "CR 0.96": round(m.current_assets / m.current_liabilities, 2) == 0.96,
       "equity -129.8": round((m.total_assets - m.total_liabilities) / 1e6, 1) == -129.8,
       "NI/TA -1.01": round(m.net_income / m.total_assets, 2) == -1.01,
       "months 3.1": round(10137 / ((12172 - 2362) / 3), 1) == 3.1,
       "months 4.6": round(10137 / ((12172 + 1122) / 6), 1) == 4.6,
       "Q2 burn 9.8": round((12172 - 2362) / 1000, 1) == 9.8,
       "debt 166": round((4179 + 59045 + 47749 + 43402 + 11396) / 1000) == 166,
       "fortress 111": round((4179 + 59045 + 47749) / 1000) == 111,
       "adj FY21 -65": round((-70526 + 5132) / 1000) == -65,
       "adj FY22 -63": round((-85382 + 22610) / 1000) == -63,
       "adj H1 -69": round((-54496 + 20153) * 2 / 1000) == -69,
       "noncash 37%": round(20153 / 54496 * 100) == 37,
       "product rev -36%": round((49788 / 77604 - 1) * 100) == -36,
       "yr-before rev 169.0": round(84509 * 2 / 1000, 1) == 169.0,
       "yr-before NI -101.5": round(-50755 * 2 / 1000, 1) == -101.5,
       "yr-before OI -87.0": round(-43499 * 2 / 1000, 1) == -87.0,
       "yr-before OCF -45.0": round(-22494 * 2 / 1000, 1) == -45.0,
       "best case 70": 10.1 + 60 < 166}
for k, v in chk.items(): print("NUM", "OK " if v else "BAD", k)
# filing figures present in text
for s in ["10,137", "12,172", "54,496", "20,153", "85,382", "22,610", "70,526", "5,132", "3,316", "7,287", "63,122", "36,356",
          "49,788", "77,604", "84,509", "50,755", "43,499", "22,494", "47,749", "59,045", "43,402", "11,396", "4,179", "19,981"]:
    print("FIG", "OK " if s in alltext else "MISSING", s)
body = re.sub(r"\(https?://[^)]+\)", "", rep)
print("words:", len(re.findall(r"\S+", body)))
