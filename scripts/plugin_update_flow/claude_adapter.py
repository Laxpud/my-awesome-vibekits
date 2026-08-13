"""Claude Code plugin CLI 的窄适配层。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping, Protocol, Sequence

from .git_channel import digest_directory
from .models import Artifact, Installation, PluginTarget
from .runtime import CommandResult, RetryPolicy
from .smoke import SMOKE_PROMPT, SMOKE_SCHEMA, parse_claude_smoke


class Runner(Protocol):
    def run(self, args: list[str], **kwargs: object) -> CommandResult: ...


class ClaudeAdapter:
    """构造 Claude Code 命令，并保留每个安装实例的 scope/projectPath。"""

    def __init__(
        self,
        runner: Runner,
        *,
        target: PluginTarget,
        env: Mapping[str, str] | None = None,
        command: Sequence[str] = ("claude",),
        max_budget_usd: float = 1.0,
    ) -> None:
        self.runner = runner
        self.target = target
        self.env = dict(env or {})
        self.command = tuple(command)
        self.max_budget_usd = max_budget_usd

    def install_plugin(self, *, scope: str = "user", cwd: Path | None = None) -> None:
        self.runner.run(
            [*self.command, "plugin", "install", self.target.qualified_id, "--scope", scope],
            cwd=cwd,
            env=self.env,
            retry=RetryPolicy(),
        )

    def set_enabled(
        self, enabled: bool, *, scope: str = "user", cwd: Path | None = None
    ) -> None:
        action = "enable" if enabled else "disable"
        self.runner.run(
            [*self.command, "plugin", action, self.target.plugin_id, "--scope", scope],
            cwd=cwd,
            env=self.env,
        )

    def uninstall_plugin(
        self, *, scope: str = "user", cwd: Path | None = None
    ) -> None:
        self.runner.run(
            [
                *self.command,
                "plugin",
                "uninstall",
                self.target.plugin_id,
                "--scope",
                scope,
            ],
            cwd=cwd,
            env=self.env,
        )

    def update_plugin_scopes(self, scopes: list[tuple[str, str | None]]) -> None:
        self.runner.run(
            [*self.command, "plugin", "marketplace", "update", self.target.marketplace],
            env=self.env,
            retry=RetryPolicy(),
        )
        for scope, project_path in scopes:
            cwd = Path(project_path) if project_path else None
            self.runner.run(
                [
                    *self.command,
                    "plugin",
                    "update",
                    self.target.qualified_id,
                    "--scope",
                    scope,
                ],
                cwd=cwd,
                env=self.env,
                retry=RetryPolicy(),
            )

    def list_instances(self) -> list[Installation]:
        result = self.runner.run(
            [*self.command, "plugin", "list", "--json"], env=self.env
        )
        value = json.loads(result.stdout)
        if not isinstance(value, list):
            raise ValueError("Claude plugin list is not an array")
        instances: list[Installation] = []
        for item in value:
            if not isinstance(item, dict) or item.get("id") != self.target.qualified_id:
                continue
            install_path = item.get("installPath")
            if not isinstance(install_path, str):
                raise ValueError("Claude target plugin has no installPath")
            instances.append(
                Installation(
                    platform="claude",
                    plugin_id=self.target.qualified_id,
                    marketplace=self.target.marketplace,
                    version=str(item.get("version", "")),
                    enabled=bool(item.get("enabled", False)),
                    install_path=Path(install_path),
                    source=self.target.marketplace,
                    scope=str(item.get("scope", "")),
                    project_path=(
                        str(item["projectPath"]) if item.get("projectPath") else None
                    ),
                )
            )
        return instances

    def verify_targets(self, artifact: Artifact) -> list[Installation]:
        instances = self.list_instances()
        if not instances:
            raise ValueError("expected at least one Claude installation")
        verified: list[Installation] = []
        for instance in instances:
            if not (instance.install_path / self.target.required_skill).is_file():
                raise ValueError(
                    f"Claude installation is missing {self.target.plugin_id} skill: "
                    f"{self.target.required_skill}"
                )
            digest = digest_directory(instance.install_path)
            if instance.version != artifact.version:
                raise ValueError(
                    f"Claude version mismatch for {instance.project_path}: "
                    f"{instance.version!r} != {artifact.version!r}"
                )
            if digest != artifact.plugin_digest:
                raise ValueError(
                    f"Claude plugin digest mismatch for {instance.project_path}: "
                    f"{digest} != {artifact.plugin_digest}"
                )
            verified.append(
                Installation(**{**instance.__dict__, "plugin_digest": digest})
            )
        return verified

    def run_smoke(self, cwd: Path) -> dict[str, str]:
        result = self.runner.run(
            [
                *self.command,
                "--print",
                "--no-session-persistence",
                "--setting-sources",
                "user",
                "--tools",
                "",
                "--permission-mode",
                "dontAsk",
                "--max-budget-usd",
                str(self.max_budget_usd),
                "--output-format",
                "json",
                "--json-schema",
                json.dumps(SMOKE_SCHEMA, separators=(",", ":")),
                SMOKE_PROMPT,
            ],
            cwd=cwd,
            env=self.env,
            retry=RetryPolicy(),
        )
        return parse_claude_smoke(result.stdout)
