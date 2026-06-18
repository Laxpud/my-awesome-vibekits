# 插件发布与客户端更新

本文说明维护者发布新版 `laxpud-vibekits` 后，使用者如何在 Codex 与 Claude Code 中刷新插件。插件更新和客户端自身更新是两件事：本页前半部分只更新插件，末尾单独列出客户端更新入口。

## 发布前提

Codex 和 Claude Code 的 Git marketplace 都只能取得已经推送到远端仓库的内容。本地修改完成后，维护者先同步版本并验证：

```bash
python scripts/sync_plugin_metadata.py --set-version <semver>
python scripts/check_codex_install.py
```

提交并推送相关文件后，客户端才能拉取新版本。推送完成后可运行以下远端检查，确认 GitHub 默认分支中的安装链路有效：

```bash
python scripts/check_codex_install.py --remote
```

## 自动化升级门禁

`scripts/plugin_update_e2e.py` 会通过真实 Codex CLI 与 Claude Code CLI 验证“旧版安装 → marketplace 刷新 → 目标版更新”的完整链路。默认只检查 version、marketplace/source、payload digest 和已安装的 `skills/pyproject-standard/SKILL.md`，不调用模型、不消耗 token，也不修改日常安装：

```bash
python scripts/plugin_update_e2e.py
python scripts/plugin_update_e2e.py --from-ref <commit-or-tag>
```

未指定 `--from-ref` 时，脚本从目标提交向后查找最近一个 manifest 版本不同的祖先。目标默认是 `origin/main`，也可显式设置报告和超时：

```bash
python scripts/plugin_update_e2e.py \
  --target-ref origin/main \
  --report artifacts/plugin-update-e2e/result.json \
  --timeout 300
```

每次运行会创建唯一的远端分支 `automation/plugin-e2e/<run-id>`，先指向旧提交，再以 `--force-with-lease` 推进到目标提交。两端都从该分支安装旧版和更新目标版；退出、失败、超时或中断时均尝试删除分支。远端分支未清理成功时，日常晋级不会开始。

隔离环境只复制 Codex `auth.json` 和 Claude `.credentials.json`，不会复制日常 `config.toml`、插件、skills、sessions 或 rules。凭据副本位于当前用户的私有临时目录，正常和异常退出都会删除；JSON 报告不会记录凭据内容、环境变量值或未脱敏配置。

### 可选的模型 smoke test

只有需要额外验证“客户端能够发现并调用 skill”时才添加 `--skill-smoke`：

```bash
python scripts/plugin_update_e2e.py --skill-smoke
```

该选项会调用 Codex 与 Claude 模型并消耗 token，不是安装或更新验收的默认条件。脚本在无 Git 仓库、无 Vibekits 源码的空目录中启动两端的新会话，并显式调用已安装的 `pyproject-standard`；两端必须分别返回以下固定值：

```json
{
  "buildBackend": "hatchling.build",
  "packageManager": "uv",
  "versionPath": "src/__init__.py",
  "licenseFile": "LICENSE",
  "indexName": "tsinghua",
  "indexUrl": "https://pypi.tuna.tsinghua.edu.cn/simple"
}
```

启用后，JSON Schema 和固定值必须同时通过。版本、正式来源、skill 路径和 payload digest 始终先验证；确定性契约错误不会重试，只有 Git/network、rate limit 和 transport timeout 最多重试三次。

payload digest 覆盖两端实际安装的共享内容，不包含只用于运输的 `.codex-plugin/`、`.claude-plugin/` manifest；UTF-8 文本在哈希前统一换行，因此同一 payload 在 Windows CRLF 与 Git LF checkout 中结果一致，二进制资源仍逐字节校验。

### 更新日常安装

只有测试通过后确实要更新当前用户安装时，才显式添加 `--promote`：

```bash
python scripts/plugin_update_e2e.py --promote
```

晋级模式额外要求：

- Git 工作区干净，并且 `HEAD`、`origin/main`、`--target-ref` 指向同一提交。
- Codex 与 Claude Code 至少各有一个已安装实例。
- Codex App、Claude Desktop 和交互式 CLI 已完全退出。
- 没有另一个 `--promote` 进程持有互斥锁。

脚本会更新 Codex 日常实例以及 Claude Code 的全部 `user`、`project`、`local` 实例，保持每个实例原有的 `scope`、`projectPath` 和 `enabled` 状态。已经达到目标 version 和 digest 的实例按幂等成功处理，不刷新 marketplace，也不创建快照。

更新前只备份以下状态：

- Codex：`config.toml`、`.tmp/marketplaces/laxpud-vibekits/`。
- Claude Code：`plugins/installed_plugins.json`、`plugins/known_marketplaces.json`、`plugins/marketplaces/laxpud-vibekits-dev/`、`plugins/cache/laxpud-vibekits-dev/`。

任一平台更新或最终校验失败时，两端都恢复到晋级前状态。回滚成功返回退出码 `2`；回滚失败返回 `3`，保留快照，并在报告中记录 `recoveryPath` 和逐实例 `manualCommands`。成功后 Codex 需要新建线程；Claude Code 运行 `/reload-plugins` 或重启会话。

