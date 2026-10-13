# 维护体验与发布可靠性里程碑归档

状态：2026-10-12 完成并归档。以下保留原清单及当时的记录；未完成的外部客户端验证与未来分发安排见[路线图](../roadmap.md)，插件专属问题保留其独立仓库去向。历史版本、布局与“尚未发布”等说明不代表当前状态。

## 当前里程碑：维护体验与发布可靠性

状态：2026-08-13 “Codex / Claude Code 多插件目录与分发”里程碑完成并归档后恢复为当前里程碑。暂停期间的已完成、部分完成和未完成记录均保持原状态。

审查记录（2026-09-24）：已按插件记录当时的 7 项技能指令问题：[code-quality 3 项](https://github.com/Laxpud/agent-dev-standards/blob/main/docs/reviews/2026-09-24-code-quality.md)、[python-project 1 项](https://github.com/Laxpud/agent-dev-standards/blob/main/docs/reviews/2026-09-24-python-project.md)、[project-docs 3 项](https://github.com/Laxpud/agent-docs-maintainer/blob/main/docs/reviews/2026-09-24-project-docs.md)。原审查保留为历史；project-docs 的 A5–A7 和 code-quality 的 A1–A3 已在后续改造中处理，python-project 的 A4 已移交 [Agent Dev Standards 的 MIGRATION.md](https://github.com/Laxpud/agent-dev-standards/blob/main/MIGRATION.md)，保持未完成。

- [x] 为每个已收录技能补充一个 README 可链接的最小使用示例。
  - 验收条件：根 README 的按目标入口能指向示例或对应 `SKILL.md` 中的示例段落，读者无需先阅读完整 Skill 正文即可判断适用场景并复制最小提示词。
  - 完成记录：2026-09-01。
  - 验证证据：中英文 README 均按用户目标列出 catalog 中全部八个 Skill、对应 Plugin、Skill 直达链接和可复制最小提示词；`project-docs-readme` 另有展开的首次成功路径。2026-09-01 catalog/生成物同步、Codex 本地安装 smoke test、Markdown 链接、Skill quick validator、三个 Codex plugin validator、`git diff --check` 和 72 项测试全部通过。

- [x] 建立插件发布前检查清单。
  - 验收条件：清单覆盖 Claude marketplace、Codex marketplace、两端 plugin manifest、技能 frontmatter、README 技能表和 JSON 解析验证。
  - 完成记录：2026-06-18。
  - 验证证据：`docs/SKILL_RULE_GUIDELINES.md` 的“适配层同步清单”和“验证”章节覆盖全部验收项；提交 `12a193c` 增加发布同步与更新指引。

- [x] 落实英文根 README 与中文 `docs/README.cn.md` 的双语策略。
  - 验收条件：根 README 使用英文，中文翻译位于 `docs/README.cn.md`，技术文档索引位于 `docs/index.md`。
  - 完成记录：2026-06-18。
  - 验证证据：提交 `4603f13` 补充双语 README 顶部互链；当前三个文件均存在且职责分离。

- [x] 基于真实仓库使用反馈改造 `project-docs` 多 Skill 体系。
  - 验收条件：落实已确认的文档管理、模板与写作规则，并按[技能内容的轻量验收](https://github.com/Laxpud/my-awesome-vibekits/blob/90348c81ddeddceb989e3ea7a56f6d5fc36ff7df/docs/SKILL_RULE_GUIDELINES.md#技能内容的轻量验收)审阅；本轮安装与加载只检查 Codex。实际行为留待真实使用反馈，不要求第二个仓库逐项试跑。
  - 验收调整：2026-09-26 用户确认采用轻量验收，取消本轮额外行为试跑和其他客户端验证门槛；正式平台分发调整另列为后续工作。
  - 优先级调整：2026-09-01 用户明确把单 Skill 拆分提升为当前工作，不归档或隐藏本里程碑其他未完成项。
  - 当前状态：2026-09-26 已按[改造设计](https://github.com/Laxpud/agent-docs-maintainer/blob/main/docs/design/project-docs-multi-skill.md)完成七技能、模板、调用配置与入口同步，补齐其他 agent 使用的 `disable-model-invocation`，并分离维护源与自包含安装目录；尚未发布或更新日常安装。
  - 验证：生成一致性、42 处技能内链接、Codex 隔离安装与七技能发现通过；外部静态校验器仍不接受调用扩展，限制见[维护规范](https://github.com/Laxpud/my-awesome-vibekits/blob/90348c81ddeddceb989e3ea7a56f6d5fc36ff7df/docs/SKILL_RULE_GUIDELINES.md#技能内容的轻量验收)。
  - 历史验证（2026-09-01）：六个 Skill 均通过 quick validator，`project-docs` 通过 Codex plugin validator，catalog/双平台生成物和本地 Codex 安装元数据一致，Markdown 链接、`git diff --check` 与 72 项测试通过；真实 Codex CLI 显式加载六个 Skill，并通过 refactor 模糊路由、例行 TODO 不触发 planning、architecture 主导并组合 planning 三个边界场景。独立只读前向评审发现的主次、bootstrap/refactor 和 Plan 创建边界已修正。2026-09-01 README 契约更新后再次通过 `project-docs-readme` quick validator、三个 Codex plugin validator、catalog/生成物同步、本地安装 smoke test、Markdown 链接、`git diff --check` 和 72 项测试。仓库没有 Mermaid renderer，本轮只完成了基础语法与 fenced block 人工检查。

- [x] 更新 README 开头模板与 Orbit 徽章规范。
  - 验收条件：模板按项目需要组合语言切换、居中定位、徽章、预览和快捷链接；落实极光紫单区块、Simple Icons 优先、Inter 500 与图标校准，生成自包含安装资料，并明确 Badgewind 实际生成的验证边界。
  - 完成记录：2026-09-29；生成一致性、本地安装元数据、Markdown 链接与 diff 检查通过，quick validator 仍受已有调用字段限制；Badgewind 实际 SVG 未验证（本环境公共端点返回 403），字体加载边界见 [Orbit 徽章规范](https://github.com/Laxpud/agent-docs-maintainer/blob/main/sources/project-docs/references/readme-badge-rules.md)；尚未发布或更新日常安装。

- [x] 将 Orbit 首屏应用到当前仓库的双语 README，并明确徽章按统一 URL 模板复用。
  - 完成记录：2026-09-30；只替换文字、图标、品牌色与链接，撤销本轮本地 SVG 资源；同步技能模板与生成资料，不再要求逐枚渲染、微调或导出。已按 Iconify 官方数据选用 Codex 浅深色标志和 Claude Code 原色标志；公共 API 返回 403，在线显示尚未确认。

- [x] README 徽章统一通过 Iconify 查找资源，并增加首次生成时的素材方式选择：用户提供、AI 查找或不添加；已有决定不重复询问。
  - 规范保持通用：保留统一模板和品牌色考虑，移除图标集优先级、特定品牌特例与固定检索步骤。

- [x] 修复 GitHub 深色徽章 URL 被 `srcset` 中逗号截断的问题，并同步双语 README 与模板。
  - 验证：GitHub Markdown API 保留完整参数，六个图片代理响应均保留 32px 高度与 Orbit 配色；生成一致性、Markdown 链接和 diff 检查通过。

- [x] 清除徽章链接内的空白下划线，同步双语 README 与模板；GitHub Markdown API 确认三个徽章链接均无空白文本节点。

- [x] 补齐 project-docs 的共享规范引用，并扩展 progress 的 plan/spec 文件保存约定。
  - 验证：规范与场景审阅、生成一致性、元数据、链接及本地安装契约通过；Codex 隔离发现七技能、调用配置与 68 处安装资料引用通过，实际行为待使用反馈；未发布或更新日常安装。

- [x] 将 project-docs 全部规范与 Markdown 模板集中到共享 references，按引用生成自包含技能，并按六项规则精简指令。
  - 验证：生成与元数据一致性、链接、本地安装契约、现有 72 项测试及 Codex 隔离七技能发现通过；保留必要验证与明确权限边界，未新增测试或更新日常安装。

- [x] 按“主题 + 用途”统一 project-docs 参考文件名与标题，同步引用和生成物。

- [x] 将 code-comment-standard 改为专项注释审查、补全与整改技能，精简入口并补充带上下文和改写理由的五组正反例。
  - 验证：内容审阅、静态校验、元数据及链接检查、Codex 隔离安装发现与例库完整性通过；实际写作效果待使用反馈，未发布或更新日常安装。

- [x] 在 [sources/code-comment-examples](https://github.com/Laxpud/agent-dev-standards/blob/main/sources/code-comment-examples/README.md) 按 positive/negative 扁平归档用户提供的 7 个正例和 3 个反例，并为 code-comment-standard 补齐展示元数据、默认提示词与 YAML/frontmatter 双重手动触发配置。
  - 验证：10 个样本 SHA256 与原文件一致，调用配置、元数据、链接及 Codex 隔离安装发现与资料完整性检查通过；quick validator 不接受调用扩展字段，限制见[维护规范](https://github.com/Laxpud/my-awesome-vibekits/blob/90348c81ddeddceb989e3ea7a56f6d5fc36ff7df/docs/SKILL_RULE_GUIDELINES.md#技能内容的轻量验收)；未发布或更新日常安装。

- [x] 新增 `task-continuation:quota-resume`，指导创建五小时额度恢复后的自动续跑任务。
  - 验收条件：技能包含五小时与周额度复查、会话持有者复用与无持有者时恢复原线程、队列启动、自动审批等待、按授权限次使用重置卡、真实执行追踪、持久去重和停止条件；frontmatter 与 `openai.yaml` 均限定手动调用；catalog、生成元数据与双语 README 同步，完成内容审阅及 Codex 隔离发现检查。
  - 验证（2026-10-11）：内容审阅、元数据、本地安装、链接、72 项既有测试与 Codex 隔离安装发现通过；4 份技能文件及调用配置完整，quick validator 的已有调用扩展限制见[维护规范](https://github.com/Laxpud/my-awesome-vibekits/blob/90348c81ddeddceb989e3ea7a56f6d5fc36ff7df/docs/SKILL_RULE_GUIDELINES.md#技能内容的轻量验收)。真实续跑与卡兑换待使用验证，未更新日常安装。

- 已取消（2026-10-12）：建立旧本地插件更新端到端测试自动化。
  - 原因：插件已迁至独立仓库，用户确认清除内部插件及旧生命周期工具；以下原验收条件与部分完成记录保留，外部生命周期验证转入未来方向。
  - 验收条件：
    - 在隔离的测试配置中，分别通过 Codex CLI 和 Claude Code CLI 从测试 marketplace 安装旧版、刷新 marketplace 并更新到目标版本。
    - 更新后校验实际安装版本、插件来源、payload digest 和目标插件在 catalog 中声明的完整 Skill 集合；默认不得调用模型或消耗 token，可用 `--skill-smoke` 额外验证新会话中的 `pyproject-standard` skill 发现与调用。
    - 只有两端隔离测试及临时远端分支清理全部成功，并显式传入 `--promote` 时，才更新日常用户配置；任一门禁失败不得修改日常安装。
    - 晋级覆盖 Codex 实例与 Claude Code 的全部 `user`、`project`、`local` 实例，保持原 `scope`、`projectPath` 和 `enabled` 状态；任一失败必须恢复两端快照。
    - 晋级后再次校验两端 version、source 和 digest，并提示新建会话或重新加载插件；隔离测试产生的 marketplace、缓存、配置和凭据副本必须清理。
    - 仅在 Windows Live E2E 完成真实 `1.1.0 → 1.1.1` 测试，并验证一次幂等 `--promote` 后勾选本项。
  - 取消前状态：部分完成。提交 `1430832` 已实现跨客户端更新验收工具及配套文档；2026-08-13 已在多插件里程碑中将工具改为 catalog 驱动的独立插件流程并通过 fixture 回归；2026-09-01 将安装契约扩展为 baseline 按历史实际 Skill 集合、target 按 catalog 完整集合验证，并通过 `project-docs` 单 Skill 旧版升级到六 Skill 目标版的 fake-client 回归。剩余条件仍是完成 Windows Live E2E 的真实 `1.1.0 → 1.1.1` 升级与幂等 `--promote` 验证。

- [x] 清除内部插件与旧发布工具，迁出插件专属资料并保留外部市场维护入口。
  - 验收条件：删除旧插件、维护源、生成器与旧生命周期工具；六份文档在独立仓库可访问，未完成问题有明确去向；两端市场收录和展示内容保持不变，元数据、安装契约、链接、现有市场测试和 diff 检查通过。
  - 验证：2026-10-12 元数据、外部双端 manifest 与十技能入口、5 项保留的市场检查、迁入文档链接及 diff 检查通过；外部回填预览零差异，空 standalone/ 目录已移除；未更新日常安装。

- [x] 将插件迁移至外部独立仓库，本仓库保留 marketplace 聚合分发入口。
  - `project-docs` 和 `task-continuation` 分别迁移至独立仓库；将 `code-comment-standard` 和 `pyproject-standard` 合并为一个插件，再迁移至另一个独立仓库。
  - 将 Codex 与 Claude Code 两端 `marketplace.json` 中各插件的来源地址改为对应外部仓库地址，使插件在各自仓库独立维护与分发。
  - 当前状态：2026-10-12 用户确认迁移完成；[Agent Docs Maintainer](https://github.com/Laxpud/agent-docs-maintainer)、[Agent Task Resume](https://github.com/Laxpud/agent-task-resume)、[Agent Dev Standards](https://github.com/Laxpud/agent-dev-standards) 的独立源码与两端外部市场来源均已建立。旧源码、生成器与生命周期工具已清除，插件专属资料迁入对应仓库；客户端验证单列在[路线图](../roadmap.md#外部市场与客户端生命周期)，未视为已完成。

- [x] 按外部插件市场的职责重构全部活动文档。
  - 验收条件：双语 README 保留十技能入口和最小提示词；架构与维护流程各有唯一维护位置；未来任务移入路线图，完成与取消记录保留原文；AI 路由、链接和现有交付检查通过。
  - 验证：元数据、安装契约、外部包、链接与 5 项既有测试通过；Mermaid 图仅人工核对。

### 里程碑级完成条件

- [x] 当前范围内的任务满足完成条件并标记为 `[x]`；已取消任务明确保留取消原因，未完成事项有具体去向。
- [x] 市场元数据一致性、外部安装契约、现有市场 catalog 测试、Markdown 链接和 `git diff --check` 全部通过；技能与插件内容验证由独立仓库负责。
- [x] 未解决决策和活动工作均保留在本文件或具名技术文档中，没有通过删除、弱化或提前归档隐藏。
