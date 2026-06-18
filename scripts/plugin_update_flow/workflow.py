"""编排隔离测试、日常晋级与补偿回滚。"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Protocol

from .git_channel import digest_directory
from .models import Artifact, Installation
from .smoke import SMOKE_SCHEMA


class Channel(Protocol):
    def create(self) -> None: ...
    def advance(self) -> None: ...
    def cleanup(self) -> None: ...


class PromotionError(RuntimeError):
    """表示日常环境晋级失败，并携带补偿回滚是否成功。"""

    def __init__(
        self,
        message: str,
        *,
        rollback_succeeded: bool,
        recovery_path: Path | None = None,
        manual_commands: list[dict[str, object]] | None = None,
    ) -> None:
        super().__init__(message)
        self.rollback_succeeded = rollback_succeeded
        self.recovery_path = recovery_path
        self.manual_commands = list(manual_commands or [])


class StateSnapshot:
    """只备份晋级会改动的文件和目录，并可恢复“原先不存在”的状态。"""

    def __init__(self, backup_root: Path, paths: list[Path]) -> None:
        self.backup_root = backup_root
        self.paths = paths
        self._entries: list[tuple[Path, Path, bool]] = []

    def capture(self) -> None:
        if self.backup_root.exists():
            raise FileExistsError(f"snapshot already exists: {self.backup_root}")
        self.backup_root.mkdir(parents=True)
        self._entries = []
        for index, target in enumerate(self.paths):
            backup = self.backup_root / f"{index:02d}"
            existed = target.exists()
            self._entries.append((target, backup, existed))
            if not existed:
                continue
            if target.is_dir():
                shutil.copytree(target, backup)
            else:
                shutil.copy2(target, backup)

    def restore(self) -> None:
        if not self._entries:
            raise RuntimeError("snapshot has not been captured")
        for target, backup, existed in self._entries:
            _remove_path(target)
            if not existed:
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            if backup.is_dir():
                shutil.copytree(backup, target)
            else:
                shutil.copy2(backup, target)

    def cleanup(self) -> None:
        _remove_path(self.backup_root)


def _remove_path(path: Path) -> None:
    """删除快照管理的单个路径；目录与文件使用不同的标准库操作。"""

    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()


def _installation_with_digest(instance: Installation) -> Installation:
    """用实际 payload 补齐 digest；测试替身可直接提供固定 digest。"""

    digest = instance.plugin_digest
    if digest is None:
        if not instance.install_path.is_dir():
            raise FileNotFoundError(
                f"missing plugin install directory: {instance.install_path}"
            )
        digest = digest_directory(instance.install_path)
    return Installation(**{**instance.__dict__, "plugin_digest": digest})


def _installation_state(instance: Installation) -> tuple[object, ...]:
    """返回回滚和最终校验所需的稳定实例身份，不依赖列表顺序。"""

    return (
        instance.platform,
        instance.plugin_id,
        instance.marketplace,
        instance.version,
        instance.enabled,
        str(instance.install_path),
        instance.source,
        instance.scope,
        instance.project_path,
        instance.plugin_digest,
    )


def _states(instances: list[Installation]) -> list[tuple[object, ...]]:
    return sorted(_installation_state(item) for item in instances)


def _manual_recovery_commands(
    codex_instances: list[Installation], claude_instances: list[Installation]
) -> list[dict[str, object]]:
    """按晋级前实例生成可复制的逐实例人工修复命令。"""

    commands: list[dict[str, object]] = []
    for _instance in codex_instances:
        commands.append(
            {
                "platform": "codex",
                "cwd": None,
                "command": (
                    "codex plugin add "
                    "laxpud-vibekits@laxpud-vibekits --json"
                ),
            }
        )
    for instance in claude_instances:
        commands.append(
            {
                "platform": "claude",
                "cwd": instance.project_path,
                "command": (
                    "claude plugin update laxpud-vibekits --scope "
                    f"{instance.scope or 'user'}"
                ),
            }
        )
    return commands


class IsolatedHomes:
    """创建仅包含认证和测试 marketplace 的临时用户目录。"""

    def __init__(
        self,
        *,
        real_codex_home: Path,
        real_claude_home: Path,
        repository: str,
        branch: str,
        parent: Path | None = None,
    ) -> None:
        self.real_codex_home = real_codex_home
        self.real_claude_home = real_claude_home
        self.repository = repository
        self.branch = branch
        self.parent = parent
        self._temporary: tempfile.TemporaryDirectory[str] | None = None
        self.root = Path()
        self.codex_home = Path()
        self.claude_home = Path()
        self.smoke_dir = Path()
        self.schema_path = Path()

    def __enter__(self) -> "IsolatedHomes":
        self._temporary = tempfile.TemporaryDirectory(
            prefix="vibekits-plugin-e2e-",
            dir=self.parent,
        )
        self.root = Path(self._temporary.name)
        try:
            self.codex_home = self.root / "codex"
            self.claude_home = self.root / "claude"
            self.smoke_dir = self.root / "smoke-workspace"
            self.schema_path = self.root / "smoke-schema.json"
            for path in (self.codex_home, self.claude_home, self.smoke_dir):
                path.mkdir(parents=True)

            self._copy_credential(
                self.real_codex_home / "auth.json", self.codex_home
            )
            self._copy_credential(
                self.real_claude_home / ".credentials.json", self.claude_home
            )
            settings = {
                "extraKnownMarketplaces": {
                    "laxpud-vibekits-dev": {
                        "source": {
                            "source": "github",
                            "repo": self.repository,
                            "ref": self.branch,
                        }
                    }
                }
            }
            (self.claude_home / "settings.json").write_text(
                json.dumps(settings, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            self.schema_path.write_text(
                json.dumps(SMOKE_SCHEMA, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            return self
        except BaseException:
            # __enter__ 抛错时 Python 不会调用 __exit__，必须在这里清除已复制凭据。
            self._temporary.cleanup()
            self._temporary = None
            raise

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if self._temporary is not None:
            self._temporary.cleanup()
            self._temporary = None

    def codex_env(self) -> dict[str, str]:
        return {"CODEX_HOME": str(self.codex_home)}

    def claude_env(self) -> dict[str, str]:
        return {
            "CLAUDE_CONFIG_DIR": str(self.claude_home),
            "CLAUDE_CODE_PLUGIN_PREFER_HTTPS": "1",
        }

    @staticmethod
    def _copy_credential(source: Path, destination_directory: Path) -> None:
        if not source.is_file():
            raise FileNotFoundError(f"missing credential file: {source.name}")
        destination = destination_directory / source.name
        shutil.copyfile(source, destination)
        os.chmod(destination, 0o600)


def run_isolated_upgrade(
    *,
    channel: Channel,
    codex: Any,
    claude: Any,
    baseline: Artifact,
    target: Artifact,
    marketplace_source: str,
    branch: str,
    smoke_dir: Path,
    schema_path: Path,
    run_skill_smoke: bool = False,
) -> dict[str, Any]:
    """执行旧版安装、真实刷新、目标校验和技能 smoke test。"""

    try:
        channel.create()
        codex.add_marketplace(marketplace_source, branch)
        codex.install_plugin()
        claude.install_plugin(scope="user", cwd=smoke_dir)
        codex_baseline = codex.verify_target(baseline)
        claude_baseline = claude.verify_targets(baseline)

        channel.advance()
        codex.update_plugin()
        claude.update_plugin_scopes([("user", None)])
        codex_target = codex.verify_target(target)
        claude_target = claude.verify_targets(target)

        if run_skill_smoke:
            codex_smoke = {
                "result": "passed",
                "output": codex.run_smoke(smoke_dir, schema_path),
            }
            claude_smoke = {
                "result": "passed",
                "output": claude.run_smoke(smoke_dir),
            }
        else:
            codex_smoke = {"result": "skipped"}
            claude_smoke = {"result": "skipped"}
        return {
            "codex": {
                "result": "passed",
                "baseline": codex_baseline.to_dict(),
                "target": codex_target.to_dict(),
                "smoke": codex_smoke,
            },
            "claude": {
                "result": "passed",
                "baseline": [item.to_dict() for item in claude_baseline],
                "target": [item.to_dict() for item in claude_target],
                "smoke": claude_smoke,
            },
        }
    finally:
        channel.cleanup()


def run_promotion(
    codex: Any,
    claude: Any,
    target: Artifact,
    snapshot: StateSnapshot,
) -> dict[str, Any]:
    """更新所有日常安装；任一失败时恢复两端的晋级前状态。"""

    codex_before = [_installation_with_digest(item) for item in codex.list_instances()]
    claude_before = [
        _installation_with_digest(item) for item in claude.list_instances()
    ]
    if not codex_before or not claude_before:
        raise ValueError("both Codex and Claude must have an installed plugin instance")

    already_current = all(
        item.version == target.version and item.plugin_digest == target.plugin_digest
        for item in codex_before + claude_before
    )
    if already_current:
        codex_current = [_installation_with_digest(codex.verify_target(target))]
        claude_current = [
            _installation_with_digest(item) for item in claude.verify_targets(target)
        ]
        return {
            "result": "passed",
            "instances": [
                item.to_dict() for item in codex_current + claude_current
            ],
        }

    snapshot.capture()
    try:
        # Claude marketplace 由 adapter 内部只刷新一次，再按原 scope/projectPath 更新。
        codex.update_plugin()
        claude.update_plugin_scopes(
            [(item.scope or "user", item.project_path) for item in claude_before]
        )
        codex_after = [_installation_with_digest(codex.verify_target(target))]
        claude_after = [
            _installation_with_digest(item) for item in claude.verify_targets(target)
        ]

        # 版本和 digest 由 adapter 验证；这里额外确保 scope、projectPath 与 enabled 未漂移。
        before_identity = sorted(
            (item.platform, item.plugin_id, item.scope, item.project_path, item.enabled)
            for item in codex_before + claude_before
        )
        after_identity = sorted(
            (item.platform, item.plugin_id, item.scope, item.project_path, item.enabled)
            for item in codex_after + claude_after
        )
        if before_identity != after_identity:
            raise ValueError("promotion changed installation identity or enabled state")

        snapshot.cleanup()
        return {
            "result": "passed",
            "instances": [item.to_dict() for item in codex_after + claude_after],
        }
    except BaseException as promotion_error:
        try:
            snapshot.restore()
            codex_restored = [
                _installation_with_digest(item) for item in codex.list_instances()
            ]
            claude_restored = [
                _installation_with_digest(item) for item in claude.list_instances()
            ]
            if _states(codex_restored) != _states(codex_before) or _states(
                claude_restored
            ) != _states(claude_before):
                raise RuntimeError("restored plugin state does not match snapshot")
            snapshot.cleanup()
        except BaseException as rollback_error:
            recovery_path = getattr(snapshot, "backup_root", None)
            raise PromotionError(
                f"promotion failed and rollback failed: {rollback_error}",
                rollback_succeeded=False,
                recovery_path=recovery_path,
                manual_commands=_manual_recovery_commands(
                    codex_before, claude_before
                ),
            ) from promotion_error
        raise PromotionError(
            f"promotion failed and was rolled back: {promotion_error}",
            rollback_succeeded=True,
        ) from promotion_error
