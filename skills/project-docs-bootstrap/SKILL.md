---
name: project-docs-bootstrap
description: Initialize a maintainable documentation baseline for a new, empty, or early-stage project. Use when the user asks to bootstrap project docs, create README/TODO/docs guidance, turn a rough project idea into durable documentation, define documentation ownership, or reorganize an existing messy docs tree into clear entry points and collaboration rules.
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

- root `README.md` as the concise public entry;
- root `TODO.md` as the active milestone and acceptance checklist;
- `docs/` as the home for technical notes, design details, and archived plans;
- `docs/README.cn.md` as the Chinese translation of the root README when bilingual docs are desired;
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

## Initialization Workflow

Use this workflow when the project is new, empty, or early-stage.

1. Inspect the starting point.
   - Read existing `README*`, `TODO.md`, `docs/`, guidance files, planning drafts, manifests, and Git status.
   - If the project has source files or config files, infer the project purpose from them before asking the user.
   - Identify temporary notes or rough plans whose decisions should be migrated into durable docs.

2. Establish the minimum documentation contract.
   - Choose the files that should exist now, not every file that might be useful someday.
   - Default contract: `README.md`, `TODO.md`, and `docs/`.
   - Add `docs/README.cn.md` when bilingual documentation is useful.
   - Add or refine a contributor or agent guidance file only when project-specific rules will prevent concrete future mistakes.
   - Add directory-level READMEs only where they explain stable responsibilities and boundaries.
   - Make clear where each topic belongs: README for entry, TODO for active work, `docs/` for details, archive for completed planning history.

3. Create or update `README.md`.
   - Keep it short and useful on the first screen.
   - Include purpose, non-goals, current status, first practical milestone, setup or usage notes that actually exist, and links to `TODO.md` and `docs/`.
   - Avoid dumping full file trees, speculative architecture, or long implementation notes into README.

4. Create or update `TODO.md`.
   - Use Markdown checkboxes.
   - Write tasks in Chinese by default unless the project already uses another language.
   - Group work by phases or milestones.
   - Add acceptance criteria for nontrivial tasks so "done" is testable.
   - Preserve completed items unless the user asks to archive history.

5. Create or update `docs/`.
   - Start with the smallest useful technical index, usually `docs/README.md` if there will be multiple technical docs.
   - Add only documents that reduce future ambiguity, such as `architecture.md`, `design.md`, `data_layout.md`, `implementation_notes.md`, or `results_notes.md`.
   - Put long-form explanations, feasibility notes, historical plans, and design rationale under `docs/`, not in the root README.
   - If `docs/README.cn.md` is used as the Chinese root README translation, use `docs/README.md` as the technical docs index.

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
   - When initializing `AGENTS.md`, use the default preferences below as a starting point, then remove anything that does not fit the specific project.

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

Use this sequence when the repository already has scattered, duplicated, or stale documentation.

1. Inventory the current docs and read their content, not only filenames.
2. Identify the source of truth for each topic before moving files.
3. Separate entry docs, technical docs, active TODOs, archives, and component-local READMEs.
4. Move files with history-preserving commands when possible.
5. Rewrite moved content for its destination instead of leaving stale phase language in place.
6. Replace duplicated definitions with summaries and links to the authoritative document.
7. Update README, docs indexes, translated READMEs, guidance files, and component READMEs so the new structure is discoverable.
8. Validate that old paths are gone or redirected and that the requested directory invariants hold.

Prefer consistent placement over ad hoc exceptions. If one detailed explanation belongs in `docs/`, similar explanations should also live in `docs/` unless the user intentionally chose a different rule.

## Content Rules

- Root README is an entry point, not a design archive.
- `TODO.md` is active work; archived plans belong under `docs/archive/` when historical traceability matters.
- Technical docs should explain durable decisions, data formats, architecture, methodology, results, and implementation notes.
- Bilingual docs should stay structurally aligned: when `README.md` changes, update `docs/README.cn.md` in the same turn unless the user says not to.
- Code identifiers, commands, config keys, paths, terminal output, log messages, and exception names stay in English.
- User-facing Chinese documentation is acceptable and often preferred for TODOs, planning notes, and project guidance when the project uses Chinese.
- Comments or prose added by an assistant should explain purpose, data flow, assumptions, and edge cases; avoid comments that simply restate obvious content.

