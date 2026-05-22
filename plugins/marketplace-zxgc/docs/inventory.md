# marketplace-zxgc Inventory

## Packaged Assets

### Skills

- `marketplace-zxgc`: operate this marketplace pack.
- `session-self-improvement`: session retrospective and persistence targeting.
- `self-improving-agent`: semantic/episodic self-improvement workflow.
- `continuous-learning-v2`: learning candidate pipeline.
- `code-refactor`: automated helper commands for autocommit, autofix, autosummary, autodoc, autointerpret, and auto-merge-request workflows.
- `codex-hooks` and `codex-hook`: hook configuration workflows.
- `codex-remote-container` and `codex-ssh-remote-config`: remote Codex/container workflows.
- `task2zxgc`: task export workflow.

### Templates

- `templates/AGENTS.global.md`: current global user-level AGENTS.md template.
- `templates/rules/default.rules`: curated, secret-free Codex rules template for safe marketplace maintenance and local inspection.

### Hooks

- `hooks/codex_learning_hook.py`
- `hooks/task2zxgc_posthook.py`
- `hooks/learning_review.py`
- `hooks.json.template`: portable Codex hook configuration template using `{{PLUGIN_ROOT}}`.
- `hooks.json`: repository example/template copy; install with `scripts/install-hooks.sh` so machine-specific paths are rendered at install time.

### Scripts

- `scripts/validate-pack.sh`
- `scripts/sync-skills.sh`
- `scripts/install-agents-md.sh`
- `scripts/install-hooks.sh`
- `scripts/install-rules.sh`

## Excluded Assets

- `~/.codex/auth.json`
- API keys, tokens, cookies, private keys
- raw logs and SQLite runtime state
- personal cache directories
