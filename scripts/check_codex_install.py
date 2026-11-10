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


def git_output(root: Path, *arguments: str) -> str:
    """在临时 checkout 中执行 Git 并返回输出；失败转换为维护脚本诊断。"""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *arguments], check=True,
            capture_output=True, text=True, timeout=120,
        )
    except FileNotFoundError as error:
        raise SmokeTestError("git is required for remote source checks") from error
    except subprocess.CalledProcessError as error:
        raise SmokeTestError(f"git {arguments[0]} failed: {error.stderr.strip()}") from error
    except subprocess.TimeoutExpired as error:
        raise SmokeTestError(f"git {arguments[0]} timed out after 120 seconds") from error
    return result.stdout.strip()


def validate_dsh_package(
    package_root: Path, name: str, version: str, expected_engine: str | None = None,
) -> dict[str, Any]:
    """读取 DSH 包声明并核对身份、版本、范围与 patch，不执行包内代码。

    expected_engine 只用于固定发布记录；分支或本地开发快照只检查声明完整性，
    不把未发布的兼容变更误当成历史版本应有的范围。
    """
    package_file = package_root / "package.json"
    if not package_file.resolve().is_relative_to(package_root.resolve()):
        raise SmokeTestError("DSH package.json escapes package root")
    package = load_json(package_file)
    if package.get("name") != name or package.get("version") != version:
        raise SmokeTestError(f"DSH package identity/version differs: expected {name}@{version}")
    engines = package.get("engines")
    if not isinstance(engines, dict):
        raise SmokeTestError("DSH package.engines: expected an object")
    require_string(engines.get("dsh"), "DSH package.engines.dsh")
    if expected_engine is not None and engines["dsh"] != expected_engine:
        raise SmokeTestError("DSH package engines differ from release record")
    dsh = package.get("dsh")
    bundle = dsh.get("bundle") if isinstance(dsh, dict) else None
    patch = bundle.get("patch") if isinstance(bundle, dict) else None
    patch = require_string(patch, "DSH package.dsh.bundle.patch")
    target = (package_root / patch).resolve()
    if not target.is_relative_to(package_root.resolve()) or not target.is_file():
        raise SmokeTestError("DSH bundle patch is missing or escapes package root")
    return package


def validate_dsh_releases(plugin: PluginSpec, checkout: Path) -> None:
    """逐条核对固定 commit 中的 DSH 包，完成后恢复临时 checkout 的原 HEAD。

    调用者只能传入可丢弃的远端 clone，不能传日常源码或本地覆盖目录。
    历史包按各自 source.path 定位，不使用分支最新包替代，也不核对当前技能清单。
    """
    if plugin.dsh is None or not plugin.dsh["versions"]:
        return
    original = git_output(checkout, "rev-parse", "HEAD")
    try:
        for release in plugin.dsh["versions"]:
            source = release["source"]
            commit = source["commit"]
            try:
                # 浅克隆可能不含历史对象；显式拉取 SHA 后再次验证，不能退回 main。
                if git_output(checkout, "rev-parse", "HEAD") != commit:
                    git_output(checkout, "fetch", "--depth", "1", source["url"], commit)
                    git_output(checkout, "checkout", "--detach", commit)
                if git_output(checkout, "rev-parse", "HEAD") != commit:
                    raise SmokeTestError("DSH checkout does not match release commit")
                package_root = (checkout / source.get("path", "")).resolve()
                if not package_root.is_relative_to(checkout.resolve()):
                    raise SmokeTestError("DSH source.path escapes checkout")
                validate_dsh_package(
                    package_root, plugin.dsh["name"], release["version"], release["engines"],
                )
                # 本市场双端 manifest 位于仓库根目录；历史版本仍须与历史 DSH 包一致。
                for manifest_path in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
                    manifest = load_json(checkout / manifest_path)
                    if manifest.get("name") != plugin.id or manifest.get("version") != release["version"]:
                        raise SmokeTestError(f"{manifest_path}: identity/version differs from DSH release")
                print(f"VERIFIED: {plugin.id}@{release['version']} commit={commit} engines={release['engines']}")
            except SmokeTestError as error:
                raise SmokeTestError(f"{plugin.id}@{release['version']} ({commit}): {error}") from error
    finally:
        if git_output(checkout, "rev-parse", "HEAD") != original:
            git_output(checkout, "checkout", "--detach", original)


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
    plugin: PluginSpec,
    entry: dict[str, Any],
    marketplace_path: Path,
    check_external: bool = False,
    local_root: Path | None = None,
) -> str:
    """校验外部来源与策略；显式联网时再读取双端 manifest 和完整技能入口。"""

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
    slug = plugin.github["repo"]
    if not check_external:
        return f"{slug} (external source configured; payload not fetched)"
    if local_root is not None:
        _validate_payload(local_root.resolve(), plugin, prefix, slug)
        return f"{slug} (LOCAL override: {local_root}; not a remote release check)"
    with tempfile.TemporaryDirectory(prefix="codex-external-plugin-") as directory:
        plugin_root = Path(directory) / "plugin"
        clone_remote(source["url"], plugin.github.get("ref"), plugin_root)
        _validate_payload(plugin_root, plugin, prefix, slug)
        validate_dsh_releases(plugin, plugin_root)
    return f"{slug} (external manifests, all skills and pinned DSH releases verified)"


