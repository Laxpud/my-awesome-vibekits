# Codex 多插件 GitHub 安装 Smoke Test

本文面向维护者，验证 Codex 从 GitHub marketplace 定位多个独立插件时依赖的元数据链路。

## 检查范围

`scripts/check_codex_install.py` 通过 [`plugin-catalog.json`](../plugin-catalog.json) 解析目标，并逐插件检查：

- `.agents/plugins/marketplace.json` 可解析，顶层名称与 catalog 一致，条目集合无缺失或额外插件；
- 每个条目的 `source.path` 精确定位 `plugins/<plugin-id>/`，且不逃出仓库；
- marketplace 条目、插件目录、版本和 `.codex-plugin/plugin.json` 与 catalog 一致；
- `policy.installation`、`policy.authentication` 和 `category` 完整；
- manifest 的 `skills` 指向插件自己的 `./skills/`，且 catalog 声明的每个 `SKILL.md` 都存在；
- manifest 的 GitHub repository 与中英文 README 的 `codex plugin marketplace add <owner>/<repo>` 一致；
- 两份 README 都引导用户进入 `/plugins`，并列出三个独立插件 ID。

单条目失败时，诊断包含 marketplace 路径、插件 ID 和具体字段，不使用 `plugins[0]` 代称整个目录。

## 本地检查

默认校验全部插件：

```bash
python scripts/check_codex_install.py
python scripts/check_codex_install.py --all
```

也可以选择一个或多个插件：

```bash
python scripts/check_codex_install.py --plugin code-quality
python scripts/check_codex_install.py --plugin python-project --plugin project-docs
```

脚本只读取 checkout，不修改 Codex 配置。成功退出码为 `0`；失败退出码为 `1`。

## 已发布远端检查

变更推送到 GitHub 后运行：

```bash
python scripts/check_codex_install.py --remote --all
```

远端模式从 catalog 读取 repository，浅克隆 GitHub 默认分支到临时目录，再执行同一检查。验证特定分支或 tag：

```bash
python scripts/check_codex_install.py --remote --ref <branch-or-tag> --all
```

远端模式需要 Git 和网络，但不会调用 `codex plugin marketplace add`，因此不写维护者的全局配置。发布后的真实安装、启停、升级、卸载和独立回滚属于 [`PLUGIN_UPDATE.md`](PLUGIN_UPDATE.md) 的独立客户端门禁。

## 维护约定

- 不在检查脚本中维护插件名、目录、版本或 repository 常量。
- 新增插件必须先进入 catalog，再生成 marketplace；不得手工追加 JSON。
- 三个插件可分别检查，默认行为是检查全部；每个被选插件都校验其 catalog 声明的完整 Skill 集合，而非只检查数组首项。
- 原 `laxpud-vibekits` 聚合插件条目不得作为兼容项恢复。
