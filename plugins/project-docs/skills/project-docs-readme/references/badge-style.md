# Orbit 徽章规范

创建或调整 README 顶部徽章时读取。保持统一视觉风格，徽章内容和素材按项目需要选择。开头结构见 [README 模板](../assets/readme-template.md)。

## 视觉基线

采用极光紫单区块胶囊，图标与文字共享连续底色。文字统一使用主题紫色，图标兼顾品牌辨识度与整体协调性。

| 项目 | 默认值 |
| --- | --- |
| 高度、圆角、边框 | 32px、完全圆角、1px 实线 |
| 左右内边距、图文间距 | 左右各 12px、间距 5px |
| 字体 | Inter，目标字重 500，12px；文字行框 16px |
| 图标 | 默认 15px，统一上移 0.75px |

| 颜色用途 | 浅色主题 | 深色主题 |
| --- | --- | --- |
| 胶囊底色 | `#F3EDFC` | `#2B223A` |
| 边框 | `#D7C7ED` | `#58446D` |
| 文字 | `#59416F` | `#E5D8FA` |
| 通用图标 | `#7548A3` | `#CFADFF` |

## 素材与品牌色

按 [README 约定](readme-contract.md)确认由用户提供素材、AI 寻找，或不添加徽章。AI 寻找时以 [Iconify](https://icon-sets.iconify.design/)为统一入口，根据语义、品牌识别、视觉协调性和使用条件选择合适资源，不预设图标集优先级。用户提供的素材优先尊重其意图，适配方式按实际服务能力判断。

品牌图标应考虑品牌色彩，可采用资源自带的合适配色，也可依据品牌资料设置颜色；通用图标默认使用主题紫色。具体图形、颜色和来源由项目决定，不将某次设计选择固化为通用规则。

Iconify 的 [SVG API](https://iconify.design/docs/api/svg.html)通过 `color` 替换 `currentColor`；固定配色图标可以保留自带颜色。[集合元数据](https://iconify.design/docs/types/iconify-info.html)中的 `palette` 表示是否使用固定颜色，不是品牌色值表。目前查阅的官方 API 文档未提供专门的品牌主题色查询接口；需要确认品牌色时可参考原资源或官方品牌资料。

需要查找资源或确认服务能力时，按需查阅 [Iconify API 文档](https://iconify.design/docs/api/)，不要求固定检索步骤。

## 统一 URL 模板

直接复用 [Badgewind](https://github.com/agmmnn/badgewind) 在线 URL，替换文字、图标、颜色及目标链接。日常应用不逐枚渲染、微调或导出本地图片。

以下依次为浅色、深色模板：

```text
https://badgewind.agmmnn.workers.dev/TEXT?font=inter&textShadow=false&badgeStyle=h-(32px),rounded-full,border,border-solid,border-(@D7C7ED),bg-(@F3EDFC),text-(@59416F)&leftStyle=h-full,bg-transparent,rounded-full,px-3,py-0,text-(12px),leading-(16px),font-medium&icon=ICON_ID&iconStyle=w-(15px),h-(15px),mr-(5px),-translate-y-(0.75px),text-(@ICON_COLOR)

https://badgewind.agmmnn.workers.dev/TEXT?font=inter&textShadow=false&badgeStyle=h-(32px),rounded-full,border,border-solid,border-(@58446D),bg-(@2B223A),text-(@E5D8FA)&leftStyle=h-full,bg-transparent,rounded-full,px-3,py-0,text-(12px),leading-(16px),font-medium&icon=ICON_ID&iconStyle=w-(15px),h-(15px),mr-(5px),-translate-y-(0.75px),text-(@ICON_COLOR)
```

`TEXT` 为单段文字，空格写 `_`，连字符写 `--`；`ICON_ID` 使用 Iconify 的 `集合:名称`；`ICON_COLOR` 为不带 `#` 的色值。图标自带固定配色时，颜色参数可能不影响这些颜色。HTML 属性中的 `&` 写为 `&amp;`，主题切换方式见 [README 模板](../assets/readme-template.md)。

在线服务的实际字体与显示能力可能与设计基线有差异；`font-medium` 不保证服务加载真实 Inter 500。核实改动的字段、链接与双语一致性，无法确认的在线效果如实说明。动态状态徽章保留真实数据来源。
