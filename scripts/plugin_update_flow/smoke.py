"""定义跨平台一致的技能 smoke test 输入输出契约。"""

from __future__ import annotations

import json
from typing import Any


EXPECTED_SMOKE_RESULT: dict[str, str] = {
    "buildBackend": "hatchling.build",
    "packageManager": "uv",
    "versionPath": "src/__init__.py",
    "licenseFile": "LICENSE",
    "indexName": "tsinghua",
    "indexUrl": "https://pypi.tuna.tsinghua.edu.cn/simple",
}

SMOKE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        key: {"type": "string", "const": value}
        for key, value in EXPECTED_SMOKE_RESULT.items()
    },
    "required": list(EXPECTED_SMOKE_RESULT),
    "additionalProperties": False,
}

SMOKE_PROMPT = """\
Explicitly use the installed pyproject-standard skill.
This is a read-only conformance probe: do not inspect files, use tools, ask questions,
or create a project. Return only the JSON object required by the supplied schema,
summarizing the skill's fixed build backend, package manager, dynamic version path,
license file, and uv index name and URL.
"""


def validate_smoke_payload(value: Any) -> dict[str, str]:
    """执行独立于模型 JSON Schema 支持的精确值校验。"""

    if not isinstance(value, dict):
        raise ValueError("smoke result must be a JSON object")
    for key, expected in EXPECTED_SMOKE_RESULT.items():
        actual = value.get(key)
        if actual != expected:
            raise ValueError(
                f"smoke result {key} mismatch: expected {expected!r}, got {actual!r}"
            )
    extra = set(value) - set(EXPECTED_SMOKE_RESULT)
    if extra:
        raise ValueError(f"smoke result has unexpected fields: {sorted(extra)}")
    return {key: str(value[key]) for key in EXPECTED_SMOKE_RESULT}


def parse_codex_smoke(output: str) -> dict[str, str]:
    """从 Codex JSONL 事件中提取最后一条 agent message。"""

    messages: list[str] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        item = event.get("item") if isinstance(event, dict) else None
        if isinstance(item, dict) and item.get("type") == "agent_message":
            text = item.get("text")
            if isinstance(text, str):
                messages.append(text)
    if not messages:
        raise ValueError("Codex output contains no agent_message event")
    return validate_smoke_payload(_parse_json_text(messages[-1]))


def parse_claude_smoke(output: str) -> dict[str, str]:
    """从 Claude ``--output-format json`` 包装中提取 result。"""

    wrapper = json.loads(output)
    if not isinstance(wrapper, dict) or "result" not in wrapper:
        raise ValueError("Claude output contains no result field")
    result = wrapper["result"]
    if isinstance(result, str):
        result = _parse_json_text(result)
    return validate_smoke_payload(result)


def _parse_json_text(value: str) -> Any:
    text = value.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()
    return json.loads(text)
