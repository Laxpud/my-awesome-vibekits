# 多插件发布与客户端更新

本文说明三个独立插件的版本发布、双客户端验证、更新、晋级和回滚。插件版本彼此独立；marketplace 顶层名称统一为 `laxpud-vibekits`。

## 目标选择

元数据、安装检查和 E2E 命令都使用同一选择规则：

- 不传选择参数：处理 catalog 中全部插件；
- 重复 `--plugin <id>`：按给定顺序处理一个或多个插件；
- `--all`：显式处理全部插件。

合法 ID 是 `code-quality`、`python-project` 和 `project-docs`。发布、digest、安装校验、晋级和回滚的最小目标都是 `(platform, marketplace, plugin)`；一次操作不得改写兄弟插件的版本、来源或 enabled 状态。

## 发布前提

先修改 [`plugin-catalog.json`](../plugin-catalog.json) 中目标插件的版本和元数据，再生成并验证：

```bash
python scripts/sync_plugin_metadata.py --plugin python-project --set-version <semver>
python scripts/sync_plugin_metadata.py
python scripts/check_codex_install.py --all
python -m unittest discover -s tests -p "test_*.py" -v
```

多个插件同版发布时可以重复 `--plugin`，只有确实要求同时发版时才使用 `--all --set-version`。生成器同步两份 marketplace 与选中插件的两端 manifest；技能内容不复制。

提交并推送后执行远端检查：

```bash
python scripts/check_codex_install.py --remote --all
```

## 验证矩阵与门禁

验证按固定顺序分层：

| 门禁 | 环境 | 覆盖内容 | 是否调用模型 |
| --- | --- | --- | --- |
| catalog 与生成物 | 普通 CI | ID/路径/Skill 冲突、双端 manifest、marketplace、防漂移 | 否 |
| 隔离生命周期 fixture | 普通 CI | 三插件双端发现、逐插件安装、Claude 启停、Codex enabled 状态保留、Skill 路径、升级、卸载、独立回滚、故障隔离 | 否 |
| 客户端 schema/CLI | 有 Codex 与 Claude CLI 的环境 | 三个正式插件及两份 marketplace validator | 否 |
| Live E2E | 有凭据、网络和远端写权限的 Windows runner | 真实 marketplace 刷新、逐插件安装/升级、version/source/digest、清理 | 默认否 |
| Skill smoke | Live E2E 可选项 | 新会话发现并调用 `python-project:pyproject-standard` | 是 |
| Codex GUI 生命周期 | Codex App 或 CLI `/plugins` | 逐插件启停和卸载，确认兄弟插件状态不变 | 否 |

普通 CI 先运行静态门禁，再运行确定性的 fake-client 生命周期测试。需要凭据、网络、GUI 或模型的门禁独立运行，不得让凭据缺失伪装成静态检查成功，也不得默认消耗 token。

测试 fixture 明确包括：三个正式插件；两个插件内同名 `shared-name` 候选 Skill 的冲突 catalog；一个越过根目录的无效路径 catalog；以及只升级和回滚 `python-project`、保持另外两插件不变的生命周期场景。

## 自动化升级门禁

`scripts/plugin_update_e2e.py` 默认按 catalog 逐个测试全部插件，也支持选择：

```bash
python scripts/plugin_update_e2e.py
python scripts/plugin_update_e2e.py --plugin python-project
python scripts/plugin_update_e2e.py --plugin code-quality --plugin project-docs
python scripts/plugin_update_e2e.py --all --from-ref <commit-or-tag>
```

每个插件使用独立临时分支 `automation/plugin-e2e/<run-id>-<plugin-id>`，完成“旧版安装 → marketplace 刷新 → 目标版更新”。两端均检查目标插件的 version、marketplace/source、插件自己的 Skill 路径和 payload digest。退出、失败、超时或中断都清理临时分支、隔离配置和凭据副本；任一清理失败会阻止日常晋级。

未指定 `--from-ref` 时，工具在目标插件自己的 manifest 历史中查找最近的不同版本祖先。目标默认是 `origin/main`。每个插件的报告数据按插件 ID 分组，避免一个条目的结果覆盖其他条目。

