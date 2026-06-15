# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目架构
这是一个平台无关的技能和规则集合仓库，核心结构：
- `skills/`：存储可复用的技能，每个技能对应一个独立子目录，包含技能的完整文档和使用说明
- `rules/`：存储轻量可复用的规则，每个规则对应一个独立markdown文件
- `.claude-plugin/`：Claude Code插件适配层，包含插件的配置文件和市场发布信息，与通用技能/规则完全解耦
- `.codex-plugin/`：Codex插件清单，声明插件元数据并指向通用 `skills/` 目录
- `.agents/plugins/marketplace.json`：Codex插件市场索引，用于让 `codex plugin marketplace add` 发现本仓库插件

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
1. **技能结构**：`skills/<skill-name>/SKILL.md`
2. **规则结构**：`rules/<rule-name>.md`，规则文件长度不得超过1000字符
3. **内容要求**：必须具备可复用性、清晰的使用说明，不包含平台特定的配置或逻辑
4. **适配层隔离**：平台特定配置必须放在对应平台的官方适配位置，例如 Claude Code 使用 `.claude-plugin/`，Codex 使用 `.codex-plugin/` 和 `.agents/plugins/marketplace.json`，不得污染通用技能/规则内容
