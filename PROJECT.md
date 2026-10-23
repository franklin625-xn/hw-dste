# hw-dste 知识库构建说明

## 定位

`hw-dste` 是一个 **DSTE 专家**：用户随时提问，它按顾问的方式回答——给判断、给出处、讲边界，缺信息时先问。事实与素材来自四本 DSTE / 华为经营管理书籍的提炼（`references/`，每条带出处），但不局限于书：书里没有的可以检索公开资料，需注明来源并与书中说法区分。

它**只承载方法论参照**，不承载道通的正式制度、口径与数据。`SKILL.md` 只定专家行为（v2.0）；素材在 `references/`。

## 源书（原件在 DSTE 项目 `01_Source/`，保持只读）

| 简称 | 书 | 作者 | 格式 | 来源 |
|---|---|---|---|---|
| 谢宁 | 《华为战略管理法：DSTE实战体系》 | 谢宁 | PDF，364 页，有文字层 | 用户提供（2026-10-23 放入项目 01_Source） |
| 胡红卫 | 《DSTE：从战略到执行》 | 胡红卫 | EPUB | 同上 |
| 陈雨点 | 《华为战略解码：从战略规划到落地执行的管理系统》 | 陈雨点 | EPUB | 同上 |
| 冯德刚 | 《从跟随到领先：华为管理体系重构之路》 | 冯德刚，清华大学出版社 2024 | EPUB | 同上 |

四本均为第三方正版电子书，版权归原作者与出版方。本知识库是提炼笔记，**仅限内部学习使用，不得对外分发或发布为公开仓库**。

## 构建方法

采用 [weitzu-com/book-to-skill](https://github.com/weitzu-com/book-to-skill)（书道）v2.4 的思路，并做两处调整：

1. **不从单本书产出单本书的 skill**，而是四本合并成一套按课程主题组织的知识库，避免「一本一个 skill」造成重复和切换成本。
2. **输出位置**：书道默认输出到 `~/.claude/skills/`；本项目改为 `98_系统与模板/hw_dste_skill/`，本项目内通过 `2026_DSTE经营管理课程/.claude/skills/` 软链接加载。不自动写用户全局目录。

流程图（对应书道阶段）：

- 阶段零 预处理：PDF 用 PyMuPDF 提文字层（谢宁书为 CID 字体，`pdftotext` 提不出汉字，已弃用）；EPUB 用 Python 标准库解析 OPF 顺序和 XHTML 正文。产物在 DSTE 项目 `02_AI_Workspace/_temp/books_text/`。
- 阶段一 结构化：按 `<<<PAGE N>>>`（PDF）或 `<<<DOC n 路径>>>`（EPUB）标记切分，保留可定位的出处单位。
- 阶段二 深度解析：四书并行，每书 1–3 个 Agent，四层提取（概念/框架/方法/原则 + 案例），强制 source 锚点。原始输出在 `book_parse/*.json`。
- 阶段三/四 编写：合并去重后按课程主题写入 `references/` 七件套（在书道六件套基础上增加 glossary 与 huawei_vs_portable）。
- 阶段五 验证：抽查 source 能否在原文找回；检查每章是否覆盖；检查华为专属与一般方法的边界标注。
- 阶段六 归档：本文件 + `PROJECT.md` 记录构建时间、源书版本和已知局限。

## 环境说明（2026-10-23）

- 本机无 Python、无 Node、无 Calibre。安装器静默安装需要管理员而对当前用户卡住，改用 **嵌入式 Python 3.12**（用户目录 `%TEMP%\py_embed`，`python312._pth` 里追加了 `..\pylib`）+ **PyMuPDF 1.24.14**（装到 `%TEMP%\pylib`）。
- 这些都在临时目录里，重装或清理临时文件后需重建；提取、校验、合并脚本见本目录 `scripts/`（extract_pdf.py、extract_epub.py、verify_sources.py、build_references.py）。
- 如需长期使用，建议后续正式安装 Python 3.12（当前用户）并 `pip install pymupdf`，再把脚本移入本目录 `scripts/`。

## 更新方式

新增一本书：放入项目 `01_Source/` → 按上述流程提取 → 新增解析 JSON → 合并进 `references/`，在 `knowledge_graph.md` 与各条目的 source 中加上书目简称，更新本文件与 `SKILL.md` 的 source_books。不得覆盖已有条目，冲突的写法放入 principles 的矛盾调和。

## 已知局限

- 谢宁书为 PDF，页码是 PDF 页码，与原书印刷页码可能存在偏移；引用时以「谢宁 p.N + 原文片段」为准，人工核验时按原文片段搜索。
- EPUB 三本无印刷页码，source 用章节 + 原文片段。
- 书籍内容有时效性，书中的华为数据仅作背景。
