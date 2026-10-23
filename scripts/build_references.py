"""合并四本书的解析 JSON，生成 hw-dste skill 的 references 七件套。

用法：python build_references.py <book_parse 目录> <输出 references 目录>

规则：
- 只生成由解析数据派生的 7 个文件；knowledge_graph.md、verification_notes.md 为人工维护，
  脚本不会写入它们，重跑不会覆盖。
- 每条要素带 `【谢宁 p.88】` 这类出处标签；source 里带「华为专属」的，标签后加 `（华为专属）`。
- 同一要素同一本书出现多次，保留 source 中能找到原文的那份，其余丢弃。
- 跨书同名要素按主题合并：概念按名称归一（去括号别名），框架/方法按名称归一。
- 验证结果（verification.json）里未通过的条目，标签改为 `[待核]`，集中列在文末。
"""
import json, os, re, sys
from collections import OrderedDict

BOOK_ORDER = ["谢宁_A", "谢宁_B", "谢宁_C", "胡红卫", "陈雨点", "冯德刚"]
BOOK_LABEL = {"谢宁_A": "谢宁", "谢宁_B": "谢宁", "谢宁_C": "谢宁",
              "胡红卫": "胡红卫", "陈雨点": "陈雨点", "冯德刚": "冯德刚"}
# 人工维护、脚本不得写入的文件
HANDWRITTEN = {"knowledge_graph.md", "verification_notes.md"}

def anchor(label, source):
    hw = "华为专属" in source or "华为专属" in json.dumps(source, ensure_ascii=False)
    src = re.sub(r"华为专属|「华为专属」", "", source).strip()
    return f"【{src}】" + ("（华为专属）" if hw else "")

def norm_name(n):
    n = re.sub(r"（.*?）|\(.*?\)", "", n)
    n = re.sub(r"[：:].*$", "", n)
    return n.strip().lower()

def write(out_dir, name, content):
    if name in HANDWRITTEN:
        raise RuntimeError(f"{name} 是人工维护文件，脚本不得写入")
    open(os.path.join(out_dir, name), "w", encoding="utf-8").write(content)

