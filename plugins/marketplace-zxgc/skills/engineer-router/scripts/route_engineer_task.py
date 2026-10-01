#!/usr/bin/env python3
"""Emit a portable role suggestion and a separately bound project context."""
from __future__ import annotations

import argparse
import json

from product_scope import resolve_context


def route_task(text: str, *, product_line: str = "shared", workspace: str) -> dict:
    context = resolve_context(text, product_line=product_line, workspace=workspace)
    lowered = text.casefold()
    if any(word in lowered for word in ("orchestrat", "agent", "编排", "智能体")):
        role = "workflow-engineer"
    elif any(word in lowered for word in ("data", "dataset", "数据")):
        role = "data-engineer"
    elif any(word in lowered for word in ("review", "审查", "审阅")):
        role = "reviewer"
    else:
        role = "software-engineer"
    return {
        "schema_version": 1,
        "status": "routed",
        "primary_role": role,
        "role_semantics": "advisory_label_only",
        "product_context": context,
        "runtime_action": "none",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", nargs="?", help="task description (or use --task)")
    parser.add_argument("--task", help="task description")
    parser.add_argument("--product-line", default="shared", help="explicit arbitrary project identifier")
    parser.add_argument("--workspace", required=True, help="existing project directory")
    args = parser.parse_args()
    try:
        if args.text is not None and args.task is not None:
            raise ValueError("supply either positional text or --task")
        result = route_task(args.task if args.task is not None else args.text,
                            product_line=args.product_line, workspace=args.workspace)
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
