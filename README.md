# Vibekits

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Plugins](https://img.shields.io/badge/plugins-3-2563EB)](plugin-catalog.json)
[![Skills](https://img.shields.io/badge/skills-3-brightgreen)](#included-plugins-and-skills)
[![Codex Marketplace](https://img.shields.io/badge/Codex-Marketplace-111827)](.agents/plugins/marketplace.json)
[![Claude Code Marketplace](https://img.shields.io/badge/Claude%20Code-Marketplace-D97706)](.claude-plugin/marketplace.json)
[![中文](https://img.shields.io/badge/README-中文-C026D3)](docs/README.cn.md)

Vibekits is a catalog of independent, platform-neutral workflow plugins for Codex and Claude Code. Each plugin owns one reusable skill and can be installed, upgraded, disabled, removed, or rolled back without changing its siblings.

The repository keeps one [`plugin-catalog.json`](plugin-catalog.json) as the distribution source of truth. It generates both marketplaces and each plugin's Codex and Claude Code manifests; the plugin-local `skills/` directory remains the only source for skill content.

## Current Status

- The marketplace exposes three independently versioned plugins: `code-quality`, `python-project`, and `project-docs`.
- The former `laxpud-vibekits` aggregate plugin was removed. This split intentionally provides no deprecated bundle, alias, or migration compatibility layer.
- Validation covers catalog conflicts, generated-file drift, both manifest formats, README install paths, and isolated three-plugin lifecycle and rollback behavior.

## Start Here

If you want to try one capability first:

- Organize project documentation with [`project-docs-bootstrap`](plugins/project-docs/skills/project-docs-bootstrap/SKILL.md) from `project-docs`.
- Standardize code comments with [`code-comment-standard`](plugins/code-quality/skills/code-comment-standard/SKILL.md) from `code-quality`.
- Create or review `pyproject.toml` with [`pyproject-standard`](plugins/python-project/skills/pyproject-standard/SKILL.md) from `python-project`.

## Quick Install

### Claude Code

```bash
/plugin marketplace add https://github.com/Laxpud/my-awesome-vibekits
/plugin install code-quality@laxpud-vibekits
/plugin install python-project@laxpud-vibekits
/plugin install project-docs@laxpud-vibekits
```

Install only the plugins you need. After installation, start a new session and describe the task directly, or explicitly ask for a skill:

```text
Use project-docs-bootstrap to reorganize this repository documentation.
```

### Codex

```bash
codex plugin marketplace add Laxpud/my-awesome-vibekits
codex
/plugins
```

Choose `code-quality`, `python-project`, and/or `project-docs` from the plugin list. Each selection is independent. Start a new task after installing or upgrading so the selected skills are loaded.

### Manual Browse

```bash
git clone https://github.com/Laxpud/my-awesome-vibekits.git
```

After cloning, start with the [technical documentation index](docs/index.md), the [plugin catalog](plugin-catalog.json), or the [active milestone](TODO.md).

## Included Plugins and Skills

| Plugin | Skill | Use when | What it provides |
| --- | --- | --- | --- |
| `code-quality` | [`code-comment-standard`](plugins/code-quality/skills/code-comment-standard/SKILL.md) | You need to generate, review, complete, or standardize comments, docstrings, TODOs, or public API documentation. | Cross-language comment levels, quality standards, anti-patterns, and a maintainer-oriented commenting workflow. |
| `python-project` | [`pyproject-standard`](plugins/python-project/skills/pyproject-standard/SKILL.md) | You are creating or editing a Python project's `pyproject.toml`. | Standards for `uv`, `hatchling`, dynamic versions, licenses, dependencies, classifiers, scripts, and package index configuration. |
| `project-docs` | [`project-docs-bootstrap`](plugins/project-docs/skills/project-docs-bootstrap/SKILL.md) | A repository needs clear documentation ownership, milestone-driven TODO workflows, or concise project-guidance routes. | README/TODO/docs ownership, milestone acceptance rules, project-guidance review, and archive and directory-README boundaries. |

## Included Rules

| Rule | Purpose |
| --- | --- |
| [`codex-user-global-rules`](rules/codex-user-global-rules.md) | A personal Codex global-rules backup for migration and version history. It is not a platform-neutral shared rule. |

## Maintenance

- Use [`docs/index.md`](docs/index.md) to find the authoritative technical document for a change.
- Read [`docs/SKILL_RULE_GUIDELINES.md`](docs/SKILL_RULE_GUIDELINES.md) before changing skills, catalog data, or generated adapter metadata.
- Follow [`docs/PLUGIN_UPDATE.md`](docs/PLUGIN_UPDATE.md) for independent versioning, release, client update, and rollback workflows.
- Follow [`docs/CODEX_INSTALL_SMOKE_TEST.md`](docs/CODEX_INSTALL_SMOKE_TEST.md) after changing Codex marketplace metadata or installation instructions.
- Track active work, acceptance conditions, and completion evidence in [`TODO.md`](TODO.md).

## License

MIT License. See [LICENSE](LICENSE).
