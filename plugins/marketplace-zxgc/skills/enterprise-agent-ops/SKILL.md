---
name: enterprise-agent-ops
description: Operate long-lived agent workloads with observability, security boundaries, rollout controls, incident response, and lifecycle management. Use for production or service-like agent runners beyond a single local CLI loop.
---

# Enterprise Agent Ops

## Purpose

Operate long-lived or service-like agent workloads that need controls beyond a single local session. This skill complements `continuous-agent-loop`: use `continuous-agent-loop` for task-loop design and checkpoints; use `enterprise-agent-ops` when the agent behaves like a deployed workload with runtime lifecycle, observability, permissions, rollout, rollback, or incident handling.

## When To Use

- The user mentions long-lived agent, agent runner, production runner, service agent, PM2, systemd, container, CI/CD runner, rollout, rollback, observability, or kill switch.
- An agent process should continue outside the current interactive session.
- A remote/batch/daemon agent needs logs, metrics, traces, restart policy, timeout budgets, or permission controls.
- The task asks how to operate, monitor, recover, or safely deploy agent workloads.

## Operational Domains

1. Runtime lifecycle: start, pause, stop, restart, resume.
2. Observability: logs, metrics, traces, checkpoints, audit events.
3. Safety controls: least privilege, scoped credentials, kill switches, timeout and retry budgets.
4. Change management: rollout, canary, rollback, approval gates, versioned artifacts.
5. Incident response: freeze, capture, isolate, patch, regress, resume.

## Baseline Controls

- Immutable deployment artifacts or pinned commit/version.
- Environment-level secret injection; never hard-code tokens or raw auth material.
- Least-privilege credentials and scoped filesystem/network access.
- Hard timeout, retry, and cost budgets.
- Structured logs with task id, run id, input category, outcome, failure class, and artifact links.
- Audit log for high-risk actions.
- Explicit stop/kill command documented before start.

## Metrics To Track

- Success rate.
- Mean retries per task.
- Time to recovery.
- Cost per successful task.
- Failure class distribution.
- Queue age / stuck task count.
- Rollback frequency.

## Incident Pattern

When failure spikes:

1. Freeze new rollout or stop accepting new work.
2. Capture representative traces and recent deployment identifiers.
3. Isolate the failing route, permission, input class, or dependency.
4. Patch with the smallest safe change.
5. Run regression and security checks.
6. Resume gradually with monitoring.

## Deployment Integrations

- PM2 workflows.
- systemd services.
- container orchestrators.
- CI/CD gates.
- remote tmux/session managers.
- batch/eval runners.

## Handoff To Other Skills

- Use `continuous-agent-loop` for local long-running loop structure, checkpoints, and stop conditions.
- Use `codex-remote-container` or `codex-ssh-remote-config` for remote execution setup.
- Use `algorithm-eval-closure` for algorithm/eval runner closure and failure taxonomy.
- Use `session-self-improvement` and `twin-agent-zyy` after significant operational lessons.
