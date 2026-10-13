<a id="readme-top"></a>

<div align="right">
  <strong>English</strong> | <a href="docs/README.cn.md">简体中文</a>
</div>

<div align="center">

<h1>Vibekits</h1>

<p><strong>A plugin marketplace for AI engineering workflows</strong><br />
<sub>Documentation · Code comments · Python projects · Task resumption</sub></p>

<p>
  <a href="#codex-cli"><picture><source media="(prefers-color-scheme: dark)" srcset="https://badgewind.agmmnn.workers.dev/Codex_CLI?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@58446D)%2Cbg-(@2B223A)%2Ctext-(@E5D8FA)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=logos:codex-dark&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@FFFFFF)" /><img height="32" src="https://badgewind.agmmnn.workers.dev/Codex_CLI?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@D7C7ED)%2Cbg-(@F3EDFC)%2Ctext-(@59416F)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=logos:codex&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@111111)" alt="Codex CLI" /></picture></a>
  &nbsp;
  <a href="#claude-code"><picture><source media="(prefers-color-scheme: dark)" srcset="https://badgewind.agmmnn.workers.dev/Claude_Code?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@58446D)%2Cbg-(@2B223A)%2Ctext-(@E5D8FA)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=logos:claude-code&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@D97757)" /><img height="32" src="https://badgewind.agmmnn.workers.dev/Claude_Code?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@D7C7ED)%2Cbg-(@F3EDFC)%2Ctext-(@59416F)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=logos:claude-code&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@D97757)" alt="Claude Code" /></picture></a>
  &nbsp;
  <a href="LICENSE"><picture><source media="(prefers-color-scheme: dark)" srcset="https://badgewind.agmmnn.workers.dev/MIT_License?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@58446D)%2Cbg-(@2B223A)%2Ctext-(@E5D8FA)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=material-symbols:balance&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@CFADFF)" /><img height="32" src="https://badgewind.agmmnn.workers.dev/MIT_License?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@D7C7ED)%2Cbg-(@F3EDFC)%2Ctext-(@59416F)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=material-symbols:balance&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@7548A3)" alt="License: MIT" /></picture></a>
</p>

<p><sub>
  <a href="#quick-start">Quick start</a> ·
  <a href="#choose-a-skill-by-goal">Browse skills</a> ·
  <a href="docs/index.md">Documentation</a> ·
  <a href="https://github.com/Laxpud/my-awesome-vibekits/issues">Feedback</a>
</sub></p>

</div>

Vibekits is a Codex and Claude Code plugin marketplace for reusable engineering workflows. Add the marketplace, install the plugin that fits your task, and ask your coding agent to use its skills.

## What You Can Do

The marketplace lists three independent plugins and ten skills:

