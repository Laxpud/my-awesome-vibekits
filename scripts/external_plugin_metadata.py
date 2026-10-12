"""拉取独立插件仓库，把可分发的元数据回填到内存中的 catalog 候选。

本模块只读取远端、准备候选数据；预览、完整校验和写入由元数据生成器统一处理。
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
from typing import Any

from scripts.check_codex_install import SmokeTestError, clone_remote, repository_slug
from scripts.plugin_catalog import (
    CATALOG_PATH,
    CODEX_INTERFACE_METADATA_FIELDS,
    MANIFEST_METADATA_FIELDS,
    PluginSpec,
)


class ExternalMetadataError(RuntimeError):
    """表示远端包不满足本市场现有的双端插件收录契约。"""


def _read_manifest(plugin_root: Path, relative_path: str) -> dict[str, Any]:
    """读取包内 JSON，拒绝指向临时 checkout 之外的文件。"""

    path = plugin_root / relative_path
    if not path.resolve().is_relative_to(plugin_root.resolve()):
        raise ExternalMetadataError(f"{relative_path}: manifest escapes plugin root")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ExternalMetadataError(f"{relative_path}: {error}") from error
    if not isinstance(data, dict):
        raise ExternalMetadataError(f"{relative_path}: expected a JSON object")
    return data


def _update_entry(entry: dict[str, Any], plugin: PluginSpec, plugin_root: Path) -> None:
    """用实际包更新一个收录快照，保留市场来源、策略和 Claude 分类与标签。"""

    codex = _read_manifest(plugin_root, ".codex-plugin/plugin.json")
    claude = _read_manifest(plugin_root, ".claude-plugin/plugin.json")
    assert plugin.github is not None

    # 1. 同一 checkout 中的两个 manifest 必须指向同一个插件和版本，不能混合发布。
    if codex.get("name") != plugin.id:
        raise ExternalMetadataError(f"manifest.name must remain {plugin.id!r}")
    for field in ("name", "version", "description"):
        if claude.get(field) != codex.get(field):
            raise ExternalMetadataError(f"Claude manifest.{field} differs from Codex manifest")
    for manifest in (codex, claude):
        repository = manifest.get("repository")
        if not isinstance(repository, str) or repository_slug(repository) != plugin.github["repo"]:
            raise ExternalMetadataError("manifest.repository does not match configured source")
    if codex.get("skills") != "./skills/" or claude.get("skills") != ["./skills/"]:
        raise ExternalMetadataError("both manifests must use the supported ./skills/ layout")

    # 2. 从实际技能目录刷新清单；已有技能保留次序，新技能按名称追加。
    old_order = {skill.id: index for index, skill in enumerate(plugin.skills)}
    skills = []
    for skill_file in sorted(plugin_root.glob("skills/*/SKILL.md")):
        if not skill_file.resolve().is_relative_to(plugin_root.resolve()):
            raise ExternalMetadataError(f"skill escapes plugin root: {skill_file.parent.name}")
        skills.append({"id": skill_file.parent.name, "path": f"skills/{skill_file.parent.name}"})
    skills.sort(key=lambda skill: (old_order.get(skill["id"], len(old_order)), skill["id"]))
    for field in ("version", "description", "keywords"):
        if field not in codex:
            raise ExternalMetadataError(f"manifest.{field} is required")
        entry[field] = deepcopy(codex[field])
    entry["skills"] = skills
    entry["manifestMetadata"] = {
        field: deepcopy(codex[field]) for field in MANIFEST_METADATA_FIELDS if field in codex
    }

    # 3. 展示字段来自远端 interface；本市场的策略和展示开关不接受远端覆盖。
    interface = codex.get("interface")
    if not isinstance(interface, dict):
        raise ExternalMetadataError("manifest.interface must be an object")
    adapter = entry["platforms"]["codex"]
    updated_adapter = {
        key: value for key, value in adapter.items()
        if key not in CODEX_INTERFACE_METADATA_FIELDS
    }
    updated_adapter.update({
        field: deepcopy(interface[field])
        for field in CODEX_INTERFACE_METADATA_FIELDS if interface.get(field) is not None
    })
    entry["platforms"]["codex"] = updated_adapter
    if interface.get("category") is not None:
        entry["category"] = interface["category"]
    if "author" in claude:
        entry["platforms"]["claude"]["author"] = deepcopy(claude["author"])
    else:
        entry["platforms"]["claude"].pop("author", None)


def fetch_external_metadata(root: Path, plugins: tuple[PluginSpec, ...]) -> dict[str, Any]:
    """按配置的 ref 读取全部选中外部包；任何失败都不写本地 catalog。"""

    data = json.loads((root / CATALOG_PATH).read_text(encoding="utf-8"))
    entries = {entry["id"]: entry for entry in data["plugins"]}
    external = [plugin for plugin in plugins if plugin.github is not None]
    if not external:
        raise ExternalMetadataError("no external plugins selected")
    with tempfile.TemporaryDirectory(prefix="vibekits-external-metadata-") as directory:
        for plugin in external:
            assert plugin.github is not None
            print(
                f"FETCH: {plugin.id} ({plugin.github['repo']}, "
                f"ref={plugin.github.get('ref', 'default')})", flush=True,
            )
            plugin_root = Path(directory) / plugin.id
            try:
                clone_remote(plugin.codex_source["url"], plugin.github.get("ref"), plugin_root)
                _update_entry(entries[plugin.id], plugin, plugin_root)
            except (ExternalMetadataError, SmokeTestError) as error:
                raise ExternalMetadataError(f"{plugin.id}: {error}") from error
    return data
