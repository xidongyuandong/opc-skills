# marketplace-zxgc

Local Codex marketplace for ZXGC workflows.

This marketplace packages selected user-level Codex assets:

- custom skills
- AGENTS.md templates
- curated Codex rules templates
- learning/export hooks
- maintenance scripts
- plugin and marketplace manifests

It intentionally excludes authentication files, tokens, cookies, private keys, and raw credential output.

## Install On Other Machines

For the full cross-machine installation and usage guide, see the repository-level `docs/install-on-other-machines.md`.

## Install

From any shell:

```bash
codex plugin marketplace add "$HOME/marketplace-zxgc"
```

Upgrade after edits:

```bash
codex plugin marketplace upgrade marketplace-zxgc
```

## Validate

```bash
"$HOME/marketplace-zxgc/plugins/marketplace-zxgc/scripts/validate-pack.sh"
```

## Sync Packaged Skills

Dry run:

```bash
"$HOME/marketplace-zxgc/plugins/marketplace-zxgc/scripts/sync-skills.sh" --dry-run
```

Apply:

```bash
"$HOME/marketplace-zxgc/plugins/marketplace-zxgc/scripts/sync-skills.sh" --apply
```

`code-refactor` is included in the default sync set with its `commands/` references so each subcommand can load the required procedure file.

The algorithm engineering skill set is included in the default sync set:

- `algorithm-engineer-workflow`
- `algorithm-data-diagnosis`
- `algorithm-tensorboard-analysis`
- `algorithm-training-debug`
- `algorithm-training-review`
- `algorithm-rl-debug`
- `algorithm-eval-diagnosis`
- `algorithm-eval-closure`
- `algorithm-agent-trace-analysis`

`task2zxgc` is intentionally excluded from the default sync set so the marketplace copy remains the only maintained copy.

Existing skills are backed up under `$CODEX_HOME/backups/skills/<timestamp>/` before replacement. Backups are intentionally kept outside `$CODEX_HOME/skills` so old skill copies are not rediscovered as active skills.

Limit skills:

```bash
ZXGC_SKILLS="marketplace-zxgc session-self-improvement" \
  "$HOME/marketplace-zxgc/plugins/marketplace-zxgc/scripts/sync-skills.sh" --apply
```

## Install AGENTS.md Template

Preview:

```bash
"$HOME/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-agents-md.sh" --mode replace
```

Apply with backup:

```bash
"$HOME/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-agents-md.sh" --mode replace --yes
```

## Install Hooks

Dry run:

```bash
"$HOME/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-hooks.sh" --dry-run
```

Apply with backup:

```bash
"$HOME/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-hooks.sh" --apply
```

## Install Rules Template

The packaged rules template is curated and secret-free. It is not a raw mirror of local runtime rules.
Only portable user-level rules belong here. Absolute-path or repository-specific entries should be converted into reusable guidance or handled by target-local install scripts.

Dry run:

```bash
"$HOME/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-rules.sh" --dry-run
```

Apply with backup:

```bash
"$HOME/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-rules.sh" --apply
```
