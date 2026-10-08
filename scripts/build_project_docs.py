#!/usr/bin/env python3
"""将 project-docs 维护源生成独立技能包；默认只检查，不写入文件。"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import quote, unquote, urlsplit


# 维护源使用普通 Markdown 相对链接；代码围栏中的示例路径不是打包依赖。
# 支持行内链接、引用式定义、HTML href/src；不支持带嵌套括号的未编码路径。
LINK = re.compile(
    r'!?\[[^\]\n]*\]\(<?(?P<inline>[^\s<>)]*)>?(?:\s+"[^"\n]*")?\)'
    r'|^\s{0,3}\[[^\]\n]+\]:\s*<?(?P<reference>[^\s<>]+)>?'
    r'|\b(?:href|src)=["\'](?P<html>[^"\']+)["\']',
    re.MULTILINE,
)
FENCE = re.compile(r'^\s{0,3}(`{3,}|~{3,})(.*)$')


class BundleError(ValueError):
    """源引用或安装文件不符合自包含约定。"""


def rewrite_links(text: str, replace) -> str:
    """只处理围栏之外的实际链接，保持示例、正文和 frontmatter 原样。"""
    result: list[str] = []
    fence: str | None = None
    for line in text.splitlines(keepends=True):
        match = FENCE.match(line)
        if match:
            marker, tail = match.groups()
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence) and not tail.strip():
                fence = None
            result.append(line)
            continue
        if fence:
            result.append(line)
            continue

        def substitute(match: re.Match[str]) -> str:
            group = next(key for key, value in match.groupdict().items() if value is not None)
            start, end = match.span(group)
            offset = match.start()
            return match[0][:start - offset] + replace(match[group]) + match[0][end - offset:]

        result.append(LINK.sub(substitute, line))
    return ''.join(result)


def build_files(root: Path) -> dict[Path, bytes]:
    """计算完整输出；从技能入口递归收集共享资料，不修改源文件或安装目录。"""
    source = (root / 'sources/project-docs').resolve()
    catalog = json.loads((root / 'plugin-catalog.json').read_text(encoding='utf-8'))
    plugin = next(item for item in catalog['plugins'] if item['id'] == 'project-docs')
    output = root / plugin['directory'] / 'skills'
    names = {item['id'] for item in plugin['skills']}
    actual = {p.name for p in (source / 'skills').iterdir() if p.is_dir()}
    if actual != names:
        raise BundleError('Source skill directories differ from the catalog')
    if output.is_symlink() or any(p.is_symlink() for p in output.rglob('*')):
        raise BundleError('Generated skills must contain regular files, not symlinks')
    generated: dict[Path, bytes] = {}

    for name in sorted(names):
        owner = source / 'skills' / name
        entry = owner / 'SKILL.md.in'
        if not entry.is_file():
            raise BundleError(f'Missing source entry: {entry}')
        pending = sorted(p for p in owner.rglob('*') if p.is_file())
        seen: set[Path] = set()
        bundle = output / name

        def destination(path: Path) -> Path:
            # 1. 技能仅维护入口和调用配置；共享资料按原相对路径进入自身 references。
            if path.is_relative_to(owner):
                relative = path.relative_to(owner)
                if relative == Path('SKILL.md.in'):
                    return bundle / 'SKILL.md'
                if relative.parts[0] == 'agents':
                    return bundle / relative
            references = source / 'references'
            if path.is_relative_to(references):
                return bundle / 'references' / path.relative_to(references)
            raise BundleError(f'Unsupported source dependency; use shared references: {path}')

        while pending:
            path = pending.pop()
            if path in seen:
                continue
            if path.is_symlink() or not path.resolve().is_relative_to(source):
                raise BundleError(f'Source dependency escapes its root or uses a symlink: {path}')
            seen.add(path)
            target = destination(path)
            content = path.read_bytes()
            if path.suffix == '.md' or path.name == 'SKILL.md.in':
                def replace(link: str) -> str:
                    parts = urlsplit(link)
                    if parts.scheme or parts.netloc or not parts.path:
                        return link
                    # 2. 收集引用闭包，并按输出位置改写链接；不读取另一个 SKILL 正文。
                    dependency = (path.parent / unquote(parts.path)).resolve()
                    if not dependency.is_relative_to(source) or not dependency.is_file():
                        raise BundleError(f'{path}: missing or external dependency: {link}')
                    mapped = destination(dependency)
                    if not mapped.is_relative_to(bundle):
                        raise BundleError(f'Dependency escapes installed skill: {link}')
                    pending.append(dependency)
                    relative = Path(os.path.relpath(mapped, target.parent)).as_posix()
                    suffix = ('?' + parts.query if parts.query else '')
                    suffix += '#' + parts.fragment if parts.fragment else ''
                    return quote(relative, safe='/._-') + suffix

                content = rewrite_links(content.decode('utf-8'), replace).encode('utf-8')
            if target in generated and generated[target] != content:
                raise BundleError(f'Two sources map to the same destination: {target}')
            generated[target] = content
    return generated


def synchronize(root: Path, write: bool) -> list[str]:
    """校验输出漂移；写入模式只更新专属生成目录并清除已失去来源的文件。"""
    expected = build_files(root)
    output = root / 'plugins/project-docs/skills'
    present = {p for p in output.rglob('*') if p.is_file()}
    changes: list[str] = []
    # 3. 所有依赖先解析成功，再改动输出，避免缺失引用时留下部分构建。
    for path, data in sorted(expected.items()):
        if not path.is_file() or path.read_bytes() != data:
            changes.append(str(path.relative_to(root)))
            if write:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
    for path in sorted(present - expected.keys()):
        changes.append(f'{path.relative_to(root)} (stale)')
        if write:
            path.unlink()
    if write:
        for directory in sorted(output.rglob('*'), key=lambda p: len(p.parts), reverse=True):
            if directory.is_dir() and not any(directory.iterdir()):
                directory.rmdir()
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='regenerate self-contained skills')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        changes = synchronize(args.root.resolve(), args.write)
    except (OSError, ValueError, KeyError, StopIteration) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        return 1
    if changes and not args.write:
        print('FAIL: generated skills differ; run scripts/build_project_docs.py --write')
        for path in changes:
            print(f'  {path}')
        return 1
    print(f'PASS: self-contained project-docs skills; {len(changes)} files changed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
