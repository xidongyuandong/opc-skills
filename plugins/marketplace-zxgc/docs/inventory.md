# marketplace-zxgc Inventory

## Packaged Assets

### Skills

- `marketplace-zxgc`: operate this marketplace pack.
- `session-self-improvement`: session retrospective and persistence targeting.
- `twin-agent-zyy`: Zheng Yuyu twin-agent evolution summaries, task-evolution templates, OKR/IR/SR/AR routing, and no-regression boundaries.
- `continuous-agent-loop`: long-running and continuous agent task loops with quality gates, checkpoints, and recovery controls.
- `self-improving-agent`: semantic/episodic self-improvement workflow.
- `continuous-learning-v2`: learning candidate pipeline.
- `code-refactor`: automated helper commands for autocommit, autofix, autosummary, autodoc, autointerpret, and auto-merge-request workflows.
- `codex-hooks` and `codex-hook`: hook configuration workflows.
- `codex-remote-container` and `codex-ssh-remote-config`: remote Codex/container workflows.
- `algorithm-engineer-workflow`: top-level algorithm engineering workflow for ML data, training, evaluation, TensorBoard, RL, and agent trace work.
- `algorithm-data-diagnosis`, `algorithm-tensorboard-analysis`, `algorithm-training-debug`, `algorithm-training-review`, `algorithm-rl-debug`, `algorithm-eval-diagnosis`, `algorithm-eval-closure`, and `algorithm-agent-trace-analysis`: focused algorithm engineering diagnosis and review skills.
- `task2zxgc`: task export workflow.

### Templates

- `templates/AGENTS.global.md`: current global user-level AGENTS.md template.
- `templates/rules/default.rules`: curated, secret-free Codex rules template for safe marketplace maintenance and local inspection.

### Hooks

- `hooks/codex_learning_hook.py`
- `hooks/task2zxgc_posthook.py`
- `hooks/learning_review.py`
- `hooks.json.template`: portable Codex hook configuration template using `{{PLUGIN_ROOT}}`.
- `hooks.json`: intentionally empty plugin-level hook manifest. Install real hooks with `scripts/install-hooks.sh` so machine-specific paths are rendered into `CODEX_HOME/hooks.json`.

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
