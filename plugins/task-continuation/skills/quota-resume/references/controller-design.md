# 续跑控制器设计

这是 [`../SKILL.md`](../SKILL.md) 的可执行配套实现。技能负责契约与判断，本实现负责
**已经写好、不需要每次重新生成**的调度机制：新增一个任务只需写一份 JSON 配置和一份
续跑指令，不再需要模型现场设计调度器。

安装、启用、停止命令见 [`controller-usage.md`](controller-usage.md)。

## 组成

| 文件 | 作用 |
| --- | --- |
| [`../scripts/quota_resume.py`](../scripts/quota_resume.py) | 参数化控制器：额度门、投递、回执跟踪、状态机、通知 |
| [`../scripts/units/quota-resume@.service`](../scripts/units/quota-resume@.service) | 模板 service，`%i` 为任务名 |
| [`../scripts/units/quota-resume@.timer`](../scripts/units/quota-resume@.timer) | 模板 timer，每分钟轻量唤醒 |

控制器只依赖 Python 标准库和目标环境的 `codex` 可执行文件，不导入技能外的仓库代码。

## 设计要点（对应技能契约）

- **额度判定**：只有 `ordinaryUsageAllowed` 明确为 `true` 才算有额度；`null` 或缺失保持未知。
  查询失败记 `retry_wait`，与「没有额度」区分开。
- **等待时长**：只用后端给出的 `resetsAt` 安排复查，并用 `usedPercent >= 100` 判断
  **哪个窗口真的耗尽**。未耗尽窗口的重置时间不会推迟检查——否则 5 小时窗口会被
  周窗口的重置时间掩盖，白等一周。
- **入队不等于执行**：`queued` 状态等待匹配轮次出现在 rollout 中，超期转入
  `needs_attention`，不重复入队。
- **轮次结束不等于任务完成**：由配置的完成/停止标记判定，完成证据落盘后才停。
- **终态持久**：`completed` / `needs_attention` / `stopped` 写入状态文件，重启或重载单元都不会清除。
- **无需模型推理**：等待、查询、回执跟踪、通知全部在控制器内完成；只有续跑消息本身消耗额度。

## 状态机

```
waiting_quota ──额度允许且线程空闲、间隔满足──> queued ──匹配轮次出现──> running ──证据──> completed
      ^                       │                        │
      │                       └──超期未消费──> needs_attention
      └────── 查询失败 retry_wait ──────┘        running ──继续可执行──> waiting_quota
```

状态文件字段：`status`、`nextCheckAt`、`lastQuota`、`queuedSubmissionId`、`queuedAt`、
`consumeDeadline`、`turnCompletedAt`、`lastMessage`、`lastError`。
事件流追加写入同目录 `events.jsonl`。

## 任务配置

放在 `~/.config/quota-resume/tasks/<task>.json`（私有数据，不入库）：

```json
{
  "name": "my-task",
  "pollSeconds": 300,
  "minSecondsBetweenDeliveries": 900,
  "target": {
    "threadId": "<目标线程 UUID>",
    "threadName": "会话显示名（仅记录用）",
    "cwd": "<目标任务的工作目录>"
  },
  "delivery": {
    "codexBin": "/path/to/codex",
    "messageFile": "<续跑指令 Markdown 绝对路径>",
    "approvalsReviewer": "auto_review",
    "extraArgs": ["--approve-for-me"]
  },
  "quota": {
    "allowance": "natural",
    "marginSeconds": 120,
    "maxResetCredits": 0,
    "resetCreditAuthorized": false
  },
  "autoStopOnTerminal": true,
  "timerUnit": "quota-resume@<task>.timer",
  "completion": {
    "markers": ["任务完成，停止定时续跑。"],
    "resumeOnlyOnQuotaLimit": true,
    "maxRoundsWithoutProgress": 3
  },
  "notify": { "command": ["notify-send", "--app-name", "quota-resume"] }
}
```

- `allowance`：`natural` 只等自然恢复；`reset_credit` 才允许消耗已有的重置卡，
  且必须同时给出 `resetCreditAuthorized: true` 与 `maxResetCredits` 上限。
  购买额度、充值、切换计费路径不在授权范围内。
