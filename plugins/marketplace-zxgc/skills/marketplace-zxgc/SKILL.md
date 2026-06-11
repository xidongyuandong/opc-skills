---
name: marketplace-zxgc
description: Maintain the local OPC/opc-skills Codex marketplace plugin pack while preserving legacy marketplace-zxgc runtime identifiers, including packaged skills, AGENTS.md templates, hook scripts, install scripts, catalog docs, and validation. Use when asked to update, install, sync, validate, rename, or explain marketplace-zxgc/opc-skills.
---

# Marketplace OPC / marketplace-zxgc

Use this skill to operate the local marketplace pack from the current cloned repository path.

## What This Plugin Owns

- Selected custom Codex skills under `skills/`.
- Safe AGENTS.md templates under `templates/`.
- Curated, secret-free Codex rules templates under `templates/rules/`.
- Learning and export hook scripts under `hooks/`.
- Maintenance scripts under `scripts/`.
- Marketplace metadata under `.agents/plugins/marketplace.json` and `.codex-plugin/plugin.json`.

## Public Branding And Legacy Runtime Names

The public-facing marketplace direction is `OPC` / `opc-skills`. Prefer that naming in README files, architecture docs, standards docs, public descriptions, and display metadata.

Do not blindly replace every `zxgc` or `ZXGC` occurrence with `opc` or `OPC`. First classify each occurrence as public-facing, compatibility/runtime, or historical evidence.

Preserve these legacy/runtime identifiers unless a separate migration plan explicitly covers install compatibility, target-machine paths, skill discovery, and rollback:

- `marketplace-zxgc`
- `plugins/marketplace-zxgc`
- plugin package `name`
- `MARKETPLACE_ZXGC_HOME`
- `ZXGC_SKILLS`
- `task2zxgc`

If a rename request says `zxgc -> opc`, use the default policy `public-facing opc + legacy/runtime compatibility`: update user-visible docs and display metadata, keep runtime identifiers stable, then document the remaining legacy names as intentional compatibility anchors.

## What This Plugin Must Not Own

- `auth.json`, API keys, cookies, private keys, or token files.
- Machine-specific secrets or raw credential output.
- Silent overwrites of user `AGENTS.md`, `hooks.json`, or existing skills.

## Common Commands

From the plugin root:

```bash
./scripts/validate-pack.sh
./scripts/sync-skills.sh --dry-run
./scripts/sync-skills.sh --apply
./scripts/install-agents-md.sh --mode replace --yes
./scripts/install-hooks.sh --dry-run
./scripts/install-hooks.sh --apply
./scripts/install-rules.sh --dry-run
./scripts/install-rules.sh --apply
```

From the marketplace root:

```bash
codex plugin marketplace add "$HOME/marketplace-zxgc"
codex plugin marketplace upgrade marketplace-zxgc
codex plugin marketplace remove marketplace-zxgc
./scripts/auto-submit-marketplace-change.sh --dry-run --title "update marketplace"
./scripts/auto-submit-marketplace-change.sh --apply --title "update marketplace"
```

Prefer `./scripts/install-marketplace-zxgc.sh --dry-run` and then `--apply` for local marketplace refresh. Codex CLI plugin commands differ by version: some versions support installed plugin `add/list`, while newer local-marketplace flows only support `plugin marketplace add/upgrade/remove` and may reject `marketplace upgrade` for a local directory. The install script owns that compatibility check.

## Update Workflow

1. Copy or edit assets inside `plugins/marketplace-zxgc/`.
2. Keep plugin metadata and `docs/skills-catalog.md` in sync with added capabilities.
   Adding a new packaged skill or capability does not imply it should be installed by default. Before adding any new skill to `scripts/sync-skills.sh` `DEFAULT_SKILLS`, or otherwise making it active on target machines, get explicit human confirmation for that exact default-sync change.
3. When editing operation docs, classify each step as automated, parameterized, web-console manual, credential/manual, or destructive/manual before writing labels.
4. Run `./scripts/validate-pack.sh`.
5. Install or refresh the marketplace with `scripts/install-marketplace-zxgc.sh`; it performs marketplace registration, plugin-cache compatibility handling, skill/rule/hook sync, and verification.
6. Only run installation scripts with `--apply` after reviewing the dry run.

## Skills Catalog Workflow

When adding, removing, renaming, or materially changing packaged skills, keep `docs/skills-catalog.md` as the single discoverability surface for current packaged skills.

Before writing a custom catalog generator or checker, search existing local tooling first, especially `find-skills`, `skill-creator`, `plugin-creator`, `cursor-quality-inspection`, and this pack's `scripts/validate-pack.sh`. External marketplace validators can inform the design, but local validation must remain runnable without depending on external services.

Minimum workflow:

1. Scan `plugins/marketplace-zxgc/skills/*/SKILL.md`.
2. Ensure every packaged skill directory appears exactly once in `docs/skills-catalog.md`.
3. Keep each catalog row aligned with the skill's `name`, description, and current default-sync or opt-in policy.
4. Cross-check default-sync claims against `plugins/marketplace-zxgc/scripts/sync-skills.sh`.
5. Run `plugins/marketplace-zxgc/scripts/validate-pack.sh`.

Longer term, prefer a small generator/checker that reads `SKILL.md` metadata and fails validation on missing or duplicate catalog entries. Do not block urgent marketplace PRs on that generator if the current manual catalog check passes.

## Safety Rules

- Back up before replacing `AGENTS.md`, `hooks.json`, or existing skills.
- Treat marketplace skill additions in two stages: packaging is allowed after validation, but default synchronization/activation requires explicit human confirmation. Prefer optional `ZXGC_SKILLS=...` instructions for low-frequency or high-impact skills.
- For OPC/opc-skills branding, preserve legacy runtime identifiers until an explicit migration plan is confirmed; avoid broad text replacement across scripts, env vars, plugin names, or task-specific skill names.
- Keep skill backups outside the active skills directory, such as `$CODEX_HOME/backups/skills/<timestamp>/`, so old skill copies are not rediscovered.
- For c250 user-level `AGENTS.md` sync, do not treat local as the only source of truth. Read both local and remote `AGENTS.md`, merge durable user-level constraints, write the merged result back to both sides, then verify hashes match. If a conflict cannot be safely resolved, preserve both versions in a reviewable merge artifact instead of overwriting either side.
- Prefer managed templates and explicit scripts over free-form manual instructions.
- Do not mark a step as `【人工】` when it can be handled through parameters, environment variables, dry-run/apply, GitLab API, or an existing marketplace script.
- If a step truly requires GitLab web UI, say `GitLab 网页端` explicitly and keep CLI commands as fallback only.
- Keep paths portable where possible; if a hook needs an absolute path, regenerate it with `install-hooks.sh`.
- Package only user-level constraints, rules, and workflows that are independent of a specific absolute path or repository.
- For absolute-path or repository-specific local rules, extract the reusable guidance into docs/templates and leave target-local commands to install scripts or local configuration.
- Never mirror raw local rules wholesale; curate them first and remove secrets, credentials, transient commands, and machine-only assumptions.
