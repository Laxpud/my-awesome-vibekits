# TODO

本文件记录 Vibekits 当前活跃维护事项。已完成的历史规划可在需要时归档到 `docs/archive/`。

## 下一阶段

- [ ] 为每个已收录技能补充一个 README 可链接的最小使用示例。
  - 验收标准：根 README 的技能表能指向示例或对应 `SKILL.md` 中的示例段落，读者能在 1 分钟内判断技能适用场景。
- [ ] 建立插件发布前检查清单。
  - 验收标准：清单覆盖 Claude marketplace、Codex marketplace、两端 plugin manifest、技能 frontmatter、README 技能表和 JSON 解析验证。
- [ ] 评估是否需要英文根 README 或 `README.en.md`。
  - 验收标准：明确选择一种双语策略，并保证中文维护者说明仍可从根 README 或 `docs/` 发现。

## 维护原则

- README 只放入口信息和高频路径，长说明进入 `docs/`。
- TODO 使用复选框，并为非简单事项写出可验证的验收标准。
- 平台适配层和通用技能来源保持隔离，避免把 Claude Code 或 Codex 专属逻辑写进共享 `SKILL.md`。
