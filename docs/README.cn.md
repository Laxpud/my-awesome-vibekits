<a id="readme-top"></a>

<div align="right">
  <a href="../README.md">English</a> | <strong>简体中文</strong>
</div>

<div align="center">

<h1>Vibekits</h1>

<p><strong>面向 AI 工程工作流的插件市场</strong><br />
<sub>项目文档 · 代码注释 · Python 项目 · 任务续跑</sub></p>

<p>
  <a href="#codex-cli"><picture><source media="(prefers-color-scheme: dark)" srcset="https://badgewind.agmmnn.workers.dev/Codex_CLI?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@58446D)%2Cbg-(@2B223A)%2Ctext-(@E5D8FA)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=logos:codex-dark&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@FFFFFF)" /><img height="32" src="https://badgewind.agmmnn.workers.dev/Codex_CLI?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@D7C7ED)%2Cbg-(@F3EDFC)%2Ctext-(@59416F)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=logos:codex&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@111111)" alt="Codex CLI" /></picture></a>
  &nbsp;
  <a href="#claude-code"><picture><source media="(prefers-color-scheme: dark)" srcset="https://badgewind.agmmnn.workers.dev/Claude_Code?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@58446D)%2Cbg-(@2B223A)%2Ctext-(@E5D8FA)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=logos:claude-code&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@D97757)" /><img height="32" src="https://badgewind.agmmnn.workers.dev/Claude_Code?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@D7C7ED)%2Cbg-(@F3EDFC)%2Ctext-(@59416F)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=logos:claude-code&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@D97757)" alt="Claude Code" /></picture></a>
  &nbsp;
  <a href="../LICENSE"><picture><source media="(prefers-color-scheme: dark)" srcset="https://badgewind.agmmnn.workers.dev/MIT_License?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@58446D)%2Cbg-(@2B223A)%2Ctext-(@E5D8FA)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=material-symbols:balance&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@CFADFF)" /><img height="32" src="https://badgewind.agmmnn.workers.dev/MIT_License?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px)%2Crounded-full%2Cborder%2Cborder-solid%2Cborder-(@D7C7ED)%2Cbg-(@F3EDFC)%2Ctext-(@59416F)&amp;leftStyle=h-full%2Cbg-transparent%2Crounded-full%2Cpx-3%2Cpy-0%2Ctext-(12px)%2Cleading-(16px)%2Cfont-medium&amp;icon=material-symbols:balance&amp;iconStyle=w-(15px)%2Ch-(15px)%2Cmr-(5px)%2C-translate-y-(0.75px)%2Ctext-(@7548A3)" alt="许可证：MIT" /></picture></a>
</p>

<p><sub>
  <a href="#快速开始">快速开始</a> ·
  <a href="#按目标选择-skill">浏览技能</a> ·
  <a href="index.md">文档</a> ·
  <a href="https://github.com/Laxpud/my-awesome-vibekits/issues">反馈问题</a>
</sub></p>

</div>

Vibekits 是 Codex 与 Claude Code 的插件市场，收录可复用的工程工作流。添加市场、安装适合当前任务的插件，再让编码 Agent 使用其中的技能。

## 适合做什么

当前市场收录三个独立插件和十个技能：

