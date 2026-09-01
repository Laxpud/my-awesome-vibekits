---
name: project-docs-planning
description: 设计、创建或实质维护仓库内的项目规划体系，包括 TODO.md、roadmap、milestone、backlog、task、活动工作入口和复杂实施 plan。适用于调整承诺、优先级、退出条件、规划文件结构或归档；同一请求还要定义目标系统结构时组合 project-docs-architecture 并以 architecture 为主，普通 checkbox/证据同步、代码 TODO 注释和外部 tracker 同步不属于本 Skill。
---

# 项目规划文档维护

## 目标

建立一个能区分方向、承诺、候选工作、执行单元和实施方法的规划体系。固定的是概念和唯一活动入口，不是某个文件名或完整目录模板。

本 Skill 在创建、重构或实质调整规划体系时触发。普通任务完成后，只按仓库已有契约补一条状态或证据时直接更新，不加载本 Skill。

同一请求同时要求定义目标系统结构和编写实施步骤时，先由 `project-docs-architecture` 作为主 Skill 确立目标边界，再由本 Skill 编写阶段、验证和回滚并链接目标文档。目标结构已经由权威文档确定、请求只问如何实施时，本 Skill 单独作为主 Skill，不重复加载 architecture。

## 共同底线

1. 编辑前读取仓库证据和适用项目指导。
2. 尊重既有权威位置、清晰约定和用户拥有的改动。
3. 不编造项目目的、架构、命令结果或完成状态。
4. 同一主题保留一个权威来源，其他位置使用短路由或链接。
5. 按“仓库证据 → 插件默认值 → 高风险澄清”决策；用户要求“按默认值”也不授权不可逆操作。
6. 回读改动，检查链接和 diff，并报告假设、验证及未执行门禁。

## Reference 路由

创建规划体系、改变 planning authority、设计 milestone/task 状态或归档历史时，读取 [`references/planning-model.md`](references/planning-model.md)。只做已有契约下的局部内容维护时不必重新加载完整模型。

## 规划流程

1. **发现规划权威。**
   - 读取 README、`TODO.md`、`ROADMAP.md`、`docs/plans/`、`docs/milestones/`、项目指导文件和外部 tracker 路由。
   - 找出当前实际权威来源、重复状态、未解决工作和已成为历史的计划。
   - 外部 tracker 可以是权威来源，但本 Skill 只维护仓库内路由和仓库级契约，不复制或同步外部状态。

2. **按概念分类。**
   - Roadmap 回答方向、结果、阶段和依赖。
   - Milestone 表示已承诺、有 outcome 和退出条件的交付边界。
   - Backlog 保存尚未承诺的候选工作。
   - Task 是可执行、可验证的工作单元。
   - Plan 保存复杂任务或 milestone 的实施顺序、验证和回滚。
   - `TODO.md` 只是这些概念的一种载体，不能反过来决定语义。

3. **选择渐进布局。**
   - 每个项目声明一个唯一活动工作入口；新项目存在真实活动工作时默认根 `TODO.md`。
   - 轻量项目可在一个入口中表达 primary milestone、tasks 和 backlog。
   - 存在多个阶段或长期方向时增加 `ROADMAP.md`；复杂 milestone 或 task 按需增加 `docs/milestones/` 或 `docs/plans/`。
   - 不预创建空目录、空模板或重复任务状态。

4. **维护承诺和执行。**
   - 允许一个 primary milestone 和明确标记的 secondary active milestones。
   - 用户指定工作优先；否则选择 primary 的有效 Current focus、显式高优先级 ready task，再按文档顺序选择 ready task。
   - 跳过 `Blocked by` 尚未解除的 task。Primary 没有 ready task 时报告状态并建议 secondary，不自动切换或提升 backlog。
   - Backlog 只有在用户明确要求，或一次明确的规划/优先级维护操作中才提升为承诺工作。

5. **维护完成与范围变化。**
   - Milestone 必须写 outcome、退出条件和 tasks；依赖、非目标、风险和日期仅在真实有用时添加。
   - Milestone 以 outcome 和退出条件完成。Tasks 可以新增、替换、取消或移回 backlog，但必须留下理由，且不能删除或弱化退出条件制造完成状态。
   - 简单 task 可以只勾选；非简单 task 记录关键验证。Milestone 完成时记录结果摘要、退出条件证据和未解决事项。

6. **管理 Plan 和历史。**
   - 只有存在重要方案选择、跨模块工作、较高风险、分阶段验证，或 task 描述不足以恢复上下文时才创建独立 Plan。
   - 完成后将持久架构事实和决策迁入 architecture、ADR 或其他权威文档，再按项目策略归档或删除 Plan。
   - 小项目可以暂留最近完成项；历史开始干扰活动工作时，将详细记录移入 `docs/archive/`，入口只保留简短结果和链接。

7. **验证。**
   - 确认只有一个活动工作入口，每个 active milestone 的角色明确，backlog 没有被伪装为承诺。
   - 检查 blocker、Current focus、退出条件、证据和跨文档链接互相一致。
   - 确认归档没有隐藏未完成工作，外部 tracker 状态没有被复制成易漂移缓存。

## 示例

正例：

```text
把现在混在 TODO 里的长期方向、当前 milestone 和候选工作重新整理，并定义默认下一任务规则。
```

预期：识别唯一活动入口，区分 roadmap、milestone、backlog 和 task，采用与项目复杂度相称的渐进布局。

近邻反例：

```text
功能已经完成，请按 TODO 顶部现有规则勾选任务并补充刚刚执行的测试命令。
```

这是既有契约下的例行状态同步，直接更新即可，不加载本 Skill。
