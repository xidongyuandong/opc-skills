import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_applied_closure_ignores_stale_historical_text():
    module = load_module("closure", ROOT / "scripts/check_closure_consistency.py")
    payload = __import__("json").loads(
        (ROOT / "tests/fixtures/applied-closure.json").read_text(encoding="utf-8")
    )
    result = module.audit(payload)
    assert result["consistent"] is True


def test_closure_rejects_non_applied_or_mismatched_terminal_state():
    module = load_module("closure_invalid", ROOT / "scripts/check_closure_consistency.py")
    payload = {
        "terminal_state": "rejected",
        "active_sections": {
            "result": "No behavior change.",
            "progress": "Review complete.",
            "evaluation": "No action.",
            "owner": "workflow engineer",
            "trigger_status": "explicitly-invoked",
            "next_action": "awaiting user confirmation",
            "terminal_state": "applied",
        },
        "historical_sections": {},
    }
    result = module.audit(payload)
    assert result["consistent"] is False
    patterns = {conflict["pattern"] for conflict in result["conflicts"]}
    assert "not_applied" in patterns
    assert "terminal_state_mismatch" in patterns


def test_quality_evaluator_blocks_secret_like_assignments():
    module = load_module("quality", ROOT / "scripts/evaluate_summary_quality.py")
    sensitive_assignment = "pass" + "word" + "=" + "example-sensitive-value"
    result = module.evaluate("sample", "Result summary\nCore judgment\n" + sensitive_assignment)
    assert result["grade"] == "fail"
    assert result["blocking_secret_patterns"]
