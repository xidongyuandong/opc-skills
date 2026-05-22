# marketplace-zxgc

ZXGC local Codex marketplace.

This repository packages personal/user-level Codex assets as a marketplace:

- `plugins/marketplace-zxgc/skills/`: selected custom skills
- `plugins/marketplace-zxgc/templates/`: AGENTS.md, rules, and configuration templates
- `plugins/marketplace-zxgc/hooks/`: hook scripts
- `plugins/marketplace-zxgc/scripts/`: install, sync, and validation scripts
- `.agents/plugins/marketplace.json`: marketplace catalog

It is intentionally local-first. Do not add auth files, tokens, cookies, private keys, or raw credential output.

## Install On Other Machines

For a step-by-step guide covering clone, validation, marketplace registration, skills sync, AGENTS.md, rules, hooks, verification, upgrade, and rollback, see [docs/install-on-other-machines.md](docs/install-on-other-machines.md).

## Register With Codex

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

## Push Updates

The repository remote is:

```bash
https://gitlab.chehejia.com/zhengyuyu/marketplace-zxgc.git
```

Push local marketplace changes after validation:

```bash
"$HOME/marketplace-zxgc/scripts/push-marketplace.sh"
```

The push script discovers the repository root from its own path. For GitLab authentication, use one of:

- Export `GITLAB_PERSONAL_ACCESS_TOKEN` or `GITLAB_TOKEN` in the shell.
- Point `MARKETPLACE_ZXGC_ENV_FILE` to a local env file containing one of those variables.
- Store a local env file at `$HOME/.config/marketplace-zxgc/env` or `$HOME/.marketplace-zxgc.env`.
- Configure Git's credential helper for the GitLab remote.

Do not commit local env files, tokens, cookies, private keys, or raw credential output.

## Safe Install Actions

Preview skill sync:

```bash
"$HOME/marketplace-zxgc/plugins/marketplace-zxgc/scripts/sync-skills.sh" --dry-run
```

Preview AGENTS.md install:

```bash
"$HOME/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-agents-md.sh" --mode replace
```

Preview hooks install:

```bash
"$HOME/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-hooks.sh" --dry-run
```

Preview rules install:

```bash
"$HOME/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-rules.sh" --dry-run
```

Rules templates are curated for portable user-level behavior. Local absolute paths and repository-specific commands should stay in local configuration or be expressed as reusable guidance before packaging.

## Included Skills

The initial pack includes:

- `marketplace-zxgc`
- `session-self-improvement`
- `self-improving-agent`
- `continuous-learning-v2`
- `codex-hooks`
- `codex-hook`
- `codex-remote-container`
- `codex-ssh-remote-config`
- `algorithm-engineer-workflow`
- `algorithm-data-diagnosis`
- `algorithm-tensorboard-analysis`
- `algorithm-training-debug`
- `algorithm-training-review`
- `algorithm-rl-debug`
- `algorithm-eval-diagnosis`
- `algorithm-eval-closure`
- `algorithm-agent-trace-analysis`
- `task2zxgc`

`task2zxgc` is kept marketplace-local as the single source of truth. It is not synced into `~/.codex/skills` by default.
