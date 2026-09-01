# 按用户意图拆分 Project Docs Skill

`project-docs` 2.0 将原有全能 `project-docs-bootstrap` 拆为 bootstrap、refactor、readme、planning、architecture 和 guidance 六个 Skill，并以用户要解决的问题而不是文件数量作为 interface。我们选择生命周期与文档专项混合结构，是因为纯生命周期结构无法让单文档能力独立触发，纯文档结构又无法深封装跨文档初始化和重构；保留 bootstrap ID 但收窄职责，因此以 2.0 表达 breaking change。

详细目标设计见 [`project-docs-multi-skill.md`](../design/project-docs-multi-skill.md)。
