#!/usr/bin/env python3
"""额度恢复续跑控制器：参数化实现，按任务配置驱动。

设计契约（详见 ../skills/quota-resume/SKILL.md）：
- 额度查询、等待、回执跟踪、通知都不需要模型推理；只有续跑消息本身会消耗额度。
- 入队只证明 queued；只有匹配轮次真正执行后才记 running。
- 轮次结束不等于任务完成；完成由事先约定的证据判定。
- 终态持久保留，进程重启或单元重载都不清除。

任务配置、状态与日志都属于当前用户私有数据，由调用方通过命令行传入，
不写死在控制器里。本文件不包含任何个人路径或线程 ID。

用法：
    quota_resume.py --check   --config <task.json>      # 只做静态校验与额度查询，不入队
    quota_resume.py --cycle   --config <task.json>      # 执行一个调度周期
    quota_resume.py --status  --config <task.json>      # 打印当前状态
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

STATE_VERSION = 1
DEFAULT_MARGIN_SECONDS = 120
DEFAULT_POLL_SECONDS = 300
# 两次投递之间的最小间隔：防止一轮结束却无完成证据时反复催促同一会话。
DEFAULT_MIN_DELIVERY_GAP_SECONDS = 900
WAITING_RECHECK_SECONDS = 600
QUEUE_CONSUME_DEADLINE_SECONDS = 6 * 3600

# 状态机取值，与技能契约一一对应。
WAITING_QUOTA = "waiting_quota"
QUEUED = "queued"
RUNNING = "running"
RETRY_WAIT = "retry_wait"
COMPLETED = "completed"
NEEDS_ATTENTION = "needs_attention"
STOPPED = "stopped"

TERMINAL_STATES = {COMPLETED, NEEDS_ATTENTION, STOPPED}


class ConfigError(RuntimeError):
    """任务配置不完整或不可用。"""


# --------------------------------------------------------------------------
# 配置
# --------------------------------------------------------------------------


@dataclass
class TaskConfig:
    raw: dict
    path: Path
    name: str
    state_dir: Path
    log_dir: Path

    # 目标身份
    thread_id: str
    thread_name: str
    cwd: Path
    rollout_path: Path | None

    # 执行宿主
    codex_bin: str
    message_file: Path
    extra_queue_args: list[str] = field(default_factory=list)

    # 额度与调度
    margin_seconds: int = DEFAULT_MARGIN_SECONDS
    poll_seconds: int = DEFAULT_POLL_SECONDS
    min_seconds_between_deliveries: int = DEFAULT_MIN_DELIVERY_GAP_SECONDS
    allowance: str = "natural"  # natural | reset_credit
    max_reset_credits: int = 0
    reset_credit_authorized: bool = False

    # 完成判定
    completion_markers: list[str] = field(default_factory=list)
    stop_markers: list[str] = field(default_factory=list)
    max_rounds_without_progress: int = 3

    # 通知
    notify_command: list[str] = field(default_factory=list)

    # 参数化额外 turn 设置（camelCase，直接透传给协议）
    approvals_reviewer: str = "auto_review"

    def summary(self) -> str:
        return f"{self.name} (thread {self.thread_id})"


def _require(raw: dict, key: str, cfg_path: Path):
    if key not in raw:
        raise ConfigError(f"{cfg_path}: 缺少必填字段 `{key}`")
    return raw[key]


def load_config(cfg_path: Path) -> TaskConfig:
    if not cfg_path.is_file():
        raise ConfigError(f"任务配置不存在: {cfg_path}")
    try:
        raw = json.loads(cfg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"{cfg_path}: JSON 解析失败: {exc}") from exc

    target = raw.get("target") or {}
    delivery = raw.get("delivery") or {}
    quota = raw.get("quota") or {}
    completion = raw.get("completion") or {}
    notify = raw.get("notify") or {}

    thread_id = str(_require(target, "threadId", cfg_path))
    if not re.fullmatch(r"[0-9a-fA-F-]{16,64}", thread_id):
        raise ConfigError(f"{cfg_path}: target.threadId 不是合法的线程 ID: {thread_id!r}")

    state_dir = Path(raw.get("stateDir") or (Path.home() / ".local/state/quota-resume" / str(raw.get("name") or thread_id)))
    log_dir = Path(raw.get("logDir") or state_dir / "logs")

    message_file = Path(_require(delivery, "messageFile", cfg_path))
    if not message_file.is_file():
        raise ConfigError(f"{cfg_path}: delivery.messageFile 不存在: {message_file}")

    rollout = target.get("rolloutPath")
    return TaskConfig(
        raw=raw,
        path=cfg_path,
        name=str(raw.get("name") or thread_id[:8]),
        state_dir=state_dir,
        log_dir=log_dir,
        thread_id=thread_id,
        thread_name=str(target.get("threadName") or ""),
        cwd=Path(_require(target, "cwd", cfg_path)),
        rollout_path=Path(rollout) if rollout else None,
        codex_bin=str(delivery.get("codexBin") or "codex"),
        message_file=message_file,
        extra_queue_args=[str(a) for a in (delivery.get("extraArgs") or [])],
        margin_seconds=int(quota.get("marginSeconds", DEFAULT_MARGIN_SECONDS)),
        poll_seconds=int(raw.get("pollSeconds", DEFAULT_POLL_SECONDS)),
        min_seconds_between_deliveries=int(raw.get("minSecondsBetweenDeliveries", DEFAULT_MIN_DELIVERY_GAP_SECONDS)),
        allowance=str(quota.get("allowance") or "natural"),
        max_reset_credits=int(quota.get("maxResetCredits", 0)),
        reset_credit_authorized=bool(quota.get("resetCreditAuthorized", False)),
        completion_markers=[str(m) for m in (completion.get("markers") or [])],
        stop_markers=[str(m) for m in (completion.get("stopMarkers") or [])],
        max_rounds_without_progress=int(completion.get("maxRoundsWithoutProgress", 3)),
        notify_command=[str(c) for c in (notify.get("command") or [])],
        approvals_reviewer=str(delivery.get("approvalsReviewer") or "auto_review"),
    )


# --------------------------------------------------------------------------
# 状态：同目录临时文件 + 原子替换
# --------------------------------------------------------------------------


def state_path(cfg: TaskConfig) -> Path:
    return cfg.state_dir / "state.json"


def load_state(cfg: TaskConfig) -> dict:
    p = state_path(cfg)
    if not p.is_file():
        return {}
    try:
        state = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        # 状态损坏不能当成新任务：宁可报错，也不覆盖已有回执。
        raise ConfigError(f"状态文件损坏，需人工检查: {p}")
    if state.get("threadId") and state["threadId"] != cfg.thread_id:
        raise ConfigError(
            f"状态文件属于其它线程 ({state['threadId']})，拒绝复用: {p}"
        )
    return state


def save_state(cfg: TaskConfig, state: dict) -> None:
    cfg.state_dir.mkdir(parents=True, exist_ok=True)
    state["stateVersion"] = STATE_VERSION
    state["threadId"] = cfg.thread_id
    state["updatedAt"] = int(time.time())
    tmp = state_path(cfg).with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, state_path(cfg))


def log_event(cfg: TaskConfig, event: str, **fields) -> None:
    cfg.state_dir.mkdir(parents=True, exist_ok=True)
    record = {"ts": int(time.time()), "event": event, **fields}
    line = json.dumps(record, ensure_ascii=False, sort_keys=True)
    with (cfg.state_dir / "events.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    print(line, flush=True)


# --------------------------------------------------------------------------
# 额度
# --------------------------------------------------------------------------


def read_usage(cfg: TaskConfig, timeout: float = 45.0) -> dict:
    """通过官方 stdio 通道读取额度；只读，不触发模型推理。"""
    proc = subprocess.Popen(
        [cfg.codex_bin, "app-server", "--stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )
    try:
        def send(obj: dict) -> None:
            assert proc.stdin is not None
            proc.stdin.write(json.dumps(obj) + "\n")
            proc.stdin.flush()

        send({"id": 1, "method": "initialize", "params": {"clientInfo": {"name": "quota_resume", "version": "1"}}})
        send({"method": "initialized"})
        send({"id": 2, "method": "account/rateLimits/read", "params": {"excludeResetCreditDetails": True}})

        deadline = time.monotonic() + timeout
        assert proc.stdout is not None
        while time.monotonic() < deadline:
            line = proc.stdout.readline()
            if not line:
                raise RuntimeError("app-server 关闭了连接")
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if msg.get("id") != 2:
                continue
            if "error" in msg:
                raise RuntimeError(f"account/rateLimits/read 失败: {msg['error']}")
            return msg["result"]
        raise TimeoutError("额度查询超时")
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=10)
        except Exception:
            proc.kill()


def _window(limits: dict, key: str) -> dict:
    return limits.get(key) or {}


def evaluate_quota(usage: dict, unwrap: bool = True) -> dict:
    """把额度响应归一化成可判定结果。

    只有 ordinaryUsageAllowed 为 true 才算有额度；缺失或 null 保持未知。
    """
    limits = usage.get("rateLimits") or {}
    primary = _window(limits, "primary")
    secondary = _window(limits, "secondary")
    allowed = usage.get("ordinaryUsageAllowed")
    return {
        "ordinaryUsageAllowed": allowed,
        "primaryUsedPercent": primary.get("usedPercent"),
        "primaryWindowMins": primary.get("windowDurationMins"),
        "primaryResetsAt": primary.get("resetsAt"),
        "secondaryUsedPercent": secondary.get("usedPercent"),
        "secondaryWindowMins": secondary.get("windowDurationMins"),
        "secondaryResetsAt": secondary.get("resetsAt"),
        "planType": limits.get("planType"),
        "rateLimitReachedType": limits.get("rateLimitReachedType"),
        "resetCreditsAvailable": (usage.get("rateLimitResetCredits") or {}).get("availableCount"),
    }


def next_check_after_quota(quota: dict, cfg: TaskConfig) -> int:
    """用后端给的重置时间安排下一次检查，绝不据百分比或经过时长推断已恢复。

    只有真正耗尽的窗口才决定等待时长：某个窗口 100% 时等它重置，
    其它未耗尽窗口的重置时间不能拿来推迟检查（否则 5 小时窗口会被
    周窗口的重置时间掩盖，白等一周）。多个窗口同时耗尽时，取最晚的重置。
    """
    windows = (
        (quota.get("primaryUsedPercent"), quota.get("primaryResetsAt")),
        (quota.get("secondaryUsedPercent"), quota.get("secondaryResetsAt")),
    )
    exhausted = [r for used, r in windows if r and (used or 0) >= 100]
    if exhausted:
        return int(max(exhausted)) + cfg.margin_seconds
    # 额度不允许但没有窗口报告 100%（例如被其它限制挡住）：只做有限退避复查。
    return int(time.time()) + WAITING_RECHECK_SECONDS


# --------------------------------------------------------------------------
# 目标线程与完成判定
# --------------------------------------------------------------------------


def resolve_rollout(cfg: TaskConfig) -> Path:
    if cfg.rollout_path and cfg.rollout_path.is_file():
        return cfg.rollout_path
    index = Path.home() / ".codex" / "state_5.sqlite"
    if index.is_file():
        import sqlite3

        con = sqlite3.connect(f"file:{index}?mode=ro", uri=True)
        try:
            row = con.execute(
                "select rollout_path from threads where id = ?", (cfg.thread_id,)
            ).fetchone()
        finally:
            con.close()
        if row and row[0]:
            p = Path(row[0])
            if p.is_file():
                return p
    raise ConfigError("无法解析目标线程的 rollout 路径（配置未提供且索引查询失败）")


def tail_events(rollout: Path, limit: int = 400) -> list[dict]:
    """反向读取 rollout 尾部；rollout 可达数百 MB，不回读全文。"""
    size = rollout.stat().st_size
    block = min(size, 512 * 1024)
    with rollout.open("rb") as fh:
        fh.seek(size - block)
        data = fh.read()
    lines = data.split(b"\n")
    out: list[dict] = []
    for raw in reversed(lines[-(limit + 1):]):
        if not raw.strip():
            continue
        try:
            out.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    out.reverse()
    return out


def classify_turn(events: list[dict], since_epoch: int) -> dict:
    """在 since_epoch 之后寻找轮次状态与完成/阻塞证据。

    turnRunning 表示脚本最近一次 task_started 之后没有出现终态，即该线程确实
    正在执行。投递决策必须区分「在跑」与「已跑完」：前者绝不能追加消息。
    """
    result = {"turnCompleted": False, "turnRunning": False, "userMessage": False,
              "completedAt": None, "blocker": None}
    for ev in events:
        ts = ev.get("timestamp")
        if not ts:
            continue
        epoch = int(time.mktime(time.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S"))) - time.timezone
        if epoch < since_epoch:
            continue
        payload = ev.get("payload") or {}
        ptype = payload.get("type")
        if ptype == "task_started":
            result["turnRunning"] = True
        elif ptype == "task_complete":
            result["turnCompleted"] = True
            result["turnRunning"] = False
            result["completedAt"] = epoch
            msg = payload.get("last_agent_message") or payload.get("message") or ""
            result["lastMessage"] = msg if isinstance(msg, str) else json.dumps(msg, ensure_ascii=False)
        elif ptype == "turn_aborted":
            result["turnCompleted"] = True
            result["turnRunning"] = False
            result["completedAt"] = epoch
            result["blocker"] = f"turn_aborted: {payload.get('reason')}"
        elif ptype == "message" and payload.get("role") == "user":
            result["userMessage"] = True
    return result


def match_markers(text: str, markers: list[str]) -> bool:
    return any(m and m in text for m in markers)


# --------------------------------------------------------------------------
# 投递
# --------------------------------------------------------------------------


def delivery_gate(state: dict, verdict: dict, cfg: TaskConfig, now: int) -> dict:
    """投递前的纯判定：额度已经允许时，是否真的应该现在投递。

    两条闸门都来自实测问题：
    - 线程正在执行时绝不追加消息（否则等于每轮都催一次在跑的会话）。
    - 两次投递之间保持最小间隔（否则一轮结束却无完成证据时，会在额度可用的
      情况下每个轮询周期都重复催促同一会话）。

    返回 {allow, status, nextCheckAt, event, fields}；不修改 state、不落盘。
    """
    if verdict.get("turnRunning"):
        return {
            "allow": False,
            "status": RUNNING,
            "nextCheckAt": now + cfg.poll_seconds,
            "event": "skip_while_running",
            "fields": {},
        }

    last_delivery = int(state.get("lastDeliveryAt") or 0)
    if last_delivery and now - last_delivery < cfg.min_seconds_between_deliveries:
        return {
            "allow": False,
            "status": RUNNING,
            "nextCheckAt": max(now + cfg.poll_seconds,
                               last_delivery + cfg.min_seconds_between_deliveries),
            "event": "delivery_throttled",
            "fields": {"sinceLastSec": now - last_delivery},
        }

    return {"allow": True, "status": "", "nextCheckAt": 0, "event": "", "fields": {}}


def queue_message(cfg: TaskConfig, message: str) -> tuple[int, str, str]:
    """投递续跑消息。

    必须显式给 stdin 一个确定来源：交互式环境下 `codex queue` 可以继承 TTY，
    但在 systemd 等无终端环境里继承 stdin 有挂起的风险。超时或启动失败一律
    转成返回值，绝不抛出——调用方需要拿这个结果去写状态，异常逃出去会让进程
    在写入任何回执之前死掉（实测过：state.json 完全缺失、无事件记录）。
    """
    cmd = [
        cfg.codex_bin, "queue",
        "--thread", cfg.thread_id,
        "--message", message,
        "-C", str(cfg.cwd),
        *cfg.extra_queue_args,
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(cfg.cwd),
            stdin=subprocess.DEVNULL,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return 1, "", "投递超时：codex queue 未在 120 秒内返回"
    except OSError as exc:
        return 1, "", f"投递无法启动: {exc!r}"

    out = (proc.stdout or "") + (proc.stderr or "")
    match = re.search(r"Queued message ([0-9a-fA-F-]{8,64})", out)
    return proc.returncode, (match.group(1) if match else ""), out.strip()[-500:]


# --------------------------------------------------------------------------
# 通知
# --------------------------------------------------------------------------


def notify(cfg: TaskConfig, title: str, body: str) -> None:
    log_event(cfg, "notify", title=title, body=body[:500])
    cmd = list(cfg.notify_command)
    if not cmd:
        return
    try:
        subprocess.run(cmd + [f"{title}\n{body}"], timeout=20, check=False)
    except Exception as exc:  # 通知失败不能影响调度
        log_event(cfg, "notify_failed", error=repr(exc))


# --------------------------------------------------------------------------
# 周期
# --------------------------------------------------------------------------


def cycle(cfg: TaskConfig) -> int:
    cfg.state_dir.mkdir(parents=True, exist_ok=True)
    cfg.log_dir.mkdir(parents=True, exist_ok=True)
    lock_file = (cfg.state_dir / "run.lock").open("w")
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        log_event(cfg, "skipped_busy")
        return 0

    state = load_state(cfg)
    if state.get("status") in TERMINAL_STATES:
        log_event(cfg, "terminal_state", status=state["status"])
        return 0

    now = int(time.time())
    if state.get("nextCheckAt") and now < int(state["nextCheckAt"]):
        return 0

    # 1. 有未消费的排队消息：先追踪，不重复入队。
    if state.get("status") == QUEUED:
        return track_queued(cfg, state, now)

    # 2. 额度门：读不到就退避，读不到 ≠ 没有额度。
    try:
        quota = evaluate_quota(read_usage(cfg))
    except Exception as exc:
        state.update({"status": RETRY_WAIT, "lastError": repr(exc), "nextCheckAt": now + WAITING_RECHECK_SECONDS})
        save_state(cfg, state)
        log_event(cfg, "retry_wait", error=repr(exc))
        return 1

    state["lastQuota"] = quota
    if quota.get("ordinaryUsageAllowed") is not True:
        state.update({"status": WAITING_QUOTA, "nextCheckAt": next_check_after_quota(quota, cfg)})
        save_state(cfg, state)
        log_event(cfg, "waiting_quota", **{k: v for k, v in quota.items() if v is not None})
        return 0

    # 3. 额度允许。投递前有两道闸：线程是否正在跑、以及距上次投递是否太近。
    try:
        verdict = classify_turn(tail_events(resolve_rollout(cfg)), 0)
    except Exception as exc:
        state.update({"status": RETRY_WAIT, "lastError": repr(exc), "nextCheckAt": now + WAITING_RECHECK_SECONDS})
        save_state(cfg, state)
        log_event(cfg, "rollout_unreadable", error=repr(exc))
        return 1

    decision = delivery_gate(state, verdict, cfg, now)
    if not decision["allow"]:
        state.update({"status": decision["status"], "nextCheckAt": decision["nextCheckAt"]})
        save_state(cfg, state)
        log_event(cfg, decision["event"], **decision.get("fields", {}))
        return 0

    # 4. 额度允许且线程空闲，投递续跑消息。
    message = cfg.message_file.read_text(encoding="utf-8")
    code, submission_id, out = queue_message(cfg, message)
    if code != 0 or not submission_id:
        state.update({"status": RETRY_WAIT, "lastError": out, "nextCheckAt": now + WAITING_RECHECK_SECONDS})
        save_state(cfg, state)
        log_event(cfg, "queue_failed", code=code, output=out)
        return 1

    state.update({
        "status": QUEUED,
        "queuedSubmissionId": submission_id,
        "queuedAt": now,
        "lastDeliveryAt": now,
        "consumeDeadline": now + QUEUE_CONSUME_DEADLINE_SECONDS,
        "rolloutOffset": rollout_offset(cfg),
        "nextCheckAt": now + cfg.poll_seconds,
    })
    save_state(cfg, state)
    log_event(cfg, "queued", submissionId=submission_id)
    # 回执写入后立刻回读校验：进程若在写入前后被终止，外层要能看出状态未曾落盘。
    persisted = load_state(cfg)
    if persisted.get("queuedSubmissionId") != submission_id:
        log_event(cfg, "queued_not_persisted", submissionId=submission_id)
        return 1
    return 0


def rollout_offset(cfg: TaskConfig) -> int:
    try:
        return resolve_rollout(cfg).stat().st_size
    except Exception:
        return 0


def pending_submission_ids(cfg: TaskConfig) -> set[str] | None:
    """读取本机队列里仍在等待消费的提交 ID。

    返回 None 表示无法判定（另装实例、自定义 CODEX_HOME、库不可读等），
    调用方必须把 None 与「空集合」区别对待：空集合是确定的"没有待消费消息"。
    """
    codex_home = Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex"))
    db = codex_home / "queue_1.sqlite"
    if not db.is_file():
        return None
    try:
        import sqlite3

        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=5)
        try:
            rows = con.execute(
                "select id from queued_items where thread_id = ?", (cfg.thread_id,)
            ).fetchall()
        finally:
            con.close()
        return {r[0] for r in rows}
    except Exception:
        return None


def track_queued(cfg: TaskConfig, state: dict, now: int) -> int:
    if now > int(state.get("consumeDeadline") or 0):
        state.update({"status": NEEDS_ATTENTION, "blocker": "排队消息在规定期限内未被消费"})
        save_state(cfg, state)
        log_event(cfg, "consume_timeout", submissionId=state.get("queuedSubmissionId"))
        notify(cfg, f"[{cfg.name}] 需要处理", "续跑消息入队后长期未被消费，请检查宿主与额度。")
        return 0

    submission_id = state.get("queuedSubmissionId")
    queued_at = int(state.get("queuedAt") or now)

    # 被追踪的提交可能被外部删除（人工清理、其它客户端撤销），此时它永远不会被
    # 消费。必须区分三种情况，否则会一直等到 6 小时期限：确实还在等、已被消费、
    # 已被删除。判据是「队列中已无此提交」且「rollout 自入队后没有任何增长」。
    if submission_id:
        pending = pending_submission_ids(cfg)
        size_now = rollout_offset(cfg)
        grew = size_now > int(state.get("rolloutOffset") or 0)
        if pending is not None and submission_id not in pending and not grew:
            state.update({
                "status": RETRY_WAIT,
                "droppedSubmissionId": submission_id,
                "lastError": "被追踪的排队消息已不在队列中且未被消费（可能被外部删除）",
                "nextCheckAt": now + cfg.poll_seconds,
            })
            save_state(cfg, state)
            log_event(cfg, "submission_dropped", submissionId=submission_id)
            notify(cfg, f"[{cfg.name}] 待投递消息被移除",
                   "队列中已找不到该续跑消息，且会话未推进；将在下一个额度窗口重新评估。")
            return 0

    try:
        events = tail_events(resolve_rollout(cfg))
    except Exception as exc:
        state["nextCheckAt"] = now + cfg.poll_seconds
        save_state(cfg, state)
        log_event(cfg, "rollout_unreadable", error=repr(exc))
        return 1

    verdict = classify_turn(events, queued_at)

    # 该线程正在执行：绝不追加续跑消息，只跟踪。
    # 这是防止「额度可用就每轮投递」的关键判据——正在跑的会话不需要被催。
    if verdict["turnRunning"]:
        state.update({"status": RUNNING, "nextCheckAt": now + cfg.poll_seconds})
        save_state(cfg, state)
        log_event(cfg, "thread_running", elapsedSec=now - queued_at)
        return 0

    if not verdict["turnCompleted"]:
        state["nextCheckAt"] = now + cfg.poll_seconds
        save_state(cfg, state)
        log_event(cfg, "awaiting_execution", elapsedSec=now - queued_at)
        return 0

    # 消息已被消费并跑完一轮。轮次结束 ≠ 任务完成。
    last = verdict.get("lastMessage") or ""
    state.update({
        "status": RUNNING,
        "turnCompletedAt": verdict["completedAt"],
        "lastMessage": last[:2000],
        "nextCheckAt": now + cfg.poll_seconds,
    })
    log_event(cfg, "turn_completed", blocker=verdict.get("blocker"))

    if cfg.stop_markers and match_markers(last, cfg.stop_markers):
        state["status"] = STOPPED
        save_state(cfg, state)
        notify(cfg, f"[{cfg.name}] 已停止", "续跑消息报告为停止状态。")
        return 0
    if cfg.completion_markers and match_markers(last, cfg.completion_markers):
        state["status"] = COMPLETED
        save_state(cfg, state)
        log_event(cfg, "completed", evidence=last[:300])
        notify(cfg, f"[{cfg.name}] 已完成", "完成证据已记录，调度停止。")
        return 0

    # 既非完成也非停止：继续下一轮投递（下一周期由额度门决定）。
    # 但必须有界：一轮结束却没有约定证据，就是「无进展」。没有这个上限时，
    # 一个持续返回同样结果的任务会每轮都重新投递，白烧额度。
    rounds = int(state.get("roundsWithoutProgress") or 0) + 1
    if rounds >= cfg.max_rounds_without_progress:
        state.update({
            "status": NEEDS_ATTENTION,
            "roundsWithoutProgress": rounds,
            "blocker": f"连续 {rounds} 轮未取得约定证据",
        })
        save_state(cfg, state)
        log_event(cfg, "no_progress_limit", rounds=rounds)
        notify(cfg, f"[{cfg.name}] 需要处理",
               f"连续 {rounds} 轮没有取得完成证据，已停止自动续跑。")
        return 0

    state.update({"status": WAITING_QUOTA, "roundsWithoutProgress": rounds})
    save_state(cfg, state)
    log_event(cfg, "continue_next_round", roundsWithoutProgress=rounds)
    return 0


def do_check(cfg: TaskConfig) -> int:
    print(f"任务: {cfg.summary()}")
    print(f"  配置文件   : {cfg.path}")
    print(f"  工作目录   : {cfg.cwd} (exists={cfg.cwd.is_dir()})")
    print(f"  状态目录   : {cfg.state_dir}")
    print(f"  续跑指令   : {cfg.message_file} ({cfg.message_file.stat().st_size} bytes)")
    print(f"  审批审查方 : {cfg.approvals_reviewer}")
    print(f"  额度策略   : {cfg.allowance}"
          + (f" (上限 {cfg.max_reset_credits} 张, 已授权={cfg.reset_credit_authorized})"
             if cfg.allowance == "reset_credit" else ""))
    try:
        rollout = resolve_rollout(cfg)
        print(f"  rollout    : {rollout} ({rollout.stat().st_size} bytes)")
    except Exception as exc:
        print(f"  rollout    : 解析失败 {exc}")
        return 1
    try:
        quota = evaluate_quota(read_usage(cfg))
    except Exception as exc:
        print(f"  额度查询   : 失败 {exc}")
        return 1
    print("  额度       : " + json.dumps(quota, ensure_ascii=False, sort_keys=True))
    print(f"  当前判定   : {'允许续跑' if quota.get('ordinaryUsageAllowed') is True else '等待额度'}")
    print(f"  下次检查   : {next_check_after_quota(quota, cfg)} "
          f"({time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_check_after_quota(quota, cfg)))})")
    print("  --check 不投递消息、不消耗额度。")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="额度恢复续跑控制器")
    ap.add_argument("--config", required=True, type=Path)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="静态校验 + 额度查询，不入队")
    group.add_argument("--cycle", action="store_true", help="执行一个调度周期")
    group.add_argument("--status", action="store_true", help="打印当前状态")
    args = ap.parse_args(argv)

    try:
        cfg = load_config(args.config)
        if args.check:
            return do_check(cfg)
        if args.status:
            print(json.dumps(load_state(cfg), ensure_ascii=False, indent=1, sort_keys=True))
            return 0
        return cycle(cfg)
    except ConfigError as exc:
        print(f"配置错误: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
