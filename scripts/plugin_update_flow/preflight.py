"""在任何远端测试分支或日常配置写入前固定发布目标。"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from urllib.parse import urlparse

from .git_channel import GitRepository
from .models import Artifact, PluginTarget
from .runtime import CommandResult, RetryPolicy
from scripts.plugin_catalog import PluginSpec, load_catalog


class Runner(Protocol):
    def run(self, args: list[str], **kwargs: object) -> CommandResult: ...


class Repository(Protocol):
    def resolve_commit(self, ref: str) -> str: ...

    def resolve_artifacts(
        self, target_ref: str, *, from_ref: str | None = None
    ) -> tuple[Artifact, Artifact]: ...

    def skill_paths_at(self, commit: str) -> tuple[Path, ...]: ...


class PreflightError(RuntimeError):
    """表示运行环境或发布目标不满足自动化前置条件。"""


@dataclass(frozen=True)
class PluginRelease:
    """一个插件在预检后固定不变的旧版与目标版制品。"""

    coordinates: PluginTarget
    plugin_root: Path
    baseline: Artifact
    target: Artifact


@dataclass(frozen=True)
class PreflightResult:
    """预检后固定不变的逐插件制品和 GitHub marketplace 来源。"""

    releases: tuple[PluginRelease, ...]
    repository_slug: str


class ReleasePreflight:
    """按固定顺序执行工作区、Git 引用和跨平台元数据门禁。"""

    def __init__(
        self,
        *,
        root: Path,
        runner: Runner,
        repository: Repository | None = None,
        codex_home: Path | None = None,
        python_executable: str | None = None,
    ) -> None:
        self.root = root.resolve()
        self.runner = runner
        self.repository = repository
        self.codex_home = (codex_home or Path.home() / ".codex").resolve()
        self.python_executable = python_executable or sys.executable

    def run(
        self,
        *,
        target_ref: str,
        from_ref: str | None,
        promote: bool,
        plugin_ids: list[str] | None = None,
    ) -> PreflightResult:
        # 1. 脏工作区会让 HEAD 制品与本地脚本语义不一致，因此必须在 fetch 前拒绝。
        status = self.runner.run(
            ["git", "status", "--porcelain"], cwd=self.root
        ).stdout
        if status.strip():
            raise PreflightError("working tree must be clean before plugin E2E")

        self.runner.run(
            ["git", "fetch", "origin", "main"],
            cwd=self.root,
            retry=RetryPolicy(),
        )
        catalog = load_catalog(self.root)
        selected = catalog.select(plugin_ids)
        first_root = Path(selected[0].directory.as_posix())
        commit_resolver = self.repository or GitRepository(
            self.root, plugin_root=first_root
        )
        if promote:
            head = commit_resolver.resolve_commit("HEAD")
            origin_main = commit_resolver.resolve_commit("origin/main")
            target = commit_resolver.resolve_commit(target_ref)
            if len({head, origin_main, target}) != 1:
                raise PreflightError(
                    "--promote requires HEAD, origin/main and target to resolve "
                    "to the same commit"
                )

        self._run_validators(selected)
        releases: list[PluginRelease] = []
        repository = catalog.publisher["repository"]
        parsed = urlparse(repository)
        expected_repository = parsed.netloc.lower() + parsed.path.removesuffix(".git").lower()
        for plugin in selected:
            plugin_root = Path(plugin.directory.as_posix())
            resolver = self.repository or GitRepository(
                self.root, plugin_root=plugin_root
            )
            baseline, target = resolver.resolve_artifacts(
                target_ref, from_ref=from_ref
            )
            baseline_required_skills = resolver.skill_paths_at(baseline.commit)
            releases.append(
                PluginRelease(
                    coordinates=PluginTarget(
                        plugin.id,
                        catalog.marketplace_id,
                        plugin.required_skills,
                        expected_repository,
                        baseline_required_skills,
                    ),
                    plugin_root=plugin_root,
                    baseline=baseline,
                    target=target,
                )
            )
        return PreflightResult(
            releases=tuple(releases),
            repository_slug=self._repository_slug(),
        )

    def _run_validators(self, plugins: tuple[PluginSpec, ...]) -> None:
        marketplace = self.root / ".claude-plugin/marketplace.json"
        validator = (
            self.codex_home
            / "skills/.system/plugin-creator/scripts/validate_plugin.py"
        )
        if not validator.is_file():
            raise PreflightError(f"Codex plugin validator not found: {validator}")

        commands = [
            [self.python_executable, str(self.root / "scripts/sync_plugin_metadata.py")],
            [self.python_executable, str(self.root / "scripts/check_codex_install.py")],
        ]
        for plugin in plugins:
            plugin_root = self.root / Path(plugin.directory.as_posix())
            commands.append([self.python_executable, str(validator), str(plugin_root)])
            commands.append(["claude", "plugin", "validate", str(plugin_root)])
        commands.append(["claude", "plugin", "validate", str(marketplace)])
        for command in commands:
            self.runner.run(command, cwd=self.root)

    def _repository_slug(self) -> str:
        repository_url = load_catalog(self.root).publisher["repository"]
        parsed = urlparse(repository_url)
        parts = [part for part in parsed.path.removesuffix(".git").split("/") if part]
        if (
            parsed.scheme != "https"
            or parsed.netloc.lower() != "github.com"
            or len(parts) != 2
        ):
            raise PreflightError(
                "manifest repository must be an https GitHub owner/repository URL"
            )
        return "/".join(parts)
