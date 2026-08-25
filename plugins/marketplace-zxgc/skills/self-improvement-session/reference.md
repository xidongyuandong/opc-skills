# Self Improvement Session Reference

## Candidate routing

| Observation | Primary target | Why |
|---|---|---|
| One completed incident | case or task record | Describes what happened |
| Stable cross-task behavior requirement | rule or agent instructions | Governs future behavior |
| Reusable multi-step procedure | skill or workflow | Encodes execution decisions |
| Role-specific judgment or responsibility | role | Loaded for that task class |
| Stable user working preference | preference store | Describes the user, not system policy |
| Tool/environment fact | memory or repository context | Factual, not behavioral |
| Domain knowledge entry | knowledge base | Should be retrievable as knowledge |
| Deterministic acceptance condition | regression test or guard | Automatically proves a contract |
| Output-quality judgment with labels | evaluator | Requires calibration evidence |

Choose one authoritative target per business meaning. Cross-reference adjacent assets instead of copying full bodies.

## Repeated-correction root-cause table

| Root cause | Evidence | Earlier prevention |
|---|---|---|
| Requirement coverage gap | user adds missing goal/scope/acceptance | requirement coverage matrix |
| Evidence gap | conclusion preceded source inspection | evidence-first probe |
| Planning gap | Todo omitted a necessary change or validation | Todo-to-patch and gate mapping |
| Execution drift | implementation leaves confirmed scope | diff-to-plan review |
| Verification gap | tests cover structure but not behavior | proof-boundary checklist |
| Truth-source gap | facts split across conflicting files | single-source audit |
| Persistence gap | same correction recurs across tasks | confirmed rule/skill/role delta |

## Behavior candidate template

```markdown
### <candidate name>
- Evidence:
- Confidence:
- Terminal state:
- Proposed target:
- Proposed patch:
- Why this target:
- Rejected adjacent targets:
- Expected upside:
- Possible downside:
- Validation:
- Rollback:
- Confirmation required:
```

## Workflow candidate template

```markdown
### Workflow: <name>
- Trigger:
- Applicable:
- Not applicable:
- Input truth sources:
- Steps:
- Decision points:
- Validation gates:
- Failure recovery:
- Rollback:
- Proposed target:
- Why not only a case/rule/evaluator:
- Terminal state:
```

## Evidence reference template

```yaml
evidence_refs:
  - id: EVIDENCE-001
    source_system: local_file | command_output | issue | task_record | session_index
    relation: primary | related | mentioned | unknown
    path: <sanitized absolute path, repository-relative path, or TBD>
    locator: <heading, line, command, or search terms>
    proves: <claim supported>
    current_verification: verified | required | blocked-with-reason
```

Avoid storing credentials, private keys, cookies, authorization headers, or unnecessary personal data. Prefer references and sanitized summaries over raw transcript copies.

## Bad-case template

```markdown
### Wrong trigger
What request incorrectly activated which workflow?

### Why it was wrong
What intent, evidence, or boundary was missed?

### Correct route
What should the first action and validation gate be next time?
```

## Evaluation decision template

```markdown
### Evaluation readiness
- Deterministic checks:
- Traces:
- Human labels:
- Metrics:
- Judge prompt/config:
- Calibration evidence:
- Decision: deterministic-regression | error-analysis | evaluator-audit | judge-calibration | no-action | blocked-with-reason
- What improvement may be inferred:
- What must not be inferred:
```
