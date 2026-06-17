# Reorganizing Existing Docs

Use this reference when the repository already has scattered, duplicated, stale, or misplaced documentation.

## Workflow

1. Inventory the current docs and read their content, not only filenames.
2. Identify the source of truth for each topic before moving files.
3. Separate entry docs, technical docs, active TODOs, archives, and component-local READMEs.
4. Move files with history-preserving commands when possible.
5. Rewrite moved content for its destination instead of leaving stale phase language in place.
6. Replace duplicated definitions with summaries and links to the authoritative document.
7. Update root `README.md`, `docs/README.cn.md`, named technical docs, guidance files, and component-local READMEs so the new structure is discoverable.
8. Validate that old paths are gone, redirected, or intentionally preserved.

## Source-of-Truth Rules

- Root `README.md` is the English public entry point.
- `docs/README.cn.md` is the Chinese translation of the root README.
- `TODO.md` tracks active work and acceptance criteria.
- `docs/` holds durable technical details, design rationale, troubleshooting, and archived plans.
- Directory-level README files explain local folder ownership and navigation only.

Prefer consistent placement over ad hoc exceptions. If one detailed explanation belongs in `docs/`, similar explanations should also live in `docs/` unless the user intentionally chose a different rule.

## Link Rules

- Do not link directory-level README files from root `README.md` or `docs/README.cn.md`.
- Avoid links such as `docs/`, `src/`, or `packages/` from public entry documents when those links resolve to directory README files.
- Link named technical documents directly, such as `docs/architecture.md`, `docs/design.md`, or `docs/troubleshooting.md`.
- Technical docs indexes may link directory READMEs when doing so helps maintainers navigate ownership boundaries.

## Validation

- Re-read changed Markdown files after moving content.
- Search for old paths, obsolete filenames, and references to removed drafts.
- Check that every active decision is visible from root `README.md`, `TODO.md`, or a named technical doc.
- Do not delete unresolved decisions; move them into TODO or a technical note first.
