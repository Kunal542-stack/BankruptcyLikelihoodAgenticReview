"""Convert saved filing HTML to plain text, one table row per line. Usage: python -I to_text.py <filings_dir>"""
import glob
import re
import sys

from bs4 import BeautifulSoup

folder = sys.argv[1]
for path in glob.glob(f"{folder}/*.htm"):
    soup = BeautifulSoup(open(path, "rb").read(), "html.parser")
    for tag in soup.find_all(["ix:header", "script", "style"]):
        tag.decompose()
    for div in soup.find_all(style=re.compile(r"display:\s*none")):
        div.decompose()
    for tr in soup.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        cells = [c for c in cells if c and c not in ("$", ")", "%")]
        tr.replace_with(soup.new_string("\n" + " | ".join(cells) + "\n"))
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for blk in soup.find_all(["p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6"]):
        blk.insert_before("\n")
        blk.insert_after("\n")
    text = soup.get_text()
    text = text.replace("\xa0", " ").replace("’", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    open(path.rsplit(".", 1)[0] + ".txt", "w").write(text)
    print(path, len(text))
