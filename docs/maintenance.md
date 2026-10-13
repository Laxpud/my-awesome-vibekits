# 市场维护指南

本文面向维护者，说明如何更新外部插件收录和验证结果。数据来源、字段约束与脚本关系见[架构总览](tech/architecture.md)；首次安装见 [README](../README.md)。以下 Python 命令均在本仓库根目录运行。

## 更新已有插件

准备：目标插件已在其独立仓库完成内容修改、相关验证和发布。先读取该仓库的 `AGENTS.md`；插件版本以独立仓库双端 manifest 为准，本市场不修改插件版本或外部 manifest。

### 1. 预览并回填收录快照

以下以 `agent-docs-maintainer` 为例。第一条只预览；确认差异属于目标更新后，第二条写入 catalog 和两份 marketplace：

```bash
python3 scripts/sync_plugin_metadata.py --fetch-external --plugin agent-docs-maintainer
python3 scripts/sync_plugin_metadata.py --fetch-external --plugin agent-docs-maintainer --write
```

`--plugin` 可重复以选择多个插件；省略选择或传 `--all` 时处理全部插件。选择单个插件仍保留兄弟市场条目。没有外部更新、只需根据已编辑的 catalog 重新生成市场时运行：

```bash
python3 scripts/sync_plugin_metadata.py --write
```

默认离线检查与显式外部回填的区别、保留字段及失败恢复方式见[生成过程](tech/architecture.md#数据来源与生成过程)。不要手改生成物。

### 2. 同步公开入口

核对外部来源、版本、完整技能清单和展示快照是否符合这次发布；名称、能力、描述或定位变化时，同步双语 README 的插件选择、技能入口及最小提示词。两端来源应指向同一仓库和 `ref`，插件网站链接指向独立仓库。

插件使用说明、设计与审查继续链接到对应独立仓库。当前市场不保留旧插件兼容包或别名，不恢复本地技能副本。

### 3. 执行本地交付检查

```bash
python3 scripts/sync_plugin_metadata.py
python3 scripts/check_codex_install.py --all
python3 scripts/check_markdown_links.py
python3 -m unittest discover -s tests -p "test_*.py" -v
git diff --check
```

这些命令成功退出时返回 `0`。安装检查失败返回 `1`，诊断指出市场路径、插件 ID 和字段。另行核对改动的 HTML 链接、页内锚点、正式翻译章节和 Mermaid 图；现有链接脚本不能覆盖这些内容。沿用已有测试，未经用户授权不新增测试。

涉及外部收录内容时，再显式检查实际包：

```bash
python3 scripts/check_codex_install.py --all --check-external
```

检查使用临时 clone，完成后清理，不修改日常安装、不调用模型。离线、外部包与客户端检查的覆盖区别见[检查边界](tech/architecture.md#检查能够证明什么)。

### 4. 发布市场并核对远端

只有用户明确要求时才提交和推送本市场，暂存范围限于本轮相关文件。推送后检查已发布入口：

```bash
python3 scripts/check_codex_install.py --remote --all --check-external
```

远端模式从 catalog 的市场仓库地址克隆默认分支。需要检查指定分支或 tag 时使用 `--remote --ref <branch-or-tag>`；`--ref` 不能单独使用。此命令验证远端 checkout 的安装契约，不代表未发布本地修改或真实客户端操作已通过。

## 新增收录

先在独立仓库建立可分发插件，再按 [catalog 契约](tech/architecture.md#catalog-契约)添加唯一 ID、GitHub 来源、收录字段、完整技能清单和双端平台配置。需要 Codex 安装前详情时启用 `platforms.codex.marketplaceMetadata: true`，然后预览实际 manifest 回填，避免手工编写第二套展示文案。

生成两份市场，补齐双语 README 的选择和首次使用入口，执行上述本地与外部包检查，核对本市场声明的来源、版本与技能入口。客户端展示和安装结果用于补充确认分发入口可用，不追加客户端完整生命周期验证门槛。

## 选择检查目标

安装检查默认覆盖全部插件，也支持单个或多个目标：

```bash
python3 scripts/check_codex_install.py --plugin agent-dev-standards
python3 scripts/check_codex_install.py --plugin agent-docs-maintainer --plugin agent-task-resume
```

选定目标只缩小逐插件检查范围，市场顶层身份和完整条目集合仍须正确。提交市场变更前执行全市场检查，避免只验证目标插件而遗漏兄弟条目。

## 客户端更新与旧安装迁移

市场发布后，用户在客户端刷新 `laxpud-vibekits`，再安装或更新需要的插件。市场快照更新不会自动完成日常安装更新。

| 旧插件 ID | 当前插件 ID |
| --- | --- |
| `project-docs` | `agent-docs-maintainer` |
| `task-continuation` | `agent-task-resume` |
| `code-quality`、`python-project` | `agent-dev-standards` |

先安装并确认新插件可用，再禁用或卸载对应旧插件，避免重复技能。Skill ID 保持不变，显式调用时使用新插件前缀；可复制示例见双语 README。具体刷新与管理操作参照 [Codex 官方插件说明](https://learn.chatgpt.com/docs/plugins)和 [Claude Code 官方插件管理说明](https://code.claude.com/docs/en/discover-plugins)。

本市场交付检查聚焦插件来源、收录快照、包内技能入口及安装更新说明。客户端负责执行刷新、安装、更新和已安装插件管理；启停、本地降级、客户端安装隔离和失败恢复不作为本市场交付门槛。日常配置修改只在当前任务明确授权的范围内执行。

旧同仓库 E2E、临时发布分支与日常晋级工具已移除，不作为市场维护工作恢复。客户端生命周期验证及其自动化规划已取消，原范围见[路线图](roadmap.md#已取消安排)。

## 回退与常见失败

- **生成物与 catalog 不一致：** 检查 catalog 修改是否正确，再用 `--write` 重新生成。不要通过手改 marketplace 消除报错。
- **外部拉取失败或双端版本不一致：** 检查来源、网络和独立仓库发布状态；外部回填在候选校验通过前不写本地文件。
- **外部检查报告版本或技能入口变化：** 核对独立仓库是否已发布新内容；按预览流程更新收录快照，不降低校验条件。
- **客户端显示或加载异常：** 检查市场是否刷新、目标插件是否安装并启用，以及当前会话是否已加载新技能。静态检查通过不能替代该环节。
- **需要回退市场收录：** 恢复对应 catalog 修改，重新生成两份 marketplace，执行同样的交付检查。
- **需要回退插件内容或已安装版本：** 插件内容在独立仓库处理；恢复旧内容后发布更高版本按正常收录更新维护。已安装版本的恢复由客户端处理，本市场不实现本地降级；恢复市场快照不会自动恢复客户端已安装内容。

[返回文档索引](index.md) · [架构总览](tech/architecture.md)
