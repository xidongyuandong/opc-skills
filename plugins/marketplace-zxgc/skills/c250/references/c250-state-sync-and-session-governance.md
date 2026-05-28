# C250 State Sync And Session Governance

## Core Claim

c250 Codex work must treat the local machine as the source of truth for reusable configuration and wrapper changes, then sync to `/data/jenkins/.codex/home` and verify the remote result; already-running remote Codex sessions may keep stale instruction context until restarted.

## Reader Task

Use this note to understand, solve, and verify cases where c250 did not follow updated user-level rules, a remote session still behaves like an older configuration, or a named `c250-codex` session fails before Codex starts.

## Source Of Truth

- User-level rules source: `~/AGENTS.md`.
- Remote user-level rules target: `/data/jenkins/.codex/home/AGENTS.md`.
- Local c250 wrappers: `~/.local/bin/c250-*`.
- Local c250 skill: `~/.codex/skills/c250`.
- Remote Codex home: `/data/jenkins/.codex/home`.

Make durable edits locally first. Then sync or copy to c250 and verify checksums, grep results, or a smoke session. Remote-only hotfixes are acceptable only for diagnosis; backport them locally before closing the task.

## AGENTS.md Propagation

`c250-sync-codex --agents` copies the local user-level `AGENTS.md` to remote Codex home. `c250-codex true <session>` runs the safe sync path before opening a persistent session.

Verification:

```bash
shasum -a 256 ~/AGENTS.md
c250-exec 'sha256sum /data/jenkins/.codex/home/AGENTS.md'
c250-exec 'grep -n "three-role\|separate responsibilities\|durable result writing" /data/jenkins/.codex/home/AGENTS.md'
```

If the hashes match but behavior still follows old rules, check whether the task is running inside an already-started `c250-session` tmux Codex process. Existing sessions can keep instruction context from process start. Restart with `--force` or use a new session name.

```bash
c250-codex true qwen3.6-eval-2 --force
```

## Requirement File Workflow Check

Current user-level requirement-file rules distinguish three roles:

- `{需求文件}.md`: requirement entry and final user-facing requirement answer.
- `{需求文件}.plan.md`: requirement clarification, implementation plan, TODO modules, and human confirmation gate.
- `{需求文件}.task.md`: post-execution acceptance record, verification, completed-vs-uncompleted TODO status, and residual risks.

Do not create `{需求文件}.task.md` or write durable result content before the plan is confirmed by the human. Do not create `{需求文件}.requirment.md` by default; merge an existing one into `{需求文件}.plan.md` if present.

## Session Name Normalization

The local wrappers accept letters, numbers, `_`, `-`, and `.` in user-facing session names. Remote tmux session names should not contain `.` because tmux target parsing can reject names such as `c250-qwen3.6-eval-2` with `bad session name`. `c250-session` normalizes dots to hyphens:

```text
qwen3.6-eval-2 -> c250-qwen3-6-eval-2
```

When checking, tailing, or stopping a session, use the original user-facing name with `c250-session`; the wrapper will normalize consistently.

## Permission And Config Checks

Safe remote Codex home permissions:

```text
/data/jenkins/.codex           755
/data/jenkins/.codex/home      755
config.toml                    644
AGENTS.md                      644
auth.json                      600
```

If a remote TUI reports `failed to reload config: Permission denied`, verify directory traversal and `config.toml` readability before changing auth permissions:

```bash
c250-exec 'stat -c "%U:%G %a %n" /data/jenkins/.codex /data/jenkins/.codex/home /data/jenkins/.codex/home/config.toml /data/jenkins/.codex/home/AGENTS.md'
```

## Checklist

1. Edit local source first: wrapper, skill, `AGENTS.md`, plugin source, or reusable script.
2. Validate locally: `bash -n`, `quick_validate.py`, or focused grep/checksum.
3. Sync narrowly: `c250-sync-codex --agents`, `--skills c250`, or the specific safe copy path.
4. Verify remotely with checksum, grep, permissions, or a smoke session.
5. Restart existing c250 Codex sessions when testing changed user-level rules.
6. Record whether the issue was stale remote state, stale running session context, local source drift, or repository-level `AGENTS.md` override.

## Boundary And Risks

- Do not sync local MCP settings to c250 by default; local paths, tokens, and network assumptions often do not hold in the container.
- Do not print or store `auth.json`, tokens, credentials, or private hook trust details.
- Do not assume a matching remote `AGENTS.md` guarantees a running session has reloaded it.
- Repository-level `AGENTS.md` files can override broader user-level guidance inside their scope.

## Not Persisted

- Raw remote Codex transcripts, full shell output, and one-off task prompts are not part of this reference.
- Machine-specific hook trust hashes and session-local Codex UI state are runtime state, not reusable c250 guidance.
- Repository-specific implementation details belong in that repository's `AGENTS.md` or `docs/总结`, not in this c250 skill reference.
