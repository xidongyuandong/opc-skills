from pathlib import Path


SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"


def test_execution_contract_contains_core_gates():
    text = SKILL.read_text(encoding="utf-8")
    required = [
        "Entry gate",
        "Confirmation boundary",
        "Search before coding",
        "Worktree safety",
        "TDD and bug fixes",
        "Verification ladder",
        "Evidence closeout",
        "Completion signature",
        "what it proves and what it cannot prove",
    ]
    for marker in required:
        assert marker in text


def test_contract_does_not_hardcode_a_home_directory():
    text = SKILL.read_text(encoding="utf-8")
    assert "/" + "Users/" not in text
    assert "/" + "home/" not in text
