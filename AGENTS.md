# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## 项目架构
这是一个平台无关的技能和规则集合仓库，核心结构：
- `plugins/laxpud-vibekits/skills/`：存储可复用的通用技能，每个技能对应一个独立子目录，包含技能的完整文档和使用说明
- `rules/`：优先存储轻量可复用的规则；也可保存明确标注用途的个人全局规则备份
- `.claude-plugin/`：Claude Code插件市场索引，指向统一插件包
- `plugins/laxpud-vibekits/`：Claude Code 与 Codex 共用的可安装插件包，内部包含各平台插件清单和唯一 `skills/` 目录
- `.agents/plugins/marketplace.json`：Codex插件市场索引，用于让 `codex plugin marketplace add` 发现本仓库插件
- `docs/index.md`：技术文档索引；根目录 `README.md` 使用英文，`docs/README.cn.md` 是中文翻译

## 常用命令
本项目是纯文档型仓库，无构建/测试/lint命令，常用操作命令：
```bash
# Claude Code：添加本地开发插件市场
/plugin marketplace add .

# Claude Code：安装本地开发版本插件
/plugin install laxpud-vibekits@laxpud-vibekits-dev

# Claude Code：重载插件
/reload-plugins

# Codex：添加本仓库插件市场
codex plugin marketplace add Laxpud/my-awesome-vibekits

# Codex：打开插件目录后选择 laxpud-vibekits 安装
codex
/plugins
```

## 技能/规则开发规范（必须严格遵守）
所有技能和规则必须保持平台无关性，禁止绑定到任何特定AI助手或IDE平台：
1. **技能结构**：`plugins/laxpud-vibekits/skills/<skill-name>/SKILL.md`
2. **可复用规则结构**：`rules/<rule-name>.md`，建议不超过1000字符
3. **内容要求**：通用技能和可复用规则必须具备可复用性、清晰的使用说明，不包含平台特定的配置或逻辑
4. **个人备份例外**：个人全局规则备份可以放在 `rules/`，但文件名和开头说明必须明确标注备份用途，避免被误认为通用规则
5. **适配层隔离**：平台特定配置必须放在对应平台的官方适配位置，例如 Claude Code 使用根 `.claude-plugin/marketplace.json` 与 `plugins/laxpud-vibekits/.claude-plugin/`，Codex 使用 `.agents/plugins/marketplace.json` 与 `plugins/laxpud-vibekits/.codex-plugin/`，不得污染通用技能/规则内容
6. **单一技能来源**：`plugins/laxpud-vibekits/skills/` 是唯一技能来源，禁止再创建根目录 `skills/` 副本
7. **文档入口边界**：根目录 `README.md` 保持英文公开入口；中文翻译放在 `docs/README.cn.md`；技术文档索引用 `docs/index.md`，不要重新创建 `docs/README.md` 作为索引
