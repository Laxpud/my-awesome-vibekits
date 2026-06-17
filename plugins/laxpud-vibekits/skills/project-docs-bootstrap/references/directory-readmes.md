# Directory README Rules

Use this reference when creating, removing, linking, or editing directory-level README files.

## Purpose

Directory READMEs are maps of stable folder boundaries. They should help maintainers understand ownership, responsibilities, entry points, and local modification hazards inside that folder.

They are not public entry documents, generated file catalogs, or substitutes for root README/docs.

## When To Add One

Prefer a directory README for:

- high-level source directories such as `src/`, `packages/`, `apps/`, or `services/` when they contain multiple packages or application areas;
- important package directories with non-obvious public APIs, data flow, extension points, or common modification risks;
- stable utility directories in teaching-oriented projects where a short file map genuinely helps.

Do not add one for empty, obvious, or volatile folders.

## What To Include

- The directory's responsibility and non-goals.
- Major packages or subareas and their relationships.
- Public entry points and extension points.
- Local conventions, generated-file boundaries, or migration hazards that prevent mistakes.
- Links to named technical docs when details belong elsewhere.

## What To Avoid

- Do not list every file by default; file catalogs become stale after renames, splits, and merges.
- Do not repeat long architecture, troubleshooting, or tutorial content; put that in named files under `docs/`.
- Do not make directory READMEs discoverable from root `README.md` or `docs/README.cn.md`.
- Do not use links such as `docs/`, `src/`, or `packages/` from public entry documents when those paths resolve to directory README files.

Keep directory READMEs discoverable from their owning directory, from nearby package docs, or from a technical docs index when maintainer navigation needs it.
