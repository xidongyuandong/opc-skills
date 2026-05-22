#!/usr/bin/env python3
"""Review and promote Codex learning candidates."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CODEX_HOME = Path.home() / ".codex"
LEARNING_DIR = CODEX_HOME / "learning"
CANDIDATES_FILE = LEARNING_DIR / "candidates.jsonl"
APPROVED_MEMORY_FILE = LEARNING_DIR / "approved-memories.jsonl"
EVALS_DIR = LEARNING_DIR / "evals"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return out


def append_jsonl(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")


def list_candidates(limit: int) -> int:
    candidates = [c for c in read_jsonl(CANDIDATES_FILE) if c.get("status") == "pending"]
    for item in candidates[-limit:]:
        print(f"{item['id']} [{item.get('kind')}] {item.get('project_name')} - {item.get('reason')}")
        evidence = str(item.get("evidence", "")).replace("\n", " ")
        print(f"  {evidence[:220]}")
    if not candidates:
        print("No pending learning candidates.")
    return 0


def promote(candidate_id: str, title: str | None) -> int:
    candidates = read_jsonl(CANDIDATES_FILE)
    match = next((c for c in candidates if c.get("id") == candidate_id), None)
    if not match:
        print(f"Candidate not found: {candidate_id}")
        return 1

    memory = {
        "id": match["id"],
        "timestamp": now_iso(),
        "project_id": match.get("project_id"),
        "project_name": match.get("project_name"),
        "title": title or match.get("reason") or match["id"],
        "content": match.get("evidence", ""),
        "source": "codex-learning-candidate",
        "kind": match.get("kind"),
    }
    append_jsonl(APPROVED_MEMORY_FILE, memory)
    print(f"Promoted memory: {memory['id']}")
    return 0


def export_eval(candidate_id: str) -> int:
    candidates = read_jsonl(CANDIDATES_FILE)
    match = next((c for c in candidates if c.get("id") == candidate_id), None)
    if not match:
        print(f"Candidate not found: {candidate_id}")
        return 1

    task = match.get("suggested_eval", {})
    project = match.get("project_name") or "global"
    path = EVALS_DIR / project / f"{task.get('id', candidate_id)}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(task, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(str(path))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_list = sub.add_parser("list")
    p_list.add_argument("--limit", type=int, default=20)
    p_promote = sub.add_parser("promote")
    p_promote.add_argument("candidate_id")
    p_promote.add_argument("--title")
    p_eval = sub.add_parser("export-eval")
    p_eval.add_argument("candidate_id")
    args = parser.parse_args()

    if args.cmd == "list":
        return list_candidates(args.limit)
    if args.cmd == "promote":
        return promote(args.candidate_id, args.title)
    if args.cmd == "export-eval":
        return export_eval(args.candidate_id)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
