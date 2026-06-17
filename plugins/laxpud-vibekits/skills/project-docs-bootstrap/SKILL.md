---
name: project-docs-bootstrap
description: Initialize or reorganize maintainable project documentation structure. Use when creating or cleaning README, TODO, docs indexes, Chinese README translations, project guidance, documentation ownership, or archive boundaries for new or messy repositories. Do not use for small copy edits to a single document unless structure or ownership must change.
---

# Project Docs Bootstrap

## Goal

Create a practical documentation baseline for a project that is just starting, still fuzzy, or missing durable entry points.

Prefer a small, useful v1 over a large documentation system. The first pass should help a future contributor understand:

- what the project is for and what it is not for;
- what exists now and what the first practical milestone is;
- where active work is tracked;
- where technical details belong;
- which collaboration rules prevent likely mistakes.

The usual baseline is:

- root `README.md` as the concise English public entry;
- root `TODO.md` as the active milestone and acceptance checklist;
- `docs/` as the home for technical notes, design details, and archived plans;
- `docs/README.cn.md` as the Chinese translation of the root README;
- an agent or contributor guidance file, such as `AGENTS.md`, only when the repository uses one.

## When To Use

Use this skill when the user says things like:

- "initialize the docs for this new project";
- "bootstrap README, TODO, docs, and project guidance";
- "I only have a rough project idea, turn it into project docs";
- "set up a documentation structure for this repository";
- "clean up this messy docs tree and make the entry points clear".

Also use it after a completed planning session when the useful decisions should become durable project documentation instead of staying in chat or temporary notes.

## When Not To Use

Do not turn this into a language, framework, or package scaffold. This skill can document a project structure, but it should not generate application source code, install dependencies, create build systems, or add platform-specific adapter metadata unless the user separately asks for that work.

Keep the skill platform-neutral. Generic project docs and reusable collaboration guidance belong in normal project files. Platform-specific configuration belongs in that platform's adapter directory, not in shared docs or shared skills.

Do not use this skill for small copy edits, typo fixes, badge updates, or isolated changes to a single document unless the user is also changing documentation structure, ownership, language policy, or discoverability.

## Reference Routing

Keep the main workflow lightweight. Read these references only when the task needs them:

- [`references/reorganizing-docs.md`](references/reorganizing-docs.md): use when an existing repository has scattered, duplicated, stale, or misplaced docs.
- [`references/directory-readmes.md`](references/directory-readmes.md): use when creating, deleting, linking, or updating directory-level README files.
- [`references/project-guidance.md`](references/project-guidance.md): use when creating or revising `AGENTS.md`, `CLAUDE.md`, contributor guidance, or other project-specific collaboration rules.

Do not load all references by default. Start with the core workflow, then read only the reference whose condition is met.

## Initialization Workflow

Use this workflow when the project is new, empty, or early-stage.

1. Inspect the starting point.
   - Read existing `README*`, `TODO.md`, `docs/`, guidance files, planning drafts, manifests, and Git status.
   - If the project has source files or config files, infer the project purpose from them before asking the user.
   - Identify temporary notes or rough plans whose decisions should be migrated into durable docs.

2. Establish the minimum documentation contract.
   - Choose the files that should exist now, not every file that might be useful someday.
   - Default contract: English `README.md`, `TODO.md`, `docs/`, and Chinese `docs/README.cn.md`.
   - Add or refine a contributor or agent guidance file only when project-specific rules will prevent concrete future mistakes.
   - Add directory-level READMEs only where they explain stable responsibilities and boundaries.
   - Make clear where each topic belongs: README for entry, TODO for active work, `docs/` for details, archive for completed planning history.

3. Create or update `README.md`.
   - Write the root README in English by default, even when other project docs use the user's communication language.
   - Keep it short and useful on the first screen.
   - Include purpose, non-goals, current status, first practical milestone, and setup or usage notes that actually exist.
   - Link only top-level entry files or named technical documents, such as `TODO.md`, `docs/README.cn.md`, or `docs/architecture.md`.
   - Do not link directory-level README files from the root README, including `docs/README.md`, `src/README.md`, `packages/README.md`, or links that resolve to directory READMEs such as `docs/` or `src/`.
   - Avoid dumping full file trees, speculative architecture, or long implementation notes into README.

4. Create or update `TODO.md`.
   - Use Markdown checkboxes.
   - Write tasks in the user's communication language by default unless the project already has a stronger language convention.
   - Group work by phases or milestones.
   - Add acceptance criteria for nontrivial tasks so "done" is testable.
   - Preserve completed items unless the user asks to archive history.

5. Create or update `docs/`.
   - Start with the smallest useful technical index, usually `docs/README.md` if there will be multiple technical docs.
   - Add only documents that reduce future ambiguity, such as `architecture.md`, `design.md`, `data_layout.md`, `implementation_notes.md`, or `results_notes.md`.
   - Put long-form explanations, feasibility notes, historical plans, and design rationale under `docs/`, not in the root README.
   - Maintain `docs/README.cn.md` as the Chinese translation of the English root README.
   - If `docs/README.md` exists, treat it as a technical docs index, not as the Chinese root README translation.
   - Do not link directory-level README files from `docs/README.cn.md`; keep it structurally aligned with the root README and link named top-level or technical documents directly.

