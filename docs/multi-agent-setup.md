# Configure multi-agent collaboration

This optional pack adds explicit planning/execution handoff, bounded model routing,
dependency waves, retry preservation and coordinator acceptance. It does not launch
models by itself. A Codex environment with native delegation is required for real
parallel work; unsupported tools/models remain coordinator work. Copying skill files
to another app does not prove that app supports the native parameters.

## Install as one sibling set

Copy these directories from `plugins/marketplace-zxgc/skills/` to your chosen skill
root: `engineer-router`, `requirement-to-plan`, `code-exec`, `multi-agent-orchestrator`.
Keep sibling names and bundled scripts/references/tests. Back up existing installations
and review differences before updating. No installer overwrites user skills here.
For repository-only trials, use the directories in place. Python 3.9+ is required.

Only code-exec is the execution entry. Existing planning/execution skills remain
usable on their own; the four-skill set is required for this optional collaboration mode.
No global AGENTS, hooks, provider services or credentials are installed.

## Configure models

Edit `code-exec/references/tiered-execution-policy.json` in the installed copy:

- strong: coordinator responsibility; it does not switch the active coordinator model.
- worker: bounded implementation; use a supported capable model ID.
- scout: bounded read-only evidence collection; use a supported economical model ID.
- max_attempts: total attempts including failures; defaults to 2.
- max_context_chars: serialized input character limit, not token/price measurement.

The bundled IDs are placeholders. They must not be sent to a provider. Derive
available_models from the current tool and verify its support for model, default
agent_type, medium reasoning_effort and fork_turns=none. Unsupported parameters
require coordinator handling; never silently change providers. Native roles are not
created by this pack. Role labels from the router are responsibilities only.

## Reproducible dry run

From this repository root (shell variables are local to this example):

```bash
skills_root="$PWD/plugins/marketplace-zxgc/skills"
python3 "$skills_root/engineer-router/scripts/route_engineer_task.py" \
  'Inspect two independent documentation files' --workspace "$PWD" \
  --product-line shared > /tmp/opc-example-context.json
python3 "$skills_root/multi-agent-orchestrator/scripts/make_example.py" \
  --context /tmp/opc-example-context.json --model your-scout-model \
  > /tmp/opc-example-workflow.json
python3 "$skills_root/multi-agent-orchestrator/scripts/orchestrate.py" \
  --workflow /tmp/opc-example-workflow.json \
  --product-context /tmp/opc-example-context.json \
  --active-module-key example-collaboration --format json
```

The example is deliberately unconfirmed and must not yield dispatchable work.
After real authorization, configure actual model IDs, verify file scope and runtime
capacity, set confirmed=true and recompute. Never use this sample as authorization.
The coordinator records running + attempts before spawning and owns state updates.
Only passed AND accepted prerequisites release downstream tasks. Restore running
agents rather than dispatching them again. Unknown usage stays unknown.

## Validate without model calls

```bash
python3 -m pytest plugins/marketplace-zxgc/skills/engineer-router/tests \
  plugins/marketplace-zxgc/skills/code-exec/tests \
  plugins/marketplace-zxgc/skills/requirement-to-plan/tests \
  plugins/marketplace-zxgc/skills/multi-agent-orchestrator/tests
```

Tests prove deterministic contracts, not LLM quality or token savings. Real runtime
smoke tests and paired usage evaluation remain environment-specific. The repository's
legacy validate-pack.sh may stop on missing baseline marketplace files; this pack
does not reconstruct those unrelated files or claim full marketplace installation.

Rollback: restore the backed-up four skill directories, or revert the publishing PR.
Existing task state and evidence should be retained for audit and recovery.
