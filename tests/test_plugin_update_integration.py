from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.plugin_update_flow.claude_adapter import ClaudeAdapter
from scripts.plugin_update_flow.codex_adapter import CodexAdapter
from scripts.plugin_update_flow.git_channel import digest_directory
from scripts.plugin_update_flow.models import Artifact, PluginTarget
from scripts.plugin_update_flow.runtime import CommandRunner
from scripts.plugin_update_flow.smoke import SMOKE_SCHEMA
from scripts.plugin_update_flow.workflow import (
    PromotionError,
    StateSnapshot,
    run_isolated_upgrade,
    run_promotion,
)


class AdvancingFakeChannel:
    def __init__(self, state_path: Path) -> None:
        self.state_path = state_path
        self.events: list[str] = []

    def create(self) -> None:
        self.events.append("create")

    def advance(self) -> None:
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        state["phase"] = "new"
        self.state_path.write_text(json.dumps(state), encoding="utf-8")
        self.events.append("advance")

    def cleanup(self) -> None:
        self.events.append("cleanup")


class FakeCliIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.old_payload = self.root / "old-payload"
        self.target_payload = self.root / "target-payload"
        self.old_payload.mkdir()
        self.target_payload.mkdir()
        (self.old_payload / "payload.txt").write_text("old", encoding="utf-8")
        (self.target_payload / "payload.txt").write_text("new", encoding="utf-8")
        for payload in (self.old_payload, self.target_payload):
            for skill_id in (
                "code-comment-standard",
                "pyproject-standard",
                "project-docs-bootstrap",
            ):
                skill = payload / f"skills/{skill_id}/SKILL.md"
                skill.parent.mkdir(parents=True)
                skill.write_text(f"---\nname: {skill_id}\n---\n", encoding="utf-8")
        self.state_path = self.root / "state.json"
        self.install_root = self.root / "installs"
        self.env = {
            "FAKE_PLUGIN_STATE": str(self.state_path),
            "FAKE_OLD_PAYLOAD": str(self.old_payload),
            "FAKE_TARGET_PAYLOAD": str(self.target_payload),
            "FAKE_OLD_VERSION": "1.0.0",
            "FAKE_TARGET_VERSION": "1.1.0",
            "FAKE_INSTALL_ROOT": str(self.install_root),
        }
        fixture = Path(__file__).parent / "fixtures/fake_plugin_cli.py"
        runner = CommandRunner(timeout=10)
        self.plugin_target = PluginTarget(
            "python-project",
            "laxpud-vibekits",
            Path("skills/pyproject-standard/SKILL.md"),
            "github.com/laxpud/my-awesome-vibekits",
        )
        self.codex = CodexAdapter(
            runner,
            target=self.plugin_target,
            env=self.env,
            command=(sys.executable, str(fixture), "codex"),
        )
        self.claude = ClaudeAdapter(
            runner,
            target=self.plugin_target,
            env=self.env,
            command=(sys.executable, str(fixture), "claude"),
        )
        self.baseline = Artifact(
            "old", "a" * 40, "1.0.0", digest_directory(self.old_payload)
        )
        self.target = Artifact(
            "target", "b" * 40, "1.1.0", digest_directory(self.target_payload)
        )

    def _adapters(self, plugin_id: str, skill_id: str) -> tuple[CodexAdapter, ClaudeAdapter]:
        target = PluginTarget(
            plugin_id,
            "laxpud-vibekits",
            Path(f"skills/{skill_id}/SKILL.md"),
            "github.com/laxpud/my-awesome-vibekits",
        )
        fixture = Path(__file__).parent / "fixtures/fake_plugin_cli.py"
        runner = CommandRunner(timeout=10)
        command = (sys.executable, str(fixture))
        return (
            CodexAdapter(runner, target=target, env=self.env, command=(*command, "codex")),
            ClaudeAdapter(runner, target=target, env=self.env, command=(*command, "claude")),
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_old_install_advances_updates_and_smokes_on_both_platforms(self) -> None:
        schema_path = self.root / "schema.json"
        schema_path.write_text(json.dumps(SMOKE_SCHEMA), encoding="utf-8")
        smoke_dir = self.root / "empty-smoke"
        smoke_dir.mkdir()
        channel = AdvancingFakeChannel(self.state_path)

        result = run_isolated_upgrade(
            channel=channel,
            codex=self.codex,
            claude=self.claude,
            baseline=self.baseline,
            target=self.target,
            marketplace_source="Laxpud/my-awesome-vibekits",
            branch="automation/plugin-e2e/fake",
            smoke_dir=smoke_dir,
            schema_path=schema_path,
            run_skill_smoke=True,
        )

        self.assertEqual("passed", result["codex"]["result"])
        self.assertEqual("passed", result["claude"]["result"])
        self.assertEqual(["create", "advance", "cleanup"], channel.events)
        self.assertEqual("1.1.0", self.codex.list_instances()[0].version)
        self.assertEqual("1.1.0", self.claude.list_instances()[0].version)

    def test_partial_promotion_failure_restores_both_fake_clients(self) -> None:
        project_a = self.root / "project-a"
        project_b = self.root / "project-b"
        project_a.mkdir()
        project_b.mkdir()
        self.codex.add_marketplace("Laxpud/my-awesome-vibekits", "old")
        self.codex.install_plugin()
        self.claude.install_plugin(scope="project", cwd=project_a)
        self.claude.install_plugin(scope="local", cwd=project_b)
        failing_claude = ClaudeAdapter(
            self.claude.runner,
            target=self.plugin_target,
            env={**self.env, "FAKE_CLAUDE_FAIL_SCOPE": "local"},
            command=self.claude.command,
        )
        snapshot = StateSnapshot(
            self.root / "backup", [self.state_path, self.install_root]
        )

        with self.assertRaises(PromotionError) as raised:
            run_promotion(self.codex, failing_claude, self.target, snapshot)

        self.assertTrue(raised.exception.rollback_succeeded)
        self.assertEqual("1.0.0", self.codex.list_instances()[0].version)
        self.assertEqual(
            ["1.0.0", "1.0.0"],
            [item.version for item in self.claude.list_instances()],
        )
        self.assertFalse((self.root / "backup").exists())

    def test_three_plugins_have_independent_lifecycles_and_rollback(self) -> None:
        adapters = {
            "code-quality": self._adapters("code-quality", "code-comment-standard"),
            "python-project": self._adapters("python-project", "pyproject-standard"),
            "project-docs": self._adapters("project-docs", "project-docs-bootstrap"),
        }
        first_codex, _ = adapters["code-quality"]
        first_codex.add_marketplace("Laxpud/my-awesome-vibekits", "old")
        for codex, claude in adapters.values():
            codex.install_plugin()
            claude.install_plugin()

        # 1. Claude CLI 启停和双端卸载只作用于选中插件；Codex 的启停入口在
        #    `/plugins` 交互界面，自动化适配器不得伪造不存在的 CLI 子命令。
        code_codex, code_claude = adapters["code-quality"]
        code_claude.set_enabled(False)
        self.assertFalse(code_claude.list_instances()[0].enabled)
        self.assertTrue(code_codex.list_instances()[0].enabled)
        self.assertTrue(adapters["python-project"][0].list_instances()[0].enabled)
        self.assertTrue(adapters["project-docs"][1].list_instances()[0].enabled)
        code_claude.set_enabled(True)

        docs_codex, docs_claude = adapters["project-docs"]
        docs_codex.uninstall_plugin()
        docs_claude.uninstall_plugin()
        self.assertEqual([], docs_codex.list_instances())
        self.assertEqual([], docs_claude.list_instances())
        self.assertEqual(1, adapters["code-quality"][0].list_instances().__len__())
        docs_codex.install_plugin()
        docs_claude.install_plugin()

        # 2. 只升级 python-project，再回滚到旧 payload；其他插件版本始终不变。
        python_codex, python_claude = adapters["python-project"]
        python_codex.update_plugin()
        python_claude.update_plugin_scopes([("user", None)])
        self.assertEqual("1.1.0", python_codex.list_instances()[0].version)
        self.assertEqual("1.1.0", python_claude.list_instances()[0].version)
        self.assertEqual("1.0.0", code_codex.list_instances()[0].version)
        self.assertEqual("1.0.0", docs_claude.list_instances()[0].version)

        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        state["phase"] = "old"
        self.state_path.write_text(json.dumps(state), encoding="utf-8")
        python_codex.install_plugin()
        python_claude.install_plugin()
        self.assertEqual("1.0.0", python_codex.list_instances()[0].version)
        self.assertEqual("1.0.0", python_claude.list_instances()[0].version)
        self.assertEqual("1.0.0", code_codex.list_instances()[0].version)
        self.assertEqual("1.0.0", docs_codex.list_instances()[0].version)


if __name__ == "__main__":
    unittest.main()
