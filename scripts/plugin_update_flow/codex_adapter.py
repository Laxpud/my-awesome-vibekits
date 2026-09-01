"""Codex plugin CLI 的窄适配层。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping, Protocol, Sequence

from .git_channel import digest_directory
from .models import Artifact, Installation, PluginTarget
from .runtime import CommandResult, RetryPolicy
from .smoke import SMOKE_PROMPT, parse_codex_smoke


class Runner(Protocol):
    def run(self, args: list[str], **kwargs: object) -> CommandResult: ...


class CodexAdapter:
    """构造 Codex 命令，并把输出归一化为平台无关安装实例。"""

    def __init__(
        self,
        runner: Runner,
        *,
        target: PluginTarget,
        env: Mapping[str, str] | None = None,
        command: Sequence[str] = ("codex",),
    ) -> None:
        self.runner = runner
        self.target = target
        self.env = dict(env or {})
        self.command = tuple(command)

    def add_marketplace(self, source: str, branch: str) -> None:
        self.runner.run(
            [
                *self.command,
                "plugin",
                "marketplace",
                "add",
                source,
                "--ref",
                branch,
                "--json",
            ],
            env=self.env,
            retry=RetryPolicy(),
        )

    def install_plugin(self) -> None:
        self.runner.run(
            [*self.command, "plugin", "add", self.target.qualified_id, "--json"],
            env=self.env,
            retry=RetryPolicy(),
        )

    def uninstall_plugin(self) -> None:
        self.runner.run(
            [*self.command, "plugin", "remove", self.target.qualified_id, "--json"],
            env=self.env,
        )

    def update_plugin(self) -> None:
        self.runner.run(
            [
                *self.command,
                "plugin",
                "marketplace",
                "upgrade",
                self.target.marketplace,
                "--json",
            ],
            env=self.env,
            retry=RetryPolicy(),
        )
        self.install_plugin()

    def list_instances(self) -> list[Installation]:
        result = self.runner.run(
            [*self.command, "plugin", "list", "--json"], env=self.env
        )
        value = json.loads(result.stdout)
        installed = value.get("installed") if isinstance(value, dict) else None
        if not isinstance(installed, list):
            raise ValueError("Codex plugin list has no installed array")
        instances: list[Installation] = []
        for item in installed:
            if not isinstance(item, dict) or item.get("pluginId") != self.target.qualified_id:
                continue
            source = item.get("source")
            marketplace_source = item.get("marketplaceSource")
            path = source.get("path") if isinstance(source, dict) else None
            remote = (
                marketplace_source.get("source")
                if isinstance(marketplace_source, dict)
                else None
            )
            if not isinstance(path, str):
                raise ValueError("Codex target plugin has no source.path")
            instances.append(
                Installation(
                    platform="codex",
                    plugin_id=self.target.qualified_id,
                    marketplace=self.target.marketplace,
                    version=str(item.get("version", "")),
                    enabled=bool(item.get("enabled", False)),
                    install_path=Path(path),
                    source=remote if isinstance(remote, str) else None,
                )
            )
        return instances

    def verify_baseline(self, artifact: Artifact) -> Installation:
        """Verify an installed historical payload against its own skill set."""

        return self._verify(artifact, self.target.baseline_skills)

    def verify_target(self, artifact: Artifact) -> Installation:
        """Verify an installed target payload against the complete catalog contract."""

        return self._verify(artifact, self.target.required_skills)

    def _verify(
        self, artifact: Artifact, required_skills: tuple[Path, ...]
    ) -> Installation:
        instances = self.list_instances()
        if len(instances) != 1:
            raise ValueError(f"expected one Codex installation, found {len(instances)}")
        instance = instances[0]
        source = (instance.source or "").strip().lower()
        source = source.removeprefix("https://").removeprefix("http://")
        source = source.removeprefix("git@github.com:")
        source = source.removesuffix(".git").rstrip("/")
        if source != self.target.expected_repository:
            raise ValueError(
                f"Codex marketplace source mismatch: {instance.source!r}"
            )
        missing_skills = [
            skill
            for skill in required_skills
            if not (instance.install_path / skill).is_file()
        ]
        if missing_skills:
            missing = ", ".join(str(skill) for skill in missing_skills)
            raise ValueError(
                f"Codex installation is missing {self.target.plugin_id} skill(s): "
                f"{missing}"
            )
        digest = digest_directory(instance.install_path)
        if instance.version != artifact.version:
            raise ValueError(
                f"Codex version mismatch: {instance.version!r} != {artifact.version!r}"
            )
        if digest != artifact.plugin_digest:
            raise ValueError(f"Codex plugin digest mismatch: {digest} != {artifact.plugin_digest}")
        return Installation(**{**instance.__dict__, "plugin_digest": digest})

    def run_smoke(self, cwd: Path, schema_path: Path) -> dict[str, str]:
        result = self.runner.run(
            [
                *self.command,
                "exec",
                "--ephemeral",
                "--skip-git-repo-check",
                "--sandbox",
                "read-only",
                "--output-schema",
                str(schema_path),
                "--json",
                "--cd",
                str(cwd),
                SMOKE_PROMPT,
            ],
            cwd=cwd,
            env=self.env,
            retry=RetryPolicy(),
        )
        return parse_codex_smoke(result.stdout)
