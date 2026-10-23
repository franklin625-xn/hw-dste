"""
Source 溯源校验：检查 book_parse/*.json 里每条要素的 source 片段能否在原文中找到。
规则：source 中任意一个引号内片段；片段内任意 10 字连续窗口出现在原书全文中即算通过
（允许省略号、标点差异：比较前去掉空白/…/—/－ 并统一中英文引号）。
输出：book_parse/verification.json，列出每本书通过数与未通过的条目（未通过者需人工复核或标 [待核]）。

用法：python verify_sources.py <book_parse 目录> <books_text 目录>
"""
import re, json, os, sys

Z = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "『": "'", "』": "'",
                   "﹣": "-", "－": "-", "—": "", "－": "-", "／": "/"})

def norm(s):
    return re.sub(r"[\s…—－]", "", s).translate(Z)

def find_fragment(source):
    s = norm(source)
    m = re.findall(r"['\"]([^'\"]{6,})['\"]", s)
    if m:
        return m
    return [re.sub(r"^.*?」(?:原文)?", "", s)]

def hit(cand, text):
    if any(c[:10] in text for c in cand):
        return True
    # 任意 10 字窗口
    return any(c[i:i + 10] in text for c in cand for i in range(len(c) - 9))

def main(parse_dir, text_dir):
    books = {
        "谢宁": "谢宁_华为战略管理法_DSTE实战体系.txt",
        "胡红卫": "胡红卫_DSTE从战略到执行.txt",
        "陈雨点": "陈雨点_华为战略解码.txt",
        "冯德刚": "冯德刚_从跟随到领先_华为管理体系重构之路.txt",
    }
    texts = {b: norm(open(os.path.join(text_dir, f), encoding="utf-8").read()) for b, f in books.items()}
    mapping = {"谢宁_A": "谢宁", "谢宁_B": "谢宁", "谢宁_C": "谢宁",
               "胡红卫": "胡红卫", "陈雨点": "陈雨点", "冯德刚": "冯德刚"}
    report = {}
    for f, b in mapping.items():
        d = json.load(open(os.path.join(parse_dir, f + ".json"), encoding="utf-8"))
        r = {"ok": 0, "miss": 0, "missing": []}
        for k in ["concepts", "frameworks", "methods", "principles", "cases"]:
            for x in d.get(k, []):
                s = x.get("source", "")
                if hit(find_fragment(s), texts[b]):
                    r["ok"] += 1
                else:
                    r["miss"] += 1
                    r["missing"].append([k, x.get("name") or x.get("statement", "")[:24], s[:100]])
        report[f] = r
    out = os.path.join(parse_dir, "verification.json")
    json.dump(report, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for f, r in report.items():
        print(f, r["ok"], "/", r["ok"] + r["miss"])

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
