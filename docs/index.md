# 项目文档索引

本文件是 Vibekits 项目文档的技术导航入口。面向用户的介绍与最短使用路径在根 `README.md`；活动任务和验收状态在 `TODO.md`。

## 项目入口

| 文档 | 用途 |
| --- | --- |
| [`README.md`](../README.md) | 英文公开入口：项目定位、能力、支持环境和最短使用路径。 |
| [`README.cn.md`](README.cn.md) | 根 README 的中文翻译，与英文版同步维护。 |
| [`TODO.md`](../TODO.md) | 当前里程碑、活动任务、验收条件、完成证据和状态维护规则。 |
| [`plugin-catalog.json`](../plugin-catalog.json) | 插件身份、独立版本、Skill 路径和双端分发元数据的唯一事实来源。 |

## 维护文档

| 文档 | 修改什么内容前先读 |
| --- | --- |
| [`SKILL_RULE_GUIDELINES.md`](SKILL_RULE_GUIDELINES.md) | 通用技能、可复用规则、插件适配层、同步目标或静态验证。 |
| [`PLUGIN_UPDATE.md`](PLUGIN_UPDATE.md) | 插件版本发布、隔离 E2E、客户端更新、日常晋级或回滚。 |
| [`CODEX_INSTALL_SMOKE_TEST.md`](CODEX_INSTALL_SMOKE_TEST.md) | Codex marketplace、manifest 或 README 安装说明。 |

## AI 工作入口

| 文件 | 用途 |
| --- | --- |
| [`AGENTS.md`](../AGENTS.md) | Codex 的快速路由、工作流触发器和少量高风险边界。 |
| [`CLAUDE.md`](../CLAUDE.md) | Claude Code 的快速路由、工作流触发器和少量高风险边界。 |

## 里程碑归档

| 文档 | 内容 |
| --- | --- |
| [`2026-08-13-codex-claude-multi-plugin-distribution.md`](archive/2026-08-13-codex-claude-multi-plugin-distribution.md) | 统一 catalog、三插件拆分、双端生成和验证门禁的完成记录。 |

## 文档所有权

| 内容 | 权威位置 |
| --- | --- |
| 面向用户的项目介绍、能力、环境和最短使用路径 | 根 `README.md` |
| 活动任务、里程碑、验收条件和状态维护流程 | 根 `TODO.md` |
| 架构、配置、测试、发布流程和其他稳定技术细节 | `docs/` 下的具名技术文档 |
| AI 工作入口、文档与代码路由、工作流触发器和少量高风险边界 | `AGENTS.md`、`CLAUDE.md` |

项目指导文件应链接上述权威位置，不复制 README、TODO 或专题技术文档的详细内容。已完成里程碑只有在 `TODO.md` 顶部规则允许后，才能归档到 `docs/archive/`。
