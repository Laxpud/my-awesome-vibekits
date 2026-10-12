# AGENTS.md

本文件是 AI 在本仓库工作的快速路由入口；`CLAUDE.md` 通过相对软链使用同一正文。

开始或继续里程碑任务前先读取 [`TODO.md`](TODO.md)；交付前按其顶部规则同步状态。

## 按改动类型路由

| 变更类型 | 先读 |
| --- | --- |
| 项目定位、用户能力、安装路径或已收录内容 | [`README.md`](README.md)；公开内容变化时同时检查 [`docs/README.cn.md`](docs/README.cn.md) |
| 文档结构、入口或所有权 | [`docs/index.md`](docs/index.md) |
| 插件 catalog、外部展示元数据或平台适配层 | [`docs/SKILL_RULE_GUIDELINES.md`](docs/SKILL_RULE_GUIDELINES.md) |
| 独立插件发布后的市场更新或客户端迁移 | [`docs/PLUGIN_UPDATE.md`](docs/PLUGIN_UPDATE.md) |
| Codex marketplace、manifest 或安装说明 | [`docs/CODEX_INSTALL_SMOKE_TEST.md`](docs/CODEX_INSTALL_SMOKE_TEST.md) |

## 工作流触发器

- 修改根 [`README.md`](README.md) 的公开内容时，在同一轮同步更新 [`docs/README.cn.md`](docs/README.cn.md) 并保持章节结构对齐。
- 独立插件能力、名称、`description` 或定位变化后，同步市场收录快照时按 [`docs/SKILL_RULE_GUIDELINES.md`](docs/SKILL_RULE_GUIDELINES.md) 的适配层同步清单检查 README、catalog 和 marketplace。
- 独立仓库发布后，按 [`docs/PLUGIN_UPDATE.md`](docs/PLUGIN_UPDATE.md) 回填收录快照并验证市场；本仓库不修改插件版本或外部 manifest。
- 修改 Codex marketplace、manifest 或 README 安装说明时，按 [`docs/CODEX_INSTALL_SMOKE_TEST.md`](docs/CODEX_INSTALL_SMOKE_TEST.md) 执行对应本地或远端检查。

## 市场维护与插件所有权

- 当前市场收录三个外部插件；技能、manifest、版本与插件发布在对应独立仓库维护，入口见 README 的插件列表。
- 本仓库只维护 `plugin-catalog.json` 中的来源与收录元数据，运行 `python3 scripts/sync_plugin_metadata.py --write` 生成两端 marketplace；不在本仓库生成外部插件 manifest。
- 本仓库仅维护外部插件市场，不保存插件源码、例库、技能生成器或插件专属设计与审查；修改这些内容前，转到对应独立仓库并读取其 AGENTS.md。旧资料通过独立仓库或 Git 历史回查，不恢复本地发现入口。
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
- 市场静态检查和外部包检查不代表客户端生命周期已验证；真实客户端配置修改、插件安装或更新按当前任务授权执行，边界见 [`docs/PLUGIN_UPDATE.md`](docs/PLUGIN_UPDATE.md)。
