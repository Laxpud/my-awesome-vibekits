"""解析不可变发布制品，并管理临时远端 marketplace 分支。"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from .models import Artifact, SemVer
from .runtime import CommandRunner, RetryPolicy


_IGNORED_PARTS = {
    ".git",
    "__pycache__",
    # 两个平台的安装缓存都会省略运输 manifest。payload digest 只覆盖真正
    # 进入两端运行时的共享内容，版本与来源则由独立字段验证。
    ".codex-plugin",
    ".claude-plugin",
}


def digest_directory(root: Path) -> str:
    """按相对路径和文件字节计算与遍历顺序无关的插件 payload 摘要。"""

    digest = hashlib.sha256()
    files = [
        path
        for path in root.rglob("*")
        if path.is_file()
        and not any(part in _IGNORED_PARTS for part in path.relative_to(root).parts)
        and path.suffix not in {".pyc", ".pyo"}
    ]
    # 不使用 Path 的原生排序：WindowsPath 与 Git 的 POSIX 路径排序规则不同，
    # 会让同一 payload 在 checkout 和 Git tree 中得到不同摘要。
    files.sort(key=lambda path: path.relative_to(root).as_posix())
    for path in files:
        relative = path.relative_to(root).as_posix().encode("utf-8")
        content = _payload_bytes(path.read_bytes())
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return "sha256:" + digest.hexdigest()


def _payload_bytes(content: bytes) -> bytes:
    """规范化 UTF-8 文本换行，同时保持图片等二进制资源逐字节校验。"""

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return content
    if "\x00" in text:
        return content
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


class GitRepository:
    """封装发布目标、历史版本和 Git 树内容读取。"""

    def __init__(
        self,
        root: Path,
        *,
        plugin_root: Path = Path("plugins/python-project"),
    ) -> None:
        self.root = root.resolve()
        self.plugin_root = plugin_root
        self.manifest_path = plugin_root / ".codex-plugin/plugin.json"

    def resolve_artifacts(
        self, target_ref: str, *, from_ref: str | None = None
    ) -> tuple[Artifact, Artifact]:
        target_commit = self.resolve_commit(target_ref)
        target = self.artifact(target_ref, target_commit)
        if from_ref:
            baseline_commit = self.resolve_commit(from_ref)
            if not self.is_ancestor(baseline_commit, target_commit):
                raise ValueError(f"baseline {from_ref!r} is not an ancestor of target")
            baseline = self.artifact(from_ref, baseline_commit)
            self._require_older(baseline, target)
            return baseline, target

        commits = self._git_text(
            "rev-list", target_commit, "--", self.manifest_path.as_posix()
        ).splitlines()
        for commit in commits:
            candidate = self.artifact(commit, commit)
            if candidate.version == target.version:
                continue
            self._require_older(candidate, target)
            return candidate, target
        raise ValueError("could not find an ancestor with a different plugin version")

    def resolve_commit(self, ref: str) -> str:
        return self._git_text("rev-parse", "--verify", f"{ref}^{{commit}}").strip()

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            cwd=self.root,
            capture_output=True,
            check=False,
        )
        if result.returncode not in (0, 1):
            raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
        return result.returncode == 0

    def artifact(self, ref: str, commit: str | None = None) -> Artifact:
        resolved = commit or self.resolve_commit(ref)
        manifest = json.loads(
            self._git_bytes("show", f"{resolved}:{self.manifest_path.as_posix()}").decode(
                "utf-8"
            )
        )
        version = manifest.get("version")
        if not isinstance(version, str):
            raise ValueError(f"manifest at {resolved} has no string version")
        SemVer.parse(version)
        return Artifact(ref, resolved, version, self.plugin_digest_at(resolved))

    def plugin_digest_at(self, commit: str) -> str:
        names = self._git_text(
            "ls-tree", "-r", "--name-only", commit, "--", self.plugin_root.as_posix()
        ).splitlines()
        digest = hashlib.sha256()
        for name in sorted(names):
            relative_path = Path(name).relative_to(self.plugin_root)
            if any(part in _IGNORED_PARTS for part in relative_path.parts):
                continue
            relative = relative_path.as_posix().encode("utf-8")
            content = _payload_bytes(self._git_bytes("show", f"{commit}:{name}"))
            digest.update(len(relative).to_bytes(8, "big"))
            digest.update(relative)
            digest.update(len(content).to_bytes(8, "big"))
            digest.update(content)
        return "sha256:" + digest.hexdigest()

    def _require_older(self, baseline: Artifact, target: Artifact) -> None:
        if not SemVer.parse(baseline.version) < SemVer.parse(target.version):
            raise ValueError(
                f"baseline version {baseline.version} must be older than target "
                f"version {target.version}"
            )

    def _git_text(self, *args: str) -> str:
        return self._git_bytes(*args).decode("utf-8", errors="strict")

    def _git_bytes(self, *args: str) -> bytes:
        result = subprocess.run(
            ["git", *args],
            cwd=self.root,
            check=True,
            capture_output=True,
        )
        return result.stdout


class TemporaryGitChannel:
    """把唯一远端分支从旧制品安全推进到目标制品。"""

    def __init__(
        self,
        *,
        runner: CommandRunner,
        root: Path,
        remote: str,
        branch: str,
        baseline_commit: str,
        target_commit: str,
    ) -> None:
        self.runner = runner
        self.root = root
        self.remote = remote
        self.branch = branch
        self.baseline_commit = baseline_commit
        self.target_commit = target_commit
        self.created = False
        self.create_attempted = False

    def create(self) -> None:
        # 先记录尝试，再发 push。若远端成功而响应在传输途中丢失，finally 仍会
        # 尝试删除这个唯一分支；删除失败会阻止进入日常晋级。
        self.create_attempted = True
        self.runner.run(
            [
                "git",
                "push",
                self.remote,
                f"{self.baseline_commit}:refs/heads/{self.branch}",
            ],
            cwd=self.root,
            retry=RetryPolicy(),
        )
        self.created = True

    def advance(self) -> None:
        if not self.created:
            raise RuntimeError("temporary Git channel has not been created")
        self.runner.run(
            [
                "git",
                "push",
                f"--force-with-lease=refs/heads/{self.branch}:{self.baseline_commit}",
                self.remote,
                f"{self.target_commit}:refs/heads/{self.branch}",
            ],
            cwd=self.root,
            retry=RetryPolicy(),
        )

    def cleanup(self) -> None:
        if not self.create_attempted:
            return
        self.runner.run(
            ["git", "push", self.remote, "--delete", self.branch],
            cwd=self.root,
            retry=RetryPolicy(),
        )
        self.created = False
        self.create_attempted = False
