"""Validate a task contract and compile a proposed subagent spawn call.

This module never starts an agent, executes a command, or grants filesystem
permissions. The caller must verify its router handoff before calling it and
must independently confirm the actual spawned model and task outcome.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'engineer-router/scripts'))
import product_scope


POLICY_PATH = Path(__file__).resolve().parents[1] / "references" / "tiered-execution-policy.json"
REQUIRED = frozenset({
    "task_id", "task_class", "goal", "confirmed", "allowed_files",
    "evidence_refs", "acceptance", "constraints", "available_models",
    "write_owner", "active_write_owners", "attempt", "failure_reason",
})
CLASSES = frozenset({"simple", "readonly", "bounded_write", "complex", "high_risk"})
ESCALATION_CODES = frozenset({
    "permission", "权限", "model_unavailable", "unknown_model", "模型不可用",
    "ambiguous", "歧义",
})


def _result(status, reason, task_class=None, model_tier=None, write_owner="",
            context_refs=None, fallback="primary_agent"):
    return {
        "status": status,
        "reason": reason,
        "task_class": task_class,
        "model_tier": model_tier,
        "write_owner": write_owner,
        "context_refs": context_refs if context_refs is not None else [],
        "fallback": fallback,
    }


def _nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _string_list(value, nonempty=False):
    return (isinstance(value, list) and (not nonempty or bool(value))
            and all(_nonempty_string(item) for item in value))


def _absolute_paths(paths, file_only=False):
    if not _string_list(paths):
        raise ValueError("path list must contain strings")
    result = []
    for raw in paths:
        path = Path(raw)
        if not path.is_absolute():
            raise ValueError("path must be absolute: " + raw)
        resolved = path.resolve(strict=False)
        if file_only:
            if resolved.is_dir() or (resolved.exists() and not resolved.is_file()):
                raise ValueError("write allowlist path must be a file: " + raw)
            if not resolved.parent.is_dir():
                raise ValueError("write allowlist parent must be an existing directory: " + raw)
        result.append(str(resolved))
    return result


def _read_policy():
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    if (not isinstance(policy, dict) or type(policy.get("version")) is not int
            or policy["version"] != 1 or not isinstance(policy.get("models"), dict)
            or type(policy.get("max_attempts")) is not int
            or policy["max_attempts"] < 1
            or type(policy.get("max_context_chars")) is not int
            or policy["max_context_chars"] < 1
            or any(not _nonempty_string(policy["models"].get(tier))
                   for tier in ("strong", "worker", "scout"))):
        raise ValueError("invalid tiered execution policy")
    return policy


def _task_name(task_id, attempt):
    slug = re.sub(r"[^a-z0-9]+", "_", task_id.lower()).strip("_")[:32]
    digest = hashlib.sha256(task_id.encode("utf-8")).hexdigest()[:8]
    return "task_" + (slug or "item") + "_a" + str(attempt) + "_" + digest


def prepare_execution(contract: dict, expected_product_context: dict | None = None,
                      expected_active_module_key: str | None = None) -> dict:
    """Return an explicit routing decision and, only if ready, spawn_args.

    ``confirmed`` is an input assertion, not authorization: the caller must
    separately enforce its execution handoff and user confirmation gate.
    """
    if not contract:
        return _result("recover_contract", "task contract is absent; recover the confirmed source")
    if not isinstance(contract, dict):
        return _result("blocked", "task contract must be an object")

    scoped_fields = {'product_context', 'active_module_key'}
    if expected_product_context is not None or scoped_fields.intersection(contract):
        try:
            if expected_product_context is None:
                raise ValueError('independent expected_product_context required for scoped execution')
            product_scope.validate_recovery(expected_product_context, contract, expected_active_module_key)
        except ValueError as exc:
            return _result('blocked', str(exc))

    missing = REQUIRED - contract.keys()
    if missing:
        return _result("blocked", "task contract missing fields: " + ", ".join(sorted(missing)),
                       contract.get("task_class"))
    task_class = contract["task_class"]
    if contract["confirmed"] is not True:
        return _result("blocked", "task contract is not explicitly confirmed", task_class)
    if not isinstance(task_class, str) or task_class not in CLASSES:
        return _result("escalate_primary", "unknown task class", task_class)
    if contract.keys() - REQUIRED - scoped_fields:
        return _result("escalate_primary", "unknown contract fields require primary review", task_class)

    try:
        policy = _read_policy()
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return _result("escalate_primary", "policy unavailable or invalid: " + str(exc), task_class)

    if (not isinstance(contract["task_id"], str)
            or not isinstance(contract["goal"], str)
            or type(contract["confirmed"]) is not bool
            or not isinstance(contract["acceptance"], list)
            or not isinstance(contract["constraints"], list)
            or not _string_list(contract["available_models"], nonempty=True)
            or not isinstance(contract["write_owner"], str)
            or not isinstance(contract["active_write_owners"], dict)
            or type(contract["attempt"]) is not int or contract["attempt"] < 0
            or not isinstance(contract["failure_reason"], str)):
        return _result("escalate_primary", "invalid contract field type or empty required content", task_class)
    if (not contract["task_id"].strip() or not contract["goal"].strip()
            or not contract["acceptance"] or not contract["constraints"]):
        return _result("blocked", "task contract has empty required fields", task_class)
    if (not _string_list(contract["acceptance"], nonempty=True)
            or not _string_list(contract["constraints"], nonempty=True)):
        return _result("escalate_primary", "acceptance and constraints require nonempty strings", task_class)

    try:
        allowed_files = _absolute_paths(contract["allowed_files"], file_only=True)
        evidence_refs = _absolute_paths(contract["evidence_refs"])
        if expected_product_context is not None:
            product_scope.validate_execution_paths(expected_product_context, allowed_files + evidence_refs)
        owner_items = contract["active_write_owners"].items()
        active_owners = {}
        for raw_path, owner in owner_items:
            if not _nonempty_string(raw_path) or not _nonempty_string(owner):
                raise ValueError("active write owners need absolute paths and nonempty owners")
            path = _absolute_paths([raw_path], file_only=True)[0]
            if path in active_owners and active_owners[path] != owner:
                raise ValueError("conflicting owners resolve to the same path")
            active_owners[path] = owner
    except (TypeError, ValueError, OSError, RuntimeError) as exc:
        return _result("escalate_primary", "invalid or conflicting path ownership: " + str(exc), task_class)

    packet = {
        "task_id": contract["task_id"],
        "task_class": task_class,
        "goal": contract["goal"],
        "allowed_files": allowed_files,
        "evidence_refs": evidence_refs,
        "acceptance": contract["acceptance"],
        "constraints": contract["constraints"],
        "write_owner": contract["write_owner"],
        "attempt": contract["attempt"],
        "failure_reason": contract["failure_reason"],
    }
    if expected_product_context is not None:
        packet['product_context'] = expected_product_context
        packet['active_module_key'] = contract['active_module_key']
    packet_json = json.dumps(packet, ensure_ascii=False, separators=(",", ":"))
    if len(packet_json) > policy["max_context_chars"]:
        return _result("escalate_primary", "task context exceeds policy max_context_chars; no truncation",
                       task_class, context_refs=evidence_refs)
    if contract["attempt"] >= policy["max_attempts"]:
        return _result("escalate_primary", "retry limit reached; primary agent must inspect failure",
                       task_class, context_refs=evidence_refs)
    failure_code = contract["failure_reason"].split(":", 1)[0].strip().lower()
    if failure_code in ESCALATION_CODES:
        return _result("escalate_primary", "non-retryable failure code: " + failure_code,
                       task_class, context_refs=evidence_refs)
    if task_class in {"complex", "high_risk"}:
        return _result("escalate_primary", "complex or high-risk task requires primary judgment",
                       task_class, model_tier="strong", context_refs=evidence_refs)

    if task_class in {"bounded_write", "simple"}:
        if task_class == "bounded_write" and (
                not _nonempty_string(contract["write_owner"]) or not allowed_files):
            return _result("escalate_primary", "bounded write requires owner and allowed files",
                           task_class, context_refs=evidence_refs)
        for path in allowed_files:
            if path in active_owners and active_owners[path] != contract["write_owner"]:
                return _result("escalate_primary", "write ownership conflict on resolved path",
                               task_class, write_owner=contract["write_owner"], context_refs=evidence_refs)
    elif contract["write_owner"].strip() or allowed_files:
        return _result("escalate_primary", "non-write task carries write owner or allowed files",
                       task_class, context_refs=evidence_refs)

    if task_class == "simple":
        return _result("inline", "simple confirmed task stays with primary agent",
                       task_class, context_refs=evidence_refs, fallback="primary_agent_inline")

    tier = "scout" if task_class == "readonly" else "worker"
    model = policy["models"][tier]
    if model not in contract["available_models"]:
        return _result("escalate_primary", "selected policy model is unavailable in this session",
                       task_class, model_tier=tier, write_owner=contract["write_owner"],
                       context_refs=evidence_refs)
    remaining = policy["max_attempts"] - contract["attempt"]
    instructions = (
        "You are not alone in the codebase. Do not revert others' edits. "
        "Do not delegate or spawn subagents. Work only within this task contract. "
        "Remaining attempts: " + str(remaining) + "; do not exceed this limit. "
        "Stop and report to the primary agent if scope, permissions, ownership, "
        "evidence, or acceptance are ambiguous, or if this attempt fails. "
        "For readonly work, make no file changes. For bounded_write work, modify "
        "only allowed_files. Return summary, artifacts, tests, risks, and "
        "escalation_reason (empty if none)."
    )
    message = instructions + "\nTask packet: " + packet_json
    if len(message) > policy["max_context_chars"]:
        return _result("escalate_primary", "full spawn message exceeds policy max_context_chars; no truncation",
                       task_class, model_tier=tier, write_owner=contract["write_owner"],
                       context_refs=evidence_refs)
    output = _result("ready", "validated task packet is ready for primary agent to spawn",
                     task_class, model_tier=tier, write_owner=contract["write_owner"],
                     context_refs=evidence_refs, fallback="escalate_primary_on_failure")
    output["spawn_args"] = {
        "agent_type": "default",
        "fork_turns": "none",
        "model": model,
        "reasoning_effort": "medium",
        "task_name": _task_name(contract["task_id"], contract["attempt"]),
        "message": message,
    }
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, type=Path, help="JSON task contract")
    parser.add_argument('--product-context', type=Path, help='Independent route context for scoped contracts')
    parser.add_argument('--active-module-key', help='Independent current confirmed module identity')
    args = parser.parse_args()
    try:
        contract = json.loads(args.contract.read_text(encoding="utf-8"))
        context = product_scope.load_context(args.product_context) if args.product_context else None
        result = prepare_execution(contract, expected_product_context=context,
                                   expected_active_module_key=args.active_module_key)
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        result = _result("blocked", "cannot read contract JSON: " + str(exc))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
