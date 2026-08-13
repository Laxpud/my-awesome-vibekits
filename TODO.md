# TODO

本文件是 Vibekits 活动任务、里程碑、验收条件和状态维护流程的权威位置。长期技术规则见 [`docs/index.md`](docs/index.md)；只有满足下述归档门槛后，才把完成记录移入 `docs/archive/`。

## 执行与维护规则

1. 除非用户明确指定其他任务，否则默认执行当前里程碑中第一个未完成任务。
2. 只有任务的全部验收条件通过后才能将其标记为 `[x]`，并同时记录完成日期和验证证据。
3. 部分完成的任务保持 `[ ]`，并记录已完成内容和仍未满足的条件。
4. 不得通过删除、弱化或降低验收条件来制造完成状态。
5. 正常推进时，只有当前里程碑的全部任务和全部里程碑级完成条件都通过后，才能将完成记录归档到 `docs/archive/` 并把下一里程碑提升为当前里程碑；用户明确调整优先级时，必须保留被暂停里程碑的全部状态并记录调整，不得归档或制造完成状态。
6. 每次交付前按本节规则同步任务状态、剩余条件和验证证据。

## 暂停里程碑：维护体验与发布可靠性

状态：2026-08-13 根据用户明确的优先级调整暂停。全部已完成、部分完成和未完成记录保持原状，不归档；完成当前“Codex / Claude Code 多插件目录与分发”里程碑后再决定恢复顺序。

- [ ] 为每个已收录技能补充一个 README 可链接的最小使用示例。
  - 验收条件：根 README 的技能表能指向示例或对应 `SKILL.md` 中的示例段落，读者能在 1 分钟内判断技能适用场景。
  - 当前状态：部分完成。`project-docs-bootstrap` 已有“示例”章节；`code-comment-standard` 和 `pyproject-standard` 仍缺少可直接定位的最小示例及对应入口。

- [x] 建立插件发布前检查清单。
  - 验收条件：清单覆盖 Claude marketplace、Codex marketplace、两端 plugin manifest、技能 frontmatter、README 技能表和 JSON 解析验证。
  - 完成记录：2026-06-18。
  - 验证证据：`docs/SKILL_RULE_GUIDELINES.md` 的“适配层同步清单”和“验证”章节覆盖全部验收项；提交 `12a193c` 增加发布同步与更新指引。

- [x] 落实英文根 README 与中文 `docs/README.cn.md` 的双语策略。
  - 验收条件：根 README 使用英文，中文翻译位于 `docs/README.cn.md`，技术文档索引位于 `docs/index.md`。
  - 完成记录：2026-06-18。
  - 验证证据：提交 `4603f13` 补充双语 README 顶部互链；当前三个文件均存在且职责分离。

- [ ] 基于真实仓库使用反馈继续改进 `project-docs-bootstrap`。
  - 验收条件：至少用 2 个不同规模的真实仓库验证后，再决定是否补充大仓库扫描策略、旧路径 redirect note 模板、双语 README 同步检查细则，以及最终报告中的澄清/假设摘要格式。
  - 当前状态：部分完成（1/2）。2026-08-08 已在本仓库应用新版文档所有权、里程碑 TODO 和项目指导路由规则；仍需至少 1 个不同规模的真实仓库验证，再评估候选增强项。

- [ ] 建立插件更新端到端测试自动化。
  - 验收条件：
    - 在隔离的测试配置中，分别通过 Codex CLI 和 Claude Code CLI 从测试 marketplace 安装旧版、刷新 marketplace 并更新到目标版本。
    - 更新后校验实际安装版本、插件来源、payload digest 和 `pyproject-standard/SKILL.md` 路径；默认不得调用模型或消耗 token，可用 `--skill-smoke` 额外验证新会话中的 skill 发现与调用。
    - 只有两端隔离测试及临时远端分支清理全部成功，并显式传入 `--promote` 时，才更新日常用户配置；任一门禁失败不得修改日常安装。
    - 晋级覆盖 Codex 实例与 Claude Code 的全部 `user`、`project`、`local` 实例，保持原 `scope`、`projectPath` 和 `enabled` 状态；任一失败必须恢复两端快照。
    - 晋级后再次校验两端 version、source 和 digest，并提示新建会话或重新加载插件；隔离测试产生的 marketplace、缓存、配置和凭据副本必须清理。
    - 仅在 Windows Live E2E 完成真实 `1.1.0 → 1.1.1` 测试，并验证一次幂等 `--promote` 后勾选本项。
  - 当前状态：部分完成。提交 `1430832` 已实现跨客户端更新验收工具及配套文档；剩余条件是完成 Windows Live E2E 的真实升级与幂等 `--promote` 验证。

