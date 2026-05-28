---
name: continuous-agent-loop
description: Patterns for long-running or continuous autonomous agent tasks with loop selection, quality gates, progress checkpoints, recovery controls, and handoff boundaries. Use when the user asks for 长程任务, long runner, continuous agent loop, autonomous loop, multi-step unattended execution, or long-running task governance.
---

# Continuous Agent Loop

## Purpose

Operate long-running agent work without losing control of scope, quality, progress, or recovery. This skill is for task execution patterns that may span many iterations, tools, validations, commits, or handoffs.

It does not grant permission to run indefinitely. Every loop needs a measurable goal, stop condition, checkpoint cadence, recovery plan, and user-visible status.

## When To Use

- The user mentions `长程任务`, `long runner`, `long-running`, `continuous-agent-loop`, `autonomous loop`, or `持续执行`.
- A task requires repeated investigate -> implement -> verify -> repair cycles.
- A task has multiple independent phases that should be checkpointed.
- A task may run commands or remote jobs that need polling, status summaries, and resumable state.
- A task needs quality gates before continuing to the next phase.

## Loop Selection

| Pattern | Use When | Stop Condition |
| --- | --- | --- |
| sequential loop | One agent can progress through ordered phases | all planned phases pass verification |
| repair loop | A failing check can be repeatedly diagnosed and fixed | check passes or root cause is blocked |
| eval loop | Metrics or benchmark output drives next changes | metric target reached or regression risk exceeds value |
| remote job loop | Work runs in remote shell, batch job, CI, or eval service | job completes, fails with actionable cause, or timeout |
| parallel sidecar loop | Independent analysis or verification can run while main work continues | sidecar result integrated or discarded with reason |
| checkpoint/handoff loop | Work may exceed one session or context window | durable checkpoint written and next action clear |

## Required Control Plan

Before starting a long loop, write or state:

- `Goal`: what outcome closes the loop.
- `Scope`: what is in and out.
- `Progress signal`: how progress will be measured.
- `Quality gate`: command, test, metric, review, or artifact required before advancing.
- `Checkpoint cadence`: when to summarize state, usually after each phase or every material blocker.
- `Stop conditions`: success, repeated same failure, missing permission, unsafe action, cost/time limit, or user decision.
- `Recovery`: how to resume, rollback, shrink scope, or ask for input.

## Execution Rules

- Prefer small loops with concrete verification over broad autonomous runs.
- Do not repeat the same failing action without a changed hypothesis, input, or environment.
- If a loop stalls, freeze it, write the current state, identify the root blocker, and reduce scope to the smallest failing unit.
- Keep user updates concise and evidence-based during long work.
- Persist durable state in the task's natural place: requirement `.plan.md` / `.task.md`, repo `docs/总结`, CI logs, eval reports, or a checkpoint file.
- Do not store raw secrets, auth files, cookies, private keys, or long command dumps.

## Checkpoint Template

```md
# Long-Running Task Checkpoint

- Goal:
- Current phase:
- Completed:
- Running:
- Blocked:
- Evidence:
- Quality gate status:
- Next action:
- Stop / rollback condition:
- User decision needed:
```

## Failure Modes

- Loop churn without measurable progress.
- Retrying with the same root cause.
- Expanding scope to avoid a blocker.
- Passing a local check that is unrelated to the user's success criterion.
- Losing branch/process/job state after context compaction.
- Allowing background sessions to continue after the task is done.

## Recovery Controls

1. Freeze the loop and stop launching new work.
2. Capture current branch, process, job, log path, and last successful artifact.
3. State the root blocker and what changed since the last attempt.
4. Reduce to the smallest reproducible failing unit.
5. Run one targeted verification.
6. Resume only with a new hypothesis or user-approved path.

## Integration

- Use `session-self-improvement` after significant long-running work to persist reusable lessons.
- Use `twin-agent-zyy` when the loop reveals how the agent should better match the user's work style.
- Use `code-refactor` for MR/issue delivery when the loop produces code changes.
- Use domain-specific skills such as `algorithm-eval-closure` or `algorithm-agent-trace-analysis` when the loop is evaluation or trace-analysis focused.
