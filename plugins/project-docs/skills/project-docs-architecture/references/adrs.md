# Architecture Decision Records

## 创建门槛

只有以下三个条件同时成立才创建 ADR：

1. **难以逆转**：以后改变会产生有意义的迁移或协调成本。
2. **缺少背景会令人意外**：未来读者很可能误以为当前选择是错误或偶然的。
3. **存在真实取舍**：曾有合理替代方案，并因具体理由选择了当前方案。

常见候选包括系统形态、上下文集成方式、带锁定成本的基础设施、所有权边界、非显然的偏离和代码中不可见的约束。普通库选择、容易撤回的偏好和唯一显然方案不创建 ADR。

## 路径与编号

沿用仓库现有清晰 ADR 约定；没有约定时：

- 首个 ADR 出现时才创建 `docs/adr/`；
- 文件名使用连续编号 `0001-short-slug.md`；
- 扫描现有最高编号后递增，不复用已经删除的编号。

## 默认格式

```markdown
# <简短决定标题>

<一至三句说明背景、决定和选择原因。>
```

只有确实增加信息时才添加：

- `Status`：`proposed`、`accepted`、`deprecated` 或 `superseded by ADR-NNNN`；
- Considered Options：被拒替代值得未来读者记住时；
- Consequences：非显然下游影响需要醒目标识时。

## 生命周期

- Proposed ADR 可以随讨论更新。
- Accepted ADR 保留当时语义，只修正明显错误或更新状态。
- 决定改变时创建新 ADR，并把旧 ADR 标记为 deprecated 或 superseded；新旧记录互相链接。
- Current architecture 文档更新为当前事实，不通过改写旧 ADR 伪造一致历史。
