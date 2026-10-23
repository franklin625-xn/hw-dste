# hw-dste

A Claude Code / Agent Skills skill that turns AI into a **DSTE expert**: answers strategy-to-execution questions with a judgment first, then the evidence and the boundary — instead of listing framework names.

`references/` is a topic-organised knowledge base distilled from four published books on Huawei's DSTE (Develop Strategy to Execute) management system. Every entry carries a source citation (book, page, quoted passage). Entries marked 华为专属 (Huawei-specific) are internal Huawei practices and should not be presented as another company's policy.

- Structured extraction follows the approach of [weitzu-com/book-to-skill](https://github.com/weitzu-com/book-to-skill).
- Source verification: `scripts/verify_sources.py`.
- Pending items and inconsistent figures inside the books: `references/verification_notes.md`.

Sources (Chinese editions):

- 谢宁《华为战略管理法：DSTE实战体系》
- 胡红卫《DSTE：从战略到执行》
- 陈雨点《华为战略解码：从战略规划到落地执行的管理系统》
- 冯德刚《从跟随到领先：华为管理体系重构之路》(Tsinghua University Press, 2024)

Install:

```bash
git clone https://github.com/franklin625-xn/hw-dste.git ~/.claude/skills/hw-dste
```

## Copyright / Disclaimer

The distilled material is derived from the published books above; copyright remains with their authors and publishers. It is provided for study and research only, not for commercial redistribution. If a rights holder considers this material unsuitable for public release, contact the maintainer and it will be removed.
