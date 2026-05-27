---
name: twin-agent-zyy
description: Maintain Zheng Yuyu's twin-agent evolution artifacts. Use when the user mentions 分身智能体, agent-twin, twin-agent, Persona Evolution, OKR, IR/SR/AR, or asks session-self-improvement to summarize how the agent should learn the user's working style.
---

# Twin Agent ZYY

## Purpose

Turn task evidence into reviewable twin-agent evolution artifacts so future agents can work closer to the user's real working style. This skill owns all twin-agent-specific requirements, logic, templates, safety boundaries, and content routing.

The goal is not ordinary task logging. The goal is to learn how the user defines work, why that definition is chosen, how the task is executed, how blockers are diagnosed, which surrounding tools and information are used, and what reusable capability should reduce the user's future workload.

## Storage

- Durable local store: `~/.codex/twin-agent-zyy/`
- Session/eval artifacts: `~/.codex/twin-agent-zyy/evals/`
- Stable profile material: `~/.codex/twin-agent-zyy/profile/`
- Canonical reference copy: `~/.codex/twin-agent-zyy/skills/persona-evolution-card.md`
- Discovery index: `~/.codex/twin-agent-zyy/README.md`

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
| OKR fit | The lesson maps to `O1 RD->PD`, `O2 vertical coding-agent capability`, or `O3 learning delivery` in `~/.codex/twin-agent-zyy/profile/okr-profile.md`. |
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

## 2. Task Definition
- Original request:
- Interpreted task:
- Scope:
- Non-scope:
- Completion criteria:

## 3. Why This Definition
- Reasoning:
- Alternatives considered:
- User working-style alignment:
- Risk control:
- Human confirmation points:

## 4. Execution Path
- Investigation:
- Plan:
- Implementation:
- Verification:
- Delivery:

## 5. Problems And Resolution
- Problems encountered:
- Diagnosis:
- Root cause:
- Fix:
- Remaining risk:

## 6. Tools And Context Used
- Skills:
- MCP / plugins:
- Scripts / CLI:
- Docs / logs / configs:
- Key evidence:

## 7. User Work Style Learned
- Decision pattern:
- Quality bar:
- Preferred workflow:
- Safety boundary:
- Delivery expectation:

## 8. Agent Capability Learned
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
2. Apply the relevance gate and OKR mapping.
3. Write or update one concise artifact under `~/.codex/twin-agent-zyy/evals/`.
4. Update `~/.codex/twin-agent-zyy/README.md` or an eval index with a one-line discoverable link and reusable capability.
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
p = Path("~/.codex/twin-agent-zyy/evals/<artifact>.md").expanduser()
text = p.read_text()
required = [
    "Why This Task", "Task Definition", "Why This Definition",
    "Execution Path", "Problems And Resolution", "Tools And Context Used",
    "User Work Style Learned", "Agent Capability Learned",
    "Reusable capability", "User pressure reduced", "Next trigger",
]
missing = [x for x in required if x not in text]
raise SystemExit("missing: " + ", ".join(missing) if missing else "twin-agent-summary-ok")
PY
```

Search for sensitive categories, but report only categories and paths, not raw matches.
