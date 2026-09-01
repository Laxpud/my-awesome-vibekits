"""读取并校验仓库级插件 catalog。

catalog 是插件身份、目录、独立版本和双平台分发元数据的唯一事实来源。
生成器、安装检查和更新流程都通过本模块解析目标，避免各自维护插件常量。
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
    """生成 manifest、marketplace 和生命周期目标所需的插件契约。"""

    id: str
    directory: PurePosixPath
    version: str
    description: str
    category: str
    keywords: tuple[str, ...]
    skills: tuple[SkillSpec, ...]
    codex: dict[str, Any]
    claude: dict[str, Any]

    @property
    def source(self) -> str:
        return f"./{self.directory.as_posix()}"

    @property
    def required_skills(self) -> tuple[Path, ...]:
        """Return every skill entrypoint promised by the catalog."""

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
    data = _mapping(raw, str(path))
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
    directories: set[PurePosixPath] = set()
    for index, raw_plugin in enumerate(raw_plugins):
        field = f"plugins[{index}]"
        item = _mapping(raw_plugin, field)
        plugin_id = _string(item.get("id"), f"{field}.id")
        if not ID_PATTERN.fullmatch(plugin_id):
            raise CatalogError(f"{field}.id: expected lower-case kebab-case")
        if plugin_id in plugin_ids:
            raise CatalogError(f"{field}.id: duplicate plugin ID {plugin_id!r}")
        plugin_ids.add(plugin_id)

        directory = _safe_relative(
            _string(item.get("directory"), f"{field}.directory"),
            f"{field}.directory",
        )
        expected_directory = PurePosixPath("plugins") / plugin_id
        if directory != expected_directory:
            raise CatalogError(
                f"{field}.directory: expected {expected_directory.as_posix()!r}"
            )
        if directory in directories:
            raise CatalogError(f"{field}.directory: duplicate directory")
        directories.add(directory)
        plugin_root = (root / Path(directory.as_posix())).resolve()
        try:
            plugin_root.relative_to(root.resolve())
        except ValueError as error:
            raise CatalogError(f"{field}.directory: escapes repository root") from error
        if not plugin_root.is_dir():
            raise CatalogError(f"{field}.directory: directory does not exist")

        version = _string(item.get("version"), f"{field}.version")
        if not SEMVER_PATTERN.fullmatch(version):
            raise CatalogError(f"{field}.version: expected SemVer")
        description = _string(item.get("description"), f"{field}.description")
        category = _string(item.get("category"), f"{field}.category")
        keywords = _string_list(item.get("keywords"), f"{field}.keywords")

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
            skill_file = plugin_root / Path(skill_path.as_posix()) / "SKILL.md"
            if not skill_file.is_file():
                raise CatalogError(f"{skill_field}.path: missing {skill_file}")
            skills.append(SkillSpec(skill_id, skill_path))

        platforms = _mapping(item.get("platforms"), f"{field}.platforms")
        codex = _mapping(platforms.get("codex"), f"{field}.platforms.codex")
        claude = _mapping(platforms.get("claude"), f"{field}.platforms.claude")
        for codex_field in (
            "installation", "authentication", "displayName", "shortDescription",
            "longDescription",
        ):
            _string(codex.get(codex_field), f"{field}.platforms.codex.{codex_field}")
        _string_list(codex.get("defaultPrompt"), f"{field}.platforms.codex.defaultPrompt")
        _string(claude.get("category"), f"{field}.platforms.claude.category")
        _string_list(claude.get("tags"), f"{field}.platforms.claude.tags")

        # 发布包必须自包含；显式拒绝最常见的跨插件共享目录逃逸写法。
        for content_path in plugin_root.rglob("*"):
            if not content_path.is_file() or content_path.suffix.lower() not in {
                ".md", ".json", ".py", ".toml", ".yaml", ".yml"
            }:
                continue
            text = content_path.read_text(encoding="utf-8")
            if "../shared" in text or "..\\shared" in text:
                raise CatalogError(
                    f"{field}.directory: runtime reference escapes plugin package: "
                    f"{content_path.relative_to(root)}"
                )

        plugins.append(
            PluginSpec(
                plugin_id,
                directory,
                version,
                description,
                category,
                keywords,
                tuple(skills),
                codex,
                claude,
            )
        )

    return PluginCatalog(marketplace, publisher, tuple(plugins))
