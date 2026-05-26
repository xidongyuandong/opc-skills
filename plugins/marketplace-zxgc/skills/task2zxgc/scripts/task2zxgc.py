#!/usr/bin/env python3
"""Create a task summary from a Codex session and optionally push it to GitLab."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


HOME = Path.home()


def env_first(*names: str, default: str = "") -> str:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return default


def path_from_env(*names: str, default: Path) -> Path:
    return Path(env_first(*names, default=str(default))).expanduser()


def repo_dir_name(repo_url: str) -> str:
    cleaned = repo_url.rstrip("/")
    if not cleaned:
        return "task2zxgc-reports"
    name = cleaned.rsplit("/", 1)[-1]
    if name.endswith(".git"):
        name = name[:-4]
    name = re.sub(r"[^\w.\-\u4e00-\u9fff]+", "-", name.strip(), flags=re.UNICODE)
    name = re.sub(r"-+", "-", name).strip("-._")
    return name[:80] or "task2zxgc-reports"


DEFAULT_REPO_URL = env_first(
    "TASK2ZXGC_REPO_URL",
    "TASK2ZXGC_GIT_REPO",
    default="https://gitlab.chehejia.com/ep/ai/ai-coding-zxgc-managment.git",
)
CODEX_HOME = path_from_env("TASK2ZXGC_CODEX_HOME", "CODEX_HOME", default=HOME / ".codex")
SESSIONS_DIR = CODEX_HOME / "sessions"
STATE_DIR = path_from_env("TASK2ZXGC_STATE_DIR", default=CODEX_HOME / "task2zxgc")
PENDING_FILE = STATE_DIR / "pending.json"
DEFAULT_REPO_DIR = path_from_env("TASK2ZXGC_REPO_DIR", default=STATE_DIR / repo_dir_name(DEFAULT_REPO_URL))
DEFAULT_AI_INSIGHTS_REPO = path_from_env("AI_INSIGHTS_REPO", default=HOME / "ai-insights")


@dataclass
class SessionSummary:
    session_path: Path
    session_id: str = ""
    user_messages: list[str] = field(default_factory=list)
    raw_user_inputs: list[str] = field(default_factory=list)
    assistant_finals: list[str] = field(default_factory=list)
    tool_events: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def sanitize_path_part(value: str, fallback: str) -> str:
    cleaned = re.sub(r"[^\w.\-\u4e00-\u9fff]+", "-", value.strip(), flags=re.UNICODE)
    cleaned = re.sub(r"-+", "-", cleaned).strip("-._")
    return cleaned[:80] or fallback


def display_path(path: Path) -> str:
    expanded = path.expanduser()
    for base, label in ((CODEX_HOME, "$CODEX_HOME"), (HOME, "$HOME")):
        try:
            return str(Path(label) / expanded.relative_to(base.expanduser()))
        except ValueError:
            continue
    return str(expanded)


def username() -> str:
    configured = env_first("TASK2ZXGC_USERNAME", "TASK2ZXGC_AUTHOR")
    if configured:
        return sanitize_path_part(configured, "unknown")
    try:
        result = run(["git", "config", "--get", "user.name"], check=False)
        if result.returncode == 0 and result.stdout.strip():
            return sanitize_path_part(result.stdout.strip(), "unknown")
    except OSError:
        pass
    return sanitize_path_part(os.environ.get("USER") or os.environ.get("USERNAME") or "unknown", "unknown")


def latest_session() -> Path:
    candidates = list(SESSIONS_DIR.glob("**/rollout-*.jsonl"))
    if not candidates:
        raise SystemExit(f"No Codex session files found under {SESSIONS_DIR}")
    return max(candidates, key=lambda path: path.stat().st_mtime)


def session_by_id(session_id: str) -> Path:
    matches = [path for path in SESSIONS_DIR.glob("**/rollout-*.jsonl") if session_id in path.name]
    if not matches:
        raise SystemExit(f"No Codex session found for session id: {session_id}")
    return max(matches, key=lambda path: path.stat().st_mtime)


def text_from_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text") or item.get("input_text")
                if isinstance(text, str):
                    parts.append(text)
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts)
    return ""


def append_unique(items: list[str], text: str, limit: int = 4000) -> None:
    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    if not text:
        return
    if len(text) > limit:
        text = text[:limit].rstrip() + "..."
    if text not in items:
        items.append(text)


def append_raw(items: list[str], text: str) -> None:
    if text:
        items.append(text)


def parse_session(path: Path) -> SessionSummary:
    summary = SessionSummary(session_path=path)
    fallback_user_inputs: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
            event_type = event.get("type")

            if event_type == "session_meta":
                summary.session_id = str(payload.get("id") or summary.session_id)
                continue

            item = payload if payload.get("type") else payload.get("item")
            if isinstance(item, dict) and item.get("type") == "message":
                role = item.get("role")
                text = text_from_content(item.get("content"))
                if role == "user":
                    append_raw(summary.raw_user_inputs, text)
                    append_unique(summary.user_messages, text)
                elif role == "assistant":
                    append_unique(summary.assistant_finals, text, limit=2500)

            if event_type == "event_msg":
                msg = str(payload.get("message") or payload.get("text") or "")
                if payload.get("type") == "user_message":
                    append_raw(fallback_user_inputs, msg)
                    append_unique(summary.user_messages, msg)
                elif payload.get("type") == "agent_message" and payload.get("phase") == "final_answer":
                    append_unique(summary.assistant_finals, msg, limit=2500)
                elif payload.get("type") in {"exec_command", "tool_result", "error"}:
                    append_unique(summary.tool_events, msg, limit=800)
                elif msg and any(token in msg.lower() for token in ["error", "failed", "permission", "traceback"]):
                    append_unique(summary.errors, msg, limit=800)

            if isinstance(item, dict):
                if item.get("type") in {"function_call", "local_shell_call"}:
                    name = str(item.get("name") or item.get("call_id") or item.get("type"))
                    args = item.get("arguments") or item.get("action") or ""
                    append_unique(summary.tool_events, f"{name}: {args}", limit=800)
                elif item.get("type") in {"function_call_output", "local_shell_call_output"}:
                    output = text_from_content(item.get("output") or item.get("content"))
                    if output:
                        append_unique(summary.tool_events, output, limit=800)
                        if re.search(r"\b(error|failed|permission denied|operation not permitted|traceback)\b", output, re.I):
                            append_unique(summary.errors, output, limit=800)

    if not summary.raw_user_inputs:
        summary.raw_user_inputs = fallback_user_inputs
    return summary


def bulletize(lines: list[str], max_items: int = 12) -> str:
    selected = [line.strip() for line in lines if line.strip()]
    if not selected:
        return "- 暂未从会话中提取到明确内容。"
    return "\n".join(f"- {line}" for line in selected[:max_items])


def compact_message(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text[:220] + ("..." if len(text) > 220 else "")


def is_internal_message(text: str) -> bool:
    stripped = text.lstrip()
    return stripped.startswith(("<environment_context>", "<skill>", "<turn_aborted>", "<permissions instructions>"))


def user_messages(summary: SessionSummary) -> list[str]:
    return [message for message in summary.user_messages if not is_internal_message(message)]


def raw_user_inputs(summary: SessionSummary) -> list[str]:
    return [message for message in summary.raw_user_inputs if not is_internal_message(message)]


def redact_sensitive_text(text: str) -> str:
    redacted = re.sub(
        r"(?i)\b(password|passwd|pwd|token|api[_-]?key|secret|cookie|authorization)\b\s*[:=]\s*([^\s,;]+)",
        r"\1=[REDACTED]",
        text,
    )
    redacted = re.sub(
        r"(密码|口令|密钥|令牌)\s*(?:是|为)?\s*[：:=]\s*[\s\S]*?(?=$|[，,；;。])",
        r"\1=[REDACTED]",
        redacted,
    )
    redacted = re.sub(r"(?i)\b(bearer|basic)\s+[A-Za-z0-9._~+/=-]{12,}", r"\1 [REDACTED]", redacted)

    stripped = redacted.strip()
    if re.fullmatch(r"[A-Za-z0-9_.@-]{2,64}\s+[A-Za-z0-9!@#$%^&*()_+=,.?-]{8,}", stripped):
        first, second = stripped.split(maxsplit=1)
        if re.search(r"[A-Za-z]", second) and re.search(r"\d", second):
            return f"{first} [REDACTED]"
    return redacted


def compact_user_input(text: str, limit: int = 500) -> str:
    text = redact_sensitive_text(text)
    if len(text) <= limit:
        return text
    omitted = len(text) - limit
    return f"{text[:limit]}\n\n...（已缩略 {omitted} 字）"


def markdown_code_fence(text: str) -> str:
    max_backticks = max((len(match.group(0)) for match in re.finditer(r"`+", text)), default=0)
    return "`" * max(3, max_backticks + 1)


def render_user_inputs(summary: SessionSummary, limit: int = 500) -> str:
    messages = raw_user_inputs(summary)
    if not messages:
        return "- 暂未从会话中提取到用户输入。"
    sections: list[str] = []
    for index, message in enumerate(messages, start=1):
        rendered = compact_user_input(message, limit=limit)
        fence = markdown_code_fence(rendered)
        sections.extend([f"### 用户输入 {index}", "", f"{fence}text", rendered, fence, ""])
    return "\n".join(sections).rstrip()


def task_title(summary: SessionSummary) -> str:
    for message in reversed(user_messages(summary)):
        task_match = re.search(r"[【\[]?(任务\d+)[】\]]?", message)
        if task_match:
            return sanitize_path_part(task_match.group(1), "codex-session-summary")
        for line in message.splitlines():
            line = line.strip()
            if line and not line.startswith("<") and len(line) > 3:
                title = line
                title = re.sub(r"^/task2zxgc\s*", "", title).strip() or title
                title = title.replace("实现需求文件的", "").strip()
                return sanitize_path_part(title[:60], "codex-session-summary")
    return "codex-session-summary"


def task_theme(summary: SessionSummary) -> str:
    return "未提供 Agent summary；请先使用 --dump-context 让 Codex Agent 归纳任务主题，再通过 --agent-summary-file、--agent-summary-json 或 --agent-summary-stdin 输入。"


def extract_requirements(summary: SessionSummary) -> list[str]:
    return [compact_message(message) for message in user_messages(summary)]


def extract_done(summary: SessionSummary) -> list[str]:
    done: list[str] = []
    for final in summary.assistant_finals:
        for line in re.split(r"[\n。；;]", final):
            line = line.strip(" -\t")
            if not line:
                continue
            if any(token in line for token in ["完成", "已", "实现", "迁移", "安装", "验证", "修改", "新增"]):
                done.append(compact_message(line))
    if not done and summary.assistant_finals:
        done = [compact_message(text) for text in summary.assistant_finals[-3:]]
    return done


def extract_improvements(summary: SessionSummary) -> list[str]:
    return ["未提供 Agent summary；待优化点必须由 Codex Agent 基于 --dump-context 输出归纳生成。"]


def evidence(summary: SessionSummary) -> list[str]:
    items: list[str] = []
    messages = user_messages(summary)
    items.extend(f"用户请求：{compact_message(message)}" for message in messages[-8:])
    items.extend(f"工具/执行记录：{compact_message(event)}" for event in summary.tool_events[-8:])
    return items


def ai_insights_reference(repo_dir: Path = DEFAULT_AI_INSIGHTS_REPO) -> dict[str, Any]:
    return {
        "source_repo": display_path(repo_dir),
        "purpose": "ai-insights 将 AI 编程会话解析为结构化 facets、prompt quality、friction、outcome 和 evidence sidecar，用于报告、评估和复核。",
        "reference_points": [
            "按单次会话提取 semantic facets，再聚合成跨会话报告；task2zxgc 可借鉴为单任务报告提供稳定诊断维度。",
            "friction 使用 canonical taxonomy，并要求 attribution、severity、confidence；task2zxgc 的待优化点应区分 user-actionable、ai-capability、environmental。",
            "effective_patterns 独立记录有效做法，避免报告只列问题；task2zxgc 应同时呈现执行中的有效模式。",
            "outcome guidance 默认以具体落地结果判断完成度，而不是等待用户明确说完成；task2zxgc 应单列执行结果和完成度。",
            "prompt quality 从 context、specificity、scope、timing、correction 评估需求输入质量；task2zxgc 应诊断需求描述本身的清晰度和约束时机。",
            "报告保留 evidence sidecar 思路：总结和诊断必须可回溯到用户请求、修改文件、验证命令或推送结果。",
        ],
        "recommended_agent_summary_fields": [
            "task_theme",
            "core_requirement",
            "raw_requirements",
            "requirements",
            "execution_process",
            "completed_tasks",
            "execution_result",
            "improvement_points",
            "diagnostics",
            "evidence",
        ],
    }


def session_context(summary: SessionSummary, ai_insights_repo: Path = DEFAULT_AI_INSIGHTS_REPO) -> dict[str, Any]:
    return {
        "session_id": summary.session_id,
        "session_path": display_path(summary.session_path),
        "user_messages": user_messages(summary),
        "raw_user_inputs": raw_user_inputs(summary),
        "assistant_final_messages": summary.assistant_finals,
        "tool_event_samples": summary.tool_events[-20:],
        "reference_points_ai_insights": ai_insights_reference(ai_insights_repo),
        "instructions": {
            "task_title": "短标题，用于 Markdown 标题和文件名；优先保留明确任务编号，例如 任务051902。",
            "theme_split": "先完整阅读上下文并执行主题拆分。每个报告只能服务一个独立技术主张；如果会话包含多个不能由同一句核心主张统摄的主题，必须输出 reports 数组，每个元素按单主题完整填写。不要只挑选局部重点。",
            "split_policy": "拆分数量取最小值：能用一个核心主张统摄则单报告；存在多个彼此独立的排障、实现、调研、仓库梳理或治理链路时拆成多个报告；拆分后每篇报告必须能独立阅读。",
            "material_type": "为每个报告选择主线：debug/troubleshooting、feature implementation、research/decision、repository analysis、general workflow、algorithm direction。",
            "core_claim": "每个报告的 task_theme/core_requirement 必须能表达对象、判断、价值和边界，避免写成按时间排列的会话流水账。",
            "task_theme": "用 1 段话总结本次任务的核心目标，不要复制原始消息。",
            "user_original_inputs": "独立模块，保留用户原始输入的脱敏摘录；按来源区分需求文件内容、命令行输入、会话用户消息等，用于评估用户是否高效使用智能体完成任务。",
            "requirements": "用条目归纳用户需求描述，可以保留关键路径、仓库、命令和约束。",
            "execution_process": "按阶段归纳任务执行过程，说明关键决策、实现步骤和验证动作，不要列原始工具流水账。",
            "completed_tasks": "用条目归纳已经完成的工作。",
            "execution_result": "诊断执行结果和完成度，参考 ai-insights outcome guidance，可包含 fully_achieved/mostly_achieved/partially_achieved/ongoing/unclear。",
            "improvement_points": "用条目总结需求描述中的待优化点，由 Agent 归纳，不要复制原始信息或工具错误日志。",
            "diagnostics": "对需求描述、任务执行过程、执行结果做全方位诊断；建议包含 category、attribution、severity、confidence、description、suggested_action。",
            "reference_points_ai_insights": "内部参考输入；用于提升各总结维度质量，不要作为 Agent summary 字段输出，也不要渲染成 Markdown 章节。",
            "evidence": "少量证据摘要，用于说明归纳依据。",
            "multi_report_shape": "多主题时输出 {\"reports\": [{...单报告字段...}, {...单报告字段...}]}；单主题时仍可输出原兼容 JSON object。",
        },
    }


def format_summary_item(item: Any) -> str:
    if isinstance(item, dict):
        ordered_keys = [
            "category",
            "attribution",
            "severity",
            "confidence",
            "description",
            "suggested_action",
        ]
        parts = [f"{key}: {item[key]}" for key in ordered_keys if item.get(key) not in (None, "")]
        extra = [f"{key}: {value}" for key, value in item.items() if key not in ordered_keys and value not in (None, "")]
        return "；".join(parts + extra)
    return str(item).strip()


def normalize_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [formatted for item in value if (formatted := format_summary_item(item))]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    if isinstance(value, dict):
        formatted = format_summary_item(value)
        return [formatted] if formatted else []
    return []


def normalize_user_original_inputs(value: Any) -> list[dict[str, str]]:
    if not value:
        return []
    raw_items = value if isinstance(value, list) else [value]
    normalized: list[dict[str, str]] = []
    for item in raw_items:
        if isinstance(item, dict):
            content = str(
                item.get("content")
                or item.get("text")
                or item.get("value")
                or item.get("raw")
                or ""
            ).strip()
            if not content:
                continue
            source = str(item.get("source") or item.get("type") or item.get("kind") or "用户输入").strip()
            note = str(item.get("note") or item.get("path") or "").strip()
        else:
            content = str(item).strip()
            source = "用户输入"
            note = ""
        if len(content) > 1800:
            content = content[:1800].rstrip() + "\n...（已截断）"
        entry = {"source": source, "content": content}
        if note:
            entry["note"] = note
        normalized.append(entry)
    return normalized


def original_inputs_from_session(summary: SessionSummary) -> list[dict[str, str]]:
    inputs: list[dict[str, str]] = []
    for message in user_messages(summary):
        inputs.append({"source": "会话用户消息", "content": message})
    return normalize_user_original_inputs(inputs)


def user_original_inputs(agent_summary: dict[str, Any] | None, summary: SessionSummary) -> list[dict[str, str]]:
    if agent_summary:
        for key in ("user_original_inputs", "original_inputs", "raw_user_inputs"):
            if agent_summary.get(key):
                return normalize_user_original_inputs(agent_summary[key])
        raw_requirements = normalize_string_list(agent_summary.get("raw_requirements"))
        if raw_requirements:
            return normalize_user_original_inputs(
                [{"source": "原始需求描述摘要", "content": item} for item in raw_requirements]
            )
    return original_inputs_from_session(summary)


def render_user_original_inputs(items: list[dict[str, str]], max_items: int = 12) -> str:
    if not items:
        return "- 暂未从会话或 Agent summary 中提取到用户原始输入。"
    rendered: list[str] = []
    for index, item in enumerate(items[:max_items], start=1):
        source = item.get("source") or "用户输入"
        note = item.get("note") or ""
        title = f"{index}. 来源：{source}"
        if note:
            title += f"（{note}）"
        rendered.extend([title, "", "```text", item.get("content", ""), "```", ""])
    if len(items) > max_items:
        rendered.append(f"（另有 {len(items) - max_items} 条用户原始输入未展示）")
    return "\n".join(rendered).rstrip()


def load_agent_summary(args: argparse.Namespace) -> dict[str, Any] | None:
    raw = ""
    if args.agent_summary_file:
        raw = Path(args.agent_summary_file).expanduser().read_text(encoding="utf-8")
    elif args.agent_summary_json:
        raw = args.agent_summary_json
    elif args.agent_summary_stdin:
        raw = sys.stdin.read()
    if not raw.strip():
        return None
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise SystemExit("Agent summary must be a JSON object.")
    return data


def agent_reports(agent_summary: dict[str, Any] | None) -> list[dict[str, Any] | None]:
    if not agent_summary:
        return [None]
    reports = agent_summary.get("reports")
    if reports is None:
        reports = agent_summary.get("summaries")
    if reports is None:
        return [agent_summary]
    if not isinstance(reports, list) or not reports:
        raise SystemExit("Agent summary field 'reports' must be a non-empty list when provided.")
    normalized: list[dict[str, Any]] = []
    for index, report in enumerate(reports, start=1):
        if not isinstance(report, dict):
            raise SystemExit(f"Agent summary report #{index} must be a JSON object.")
        normalized.append(report)
    return normalized


def value_or_default(agent_summary: dict[str, Any] | None, key: str, default: Any) -> Any:
    if agent_summary and agent_summary.get(key):
        return agent_summary[key]
    return default


def render_markdown(
    summary: SessionSummary,
    user: str,
    dt: datetime,
    repo_url: str,
    agent_summary: dict[str, Any] | None = None,
) -> tuple[str, str]:
    title = str(value_or_default(agent_summary, "task_title", task_title(summary))).strip()
    theme = str(value_or_default(agent_summary, "task_theme", task_theme(summary))).strip()
    core_requirement = str(value_or_default(agent_summary, "core_requirement", "")).strip()
    raw_requirements = normalize_string_list(value_or_default(agent_summary, "raw_requirements", []))
    original_inputs = user_original_inputs(agent_summary, summary)
    compatibility_requirements = normalize_string_list(
        value_or_default(agent_summary, "requirements", extract_requirements(summary))
    )
    requirements: list[str] = []
    if core_requirement:
        requirements.append(f"核心需求描述：{core_requirement}")
    if not requirements:
        requirements = compatibility_requirements
    process = normalize_string_list(value_or_default(agent_summary, "execution_process", []))
    done = normalize_string_list(value_or_default(agent_summary, "completed_tasks", extract_done(summary)))
    result = normalize_string_list(value_or_default(agent_summary, "execution_result", []))
    improvements = normalize_string_list(value_or_default(agent_summary, "improvement_points", extract_improvements(summary)))
    diagnostics = normalize_string_list(value_or_default(agent_summary, "diagnostics", []))
    evidence_items = normalize_string_list(value_or_default(agent_summary, "evidence", evidence(summary)))
    date_text = dt.strftime("%Y-%m-%d-%H")
    session_ref = summary.session_id or summary.session_path.name

    content = f"""# {title}

