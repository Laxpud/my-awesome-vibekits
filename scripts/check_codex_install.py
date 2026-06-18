#!/usr/bin/env python3
"""验证 Codex marketplace、plugin manifest 与 README 安装说明的一致性。"""

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


MARKETPLACE_PATH = Path(".agents/plugins/marketplace.json")
README_PATHS = (Path("README.md"), Path("docs/README.cn.md"))
REQUIRED_INSTALLATION_POLICY = "AVAILABLE"
REQUIRED_AUTHENTICATION_POLICY = "ON_INSTALL"


class SmokeTestError(RuntimeError):
    """表示远程安装链路中的可操作配置错误。"""


def load_json(path: Path) -> dict[str, Any]:
    """读取 JSON 对象，并把解析错误转换成带路径的诊断信息。"""

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
    """读取必须存在的非空字符串字段。"""

    if not isinstance(value, str) or not value.strip():
        raise SmokeTestError(f"expected a non-empty string: {field}")
    return value.strip()


def repository_slug(repository_url: str) -> str:
    """把 GitHub HTTPS 仓库 URL 转换为 Codex CLI 接受的 owner/repo。"""

    parsed = urlparse(repository_url)
    if parsed.scheme != "https" or parsed.netloc.lower() != "github.com":
        raise SmokeTestError(
            "manifest repository must be an https://github.com/<owner>/<repo> URL"
        )

    parts = [part for part in parsed.path.removesuffix(".git").split("/") if part]
    if len(parts) != 2:
        raise SmokeTestError(
            "manifest repository must identify exactly one GitHub owner/repository"
        )
    return "/".join(parts)


def resolve_plugin_path(root: Path, source_path: str) -> Path:
    """解析 marketplace 的本地 source.path，并阻止路径逃出仓库。"""

    plugin_path = (root / source_path).resolve()
    try:
        plugin_path.relative_to(root.resolve())
    except ValueError as error:
        raise SmokeTestError(
            f"marketplace source.path escapes repository root: {source_path}"
        ) from error
    return plugin_path


def validate_repository(root: Path) -> list[str]:
    """验证一个本地 checkout 是否具备 README 所声明的 Codex 安装链路。"""

    marketplace_file = root / MARKETPLACE_PATH
    marketplace = load_json(marketplace_file)
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        raise SmokeTestError(
            f"expected exactly one plugin entry: {marketplace_file}"
        )

    entry = plugins[0]
    if not isinstance(entry, dict):
        raise SmokeTestError(f"expected a plugin object: {marketplace_file}")

    plugin_name = require_string(entry.get("name"), "marketplace.plugins[0].name")
    source = entry.get("source")
    if not isinstance(source, dict) or source.get("source") != "local":
        raise SmokeTestError("marketplace plugin source.source must be 'local'")
    source_path = require_string(source.get("path"), "marketplace source.path")

    # 1. source.path 是远程 marketplace checkout 内的相对定位契约；路径失配时，
    #    GitHub 仓库可以被添加为 marketplace，但 Codex 无法继续找到插件清单。
    plugin_root = resolve_plugin_path(root, source_path)
    manifest_file = plugin_root / ".codex-plugin/plugin.json"
    manifest = load_json(manifest_file)
    manifest_name = require_string(manifest.get("name"), "manifest.name")
    if manifest_name != plugin_name:
        raise SmokeTestError(
            f"plugin name mismatch: marketplace={plugin_name!r}, manifest={manifest_name!r}"
        )
    if plugin_root.name != plugin_name:
        raise SmokeTestError(
            f"plugin directory must match plugin name: {plugin_root.name!r} != {plugin_name!r}"
        )

    # 2. 这些字段由 Codex marketplace 摄取链路消费。把它们纳入 smoke test，
    #    可以在发布前发现“JSON 合法但插件列表不可安装”的退化。
    policy = entry.get("policy")
    if not isinstance(policy, dict):
        raise SmokeTestError("marketplace plugin policy must be an object")
    if policy.get("installation") != REQUIRED_INSTALLATION_POLICY:
        raise SmokeTestError(
            f"policy.installation must be {REQUIRED_INSTALLATION_POLICY!r}"
        )
    if policy.get("authentication") != REQUIRED_AUTHENTICATION_POLICY:
        raise SmokeTestError(
            f"policy.authentication must be {REQUIRED_AUTHENTICATION_POLICY!r}"
        )
    require_string(entry.get("category"), "marketplace plugin category")

    repository_url = require_string(manifest.get("repository"), "manifest.repository")
    slug = repository_slug(repository_url)
    install_command = f"codex plugin marketplace add {slug}"

    # 3. README 是用户真正复制的安装契约。英文入口与中文翻译都必须包含
    #    同一 GitHub slug、插件选择入口和 manifest 中的插件名。
    for relative_path in README_PATHS:
        readme_path = root / relative_path
        try:
            readme = readme_path.read_text(encoding="utf-8")
        except FileNotFoundError as error:
            raise SmokeTestError(f"missing required file: {readme_path}") from error
        if install_command not in readme:
            raise SmokeTestError(
                f"{relative_path} must contain install command: {install_command}"
            )
        if not re.search(r"(?m)^/plugins\s*$", readme):
            raise SmokeTestError(f"{relative_path} must document the /plugins command")
        if f"`{plugin_name}`" not in readme:
            raise SmokeTestError(
                f"{relative_path} must name the selectable plugin: `{plugin_name}`"
            )

    return [
        f"marketplace entry resolves to {manifest_file.relative_to(root)}",
        f"marketplace and manifest agree on plugin name {plugin_name!r}",
        f"README install command matches manifest repository {slug!r}",
        "English and Chinese README files document /plugins and the plugin selection",
    ]


