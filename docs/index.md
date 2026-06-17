# Project Documentation Index

This directory stores Vibekits maintenance notes, skill/rule guidelines, and durable technical records. The root `README.md` is the concise English public entry, `docs/README.cn.md` is its Chinese translation, and `TODO.md` tracks active maintenance work.

## Document Map

| Document | Purpose |
| --- | --- |
| [README.cn.md](README.cn.md) | Chinese translation of the root README. |
| [SKILL_RULE_GUIDELINES.md](SKILL_RULE_GUIDELINES.md) | Structure, boundary, synchronization, and validation rules for shared skills, reusable rules, and platform adapters. |
| [../TODO.md](../TODO.md) | Active maintenance tasks, acceptance criteria, and future improvement candidates. |
| [../AGENTS.md](../AGENTS.md) | Project-level constraints for Codex work in this repository. |
| [../CLAUDE.md](../CLAUDE.md) | Project-level constraints for Claude Code work in this repository. |

## Documentation Ownership

- `README.md`: English public entry for GitHub readers, installation paths, included skills, and contribution basics.
- `docs/README.cn.md`: Chinese translation of the root README; keep it structurally aligned when the root README changes.
- `TODO.md`: active maintenance work, written with checkboxes and verifiable acceptance criteria.
- `docs/index.md`: technical documentation index for maintainers.
- `docs/`: durable maintenance rules, design boundaries, technical notes, and historical records.
- `plugins/laxpud-vibekits/skills/`: the only shared skill source. Each skill should contain only the `SKILL.md` and resources needed to run that skill.
- `.claude-plugin/`, `.agents/`, `plugins/laxpud-vibekits/.claude-plugin/`, and `plugins/laxpud-vibekits/.codex-plugin/`: platform adapter layers for marketplace or plugin manifests.

## Maintenance Conventions

- Keep the root README in English and keep `docs/README.cn.md` aligned as the Chinese translation.
- Use `docs/index.md` as the technical documentation index. Do not recreate `docs/README.md` for that role.
- When changing skill capabilities, names, or trigger descriptions, check the README skill table, Claude/Codex plugin manifests, and marketplace descriptions.
- Add platform adapter information only under the corresponding platform adapter directory; do not write platform-specific behavior into shared skill bodies.
- Keep reusable rules short, clear, and platform-neutral. Personal global-rule backups must be labeled in both filename and opening note.
- After documentation changes, validate JSON parsing, Markdown links, skill metadata, and `git diff`.