## 元信息

- username: {user}
- datetime: {date_text}
- session: {session_ref}
- source_session: {display_path(summary.session_path)}
- target_repo: {repo_url}

## 任务主题

{theme}

## 用户原始输入

本模块保留用户需求文件内容、命令行输入或会话用户消息等原始输入的可追溯摘录，用于分析用户是否高效使用智能体完成任务。内容应脱敏并按长度截断，不记录 token、cookie、私钥、认证 header 或完整长日志。

{render_user_original_inputs(original_inputs, max_items=12)}

## 需求描述

{bulletize(requirements, max_items=20)}

## 用户输入逐条记录

{render_user_inputs(summary)}

## 任务执行过程

{bulletize(process, max_items=20)}

## 完成的任务

{bulletize(done, max_items=16)}

## 执行结果

{bulletize(result, max_items=12)}

## 需求描述中的待优化点

{bulletize(improvements, max_items=16)}

## 全方位诊断

{bulletize(diagnostics, max_items=20)}

## 会话证据摘要

{bulletize(evidence_items, max_items=20)}
"""
    return title, content


def ensure_repo(repo_url: str, repo_dir: Path) -> None:
    if repo_dir.exists():
        run(["git", "pull", "--ff-only"], cwd=repo_dir)
        return
    repo_dir.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "clone", repo_url, str(repo_dir)])


def commit_and_push(repo_dir: Path, relative_path: Path, title: str) -> str:
    run(["git", "add", str(relative_path)], cwd=repo_dir)
    diff = run(["git", "diff", "--cached", "--quiet"], cwd=repo_dir, check=False)
    if diff.returncode == 0:
        return "no changes to commit"
    run(["git", "commit", "-m", f"task2zxgc: {title}"], cwd=repo_dir)
    run(["git", "push"], cwd=repo_dir)
    return "pushed"


def commit_and_push_many(repo_dir: Path, relative_paths: list[Path], title: str) -> str:
    run(["git", "add", *[str(path) for path in relative_paths]], cwd=repo_dir)
    diff = run(["git", "diff", "--cached", "--quiet"], cwd=repo_dir, check=False)
    if diff.returncode == 0:
        return "no changes to commit"
    suffix = f" and {len(relative_paths) - 1} more" if len(relative_paths) > 1 else ""
    run(["git", "commit", "-m", f"task2zxgc: {title}{suffix}"], cwd=repo_dir)
    run(["git", "push"], cwd=repo_dir)
    return "pushed"


def report_relative_path(repo_dir: Path, user: str, title: str, dt: datetime, used: set[Path]) -> Path:
    base = Path(user) / f"{dt.strftime('%Y-%m-%d-%H')}-{sanitize_path_part(title, 'codex-session-summary')}.md"
    relative = base
    counter = 2
    while relative in used or (repo_dir / relative).exists():
        relative = base.with_name(f"{base.stem}-{counter}{base.suffix}")
        counter += 1
    used.add(relative)
    return relative


def write_report(content: str, repo_dir: Path, user: str, title: str, dt: datetime, used: set[Path] | None = None) -> Path:
    relative = report_relative_path(repo_dir, user, title, dt, used or set())
    target = repo_dir / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return relative


def request_posthook(args: argparse.Namespace) -> None:
    if not args.agent_summary_file:
        raise SystemExit("Posthook requests require --agent-summary-file so summarization stays Agent-based.")
    session_path = Path(args.session).expanduser() if args.session else latest_session()
    summary = parse_session(session_path)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    marker = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "session_path": str(session_path),
        "session_id": summary.session_id,
        "repo_url": args.repo_url,
        "repo_dir": str(Path(args.repo_dir).expanduser()),
    }
    if args.username:
        marker["username"] = args.username
    if args.agent_summary_file:
        marker["agent_summary_file"] = str(Path(args.agent_summary_file).expanduser())
    PENDING_FILE.write_text(json.dumps(marker, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"task2zxgc posthook request registered: {PENDING_FILE}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", help="Path to a Codex rollout JSONL session file.")
    parser.add_argument("--session-id", help="Codex session id substring to resolve under ~/.codex/sessions.")
    parser.add_argument("--repo-url", default=DEFAULT_REPO_URL)
    parser.add_argument("--repo-dir", default=str(DEFAULT_REPO_DIR))
    parser.add_argument("--username", help="Output namespace under the report repository. Defaults to TASK2ZXGC_USERNAME, git user.name, or OS user.")
    parser.add_argument("--ai-insights-repo", default=str(DEFAULT_AI_INSIGHTS_REPO), help="Path to ai-insights repo used as diagnostic reference.")
    parser.add_argument("--dry-run", action="store_true", help="Render the report to stdout without cloning, committing, or pushing.")
    parser.add_argument("--push", action="store_true", help="Clone/pull the target repo, write the report, commit, and push.")
    parser.add_argument("--request-posthook", action="store_true", help="Create a pending marker for the Stop posthook.")
    parser.add_argument("--dump-context", action="store_true", help="Print session context JSON for Agent-based summarization.")
    parser.add_argument("--agent-summary-file", help="Path to Agent-generated summary JSON.")
    parser.add_argument("--agent-summary-json", help="Agent-generated summary JSON string.")
    parser.add_argument("--agent-summary-stdin", action="store_true", help="Read Agent-generated summary JSON from stdin.")
    parser.add_argument("--allow-fallback-summary", action="store_true", help="Allow legacy script-generated summary when no Agent summary is provided.")
    args = parser.parse_args()

    if args.request_posthook:
        request_posthook(args)
        return 0

    if args.session:
        session_path = Path(args.session).expanduser()
    elif args.session_id:
        session_path = session_by_id(args.session_id)
    else:
        session_path = latest_session()

    summary = parse_session(session_path)
    if args.dump_context:
        print(json.dumps(session_context(summary, Path(args.ai_insights_repo).expanduser()), ensure_ascii=False, indent=2))
        return 0

    agent_summary = load_agent_summary(args)
    if args.push and not agent_summary and not args.allow_fallback_summary:
        raise SystemExit("Refusing to push without Agent-generated summary. Use --agent-summary-file/--agent-summary-json/--agent-summary-stdin.")
    user = sanitize_path_part(args.username, "unknown") if args.username else username()
    now = datetime.now()
    rendered_reports = [render_markdown(summary, user, now, args.repo_url, report) for report in agent_reports(agent_summary)]

    if args.dry_run or not args.push:
        for index, (_title, content) in enumerate(rendered_reports, start=1):
            if len(rendered_reports) > 1:
                print(f"<!-- task2zxgc report {index}/{len(rendered_reports)} -->")
            print(content)
        return 0

    repo_dir = Path(args.repo_dir).expanduser()
    ensure_repo(args.repo_url, repo_dir)
    used_paths: set[Path] = set()
    relative_paths: list[Path] = []
    for title, content in rendered_reports:
        relative_paths.append(write_report(content, repo_dir, user, title, now, used_paths))
    status = commit_and_push_many(repo_dir, relative_paths, rendered_reports[0][0])
    for relative_path in relative_paths:
        print(f"task2zxgc {status}: {repo_dir / relative_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        if exc.stdout:
            sys.stderr.write(exc.stdout)
        if exc.stderr:
            sys.stderr.write(exc.stderr)
        raise SystemExit(exc.returncode)