def _validate_payload(
    plugin_root: Path,
    plugin: PluginSpec,
    prefix: str,
    expected_slug: str,
) -> str:
    """核对独立仓库的双端身份、版本、仓库地址和 catalog 承诺的技能入口。"""
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
    if slug != expected_slug:
        raise SmokeTestError(f"{prefix}: manifest.repository does not match source repository")
    claude = load_json(plugin_root / ".claude-plugin/plugin.json")
    for field in ("name", "version", "description"):
        if claude.get(field) != expected_fields[field]:
            raise SmokeTestError(f"{prefix}: Claude manifest.{field} does not match catalog")
    claude_slug = repository_slug(require_string(
        claude.get("repository"), f"{prefix}: Claude manifest.repository"
    ))
    if claude_slug != slug:
        raise SmokeTestError(f"{prefix}: Claude manifest.repository does not match source repository")

    if plugin.dsh is not None:
        # 这里只核对当前分支／本地覆盖的包；历史范围在各自固定提交中独立核对。
        validate_dsh_package(plugin_root, plugin.dsh["name"], plugin.version)

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
    root: Path, plugin_ids: list[str] | None = None, *, check_external: bool = False,
    local_plugins: dict[str, Path] | None = None
) -> list[str]:
    """检查市场引用和 README；按需下载外部包，不写客户端安装配置。"""
    catalog = load_catalog(root)
    selected = catalog.select(plugin_ids)
    local_plugins = local_plugins or {}
    unknown = set(local_plugins) - {plugin.id for plugin in selected}
    if unknown or (local_plugins and not check_external):
        raise SmokeTestError("local overrides require --check-external and selected plugin IDs")
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
        manifest_path = _validate_plugin(
            plugin, entries[plugin.id], marketplace_path, check_external, local_plugins.get(plugin.id)
        )
        checks.append(f"{plugin.id}: marketplace resolves to {manifest_path}")

    install_command = f"codex plugin marketplace add {slug}"
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
    # README 只检查已有的通用安装入口；插件集合由 catalog 和市场文件核对，
    # 不以新增收录为理由强制扩写 README。
    checks.append("English and Chinese README files retain the marketplace installation entry")
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
    parser.add_argument("--local-plugin", action="append", default=[], metavar="ID=PATH",
                        help="check an explicitly selected local payload instead of cloning it")
    parser.add_argument("--ref")
    args = parser.parse_args()
    if args.local_plugin and (args.remote or not args.check_external):
        parser.error("--local-plugin requires --check-external and cannot accompany --remote")
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
        overrides = {}
        for value in args.local_plugin:
            key, separator, path = value.partition("=")
            if not separator or not path or key in overrides:
                raise SmokeTestError("--local-plugin requires unique ID=PATH entries")
            overrides[key] = Path(path)
        checks = validate_repository(target, args.plugins, check_external=args.check_external,
                                     local_plugins=overrides)
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
