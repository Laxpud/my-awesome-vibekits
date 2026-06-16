# Vibekits

实用技能（skills）和规则（rules）集合，用于沉淀、复用和分享跨项目工作流。

本仓库的核心内容保持平台无关：`skills/` 存放通用技能，`rules/` 优先存放通用规则；`.claude-plugin/`、`.codex-plugin/` 与 `.agents/plugins/marketplace.json` 仅作为不同平台的适配层。

按维护者个人备份需求，`rules/` 也可以保存明确标注用途的个人全局规则备份。这类文件用于 GitHub 备份和人工迁移，不作为平台无关通用规则对外分发。

## 如何使用

### 通用方式

1. 克隆仓库到本地
2. 浏览 `skills/` 或 `rules/` 目录查看可用内容
3. 按照各目录中的说明文件使用

### Claude Code 插件使用

本项目已内置 Claude Code 插件支持，开箱即用：

```bash
# 添加插件市场
/plugin marketplace add https://github.com/Laxpud/my-awesome-vibekits

# 安装插件
/plugin install laxpud-vibekits@laxpud-vibekits-dev
```

### Codex 插件使用

Codex 推荐通过插件（plugin）分发可复用 skills。本仓库提供 `.agents/plugins/marketplace.json` 作为插件市场索引，并通过 `.codex-plugin/plugin.json` 暴露通用 `skills/` 目录；通用技能内容仍保持平台无关。

添加插件市场后，在 Codex 的插件目录中安装：

```bash
# 添加插件市场
codex plugin marketplace add Laxpud/my-awesome-vibekits

# 打开 Codex CLI 插件目录
codex
/plugins
```

在插件目录中选择 `laxpud-vibekits` 并安装。安装后开启新线程，可直接描述任务，或使用 `@` 显式调用插件/技能。

### 已收录技能

- `code-comment-standard`：代码注释生成与规范化标准。
- `project-docs-bootstrap`：项目文档初始化、重组与文档契约维护流程。
- `pyproject-standard`：标准 `pyproject.toml` 配置生成与检查。
- `zotero-tag-classifier`：Zotero 文献库标签优先分类、Collections 迁移与论文标签建议。

### 已收录规则

- `codex-user-global-rules`：Codex 用户全局规则备份，用于个人迁移和版本留档。

## 目录结构

```
├── skills/                # 技能目录                                  
│   ├── code-comment-standard/  # 代码注释标准技能                     
│   ├── project-docs-bootstrap/ # 项目文档初始化与重组技能
│   ├── pyproject-standard/     # 标准pyproject.toml配置技能           
│   └── zotero-tag-classifier/  # Zotero文献标签分类技能               
├── rules/                 # 规则目录与个人全局规则备份
│   └── codex-user-global-rules.md # Codex用户全局规则备份
├── .agents/               # Codex通用代理配置                         
│   └── plugins/marketplace.json  # Codex插件市场索引                  
├── .claude-plugin/        # Claude Code插件适配层                     
├── .codex-plugin/         # Codex插件清单                             
├── docs/                  # 项目文档                                  
├── .gitignore             # Git忽略文件                               
├── CLAUDE.md              # Claude Code Guidelines                    
├── AGENTS.md              # Codex Guidelines                          
├── LICENSE                # 许可证文件                                
└── README.md              # 仓库说明文件
```

## 贡献

欢迎添加新的技能或改进现有内容。贡献时请保持以下边界：

- 技能结构：`skills/<skill-name>/SKILL.md`
- 可复用规则结构：`rules/<rule-name>.md`
- 可复用规则文件建议不超过 1000 字符
- 通用技能和可复用规则不得绑定特定 AI 助手或 IDE 平台
- 个人全局规则备份可以放在 `rules/`，但文件名和开头说明必须明确标注备份用途，避免被误认为通用规则
- Claude Code 专属配置放在 `.claude-plugin/`
- Codex 专属配置放在 `.codex-plugin/` 和 `.agents/plugins/marketplace.json`
