from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.plugin_update_flow.claude_adapter import ClaudeAdapter
from scripts.plugin_update_flow.codex_adapter import CodexAdapter
from scripts.plugin_update_flow.git_channel import digest_directory
from scripts.plugin_update_flow.models import Artifact, PluginTarget
from scripts.plugin_update_flow.runtime import CommandResult
from scripts.plugin_update_flow.smoke import (
    EXPECTED_SMOKE_RESULT,
    parse_claude_smoke,
    parse_codex_smoke,
    validate_smoke_payload,
)


TARGET = PluginTarget(
    "python-project",
    "laxpud-vibekits",
    (Path("skills/pyproject-standard/SKILL.md"),),
    "github.com/laxpud/my-awesome-vibekits",
)

MULTI_SKILL_TARGET = PluginTarget(
    "project-docs",
    "laxpud-vibekits",
    (
        Path("skills/project-docs-bootstrap/SKILL.md"),
        Path("skills/project-docs-planning/SKILL.md"),
    ),
    "github.com/laxpud/my-awesome-vibekits",
    (Path("skills/project-docs-bootstrap/SKILL.md"),),
)


class QueueRunner:
    def __init__(self, outputs: list[str]) -> None:
        self.outputs = list(outputs)
        self.calls: list[tuple[tuple[str, ...], Path | None, dict[str, str] | None]] = []

    def run(
        self,
        args: list[str],
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
        **_: object,
    ) -> CommandResult:
        self.calls.append((tuple(args), cwd, env))
        output = self.outputs.pop(0) if self.outputs else ""
        return CommandResult(tuple(args), 0, output, "", 1)


class SmokeTests(unittest.TestCase):
    def test_parses_codex_jsonl_agent_message(self) -> None:
        payload = json.dumps(EXPECTED_SMOKE_RESULT)
        output = "\n".join(
            [
                json.dumps({"type": "thread.started"}),
                json.dumps(
                    {
                        "type": "item.completed",
                        "item": {"type": "agent_message", "text": payload},
                    }
                ),
            ]
        )
        self.assertEqual(EXPECTED_SMOKE_RESULT, parse_codex_smoke(output))

    def test_parses_claude_result_wrapper(self) -> None:
        output = json.dumps({"result": json.dumps(EXPECTED_SMOKE_RESULT)})
        self.assertEqual(EXPECTED_SMOKE_RESULT, parse_claude_smoke(output))

    def test_rejects_deterministic_contract_mismatch(self) -> None:
        wrong = dict(EXPECTED_SMOKE_RESULT, packageManager="pip")
        with self.assertRaisesRegex(ValueError, "packageManager"):
            validate_smoke_payload(wrong)


