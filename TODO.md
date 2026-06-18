# TODO

本文件记录 Vibekits 当前活跃维护事项。已完成的历史规划可在需要时归档到 `docs/archive/`。

## 下一阶段

- [ ] 为每个已收录技能补充一个 README 可链接的最小使用示例。
  - 验收标准：根 README 的技能表能指向示例或对应 `SKILL.md` 中的示例段落，读者能在 1 分钟内判断技能适用场景。
- [ ] 建立插件发布前检查清单。
  - 验收标准：清单覆盖 Claude marketplace、Codex marketplace、两端 plugin manifest、技能 frontmatter、README 技能表和 JSON 解析验证。
- [x] 落实英文根 README 与中文 `docs/README.cn.md` 的双语策略。
  - 验收标准：根 README 使用英文，中文翻译位于 `docs/README.cn.md`，技术文档索引位于 `docs/index.md`。
- [ ] 基于真实仓库使用反馈继续改进 `project-docs-bootstrap`。
  - 验收标准：至少用 2 个不同规模的真实仓库验证后，再决定是否补充大仓库扫描策略、旧路径 redirect note 模板、双语 README 同步检查细则，以及最终报告中的澄清/假设摘要格式。
- [ ] 建立插件更新端到端测试自动化。
  - 验收标准：
    - 在隔离的测试配置中，分别通过 Codex CLI 和 Claude Code CLI 从测试 marketplace 安装旧版、刷新 marketplace 并更新到目标版本。
    - 更新后校验实际安装版本、插件来源、payload digest 和 `pyproject-standard/SKILL.md` 路径；默认不得调用模型或消耗 token，可用 `--skill-smoke` 额外验证新会话中的 skill 发现与调用。
    - 只有两端隔离测试及临时远端分支清理全部成功，并显式传入 `--promote` 时，才更新日常用户配置；任一门禁失败不得修改日常安装。
    - 晋级覆盖 Codex 实例与 Claude Code 的全部 `user`、`project`、`local` 实例，保持原 scope、projectPath 和 enabled 状态；任一失败必须恢复两端快照。
    - 晋级后再次校验两端 version、source 和 digest，并提示新建会话或重新加载插件；隔离测试产生的 marketplace、缓存、配置和凭据副本必须清理。
    - 仅在 Windows Live E2E 完成真实 `1.1.0 → 1.1.1` 测试，并验证一次幂等 `--promote` 后勾选本项。

## 维护原则

- 根 README 使用英文，只放入口信息和高频路径；中文翻译放在 `docs/README.cn.md`，长说明进入 `docs/`。
- `docs/index.md` 是技术文档索引，避免重新创建 `docs/README.md` 作为索引。
- TODO 使用复选框，并为非简单事项写出可验证的验收标准。
- 平台适配层和通用技能来源保持隔离，避免把 Claude Code 或 Codex 专属逻辑写进共享 `SKILL.md`。
