"""定义插件更新流程跨阶段共享的数据契约。"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import IntEnum
from functools import total_ordering
from pathlib import Path
from typing import Any


_SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)


class ExitCode(IntEnum):
    """脚本对调用者公开的稳定退出码。"""

    SUCCESS = 0
    TEST_FAILED = 1
    PROMOTION_ROLLED_BACK = 2
    ROLLBACK_FAILED = 3
    PRECONDITION_FAILED = 4


@dataclass(frozen=True)
class PluginTarget:
    """一次平台操作的插件坐标与安装后内容契约。"""

    plugin_id: str
    marketplace: str
    required_skill: Path
    expected_repository: str

    @property
    def qualified_id(self) -> str:
        return f"{self.plugin_id}@{self.marketplace}"


@total_ordering
@dataclass(frozen=True)
class SemVer:
    """足以完成发布门禁比较的 SemVer 2.0.0 值对象。"""

    major: int
    minor: int
    patch: int
    prerelease: tuple[str, ...] = ()
    build: tuple[str, ...] = ()

    @classmethod
    def parse(cls, value: str) -> "SemVer":
        match = _SEMVER_RE.fullmatch(value)
        if not match:
            raise ValueError(f"invalid SemVer: {value!r}")
        prerelease = tuple(match.group(4).split(".")) if match.group(4) else ()
        for identifier in prerelease:
            if identifier.isdigit() and len(identifier) > 1 and identifier.startswith("0"):
                raise ValueError(
                    f"numeric prerelease identifier has a leading zero: {value!r}"
                )
        build = tuple(match.group(5).split(".")) if match.group(5) else ()
        return cls(
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3)),
            prerelease,
            build,
        )

    def __str__(self) -> str:
        value = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            value += "-" + ".".join(self.prerelease)
        if self.build:
            value += "+" + ".".join(self.build)
        return value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SemVer):
            return NotImplemented
        return (
            self.major,
            self.minor,
            self.patch,
            self.prerelease,
        ) == (
            other.major,
            other.minor,
            other.patch,
            other.prerelease,
        )

    def __hash__(self) -> int:
        # SemVer 规定 build metadata 不参与优先级和相等性，因此也不能进入哈希。
        return hash((self.major, self.minor, self.patch, self.prerelease))

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, SemVer):
            return NotImplemented
        core_self = (self.major, self.minor, self.patch)
        core_other = (other.major, other.minor, other.patch)
        if core_self != core_other:
            return core_self < core_other
        if not self.prerelease:
            return bool(other.prerelease)
        if not other.prerelease:
            return True
        for left, right in zip(self.prerelease, other.prerelease, strict=False):
            if left == right:
                continue
            left_numeric = left.isdigit()
            right_numeric = right.isdigit()
            if left_numeric and right_numeric:
                return int(left) < int(right)
            if left_numeric != right_numeric:
                return left_numeric
            return left < right
        return len(self.prerelease) < len(other.prerelease)


@dataclass(frozen=True)
class Artifact:
    """一次测试中固定不变的插件制品身份。"""

    ref: str
    commit: str
    version: str
    plugin_digest: str

    def to_dict(self) -> dict[str, str]:
        return {
            "ref": self.ref,
            "commit": self.commit,
            "version": self.version,
            "pluginDigest": self.plugin_digest,
        }


@dataclass(frozen=True)
class Installation:
    """一个平台中已安装插件实例的可恢复身份。"""

    platform: str
    plugin_id: str
    marketplace: str
    version: str
    enabled: bool
    install_path: Path
    source: str | None = None
    scope: str | None = None
    project_path: str | None = None
    plugin_digest: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "platform": self.platform,
            "pluginId": self.plugin_id,
            "marketplace": self.marketplace,
            "version": self.version,
            "enabled": self.enabled,
            "installPath": str(self.install_path),
            "source": self.source,
            "scope": self.scope,
            "projectPath": self.project_path,
            "pluginDigest": self.plugin_digest,
        }


@dataclass
class PromotionReport:
    """日常环境晋级与补偿回滚结果。"""

    requested: bool = False
    instances: list[dict[str, Any]] = field(default_factory=list)
    result: str = "not-requested"
    rollback: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "requested": self.requested,
            "instances": self.instances,
            "result": self.result,
            "rollback": self.rollback,
        }


@dataclass
class RunReport:
    """机器可读的完整运行报告。"""

    run_id: str
    mode: str
    baseline: Artifact
    target: Artifact
    started_at: str
    finished_at: str | None = None
    platforms: dict[str, Any] = field(default_factory=dict)
    promotion: PromotionReport = field(default_factory=PromotionReport)
    cleanup: dict[str, Any] = field(default_factory=dict)
    result: str = "running"
    errors: list[str] = field(default_factory=list)

    @classmethod
    def new(
        cls, run_id: str, mode: str, baseline: Artifact, target: Artifact
    ) -> "RunReport":
        return cls(
            run_id=run_id,
            mode=mode,
            baseline=baseline,
            target=target,
            started_at=datetime.now(UTC).isoformat(),
            promotion=PromotionReport(requested=mode == "promote"),
        )

    def finish(self, result: str) -> None:
        self.result = result
        self.finished_at = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schemaVersion": 1,
            "runId": self.run_id,
            "mode": self.mode,
            "startedAt": self.started_at,
            "finishedAt": self.finished_at,
            "baseline": self.baseline.to_dict(),
            "target": self.target.to_dict(),
            "platforms": self.platforms,
            "promotion": self.promotion.to_dict(),
            "cleanup": self.cleanup,
            "result": self.result,
            "errors": self.errors,
        }