6. Create or update directory READMEs only where useful.
   - High-level source directories such as `src/`, `packages/`, `apps/`, or `services/` may get a short navigation README that explains top-level packages, responsibilities, boundaries, and main entry points.
   - Important package directories may get a `README.md` when the package has non-obvious responsibilities, multiple cooperating modules, public APIs, data flow, extension points, or common modification hazards.
   - Do not default to a README in every directory. Empty or obvious directories should stay quiet.
   - Do not default to per-file explanation lists. File responsibilities should usually live in file names, module docstrings, public API docs, and code comments.
   - Use per-file lists only for small stable utility directories, teaching-oriented projects, or when the user explicitly asks for file-by-file documentation.

7. Create or refine project guidance.
   - Keep only project-specific rules and user preferences.
   - Include rules that prevent likely mistakes, such as source-of-truth boundaries, language conventions, TODO rules, dependency limits, data format constraints, or commit message policy.
   - Do not include generic agent behavior such as "read files before editing" or "check Git status"; those are baseline work habits, not project rules.
   - Do not copy personal global defaults into project guidance unless they materially change how this project should be maintained.
   - When initializing `AGENTS.md`, use the default preferences below as a review checklist, then keep only items that are project-specific, requested by the user, or needed to prevent concrete mistakes.

8. Archive or remove planning leftovers.
   - If a rough plan has been absorbed into README, TODO, and `docs/`, remove it or move it under `docs/archive/` with a short archive note.
   - Do not delete unresolved decisions. Move them into TODO or a technical note first.
   - Keep active work visible from the root README.

9. Validate the baseline.
   - Read back changed Markdown files.
   - Search for stale links, old paths, and references to removed drafts.
   - Check that every important document is discoverable from README or a docs index.
   - For documentation-only work, run whitespace and path checks instead of unrelated heavy tests.
   - Check Git status and diff before reporting the result.

## Reorganizing Existing Docs

When existing docs are scattered, duplicated, stale, or misplaced, read [`references/reorganizing-docs.md`](references/reorganizing-docs.md) before editing. That reference contains the detailed inventory, source-of-truth, move, rewrite, and validation sequence.

## Content Rules

- Root README is an entry point, not a design archive.
- Root README is English by default. Put its Chinese translation in `docs/README.cn.md`.
- `TODO.md` is active work; archived plans belong under `docs/archive/` when historical traceability matters.
- Technical docs should explain durable decisions, data formats, architecture, methodology, results, and implementation notes.
- Bilingual docs should stay structurally aligned: when `README.md` changes, update `docs/README.cn.md` in the same turn unless the user says not to.
- `README.md` and `docs/README.cn.md` should not link directory-level README files. Directory READMEs are navigation aids for maintainers inside a folder, and linking them from public entry documents can confuse entry docs with directory maps.
- Code identifiers, commands, config keys, paths, terminal output, log messages, and exception names stay in English.
- User-facing documentation should follow the user's communication language unless the project already has a stronger language convention.
- Comments or prose added by an assistant should explain purpose, data flow, assumptions, and edge cases; avoid comments that simply restate obvious content.

## Output Checklist

Before reporting completion, verify the output against this checklist:

- Root `README.md` is English.
- `docs/README.cn.md` exists as the Chinese translation when the documentation baseline is being created or rewritten.
- `README.md` and `docs/README.cn.md` do not link directory-level README files or directory paths that resolve to README files.
- Technical details, design rationale, long troubleshooting notes, and historical plans live under `docs/`, not in the root README.
- `TODO.md` uses Markdown checkboxes and gives acceptance criteria for nontrivial work.
- Directory READMEs are created only when they explain stable folder ownership or navigation boundaries.
- The final report mentions validation performed and any checks that could not run.

## Directory README Rules

Directory READMEs are optional folder maps, not public entry points. When the task involves directory-level README files, read [`references/directory-readmes.md`](references/directory-readmes.md) before editing.

## Guidance File Rules

Project guidance files should prevent concrete future mistakes, not collect generic agent behavior. When the task involves `AGENTS.md`, `CLAUDE.md`, contributor docs, or collaboration rules, read [`references/project-guidance.md`](references/project-guidance.md) before editing.

## AGENTS.md Defaults

When initializing `AGENTS.md`, use the checklist in [`references/project-guidance.md`](references/project-guidance.md). Keep only project-specific facts, paths, commands, and module names grounded in the actual repository.

## Examples

User prompt:

```text
Help me initialize documentation for this new project.
```

Expected behavior: inspect the repository, infer the project purpose, create or update `README.md`, `TODO.md`, and `docs/` with a small useful baseline, then report the changed files and validation checks.

User prompt:

```text
I only have a rough plan in notes.md. Turn it into project docs.
```

Expected behavior: extract durable decisions from the rough plan, put entry-level content in README, active work in TODO, technical details in `docs/`, and archive or remove the temporary note only after its useful content is preserved.

User prompt:

```text
This project's docs are messy. Make the entry points clear.
```

Expected behavior: inventory the existing docs, decide source-of-truth ownership, reorganize and rewrite content, update links and indexes, and validate that stale references are gone.

## Reusable Defaults

Use these defaults unless the user or existing repository says otherwise:

- English root `README.md`.
- Chinese `docs/README.cn.md` as the translation of the root README.
- User-facing docs under `docs/` follow the user's communication language unless the project already has a stronger language convention.
- `TODO.md` follows the user's communication language, with checkbox tasks and acceptance criteria.
- `docs/` instead of `doc/` for general project documentation.
- `docs/README.md` as the technical docs index when `docs/README.cn.md` is reserved for the translated root README.
- Do not link directory-level README files from root `README.md` or `docs/README.cn.md`.
- Remove obsolete planning drafts after their useful content is migrated.
- Archive completed milestone TODOs under `docs/archive/` when the project values traceability.
