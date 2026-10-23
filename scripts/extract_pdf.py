import sys, re, json, fitz
src, out = sys.argv[1], sys.argv[2]
doc = fitz.open(src)
pages = []
for i, page in enumerate(doc):
    pages.append({"page": i + 1, "text": page.get_text("text")})
with open(out, "w", encoding="utf-8") as f:
    for p in pages:
        f.write(f"\n\n<<<PAGE {p['page']}>>>\n{p['text']}")
print(json.dumps({"pages": doc.page_count,
                  "chars": sum(len(p["text"]) for p in pages),
                  "empty_pages": sum(1 for p in pages if len(p["text"].strip()) < 20)}, ensure_ascii=False))
