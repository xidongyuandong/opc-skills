# opc-skills

Local Codex marketplace for OPC workflows.

This marketplace packages selected OPC user-level Codex assets:

- custom skills
- AGENTS.md templates
- curated Codex rules templates
- learning/export hooks
- maintenance scripts
- plugin and marketplace manifests

It intentionally excludes authentication files, tokens, cookies, private keys, and raw credential output.

## Legacy Runtime Names

The public marketplace name is `opc-skills`. The current plugin directory, several scripts, and environment variables still use `marketplace-zxgc` / `ZXGC` as legacy runtime identifiers. Keep those names unless a separate compatibility migration is planned.

## Optional MCP: agentMemory

`agent-memory-mcp` is packaged with its Codex-adapted MCP server source under `tools/agentMemory`. It is not part of default skill sync because enabling MCP modifies the target `config.toml` and should be explicit per machine.

Install on a target machine:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}" \
AGENT_MEMORY_PROJECT_ID="${AGENT_MEMORY_PROJECT_ID:-$(whoami)-agent-memory}" \
AGENT_MEMORY_WORKSPACE="${AGENT_MEMORY_WORKSPACE:-$HOME}" \
"$MARKETPLACE_ZXGC_HOME/plugins/marketplace-zxgc/scripts/install-agent-memory-mcp.sh" --apply
```

c250:

```bash
CODEX_HOME=/data/jenkins/.codex/home \
AGENT_MEMORY_PROJECT_ID=c250-jenkins-home \
AGENT_MEMORY_WORKSPACE=/data/jenkins \
/data/jenkins/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-agent-memory-mcp.sh --apply
```

## Install On Other Machines

For the full cross-machine installation and usage guide, see the repository-level `docs/install-on-other-machines.md`.

For repository maintainers, see the repository-level marketplace docs:

- `docs/marketplace-architecture.md`: marketplace logic map and ownership boundaries.
- `docs/skills-catalog.md`: packaged skills, purposes, and default-sync policy.
- `docs/marketplace-standards-gap.md`: public marketplace standards comparison and open publication gates.

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

The marketplace also packages a portable core workflow chain:

- `requirement-to-plan`: evidence-first planning with a one-time confirmation gate.
- `code-exec`: confirmed implementation, testing, review, and evidence closeout.
- `self-improvement-session`: factual retrospectives plus confirmation-gated behavior improvement candidates.

These skills are packaged as generic, machine-independent derivatives. Packaging does not imply default activation; default sync remains controlled by the sync script when that script is present in the installed marketplace version.

The self-improvement skill set is included in the default sync set:

- `session-self-improvement`
- `session-self-improvement-eval`
- `twin-agent-zyy`

These skills use `$CODEX_HOME` for durable twin-agent artifacts and fall back to bundled `twin-agent-zyy/references/` files when `$CODEX_HOME/twin-agent-zyy/` has not been created on a target machine.

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

`kg-code` is packaged for multi-repository code graph create/query work. It is intentionally excluded from the default sync set; install it explicitly with `ZXGC_SKILLS="kg-code" .../sync-skills.sh --apply` or `c250-sync-codex --skills kg-code`. Its `ensure-skills` helper can auto-install missing dependent skills from local sources; `c250` is packaged only to support that opt-in dependency path.

`task2zxgc` is intentionally excluded from the default sync set so the marketplace copy remains the only maintained copy.

`agent-memory-mcp` is also excluded from the default sync set. Use `install-agent-memory-mcp.sh` so the skill, MCP server source, dependencies, and target-local `config.toml` block are installed together.

## Application: task2zxgc

`task2zxgc` turns the current Codex session into a structured task report and pushes it to a configured report Git repository.

Default target:

```text
https://gitlab.chehejia.com/ep/ai/ai-coding-zxgc-managment.git
```

Default GitLab URL pattern after push:

```text
https://gitlab.chehejia.com/ep/ai/ai-coding-zxgc-managment/-/blob/master/{username}/{YYYY-MM-DD-HH}-{task-title}.md
```

Use local environment variables for team machines:

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

Existing skills are backed up under `$CODEX_HOME/backups/skills/<timestamp>/` before replacement. Backups are intentionally kept outside `$CODEX_HOME/skills` so old skill copies are not rediscovered as active skills.
Known deprecated skill stubs, such as `auto-merge-request.moved-to-code-refactor.20260521`, are also moved into the same backup area during sync.

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
