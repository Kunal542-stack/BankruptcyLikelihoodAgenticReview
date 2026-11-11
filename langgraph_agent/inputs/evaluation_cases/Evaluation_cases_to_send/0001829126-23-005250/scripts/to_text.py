"""Convert saved filings (HTML) to plain text, one table row per line. Output: filings/text/<name>.txt"""
import os, re, sys
from bs4 import BeautifulSoup

folder = sys.argv[1]
out = os.path.join(folder, "text")
os.makedirs(out, exist_ok=True)
for f in sorted(os.listdir(folder)):
    if not f.endswith(".htm"):
        continue
    soup = BeautifulSoup(open(os.path.join(folder, f), "rb").read(), "html.parser")
    for t in soup(["script", "style"]):
        t.decompose()
    for t in soup.find_all(lambda x: x.name and x.name.startswith("ix:header")):
        t.decompose()
    for tr in soup.find_all("tr"):
        cells = [re.sub(r"\s+", " ", td.get_text(" ")).strip() for td in tr.find_all(["td", "th"])]
        cells = [c for c in cells if c]
        tr.replace_with(soup.new_string("\n" + " | ".join(cells) + "\n"))
    text = soup.get_text("\n")
    text = text.replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", l).strip() for l in text.split("\n")]
    text = "\n".join(l for l in lines if l)
    open(os.path.join(out, f.replace(".htm", ".txt")), "w").write(text)
    print(f, len(text))
