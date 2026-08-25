---
name: code-exec
description: Execute an already confirmed implementation Plan/Todo through scoped changes, testing, review, verification, and evidence closeout. Use after planning is complete and the user has confirmed the executable scope.
---

# Code Exec

Implement the confirmed plan. A code diff is not the completion target; the relevant acceptance and regression gates are.

## Entry gate

Before editing:

1. Recover the executable source of truth: confirmed plan, issue, spec, or Todo.
2. Re-read its scope, non-goals, validation, and rollback.
3. Inspect current repository and worktree state.
4. Verify historical completion claims against current files.
5. Stop if the plan is missing, stale, ambiguous, or was newly created in the current turn.

A short message such as “confirm, implement” should recover the latest visible plan from conversation or project artifacts. It is not a new standalone requirement. If recovery fails, ask for the plan identifier instead of inventing scope.

## Confirmation boundary

A prior-turn confirmation authorizes all listed Todos, tests, repair loops, reviews, and evidence closeout. Do not pause between them.

Pause only when execution would:

- leave the confirmed scope;
- destroy or irreversibly change user data;
- publish, send, pay, or change permissions without prior approval;
- mutate production or remote environments outside the plan;
- expose credentials or create significant cost, compliance, or security risk;
- proceed without context needed for safe execution.

## Search before coding

Inspect existing source, tests, helpers, configuration, and local tooling before creating new behavior. Prefer repository indexes or code graphs when available, then verify important hits against real files.

Use historical evidence only as a pointer. Current files and deterministic checks remain authoritative.

Use external research only when current vendor, protocol, legal, or library facts affect the implementation.

## Worktree safety

Run:

```bash
git status --short --branch
git worktree list
```

If the checkout contains unrelated changes and the task is non-trivial, use an isolated branch/worktree unless the user explicitly selected the dirty checkout. Never revert unrelated user changes.

## Implementation rules

- Execute only confirmed Todos, in dependency order.
- Prefer the smallest change that satisfies the accepted behavior.
- Reuse project patterns and helpers.
- Do not add a second configuration or data truth.
- Do not add test-only production switches; isolate tests through fixtures, dependency injection, or monkeypatching.
- If new evidence changes scope or risk, stop and refresh the plan.

## TDD and bug fixes

For behavior changes, bugs, and refactors, prefer:

1. Reproduce or localize the symptom.
2. State the root cause.
3. Add a failing regression test when feasible.
4. Apply the smallest production fix.
5. Run the focused test.
6. Broaden to contract, integration, E2E, or full regression according to impact.

If a regression test is not feasible, record why and add the smallest deterministic guard available.

Failed tests are implementation feedback. Diagnose ownership before broadening the patch:

- current-task regression;
- unrelated dirty baseline;
- environment/provider/manual gate;
- unknown.

Only current-task regressions authorize changes inside the confirmed scope.

## Parallel execution

Use parallel workers only when the plan has disjoint write scopes and explicit interfaces. Each worker needs:

- owned files/modules;
- upstream dependencies;
- expected artifact;
- verification command;
- forbidden scope.

The main agent owns integration, conflict resolution, final verification, and reporting. Use serial execution for shared files or shared contracts.

## Verification ladder

Run the smallest useful checks first, then broaden:

1. Syntax or static checks.
2. Focused unit/regression tests.
3. Contract or integration checks.
4. Build/type/lint/security checks.
5. E2E or real-environment validation when required by the plan.
6. Diff and scope review.

For every meaningful result state what it proves and what it cannot prove. A structure check does not prove production behavior; a unit test does not prove deployment.

## Review

Use an independent review for non-trivial changes. Add security review when touching authentication, permissions, secrets, shell execution, network input, databases, or sensitive file operations.

Review against:

- requirement fit;
- hidden scope expansion;
- failure paths;
- rollback quality;
- test adequacy;
- security and privacy;
- portability and maintainability.

## Evidence closeout

When the task is requirement-driven, write execution evidence to the task record, not the requirement source. Put user value before logs:

```markdown
## Result summary
- What changed for the user:
- Core judgment:
- Status:

## Verification
- Check:
  - Result:
  - Proves:
  - Does not prove:

## Intentionally not done
- ...

## Rollback
- ...

## Evidence details
- Changed files:
- Commands:
- Residual risks:
```

Before declaring completion, scan the confirmed Todo for unresolved markers and classify every item as completed, intentionally skipped, blocked with reason, or out of scope.

## Completion signature

Final reporting should include:

- Requirement or issue identifier, or `N/A`.
- Requirement module.
- Accepted outcome.
- Actual result and user-visible behavior change.
- Core implementation judgment.
- Verification results with proof boundaries.
- Next action, if any.
- Skills/capabilities actually used.
- Historical evidence used or skipped.
- Important capabilities intentionally skipped and why.
- Intentionally untouched scope.
- Exact rollback point.

Do not lead with file counts, test counts, or command names. They are evidence, not the result.

## Final checklist

- [ ] Confirmed source of truth recovered.
- [ ] Current worktree inspected.
- [ ] Only confirmed scope changed.
- [ ] Existing implementation searched before adding new code.
- [ ] Regression/TDD route applied or explicitly skipped.
- [ ] Focused checks passed.
- [ ] Broader checks selected according to risk.
- [ ] Failure ownership classified.
- [ ] Diff reviewed for secrets and unrelated changes.
- [ ] Evidence explains what each check proves and cannot prove.
- [ ] Intentionally untouched scope and rollback are explicit.
