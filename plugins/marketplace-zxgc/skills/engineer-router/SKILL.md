---
name: engineer-router
description: Bind a task to an explicit project workspace and suggest a generic engineering role before contract compilation or workflow recovery.
---

# Portable engineer router

Use this skill when a task needs a project-scoped handoff to `code-exec` or
`multi-agent-orchestrator`. Produce `product_context` independently from
`primary_role`: the project/workspace identity constrains recovery and file
references; the role is only an advisory label. No role installation is implied.

## Workflow

1. Identify the intended existing workspace and an explicit project identifier.
   Identifiers accept letters, digits, `_`, `.` and `-` (maximum 128 characters).
   The default identifier is `shared`; it grants no access outside the workspace.
2. Run the router from this skill directory, substituting your workspace:

   ```bash
   python3 scripts/route_engineer_task.py --task "Review the dataset importer" \
     --product-line sample-project --workspace /absolute/project > route.json
   ```

3. Inspect the result. Pass the complete `product_context` into contracts and
   workflows. Keep a separately obtained expected context for recovery; never
   accept the record being recovered as its own source of expected identity.
4. Supply the expected module key separately when validating recovery. A missing
   context, changed project/workspace identity or different module blocks recovery.
5. Validate explicit absolute file paths before handing off work. Files must stay
   inside the canonical workspace after symlink resolution. Existing directories,
   special files, relative paths and missing parent directories are rejected.

## Public scope and limits

This is a reduced, standalone public router. It has no private project registry,
business-specific role routing, history ingestion, global asset discovery or
automatic installation. Project names and role suggestions do not imply ownership
verification. Callers explicitly bind identity; text keywords only suggest a role.

The scripts do not spawn agents, call model APIs, choose models, execute shell
commands, create archives, or grant permissions. They emit JSON to stdout. Any
output redirection is an explicit caller action. Model availability and execution
authorization remain the caller's responsibility.

Checks are workflow validation, not an operating-system sandbox. They cannot
prevent later filesystem changes, hard-link aliases, arbitrary executed code or
time-of-check/time-of-use races. Revalidate before execution and use an actual
sandbox for untrusted workloads. Separate projects sharing a workspace still
share its filesystem; use separate workspaces for filesystem isolation.

## Python compatibility surface

`scripts/product_scope.py` exposes `resolve_context`, `validate_context`,
`validate_recovery`, `validate_execution_paths` and `load_context`. All public
contexts require an existing canonical workspace, even if `require_workspace`
is omitted. `load_context` accepts a direct context or a JSON object containing
`product_context`.

Run the focused checks with:

```bash
python3 -m unittest discover -s tests -v
```
