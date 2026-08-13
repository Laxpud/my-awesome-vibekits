#!/usr/bin/env python3
"""从统一 catalog 生成或校验 Codex/Claude marketplace 与 manifest。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.plugin_catalog import (
    CATALOG_PATH,
    CLAUDE_MARKETPLACE_PATH,
    CODEX_MARKETPLACE_PATH,
    SEMVER_PATTERN,
    CatalogError,
    PluginCatalog,
    PluginSpec,
    load_catalog,
)


class MetadataError(RuntimeError):
    """表示生成物与 catalog 不一致或无法安全更新。"""


def _json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def codex_manifest(catalog: PluginCatalog, plugin: PluginSpec) -> dict[str, Any]:
    """生成 Codex 专属 manifest；通用 Skill 内容保持在插件 skills/ 中。"""

    publisher = catalog.publisher
    adapter = plugin.codex
    return {
        "name": plugin.id,
        "version": plugin.version,
        "description": plugin.description,
        "author": {"name": publisher["name"], "url": publisher["url"]},
        "homepage": publisher["homepage"],
        "repository": publisher["repository"],
        "license": publisher["license"],
        "keywords": list(plugin.keywords),
        "skills": "./skills/",
        "interface": {
            "displayName": adapter["displayName"],
            "shortDescription": adapter["shortDescription"],
            "longDescription": adapter["longDescription"],
            "developerName": publisher["name"],
            "category": plugin.category,
            "capabilities": ["Skills"],
            "websiteURL": publisher["homepage"],
            "defaultPrompt": adapter["defaultPrompt"],
            "brandColor": "#2563EB",
        },
    }


def claude_manifest(catalog: PluginCatalog, plugin: PluginSpec) -> dict[str, Any]:
    return {
        "name": plugin.id,
        "description": plugin.description,
        "version": plugin.version,
        "author": {"name": catalog.publisher["name"]},
        "homepage": catalog.publisher["homepage"],
        "repository": catalog.publisher["repository"],
        "license": catalog.publisher["license"],
        "keywords": list(plugin.keywords),
        "skills": ["./skills/"],
    }


def codex_marketplace(catalog: PluginCatalog) -> dict[str, Any]:
    return {
        "name": catalog.marketplace_id,
        "interface": {"displayName": catalog.marketplace["displayName"]},
        "plugins": [
            {
                "name": plugin.id,
                "source": {"source": "local", "path": plugin.source},
                "policy": {
                    "installation": plugin.codex["installation"],
                    "authentication": plugin.codex["authentication"],
                },
                "category": plugin.category,
            }
            for plugin in catalog.plugins
        ],
    }


def claude_marketplace(catalog: PluginCatalog) -> dict[str, Any]:
    return {
        "name": catalog.marketplace_id,
        "description": catalog.marketplace["description"],
        "owner": {"name": catalog.marketplace["owner"]},
        "plugins": [
            {
                "name": plugin.id,
                "description": plugin.description,
                "version": plugin.version,
                "author": {"name": catalog.publisher["name"]},
                "source": plugin.source,
                "category": plugin.claude["category"],
                "tags": plugin.claude["tags"],
            }
            for plugin in catalog.plugins
        ],
    }


def generated_files(
    root: Path,
    catalog: PluginCatalog,
    plugins: Iterable[PluginSpec] | None = None,
) -> dict[Path, str]:
    """返回共享 marketplace 与选中插件 manifest 的稳定生成物。"""

    files = {
        CODEX_MARKETPLACE_PATH: _json(codex_marketplace(catalog)),
        CLAUDE_MARKETPLACE_PATH: _json(claude_marketplace(catalog)),
    }
    selected = catalog.plugins if plugins is None else tuple(plugins)
    for plugin in selected:
        plugin_root = Path(plugin.directory.as_posix())
        files[plugin_root / ".codex-plugin/plugin.json"] = _json(
            codex_manifest(catalog, plugin)
        )
        files[plugin_root / ".claude-plugin/plugin.json"] = _json(
            claude_manifest(catalog, plugin)
        )
    return files


def check_generated(
    root: Path,
    catalog: PluginCatalog,
    plugins: Iterable[PluginSpec] | None = None,
) -> list[str]:
    errors: list[str] = []
    for relative_path, expected in generated_files(root, catalog, plugins).items():
        path = root / relative_path
        try:
            actual = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            errors.append(f"{relative_path}: missing generated file; run with --write")
            continue
        if actual != expected:
            errors.append(f"{relative_path}: differs from catalog; run with --write")
    return errors


def write_generated(
    root: Path,
    catalog: PluginCatalog,
    plugins: Iterable[PluginSpec] | None = None,
) -> list[Path]:
    changed: list[Path] = []
    for relative_path, content in generated_files(root, catalog, plugins).items():
        path = root / relative_path
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == content:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        changed.append(relative_path)
    return changed


def set_versions(
    root: Path, catalog: PluginCatalog, plugins: tuple[PluginSpec, ...], version: str
) -> None:
    """只改选中插件的 catalog 版本，兄弟插件保持独立。"""

    if not SEMVER_PATTERN.fullmatch(version):
        raise MetadataError(f"version must be SemVer without a 'v' prefix: {version!r}")
    path = root / CATALOG_PATH
    data = json.loads(path.read_text(encoding="utf-8"))
    selected = {plugin.id for plugin in plugins}
    for item in data["plugins"]:
        if item["id"] in selected:
            item["version"] = version
    path.write_text(_json(data), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate or verify all plugin metadata from plugin-catalog.json."
    )
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--plugin", action="append", dest="plugins", metavar="ID",
        help="select one plugin; repeat for multiple plugins",
    )
    selection.add_argument("--all", action="store_true", help="select every plugin")
    parser.add_argument("--write", action="store_true", help="rewrite generated files")
    parser.add_argument("--set-version", metavar="SEMVER", help="set selected version")
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1],
        help="repository root",
    )
    args = parser.parse_args()
    if args.set_version and not (args.plugins or args.all):
        parser.error("--set-version requires --plugin or --all")
    return args


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    try:
        catalog = load_catalog(root)
        selected = catalog.select(args.plugins)
        if args.set_version:
            set_versions(root, catalog, selected, args.set_version)
            catalog = load_catalog(root)
        if args.write or args.set_version:
            for path in write_generated(root, catalog, selected):
                print(f"UPDATED: {path.as_posix()}")
        errors = check_generated(root, catalog, selected)
        if errors:
            for error in errors:
                print(f"FAIL: {error}", file=sys.stderr)
            return 1
        labels = ", ".join(f"{item.id}@{item.version}" for item in selected)
        print(f"PASS: catalog and generated metadata are synchronized ({labels})")
        return 0
    except (CatalogError, MetadataError, OSError, KeyError, TypeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
