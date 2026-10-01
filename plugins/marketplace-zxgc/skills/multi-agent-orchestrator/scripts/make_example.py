"""Print an unconfirmed synthetic workflow; never dispatch or write state."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "engineer-router/scripts"))
from product_scope import load_context


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", required=True, type=Path)
    parser.add_argument("--model", action="append", required=True)
    parser.add_argument("--module", default="example-collaboration")
    args = parser.parse_args()
    context = load_context(args.context)
    workspace = Path(context["workspace"])
    tasks = []
    for task_id, relative in [("inspect_readme", "README.md"), ("inspect_catalog", "docs/skills-catalog.md")]:
        tasks.append({"id": task_id, "kind": "query", "difficulty": "low", "risk": "low",
            "goal": "Summarize this example evidence file", "dependencies": [],
            "allowed_files": [], "evidence_refs": [str(workspace / relative)],
            "acceptance": ["Summary matches source; coordinator verifies"],
            "constraints": ["Read only; no network or recursive delegation"]})
    state = {t["id"]: {"status": "pending", "accepted": False, "attempts": 0,
             "failure_reason": "", "usage": None} for t in tasks}
    print(json.dumps({"product_context": context, "active_module_key": args.module,
        "confirmed": False, "available_models": args.model,
        "capacity": {"total_slots": 3, "root_slots": 1}, "tasks": tasks, "state": state}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}))
        raise SystemExit(2)
