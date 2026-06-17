# Vibekits

[![Version](https://img.shields.io/badge/version-1.1.1-2563EB)](../plugins/laxpud-vibekits/.codex-plugin/plugin.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](../LICENSE)
[![Skills](https://img.shields.io/badge/skills-3-brightgreen)](#已收录技能)
[![Codex Plugin](https://img.shields.io/badge/Codex-Plugin-111827)](../.agents/plugins/marketplace.json)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-D97706)](../.claude-plugin/marketplace.json)
[![Platform Neutral](https://img.shields.io/badge/platform-neutral-0F766E)](SKILL_RULE_GUIDELINES.md)

Vibekits 是一组平台无关的可复用 agent skills 和 rules，适用于 Codex、Claude Code 以及兼容 `SKILL.md` 的工作流。

这个仓库有意保持文档优先：共享技能来源只放在一个插件包中，Codex 和 Claude Code 的适配层都指向同一份来源，不把平台专属逻辑写进通用技能。

## 当前状态

- 当前插件版本：`1.1.1`。
- 已收录技能：代码注释标准、Python `pyproject.toml` 标准、项目文档引导。
- 本仓库没有构建步骤；验证重点是 JSON 清单、技能元数据、Markdown 链接和仓库结构。

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
Use project-docs-bootstrap to reorganize this repository docs.
```

### Codex

```bash
codex plugin marketplace add Laxpud/my-awesome-vibekits
codex
/plugins
```

在插件列表中选择 `laxpud-vibekits`。开启新线程后，可以直接描述任务，或显式引用插件/技能。

### 手动浏览

```bash
git clone https://github.com/Laxpud/my-awesome-vibekits.git
```

常用入口：

- [`docs/index.md`](index.md)：技术文档索引。
- [`docs/README.cn.md`](README.cn.md)：根 README 的中文翻译。
- [`docs/SKILL_RULE_GUIDELINES.md`](SKILL_RULE_GUIDELINES.md)：技能、规则和适配层维护规范。
- [`TODO.md`](../TODO.md)：当前活跃维护事项。

## 已收录技能

| Skill | 适用场景 | 提供内容 |
| --- | --- | --- |
| [`code-comment-standard`](../plugins/laxpud-vibekits/skills/code-comment-standard/SKILL.md) | 需要生成、审查、补全或规范代码注释、docstring、TODO、公共 API 文档时。 | 跨语言注释层级、质量标准、反模式和维护者视角的注释流程。 |
| [`project-docs-bootstrap`](../plugins/laxpud-vibekits/skills/project-docs-bootstrap/SKILL.md) | 新项目、早期项目或文档混乱的仓库需要明确 README、TODO、docs 和项目 guidance 边界时。 | 公开入口文档、活跃 TODO、技术文档、归档边界和协作说明的整理流程。 |
| [`pyproject-standard`](../plugins/laxpud-vibekits/skills/pyproject-standard/SKILL.md) | 创建或修改 Python 项目的 `pyproject.toml` 时。 | `uv`、`hatchling`、动态版本、许可证、依赖、分类器、脚本入口和包索引配置标准。 |

## 已收录规则

| Rule | 用途 |
| --- | --- |
| [`codex-user-global-rules`](../rules/codex-user-global-rules.md) | Codex 用户全局规则备份，用于个人迁移和版本留档；它不是平台无关通用规则。 |

## 仓库原则

- **平台无关核心**：共享技能和可复用规则不得依赖特定 AI 助手、IDE 或运行时。
- **适配层隔离**：Claude Code 配置放在 `.claude-plugin/` 和 `plugins/laxpud-vibekits/.claude-plugin/`；Codex 配置放在 `.agents/` 和 `plugins/laxpud-vibekits/.codex-plugin/`。
- **单一技能来源**：`plugins/laxpud-vibekits/skills/` 是唯一技能来源，禁止创建根目录 `skills/` 副本。
- **明确标注备份**：个人全局规则备份可以放在 `rules/`，但文件名和开头说明必须标注备份用途。

## 仓库结构

```text
plugins/laxpud-vibekits/
  .claude-plugin/      # Claude Code plugin manifest
  .codex-plugin/       # Codex plugin manifest
  skills/              # shared skill source of truth
.claude-plugin/        # Claude Code marketplace index
.agents/plugins/       # Codex marketplace index
rules/                 # reusable rules and clearly labeled backups
docs/                  # technical docs, Chinese README, and maintenance notes
```

## 贡献

新增或修改技能和规则时：

- 新技能放在 `plugins/laxpud-vibekits/skills/<skill-name>/SKILL.md`。
- 可复用规则放在 `rules/<rule-name>.md`，并保持短小、清晰、平台无关。
- 技能能力或描述变化时，同步技能表、Claude/Codex plugin manifest 和 marketplace 元数据。
- 平台专属行为不要写进共享 `SKILL.md`。
- 发布前验证 JSON 清单、Markdown 链接、技能 frontmatter 和 Git diff。

## 许可证

MIT License. See [LICENSE](../LICENSE).
