from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.plugin_update_flow.models import Artifact, Installation
from scripts.plugin_update_flow.workflow import (
    IsolatedHomes,
    PromotionError,
    StateSnapshot,
    run_isolated_upgrade,
    run_promotion,
)


class FakeChannel:
    def __init__(self) -> None:
        self.events: list[str] = []

    def create(self) -> None:
        self.events.append("create")

    def advance(self) -> None:
        self.events.append("advance")

    def cleanup(self) -> None:
        self.events.append("cleanup")


class CleanupFailChannel(FakeChannel):
    def cleanup(self) -> None:
        super().cleanup()
        raise RuntimeError("remote branch cleanup failed")


class FakeCodex:
    def __init__(self) -> None:
        self.events: list[str] = []

    def add_marketplace(self, source: str, branch: str) -> None:
        self.events.append(f"marketplace:{source}:{branch}")

    def install_plugin(self) -> None:
        self.events.append("install")

    def update_plugin(self) -> None:
        self.events.append("update")

    def verify_baseline(self, artifact: Artifact) -> Installation:
        return self.verify_target(artifact)

    def verify_target(self, artifact: Artifact) -> Installation:
        self.events.append(f"verify:{artifact.version}")
        return Installation(
            "codex",
            "python-project@laxpud-vibekits",
            "laxpud-vibekits",
            artifact.version,
            True,
            Path("/plugin"),
            plugin_digest=artifact.plugin_digest,
        )

    def run_smoke(self, cwd: Path, schema_path: Path) -> dict[str, str]:
        self.events.append("smoke")
        return {"ok": "codex"}


class FakeClaude:
    def __init__(self, *, fail_smoke: bool = False) -> None:
        self.events: list[str] = []
        self.fail_smoke = fail_smoke

    def install_plugin(self, *, scope: str = "user", cwd: Path | None = None) -> None:
        self.events.append(f"install:{scope}")

    def update_plugin_scopes(self, scopes: list[tuple[str, str | None]]) -> None:
        self.events.append(f"update:{scopes!r}")

    def verify_baseline(self, artifact: Artifact) -> list[Installation]:
        return self.verify_targets(artifact)

    def verify_targets(self, artifact: Artifact) -> list[Installation]:
        self.events.append(f"verify:{artifact.version}")
        return [
            Installation(
                "claude",
                "python-project@laxpud-vibekits",
                "laxpud-vibekits",
                artifact.version,
                True,
                Path("/plugin"),
                scope="user",
                plugin_digest=artifact.plugin_digest,
            )
        ]

    def run_smoke(self, cwd: Path) -> dict[str, str]:
        self.events.append("smoke")
        if self.fail_smoke:
            raise ValueError("Claude smoke failed")
        return {"ok": "claude"}


class InterruptClaude(FakeClaude):
    def run_smoke(self, cwd: Path) -> dict[str, str]:
        raise KeyboardInterrupt()


class IsolatedHomesTests(unittest.TestCase):
    def test_partial_setup_failure_deletes_copied_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            real_codex = root / "real-codex"
            real_claude = root / "real-claude"
            real_codex.mkdir()
            real_claude.mkdir()
            (real_codex / "auth.json").write_text("codex-secret", encoding="utf-8")
            homes = IsolatedHomes(
                real_codex_home=real_codex,
                real_claude_home=real_claude,
                repository="Laxpud/my-awesome-vibekits",
                branch="automation/plugin-e2e/run-1",
                parent=root,
            )

            with self.assertRaisesRegex(FileNotFoundError, ".credentials.json"):
                homes.__enter__()

            self.assertFalse(homes.root.exists())

    def test_copies_only_credentials_and_writes_minimal_claude_settings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            real_codex = root / "real-codex"
            real_claude = root / "real-claude"
            real_codex.mkdir()
            real_claude.mkdir()
            (real_codex / "auth.json").write_text("codex-secret", encoding="utf-8")
            (real_codex / "config.toml").write_text("must-not-copy", encoding="utf-8")
            (real_claude / ".credentials.json").write_text(
                "claude-secret", encoding="utf-8"
            )
            (real_claude / "settings.json").write_text(
                "must-not-copy", encoding="utf-8"
            )

            with IsolatedHomes(
                real_codex_home=real_codex,
                real_claude_home=real_claude,
                repository="Laxpud/my-awesome-vibekits",
                branch="automation/plugin-e2e/run-1",
                parent=root,
            ) as homes:
                self.assertTrue((homes.codex_home / "auth.json").is_file())
                self.assertFalse((homes.codex_home / "config.toml").exists())
                settings = json.loads(
                    (homes.claude_home / "settings.json").read_text(encoding="utf-8")
                )
                source = settings["extraKnownMarketplaces"]["laxpud-vibekits"]["source"]
                self.assertEqual("automation/plugin-e2e/run-1", source["ref"])
                self.assertFalse((homes.claude_home / "plugins").exists())
                temporary_root = homes.root

            self.assertFalse(temporary_root.exists())


class IsolatedUpgradeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.baseline = Artifact("old", "a" * 40, "1.0.0", "sha256:old")
        self.target = Artifact("origin/main", "b" * 40, "1.1.0", "sha256:new")

    def test_runs_real_update_order_and_cleans_channel(self) -> None:
        channel = FakeChannel()
        codex = FakeCodex()
        claude = FakeClaude()

        result = run_isolated_upgrade(
            channel=channel,
            codex=codex,
            claude=claude,
            baseline=self.baseline,
            target=self.target,
            marketplace_source="Laxpud/my-awesome-vibekits",
            branch="automation/plugin-e2e/run-1",
            smoke_dir=Path("/smoke"),
            schema_path=Path("/schema.json"),
            run_skill_smoke=True,
        )

        self.assertEqual(["create", "advance", "cleanup"], channel.events)
        self.assertEqual(
            [
                "marketplace:Laxpud/my-awesome-vibekits:automation/plugin-e2e/run-1",
                "install",
                "verify:1.0.0",
                "update",
                "verify:1.1.0",
                "smoke",
            ],
            codex.events,
        )
        self.assertEqual("passed", result["codex"]["result"])
        self.assertEqual("passed", result["claude"]["result"])

    def test_skips_model_skill_smoke_by_default(self) -> None:
        channel = FakeChannel()
        codex = FakeCodex()
        claude = FakeClaude()

        result = run_isolated_upgrade(
            channel=channel,
            codex=codex,
            claude=claude,
            baseline=self.baseline,
            target=self.target,
            marketplace_source="Laxpud/my-awesome-vibekits",
            branch="automation/plugin-e2e/run-1",
            smoke_dir=Path("/smoke"),
            schema_path=Path("/schema.json"),
        )

        self.assertNotIn("smoke", codex.events)
        self.assertNotIn("smoke", claude.events)
        self.assertEqual("skipped", result["codex"]["smoke"]["result"])
        self.assertEqual("skipped", result["claude"]["smoke"]["result"])

    def test_cleans_channel_when_smoke_fails(self) -> None:
        channel = FakeChannel()

        with self.assertRaisesRegex(ValueError, "Claude smoke failed"):
            run_isolated_upgrade(
                channel=channel,
                codex=FakeCodex(),
                claude=FakeClaude(fail_smoke=True),
                baseline=self.baseline,
                target=self.target,
                marketplace_source="Laxpud/my-awesome-vibekits",
                branch="automation/plugin-e2e/run-1",
                smoke_dir=Path("/smoke"),
                schema_path=Path("/schema.json"),
                run_skill_smoke=True,
            )

        self.assertEqual("cleanup", channel.events[-1])

    def test_keyboard_interrupt_still_cleans_channel(self) -> None:
        channel = FakeChannel()

        with self.assertRaises(KeyboardInterrupt):
            run_isolated_upgrade(
                channel=channel,
                codex=FakeCodex(),
                claude=InterruptClaude(),
                baseline=self.baseline,
                target=self.target,
                marketplace_source="Laxpud/my-awesome-vibekits",
                branch="automation/plugin-e2e/run-1",
                smoke_dir=Path("/smoke"),
                schema_path=Path("/schema.json"),
                run_skill_smoke=True,
            )

        self.assertEqual("cleanup", channel.events[-1])

    def test_cleanup_failure_is_a_test_failure(self) -> None:
        channel = CleanupFailChannel()

        with self.assertRaisesRegex(RuntimeError, "cleanup failed"):
            run_isolated_upgrade(
                channel=channel,
                codex=FakeCodex(),
                claude=FakeClaude(),
                baseline=self.baseline,
                target=self.target,
                marketplace_source="Laxpud/my-awesome-vibekits",
                branch="automation/plugin-e2e/run-1",
                smoke_dir=Path("/smoke"),
                schema_path=Path("/schema.json"),
            )


class PromotionAdapter:
    def __init__(
        self,
        platform: str,
        before: list[Installation],
        after: list[Installation],
        *,
        fail_update: bool = False,
    ) -> None:
        self.platform = platform
        self.before = before
        self.after = after
        self.current = before
        self.fail_update = fail_update
        self.events: list[str] = []

    def list_instances(self) -> list[Installation]:
        return self.current

    def update_plugin(self) -> None:
        self.events.append("update")
        if self.fail_update:
            raise RuntimeError(f"{self.platform} update failed")
        self.current = self.after

    def update_plugin_scopes(self, scopes: list[tuple[str, str | None]]) -> None:
        self.events.append(f"update:{scopes!r}")
        if self.fail_update:
            raise RuntimeError(f"{self.platform} update failed")
        self.current = self.after

    def verify_target(self, artifact: Artifact) -> Installation:
        instance = self.current[0]
        if instance.version != artifact.version:
            raise ValueError("wrong version")
        return instance

    def verify_targets(self, artifact: Artifact) -> list[Installation]:
        if any(item.version != artifact.version for item in self.current):
            raise ValueError("wrong version")
        return self.current


