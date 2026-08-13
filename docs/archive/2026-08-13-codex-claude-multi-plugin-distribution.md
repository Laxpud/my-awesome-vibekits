# Codex / Claude Code 多插件目录与分发里程碑归档

状态：2026-08-13 完成并归档。本里程碑将原聚合插件直接拆分为三个可独立分发的插件，并建立以仓库级 catalog 为唯一事实来源的 Codex / Claude Code 双端生成、校验和生命周期流程。

## 已完成任务

- [x] 建立仓库级统一插件 catalog，作为插件身份和分发元数据的唯一事实来源。
  - 验收条件：
    - catalog 记录每个插件的稳定 ID、目录、版本、描述、分类，以及 Codex、Claude Code 所需的平台覆盖项。
    - `plugins/<plugin-id>/` 中的每个插件可独立安装、升级、禁用、卸载和回滚，不要求兄弟插件同步发版。
    - catalog 校验拒绝重复插件 ID、重复或冲突的 Skill ID、不存在的目录、越过插件根目录的路径，以及 manifest 与 catalog 身份不一致。
    - 插件发布包自包含；运行时不通过 `../shared` 引用兄弟插件或仓库级共享文件。
  - 完成记录：2026-08-13。
  - 验证证据：新增 `plugin-catalog.json` 和 `scripts/plugin_catalog.py`；`tests/test_plugin_catalog.py` 覆盖三个正式插件、重复 Skill、越界路径、生成稳定性、漂移检测和单插件版本隔离。

- [x] 将原 `laxpud-vibekits` 单插件直接拆分为三个独立插件。
  - 验收条件：
    - marketplace 顶层名称继续使用 `laxpud-vibekits`；插件目录和插件 ID 为 `plugins/code-quality/`、`plugins/python-project/` 和 `plugins/project-docs/`，且分别只包含对应 Skill。
    - 三个插件分别拥有独立的 Codex、Claude Code manifest 和版本；Skill ID 保持不变。
    - 删除旧 `plugins/laxpud-vibekits/` 插件包及其 marketplace 条目，不保留 deprecated bundle、兼容别名、聚合依赖包或人工维护的 Skills 副本。
    - 根 README、中文 README、安装与更新文档、适配层规范、fixture 和测试全部改为三个独立插件，并明确此次变更不提供旧插件迁移兼容层。
    - 三个插件均能独立执行生命周期操作，任一插件操作不改变另外两个插件。
  - 完成记录：2026-08-13。
  - 验证证据：三个新插件目录及其双端 manifest 均通过 Plugin Creator、Skill Creator 和 Claude Code `plugin validate --strict`；Codex CLI `0.147.0` 与 Claude Code `2.1.229` 的隔离实测均能发现、安装和卸载三个插件，并验证单插件启停或卸载不改变兄弟插件。

- [x] 从统一 catalog 生成 Codex 与 Claude Code 的多插件 marketplace。
  - 验收条件：
    - `.agents/plugins/marketplace.json` 和 `.claude-plugin/marketplace.json` 的 `plugins[]` 包含并正确解析三个独立插件。
    - 生成过程保留 Codex 的 `policy.installation`、`policy.authentication`、`category` 及 Claude marketplace 必需字段，不以手工复制 JSON 作为长期维护方式。
    - 每个 marketplace 条目指向独立的 `plugins/<plugin-id>/`，且各插件 manifest、版本、名称和 Skills 路径通过静态校验。
    - 单个条目无效时精确报告对应 marketplace、插件 ID 和字段，不以 `plugins[0]` 代表整个目录。
  - 完成记录：2026-08-13。
  - 验证证据：`scripts/sync_plugin_metadata.py` 从 catalog 生成两份 marketplace 和六份 manifest；无输入变化时校验通过，手工漂移测试按目标文件报告修复命令。

