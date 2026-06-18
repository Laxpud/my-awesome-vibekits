"""在任何远端测试分支或日常配置写入前固定发布目标。"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from urllib.parse import urlparse

from .git_channel import GitRepository
from .models import Artifact
from .runtime import CommandResult, RetryPolicy


class Runner(Protocol):
    def run(self, args: list[str], **kwargs: object) -> CommandResult: ...


class Repository(Protocol):
    def resolve_commit(self, ref: str) -> str: ...

    def resolve_artifacts(
        self, target_ref: str, *, from_ref: str | None = None
    ) -> tuple[Artifact, Artifact]: ...


class PreflightError(RuntimeError):
    """表示运行环境或发布目标不满足自动化前置条件。"""


@dataclass(frozen=True)
class PreflightResult:
    """预检后固定不变的旧版、目标版和 GitHub marketplace 来源。"""

    baseline: Artifact
    target: Artifact
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
        self.repository = repository or GitRepository(self.root)
        self.codex_home = (codex_home or Path.home() / ".codex").resolve()
        self.python_executable = python_executable or sys.executable

    def run(
        self,
        *,
        target_ref: str,
        from_ref: str | None,
        promote: bool,
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
        if promote:
            head = self.repository.resolve_commit("HEAD")
            origin_main = self.repository.resolve_commit("origin/main")
            target = self.repository.resolve_commit(target_ref)
            if len({head, origin_main, target}) != 1:
                raise PreflightError(
                    "--promote requires HEAD, origin/main and target to resolve "
                    "to the same commit"
                )

        self._run_validators()
        baseline, target = self.repository.resolve_artifacts(
            target_ref, from_ref=from_ref
        )
        return PreflightResult(
            baseline=baseline,
            target=target,
            repository_slug=self._repository_slug(),
        )

    def _run_validators(self) -> None:
        plugin_root = self.root / "plugins/laxpud-vibekits"
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
            [self.python_executable, str(validator), str(plugin_root)],
            ["claude", "plugin", "validate", str(plugin_root)],
            ["claude", "plugin", "validate", str(marketplace)],
        ]
        for command in commands:
            self.runner.run(command, cwd=self.root)

    def _repository_slug(self) -> str:
        manifest_path = (
            self.root / "plugins/laxpud-vibekits/.codex-plugin/plugin.json"
        )
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            repository_url = manifest["repository"]
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
            raise PreflightError(
                f"cannot read manifest repository: {manifest_path}"
            ) from error
        if not isinstance(repository_url, str):
            raise PreflightError("manifest repository must be a string")
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
