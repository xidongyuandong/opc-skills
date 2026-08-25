#!/usr/bin/env python3
"""Deterministically check retrospective structure and obvious secret-like text."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


CHECKS = {
    "result": [r"Result summary|结果摘要", r"Core judgment|关键结论"],
    "evidence": [r"Evidence|证据", r"proves|证明", r"cannot prove|不能证明"],
    "corrections": [r"User corrections|用户纠偏|open loops?"],
    "ownership": [r"task owner|primary owner|主责"],
    "candidates": [r"candidate matrix|候选矩阵", r"terminal state|终态"],
    "evaluation": [r"Evaluation|评测", r"no-action|blocked-with-reason|deterministic"],
    "workflow": [r"Workflow|工作流", r"trigger|触发"],
    "safety": [r"Risk|风险", r"Rollback|回滚"],
}

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\b(?:token|secret|password|authorization|cookie)\b\s*[:=]\s*\S+", re.I),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bxox[baprs]-[0-9A-Za-z-]+\b"),
]


def evaluate(name: str, text: str) -> dict[str, object]:
    areas: dict[str, bool] = {}
    missing: list[str] = []
    for area, patterns in CHECKS.items():
        passed = all(re.search(pattern, text, re.I) for pattern in patterns)
        areas[area] = passed
        if not passed:
            missing.append(area)
    secret_hits = [pattern.pattern for pattern in SECRET_PATTERNS if pattern.search(text)]
    score = round(100 * sum(areas.values()) / len(areas))
    grade = "fail" if secret_hits or score < 70 else "pass-with-fixes" if score < 90 else "pass"
    return {
        "artifact": name,
        "grade": grade,
        "score": score,
        "areas": areas,
        "missing_areas": missing,
        "blocking_secret_patterns": secret_hits,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    results = []
    for path in args.paths:
        resolved = path.expanduser().resolve()
        if not resolved.exists():
            results.append({"artifact": str(resolved), "grade": "fail", "score": 0, "missing": True})
        else:
            results.append(evaluate(str(resolved), resolved.read_text(encoding="utf-8", errors="replace")))
    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    return 0 if all(item["grade"] != "fail" for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
