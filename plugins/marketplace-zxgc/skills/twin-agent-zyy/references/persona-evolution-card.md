# Persona Evolution Card Reference

Evolution marker: pattern-extraction
Source evidence: Task052601 confirmed an OKR-driven twin-agent design that must reduce work pressure without changing ordinary Codex task execution.
Changed target: `$CODEX_HOME/twin-agent-zyy/skills/persona-evolution-card.md`, linked from `session-self-improvement` and the `twin-agent-zyy` skill. Resolve `CODEX_HOME` from the environment, defaulting to `~/.codex`.
Why this target: Persona evolution is workflow-specific and should not become always-on user-level instructions.
Rejected broader targets: no AGENTS.md, hook, memory, or rule change by default.
Validation: run skill structure validation and session-self-improvement-eval after edits.

## Trigger

Use this reference only when the user explicitly asks for one of these during a self-improvement or retrospective request:

- `分身智能体`
- `Persona Evolution`
- `OKR`
- `IR/SR/AR`
- "减轻我的工作压力" in the context of personal agent evolution

Do not use this reference for ordinary `$session-self-improvement` runs that do not mention personal agent evolution.

## Purpose

The persona evolution sidecar helps the user turn task evidence into reviewable improvement proposals aligned with personal OKRs. It is not a new runtime agent, not an always-on persona prompt, and not permission to automatically modify high-weight Codex configuration.

The authoritative execution workflow is the `twin-agent-zyy` skill. This file remains the compact reference for Persona Evolution Cards, while `twin-agent-zyy` owns the full Task Evolution Summary dimensions: why the task exists, how it was defined, why that definition was chosen, how it was executed, how blockers were solved, which surrounding tools/information were used, and what working-style capability was learned.

## OKR Mapping

- `O1 RD->PD`: research-to-engineering conversion, Charter pre-research landing, verification quality.
- `O2 vertical capability`: M100, static analysis repair, test generation, RAG, code completion, full-file editing, business landing.
- `O3 learning delivery`: paper sharing, CodeReview, CodeInspection, team training, reusable review and delivery mechanisms.
- `none`: useful local context with no clear OKR alignment; default to `skip` unless there is strong safety or user-preference evidence.

## IR/SR/AR

- `IR` means Intent / Impact Requirement: why this matters, which OKR it serves, and what impact it should create.
- `SR` means Strategy / System Requirement: what workflow, tool boundary, persistence route, or no-regression guard should be used.
- `AR` means Action / Artifact Requirement: what concrete artifact, command, evaluation, file, proposal, or no-action decision closes the loop.

## Persona Evolution Card

Use one card per durable candidate:

```text
Persona Evolution Card
- Session theme:
- OKR: O1 / O2 / O3 / none
- IR:
- SR:
- AR:
- Evidence:
- Candidate type: semantic memory / episodic summary / procedural skill / hook gate / AGENTS rule / repo docs / no action
- Proposed target:
- Expected upside:
- Possible downside:
- Verification:
- Rollback:
- Decision: persist / defer / skip
```

## Task Evolution Summary Link

When the user asks for agent evolution toward "working like me", write a full Task Evolution Summary, not only a Persona Evolution Card. The summary must cover:

- Why this task.
- Task definition.
- Why this definition.
- Execution path.
- Problems and resolution.
- Tools and context used.
- User work style learned.
- Agent capability learned.

Use `$CODEX_HOME/skills/twin-agent-zyy/SKILL.md` as the canonical template. If this file is being read from the bundled marketplace skill rather than the durable store, use the local `twin-agent-zyy` skill's bundled references as read-only fallbacks.

## Decision Rules

- If `OKR=none` and evidence is weak, default to `Decision=skip`.
- If `AR` cannot point to a file, command, evaluation, proposal, candidate card, or explicit no-action conclusion, return to clarification.
- If `Candidate type` is `AGENTS rule`, `hook gate`, `procedural skill`, `semantic memory`, or `rules`, default to a proposal unless the user explicitly confirms that write target.
- If `Possible downside` is unclear, do not persist to high-weight targets.
- If a task is blocked by permission, external data, remote environment, Feishu scope, or user decision, route it to an approval queue instead of calling it complete.
- If the candidate would affect ordinary task execution, reject it unless the user explicitly asks for a separate implementation task and a no-regression verification plan exists.

## No-Regression Guard

A persona evolution output must state whether it:

- changes ordinary task execution paths;
- adds default context to unrelated sessions;
- writes or proposes changes to `AGENTS.md`, hooks, skills, rules, or memory;
- depends on raw session logs or sensitive data;
- has a verification and rollback path.

Any `yes` answer for the first four items means the output is a proposal, not an applied change.

## Historical Task Dry Run Rubric

Use these grades when simulating whether the persona agent can handle historical tasks:

- `A`: can independently complete requirement framing, context recovery, IR/SR/AR, method choice, documentation closure, and verification record without new permission or Codex-system changes.
- `B`: can complete analysis and plan, but real closure depends on user confirmation, external permission, remote environment, Feishu scope, evaluation data, or later source implementation. Put these into an approval queue.
- `C`: can only pre-analyze; core judgment requires real runtime access, unauthorized data, production permission, or actual source edits.

Do not treat an `A` dry-run grade as proof that a real external task has already executed.

## Output Placement

- Put durable twin-agent data and evaluation records under `$CODEX_HOME/twin-agent-zyy/`.
- Put durable project-specific knowledge in repo `docs/总结`.
- Put current task closure in `.task.md`.
- Put research and design evidence in `.research.md`.
- Put high-weight write targets in proposals until explicitly confirmed.
- Never store raw chat logs, raw session JSONL, tokens, credentials, cookies, private keys, or raw auth material.
