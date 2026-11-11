"""Convert saved filings (HTML) to plain text, one table row per line. Usage: to_text.py <filings_dir>"""
import sys, os, re
from bs4 import BeautifulSoup
d = sys.argv[1]
for f in sorted(os.listdir(d)):
    if not f.endswith(".htm"):
        continue
    soup = BeautifulSoup(open(os.path.join(d, f), "rb").read(), "html.parser")
    for t in soup.find_all(["ix:header", "script", "style"]):
        t.decompose()
    for tr in soup.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        tr.replace_with(soup.new_string("\n" + " | ".join(c for c in cells if c) + "\n"))
    for b in soup.find_all(["p", "div", "br", "li", "h1", "h2", "h3", "h4"]):
        b.insert_after(soup.new_string("\n"))
    txt = soup.get_text()
    txt = txt.replace("\xa0", " ")
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = re.sub(r"\n\s*\n+", "\n", txt)
    open(os.path.join(d, f[:-4] + ".txt"), "w").write(txt)
    print(f, len(txt))
