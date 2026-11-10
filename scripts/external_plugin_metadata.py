"""拉取独立插件仓库，把可分发的元数据回填到内存中的 catalog 候选。

本模块只读取远端、准备候选数据；预览、完整校验和写入由元数据生成器统一处理。
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import tempfile
import time
from typing import Any

from scripts.check_codex_install import (
    SmokeTestError, clone_remote, git_output, repository_slug,
    validate_dsh_package, validate_dsh_releases,
)
from scripts.plugin_catalog import (
    CATALOG_PATH,
    CODEX_INTERFACE_METADATA_FIELDS,
    MANIFEST_METADATA_FIELDS,
    SEMVER_PATTERN,
    PluginSpec,
)


class ExternalMetadataError(RuntimeError):
    """表示远端包不满足本市场的双端插件或已登记的 DSH 收录契约。"""


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


@dataclass
class MetadataPreview:
    """保存可生成的候选与待补事项；待补记录只展示，不能混入可安装索引。"""

    data: dict[str, Any]
    pending: list[str] = field(default_factory=list)


def load_release_info(path: Path | None) -> dict[tuple[str, str, str], dict[str, Any]]:
    """读取维护者核实的发布时间及出处，以插件／版本／commit 精确绑定。

    不以本机时间、Git 提交时间或 tag 创建时间推算发布事件；此输入是维护者的
    明确声明，脚本只校验绑定与格式，不声称已独立核实证据内容。
    """
    if path is None:
        return {}
    data = _read_manifest(path.resolve().parent, path.resolve().name)
    releases = data.get("releases")
    if set(data) != {"releases"} or not isinstance(releases, list):
        raise ExternalMetadataError("release-info: expected an object containing a releases array")
    result = {}
    for item in releases:
        fields = {"plugin", "version", "commit", "publishTimestamp", "publishEvidence"}
        if not isinstance(item, dict) or set(item) != fields:
            raise ExternalMetadataError("release-info: expected plugin, version, commit, publishTimestamp and publishEvidence")
        if any(not isinstance(item[key], str) or not item[key].strip()
               for key in ("plugin", "version", "commit", "publishEvidence")):
            raise ExternalMetadataError("release-info: identity and evidence fields must be non-empty strings")
        if not SEMVER_PATTERN.fullmatch(item["version"]) or not re.fullmatch(r"[0-9a-f]{40}", item["commit"]):
            raise ExternalMetadataError("release-info: expected SemVer and a full Git SHA")
        stamp = item["publishTimestamp"]
        if type(stamp) is not int or stamp <= 0 or stamp > time.time():
            raise ExternalMetadataError("release-info: publishTimestamp must be positive Unix seconds, not in the future")
        key = (item["plugin"], item["version"], item["commit"])
        if key in result:
            raise ExternalMetadataError(f"release-info: duplicate release {key}")
        result[key] = {name: item[name] for name in ("publishTimestamp", "publishEvidence")}
    return result


def _dsh_display_metadata(package: dict[str, Any], plugin: PluginSpec) -> dict[str, Any]:
    """提取 DSH 索引支持的包展示字段；缺失时不冒用市场发布者或 Codex 文案。"""
    metadata = {}
    for key in ("description", "homepage", "author"):
        if key not in package:
            continue
        value = package[key]
        if key == "author" and isinstance(value, dict):
            value = value.get("name")
        if not isinstance(value, str) or not value.strip():
            raise ExternalMetadataError(f"package.{key}: expected a non-empty display string")
        metadata[key] = value
    if "repository" in package:
        repository = package["repository"]
        url = repository.get("url") if isinstance(repository, dict) else repository
        if not isinstance(url, str) or repository_slug(url.removeprefix("git+")) != plugin.github["repo"]:
            raise ExternalMetadataError("package.repository does not match configured source")
        metadata["repository"] = {"url": f"https://github.com/{plugin.github['repo']}"}
    return metadata


def _update_dsh_release(
    entry: dict[str, Any], plugin: PluginSpec, checkout: Path, preview: MetadataPreview,
    release_info: dict[tuple[str, str, str], dict[str, Any]], used_info: set[tuple[str, str, str]],
) -> None:
    """从同一 checkout 准备完整发布记录；只追加新版本，不覆盖已有版本。

    无发布时间的新版本与同版本换提交都列为待补／冲突，保留原 versions，
    由上层禁止整次写入，防止只更新展示或双端版本造成半同步。
    """
    if plugin.dsh is None:
        return
    package = validate_dsh_package(checkout, plugin.dsh["name"], entry["version"])
    commit = git_output(checkout, "rev-parse", "HEAD")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ExternalMetadataError("DSH release requires a full Git SHA")
    version = package["version"]
    engine = package["engines"]["dsh"]
    # plugin.dsh 已由 parser 将旧插件级范围冻结到各历史版本；复制后不再使用最新范围兜底。
    adapter = deepcopy(plugin.dsh)
    adapter["metadata"] = _dsh_display_metadata(package, plugin)
    entry["platforms"]["dsh"] = adapter
    source = {"type": "git", "url": f"https://github.com/{plugin.github['repo']}", "commit": commit}
    candidate = {"version": version, "source": source, "engines": engine}
    key = (plugin.id, version, commit)
    evidence = release_info.get(key)
    if evidence is not None:
        used_info.add(key)
    existing = next((release for release in adapter["versions"] if release["version"] == version), None)
    print(f"DSH CANDIDATE: {plugin.id}@{version} commit={commit} engines={engine}")
    if existing is not None:
        if existing["source"] != source:
            preview.pending.append(
                f"{plugin.id}@{version}: same-version source change; "
                f"recorded={json.dumps(existing['source'], sort_keys=True)} "
                f"candidate={json.dumps(source, sort_keys=True)}; publish a new version; history preserved"
            )
        elif existing["engines"] != engine:
            preview.pending.append(f"{plugin.id}@{version}: recorded engines differ at the same commit; history preserved")
        elif evidence is not None and evidence["publishTimestamp"] != existing["publishTimestamp"]:
            preview.pending.append(f"{plugin.id}@{version}: supplied timestamp conflicts with immutable release record")
        else:
            print(f"DSH UNCHANGED: {plugin.id}@{version}; recorded timestamp and history retained")
        return
    if evidence is None:
        preview.pending.append(
            f"{plugin.id}@{version}: publishTimestamp pending for commit={commit}, engines={engine}; "
            "supply verified publication time and evidence with --release-info; candidate not indexed"
        )
        return
    # 发布时间只取显式核实输入，证据保存在 catalog；索引仅输出 DSH 原生字段。
    adapter["versions"].append({**candidate, **evidence})
    print(f"DSH NEW RELEASE: {plugin.id}@{version} publishTimestamp={evidence['publishTimestamp']}")


def _print_summary(before: dict[str, Any], after: dict[str, Any]) -> None:
    """在 JSON diff 前列出版本、技能增删与展示变化，便于维护者识别同步范围。"""
    old_skills = {skill["id"] for skill in before["skills"]}
    new_skills = {skill["id"] for skill in after["skills"]}
    changed = [key for key in after if before.get(key) != after[key]]
    print(f"SUMMARY: {after['id']} version={before['version']} -> {after['version']}; "
          f"skills_added={sorted(new_skills - old_skills)}; skills_removed={sorted(old_skills - new_skills)}; "
          f"changed_fields={changed}")
    for platform in ("codex", "claude", "dsh"):
        old = before["platforms"].get(platform, {})
        new = after["platforms"].get(platform, {})
        fields = sorted(key for key in old.keys() | new.keys() if old.get(key) != new.get(key))
        if fields:
            print(f"DISPLAY/PLATFORM: {after['id']} {platform} changed_fields={fields}")


def fetch_external_metadata(
    root: Path, plugins: tuple[PluginSpec, ...], release_info_path: Path | None = None,
) -> MetadataPreview:
    """读取远端分支与固定发布包，返回候选及待补事项；本函数从不写市场文件。"""
    data = json.loads((root / CATALOG_PATH).read_text(encoding="utf-8"))
    preview = MetadataPreview(data)
    entries = {entry["id"]: entry for entry in data["plugins"]}
    if not plugins:
        raise ExternalMetadataError("no external plugins selected")
    release_info = load_release_info(release_info_path)
    used_info: set[tuple[str, str, str]] = set()
    with tempfile.TemporaryDirectory(prefix="vibekits-external-metadata-") as directory:
        for plugin in plugins:
            print(f"FETCH: {plugin.id} ({plugin.github['repo']}, ref={plugin.github.get('ref', 'default')})", flush=True)
            plugin_root = Path(directory) / plugin.id
            before = deepcopy(entries[plugin.id])
            try:
                clone_remote(plugin.codex_source["url"], plugin.github.get("ref"), plugin_root)
                _update_entry(entries[plugin.id], plugin, plugin_root)
                _update_dsh_release(entries[plugin.id], plugin, plugin_root, preview, release_info, used_info)
                # 在临时 clone 中检查历史，且恢复 HEAD；缺少历史对象不能用最新包代替。
                validate_dsh_releases(plugin, plugin_root)
                _print_summary(before, entries[plugin.id])
            except (ExternalMetadataError, SmokeTestError) as error:
                raise ExternalMetadataError(f"{plugin.id}: {error}") from error
    unused = set(release_info) - used_info
    if unused:
        raise ExternalMetadataError(f"release-info: entries do not match selected upstream candidates: {sorted(unused)}")
    return preview
