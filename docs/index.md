# 项目文档索引

本文件是 Vibekits 项目文档的技术导航入口。面向用户的介绍与最短使用路径在根 `README.md`；活动任务和验收状态在 `TODO.md`。

## 项目入口

| 文档 | 用途 |
| --- | --- |
| [`README.md`](../README.md) | 英文公开入口：项目定位、能力、支持环境和最短使用路径。 |
| [`README.cn.md`](README.cn.md) | 根 README 的中文翻译，与英文版同步维护。 |
| [`使用说明`](usage.md) | 文档技能的选择、进度维护方式与按需操作示例。 |
| [`TODO.md`](../TODO.md) | 当前里程碑、活动任务、验收条件、必要验证结论和状态维护规则。 |
| [`plugin-catalog.json`](../plugin-catalog.json) | 插件身份、独立版本、Skill 路径和双端分发元数据的唯一事实来源。 |

## 维护文档

| 文档 | 修改什么内容前先读 |
| --- | --- |
| [`SKILL_RULE_GUIDELINES.md`](SKILL_RULE_GUIDELINES.md) | 技能维护源与安装文件、插件 catalog、平台适配层、生成步骤或静态验证。 |
| [`PLUGIN_UPDATE.md`](PLUGIN_UPDATE.md) | 插件版本发布、隔离 E2E、客户端更新、日常晋级或回滚。 |
| [`CODEX_INSTALL_SMOKE_TEST.md`](CODEX_INSTALL_SMOKE_TEST.md) | Codex marketplace、manifest 或 README 安装说明。 |

## 设计与决策

| 文档 | 内容 |
| --- | --- |
| [`project-docs 改造设计`](design/project-docs-multi-skill.md) | 已在源码中实施、尚未发布的七技能分工、文档模板与生命周期、C4 技术说明、共享写作规则和轻量验收。 |
| [`ADR 0001：按用户意图拆分 project-docs`](adr/0001-split-project-docs-by-user-intent.md) | 记录从单一综合 Skill 直接迁移到六个独立 Skill 的决定与后果。 |

## 技能指令审查记录

以下记录保存 2026-09-24 整理的既有审查问题与建议方向，不作为新的执行规则。活动工作仍以 `TODO.md` 为入口。

| 插件 | 问题记录 |
| --- | --- |
| `code-quality` | [注释技能的分层、阅读范围与重复询问](reviews/2026-09-24-code-quality.md) |
| `python-project` | [配置技能的无条件元数据问答](reviews/2026-09-24-python-project.md) |
| `project-docs` | [文档技能的盘点范围与验证触发条件](reviews/2026-09-24-project-docs.md) |

## AI 工作入口

| 文件 | 用途 |
| --- | --- |
| [`AGENTS.md`](../AGENTS.md) | Codex 的快速路由、工作流触发器和少量高风险边界。 |
| [`CLAUDE.md`](../CLAUDE.md) | 指向 AGENTS.md 的相对软链，不单独维护正文。 |

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
| AI 工作入口、文档与代码路由、工作流触发器和少量高风险边界 | `AGENTS.md`（`CLAUDE.md` 为软链） |

项目指导文件应链接上述权威位置，不复制 README、TODO 或专题技术文档的详细内容。已完成里程碑只有在 `TODO.md` 顶部规则允许后，才能归档到 `docs/archive/`。
