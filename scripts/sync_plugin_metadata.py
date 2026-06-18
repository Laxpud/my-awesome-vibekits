#!/usr/bin/env python3
"""同步并校验跨平台插件发布元数据中的版本与路径。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


PLUGIN_ROOT = Path("plugins/laxpud-vibekits")
CODEX_MANIFEST = PLUGIN_ROOT / ".codex-plugin/plugin.json"
CLAUDE_MANIFEST = PLUGIN_ROOT / ".claude-plugin/plugin.json"
CODEX_MARKETPLACE = Path(".agents/plugins/marketplace.json")
CLAUDE_MARKETPLACE = Path(".claude-plugin/marketplace.json")
README_PATHS = (Path("README.md"), Path("docs/README.cn.md"))
EXPECTED_MARKETPLACE_SOURCE = "./plugins/laxpud-vibekits"
EXPECTED_SKILLS_SOURCE = "./skills/"

# 接受 SemVer 2.0.0 的常用形式，拒绝容易误写进发布清单的 v 前缀和不完整版本。
SEMVER_PATTERN = re.compile(
    r"^(?:0|[1-9]\d*)\."
    r"(?:0|[1-9]\d*)\."
    r"(?:0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


class MetadataError(RuntimeError):
    """表示发布元数据无法安全同步或彼此不一致。"""


def load_json(path: Path) -> dict[str, Any]:
    """读取 JSON 对象，并保留足够的路径与行列诊断。"""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise MetadataError(f"missing required file: {path}") from error
    except json.JSONDecodeError as error:
        raise MetadataError(
            f"invalid JSON: {path}:{error.lineno}:{error.colno}: {error.msg}"
        ) from error
    if not isinstance(value, dict):
        raise MetadataError(f"expected a JSON object: {path}")
    return value


def require_string(value: Any, field: str) -> str:
    """读取发布契约要求的非空字符串。"""

    if not isinstance(value, str) or not value.strip():
        raise MetadataError(f"expected a non-empty string: {field}")
    return value.strip()


def only_plugin(marketplace: dict[str, Any], path: Path) -> dict[str, Any]:
    """返回当前单插件 marketplace 的唯一条目。"""

    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        raise MetadataError(f"expected exactly one plugin entry: {path}")
    plugin = plugins[0]
    if not isinstance(plugin, dict):
        raise MetadataError(f"expected a plugin object: {path}")
    return plugin


def marketplace_source(plugin: dict[str, Any], platform: str) -> str:
    """统一读取 Claude 字符串 source 与 Codex 对象 source.path。"""

    source = plugin.get("source")
    if platform == "Claude":
        return require_string(source, "Claude marketplace source")
    if not isinstance(source, dict) or source.get("source") != "local":
        raise MetadataError("Codex marketplace source.source must be 'local'")
    return require_string(source.get("path"), "Codex marketplace source.path")


def resolve_inside_root(root: Path, source: str, field: str) -> Path:
    """解析仓库相对路径，同时阻止 marketplace 路径逃出仓库。"""

    resolved = (root / source).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as error:
        raise MetadataError(f"{field} escapes repository root: {source}") from error
    return resolved


def expected_readme_fragments(path: Path, version: str) -> tuple[str, str]:
    """按 README 语言返回版本 badge 与状态文本。"""

    badge = f"version-{version}-2563EB"
    status = (
        f"Current plugin version: `{version}`."
        if path.name == "README.md" and path.parent == Path(".")
        else f"当前插件版本：`{version}`。"
    )
    return badge, status


def collect_errors(root: Path) -> tuple[str, list[str]]:
    """以 Codex manifest 为权威源，收集所有版本和路径漂移。"""

    codex_manifest = load_json(root / CODEX_MANIFEST)
    claude_manifest = load_json(root / CLAUDE_MANIFEST)
    codex_marketplace = load_json(root / CODEX_MARKETPLACE)
    claude_marketplace = load_json(root / CLAUDE_MARKETPLACE)
    codex_plugin = only_plugin(codex_marketplace, CODEX_MARKETPLACE)
    claude_plugin = only_plugin(claude_marketplace, CLAUDE_MARKETPLACE)

    plugin_name = require_string(codex_manifest.get("name"), "Codex manifest name")
    version = require_string(codex_manifest.get("version"), "Codex manifest version")
    errors: list[str] = []

    # 1. 身份与版本必须在两套平台清单及 Claude marketplace 中保持一致。
    named_values = {
        "plugin directory": PLUGIN_ROOT.name,
        "Claude manifest name": require_string(
            claude_manifest.get("name"), "Claude manifest name"
        ),
        "Codex marketplace name": require_string(
            codex_plugin.get("name"), "Codex marketplace name"
        ),
        "Claude marketplace name": require_string(
            claude_plugin.get("name"), "Claude marketplace name"
        ),
    }
    for label, value in named_values.items():
        if value != plugin_name:
            errors.append(f"{label} is {value!r}; expected {plugin_name!r}")

    versioned_values = {
        "Claude manifest version": require_string(
            claude_manifest.get("version"), "Claude manifest version"
        ),
        "Claude marketplace version": require_string(
            claude_plugin.get("version"), "Claude marketplace version"
        ),
    }
    for label, value in versioned_values.items():
        if value != version:
            errors.append(f"{label} is {value!r}; expected {version!r}")

    # 2. 两个平台必须从仓库根目录解析到同一个共享插件包。
    sources = {
        "Codex marketplace source.path": marketplace_source(codex_plugin, "Codex"),
        "Claude marketplace source": marketplace_source(claude_plugin, "Claude"),
    }
    expected_root = (root / PLUGIN_ROOT).resolve()
    for label, source in sources.items():
        resolved = resolve_inside_root(root, source, label)
        if source != EXPECTED_MARKETPLACE_SOURCE:
            errors.append(
                f"{label} is {source!r}; expected {EXPECTED_MARKETPLACE_SOURCE!r}"
            )
        if resolved != expected_root:
            errors.append(f"{label} resolves to {resolved}; expected {expected_root}")

    # 3. skills 字段语法可以平台化，但最终都只能指向唯一共享技能目录。
    if codex_manifest.get("skills") != EXPECTED_SKILLS_SOURCE:
        errors.append(
            f"Codex manifest skills must be {EXPECTED_SKILLS_SOURCE!r}"
        )
    if claude_manifest.get("skills") != [EXPECTED_SKILLS_SOURCE]:
        errors.append(
            f"Claude manifest skills must be [{EXPECTED_SKILLS_SOURCE!r}]"
        )
    skills_root = expected_root / EXPECTED_SKILLS_SOURCE
    if not skills_root.is_dir():
        errors.append(f"shared skills directory does not exist: {skills_root}")

    # 4. README 是公开版本展示面，也纳入同一校验，避免发布页继续显示旧版本。
    for relative_path in README_PATHS:
        path = root / relative_path
        try:
            content = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            errors.append(f"missing required file: {relative_path}")
            continue
        for fragment in expected_readme_fragments(relative_path, version):
            if fragment not in content:
                errors.append(f"{relative_path} does not contain {fragment!r}")

    return version, errors


def replace_once(content: str, pattern: str, replacement: str, label: str) -> str:
    """执行必须且只能命中一次的文本替换，防止静默改错位置。"""

    updated, count = re.subn(pattern, replacement, content, count=2, flags=re.MULTILINE)
    if count != 1:
        raise MetadataError(f"expected exactly one version occurrence in {label}; found {count}")
    return updated


def update_version(root: Path, version: str) -> list[Path]:
    """一次更新所有公开版本镜像，不改写无关 JSON 格式。"""

    if not SEMVER_PATTERN.fullmatch(version):
        raise MetadataError(f"version must be SemVer without a 'v' prefix: {version!r}")

    # 先完成全部读取和唯一匹配，再统一写入。任何文件结构异常都不会留下半次 bump。
    pending: dict[Path, str] = {}
    for relative_path in (CODEX_MANIFEST, CLAUDE_MANIFEST, CLAUDE_MARKETPLACE):
        path = root / relative_path
        content = path.read_text(encoding="utf-8")
        updated = replace_once(
            content,
            r'(^\s*"version"\s*:\s*")[^"]+("\s*,?\s*$)',
            rf"\g<1>{version}\g<2>",
            str(relative_path),
        )
        if updated != content:
            pending[relative_path] = updated

    for relative_path in README_PATHS:
        path = root / relative_path
        content = path.read_text(encoding="utf-8")
        updated = replace_once(
            content,
            r"version-[0-9A-Za-z.+-]+-2563EB",
            f"version-{version}-2563EB",
            f"{relative_path} badge",
        )
        status_pattern = (
            r"Current plugin version: `[^`]+`\."
            if relative_path == Path("README.md")
            else r"当前插件版本：`[^`]+`。"
        )
        status_replacement = expected_readme_fragments(relative_path, version)[1]
        updated = replace_once(
            updated,
            status_pattern,
            status_replacement,
            f"{relative_path} status",
        )
        if updated != content:
            pending[relative_path] = updated

    for relative_path, updated in pending.items():
        (root / relative_path).write_text(updated, encoding="utf-8")

    return list(pending)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check plugin release versions and paths, or bump every version mirror."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (default: script parent repository)",
    )
    parser.add_argument(
        "--set-version",
        metavar="SEMVER",
        help="update all version mirrors before validating",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    try:
        if args.set_version:
            changed = update_version(root, args.set_version)
            for path in changed:
                print(f"UPDATED: {path}")

        version, errors = collect_errors(root)
        if errors:
            for error in errors:
                print(f"FAIL: {error}", file=sys.stderr)
            return 1

        print(f"PASS: plugin release metadata is synchronized (version {version})")
        print(f"  - plugin root: {PLUGIN_ROOT.as_posix()}")
        print(f"  - marketplace source: {EXPECTED_MARKETPLACE_SOURCE}")
        print(f"  - shared skills source: {EXPECTED_SKILLS_SOURCE}")
        return 0
    except (MetadataError, OSError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
