# Codex 多插件 GitHub 安装 Smoke Test

本文面向维护者，验证 Codex 从 GitHub marketplace 定位多个独立插件时依赖的元数据链路。

## 检查范围

`scripts/check_codex_install.py` 通过 [`plugin-catalog.json`](../plugin-catalog.json) 解析目标，并逐插件检查：

- `.agents/plugins/marketplace.json` 可解析，顶层名称与 catalog 一致，条目集合无缺失或额外插件；
- 本地条目的 `source.path` 精确定位 `plugins/<plugin-id>/`，且不逃出仓库；外部条目使用 `source: "url"`，URL 与 ref 均与 catalog 的 GitHub 来源一致；
- 本地包的版本与 `.codex-plugin/plugin.json` 与 catalog 一致；外部包默认不读取，显式传入 `--check-external` 后克隆核对双端 manifest 的身份、版本、描述和仓库地址；
- `policy.installation`、`policy.authentication` 和 `category` 完整；
- 已读取包的 Codex manifest 中 `skills` 指向插件自己的 `./skills/`，且 catalog 声明的每个 `SKILL.md` 都存在；
- 中英文 README 的 `codex plugin marketplace add <owner>/<repo>` 指向本聚合市场，外部插件 manifest 的 repository 则指向各自独立仓库；
- 两份 README 都引导用户进入 `/plugins`，并列出 catalog 中的全部独立插件 ID。

单条目失败时，诊断包含 marketplace 路径、插件 ID 和具体字段，不使用 `plugins[0]` 代称整个目录。

## 本地检查

默认校验全部插件：

```bash
python scripts/check_codex_install.py
python scripts/check_codex_install.py --all
```

也可以选择一个或多个插件：

```bash
python scripts/check_codex_install.py --plugin agent-dev-standards
python scripts/check_codex_install.py --plugin agent-docs-maintainer --plugin agent-task-resume
```

脚本只读取 checkout，不修改 Codex 配置。成功退出码为 `0`；失败退出码为 `1`。

当前三个条目均来自外部 GitHub 仓库。离线成功只表示来源和 README 契约正确；核对外部实际安装包时运行：

```bash
python scripts/check_codex_install.py --all --check-external
```

外部包按 catalog 中的 `ref` 克隆到临时目录，检查完成后清理，不修改日常安装，不调用模型。此检查不代替用户在 Codex 与 Claude Code 中测试安装、更新和执行。

需要回填外部更新时，先运行 `python3 scripts/sync_plugin_metadata.py --fetch-external --plugin agent-docs-maintainer` 预览，再加 `--write` 写入 catalog 和两端市场；省略插件选择时处理全部外部条目。此流程会在写入前读取双端 manifest、核对身份和版本并校验完整候选 catalog，随后仍需运行元数据同步检查和本安装契约检查。

`agent-docs-maintainer` 的 Codex 市场条目已启用展示元数据快照，由 `sync_plugin_metadata.py` 检查生成一致性。客户端刷新后需人工确认名称、简介、详细介绍、推荐提示词及独立仓库网站链接；外部插件安装前的技能列表仍依赖客户端加载实际包，不能用这些静态检查代替界面验证。

## 已发布远端检查

变更推送到 GitHub 后运行：

```bash
python scripts/check_codex_install.py --remote --all --check-external
```

远端模式从 catalog 读取 repository，浅克隆 GitHub 默认分支到临时目录，再执行同一检查。验证特定分支或 tag：

```bash
python scripts/check_codex_install.py --remote --ref <branch-or-tag> --all
```

远端模式需要 Git 和网络，但不会调用 `codex plugin marketplace add`，因此不写维护者的全局配置。发布后的真实安装、启停、升级、卸载和独立回滚属于 [`PLUGIN_UPDATE.md`](PLUGIN_UPDATE.md) 的独立客户端门禁。

## 维护约定

- 不在检查脚本中维护插件名、目录、版本或 repository 常量。
- 新增插件必须先进入 catalog，再生成 marketplace；不得手工追加 JSON。
- 各插件可分别检查，默认行为是检查全部；每个被选插件都校验其 catalog 声明的完整 Skill 集合，而非只检查数组首项。
- 原 `laxpud-vibekits` 聚合插件条目不得作为兼容项恢复。
