---
name: twin-agent-zyy
description: Maintain Zheng Yuyu's twin-agent evolution artifacts. Use when the user mentions 分身智能体, agent-twin, twin-agent, Persona Evolution, OKR, IR/SR/AR, or asks session-self-improvement to summarize how the agent should learn the user's working style.
---

# Twin Agent ZYY

## Purpose

Turn task evidence into reviewable twin-agent evolution artifacts so future agents can work closer to the user's real working style. This skill owns all twin-agent-specific requirements, logic, templates, safety boundaries, and content routing.

The goal is not ordinary task logging. The goal is to learn how the user defines work, why that definition is chosen, how the task is executed, how blockers are diagnosed, which surrounding tools and information are used, and what reusable capability should reduce the user's future workload.

## Storage

- Resolve `CODEX_HOME` from the environment; if unset, use `~/.codex`.
- Durable local store: `$CODEX_HOME/twin-agent-zyy/`
- Session/eval artifacts: `$CODEX_HOME/twin-agent-zyy/evals/`
- Stable profile material: `$CODEX_HOME/twin-agent-zyy/profile/`
- Canonical reference copy: `$CODEX_HOME/twin-agent-zyy/skills/persona-evolution-card.md`
- Discovery index: `$CODEX_HOME/twin-agent-zyy/README.md`
- If the durable store is absent on a newly installed machine, use this skill's bundled `references/okr-profile.md` and `references/persona-evolution-card.md` as read-only fallbacks, then create `$CODEX_HOME/twin-agent-zyy/` only when a twin-agent artifact is actually persisted.

Do not store raw session JSONL, raw chat logs, tokens, cookies, private keys, API keys, raw auth files, or unredacted sensitive payloads.

## Trigger

Use this skill when:

- The user explicitly mentions `分身智能体`, `agent-twin`, `twin-agent`, `Persona Evolution`, `OKR`, or `IR/SR/AR`.
- `$session-self-improvement` finds evidence that the task reduced user work pressure through repeatable agent assistance.
- The user asks why a task was done, how it was defined, why it was defined that way, how it was executed, how problems were solved, or which surrounding tools/information were used.

Do not make this an always-on persona. Ordinary task execution must not depend on this directory unless the user explicitly asks for twin-agent analysis or `$session-self-improvement` routes here through its relevance gate.

## Relevance Gate

Before writing a twin-agent artifact, check:

| Question | Pass condition |
| --- | --- |
| Trigger | Explicit twin-agent wording is present, or the session shows clear repeatable work-pressure reduction. |
| OKR fit | The lesson maps to `O1 RD->PD`, `O2 vertical coding-agent capability`, or `O3 learning delivery` in `$CODEX_HOME/twin-agent-zyy/profile/okr-profile.md`, or to bundled `references/okr-profile.md` when the durable store has not been created yet. |
| Goal alignment | The artifact can explain which OKR / IR / SR / AR dimension the task belongs to, how solving it helps that goal, and whether a higher-priority task should have been preferred. |
| Artifact value | A future twin-agent review could use the summary to understand, evaluate, or improve the user's personal agent workflow. |
| Safety | The artifact can be written without raw logs, secrets, credentials, raw auth files, or broad always-on instructions. |
| No-regression | The artifact does not alter ordinary Codex task execution; high-weight targets remain proposals unless explicitly confirmed. |

If the gate fails, report `No twin-agent summary written` and explain why.

## Task Evolution Summary

Every persisted twin-agent task summary must answer the user's working-style questions:

```md
# Twin Agent Task Evolution Summary

## 1. Why This Task
- Background:
- User intent:
- Business / engineering relevance:
- Why now:
- OKR / IR / SR / AR alignment:
- Target contribution after solving:
- Higher-priority alternative:

## 2. Task Definition
- Original request:
- Interpreted task:
- Scope:
- Non-scope:
- Completion criteria:

## 3. Demand Evolution
- User input / demand event:
- Demand represented:
- Why this demand emerged:
- Resolution strategy:
- Relationship to previous demands:
- Short-term goal alignment:
- Mid-term goal alignment:
- Long-term goal alignment:

## 4. Why This Definition
- Reasoning:
- Alternatives considered:
- Priority reasoning:
- User working-style alignment:
- Risk control:
- Human confirmation points:

## 5. Execution Path
- Investigation:
- Plan:
- Implementation:
- Verification:
- Delivery:

## 6. Problems And Resolution
- Problems encountered:
- Diagnosis:
- Root cause:
- Fix:
- Remaining risk:

## 7. Tools And Context Used
- Skills:
- MCP / plugins:
- Scripts / CLI:
- Docs / logs / configs:
- Key evidence:

## 8. User Work Style Learned
- Decision pattern:
- Quality bar:
- Preferred workflow:
- Safety boundary:
- Delivery expectation:

## 9. Agent Capability Learned
- Reusable capability:
- User pressure reduced:
- Persistence target:
- Not persisted:
- Next trigger:
```