class SnapshotDouble:
    def __init__(self, codex: PromotionAdapter, claude: PromotionAdapter) -> None:
        self.codex = codex
        self.claude = claude
        self.events: list[str] = []
        self.fail_restore = False

    def capture(self) -> None:
        self.events.append("capture")

    def restore(self) -> None:
        self.events.append("restore")
        if self.fail_restore:
            raise RuntimeError("restore failed")
        self.codex.current = self.codex.before
        self.claude.current = self.claude.before

    def cleanup(self) -> None:
        self.events.append("cleanup")


class PromotionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.target = Artifact("origin/main", "b" * 40, "1.1.0", "sha256:new")
        self.codex_before = [
            Installation(
                "codex",
                "python-project@laxpud-vibekits",
                "laxpud-vibekits",
                "1.0.0",
                True,
                Path("/codex"),
                plugin_digest="sha256:old",
            )
        ]
        self.codex_after = [
            Installation(
                **{
                    **self.codex_before[0].__dict__,
                    "version": "1.1.0",
                    "plugin_digest": "sha256:new",
                }
            )
        ]
        self.claude_before = [
            Installation(
                "claude",
                "python-project@laxpud-vibekits",
                "laxpud-vibekits",
                "1.0.0",
                True,
                Path("/claude-a"),
                scope="project",
                project_path="/project-a",
                plugin_digest="sha256:old",
            ),
            Installation(
                "claude",
                "python-project@laxpud-vibekits",
                "laxpud-vibekits",
                "1.0.0",
                False,
                Path("/claude-b"),
                scope="local",
                project_path="/project-b",
                plugin_digest="sha256:old",
            ),
        ]
        self.claude_after = [
            Installation(
                **{
                    **item.__dict__,
                    "version": "1.1.0",
                    "plugin_digest": "sha256:new",
                }
            )
            for item in self.claude_before
        ]

    def test_success_updates_all_scopes_and_cleans_snapshot(self) -> None:
        codex = PromotionAdapter("codex", self.codex_before, self.codex_after)
        claude = PromotionAdapter("claude", self.claude_before, self.claude_after)
        snapshot = SnapshotDouble(codex, claude)

        result = run_promotion(codex, claude, self.target, snapshot)

        self.assertEqual("passed", result["result"])
        self.assertEqual(["capture", "cleanup"], snapshot.events)
        self.assertIn("project", claude.events[0])
        self.assertIn("local", claude.events[0])

    def test_already_current_instances_are_idempotent_without_snapshot(self) -> None:
        codex = PromotionAdapter("codex", self.codex_after, self.codex_after)
        claude = PromotionAdapter("claude", self.claude_after, self.claude_after)
        snapshot = SnapshotDouble(codex, claude)

        result = run_promotion(codex, claude, self.target, snapshot)

        self.assertEqual("passed", result["result"])
        self.assertEqual([], codex.events)
        self.assertEqual([], claude.events)
        self.assertEqual([], snapshot.events)

    def test_half_failure_rolls_back_both_platforms(self) -> None:
        codex = PromotionAdapter("codex", self.codex_before, self.codex_after)
        claude = PromotionAdapter(
            "claude", self.claude_before, self.claude_after, fail_update=True
        )
        snapshot = SnapshotDouble(codex, claude)

        with self.assertRaises(PromotionError) as raised:
            run_promotion(codex, claude, self.target, snapshot)

        self.assertTrue(raised.exception.rollback_succeeded)
        self.assertEqual(self.codex_before, codex.current)
        self.assertEqual(["capture", "restore", "cleanup"], snapshot.events)

    def test_rollback_failure_preserves_snapshot(self) -> None:
        codex = PromotionAdapter("codex", self.codex_before, self.codex_after)
        claude = PromotionAdapter(
            "claude", self.claude_before, self.claude_after, fail_update=True
        )
        snapshot = SnapshotDouble(codex, claude)
        snapshot.fail_restore = True

        with self.assertRaises(PromotionError) as raised:
            run_promotion(codex, claude, self.target, snapshot)

        self.assertFalse(raised.exception.rollback_succeeded)
        self.assertNotIn("cleanup", snapshot.events)
        self.assertEqual(3, len(raised.exception.manual_commands))
        self.assertEqual(
            {None, "/project-a", "/project-b"},
            {item["cwd"] for item in raised.exception.manual_commands},
        )


class StateSnapshotTests(unittest.TestCase):
    def test_restores_files_directories_and_removes_new_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state_file = root / "state.json"
            state_dir = root / "marketplace"
            new_path = root / "created-during-update"
            state_file.write_text("before", encoding="utf-8")
            state_dir.mkdir()
            (state_dir / "value").write_text("before", encoding="utf-8")
            snapshot = StateSnapshot(
                root / "backup", [state_file, state_dir, new_path]
            )
            snapshot.capture()
            state_file.write_text("after", encoding="utf-8")
            (state_dir / "value").write_text("after", encoding="utf-8")
            new_path.mkdir()

            snapshot.restore()

            self.assertEqual("before", state_file.read_text(encoding="utf-8"))
            self.assertEqual(
                "before", (state_dir / "value").read_text(encoding="utf-8")
            )
            self.assertFalse(new_path.exists())


if __name__ == "__main__":
    unittest.main()