### 可选 Skill smoke

只有需要验证新会话的 Skill 发现与调用时才添加：

```bash
python scripts/plugin_update_e2e.py --plugin python-project --skill-smoke
```

该选项会调用 Codex 与 Claude 模型并消耗 token，默认关闭。当前固定 smoke 契约属于 `pyproject-standard`，因此选择全部插件时也只对 `python-project` 运行模型 smoke；安装、版本、来源、路径和 digest 检查始终不调用模型。

## 更新日常安装

只有所有选中插件的隔离测试和临时分支清理都成功，并且确实要更新日常安装时，才显式添加 `--promote`：

```bash
python scripts/plugin_update_e2e.py --plugin python-project --promote
python scripts/plugin_update_e2e.py --all --promote
```

晋级额外要求工作区干净，`HEAD`、`origin/main` 和目标 ref 为同一提交，Codex 与 Claude Code 均有选中插件实例，相关客户端完全退出，且没有并发晋级进程。

工具逐插件保存最小状态快照，更新 Codex 实例和 Claude Code 的全部 `user`、`project`、`local` 实例，并保持原 `scope`、`projectPath` 与 enabled 状态。单插件失败时只恢复该插件目标的两端快照；已经成功或未选择的兄弟插件不会被回滚或改写。已经达到目标 version 与 digest 的插件按幂等成功处理。

成功后 Codex 新建任务；Claude Code 运行 `/reload-plugins` 或重启会话。

## 手动生命周期确认

### Codex

刷新 marketplace：

```bash
codex plugin marketplace upgrade laxpud-vibekits
codex
/plugins
```

在 `laxpud-vibekits` marketplace 标签中逐个打开插件。Codex CLI 的 `/plugins` 浏览器支持安装、卸载，并用 `Space` 单独启停已安装插件。对一个插件执行操作后，核对另外两个插件的安装和启用状态未变化。

### Claude Code

```bash
claude plugin marketplace update laxpud-vibekits
claude plugin install python-project@laxpud-vibekits
claude plugin disable python-project
claude plugin enable python-project
claude plugin update python-project@laxpud-vibekits
claude plugin uninstall python-project
```

替换插件 ID，逐一覆盖三个插件。`project` 或 `local` 实例应在对应项目目录并带相应 `--scope` 执行。更新后运行 `/reload-plugins` 或新建会话。

## 报告、退出码与恢复

默认报告位于 `artifacts/plugin-update-e2e/<run-id>.json`，该目录不会提交。报告记录逐插件 baseline/target commit、version、digest，两个平台结果、晋级、回滚和清理状态，不记录凭据或未脱敏配置。

| 退出码 | 含义 |
| --- | --- |
| `0` | 所有选中插件的隔离测试成功；若请求晋级，晋级也成功。 |
| `1` | 隔离安装、更新、校验、可选 smoke 或清理失败。 |
| `2` | 日常晋级失败，但选中插件的两端自动回滚成功。 |
| `3` | 自动回滚失败；报告保留 recovery path 和逐实例人工命令。 |
| `4` | 参数、Git 状态、客户端进程、认证或安装状态不满足前提。 |

任何失败都应先按报告中的 `(platform, marketplace, plugin)` 确认影响范围，再执行人工恢复。不得通过安装旧聚合插件来恢复。

## 无兼容迁移层

原 `laxpud-vibekits` 插件 ID 和 `plugins/laxpud-vibekits/` 已直接删除。旧安装需要先在各客户端卸载旧 ID，再按 README 选择三个新插件；仓库不提供 deprecated bundle、别名、聚合依赖或 Skills 副本。

Codex 的 marketplace 和 `/plugins` 行为参考 [official OpenAI plugin documentation](https://learn.chatgpt.com/docs/plugins) 与 [plugin packaging guide](https://developers.openai.com/plugins/build/plugins)。Claude Code 生命周期命令参考 [Discover and manage plugins](https://code.claude.com/docs/en/discover-plugins)。
