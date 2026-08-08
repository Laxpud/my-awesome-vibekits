# 技能与规则维护规范

本规范用于维护 Vibekits 的通用技能、可复用规则和平台适配层。目标是让仓库既能被 Claude Code、Codex 等工具安装，又不把任何平台的专属逻辑污染到共享技能来源中。

项目文档所有权和入口见 [`docs/index.md`](index.md)。本文件只维护技能、规则、平台适配层及其验证契约。

## 权威位置

| 内容 | 权威位置 |
| --- | --- |
| 通用技能 | `plugins/laxpud-vibekits/skills/<skill-name>/SKILL.md` |
| 可复用规则 | `rules/<rule-name>.md` |
| Codex 插件市场 | `.agents/plugins/marketplace.json` |
| Codex 插件清单 | `plugins/laxpud-vibekits/.codex-plugin/plugin.json` |
| Claude Code 插件市场 | `.claude-plugin/marketplace.json` |
| Claude Code 插件清单 | `plugins/laxpud-vibekits/.claude-plugin/plugin.json` |

`plugins/laxpud-vibekits/skills/` 是唯一技能来源。不要在根目录创建 `skills/` 副本，也不要把某个平台的私有路径、命令或安装假设写进通用技能正文。

## 技能要求

每个技能目录必须采用以下结构：

```text
plugins/laxpud-vibekits/skills/<skill-name>/
├── SKILL.md
├── references/  # 可选：按需加载的详细参考资料
├── scripts/     # 可选：可复用的确定性脚本
└── assets/      # 可选：输出所需模板或静态资源
```

`SKILL.md` 的 frontmatter 只保留 `name` 和 `description`。其中 `description` 是触发技能的主要元数据，应同时说明能力范围和适用场景，例如“创建或编辑 pyproject.toml 时使用”。

技能正文应专注于让 Agent 正确执行任务：

- 写清楚流程、输入输出契约、边界条件和验证方式。
- 只保留执行技能所需的信息；长期维护说明、安装介绍和发布记录放到仓库文档中。
- 需要脚本、参考资料或模板时，可在技能目录下添加 `scripts/`、`references/` 或 `assets/`，并在 `SKILL.md` 中说明何时读取或使用。
- 新增或大改技能后，检查 README 技能表、两端 plugin manifest 的描述/关键词是否需要同步。

## 规则要求

可复用规则使用以下结构：

```text
rules/<rule-name>.md
```

规则应短小、清晰、平台无关，建议不超过 1000 字符。规则适合沉淀轻量偏好或行为边界；如果需要多步骤流程、示例、脚本或复杂上下文，应创建技能而不是规则。

个人全局规则备份可以放在 `rules/`，但文件名和开头说明必须明确标注“备份”用途。这类文件不视为平台无关通用规则。

## 适配层同步清单

当技能能力、插件定位或对外描述发生变化时，按顺序检查：

- `plugins/laxpud-vibekits/skills/*/SKILL.md` 的 `description` 是否仍准确。
- `plugins/laxpud-vibekits/.codex-plugin/plugin.json` 的 `description`、`keywords`、`interface.shortDescription`、`interface.longDescription` 和 `interface.defaultPrompt` 是否同步。
- `plugins/laxpud-vibekits/.claude-plugin/plugin.json` 的 `description`、`keywords` 和 `skills` 路径是否同步。
- `.agents/plugins/marketplace.json` 是否保留 Codex 必需的 `policy.installation`、`policy.authentication` 和 `category`。
- `.claude-plugin/marketplace.json` 的插件描述、版本、标签和 `source` 是否指向统一插件包。
- `README.md` 与 `docs/README.cn.md` 的技能表、安装说明和章节结构是否仍匹配；`docs/index.md` 的权威文档路由是否仍准确。

## 验证

插件版本以 `plugins/laxpud-vibekits/.codex-plugin/plugin.json` 为权威源。发布前不要逐个文件手工修改版本；使用：

```bash
python scripts/sync_plugin_metadata.py --set-version <semver>
```

该命令同步 Codex/Claude manifest、Claude marketplace 以及中英文 README 的版本展示，并立即校验两套 marketplace 的插件名、插件路径和共享 `skills` 路径。只检查而不写入时运行：

```bash
python scripts/sync_plugin_metadata.py
```

文档型变更至少执行以下检查：

- JSON 文件能被解析。
- 技能 frontmatter 只有 `name` 和 `description`，且目录名与技能名一致。
- README 和 docs 中的相对链接指向真实文件。
- 根 README 保持英文，`docs/README.cn.md` 与其结构对齐，`docs/index.md` 作为技术索引存在。
- `git diff` 中不包含缓存、虚拟环境、本地测试输出或无关改动。

修改 `.agents/plugins/marketplace.json`、Codex plugin manifest 或 README 安装说明后，还必须运行：

```bash
python scripts/check_codex_install.py
```

变更推送到 GitHub 后，用 `python scripts/check_codex_install.py --remote` 检查已发布 checkout。详细契约和边界见 [Codex GitHub 安装 Smoke Test](CODEX_INSTALL_SMOKE_TEST.md)。
