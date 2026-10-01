"""Validate a human/primary-agent-authored workflow and propose one wave.

No semantic decomposition, model/API call, tool execution, or state mutation occurs.
See module docstring and --help for the JSON contract.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


COMPILER_PATH = Path(__file__).resolve().parents[2] / "code-exec/scripts/tiered_execution.py"
spec = importlib.util.spec_from_file_location("code_exec_tiered_execution", COMPILER_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("code-exec compiler unavailable")
compiler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compiler)
product_scope = compiler.product_scope

KINDS = {"planning", "implementation", "evaluation", "research", "query"}
DIFFICULTIES = {"low", "medium", "high"}
RISKS = {"low", "high"}
STATUSES = {"pending", "running", "passed", "failed"}
WORKFLOW_KEYS = {"product_context", "active_module_key", "confirmed", "available_models",
                 "capacity", "tasks", "state"}
TASK_KEYS = {"id", "kind", "difficulty", "risk", "goal", "dependencies",
             "allowed_files", "evidence_refs", "acceptance", "constraints"}
STATE_KEYS = {"status", "accepted", "attempts", "failure_reason", "usage"}


def _require_object(value, keys, label):
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError(f"{label} must be an object with exactly {', '.join(sorted(keys))}")


def _strings(value, label, *, nonempty=False):
    if (not isinstance(value, list) or (nonempty and not value)
            or any(not isinstance(x, str) or not x.strip() for x in value)):
        raise ValueError(f"{label} must be a list of nonempty strings")


def _paths(value, label, *, write=False):
    _strings(value, label)
    try:
        return compiler._absolute_paths(value, file_only=write)
    except (OSError, ValueError, RuntimeError) as exc:
        raise ValueError(f"{label}: {exc}") from exc


def _validate(workflow, expected_context, expected_key):
    _require_object(workflow, WORKFLOW_KEYS, "workflow")
    product_scope.validate_recovery(expected_context, workflow, expected_key)
    if type(workflow["confirmed"]) is not bool:
        raise ValueError("confirmed must be an explicit boolean")
    _strings(workflow["available_models"], "available_models", nonempty=True)
    if len(set(workflow["available_models"])) != len(workflow["available_models"]):
        raise ValueError("duplicate available_models")
    cap = workflow["capacity"]
    _require_object(cap, {"total_slots", "root_slots"}, "capacity")
    if (type(cap["total_slots"]) is not int or type(cap["root_slots"]) is not int
            or cap["root_slots"] != 1 or cap["total_slots"] < 1):
        raise ValueError("capacity requires total_slots >= 1 and root_slots = 1")
    tasks = workflow["tasks"]
    state = workflow["state"]
    if not isinstance(tasks, list) or not isinstance(state, dict):
        raise ValueError("tasks must be a list and state must be an object")
    if not tasks:
        raise ValueError("tasks must be nonempty")
    ids = set()
    paths = {}
    for task in tasks:
        _require_object(task, TASK_KEYS, "task")
        task_id = task["id"]
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError("task id must be a nonempty string")
        if task_id in ids:
            raise ValueError("duplicate task id: " + task_id)
        ids.add(task_id)
        for field, choices in (("kind", KINDS), ("difficulty", DIFFICULTIES), ("risk", RISKS)):
            if not isinstance(task[field], str) or task[field] not in choices:
                raise ValueError(f"invalid {field} for {task_id}")
        if not isinstance(task["goal"], str) or not task["goal"].strip():
            raise ValueError("goal must be a nonempty string for " + task_id)
        for field in ("dependencies", "acceptance", "constraints"):
            _strings(task[field], f"{task_id}.{field}", nonempty=field != "dependencies")
        if len(set(task["dependencies"])) != len(task["dependencies"]):
            raise ValueError("duplicate dependency for " + task_id)
        writes = _paths(task["allowed_files"], f"{task_id}.allowed_files", write=True)
        reads = _paths(task["evidence_refs"], f"{task_id}.evidence_refs")
        product_scope.validate_execution_paths(expected_context, writes + reads)
        paths[task_id] = (set(writes), set(reads))
        if task["kind"] != "implementation" and writes:
            raise ValueError("only implementation tasks may carry allowed_files: " + task_id)
    if set(state) != ids:
        raise ValueError("state ids must exactly match task ids")
    for task in tasks:
        for dep in task["dependencies"]:
            if dep not in ids:
                raise ValueError(f"unknown dependency {dep} for {task['id']}")
            if dep == task["id"]:
                raise ValueError("dependency cycle at " + dep)
    visiting, visited = set(), set()
    task_by_id = {x["id"]: x for x in tasks}

    def visit(node):
        if node in visiting:
            raise ValueError("dependency cycle at " + node)
        if node in visited:
            return
        visiting.add(node)
        for dep in task_by_id[node]["dependencies"]:
            visit(dep)
        visiting.remove(node)
        visited.add(node)

    for task_id in ids:
        visit(task_id)
    for task_id, record in state.items():
        _require_object(record, STATE_KEYS, "state for " + task_id)
        if not isinstance(record["status"], str) or record["status"] not in STATUSES:
            raise ValueError("invalid status for " + task_id)
        if type(record["accepted"]) is not bool:
            raise ValueError("accepted must be a boolean for " + task_id)
        if record["accepted"] and record["status"] != "passed":
            raise ValueError("accepted cannot claim a task that is not passed: " + task_id)
        if type(record["attempts"]) is not int or record["attempts"] < 0:
            raise ValueError("attempts must be a nonnegative integer for " + task_id)
        if record["status"] != "pending" and record["attempts"] == 0:
            raise ValueError("nonpending task needs at least one attempt: " + task_id)
        if not isinstance(record["failure_reason"], str):
            raise ValueError("failure_reason must be a string for " + task_id)
        if record["status"] == "failed" and not record["failure_reason"].strip():
            raise ValueError("failed task needs failure_reason: " + task_id)
        if record["status"] == "passed" and record["failure_reason"].strip():
            raise ValueError("passed task cannot retain failure_reason: " + task_id)
        usage = record["usage"]
        if usage is not None:
            _require_object(usage, {"input_tokens", "output_tokens"}, "usage for " + task_id)
            if (record["attempts"] == 0 or any(type(v) is not int or v < 0 for v in usage.values())):
                raise ValueError("usage needs measured nonnegative tokens and an attempt: " + task_id)
    return paths


def _classify(task):
    if task["risk"] == "high":
        return "high_risk"
    if task["difficulty"] == "high" or task["kind"] in {"planning", "evaluation"}:
        return "complex"
    if task["kind"] == "implementation":
        return "bounded_write" if task["allowed_files"] else "complex"
    if task["kind"] in {"query", "research"} and task["difficulty"] == "low":
        return "readonly"
    return "complex"


def _usage(state):
    attempted = [record for record in state.values() if record["attempts"]]
    if not attempted or any(record["usage"] is None for record in attempted):
        return {"input_tokens": None, "output_tokens": None, "status": "unknown",
                "reported_task_subtotal": None, "overall_status": "unknown",
                "reason": "no reported usage or at least one attempted task lacks usage; "
                          "retry and primary-agent overhead are not independently verified"}
    subtotal = {"input_tokens": sum(x["usage"]["input_tokens"] for x in attempted),
                "output_tokens": sum(x["usage"]["output_tokens"] for x in attempted)}
    return {**subtotal, "reported_task_subtotal": subtotal, "status": "reported_task_subtotal",
            "overall_status": "unknown",
            "reason": "sum of supplied task usage only; retry and primary-agent overhead "
                      "are not independently verified"}


def plan_wave(workflow: dict, expected_context: dict, expected_key: str) -> dict:
    """Return a proposed wave. Caller owns every spawn, review, and state update."""
    paths = _validate(workflow, expected_context, expected_key)
    tasks, state = workflow["tasks"], workflow["state"]
    result = {"status": "proposed" if workflow["confirmed"] else "blocked",
              "active_module_key": expected_key, "wave": [], "deferred": {},
              "usage": _usage(state)}
    if not workflow["confirmed"]:
        result["reason"] = "workflow is not explicitly confirmed"
        result["deferred"] = {x["id"]: "workflow is not explicitly confirmed" for x in tasks
                              if state[x["id"]]["status"] == "pending"}
        return result
    if all(x["status"] == "passed" and x["accepted"] for x in state.values()):
        result["status"] = "complete"
        return result
    running = [t for t in tasks if state[t["id"]]["status"] == "running"]
    running_primary = [t for t in running if _classify(t) in {"complex", "high_risk"}]
    if len(running_primary) > 1:
        raise ValueError("multiple running tasks claim the single root slot")
    if any(_classify(t) == "high_risk" for t in running) and len(running) > 1:
        raise ValueError("running high-risk task violates global exclusivity")
    running_workers = len(running) - len(running_primary)
    if 1 + running_workers > workflow["capacity"]["total_slots"]:
        raise ValueError("running tasks plus root exceed capacity")
    worker_slots = workflow["capacity"]["total_slots"] - 1 - running_workers
    active_owners = {}
    active_reads = set()
    for task in running:
        active_reads.update(paths[task["id"]][1])
        for path in paths[task["id"]][0]:
            if path in active_owners:
                raise ValueError("running tasks claim conflicting write ownership: " + path)
            active_owners[path] = task["id"]
    if any(paths[t["id"]][0] & paths[other["id"]][1]
           for t in running for other in running if t["id"] != other["id"]):
        raise ValueError("running tasks have a write/read conflict")
    selected_writes = set()
    selected_reads = set()
    primary_selected = bool(running_primary)
    high_risk_running = any(_classify(t) == "high_risk" for t in running)
    high_risk_selected = False
    unaccepted_writes = {t["id"]: paths[t["id"]][0] for t in tasks
        if state[t["id"]]["status"] == "failed" or
        (state[t["id"]]["status"] == "passed" and not state[t["id"]]["accepted"]) or
        (state[t["id"]]["status"] == "pending" and state[t["id"]]["attempts"] > 0)}
    for task in tasks:
        task_id = task["id"]
        record = state[task_id]
        if record["status"] == "failed":
            result["deferred"][task_id] = "failed task requires primary review; no automatic retry"
            continue
        if record["status"] == "passed" and not record["accepted"]:
            result["deferred"][task_id] = "passed task awaits acceptance"
            continue
        if record["status"] != "pending":
            continue
        unmet = next((dep for dep in task["dependencies"] if
                      state[dep]["status"] != "passed" or not state[dep]["accepted"]), None)
        if unmet:
            result["deferred"][task_id] = f"dependency {unmet} is not passed and accepted"
            continue
        writes, reads = paths[task_id]
        task_class = _classify(task)
        if high_risk_running or high_risk_selected:
            result["deferred"][task_id] = "high-risk task requires exclusive execution"
            continue
        if task_class == "high_risk" and (running or result["wave"]):
            result["deferred"][task_id] = "high-risk task requires exclusive execution"
            continue
        if writes & (set(active_owners) | selected_writes):
            result["deferred"][task_id] = "write conflict with running or selected wave owner"
            continue
        if writes & (active_reads | selected_reads):
            result["deferred"][task_id] = "write/read conflict with running or selected wave reader"
            continue
        if any(reads & write_paths for owner, write_paths in unaccepted_writes.items()
               if owner != task_id):
            result["deferred"][task_id] = "evidence read overlaps failed or unaccepted write"
            continue
        if reads & (set(active_owners) | selected_writes):
            result["deferred"][task_id] = "evidence read overlaps running or selected wave write"
            continue
        primary = task_class in {"complex", "high_risk"}
        if primary and primary_selected:
            result["deferred"][task_id] = "primary agent already has a task in this wave"
            continue
        if not primary and worker_slots <= 0:
            result["deferred"][task_id] = "capacity has no free worker slot"
            continue
        contract = {
            "task_id": task_id, "task_class": task_class, "goal": task["goal"],
            "confirmed": workflow["confirmed"], "allowed_files": task["allowed_files"],
            "evidence_refs": task["evidence_refs"], "acceptance": task["acceptance"],
            "constraints": task["constraints"], "available_models": workflow["available_models"],
            "write_owner": task_id if task_class == "bounded_write" else "",
            "active_write_owners": active_owners, "attempt": record["attempts"],
            "failure_reason": record["failure_reason"],
            "product_context": workflow["product_context"],
            "active_module_key": workflow["active_module_key"],
        }
        decision = compiler.prepare_execution(contract, expected_product_context=expected_context,
                                              expected_active_module_key=expected_key)
        if primary:
            if (decision["status"] != "escalate_primary"
                    or decision["reason"] != "complex or high-risk task requires primary judgment"):
                result["deferred"][task_id] = "compiler refused primary routing: " + decision["reason"]
                continue
            result["wave"].append({"id": task_id, "route": "primary_agent",
                                   "task_class": task_class, "reason": decision["reason"]})
            primary_selected = True
            selected_writes.update(writes)
            selected_reads.update(reads)
            active_owners.update({path: task_id for path in writes})
            high_risk_selected = task_class == "high_risk"
        elif decision["status"] == "ready" and "spawn_args" in decision:
            result["wave"].append({"id": task_id, "route": "subagent",
                                   "task_class": task_class, "spawn_args": decision["spawn_args"]})
            selected_writes.update(writes)
            selected_reads.update(reads)
            active_owners.update({path: task_id for path in writes})
            worker_slots -= 1
        else:
            result["deferred"][task_id] = decision["reason"]
    if not result["wave"]:
        result["status"] = ("waiting" if running or any(
            x["status"] == "passed" and not x["accepted"] for x in state.values()) else "blocked")
        if any(x["status"] == "failed" for x in state.values()):
            result["status"] = "blocked"
    return result


def _markdown(result):
    lines = [f"# 当前 wave：{result['active_module_key']}", "",
             f"状态：{result['status']}。脚本未派生代理或修改任务状态。", ""]
    for item in result["wave"]:
        lines.append(f"- {item['id']}：{item['route']} / {item['task_class']}")
    for task_id, reason in result["deferred"].items():
        lines.append(f"- 暂缓 {task_id}：{reason}")
    lines.extend(["", "usage：" + result["usage"]["status"]])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow", required=True, type=Path, help="primary-authored workflow JSON")
    parser.add_argument("--product-context", required=True, type=Path,
                        help="independent resolved runtime product context JSON")
    parser.add_argument("--active-module-key", required=True, help="independent current module key")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    args = parser.parse_args()
    try:
        workflow = json.loads(args.workflow.read_text(encoding="utf-8"))
        context = product_scope.load_context(args.product_context)
        result = plan_wave(workflow, context, args.active_module_key)
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        result = {"status": "blocked", "reason": str(exc), "wave": [], "deferred": {},
                  "usage": {"input_tokens": None, "output_tokens": None, "status": "unknown"}}
    if args.format == "markdown" and "active_module_key" in result:
        print(_markdown(result))
    else:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] in {"proposed", "complete", "waiting"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
