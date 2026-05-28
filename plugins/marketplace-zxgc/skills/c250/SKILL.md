---
name: c250
description: Operate container250 through local c250 wrappers. Use when the user says c250, container250, c250-codex, c250-exec, c250 sync, or asks to run/analyze tasks in /home/chehejia/cov-evalution on c250.
---

# C250 Remote Workflow

Use the local wrappers as the supported entry points:

- `c250:codex`: convenience entry for persistent remote Codex work; starts, sends to, or attaches to a named `c250-session`.
- `c250-session`: persistent multi-turn remote Codex session manager backed by remote `tmux`.
- `c250-codex`: user-facing resilient Codex entry; by default it routes to persistent `c250-session`/remote `tmux`, with `--direct` available for the old direct Docker TTY behavior.
- `c250-exec`: run a single remote shell command inside container250.
- `c250-sync-codex`: sync the minimum required Codex state to the remote container.

Default values:

```text
Docker Host: tcp://10.134.43.250:2376
Container: 0fd6ab612053
Remote CODEX_HOME: /data/jenkins/.codex/home
Remote Codex wrapper: /data/jenkins/.codex/bin/codex
Default workdir: /data/jenkins
Common eval repo: /home/chehejia/cov-evalution
```

For sustained multi-turn work, prefer a named persistent session:

```bash
c250:codex eval052001 -C /home/chehejia/cov-evalution "initial task"
c250:codex eval052001 "follow-up message"
c250:codex eval052001

c250-session start eval052001 -C /home/chehejia/cov-evalution "initial task"
c250-session send eval052001 "follow-up message"
c250-session tail eval052001 -n 160
c250-session attach eval052001
```

`c250-session` stores interaction state in the remote Codex process inside the remote `tmux` session. `c250:codex` is only a routing convenience over that stateful session layer. `c250-codex` now uses that persistent path by default, so a local Docker TCP reset does not kill the remote Codex process; reconnect with the same session name. Use `c250-codex --direct` only when the human explicitly wants a one-off direct Docker TTY.

Session names accepted by the local wrappers may contain letters, numbers, `_`, `-`, and `.`. Because tmux treats `.` specially in target names, `c250-session` normalizes dots to hyphens for the remote tmux session; for example, `qwen3.6-eval-2` maps to remote session `c250-qwen3-6-eval-2`.

`c250-codex` also auto-syncs local Codex state before opening a persistent session:

- `c250-sync-codex --all-safe` for auth, user-level `AGENTS.md`, plus `config.toml` with all `[mcp_servers.*]` sections removed.
- `c250-sync-codex --skills ...` for common c250, query-history, and algorithm skills.

MCP settings are intentionally excluded from the default remote sync because local MCP paths, tokens, and network assumptions usually do not hold inside container250. Existing remote hook trust state is preserved by default. Use `c250-codex true|false <session>` or `c250-codex --sync true|false <session>` as the explicit whole-sync switch: `true` runs the full auto-sync flow, `false` skips auth/config/skills sync. Use `c250-codex --local-hook-trust true|false <session>` to control whether local `hooks.state` entries are included in the filtered config; default is `false`. Use `c250-sync-codex --config` only for an explicit full config copy when the remote container can start the same MCP servers and use the same hook paths; use `c250-sync-codex --config-no-mcp --local-hook-trust true|false` for config-only sync without MCP. `c250-codex --no-sync <session>` is kept as an alias for `--sync false`. Use `c250-codex --sync-strict <session>` when stale remote state should fail the session startup instead of warning and continuing. Override the skill list with `C250_CODEX_AUTO_SYNC_SKILLS=skill1,skill2`; disable by setting `C250_CODEX_AUTO_SYNC=0`.

Use `c250-sync-codex --agents` to refresh only the remote user-level `AGENTS.md`. The default source is `~/AGENTS.md`; override it with `C250_AGENTS_FILE=/path/to/AGENTS.md` when testing a candidate rule file.

After syncing `AGENTS.md`, restart or start a new remote Codex session before relying on the new rules. Existing `c250-session` / tmux Codex processes may keep the instruction context loaded at session start, so use `c250-codex true <session> --force` or a new session name when validating updated user-level constraints.

Remote `CODEX_HOME` permission policy: keep `/data/jenkins/.codex` and `/data/jenkins/.codex/home` traversable (`755`) and keep `config.toml` world-readable (`644`) so TUI/app-server skill refreshes and other container users can read non-secret config. Keep `auth.json` and token-bearing state private (`600`). Do not "fix" `skills/list failed ... config.toml: Permission denied` by broadening `auth.json`; fix directory traversal and `config.toml` readability, then smoke test with `CODEX_HOME=/data/jenkins/.codex/home /data/jenkins/.codex/bin/codex debug prompt-input ping`.

If the permission failure appears during `c250-sync-codex`, treat it as a possible config replacement race: `docker cp` can briefly leave `config.toml` with restrictive temporary-file permissions before the final chmod. The sync wrapper should install config and AGENTS through a remote temp file, set owner/mode first, then atomically `mv` into place. After changing the wrapper, verify `config.toml` is `644`, `auth.json` is `600`, and `CODEX_HOME=/data/jenkins/.codex/home /data/jenkins/.codex/bin/codex debug prompt-input "skills refresh smoke"` reports available skills.

