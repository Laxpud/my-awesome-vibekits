# AGENTS.md

本文件是 AI 在本仓库工作的快速路由入口；`CLAUDE.md` 通过相对软链使用同一正文。

开始或继续里程碑任务前先读取 [`TODO.md`](TODO.md)；交付前按其顶部规则同步状态。

## 按改动类型路由

| 变更类型 | 先读 |
| --- | --- |
| 项目定位、用户能力、安装路径或已收录内容 | [`README.md`](README.md)；公开内容变化时同时检查 [`docs/README.cn.md`](docs/README.cn.md) |
| 文档结构、入口或所有权 | [`docs/index.md`](docs/index.md) |
| 通用技能、插件 catalog 或平台适配层 | [`docs/SKILL_RULE_GUIDELINES.md`](docs/SKILL_RULE_GUIDELINES.md) |
| 插件发布、客户端更新、隔离 E2E 或日常晋级 | [`docs/PLUGIN_UPDATE.md`](docs/PLUGIN_UPDATE.md) |
| Codex marketplace、manifest 或安装说明 | [`docs/CODEX_INSTALL_SMOKE_TEST.md`](docs/CODEX_INSTALL_SMOKE_TEST.md) |

## 工作流触发器

- 修改根 [`README.md`](README.md) 的公开内容时，在同一轮同步更新 [`docs/README.cn.md`](docs/README.cn.md) 并保持章节结构对齐。
- 修改技能能力、名称、`description` 或插件定位时，按 [`docs/SKILL_RULE_GUIDELINES.md`](docs/SKILL_RULE_GUIDELINES.md) 的适配层同步清单检查 README、manifest 和 marketplace。
- 准备发布时，先按 [`docs/PLUGIN_UPDATE.md`](docs/PLUGIN_UPDATE.md) 同步版本并完成发布验证；不要手工分别修改版本镜像。
- 修改 Codex marketplace、manifest 或 README 安装说明时，按 [`docs/CODEX_INSTALL_SMOKE_TEST.md`](docs/CODEX_INSTALL_SMOKE_TEST.md) 执行对应本地或远端检查。

## 技能维护与生成

- `project-docs` 只编辑 `sources/project-docs/`：入口为 `skills/<skill-id>/SKILL.md.in`，技能目录仅保留入口与调用配置；规范、示例和 Markdown 模板统一放在 `references/`。
- 修改维护源后运行 `python3 scripts/build_project_docs.py --write`，生成 `plugins/project-docs/skills/`。不要手改生成文件；安装技能必须包含自身所需资料，不依赖兄弟技能或维护源路径。
- 提交前运行 `python3 scripts/build_project_docs.py` 检查生成结果，并将维护源和受影响的生成文件一起提交。生成器与资料分发约定见[维护规范](docs/SKILL_RULE_GUIDELINES.md#生成自包含的-project-docs-技能)。
- 其他插件仍直接维护各自的 `plugins/<plugin-id>/skills/`，不因局部任务自动迁移。技能内容检查采用[轻量验收](docs/SKILL_RULE_GUIDELINES.md#技能内容的轻量验收)，不默认追加模型试跑或其他平台验证。

## 高风险边界

- `plugin-catalog.json` 是插件身份与分发元数据的唯一来源；manifest 与 marketplace 由元数据生成器同步，不手改镜像，不建立跨插件运行时引用。
- 平台专属配置只能进入对应适配层；修改边界前先读 [`docs/SKILL_RULE_GUIDELINES.md`](docs/SKILL_RULE_GUIDELINES.md)。
- `scripts/plugin_update_e2e.py --promote` 会修改日常用户安装。只有目标版本已提交并推送、隔离测试通过、工作区干净且相关客户端完全退出时，才按 [`docs/PLUGIN_UPDATE.md`](docs/PLUGIN_UPDATE.md) 执行。
