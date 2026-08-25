#!/usr/bin/env python3
"""Detect accidental deletion of modules or large sections from a plan file."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


MODULE_RE = re.compile(
    r"(?m)^(?P<heading>##\s+(?:Module|Historical Module|Superseded Module)\b[^\n]*)"
)


@dataclass(frozen=True)
class Snapshot:
    path: Path
    text: str
    lines: int
    modules: tuple[str, ...]


def read_snapshot(path: str) -> Snapshot:
    resolved = Path(path)
    text = resolved.read_text(encoding="utf-8")
    modules = tuple(match.group("heading").strip().lower() for match in MODULE_RE.finditer(text))
    return Snapshot(resolved, text, len(text.splitlines()), modules)


def approved(text: str) -> bool:
    return bool(
        re.search(
            r"(?mi)^\s*(?:Plan History Deletion Approval|plan_history_deletion_approval)"
            r"\s*:\s*(?:true|approved|yes)\s*$",
            text,
        )
    )


def check(before: Snapshot, after: Snapshot) -> list[str]:
    errors: list[str] = []
    deletion_allowed = approved(after.text)
    missing = sorted(set(before.modules) - set(after.modules))
    if missing and not deletion_allowed:
        errors.append("module headings disappeared without approval: " + "; ".join(missing[:20]))
    if before.lines >= 80 and after.lines * 100 < before.lines * 85 and not deletion_allowed:
        errors.append(f"line count dropped from {before.lines} to {after.lines} (>15%)")
    if before.text and not after.text.strip():
        errors.append("after plan is empty")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before")
    parser.add_argument("after")
    args = parser.parse_args()
    before = read_snapshot(args.before)
    after = read_snapshot(args.after)
    errors = check(before, after)
    if errors:
        print("FAIL plan preservation guard")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS plan preservation guard")
    print(f"before={before.path} modules={len(before.modules)} lines={before.lines}")
    print(f"after={after.path} modules={len(after.modules)} lines={after.lines}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
