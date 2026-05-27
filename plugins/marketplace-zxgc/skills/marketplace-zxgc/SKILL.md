---
name: marketplace-zxgc
description: Maintain the local ZXGC Codex marketplace plugin pack, including packaged skills, AGENTS.md templates, hook scripts, install scripts, and validation. Use when asked to update, install, sync, validate, or explain marketplace-zxgc.
---

# Marketplace ZXGC

Use this skill to operate the local marketplace pack from the current cloned repository path.

## What This Plugin Owns

- Selected custom Codex skills under `skills/`.
- Safe AGENTS.md templates under `templates/`.
- Curated, secret-free Codex rules templates under `templates/rules/`.
- Learning and export hook scripts under `hooks/`.
- Maintenance scripts under `scripts/`.
- Marketplace metadata under `.agents/plugins/marketplace.json` and `.codex-plugin/plugin.json`.

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
2. Keep plugin metadata in sync with added capabilities.
3. When editing operation docs, classify each step as automated, parameterized, web-console manual, credential/manual, or destructive/manual before writing labels.
4. Run `./scripts/validate-pack.sh`.
5. Install or refresh the marketplace with `scripts/install-marketplace-zxgc.sh`; it performs marketplace registration, plugin-cache compatibility handling, skill/rule/hook sync, and verification.
6. Only run installation scripts with `--apply` after reviewing the dry run.

## Safety Rules

- Back up before replacing `AGENTS.md`, `hooks.json`, or existing skills.
- Keep skill backups outside the active skills directory, such as `$CODEX_HOME/backups/skills/<timestamp>/`, so old skill copies are not rediscovered.
- Prefer managed templates and explicit scripts over free-form manual instructions.
- Do not mark a step as `【人工】` when it can be handled through parameters, environment variables, dry-run/apply, GitLab API, or an existing marketplace script.
- If a step truly requires GitLab web UI, say `GitLab 网页端` explicitly and keep CLI commands as fallback only.
- Keep paths portable where possible; if a hook needs an absolute path, regenerate it with `install-hooks.sh`.
- Package only user-level constraints, rules, and workflows that are independent of a specific absolute path or repository.
- For absolute-path or repository-specific local rules, extract the reusable guidance into docs/templates and leave target-local commands to install scripts or local configuration.
- Never mirror raw local rules wholesale; curate them first and remove secrets, credentials, transient commands, and machine-only assumptions.
