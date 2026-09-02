# Vibekits

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](../LICENSE)
[![English](https://img.shields.io/badge/README-English-C026D3)](../README.md)

[技术文档](index.md) · [路线图](../TODO.md) · [反馈问题](https://github.com/Laxpud/my-awesome-vibekits/issues)

Vibekits 是我个人孵化的一组 Codex 与 Claude Code 可复用工作流。它不是一个需要单独运行的应用：安装与你目标对应的插件，再让编码 Agent 使用其中的 Skill 即可。

当前目录包含三个可独立安装的插件和八个 Skill，覆盖代码注释、Python 项目元数据与仓库文档。已经发布的 Skill 面向日常使用；反馈和新想法会继续在这个仓库中孵化。

## 适合谁

如果你的电脑上已经有一个项目，并且会使用——或愿意安装——Codex CLI 或 Claude Code 中的任意一个，就可以从这里开始。按照快速开始操作前，不需要理解 marketplace、plugin 或 Skill。

Vibekits 的作用是让编码 Agent 遵循可重复的工作流。它不能替代 Codex 或 Claude Code，也不提供自己的图形应用。

## 工作方式

- **Agent：** Codex 或 Claude Code，也就是读取你的项目并执行请求的工具。
- **Skill：** 针对一类任务的可复用指令，例如审查 README。
- **Plugin：** 包含一个或多个相关 Skill 的可安装软件包。
- **Marketplace：** 告诉 Agent 去哪里查找这些 Plugin 的目录。

你只需添加一次这个仓库的 marketplace，按需安装一个 Plugin，然后用自然语言描述任务。第一次使用或希望指定工作流时，显式写出 Skill 名最稳妥。

## 前置条件

从下面选择**一个**客户端。如果它已经能在你的项目中正常打开，可以直接跳到[快速开始](#快速开始)。

**终端**是输入安装和启动命令的窗口：macOS 使用“终端”，Linux 使用终端应用，Windows 使用 PowerShell。以 `/` 开头的命令稍后要输入 Codex 或 Claude Code，而不是这个系统终端。

### Codex CLI

通过 [Codex CLI 官方指南](https://learn.chatgpt.com/docs/codex/cli)查看最新要求和其他安装方式。按你的系统选择官方独立安装命令。

**macOS 或 Linux——终端**

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

**Windows——PowerShell**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
```

在你的项目目录中打开终端，验证安装，然后启动 Codex：

```bash
codex --version
codex
```

第一次运行时按照提示登录。版本命令能输出版本，并且 Codex 输入界面的工作目录是你的项目，就表示准备完成。

### Claude Code

通过 [Claude Code 官方安装指南](https://code.claude.com/docs/en/installation)查看最新要求、账户权限和其他安装方式。按你的系统选择官方推荐的原生安装命令。

**macOS、Linux 或 WSL——终端**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows——PowerShell**

```powershell
irm https://claude.ai/install.ps1 | iex
```

在你的项目目录中打开终端，验证安装，然后启动 Claude Code：

```bash
claude --version
claude
```

如果出现提示，按照浏览器流程登录。版本命令能输出版本，并且 Claude Code 输入界面打开的是你的项目，就表示准备完成。

## 快速开始

第一次体验只安装 `project-docs`，并让 `project-docs-readme` 对 README 做只读审查。选择你已经在用的客户端即可，不需要同时安装两个。

### 在 Codex 中安装

在系统终端中添加这个 marketplace，并从项目目录启动 Codex：

```bash
codex plugin marketplace add Laxpud/my-awesome-vibekits
codex
```

在 Codex 输入区中输入：

```text
/plugins
```

找到 `project-docs`，安装并启用它。然后为同一个项目新建 Codex 任务，让刚安装的 Skill 被加载。

### 在 Claude Code 中安装

从项目目录启动 Claude Code。在 **Claude Code 输入区**中逐条输入：

```text
/plugin marketplace add https://github.com/Laxpud/my-awesome-vibekits
/plugin install project-docs@laxpud-vibekits
```

然后为同一个项目新建 Claude Code 会话，让刚安装的 Skill 被加载。

### 运行第一个 Skill

把下面这段话粘贴到新的 Codex 任务或 Claude Code 会话：

```text
使用 project-docs-readme 从首次访问者的视角审查这个仓库的根 README。识别目标读者、缺失的前置条件和当前最短已验证路径，然后给出按优先级排序的修改计划；在我确认前不要编辑文件。
```

### 成功时会看到什么

Agent 应该报告：

1. README 面向谁；
2. 哪些前置条件缺失或不清楚；
3. 新用户真正能走通的最短路径；
4. 按顺序排列的修改计划。

此时它**不应编辑文件**。先检查计划；如果没有问题，可以明确回复：

```text
计划没有问题。请开始实施，保持正式翻译同步，并验证所有改动过的链接和命令。
```

> **正在从原聚合 Plugin 迁移？** 先在客户端中移除 `laxpud-vibekits`，再安装你需要的独立 Plugin。旧 Plugin 不提供兼容别名或 deprecated bundle。新用户可以忽略这段说明。

## 按目标选择 Skill

尝试下面的其他提示词前，先从同一个 marketplace 安装对应 Plugin。在 Codex 中打开 `/plugins` 并选择它；在 Claude Code 输入区中输入 `/plugin install <plugin-id>@laxpud-vibekits`。

### 编辑前审查 README

Plugin：`project-docs` · Skill：[`project-docs-readme`](../plugins/project-docs/skills/project-docs-readme/SKILL.md)

```text
使用 project-docs-readme 从首次访问者的视角审查这个仓库的根 README。识别目标读者、缺失的前置条件和当前最短已验证路径，然后给出按优先级排序的修改计划；在我确认前不要编辑文件。
```

### 创建缺失的文档基线

Plugin：`project-docs` · Skill：[`project-docs-bootstrap`](../plugins/project-docs/skills/project-docs-bootstrap/SKILL.md)

```text
使用 project-docs-bootstrap 检查这个仓库。如果它缺少可用的文档基线，提出一组基于证据的最小文档，并在我确认前不要编辑文件。
```

### 重组现有文档

Plugin：`project-docs` · Skill：[`project-docs-refactor`](../plugins/project-docs/skills/project-docs-refactor/SKILL.md)

```text
使用 project-docs-refactor 审查这个仓库的文档所有权、导航和重复内容。给出按顺序排列的迁移计划，并在我确认前不要编辑文件。
```

### 改进规划文档

Plugin：`project-docs` · Skill：[`project-docs-planning`](../plugins/project-docs/skills/project-docs-planning/SKILL.md)

```text
使用 project-docs-planning 审查这个仓库的活动规划文档。识别权威规划入口、含糊的承诺或就绪状态，以及缺失的验收条件，然后在编辑前提出修改方案。
```

### 记录架构与决策

Plugin：`project-docs` · Skill：[`project-docs-architecture`](../plugins/project-docs/skills/project-docs-architecture/SKILL.md)

```text
使用 project-docs-architecture 根据代码证据记录这个仓库的当前架构。区分当前状态和目标状态，提出真正需要的最小图表或 ADR，并在我确认前不要编辑文件。
```

### 精简 Agent 指导

Plugin：`project-docs` · Skill：[`project-docs-guidance`](../plugins/project-docs/skills/project-docs-guidance/SKILL.md)

```text
使用 project-docs-guidance 审查这个仓库的 AGENTS.md 和 CLAUDE.md。找出重复事实、缺失路由和高风险边界，然后在编辑前提出精简的指导结构。
```

### 审查或规范代码注释

Plugin：`code-quality` · Skill：[`code-comment-standard`](../plugins/code-quality/skills/code-comment-standard/SKILL.md)

```text
使用 code-comment-standard 审查这个仓库的代码注释。报告不准确、冗余或缺失的高价值注释，并在不改变代码行为的前提下提出聚焦的改进方案。
```

### 创建或审查 pyproject.toml

Plugin：`python-project` · Skill：[`pyproject-standard`](../plugins/python-project/skills/pyproject-standard/SKILL.md)

```text
使用 pyproject-standard 审查这个 Python 项目的 pyproject.toml。识别有仓库证据支持的改动，向我展示拟议配置，并在编辑前询问。
```

第一次成功使用后，通常可以只用自然语言描述目标，让 Agent 自动选择相关 Skill。

## 故障排查

- **提示“找不到命令”。** 先确认它应该输入系统终端还是 Agent 输入区。安装命令、`codex plugin marketplace add`、`codex` 和 `claude` 输入终端；`/plugins`、`/plugin ...` 和任务提示词输入 Agent。
- **插件没有出现在列表里。** 确认添加 marketplace 的命令已经成功，再检查所需 Plugin 是否已经安装并启用。
- **Agent 没有使用 Skill。** 安装后新建任务或会话，并在提示词中显式写出 Skill 名。
- **客户端安装或登录失败。** 按最新的 [Codex CLI](https://learn.chatgpt.com/docs/codex/cli) 或 [Claude Code](https://code.claude.com/docs/en/installation) 官方指南处理，不要尝试非官方来源中的命令。

## 当前范围

Vibekits 当前支持 Codex 和 Claude Code 的 Plugin Marketplace：

- `code-quality` 包含一个代码注释 Skill；
- `python-project` 包含一个 `pyproject.toml` Skill；
- `project-docs` 包含六个文档 Skill。

每个 Plugin 都独立安装和维护版本，因此安装、禁用、更新或移除其中一个时，不需要改变其他 Plugin。

## 路线图

未来计划支持通过 `npx skills` 直接安装，但它目前还不是受支持或经过验证的安装路径。所需的发现、安装、更新、移除与跨客户端门禁记录在[路线图](../TODO.md#未来发展方向跨-harness-兼容与分发)中。

如果有功能建议或使用反馈，欢迎[提交 Issue](https://github.com/Laxpud/my-awesome-vibekits/issues)。

## 面向维护者与贡献者

如需浏览源码或参与贡献：

```bash
git clone https://github.com/Laxpud/my-awesome-vibekits.git
```

从[技术文档索引](index.md)、[插件 Catalog](../plugin-catalog.json)和[当前路线图](../TODO.md)开始。发布、生成元数据、验证和回滚细节保留在这些维护文档中，不放进新手路径。

## 许可证

MIT License。参见 [LICENSE](../LICENSE)。
