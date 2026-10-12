#!/usr/bin/env python3
"""从统一 catalog 生成或校验 Codex/Claude marketplace 与 manifest。"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.plugin_catalog import (
    CATALOG_PATH,
    CLAUDE_MARKETPLACE_PATH,
    CODEX_MARKETPLACE_PATH,
    CODEX_INTERFACE_METADATA_FIELDS,
    SEMVER_PATTERN,
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


def codex_manifest(catalog: PluginCatalog, plugin: PluginSpec) -> dict[str, Any]:
    """生成 Codex 专属 manifest；通用 Skill 内容保持在插件 skills/ 中。"""

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
            "skills": "./skills/",
            "interface": {
                field: adapter[field] for field in CODEX_INTERFACE_METADATA_FIELDS if field in adapter
            },
        }
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

    # 1. 复用 catalog 中的文案与发布者信息；市场只携带元数据，不声明本地技能路径。
    metadata = codex_manifest(catalog, plugin)
    metadata.pop("skills")

    # 2. 外部插件的网站和仓库链接属于独立仓库，不能沿用聚合市场的 publisher 链接。
    if plugin.github is not None and plugin.manifest_metadata is None:
        repository = f"https://github.com/{plugin.github['repo']}"
        metadata["homepage"] = repository
        metadata["repository"] = repository
        metadata["interface"]["websiteURL"] = repository
    entry.update(metadata)
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


def generated_files(
    root: Path,
    catalog: PluginCatalog,
    plugins: Iterable[PluginSpec] | None = None,
) -> dict[Path, str]:
    """生成共享市场与本地插件 manifest；外部 manifest 由各独立仓库维护。"""

    files = {
        CODEX_MARKETPLACE_PATH: _json(codex_marketplace(catalog)),
        CLAUDE_MARKETPLACE_PATH: _json(claude_marketplace(catalog)),
    }
    selected = catalog.plugins if plugins is None else tuple(plugins)
    for plugin in selected:
        if plugin.directory is None:
            continue
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
    if any(plugin.github is not None for plugin in plugins):
        raise MetadataError("external plugin versions must be released in their own repositories; update the catalog snapshot afterwards")
    path = root / CATALOG_PATH
    data = json.loads(path.read_text(encoding="utf-8"))
    selected = {plugin.id for plugin in plugins}
    for item in data["plugins"]:
        if item["id"] in selected:
            item["version"] = version
    path.write_text(_json(data), encoding="utf-8")


def sync_external_metadata(root: Path, plugins: tuple[PluginSpec, ...], write: bool) -> None:
    """预览外部快照及市场差异；显式写入时先准备全部文件，再替换生成物。"""

    from scripts.external_plugin_metadata import fetch_external_metadata

    # 1. 全部远端拉取成功并通过完整 catalog 校验后，才准备本地文件变更。
    data = fetch_external_metadata(root, plugins)
    catalog = parse_catalog(root, data)
    planned = {CATALOG_PATH: _json(data), **generated_files(root, catalog, ())}
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
        "--fetch-external", action="store_true",
        help="fetch external manifests and preview catalog/marketplace changes; combine with --write to apply",
    )
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1],
        help="repository root",
    )
    args = parser.parse_args()
    if args.set_version and not (args.plugins or args.all):
        parser.error("--set-version requires --plugin or --all")
    if args.fetch_external and args.set_version:
        parser.error("--fetch-external cannot be combined with --set-version")
    return args


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
