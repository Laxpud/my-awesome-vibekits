#!/usr/bin/env python3
"""从外部插件收录快照生成两端 marketplace，或显式拉取独立仓库元数据。"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.plugin_catalog import (
    CATALOG_PATH,
    CLAUDE_MARKETPLACE_PATH,
    CODEX_MARKETPLACE_PATH,
    CODEX_INTERFACE_METADATA_FIELDS,
    CatalogError,
    PluginCatalog,
    PluginSpec,
    load_catalog,
    parse_catalog,
)


class MetadataError(RuntimeError):
    """表示生成物与 catalog 不一致或无法安全更新。"""


def _json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def codex_display_metadata(catalog: PluginCatalog, plugin: PluginSpec) -> dict[str, Any]:
    """为市场生成安装前展示字段，不生成插件 manifest 或包内路径。"""

    publisher = catalog.publisher
    adapter = plugin.codex
    if plugin.manifest_metadata is not None:
        # 已拉取的外部快照使用实际发布者和 interface，不补回远端已删除的默认字段。
        return {
            "name": plugin.id,
            "version": plugin.version,
            "description": plugin.description,
            **plugin.manifest_metadata,
            "keywords": list(plugin.keywords),
            "interface": {
                field: adapter[field] for field in CODEX_INTERFACE_METADATA_FIELDS if field in adapter
            },
        }
    repository = f"https://github.com/{plugin.github['repo']}"
    return {
        "name": plugin.id,
        "version": plugin.version,
        "description": plugin.description,
        "author": {"name": publisher["name"], "url": publisher["url"]},
        "homepage": repository,
        "repository": repository,
        "license": publisher["license"],
        "keywords": list(plugin.keywords),
        "interface": {
            "displayName": adapter["displayName"],
            "shortDescription": adapter["shortDescription"],
            "longDescription": adapter["longDescription"],
            "developerName": publisher["name"],
            "category": plugin.category,
            "capabilities": ["Skills"],
            "websiteURL": repository,
            "defaultPrompt": adapter["defaultPrompt"],
            "brandColor": "#2563EB",
        },
    }


def codex_marketplace_entry(catalog: PluginCatalog, plugin: PluginSpec) -> dict[str, Any]:
    """生成安装来源；按 catalog 开关附带安装前可读取的展示元数据。"""

    entry = {
        "name": plugin.id,
        "source": plugin.codex_source,
        "policy": {
            "installation": plugin.codex["installation"],
            "authentication": plugin.codex["authentication"],
        },
        "category": plugin.category,
    }
    if not plugin.codex.get("marketplaceMetadata", False):
        return entry

    # 展示快照与安装来源同时进入市场条目；实际技能仍由独立仓库提供。
    entry.update(codex_display_metadata(catalog, plugin))
    return entry


def codex_marketplace(catalog: PluginCatalog) -> dict[str, Any]:
    return {
        "name": catalog.marketplace_id,
        "interface": {"displayName": catalog.marketplace["displayName"]},
        "plugins": [
            codex_marketplace_entry(catalog, plugin)
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
                "author": plugin.claude.get("author", {"name": catalog.publisher["name"]}),
                "source": plugin.source,
                "category": plugin.claude["category"],
                "tags": plugin.claude["tags"],
            }
            for plugin in catalog.plugins
        ],
    }


def generated_files(catalog: PluginCatalog) -> dict[Path, str]:
    """仅生成两份共享市场；选择插件不会裁掉兄弟条目。"""

    return {
        CODEX_MARKETPLACE_PATH: _json(codex_marketplace(catalog)),
        CLAUDE_MARKETPLACE_PATH: _json(claude_marketplace(catalog)),
    }


def check_generated(
    root: Path,
    catalog: PluginCatalog,
) -> list[str]:
    """核对两端市场与完整 catalog 是否一致，返回可操作的漂移诊断。"""
    errors: list[str] = []
    for relative_path, expected in generated_files(catalog).items():
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
) -> list[Path]:
    """只重写发生变化的两端市场，返回本轮实际变更路径。"""
    changed: list[Path] = []
    for relative_path, content in generated_files(catalog).items():
        path = root / relative_path
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == content:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        changed.append(relative_path)
    return changed


def sync_external_metadata(root: Path, plugins: tuple[PluginSpec, ...], write: bool) -> None:
    """预览外部快照及市场差异；显式写入时先准备全部文件，再替换生成物。"""

    from scripts.external_plugin_metadata import fetch_external_metadata

    # 1. 全部远端拉取成功并通过完整 catalog 校验后，才准备本地文件变更。
    data = fetch_external_metadata(root, plugins)
    catalog = parse_catalog(data)
    planned = {CATALOG_PATH: _json(data), **generated_files(catalog)}
    changes = {}
    for relative_path, content in planned.items():
        path = root / relative_path
        original = path.read_text(encoding="utf-8") if path.exists() else None
        if original != content:
            changes[relative_path] = (original, content)
            print("".join(difflib.unified_diff(
                (original or "").splitlines(keepends=True), content.splitlines(keepends=True),
                fromfile=f"a/{relative_path.as_posix()}", tofile=f"b/{relative_path.as_posix()}",
            )), end="")
    if not write:
        print(f"PREVIEW: {len(changes)} file(s) would change; rerun with --write to apply this selection")
        return

    # 2. 同目录临时文件验证所有目标可写；权限失败时还没有替换 catalog 或市场。
    staged: dict[Path, Path] = {}
    replaced: list[Path] = []
    try:
        for relative_path, (_, content) in changes.items():
            target = root / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", newline="", dir=target.parent,
                prefix=f".{target.name}.", suffix=".tmp", delete=False,
            ) as handle:
                staged[relative_path] = Path(handle.name)
                handle.write(content)
            if target.exists():
                os.chmod(staged[relative_path], target.stat().st_mode & 0o777)
        for relative_path, temporary_path in staged.items():
            temporary_path.replace(root / relative_path)
            replaced.append(relative_path)
    except OSError:
        # 替换过程中失败时恢复已经替换的文件；临时文件始终在 finally 中清理。
        for relative_path in reversed(replaced):
            original, _ = changes[relative_path]
            target = root / relative_path
            if original is None:
                target.unlink()
            else:
                target.write_text(original, encoding="utf-8", newline="")
        raise
    finally:
        for temporary_path in staged.values():
            temporary_path.unlink(missing_ok=True)
    for relative_path in changes:
        print(f"UPDATED: {relative_path.as_posix()}")
    print("PASS: external metadata and marketplaces are synchronized")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate or verify marketplaces from external plugin snapshots."
    )
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--plugin", action="append", dest="plugins", metavar="ID",
        help="select one plugin; repeat for multiple plugins",
    )
    selection.add_argument("--all", action="store_true", help="select every plugin")
    parser.add_argument("--write", action="store_true", help="rewrite generated files")
    parser.add_argument(
        "--fetch-external", action="store_true",
        help="fetch external manifests and preview catalog/marketplace changes; combine with --write to apply",
    )
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1],
        help="repository root",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    try:
        catalog = load_catalog(root)
        selected = catalog.select(args.plugins)
        if args.fetch_external:
            from scripts.external_plugin_metadata import ExternalMetadataError

            try:
                sync_external_metadata(root, selected, args.write)
            except ExternalMetadataError as error:
                raise MetadataError(str(error)) from error
            return 0
        if args.write:
            for path in write_generated(root, catalog):
                print(f"UPDATED: {path.as_posix()}")
        errors = check_generated(root, catalog)
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
