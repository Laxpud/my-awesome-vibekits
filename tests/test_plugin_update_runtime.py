from __future__ import annotations

import tempfile
import unittest
import sys
from pathlib import Path

from scripts.plugin_update_flow.runtime import (
    CommandFailure,
    CommandRunner,
    ProcessLock,
    RetryPolicy,
    find_blocking_processes,
    is_retryable_failure,
    redact_text,
    require_plugin_clients_stopped,
)


class RuntimeTests(unittest.TestCase):
    def test_redacts_credentials_and_user_home(self) -> None:
        home = Path.home()
        text = f"token=secret auth={home / '.codex' / 'auth.json'} path={home / 'work'}"

        redacted = redact_text(text, secrets=("secret",), home=home)

        self.assertNotIn("secret", redacted)
        self.assertNotIn(str(home), redacted)
        self.assertIn("<redacted>", redacted)
        self.assertIn("~", redacted)

    def test_retries_only_transport_failures(self) -> None:
        retryable = "HTTP 429 rate limit while cloning marketplace"
        deterministic = "installed version mismatch: expected 1.1.1"

        self.assertTrue(is_retryable_failure(retryable))
        self.assertFalse(is_retryable_failure(deterministic))
        self.assertEqual((0.0, 0.0), RetryPolicy(attempts=3, base_delay=0).delays())

    def test_process_lock_rejects_second_holder(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            lock_path = Path(directory) / "promotion.lock"
            with ProcessLock(lock_path):
                with self.assertRaises(RuntimeError):
                    with ProcessLock(lock_path):
                        pass

    def test_finds_plugin_clients_but_ignores_current_and_unrelated_processes(self) -> None:
        processes = [
            (10, "Codex.exe", "Codex.exe"),
            (11, "claude", "claude"),
            (12, "python.exe", "python worker.py"),
            (99, "codex.exe", "codex.exe"),
        ]

        found = find_blocking_processes(processes, current_pid=99)

        self.assertEqual(["Codex.exe (pid 10)", "claude (pid 11)"], found)

    def test_rejects_promotion_when_a_client_is_running(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "close Codex and Claude"):
            require_plugin_clients_stopped(
                [(10, "Claude.exe", "Claude.exe")], current_pid=99
            )

    def test_subprocess_timeout_is_reported_as_exit_124(self) -> None:
        runner = CommandRunner(timeout=0.05)

        with self.assertRaises(CommandFailure) as raised:
            runner.run(
                [sys.executable, "-c", "import time; time.sleep(1)"],
                retry=RetryPolicy(attempts=1),
            )

        self.assertEqual(124, raised.exception.result.returncode)
        self.assertIn("timeout", raised.exception.result.stderr)


if __name__ == "__main__":
    unittest.main()
