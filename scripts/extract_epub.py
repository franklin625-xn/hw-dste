import sys, os, re, json, zipfile
from html.parser import HTMLParser

BLOCK = {"p","div","h1","h2","h3","h4","h5","h6","li","tr","br","td","th","blockquote","section","title"}
SKIP = {"style","script","head"}

class Conv(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []; self.skip = 0; self.h = None
    def handle_starttag(self, tag, attrs):
        if tag in SKIP: self.skip += 1
        if tag in ("h1","h2","h3","h4","h5","h6"): self.h = int(tag[1])
        if tag in BLOCK: self.out.append("\n")
        if tag in ("td","th"): self.out.append(" | ")
    def handle_endtag(self, tag):
        if tag in SKIP and self.skip: self.skip -= 1
        if tag in ("h1","h2","h3","h4","h5","h6"): self.h = None
        if tag in BLOCK: self.out.append("\n")
    def handle_data(self, data):
        if self.skip: return
        if self.h: self.out.append("\n" + "#"*self.h + " " + data.strip() + "\n")
        else: self.out.append(data)

src, out = sys.argv[1], sys.argv[2]
z = zipfile.ZipFile(src)
opfs = [n for n in z.namelist() if n.lower().endswith(".opf")]
opf = z.read(opfs[0]).decode("utf-8", "ignore")
base = os.path.dirname(opfs[0])
items = dict(re.findall(r'<item[^>]*id="([^"]+)"[^>]*href="([^"]+)"', opf))
items.update({m[1]: m[0] for m in re.findall(r'<item[^>]*href="([^"]+)"[^>]*id="([^"]+)"', opf)})
order = re.findall(r'<itemref[^>]*idref="([^"]+)"', opf)
names = []
for idref in order:
    href = items.get(idref)
    if href and not names.__contains__(href):
        names.append(href)
if not names:
    names = sorted([n for n in z.namelist() if n.lower().endswith((".html", ".xhtml", ".htm"))])
def norm(h):
    h = h.split("#")[0]
    return os.path.normpath(os.path.join(base, h)).replace("\\", "/")
chunks = []
total = 0
for i, href in enumerate(names, 1):
    p = norm(href)
    try: data = z.read(p).decode("utf-8", "ignore")
    except KeyError: continue
    c = Conv(); c.feed(data)
    text = re.sub(r"[ \t\u3000]+", " ", "".join(c.out))
    text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
    if not text: continue
    total += len(text)
    chunks.append(f"\n\n<<<DOC {i} {p}>>>\n{text}")
with open(out, "w", encoding="utf-8") as f: f.write("".join(chunks))
print(json.dumps({"docs": len(chunks), "chars": total}, ensure_ascii=False))
