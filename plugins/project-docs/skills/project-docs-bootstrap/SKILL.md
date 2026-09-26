---
name: project-docs-bootstrap
description: Use only when explicitly requested to initialize a missing documentation baseline or create the minimum useful project documentation.
---

# 初始化文档入口

仅在用户显式调用本技能时使用。读取[共同写作约定](../project-docs-progress/references/writing-style.md)。先看现有入口和能说明项目用途、运行方式的少量配置与代码，再补缺失事实；不通读整个仓库。

只建立当前真实需要的入口，已有清晰布局优先。通常先解决 README；有活动项目管理需求才建 TODO / roadmap，有理解实现的需求才建技术说明，需要项目规则才建 AGENTS。不要一次生成所有目录或空白文档套件。

| 需要建立的内容 | 按需读取的资料 |
| --- | --- |
| README / 使用说明 | [README 约定](../project-docs-readme/references/readme-contract.md)、[模板](../project-docs-readme/assets/readme-template.md)；需要日常用法时读[使用说明](../project-docs-readme/references/usage-guide.md) |
| 当前与未来工作 | [规划职责](../project-docs-planning/references/planning-model.md)、[模板](../project-docs-planning/assets/planning-templates.md) |
| 技术入口 | [C4 与源码导航](../project-docs-architecture/references/architecture-diagrams.md)、[技术页示例](../project-docs-architecture/assets/technical-templates.md) |
| 项目指导 | [AGENTS 与软链](../project-docs-guidance/references/project-guidance.md) |

这些是本插件的配套资料，不是自动调用其他技能。只读正在创建的文档类型；计划归档等未发生的流程不提前加载。

用户已要求创建则直接完成范围内工作；关键用途或推荐使用路径缺失时才询问。只要求审查则交付发现，不修改。检查新入口和链接是否可用，不把“初始化文档”扩大成源码改造、发布或迁移全部历史。
