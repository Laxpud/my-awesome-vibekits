---
name: project-docs-guidance
description: Use only when explicitly requested to create, review, or refine AGENTS.md and its CLAUDE.md symlink or scoped repository guidance.
disable-model-invocation: true
---

# 项目工作规则

仅在用户显式调用本技能时使用。读取[共同写作约定](references/common/writing-style.md)和[指导文件约定与模板](references/project-guidance.md)。

只读本次范围内生效的父级与局部指导、相关权威来源以及受影响入口，不因改一条规则扫描所有代码或所有子目录规则。

保留真实项目事实、安全边界、团队规范和仍适用的用户偏好；不要因为具体或属于个人要求就删除。把重复事实改为带触发条件的阅读路由，缺少证据不宣称旧要求已过时。

以 AGENTS.md 为唯一正文，CLAUDE.md 使用相对软链。已有独立内容先合并仍有效的独有规则，再替换，不能丢失约定。目录级规则只有真正独立约束时才创建。

检查本次改动的规则是否可定位、引用是否存在、软链是否指向正确 AGENTS 且无循环。不因此安排其他客户端运行验证，不修改用户全局配置，不额外产规则审计报告。
