#!/usr/bin/env python3
"""Lightweight structural evaluator for requirement plans."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


CHECKS = {
    "clarification": [r"Requirement clarification|需求澄清", r"Goal:|目标："],
    "evidence": [r"Evidence:|证据：|已检查"],
    "contradiction": [r"Contradiction analysis|矛盾分析", r"main contradiction|主要矛盾", r"Monitor:|监控"],
    "approaches": [r"Approach exploration|方案探索", r"Selected approach|最终选择"],
    "todo": [r"Todo list|Todo List|待办", r"Positive impact|正向影响", r"Rollback|回滚"],
    "validation": [r"Validation|验收|验证"],
    "confirmation": [r"Confirmation gate|确认门禁|Waiting for one plan-level confirmation"],
}

HISTORY_HEADING_RE = re.compile(r"(?m)^##\s+(?:Historical Module|Superseded Module)\b")
CURRENT_MODULE_RE = re.compile(r"(?m)^##\s+Module:\s*[^\n]+")
MODULE_KEY_RE = re.compile(r"(?mi)^\s*active_module_key\s*[:：]\s*`?([^`\s]+)`?\s*$")


def read_text(path: str) -> str:
    return sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")


def current_modules(text: str) -> list[tuple[str, str]]:
    """Return every current module while excluding historical modules."""
    history = HISTORY_HEADING_RE.search(text)
    current = text[: history.start()] if history else text
    modules = list(CURRENT_MODULE_RE.finditer(current))
    if not modules:
        return [("document", current)]
    result: list[tuple[str, str]] = []
    for index, match in enumerate(modules):
        end = modules[index + 1].start() if index + 1 < len(modules) else len(current)
        result.append((match.group(0).strip(), current[match.start() : end]))
    return result


def module_key_errors(modules: list[tuple[str, str]]) -> list[str]:
    errors: list[str] = []
    keys: list[str] = []
    for label, body in modules:
        matches = [match.group(1).strip().lower() for match in MODULE_KEY_RE.finditer(body)]
        if len(modules) > 1 and len(matches) != 1:
            errors.append(f"{label}: expected exactly one active_module_key, found {len(matches)}")
        keys.extend(matches)
    duplicates = sorted({key for key in keys if keys.count(key) > 1})
    if duplicates:
        errors.append("duplicate current keys " + ", ".join(duplicates))
    return errors


def evaluate_module(label: str, text: str) -> list[str]:
    failures: list[str] = []
    for name, patterns in CHECKS.items():
        missing = [pattern for pattern in patterns if not re.search(pattern, text, re.I)]
        if missing:
            failures.append(f"{label} {name}: missing {missing}")
    approach_numbers = {
        int(number) for number in re.findall(r"(?m)^\s*\|\s*([1-5])\s*\|", text)
    }
    if approach_numbers != {1, 2, 3, 4, 5}:
        failures.append(
            f"{label} approaches: expected numbered rows 1-5, found {sorted(approach_numbers)}"
        )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path")
    args = parser.parse_args()
    original = read_text(args.path)
    modules = current_modules(original)
    failures: list[str] = []
    failures.extend(f"active_module_key: {error}" for error in module_key_errors(modules))
    for label, body in modules:
        failures.extend(evaluate_module(label, body))
    if failures:
        print("FAIL requirement plan structure")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS requirement plan structure")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
