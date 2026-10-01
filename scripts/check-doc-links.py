#!/usr/bin/env python3
"""Offline Markdown file targets and published skill inventory checks (Python 3.9+).

Checks inline/image, reference, angle-autolink and HTML href/src links. Ignores examples in fenced
or inline code, HTML comments, external URLs, non-main GitHub revisions and anchor
fragments. Does not claim to validate every Markdown extension or heading slug.
"""
import argparse
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re
from typing import Optional
from urllib.parse import unquote, urlsplit


def blank(text: str) -> str:
    return ''.join('\n' if c == '\n' else ' ' for c in text)


def prose(text: str) -> str:
    """Mask examples without changing offsets used by diagnostics."""
    text = re.sub(r'<!--[\s\S]*?-->', lambda m: blank(m.group()), text)
    lines = []
    fence = None
    list_contents = []
    for line in text.splitlines(keepends=True):
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if fence:
            lines.append(blank(line))
            if re.match(r'^ {0,3}' + re.escape(fence[0]) + '{' + str(len(fence)) + r',}\s*$', line):
                fence = None
        elif marker:
            fence = marker.group(1)
            lines.append(blank(line))
        else:
            expanded = line.expandtabs(4)
            indent = len(expanded) - len(expanded.lstrip())
            if expanded.strip():
                while list_contents and indent < list_contents[-1]:
                    list_contents.pop()
            base = list_contents[-1] if list_contents else 0
            list_marker = re.match(r' *(?:[-+*]|[0-9]+[.)]) +', expanded)
            if list_marker and indent < base + 4:
                list_contents.append(list_marker.end())
                lines.append(line)
            elif expanded.strip() and indent >= base + 4:
                lines.append(blank(line))
            else:
                lines.append(line)
    text = ''.join(lines)
    return re.sub(r'(`+)(?!`)([\s\S]*?)(?<!`)\1(?!`)', lambda m: blank(m.group()), text)


def destination(text: str, start: int) -> Optional[str]:
    """Read angle-bracket or balanced-parenthesis destination, excluding title."""
    i = start
    while i < len(text) and text[i].isspace():
        i += 1
    if i < len(text) and text[i] == '<':
        end = text.find('>', i + 1)
        return text[i + 1:end] if end >= 0 else None
    out = []
    depth = 0
    while i < len(text):
        char = text[i]
        if char == '\\' and i + 1 < len(text):
            i += 1
            out.append(text[i])
        elif char == '(':
            depth += 1
            out.append(char)
        elif char == ')':
            if not depth:
                break
            depth -= 1
            out.append(char)
        elif char.isspace() and not depth:
            break
        else:
            out.append(char)
        i += 1
    return ''.join(out) or None


class HtmlLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        for key, value in attrs:
            if key in ('href', 'src') and value:
                self.links.append((self.getpos()[0], value))


def links(text: str) -> list[tuple[int, str]]:
    text = prose(text)
    found = []
    for match in re.finditer(r'\]\(\s*', text):
        target = destination(text, match.end())
        if target:
            found.append((text.count('\n', 0, match.start()) + 1, target))
    refs = {}
    def normalize(label: str) -> str:
        return ' '.join(label.split()).casefold()
    for match in re.finditer(r'^ {0,3}\[([^\]\n]+)\]:\s*', text, re.M):
        refs.setdefault(normalize(match.group(1)), destination(text, match.end()))
    for match in re.finditer(r'\[([^\]\n]+)\](?:\[([^\]\n]*)\])?', text):
        if text[match.end():match.end() + 1] in ('(', ':'):
            continue
        label = match.group(2) or match.group(1)
        target = refs.get(normalize(label))
        if target:
            found.append((text.count('\n', 0, match.start()) + 1, target))
    for match in re.finditer(r'<(https?://[^<>\s]+)>', text):
        found.append((text.count("\n", 0, match.start()) + 1, match.group(1)))
    parser = HtmlLinks()
    parser.feed(text)
    return found + parser.links


