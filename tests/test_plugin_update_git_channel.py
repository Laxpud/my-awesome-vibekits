from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.plugin_update_flow.git_channel import (
    GitRepository,
    TemporaryGitChannel,
    digest_directory,
)
from scripts.plugin_update_flow.runtime import CommandResult


class RecordingRunner:
    def __init__(self) -> None:
        self.commands: list[tuple[str, ...]] = []

    def run(self, args: list[str], **_: object) -> CommandResult:
        self.commands.append(tuple(args))
        return CommandResult(tuple(args), 0, "", "", 1)


class FailFirstRunner(RecordingRunner):
    def run(self, args: list[str], **kwargs: object) -> CommandResult:
        result = super().run(args, **kwargs)
        if len(self.commands) == 1:
            raise RuntimeError("push result unknown")
        return result


class GitRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self._git("init")
        self._git("config", "user.name", "Test User")
        self._git("config", "user.email", "test@example.com")
        self.manifest = (
            self.root
            / "plugins"
            / "laxpud-vibekits"
            / ".codex-plugin"
            / "plugin.json"
        )
        self.manifest.parent.mkdir(parents=True)
        self.skill = self.manifest.parents[1] / "skills" / "sample" / "SKILL.md"
        self.skill.parent.mkdir(parents=True)
        self._write_version("1.0.0", "old")
        self._git("add", ".")
        self._git("commit", "-m", "old")
        self.old_commit = self._git("rev-parse", "HEAD").strip()
        self._write_version("1.1.0", "new")
        self._git("add", ".")
        self._git("commit", "-m", "new")
        self.target_commit = self._git("rev-parse", "HEAD").strip()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout

    def _write_version(self, version: str, skill_marker: str) -> None:
        self.manifest.write_text(
            json.dumps({"name": "laxpud-vibekits", "version": version}),
            encoding="utf-8",
        )
        self.skill.write_text(skill_marker, encoding="utf-8")

    def test_auto_selects_nearest_ancestor_with_lower_version(self) -> None:
        repository = GitRepository(self.root)

        baseline, target = repository.resolve_artifacts("HEAD")

        self.assertEqual(self.old_commit, baseline.commit)
        self.assertEqual("1.0.0", baseline.version)
        self.assertEqual(self.target_commit, target.commit)
        self.assertEqual("1.1.0", target.version)
        self.assertNotEqual(baseline.plugin_digest, target.plugin_digest)

    def test_rejects_explicit_ref_that_is_not_older(self) -> None:
        repository = GitRepository(self.root)

        with self.assertRaisesRegex(ValueError, "older than target"):
            repository.resolve_artifacts("HEAD", from_ref="HEAD")

    def test_manifest_only_version_bump_does_not_change_payload_digest(self) -> None:
        repository = GitRepository(self.root)
        before = repository.artifact("HEAD")
        self._write_version("1.2.0", "new")
        self._git("add", ".")
        self._git("commit", "-m", "manifest only")

        after = repository.artifact("HEAD")

        self.assertEqual(before.plugin_digest, after.plugin_digest)

    def test_git_tree_and_checkout_use_the_same_cross_platform_order(self) -> None:
        reference = self.skill.parent / "references" / "details.md"
        reference.parent.mkdir()
        reference.write_text("details", encoding="utf-8")
        self._git("add", ".")
        self._git("commit", "-m", "nested payload")
        repository = GitRepository(self.root)

        git_digest = repository.artifact("HEAD").plugin_digest
        checkout_digest = digest_directory(self.manifest.parents[1])

        self.assertEqual(git_digest, checkout_digest)

    def test_directory_digest_is_stable_and_ignores_python_cache(self) -> None:
        plugin_root = self.manifest.parents[1]
        first = digest_directory(plugin_root)
        cache = plugin_root / "__pycache__"
        cache.mkdir()
        (cache / "ignored.pyc").write_bytes(b"ignored")
        second = digest_directory(plugin_root)
        self.manifest.write_text(
            json.dumps({"name": "laxpud-vibekits", "version": "9.9.9"}),
            encoding="utf-8",
        )
        manifest_only = digest_directory(plugin_root)
        self.skill.write_text("changed", encoding="utf-8")
        third = digest_directory(plugin_root)

        self.assertEqual(first, second)
        self.assertEqual(second, manifest_only)
        self.assertNotEqual(manifest_only, third)

    def test_text_line_endings_do_not_change_payload_digest(self) -> None:
        plugin_root = self.manifest.parents[1]
        self.skill.write_bytes(b"line one\nline two\n")
        lf_digest = digest_directory(plugin_root)
        self.skill.write_bytes(b"line one\r\nline two\r\n")

        crlf_digest = digest_directory(plugin_root)

        self.assertEqual(lf_digest, crlf_digest)


class TemporaryGitChannelTests(unittest.TestCase):
    def test_create_result_unknown_still_attempts_remote_cleanup(self) -> None:
        runner = FailFirstRunner()
        channel = TemporaryGitChannel(
            runner=runner,
            root=Path("/repo"),
            remote="origin",
            branch="automation/plugin-e2e/run-unknown",
            baseline_commit="a" * 40,
            target_commit="b" * 40,
        )

        with self.assertRaisesRegex(RuntimeError, "result unknown"):
            channel.create()
        channel.cleanup()

        self.assertEqual(
            ("git", "push", "origin", "--delete", "automation/plugin-e2e/run-unknown"),
            runner.commands[-1],
        )

    def test_uses_force_with_lease_and_deletes_unique_branch(self) -> None:
        runner = RecordingRunner()
        channel = TemporaryGitChannel(
            runner=runner,
            root=Path("/repo"),
            remote="origin",
            branch="automation/plugin-e2e/run-1",
            baseline_commit="a" * 40,
            target_commit="b" * 40,
        )

        channel.create()
        channel.advance()
        channel.cleanup()

        self.assertEqual(
            (
                "git",
                "push",
                "origin",
                f"{'a' * 40}:refs/heads/automation/plugin-e2e/run-1",
            ),
            runner.commands[0],
        )
        self.assertIn("--force-with-lease=refs/heads/automation/plugin-e2e/run-1:" + "a" * 40, runner.commands[1])
        self.assertEqual(
            ("git", "push", "origin", "--delete", "automation/plugin-e2e/run-1"),
            runner.commands[2],
        )


if __name__ == "__main__":
    unittest.main()