### 报告和退出码

默认报告位于 `artifacts/plugin-update-e2e/<run-id>.json`，该目录不会提交到 Git。报告使用 `schemaVersion: 1`，包含固定的 baseline/target commit、version、digest，两端独立结果、promotion/rollback 和 cleanup 状态。

| 退出码 | 含义 |
| --- | --- |
| `0` | 隔离测试成功；若请求晋级，则晋级也成功。 |
| `1` | 隔离安装、更新、校验、可选 smoke 或清理失败。 |
| `2` | 日常晋级失败，但两端自动回滚成功。 |
| `3` | 自动回滚失败，需要按报告人工修复。 |
| `4` | 参数、Git 状态、客户端进程、认证、安装状态或运行环境不满足要求。 |

### 首次 Windows Live E2E

真实 E2E 会写入临时远端分支，因此不在 GitHub Actions 中运行。首次发布此工具时采用两阶段 bootstrap：

```bash
python -m unittest discover -s tests -p "test_plugin_update_*.py" -v
python scripts/plugin_update_e2e.py --from-ref b20b9c2
python scripts/plugin_update_e2e.py --from-ref b20b9c2 --promote
```

第一步和静态 validator 通过后，先把工具推送到 `origin/main`，再关闭 Codex App、Claude Desktop 和交互式 CLI，运行后两步。预期验证真实 `1.1.0 → 1.1.1`，且第二次 `--promote` 验证幂等行为。完成前不要勾选 `TODO.md` 中的端到端自动化事项。

## Codex

### Codex CLI

本仓库注册后的 Codex marketplace 名称是 `laxpud-vibekits`。刷新 marketplace snapshot 并确认插件版本：

```bash
codex plugin marketplace upgrade laxpud-vibekits
codex plugin list
```

如果 marketplace 已刷新但安装状态仍未更新，可重装插件：

```bash
codex plugin remove laxpud-vibekits@laxpud-vibekits
codex plugin add laxpud-vibekits@laxpud-vibekits
codex plugin list
```

完成后退出当前 CLI 会话，重新运行 `codex`，并新建线程。插件技能和工具以新线程作为安全的重新加载边界。

### Codex App

Codex App 与 CLI 在同一台主机上共享配置层，因此用上述 CLI 命令更新后，完全退出并重启 App，再新建线程即可使用新版插件。

只有 Codex App、没有可用 CLI 时，可以先完全退出并重启 App，然后打开 **Plugins → Created by you → laxpud-vibekits**，尝试卸载后重新安装。需要注意：当前官方文档只明确提供 App 中的安装、卸载和启停操作，没有给出强制刷新 Git marketplace snapshot 的 GUI 命令。如果重装后仍显示旧版本，需要使用 `codex plugin marketplace upgrade laxpud-vibekits` 刷新 marketplace，或等待 App 自身刷新可用版本。

参考：[Codex Plugins](https://developers.openai.com/codex/plugins)、[Build plugins](https://developers.openai.com/codex/plugins/build)。

## Claude Code

### Claude Code CLI

本仓库的 Claude Code marketplace 名称是 `laxpud-vibekits-dev`。直接在终端刷新 marketplace 并更新插件：

```bash
claude plugin marketplace update laxpud-vibekits-dev
claude plugin update laxpud-vibekits
```

第一条命令刷新 marketplace，第二条更新已安装插件。命令完成后重新启动 Claude Code 会话以加载新版插件。

### Claude Desktop 中的 Claude Code

本地或 SSH 会话可以直接从 Desktop 管理插件：

1. 点击输入框旁的 **+**。
2. 选择 **Plugins**。
3. 使用 **Add plugin** 安装插件，或使用 **Manage plugins** 启用、禁用和卸载插件。

需要立即更新时，可以在 Desktop 会话中运行：

```text
/plugin marketplace update laxpud-vibekits-dev
/plugin update laxpud-vibekits
/reload-plugins
```

也可以启用自动更新：

1. 运行 `/plugin` 打开插件管理器。
2. 选择 **Marketplaces → laxpud-vibekits-dev**。
3. 选择 **Enable auto-update**。

Claude Code 默认会为官方 marketplace 开启自动更新，但第三方和本地开发 marketplace 默认关闭。启用后，Claude Code 在启动时刷新 marketplace 和已安装插件；收到更新通知后运行 `/reload-plugins`。Desktop 的插件只适用于本地和 SSH 会话，不适用于 cloud session。

参考：[Discover and manage plugins](https://code.claude.com/docs/en/discover-plugins)、[Claude Code on desktop](https://code.claude.com/docs/en/desktop)。

## 更新客户端本身

以下操作不会更新 `laxpud-vibekits`，只更新客户端程序：

- Codex CLI：运行 `codex update`。
- Codex App：使用 App 自身的更新入口，然后重启 App。
- Claude Code CLI：运行 `claude update`；默认也会在后台检查更新。
- Claude Desktop：macOS 使用 **Claude → Check for Updates**，Windows 使用 **Help → Check for Updates**。

Claude Code 客户端更新参考：[Set up Claude Code](https://code.claude.com/docs/en/setup)。
