# Vibekits

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](../LICENSE)
[![Plugins](https://img.shields.io/badge/plugins-3-2563EB)](../plugin-catalog.json)
[![Skills](https://img.shields.io/badge/skills-3-brightgreen)](#已收录插件与技能)
[![Codex Marketplace](https://img.shields.io/badge/Codex-Marketplace-111827)](../.agents/plugins/marketplace.json)
[![Claude Code Marketplace](https://img.shields.io/badge/Claude%20Code-Marketplace-D97706)](../.claude-plugin/marketplace.json)
[![English](https://img.shields.io/badge/README-English-C026D3)](../README.md)

Vibekits 是面向 Codex 和 Claude Code 的独立、平台无关工作流插件目录。每个插件拥有一个可复用技能，可以单独安装、升级、禁用、卸载或回滚，不改变兄弟插件。

仓库使用唯一的 [`plugin-catalog.json`](../plugin-catalog.json) 作为分发事实来源，由它生成两端 marketplace 和每个插件的 Codex、Claude Code manifest；插件自己的 `skills/` 目录始终是技能内容的唯一来源。

## 当前状态

- marketplace 提供三个独立版本插件：`code-quality`、`python-project` 和 `project-docs`。
- 原 `laxpud-vibekits` 聚合插件已删除。本次拆分有意不提供 deprecated bundle、别名或迁移兼容层。
- 验证覆盖 catalog 冲突、生成物漂移、两端 manifest、README 安装路径，以及隔离的三插件生命周期与回滚行为。

## 从这里开始

如果只想先试一个能力：

- 用 `project-docs` 中的 [`project-docs-bootstrap`](../plugins/project-docs/skills/project-docs-bootstrap/SKILL.md) 整理项目文档。
- 用 `code-quality` 中的 [`code-comment-standard`](../plugins/code-quality/skills/code-comment-standard/SKILL.md) 规范代码注释。
- 用 `python-project` 中的 [`pyproject-standard`](../plugins/python-project/skills/pyproject-standard/SKILL.md) 创建或检查 `pyproject.toml`。

## 快速安装

### Claude Code

```bash
/plugin marketplace add https://github.com/Laxpud/my-awesome-vibekits
/plugin install code-quality@laxpud-vibekits
/plugin install python-project@laxpud-vibekits
/plugin install project-docs@laxpud-vibekits
```

只需安装需要的插件。安装后开启新会话，可以直接描述任务，也可以显式要求使用某个 skill：

```text
使用 project-docs-bootstrap 按文档所有权规则整理这个仓库。
```

### Codex

```bash
codex plugin marketplace add Laxpud/my-awesome-vibekits
codex
/plugins
```

在插件列表中选择 `code-quality`、`python-project` 和/或 `project-docs`，各选择彼此独立。安装或升级后新建任务，让所选技能重新加载。

### 手动浏览

```bash
git clone https://github.com/Laxpud/my-awesome-vibekits.git
```

克隆后，从 [技术文档索引](index.md)、[插件 catalog](../plugin-catalog.json) 或 [当前里程碑](../TODO.md) 开始。

## 已收录插件与技能

| 插件 | Skill | 适用场景 | 提供内容 |
| --- | --- | --- | --- |
| `code-quality` | [`code-comment-standard`](../plugins/code-quality/skills/code-comment-standard/SKILL.md) | 需要生成、审查、补全或规范代码注释、docstring、TODO 或公共 API 文档时。 | 跨语言注释层级、质量标准、反模式和维护者视角的注释流程。 |
| `python-project` | [`pyproject-standard`](../plugins/python-project/skills/pyproject-standard/SKILL.md) | 创建或修改 Python 项目的 `pyproject.toml` 时。 | `uv`、`hatchling`、动态版本、许可证、依赖、分类器、脚本入口和包索引配置标准。 |
| `project-docs` | [`project-docs-bootstrap`](../plugins/project-docs/skills/project-docs-bootstrap/SKILL.md) | 仓库需要明确文档所有权、里程碑式 TODO 工作流或简短的项目指导路由时。 | README/TODO/docs 所有权、里程碑验收规则、项目指导文件审查，以及归档和目录 README 边界。 |

## 已收录规则

| Rule | 用途 |
| --- | --- |
| [`codex-user-global-rules`](../rules/codex-user-global-rules.md) | Codex 用户全局规则备份，用于个人迁移和版本留档；它不是平台无关通用规则。 |

## 维护

- 使用 [`docs/index.md`](index.md) 查找某类改动的权威技术文档。
- 修改技能、catalog 或生成的适配层元数据前，先读 [`docs/SKILL_RULE_GUIDELINES.md`](SKILL_RULE_GUIDELINES.md)。
- 独立版本、发布、客户端更新和回滚遵循 [`docs/PLUGIN_UPDATE.md`](PLUGIN_UPDATE.md)。
- 修改 Codex marketplace 元数据或安装说明后，遵循 [`docs/CODEX_INSTALL_SMOKE_TEST.md`](CODEX_INSTALL_SMOKE_TEST.md)。
- 在 [`TODO.md`](../TODO.md) 中维护活动工作、验收条件和完成证据。

## 许可证

MIT License. 参见 [LICENSE](../LICENSE)。
