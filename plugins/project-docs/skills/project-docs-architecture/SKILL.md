---
name: project-docs-architecture
description: Use only when explicitly requested to document architecture, source relationships, technical mechanisms, or significant decisions using C4 and focused diagrams.
---

# 技术文档与架构

仅在用户显式调用本技能时使用。读取[共同写作约定](../project-docs-progress/references/writing-style.md)，按任务读取相关代码、配置和现有技术入口，用实际实现支撑说明，不因文档任务通读全仓库。

| 当前任务 | 按需读取 |
| --- | --- |
| 架构、组件、流程或源码关系 | [C4 与源码导航](references/architecture-diagrams.md)、[技术页示例](assets/technical-templates.md) |
| 判断或记录重要决定 | [ADR 规则与模板](references/adrs.md) |

默认维护最近核对过的当前实现；参考 spec 理解意图，但不能将未实现规格写成当前行为。实质差异指出或作为待处理任务，不擅改 spec 或源码。用户明确要求目标架构时标为目标，并与当前状态分开。

按里程碑收尾、已计划的中途节点或发布节点更新；普通代码任务完成不自动触发全篇同步。核对 TODO 中文档同步条目，只改受影响部分；直接阻碍当前工作的错误可以及时修复。没有变化无需改正文。

技术入口标明最近核对的里程碑或版本，并链接 TODO 的后续工作，不逐任务追加过期提醒。已实现并核对的代码不因尚未发布被写成未来状态。

检查实际修改的图和说明是否符合代码、是否可读；可用时渲染改动图，无法渲染就说明限制。不重验未改图，不另建技术文档验收报告。ADR 改名或移动才检查受影响引用，保持历史决定。