### 里程碑级完成条件

- [ ] 上述全部任务均标记为 `[x]`，且各自记录完成日期和验证证据。
- [ ] 发布元数据一致性、插件更新单元测试、技能与插件静态验证、Markdown 链接和 `git diff --check` 全部通过。
- [ ] 未解决决策和活动工作均保留在本文件或具名技术文档中，没有通过删除、弱化或提前归档隐藏。

## 当前里程碑：Codex / Claude Code 多插件目录与分发

状态：2026-08-13 根据用户明确安排提升为当前里程碑，并将范围收敛到 Codex 与 Claude Code。目标是维护一个逻辑插件目录和唯一内容源，可靠生成两端 marketplace 与 manifest；其他 Harness 只作为未来发展方向，不进入本里程碑验收门禁。

- [ ] 建立仓库级统一插件 catalog，作为插件身份和分发元数据的唯一事实来源。
  - 验收条件：
    - catalog 至少记录每个插件的稳定 ID、目录、版本、描述、分类，以及 Codex、Claude Code 所需的平台覆盖项。
    - `plugins/<plugin-id>/` 中的每个插件可独立安装、升级、禁用、卸载和回滚，不要求兄弟插件同步发版。
    - catalog 校验拒绝重复插件 ID、重复或冲突的 Skill ID、不存在的目录、越过插件根目录的路径，以及 manifest 与 catalog 身份不一致。
    - 插件发布包必须自包含；运行时不得通过 `../shared` 引用兄弟插件或仓库级共享文件。

- [ ] 将现有 `laxpud-vibekits` 单插件直接拆分为三个独立插件。
  - 验收条件：
    - marketplace 顶层名称继续使用 `laxpud-vibekits`；插件目录和插件 ID 调整为：
      - `plugins/code-quality/`，仅包含 `skills/code-comment-standard/`；
      - `plugins/python-project/`，仅包含 `skills/pyproject-standard/`；
      - `plugins/project-docs/`，仅包含 `skills/project-docs-bootstrap/`。
    - 三个插件分别拥有独立的 Codex、Claude Code manifest 和版本；Skill ID 保持不变，在提供插件命名空间的平台上分别使用 `code-quality:code-comment-standard`、`python-project:pyproject-standard` 和 `project-docs:project-docs-bootstrap`。
    - 删除旧 `plugins/laxpud-vibekits/` 插件包及其 marketplace 条目，不保留 deprecated bundle、兼容别名、聚合依赖包或人工维护的 Skills 副本。
    - 根 README、中文 README、安装与更新文档、适配层规范、fixture 和测试全部改为三个独立插件，并明确此次变更不提供旧插件迁移兼容层。
    - 三个插件均能在 Codex 与 Claude Code 中独立安装、升级、禁用、卸载和回滚；任一插件操作不得改变另外两个插件。

- [ ] 从统一 catalog 生成 Codex 与 Claude Code 的多插件 marketplace。
  - 验收条件：
    - `.agents/plugins/marketplace.json` 和 `.claude-plugin/marketplace.json` 的 `plugins[]` 包含并正确解析上述三个独立插件。
    - 生成过程保持 Codex 的 `policy.installation`、`policy.authentication`、`category` 及 Claude marketplace 必需字段，不以手工复制 JSON 作为长期维护方式。
    - 每个 marketplace 条目指向独立的 `plugins/<plugin-id>/`，且各插件 manifest、版本、名称和 Skills 路径通过静态校验。
    - 单个条目无效时能精确报告对应 marketplace、插件 ID 和字段，不再以 `plugins[0]` 代表整个目录。

- [ ] 消除元数据同步、安装检查和更新流程中的单插件假设。
  - 验收条件：
    - 移除固定 `PLUGIN_ROOT`、`PLUGIN_NAME`、`MARKETPLACE_NAME`、`plugins[0]` 和 `len(plugins) == 1` 等单插件约束，改由 catalog 解析目标。
    - 相关命令支持选择一个插件、多个插件或 `--all`，且默认行为有文档和测试覆盖。
    - 发布、digest、安装检查、晋级和回滚均以 `(platform, marketplace, plugin)` 为目标；一个插件失败或回滚不得改变兄弟插件的版本、启用状态或安装来源。
    - 旧 `laxpud-vibekits` 插件 ID、目录和 marketplace 条目被直接移除；测试不得以兼容旧单插件行为为通过条件。

