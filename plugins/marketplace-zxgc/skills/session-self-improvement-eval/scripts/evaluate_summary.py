#!/usr/bin/env python3
"""Heuristically evaluate session-self-improvement summary artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SENSITIVE_PATTERNS = [
    re.compile(r"\b(token|secret|password|authorization|credential|cookie)\b\s*[:=]\s*\S+", re.I),
    re.compile(r"authorization\s*:\s*bearer\s+\S+", re.I),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"sk-[A-Za-z0-9]{16,}"),
    re.compile(r"/Users/[^/\s]+/"),
]


CHECKS = {
    "theme_split": {
        "points": 20,
        "patterns": [r"核心主张|core claim|主题|theme", r"读者|reader|future|未来", r"边界|boundary"],
    },
    "persistence_routing": {
        "points": 20,
        "patterns": [r"AGENTS\.md|memory|skill|hook|docs/总结|持久化", r"不写入|not persisted|no action|排除"],
    },
    "evidence_verification": {
        "points": 20,
        "patterns": [r"验证|validation|verified|命令|command|result|输出", r"`[^`]+`|\b[A-Za-z0-9_./~-]+\.md\b"],
    },
    "reuse_value": {
        "points": 20,
        "patterns": [r"如何|how to|流程|步骤|checklist|检查清单|next", r"实现|solve|解决|understand|理解"],
    },
    "safety_boundaries": {
        "points": 20,
        "patterns": [r"secret|token|敏感|auth|credential|cookie|密钥", r"边界|boundary|风险|risk"],
    },
}


def score_patterns(text: str, patterns: list[str], points: int) -> tuple[int, list[str]]:
    matched = 0
    missing: list[str] = []
    for pattern in patterns:
        if re.search(pattern, text, re.I):
            matched += 1
        else:
            missing.append(pattern)
    return round(points * matched / len(patterns)), missing


def find_sensitive(text: str) -> list[str]:
    hits: list[str] = []
    for pattern in SENSITIVE_PATTERNS:
        if pattern.search(text):
            hits.append(pattern.pattern)
    return hits


def evaluate_text(name: str, text: str) -> dict[str, object]:
    scores: dict[str, int] = {}
    findings: list[str] = []
    for area, spec in CHECKS.items():
        score, missing = score_patterns(text, spec["patterns"], spec["points"])
        scores[area] = score
        if missing:
            findings.append(f"{area}: missing signals {missing}")

    sensitive_hits = find_sensitive(text)
    blocking: list[str] = []
    if sensitive_hits:
        scores["safety_boundaries"] = min(scores["safety_boundaries"], 5)
        blocking.append(f"possible sensitive patterns in {name}: {sensitive_hits}")

    total = sum(scores.values())
    if blocking or total < 70:
        grade = "fail"
    elif total < 85:
        grade = "pass-with-fixes"
    else:
        grade = "pass"

    return {
        "artifact": name,
        "grade": grade,
        "score": total,
        "area_scores": scores,
        "findings": findings,
        "blocking_issues": blocking,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Markdown artifacts to evaluate")
    parser.add_argument("--stdin", action="store_true", help="Read one artifact from stdin")
    args = parser.parse_args()

    results: list[dict[str, object]] = []
    if args.stdin:
        results.append(evaluate_text("<stdin>", sys.stdin.read()))

    for path in args.paths:
        resolved = path.expanduser().resolve()
        if not resolved.exists():
            results.append(
                {
                    "artifact": str(resolved),
                    "grade": "fail",
                    "score": 0,
                    "area_scores": {},
                    "findings": [],
                    "blocking_issues": [f"missing artifact: {resolved}"],
                }
            )
            continue
        results.append(evaluate_text(str(resolved), resolved.read_text(encoding="utf-8", errors="replace")))

    if not results:
        parser.error("provide at least one path or --stdin")

    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    return 0 if all(result["grade"] != "fail" for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