## Directory README Rules

Use directory READMEs as maps of stable boundaries, not as generated file catalogs.

- Prefer `src/README.md`, `packages/README.md`, `apps/README.md`, or `services/README.md` when a high-level source directory contains multiple packages or application areas.
- In high-level source READMEs, describe the major packages, their responsibilities, public entry points, and how they depend on each other.
- Add package-level READMEs only for important packages whose purpose, public API, data flow, extension model, or modification risks are not obvious from the code layout.
- Avoid listing every file by default because those lists become stale after renames, splits, and merges.
- If file-level explanation is useful, keep it brief and limited to small stable utility directories, teaching-oriented projects, or user-requested walkthroughs.
- Put long learning-oriented explanations under `docs/`; keep directory READMEs focused on navigation and ownership.

## Guidance File Rules

Include project guidance only when it prevents concrete mistakes. Useful sections may include:

- project purpose and non-goals;
- common entry points;
- README versus docs ownership;
- language conventions;
- TODO and acceptance criteria rules;
- dependency or scaffold limits;
- data, API, or file format constraints;
- Git or release conventions.

Avoid turning one project's local preferences into universal rules. Keep the file short enough that future contributors will actually read it.

## AGENTS.md Defaults

When initializing `AGENTS.md`, start from these user preferences and adapt them to the project. Keep project-specific facts, paths, commands, and module names grounded in the actual repository.

- Write `AGENTS.md` primarily as an entry index, routing guide, and behavior boundary. Long architecture, configuration, usage, troubleshooting, and tutorial content should live in `docs/`.
- Keep README concise. Put implementation details, file responsibilities, data flow, conversion chains, benchmark design, and troubleshooting notes in `docs/`.
- Maintain clear documentation ownership: root README for public entry, `TODO.md` for active work, `docs/` for technical details, and `docs/archive/` for completed planning history when traceability matters.
- Use checkbox TODOs. Write new TODO items in Chinese by default, include goal/current state/acceptance criteria when useful, update progress in the same change that completes or partially completes the work, and preserve completed history unless deliberately archiving.
- Keep code identifiers, module names, commands, terminal output, logs, exception messages, and config keys in English.
- Prefer Chinese for user-facing planning docs when the project already uses Chinese.
- When an assistant adds or edits comments, docstrings, function descriptions, or complex logic explanations, prefer Chinese and write enough explanation for less experienced readers to follow the purpose, data flow, assumptions, edge cases, and reasons for non-obvious choices.
- Add more explanatory comments around meaningful steps, branches, loops, data transformations, geometry/math, validation, configuration handling, process boundaries, timing boundaries, and file or result output.
- Avoid noisy line-by-line comments that merely repeat an assignment or function call.
- If a code change makes a file harder to understand, update nearby comments or docstrings in the same turn instead of leaving "working but unreadable" code.
- Keep generated files, caches, virtual environments, local real-data test inputs, and build outputs out of commits unless the project explicitly tracks them.
- Prefer focused changes. Do not mix unrelated refactors, generated outputs, or user-owned worktree changes into the same commit.
- Use Conventional Commits by default, with a concrete summary and, for nontrivial changes, a body that lists the main changes and verification.

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
- Chinese `docs/README.cn.md` as a translation of the root README when bilingual docs are desired.
- Chinese user-facing docs under `docs/` when the project already uses Chinese.
- Chinese `TODO.md` with checkbox tasks and acceptance criteria.
- `docs/` instead of `doc/` for general project documentation.
- `docs/README.md` as the technical docs index when `docs/README.cn.md` is reserved for the translated root README.
- Remove obsolete planning drafts after their useful content is migrated.
- Archive completed milestone TODOs under `docs/archive/` when the project values traceability.
