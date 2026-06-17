# Skill and Rule Guidelines

本规范用于维护 Vibekits 的通用技能、可复用规则和平台适配层。目标是让仓库既能被 Claude Code、Codex 等工具安装，又不把任何平台的专属逻辑污染到共享技能来源中。

文档入口约定：根目录 `README.md` 使用英文，`docs/README.cn.md` 是根 README 的中文翻译，`docs/index.md` 是技术文档索引。不要用 `docs/README.md` 作为技术索引，避免与目录 README 语义混淆。

## Source of Truth

| 内容 | 权威位置 |
| --- | --- |
| 通用技能 | `plugins/laxpud-vibekits/skills/<skill-name>/SKILL.md` |
| 可复用规则 | `rules/<rule-name>.md` |
| Codex 插件市场 | `.agents/plugins/marketplace.json` |
| Codex 插件清单 | `plugins/laxpud-vibekits/.codex-plugin/plugin.json` |
| Claude Code 插件市场 | `.claude-plugin/marketplace.json` |
| Claude Code 插件清单 | `plugins/laxpud-vibekits/.claude-plugin/plugin.json` |

`plugins/laxpud-vibekits/skills/` 是唯一技能来源。不要在根目录创建 `skills/` 副本，也不要把某个平台的私有路径、命令或安装假设写进通用技能正文。

## Skill Requirements

每个技能目录必须采用以下结构：

```text
plugins/laxpud-vibekits/skills/<skill-name>/
└── SKILL.md
```

`SKILL.md` 的 frontmatter 只保留 `name` 和 `description`。其中 `description` 是触发技能的主要元数据，应同时说明能力范围和适用场景，例如“创建或编辑 pyproject.toml 时使用”。

技能正文应专注于让 Agent 正确执行任务：

- 写清楚流程、输入输出契约、边界条件和验证方式。
- 只保留执行技能所需的信息；长期维护说明、安装介绍和发布记录放到仓库文档中。
- 需要脚本、参考资料或模板时，可在技能目录下添加 `scripts/`、`references/` 或 `assets/`，并在 `SKILL.md` 中说明何时读取或使用。
- 新增或大改技能后，检查 README 技能表、两端 plugin manifest 的描述/关键词是否需要同步。

## Rule Requirements

可复用规则使用以下结构：

```text
rules/<rule-name>.md
```

规则应短小、清晰、平台无关，建议不超过 1000 字符。规则适合沉淀轻量偏好或行为边界；如果需要多步骤流程、示例、脚本或复杂上下文，应创建技能而不是规则。

个人全局规则备份可以放在 `rules/`，但文件名和开头说明必须明确标注“备份”用途。这类文件不视为平台无关通用规则。

## Adapter Sync Checklist

当技能能力、插件定位或对外描述发生变化时，按顺序检查：

- `plugins/laxpud-vibekits/skills/*/SKILL.md` 的 `description` 是否仍准确。
- `plugins/laxpud-vibekits/.codex-plugin/plugin.json` 的 `description`、`keywords`、`interface.shortDescription`、`interface.longDescription` 和 `interface.defaultPrompt` 是否同步。
- `plugins/laxpud-vibekits/.claude-plugin/plugin.json` 的 `description`、`keywords` 和 `skills` 路径是否同步。
- `.agents/plugins/marketplace.json` 是否保留 Codex 必需的 `policy.installation`、`policy.authentication` 和 `category`。
- `.claude-plugin/marketplace.json` 的插件描述、版本、标签和 `source` 是否指向统一插件包。
- `README.md`、`docs/README.cn.md`、`docs/index.md` 的技能表、安装说明、贡献边界和文档入口是否仍匹配。

## Validation

文档型变更至少执行以下检查：

- JSON 文件能被解析。
- 技能 frontmatter 只有 `name` 和 `description`，且目录名与技能名一致。
- README 和 docs 中的相对链接指向真实文件。
- 根 README 保持英文，`docs/README.cn.md` 与其结构对齐，`docs/index.md` 作为技术索引存在。
- `git diff` 中不包含缓存、虚拟环境、本地测试输出或无关改动。
