#!/usr/bin/env python3
"""Format context into the standard auto-issue schema."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from typing import Literal


TargetType = Literal["issue_url", "repo_url", "unknown"]


SECRET_RE = re.compile(
    r"(?i)(token|secret|password|authorization|credential|cookie|private[_-]?key|api[_-]?key)"
    r"([\"'\\s:=]+)"
    r"([A-Za-z]+\\s+)?"
    r"([A-Za-z0-9_./+=\\-]{8,})"
)


@dataclass
class IssueDraft:
    title: str
    target_url: str
    target_type: TargetType
    body: str
    missing: list[str]


def scrub(text: str) -> str:
    return SECRET_RE.sub(lambda m: f"{m.group(1)}{m.group(2)}{m.group(3) or ''}[REDACTED]", text)


def classify_url(url: str) -> TargetType:
    if not url:
        return "unknown"
    if "/-/issues/" in url:
        return "issue_url"
    if re.match(r"^https?://[^/]+/.+/.+", url):
        return "repo_url"
    return "unknown"


def compact_lines(text: str, max_lines: int = 12) -> list[str]:
    lines = [line.strip() for line in scrub(text).splitlines() if line.strip()]
    return lines[:max_lines]


def infer_title(text: str, title: str | None) -> str:
    if title:
        return title.strip()
    lines = compact_lines(text, 1)
    if lines:
        first = re.sub(r"^[#*\\-\\d.\\s]+", "", lines[0])
        return first[:80] or "待提交 issue"
    return "待提交 issue"


def bullet_section(lines: list[str], fallback: str) -> str:
    if not lines:
        return f"- {fallback}"
    return "\n".join(f"- {line}" for line in lines)


def split_fragments(text: str) -> list[str]:
    fragments: list[str] = []
    for line in compact_lines(text, 24):
        parts = re.split(r"[;；]\s*", line)
        fragments.extend(part.strip() for part in parts if part.strip())
    return fragments


def strip_label(fragment: str) -> tuple[str, str]:
    match = re.match(r"^([#*\-\d.\s]*)(任务|问题|背景描述|背景|依赖|相关文件|文件|技能|预期效果|预期|效果|评测|验证|校验|测试)[:：\s]*(.+)$", fragment)
    if not match:
        return "", fragment
    return match.group(2), match.group(3).strip()


def extract_sections(text: str) -> dict[str, list[str]]:
    sections = {
        "task": [],
        "background": [],
        "dependencies": [],
        "expected": [],
        "evaluation": [],
    }
    for fragment in split_fragments(text):
        label, value = strip_label(fragment)
        if not value:
            continue
        if label in {"任务", "问题"}:
            sections["task"].append(value)
        elif label in {"背景描述", "背景"}:
            sections["background"].append(value)
        elif label in {"依赖", "相关文件", "文件", "技能"}:
            sections["dependencies"].append(value)
        elif label in {"预期效果", "预期", "效果"}:
            sections["expected"].append(value)
        elif label in {"评测", "验证", "校验", "测试"}:
            sections["evaluation"].append(value)
        elif not sections["task"]:
            sections["task"].append(value)
        else:
            sections["background"].append(value)
    return sections


def build_issue(text: str, url: str = "", title: str | None = None) -> IssueDraft:
    cleaned = scrub(text.strip())
    sections = extract_sections(cleaned)
    target_type = classify_url(url)
    missing: list[str] = []
    if target_type == "unknown":
        missing.append("target GitLab repo or issue URL")
    if not cleaned:
        missing.append("issue source context")

    issue_title = infer_title(cleaned, title)
    body = "\n\n".join(
        [
            "## 任务\n" + bullet_section(sections["task"][:3], "待补充要解决的问题。"),
            "## 背景描述\n" + bullet_section(sections["background"][:4], "待补充上下文、现象、日志或用户反馈。"),
            "## 依赖\n" + bullet_section(sections["dependencies"][:4], "待确认相关仓库、文件、技能、权限或外部服务。"),
            "## 预期效果\n" + bullet_section(sections["expected"][:3], "待确认完成后的可观察效果。"),
            "## 评测\n" + bullet_section(sections["evaluation"][:4], "待确认验证命令、检查项或验收标准。"),
        ]
    )
    return IssueDraft(
        title=issue_title,
        target_url=url,
        target_type=target_type,
        body=body,
        missing=missing,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", default="", help="Source context for the issue")
    parser.add_argument("--url", default="", help="GitLab issue or repository URL")
    parser.add_argument("--title", default="", help="Issue title override")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown")
    args = parser.parse_args()

    text = args.text or sys.stdin.read()
    draft = build_issue(text=text, url=args.url, title=args.title or None)

    if args.json:
        print(json.dumps(asdict(draft), ensure_ascii=False, indent=2))
    else:
        print(f"# {draft.title}\n")
        print(f"Target: {draft.target_url or '待确认'}")
        print(f"Target type: {draft.target_type}")
        if draft.missing:
            print("Missing: " + ", ".join(draft.missing))
        print()
        print(draft.body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
