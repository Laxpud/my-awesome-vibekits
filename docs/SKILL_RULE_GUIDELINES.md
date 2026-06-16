# Agent Guidelines

## Project Purpose

This repository (`my-awesome-vibekits`) is a **collection of skills and rules** intended for sharing on GitHub. Its purpose is to gather and organize useful skills and rules that can be reused across different projects. It may also keep clearly labeled personal global-rule backups when the maintainer explicitly wants GitHub-based backup.

## When Creating Skills or Rules

**IMPORTANT**: When you are asked to create a skill or rule within this project, your goal is to **contribute to this collection** — not to create platform-specific skills or rules for any AI assistant platform (such as Trae IDE, Cursor, Claude, etc.).

### What This Means

- **DO**: Create reusable skill and rule files that will be added to this repository's `skills/` or `rules/` directories.
- **DO NOT**: Attempt to create skills or rules that would be registered with or configured for any specific AI assistant platform's internal systems.
- **DO**: Keep platform-specific adapter metadata in the matching adapter folder, such as `.claude-plugin/` or `.codex-plugin/`.
- **DO**: Keep personal global-rule backups clearly named and labeled when they intentionally live under `rules/`.

### Skill Structure

Skills should follow this structure:
```
skills/<skill-name>/
└── SKILL.md
```

### Reusable Rule Structure

Rules should follow this structure:
```
rules/<rule-name>.md
```

**Additional Requirements**:
- Reusable rule files should not exceed 1000 characters in length
- Keep reusable rules concise and focused on specific guidance
- Use clear, actionable language that can be easily understood and applied
- Personal global-rule backups are exempt from the length and platform-neutrality expectations, but must say they are backups rather than reusable rules.

## Contributing

When adding new reusable skills or rules to this collection, ensure they are:
- **Reusable**: Can be applied across multiple projects
- **Well-documented**: Include clear descriptions and usage examples
- **Platform-agnostic**: Not tied to any specific AI assistant or platform
