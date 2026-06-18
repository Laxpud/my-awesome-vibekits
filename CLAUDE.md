# CLAUDE.md

This file provides Claude Code-specific project guidance for this repository.

## 项目定位

Vibekits 是一个平台无关的 reusable skills 和 rules 仓库。它的核心目标是沉淀可复用的 agent 工作流，并通过 Codex 与 Claude Code 的插件适配层暴露同一份技能来源。

非目标：

- 不在本仓库创建应用源码脚手架、运行时框架或项目模板。
- 不把 Codex、Claude Code 或其他平台的专属逻辑写入共享 `SKILL.md`。
- 不维护根目录 `skills/` 副本。

## 权威位置

| 内容 | 权威位置 |
| --- | --- |
| 通用技能 | `plugins/laxpud-vibekits/skills/<skill-name>/SKILL.md` |
| 可复用规则 | `rules/<rule-name>.md` |
| Codex marketplace | `.agents/plugins/marketplace.json` |
| Codex plugin manifest | `plugins/laxpud-vibekits/.codex-plugin/plugin.json` |
| Claude Code marketplace | `.claude-plugin/marketplace.json` |
| Claude Code plugin manifest | `plugins/laxpud-vibekits/.claude-plugin/plugin.json` |

`plugins/laxpud-vibekits/skills/` 是唯一技能来源。新增或移动技能时，围绕这个目录维护，不要复制到其他平台目录。

## 文档归属

- 根目录 `README.md` 是英文公开入口。
- `docs/README.cn.md` 是根 README 的中文翻译，根 README 改动时同步检查它。
- `docs/index.md` 是中文技术文档索引。
- `TODO.md` 记录活跃维护事项，使用复选框，并为非简单事项写验收标准。
- `docs/SKILL_RULE_GUIDELINES.md` 保留在 `docs/`，用于维护技能、规则和平台适配层的结构规范、同步清单和验证要求。

不要重新创建 `docs/README.md` 作为技术索引；这个项目使用 `docs/index.md` 避免与目录 README 语义混淆。

## 技能与规则维护

- 每个技能目录必须包含 `SKILL.md`，路径为 `plugins/laxpud-vibekits/skills/<skill-name>/SKILL.md`。
- `SKILL.md` frontmatter 只保留 `name` 和 `description`；`description` 要准确描述触发场景和能力边界。
- 技能正文只写执行该技能所需的流程、输入输出契约、边界条件和验证方式。
- 长期维护说明、安装介绍、发布检查和跨技能规则放到 `docs/`，不要塞进单个技能正文。
- 规则文件放在 `rules/<rule-name>.md`，保持短小、清晰、平台无关；个人全局规则备份必须在文件名和开头说明中标注备份用途。

当技能能力、技能名称、触发描述或插件定位变化时，同步检查：

- 根 README 的技能表和安装说明。
- `docs/README.cn.md` 的对应翻译。
- `docs/index.md` 和 `docs/SKILL_RULE_GUIDELINES.md` 的维护入口。
- Codex 与 Claude Code 的 plugin manifest 和 marketplace 描述。

## 平台适配边界

- Codex 专属配置只放在 `.agents/` 和 `plugins/laxpud-vibekits/.codex-plugin/`。
- Claude Code 专属配置只放在 `.claude-plugin/` 和 `plugins/laxpud-vibekits/.claude-plugin/`。
- 共享技能和规则不得假设某个平台特有的命令、目录、MCP 工具或插件安装状态。
- 同时修改 `AGENTS.md` 和 `CLAUDE.md` 时，保持共享项目事实一致，只保留各平台特有的入口说明差异。

## 常用验证

本项目是文档型仓库，无构建、测试或 lint 流程。文档或插件元数据变更后，优先执行：

```bash
.venv\Scripts\python.exe -X utf8 scripts\sync_plugin_metadata.py
.venv\Scripts\python.exe -X utf8 C:\Users\YangFan\.codex\skills\.system\skill-creator\scripts\quick_validate.py plugins\laxpud-vibekits\skills\project-docs-bootstrap
.venv\Scripts\python.exe -X utf8 C:\Users\YangFan\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py plugins\laxpud-vibekits
git diff --check
```

发布 bump 使用 `scripts\sync_plugin_metadata.py --set-version <semver>`，不要分别手工修改 manifest、marketplace 和 README 中的版本。

还应按变更范围检查 JSON 是否可解析、Markdown 相对链接是否存在、根 README 是否仍为英文，以及 `docs/README.cn.md` 是否与根 README 结构对齐。

## 安装调试命令

```bash
# Claude Code：添加本地开发插件市场
/plugin marketplace add .

# Claude Code：安装本地开发版本插件
/plugin install laxpud-vibekits@laxpud-vibekits-dev

# Claude Code：重载插件
/reload-plugins

# Codex：添加本仓库插件市场
codex plugin marketplace add Laxpud/my-awesome-vibekits

# Codex：打开插件目录后选择 laxpud-vibekits 安装
codex
/plugins
```

## 提交边界

只提交本轮相关文件。不要混入缓存、虚拟环境、本地测试输出、生成物或用户未要求处理的参考材料。
