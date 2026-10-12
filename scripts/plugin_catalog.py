"""读取并校验仓库级插件 catalog。

catalog 是本市场的来源与收录元数据入口；外部插件的发布以独立仓库为准。
生成器与安装检查通过本模块解析外部目标，避免各自维护插件常量。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


CATALOG_PATH = Path("plugin-catalog.json")
CODEX_MARKETPLACE_PATH = Path(".agents/plugins/marketplace.json")
CLAUDE_MARKETPLACE_PATH = Path(".claude-plugin/marketplace.json")
SEMVER_PATTERN = re.compile(
    r"^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# 市场展示只接收可独立携带的字段；包内图片路径仍由安装后的 manifest 解析。
CODEX_INTERFACE_METADATA_FIELDS = (
    "displayName", "shortDescription", "longDescription", "developerName",
    "category", "capabilities", "websiteURL", "websiteUrl", "defaultPrompt",
    "brandColor", "privacyPolicyURL", "privacyPolicyUrl", "termsOfServiceURL",
    "termsOfServiceUrl", "composerIconUrl", "logoUrl", "logoUrlDark", "screenshotUrls",
)
MANIFEST_METADATA_FIELDS = ("author", "homepage", "repository", "license")


class CatalogError(RuntimeError):
    """表示 catalog 或其引用的插件内容违反分发契约。"""


def _string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CatalogError(f"{field}: expected a non-empty string")
    return value.strip()


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CatalogError(f"{field}: expected an object")
    return value


def _string_list(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise CatalogError(f"{field}: expected a non-empty string array")
    return tuple(_string(item, f"{field}[{index}]") for index, item in enumerate(value))


def _safe_relative(value: str, field: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or ".." in path.parts or "." in path.parts:
        raise CatalogError(f"{field}: path must stay inside the plugin root: {value!r}")
    if "\\" in value:
        raise CatalogError(f"{field}: path must use POSIX separators: {value!r}")
    return path


@dataclass(frozen=True)
class SkillSpec:
    """catalog 中一个技能的稳定身份和插件内相对路径。"""

    id: str
    path: PurePosixPath


@dataclass(frozen=True)
class PluginSpec:
    """独立 GitHub 插件的来源、完整技能清单和市场展示快照。"""

    id: str
    version: str
    description: str
    category: str
    keywords: tuple[str, ...]
    skills: tuple[SkillSpec, ...]
    codex: dict[str, Any]
    claude: dict[str, Any]
    github: dict[str, str]
    manifest_metadata: dict[str, Any] | None = None

    @property
    def source(self) -> dict[str, str]:
        """返回 Claude 来源；GitHub 条目指向独立仓库根目录。"""
        return {"source": "github", **self.github}

    @property
    def codex_source(self) -> dict[str, str]:
        """将同一 GitHub 来源转换成 Codex 的 url 格式。"""
        return {
            "source": "url",
            "url": f"https://github.com/{self.github['repo']}.git",
            **({"ref": self.github["ref"]} if "ref" in self.github else {}),
        }

    @property
    def required_skills(self) -> tuple[Path, ...]:
        """列出 catalog 承诺的全部技能入口，路径相对于各插件根目录。"""

        return tuple(
            Path(skill.path.as_posix()) / "SKILL.md" for skill in self.skills
        )


@dataclass(frozen=True)
class PluginCatalog:
    """已完成结构和跨插件冲突校验的 catalog。"""

    marketplace: dict[str, Any]
    publisher: dict[str, Any]
    plugins: tuple[PluginSpec, ...]

    @property
    def marketplace_id(self) -> str:
        return _string(self.marketplace.get("id"), "marketplace.id")

    def select(self, plugin_ids: Iterable[str] | None = None) -> tuple[PluginSpec, ...]:
        requested = tuple(plugin_ids or ())
        if not requested:
            return self.plugins
        by_id = {plugin.id: plugin for plugin in self.plugins}
        unknown = [plugin_id for plugin_id in requested if plugin_id not in by_id]
        if unknown:
            raise CatalogError("unknown plugin ID(s): " + ", ".join(unknown))
        if len(set(requested)) != len(requested):
            raise CatalogError("plugin selection contains duplicate IDs")
        return tuple(by_id[plugin_id] for plugin_id in requested)


def load_catalog(root: Path, path: Path = CATALOG_PATH) -> PluginCatalog:
    """加载 catalog，并在访问任何生成物前验证全部身份与路径。"""

    catalog_file = root / path
    try:
        raw = json.loads(catalog_file.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise CatalogError(f"missing catalog: {path}") from error
    except json.JSONDecodeError as error:
        raise CatalogError(
            f"invalid JSON: {path}:{error.lineno}:{error.colno}: {error.msg}"
        ) from error
    return parse_catalog(raw)


def parse_catalog(raw: Any) -> PluginCatalog:
    """校验内存中的完整候选 catalog，使外部同步可在写入前发现跨插件冲突。"""

    data = _mapping(raw, str(CATALOG_PATH))
    if data.get("schemaVersion") != 1:
        raise CatalogError("schemaVersion: expected 1")
    marketplace = _mapping(data.get("marketplace"), "marketplace")
    publisher = _mapping(data.get("publisher"), "publisher")
    _string(marketplace.get("id"), "marketplace.id")
    _string(marketplace.get("displayName"), "marketplace.displayName")
    _string(marketplace.get("description"), "marketplace.description")
    _string(marketplace.get("owner"), "marketplace.owner")
    for field in ("name", "url", "homepage", "repository", "license"):
        _string(publisher.get(field), f"publisher.{field}")

    raw_plugins = data.get("plugins")
    if not isinstance(raw_plugins, list) or not raw_plugins:
        raise CatalogError("plugins: expected a non-empty array")

    plugins: list[PluginSpec] = []
    plugin_ids: set[str] = set()
    skill_ids: dict[str, str] = {}
    for index, raw_plugin in enumerate(raw_plugins):
        field = f"plugins[{index}]"
        item = _mapping(raw_plugin, field)
        plugin_id = _string(item.get("id"), f"{field}.id")
        if not ID_PATTERN.fullmatch(plugin_id):
            raise CatalogError(f"{field}.id: expected lower-case kebab-case")
        if plugin_id in plugin_ids:
            raise CatalogError(f"{field}.id: duplicate plugin ID {plugin_id!r}")
        plugin_ids.add(plugin_id)

        # 1. 市场只收录独立仓库；拒绝旧目录字段，避免重新接入本地快照。
        if "directory" in item:
            raise CatalogError(f"{field}.directory: local plugin packages are not supported")
        source = _mapping(item.get("source"), f"{field}.source")
        if set(source) - {"type", "repo", "ref"} or source.get("type") != "github":
            raise CatalogError(f"{field}.source: expected GitHub repo and optional ref")
        repo = _string(source.get("repo"), f"{field}.source.repo")
        repo_pattern = r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?/[A-Za-z0-9_.-]+"
        if (
            not re.fullmatch(repo_pattern, repo)
            or repo.split("/")[1] in {".", ".."}
            or repo.endswith(".git")
        ):
            raise CatalogError(f"{field}.source.repo: expected GitHub owner/repo without .git")
        github = {"repo": repo}
        if "ref" in source:
            ref = _string(source["ref"], f"{field}.source.ref")
            if ref.startswith("-") or any(char.isspace() or ord(char) < 32 for char in ref):
                raise CatalogError(f"{field}.source.ref: invalid Git ref")
            github["ref"] = ref

        version = _string(item.get("version"), f"{field}.version")
        if not SEMVER_PATTERN.fullmatch(version):
            raise CatalogError(f"{field}.version: expected SemVer")
        description = _string(item.get("description"), f"{field}.description")
        category = _string(item.get("category"), f"{field}.category")
        keywords = _string_list(item.get("keywords"), f"{field}.keywords")
        manifest_metadata = None
        if "manifestMetadata" in item:
            manifest_metadata = _mapping(item["manifestMetadata"], f"{field}.manifestMetadata")
            if set(manifest_metadata) - set(MANIFEST_METADATA_FIELDS):
                raise CatalogError(f"{field}.manifestMetadata: unsupported manifest field")
            for metadata_field, value in manifest_metadata.items():
                metadata_path = f"{field}.manifestMetadata.{metadata_field}"
                if metadata_field == "author":
                    author = _mapping(value, metadata_path)
                    _string(author.get("name"), f"{metadata_path}.name")
                    for author_field, author_value in author.items():
                        _string(author_value, f"{metadata_path}.{author_field}")
                else:
                    _string(value, metadata_path)

        # 2. 离线校验完整技能清单与跨插件冲突；实际文件交给外部包检查。
        raw_skills = item.get("skills")
        if not isinstance(raw_skills, list) or not raw_skills:
            raise CatalogError(f"{field}.skills: expected a non-empty array")
        skills: list[SkillSpec] = []
        for skill_index, raw_skill in enumerate(raw_skills):
            skill_field = f"{field}.skills[{skill_index}]"
            skill_data = _mapping(raw_skill, skill_field)
            skill_id = _string(skill_data.get("id"), f"{skill_field}.id")
            if not ID_PATTERN.fullmatch(skill_id):
                raise CatalogError(f"{skill_field}.id: expected lower-case kebab-case")
            collision_key = skill_id.casefold()
            if collision_key in skill_ids:
                raise CatalogError(
                    f"{skill_field}.id: Skill ID {skill_id!r} conflicts with "
                    f"plugin {skill_ids[collision_key]!r}"
                )
            skill_ids[collision_key] = plugin_id
            skill_path = _safe_relative(
                _string(skill_data.get("path"), f"{skill_field}.path"),
                f"{skill_field}.path",
            )
            expected_skill_path = PurePosixPath("skills") / skill_id
            if skill_path != expected_skill_path:
                raise CatalogError(
                    f"{skill_field}.path: expected {expected_skill_path.as_posix()!r}"
                )
            skills.append(SkillSpec(skill_id, skill_path))

        platforms = _mapping(item.get("platforms"), f"{field}.platforms")
        codex = _mapping(platforms.get("codex"), f"{field}.platforms.codex")
        claude = _mapping(platforms.get("claude"), f"{field}.platforms.claude")
        if not isinstance(codex.get("marketplaceMetadata", False), bool):
            raise CatalogError(
                f"{field}.platforms.codex.marketplaceMetadata: expected a boolean"
            )
        for codex_field in (
            "installation", "authentication", "displayName", "shortDescription",
            "longDescription",
        ):
            _string(codex.get(codex_field), f"{field}.platforms.codex.{codex_field}")
        _string_list(codex.get("defaultPrompt"), f"{field}.platforms.codex.defaultPrompt")
        for interface_field in CODEX_INTERFACE_METADATA_FIELDS:
            if interface_field not in codex:
                continue
            value = codex[interface_field]
            interface_path = f"{field}.platforms.codex.{interface_field}"
            if interface_field in {"defaultPrompt", "capabilities", "screenshotUrls"}:
                if not isinstance(value, list):
                    raise CatalogError(f"{interface_path}: expected a string array")
                for index, item_value in enumerate(value):
                    _string(item_value, f"{interface_path}[{index}]")
            else:
                _string(value, interface_path)
        _string(claude.get("category"), f"{field}.platforms.claude.category")
        _string_list(claude.get("tags"), f"{field}.platforms.claude.tags")
        if "author" in claude:
            author = _mapping(claude["author"], f"{field}.platforms.claude.author")
            _string(author.get("name"), f"{field}.platforms.claude.author.name")
            for author_field, author_value in author.items():
                _string(author_value, f"{field}.platforms.claude.author.{author_field}")

        # 3. 保存可独立生成两端 marketplace 的收录快照，不访问插件源码。
        plugins.append(
            PluginSpec(
                plugin_id,
                version,
                description,
                category,
                keywords,
                tuple(skills),
                codex,
                claude,
                github,
                manifest_metadata,
            )
        )

    return PluginCatalog(marketplace, publisher, tuple(plugins))
