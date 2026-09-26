# 文档技能使用说明

适用范围：当前源码中的 project-docs 七技能改造，尚未发布。以下调用设置本轮只核对 Codex，其他客户端未验证。安装入口见 [README](../README.md#quick-start)，中文说明见[中文 README](README.cn.md#快速开始)。

## 继续已有任务

项目已有 TODO 时，可以直接要求 Codex 继续当前已授权任务。轻量技能 `project-docs-progress` 可自动参与，也可以显式指定：

```text
使用 $project-docs:project-docs-progress 继续 TODO 中当前任务。完成后只勾选；必要验证最多保留一句结论，不写工作日志。
```

预期结果：更新原有条目中的完成情况、必要阻塞或下一步。不另建报告；没有 TODO 时不自动创建文档体系。结束当前里程碑也不代表自动开始下一个。

## 选择专项文档工作

其余六个文档技能在 Codex 中仅显式调用。下面的提示词授权编辑；若只想看建议，将要求改为“只审查，不修改”。

| 需要做什么 | 可直接使用的提示词 |
| --- | --- |
| 缺少基本文档 | 使用 $project-docs:project-docs-bootstrap 建立这个项目当前真正需要的最小文档入口。 |
| 文档太多、重复或难找 | 使用 $project-docs:project-docs-refactor 整理活动文档与导航，保留旧历史原文。 |
| 新用户不知道怎么用 | 使用 $project-docs:project-docs-readme 改进 README 和正式翻译；常用操作需要展开时补使用说明。 |
| 建立任务与未来方向 | 使用 $project-docs:project-docs-planning 组织 TODO 和 roadmap，保留讨论过的初步方案与链接。 |
| 理解系统和源码关系 | 使用 $project-docs:project-docs-architecture 更新本里程碑影响的技术说明，用 C4 和源码映射展示关系。 |
| AI 规则太长或重复 | 使用 $project-docs:project-docs-guidance 精简 AGENTS 的阅读路由，保留真实约束，把 CLAUDE 改为相对软链。 |

预期结果是所选范围的文档修改。技能不会因为文档间有链接而自动调用其他专项技能，也不要求先生成审计报告并再次批准已经授权的编辑。

## 保存未来会用到的方案

Agent 按自己的方式生成 plan/spec。如果要在以后实施时继续引用，可明确要求：

```text
使用 $project-docs:project-docs-planning 把刚才讨论的候选方案关联到 roadmap 的 Backlog。需要长期引用的 plan/spec 保存到项目中，不改写正文；本次不开始实施。
```

默认需要长期保留的文件进入 `docs/plans/` 或 `docs/specs/`，名称包含创建时间并精确到分钟；完成后原文移入统一 `docs/archive/`，保留任务链接。不是每个任务都需要 plan/spec。

## 控制记录量和更新时机

| 内容 | 默认做法 |
| --- | --- |
| 已完成任务 | 勾选；有必要才附一条短验证结论。 |
| 未来方向 | Roadmap 后续里程碑，尚未承诺的候选放 Backlog。 |
| 技术文档与用户说明 | 里程碑或发布节点核对受影响内容；直接阻碍使用的错误及时改。 |
| 已完成里程碑 | 原 TODO 区块移到 archive；roadmap 只留名称与链接。 |
| 原始证据 | 有复现或判断需要才保留；已有持久来源直接链接。 |
| 旧历史 | 默认不加工；明确要求时才统一格式。 |

## 技能没有出现或行为不符

先检查插件已安装并启用，再新建 Codex 任务。本轮改造未发布，远端已安装版本可能仍只有六个技能。技能可见后，专项工作使用 `$project-docs:project-docs-readme` 等显式名称。

这些规则限制预期行为，不能保证模型每次都遵守。若实际仍产生冗长日志，保留触发提示词与对应条目作为反馈即可，不必为此生成一份完整验证报告。

## 进一步阅读

[当前进度](../TODO.md) · [改造设计](design/project-docs-multi-skill.md) · [维护文档入口](index.md)
