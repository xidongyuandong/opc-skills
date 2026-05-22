#!/usr/bin/env python3
"""Codex Stop posthook for task2zxgc.

The hook is idle unless ~/.codex/task2zxgc/pending.json exists.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


HOME = Path.home()
CODEX_HOME = Path.home() / ".codex"
PLUGIN_ROOT = Path(__file__).resolve().parents[1]
PENDING_FILE = CODEX_HOME / "task2zxgc" / "pending.json"
PLUGIN_SCRIPT = PLUGIN_ROOT / "skills" / "task2zxgc" / "scripts" / "task2zxgc.py"
INSTALLED_SCRIPT = CODEX_HOME / "skills" / "task2zxgc" / "scripts" / "task2zxgc.py"


def resolve_task2zxgc_script() -> Path:
    if PLUGIN_SCRIPT.exists():
        return PLUGIN_SCRIPT
    return INSTALLED_SCRIPT


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", default="Stop")
    parser.parse_args()

    if not PENDING_FILE.exists():
        return 0

    try:
        pending = json.loads(PENDING_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"Invalid task2zxgc pending marker: {exc}\n")
        return 1

    script = resolve_task2zxgc_script()
    cmd = ["python3", str(script), "--push"]
    session_path = pending.get("session_path")
    session_id = pending.get("session_id")
    repo_url = pending.get("repo_url")
    repo_dir = pending.get("repo_dir")
    agent_summary_file = pending.get("agent_summary_file")
    if session_path:
        cmd.extend(["--session", str(session_path)])
    elif session_id:
        cmd.extend(["--session-id", str(session_id)])
    if repo_url:
        cmd.extend(["--repo-url", str(repo_url)])
    if repo_dir:
        cmd.extend(["--repo-dir", str(repo_dir)])
    if agent_summary_file:
        cmd.extend(["--agent-summary-file", str(agent_summary_file)])

    result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    if result.returncode == 0:
        PENDING_FILE.unlink(missing_ok=True)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
