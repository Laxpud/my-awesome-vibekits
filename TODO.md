# TODO

本文件是 Vibekits 活动任务、里程碑、验收条件和状态维护流程的权威位置。长期技术规则见 [`docs/index.md`](docs/index.md)；只有满足下述归档门槛后，才把完成记录移入 `docs/archive/`。

## 执行与维护规则

1. 除非用户明确指定其他任务，否则默认执行当前里程碑中第一个未完成任务。
2. 只有任务的全部验收条件通过后才能将其标记为 `[x]`，并同时记录完成日期和验证证据。
3. 部分完成的任务保持 `[ ]`，并记录已完成内容和仍未满足的条件。
4. 不得通过删除、弱化或降低验收条件来制造完成状态。
5. 正常推进时，只有当前里程碑的全部任务和全部里程碑级完成条件都通过后，才能将完成记录归档到 `docs/archive/` 并把下一里程碑提升为当前里程碑；用户明确调整优先级时，必须保留被暂停里程碑的全部状态并记录调整，不得归档或制造完成状态。
6. 每次交付前按本节规则同步任务状态、剩余条件和验证证据。

## 当前里程碑：维护体验与发布可靠性

状态：2026-08-13 “Codex / Claude Code 多插件目录与分发”里程碑完成并归档后恢复为当前里程碑。暂停期间的已完成、部分完成和未完成记录均保持原状态。

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
  - 当前状态：部分完成（1/2）。2026-08-08 已在本仓库应用新版文档所有权、里程碑 TODO 和项目指导路由规则；2026-08-27 根据使用反馈补充项目指导文件的目录作用域、规则下沉、继承去重和渐进式注入要求，并通过技能结构、生成元数据一致性与 Markdown 链接检查。仍需至少 1 个不同规模的真实仓库验证，再评估候选增强项。

- [ ] 建立插件更新端到端测试自动化。
  - 验收条件：
    - 在隔离的测试配置中，分别通过 Codex CLI 和 Claude Code CLI 从测试 marketplace 安装旧版、刷新 marketplace 并更新到目标版本。
    - 更新后校验实际安装版本、插件来源、payload digest 和 `pyproject-standard/SKILL.md` 路径；默认不得调用模型或消耗 token，可用 `--skill-smoke` 额外验证新会话中的 skill 发现与调用。
    - 只有两端隔离测试及临时远端分支清理全部成功，并显式传入 `--promote` 时，才更新日常用户配置；任一门禁失败不得修改日常安装。
    - 晋级覆盖 Codex 实例与 Claude Code 的全部 `user`、`project`、`local` 实例，保持原 `scope`、`projectPath` 和 `enabled` 状态；任一失败必须恢复两端快照。
    - 晋级后再次校验两端 version、source 和 digest，并提示新建会话或重新加载插件；隔离测试产生的 marketplace、缓存、配置和凭据副本必须清理。
    - 仅在 Windows Live E2E 完成真实 `1.1.0 → 1.1.1` 测试，并验证一次幂等 `--promote` 后勾选本项。
  - 当前状态：部分完成。提交 `1430832` 已实现跨客户端更新验收工具及配套文档；2026-08-13 已在多插件里程碑中将工具改为 catalog 驱动的独立插件流程并通过 fixture 回归。剩余条件仍是完成 Windows Live E2E 的真实 `1.1.0 → 1.1.1` 升级与幂等 `--promote` 验证。

### 里程碑级完成条件

- [ ] 上述全部任务均标记为 `[x]`，且各自记录完成日期和验证证据。
- [ ] 发布元数据一致性、插件更新单元测试、技能与插件静态验证、Markdown 链接和 `git diff --check` 全部通过。
- [ ] 未解决决策和活动工作均保留在本文件或具名技术文档中，没有通过删除、弱化或提前归档隐藏。

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