def local_target(url: str, source: Path, root: Path, repository: str) -> Optional[Path]:
    parsed = urlsplit(url)
    path = unquote(parsed.path)
    if parsed.netloc:
        host = parsed.netloc.lower()
        if host == 'github.com':
            prefix = '/' + repository + '/'
            if not path.startswith(prefix):
                return None
            parts = path[len(prefix):].split('/', 2)
            if len(parts) != 3 or parts[0] not in ('blob', 'tree') or parts[1] not in ('main', 'master', 'HEAD'):
                return None
            return root / parts[2]
        if host == 'raw.githubusercontent.com':
            prefix = '/' + repository + '/'
            if path.startswith(prefix):
                parts = path[len(prefix):].split('/', 1)
                if len(parts) == 2 and parts[0] in ('main', 'master', 'HEAD'):
                    return root / parts[1]
        return None
    if parsed.scheme or not path:
        return None
    return (root / path.lstrip('/')) if path.startswith('/') else source.parent / path


def exact_exists(path: Path, root: Path) -> bool:
    """Case-sensitive even on a case-insensitive macOS working copy."""
    relative = path.relative_to(root)
    current = root
    for part in relative.parts:
        if not current.is_dir() or part not in {p.name for p in current.iterdir()}:
            return False
        current /= part
    return current.exists()


def check_links(root: Path, repository: str) -> tuple[list[str], int]:
    root = root.resolve()
    errors = []
    checked = 0
    for source in sorted(root.rglob('*')):
        if not source.is_file() or source.suffix.lower() != '.md' or '.git' in source.relative_to(root).parts:
            continue
        for line, url in links(source.read_text(encoding='utf-8')):
            try:
                target = local_target(url, source, root, repository)
                if target is None:
                    continue
                checked += 1
                target = target.resolve()
                if not target.is_relative_to(root):
                    reason = 'outside repository'
                elif not exact_exists(target, root):
                    reason = 'missing file target'
                else:
                    continue
            except (OSError, ValueError) as error:
                reason = 'unreadable/invalid target: ' + type(error).__name__
            errors.append(f'{source.relative_to(root)}:{line}: {reason}: {url}')
    return errors, checked


def inventory_errors(label: str, names: list[str], actual: set[str]) -> list[str]:
    counts = Counter(names)
    errors = [f'{label}: duplicate skill {name}' for name, count in counts.items() if count > 1]
    errors += [f'{label}: missing packaged skill {name}' for name in sorted(actual - counts.keys())]
    errors += [f'{label}: unpackaged current skill {name}' for name in sorted(counts.keys() - actual)]
    return errors


def check_inventory(root: Path, repository: str = 'xidongyuandong/opc-skills') -> list[str]:
    root = root.resolve()
    base = root / 'plugins/marketplace-zxgc/skills'
    directories = {p.name for p in base.iterdir() if p.is_dir()} if base.is_dir() else set()
    actual = {name for name in directories if (base / name / 'SKILL.md').is_file()}
    errors = [f'packaged directory missing SKILL.md: {name}' for name in sorted(directories - actual)]
    if not actual:
        errors.append('no packaged skills found')
    for name in ('README.md', 'README.en.md'):
        path = root / name
        if not path.is_file():
            errors.append('missing navigation: ' + name)
            continue
        names = []
        for _, url in links(path.read_text(encoding='utf-8')):
            try:
                target = local_target(url, path, root, repository)
                if target is None:
                    continue
                target = target.resolve()
                if not target.is_relative_to(root):
                    errors.append(f'{name}: outside repository: {url}')
                    continue
                relative = target.relative_to(root).as_posix()
                match = re.fullmatch(r'plugins/marketplace-zxgc/skills/([^/]+)/SKILL\.md', relative)
                if match:
                    names.append(match.group(1))
            except (OSError, ValueError):
                errors.append(f'{name}: invalid navigation target: {url}')
        errors += inventory_errors(name, names, actual)
    catalog = root / 'docs/skills-catalog.md'
    if not catalog.is_file():
        return errors + ['missing docs/skills-catalog.md']
    text = catalog.read_text(encoding='utf-8')
    match = re.search(r'^## Packaged Skills\s*\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    if not match:
        return errors + ['catalog missing Packaged Skills section']
    names = re.findall(r'^\|\s*`([^`]+)`\s*\|', match.group(1), re.M)
    return errors + inventory_errors('catalog Packaged Skills', names, actual)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--repository', default='xidongyuandong/opc-skills')
    args = parser.parse_args()
    root = args.root.resolve()
    errors, count = check_links(root, args.repository)
    errors += check_inventory(root, args.repository)
    for error in errors:
        print(error)
    print(f'{count} local file links checked; {len(errors)} error(s). External URLs and heading anchors are not checked.')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
