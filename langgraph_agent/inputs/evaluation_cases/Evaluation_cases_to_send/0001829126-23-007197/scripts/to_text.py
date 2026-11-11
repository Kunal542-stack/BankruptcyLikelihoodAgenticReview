"""Convert saved filings (HTML) to text with table rows on one line. Usage: python -I to_text.py <filings_dir>"""
import os, re, sys
from bs4 import BeautifulSoup

d = sys.argv[1]
for f in sorted(os.listdir(d)):
    if not f.endswith(".htm"):
        continue
    soup = BeautifulSoup(open(os.path.join(d, f), "rb").read(), "lxml")
    for t in soup.find_all(["ix:header", "script", "style"]):
        t.decompose()
    for div in soup.find_all(style=re.compile(r"display:\s*none")):
        div.decompose()
    for tr in soup.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        cells = [c for c in cells if c]
        tr.replace_with(soup.new_string("\n" + " | ".join(cells) + "\n"))
    text = soup.get_text("\n")
    text = re.sub(r"[ \t\xa0]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    open(os.path.join(d, f.replace(".htm", ".txt")), "w").write(text)
    print(f, len(text))
