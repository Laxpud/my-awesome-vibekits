# 项目文档

Vibekits 维护外部插件的 Codex 与 Claude Code 聚合市场。按你要完成的事情选择入口；每类信息只在下表所列位置维护。

## 使用插件

从 [README](../README.md) 或[中文 README](README.cn.md)了解用途、完成安装并浏览插件与技能目录。十个技能均提供一句话介绍和操作说明链接，具体用法与示例在对应独立仓库维护。

技能的详细操作、模板、写作规则与执行资料见下方独立插件资料。旧安装迁移见[维护指南的迁移对应表](maintenance.md#客户端更新与旧安装迁移)。

## 维护市场

先读[架构总览](tech/architecture.md)理解独立仓库、catalog 和两端 marketplace 的关系，再按[维护指南](maintenance.md)更新收录、验证或回退。修改插件内容时转到对应独立仓库。

| 维护位置 | 唯一负责的内容 |
| --- | --- |
| [plugin-catalog.json](../plugin-catalog.json) | 本市场的来源、收录快照、完整技能清单与平台策略。 |
| [架构总览](tech/architecture.md) | 当前实现、字段契约、生成与回填机理、源码映射和检查边界。 |
| [维护指南](maintenance.md) | 更新、新增、验证、市场发布、客户端迁移与回退操作。 |
| [AGENTS.md](../AGENTS.md) / [CLAUDE.md](../CLAUDE.md) | AI 阅读路由和必要项目边界，共用一份正文。 |

## 查看进展

[TODO](../TODO.md)维护当前任务、完成条件与状态规则；[路线图](roadmap.md)维护未来工作、候选方向和已完成里程碑入口。完成清单及旧历史保存在 `docs/archive/`，不作为当前维护操作说明。

## 独立插件资料

| 插件 | 内容维护入口 |
| --- | --- |
| Agent Docs Maintainer | [仓库](https://github.com/Laxpud/agent-docs-maintainer)、[使用说明](https://github.com/Laxpud/agent-docs-maintainer/blob/main/docs/usage.md)、[技术资料与历史设计、审查](https://github.com/Laxpud/agent-docs-maintainer/blob/main/docs/index.md)。 |
| Agent Task Resume | [仓库、技能与执行资料](https://github.com/Laxpud/agent-task-resume)。 |
| Agent Dev Standards | [仓库](https://github.com/Laxpud/agent-dev-standards)、[原始例库与历史审查](https://github.com/Laxpud/agent-dev-standards/blob/main/docs/index.md)。 |

本市场不复制插件正文、例库或专属设计。历史原文通过独立仓库和 Git 历史查阅，旧插件名称只在迁移说明及历史记录中使用。
