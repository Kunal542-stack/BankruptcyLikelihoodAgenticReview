"""Convert saved filings (HTML) to plain text, one table row per line. Usage: python -I to_text.py <filings_dir>"""
import sys, os, re
from bs4 import BeautifulSoup

folder = sys.argv[1]
for name in sorted(os.listdir(folder)):
    if not name.endswith(".htm"):
        continue
    html = open(os.path.join(folder, name), "rb").read()
    soup = BeautifulSoup(html, "html.parser")
    for t in soup.find_all(["ix:header", "script", "style"]):
        t.decompose()
    for d in soup.find_all(style=re.compile(r"display:\s*none")):
        d.decompose()
    for tr in soup.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        cells = [c for c in cells if c and c not in ("$", ")", "%")]
        tr.replace_with(soup.new_string("\n" + " | ".join(cells) + "\n"))
    text = soup.get_text("\n")
    text = re.sub(r"[ \t\xa0​]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    open(os.path.join(folder, name[:-4] + ".txt"), "w").write(text)
    print(name, len(text))
