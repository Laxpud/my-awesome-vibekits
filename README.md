# Vibekits

[![Version](https://img.shields.io/badge/version-1.1.2-2563EB)](plugins/laxpud-vibekits/.codex-plugin/plugin.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-3-brightgreen)](#included-skills)
[![Codex Plugin](https://img.shields.io/badge/Codex-Plugin-111827)](.agents/plugins/marketplace.json)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-D97706)](.claude-plugin/marketplace.json)
[![Platform Neutral](https://img.shields.io/badge/platform-neutral-0F766E)](docs/SKILL_RULE_GUIDELINES.md)
[![中文](https://img.shields.io/badge/README-中文-C026D3)](docs/README.cn.md)

Vibekits is a platform-neutral collection of reusable agent skills and rules for Codex, Claude Code, and `SKILL.md`-compatible workflows.

The repository is intentionally documentation-first: one shared plugin package owns the reusable skills, while Codex and Claude Code adapters expose that same source without adding platform-specific logic to the skills.

## Current Status

- Current plugin version: `1.1.2`.
- Included skills cover code comments, Python `pyproject.toml`, and project documentation ownership and maintenance workflows.
- Distribution is documentation-only; there is no build step, and repository validation focuses on plugin metadata, skill structure, Markdown links, and update tooling.

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
Use project-docs-bootstrap to reorganize this repository documentation.
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

After cloning, start with the [technical documentation index](docs/index.md) or the [active milestone](TODO.md).

## Included Skills

| Skill | Use when | What it provides |
| --- | --- | --- |
| [`code-comment-standard`](plugins/laxpud-vibekits/skills/code-comment-standard/SKILL.md) | You need to generate, review, complete, or standardize comments, docstrings, TODOs, or public API documentation. | Cross-language comment levels, quality standards, anti-patterns, and a maintainer-oriented commenting workflow. |
| [`project-docs-bootstrap`](plugins/laxpud-vibekits/skills/project-docs-bootstrap/SKILL.md) | A repository needs clear documentation ownership, milestone-driven TODO workflows, or concise project-guidance routes. | README/TODO/docs ownership, milestone acceptance rules, project-guidance review, and archive and directory-README boundaries. |
| [`pyproject-standard`](plugins/laxpud-vibekits/skills/pyproject-standard/SKILL.md) | You are creating or editing a Python project's `pyproject.toml`. | Standards for `uv`, `hatchling`, dynamic versions, licenses, dependencies, classifiers, scripts, and package index configuration. |

## Included Rules

| Rule | Purpose |
| --- | --- |
| [`codex-user-global-rules`](rules/codex-user-global-rules.md) | A personal Codex global-rules backup for migration and version history. It is not a platform-neutral shared rule. |

## Maintenance

- Use [`docs/index.md`](docs/index.md) to find the authoritative technical document for a change.
- Read [`docs/SKILL_RULE_GUIDELINES.md`](docs/SKILL_RULE_GUIDELINES.md) before changing skills, rules, or adapter metadata.
- Follow [`docs/PLUGIN_UPDATE.md`](docs/PLUGIN_UPDATE.md) for release and client-update workflows.
- Follow [`docs/CODEX_INSTALL_SMOKE_TEST.md`](docs/CODEX_INSTALL_SMOKE_TEST.md) after changing Codex installation metadata or instructions.
- Track active work, acceptance conditions, and completion evidence in [`TODO.md`](TODO.md).

## License

MIT License. See [LICENSE](LICENSE).
