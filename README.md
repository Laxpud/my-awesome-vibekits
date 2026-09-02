# Vibekits

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![中文](https://img.shields.io/badge/README-中文-C026D3)](docs/README.cn.md)

[Documentation](docs/index.md) · [Roadmap](TODO.md) · [Report an issue](https://github.com/Laxpud/my-awesome-vibekits/issues)

Vibekits is my personally incubated collection of reusable workflows for Codex and Claude Code. It is not an application you run: install the plugin that matches your goal, then ask your coding agent to use one of its skills.

The current catalog contains three independently installable plugins and eight skills for code comments, Python project metadata, and repository documentation. Published skills are intended for normal use; feedback and new ideas continue to be incubated in this repository.

## Who This Is For

Start here if you have a project on your computer and can use—or are willing to install—either Codex CLI or Claude Code. You do not need to know how marketplaces, plugins, or skills work before following the quick start.

Vibekits helps the coding agent follow a repeatable workflow. It does not replace Codex or Claude Code, and it does not provide a graphical application of its own.

## How It Works

- **Agent:** Codex or Claude Code—the tool that reads your project and carries out your request.
- **Skill:** reusable instructions for one kind of task, such as reviewing a README.
- **Plugin:** an installable package containing one or more related skills.
- **Marketplace:** a catalog that tells your agent where it can find those plugins.

You add this repository as a marketplace once, install only the plugin you need, and then describe your task in normal language. Naming the skill explicitly is useful for your first run and whenever you want a specific workflow.

## Prerequisites

Choose **one** client below. If it already opens successfully in your project, skip to [Quick Start](#quick-start).

A **terminal** is the window where you type installation and startup commands: Terminal on macOS, a terminal app on Linux, or PowerShell on Windows. Commands beginning with `/` are entered later inside Codex or Claude Code, not in this terminal.

### Codex CLI

Use the [official Codex CLI guide](https://learn.chatgpt.com/docs/codex/cli) for current requirements and alternative installation methods. Choose the official standalone installer for your system.

**macOS or Linux — Terminal**

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

**Windows — PowerShell**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
```

Open a terminal in your project folder, verify the installation, and start Codex:

```bash
codex --version
codex
```

On the first run, follow the sign-in instructions. Success means the version command prints a version and the Codex prompt opens with your project as its working directory.

### Claude Code

Use the [official Claude Code installation guide](https://code.claude.com/docs/en/installation) for current requirements, account access, and alternative installation methods. Choose the recommended native installer for your system.

**macOS, Linux, or WSL — Terminal**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows — PowerShell**

```powershell
irm https://claude.ai/install.ps1 | iex
```

Open a terminal in your project folder, verify the installation, and start Claude Code:

```bash
claude --version
claude
```

Follow the browser sign-in instructions if prompted. Success means the version command prints a version and the Claude Code prompt opens for that project.

## Quick Start

This first run installs only `project-docs` and asks `project-docs-readme` for a read-only README review. Choose the client you already use; you do not need both.

### Install in Codex

In your system terminal, add this marketplace and start Codex from your project:

```bash
codex plugin marketplace add Laxpud/my-awesome-vibekits
codex
```

In the Codex input area, enter:

```text
/plugins
```

Find `project-docs`, then install and enable it. Start a new Codex task for the same project so the newly installed skills are loaded.

### Install in Claude Code

Start Claude Code from your project folder. In the **Claude Code input area**, enter these commands one at a time:

```text
/plugin marketplace add https://github.com/Laxpud/my-awesome-vibekits
/plugin install project-docs@laxpud-vibekits
```

Start a new Claude Code session for the same project so the newly installed skills are loaded.

### Run Your First Skill

Paste this into the new Codex task or Claude Code session:

```text
Use project-docs-readme to review this repository's root README for a first-time user. Identify its intended audience, missing prerequisites, and shortest verified path. Then propose an ordered change plan and wait for my confirmation before editing.
```

### What Success Looks Like

The agent should report:

1. who the README is for;
2. which prerequisites are missing or unclear;
3. the shortest path a new user can actually follow;
4. an ordered change plan.

It should **not edit files yet**. Review the plan first. If it looks right, reply with a clear instruction such as:

```text
The plan looks good. Apply it, keep official translations aligned, and verify every changed link and command.
```

> **Updating from the former aggregate plugin?** Remove `laxpud-vibekits` in your client, then install the individual plugins you need. The old plugin has no compatibility alias or deprecated bundle. New users can ignore this note.

## Choose a Skill by Goal

Before trying another prompt, install its named plugin from the same marketplace. In Codex, open `/plugins` and select it. In Claude Code, enter `/plugin install <plugin-id>@laxpud-vibekits` in the Claude Code input area.

### Review a README Before Editing

Plugin: `project-docs` · Skill: [`project-docs-readme`](plugins/project-docs/skills/project-docs-readme/SKILL.md)

```text
Use project-docs-readme to review this repository's root README for a first-time user. Identify its intended audience, missing prerequisites, and shortest verified path. Then propose an ordered change plan and wait for my confirmation before editing.
```

### Create a Missing Documentation Baseline

Plugin: `project-docs` · Skill: [`project-docs-bootstrap`](plugins/project-docs/skills/project-docs-bootstrap/SKILL.md)

```text
Use project-docs-bootstrap to inspect this repository. If it lacks a usable documentation baseline, propose the smallest evidence-based set of documents and wait for my confirmation before editing.
```

### Reorganize Existing Documentation

Plugin: `project-docs` · Skill: [`project-docs-refactor`](plugins/project-docs/skills/project-docs-refactor/SKILL.md)

```text
Use project-docs-refactor to audit this repository's documentation ownership, navigation, and duplicated content. Propose an ordered migration plan and wait for my confirmation before editing.
```

### Improve Planning Documents

Plugin: `project-docs` · Skill: [`project-docs-planning`](plugins/project-docs/skills/project-docs-planning/SKILL.md)

```text
Use project-docs-planning to review this repository's active planning documents. Identify the authoritative planning entry, unclear commitment or readiness, and missing acceptance criteria, then propose changes before editing.
```

### Document Architecture and Decisions

Plugin: `project-docs` · Skill: [`project-docs-architecture`](plugins/project-docs/skills/project-docs-architecture/SKILL.md)

```text
Use project-docs-architecture to document this repository's current architecture from code evidence. Separate current and target states, propose the minimum useful diagrams or ADRs, and wait for my confirmation before editing.
```

### Refine Agent Guidance

Plugin: `project-docs` · Skill: [`project-docs-guidance`](plugins/project-docs/skills/project-docs-guidance/SKILL.md)

```text
Use project-docs-guidance to review this repository's AGENTS.md and CLAUDE.md. Find duplicated facts, missing routes, and high-risk boundaries, then propose a thin guidance structure before editing.
```

### Review or Standardize Code Comments

Plugin: `code-quality` · Skill: [`code-comment-standard`](plugins/code-quality/skills/code-comment-standard/SKILL.md)

```text
Use code-comment-standard to review comments in this repository. Report inaccurate, redundant, or missing high-value comments and propose focused improvements without changing code behavior.
```

### Create or Review pyproject.toml

Plugin: `python-project` · Skill: [`pyproject-standard`](plugins/python-project/skills/pyproject-standard/SKILL.md)

```text
Use pyproject-standard to review this Python project's pyproject.toml. Identify evidence-backed changes, show me the proposed configuration, and ask before editing.
```

After your first successful run, you can usually describe the goal naturally and let the agent select the relevant skill.

## Troubleshooting

- **A command says “not found.”** Check whether it belongs in the system terminal or the agent input area. Installer commands, `codex plugin marketplace add`, `codex`, and `claude` go in the terminal. `/plugins`, `/plugin ...`, and task prompts go inside the agent.
- **The plugin is missing from the list.** Confirm the marketplace-add command completed, then check that the required plugin is installed and enabled.
- **The agent does not use the skill.** Start a new task or session after installation and name the skill explicitly in the prompt.
- **Client installation or sign-in fails.** Follow the current [Codex CLI](https://learn.chatgpt.com/docs/codex/cli) or [Claude Code](https://code.claude.com/docs/en/installation) official guide rather than trying commands from an unofficial source.

## Current Scope

Vibekits currently supports the Codex and Claude Code plugin marketplaces:

- `code-quality` contains one code-comment skill;
- `python-project` contains one `pyproject.toml` skill;
- `project-docs` contains six documentation skills.

Each plugin is installed and versioned independently, so installing, disabling, updating, or removing one does not require changing its siblings.

## Roadmap

Direct installation through `npx skills` is planned, but it is not a supported or verified installation path yet. The required discovery, install, update, removal, and cross-client checks are tracked in the [roadmap](TODO.md#未来发展方向跨-harness-兼容与分发).

For feature requests or usage feedback, [open an issue](https://github.com/Laxpud/my-awesome-vibekits/issues).

## For Maintainers and Contributors

To browse or contribute to the source:

```bash
git clone https://github.com/Laxpud/my-awesome-vibekits.git
```

Start with the [technical documentation index](docs/index.md), [plugin catalog](plugin-catalog.json), and [active roadmap](TODO.md). Release, generated metadata, validation, and rollback details live in the linked maintainer documentation rather than this newcomer path.

## License

MIT License. See [LICENSE](LICENSE).
