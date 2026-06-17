# Vibekits

[![Version](https://img.shields.io/badge/version-1.1.1-2563EB)](plugins/laxpud-vibekits/.codex-plugin/plugin.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-3-brightgreen)](#included-skills)
[![Codex Plugin](https://img.shields.io/badge/Codex-Plugin-111827)](.agents/plugins/marketplace.json)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-D97706)](.claude-plugin/marketplace.json)
[![Platform Neutral](https://img.shields.io/badge/platform-neutral-0F766E)](docs/SKILL_RULE_GUIDELINES.md)
[![中文](https://img.shields.io/badge/README-中文-C026D3)](docs/README.cn.md)

Vibekits is a platform-neutral collection of reusable agent skills and rules for Codex, Claude Code, and `SKILL.md`-compatible workflows.

The repository is intentionally documentation-first: the shared skill source lives in one plugin package, while Codex and Claude Code adapters point to that same source without adding platform-specific logic to the skills.

## Current Status

- Current plugin version: `1.1.1`.
- Included skills: code comment standards, Python `pyproject.toml` standards, and project documentation bootstrapping.
- No build step is required; validation focuses on JSON manifests, skill metadata, Markdown links, and repository structure.

## Start Here

If you want to try one capability first:

- Organize project documentation with [`project-docs-bootstrap`](plugins/laxpud-vibekits/skills/project-docs-bootstrap/SKILL.md).
- Standardize code comments with [`code-comment-standard`](plugins/laxpud-vibekits/skills/code-comment-standard/SKILL.md).
- Create or review `pyproject.toml` with [`pyproject-standard`](plugins/laxpud-vibekits/skills/pyproject-standard/SKILL.md).

## Quick Install

### Claude Code

```bash
/plugin marketplace add https://github.com/Laxpud/my-awesome-vibekits
/plugin install laxpud-vibekits@laxpud-vibekits-dev
```

After installation, start a new session and describe the task directly, or explicitly ask for a skill:

```text
Use project-docs-bootstrap to reorganize this repository docs.
```

### Codex

```bash
codex plugin marketplace add Laxpud/my-awesome-vibekits
codex
/plugins
```

Choose `laxpud-vibekits` from the plugin list. In a new thread, describe the task directly or explicitly reference the plugin or skill.

### Manual Browse

```bash
git clone https://github.com/Laxpud/my-awesome-vibekits.git
```

Useful entry points:

- [`docs/index.md`](docs/index.md): technical documentation index.
- [`docs/README.cn.md`](docs/README.cn.md): Chinese translation of this README.
- [`docs/SKILL_RULE_GUIDELINES.md`](docs/SKILL_RULE_GUIDELINES.md): skill, rule, and adapter maintenance rules.
- [`TODO.md`](TODO.md): active maintenance work.

## Included Skills

| Skill | Use when | What it provides |
| --- | --- | --- |
| [`code-comment-standard`](plugins/laxpud-vibekits/skills/code-comment-standard/SKILL.md) | You need to generate, review, complete, or standardize comments, docstrings, TODOs, or public API documentation. | Cross-language comment levels, quality standards, anti-patterns, and a maintainer-oriented commenting workflow. |
| [`project-docs-bootstrap`](plugins/laxpud-vibekits/skills/project-docs-bootstrap/SKILL.md) | A new, early-stage, or messy repository needs clear README, TODO, docs, and project guidance boundaries. | A workflow for public entry docs, active TODOs, technical docs, archive boundaries, and collaboration guidance. |
| [`pyproject-standard`](plugins/laxpud-vibekits/skills/pyproject-standard/SKILL.md) | You are creating or editing a Python project's `pyproject.toml`. | Standards for `uv`, `hatchling`, dynamic versions, licenses, dependencies, classifiers, scripts, and package index configuration. |

## Included Rules

| Rule | Purpose |
| --- | --- |
| [`codex-user-global-rules`](rules/codex-user-global-rules.md) | A personal Codex global-rules backup for migration and version history. It is not a platform-neutral shared rule. |

## Repository Principles

- **Platform-neutral core**: shared skills and reusable rules must not depend on a specific AI assistant, IDE, or runtime.
- **Adapter isolation**: Claude Code configuration lives in `.claude-plugin/` and `plugins/laxpud-vibekits/.claude-plugin/`; Codex configuration lives in `.agents/` and `plugins/laxpud-vibekits/.codex-plugin/`.
- **Single skill source**: `plugins/laxpud-vibekits/skills/` is the only skill source. Do not create a root `skills/` copy.
- **Explicit backups**: personal global-rule backups may live in `rules/`, but their filenames and opening notes must mark them as backups.

## Repository Layout

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

## Contributing

When adding or changing skills and rules:

- Put new skills in `plugins/laxpud-vibekits/skills/<skill-name>/SKILL.md`.
- Put reusable rules in `rules/<rule-name>.md`, and keep them short, clear, and platform-neutral.
- Update the skill table, Claude/Codex plugin manifests, and marketplace metadata when a skill's capability or description changes.
- Keep platform-specific behavior out of shared `SKILL.md` files.
- Validate JSON manifests, Markdown links, skill frontmatter, and Git diff before publishing.

## License

MIT License. See [LICENSE](LICENSE).
