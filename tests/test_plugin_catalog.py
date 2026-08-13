from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.plugin_catalog import CatalogError, load_catalog
from scripts.sync_plugin_metadata import check_generated, set_versions, write_generated


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures"


class CatalogTests(unittest.TestCase):
    def test_production_catalog_contains_three_self_contained_plugins(self) -> None:
        catalog = load_catalog(REPOSITORY_ROOT)

        self.assertEqual(
            ["code-quality", "python-project", "project-docs"],
            [plugin.id for plugin in catalog.plugins],
        )
        for plugin in catalog.plugins:
            plugin_root = REPOSITORY_ROOT / Path(plugin.directory.as_posix())
            self.assertEqual(1, len(plugin.skills))
            self.assertTrue((plugin_root / plugin.required_skill).is_file())
            self.assertTrue((plugin_root / ".codex-plugin/plugin.json").is_file())
            self.assertTrue((plugin_root / ".claude-plugin/plugin.json").is_file())
        self.assertFalse((REPOSITORY_ROOT / "plugins/laxpud-vibekits").exists())

    def test_production_scripts_have_no_single_plugin_shortcuts(self) -> None:
        forbidden = (
            "plugins[0]",
            "len(plugins) == 1",
            "plugins/laxpud-vibekits",
            'PLUGIN_NAME = "',
            'MARKETPLACE_NAME = "',
        )
        for path in (REPOSITORY_ROOT / "scripts").rglob("*.py"):
            content = path.read_text(encoding="utf-8")
            for fragment in forbidden:
                self.assertNotIn(fragment, content, f"{path}: {fragment}")

    def test_rejects_same_skill_id_across_two_plugins(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copyfile(
                FIXTURES / "catalog_skill_conflict.json",
                root / "plugin-catalog.json",
            )
            for plugin_id in ("first-plugin", "second-plugin"):
                skill = root / f"plugins/{plugin_id}/skills/shared-name/SKILL.md"
                skill.parent.mkdir(parents=True)
                skill.write_text("---\nname: shared-name\n---\n", encoding="utf-8")

            with self.assertRaisesRegex(CatalogError, "conflicts with plugin"):
                load_catalog(root)

    def test_rejects_path_that_escapes_plugin_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copyfile(
                FIXTURES / "catalog_invalid_path.json",
                root / "plugin-catalog.json",
            )

            with self.assertRaisesRegex(CatalogError, "stay inside"):
                load_catalog(root)

    def test_generation_is_idempotent_and_detects_manual_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copyfile(REPOSITORY_ROOT / "plugin-catalog.json", root / "plugin-catalog.json")
            for source in (REPOSITORY_ROOT / "plugins").iterdir():
                if source.name in {"code-quality", "python-project", "project-docs"}:
                    shutil.copytree(source, root / "plugins" / source.name)
            catalog = load_catalog(root)

            first = write_generated(root, catalog)
            second = write_generated(root, catalog)
            self.assertTrue(first)
            self.assertEqual([], second)
            self.assertEqual([], check_generated(root, catalog))

            manifest = root / "plugins/python-project/.codex-plugin/plugin.json"
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["name"] = "manual-drift"
            manifest.write_text(json.dumps(data), encoding="utf-8")

            errors = check_generated(root, catalog)
            self.assertEqual(1, len(errors))
            self.assertIn("python-project", errors[0])
            self.assertIn("--write", errors[0])

    def test_version_update_changes_only_selected_plugin(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copyfile(REPOSITORY_ROOT / "plugin-catalog.json", root / "plugin-catalog.json")
            for source in (REPOSITORY_ROOT / "plugins").iterdir():
                if source.name in {"code-quality", "python-project", "project-docs"}:
                    shutil.copytree(source, root / "plugins" / source.name)
            catalog = load_catalog(root)

            set_versions(root, catalog, catalog.select(["python-project"]), "2.0.0")
            updated = load_catalog(root)

            self.assertEqual(
                {
                    "code-quality": "1.1.2",
                    "python-project": "2.0.0",
                    "project-docs": "1.1.2",
                },
                {plugin.id: plugin.version for plugin in updated.plugins},
            )

    def test_selected_write_does_not_repair_a_sibling_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copyfile(REPOSITORY_ROOT / "plugin-catalog.json", root / "plugin-catalog.json")
            for source in (REPOSITORY_ROOT / "plugins").iterdir():
                if source.name in {"code-quality", "python-project", "project-docs"}:
                    shutil.copytree(source, root / "plugins" / source.name)
            (root / ".agents/plugins").mkdir(parents=True)
            (root / ".claude-plugin").mkdir(parents=True)
            shutil.copyfile(
                REPOSITORY_ROOT / ".agents/plugins/marketplace.json",
                root / ".agents/plugins/marketplace.json",
            )
            shutil.copyfile(
                REPOSITORY_ROOT / ".claude-plugin/marketplace.json",
                root / ".claude-plugin/marketplace.json",
            )
            catalog = load_catalog(root)
            selected = catalog.select(["python-project"])
            sibling = root / "plugins/code-quality/.codex-plugin/plugin.json"
            target = root / "plugins/python-project/.codex-plugin/plugin.json"
            sibling.write_text("{}\n", encoding="utf-8")
            target.write_text("{}\n", encoding="utf-8")

            changed = write_generated(root, catalog, selected)

            self.assertIn(
                Path("plugins/python-project/.codex-plugin/plugin.json"), changed
            )
            self.assertNotIn(
                Path("plugins/code-quality/.codex-plugin/plugin.json"), changed
            )
            self.assertEqual("{}\n", sibling.read_text(encoding="utf-8"))
            self.assertEqual([], check_generated(root, catalog, selected))
            self.assertTrue(check_generated(root, catalog))


if __name__ == "__main__":
    unittest.main()
