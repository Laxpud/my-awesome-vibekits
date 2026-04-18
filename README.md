# Vibekits

实用技能（skills）和规则（rules）集合，用于管理和分享各种实用工具和功能。

## 目录结构

```
├── skills/                # 技能目录                                  
│   ├── code-comment-standard/  # 代码注释标准技能                     
│   └── pyproject-standard/     # 标准pyproject.toml配置技能           
├── rules/                 # 规则目录                                  
│   └── code-comment-standard.md  # 代码注释标准规则                   
├── .claude-plugin/        # Claude Code插件适配层                     
├── docs/                  # 项目文档                                  
├── .gitignore             # Git忽略文件                               
├── CLAUDE.md              # Claude Code Guidelines                    
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

## 贡献

欢迎添加新的技能或改进现有内容，提交Pull Request即可。