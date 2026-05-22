#!/usr/bin/env python3
"""
Codex learning hook dispatcher.

Captures Codex lifecycle events into a local learning store, mirrors useful
observations into continuous-learning-v2's homunculus format, and creates
reviewable candidates for evals and memories. It intentionally does not edit
skills automatically.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
LEARNING_DIR = CODEX_HOME / "learning"
EVENTS_FILE = LEARNING_DIR / "events.jsonl"
CANDIDATES_FILE = LEARNING_DIR / "candidates.jsonl"
APPROVED_MEMORY_FILE = LEARNING_DIR / "approved-memories.jsonl"
MAX_FIELD_CHARS = 5000

SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|token|secret|password|authorization|credentials?|auth)"
    r"([\"'\s:=]+)"
    r"([A-Za-z]+\s+)?"
    r"([A-Za-z0-9_\-/.+=]{8,})"
)

SECRET_KEY_RE = re.compile(r"(?i)(api[_-]?key|token|secret|password|authorization|credentials?|auth)")
ERROR_RE = re.compile(
    r"(?i)(error|failed|failure|exception|traceback|panic|permission denied|operation not permitted|"
    r"could not resolve host|network error|connection closed|exit code [1-9])"
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def scrub_text(value: str) -> str:
    return SECRET_RE.sub(lambda m: f"{m.group(1)}{m.group(2)}{m.group(3) or ''}[REDACTED]", value)


def scrub(value: Any, depth: int = 0) -> Any:
    if depth > 8:
        return "[MAX_DEPTH]"
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if SECRET_KEY_RE.search(str(key)):
                out[str(key)] = "[REDACTED]"
            else:
                out[str(key)] = scrub(item, depth + 1)
        return out
    if isinstance(value, list):
        return [scrub(item, depth + 1) for item in value[:200]]
    if isinstance(value, str):
        cleaned = scrub_text(value)
        return cleaned[:MAX_FIELD_CHARS]
    return value


def atomic_append_jsonl(path: Path, obj: dict[str, Any]) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")
        return True
    except Exception:
        return False


def atomic_write_json(path: Path, obj: Any) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent), text=True)
    except Exception:
        return False
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp, path)
        return True
    except Exception:
        return False
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def run_git(cwd: Path, args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            text=True,
            capture_output=True,
            timeout=3,
        )
    except Exception:
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def normalize_remote(url: str) -> str:
    if not url:
        return ""
    is_network = (
        not url.startswith("file://")
        and ("://" in url or re.match(r"^[^@/:]+@[^:/]+:", url) is not None)
    )
    url = re.sub(r"://[^@]+@", "://", url)
    url = re.sub(r"^[A-Za-z][A-Za-z0-9+.-]*://", "", url)
    url = re.sub(r"^[^@/:]+@([^:/]+):", r"\1/", url)
    url = re.sub(r"\.git/?$", "", url)
    url = re.sub(r"/+$", "", url)
    return url.lower() if is_network else url


def project_context(cwd_str: str | None) -> dict[str, str]:
    cwd = Path(cwd_str or os.getcwd()).expanduser()
    if not cwd.exists():
        cwd = Path.home()
    root = run_git(cwd, ["rev-parse", "--show-toplevel"]) or str(cwd)
    root_path = Path(root)
    remote = normalize_remote(run_git(root_path, ["remote", "get-url", "origin"]))
    hash_input = remote or str(root_path)
    project_id = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:12]
    return {
        "id": project_id,
        "name": root_path.name or "global",
        "root": str(root_path),
        "remote": remote,
    }


def homunculus_root() -> Path:
    override = os.environ.get("CLV2_HOMUNCULUS_DIR")
    if override and Path(override).is_absolute():
        return Path(override)
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg and Path(xdg).is_absolute():
        return Path(xdg) / "ecc-homunculus"
    return Path.home() / ".local" / "share" / "ecc-homunculus"


def ensure_homunculus_project(project: dict[str, str]) -> Path:
    root = homunculus_root()
    project_dir = root / "projects" / project["id"]
    for rel in (
        "instincts/personal",
        "instincts/inherited",
        "observations.archive",
        "evolved/skills",
        "evolved/commands",
        "evolved/agents",
    ):
        (project_dir / rel).mkdir(parents=True, exist_ok=True)

    project_meta = {
        "id": project["id"],
        "name": project["name"],
        "root": project["root"],
        "remote": project["remote"],
        "last_seen": now_iso(),
    }
    atomic_write_json(project_dir / "project.json", project_meta)

    registry_file = root / "projects.json"
    try:
        registry = json.loads(registry_file.read_text(encoding="utf-8"))
    except Exception:
        registry = {}
    previous = registry.get(project["id"], {})
    registry[project["id"]] = {**previous, **project_meta}
    atomic_write_json(registry_file, registry)
    return project_dir


def compact(value: Any) -> str:
    try:
        if isinstance(value, str):
            return value[:MAX_FIELD_CHARS]
        return json.dumps(value, ensure_ascii=False, sort_keys=True)[:MAX_FIELD_CHARS]
    except Exception:
        return str(value)[:MAX_FIELD_CHARS]


def clv2_event_name(event_name: str) -> str:
    return {
        "SessionStart": "session_start",
        "UserPromptSubmit": "prompt",
        "PreToolUse": "tool_start",
        "PermissionRequest": "permission_request",
        "PostToolUse": "tool_complete",
        "Stop": "turn_stop",
    }.get(event_name, event_name)


def write_observation(payload: dict[str, Any], project: dict[str, str]) -> None:
    event_name = str(payload.get("hook_event_name") or payload.get("event") or "unknown")
    observation: dict[str, Any] = {
        "timestamp": now_iso(),
        "event": clv2_event_name(event_name),
        "session": payload.get("session_id", "unknown"),
        "project_id": project["id"],
        "project_name": project["name"],
        "cwd": payload.get("cwd", ""),
        "turn_id": payload.get("turn_id", ""),
    }

    if event_name in {"PreToolUse", "PermissionRequest", "PostToolUse"}:
        observation["tool"] = payload.get("tool_name", "unknown")
        observation["input"] = compact(scrub(payload.get("tool_input")))
    if event_name == "PostToolUse":
        observation["output"] = compact(scrub(payload.get("tool_response")))
    if event_name == "UserPromptSubmit":
        observation["prompt"] = compact(scrub(payload.get("prompt", "")))
    if event_name == "Stop":
        observation["last_assistant_message"] = compact(scrub(payload.get("last_assistant_message", "")))
    if event_name == "SessionStart":
        observation["source"] = payload.get("source", "")

    project_dir = ensure_homunculus_project(project)
    atomic_append_jsonl(project_dir / "observations.jsonl", observation)


def candidate_id(project: dict[str, str], kind: str, text: str) -> str:
    raw = f"{project['id']}:{kind}:{text[:400]}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def add_candidate(project: dict[str, str], payload: dict[str, Any], kind: str, reason: str, evidence: str) -> None:
    event_name = payload.get("hook_event_name", "unknown")
    entry = {
        "id": candidate_id(project, kind, evidence),
        "timestamp": now_iso(),
        "status": "pending",
        "kind": kind,
        "project_id": project["id"],
        "project_name": project["name"],
        "project_root": project["root"],
        "event": event_name,
        "turn_id": payload.get("turn_id", ""),
        "session_id": payload.get("session_id", ""),
        "reason": reason,
        "evidence": scrub_text(evidence[:2000]),
        "suggested_eval": {
            "id": f"{kind}-{candidate_id(project, kind, evidence)}",
            "prompt": "Reproduce the observed issue or correction from evidence.",
            "expected_outcome": "The agent avoids the failure and verifies the result.",
            "grader": "manual_or_code_based",
            "success_threshold": "No repeated failure; concrete verification present.",
            "tags": [kind, "codex-learning", project["name"]],
        },
    }
    atomic_append_jsonl(CANDIDATES_FILE, entry)


def maybe_generate_candidates(payload: dict[str, Any], project: dict[str, str]) -> None:
    event_name = str(payload.get("hook_event_name", ""))
    if event_name == "PostToolUse":
        response = compact(scrub(payload.get("tool_response")))
        if ERROR_RE.search(response):
            add_candidate(project, payload, "failure-regression", "Tool output contains a likely failure.", response)
    elif event_name == "PermissionRequest":
        add_candidate(
            project,
            payload,
            "approval-pattern",
            "A permission request may reveal a reusable approval/safety rule.",
            compact(scrub(payload.get("tool_input"))),
        )
    elif event_name == "UserPromptSubmit":
        prompt = str(payload.get("prompt", ""))
        if re.search(r"(?i)(记住|记忆|learn|remember|以后|下次|不要再|规则|经验|教训|沉淀)", prompt):
            add_candidate(project, payload, "user-correction", "User prompt appears to contain reusable learning.", prompt)
    elif event_name == "Stop":
        msg = str(payload.get("last_assistant_message") or "")
        if ERROR_RE.search(msg):
            add_candidate(project, payload, "assistant-failure", "Assistant final message reports unresolved failure.", msg)


def session_context(project: dict[str, str]) -> str:
    lines: list[str] = []
    try:
        memories = APPROVED_MEMORY_FILE.read_text(encoding="utf-8").splitlines()[-8:]
    except Exception:
        memories = []
    for line in memories:
        try:
            item = json.loads(line)
        except Exception:
            continue
        if item.get("project_id") in {project["id"], "global"}:
            title = item.get("title") or item.get("id")
            content = str(item.get("content", ""))[:300]
            lines.append(f"- {title}: {content}")
    if not lines:
        return ""
    return "Approved local learning memories for this workspace:\n" + "\n".join(lines)


def handle_hook(payload: dict[str, Any]) -> dict[str, Any] | None:
    payload = scrub(payload)
    project = project_context(str(payload.get("cwd") or os.getcwd()))
    event_record = {
        "timestamp": now_iso(),
        "project": project,
        "payload": payload,
    }
    atomic_append_jsonl(EVENTS_FILE, event_record)
    write_observation(payload, project)
    maybe_generate_candidates(payload, project)

    event_name = str(payload.get("hook_event_name", ""))
    if event_name == "SessionStart":
        context = session_context(project)
        if context:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": context,
                }
            }
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", default="")
    args = parser.parse_args()

    try:
        payload = json.load(sys.stdin)
    except Exception as exc:
        atomic_append_jsonl(EVENTS_FILE, {"timestamp": now_iso(), "error": f"invalid-json: {exc}"})
        return 0

    if args.event and "hook_event_name" not in payload:
        payload["hook_event_name"] = args.event

    try:
        response = handle_hook(payload)
    except Exception as exc:
        atomic_append_jsonl(EVENTS_FILE, {"timestamp": now_iso(), "error": f"hook-failed: {exc}"})
        return 0

    if response:
        print(json.dumps(response, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
