# Project Guidance Files

Use this reference when creating or revising `AGENTS.md`, `CLAUDE.md`, contributor guidance, or other project-specific collaboration rules.

## Purpose

Project guidance files should prevent concrete future mistakes. They should route agents and contributors to the right entry points, document project-specific boundaries, and keep repeated decisions out of chat.

Do not use them as long architecture manuals, general agent behavior lists, or personal global preference dumps.

## Useful Sections

Include only sections that matter for this repository:

- project purpose and non-goals;
- common entry points;
- README versus docs ownership;
- language conventions;
- TODO and acceptance criteria rules;
- dependency or scaffold limits;
- data, API, or file format constraints;
- generated-file, cache, or artifact boundaries;
- Git, release, or commit conventions.

## Defaults To Adapt

When initializing `AGENTS.md`, start from these defaults and keep only what is project-specific, requested by the user, or needed to prevent concrete mistakes:

- Write `AGENTS.md` primarily as an entry index, routing guide, and behavior boundary.
- Put long architecture, configuration, usage, troubleshooting, and tutorial content in `docs/`.
- Keep root `README.md` concise and English.
- Keep `docs/README.cn.md` structurally aligned with root `README.md`.
- Keep implementation details, file responsibilities, data flow, conversion chains, benchmark design, and troubleshooting notes in named technical docs.
- Maintain clear documentation ownership: root README for public entry, `TODO.md` for active work, `docs/` for technical details, and `docs/archive/` for completed planning history when traceability matters.
- Use checkbox TODOs with acceptance criteria for nontrivial work.
- Keep code identifiers, module names, commands, terminal output, logs, exception messages, and config keys in English.
- Prefer the user's communication language for user-facing planning docs unless the project already has a stronger language convention.
- Keep generated files, caches, virtual environments, local real-data test inputs, and build outputs out of commits unless the project explicitly tracks them.
- Prefer focused changes. Do not mix unrelated refactors, generated outputs, or user-owned worktree changes into the same commit.
- Use Conventional Commits by default when the user asks for a commit.

## Quality Bar

- Keep guidance short enough that future contributors will read it.
- Ground every project-specific fact in actual repository files.
- Remove generic reminders such as "read files before editing" unless they encode a real local constraint.
- When guidance changes, check whether root README, TODO, or technical docs need matching updates.
