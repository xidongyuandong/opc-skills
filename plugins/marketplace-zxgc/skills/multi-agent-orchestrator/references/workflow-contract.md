# Workflow contract

Install the four sibling skills in the repository README. Python 3.9+ is required.
Scripts use the standard library; compiler tests additionally use pytest.

Generate independent product_context with engineer-router for the canonical current
workspace. Pass that context and the active_module_key separately to orchestrate.py.
Never derive expected identity from the recovered workflow itself.

Top-level exact keys: product_context, active_module_key, confirmed, available_models,
capacity, tasks, state. Confirmation must reflect actual authorization.
Available models must be supported by the current native tool, not just a vendor list.
Capacity includes the coordinator; root_slots must be 1.

Each task has id, kind, difficulty, risk, goal, dependencies, allowed_files,
evidence_refs, acceptance, constraints. Kinds: planning/implementation/evaluation/
research/query. Difficulty: low/medium/high. Risk: low/high. File paths must be
absolute within the workspace, with existing parents. Only implementation tasks
may write. Symlink escapes, duplicate IDs, missing dependencies and cycles reject.

State has exactly one entry per task, with status, accepted, attempts, failure_reason,
usage. Status is pending/running/passed/failed. Only passed may be accepted; acceptance
requires coordinator review. Failed requires a reason; passed requires an empty reason.
Usage is null or measured cumulative {input_tokens, output_tokens}.

The coordinator alone writes state. Before spawning, mark running and increment
attempts. Count failed calls too. Retry changes status to pending after review,
never clears attempts or evidence. Running tasks are not dispatched again.
Unaccepted results never release dependencies. Read/write conflicts serialize waves;
explicit dependencies encode whether readers need the before or after version.

The scheduler prints proposals only: no model calls, state writes, background jobs,
automatic retries, OS locks, or enforced financial budgets. Inspect current native
tool compatibility before using spawn_args. Unsupported parameters return to the
coordinator. Follow docs/multi-agent-setup.md for an unconfirmed synthetic example.
