# 外部插件发布与市场更新

Vibekits 的 marketplace 名称为 laxpud-vibekits，收录 agent-docs-maintainer、agent-task-resume 和 agent-dev-standards。插件内容、版本和发布由各独立仓库维护，本仓库只更新市场收录快照。

## 更新顺序

1. 在对应独立仓库读取其 AGENTS.md，完成内容修改、生成与相关验证；插件版本以该仓库双端 manifest 为准。
2. 独立仓库发布后，在本仓库预览目标插件的元数据，再显式写入：

```bash
python3 scripts/sync_plugin_metadata.py --fetch-external --plugin agent-docs-maintainer
python3 scripts/sync_plugin_metadata.py --fetch-external --plugin agent-docs-maintainer --write
```

3. 检查完整市场；省略 --plugin 或传 --all 可同步全部插件，重复 --plugin 可选择多个。选择单个插件不会删除兄弟市场条目。

```bash
python3 scripts/sync_plugin_metadata.py
python3 scripts/check_codex_install.py --all
python3 scripts/check_codex_install.py --all --check-external
python3 scripts/check_markdown_links.py
python3 -m unittest discover -s tests -p "test_*.py" -v
git diff --check
```

4. 只有用户明确要求时才提交、推送本市场。推送后可运行 `python3 scripts/check_codex_install.py --remote --all --check-external` 检查已发布入口。

展示字段、来源与策略的同步契约见 [Catalog 规范](SKILL_RULE_GUIDELINES.md)。marketplace 只携带收录与展示元数据，不复制外部 manifest 或技能源码，也不在本仓库给插件改版本。

## 客户端更新与旧安装迁移

市场发布后，用户在 Codex 或 Claude Code 刷新 laxpud-vibekits，安装需要的 agent-* 插件。旧 project-docs、task-continuation、code-quality 和 python-project 不会自动改名；按 [README 迁移说明](../README.md#run-your-first-skill)安装新插件，再禁用或卸载旧插件，避免重复技能。旧插件名仅用于说明历史安装，不恢复兼容包或别名。

客户端安装、启停、升级、卸载和回滚分别验证；操作一个插件后，核对其他插件状态未改变。静态检查或外部包克隆成功不代表客户端生命周期已经验证。真实客户端配置修改与日常安装更新只在当前任务明确授权的范围内执行。

旧同仓库 E2E、临时发布分支与日常晋级工具已随内部插件移除。跨仓库生命周期自动化尚未实现，剩余工作见 [TODO](../TODO.md#未来发展方向跨-harness-兼容与分发)。

## 回退与验证边界

市场收录变更可回退对应 catalog 修改，再生成两端 marketplace 并执行相同检查。插件内容或版本的回退在其独立仓库完成；客户端已安装版本的回退按客户端实际能力执行，不能用恢复旧内部快照代替。

元数据回填默认只预览；拉取失败或候选 catalog 无效时不写文件。外部包检查只读临时 clone，不安装插件、不调用模型、不复制凭据。安装契约与远端模式见 [Codex 安装检查](CODEX_INSTALL_SMOKE_TEST.md)。
