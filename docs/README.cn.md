# Vibekits

[![Version](https://img.shields.io/badge/version-1.1.2-2563EB)](../plugins/laxpud-vibekits/.codex-plugin/plugin.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](../LICENSE)
[![Skills](https://img.shields.io/badge/skills-3-brightgreen)](#已收录技能)
[![Codex Plugin](https://img.shields.io/badge/Codex-Plugin-111827)](../.agents/plugins/marketplace.json)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-D97706)](../.claude-plugin/marketplace.json)
[![Platform Neutral](https://img.shields.io/badge/platform-neutral-0F766E)](SKILL_RULE_GUIDELINES.md)
[![English](https://img.shields.io/badge/README-English-C026D3)](../README.md)

Vibekits 是一组平台无关的可复用 agent skills 和 rules，适用于 Codex、Claude Code 以及兼容 `SKILL.md` 的工作流。

这个仓库有意保持文档优先：共享插件包是可复用技能的唯一来源，Codex 和 Claude Code 适配层暴露同一份来源，不把平台专属逻辑写入通用技能。

## 当前状态

- 当前插件版本：`1.1.2`。
- 已收录技能覆盖代码注释、Python `pyproject.toml`，以及项目文档所有权和维护工作流。
- 本仓库以文档形式分发，没有构建步骤；验证重点是插件元数据、技能结构、Markdown 链接和更新工具。

## 从这里开始

如果只想先试一个能力：

- 用 [`project-docs-bootstrap`](../plugins/laxpud-vibekits/skills/project-docs-bootstrap/SKILL.md) 整理项目文档。
- 用 [`code-comment-standard`](../plugins/laxpud-vibekits/skills/code-comment-standard/SKILL.md) 规范代码注释。
- 用 [`pyproject-standard`](../plugins/laxpud-vibekits/skills/pyproject-standard/SKILL.md) 创建或检查 `pyproject.toml`。

## 快速安装

### Claude Code

```bash
/plugin marketplace add https://github.com/Laxpud/my-awesome-vibekits
/plugin install laxpud-vibekits@laxpud-vibekits-dev
```

安装后开启新会话，可以直接描述任务，也可以显式要求使用某个 skill：

```text
使用 project-docs-bootstrap 按文档所有权规则整理这个仓库。
```

### Codex

```bash
codex plugin marketplace add Laxpud/my-awesome-vibekits
codex
/plugins
```

在插件列表中选择 `laxpud-vibekits`。开启新线程后，可以直接描述任务，或显式引用插件或技能。

### 手动浏览

```bash
git clone https://github.com/Laxpud/my-awesome-vibekits.git
```

克隆后，从 [技术文档索引](index.md) 或 [当前里程碑](../TODO.md) 开始。

## 已收录技能

| Skill | 适用场景 | 提供内容 |
| --- | --- | --- |
| [`code-comment-standard`](../plugins/laxpud-vibekits/skills/code-comment-standard/SKILL.md) | 需要生成、审查、补全或规范代码注释、docstring、TODO 或公共 API 文档时。 | 跨语言注释层级、质量标准、反模式和维护者视角的注释流程。 |
| [`project-docs-bootstrap`](../plugins/laxpud-vibekits/skills/project-docs-bootstrap/SKILL.md) | 仓库需要明确文档所有权、里程碑式 TODO 工作流或简短的项目指导路由时。 | README/TODO/docs 所有权、里程碑验收规则、项目指导文件审查，以及归档和目录 README 边界。 |
| [`pyproject-standard`](../plugins/laxpud-vibekits/skills/pyproject-standard/SKILL.md) | 创建或修改 Python 项目的 `pyproject.toml` 时。 | `uv`、`hatchling`、动态版本、许可证、依赖、分类器、脚本入口和包索引配置标准。 |

## 已收录规则

| Rule | 用途 |
| --- | --- |
| [`codex-user-global-rules`](../rules/codex-user-global-rules.md) | Codex 用户全局规则备份，用于个人迁移和版本留档；它不是平台无关通用规则。 |

## 维护

- 使用 [`docs/index.md`](index.md) 查找某类改动的权威技术文档。
- 修改技能、规则或适配层元数据前，先读 [`docs/SKILL_RULE_GUIDELINES.md`](SKILL_RULE_GUIDELINES.md)。
- 插件发布和客户端更新遵循 [`docs/PLUGIN_UPDATE.md`](PLUGIN_UPDATE.md)。
- 修改 Codex 安装元数据或说明后，遵循 [`docs/CODEX_INSTALL_SMOKE_TEST.md`](CODEX_INSTALL_SMOKE_TEST.md)。
- 在 [`TODO.md`](../TODO.md) 中维护活动工作、验收条件和完成证据。

## 许可证

MIT License. 参见 [LICENSE](../LICENSE)。
