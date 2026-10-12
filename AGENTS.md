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

## 市场维护与插件所有权

- 当前市场收录三个外部插件；技能、manifest、版本与插件发布在对应独立仓库维护，入口见 README 的插件列表。
- 本仓库只维护 `plugin-catalog.json` 中的来源与收录元数据，运行 `python3 scripts/sync_plugin_metadata.py --write` 生成两端 marketplace；不在本仓库生成外部插件 manifest。
- `plugins/`、`sources/` 与旧技能生成器暂时保留为迁移前快照，当前市场不引用这些内容；`plugins/` 中旧 manifest 和 `SKILL.md` 已加 `.disabled` 后缀以停用发现入口。不要恢复这些入口或运行旧生成器重建安装文件，也不要用本地快照替代外部插件的维护源；需要回查时只读备份。
- 交付前运行元数据、Codex 安装契约、Markdown 链接与 diff 检查；需要核对外部包时显式运行 `python3 scripts/check_codex_install.py --all --check-external`，真实客户端安装由当前任务约定决定。

### Codex 外部插件展示元数据

- 外部仓库来源本身不足以提供完整的安装前展示。需要展示详情的条目，应在 catalog 中启用 `platforms.codex.marketplaceMetadata: true`，由生成器附带展示元数据。
- 展示内容以独立仓库的实际 manifest 为准，核对后更新 catalog 收录快照；同步名称、简介、详细介绍、推荐提示词、发布者和分类等信息，避免两处文案漂移。
- 独立仓库发布后，运行 `python3 scripts/sync_plugin_metadata.py --fetch-external` 预览回填差异；加 `--write` 才更新 catalog 与两端 marketplace，可用 `--plugin <id>` 限定目标。同步保留本市场的来源、安装策略和展示开关。
- `homepage`、`repository` 和 `interface.websiteURL` 应指向插件自己的独立仓库；安装来源继续使用外部仓库 URL，不沿用聚合市场的网站地址。
- 市场条目只携带展示元数据，不复制 `skills` 等包内路径。外部插件安装前没有技能列表属于当前客户端行为，不通过引用旧本地副本补齐。
- 修改后运行元数据同步与安装契约检查；客户端展示和实际安装分别验证。具体字段及检查流程见 [`docs/SKILL_RULE_GUIDELINES.md`](docs/SKILL_RULE_GUIDELINES.md) 和 [`docs/CODEX_INSTALL_SMOKE_TEST.md`](docs/CODEX_INSTALL_SMOKE_TEST.md)。

## 高风险边界

- `plugin-catalog.json` 是本市场的来源与收录元数据入口；marketplace 由元数据生成器同步，不手改镜像。外部插件的身份、版本与 manifest 以各独立仓库为准，本市场核对后同步收录快照。
- 平台专属配置只能进入对应适配层；修改边界前先读 [`docs/SKILL_RULE_GUIDELINES.md`](docs/SKILL_RULE_GUIDELINES.md)。
- `scripts/plugin_update_e2e.py --promote` 会修改日常用户安装。只有目标版本已提交并推送、隔离测试通过、工作区干净且相关客户端完全退出时，才按 [`docs/PLUGIN_UPDATE.md`](docs/PLUGIN_UPDATE.md) 执行。
