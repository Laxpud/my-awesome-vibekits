# Vibekits

实用技能（skills）和规则（rules）集合，用于管理和分享各种实用工具和功能。

## 目录结构

```
├── skills/                # 技能目录                                  
│   ├── code-comment-standard/  # 代码注释标准技能                     
│   ├── pyproject-standard/     # 标准pyproject.toml配置技能           
│   └── zotero-tag-classifier/  # Zotero文献标签分类技能               
├── rules/                 # 规则目录                                  
│   └── code-comment-standard.md  # 代码注释标准规则                   
├── .claude-plugin/        # Claude Code插件适配层                     
├── .codex-plugin/         # Codex插件适配层                           
├── docs/                  # 项目文档                                  
├── .gitignore             # Git忽略文件                               
├── CLAUDE.md              # Claude Code Guidelines                    
├── AGENTS.md              # Codex Guidelines                          
├── LICENSE                # 许可证文件                                
└── README.md              # 仓库说明文件
```

## 如何使用

### 通用方式
1. 克隆仓库到本地
2. 浏览 `skills` 或 `rules` 目录查看可用内容
3. 按照各目录中的说明文件使用

### Claude Code 插件使用
本项目已内置 Claude Code 插件支持，开箱即用：

**全局安装（推荐）**：
通过 Claude Code 插件市场安装，可在所有项目中使用：

```bash
# 添加插件市场
/plugin marketplace add https://github.com/Laxpud/my-awesome-vibekits

# 安装插件
/plugin install laxpud-vibekits@laxpud-vibekits-dev
```

### Codex 插件使用
本项目同时提供 Codex 插件适配层，配置位于 `.codex-plugin/plugin.json`，指向通用 `skills/` 目录。
通用技能内容仍保持平台无关，Codex 专属元数据仅放在 `.codex-plugin/` 中。

### 已收录技能
- `code-comment-standard`：代码注释生成与规范化标准。
- `pyproject-standard`：标准 `pyproject.toml` 配置生成与检查。
- `zotero-tag-classifier`：Zotero 文献库标签优先分类、Collections 迁移与论文标签建议。

## 贡献

欢迎添加新的技能或改进现有内容，提交Pull Request即可。
