"""提供子进程、重试、脱敏和互斥锁等运行时基础设施。"""

from __future__ import annotations

import csv
import io
import os
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


_RETRYABLE_PATTERNS = (
    re.compile(r"\b429\b", re.IGNORECASE),
    re.compile(r"rate[ -]?limit", re.IGNORECASE),
    re.compile(r"timed?\s*out|timeout", re.IGNORECASE),
    re.compile(r"temporary|temporarily", re.IGNORECASE),
    re.compile(r"connection (?:reset|refused|closed)", re.IGNORECASE),
    re.compile(r"could not resolve host", re.IGNORECASE),
    re.compile(r"remote end hung up", re.IGNORECASE),
)


@dataclass(frozen=True)
class RetryPolicy:
    """定义总尝试次数和指数退避基数。"""

    attempts: int = 3
    base_delay: float = 1.0

    def delays(self) -> tuple[float, ...]:
        if self.attempts < 1:
            raise ValueError("attempts must be at least 1")
        return tuple(self.base_delay * (2**index) for index in range(self.attempts - 1))


@dataclass(frozen=True)
class CommandResult:
    """一次外部命令执行的可序列化结果。"""

    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    attempts: int


class CommandFailure(RuntimeError):
    """携带最后一次命令结果的失败。"""

    def __init__(self, result: CommandResult) -> None:
        self.result = result
        message = result.stderr.strip() or result.stdout.strip() or "command failed"
        super().__init__(
            f"command exited with {result.returncode}: "
            f"{' '.join(result.command)}: {message}"
        )


class CommandRunner:
    """集中执行子进程，确保超时、重试和环境合并规则一致。"""

    def __init__(self, *, timeout: float = 300.0) -> None:
        self.timeout = timeout

    def run(
        self,
        args: Sequence[str],
        *,
        cwd: Path | None = None,
        env: Mapping[str, str] | None = None,
        retry: RetryPolicy | None = None,
        check: bool = True,
    ) -> CommandResult:
        policy = retry or RetryPolicy(attempts=1)
        delays = policy.delays()
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        last_result: CommandResult | None = None
        for attempt in range(1, policy.attempts + 1):
            try:
                process = subprocess.run(
                    list(args),
                    cwd=cwd,
                    env=merged_env,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=self.timeout,
                    check=False,
                )
                last_result = CommandResult(
                    tuple(str(arg) for arg in args),
                    process.returncode,
                    process.stdout,
                    process.stderr,
                    attempt,
                )
            except subprocess.TimeoutExpired as error:
                last_result = CommandResult(
                    tuple(str(arg) for arg in args),
                    124,
                    _timeout_stream(error.stdout),
                    _timeout_stream(error.stderr) or f"timeout after {self.timeout}s",
                    attempt,
                )
            if last_result.returncode == 0:
                return last_result
            message = f"{last_result.stdout}\n{last_result.stderr}"
            if attempt >= policy.attempts or not is_retryable_failure(message):
                break
            time.sleep(delays[attempt - 1])
        assert last_result is not None
        if check:
            raise CommandFailure(last_result)
        return last_result


def _timeout_stream(value: bytes | str | None) -> str:
    if value is None:
        return ""
    return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value


def is_retryable_failure(message: str) -> bool:
    """只将传输层、限流和临时网络错误归类为可重试。"""

    return any(pattern.search(message) for pattern in _RETRYABLE_PATTERNS)


def redact_text(
    value: str,
    *,
    secrets: tuple[str, ...] = (),
    home: Path | None = None,
) -> str:
    """移除已知秘密并把用户主目录归一化为 ``~``。"""

    redacted = value
    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, "<redacted>")
    home_path = str(home or Path.home())
    if home_path:
        redacted = redacted.replace(home_path, "~")
    redacted = re.sub(
        r"(?i)(token|password|secret|authorization)=([^\s]+)",
        r"\1=<redacted>",
        redacted,
    )
    return redacted


class ProcessLock:
    """用原子创建锁文件阻止两个晋级流程并发修改用户配置。"""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._fd: int | None = None

    def __enter__(self) -> "ProcessLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._fd = os.open(
                self.path,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o600,
            )
        except FileExistsError as error:
            raise RuntimeError(f"another promotion is active: {self.path}") from error
        os.write(self._fd, str(os.getpid()).encode("ascii"))
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None
        self.path.unlink(missing_ok=True)


def find_blocking_processes(
    processes: Sequence[tuple[int, str, str]],
    *,
    current_pid: int | None = None,
) -> list[str]:
    """从进程快照中找出可能持有插件配置或缓存的 Codex/Claude 客户端。"""

    own_pid = current_pid if current_pid is not None else os.getpid()
    found: list[str] = []
    for pid, name, _command in processes:
        if pid == own_pid:
            continue
        normalized = Path(name).stem.lower().replace(" ", "")
        if normalized.startswith("codex") or normalized.startswith("claude"):
            found.append(f"{name} (pid {pid})")
    return found


def require_plugin_clients_stopped(
    processes: Sequence[tuple[int, str, str]] | None = None,
    *,
    current_pid: int | None = None,
) -> None:
    """晋级前要求关闭 App、Desktop 和交互式 CLI，避免并发覆盖用户配置。"""

    blockers = find_blocking_processes(
        list(processes) if processes is not None else _system_processes(),
        current_pid=current_pid,
    )
    if blockers:
        raise RuntimeError(
            "close Codex and Claude clients before --promote: " + ", ".join(blockers)
        )


def _system_processes() -> list[tuple[int, str, str]]:
    """以标准系统命令读取进程，不依赖第三方 Python 包。"""

    if os.name == "nt":
        result = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        processes: list[tuple[int, str, str]] = []
        for row in csv.reader(io.StringIO(result.stdout)):
            if len(row) < 2:
                continue
            try:
                processes.append((int(row[1]), row[0], row[0]))
            except ValueError:
                continue
        return processes

    result = subprocess.run(
        ["ps", "-eo", "pid=,comm=,args="],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    processes = []
    for line in result.stdout.splitlines():
        parts = line.strip().split(maxsplit=2)
        if len(parts) < 2:
            continue
        try:
            processes.append(
                (int(parts[0]), parts[1], parts[2] if len(parts) == 3 else parts[1])
            )
        except ValueError:
            continue
    return processes
