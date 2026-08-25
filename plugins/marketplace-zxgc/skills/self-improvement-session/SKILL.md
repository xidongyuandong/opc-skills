---
name: self-improvement-session
description: Review a completed task or corrected interaction, archive factual evidence, and propose reusable behavior improvements. Fact archives may be written automatically; rules, skills, roles, memory, preferences, knowledge bases, and other behavior-changing assets require a visible draft and user confirmation.
---

# Self Improvement Session

Turn a completed task, failure, or user correction into reusable learning without silently changing future agent behavior.

## Two-layer contract

### Layer 1: factual archive

May be written automatically unless the user asks for preview-only:

- session or task summary;
- case summary;
- sanitized evidence references;
- commands and verification results;
- user corrections and unresolved loops;
- current progress, blockers, next action, and rollback;
- evaluation evidence inventory.

Layer 1 describes what happened. It must not establish new behavioral policy.

### Layer 2: behavior-impact candidates

Must be drafted and shown before writing:

- agent instructions or rules;
- skills, hooks, roles, or workflows;
- user preferences or persistent memory;
- knowledge-base or search-index changes;
- evaluator datasets, judge prompts, or persistent configs;
- persona or long-term goal assets.

One confirmation may authorize the displayed candidate bundle. Never treat factual archival as permission to write Layer 2.

## Trigger modes

### Explicit

Use the full workflow when the user asks to run this skill, settle learning, retrospect, or improve future behavior. The final response must show:

- actual task outcome;
- trigger status: `explicitly-invoked`;
- factual archive status;
- behavior-impact candidate matrix;
- task ownership;
- workflow and evaluation decisions;
- validation boundaries;
- confirmation items and rollback.

### Automatic closeout scan

At substantial task closeout, an agent may detect candidates, draft proposals, and archive facts. Report one of:

- `candidate-detected`;
- `draft-generated`;
- `fact-archived`;
- `skipped-with-reason`;
- `blocked-with-reason`.

Automatic scanning never writes Layer 2 assets.

## Step 1: collect evidence

Inspect the current task truth before reflecting:

- original request and later corrections;
- plan, issue, spec, task ledger, checkpoint, or report;
- current source and relevant diff;
- tests, logs, metrics, labels, traces, or evaluator output;
- earlier task or session evidence when recurrence matters.

Historical evidence is guidance. Verify important claims against current files or commands.

Sanitize evidence references. Do not archive credentials, cookies, private keys, raw authorization output, private personal data, or unnecessary transcript content.

## Step 2: current task review

Record:

- Why the task existed.
- Accepted scope and non-goals.
- What actually changed.
- What was missed, retried, or left open.
- Root cause or central judgment.
- Verification status and proof boundaries.
- Current progress and first next action.
- Rollback point.

If no business or user-visible result changed, say so. Do not use document or test completion as a substitute for the actual outcome.

## Step 3: user correction analysis

Treat follow-up corrections as first-class requirement evidence. For each meaningful input, classify:

- goal or motivation;
- scope or constraint;
- acceptance criterion;
- non-goal;
- correction or open loop;
- execution authorization;
- stable preference candidate;
- governance or role candidate;
- no action.

When the user had to repeat or correct the same class of issue, explain:

- why multiple inputs were necessary;
- whether the gap was data, evidence, requirement coverage, planning, execution, verification, truth-source closure, or behavior persistence;
- which check should have happened earlier;
- the smallest reusable prevention mechanism.

## Step 4: similar-task reflection

When historical comparison is useful:

1. Query an available history index with the current task handle and failure terms.
2. Select the closest reliable match.
3. Record source, relationship, match terms, and why current verification is required.
4. Compare requirement type, correction pattern, implementation, validation, and remaining risk.
5. If evidence is weak or unavailable, report `blocked-with-reason`; do not invent recurrence.

Do not run full-history analysis unless the user explicitly requests it.

## Step 5: task ownership

Every substantive engineering retrospective should identify one accountable role or responsibility area. Auxiliary roles are advisory.

Record:

- primary owner and why;
- bounded auxiliary ownership;
- conflicting perspectives and final tradeoff;
- role improvement terminal state: `applied`, `rejected`, `needs-user-confirmation`, `blocked-with-reason`, or `no-action`.

Do not create a new role automatically. If no role fits, draft a candidate with scope and adjacent-role differences.

## Step 6: evaluation readiness

Inventory real evidence:

- deterministic tests or guards;
- traces and logs;
- human labels;
- metrics;
- evaluator configuration;
- judge prompts and calibration results;
- known failures.

Choose one terminal decision:

