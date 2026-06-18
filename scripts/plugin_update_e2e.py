#!/usr/bin/env python3
"""真实验证插件跨平台升级，并可在门禁通过后晋级日常安装。"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol, Sequence

# 该文件必须支持 `python scripts/plugin_update_e2e.py`。直接按路径执行时，
# Python 只把 scripts/ 放入 sys.path，因此需显式加入仓库根目录。
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.plugin_update_flow.models import ExitCode
from scripts.plugin_update_flow.claude_adapter import ClaudeAdapter
from scripts.plugin_update_flow.codex_adapter import CodexAdapter
from scripts.plugin_update_flow.git_channel import TemporaryGitChannel
from scripts.plugin_update_flow.preflight import (
    PreflightError,
    PreflightResult,
    ReleasePreflight,
)
from scripts.plugin_update_flow.runtime import (
    CommandRunner,
    ProcessLock,
    redact_text,
    require_plugin_clients_stopped,
)
from scripts.plugin_update_flow.workflow import (
    IsolatedHomes,
    PromotionError,
    StateSnapshot,
    run_isolated_upgrade,
    run_promotion,
)


class Operations(Protocol):
    """顶层状态机依赖的有副作用操作边界。"""

    def preflight(self, options: argparse.Namespace) -> PreflightResult: ...
    def isolated(self, result: PreflightResult) -> dict[str, object]: ...
    def promote(self, result: PreflightResult) -> dict[str, object]: ...


class LocalOperations:
    """把顶层状态机连接到真实 Git、CLI、临时目录和日常用户配置。"""

    def __init__(self, *, root: Path, timeout: float, run_id: str) -> None:
        self.root = root.resolve()
        self.run_id = run_id
        self.runner = CommandRunner(timeout=timeout)
        self.codex_home = Path(
            os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))
        ).resolve()
        self.claude_home = Path(
            os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude"))
        ).resolve()
        self.preflight_engine = ReleasePreflight(
            root=self.root,
            runner=self.runner,
            codex_home=self.codex_home,
        )
        self.run_skill_smoke = False
        self.cleanup_info: dict[str, object] = {}

    def preflight(self, options: argparse.Namespace) -> PreflightResult:
        self.run_skill_smoke = bool(options.skill_smoke)
        return self.preflight_engine.run(
            target_ref=options.target_ref,
            from_ref=options.from_ref,
            promote=bool(options.promote),
        )

    def isolated(self, result: PreflightResult) -> dict[str, object]:
        branch = f"automation/plugin-e2e/{self.run_id}"
        channel = TemporaryGitChannel(
            runner=self.runner,
            root=self.root,
            remote="origin",
            branch=branch,
            baseline_commit=result.baseline.commit,
            target_commit=result.target.commit,
        )
        try:
            with IsolatedHomes(
                real_codex_home=self.codex_home,
                real_claude_home=self.claude_home,
                repository=result.repository_slug,
                branch=branch,
            ) as homes:
                codex = CodexAdapter(self.runner, env=homes.codex_env())
                claude = ClaudeAdapter(self.runner, env=homes.claude_env())
                return run_isolated_upgrade(
                    channel=channel,
                    codex=codex,
                    claude=claude,
                    baseline=result.baseline,
                    target=result.target,
                    marketplace_source=result.repository_slug,
                    branch=branch,
                    smoke_dir=homes.smoke_dir,
                    schema_path=homes.schema_path,
                    run_skill_smoke=self.run_skill_smoke,
                )
        finally:
            self.cleanup_info = {
                "temporaryBranch": branch,
                "remoteBranchDeleted": not channel.create_attempted,
                "isolatedCredentialsDeleted": True,
            }

    def promote(self, result: PreflightResult) -> dict[str, object]:
        lock_path = self.codex_home / ".tmp/plugin-update-e2e-promotion.lock"
        with ProcessLock(lock_path):
            require_plugin_clients_stopped()
            codex = CodexAdapter(self.runner)
            claude = ClaudeAdapter(self.runner)
            if not codex.list_instances() or not claude.list_instances():
                raise PreflightError(
                    "both Codex and Claude must have an installed daily instance"
                )
            snapshot = StateSnapshot(
                self.codex_home
                / ".tmp/plugin-update-e2e-snapshots"
                / self.run_id,
                promotion_state_paths(self.codex_home, self.claude_home),
            )
            return run_promotion(codex, claude, result.target, snapshot)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """解析稳定公开 CLI；不在参数解析阶段访问网络或用户配置。"""

    parser = argparse.ArgumentParser(
        description="Test a real Codex and Claude plugin upgrade, then optionally promote."
    )
    parser.add_argument("--from-ref", help="baseline commit or tag")
    parser.add_argument(
        "--target-ref", default="origin/main", help="target Git ref (default: origin/main)"
    )
    parser.add_argument(
        "--promote",
        action="store_true",
        help="update daily installations after both isolated tests pass",
    )
    parser.add_argument(
        "--skill-smoke",
        action="store_true",
        help="invoke both models to verify skill discovery (consumes tokens)",
    )
    parser.add_argument("--report", type=Path, help="JSON report path")
    parser.add_argument(
        "--timeout",
        type=float,
        default=300.0,
        help="per-command timeout in seconds (default: 300)",
    )
    options = parser.parse_args(argv)
    if options.timeout <= 0:
        parser.error("--timeout must be greater than zero")
    return options


def promotion_state_paths(codex_home: Path, claude_home: Path) -> list[Path]:
    """返回计划明确授权备份和恢复的最小日常插件状态集合。"""

    return [
        codex_home / "config.toml",
        codex_home / ".tmp/marketplaces/laxpud-vibekits",
        claude_home / "plugins/installed_plugins.json",
        claude_home / "plugins/known_marketplaces.json",
        claude_home / "plugins/marketplaces/laxpud-vibekits-dev",
        claude_home / "plugins/cache/laxpud-vibekits-dev",
    ]


def default_report_path(root: Path, run_id: str) -> Path:
    """返回默认且已被仓库忽略的单次运行报告路径。"""

    return root / "artifacts/plugin-update-e2e" / f"{run_id}.json"


def new_run_id() -> str:
    """生成可排序且足以避免并发分支碰撞的运行标识。"""

    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    return f"{timestamp}-{secrets.token_hex(4)}"


def build_initial_report(run_id: str, *, promote: bool) -> dict[str, Any]:
    """创建即使预检失败也能落盘的 schemaVersion 1 报告骨架。"""

    return {
        "schemaVersion": 1,
        "runId": run_id,
        "mode": "promote" if promote else "test",
        "startedAt": datetime.now(UTC).isoformat(),
        "finishedAt": None,
        "baseline": None,
        "target": None,
        "platforms": {},
        "promotion": {
            "requested": promote,
            "instances": [],
            "result": "pending" if promote else "not-requested",
            "rollback": {},
        },
        "cleanup": {},
        "result": "running",
        "errors": [],
    }


def execute_operations(
    options: argparse.Namespace,
    operations: Operations,
    *,
    report_path: Path,
    run_id: str,
) -> ExitCode:
    """执行预检、双端隔离门禁和可选晋级，并保证所有路径写报告。"""

    report = build_initial_report(run_id, promote=bool(options.promote))
    exit_code = ExitCode.TEST_FAILED
    try:
        try:
            prepared = operations.preflight(options)
        except Exception as error:
            report["errors"].append(str(error))
            report["result"] = "failed"
            exit_code = ExitCode.PRECONDITION_FAILED
            return exit_code

        report["baseline"] = prepared.baseline.to_dict()
        report["target"] = prepared.target.to_dict()
        try:
            report["platforms"] = operations.isolated(prepared)
        except (Exception, KeyboardInterrupt) as error:
            report["errors"].append(str(error) or type(error).__name__)
            report["result"] = "failed"
            exit_code = ExitCode.TEST_FAILED
            return exit_code

        if not options.promote:
            report["result"] = "passed"
            exit_code = ExitCode.SUCCESS
            return exit_code

        try:
            promotion = operations.promote(prepared)
            report["promotion"].update(promotion)
            report["result"] = "passed"
            exit_code = ExitCode.SUCCESS
            return exit_code
        except PromotionError as error:
            report["errors"].append(str(error))
            if error.rollback_succeeded:
                report["promotion"]["result"] = "rolled-back"
                report["promotion"]["rollback"] = {"result": "passed"}
                exit_code = ExitCode.PROMOTION_ROLLED_BACK
            else:
                report["promotion"]["result"] = "rollback-failed"
                report["promotion"]["rollback"] = {
                    "result": "failed",
                    "recoveryPath": (
                        str(error.recovery_path) if error.recovery_path else None
                    ),
                    "manualCommands": error.manual_commands,
                }
                exit_code = ExitCode.ROLLBACK_FAILED
            report["result"] = "failed"
            return exit_code
        except (Exception, KeyboardInterrupt) as error:
            # run_promotion 在写入快照后会统一包装 PromotionError；到这里的异常属于
            # 进程未关闭、安装缺失或锁冲突等尚未改写日常状态的前置条件失败。
            report["errors"].append(str(error) or type(error).__name__)
            report["promotion"]["result"] = "failed"
            report["result"] = "failed"
            exit_code = ExitCode.PRECONDITION_FAILED
            return exit_code
    finally:
        cleanup = getattr(operations, "cleanup_info", None)
        if isinstance(cleanup, dict):
            report["cleanup"].update(cleanup)
        if report["promotion"]["result"] == "pending":
            report["promotion"]["result"] = "failed"
        report["finishedAt"] = datetime.now(UTC).isoformat()
        secrets = tuple(getattr(operations, "secret_values", ()))
        write_report(report_path, report, secrets=secrets)


def write_report(
    path: Path,
    payload: dict[str, Any],
    *,
    secrets: tuple[str, ...] = (),
) -> None:
    """递归脱敏后原子替换报告，避免失败时留下半份 JSON。"""

    sanitized = _redact_value(payload, secrets=secrets)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(sanitized, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _redact_value(value: Any, *, secrets: tuple[str, ...]) -> Any:
    if isinstance(value, str):
        return redact_text(value, secrets=secrets)
    if isinstance(value, list):
        return [_redact_value(item, secrets=secrets) for item in value]
    if isinstance(value, dict):
        return {
            str(key): _redact_value(item, secrets=secrets)
            for key, item in value.items()
        }
    return value


def main(argv: Sequence[str] | None = None) -> int:
    options = parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    run_id = new_run_id()
    report_path = (
        (root / options.report).resolve()
        if options.report and not options.report.is_absolute()
        else options.report or default_report_path(root, run_id)
    )
    operations = LocalOperations(root=root, timeout=options.timeout, run_id=run_id)
    code = execute_operations(
        options,
        operations,
        report_path=report_path,
        run_id=run_id,
    )
    label = "PASS" if code == ExitCode.SUCCESS else "FAIL"
    print(f"{label}: plugin update E2E result={code.name.lower()}")
    print(f"  report: {report_path}")
    if code == ExitCode.SUCCESS and options.promote:
        print("  Codex: start a new thread")
        print("  Claude Code: run /reload-plugins or restart the session")
    return int(code)


if __name__ == "__main__":
    raise SystemExit(main())
