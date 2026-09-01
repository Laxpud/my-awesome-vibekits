# 项目规划模型与默认布局

## 领域词汇

| 概念 | 回答的问题 | 不是 |
| --- | --- | --- |
| Roadmap | 接下来往哪里发展，结果、阶段和依赖是什么 | 更远期的 task checklist |
| Milestone | 已承诺交付什么，做到什么算完成 | 任意主题分组 |
| Backlog | 哪些工作可能有价值但尚未承诺 | 低优先级 ready queue |
| Task | 下一步可以执行和验证什么 | 完整设计或长期方向 |
| Plan | 如何分阶段实施、验证和回滚复杂工作 | 当前架构或决策历史 |
| TODO | 上述概念的一种文件载体 | 独立规划概念 |

## 唯一活动入口

项目必须声明一个活动工作入口。新项目存在真实活动工作时默认根 `TODO.md`；已有仓库可以使用其他文件或由仓库入口路由到外部 tracker。

外部 tracker 是权威来源时，仓库入口只记录链接、适用范围和仓库级规则，不复制 issue 状态或任务列表。本 Skill 不读取或改变外部状态，除非用户另行提供相应工具与授权。

## 渐进布局

### 轻量项目

一个 `TODO.md` 可以包含：

```markdown
# Project planning

本文件是活动工作入口。

## Execution rules

- 用户明确指定的工作优先。
- 默认从 primary milestone 选择 ready task。
- 交付前同步实际状态和验证证据。

## Primary milestone: <outcome>

Outcome: <bounded result>

Exit criteria:

- [ ] <observable condition>

Current focus: <one task or none>

Tasks:

- [ ] <task>
  - Acceptance: <only when needed>
  - Blocked by: <only when blocked>
  - Evidence: <add after meaningful verification>

## Backlog

- <candidate work, not committed>

## Recently completed

- <short result and link when useful>
```

省略没有真实内容的可选字段，不保留空标题。

### 多阶段项目

当项目需要表达多个未来结果、阶段顺序或长期依赖时增加 `ROADMAP.md`。Roadmap 使用结果、主题、阶段或时间范围；只有存在真实承诺时才写具体日期，并链接 milestone 详情而不复制 task 状态。

### 复杂 milestone 或 task

- Milestone 详情大到妨碍活动入口时使用 `docs/milestones/<stable-slug>.md`。
- 复杂实施上下文满足主 Skill 门槛时使用 `docs/plans/<stable-slug>.md`。
- 普通 task 不分配稳定 ID；只有独立文件和长期跨文档引用需要时才给 milestone 使用 slug 或 ID。

## 承诺、就绪与完成

不要用一个扁平 `Status` 同时表达所有维度：

- 位于 backlog 或 active milestone 表达是否承诺；
- `[ ]` / `[x]` 表达是否完成；
- `Blocked by` 表达就绪性；
- `Current focus` 表达正在进行；
- 文档顺序表达默认优先级，只有顺序不足时才添加显式优先级。

允许一个 primary milestone 和明确标记的 secondary active milestones。默认选择顺序：

1. 用户明确指定的工作；
2. Primary 中仍然 ready 的 Current focus；
3. Primary 中显式高优先级的 ready task；
4. Primary 中文档顺序最靠前的 ready task。

Primary 没有 ready task 时报告 blocker 并建议 secondary，不自动切换。Backlog 只有在用户明确要求或一次明确规划操作中才提升。

## Milestone 契约

每个 milestone 固定需要：

- Outcome：有边界的结果；
- Exit criteria：可观察、不可通过删弱制造完成的条件；
- Tasks：当前认为能实现结果的执行单元。

依赖、非目标、风险、owner、优先级和目标日期只在真实有用时添加，不为模板完整而编造。

Tasks 是实现手段，可以新增、替换、取消或移回 backlog。移除已承诺 task 时写一句理由；只有影响范围或退出条件时才记录正式范围变更。Milestone 只有在 outcome 与退出条件满足后完成，即使部分原始 tasks 被有理由地替换。

## 证据与历史

- 简单 task 可以只勾选。
- 非简单 task 记录足以证明结果的关键命令、检查、路径或外部证据链接，不复制完整终端日志。
- Milestone 完成时记录结果摘要、逐项退出条件证据和未解决事项。
- 未解决事项进入新 active milestone 或 backlog 后，才能归档旧 milestone。
- 小项目可以暂留最近完成记录；历史开始干扰活动工作时，将详情移入 `docs/archive/`，入口只留摘要和链接。

## Plan 生命周期

Plan 保存复杂工作的执行上下文。完成后：

1. 把 current/target architecture 和持久技术事实迁入具名技术文档；
2. 把合格决策迁入 ADR；
3. 把剩余工作迁入 active milestone 或 backlog；
4. 按项目策略归档或删除已经失去执行价值的 Plan。