- [ ] 建立“共享内容核心 + Codex / Claude Code 双适配”生成流程。
  - 验收条件：
    - 每个插件的 `skills/` 是该插件唯一的技能内容源；生成物和安装投影不得成为第二份人工维护的 Skill 副本。
    - 每个插件分别生成或同步 `.codex-plugin/plugin.json` 与 `.claude-plugin/plugin.json`，平台字段不得污染通用 `SKILL.md`。
    - 两端 manifest 的名称、版本、描述、Skills 路径和发布来源与 catalog 一致，同时允许各自保留必要的平台专属字段。
    - 生成器可重复执行且结果稳定；无输入变化时不得产生 diff，手工修改生成物后校验必须失败并给出修复方式。

- [ ] 建立 Codex / Claude Code 双端验证矩阵和发布门禁。
  - 验收条件：
    - Codex 与 Claude Code 分别验证 marketplace 发现/列出、逐插件安装、启用、Skill 加载、升级、禁用、卸载和独立回滚。
    - fixture 覆盖三个正式插件，并另含两个插件内的同名候选 Skill、一个无效路径和一次独立回滚，用于验证命名冲突、故障隔离和错误定位。
    - CI 必须先通过 catalog、两端生成物一致性和静态 schema 检查，再执行客户端 smoke test；需要凭据、网络或 GUI 的检查明确标为独立门禁。
    - 两端测试使用隔离配置且默认不调用模型；可选 Skill smoke test 的 token 消耗、清理边界和晋级条件必须保持显式。

### 里程碑级完成条件

- [ ] 上述全部任务均标记为 `[x]`，且各自记录完成日期和验证证据。
- [ ] 仓库中不存在把 marketplace 限制为单一插件的生产代码；指定的三个独立插件均能从同一 catalog 生成并通过 Codex、Claude Code 的安装与升级测试。
- [ ] 旧 `laxpud-vibekits` 插件 ID、目录和 marketplace 条目均不存在，且没有 deprecated bundle、兼容别名或聚合依赖包。
- [ ] Codex 与 Claude Code 的 marketplace、manifest 和安装状态均可追溯到统一 catalog 与插件内容，且一个插件的失败、升级或回滚不影响兄弟插件。
- [ ] 两端生成物均可由统一 catalog 和插件内容重新生成，`git diff` 能证明没有必须手工同步的 Skills 内容副本。

## 未来发展方向：跨 Harness 兼容与分发

本方向不属于当前里程碑，也不阻塞 Codex / Claude Code 多插件交付。进入实施前应重新核对各平台当时的官方协议、CLI 和分发政策，再把选定范围提升为具体验收里程碑。

- [ ] 评估可复用插件格式与第三方 marketplace 入口。
  - 候选范围：GitHub Copilot CLI、Qwen Code、CodeBuddy、Cursor，以及 Agent Plugins 标准。
  - 验收方向：优先复用 Claude 插件包或开放标准；只有现有格式无法表达平台能力时才新增专属 manifest，并验证多 manifest 共存时的选择优先级。

- [ ] 评估需要专属扩展 manifest 的 Harness。
  - 候选范围：Cursor Plugins、Gemini CLI extensions、Kimi Code plugins，以及未来出现稳定作者分发协议的平台。
  - 验收方向：由统一 catalog 生成薄适配文件，不复制 Skills 内容；平台专属 hooks、commands、agents、rules 和权限语义不得进入通用 `SKILL.md`。

- [ ] 评估以 Skills 目录或配置投影接入的平台。
  - 候选范围：OpenCode、TRAE、Windsurf、Qoder、Gemini CLI 及其他兼容 Agent Skills 的 Harness。
  - 验收方向：安装器支持 dry-run、选择插件、幂等安装和安全卸载，只处理自身创建的路径，不覆盖用户已有同名 Skill；扁平命名空间必须检测跨插件 Skill ID 冲突。

- [ ] 建立分级的跨 Harness 验证矩阵。
  - 验收方向：按“内容兼容、插件包兼容、marketplace 分发兼容”分别记录；有可用 CLI 的平台执行自动化 smoke test，只有 schema 的平台执行静态验证，其余平台保留明确的人工验证记录和置信度。
  - 发布边界：不得因为 `SKILL.md` 可读取就宣称 marketplace 或生命周期完全兼容，也不得让未来平台门禁阻塞当前 Codex / Claude Code 发布。
