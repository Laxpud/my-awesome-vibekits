# 项目文档

本目录存放 Vibekits 的维护说明、技能/规则规范和长期技术记录。根目录 `README.md` 只保留公开入口、快速安装和能力概览；活跃事项放在 `TODO.md`；细节规范放在 `docs/`。

## 文档地图

| 文档 | 内容 |
| --- | --- |
| [SKILL_RULE_GUIDELINES.md](SKILL_RULE_GUIDELINES.md) | 创建、修改和发布通用技能/规则时需要遵守的结构、边界和同步清单。 |
| [../TODO.md](../TODO.md) | 当前维护事项、验收标准和后续改进方向。 |
| [../AGENTS.md](../AGENTS.md) | Codex 在本仓库工作时的项目级约束。 |
| [../CLAUDE.md](../CLAUDE.md) | Claude Code 在本仓库工作时的项目级约束。 |

## 文档归属

- `README.md`：面向 GitHub 读者的入口，说明项目价值、安装方式、已收录技能和贡献入口。
- `TODO.md`：维护者当前要推进的事项，使用复选框和可验证的验收标准。
- `docs/`：长期有效的维护规则、设计边界、技术说明和历史记录。
- `plugins/laxpud-vibekits/skills/`：唯一技能来源，每个技能只包含执行该技能所需的 `SKILL.md` 和必要资源。
- `.claude-plugin/`、`.agents/`、`plugins/laxpud-vibekits/.claude-plugin/`、`plugins/laxpud-vibekits/.codex-plugin/`：平台适配层，只放平台需要的 marketplace 或 plugin manifest。

## 维护约定

- 修改技能能力、技能名称或触发描述时，同步检查 README 技能表、Claude/Codex plugin manifest 和 marketplace 描述。
- 新增平台适配信息时，只写入对应平台官方适配目录，不写进通用技能正文。
- 新增可复用规则时保持短小、明确、平台无关；个人全局规则备份必须在文件名和开头说明中标注备份用途。
- 文档调整完成后至少验证 JSON 可解析、Markdown 链接路径存在，并检查 `git diff`。