For true multi-user c250 use, prefer per-user `CODEX_HOME` values for auth, logs, sqlite state, sessions, and caches. Sharing `/data/jenkins/.codex/home` is acceptable for common config and skills only; it is not a stable multi-user runtime home because writable files such as history, state databases, sessions, and caches remain user-owned and can conflict.

When the prompt starts with `/plan `, use `c250:codex`; it sends `/plan` first, waits for Codex to enter Plan mode, then sends the remaining task text. This avoids composer text being concatenated across turns.

For remote document-generation or repository-analysis tasks, monitor both the remote Codex transcript and the expected artifact. Use `c250-session tail <name>` to confirm progress, then independently verify the target file with `c250-exec` (`test -f`, `wc -l`, and keyword checks). If the remote Codex session stalls in reasoning or editor/TUI state and no artifact is written, stop waiting and finish the narrow artifact with `c250-exec`, using only the already verified code/file evidence.

For complex remote scripts, do not inline large Python/awk/JSON/regex programs inside `c250-exec '...'`. Read `references/remote-script-execution.md` and prefer bundled skill scripts synced with `c250-sync-codex --skills ...`.

For c250 state synchronization, user-level rule propagation, and persistent-session behavior, read `references/c250-state-sync-and-session-governance.md`.

## Operational Lessons

For any c250-related change, update the local source of truth first, then push or sync it to c250 and verify the remote result. This applies to wrappers, skills, user-level rules, plugin or marketplace source, hook code, and reusable scripts. Avoid remote-only hotfixes except for emergency diagnosis; if a remote-only patch is unavoidable, immediately backport the same change locally, sync it to c250, and verify both sides.

If `c250:codex` or `c250-session` is blocked by a Codex hook error, fix the remote Codex environment first. Hook commands in the remote `CODEX_HOME` must use paths that exist inside container250; macOS host paths such as `/Users/...` are invalid there. Inspect the remote hook config and plugin cache, update only the broken command paths, then smoke test `c250:codex` before bypassing the session layer.

For plugin-packaged hooks on c250, keep the plugin manifest hook file safe to load directly. If a plugin uses `hooks.json.template` with placeholders such as `{{PLUGIN_ROOT}}`, the packaged `hooks.json` must not contain those placeholders; make it an empty hook manifest or a fully rendered remote-safe manifest, then install the real hooks into `CODEX_HOME/hooks.json` with the plugin install script. After fixing hook paths, check both `CODEX_HOME/hooks.json` and the installed plugin cache for stale placeholders.

Do not assume common local tools exist in container250. If `rg` is unavailable, use `find`, `grep -RIn`, `sed`, `nl -ba`, and `head`/`tail` without treating the missing `rg` as a blocker.

For long-running remote commands, use remote `tmux` through `c250-session` or an explicit remote `tmux` session. Plain `nohup` or `setsid` launched from a non-interactive Docker exec can fail to persist after the wrapper process exits.

For `/home/chehejia/cov-evalution` evaluations, a Git worktree isolates harness code, not mutable runtime state. Parallel evaluation sessions need independent `MVBS_PRO_DIR` target repositories, log directories, and any model/env-specific runtime outputs. Serial batches in the same session can reuse one runtime repo after reset; separate user windows or worktrees running at the same time should not share the same mutable MVBS repo.

For GitLab-backed marketplace or plugin updates on c250, keep credentials ephemeral. Pass the token into the remote process only for the command that needs it, use `GIT_ASKPASS`, run remote Git commands with `git -c credential.helper= ...`, and verify `/home/chehejia/.git-credentials` does not retain the GitLab host afterwards. Do not put tokens in remote URLs, logs, marketplace config, or plugin manifests.

For `marketplace-zxgc` on c250, use `/data/jenkins/marketplace-zxgc` as the local marketplace source after cloning or pulling GitLab. Register it with `/data/jenkins/.codex/bin/codex plugin marketplace add /data/jenkins/marketplace-zxgc`, then install with `codex plugin add marketplace-zxgc@marketplace-zxgc`. Local marketplaces cannot be refreshed with `codex plugin marketplace upgrade`; after pulling the source, refresh the installed plugin cache with `codex plugin remove marketplace-zxgc@marketplace-zxgc` followed by `codex plugin add marketplace-zxgc@marketplace-zxgc`.

For single checks, prefer:

```bash
c250-exec 'hostname; whoami; pwd'
c250-exec -C /home/chehejia/cov-evalution 'ls -la'
```

If direct Docker API calls return `EOF`, check proxy routing. The wrappers set `NO_PROXY` for `10.134.43.250,10.0.0.0/8,localhost,127.0.0.1,::1` automatically.

If `c250-codex` shows `read tcp ... connection reset by peer`, do not try to make the TCP connection immortal. The supported recovery model is persistent remote tmux:

```bash
c250-codex --session work -C /home/chehejia/cov-evalution "start task"
c250-codex --session work
c250-codex work
c250-session tail work -n 160
```

`c250-codex qwen-eval` attaches to or starts the `qwen-eval` persistent session. To send a prompt to the default `codex` session, use `--` before the prompt: `c250-codex -- "分析当前目录结构"`.

Only use `c250-codex --direct` for short one-off interactive sessions.

Do not print `auth.json` contents or private tokens.
