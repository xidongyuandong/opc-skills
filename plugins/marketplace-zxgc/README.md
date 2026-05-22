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
codex plugin marketplace add /Users/zhengyuyu/marketplace-zxgc
```

Upgrade after edits:

```bash
codex plugin marketplace upgrade marketplace-zxgc
```

## Validate

```bash
/Users/zhengyuyu/marketplace-zxgc/plugins/marketplace-zxgc/scripts/validate-pack.sh
```

## Sync Packaged Skills

Dry run:

```bash
/Users/zhengyuyu/marketplace-zxgc/plugins/marketplace-zxgc/scripts/sync-skills.sh --dry-run
```

Apply:

```bash
/Users/zhengyuyu/marketplace-zxgc/plugins/marketplace-zxgc/scripts/sync-skills.sh --apply
```

`code-refactor` is included in the default sync set with its `commands/` references so each subcommand can load the required procedure file.

`task2zxgc` is intentionally excluded from the default sync set so the marketplace copy remains the only maintained copy.

Limit skills:

```bash
ZXGC_SKILLS="marketplace-zxgc session-self-improvement" \
  /Users/zhengyuyu/marketplace-zxgc/plugins/marketplace-zxgc/scripts/sync-skills.sh --apply
```

## Install AGENTS.md Template

Preview:

```bash
/Users/zhengyuyu/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-agents-md.sh --mode replace
```

Apply with backup:

```bash
/Users/zhengyuyu/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-agents-md.sh --mode replace --yes
```

## Install Hooks

Dry run:

```bash
/Users/zhengyuyu/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-hooks.sh --dry-run
```

Apply with backup:

```bash
/Users/zhengyuyu/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-hooks.sh --apply
```

## Install Rules Template

The packaged rules template is curated and secret-free. It is not a raw mirror of local runtime rules.
Only portable user-level rules belong here. Absolute-path or repository-specific entries should be converted into reusable guidance or handled by target-local install scripts.

Dry run:

```bash
/Users/zhengyuyu/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-rules.sh --dry-run
```

Apply with backup:

```bash
/Users/zhengyuyu/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-rules.sh --apply
```
