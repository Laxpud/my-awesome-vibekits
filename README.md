# Vibekits

[![Version](https://img.shields.io/badge/version-1.1.1-2563EB)](plugins/laxpud-vibekits/.codex-plugin/plugin.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-3-brightgreen)](plugins/laxpud-vibekits/skills)
[![Codex Plugin](https://img.shields.io/badge/Codex-Plugin-111827)](.agents/plugins/marketplace.json)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-D97706)](.claude-plugin/marketplace.json)
[![Platform Neutral](https://img.shields.io/badge/platform-neutral-0F766E)](docs/SKILL_RULE_GUIDELINES.md)

Vibekits 是一组平台无关的 reusable skills 和 rules，用来沉淀跨项目可复用的 Agent 工作流。

Platform-neutral reusable skills and rules for Codex, Claude Code, and `SKILL.md`-compatible agent workflows.

## Start Here

如果只想先试一个能力：

- 整理项目文档：用 [`project-docs-bootstrap`](plugins/laxpud-vibekits/skills/project-docs-bootstrap/SKILL.md)。
- 规范代码注释：用 [`code-comment-standard`](plugins/laxpud-vibekits/skills/code-comment-standard/SKILL.md)。
- 创建或检查 `pyproject.toml`：用 [`pyproject-standard`](plugins/laxpud-vibekits/skills/pyproject-standard/SKILL.md)。

本仓库的共享内容保持平台无关。Claude Code 和 Codex 只通过各自的 marketplace/plugin manifest 读取同一份 `plugins/laxpud-vibekits/skills/`。

## Quick Install

### Claude Code

```bash
/plugin marketplace add https://github.com/Laxpud/my-awesome-vibekits
/plugin install laxpud-vibekits@laxpud-vibekits-dev
```

安装后开启新会话，可以直接描述任务，也可以显式要求使用某个 skill，例如：

```text
Use project-docs-bootstrap to reorganize this repository docs.
```

### Codex

```bash
codex plugin marketplace add Laxpud/my-awesome-vibekits
codex
/plugins
```

在插件目录中选择 `laxpud-vibekits` 安装。安装后开启新线程，可直接描述任务，或使用 `@` 显式调用插件/技能。

### Manual Browse

```bash
git clone https://github.com/Laxpud/my-awesome-vibekits.git
```

克隆后直接浏览：

- `plugins/laxpud-vibekits/skills/`：通用技能。
- `rules/`：可复用规则和明确标注的个人备份。
- `docs/`：维护规范和文档索引。

## Included Skills

| Skill | Use when | What it provides |
| --- | --- | --- |
| [`code-comment-standard`](plugins/laxpud-vibekits/skills/code-comment-standard/SKILL.md) | 需要生成、补全、审查或整改代码注释、docstring、TODO、公共 API 文档时。 | 跨语言注释层级、质量标准、禁止事项和维护者视角的注释流程。 |
| [`project-docs-bootstrap`](plugins/laxpud-vibekits/skills/project-docs-bootstrap/SKILL.md) | 新项目、早期项目或文档混乱的仓库需要建立 README/TODO/docs/AGENTS 边界时。 | 文档入口、活跃 TODO、技术 docs、归档边界和项目协作说明的整理流程。 |
| [`pyproject-standard`](plugins/laxpud-vibekits/skills/pyproject-standard/SKILL.md) | 创建或修改 Python 项目的 `pyproject.toml` 时。 | `uv`、`hatchling`、动态版本、许可证、依赖、分类器、脚本入口和镜像配置标准。 |

## Included Rules

| Rule | Purpose |
| --- | --- |
| [`codex-user-global-rules`](rules/codex-user-global-rules.md) | Codex 用户全局规则备份，用于个人迁移和版本留档；它不是平台无关通用规则。 |

## Repository Principles

- **Platform-neutral core**：通用技能和可复用规则不绑定任何 AI 助手、IDE 或运行时。
- **Adapter isolation**：Claude Code 专属配置只放在 `.claude-plugin/` 和 `plugins/laxpud-vibekits/.claude-plugin/`；Codex 专属配置只放在 `.agents/` 和 `plugins/laxpud-vibekits/.codex-plugin/`。
- **Single skill source**：`plugins/laxpud-vibekits/skills/` 是唯一技能来源，禁止再创建根目录 `skills/` 副本。
- **Explicit backups**：个人全局规则备份可以放在 `rules/`，但文件名和开头说明必须标注备份用途。

## Repository Layout

```text
plugins/laxpud-vibekits/
  .claude-plugin/      # Claude Code plugin manifest
  .codex-plugin/       # Codex plugin manifest
  skills/              # shared skill source of truth
.claude-plugin/        # Claude Code marketplace index
.agents/plugins/       # Codex marketplace index
rules/                 # reusable rules and clearly labeled backups
docs/                  # maintenance docs and documentation index
```

更多维护说明见 [docs/README.md](docs/README.md) 和 [docs/SKILL_RULE_GUIDELINES.md](docs/SKILL_RULE_GUIDELINES.md)。当前活跃事项见 [TODO.md](TODO.md)。

## Contributing

欢迎添加新的技能或改进现有内容。提交前请检查：

- 新技能位于 `plugins/laxpud-vibekits/skills/<skill-name>/SKILL.md`。
- 新规则位于 `rules/<rule-name>.md`，且保持短小、清晰、平台无关。
- 技能能力或描述变化时，同步 README 技能表、Claude/Codex plugin manifest 和 marketplace 描述。
- 平台专属逻辑没有写进共享 `SKILL.md`。
- JSON 文件可解析，链接路径有效，未混入缓存、虚拟环境或本地测试输出。

## License

MIT License. See [LICENSE](LICENSE).
