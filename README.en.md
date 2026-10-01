# opc-skills

[简体中文](README.md) | **English**

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

The legacy full installation guide and automatic installer are not included in this
public snapshot. For current installation options, use the [plugin README](plugins/marketplace-zxgc/README.md),
the [multi-agent setup guide](docs/multi-agent-setup.md), or the static-IP instructions below.
These are separate entry points, not replacements for an unavailable automatic installer.
The [skills catalog](docs/skills-catalog.md) separates packaged skills from historical names.

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


Repository documentation checks (no credentials or network needed):

```bash
python3 scripts/check-doc-links.py
python3 -m unittest discover -s tests -v
```

This checks Markdown file targets and README/catalog skill inventories, including both
README languages. It does not check external websites or heading fragments. The same
check runs in the independent `Documentation integrity` CI job and before other pack checks.

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

Available skills and historical entries are separated using the current repository files. After installation and discovery by your client, reference a skill name and supply the listed inputs; consult its SKILL.md for exact parameters. Each description, excluding its name, is at most 100 characters.

### Skills included in the current repository

| Skill | Function, value and usage |
|---|---|
| [engineer-router](plugins/marketplace-zxgc/skills/engineer-router/SKILL.md) | Bind project scope for safer handoffs; provide a task, project ID and workspace. |
| [requirement-to-plan](plugins/marketplace-zxgc/skills/requirement-to-plan/SKILL.md) | Turn requirements into a verifiable plan; provide a goal or spec to compare options. |
| [code-exec](plugins/marketplace-zxgc/skills/code-exec/SKILL.md) | Implement and verify approved scope; provide the confirmed plan and execution approval. |
| [multi-agent-orchestrator](plugins/marketplace-zxgc/skills/multi-agent-orchestrator/SKILL.md) | Coordinate dependencies and retries; provide workflow and context to compute ready waves. |
| [self-improvement-session](plugins/marketplace-zxgc/skills/self-improvement-session/SKILL.md) | Learn from outcomes or corrections; provide evidence, then approve behavior changes separately. |
| [marketplace-zxgc](plugins/marketplace-zxgc/skills/marketplace-zxgc/SKILL.md) | Maintain pack consistency; request updates, sync or validation from the cloned repository. |
| [clash-verge-add-static-ip](plugins/marketplace-zxgc/skills/clash-verge-add-static-ip/SKILL.md) | Self-contained static-IP workflow; check installation first, then provide profile and proxy details. No sibling skill needed. |

### Historical entries (not shipped in the current repository)

These names come from the original README and their descriptions from the historical catalog. Their published directories are absent: they cannot be installed from this repository and their runtime behavior is unverified. Obtain a matching implementation first.

| Skill | Function, value and usage |
|---|---|
| `session-self-improvement` | Review learning targets; obtain the skill, then provide session evidence or an improvement idea. |
| `session-self-improvement-eval` | Find retrospective gaps; obtain the skill, then provide outputs and acceptance criteria. |
| `twin-agent-zyy` | Maintain persona goals and decisions; obtain and adapt the skill, then provide goals and history. |
| `continuous-agent-loop` | Recover long-running work; obtain the skill, then provide goals, stop conditions and state. |
| `enterprise-agent-ops` | Operate persistent agents; obtain the skill, then provide environment, metrics and operating goals. |
| `self-improving-agent` | Support legacy learning calls; obtain the skill, then route work to session-self-improvement. |
| `continuous-learning-v2` | Extract learning candidates; obtain the skill, then provide session evidence and project scope. |
| `codex-hooks` | Manage hook workflows; obtain the skill, then provide events, config and intended actions. |
| `codex-hook` | Fix one hook; obtain the skill, then provide its script, config and error details. |
| `codex-remote-container` | Set up Codex containers; obtain the skill, then provide connection and container configuration. |
| `codex-ssh-remote-config` | Set up remote Codex; obtain the skill, then provide host, directories and login state. |
| `c250` | Operate a designated container; obtain and adapt the skill, then provide the intended operation. |
| `algorithm-engineer-workflow` | Coordinate ML diagnosis; obtain the skill, then provide model goals, code and experiment records. |
| `algorithm-data-diagnosis` | Diagnose data defects; obtain the skill, then provide samples, schema and observed issues. |
| `algorithm-tensorboard-analysis` | Analyze training curves; obtain the skill, then provide TensorBoard events and experiment context. |
| `algorithm-training-debug` | Debug training; obtain the skill, then provide scripts, config, logs and reproduction steps. |
| `algorithm-training-review` | Review training quality; obtain the skill, then provide experiment artifacts and goals. |
| `algorithm-rl-debug` | Diagnose RL issues; obtain the skill, then provide algorithm config, rollouts and training logs. |
| `algorithm-eval-diagnosis` | Diagnose eval regressions; obtain the skill, then provide cases, scoring and before/after data. |
| `algorithm-eval-closure` | Close evaluation gaps; obtain the skill, then provide logs, verification results and open issues. |
| `algorithm-agent-trace-analysis` | Diagnose agent traces; obtain the skill, then provide sanitized tool logs and failure examples. |
| `kg-code` | Map code relationships; obtain the skill, then provide repositories to index or a query. |
| `agent-memory-mcp` | Persist searchable memory; obtain the skill and server, then configure the target MCP connection. |
| `task2zxgc` | Export traceable reports; obtain the skill, preview sanitized output, then push with approval. |

