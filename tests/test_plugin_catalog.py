from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.plugin_catalog import CatalogError, load_catalog
from scripts.sync_plugin_metadata import check_generated, write_generated


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures"


class CatalogTests(unittest.TestCase):
    """沿用既有 catalog 检查，验证迁移后的市场契约。"""

    def test_production_catalog_contains_three_external_plugins(self) -> None:
        """市场只保存外部来源与十技能快照，不再携带可被发现的旧包。"""
        catalog = load_catalog(REPOSITORY_ROOT)
        expected_skills = {
            "agent-docs-maintainer": (
                "project-docs-bootstrap",
                "project-docs-refactor",
                "project-docs-readme",
                "project-docs-planning",
                "project-docs-architecture",
                "project-docs-guidance",
                "project-docs-progress",
            ),
            "agent-task-resume": ("quota-resume",),
            "agent-dev-standards": ("code-comment-standard", "pyproject-standard"),
        }
        self.assertEqual(list(expected_skills), [plugin.id for plugin in catalog.plugins])
        for plugin in catalog.plugins:
            self.assertEqual(f"Laxpud/{plugin.id}", plugin.github["repo"])
            self.assertEqual("main", plugin.github["ref"])
            self.assertEqual(expected_skills[plugin.id], tuple(skill.id for skill in plugin.skills))
            self.assertTrue(plugin.codex["marketplaceMetadata"])
        self.assertFalse((REPOSITORY_ROOT / "plugins").exists())
        self.assertFalse((REPOSITORY_ROOT / "sources").exists())

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
        """不同独立仓库也不能向同一市场发布冲突的技能 ID。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copyfile(FIXTURES / "catalog_skill_conflict.json", root / "plugin-catalog.json")
            with self.assertRaisesRegex(CatalogError, "conflicts with plugin"):
                load_catalog(root)

    def test_rejects_path_that_escapes_plugin_root(self) -> None:
        """技能路径仍相对于外部插件根目录，不因源码搬出而放宽边界。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copyfile(FIXTURES / "catalog_invalid_path.json", root / "plugin-catalog.json")
            with self.assertRaisesRegex(CatalogError, "stay inside"):
                load_catalog(root)

    def test_generation_is_idempotent_and_detects_manual_drift(self) -> None:
        """生成只写两份市场，并能发现绕过 catalog 的手动修改。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copyfile(REPOSITORY_ROOT / "plugin-catalog.json", root / "plugin-catalog.json")
            catalog = load_catalog(root)
            first = write_generated(root, catalog)
            self.assertEqual(
                {Path(".agents/plugins/marketplace.json"), Path(".claude-plugin/marketplace.json")},
                set(first),
            )
            self.assertEqual([], write_generated(root, catalog))
            self.assertEqual([], check_generated(root, catalog))

            marketplace = root / ".agents/plugins/marketplace.json"
            data = json.loads(marketplace.read_text(encoding="utf-8"))
            data["plugins"][0]["name"] = "manual-drift"
            marketplace.write_text(json.dumps(data), encoding="utf-8")
            errors = check_generated(root, catalog)
            self.assertEqual(1, len(errors))
            self.assertIn(".agents/plugins/marketplace.json", errors[0])
            self.assertIn("--write", errors[0])


if __name__ == "__main__":
    unittest.main()
