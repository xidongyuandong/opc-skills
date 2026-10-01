# opc-skills Skills Catalog

This catalog summarizes the packaged skills under the legacy-compatible `plugins/marketplace-zxgc/skills` path. The source of truth for each workflow remains that skill's `SKILL.md`; this file is the marketplace-level discovery view.

## Catalog Rules

- Every packaged skill directory must contain `SKILL.md`.
- Every packaged skill should appear in this catalog exactly once.
- Default sync is controlled by `plugins/marketplace-zxgc/scripts/sync-skills.sh`.
- Opt-in skills may be packaged without being active on target machines by default.
- Compatibility aliases should route to the maintained parent workflow instead of duplicating behavior.

## Packaged Skills

| Skill | Default sync | Purpose |
|---|---:|---|
| `agent-memory-mcp` | No | Packages a Codex-adapted persistent memory MCP server and install helper. Opt-in because enabling it writes target-local MCP configuration. |
| `algorithm-agent-trace-analysis` | Yes | Analyze agent trajectories, tool calls, JSONL traces, max-turn failures, protocol issues and agent evaluation logs. |
| `algorithm-data-diagnosis` | Yes | Diagnose ML/LLM training and evaluation data quality, schema, labels, leakage, drift and malformed samples. |
| `algorithm-engineer-workflow` | Yes | Top-level algorithm engineering workflow across data, training, TensorBoard, checkpoints, evaluation, RL and model quality. |
| `algorithm-eval-closure` | Yes | Close algorithm evaluation loops by reviewing entrypoints, logs, verifier status, issue resolution and next improvement plans. |
| `algorithm-eval-diagnosis` | Yes | Diagnose model or agent evaluation failures, solve/pass-rate regression, benchmark drift and scoring issues. |
| `algorithm-rl-debug` | Yes | Debug RLHF, GRPO, PPO, DPO, reward functions, rollouts, KL, advantages and verifier rewards. |
| `algorithm-tensorboard-analysis` | Yes | Analyze TensorBoard event files and training curves such as loss, reward, KL, learning rate and convergence health. |
| `algorithm-training-debug` | Yes | Debug training failures, fine-tuning scripts, optimizer/config issues, checkpoint handling, OOM, NaN and reproducibility. |
| `algorithm-training-review` | Yes | Review training workflows, scripts, TensorBoard metrics, checkpoints, reward functions, RL logs and improvement plans. |
| `auto-issue` | No | Create, update, or draft GitLab issues from user-provided context or current repository facts. |
| `c250` | No | Operate container250 through local wrappers and support c250-specific Codex sync or remote execution workflows. |
| `clash-verge-add-static-ip` | No | Collect required proxy inputs and create a separate region-named Clash Verge subscription with GUI, refresh and exit validation. Install together with `clash-verge-static-ip`. |
| `clash-verge-static-ip` | No | Shared Ruby builders, JavaScript sidecar template and offline regressions for static-IP dialer chains; required by `clash-verge-add-static-ip`. |
| `codex-hook` | Yes | Focused single-hook creation, modification, validation and troubleshooting for Codex hook scripts/config. |
| `codex-hooks` | Yes | Main workflow for Codex hook design, installation, migration, validation and troubleshooting. |
| `codex-remote-container` | Yes | Configure and operate Codex inside remote Docker/devcontainer environments. |
| `codex-ssh-remote-config` | Yes | Configure Codex SSH remote usage, remote Codex home, login state, network and sandbox setup. |
| `continuous-agent-loop` | Yes | Run long-running or continuous agent tasks with loop selection, checkpoints, recovery controls and handoff boundaries. |
| `continuous-learning-v2` | Yes | Instinct-based session learning with confidence scoring and project-scoped learning candidates. |
| `code-exec` | No | Executes an already confirmed Plan/Todo through scoped implementation, regression checks, review, and evidence closeout. |
| `enterprise-agent-ops` | Yes | Operate long-lived agent workloads with observability, security boundaries, rollout controls and lifecycle management. |
| `kg-code` | No | Build and query multi-repository code knowledge graphs for architecture lookup and impact analysis. |
| `marketplace-zxgc` | Yes | Maintain this local Codex marketplace pack, including skills, AGENTS templates, hooks, install scripts and validation. |
| `requirement-to-plan` | No | Converts ambiguous or document-driven requirements into one evidence-based, confirmation-gated Plan/Todo. |
| `self-improving-agent` | Yes | Compatibility alias for older self-improvement usage; route substantive work through `session-self-improvement`. |
| `self-improvement-session` | No | Archives factual retrospectives and drafts reusable behavior improvements while requiring confirmation for behavior-changing assets. |
| `session-self-improvement` | Yes | Review a session or idea to decide whether to update rules, AGENTS, memory, skills or docs. |
| `session-self-improvement-eval` | Yes | Evaluate whether a completed self-improvement run produced high-quality summaries, docs and final reporting. |
| `task2zxgc` | No | Summarize the current Codex session into a structured task report and push it to the configured report repository. |
| `twin-agent-zyy` | Yes | Maintain Zheng Yuyu twin-agent evolution artifacts, goals, decision memory and persona-oriented summaries. |

## Default Sync Notes

The current default sync set includes self-improvement, hook, remote setup, algorithm workflow and enterprise operations skills. Some packaged skills are intentionally opt-in:

- `agent-memory-mcp`: target-local MCP config and dependencies.
- `auto-issue`: GitLab side effects.
- `c250`: remote/container-specific workflow.
- `kg-code`: larger code graph build/query surface.
- `task2zxgc`: marketplace-local application source of truth.

If a new skill is added to the pack, update this catalog and decide separately whether default sync is justified.

## Naming Compatibility

The public marketplace direction is `opc-skills`. The `marketplace-zxgc` and `task2zxgc` skill names are preserved as legacy runtime identifiers until a separate migration plan changes active skill names, environment variables, scripts, and installation paths together.
