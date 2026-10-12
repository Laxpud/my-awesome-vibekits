#!/usr/bin/env python3
"""验证 catalog、Codex marketplace、manifest 与 README 安装契约。"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.plugin_catalog import (
    CODEX_MARKETPLACE_PATH,
    CatalogError,
    PluginSpec,
    load_catalog,
)


README_PATHS = (Path("README.md"), Path("docs/README.cn.md"))


class SmokeTestError(RuntimeError):
    """表示 GitHub marketplace 安装链路中的可操作配置错误。"""


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise SmokeTestError(f"missing required file: {path}") from error
    except json.JSONDecodeError as error:
        raise SmokeTestError(
            f"invalid JSON: {path}:{error.lineno}:{error.colno}: {error.msg}"
        ) from error
    if not isinstance(value, dict):
        raise SmokeTestError(f"expected a JSON object: {path}")
    return value


def require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SmokeTestError(f"{field}: expected a non-empty string")
    return value.strip()


def repository_slug(repository_url: str) -> str:
    parsed = urlparse(repository_url)
    parts = [part for part in parsed.path.removesuffix(".git").split("/") if part]
    if parsed.scheme != "https" or parsed.netloc.lower() != "github.com" or len(parts) != 2:
        raise SmokeTestError(
            "manifest.repository: expected https://github.com/<owner>/<repo>"
        )
    return "/".join(parts)


def _entries(marketplace: dict[str, Any], path: Path) -> dict[str, dict[str, Any]]:
    raw_entries = marketplace.get("plugins")
    if not isinstance(raw_entries, list):
        raise SmokeTestError(f"{path}: plugins must be an array")
    entries: dict[str, dict[str, Any]] = {}
    for index, raw_entry in enumerate(raw_entries):
        field = f"{path}.plugins[{index}]"
        if not isinstance(raw_entry, dict):
            raise SmokeTestError(f"{field}: expected an object")
        name = require_string(raw_entry.get("name"), f"{field}.name")
        if name in entries:
            raise SmokeTestError(f"{field}.name: duplicate plugin ID {name!r}")
        entries[name] = raw_entry
    return entries


def _validate_plugin(
    root: Path,
    plugin: PluginSpec,
    entry: dict[str, Any],
    marketplace_path: Path,
    check_external: bool = False,
) -> tuple[str, str]:
    """逐条校验并在诊断中保留 marketplace、插件 ID 和字段。"""

    prefix = f"{marketplace_path}: plugin {plugin.id!r}"
    source = entry.get("source")
    if not isinstance(source, dict):
        raise SmokeTestError(f"{prefix}: source must be an object")
    if source != plugin.codex_source:
        raise SmokeTestError(
            f"{prefix}: source is {source!r}; expected {plugin.codex_source!r}"
        )

    policy = entry.get("policy")
    if not isinstance(policy, dict):
        raise SmokeTestError(f"{prefix}: policy must be an object")
    for field in ("installation", "authentication"):
        expected = plugin.codex[field]
        if policy.get(field) != expected:
            raise SmokeTestError(
                f"{prefix}: policy.{field} is {policy.get(field)!r}; expected {expected!r}"
            )
    if entry.get("category") != plugin.category:
        raise SmokeTestError(f"{prefix}: category does not match catalog")

    # 外部来源默认只检查引用；显式联网检查才读取独立仓库中的真实安装包。
    if plugin.github is not None:
        slug = plugin.github["repo"]
        if not check_external:
            return slug, f"{slug} (external source configured; payload not fetched)"
        with tempfile.TemporaryDirectory(prefix="codex-external-plugin-") as directory:
            plugin_root = Path(directory) / "plugin"
            clone_remote(source["url"], plugin.github.get("ref"), plugin_root)
            _validate_payload(plugin_root, plugin, prefix, slug, external=True)
        return slug, f"{slug} (external manifests and all skills verified)"

    source_path = require_string(source.get("path"), f"{prefix}: source.path")
    plugin_root = (root / source_path).resolve()
    try:
        plugin_root.relative_to(root.resolve())
    except ValueError as error:
        raise SmokeTestError(f"{prefix}: source.path escapes repository root") from error
    if plugin_root.name != plugin.id:
        raise SmokeTestError(f"{prefix}: plugin directory name does not match ID")
    slug = _validate_payload(plugin_root, plugin, prefix)
    return slug, str((plugin_root / ".codex-plugin/plugin.json").relative_to(root))


def _validate_payload(
    plugin_root: Path,
    plugin: PluginSpec,
    prefix: str,
    expected_slug: str | None = None,
    *,
    external: bool = False,
) -> str:
    """核对实际 manifest 和技能入口；外部仓库同时核对 Claude manifest。"""
    manifest = load_json(plugin_root / ".codex-plugin/plugin.json")
    expected_fields = {
        "name": plugin.id,
        "version": plugin.version,
        "description": plugin.description,
        "skills": "./skills/",
    }
    for field, expected in expected_fields.items():
        if manifest.get(field) != expected:
            raise SmokeTestError(
                f"{prefix}: manifest.{field} is {manifest.get(field)!r}; expected {expected!r}"
            )
    slug = repository_slug(
        require_string(manifest.get("repository"), f"{prefix}: manifest.repository")
    )
    if expected_slug is not None and slug != expected_slug:
        raise SmokeTestError(f"{prefix}: manifest.repository does not match source repository")
    if external:
        claude = load_json(plugin_root / ".claude-plugin/plugin.json")
        for field in ("name", "version", "description"):
            if claude.get(field) != expected_fields[field]:
                raise SmokeTestError(f"{prefix}: Claude manifest.{field} does not match catalog")
        claude_slug = repository_slug(require_string(
            claude.get("repository"), f"{prefix}: Claude manifest.repository"
        ))
        if claude_slug != slug:
            raise SmokeTestError(f"{prefix}: Claude manifest.repository does not match source repository")

    missing_skills = [
        skill for skill in plugin.required_skills if not (plugin_root / skill).is_file()
    ]
    if missing_skills:
        missing = ", ".join(str(skill) for skill in missing_skills)
        raise SmokeTestError(f"{prefix}: missing required skill(s): {missing}")
    for skill in plugin.required_skills:
        if not (plugin_root / skill).resolve().is_relative_to(plugin_root.resolve()):
            raise SmokeTestError(f"{prefix}: skill path escapes plugin root: {skill}")
    return slug


def validate_repository(
    root: Path, plugin_ids: list[str] | None = None, *, check_external: bool = False
) -> list[str]:
    """检查市场引用和 README；按需下载外部包，不写客户端安装配置。"""
    catalog = load_catalog(root)
    selected = catalog.select(plugin_ids)
    marketplace_path = CODEX_MARKETPLACE_PATH
    marketplace = load_json(root / marketplace_path)
    if marketplace.get("name") != catalog.marketplace_id:
        raise SmokeTestError(
            f"{marketplace_path}: name does not match catalog marketplace.id"
        )
    entries = _entries(marketplace, marketplace_path)
    expected_ids = {plugin.id for plugin in catalog.plugins}
    if set(entries) != expected_ids:
        missing = sorted(expected_ids - set(entries))
        extra = sorted(set(entries) - expected_ids)
        raise SmokeTestError(
            f"{marketplace_path}: plugin IDs differ from catalog; missing={missing}, extra={extra}"
        )

    # 安装命令始终添加聚合市场；外部插件各有自己的 repository。
    slug = repository_slug(catalog.publisher["repository"])
    checks: list[str] = []
    for plugin in selected:
        plugin_slug, manifest_path = _validate_plugin(
            root, plugin, entries[plugin.id], marketplace_path, check_external
        )
        if plugin.github is None and plugin_slug != slug:
            raise SmokeTestError(f"{plugin.id}: local manifest repository does not match marketplace repository")
        checks.append(f"{plugin.id}: marketplace resolves to {manifest_path}")

    install_command = f"codex plugin marketplace add {slug}"
    selected_ids = {plugin.id for plugin in selected}
    for readme_path in README_PATHS:
        try:
            content = (root / readme_path).read_text(encoding="utf-8")
        except FileNotFoundError as error:
            raise SmokeTestError(f"missing required file: {readme_path}") from error
        if install_command not in content:
            raise SmokeTestError(
                f"{readme_path}: missing install command {install_command!r}"
            )
        if not re.search(r"(?m)^/plugins\s*$", content):
            raise SmokeTestError(f"{readme_path}: must document /plugins")
        for plugin_id in selected_ids:
            if f"`{plugin_id}`" not in content:
                raise SmokeTestError(
                    f"{readme_path}: must name selectable plugin `{plugin_id}`"
                )
    checks.append("English and Chinese README files document all selected plugins")
    return checks


def repository_url(root: Path) -> str:
    return require_string(
        load_catalog(root).publisher.get("repository"), "publisher.repository"
    )


def clone_remote(url: str, ref: str | None, destination: Path) -> None:
    command = ["git", "clone", "--depth", "1"]
    if ref:
        command.extend(["--branch", ref])
    command.extend([url, str(destination)])
    try:
        subprocess.run(command, check=True, text=True, timeout=120)
    except FileNotFoundError as error:
        raise SmokeTestError("git is required for remote source checks") from error
    except subprocess.CalledProcessError as error:
        raise SmokeTestError(f"remote clone failed with exit code {error.returncode}") from error
    except subprocess.TimeoutExpired as error:
        raise SmokeTestError("remote clone timed out after 120 seconds") from error


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Smoke-test the multi-plugin Codex GitHub marketplace metadata."
    )
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--plugin", action="append", dest="plugins", metavar="ID")
    selection.add_argument("--all", action="store_true", help="validate every plugin")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--remote", action="store_true")
    parser.add_argument(
        "--check-external", action="store_true",
        help="clone external plugin sources and check both manifests and every skill",
    )
    parser.add_argument("--ref")
    args = parser.parse_args()
    if args.ref and not args.remote:
        parser.error("--ref requires --remote")
    return args


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    temporary: tempfile.TemporaryDirectory[str] | None = None
    try:
        target = root
        if args.remote:
            temporary = tempfile.TemporaryDirectory(prefix="codex-install-smoke-")
            target = Path(temporary.name) / "repository"
            clone_remote(repository_url(root), args.ref, target)
        checks = validate_repository(target, args.plugins, check_external=args.check_external)
        mode = "remote GitHub checkout" if args.remote else "local checkout"
        print(f"PASS: Codex install smoke test ({mode})")
        for check in checks:
            print(f"  - {check}")
        return 0
    except (SmokeTestError, CatalogError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    finally:
        if temporary is not None:
            temporary.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
