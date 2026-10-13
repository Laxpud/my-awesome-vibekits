<a id="readme-top"></a>

<div align="right">
  <a href="../README.md">English</a> | <strong>简体中文</strong>
</div>

<div align="center">

<h1>Vibekits</h1>

<p><strong>面向 AI 工程工作流的个人插件市场</strong><br />
<sub>项目文档 · 代码注释 · Python 项目 · 任务续跑</sub></p>

<p>
  <a href="#在-codex-或-claude-code-中安装"><picture><source media="(prefers-color-scheme: dark)" srcset="https://badgewind.agmmnn.workers.dev/Codex_CLI?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@58446D)%2Cbg-(@2B223A)%2Ctext-(@E5D8FA)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=logos:codex-dark&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@FFFFFF)" /><img height="32" src="https://badgewind.agmmnn.workers.dev/Codex_CLI?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@D7C7ED)%2Cbg-(@F3EDFC)%2Ctext-(@59416F)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=logos:codex&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@111111)" alt="Codex CLI" /></picture></a>
  &nbsp;
  <a href="#在-codex-或-claude-code-中安装"><picture><source media="(prefers-color-scheme: dark)" srcset="https://badgewind.agmmnn.workers.dev/Claude_Code?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@58446D)%2Cbg-(@2B223A)%2Ctext-(@E5D8FA)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=logos:claude-code&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@D97757)" /><img height="32" src="https://badgewind.agmmnn.workers.dev/Claude_Code?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@D7C7ED)%2Cbg-(@F3EDFC)%2Ctext-(@59416F)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=logos:claude-code&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@D97757)" alt="Claude Code" /></picture></a>
  &nbsp;
  <a href="../LICENSE"><picture><source media="(prefers-color-scheme: dark)" srcset="https://badgewind.agmmnn.workers.dev/MIT_License?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@58446D)%2Cbg-(@2B223A)%2Ctext-(@E5D8FA)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=material-symbols:balance&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@CFADFF)" /><img height="32" src="https://badgewind.agmmnn.workers.dev/MIT_License?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@D7C7ED)%2Cbg-(@F3EDFC)%2Ctext-(@59416F)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=material-symbols:balance&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@7548A3)" alt="许可证：MIT" /></picture></a>
</p>

<p><sub>
  <a href="#快速开始">快速开始</a> ·
  <a href="#插件与技能">浏览技能</a> ·
  <a href="index.md">文档</a> ·
  <a href="https://github.com/Laxpud/my-awesome-vibekits/issues">反馈问题</a>
</sub></p>

</div>

Vibekits 是面向 Codex 与 Claude Code 的插件市场，收录可复用的工程工作流。

## 环境准备

你需要已安装并登录的 Codex 或 Claude Code，以及访问 GitHub 的网络。在希望处理的项目中打开客户端即可，使用市场无需先克隆 Vibekits。

## 快速开始

下面以 `agent-docs-maintainer` 演示安装，选择一个客户端即可。[插件与技能](#插件与技能)中的其他插件也通过同一个市场安装。

### 在 Codex 或 Claude Code 中安装

通过**终端**添加市场：

```bash
codex plugin marketplace add Laxpud/my-awesome-vibekits
# 或者
claude plugin marketplace add Laxpud/my-awesome-vibekits
```

启动 **Codex 或 Claude Code**：

```bash
codex
# 或
claude
```

输入：

```text
/plugins
```

在 `laxpud-vibekits` 中找到并安装 `agent-docs-maintainer`。安装并启用后，为同一项目启动新会话以加载技能；Claude Code 可以输入 `/reload-plugins`。具体客户端管理操作见 [Codex 官方插件指南](https://learn.chatgpt.com/docs/plugins) 和 [Claude Code 官方插件指南](https://code.claude.com/docs/en/discover-plugins)。

**独立安装 Skill：**通过插件市场安装会获取整个插件包。若只想直接安装选定的技能，请从下方插件仓库查看其提供的安装说明与客户端支持范围。使用 `npx skills` 等工具时，安装、更新和移除操作见[官方说明](https://github.com/vercel-labs/skills)；具体支持情况以独立仓库为准。

## 插件与技能

插件标题链接到对应仓库，技能名称链接到其操作说明；标题旁的插件 ID 用于在 `laxpud-vibekits` 中查找插件。

### [Agent Docs Maintainer](https://github.com/Laxpud/agent-docs-maintainer)（`agent-docs-maintainer`）

维护项目文档、规划、架构与 Agent 工作规则的工作流。

| Skill | 一句话介绍 |
| --- | --- |
| [project-docs-bootstrap](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-bootstrap/SKILL.md) | 为项目建立最小文档基线。 |
| [project-docs-refactor](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-refactor/SKILL.md) | 整理文档结构、内容归属与阅读入口。 |
| [project-docs-readme](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-readme/SKILL.md) | 编写或改进 README、正式翻译与使用说明。 |
| [project-docs-planning](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-planning/SKILL.md) | 组织任务、里程碑、路线图与 plan/spec 保存约定。 |
| [project-docs-architecture](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-architecture/SKILL.md) | 维护架构说明、图示与 ADR。 |
| [project-docs-guidance](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-guidance/SKILL.md) | 维护 AGENTS.md、CLAUDE.md 与目录级项目规则。 |
| [project-docs-progress](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-progress/SKILL.md) | 跟踪当前任务，并按项目约定保存计划或规格文件。 |

### [Agent Task Resume](https://github.com/Laxpud/agent-task-resume)（`agent-task-resume`）

显式调用后，为已授权的 Codex 任务安排额度恢复后的继续执行。

| Skill | 一句话介绍 |
| --- | --- |
| [quota-resume](https://github.com/Laxpud/agent-task-resume/blob/main/skills/quota-resume/SKILL.md) | 安排额度恢复后的任务续跑，并追踪实际执行。 |

### [Agent Dev Standards](https://github.com/Laxpud/agent-dev-standards)（`agent-dev-standards`）

用于代码注释审查与 Python 项目配置的开发规范。

| Skill | 一句话介绍 |
| --- | --- |
| [code-comment-standard](https://github.com/Laxpud/agent-dev-standards/blob/main/skills/code-comment-standard/SKILL.md) | 审查和改进代码注释，交代处理过程与数据含义。 |
| [pyproject-standard](https://github.com/Laxpud/agent-dev-standards/blob/main/skills/pyproject-standard/SKILL.md) | 审查 Python 项目元数据及 uv/hatchling 配置。 |

## 参与贡献

如果现有工作流还不能满足你的需要，欢迎[提出 Issue](https://github.com/Laxpud/my-awesome-vibekits/issues)，也欢迎共同改进市场与文档。

市场收录与文档向本仓库贡献，技能内容向对应独立插件仓库贡献。维护市场时，从[文档索引](index.md)和[维护指南](maintenance.md)开始。