class CodexAdapterTests(unittest.TestCase):
    def test_accepts_a_cross_platform_fake_command_prefix(self) -> None:
        runner = QueueRunner(["{}"])
        adapter = CodexAdapter(
            runner, target=TARGET, command=("python-test", "fake_plugin_cli.py", "codex")
        )

        adapter.install_plugin()

        self.assertEqual(
            ("python-test", "fake_plugin_cli.py", "codex", "plugin", "add"),
            runner.calls[0][0][:5],
        )

    def test_lists_target_plugin_and_preserves_enabled_state(self) -> None:
        source = str(Path(tempfile.gettempdir()) / "codex-plugin")
        output = json.dumps(
            {
                "installed": [
                    {
                        "pluginId": "python-project@laxpud-vibekits",
                        "name": "python-project",
                        "marketplaceName": "laxpud-vibekits",
                        "version": "1.1.1",
                        "enabled": False,
                        "source": {"source": "local", "path": source},
                        "marketplaceSource": {
                            "sourceType": "git",
                            "source": "https://github.com/Laxpud/my-awesome-vibekits.git",
                        },
                    }
                ]
            }
        )
        adapter = CodexAdapter(
            QueueRunner([output]), target=TARGET, env={"CODEX_HOME": "temp"}
        )

        instances = adapter.list_instances()

        self.assertEqual(1, len(instances))
        self.assertEqual("codex", instances[0].platform)
        self.assertFalse(instances[0].enabled)
        self.assertEqual(Path(source), instances[0].install_path)

    def test_rejects_target_from_an_unexpected_git_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            install_path = Path(directory)
            output = json.dumps(
                {
                    "installed": [
                        {
                            "pluginId": "python-project@laxpud-vibekits",
                            "version": "1.1.1",
                            "enabled": True,
                            "source": {"path": str(install_path)},
                            "marketplaceSource": {
                                "source": "https://github.com/attacker/repo.git"
                            },
                        }
                    ]
                }
            )
            adapter = CodexAdapter(QueueRunner([output]), target=TARGET)
            artifact = Artifact(
                "origin/main",
                "b" * 40,
                "1.1.1",
                digest_directory(install_path),
            )

            with self.assertRaisesRegex(ValueError, "source mismatch"):
                adapter.verify_target(artifact)

    def test_rejects_install_without_pyproject_standard_skill(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            install_path = Path(directory)
            output = json.dumps(
                {
                    "installed": [
                        {
                            "pluginId": "python-project@laxpud-vibekits",
                            "version": "1.1.1",
                            "enabled": True,
                            "source": {"path": str(install_path)},
                            "marketplaceSource": {
                                "source": "https://github.com/Laxpud/my-awesome-vibekits.git"
                            },
                        }
                    ]
                }
            )
            adapter = CodexAdapter(QueueRunner([output]), target=TARGET)
            artifact = Artifact(
                "origin/main",
                "b" * 40,
                "1.1.1",
                digest_directory(install_path),
            )

            with self.assertRaisesRegex(ValueError, "pyproject-standard"):
                adapter.verify_target(artifact)

    def test_baseline_uses_historical_skills_but_target_requires_full_set(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            install_path = Path(directory)
            bootstrap = install_path / "skills/project-docs-bootstrap/SKILL.md"
            bootstrap.parent.mkdir(parents=True)
            bootstrap.write_text("bootstrap", encoding="utf-8")
            output = json.dumps(
                {
                    "installed": [
                        {
                            "pluginId": "project-docs@laxpud-vibekits",
                            "version": "1.0.0",
                            "enabled": True,
                            "source": {"path": str(install_path)},
                            "marketplaceSource": {
                                "source": "https://github.com/Laxpud/my-awesome-vibekits.git"
                            },
                        }
                    ]
                }
            )
            adapter = CodexAdapter(
                QueueRunner([output, output]), target=MULTI_SKILL_TARGET
            )
            artifact = Artifact(
                "old", "a" * 40, "1.0.0", digest_directory(install_path)
            )

            adapter.verify_baseline(artifact)
            with self.assertRaisesRegex(ValueError, "project-docs-planning"):
                adapter.verify_target(artifact)

    def test_refreshes_marketplace_before_reinstall(self) -> None:
        runner = QueueRunner(["{}", "{}"])
        adapter = CodexAdapter(runner, target=TARGET, env={"CODEX_HOME": "temp"})

        adapter.update_plugin()

        self.assertEqual(
            ("codex", "plugin", "marketplace", "upgrade", "laxpud-vibekits", "--json"),
            runner.calls[0][0],
        )
        self.assertEqual(
            ("codex", "plugin", "add", "python-project@laxpud-vibekits", "--json"),
            runner.calls[1][0],
        )


class ClaudeAdapterTests(unittest.TestCase):
    def test_accepts_a_cross_platform_fake_command_prefix(self) -> None:
        runner = QueueRunner([""])
        adapter = ClaudeAdapter(
            runner, target=TARGET, command=("python-test", "fake_plugin_cli.py", "claude")
        )

        adapter.install_plugin()

        self.assertEqual(
            ("python-test", "fake_plugin_cli.py", "claude", "plugin", "install"),
            runner.calls[0][0][:5],
        )

    def test_smoke_sets_a_budget_limit(self) -> None:
        output = json.dumps({"result": json.dumps(EXPECTED_SMOKE_RESULT)})
        runner = QueueRunner([output])
        adapter = ClaudeAdapter(runner, target=TARGET)

        adapter.run_smoke(Path("/empty"))

        command = runner.calls[0][0]
        index = command.index("--max-budget-usd")
        self.assertEqual("1.0", command[index + 1])

    def test_lists_all_project_scopes_for_target_plugin(self) -> None:
        output = json.dumps(
            [
                {
                    "id": "python-project@laxpud-vibekits",
                    "version": "1.1.1",
                    "scope": "project",
                    "enabled": True,
                    "installPath": "C:/cache/vibekits",
                    "projectPath": "C:/project-a",
                },
                {
                    "id": "python-project@laxpud-vibekits",
                    "version": "1.1.1",
                    "scope": "project",
                    "enabled": False,
                    "installPath": "C:/cache/vibekits",
                    "projectPath": "C:/project-b",
                },
            ]
        )
        adapter = ClaudeAdapter(
            QueueRunner([output]), target=TARGET, env={"CLAUDE_CONFIG_DIR": "temp"}
        )

        instances = adapter.list_instances()

        self.assertEqual(["C:/project-a", "C:/project-b"], [item.project_path for item in instances])
        self.assertEqual([True, False], [item.enabled for item in instances])
        self.assertEqual(
            ["laxpud-vibekits", "laxpud-vibekits"],
            [item.source for item in instances],
        )

    def test_updates_each_scope_from_its_project_directory(self) -> None:
        runner = QueueRunner(["", "", ""])
        adapter = ClaudeAdapter(
            runner, target=TARGET, env={"CLAUDE_CONFIG_DIR": "temp"}
        )

        adapter.update_plugin_scopes(
            [("project", "C:/project-a"), ("local", "C:/project-b")]
        )

        self.assertEqual(
            ("claude", "plugin", "marketplace", "update", "laxpud-vibekits"),
            runner.calls[0][0],
        )
        self.assertEqual(Path("C:/project-a"), runner.calls[1][1])
        self.assertIn("python-project@laxpud-vibekits", runner.calls[1][0])
        self.assertIn("project", runner.calls[1][0])
        self.assertEqual(Path("C:/project-b"), runner.calls[2][1])
        self.assertIn("local", runner.calls[2][0])

    def test_rejects_install_without_pyproject_standard_skill(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            install_path = Path(directory)
            output = json.dumps(
                [
                    {
                        "id": "python-project@laxpud-vibekits",
                        "version": "1.1.1",
                        "scope": "user",
                        "enabled": True,
                        "installPath": str(install_path),
                    }
                ]
            )
            adapter = ClaudeAdapter(QueueRunner([output]), target=TARGET)
            artifact = Artifact(
                "origin/main",
                "b" * 40,
                "1.1.1",
                digest_directory(install_path),
            )

            with self.assertRaisesRegex(ValueError, "pyproject-standard"):
                adapter.verify_targets(artifact)

    def test_baseline_uses_historical_skills_but_target_requires_full_set(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            install_path = Path(directory)
            bootstrap = install_path / "skills/project-docs-bootstrap/SKILL.md"
            bootstrap.parent.mkdir(parents=True)
            bootstrap.write_text("bootstrap", encoding="utf-8")
            output = json.dumps(
                [
                    {
                        "id": "project-docs@laxpud-vibekits",
                        "version": "1.0.0",
                        "scope": "user",
                        "enabled": True,
                        "installPath": str(install_path),
                    }
                ]
            )
            adapter = ClaudeAdapter(
                QueueRunner([output, output]), target=MULTI_SKILL_TARGET
            )
            artifact = Artifact(
                "old", "a" * 40, "1.0.0", digest_directory(install_path)
            )

            adapter.verify_baseline(artifact)
            with self.assertRaisesRegex(ValueError, "project-docs-planning"):
                adapter.verify_targets(artifact)


if __name__ == "__main__":
    unittest.main()
