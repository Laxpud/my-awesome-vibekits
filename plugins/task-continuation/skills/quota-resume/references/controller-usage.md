# 续跑控制器安装与运维

配套实现位于 [`../scripts/quota_resume.py`](../scripts/quota_resume.py)。本页只讲安装、启用、观测、停止与回滚。

## 一次性安装

```bash
# 1. 私有配置与状态目录
mkdir -p ~/.config/quota-resume/tasks ~/.local/state/quota-resume

# 2. 安装模板单元
#    模板按仓库位于 ~/workspace 书写；若在别处，先替换单元里的
#    ExecStart 与 Documentation 路径再复制。
cp <repo>/plugins/task-continuation/skills/quota-resume/scripts/units/quota-resume@.service ~/.config/systemd/user/
cp <repo>/plugins/task-continuation/skills/quota-resume/scripts/units/quota-resume@.timer   ~/.config/systemd/user/
systemctl --user daemon-reload
systemd-analyze --user verify ~/.config/systemd/user/quota-resume@.service

# 3. 若额度查询需要代理，写入用户私有文件（无需代理可跳过）
cat > ~/.config/quota-resume/proxy.env <<'EOF'
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
ALL_PROXY=socks5://127.0.0.1:7890
EOF
```

## 新增一个任务

1. 写续跑指令：`~/.config/quota-resume/tasks/<task>.md`。
   内容要包含剩余目标、允许动作、可核对的完成证据、停止条件，并要求先核对现场产物。
2. 写任务配置：`~/.config/quota-resume/tasks/<task>.json`，字段含义见
   [`controller-design.md`](controller-design.md#任务配置)。
3. 先静态校验：

```bash
python3 <repo>/plugins/task-continuation/skills/quota-resume/scripts/quota_resume.py \
  --check --config ~/.config/quota-resume/tasks/<task>.json
```

检查输出里的工作目录、rollout、额度判定与「下次检查」时间是否符合预期。

4. 启用：

```bash
systemctl --user enable --now 'quota-resume@<task>.timer'
```

一个目标任务只应有一个投递续跑消息的调度器；修复既有任务时先停用旧的。

## 观测

```bash
# 单元状态与下次唤醒
systemctl --user status    'quota-resume@<task>.timer' --no-pager
systemctl --user list-timers 'quota-resume@*' --all --no-pager

# 单次运行结果
systemctl --user status    'quota-resume@<task>.service' --no-pager
journalctl --user -u 'quota-resume@<task>.service' --no-pager | tail -30

# 控制器状态与事件流
cat ~/.local/state/quota-resume/<task>/state.json
tail -20 ~/.local/state/quota-resume/<task>/events.jsonl

# 不产生副作用的状态查询
python3 <repo>/plugins/task-continuation/skills/quota-resume/scripts/quota_resume.py \
  --status --config ~/.config/quota-resume/tasks/<task>.json
```

汇报时区分四种结果：**配置通过**（`--check` 通过）、**已入队**（`queued`）、
**已执行**（出现匹配轮次）、**任务完成**（完成证据落盘）。
service 退出码为 0 或命中锁保护都不等于续跑成功。

## 停止与回滚

```bash
# 用户主动停止：先写终态再停用调度
systemctl --user disable --now 'quota-resume@<task>.timer'

# 查看是否仍在运行
systemctl --user is-active 'quota-resume@<task>.timer'
```

- 终态（`completed` / `needs_attention` / `stopped`）会持久保留，重启或重载单元都不清除；
  误触发的 service 遇到终态会安全退出。
- 恢复一个已到终态的任务：先核对目标与理由，再显式修改状态文件，
  不要用「删除状态文件」当常规重试手段——那会丢掉回执记录。
- 回滚到旧调度：停用新单元并恢复备份的旧单元，保留本次 `events.jsonl`，
  说明旧配置恢复后是否仍保持停用。

## 机器休眠与注销

- 用户级单元默认随登录会话结束而停止。若需要注销后仍运行，先确认
  `loginctl show-user <user> -p Linger` 的状态，仅在确有需要且已授权时调整。
- 休眠或关机期间不执行；唤醒后 timer 的 `Persistent=true` 会补触发一次，
  控制器再按 `nextCheckAt` 决定是否行动。