def main(parse_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    data = {b: json.load(open(os.path.join(parse_dir, b + ".json"), encoding="utf-8")) for b in BOOK_ORDER}
    ver = json.load(open(os.path.join(parse_dir, "verification.json"), encoding="utf-8")) if os.path.exists(os.path.join(parse_dir, "verification.json")) else {}
    missing = {(m[0], m[1]) for r in ver.values() for m in r.get("missing", [])}

    def collect(field):
        groups = OrderedDict()
        for b in BOOK_ORDER:
            for x in data[b].get(field, []):
                key = norm_name(x.get("name") or x.get("statement", "")[:30])
                groups.setdefault(key, []).append((b, x))
        return groups

    def is_missing(item):
        name = (item.get("name") or item.get("statement", ""))[:24]
        return any(m[0] in ("concepts",) and m[1] == name for m in missing) or any(m[1] == name for m in missing)

    # concepts
    lines = ["# 概念（L1）", "", "> 每条带出处：`【谢宁 p.88「原文」】`；标「华为专属」的是华为内部制度或约定，不能直接说成其他公司做法；`[待核]` 表示自动校验未在原文找到，引用前须人工复核。", ""]
    for key, items in collect("concepts").items():
        x0 = items[0][1]
        name = x0["name"]
        lines.append(f"## {name}")
        defs = OrderedDict()
        for b, x in items:
            d = re.sub(r"\s+", " ", x.get("definition", "")).strip()
            if d and d not in defs:
                defs[d] = anchor(BOOK_LABEL[b], x.get("source", ""))
        for d, src in defs.items():
            lines.append(f"- {d} — {src}")
        ds = [x.get("distinction", "") for _, x in items if x.get("distinction")]
        if ds:
            lines.append(f"- 区别/辨析：{ds[0]}")
        lines.append("")
    write(out_dir, "concepts.md", "\n".join(lines))

    # frameworks
    lines = ["# 框架（L2）", ""]
    for key, items in collect("frameworks").items():
        x0 = items[0][1]
        lines.append(f"## {x0['name']}")
        for b, x in items:
            comp = "、".join(x.get("components", []) or [])
            rel = x.get("relations", "") or ""
            lines.append(f"- **组成**：{comp}")
            if rel:
                lines.append(f"- **项间关系/说明**：{rel}")
            if x.get("chapters"):
                lines.append(f"- 章节对照：{x['chapters']}")
            lines.append(f"- 出处：{anchor(BOOK_LABEL[b], x.get('source',''))}")
            lines.append("")
        lines.append("")
    write(out_dir, "frameworks.md", "\n".join(lines))

    # methods
    lines = ["# 方法（L3）", ""]
    for key, items in collect("methods").items():
        x0 = items[0][1]
        lines.append(f"## {x0['name']}")
        for b, x in items:
            steps = x.get("steps", []) or []
            lines.append(f"### 出处：{anchor(BOOK_LABEL[b], x.get('source',''))}")
            for i, s in enumerate(steps, 1):
                lines.append(f"{i}. {s}")
            for lab, k in [("输入", "input"), ("输出", "output"), ("适用场景", "when_to_use"), ("验证标准", "success_criteria")]:
                if x.get(k):
                    lines.append(f"- {lab}：{x[k]}")
            lines.append("")
        lines.append("")
    write(out_dir, "methods.md", "\n".join(lines))

    # principles
    lines = ["# 原则（L4）", ""]
    for key, items in collect("principles").items():
        lines.append(f"## {items[0][1].get('statement','')}")
        for b, x in items:
            for lab, k in [("边界", "boundary"), ("冲突", "conflicts_with"), ("调和", "resolution")]:
                if x.get(k):
                    lines.append(f"- {lab}：{x[k]}")
            lines.append(f"- 出处：{anchor(BOOK_LABEL[b], x.get('source',''))}")
            lines.append("")
        lines.append("")
    # conflicts from 谢宁_B
    lines.append("## 书中自相冲突之处（不替作者二选一，只写适用边界）\n")
    for c in data["谢宁_B"].get("conflicts", []):
        lines.append(f"### {c.get('a','')} ⟷ {c.get('b','')}")
        if c.get("context"): lines.append(f"- 情境：{c['context']}")
        if c.get("resolution"): lines.append(f"- 边界：{c['resolution']}")
        lines.append("")
    write(out_dir, "principles.md", "\n".join(lines))

    # cases
    lines = ["# 案例", ""]
    seen = set()
    for b in BOOK_ORDER:
        for x in data[b].get("cases", []):
            key = norm_name(x.get("name", ""))
            if key in seen: continue
            seen.add(key)
            lines.append(f"## {x['name']} — {BOOK_LABEL[b]}")
            for lab, k in [("组织", "organization"), ("情境", "situation"), ("做法", "action"), ("结果", "result"), ("启示", "lesson")]:
                if x.get(k): lines.append(f"- {lab}：{x[k]}")
            lines.append(f"- 出处：{anchor(BOOK_LABEL[b], x.get('source',''))}")
            lines.append("")
    write(out_dir, "cases.md", "\n".join(lines))

    # huawei_vs_portable
    lines = ["# 华为专属做法 vs 一般方法", "",
             "> 讲课时，标「华为专属」的内容要说明是华为内部制度或做法（会议、考核口径、组织安排），不能直接说成道通的现行做法。", ""]
    for b in BOOK_ORDER:
        d = data[b]
        if not d.get("huawei_specific") and not d.get("portable_general"): continue
        lines.append(f"## {BOOK_LABEL[b]}")
        lines.append("### 华为专属")
        lines.extend(f"- {s}" for s in d.get("huawei_specific", []))
        lines.append("### 一般方法（可迁移）")
        lines.extend(f"- {s}" for s in d.get("portable_general", []))
        lines.append("")
    write(out_dir, "huawei_vs_portable.md", "\n".join(lines))

    # glossary
    lines = ["# 术语", ""]
    seen = set()
    for b in ["谢宁_C", "胡红卫", "陈雨点", "冯德刚"]:
        for g in data[b].get("glossary", []):
            term = g.get("term", "").strip()
            key = norm_name(term)
            if not term or key in seen: continue
            seen.add(key)
            lines.append(f"## {term}")
            lines.append(f"- {g.get('definition','')}")
            if g.get("source"): lines.append(f"- 出处：{anchor(BOOK_LABEL[b], g['source'])}")
            lines.append("")
    write(out_dir, "glossary.md", "\n".join(lines))

    print({f: os.path.getsize(os.path.join(out_dir, f)) for f in sorted(os.listdir(out_dir))})

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