- deterministic regression gate;
- error analysis;
- evaluator audit;
- judge creation or calibration;
- `no-action` because evidence is absent or the outcome is not evaluative;
- `blocked-with-reason`.

Do not claim improvement from keyword presence or a documentation score alone. State the object improved, capability dimension, evidence source, and what cannot be inferred.

## Step 7: workflow candidate

Decide whether the task produced a reusable multi-step workflow. If yes, draft:

- name and trigger;
- applicable and non-applicable cases;
- input truth sources;
- ordered steps and decision points;
- validation gates;
- failure recovery and rollback;
- unique persistence target;
- why a case, rule, or evaluator alone is insufficient.

Otherwise state `no-action` or `rejected` with a reason.

## Behavior-impact candidate matrix

Every explicit run evaluates at least:

| Candidate | Required decision |
|---|---|
| skill or reference | terminal state + target + reason |
| execution-skill route | terminal state + trigger + boundary |
| rule or agent instructions | terminal state + scope + reason |
| role improvement | terminal state + capability dimension |
| workflow | terminal state + unique target |
| evaluation | terminal state + evidence |
| knowledge base | terminal state + source and retrieval check |
| knowledge-base maintenance | terminal state + health evidence |
| user preference | terminal state + stability evidence |
| repository context | terminal state + target document |
| self-improvement process | terminal state + regression check |

Allowed terminal states:

- `applied`: factual layer written, or a previously confirmed behavior change applied.
- `rejected`: duplicate, unsupported, unsafe, or wrong layer.
- `needs-user-confirmation`: complete Layer 2 draft is ready.
- `blocked-with-reason`: a concrete dependency prevents a safe decision.
- `no-action`: evaluated and no change is justified.

Never leave candidates as “later”, “deferred”, or “consider someday”.

## Candidate draft requirements

Every Layer 2 candidate must show:

- evidence and confidence;
- proposed target;
- exact proposed wording or change;
- why this target is authoritative;
- why adjacent targets were rejected;
- expected upside and downside;
- validation;
- rollback;
- confirmation request.

Before drafting a new skill or role, search existing assets for the same trigger and problem. Prefer updating an existing truth source over creating a duplicate.

## Factual archive template

```markdown
# Session Summary: <theme>

- Date:
- Repository:
- Trigger status:
- Task owner:

## Result summary
- User-visible result:
- Core judgment:
- Current progress:
- Remaining work:
- Rollback:

## Evidence
| ref | sanitized source | locator | what it proves | current verification |
|---|---|---|---|---|

## Timeline and decisions
- Request and motivation:
- Investigation:
- Alternatives:
- Selected approach:
- Implementation:
- Verification:

## User corrections and open loops
| input summary | classification | gap exposed | resolution | persistence decision |
|---|---|---|---|---|

## Evaluation evidence inventory
- Deterministic checks:
- Traces/labels/metrics:
- Decision:

## Reusable candidates
- Candidate matrix reference:
```

## Case summary requirements

A reusable case should include:

- trigger and scope;
- confidence from 0.3 to 1.0;
- symptom, root cause, resolution, and verification;
- sanitized source references;
- failure boundary and rollback;
- next trigger.

Use low confidence for a single environment-specific observation, medium for reproducible repeated evidence, and high only for repeatedly verified cross-context behavior.

## Post-apply closure gate

After confirmed Layer 2 writes, re-read the active factual archives. Active conclusions must no longer say the change is awaiting confirmation. Historical drafts may remain only in clearly marked historical sections.

Use the bundled deterministic checker:

Resolve the directory containing this `SKILL.md`, then run:

```bash
cd /path/to/self-improvement-session
python3 scripts/check_closure_consistency.py closure-payload.json
```

## Quality gate

Before final reporting, run the bundled evaluator on a summary or candidate draft:

```bash
cd /path/to/self-improvement-session
python3 scripts/evaluate_summary_quality.py path/to/summary.md
```

The result measures structural coverage and sensitive-pattern risk. It does not prove business correctness, historical truth, or future behavior improvement.

## Final response order

1. Actual result and user value.
2. Core judgment and prevention mechanism.
3. Trigger and archive status.
4. Behavior-impact candidate matrix terminal states.
5. Ownership, workflow, and evaluation decisions.
6. Validation proof and boundaries.
7. Next confirmation item, intentionally untouched scope, and rollback.
8. Paths and commands only as evidence details.

## Safety boundaries

- Do not expose secrets or raw private transcripts.
- Do not write behavior assets without confirmation.
- Do not treat historical summaries as current truth.
- Do not claim model training or measurable capability lift without real evidence.
- Do not change the original requirement merely to archive execution results.
- Do not create a second memory, rule, skill, role, or workflow truth for the same meaning.