The generic planning, execution, and retrospective chain is packaged as:

1. `requirement-to-plan`: turn ambiguous or document-driven work into one confirmation-gated Plan/Todo.
2. `code-exec`: execute a previously confirmed Plan/Todo through scoped implementation, verification, and evidence closeout.
3. `self-improvement-session`: archive factual learning and draft behavior-impact improvements without silently changing rules, skills, roles, memory, or knowledge bases.

These three skills are portable derivatives. They intentionally exclude machine-specific absolute paths, private repository references, organization-specific workflows, and domain-specific examples.

The following describes historical packaging and sync design; it does not establish that these skills or installers exist on the current branch.

`task2zxgc` is kept marketplace-local as the single source of truth. It is not synced into `~/.codex/skills` by default.
`kg-code` is packaged for multi-repository code graph create/query work and is synced explicitly when needed, not by default. Its helper can auto-install missing dependent skills from this marketplace pack; `c250` is packaged to support that opt-in dependency path and is not part of the default sync set.
`agent-memory-mcp` is packaged with its MCP server source but is opt-in because installation writes a target-local `config.toml` MCP block. Use `plugins/marketplace-zxgc/scripts/install-agent-memory-mcp.sh` on each target machine.

Skill sync backs up replaced skills under `$CODEX_HOME/backups/skills/<timestamp>/` and also moves known deprecated skill stubs out of the active skills directory.

## Clash Verge Static-IP Subscriptions

`clash-verge-add-static-ip` first checks for Clash Verge. If missing, follow official
installation and recheck; if uncertain, ask for the custom application path. Then collect
the profile path, proxy protocol, endpoint, authentication and region to create a separate
region-named subscription. Remote profiles use a dedicated sidecar; Local profiles are snapshots.
GUI registration, runtime selection and live exit identity remain separate checks.

Install this single self-contained directory (fresh installation only):

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R plugins/marketplace-zxgc/skills/clash-verge-add-static-ip "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Back up an existing destination before updating. Builders, templates and tests are bundled;
no sibling skill is required. Python 3.9+ runs the read-only probe, Ruby runs builders,
and Node.js runs composition and regression tests. Default sync settings are unchanged.
Previous users should follow the [migration guide](plugins/marketplace-zxgc/skills/clash-verge-add-static-ip/references/migration.md):
back up, verify the new directory alone, update callers, and only then decide whether to remove the old copy.

Example: “Use `$clash-verge-add-static-ip` with my profile path and private proxy reference.
Create a Singapore subscription without switching my current connection.”

Offline verification from the repository root:

```bash
python3 -m unittest discover -s plugins/marketplace-zxgc/skills/clash-verge-add-static-ip/tests -v
```

Tests cover an isolated copy and synthetic installation states. They do not prove real
installation, application launch, GUI registration, supplier access or public exit identity.
The probe never executes discovered binaries; file evidence is not publisher verification.
Refresh-time name collisions still require checking the downloaded source. Never publish
real profiles, credentials, subscription URLs or private sidecars.

## Application: task2zxgc

`task2zxgc` exports the current Codex session into a structured task report and pushes it to the configured report repository. Reports include an independent original-user-input section (`用户原始输入`) for sanitized excerpts of requirement files, command-line prompts, and user chat messages, so reviewers can evaluate whether the user provided effective task context.

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

The legacy team-installation/posthook guide and `task2zxgc` implementation are not included in this snapshot. This section describes historical behavior, not an installable application; see the [current catalog](docs/skills-catalog.md) for available skills.

## Multi-agent collaboration pack

Use `engineer-router` to bind explicit task context, `requirement-to-plan` to produce stable task decomposition, `code-exec` to execute within scope, and `multi-agent-orchestrator` to manage dependency waves and acceptance. Configure model IDs actually supported by your current tool.

See [installation, limitations and a read-only dry run](docs/multi-agent-setup.md). This optional pack does not change the default sync set. Its Markdown guidance and outputs default to Simplified Chinese; necessary terms, fields, commands and links may remain in English. This English README is an explicit navigation alternative.
