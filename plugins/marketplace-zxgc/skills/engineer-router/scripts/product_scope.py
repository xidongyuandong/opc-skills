"""Portable workflow identity checks; not an OS sandbox or authorization layer."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


def _identity(product_line: str, workspace: str) -> dict:
    digest = hashlib.sha256(json.dumps([product_line, workspace]).encode()).hexdigest()[:24]
    return {
        "state_namespace": f"{product_line}/{digest}",
        "archive_root": str(Path(workspace) / ".agent-state" / product_line / digest),
    }


def _project(value: str) -> None:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", value):
        raise ValueError("product_line must be a project identifier (letters, digits, _, . or -)")


def resolve_context(text: str, *, product_line: str = "shared", workspace: str | None = None) -> dict:
    """Bind an explicit project ID to an existing workspace, without inferring ownership."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("task text is required")
    _project(product_line)
    if not isinstance(workspace, str) or not workspace.strip():
        raise ValueError("explicit workspace is required")
    path = Path(workspace).expanduser().resolve()
    if not path.is_dir():
        raise ValueError("workspace must be an existing directory")
    context = {
        "schema_version": 1,
        "product_line": product_line,
        "source": "explicit",
        "workspace": str(path),
        "status": "resolved",
        "conflicts": [],
        "allowed_scopes": [product_line],
        **_identity(product_line, str(path)),
    }
    validate_context(context, require_workspace=True)
    return context


def validate_context(context: dict, *, require_workspace: bool = False) -> None:
    """All public contexts are workspace-bound, including when the flag is omitted."""
    if not isinstance(context, dict):
        raise ValueError("product_context must be an object")
    _project(context.get("product_line"))
    if type(context.get("schema_version")) is not int or context["schema_version"] != 1:
        raise ValueError("unsupported or missing context schema_version")
    if context.get("status") != "resolved" or context.get("conflicts") != []:
        raise ValueError("product_context is unresolved or conflicting")
    workspace = context.get("workspace")
    if not isinstance(workspace, str) or not Path(workspace).is_absolute():
        raise ValueError("explicit absolute workspace is required")
    path = Path(workspace)
    if str(path.resolve()) != workspace or not path.is_dir():
        raise ValueError("workspace must be an existing canonical absolute directory")
    if context.get("allowed_scopes") != [context["product_line"]]:
        raise ValueError("allowed_scopes must match the bound project")
    for key, expected in _identity(context["product_line"], workspace).items():
        if context.get(key) != expected:
            raise ValueError(f"{key} missing or inconsistent with identity")
    if not Path(context["archive_root"]).resolve().is_relative_to(path):
        raise ValueError("archive_root escapes workspace")


def validate_recovery(context: dict, record: dict, active_module_key: str) -> None:
    validate_context(context, require_workspace=True)
    if not isinstance(record, dict) or not isinstance(active_module_key, str) or not active_module_key.strip():
        raise ValueError("recovery requires a record and active_module_key")
    bound = record.get("product_context", record)
    validate_context(bound, require_workspace=True)
    for key in ("product_line", "workspace", "state_namespace"):
        if bound[key] != context[key]:
            raise ValueError(f"recovery {key} mismatch")
    if record.get("active_module_key") != active_module_key:
        raise ValueError("recovery active_module_key mismatch or missing")


def validate_execution_paths(context: dict, paths: list[str]) -> None:
    validate_context(context, require_workspace=True)
    if not isinstance(paths, list):
        raise ValueError("execution paths must be a list")
    workspace = Path(context["workspace"])
    for value in paths:
        if not isinstance(value, str) or not value or not Path(value).is_absolute():
            raise ValueError("execution paths must be absolute file paths")
        path = Path(value).resolve()
        if not path.is_relative_to(workspace):
            raise ValueError("execution path escapes bound workspace: " + value)
        if path.is_dir() or (path.exists() and not path.is_file()):
            raise ValueError("execution path must reference a file: " + value)
        if not path.parent.is_dir():
            raise ValueError("execution file parent must exist: " + value)


def load_context(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("context document must be an object")
    context = data.get("product_context", data)
    validate_context(context, require_workspace=True)
    return context
