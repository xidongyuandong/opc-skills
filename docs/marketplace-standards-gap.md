# opc-skills Standards Gap

This document compares the local `opc-skills` repository with public skills marketplace patterns and records the smallest useful improvements.

Some runtime paths still use legacy `marketplace-zxgc` identifiers. This task treats those as compatibility names, not public branding.

## References

| Source | Observed pattern |
|---|---|
| https://github.com/addyosmani/agent-skills | Lifecycle commands, all-skills table, per-skill `SKILL.md`, setup docs for multiple agents, quality gates and checklists. |
| https://github.com/vercel-labs/skills | CLI-based add/use/list/update/remove, source formats, install scopes, symlink/copy choice and supported-agent matrix. |
| https://github.com/MiniMax-AI/skills | README skill table, official/community source labeling, per-agent install instructions, validation before contribution. |
| https://github.com/VoltAgent/awesome-openclaw-skills | Public registry/curation model, category discovery, install locations, quality/security filtering and security notice. |

## Already Satisfies

| Requirement | Current evidence |
|---|---|
| Marketplace manifest | `.agents/plugins/marketplace.json` points to the bundled local plugin. |
| Plugin manifest | `plugins/marketplace-zxgc/.codex-plugin/plugin.json` declares metadata and skill/hook/MCP/app manifest paths. The path remains legacy-compatible. |
| Skill directory convention | Packaged skills live under `plugins/marketplace-zxgc/skills/<skill>/SKILL.md`. The path remains legacy-compatible. |
| Local-first install path | Root README and plugin README document registration, sync, validation and install scripts. |
| Dry-run/apply safety | Install, sync, hooks, rules and AGENTS scripts expose dry-run or explicit apply modes. |
| Secret boundary | README and validate script reject obvious token-like values and warn against credentials. |
| Default sync separation | `sync-skills.sh` separates packaged skills from default activation. |

## Optimized In This Task

| Gap | Change |
|---|---|
| Repository logic was spread across README, scripts and manifests. | Added `docs/marketplace-architecture.md` with a system map, ownership boundaries and flows. |
| Packaged skill discovery required reading every `SKILL.md` or the partial Chinese overview. | Added `docs/skills-catalog.md` with every current packaged skill, purpose and sync policy. |
| Public marketplace standards were implicit. | Added this gap document with references and mapped requirements. |
| Validation did not require marketplace-level docs or skill catalog coverage. | Enhanced `validate-pack.sh` to check these docs and catalog entries. |
| README did not expose a compact maintainer entrypoint for architecture/catalog/gaps. | Added README pointers to the new docs. |

## Remaining Gaps

| Gap | Recommended handling |
|---|---|
| Full runtime rename is not complete. | Keep `marketplace-zxgc`, `MARKETPLACE_ZXGC_HOME`, `ZXGC_SKILLS`, and `task2zxgc` as legacy identifiers until a separate migration plan covers compatibility. |
| Skill catalog is currently hand-maintained. | Keep validate-pack coverage check. If the pack grows quickly, add a generator script that derives catalog rows from `SKILL.md` metadata. |
| Existing worktree contains many modified/deleted files unrelated to this task. | Keep this task's diff scoped to docs, README pointers and validation checks; do not revert unrelated files. |
| Security scanning is limited to regex-style secret detection. | For public release, add dependency/security checks appropriate to scripts and packaged tools. |

## Open Publication Gate

Before claiming GitHub/MR/PR completion:

1. Confirm or add a GitHub remote for `https://github.com/yiyepiaoling0715/opc-skills`.
2. Create a topic branch instead of pushing `master` directly.
3. Commit only intended files from this task, leaving unrelated dirty files untouched.
4. Push the branch to GitHub.
5. Create a PR/MR and record the URL.

If any step is blocked by authentication or missing repository access, record the exact blocker in the task ledger rather than reporting success.
