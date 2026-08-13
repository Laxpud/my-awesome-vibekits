#!/usr/bin/env python3
"""检查仓库 Markdown 中指向本地文件的相对链接。"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def tracked_markdown(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "*.md"],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return [
        path
        for line in result.stdout.splitlines()
        if line and (path := root / Path(line)).is_file()
    ]


def check_links(root: Path) -> list[str]:
    errors: list[str] = []
    for source in tracked_markdown(root):
        content = source.read_text(encoding="utf-8")
        for line_number, line in enumerate(content.splitlines(), start=1):
            for match in LINK_PATTERN.finditer(line):
                target = match.group(1).strip().strip("<>")
                parsed = urlparse(target)
                if parsed.scheme or target.startswith("#"):
                    continue
                relative = unquote(parsed.path)
                if not relative:
                    continue
                destination = (source.parent / relative).resolve()
                try:
                    destination.relative_to(root.resolve())
                except ValueError:
                    errors.append(
                        f"{source.relative_to(root)}:{line_number}: link escapes repository: {target}"
                    )
                    continue
                if not destination.exists():
                    errors.append(
                        f"{source.relative_to(root)}:{line_number}: missing link target: {target}"
                    )
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = check_links(root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: tracked Markdown file links resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
