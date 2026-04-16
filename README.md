# Vibekits

实用技能（skills）和规则（rules）集合，用于管理和分享各种实用工具和功能。

## 目录结构

```
├── skills/                # 技能目录
│   ├── code-comment-standard/  # 代码注释标准技能
│   └── pyproject-standard/     # 标准pyproject.toml配置技能
├── rules/                 # 规则目录
│   └── code-comment-standard/  # 代码注释标准规则
├── .gitignore             # Git忽略文件
├── AGENTS.md              # Agent指南
└── README.md              # 仓库说明文件
```

## 如何使用

### 通用方式
1. 克隆仓库到本地
2. 浏览 `skills` 或 `rules` 目录查看可用内容
3. 按照各目录中的说明文件使用

### Claude Code 插件使用
本项目已内置 Claude Code 插件支持，开箱即用：

1. **技能调用方式**：
   ```bash
   # 使用代码注释标准化技能
   /skill code-comment-standard
   
   # 使用PyProject配置标准化技能
   /skill pyproject-standard
   ```

2. **全局安装（推荐）**：
   通过 Claude Code 插件市场安装，可在所有项目中使用：
   ```bash
   # 添加插件市场
   /plugin marketplace add Laxpud/my-awesome-vibekits
   
   # 安装插件
   /plugin install my-awesome-vibekits@my-awesome-vibekits
   ```

3. **单项目使用**：
   直接将 CLAUDE.md 下载到你的项目根目录即可使用规则：
   ```bash
   # 新项目
   curl -o CLAUDE.md https://raw.githubusercontent.com/Laxpud/my-awesome-vibekits/main/CLAUDE.md
   
   # 现有项目（追加内容）
   echo "" >> CLAUDE.md
   curl https://raw.githubusercontent.com/Laxpud/my-awesome-vibekits/main/CLAUDE.md >> CLAUDE.md
   ```

## 贡献

欢迎添加新的技能或改进现有内容，提交Pull Request即可。