## Persona Evolution Card

Also include or reference a concise card for durable candidates:

```md
# Persona Evolution Card

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

## Required Dimensions

Each persisted artifact must contain:

- `Theme`: technical/workflow theme.
- `OKR`: matching twin-agent OKR.
- `IR`: why this matters and what impact it should create.
- `SR`: strategy, workflow, tool boundary, persistence route, or no-regression guard.
- `AR`: artifact, command, evaluation, file, proposal, or no-action decision that closes the loop.
- `Goal alignment`: whether the task is primarily OKR-level, IR-level, SR-level, or AR-level work; which objective it supports; what contribution the solved task makes; and whether a higher-priority task exists.
- `Demand Evolution`: what the user's consecutive inputs represented, why each demand emerged, how the agent solved or should solve it, how it relates to previous demands, and how it maps to short-, mid-, and long-term goals.
- `Reusable capability`: repeatable capability future agents can reuse.
- `User pressure reduced`: burden reduced for the user, such as context recovery, evidence collection, decision framing, execution, verification, MR/issue delivery, or knowledge routing.
- `Evidence`: concrete files, commands, MR/issue links, verification results, or user corrections; no raw logs.
- `Persistence target`: where the lesson was stored and why.
- `Not persisted`: intentionally excluded data and why.
- `Risk`: overfitting, context bloat, privacy risk, or execution-path side effect.
- `Verification`: checks proving usefulness and safety.
- `Rollback`: how to remove, supersede, or downgrade the artifact.
- `Next trigger`: exact phrase or scenario that should reuse this summary.
- `No-regression guard`: whether it changes ordinary task execution, adds default context to unrelated sessions, touches high-weight targets, depends on raw logs/sensitive data, and has verification/rollback.

## Workflow

1. Reconstruct task evidence from visible conversation, compacted summaries, changed files, validation output, and relevant local artifacts.
2. Apply the relevance gate, OKR mapping, and goal-priority analysis. State whether the task is mainly OKR alignment, IR definition, SR strategy/system design, or AR execution/artifact delivery.
3. Write or update one concise artifact under `$CODEX_HOME/twin-agent-zyy/evals/`.
4. Update `$CODEX_HOME/twin-agent-zyy/README.md` or an eval index with a one-line discoverable link and reusable capability.
5. Keep project-specific implementation knowledge in the repo's `docs/总结`; keep compact machine-readable lessons in MCP/agent memory only when useful.
6. Validate required dimensions, index discoverability, and sensitive-content boundaries.

## Safety And Boundaries

- Do not store raw chat logs, raw session JSONL, tokens, credentials, cookies, private keys, raw auth files, or sensitive command output.
- Do not change user-level `AGENTS.md`, hooks, skills, rules, or memory as part of a twin-agent artifact unless the user explicitly confirms that exact target.
- Do not claim external work was completed from a retrospective alone.
- Do not turn one episode into a global rule when a repo doc, skill reference, memory, or no-action decision is narrower.

## Validation

After writing an artifact:

```bash
python3 - <<'PY'
from pathlib import Path
import os
codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
p = codex_home / "twin-agent-zyy" / "evals" / "<artifact>.md"
text = p.read_text()
required = [
    "Why This Task", "Task Definition", "Why This Definition",
    "Execution Path", "Problems And Resolution", "Tools And Context Used",
    "User Work Style Learned", "Agent Capability Learned",
    "Demand Evolution", "User input / demand event", "Demand represented",
    "Why this demand emerged", "Relationship to previous demands",
    "Short-term goal alignment", "Mid-term goal alignment", "Long-term goal alignment",
    "OKR / IR / SR / AR alignment", "Target contribution after solving",
    "Higher-priority alternative", "Priority reasoning",
    "Reusable capability", "User pressure reduced", "Next trigger",
]
missing = [x for x in required if x not in text]
raise SystemExit("missing: " + ", ".join(missing) if missing else "twin-agent-summary-ok")
PY
```

Search for sensitive categories, but report only categories and paths, not raw matches.
