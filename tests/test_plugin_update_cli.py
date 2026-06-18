from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

from scripts.plugin_update_e2e import (
    build_initial_report,
    default_report_path,
    execute_operations,
    main,
    parse_args,
    promotion_state_paths,
    write_report,
)
from scripts.plugin_update_flow.models import Artifact, ExitCode
from scripts.plugin_update_flow.preflight import PreflightError, PreflightResult
from scripts.plugin_update_flow.workflow import PromotionError


class CliContractTests(unittest.TestCase):
    def test_default_report_path_is_run_specific(self) -> None:
        root = Path("C:/repo")

        self.assertEqual(
            root / "artifacts/plugin-update-e2e/run-1.json",
            default_report_path(root, "run-1"),
        )

    def test_script_entrypoint_exposes_help_when_run_by_path(self) -> None:
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, str(root / "scripts/plugin_update_e2e.py"), "--help"],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("--promote", result.stdout)

    def test_parses_public_defaults(self) -> None:
        options = parse_args([])

        self.assertEqual("origin/main", options.target_ref)
        self.assertIsNone(options.from_ref)
        self.assertFalse(options.promote)
        self.assertFalse(options.skill_smoke)
        self.assertIsNone(options.report)
        self.assertEqual(300.0, options.timeout)

    def test_parses_explicit_public_options(self) -> None:
        options = parse_args(
            [
                "--from-ref",
                "v1.0.0",
                "--target-ref",
                "origin/main",
                "--promote",
                "--skill-smoke",
                "--report",
                "result.json",
                "--timeout",
                "42",
            ]
        )

        self.assertEqual("v1.0.0", options.from_ref)
        self.assertTrue(options.promote)
        self.assertTrue(options.skill_smoke)
        self.assertEqual(Path("result.json"), options.report)
        self.assertEqual(42.0, options.timeout)

    def test_snapshot_covers_only_declared_plugin_state(self) -> None:
        codex_home = Path("C:/Users/test/.codex")
        claude_home = Path("C:/Users/test/.claude")

        paths = promotion_state_paths(codex_home, claude_home)

        self.assertEqual(
            [
                codex_home / "config.toml",
                codex_home / ".tmp/marketplaces/laxpud-vibekits",
                claude_home / "plugins/installed_plugins.json",
                claude_home / "plugins/known_marketplaces.json",
                claude_home / "plugins/marketplaces/laxpud-vibekits-dev",
                claude_home / "plugins/cache/laxpud-vibekits-dev",
            ],
            paths,
        )

    def test_report_redacts_errors_and_uses_schema_version_one(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report_path = root / "result.json"
            payload = build_initial_report("run-1", promote=False)
            payload["errors"] = [f"token=secret path={Path.home() / '.codex'}"]

            write_report(report_path, payload, secrets=("secret",))

            serialized = report_path.read_text(encoding="utf-8")
            report = json.loads(serialized)
            self.assertEqual(1, report["schemaVersion"])
            self.assertNotIn("secret", serialized)
            self.assertNotIn(str(Path.home()), serialized)
            self.assertIn("<redacted>", serialized)

    def test_main_wires_real_entrypoint_to_state_machine(self) -> None:
        operations = FakeOperations()
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "result.json"
            with patch("scripts.plugin_update_e2e.LocalOperations", return_value=operations):
                code = main(["--report", str(report)])

            self.assertEqual(int(ExitCode.SUCCESS), code)
            self.assertTrue(report.is_file())


class FakeOperations:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.preflight_error: BaseException | None = None
        self.isolated_error: BaseException | None = None
        self.promotion_error: BaseException | None = None
        self.preflight_result = PreflightResult(
            Artifact("old", "a" * 40, "1.0.0", "sha256:old"),
            Artifact("origin/main", "b" * 40, "1.1.0", "sha256:new"),
            "Laxpud/my-awesome-vibekits",
        )

    def preflight(self, options: Namespace) -> PreflightResult:
        self.calls.append("preflight")
        if self.preflight_error:
            raise self.preflight_error
        return self.preflight_result

    def isolated(self, result: PreflightResult) -> dict[str, object]:
        self.calls.append("isolated")
        if self.isolated_error:
            raise self.isolated_error
        return {"codex": {"result": "passed"}, "claude": {"result": "passed"}}

    def promote(self, result: PreflightResult) -> dict[str, object]:
        self.calls.append("promote")
        if self.promotion_error:
            raise self.promotion_error
        return {"result": "passed", "instances": [{"platform": "codex"}]}


class ApplicationStateTests(unittest.TestCase):
    def _options(self, *, promote: bool) -> Namespace:
        return Namespace(
            from_ref=None,
            target_ref="origin/main",
            promote=promote,
            skill_smoke=False,
            report=None,
            timeout=300.0,
        )

    def _execute(
        self, operations: FakeOperations, *, promote: bool
    ) -> tuple[ExitCode, dict[str, object]]:
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "result.json"
            code = execute_operations(
                self._options(promote=promote),
                operations,
                report_path=report,
                run_id="run-1",
            )
            return code, json.loads(report.read_text(encoding="utf-8"))

    def test_test_only_success_never_promotes(self) -> None:
        operations = FakeOperations()

        code, report = self._execute(operations, promote=False)

        self.assertEqual(ExitCode.SUCCESS, code)
        self.assertEqual(["preflight", "isolated"], operations.calls)
        self.assertEqual("passed", report["result"])

    def test_isolated_failure_blocks_promotion(self) -> None:
        operations = FakeOperations()
        operations.isolated_error = RuntimeError("Claude smoke failed")

        code, report = self._execute(operations, promote=True)

        self.assertEqual(ExitCode.TEST_FAILED, code)
        self.assertNotIn("promote", operations.calls)
        self.assertEqual("failed", report["result"])
        self.assertEqual("failed", report["promotion"]["result"])

    def test_preflight_failure_returns_environment_exit_code(self) -> None:
        operations = FakeOperations()
        operations.preflight_error = PreflightError("dirty worktree")

        code, _ = self._execute(operations, promote=False)

        self.assertEqual(ExitCode.PRECONDITION_FAILED, code)
        self.assertEqual(["preflight"], operations.calls)

    def test_promotion_failure_with_rollback_returns_two(self) -> None:
        operations = FakeOperations()
        operations.promotion_error = PromotionError(
            "update failed", rollback_succeeded=True
        )

        code, report = self._execute(operations, promote=True)

        self.assertEqual(ExitCode.PROMOTION_ROLLED_BACK, code)
        self.assertEqual("rolled-back", report["promotion"]["result"])

    def test_rollback_failure_returns_three_and_keeps_recovery_path(self) -> None:
        operations = FakeOperations()
        operations.promotion_error = PromotionError(
            "restore failed",
            rollback_succeeded=False,
            recovery_path=Path("C:/recovery/run-1"),
            manual_commands=[
                {"platform": "codex", "cwd": None, "command": "codex plugin list"}
            ],
        )

        code, report = self._execute(operations, promote=True)

        self.assertEqual(ExitCode.ROLLBACK_FAILED, code)
        self.assertEqual("rollback-failed", report["promotion"]["result"])
        self.assertEqual(
            str(Path("C:/recovery/run-1")),
            report["promotion"]["rollback"]["recoveryPath"],
        )
        self.assertEqual(
            "codex plugin list",
            report["promotion"]["rollback"]["manualCommands"][0]["command"],
        )


if __name__ == "__main__":
    unittest.main()
