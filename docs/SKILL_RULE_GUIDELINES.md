# Skill、Catalog 与适配层维护规范

本规范用于维护 Vibekits 的通用 Skill、插件 catalog 和平台适配层。目标是让三个插件都能被 Codex 与 Claude Code 独立安装、每个插件可拥有一个或多个职责清晰的 Skill，同时不把平台专属逻辑污染到共享 Skill 来源中。

项目文档所有权和入口见 [`docs/index.md`](index.md)。本文件只维护 Skill、catalog、双平台适配层及其验证契约。

## 权威位置

| 内容 | 权威位置 |
| --- | --- |
| 插件身份、独立版本和分发元数据 | [`plugin-catalog.json`](../plugin-catalog.json) |
| 通用技能内容 | `plugins/<plugin-id>/skills/<skill-id>/` |
| Codex marketplace 生成物 | `.agents/plugins/marketplace.json` |
| Codex manifest 生成物 | `plugins/<plugin-id>/.codex-plugin/plugin.json` |
| Claude Code marketplace 生成物 | `.claude-plugin/marketplace.json` |
| Claude Code manifest 生成物 | `plugins/<plugin-id>/.claude-plugin/plugin.json` |

每个插件自己的 `skills/` 是该插件唯一的技能内容来源。不得在根目录、兄弟插件或安装投影中创建人工维护副本，也不得通过 `../shared` 引用仓库级或兄弟插件内容。同一插件可在一个技能的 `references/` 保存共同约定，专项资料仍归对应技能；使用相对链接，安装后必须留在该插件 payload 内，不建立重复副本。`.codex-plugin/`、`.claude-plugin/` 和两份 marketplace 都是 catalog 的稳定生成物，不是独立事实来源。

## Catalog 契约

`plugin-catalog.json` 至少为每个插件维护稳定 `id`、目录、独立 SemVer、描述、分类、关键词、完整 Skill ID/路径集合，以及 Codex 和 Claude Code 的平台覆盖项。数组顺序用于稳定展示，不代表只有第一个 Skill 才属于安装契约。

校验器必须拒绝：

- 重复插件 ID 或插件目录；
- 大小写归一化后重复或冲突的 Skill ID；
- 不存在的插件目录或 `SKILL.md`；
- 绝对路径、`..`、反斜杠或不匹配 `plugins/<plugin-id>` / `skills/<skill-id>` 的路径；
- manifest、marketplace 与 catalog 的名称、版本、描述、路径或平台字段漂移；
- 插件内容中的 `../shared` 运行时引用。

当前正式目录只包含：

```text
plugins/
├── code-quality/
│   └── skills/code-comment-standard/
├── python-project/
│   └── skills/pyproject-standard/
└── project-docs/
    └── skills/
        ├── project-docs-bootstrap/
        ├── project-docs-refactor/
        ├── project-docs-readme/
        ├── project-docs-planning/
        ├── project-docs-architecture/
        ├── project-docs-guidance/
        └── project-docs-progress/
            └── references/writing-style.md  # 七技能共用一份
```

原 `plugins/laxpud-vibekits/` 聚合包、旧 marketplace 条目、兼容别名和聚合依赖包均不得恢复。

## 技能要求

每个技能目录采用以下结构：

```text
plugins/<plugin-id>/skills/<skill-id>/
├── SKILL.md
├── agents/openai.yaml  # 可选：Codex 技能调用策略等适配元数据
├── references/  # 可选：按需加载的详细参考资料
├── scripts/     # 可选：可复用的确定性脚本
└── assets/      # 可选：输出所需模板或静态资源
```

`SKILL.md` 的 frontmatter 只保留 `name` 和 `description`。`name` 必须与 Skill ID 和目录名一致；`description` 是触发技能的主要元数据，应同时说明能力范围和适用场景。

技能正文应专注于让 Agent 正确执行任务：

- 写清楚流程、输入输出契约、边界条件和验证方式。
- 只保留执行技能所需的信息；安装、平台命令和发布记录放到仓库文档或生成适配层；Codex 的技能调用设置放在各技能的 `agents/openai.yaml`，不混进 frontmatter。
- 需要脚本、参考资料或模板时，优先放在同一技能目录内；真正共用的规则可放在插件内某个技能的 `references/`，也可引用同插件其他技能的配套资料，并在 `SKILL.md` 中说明何时读取。不借引用资料自动调用其他技能。
- 新增或大改技能后，检查 catalog 描述、README 插件/技能表和生成物是否需要同步。

在提供插件命名空间的平台上，九个公开 Skill 名分别是：

