---
name: "pyproject-standard"
description: "Enforces standard configuration for pyproject.toml. Invoke when creating or modifying pyproject.toml to ensure compliance with project standards."
---

# Pyproject Standard

This skill defines the standard structure and required fields for `pyproject.toml` files in this workspace.

## Invocation Instructions

When this skill is invoked, you MUST follow the flow below. **Every prompt to the user must include a "Skip" option — if the user skips, leave the field as its placeholder (e.g., `<author-name>`, `<description>`, `<project-name>`).**

1.  **Project Name (AI proposal + user confirmation + skip)**: Propose a project name that complies with community norms (GitHub/PyPI). Ask the user to confirm, modify, or skip.
2.  **Project Description (AI proposal + user confirmation + skip)**: Derive a concise description from the project domain or existing files (e.g., README, main module docstrings). Ask the user to confirm, modify, or skip.
3.  **Author Information (name + email + skip)**: Ask the user for their name and email address to populate the `authors` field. If skipped, leave as `<author-name>` / `<author-email>`.
4.  **Analyze Python/Dependencies**: If the user's project `pyproject.toml` lacks `requires-python` or dependency version information, analyze the codebase to identify required dependencies and propose appropriate version constraints. Present the proposal to the user — they may accept, modify, or skip.

## Core Rules

1.  **Build System**: MUST use `hatchling` as the build backend.
2.  **Package Management**: MUST be compatible with `uv`.
3.  **Mirror Configuration**: MUST include the Tsinghua mirror for `uv` acceleration.
4.  **Versioning**: MUST use dynamic versioning sourced from `src/__init__.py`.
5.  **License**: MUST reference an external `LICENSE` file.
6.  **Dynamic Content**:
    *   **Classifiers**: Include basic classifiers (OS, Python version). Add specific Topic/Audience classifiers ONLY if relevant to the project domain.
    *   **Scripts (CLI)**: Define `[project.scripts]` ONLY if the project has executable CLI tools.
    *   **Plugin Entry Points**: Define `[project.entry-points]` ONLY if the project exposes plugins for other applications.
    *   **Optional Dependencies**: Define `[project.optional-dependencies]` ONLY if there are distinct feature sets (e.g., `plot`, `test`, `dev`) that require extra packages.

## Project Name Guidelines

Project names must comply with GitHub repository and PyPI package naming conventions:

1.  **Lowercase only**: Use all lowercase letters (e.g., `my-project`, not `My-Project`).
2.  **Hyphens or underscores**: Separate words with hyphens (`-`) or underscores (`_`). Hyphens are preferred for PyPI compatibility (e.g., `awesome_tool` vs `awesome-tool` — prefer `awesome-tool`).
3.  **No special characters**: Avoid symbols, spaces, or punctuation other than `-` and `_`.
4.  **Concise and descriptive**: Keep the name short (1-3 words) while reflecting the project's purpose.
5.  **Check availability**: Verify the name is not already taken on PyPI/GitHub before proposing.

When proposing a name, AI should derive it from the project description, directory structure, or main functionality. Provide 1-3 alternatives if the primary suggestion might conflict with an existing package.

## Project Description Guidelines

A good project description is:

1.  **Concise**: One to two sentences (under 60 characters ideally, max one short paragraph).
2.  **Informative**: State what the project does, not just its name.
3.  **Audience-aware**: Written for someone who might want to use or contribute to the project.
4.  **Active voice**: Prefer "A tool for ..." or "Provides ..." over vague phrasing.

AI should derive the description from existing project files (README, `__doc__`, main module docstrings, or directory structure). If no source material is available, propose a generic but plausible placeholder and clearly label it as AI-generated.

## Template

Use the following template as the baseline. **Review and Uncomment/Remove optional sections based on project needs.**

```toml
[project]
name = "<project-name>"
dynamic = ["version"]
description = "<description>"
readme = "README.md"
requires-python = "<python-version>"
license = { file = "LICENSE" }
authors = [
    { name = "<author-name>", email = "<author-email>" }
]
keywords = ["<keyword1>", "<keyword2>"]

# [Mandatory Classifiers]
classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: <python-version>",
    "Operating System :: OS Independent",
    # Add domain-specific classifiers here if applicable (e.g., "Topic :: Scientific/Engineering")
]

dependencies = [
    # Add core dependencies here (e.g., "package-name>=<major>.<minor>")
]

# [Optional] Define optional dependencies if needed
# [project.optional-dependencies]
# plot = ["matplotlib>=<version>"]
# dev = ["pytest>=<version>", "black>=<version>"]

# [Optional] Define CLI entry points if needed
# [project.scripts]
# my-tool = "package.module:function"

# [Optional] Define Plugin entry points if needed
# [project.entry-points."plugin_namespace"]
# plugin_name = "package.module:object"

[project.urls]
Repository = "<repository-url>"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.version]
path = "src/__init__.py"

[tool.hatch.build.targets.wheel]
packages = ["src"]

# 配置 uv 使用清华镜像源加速下载
[[tool.uv.index]]
name = "tsinghua"
url = "https://pypi.tuna.tsinghua.edu.cn/simple"
default = true
```

## Dependency Version Guidelines

When adding dependencies:

1.  **Analyze Existing Code**: Review the project's source files (e.g., in `src/` or the main package directory) to identify imports and usage patterns.
2.  **Determine Appropriate Versions**:
    *   For projects with existing code: Check import statements and feature usage to determine minimum version requirements.
    *   For new projects: Use widely compatible version constraints (e.g., `>=<major>.<minor>`).
3.  **Version Format Examples**:
    *   Minimum version: `"package>=<major>.<minor>"`
    *   Specific major version: `"package>=<major>.<minor>,<major_plus_one>"`
    *   Flexible version: `"package>=<major>.<minor>,<another_constraint>"`

## Checklist Before Completion

- [ ] `[build-system]` is set to `hatchling`.
- [ ] `dynamic = ["version"]` is present and linked to `src/__init__.py`.
- [ ] `license = { file = "LICENSE" }` is set.
- [ ] Tsinghua mirror configuration is present under `[[tool.uv.index]]`.
- [ ] **Optional sections (`scripts`, `entry-points`, `optional-dependencies`, specific `classifiers`) are reviewed and included only if necessary.**
