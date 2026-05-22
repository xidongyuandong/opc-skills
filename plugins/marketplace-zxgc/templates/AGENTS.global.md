# Global Agent Constraints

## Scope

- Keep this file for cross-project, user-level behavior only. Put repository commands, architecture rules, and language-specific details in the nearest repository or subdirectory `AGENTS.md`.
- Current user instructions override this file. More specific repository or subdirectory `AGENTS.md` files override broader guidance for their scope.
- Treat `~/.codex/config.toml`, `~/.codex/hooks.json`, MCP servers, plugins, skills, memory, and symlinked rules as additional user-level context entrances. Do not duplicate their detailed workflows here; route to them when relevant.

## Core Behavior

- If the user only names a skill, use or explain that skill for the current explicit task only. Do not infer unrelated side-effecting work from the skill name alone.
- Before editing code or durable docs, inspect the target file, nearby callers or related docs, and any relevant project summaries. Prefer `rg`/`rg --files` for local discovery.
- Make surgical changes: edit only what the current request requires. Mention unrelated issues instead of fixing them.
- Never revert, overwrite, or delete user changes unless explicitly requested.
- Surface conflicts between user requests, AGENTS files, skills, hooks, MCP/tool behavior, and repository conventions instead of blending incompatible rules.
- Treat labels such as `【人工】`, manual-only, fallback, optional, required, and destructive as controlled workflow terms. Before adding or preserving them, verify whether the step can instead be automated through an existing script, flag, environment variable, dry-run/apply flow, MCP, hook, or GitLab/API workflow.
- When the user asks for automatic or robust execution, do not leave parameterizable steps as manual instructions. Convert branch names, modes, toggles, MR/issue identifiers, and smoke-test behavior into explicit parameters or scripts, then document the automated path.

## Complex Task Method

- For complex tasks, configuration governance, cross-entry analysis, architecture mapping, or long-lived rule changes, investigate the real local context before deciding. Do not apply templates before reading the relevant files and tool configuration.
- Identify the main blocker or dominant contradiction for the current phase, then organize the plan and TODO list around resolving it.
- Treat each patch, verification result, and user feedback as practice evidence. Use it to revise the requirement, plan, TODO, analysis, and patch when needed.
- Keep this method lightweight: simple tasks should still use the shortest effective path.
- Do not paste theory into task output or AGENTS. Use concrete evidence, commands, file paths, and verification results.

## Local Workflow

- When working from a requirement file named `{需求文件}.md`, write `{需求文件}.plan.md` and `{需求文件}.task.md` next to it by default, unless the user explicitly requests only a specific output file or forbids extra files.
- In Git/code repositories, check `docs/总结/*.md` as optional context before substantive code changes or repository-wide analysis. Read only summaries relevant to the task, touched modules, feature names, or error keywords.
- Persist new repository understanding under `<repo-root>/docs/总结/` only when the task explicitly concerns a code/product repository and produces durable repository-wide architecture, module, dependency, build/test, or workflow knowledge.
- Do not create `docs/总结` for incidental repos, config/cache/tool folders, or one-off task logs unless the user asks. Never store secrets, raw command dumps, transient logs, or unrelated implementation notes there.

## Python / uv

- In Li Auto / lixiang Python repositories, prefer `uv` for Python versions, dependencies, virtualenvs, tests, and scripts when the task touches Python execution, dependency management, Docker/CI, or packaging.
- Before changing Python dependencies or running dependency commands, inspect the nearest `pyproject.toml`, `uv.lock`, and relevant `docs/总结/*uv*.md` or dependency summary.
- Treat per-subproject `pyproject.toml + uv.lock` as normal unless a top-level uv workspace is explicit. Run `uv sync`, `uv run pytest`, and `uv run <script>` from the target subproject so `[tool.uv.sources]` relative paths resolve correctly.
- Prefer company Artifactory-backed indexes and Python download mirrors for internal packages. In containers with a suitable Python already installed, avoid runtime Python downloads with `UV_PYTHON_DOWNLOADS=never`, `UV_PYTHON`, and `--python` when appropriate.

## Verification And Reporting

- Choose the narrowest useful verification first; broaden when shared behavior, public APIs, generated files, or user-facing flows are affected.
- For documentation that encodes workflows, verify not only syntax but also instruction compliance: search for stale manual markers, hard-coded branch names, local absolute paths, and outdated fallback wording that contradict the current user intent.
- If verification cannot run, report the exact command attempted, the failure reason, and remaining risk.
- If blocked by `Operation not permitted` on a user-owned path, distinguish sandbox limits from real file permissions. If normal Terminal/manual action is needed, provide exact commands, then re-check after the user runs them.
- Redact tokens, passwords, private keys, cookies, and internal credentials in all outputs.