| 插件 | 用途 | 技能数 |
| --- | --- | --- |
| [Agent Docs Maintainer](https://github.com/Laxpud/agent-docs-maintainer)（`agent-docs-maintainer`） | README、文档结构、规划、架构、Agent 指导与进度维护。 | 7 |
| [Agent Task Resume](https://github.com/Laxpud/agent-task-resume)（`agent-task-resume`） | 额度恢复后，安排继续执行已授权工作。 | 1 |
| [Agent Dev Standards](https://github.com/Laxpud/agent-dev-standards)（`agent-dev-standards`） | 代码注释与 Python 项目元数据。 | 2 |

**Skill** 是可复用的任务工作流，**Plugin** 将相关技能打包，**Marketplace** 告诉客户端从哪里获取插件。插件内容和版本在上述独立仓库维护，目前从各仓库的 `main` 分支获取。

本市场维护两端插件市场支持。额度续跑技能的执行资料覆盖 Codex，在其他客户端加载技能不代表支持其额度或调度接口。通过 `npx skills` 直接安装仍属于[未来安排](roadmap.md#独立-skill-分发)。

## 环境准备

选择一个客户端，在你希望处理的项目中打开它。你需要可用的客户端、登录状态及访问 GitHub 的网络；使用市场无需先克隆 Vibekits。

### Codex CLI

按 [Codex CLI 官方指南](https://learn.chatgpt.com/docs/codex/cli)完成安装和登录。在系统终端中，`codex --version` 应输出版本，`codex` 应能打开你的项目。

### Claude Code

按 [Claude Code 官方安装指南](https://code.claude.com/docs/en/installation)完成准备。在系统终端中，`claude --version` 应输出版本，`claude` 应能打开你的项目。

## 快速开始

第一次体验安装 `agent-docs-maintainer`，让它审查你的 README。选择下面一个客户端即可。

### 在 Codex 中安装

在**系统终端**添加市场，并从你的项目目录启动 Codex：

```bash
codex plugin marketplace add Laxpud/my-awesome-vibekits
codex
```

在 **Codex 输入区**输入：

```text
/plugins
```

在 `laxpud-vibekits` 中找到 `agent-docs-maintainer`，安装并启用，然后为同一项目启动新会话以加载技能。客户端细节见[官方插件指南](https://learn.chatgpt.com/docs/plugins)。

### 在 Claude Code 中安装

从你的项目目录启动 Claude Code，在 **Claude Code 输入区**逐条输入：

```text
/plugin marketplace add https://github.com/Laxpud/my-awesome-vibekits
/plugin install agent-docs-maintainer@laxpud-vibekits
```

按客户端提示完成安装，然后为这次首次体验启动新会话。插件管理细节见[官方指南](https://code.claude.com/docs/en/discover-plugins)。

### 运行第一个技能

在新会话中粘贴：

```text
使用 $agent-docs-maintainer:project-docs-readme 从新用户的视角审查这个仓库的 README。识别缺失的前置条件和最短可用路径，提出修改方案；在我确认前不要编辑文件。
```

成功时，Agent 会说明 README 的读者、前置条件和首次使用路径，然后提出方案，此时不编辑文件。审阅方案后，再授权你希望落实的修改。

> **仍在使用旧插件？** 先安装新插件并确认可用，再禁用或移除对应旧插件。Skill ID 保持不变，插件调用前缀有变化，见[迁移对应表](maintenance.md#客户端更新与旧安装迁移)。

## 按目标选择 Skill

先安装提示词对应的插件：Codex 中通过 `/plugins` 选择；Claude Code 中输入 `/plugin install <plugin-id>@laxpud-vibekits`。每个插件都可以独立管理。

### Agent Docs Maintainer

**审查 README**——[`project-docs-readme`](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-readme/SKILL.md)：使用上方[首次体验提示词](#运行第一个技能)。

**创建缺失的文档基线**——[`project-docs-bootstrap`](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-bootstrap/SKILL.md)：

```text
使用 $agent-docs-maintainer:project-docs-bootstrap 检查这个仓库，在编辑前提出最小且有用的文档基线方案。
```

**重组已有文档**——[`project-docs-refactor`](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-refactor/SKILL.md)：

```text
使用 $agent-docs-maintainer:project-docs-refactor 审查文档职责、导航和重复内容，在编辑前提出迁移方案。
```

**改进规划文档**——[`project-docs-planning`](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-planning/SKILL.md)：

```text
使用 $agent-docs-maintainer:project-docs-planning 审查当前与未来任务、实施承诺和验收条件，在编辑前提出修改方案。
```

**记录架构**——[`project-docs-architecture`](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-architecture/SKILL.md)：

```text
使用 $agent-docs-maintainer:project-docs-architecture 检查当前实现，在编辑前提出架构总览及有用的图示方案。
```

**精简 Agent 指导**——[`project-docs-guidance`](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-guidance/SKILL.md)：

```text
使用 $agent-docs-maintainer:project-docs-guidance 审查 AGENTS.md 与 CLAUDE.md，在编辑前提出清晰的阅读路由和必要项目边界。
```

**维护当前进度**——[`project-docs-progress`](https://github.com/Laxpud/agent-docs-maintainer/blob/main/skills/project-docs-progress/SKILL.md)：

```text
使用 $agent-docs-maintainer:project-docs-progress 继续 TODO 中当前已授权的任务，只更新勾选和必要阻塞。
```

Progress 在 Codex 中可自动用于已有任务和项目 plan/spec 文件请求；其余六个文档技能需要显式调用。详细写作规则与文件保存约定见插件的[使用说明](https://github.com/Laxpud/agent-docs-maintainer/blob/main/docs/usage.md)。

### Agent Task Resume

**额度恢复后继续已授权工作**——[`quota-resume`](https://github.com/Laxpud/agent-task-resume/blob/main/skills/quota-resume/SKILL.md)：

```text
使用 $agent-task-resume:quota-resume 安排五小时额度恢复后继续当前已授权任务。追踪实际执行，避免重复投递，完成或需要我提供信息时停止。
```

此技能需要显式调用。安装插件本身不会启动后台任务；执行资料和授权限制在[插件仓库](https://github.com/Laxpud/agent-task-resume)维护。

### Agent Dev Standards

**审查代码注释**——[`code-comment-standard`](https://github.com/Laxpud/agent-dev-standards/blob/main/skills/code-comment-standard/SKILL.md)：

```text
使用 $agent-dev-standards:code-comment-standard 审查这些文件的注释。解释不清楚的处理步骤和数据含义，展示聚焦的改写示例，不编辑文件。
```

此技能需要显式调用，用于专项审查或整改，参见[注释案例](https://github.com/Laxpud/agent-dev-standards/blob/main/skills/code-comment-standard/references/comment-examples.md)；日常注释偏好由全局或项目指令维护。

**审查 Python 项目元数据**——[`pyproject-standard`](https://github.com/Laxpud/agent-dev-standards/blob/main/skills/pyproject-standard/SKILL.md)：

```text
使用 $agent-dev-standards:pyproject-standard 审查这个项目的 pyproject.toml，在编辑前展示有实际依据的配置修改。
```

## 常见问题

- **找不到命令：** 确认输入位置。`codex ...` 和 `claude ...` 输入系统终端；`/plugins`、`/plugin ...` 和任务提示词输入客户端。
- **找不到插件：** 确认市场已添加，目标插件已安装并启用；使用旧快照时先刷新市场。
- **没有使用技能：** 安装后启动新会话，在提示词中明确写出插件和技能名。
- **安装或登录失败：** 按上方官方客户端指南排查；市场元数据检查不验证你的账户或客户端安装。

## 更多文档

- [文档索引](index.md)：用户与维护者的阅读路径；维护文档使用中文。
- [市场架构](tech/architecture.md)与[维护指南](maintenance.md)：实现、快照更新、验证及回退。
- [当前工作](../TODO.md)与[路线图](roadmap.md)：当前任务、未来分发和客户端验证安排。

市场发布不会自动更新日常插件安装。插件内容、例库、设计和审查继续由各独立仓库维护。

## 参与贡献

欢迎提出尚未覆盖的使用场景或[提交 Issue](https://github.com/Laxpud/my-awesome-vibekits/issues)。市场维护向本仓库贡献，技能内容向对应独立插件仓库贡献。

开发市场时克隆本仓库，从[架构总览](tech/architecture.md)、[catalog](../plugin-catalog.json)和[维护指南](maintenance.md)开始：

```bash
git clone https://github.com/Laxpud/my-awesome-vibekits.git
```
