# Directory README Rules

Use this reference when creating, removing, linking, or editing directory-level README files.

## Purpose

Directory READMEs are maps of stable folder boundaries. They should help maintainers understand ownership, responsibilities, entry points, and local modification hazards inside that folder.

They are not public entry documents, generated file catalogs, or substitutes for root README/docs.

Use `docs/index.md` for the technical docs index when one is needed. Avoid `docs/README.md` for that role so directory README behavior stays separate from the bilingual README contract.

## When To Add One

Prefer a directory README for:

- high-level source directories such as `src/`, `packages/`, `apps/`, or `services/` when they contain multiple packages or application areas;
- important package directories with non-obvious public APIs, data flow, extension points, or common modification risks;
- stable utility directories in teaching-oriented projects where a short file map genuinely helps.

Do not add one for empty, obvious, or volatile folders.

If the repository evidence does not clearly show whether a directory owns enough behavior to deserve a README, use the Clarification Gate from `SKILL.md` before creating one. For low-impact uncertainty, skip the README and record the possible follow-up in TODO.

## When Updating Existing Ones

- Read the existing directory README, nearby manifests, entry files, package files, and relevant technical docs before changing content.
- Preserve useful local constraints, ownership notes, and migration warnings.
- Replace stale file catalogs with stable responsibilities, entry points, and links to named docs.
- Remove or merge obsolete directory READMEs when the folder is empty, obvious, moved, or no longer owns distinct behavior.
- If deleting or moving a directory README, update nearby links and leave unresolved decisions in TODO or a named technical doc.
- If existing directory docs disagree with manifests, entry files, or technical docs about ownership, use the Clarification Gate before rewriting the boundary.

## What To Include

- The directory's responsibility and non-goals.
- Major packages or subareas and their relationships.
- Public entry points and extension points.
- Local conventions, generated-file boundaries, or migration hazards that prevent mistakes.
- Links to named technical docs when details belong elsewhere.

Ground each responsibility in actual repository evidence: directory structure, manifests, entry files, public APIs, existing docs, or observed generated artifacts. If the evidence is weak, describe the uncertainty or leave the decision for TODO instead of inventing ownership.

## What To Avoid

- Do not list every file by default; file catalogs become stale after renames, splits, and merges.
- Do not repeat long architecture, troubleshooting, or tutorial content; put that in named files under `docs/`.
- Do not make directory READMEs discoverable from root `README.md` or `docs/README.cn.md`.
- Do not use links such as `docs/`, `src/`, or `packages/` from public entry documents when those paths resolve to directory README files.
- Do not create `docs/README.md` as a workaround for a technical docs index; use `docs/index.md`.

Keep directory READMEs discoverable from their owning directory, owning package docs, or a technical docs index when maintainer navigation needs it.

## Language

Follow the repository's existing language convention for directory README prose. Keep code identifiers, paths, commands, config keys, logs, and protocol fields in English.
