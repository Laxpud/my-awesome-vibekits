from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.plugin_update_flow.models import Artifact
from scripts.plugin_update_flow.preflight import PreflightError, ReleasePreflight
from scripts.plugin_update_flow.runtime import CommandResult


class RecordingRunner:
    def __init__(self, *, status: str = "") -> None:
        self.status = status
        self.calls: list[tuple[str, ...]] = []

    def run(self, args: list[str], **_: object) -> CommandResult:
        command = tuple(str(item) for item in args)
        self.calls.append(command)
        stdout = self.status if command[:3] == ("git", "status", "--porcelain") else ""
        return CommandResult(command, 0, stdout, "", 1)


class FakeRepository:
    def __init__(self, refs: dict[str, str]) -> None:
        self.refs = refs
        self.baseline = Artifact("old", "a" * 40, "1.0.0", "sha256:old")
        self.target = Artifact("origin/main", "b" * 40, "1.1.0", "sha256:new")
        self.resolve_calls: list[tuple[str, str | None]] = []

    def resolve_commit(self, ref: str) -> str:
        return self.refs[ref]

    def resolve_artifacts(
        self, target_ref: str, *, from_ref: str | None = None
    ) -> tuple[Artifact, Artifact]:
        self.resolve_calls.append((target_ref, from_ref))
        return self.baseline, self.target


class PreflightTests(unittest.TestCase):
    def _root(self, directory: str) -> tuple[Path, Path]:
        root = Path(directory)
        catalog = {
            "schemaVersion": 1,
            "marketplace": {
                "id": "laxpud-vibekits",
                "displayName": "Laxpud Vibekits",
                "description": "test",
                "owner": "Laxpud",
            },
            "publisher": {
                "name": "Laxpud",
                "url": "https://github.com/Laxpud",
                "homepage": "https://github.com/Laxpud/my-awesome-vibekits",
                "repository": "https://github.com/Laxpud/my-awesome-vibekits.git",
                "license": "MIT",
            },
            "plugins": [
                {
                    "id": "python-project",
                    "directory": "plugins/python-project",
                    "version": "1.1.0",
                    "description": "Python project standards.",
                    "category": "Productivity",
                    "keywords": ["python"],
                    "skills": [
                        {"id": "pyproject-standard", "path": "skills/pyproject-standard"}
                    ],
                    "platforms": {
                        "codex": {
                            "installation": "AVAILABLE",
                            "authentication": "ON_INSTALL",
                            "displayName": "Python Project",
                            "shortDescription": "Python standards",
                            "longDescription": "Python project standards.",
                            "defaultPrompt": ["Use pyproject-standard."],
                        },
                        "claude": {"category": "workflow", "tags": ["python"]},
                    },
                }
            ],
        }
        (root / "plugin-catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
        skill = root / "plugins/python-project/skills/pyproject-standard/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("---\nname: pyproject-standard\n---\n", encoding="utf-8")
        validator = root / "codex-home/skills/.system/plugin-creator/scripts/validate_plugin.py"
        validator.parent.mkdir(parents=True)
        validator.write_text("", encoding="utf-8")
        return root, validator

    def test_rejects_dirty_worktree_before_fetch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, _ = self._root(directory)
            runner = RecordingRunner(status=" M TODO.md\n")
            preflight = ReleasePreflight(
                root=root,
                runner=runner,
                repository=FakeRepository({}),
                codex_home=root / "codex-home",
                python_executable="python-test",
            )

            with self.assertRaisesRegex(PreflightError, "working tree must be clean"):
                preflight.run(target_ref="origin/main", from_ref=None, promote=False)

            self.assertEqual([("git", "status", "--porcelain")], runner.calls)

    def test_promote_requires_head_origin_and_target_to_match(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, _ = self._root(directory)
            runner = RecordingRunner()
            repository = FakeRepository(
                {
                    "HEAD": "a" * 40,
                    "origin/main": "b" * 40,
                    "release": "b" * 40,
                }
            )
            preflight = ReleasePreflight(
                root=root,
                runner=runner,
                repository=repository,
                codex_home=root / "codex-home",
                python_executable="python-test",
            )

            with self.assertRaisesRegex(PreflightError, "HEAD, origin/main and target"):
                preflight.run(target_ref="release", from_ref=None, promote=True)

            self.assertIn(("git", "fetch", "origin", "main"), runner.calls)
            self.assertEqual([], repository.resolve_calls)

    def test_runs_all_validators_and_returns_fixed_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, validator = self._root(directory)
            runner = RecordingRunner()
            commit = "b" * 40
            repository = FakeRepository(
                {"HEAD": commit, "origin/main": commit, "origin/main^{commit}": commit}
            )
            preflight = ReleasePreflight(
                root=root,
                runner=runner,
                repository=repository,
                codex_home=root / "codex-home",
                python_executable="python-test",
            )

            result = preflight.run(
                target_ref="origin/main", from_ref="old-tag", promote=True
            )

            self.assertEqual(repository.baseline, result.releases[0].baseline)
            self.assertEqual(repository.target, result.releases[0].target)
            self.assertEqual("Laxpud/my-awesome-vibekits", result.repository_slug)
            self.assertEqual([("origin/main", "old-tag")], repository.resolve_calls)
            # Windows runner 可能以 8.3 短路径创建临时目录，而预检会将其解析为
            # 规范长路径；断言必须复用生产代码的规范化边界，不能比较路径拼写。
            canonical_root = root.resolve()
            canonical_validator = validator.resolve()
            expected = [
                (
                    "python-test",
                    str(canonical_root / "scripts/sync_plugin_metadata.py"),
                ),
                (
                    "python-test",
                    str(canonical_root / "scripts/check_codex_install.py"),
                ),
                (
                    "python-test",
                    str(canonical_validator),
                    str(canonical_root / "plugins/python-project"),
                ),
                (
                    "claude",
                    "plugin",
                    "validate",
                    str(canonical_root / "plugins/python-project"),
                ),
                (
                    "claude",
                    "plugin",
                    "validate",
                    str(canonical_root / ".claude-plugin/marketplace.json"),
                ),
            ]
            for command in expected:
                self.assertIn(command, runner.calls)


if __name__ == "__main__":
    unittest.main()
