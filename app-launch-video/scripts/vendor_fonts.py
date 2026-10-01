"""Download Google Fonts (latin subset, woff2) into assets/fonts and write assets/fonts.css.

    python3 tools/vendor_fonts.py "<UI family>:400,500,600,700" "<mono family>:400,500,600,700"

Each argument is "Family:weights", with "i" after a weight for italic. The render must never depend on
a font CDN, so the woff2 files live in the project. Load assets/fonts.css before assets/theme.css in
index.html, and name the families only in the --ui and --mono tokens.
"""

import os
import re
import subprocess
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
if len(sys.argv) < 2:
    sys.exit(__doc__)

families = []
for arg in sys.argv[1:]:
    name, _, weights = arg.partition(":")
    pairs = []
    for w in re.split(r"[,;]", weights or "400"):
        w = w.strip()
        if w:
            pairs.append((1 if w.endswith("i") else 0, int(w.rstrip("i"))))
    axis = ";".join(f"{i},{w}" for i, w in sorted(set(pairs)))
    families.append(f"family={urllib.parse.quote_plus(name)}:ital,wght@{axis}")
url = "https://fonts.googleapis.com/css2?" + "&".join(families) + "&display=block"
css = subprocess.run(["curl", "-sf", "-A", UA, url], capture_output=True, text=True, check=True).stdout

out_dir = os.path.join(ROOT, "assets", "fonts")
os.makedirs(out_dir, exist_ok=True)
faces, fetched = [], {}
for subset, body in re.findall(r"/\* (.*?) \*/\s*@font-face \{(.*?)\}", css, re.S):
    if subset != "latin":
        continue
    fam = re.search(r"font-family: '([^']+)'", body).group(1)
    style = re.search(r"font-style: (\w+)", body).group(1)
    weight = re.search(r"font-weight: (\d+)", body).group(1)
    src = re.search(r"url\((https://[^)]+\.woff2)\)", body).group(1)
    if src not in fetched:  # variable fonts serve every weight from one file
        fetched[src] = f"{fam.replace(' ', '')}-{weight}{'i' if style == 'italic' else ''}.woff2"
        subprocess.run(["curl", "-sf", "-o", os.path.join(out_dir, fetched[src]), src], check=True)
    faces.append(f"@font-face {{ font-family: '{fam}'; font-style: {style}; font-weight: {weight}; font-display: block; src: url('fonts/{fetched[src]}') format('woff2'); }}")
open(os.path.join(ROOT, "assets", "fonts.css"), "w").write("/* Vendored by tools/vendor_fonts.py (Google Fonts, latin subset). Check each family's licence. */\n" + "\n".join(faces) + "\n")
print(f"{len(faces)} faces, {len(fetched)} files -> assets/fonts")
