# Codex GitHub 安装 Smoke Test

本文面向维护者，验证 Codex 从 GitHub marketplace 定位插件时依赖的最小元数据链路。检查范围刻意保持精简：

- `.agents/plugins/marketplace.json` 可解析，且唯一插件条目的 `source.path` 能定位到插件目录。
- marketplace 条目、插件目录和 `.codex-plugin/plugin.json` 使用相同插件名。
- marketplace 保留可安装所需的 `policy.installation`、`policy.authentication` 和 `category`。
- manifest 的 GitHub `repository` 与英文、中文 README 中的 `codex plugin marketplace add <owner>/<repo>` 一致。
- 两份 README 都引导用户进入 `/plugins` 并选择 manifest 声明的插件。

## 本地检查

修改 marketplace、manifest 或 README 安装说明后，在仓库根目录运行：

```bash
python scripts/check_codex_install.py
```

脚本只读取当前 checkout，不修改 Codex 配置。检查成功时退出码为 `0`；失败时退出码为 `1`，并输出第一个断链位置。

## 已发布远端检查

变更推送到 GitHub 后运行：

```bash
python scripts/check_codex_install.py --remote
```

远端模式从本地 manifest 读取 `repository`，把 GitHub 默认分支浅克隆到临时目录，再执行完全相同的检查。它用于确认用户通过 README 命令取得的已发布仓库确实包含可解析的 marketplace 和目标 plugin manifest。

需要验证特定分支或 tag 时使用：

```bash
python scripts/check_codex_install.py --remote --ref <branch-or-tag>
```

远端模式需要 `git` 和网络访问，但仍不会调用 `codex plugin marketplace add`，因此不会写入维护者的全局 marketplace 配置。若要做发布后的最终人工确认，再按 README 执行安装命令并在 `/plugins` 中确认 `laxpud-vibekits` 可见。

## 维护约定

脚本从 manifest 的 `repository` 推导 GitHub slug，并从 marketplace 的 `source.path` 定位 manifest；不要在脚本中再维护一份仓库名或插件路径常量。若未来支持多个 Codex 插件，应明确扩展选择规则和 README 契约，而不是静默放宽“唯一插件条目”的断言。