- [x] 消除元数据同步、安装检查和更新流程中的单插件假设。
  - 验收条件：
    - 生产代码移除固定 `PLUGIN_ROOT`、`PLUGIN_NAME`、`MARKETPLACE_NAME`、`plugins[0]` 和 `len(plugins) == 1` 等单插件约束，改由 catalog 解析目标。
    - 相关命令支持选择一个插件、多个插件或 `--all`，默认行为有文档和测试覆盖。
    - 发布、digest、安装检查、晋级和回滚以 `(platform, marketplace, plugin)` 为目标；一个插件失败或回滚不改变兄弟插件的版本、启用状态或安装来源。
    - 旧聚合插件 ID、目录和 marketplace 条目被直接移除，测试不以兼容旧行为为通过条件。
  - 完成记录：2026-08-13。
  - 验证证据：元数据同步、安装检查、Git release、preflight、双端 adapter、E2E 编排和报告均改为 catalog 驱动；测试明确扫描生产脚本中的旧单插件捷径，并覆盖单插件选择、多插件选择、默认全选和独立回滚。

- [x] 建立“共享内容核心 + Codex / Claude Code 双适配”生成流程。
  - 验收条件：
    - 每个插件的 `skills/` 是该插件唯一的技能内容源；生成物和安装投影不成为第二份人工维护的 Skill 副本。
    - 每个插件分别生成 `.codex-plugin/plugin.json` 与 `.claude-plugin/plugin.json`，平台字段不污染通用 `SKILL.md`。
    - 两端 manifest 的名称、版本、描述、Skills 路径和发布来源与 catalog 一致，同时保留必要的平台专属字段。
    - 生成器可重复执行且结果稳定；无输入变化时不产生 diff，手工修改生成物后校验失败并给出修复方式。
  - 完成记录：2026-08-13。
  - 验证证据：`python scripts/sync_plugin_metadata.py` 报告 catalog 与生成物同步；幂等与漂移单元测试通过；仓库只保留三个插件自己的 `skills/` 内容源。

- [x] 建立 Codex / Claude Code 双端验证矩阵和发布门禁。
  - 验收条件：
    - 双端验证 marketplace 发现/列出、逐插件安装、启用、Skill 路径、升级、禁用、卸载和独立回滚。
    - fixture 覆盖三个正式插件，并另含两个插件内的同名候选 Skill、一个无效路径和一次独立回滚，用于验证命名冲突、故障隔离和错误定位。
    - CI 先通过 catalog、两端生成物一致性和静态 schema 检查，再执行客户端 smoke test；需要凭据、网络或 GUI 的检查标为独立门禁。
    - 两端测试使用隔离配置且默认不调用模型；可选 Skill smoke 的 token 消耗、清理边界和晋级条件保持显式。
  - 完成记录：2026-08-13。
  - 验证证据：新增 `.github/workflows/plugin-validation.yml`、冲突与无效路径 fixture、三插件生命周期集成测试和 Markdown 链接检查；68 项测试全部通过。真实客户端隔离测试未调用模型，Codex 与 Claude Code 最终均安装并启用三个 `1.1.2` 插件。

## 里程碑级完成条件

- [x] 上述全部任务均标记为 `[x]`，且各自记录完成日期和验证证据。
- [x] 仓库中不存在把 marketplace 限制为单一插件的生产代码；三个独立插件均能从同一 catalog 生成，并通过 Codex、Claude Code 的安装与升级测试。
- [x] 旧 `laxpud-vibekits` 插件 ID、目录和 marketplace 条目均不存在，且没有 deprecated bundle、兼容别名或聚合依赖包。
- [x] Codex 与 Claude Code 的 marketplace、manifest 和安装状态均可追溯到统一 catalog 与插件内容；一个插件的失败、升级或回滚不影响兄弟插件。
- [x] 两端生成物均可由统一 catalog 和插件内容重新生成，`git diff` 证明没有必须手工同步的 Skills 内容副本。

## 最终验证

- `python -m unittest discover -s tests -p "test_*.py" -v`：68 项通过。
- `python scripts/sync_plugin_metadata.py`、`python scripts/check_codex_install.py --all`、`python scripts/check_markdown_links.py`：通过。
- Plugin Creator 对三个插件的校验、Skill Creator 对三个 Skill 的快速校验、Claude Code 对三个插件及 marketplace 的严格校验：全部通过。
- Codex CLI `0.147.0`：隔离 marketplace 中发现并逐个安装三个插件；在隔离 `config.toml` 中切换单插件启用状态并由 `plugin list --json` 验证，卸载和重装后兄弟插件状态保持不变。
- Claude Code `2.1.229`：隔离 marketplace 中完成三个插件安装、单插件禁用/启用、更新、卸载和重装，最终三者均为 `1.1.2` 且启用。
- `python -m compileall -q scripts tests` 与 `git diff --check`：通过。
