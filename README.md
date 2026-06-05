# opc-skills

OPC local Codex marketplace.

This repository packages OPC personal/user-level Codex assets as a marketplace:

- `plugins/marketplace-zxgc/skills/`: selected custom skills
- `plugins/marketplace-zxgc/templates/`: AGENTS.md, rules, and configuration templates
- `plugins/marketplace-zxgc/hooks/`: hook scripts
- `plugins/marketplace-zxgc/scripts/`: install, sync, and validation scripts
- `.agents/plugins/marketplace.json`: marketplace catalog

It is intentionally local-first. Do not add auth files, tokens, cookies, private keys, or raw credential output.

## Legacy Runtime Names

This public repository is published as `opc-skills`. Some runtime identifiers are intentionally still legacy-compatible:

- local source directory examples may still use `marketplace-zxgc`;
- plugin and skill paths may still use `plugins/marketplace-zxgc`;
- environment variables such as `MARKETPLACE_ZXGC_HOME` and `ZXGC_SKILLS` remain supported;
- the `task2zxgc` application name remains unchanged for compatibility.

Do not rename those runtime identifiers without a separate migration plan.

## Install On Other Machines

For a step-by-step guide covering clone, validation, marketplace registration, skills sync, AGENTS.md, rules, hooks, verification, upgrade, and rollback, see [docs/install-on-other-machines.md](docs/install-on-other-machines.md).

For the current Chinese automated installation guide, use [操作指导.md](操作指导.md). The recommended team entrypoint is:

```bash
"$MARKETPLACE_ZXGC_HOME/scripts/install-marketplace-zxgc.sh" --dry-run
"$MARKETPLACE_ZXGC_HOME/scripts/install-marketplace-zxgc.sh" --apply
```

For a Chinese overview of packaged skills and when to use them, see [技能介绍.md](技能介绍.md).

For maintainers and agents that need to inspect this marketplace quickly:

- [docs/marketplace-architecture.md](docs/marketplace-architecture.md) maps manifests, skills, scripts, templates, hooks, tools, validation, and sync flows.
- [docs/skills-catalog.md](docs/skills-catalog.md) lists every packaged skill, its purpose, and whether it is default-synced or opt-in.
- [docs/marketplace-standards-gap.md](docs/marketplace-standards-gap.md) compares this local marketplace with public skills marketplace patterns and records remaining publication gaps.

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

## Submit Updates

The legacy internal repository remote is:

```bash
https://gitlab.chehejia.com/zhengyuyu/marketplace-zxgc.git
```

Submit local marketplace changes after validation, branch creation, commit, push, and GitLab issue/MR creation:

```bash
"$HOME/marketplace-zxgc/scripts/auto-submit-marketplace-change.sh" --dry-run --title "update marketplace"
"$HOME/marketplace-zxgc/scripts/auto-submit-marketplace-change.sh" --apply --title "update marketplace"
```

The script discovers the repository root from its own path, infers a content-based branch, and uses the packaged `code-refactor` auto-merge-request helper. For GitLab authentication, use one of:

- Export `GITLAB_PERSONAL_ACCESS_TOKEN` or `GITLAB_TOKEN` in the shell.
- Point `MARKETPLACE_ZXGC_ENV_FILE` to a local env file containing one of those variables.
- Store a local env file at `$HOME/.config/marketplace-zxgc/env` or `$HOME/.marketplace-zxgc.env`.
- Configure Git's credential helper for the GitLab remote.

Do not commit local env files, tokens, cookies, private keys, or raw credential output.

For a simple fallback that only commits and pushes the current branch, use:

```bash
"$HOME/marketplace-zxgc/scripts/push-marketplace.sh"
```

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
- `session-self-improvement-eval`
- `twin-agent-zyy`
- `continuous-agent-loop`
- `enterprise-agent-ops`
- `self-improving-agent`
- `continuous-learning-v2`
- `codex-hooks`
- `codex-hook`
- `codex-remote-container`
- `codex-ssh-remote-config`
- `c250`
- `algorithm-engineer-workflow`
- `algorithm-data-diagnosis`
- `algorithm-tensorboard-analysis`
- `algorithm-training-debug`
- `algorithm-training-review`
- `algorithm-rl-debug`
- `algorithm-eval-diagnosis`
- `algorithm-eval-closure`
- `algorithm-agent-trace-analysis`
- `kg-code`
- `agent-memory-mcp`
- `task2zxgc`

`task2zxgc` is kept marketplace-local as the single source of truth. It is not synced into `~/.codex/skills` by default.
`kg-code` is packaged for multi-repository code graph create/query work and is synced explicitly when needed, not by default. Its helper can auto-install missing dependent skills from this marketplace pack; `c250` is packaged to support that opt-in dependency path and is not part of the default sync set.
`agent-memory-mcp` is packaged with its MCP server source but is opt-in because installation writes a target-local `config.toml` MCP block. Use `plugins/marketplace-zxgc/scripts/install-agent-memory-mcp.sh` on each target machine.

Skill sync backs up replaced skills under `$CODEX_HOME/backups/skills/<timestamp>/` and also moves known deprecated skill stubs out of the active skills directory.

## Application: task2zxgc

`task2zxgc` exports the current Codex session into a structured task report and pushes it to the configured report repository. Reports include an independent `用户原始输入` section for sanitized excerpts of requirement files, command-line prompts, and user chat messages, so reviewers can evaluate whether the user provided effective task context.

Default report repository:

```text
https://gitlab.chehejia.com/ep/ai/ai-coding-zxgc-managment.git
```

Default GitLab report URL pattern:

```text
https://gitlab.chehejia.com/ep/ai/ai-coding-zxgc-managment/-/blob/master/{username}/{YYYY-MM-DD-HH}-{task-title}.md
```

Runtime configuration is local to each machine:

```bash
export TASK2ZXGC_REPO_URL="https://gitlab.chehejia.com/ep/ai/ai-coding-zxgc-managment.git"
export TASK2ZXGC_REPO_DIR="${CODEX_HOME:-$HOME/.codex}/task2zxgc/ai-coding-zxgc-managment"
export TASK2ZXGC_USERNAME="$(git config user.name 2>/dev/null || whoami)"
```

Manual flow:

```bash
TASK2ZXGC_SCRIPT="${MARKETPLACE_ZXGC_HOME:-$HOME/marketplace-zxgc}/plugins/marketplace-zxgc/skills/task2zxgc/scripts/task2zxgc.py"
python3 "$TASK2ZXGC_SCRIPT" --dump-context > /tmp/task2zxgc-context.json
python3 "$TASK2ZXGC_SCRIPT" --dry-run --agent-summary-file /tmp/task2zxgc-summary.json
python3 "$TASK2ZXGC_SCRIPT" --push --agent-summary-file /tmp/task2zxgc-summary.json
```

See [docs/install-on-other-machines.md](docs/install-on-other-machines.md#9-task2zxgc-应用说明) for team installation, posthook usage, and credential notes.
