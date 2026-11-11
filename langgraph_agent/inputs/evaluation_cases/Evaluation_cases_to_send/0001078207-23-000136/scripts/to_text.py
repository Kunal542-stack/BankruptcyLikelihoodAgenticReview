"""Convert saved filing HTML to plain text, one table row per line, hidden XBRL removed.
Usage: python -I to_text.py <filings_dir> <out_dir>"""
import os
import re
import sys

from bs4 import BeautifulSoup

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
for name in sorted(os.listdir(src)):
    if not name.endswith(".htm"):
        continue
    soup = BeautifulSoup(open(os.path.join(src, name), "rb").read(), "lxml")
    for tag in soup.find_all(["ix:header", "script", "style"]):
        tag.decompose()
    for tag in soup.find_all(style=re.compile(r"display:\s*none")):
        tag.decompose()
    for tr in soup.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        cells = [c for c in cells if c]
        tr.replace_with(soup.new_string("\n" + " | ".join(cells) + "\n"))
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for blk in soup.find_all(["p", "div", "li", "h1", "h2", "h3", "h4", "table"]):
        blk.insert_after("\n")
    text = soup.get_text()
    text = text.replace("\xa0", " ").replace("’", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    open(os.path.join(out, name.replace(".htm", ".txt")), "w").write(text)
    print(name, len(text))
