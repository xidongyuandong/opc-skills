"""Contract tests for the tiered execution task compiler."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "tiered_execution.py"


@pytest.fixture
def compiler(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("tiered_execution", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({
        "version": 1,
        "models": {
            "strong": "your-primary-model",
            "worker": "your-worker-model",
            "scout": "your-scout-model",
        },
        "max_attempts": 2,
        "max_context_chars": 12000,
    }), encoding="utf-8")
    monkeypatch.setattr(module, "POLICY_PATH", policy)
    return module


def contract(**overrides):
    data = {
        "task_id": "T-42",
        "task_class": "bounded_write",
        "goal": "Fix parser edge case",
        "confirmed": True,
        "allowed_files": ["/tmp/parser.py"],
        "evidence_refs": ["/tmp/project/plan.md"],
        "acceptance": ["Parser rejects malformed input"],
        "constraints": ["Follow project AGENTS.md"],
        "available_models": ["your-primary-model", "your-worker-model", "your-scout-model"],
        "write_owner": "parser_worker",
        "active_write_owners": {},
        "attempt": 0,
        "failure_reason": "",
    }
    data.update(overrides)
    return data


def test_missing_contract_and_unconfirmed_never_spawn(compiler):
    assert compiler.prepare_execution({})["status"] == "recover_contract"
    result = compiler.prepare_execution(contract(confirmed=False))
    assert result["status"] == "blocked"
    assert "spawn_args" not in result
    missing = compiler.prepare_execution(contract(goal=""))
    assert missing["status"] == "blocked"


def test_unknown_class_and_invalid_field_type_escalate(compiler):
    assert compiler.prepare_execution(contract(task_class="surprise"))["status"] == "escalate_primary"
    result = compiler.prepare_execution(contract(acceptance="not a list"))
    assert result["status"] == "escalate_primary"
    assert "spawn_args" not in result


def test_long_context_is_not_silently_truncated(compiler):
    result = compiler.prepare_execution(contract(goal="x" * 12001))
    assert result["status"] == "escalate_primary"
    assert "context" in result["reason"].lower()
    assert "spawn_args" not in result


def test_resolved_path_conflict_escalates(compiler, tmp_path):
    target = tmp_path / "parser.py"
    alias = tmp_path / "parser-alias.py"
    target.write_text("", encoding="utf-8")
    alias.symlink_to(target)
    result = compiler.prepare_execution(contract(
        allowed_files=[str(alias)],
        active_write_owners={str(target): "other_worker"},
    ))
    assert result["status"] == "escalate_primary"
    assert "conflict" in result["reason"].lower()


def test_symlink_loop_escalates_without_traceback(compiler, tmp_path):
    loop = tmp_path / "loop.py"
    loop.symlink_to(loop)
    result = compiler.prepare_execution(contract(allowed_files=[str(loop)]))
    assert result["status"] == "escalate_primary"
    assert "spawn_args" not in result


def test_file_allowlist_rejects_directories_but_accepts_future_file(compiler, tmp_path):
    assert compiler.prepare_execution(contract(allowed_files=["/"]))["status"] == "escalate_primary"
    assert compiler.prepare_execution(contract(
        allowed_files=[str(tmp_path)],
    ))["status"] == "escalate_primary"
    assert compiler.prepare_execution(contract(
        active_write_owners={str(tmp_path): "other"},
    ))["status"] == "escalate_primary"
    assert compiler.prepare_execution(contract(
        allowed_files=[str(tmp_path / "new.py")],
    ))["status"] == "ready"
    assert compiler.prepare_execution(contract(
        allowed_files=[str(tmp_path / "missing" / "new.py")],
    ))["status"] == "escalate_primary"
    assert compiler.prepare_execution(contract(
        task_class="readonly", allowed_files=[], write_owner="",
        evidence_refs=[str(tmp_path)],
    ))["status"] == "ready"


def test_retry_limit_and_missing_model_escalate(compiler):
    retry = compiler.prepare_execution(contract(attempt=2, failure_reason="first two failed"))
    assert retry["status"] == "escalate_primary"
    model = compiler.prepare_execution(contract(available_models=["your-scout-model"]))
    assert model["status"] == "escalate_primary"


@pytest.mark.parametrize("failure_reason", [
    "permission", "权限", "model_unavailable", "unknown_model",
    "模型不可用", "ambiguous", "歧义", "permission: denied by platform",
])
def test_machine_failure_codes_escalate_on_first_attempt(compiler, failure_reason):
    result = compiler.prepare_execution(contract(attempt=1, failure_reason=failure_reason))
    assert result["status"] == "escalate_primary"
    assert "spawn_args" not in result


def test_free_text_failure_is_not_guessed_as_machine_code(compiler):
    result = compiler.prepare_execution(contract(
        attempt=1, failure_reason="Maybe a permission concern needs review",
    ))
    assert result["status"] == "ready"
    message = result["spawn_args"]["message"]
    assert "remaining attempts: 1" in message.lower()
    assert "Do not delegate" in message
    for key in ("summary", "artifacts", "tests", "risks", "escalation_reason"):
        assert key in message


def test_retry_uses_new_task_name(compiler):
    first = compiler.prepare_execution(contract(attempt=0))
    second = compiler.prepare_execution(contract(attempt=1, failure_reason="test failed"))
    assert first["status"] == second["status"] == "ready"
    assert first["spawn_args"]["task_name"] != second["spawn_args"]["task_name"]
    assert "_a0_" in first["spawn_args"]["task_name"]
    assert "_a1_" in second["spawn_args"]["task_name"]


def test_context_limit_counts_full_spawn_message(compiler):
    baseline = compiler.prepare_execution(contract())
    assert baseline["status"] == "ready"
    policy = json.loads(compiler.POLICY_PATH.read_text(encoding="utf-8"))
    policy["max_context_chars"] = len(baseline["spawn_args"]["message"]) - 1
    compiler.POLICY_PATH.write_text(json.dumps(policy), encoding="utf-8")
    limited = compiler.prepare_execution(contract())
    assert limited["status"] == "escalate_primary"
    assert "spawn_args" not in limited


def test_bounded_write_compiles_minimal_safe_spawn(compiler):
    result = compiler.prepare_execution(contract())
    assert result["status"] == "ready"
    assert result["model_tier"] == "worker"
    args = result["spawn_args"]
    assert args["agent_type"] == "default"
    assert args["fork_turns"] == "none"
    assert args["model"] == "your-worker-model"
    assert args["reasoning_effort"] == "medium"
    assert args["task_name"].islower()
    assert "available_models" not in args["message"]
    assert "not alone" in args["message"]
    assert "stop" in args["message"].lower()


def test_readonly_uses_scout_without_claiming_sandbox(compiler):
    result = compiler.prepare_execution(contract(
        task_class="readonly", allowed_files=[], write_owner="",
    ))
    assert result["status"] == "ready"
    assert result["spawn_args"]["agent_type"] == "default"
    assert result["spawn_args"]["model"] == "your-scout-model"
    assert "sandbox" not in result["spawn_args"]["message"].lower()


def test_simple_is_inline_and_complex_or_high_risk_escalates(compiler):
    simple = compiler.prepare_execution(contract(
        task_class="simple", allowed_files=["/tmp/parser.py"],
        write_owner="",
    ))
    assert simple["status"] == "inline"
    assert "spawn_args" not in simple
    for task_class in ("complex", "high_risk"):
        result = compiler.prepare_execution(contract(task_class=task_class))
        assert result["status"] == "escalate_primary"
        assert "spawn_args" not in result


def test_invalid_write_ownership_and_relative_paths_escalate(compiler):
    assert compiler.prepare_execution(contract(write_owner=""))["status"] == "escalate_primary"
    assert compiler.prepare_execution(contract(allowed_files=[]))["status"] == "escalate_primary"
    assert compiler.prepare_execution(contract(allowed_files=["relative.py"]))["status"] == "escalate_primary"
    assert compiler.prepare_execution(contract(
        task_class="readonly", allowed_files=["/tmp/a"], write_owner="worker",
    ))["status"] == "escalate_primary"


def test_policy_is_read_each_time(compiler, tmp_path):
    first = compiler.prepare_execution(contract())
    assert first["status"] == "ready"
    policy = json.loads(compiler.POLICY_PATH.read_text(encoding="utf-8"))
    policy["models"]["worker"] = "unavailable-new-model"
    compiler.POLICY_PATH.write_text(json.dumps(policy), encoding="utf-8")
    assert compiler.prepare_execution(contract())["status"] == "escalate_primary"


def test_cli_emits_json_without_spawning(tmp_path):
    contract_path = tmp_path / "contract.json"
    contract_path.write_text(json.dumps(contract(
        task_class="simple", allowed_files=[], write_owner="",
    )), encoding="utf-8")
    process = subprocess.run(
        [sys.executable, str(MODULE_PATH), "--contract", str(contract_path)],
        check=True, capture_output=True, text=True,
    )
    result = json.loads(process.stdout)
    assert result["status"] == "inline"
    assert "spawn_args" not in result


def test_cli_symlink_loop_emits_escalation_json(tmp_path):
    loop = tmp_path / "loop.py"
    loop.symlink_to(loop)
    contract_path = tmp_path / "contract.json"
    contract_path.write_text(json.dumps(contract(allowed_files=[str(loop)])), encoding="utf-8")
    process = subprocess.run(
        [sys.executable, str(MODULE_PATH), "--contract", str(contract_path)],
        check=True, capture_output=True, text=True,
    )
    assert json.loads(process.stdout)["status"] == "escalate_primary"
    assert "Traceback" not in process.stderr


def test_directory_symlink_and_directory_owner_are_rejected(compiler, tmp_path):
    alias = tmp_path / "directory-alias"
    alias.symlink_to(tmp_path, target_is_directory=True)
    result = compiler.prepare_execution(contract(allowed_files=[str(alias)]))
    assert result["status"] == "escalate_primary"
    result = compiler.prepare_execution(contract(
        allowed_files=[str(tmp_path / "new.py")],
        active_write_owners={str(alias): "other"},
    ))
    assert result["status"] == "escalate_primary"
