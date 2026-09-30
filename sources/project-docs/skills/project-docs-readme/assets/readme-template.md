# README 模板

以下展示根 README 的结构，说明文字以中文占位；新项目默认根页输出英文，正式中文页位于 `docs/README.cn.md`。替换全部占位信息和相对路径，删除无内容的可选部分。徽章按 [Orbit 徽章规范](../references/badge-style.md)复用统一 URL 模板，只替换文字、图标、品牌色与目标链接；示例 MIT 仅展示许可证入口，不替项目选择许可证，图片直接引用 Badgewind 在线地址。

```markdown
<a id="readme-top"></a>

<!-- 1. 多语言项目保留切换；当前语言加粗，单语言项目省略整块。 -->
<div align="right">
  <strong>English</strong> | <a href="docs/README.cn.md">简体中文</a>
</div>

<div align="center">

<!-- 2. 可选：项目已有图标；项目名仅使用一个一级标题。 -->
<h1>项目名称</h1>

<p><strong>一句话说明帮助谁完成什么事。</strong><br />
<sub>可选：补充项目特点或个性的简短副标题。</sub></p>

<!-- 3. 可选：按用户提供或 AI 查找的 Iconify ID 替换模板字段；用户不要徽章时删除整块，不生成本地文件。 -->
<p>
  <a href="LICENSE">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://badgewind.agmmnn.workers.dev/MIT_License?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px),rounded-full,border,border-solid,border-(@58446D),bg-(@2B223A),text-(@E5D8FA)&amp;leftStyle=h-full,bg-transparent,rounded-full,px-3,py-0,text-(12px),leading-(16px),font-medium&amp;icon=material-symbols:balance&amp;iconStyle=w-(15px),h-(15px),mr-(5px),-translate-y-(0.75px),text-(@CFADFF)" />
      <img height="32" src="https://badgewind.agmmnn.workers.dev/MIT_License?font=inter&amp;textShadow=false&amp;badgeStyle=h-(32px),rounded-full,border,border-solid,border-(@D7C7ED),bg-(@F3EDFC),text-(@59416F)&amp;leftStyle=h-full,bg-transparent,rounded-full,px-3,py-0,text-(12px),leading-(16px),font-medium&amp;icon=material-symbols:balance&amp;iconStyle=w-(15px),h-(15px),mr-(5px),-translate-y-(0.75px),text-(@7548A3)" alt="License: MIT" />
    </picture>
  </a>
</p>

<!-- 4. 可选：替换为有助于理解项目的真实预览图；没有就删除整块。 -->
<a href="docs/images/preview.png">
  <img src="docs/images/preview.png" alt="项目效果预览" width="92%" />
</a>

<!-- 5. 可选：只保留真实可用的官网、文档、演示或讨论入口。 -->
<p><sub><a href="docs/usage.md">Documentation</a></sub></p>

</div>

## 适合做什么

真实能力、典型用途及必要限制。

## 环境准备

使用推荐方式所需的工具和条件；适合时链接官方获取入口。

## 快速开始

按本项目实际提供一个推荐路径，写清操作位置、必要输入和可观察结果。

## 接下来怎么用

说明常用下一步，较复杂操作见[使用说明][usage]。

## 常见问题

只保留首次使用常见阻碍，没有则省略。

## 更多文档

链接用户需要的使用说明和项目进展。

## 参与贡献

如果现有功能还不能满足你的需求，欢迎提出使用场景，
也欢迎一起维护这个项目、提交代码或改进文档。

提供真实反馈入口和开发者[技术文档][tech]。

[usage]: docs/usage.md
[tech]: docs/tech/index.md
```

中文页的切换区使用：

```html
<div align="right">
  <a href="../README.md">English</a> | <strong>简体中文</strong>
</div>
```

同一组在线徽章 URL 由两种语言共用，无需按 README 所在目录改写；本地链接与可选预览图仍需调整相对路径，例如 `../LICENSE`、`../docs/images/preview.png`。图片替代文字与页面语言一致。无需副标题时一并删除 `<br />` 和 `<sub>`，无需预览或快捷链接时删除整个可选块，不保留空容器或占位路径。徽章不在末尾重复。
