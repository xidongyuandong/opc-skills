#!/usr/bin/env python3
"""Check that applied behavior candidates no longer look unconfirmed in active prose."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED = {
    "result",
    "progress",
    "evaluation",
    "owner",
    "trigger_status",
    "next_action",
    "terminal_state",
}

STALE = {
    "awaiting_confirmation": re.compile(r"awaiting (?:user )?confirmation|needs-user-confirmation", re.I),
    "apply_after_confirmation": re.compile(r"apply after confirmation|write after confirmation", re.I),
    "not_applied": re.compile(r"not yet applied|not applied yet", re.I),
}


def audit(payload: dict[str, Any]) -> dict[str, Any]:
    active = payload.get("active_sections", {})
    historical = payload.get("historical_sections", {})
    if not isinstance(active, dict) or not isinstance(historical, dict):
        raise ValueError("active_sections and historical_sections must be objects")
    missing = sorted(REQUIRED - set(active))
    conflicts: list[dict[str, str]] = []
    top_state = payload.get("terminal_state")
    active_state = active.get("terminal_state")
    if top_state != "applied":
        conflicts.append(
            {"section": "terminal_state", "pattern": "not_applied", "match": str(top_state)}
        )
    if active_state != top_state:
        conflicts.append(
            {
                "section": "active_sections.terminal_state",
                "pattern": "terminal_state_mismatch",
                "match": f"top={top_state!r}, active={active_state!r}",
            }
        )
    if top_state == "applied":
        for section, value in active.items():
            text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
            for name, pattern in STALE.items():
                match = pattern.search(text)
                if match:
                    conflicts.append({"section": section, "pattern": name, "match": match.group(0)})
    return {
        "terminal_state": top_state,
        "consistent": not missing and not conflicts,
        "missing_active_sections": missing,
        "conflicts": conflicts,
        "historical_section_count": len(historical),
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: check_closure_consistency.py <payload.json>", file=sys.stderr)
        return 2
    try:
        payload = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("payload must be an object")
        result = audit(payload)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["consistent"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
