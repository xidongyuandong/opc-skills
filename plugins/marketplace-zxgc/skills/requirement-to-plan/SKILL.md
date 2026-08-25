---
name: requirement-to-plan
description: Convert ambiguous or document-driven requirements into one evidence-based, confirmation-gated Plan/Todo. Use for requirement clarification, incremental feedback, multi-step implementation planning, validation design, and rollback planning.
---

# Requirement To Plan

Turn a request into a plan that is clear enough to execute and verify. This skill plans; it does not implement the newly created plan in the same turn.

## Core contract

1. Inspect current evidence before proposing work.
2. Keep one active planning truth per requirement module.
3. Clarify goal, scope, non-goals, assumptions, acceptance criteria, and rollback.
4. Compare feasible approaches before choosing one.
5. Include impact and verification for every implementation Todo.
6. Show the Plan/Todo to the user and stop once for confirmation.
7. A later confirmation authorizes the full listed Todo and verification set unless an exception boundary is crossed.

## When to use

- A requirement document or issue is the main task carrier.
- The request is ambiguous, multi-step, cross-file, or changes behavior.
- New feedback must be merged into an existing plan.
- The user asks for a Plan, Todo list, implementation approach, or acceptance criteria.

Do not use for one-line corrections, dependency installation, or read-only diagnosis unless the user explicitly asks for a plan.

## Evidence lanes

Use only the lanes needed by the task:

- Current evidence: requirement files, source, tests, configs, logs, ledgers, and reports.
- Repository search: existing helpers, patterns, packages, and local tooling.
- Historical evidence: prior plans, task records, session indexes, or changelogs. Treat history as guidance until current files verify it.
- External research: current vendor, legal, market, or library facts when the decision depends on them.

Record what each lane proved, what was skipped, and why. Never invent missing facts.

## Planning action boundary

Planning may perform read-only searches, bounded diagnostics, dry runs, local health checks, and temporary probes when they materially improve the plan. Record cleanup and residual risk for any process started.

Before confirmation, do not edit application behavior, migrate data, publish externally, change permissions, or perform irreversible operations.

## Single planning truth

For a requirement file `feature.md`, prefer:

```text
feature.md          # requirement truth; read-only unless explicitly authorized
feature.plan.md     # intent, evidence, approaches, Plan/Todo, validation, rollback
feature.task.md     # execution and verification evidence after implementation
```

Use an `active_module_key` to identify a module. A plan file may contain multiple active modules only when their keys and scopes are distinct. The same key must not have two current executable plans.

When updating an existing plan:

1. Create a before snapshot outside the requirement directory when practical.
2. Find the same key and close aliases.
3. Classify hits as same module, related but distinct, or unrelated history.
4. Merge valid same-module content into one current module.
5. Preserve unrelated historical modules.
6. Run the preservation guard.

Resolve the directory containing this `SKILL.md`, then run the bundled script from that directory:

```bash
cd /path/to/requirement-to-plan
python3 scripts/check_plan_preservation.py BEFORE.plan.md AFTER.plan.md
```

Do not replace the whole plan or remove substantial history without explicit approval and a rollback source.

## Contradiction analysis

Every non-trivial plan includes:

1. Contradictions written as `[A] vs [B]`.
2. One `main contradiction` and why it dominates.
3. Nature: adversarial, non-adversarial, or resource constrained.
4. Response and explicit tradeoff.
5. A monitor point for a secondary contradiction that may become dominant.

## Approach exploration

Compare at least five candidates for non-trivial work:

1. Current-repository/evidence-first.
2. Existing-solution search.
3. External research, or `not applicable` with a reason.
4. Minimal reversible change.
5. Broader architecture or workflow change.

For each candidate state correctness, efficiency, complexity, impact, validation, risk, rollback, and decision. Select exactly one primary approach.

For performance-sensitive, batch, concurrent, I/O-heavy, model-call, or data-processing work, at least three candidates must be technically distinct implementations.

## Testing and execution routing

Every implementation Todo must state:

- TDD: required, preferred, not applicable, or blocked with reason.
- Regression scope: focused, contract, E2E, full, skipped, or not applicable.
- Planned command or evidence artifact.
- Risk if a gate is skipped.
- Rollback point.

If the environment provides routing or review skills, reference them as optional capabilities. Do not copy their instructions into this skill and do not assume they are installed.

## Parallel work

Use parallel workers only for genuinely independent scopes. For every slice record:

- independence and upstream dependency;
- exact write scope;
- worker role and output contract;
- integration owner;
- verification and rollback.

Use serial execution for same-file conflicts, unclear contracts, irreversible writes, or tightly coupled changes.

## Todo requirements

Every code-changing Todo includes:

- User-visible outcome.
- Dependency.
- Change block and files/modules.
- Problem solved.
- Positive impact.
- Negative impact and risk.
- Impact scope.
- Testing route and regression scope.
- Parallelization decision.
- Validation.
- Rollback.

## Confirmation gate

A plan created or materially refreshed in the current assistant turn is not confirmed by the message that requested it. Stop after presenting it. Execution requires a later user message that confirms the visible plan.

After confirmation, do not ask between individual files, Todos, tests, reviews, or evidence updates. Pause again only for:

- scope outside the confirmed plan;
- destructive or irreversible data changes;
- external publish, send, payment, or permission changes not already approved;
- production or remote mutation;
- secrets, significant cost, compliance, or security risk;
- missing context that blocks safe execution.

## Output template

```markdown
## User-facing conclusion
- Decision:
- Implementation focus:
- Acceptance:
- Waiting for confirmation:
- Non-goals:

## Requirement clarification
- Goal:
- Scope:
- Non-goals:
- Evidence:
- Assumptions and gaps:

## Plan
### Contradiction analysis
1. Contradictions:
2. Main contradiction:
3. Nature:
4. Response:
5. Monitor:

### Approach exploration
| # | Approach | Decision | Correctness | Efficiency | Complexity | Impact | Validation | Risk / rollback |
|---|---|---|---|---|---|---|---|---|

### Selected approach
- Rationale:
- Files/modules:
- Source of truth:
- Testing route:
- Validation:
- Risks and rollback:

## Todo list
1. Verb-object title
   - User-visible outcome:
   - Dependency:
   - Change block:
   - Files/modules:
   - Positive impact:
   - Negative impact/risk:
   - Testing and regression:
   - Validation:
   - Rollback:

## Confirmation gate
- Waiting for one plan-level confirmation.
```

## Self-check

Before presenting the plan, verify:

- Real files or evidence were inspected.
- Incremental feedback was merged instead of appended as a second truth.
- The main requirement remains read-only unless explicitly authorized.
- Five approaches were considered where required.
- The five-step contradiction analysis is present.
- Every implementation Todo includes impact, testing, validation, and rollback.
- Important skipped checks and residual risk are explicit.
- The confirmation boundary is visible.