- `autoStopOnTerminal`（默认 true）+ `timerUnit`：到达终态后停止 timer，避免它
  每分钟唤醒、每分钟写一条事件的永久空转。只 `stop` timer 而不 `--now` 停整个
  单元——服务此刻正在运行，停整个单元会连带终止当前进程、使本次结果无法落盘。
  停止后写 `.timer_stopped` 标记，后续运行直接安静退出，不重复记录。
- 消息文件里用 `{sentinel}` 占位符，投递时替换为 `completion.markers[0]`。
  哨兵同时出现在「投递文本」和「停止判据」两处，占位符保证它们只有一个来源，
  不会各写一份而漂移。哨兵只匹配执行端的 `last_agent_message`，不匹配用户消息，
  因此把哨兵句子放进续跑消息本身不会自触发。
- `completion.markers` 用作**停止哨兵**：续跑指令要求执行端在任务收工时原样写出
  该短语（例如「任务完成，停止定时续跑。」）。哨兵是刻意约定的固定字符串，不是
  对自然语言的猜测，判定优先级最高。局限：该短语若被引用（含否定语境）也会命中，
  因此要选一个不会在别处出现的句子，并只在完成时要求输出。
- `completion.resumeOnlyOnQuotaLimit`：为 `true` 时按**停止原因**决定是否继续——
  只有该轮因额度打满而停，才在额度恢复后注入续跑消息；任务自然完成、用户取消、
  报错结束时直接转 `completed` 并停止调度。判定依据是 rollout 里的额度事实
  （`primary.usedPercent >= 100` 或 `rateLimitReachedType`），**不是对话文本**，
  因此对 `last_agent_message` 为空的 `task_complete` 同样有效。
- **rollout 解析以状态索引为准**：会话继续时 `state_5.sqlite` 的 `rollout_path`
  会指向新的 `_<id>` 分段，而配置里的静态路径就此冻结、不再增长。若读旧分段，
  控制器会永远看不到进展（已实测踩过），因此不要依赖 `target.rolloutPath`。
- `completion.markers` 命中续跑指令约定的完成证据才记 `completed`；
  `stopMarkers` 命中则记 `stopped`。两者都不命中时继续下一轮，但受
  `maxRoundsWithoutProgress` 限制：连续若干轮拿不到约定证据就转入
  `needs_attention` 并通知，避免一个持续返回同样结果的任务每轮重复投递、白烧额度。
- `delivery.extraArgs` 里 **`--approve-for-me` 与 `--sandbox` 互斥**：前者本身已隐含
  `workspace-write` 沙箱，两个一起传会被 CLI 以参数冲突拒绝（`cannot be used with`）。
  只写 `--approve-for-me` 即可；确需自定义沙箱时改用 `--sandbox`，不要同时给。
- `minSecondsBetweenDeliveries`（默认 900 秒）是两次投递之间的最小间隔。
  一轮结束但没拿到完成证据时状态会回到 `waiting_quota`；若额度一直可用又不限制
  间隔，就会每个 `pollSeconds` 都催一次同一会话。投递前的两道闸是：**线程正在
  执行**（`task_started` 之后无终态）或**距上次投递过近**，都只跟踪、不追加消息。
- `notify.command` 可为空数组，表示只写事件日志不弹通知。

## 命令

```bash
python3 quota_resume.py --check  --config <task.json>   # 静态校验 + 额度查询，不入队
python3 quota_resume.py --cycle  --config <task.json>   # 一个调度周期（systemd 调用）
python3 quota_resume.py --status --config <task.json>   # 打印状态
```

`--check` 不投递消息、不消耗额度，适合在启用前和排障时使用。

## 环境依赖

- **代理**：额度查询访问 `chatgpt.com` 后端。systemd 不继承交互式 shell 的代理变量，
  缺少代理时额度查询会以 `-32603` 失败（`error sending request for url .../wham/usage`）。
- **`codex queue`**：投递依赖该子命令。接口按目标环境安装版本核对，不假定其它版本提供相同参数。
- **宿主消费**：`queue` 只把消息排进队列，需要目标线程的宿主（客户端或受控加载）消费它。
  未消费时控制器在 `consumeDeadline` 后转 `needs_attention` 并通知，不会无限等待。
- **bwrap**：目标环境若无法创建非特权用户命名空间，codex 的沙箱命令会告警；
  这与本控制器无关（控制器自身不需要沙箱），不影响 `queue` 投递。