def clone_remote(repository_url: str, ref: str | None, destination: Path) -> None:
    """浅克隆已发布仓库，用同一验证器检查真实远端内容。"""

    command = ["git", "clone", "--depth", "1"]
    if ref:
        command.extend(["--branch", ref])
    command.extend([repository_url, str(destination)])
    try:
        subprocess.run(command, check=True, text=True)
    except FileNotFoundError as error:
        raise SmokeTestError("git is required for --remote") from error
    except subprocess.CalledProcessError as error:
        raise SmokeTestError(f"remote clone failed with exit code {error.returncode}") from error


def repository_url_from_marketplace(root: Path) -> str:
    """沿 marketplace source.path 读取 manifest 中的远程仓库地址。"""

    marketplace = load_json(root / MARKETPLACE_PATH)
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        raise SmokeTestError("expected exactly one plugin entry before remote clone")
    entry = plugins[0]
    if not isinstance(entry, dict) or not isinstance(entry.get("source"), dict):
        raise SmokeTestError("marketplace plugin source must be an object")
    source_path = require_string(entry["source"].get("path"), "marketplace source.path")
    plugin_root = resolve_plugin_path(root, source_path)
    manifest = load_json(plugin_root / ".codex-plugin/plugin.json")
    return require_string(manifest.get("repository"), "manifest.repository")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Smoke-test the Codex GitHub marketplace installation metadata."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root to validate (default: script parent repository)",
    )
    parser.add_argument(
        "--remote",
        action="store_true",
        help="clone manifest.repository and validate the published GitHub checkout",
    )
    parser.add_argument(
        "--ref",
        help="branch or tag to clone with --remote (default: remote default branch)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()

    try:
        if args.ref and not args.remote:
            raise SmokeTestError("--ref requires --remote")

        target_root = root
        temporary_directory: tempfile.TemporaryDirectory[str] | None = None
        if args.remote:
            repository_url = repository_url_from_marketplace(root)
            temporary_directory = tempfile.TemporaryDirectory(
                prefix="codex-install-smoke-"
            )
            target_root = Path(temporary_directory.name) / "repository"
            clone_remote(repository_url, args.ref, target_root)

        checks = validate_repository(target_root)
        mode = "remote GitHub checkout" if args.remote else "local checkout"
        print(f"PASS: Codex install smoke test ({mode})")
        for check in checks:
            print(f"  - {check}")

        if temporary_directory is not None:
            temporary_directory.cleanup()
        return 0
    except SmokeTestError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
