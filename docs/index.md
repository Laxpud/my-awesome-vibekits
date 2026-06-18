# 项目文档索引

本目录存放 Vibekits 的维护说明、技能/规则规范和长期技术记录。根目录 `README.md` 是英文公开入口，`docs/README.cn.md` 是它的中文翻译，`TODO.md` 记录当前活跃维护事项。

## 文档地图

| 文档 | 用途 |
| --- | --- |
| [README.cn.md](README.cn.md) | 根 README 的中文翻译。 |
| [SKILL_RULE_GUIDELINES.md](SKILL_RULE_GUIDELINES.md) | 维护通用技能、可复用规则和平台适配层时使用的结构规范、同步清单和验证要求。 |
| [PLUGIN_UPDATE.md](PLUGIN_UPDATE.md) | Codex/Claude Code 手工更新方式，以及隔离 E2E、自动晋级、回滚和报告说明。 |
| [CODEX_INSTALL_SMOKE_TEST.md](CODEX_INSTALL_SMOKE_TEST.md) | 修改 Codex marketplace、manifest 或安装说明后，验证本地与 GitHub 远端安装链路。 |
| [../TODO.md](../TODO.md) | 当前活跃维护事项、验收标准和后续改进候选。 |
| [../AGENTS.md](../AGENTS.md) | Codex 在本仓库工作时使用的项目级约束。 |
| [../CLAUDE.md](../CLAUDE.md) | Claude Code 在本仓库工作时使用的项目级约束。 |

## 文档归属

- `README.md`：英文公开入口，面向 GitHub 读者，说明安装路径、已收录技能和贡献基础。
- `docs/README.cn.md`：根 README 的中文翻译；根 README 变化时要同步检查它。
- `TODO.md`：活跃维护事项，使用复选框，并为非简单事项写可验证的验收标准。
- `docs/index.md`：维护者使用的技术文档索引。
- `docs/`：长期有效的维护规则、设计边界、技术说明和历史记录。
- `plugins/laxpud-vibekits/skills/`：唯一共享技能来源。每个技能目录只放执行该技能所需的 `SKILL.md` 和必要资源。
- `.claude-plugin/`、`.agents/`、`plugins/laxpud-vibekits/.claude-plugin/`、`plugins/laxpud-vibekits/.codex-plugin/`：平台适配层，只放 marketplace 或 plugin manifest。

## 维护约定

- 根 README 保持英文公开入口，`docs/README.cn.md` 作为中文翻译同步维护。
- `docs/index.md` 是技术文档索引。不要重新创建 `docs/README.md` 作为索引，避免和目录 README 语义混淆。
- 修改技能能力、名称或触发描述时，同步检查 README 技能表、Claude/Codex plugin manifest 和 marketplace 描述。
- 新增平台适配信息时，只写入对应平台适配目录，不写进共享技能正文。
- 可复用规则保持短小、清晰、平台无关；个人全局规则备份必须在文件名和开头说明中标注备份用途。
- 文档调整完成后，验证 JSON 解析、Markdown 链接、技能元数据和 `git diff`；涉及 Codex 安装元数据时运行 `python scripts/check_codex_install.py`。
