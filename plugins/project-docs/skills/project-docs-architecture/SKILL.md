---
name: project-docs-architecture
description: 创建或维护 current/target architecture、Mermaid 架构图、ADR 和代码—文档一致性。适用于系统边界、部署单元、主要数据流、跨模块关系、长期约束或关键决策变化；同一请求还要写迁移步骤时以本 Skill 为主并组合 project-docs-planning，普通内部重构、单独实施计划和未授权源码修改不属于本 Skill。
---

# 项目架构文档维护

## 目标

让 architecture 文档准确区分系统当前状态、目标状态和决策理由，并能从源码、manifest、配置和测试找到证据。文档维护权限不扩展为源码迁移权限。

Plan 与 architecture 按问题分界：architecture/design 回答“系统现在或目标应是什么样”，Plan 回答“按什么顺序实现、验证和回滚”。同一请求明确要求两者时，本 Skill 作为主 Skill 先确立目标边界，再组合 `project-docs-planning` 编写实施方法；若权威目标结构已经存在且只要求实施步骤，则由 planning 单独作为主 Skill。两份文档互相链接而不复制。

## 共同底线

1. 编辑前读取仓库证据和适用项目指导。
2. 尊重既有权威位置、清晰约定和用户拥有的改动。
3. 不编造项目目的、架构、命令结果或完成状态。
4. 同一主题保留一个权威来源，其他位置使用短路由或链接。
5. 按“仓库证据 → 插件默认值 → 高风险澄清”决策；用户要求“按默认值”也不授权不可逆操作。
6. 回读改动，检查链接和 diff，并报告假设、验证及未执行门禁。

## Reference 路由

- 创建或更新 architecture 图时，读取 [`references/architecture-diagrams.md`](references/architecture-diagrams.md)。
- 判断、创建或 supersede ADR 时，读取 [`references/adrs.md`](references/adrs.md)。

只加载当前分支需要的 reference。

## 架构模型

- **Current architecture**：已经存在且可由仓库或运行证据验证的系统形态。
- **Target architecture/design**：明确标注的目标结构、边界和约束，不得写成已经实现。
- **ADR**：已经作出的关键取舍及原因，不承担当前架构概览。
- **Plan**：从当前态走向目标态的顺序、验证和回滚，由 planning interface 维护。

沿用现有清晰布局；没有约定时使用 `docs/architecture.md`，首次出现合格 ADR 时才创建 `docs/adr/`。`docs/design/`、独立 diagrams 目录和领域 glossary 只有真实内容需要时才创建。

## 维护流程

1. **建立证据图。**
   - 读取现有 architecture/design/ADR、manifest、入口、模块或包边界、配置、部署文件、关键数据流和相关测试。
   - 将每项架构陈述连接到可观察证据；无法验证的内容标记为假设、目标或待确认问题。

2. **判断变更是否属于 architecture。**
   - 系统边界、可运行或部署单元、主要数据流、跨模块关系、长期约束或合格 ADR 决策变化时更新。
   - 私有实现细节或不改变上述关系的普通内部重构不触发本 Skill。

3. **维护 current 与 target。**
   - 当前态只写已验证事实；目标态使用醒目标识。只有实施 Plan 已存在，或本次工作满足独立 Plan 门槛并明确组合 planning 时才链接，不为单纯目标设计创建空 Plan。
   - 发现代码与文档不一致时，判断文档过期、实现偏离或目标尚未落地。意图明确时修正文档；意图不明确或实现可能有问题时报告差异。
   - 除非用户同时明确要求源码变更，否则不修改源码使其追随文档。

4. **维护图与正文。**
   - 当前态总览和独立子系统 architecture 文档必须包含 Mermaid 图。
   - 使用 C4 的分层思路选择有信息量的 System Context、Container 或 Component 层级，不强制四层。
   - 正文说明边界、职责、关键流程、约束和证据入口；图展示关系与流向，不能代替正文。

5. **记录合格 ADR。**
   - 只有决定难以逆转、缺少背景会令人意外且存在真实取舍时才创建 ADR；三个条件必须同时成立。
   - Accepted ADR 保留历史语义。决定变化时创建新 ADR，并把旧 ADR 标记为 deprecated 或 superseded。

6. **验证。**
   - 回读 current/target 标识、组件名称、边界、图和正文，检查相互一致及链接可达。
   - 仓库已有 Mermaid renderer 时执行语法渲染；没有时至少检查 fenced block、节点引用和明显语法，并报告未完成的渲染验证。
   - 搜索过期组件名、旧 ADR 状态和已移动设计路径；检查 diff 没有越权源码修改。

## 示例

正例：

```text
这次改动把一个进程拆成两个可独立部署单元。请更新当前架构、Mermaid 图，并判断是否需要 ADR。
```

预期：从代码和部署证据更新 current architecture；按 C4 Container 层级表达关系；仅在三个 ADR 条件都成立时记录决策。

近邻反例：

```text
为已经确定的服务拆分写五阶段迁移、验证和回滚步骤。
```

这是 `project-docs-planning` 的实施 Plan。目标服务边界可由本 Skill 单独维护，两份文档互链。

组合示例：

```text
定义服务拆分后的目标结构，并写出五阶段迁移、验证和回滚计划。
```

以本 Skill 为主先记录目标边界和关系，再组合 `project-docs-planning` 写实施 Plan；Plan 链接目标 architecture，不复制组件说明。
