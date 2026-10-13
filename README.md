<a id="readme-top"></a>

<div align="right">
  <strong>English</strong> | <a href="docs/README.cn.md">简体中文</a>
</div>

<div align="center">

<h1>Vibekits</h1>

<p><strong>A personal plugin marketplace for AI engineering workflows</strong><br />
<sub>Documentation · Code comments · Python projects · Task resumption</sub></p>

<p>
  <a href="#install-in-codex-or-claude-code"><picture><source media="(prefers-color-scheme: dark)" srcset="https://badgewind.agmmnn.workers.dev/Codex_CLI?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@58446D)%2Cbg-(@2B223A)%2Ctext-(@E5D8FA)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=logos:codex-dark&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@FFFFFF)" /><img height="32" src="https://badgewind.agmmnn.workers.dev/Codex_CLI?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@D7C7ED)%2Cbg-(@F3EDFC)%2Ctext-(@59416F)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=logos:codex&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@111111)" alt="Codex CLI" /></picture></a>
  &nbsp;
  <a href="#install-in-codex-or-claude-code"><picture><source media="(prefers-color-scheme: dark)" srcset="https://badgewind.agmmnn.workers.dev/Claude_Code?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@58446D)%2Cbg-(@2B223A)%2Ctext-(@E5D8FA)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=logos:claude-code&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@D97757)" /><img height="32" src="https://badgewind.agmmnn.workers.dev/Claude_Code?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@D7C7ED)%2Cbg-(@F3EDFC)%2Ctext-(@59416F)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=logos:claude-code&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@D97757)" alt="Claude Code" /></picture></a>
  &nbsp;
  <a href="LICENSE"><picture><source media="(prefers-color-scheme: dark)" srcset="https://badgewind.agmmnn.workers.dev/MIT_License?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@58446D)%2Cbg-(@2B223A)%2Ctext-(@E5D8FA)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=material-symbols:balance&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@CFADFF)" /><img height="32" src="https://badgewind.agmmnn.workers.dev/MIT_License?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@D7C7ED)%2Cbg-(@F3EDFC)%2Ctext-(@59416F)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=material-symbols:balance&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@7548A3)" alt="License: MIT" /></picture></a>
</p>

<p><sub>
  <a href="#quick-start">Quick start</a> ·
  <a href="#plugins-and-skills">Browse skills</a> ·
  <a href="docs/index.md">Documentation</a> ·
  <a href="https://github.com/Laxpud/my-awesome-vibekits/issues">Feedback</a>
</sub></p>

</div>

Vibekits is a plugin marketplace for reusable engineering workflows in Codex and Claude Code.

## Prerequisites

You need Codex or Claude Code installed and signed in, plus network access to GitHub. Open the client in the project you want to work on; you do not need to clone Vibekits to use the marketplace.

## Quick Start

Use `agent-docs-maintainer` as the installation example. Choose either client; the other plugins in [Plugins and Skills](#plugins-and-skills) use the same marketplace.

### Install in Codex or Claude Code

Add the marketplace from your **terminal**:

```bash
codex plugin marketplace add Laxpud/my-awesome-vibekits
# Or
claude plugin marketplace add Laxpud/my-awesome-vibekits
```

Start **Codex or Claude Code**:

```bash
codex
# Or
claude
```

Enter:

```text
/plugins
```

Find and install `agent-docs-maintainer` in `laxpud-vibekits`. Once it is installed and enabled, start a new session for the same project to load its skills; in Claude Code, you can also enter `/reload-plugins`. For client management details, see the [official Codex plugin guide](https://learn.chatgpt.com/docs/plugins) and the [official Claude Code plugin guide](https://code.claude.com/docs/en/discover-plugins).

**Individual skills:** Marketplace installation gets a plugin bundle. If you prefer to install selected skills directly, consult the plugin repository links below for available installation instructions and supported clients. For tools such as `npx skills`, follow the [official installation, update and removal instructions](https://github.com/vercel-labs/skills); support is defined by each independent repository.

## Plugins and Skills

Each plugin heading links to its repository; each skill links to its own instructions. The plugin ID beside the heading identifies it in `laxpud-vibekits`.

### [Agent Docs Maintainer](https://github.com/Laxpud/agent-docs-maintainer) (`agent-docs-maintainer`)

Workflows for maintaining project documentation, plans, architecture and agent guidance.

| Skill | What it does |
| --- | --- |
| [project-docs-bootstrap](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-bootstrap/SKILL.md) | Establish a minimal documentation baseline for a project. |
| [project-docs-refactor](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-refactor/SKILL.md) | Reorganize documentation structure, ownership and navigation. |
| [project-docs-readme](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-readme/SKILL.md) | Write or improve READMEs, translations and usage guides. |
| [project-docs-planning](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-planning/SKILL.md) | Organize tasks, milestones, roadmaps and plan/spec storage. |
| [project-docs-architecture](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-architecture/SKILL.md) | Maintain architecture documentation, diagrams and ADRs. |
| [project-docs-guidance](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-guidance/SKILL.md) | Maintain AGENTS.md, CLAUDE.md and scoped project rules. |
| [project-docs-progress](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-progress/SKILL.md) | Track current tasks and apply project conventions when saving plans or specs. |

### [Agent Task Resume](https://github.com/Laxpud/agent-task-resume) (`agent-task-resume`)

Explicitly invoked workflows for continuing authorized Codex tasks after quota recovery.

| Skill | What it does |
| --- | --- |
| [quota-resume](https://github.com/Laxpud/agent-task-resume/blob/main/skills/quota-resume/SKILL.md) | Schedule continuation after quota recovery and track actual execution. |

### [Agent Dev Standards](https://github.com/Laxpud/agent-dev-standards) (`agent-dev-standards`)

Development standards for reviewing code comments and Python project configuration.

| Skill | What it does |
| --- | --- |
| [code-comment-standard](https://github.com/Laxpud/agent-dev-standards/blob/main/skills/code-comment-standard/SKILL.md) | Review and improve comments that explain code behavior and data meaning. |
| [pyproject-standard](https://github.com/Laxpud/agent-dev-standards/blob/main/skills/pyproject-standard/SKILL.md) | Review Python project metadata and uv/hatchling configuration. |

## Contributing

Have a workflow you would like to see covered? [Open an issue](https://github.com/Laxpud/my-awesome-vibekits/issues) or help improve the marketplace and its documentation.

Marketplace entries and documentation belong in this repository; skill changes belong in the linked plugin repositories. For marketplace maintenance, start with the [documentation index](docs/index.md) and [maintenance guide](docs/maintenance.md).
