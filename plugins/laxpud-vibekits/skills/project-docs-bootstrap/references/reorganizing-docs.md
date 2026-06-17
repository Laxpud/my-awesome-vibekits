# Reorganizing Existing Docs

Use this reference when the repository already has scattered, duplicated, stale, or misplaced documentation.

## Workflow

1. Inventory the current docs and read their content, not only filenames.
2. Identify the source of truth for each topic before moving files.
3. Separate entry docs, technical docs, active TODOs, archives, and component-local READMEs.
4. Check Git status and identify user-owned or unrelated changes before moving files.
5. Use the Clarification Gate from `SKILL.md` if source-of-truth conflicts or structural choices would affect the public entry docs.
6. Move files with history-preserving commands when possible.
7. Rewrite moved content for its destination instead of leaving stale phase language in place.
8. Replace duplicated definitions with summaries and links to the authoritative document.
9. Update root `README.md`, `docs/README.cn.md`, `docs/index.md` when present, named technical docs, guidance files, and component-local READMEs so the new structure is discoverable.
10. Validate that old paths are gone, redirected, or intentionally preserved.

## Source-of-Truth Rules

- Root `README.md` is the English public entry point unless the project or user explicitly sets another public-documentation language.
- `docs/README.cn.md` is the Chinese translation of the root README when the bilingual baseline is present.
- `docs/index.md` is the technical docs index when multiple technical docs need navigation.
- `TODO.md` tracks active work and acceptance criteria.
- `docs/` holds durable technical details, design rationale, troubleshooting, and archived plans.
- Directory-level README files explain local folder ownership and navigation only.

Prefer consistent placement over ad hoc exceptions. If one detailed explanation belongs in `docs/`, similar explanations should also live in `docs/` unless the user intentionally chose a different rule.

## Link Rules

- Do not link directory-level README files from root `README.md` or `docs/README.cn.md`.
- Avoid links such as `docs/`, `src/`, or `packages/` from public entry documents when those links resolve to directory README files.
- Link named technical documents directly, such as `docs/architecture.md`, `docs/design.md`, or `docs/troubleshooting.md`.
- Link `docs/index.md` when exposing a technical docs index from public entry documents.
- Technical docs indexes may link directory READMEs when doing so helps maintainers navigate ownership boundaries.
- If an old path is likely externally referenced, preserve it with a short redirect note instead of deleting it outright.

## Conflict Handling

- If duplicated docs agree, consolidate the content into the authoritative destination and replace duplicates with short summaries or links.
- If duplicated docs conflict, do not silently choose one. Prefer the newer or more authoritative source only when repository evidence supports it.
- Record unresolved conflicts in `TODO.md` or a named technical note with the source files and decision needed.
- If a conflict changes the immediate README, TODO, docs index, or archive structure, ask the user through the Clarification Gate before editing those files.

## Archive Rules

- Move completed plans, superseded proposals, and historical milestone notes into `docs/archive/` when traceability matters.
- Keep active work, open decisions, and acceptance criteria in `TODO.md`.
- Keep durable design rationale, current architecture, data formats, and troubleshooting in named technical docs under `docs/`.
- Do not archive content merely because it is long; archive only when it is historical or superseded.

## Validation

- Re-read changed Markdown files after moving content.
- Search for old paths, obsolete filenames, and references to removed drafts.
- Check that every active decision is visible from root `README.md`, `TODO.md`, or a named technical doc.
- Do not delete unresolved decisions; move them into TODO or a technical note first.
- Review `git diff` to confirm only the intended documentation files moved or changed.
