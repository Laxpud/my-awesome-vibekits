# 外部插件 Catalog 与适配层维护规范

Vibekits 维护 Codex 与 Claude Code 的聚合市场。技能、manifest、版本和发布在独立仓库维护，本仓库只维护收录快照并生成两端 marketplace。文档入口见 [docs/index.md](index.md)。

## 权威位置

| 内容 | 维护位置 |
| --- | --- |
| 市场身份、外部来源、版本与完整 Skill 收录快照 | [plugin-catalog.json](../plugin-catalog.json) |
| Codex marketplace 生成物 | .agents/plugins/marketplace.json |
| Claude Code marketplace 生成物 | .claude-plugin/marketplace.json |
| Agent Docs Maintainer 的技能、模板与设计 | [独立仓库](https://github.com/Laxpud/agent-docs-maintainer) |
| Agent Task Resume 的技能与执行器 | [独立仓库](https://github.com/Laxpud/agent-task-resume) |
| Agent Dev Standards 的技能、例库与审查 | [独立仓库](https://github.com/Laxpud/agent-dev-standards) |

本仓库不保存插件源码、技能生成器或本地插件 manifest，不恢复旧安装入口。修改插件内容前，读取对应独立仓库的 AGENTS.md；技能调用策略、共享资料和自包含约定由各插件维护。

## Catalog 契约

每个插件包含唯一 id、独立 SemVer、描述、分类、关键词、完整 skills 清单与双端平台字段。来源必须为 `source: {"type": "github", "repo": "owner/repo", "ref": "main"}`；ref 可省略以跟随默认分支，当前三个条目显式使用 main。不再接受 directory 本地包字段。

- repo 只接受不含 .git 后缀的 owner/repo；ref 不得包含空白、控制字符或以短横线开头。
- Skill ID 在整个市场中唯一；path 必须为 skills/<skill-id>，拒绝绝对路径、越界路径和反斜杠。
- Codex 来源生成 URL 与 ref，Claude Code 来源生成 GitHub repo 与 ref，均读取独立仓库根目录。
- 离线检查验证收录快照与市场来源；实际包内文件由显式外部检查读取，不借用本地副本。
- 版本先在独立仓库发布，再回填市场；本市场不提供改写插件版本的命令。

## Codex 安装前展示

`platforms.codex.marketplaceMetadata: true` 让生成器附带名称、简介、详细介绍、推荐提示词、发布者和 interface 展示字段；当前三个插件均已开启。展示内容以独立仓库实际 manifest 为准。

homepage、repository 和 interface.websiteURL 指向插件自己的仓库。市场条目不携带 skills 等包内路径；包内图标和截图路径也不复制到市场快照。外部插件安装前的技能列表由客户端加载实际包，静态检查不代表界面验证。

## 更新外部收录快照

先预览，再按需要写入；可重复 --plugin，省略选择或传 --all 时处理全部条目：

```bash
python3 scripts/sync_plugin_metadata.py --fetch-external --plugin agent-docs-maintainer
python3 scripts/sync_plugin_metadata.py --fetch-external --plugin agent-docs-maintainer --write
```

拉取按配置的 repo/ref 克隆到临时目录，只读同一 checkout 的双端 manifest 与技能目录，不执行插件脚本。两端身份、版本、描述和仓库地址必须一致；完整候选 catalog 校验通过后才准备写入。

回填更新版本、描述、关键词、完整技能清单、发布者与 Codex 展示快照。保留本市场的来源、安装与认证策略、展示开关，以及 Claude 分类和标签。默认输出差异，不写文件；--write 才更新 catalog 和两份 marketplace。替换失败时恢复已经替换的文件。

不传 --fetch-external 时完全离线，只生成或检查两份市场；即使选择单个插件，市场仍保留全部条目。此流程不修改独立仓库、不安装插件、不提交或推送。

## 适配层同步清单

- 独立仓库已发布目标版本，catalog 的来源、版本、描述与完整技能集合正确。
- 两端 marketplace 均由生成器更新，来源指向同一独立仓库与 ref。
- Codex 展示字段与独立仓库一致，策略和展示开关保持本市场配置。
- README.md 与 docs/README.cn.md 的插件清单、安装入口和章节结构对齐。
- 插件使用说明、设计与审查链接指向对应独立仓库。

## 验证

本地交付执行现有检查：

```bash
python3 scripts/sync_plugin_metadata.py
python3 scripts/check_codex_install.py --all
python3 scripts/check_markdown_links.py
python3 -m unittest discover -s tests -p "test_*.py" -v
git diff --check
```

按需运行 `python3 scripts/check_codex_install.py --all --check-external`，核对外部双端 manifest 和完整技能入口。检查不安装插件、不调用模型。真实客户端安装、更新、启停与卸载分别验证，边界见 [更新流程](PLUGIN_UPDATE.md) 和 [安装契约](CODEX_INSTALL_SMOKE_TEST.md)。

现有 catalog 测试覆盖外部条目、技能冲突、越界路径、生成幂等和手动漂移；旧本地发布与晋级实现及其专属测试已移除。未经用户授权不新增测试。
