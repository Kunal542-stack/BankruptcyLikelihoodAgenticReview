"""Convert saved filings (HTML) to plain text, keeping each table row on one line."""
import glob
import os
import re
import sys

from bs4 import BeautifulSoup

folder = sys.argv[1]
out = os.path.join(folder, "text")
os.makedirs(out, exist_ok=True)
for path in glob.glob(os.path.join(folder, "*.htm")):
    soup = BeautifulSoup(open(path, "rb").read(), "lxml")
    for t in soup(["script", "style"]):
        t.decompose()
    for t in soup.find_all(lambda x: x.name and x.name.lower() in ("ix:header",)):
        t.decompose()
    for t in soup.find_all(style=re.compile(r"display:\s*none", re.I)):
        t.decompose()
    for tr in soup.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        cells = [c for c in cells if c]
        tr.replace_with(soup.new_string("\n" + " | ".join(cells) + "\n"))
    for br in soup.find_all(["br", "p", "div"]):
        br.insert_after(soup.new_string("\n"))
    text = soup.get_text()
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    with open(os.path.join(out, os.path.basename(path).replace(".htm", ".txt")), "w") as f:
        f.write(text)
    print(path, len(text))
