# CLAUDE.md

本文件是 Claude Code 在本仓库工作的快速路由入口。

开始或继续里程碑任务前先读取 [`TODO.md`](TODO.md)；交付前按其顶部规则同步状态。

## 按改动类型路由

| 变更类型 | 先读 |
| --- | --- |
| 项目定位、用户能力、安装路径或已收录内容 | [`README.md`](README.md)；公开内容变化时同时检查 [`docs/README.cn.md`](docs/README.cn.md) |
| 文档结构、入口或所有权 | [`docs/index.md`](docs/index.md) |
| 通用技能、插件 catalog、可复用规则或平台适配层 | [`docs/SKILL_RULE_GUIDELINES.md`](docs/SKILL_RULE_GUIDELINES.md) |
| 插件发布、客户端更新、隔离 E2E 或日常晋级 | [`docs/PLUGIN_UPDATE.md`](docs/PLUGIN_UPDATE.md) |
| Codex marketplace、manifest 或安装说明 | [`docs/CODEX_INSTALL_SMOKE_TEST.md`](docs/CODEX_INSTALL_SMOKE_TEST.md) |

## 工作流触发器

- 修改根 [`README.md`](README.md) 的公开内容时，在同一轮同步更新 [`docs/README.cn.md`](docs/README.cn.md) 并保持章节结构对齐。
- 修改技能能力、名称、`description` 或插件定位时，按 [`docs/SKILL_RULE_GUIDELINES.md`](docs/SKILL_RULE_GUIDELINES.md) 的适配层同步清单检查 README、manifest 和 marketplace。
- 准备发布时，先按 [`docs/PLUGIN_UPDATE.md`](docs/PLUGIN_UPDATE.md) 同步版本并完成发布验证；不要手工分别修改版本镜像。
- 修改 Codex marketplace、manifest 或 README 安装说明时，按 [`docs/CODEX_INSTALL_SMOKE_TEST.md`](docs/CODEX_INSTALL_SMOKE_TEST.md) 执行对应本地或远端检查。

## 高风险边界

- `plugin-catalog.json` 是插件身份与分发元数据的唯一来源；每个 `plugins/<plugin-id>/skills/` 是该插件唯一的技能来源，不得创建副本或跨插件 `../shared` 引用。
- 平台专属配置只能进入对应适配层；修改边界前先读 [`docs/SKILL_RULE_GUIDELINES.md`](docs/SKILL_RULE_GUIDELINES.md)。
- `scripts/plugin_update_e2e.py --promote` 会修改日常用户安装。只有目标版本已提交并推送、隔离测试通过、工作区干净且相关客户端完全退出时，才按 [`docs/PLUGIN_UPDATE.md`](docs/PLUGIN_UPDATE.md) 执行。
