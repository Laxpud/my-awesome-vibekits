#!/usr/bin/env python3
"""供插件更新集成测试使用的跨平台 Codex/Claude CLI 替身。"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path


EXPECTED = {
    "buildBackend": "hatchling.build",
    "packageManager": "uv",
    "versionPath": "src/__init__.py",
    "licenseFile": "LICENSE",
    "indexName": "tsinghua",
    "indexUrl": "https://pypi.tuna.tsinghua.edu.cn/simple",
}


def load_state() -> tuple[Path, dict[str, object]]:
    path = Path(os.environ["FAKE_PLUGIN_STATE"])
    if path.is_file():
        return path, json.loads(path.read_text(encoding="utf-8"))
    return path, {"phase": "old", "codex": None, "claude": []}


def save_state(path: Path, state: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def payload(phase: str) -> tuple[Path, str]:
    prefix = "OLD" if phase == "old" else "TARGET"
    return Path(os.environ[f"FAKE_{prefix}_PAYLOAD"]), os.environ[f"FAKE_{prefix}_VERSION"]


def install_payload(platform: str, key: str, phase: str) -> tuple[str, str]:
    source, version = payload(phase)
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]
    destination = Path(os.environ["FAKE_INSTALL_ROOT"]) / platform / digest
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
    return str(destination), version


def codex(args: list[str], path: Path, state: dict[str, object]) -> int:
    if args[:3] == ["plugin", "marketplace", "add"]:
        state["phase"] = "old"
        save_state(path, state)
        print("{}")
        return 0
    if args[:3] == ["plugin", "marketplace", "upgrade"]:
        state["phase"] = "new"
        save_state(path, state)
        print("{}")
        return 0
    if args[:2] == ["plugin", "add"]:
        install_path, version = install_payload("codex", "global", str(state["phase"]))
        state["codex"] = {
            "pluginId": "laxpud-vibekits@laxpud-vibekits",
            "version": version,
            "enabled": True,
            "source": {"path": install_path},
            "marketplaceSource": {
                "source": "https://github.com/Laxpud/my-awesome-vibekits.git"
            },
        }
        save_state(path, state)
        print("{}")
        return 0
    if args[:3] == ["plugin", "list", "--json"]:
        installed = [state["codex"]] if state.get("codex") else []
        print(json.dumps({"installed": installed}))
        return 0
    if args and args[0] == "exec":
        print(json.dumps({"type": "thread.started"}))
        print(
            json.dumps(
                {
                    "type": "item.completed",
                    "item": {"type": "agent_message", "text": json.dumps(EXPECTED)},
                }
            )
        )
        return 0
    return fail(f"unsupported codex command: {args!r}")


def claude(args: list[str], path: Path, state: dict[str, object]) -> int:
    if args[:3] == ["plugin", "marketplace", "update"]:
        state["phase"] = "new"
        save_state(path, state)
        return 0
    if args[:2] == ["plugin", "install"]:
        scope = value_after(args, "--scope", "user")
        project = str(Path.cwd()) if scope in {"project", "local"} else None
        key = f"{scope}:{project or 'user'}"
        install_path, version = install_payload("claude", key, str(state["phase"]))
        item = {
            "id": "laxpud-vibekits@laxpud-vibekits-dev",
            "version": version,
            "scope": scope,
            "enabled": scope != "local",
            "installPath": install_path,
            "projectPath": project,
        }
        state["claude"] = [
            existing
            for existing in state.get("claude", [])
            if not (
                existing.get("scope") == scope
                and existing.get("projectPath") == project
            )
        ] + [item]
        save_state(path, state)
        return 0
    if args[:2] == ["plugin", "update"]:
        scope = value_after(args, "--scope", "user")
        if os.environ.get("FAKE_CLAUDE_FAIL_SCOPE") == scope:
            return fail(f"forced Claude update failure for scope {scope}")
        project = str(Path.cwd()) if scope in {"project", "local"} else None
        updated = False
        for item in state.get("claude", []):
            if item.get("scope") == scope and item.get("projectPath") == project:
                key = f"{scope}:{project or 'user'}"
                install_path, version = install_payload("claude", key, str(state["phase"]))
                item["installPath"] = install_path
                item["version"] = version
                updated = True
        if not updated:
            return fail(f"missing Claude instance for {scope}:{project}")
        save_state(path, state)
        return 0
    if args[:3] == ["plugin", "list", "--json"]:
        print(json.dumps(state.get("claude", [])))
        return 0
    if "--print" in args:
        print(json.dumps({"result": json.dumps(EXPECTED)}))
        return 0
    return fail(f"unsupported claude command: {args!r}")


def value_after(args: list[str], flag: str, default: str) -> str:
    try:
        return args[args.index(flag) + 1]
    except (ValueError, IndexError):
        return default


def fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 1


def main() -> int:
    if len(sys.argv) < 2:
        return fail("platform argument is required")
    platform, args = sys.argv[1], sys.argv[2:]
    path, state = load_state()
    if platform == "codex":
        return codex(args, path, state)
    if platform == "claude":
        return claude(args, path, state)
    return fail(f"unsupported platform: {platform}")


if __name__ == "__main__":
    raise SystemExit(main())
