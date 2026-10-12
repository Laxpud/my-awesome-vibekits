# 项目文档索引

Vibekits 维护外部插件市场。用户介绍与安装入口在根 README，活动任务在 TODO；插件技能、使用说明、设计与审查分别在独立仓库维护。

## 项目入口

| 文档 | 用途 |
| --- | --- |
| [README.md](../README.md) / [中文 README](README.cn.md) | 项目定位、插件与技能选择、安装和旧安装迁移。 |
| [TODO.md](../TODO.md) | 当前任务、验收条件、未来方向及必要状态。 |
| [plugin-catalog.json](../plugin-catalog.json) | 外部来源、版本与完整 Skill 收录快照，以及双端市场展示配置。 |

## 市场维护

| 文档 | 用途 |
| --- | --- |
| [Catalog 与适配层规范](SKILL_RULE_GUIDELINES.md) | 外部来源、展示元数据、快照回填与两端生成契约。 |
| [发布与市场更新](PLUGIN_UPDATE.md) | 独立仓库发布、本市场更新、旧安装迁移和验证边界。 |
| [Codex 安装检查](CODEX_INSTALL_SMOKE_TEST.md) | 本地市场、外部包与已发布入口的检查流程。 |
| [AGENTS.md](../AGENTS.md) / [CLAUDE.md](../CLAUDE.md) | AI 工作路由；CLAUDE.md 为相对软链。 |

## 独立插件资料

| 插件 | 维护入口 |
| --- | --- |
| Agent Docs Maintainer | [仓库](https://github.com/Laxpud/agent-docs-maintainer)；[使用说明、设计与历史审查](https://github.com/Laxpud/agent-docs-maintainer/blob/main/docs/index.md)。 |
| Agent Task Resume | [仓库与执行资料](https://github.com/Laxpud/agent-task-resume)。 |
| Agent Dev Standards | [仓库](https://github.com/Laxpud/agent-dev-standards)；[原始例库与历史审查](https://github.com/Laxpud/agent-dev-standards/blob/main/docs/index.md)。 |

## 里程碑归档

[2026-08-13 多插件目录与分发](archive/2026-08-13-codex-claude-multi-plugin-distribution.md)保留当时的完成清单与布局，不作为当前插件维护规则。

## 文档所有权

README 维护公开介绍，TODO 维护活动状态，docs/ 的具名文件维护稳定市场规则，AGENTS.md 仅保留路由与高风险边界。插件内容与其专属资料只在独立仓库维护；本市场不保留第二份技能包、维护源或历史审查副本。
