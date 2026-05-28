# marketplace-zxgc Inventory

## Packaged Assets

### Skills

- `marketplace-zxgc`: operate this marketplace pack.
- `session-self-improvement`: session retrospective and persistence targeting.
- `session-self-improvement-eval`: quality audit for completed self-improvement outputs.
- `twin-agent-zyy`: Zheng Yuyu twin-agent evolution summaries, task-evolution templates, OKR/IR/SR/AR routing, and no-regression boundaries.
- `continuous-agent-loop`: long-running and continuous agent task loops with quality gates, checkpoints, and recovery controls.
- `enterprise-agent-ops`: long-lived/service-like agent runner operations with observability, safety controls, rollout, rollback, and incident response.
- `self-improving-agent`: semantic/episodic self-improvement workflow.
- `continuous-learning-v2`: learning candidate pipeline.
- `code-refactor`: automated helper commands for autocommit, autofix, autosummary, autodoc, autointerpret, and auto-merge-request workflows.
- `codex-hooks` and `codex-hook`: hook configuration workflows.
- `codex-remote-container` and `codex-ssh-remote-config`: remote Codex/container workflows.
- `c250`: optional c250 remote workflow skill, packaged so `kg-code ensure-skills --include-remote` can install its missing dependency without making it a default active skill.
- `algorithm-engineer-workflow`: top-level algorithm engineering workflow for ML data, training, evaluation, TensorBoard, RL, and agent trace work.
- `algorithm-data-diagnosis`, `algorithm-tensorboard-analysis`, `algorithm-training-debug`, `algorithm-training-review`, `algorithm-rl-debug`, `algorithm-eval-diagnosis`, `algorithm-eval-closure`, and `algorithm-agent-trace-analysis`: focused algorithm engineering diagnosis and review skills.
- `kg-code`: multi-repository code graph create/query workflow with code-review-graph, graphify, GitNexus, Understand-Anything-compatible artifacts, c250, and lpai-dev routing. It is packaged for opt-in sync, not default activation, and can auto-install missing dependent skills from local skill sources.
- `task2zxgc`: task export workflow.
- `agent-memory-mcp`: optional persistent memory MCP workflow. It is installed with its MCP server by `scripts/install-agent-memory-mcp.sh`, not by default skill sync.

### Tools

- `tools/agentMemory`: Codex-adapted agentMemory MCP server source and compiled output. `node_modules` is excluded; target machines install dependencies locally.

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
- `scripts/install-agent-memory-mcp.sh`

## Excluded Assets

- `~/.codex/auth.json`
- API keys, tokens, cookies, private keys
- Raw `$CODEX_HOME/twin-agent-zyy/evals/` session artifacts. The packaged `twin-agent-zyy/references/` files are seed references only; durable eval/profile data stays target-local under `$CODEX_HOME/twin-agent-zyy/`.
- raw logs and SQLite runtime state
- personal cache directories
- `tools/agentMemory/node_modules`