| Plugin | Use it for | Skills |
| --- | --- | --- |
| [Agent Docs Maintainer](https://github.com/Laxpud/agent-docs-maintainer) (`agent-docs-maintainer`) | README, documentation structure, planning, architecture, agent guidance and progress. | 7 |
| [Agent Task Resume](https://github.com/Laxpud/agent-task-resume) (`agent-task-resume`) | Scheduling continuation of authorized work after quota recovery. | 1 |
| [Agent Dev Standards](https://github.com/Laxpud/agent-dev-standards) (`agent-dev-standards`) | Code comments and Python project metadata. | 2 |

A **skill** is a reusable task workflow; a **plugin** packages related skills; this **marketplace** tells the client where to fetch each plugin. Plugin content and versions are maintained in the linked independent repositories, currently fetched from their `main` branches.

Both plugin marketplaces are maintained. The quota-resume execution guidance covers Codex; loading that skill in another client does not establish support for its quota or scheduling APIs. Direct installation through `npx skills` remains [planned](docs/roadmap.md#独立-skill-分发).

This marketplace maintains plugin sources, release snapshots, generated catalogs, and installation/update instructions. Clients perform installation and manage installed plugins; full client lifecycle testing is outside this repository's delivery requirements.

## Prerequisites

Choose one client and open it in the project you want to work on. You need a working client installation, sign-in and network access to GitHub; you do not need to clone Vibekits to use its marketplace.

### Codex CLI

Follow the [official Codex CLI guide](https://learn.chatgpt.com/docs/codex/cli) to install and sign in. In your system terminal, `codex --version` should print a version and `codex` should open your project.

### Claude Code

Follow the [official Claude Code installation guide](https://code.claude.com/docs/en/installation). In your system terminal, `claude --version` should print a version and `claude` should open your project.

## Quick Start

For a first run, install `agent-docs-maintainer` and ask it to review your README. Choose one client below.

### Install in Codex

In your **system terminal**, add the marketplace and start Codex from your project directory:

```bash
codex plugin marketplace add Laxpud/my-awesome-vibekits
codex
```

In the **Codex input area**, enter:

```text
/plugins
```

Find `agent-docs-maintainer` in `laxpud-vibekits`, install and enable it, then start a new session for the same project to load its skills. See the [official plugin guide](https://learn.chatgpt.com/docs/plugins) for client details.

### Install in Claude Code

Start Claude Code from your project directory. In the **Claude Code input area**, enter these commands one at a time:

```text
/plugin marketplace add https://github.com/Laxpud/my-awesome-vibekits
/plugin install agent-docs-maintainer@laxpud-vibekits
```

Follow the client prompts to finish installation, then start a new session for this first run. Plugin management details are in the [official guide](https://code.claude.com/docs/en/discover-plugins).

### Run Your First Skill

Paste this into the new session:

```text
Use $agent-docs-maintainer:project-docs-readme to review this repository's README for a new user. Identify missing prerequisites and the shortest usable path. Propose changes and wait for my confirmation before editing.
```

Success means the agent explains the README's audience, prerequisites and first-use path, then proposes changes without editing files. Review the proposal and authorize the changes you want.

> **Using the previous plugins?** Install the new plugin, confirm it works, then disable or remove its old counterpart. Skill IDs stay the same; plugin prefixes change. See the [migration mapping](docs/maintenance.md#客户端更新与旧安装迁移).

## Choose a Skill by Goal

Install the named plugin before using its prompt: select it through `/plugins` in Codex, or run `/plugin install <plugin-id>@laxpud-vibekits` inside Claude Code. Each plugin can be managed independently.

### Agent Docs Maintainer

**Review a README** — [`project-docs-readme`](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-readme/SKILL.md): use the [first-run prompt](#run-your-first-skill).

**Create a missing documentation baseline** — [`project-docs-bootstrap`](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-bootstrap/SKILL.md):

```text
Use $agent-docs-maintainer:project-docs-bootstrap to inspect this repository and propose the smallest useful documentation baseline before editing.
```

**Reorganize existing documentation** — [`project-docs-refactor`](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-refactor/SKILL.md):

```text
Use $agent-docs-maintainer:project-docs-refactor to review documentation ownership, navigation and duplication. Propose a migration plan before editing.
```

**Improve planning documents** — [`project-docs-planning`](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-planning/SKILL.md):

```text
Use $agent-docs-maintainer:project-docs-planning to review current and future tasks, commitments and acceptance criteria. Propose changes before editing.
```

**Document architecture** — [`project-docs-architecture`](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-architecture/SKILL.md):

```text
Use $agent-docs-maintainer:project-docs-architecture to inspect the current implementation and propose an architecture overview with useful diagrams before editing.
```

**Refine agent guidance** — [`project-docs-guidance`](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-guidance/SKILL.md):

```text
Use $agent-docs-maintainer:project-docs-guidance to review AGENTS.md and CLAUDE.md. Propose clear reading routes and necessary project boundaries before editing.
```

**Maintain current progress** — [`project-docs-progress`](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-progress/SKILL.md):

```text
Use $agent-docs-maintainer:project-docs-progress to continue the current authorized TODO task and update only checkboxes and necessary blockers.
```

Progress may run automatically in Codex for existing tasks and project plan/spec file requests; explicitly invoke the other six documentation skills. Detailed writing rules and file-saving conventions belong in the plugin's [usage guide](https://github.com/Laxpud/agent-docs-maintainer/blob/main/docs/usage.md).

### Agent Task Resume

**Resume authorized work after quota recovery** — [`quota-resume`](https://github.com/Laxpud/agent-task-resume/blob/main/skills/quota-resume/SKILL.md):

```text
Use $agent-task-resume:quota-resume to schedule continuation of this authorized task after its five-hour quota recovers. Track actual execution, avoid duplicate submissions, and stop when complete or when my input is needed.
```

Invoke it explicitly. Installing the plugin does not start a background task. Execution guidance and authorization limits are maintained in the [plugin repository](https://github.com/Laxpud/agent-task-resume).

### Agent Dev Standards

**Review code comments** — [`code-comment-standard`](https://github.com/Laxpud/agent-dev-standards/blob/main/skills/code-comment-standard/SKILL.md):

```text
Use $agent-dev-standards:code-comment-standard to review comments in these files. Explain unclear processing steps and data meaning, then show focused rewrites without editing.
```

Invoke this skill explicitly for a focused review or edit. See its [comment examples](https://github.com/Laxpud/agent-dev-standards/blob/main/skills/code-comment-standard/references/comment-examples.md); everyday commenting preferences belong in your global or project instructions.

**Review Python project metadata** — [`pyproject-standard`](https://github.com/Laxpud/agent-dev-standards/blob/main/skills/pyproject-standard/SKILL.md):

```text
Use $agent-dev-standards:pyproject-standard to review this project's pyproject.toml. Show evidence-backed configuration changes before editing.
```

## Troubleshooting

- **Command not found:** check where you entered it. `codex ...` and `claude ...` belong in the system terminal; `/plugins`, `/plugin ...` and task prompts belong inside the client.
- **Plugin missing:** confirm the marketplace was added and the plugin is installed and enabled. Refresh the marketplace if you are using an older snapshot.
- **Skill not used:** start a new session after installation and name the plugin and skill explicitly.
- **Installation or sign-in fails:** use the linked official client guide. Marketplace metadata checks do not verify your account or client installation.

## More Documentation

- [Documentation index](docs/index.md): user and maintainer reading paths; maintainer guides are in Chinese.
- [Market architecture](docs/tech/architecture.md) and [maintenance guide](docs/maintenance.md): implementation, snapshot updates, validation and rollback.
- [Current work](TODO.md) and [roadmap](docs/roadmap.md): marketplace maintenance progress and future distribution.

Marketplace publication does not automatically update daily plugin installations. Plugin content, examples, designs and reviews remain in each independent repository.

## Contributing

Share a missing use case or [open an issue](https://github.com/Laxpud/my-awesome-vibekits/issues). Contributions to the marketplace belong here; skill content belongs in the corresponding plugin repository.

For marketplace development, clone this repository and start with the [architecture overview](docs/tech/architecture.md), [catalog](plugin-catalog.json) and [maintenance guide](docs/maintenance.md):

```bash
git clone https://github.com/Laxpud/my-awesome-vibekits.git
```