- `code-quality:code-comment-standard`
- `python-project:pyproject-standard`
- `project-docs:project-docs-bootstrap`
- `project-docs:project-docs-refactor`
- `project-docs:project-docs-readme`
- `project-docs:project-docs-planning`
- `project-docs:project-docs-architecture`
- `project-docs:project-docs-guidance`
- `project-docs:project-docs-progress`

Skill frontmatter 中的原始 ID 保持不变，不写入平台命名空间。`project-docs-progress` 允许 Codex 隐式调用，其余六个文档技能在 `agents/openai.yaml` 设置 `policy.allow_implicit_invocation: false`，仅显式调用。描述保持简短、明确；正文以边界和按需导航为主，统一格式放入示例模板。

## 适配层同步清单

当技能能力、插件定位或对外描述发生变化时，按顺序检查：

- 对应 `plugins/<plugin-id>/skills/<skill-id>/SKILL.md` 的 `name` 与 `description` 是否准确。
- [`plugin-catalog.json`](../plugin-catalog.json) 的插件描述、版本、分类、关键词、完整 Skill 路径集合和双端覆盖项是否同步。
- `python scripts/sync_plugin_metadata.py --write` 是否只产生预期的两份 marketplace 和选中插件 manifest 变更。
- `.agents/plugins/marketplace.json` 每个条目是否保留 `policy.installation`、`policy.authentication`、`category` 和独立 source path。
- `.claude-plugin/marketplace.json` 每个条目的描述、版本、标签和 source 是否指向同一插件包。
- `README.md` 与 `docs/README.cn.md` 的插件表、安装说明和章节结构是否匹配。

## 生成与独立版本

只校验 catalog 和全部生成物，不写入：

```bash
python scripts/sync_plugin_metadata.py
```

从 catalog 稳定重建两端 marketplace 和六份 manifest：

```bash
python scripts/sync_plugin_metadata.py --all --write
```

单独更新一个或多个插件版本：

```bash
python scripts/sync_plugin_metadata.py --plugin python-project --set-version 1.2.0
python scripts/sync_plugin_metadata.py --plugin code-quality --plugin project-docs --set-version 1.2.0
```

`--set-version` 必须显式配合一个或多个 `--plugin`，或使用 `--all`。默认无选择时校验全部插件；无输入变化时重复 `--write` 不得产生 diff。手工修改生成物后，普通校验必须失败并提示运行 `--write`。

## 验证

### 技能内容的轻量验收

修改技能指令、参考资料或模板时，默认采用以下方式：

- 由 AI 根据已确认的需求审阅内容，确认职责、触发条件、模板和示例一致；不为每条指令编写测试，也不额外生成行为测试或写作审查报告。
- 内容审阅不能代替安装检查。涉及技能分发、调用设置或资源引用时，检查目标客户端能否发现技能、调用设置是否符合预期，以及模板和共享资料能否访问。
- 平台范围以当前任务约定为准；只要求 Codex 时，不扩展到其他客户端。这不改变仓库已经声明的平台支持范围。
- 实际行为通过后续真实使用反馈调整，不默认要求额外仓库试跑、模型调用或完整任务模拟；用户明确要求行为验证时再执行。
- 交付时区分已执行的检查与尚待使用反馈的行为，不把“预计会遵守指令”写成已经验证的效果。

脚本、安装器和元数据生成逻辑发生变化时，仍执行与改动相关的检查。轻量验收不替代下述正式发布检查，也不要求纯文案修改运行完整发布流程。

### 正式发布检查

发布前至少执行：

```bash
python scripts/sync_plugin_metadata.py
python scripts/check_codex_install.py --all
python scripts/check_markdown_links.py
python -m unittest discover -s tests -p "test_*.py" -v
```

另需验证：

- 每个插件通过 Codex plugin validator 和 `claude plugin validate`；
- 每个 catalog 声明的技能均存在于安装包中；升级测试按旧版实际 Skill 集合验证 baseline，按 catalog 完整集合验证 target；
- 技能 frontmatter 只有 `name` 和 `description`，且目录名、Skill ID 与 catalog 一致；
- README 和 docs 中的相对链接指向真实文件；
- 根 README 保持英文，中文 README 与其章节结构对齐；
- `git diff --check` 通过，且 diff 不含缓存、虚拟环境或本地测试输出。

修改 Codex marketplace、manifest 或 README 安装说明后，遵循 [Codex GitHub 安装 Smoke Test](CODEX_INSTALL_SMOKE_TEST.md)。发布和双客户端生命周期门禁见 [插件发布与客户端更新](PLUGIN_UPDATE.md)。
