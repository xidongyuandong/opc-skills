from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_plan_preservation_accepts_additive_update(tmp_path):
    before = tmp_path / "before.plan.md"
    after = tmp_path / "after.plan.md"
    before.write_text("# Plan\n\n## Module: alpha\n\nOriginal.\n", encoding="utf-8")
    after.write_text("# Plan\n\n## Module: alpha\n\nOriginal.\n\nMore evidence.\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_plan_preservation.py"), str(before), str(after)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_plan_preservation_rejects_module_deletion(tmp_path):
    before = tmp_path / "before.plan.md"
    after = tmp_path / "after.plan.md"
    before.write_text("# Plan\n\n## Module: alpha\n\nA.\n\n## Module: beta\n\nB.\n", encoding="utf-8")
    after.write_text("# Plan\n\n## Module: alpha\n\nA.\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_plan_preservation.py"), str(before), str(after)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "module headings disappeared" in result.stdout


def test_plan_preservation_does_not_treat_denied_as_approval(tmp_path):
    before = tmp_path / "before.plan.md"
    after = tmp_path / "after.plan.md"
    before.write_text("## Module: alpha\nA.\n\n## Module: beta\nB.\n", encoding="utf-8")
    after.write_text(
        "## Module: alpha\nA.\n\nPlan History Deletion Approval: denied\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_plan_preservation.py"), str(before), str(after)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "module headings disappeared" in result.stdout


def test_plan_preservation_enforces_exact_fifteen_percent_boundary(tmp_path):
    before = tmp_path / "before.plan.md"
    exact = tmp_path / "exact.plan.md"
    over = tmp_path / "over.plan.md"
    before.write_text("\n".join(f"line {index}" for index in range(100)), encoding="utf-8")
    exact.write_text("\n".join(f"line {index}" for index in range(85)), encoding="utf-8")
    over.write_text("\n".join(f"line {index}" for index in range(84)), encoding="utf-8")
    exact_result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_plan_preservation.py"), str(before), str(exact)],
        capture_output=True,
        text=True,
        check=False,
    )
    over_result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_plan_preservation.py"), str(before), str(over)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert exact_result.returncode == 0
    assert over_result.returncode == 1


def test_requirement_evaluator_accepts_complete_plan(tmp_path):
    plan = tmp_path / "feature.plan.md"
    plan.write_text(
        """# Feature Plan

## Requirement clarification
- Goal: ship a portable feature.
- Evidence: current source and tests were inspected.

## Plan
### Contradiction analysis
- [portability] vs [local convenience]
- main contradiction: portability.
- Monitor: dependency drift.

### Approach exploration
| Approach | Decision | Validation | Risk / rollback |
|---|---|---|---|
| 1 | reject | inspect | none |
| 2 | reject | search | none |
| 3 | reject | research | none |
| 4 | adopt | focused test | revert commit |
| 5 | reject | architecture review | revert branch |

### Selected approach
- Minimal portable change.

## Todo list
- Positive impact: reusable behavior.
- Rollback: revert commit.
- Validation: run focused tests.

## Confirmation gate
- Waiting for one plan-level confirmation.
""",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/evaluate_requirement_plan.py"), str(plan)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_requirement_evaluator_rejects_fewer_than_five_approaches(tmp_path):
    plan = tmp_path / "incomplete.plan.md"
    plan.write_text(
        """## Requirement clarification
Goal: portable change. Evidence: source inspected.
## Contradiction analysis
[A] vs [B]. main contradiction: A. Monitor: B.
## Approach exploration
| # | Approach | Decision |
|---|---|---|
| 1 | evidence first | adopt |
| 2 | minimal | reject |
| 3 | architecture | reject |
| 4 | external research | reject |
## Selected approach
Minimal.
## Todo list
Positive impact. Rollback. Validation.
## Confirmation gate
Waiting for one plan-level confirmation.
""",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/evaluate_requirement_plan.py"), str(plan)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "expected numbered rows 1-5" in result.stdout


def test_requirement_evaluator_ignores_complete_historical_module(tmp_path):
    plan = tmp_path / "historical-only.plan.md"
    plan.write_text(
        """## Module: current
active_module_key: current
Current plan is incomplete.

## Historical Module: old
Goal: old goal. Evidence: old evidence.
## Requirement clarification
## Contradiction analysis
[A] vs [B]. main contradiction: A. Monitor: B.
## Approach exploration
| 1 | old | reject |
| 2 | old | reject |
| 3 | old | reject |
| 4 | old | reject |
| 5 | old | adopt |
## Selected approach
## Todo list
Positive impact. Rollback. Validation.
## Confirmation gate
Waiting for one plan-level confirmation.
""",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/evaluate_requirement_plan.py"), str(plan)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "clarification" in result.stdout


def test_requirement_evaluator_rejects_duplicate_current_module_keys(tmp_path):
    plan = tmp_path / "duplicate.plan.md"
    plan.write_text(
        """## Module: first
active_module_key: duplicate
## Module: second
active_module_key: duplicate
""",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/evaluate_requirement_plan.py"), str(plan)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "duplicate current keys" in result.stdout


def complete_module(name: str, key: str) -> str:
    return f"""## Module: {name}
active_module_key: {key}
## Requirement clarification
Goal: portable change. Evidence: current source inspected.
## Contradiction analysis
[A] vs [B]. main contradiction: A. Monitor: B.
## Approach exploration
| 1 | evidence first | reject |
| 2 | existing solution | reject |
| 3 | external research | reject |
| 4 | minimal | adopt |
| 5 | architecture | reject |
## Selected approach
Minimal.
## Todo list
Positive impact. Rollback. Validation.
## Confirmation gate
Waiting for one plan-level confirmation.
"""


def test_requirement_evaluator_validates_every_current_module(tmp_path):
    plan = tmp_path / "second-incomplete.plan.md"
    plan.write_text(
        complete_module("first", "first")
        + "\n## Module: second\nactive_module_key: second\nIncomplete.\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/evaluate_requirement_plan.py"), str(plan)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "## Module: second clarification" in result.stdout


def test_requirement_evaluator_requires_keys_for_multiple_modules(tmp_path):
    plan = tmp_path / "missing-key.plan.md"
    second_without_key = complete_module("second", "second").replace(
        "active_module_key: second\n", ""
    )
    plan.write_text(complete_module("first", "first") + "\n" + second_without_key, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/evaluate_requirement_plan.py"), str(plan)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "expected exactly one active_module_key" in result.stdout


def test_requirement_evaluator_rejects_repeated_approach_number(tmp_path):
    plan = tmp_path / "repeated-number.plan.md"
    repeated = complete_module("only", "only").replace(
        "| 2 | existing solution | reject |\n"
        "| 3 | external research | reject |\n"
        "| 4 | minimal | adopt |\n"
        "| 5 | architecture | reject |",
        "| 1 | existing solution | reject |\n"
        "| 1 | external research | reject |\n"
        "| 1 | minimal | adopt |\n"
        "| 1 | architecture | reject |",
    )
    plan.write_text(repeated, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/evaluate_requirement_plan.py"), str(plan)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "found [1]" in result.stdout
