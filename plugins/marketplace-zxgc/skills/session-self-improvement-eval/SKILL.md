---
name: session-self-improvement-eval
description: Evaluate whether a completed session-self-improvement run produced high-quality task summaries, repo docs/总结 notes, memory/rule updates, and final reporting. Use after $session-self-improvement finishes, when the user asks to grade self-improvement output quality, or when checking whether session summaries meet expectations before closing the task.
---

# Session Self Improvement Eval

## Overview

Use this skill to audit the output of `$session-self-improvement` before treating the self-improvement task as complete. It checks whether the run split the session into useful themes, persisted the right artifacts, avoided unsafe content, and produced summaries that future agents can use to understand, solve, or implement similar work.

## Boundary

This skill evaluates completed artifacts; it does not perform the self-improvement pass itself. If defects are narrow and files are writable, patch the summary or skill that caused the defect, then re-run the evaluation. If the user requires event-level automatic execution after another skill completes, route to Codex hooks; a skill can only express workflow-level chaining.

## Inputs

Evaluate all available outputs from the just-finished `$session-self-improvement` run:

- Final assistant report, especially `Persisted`, `Not persisted`, `Decision analysis`, `Validation`, and `Next trigger`.
- Changed `AGENTS.md`, skill files, hook config, memories, and rule files when they were touched.
- Repository summaries under `<repo-root>/docs/总结/`.
- Requirement phase files such as `.requirment.md`, `.plan.md`, `.task.md`, and `.checkpoint.md` when the run involved a requirement file.
- Persona evolution outputs when the run explicitly used 分身智能体 / Persona Evolution / OKR / IR/SR/AR.
- Twin-agent artifacts under `$CODEX_HOME/twin-agent-zyy/` when they were created or updated. Resolve `CODEX_HOME` from the environment, defaulting to `~/.codex`.

## Rubric

Score 100 points total:

| Area | Points | Pass criteria |
| --- | ---: | --- |
| Theme split | 20 | Uses the minimum set of independent themes; each theme has one clear claim and reader task. |
| Persistence routing | 20 | Chooses the right target for each lesson: memory, AGENTS.md, skill, hook, repo `docs/总结`, task file, or no action. |
| Evidence and verification | 20 | Grounds claims in visible evidence, changed files, commands, and validation results. |
| Reuse value | 20 | Explains how future agents should understand, solve, or implement similar work; includes next actions or checklists. |
| Safety and boundaries | 20 | Excludes secrets, raw auth data, long logs, raw chat dumps, and unrelated transient progress; states automation boundaries. |

Grades:

- `pass`: score >= 85 and no blocking issue.
- `pass-with-fixes`: score 70-84 or only minor repairable issues.
- `fail`: score < 70, missing required artifacts, unsafe content, wrong persistence target, or no usable future-facing summary.

## Workflow

1. Reconstruct what `$session-self-improvement` changed.
   - Read the final report and changed file paths if visible.
   - Use `git status --short` inside relevant repositories when needed.
   - Inspect only the artifacts that matter to the self-improvement run.

2. Check topic quality.
   - Confirm summaries are not chronological chat logs.
   - Confirm each repo summary has one core claim and serves one future reader task.
   - Confirm split count is minimal; merge over-split notes or flag missing splits.

3. Check persistence quality.
   - Global `AGENTS.md` should contain only short, broadly applicable trigger rules.
   - Detailed workflows should live in skills.
   - Repository-specific understanding should live in the relevant repo's `docs/总结`.
   - One-off task state should stay in task/checkpoint files or not be persisted.

4. Check evidence, verification, and reuse value.
   - Require concrete file paths, commands, validation results, or user corrections for important claims.
   - Require practical future-use content: checklist, next trigger, implementation route, debugging route, or boundary conditions.
   - For persona evolution outputs, require a `Persona Evolution Card` or equivalent fields: OKR, IR, SR, AR, evidence, candidate type, proposed target, upside, downside, verification, rollback, and decision.
   - For twin-agent evolution outputs, require a `Twin Agent Task Evolution Summary` or equivalent sections: Why This Task, OKR / IR / SR / AR alignment, target contribution after solving, higher-priority alternative, Task Definition, Why This Definition, priority reasoning, Execution Path, Problems And Resolution, Tools And Context Used, User Work Style Learned, Agent Capability Learned, reusable capability, user pressure reduced, persistence target, not persisted, risk, verification, rollback, next trigger, and no-regression guard.
   - For persona evolution dry runs, confirm A/B/C ratings do not overclaim real execution. B-class items should name the approval queue dependency: user confirmation, external permission, remote environment, Feishu scope, evaluation data, or later source implementation.
   - When `$CODEX_HOME/twin-agent-zyy/` is used, confirm it stores only redacted data, profile/reference material, and evaluation artifacts rather than raw session JSONL.

5. Check safety.
   - Search for obvious sensitive patterns: token, secret, password, authorization, credential, cookie, private key, and unredacted local/user paths when the output is intended for shared repo docs.
   - Do not print raw sensitive matches; report only the category and file path.
   - For persona evolution and twin-agent outputs, verify that high-weight targets such as `AGENTS.md`, hooks, skills, rules, and memory are proposals unless the user explicitly confirmed that exact target.

6. Run the helper script on Markdown artifacts when useful.

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/session-self-improvement-eval/scripts/evaluate_summary.py" \
  /path/to/repo/docs/总结/example.md
```

7. Repair or report.
   - If a defect is narrow and the responsible file is in scope, patch it and re-run the check.
   - If the defect requires user judgment or hook-level automation, report it as a blocker or follow-up.

## Output Shape

Return:

- `Grade`: pass, pass-with-fixes, or fail.
- `Score`: total and per-area scores.
- `Blocking issues`: issues that prevent closing the self-improvement task.
- `Fixes applied`: files patched during evaluation.
- `Residual risks`: items not fixed and why.
- `Next trigger`: use `$session-self-improvement-eval` after future `$session-self-improvement` runs.
