from pathlib import Path


SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"


def test_execution_contract_contains_core_gates():
    text = SKILL.read_text(encoding="utf-8")
    required = [
        "执行入口门禁",
        "确认边界",
        "编码前先检索",
        "工作树安全",
        "测试驱动开发与缺陷修复",
        "逐级验证",
        "证据收尾",
        "完成输出签名",
        "它证明了什么、不能证明什么",
    ]
    for marker in required:
        assert marker in text


def test_contract_does_not_hardcode_a_home_directory():
    text = SKILL.read_text(encoding="utf-8")
    assert "/" + "Users/" not in text
    assert "/" + "home/" not in text


def test_markdown_artifacts_default_to_simplified_chinese():
    template = SKILL.parent / "templates" / "code-exec-task-checklist.md"
    for path in (SKILL, template):
        text = path.read_text(encoding="utf-8")
        assert "Markdown 产物默认使用简体中文" in text
        assert "命令、路径和链接可保留英文" in text
