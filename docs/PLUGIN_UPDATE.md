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
