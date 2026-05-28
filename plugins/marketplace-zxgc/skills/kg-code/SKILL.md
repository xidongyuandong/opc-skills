---
name: kg-code
description: Use when a task needs multi-repository code knowledge graphs, code-review-graph MCP/CLI, cross-repo architecture lookup, impact analysis, c250 graph checks, or the user mentions index-code-graph.md, code graph, code knowledge graph, or 多仓代码图谱.
---

# kg-code

Use this skill to make codebase exploration start from the durable multi-repo graph and index instead of ad hoc file scans.

## Entry Points

- Top index: `$CODEX_HOME/memories/index-code-graph.md` (use `~/.codex/memories/index-code-graph.md` if `CODEX_HOME` is unset)
- Command helper: `$CODEX_HOME/skills/kg-code/scripts/kg_code.py`
- Regression eval helper: `$CODEX_HOME/skills/kg-code/scripts/kg_code_eval.py`
- Local graph CLI: `code-review-graph`
- Local MCP server: `code-review-graph`
- c250 remote wrapper: `c250-exec`, with common repo `/home/chehejia/cov-evalution`
- LPAI dev paths, accessed with `ssh lpai-zyy-dev`:
  - `/lpai/code/rllm`
  - `/lpai/code/code-complete`
- Supplemental graph tools named by the user:
  - `code-review-graph`: primary installed CLI/MCP for structural code graphs.
  - `graphify`: installed at `/Users/zhengyuyu/.local/bin/graphify`; broad local graph for code, Markdown, docs, shell, SQL, config, and media sidecars.
  - `GitNexus`: installed at `/opt/homebrew/bin/gitnexus`; alternate local CLI/MCP graph with flows, FTS, clusters, and impact/query commands.
  - `Understand-Anything`: plugin-style graph format. In Codex, use existing `.understand-anything/knowledge-graph.json` artifacts; if the full `/understand` plugin command is unavailable, use the kg-code compatibility graph generated from `graphify-out/graph.json`.

## Workflow

`kg-code` exposes two user-facing operations:

- `create`: build or refresh code graph artifacts.
- `query`: answer from existing code graph artifacts and document layers.

Use the helper directly when the user asks for one of these operations:

```bash
python3 "$CODEX_HOME/skills/kg-code/scripts/kg_code.py" create --repo rllm --tools code-review-graph,graphify,understand-compatible
python3 "$CODEX_HOME/skills/kg-code/scripts/kg_code.py" query --repo rllm "APR SFT training shell" --limit 10
python3 "$CODEX_HOME/skills/kg-code/scripts/kg_code_eval.py"
```

1. Read `index-code-graph.md` first when the task may span `rllm`, `code-complete`, c250, or AI coding workspace infrastructure.
2. Check the nearest `AGENTS.md` before acting inside a repo. For `rllm`, use code-review-graph MCP before grep-style exploration when the graph covers the question.
3. Prefer graph queries for architecture, impact, code review, and entity lookup:
   - `list_graph_stats` for graph freshness and scale.
   - `get_architecture_overview` for module/community structure.
   - `get_review_context` for changed files.
   - `cross_repo_search` for registered local repos.
4. Treat Markdown and durable docs as a parallel document layer, not as failed code graph coverage. Use `rg --files -g '*.md'`, `rg -n`, and direct reads to connect docs to code graph nodes.
5. Fall back to `rg`, `find`, and direct file reads when graph data is missing, stale, too broad, or the target is a document/config file.
6. For c250, use `c250-exec` rather than direct Docker commands. Do not print credentials or auth files.

## Build And Query Modes

- `create` parameter:
  - Purpose: build code graph indexes.
  - Local implementation: runs `code-review-graph update || build`, optionally `graphify update`, optionally GitNexus, and refreshes `.understand-anything/knowledge-graph.json` from `graphify-out/graph.json`.
  - Example: `python3 "$CODEX_HOME/skills/kg-code/scripts/kg_code.py" create --repo /path/to/repo --alias my-repo`.
  - c250/lpai-dev: use the documented remote shell templates when the helper is not physically available in that environment.
- `query` parameter:
  - Purpose: query code graph indexes.
  - Local implementation: searches `.code-review-graph/graph.db`, `graphify-out/graph.json` or `.understand-anything/knowledge-graph.json`, then Markdown/shell/Python/config files as fallback.
  - Remote aliases: `cov-evalution`, `cov-evalution-qwen3_6`, `code-complete-c250`, `rllm-lpai-dev`, and `code-complete-lpai-dev` route through `c250-exec` or `ssh lpai-zyy-dev` and combine remote file/doc scans with GitNexus query output.
  - Example: `python3 "$CODEX_HOME/skills/kg-code/scripts/kg_code.py" query --repo rllm "train_smolagents_prod" --json`.
- Structural build: `code-review-graph build/update/status` for Python, shell, Rust, and other source files.
- MCP query: `list_graph_stats`, `get_architecture_overview`, `get_review_context`, and `cross_repo_search`.
- SQLite/file exact query: inspect `.code-review-graph/graph.db` or test exact paths when a file-level answer is required.
- Document index query: search Markdown and adjacent docs first, then follow their referenced paths into code graph or c250.
- Remote query: run the same status/search/file checks through `c250-exec -C <repo>`.
- Graphify query: use `graphify query/path/explain/affected --graph <repo>/graphify-out/graph.json` when Markdown/config/shell relationships matter.
- GitNexus query: use `gitnexus query/context/impact/cypher` for local indexed repos when flows, FTS, clusters, or alternate MCP context may improve recall.
- Understand-Anything-compatible query: use `jq` against `<repo>/.understand-anything/knowledge-graph.json` for node/edge/layer lookup, or use the Understand-Anything dashboard/chat skills in environments where those plugin commands are available.

## Multi-Tool Build Logic

For local target repos, refresh all available graph layers:

```bash
code-review-graph update --repo /Users/zhengyuyu/programs/lixiang/rllm
code-review-graph build --repo /Users/zhengyuyu/programs/lixiang/code-complete
graphify update /Users/zhengyuyu/programs/lixiang/rllm
graphify update /Users/zhengyuyu/programs/lixiang/code-complete
graphify update /Users/zhengyuyu/programs/lixiang/agent_create_code/output/开发模式/team-workspace
GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 gitnexus analyze --index-only --drop-embeddings --name rllm /Users/zhengyuyu/programs/lixiang/rllm
GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 gitnexus analyze --index-only --drop-embeddings --name code-complete /Users/zhengyuyu/programs/lixiang/code-complete
GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 gitnexus analyze --index-only --drop-embeddings --name team-workspace /Users/zhengyuyu/programs/lixiang/agent_create_code/output/开发模式/team-workspace
```

For c250 target repos:

```bash
c250-exec -C /home/chehejia/cov-evalution 'code-review-graph update --repo /home/chehejia/cov-evalution || code-review-graph build --repo /home/chehejia/cov-evalution'
c250-exec -C /home/chehejia/cov-evalution-qwen3_6-eval-0521 'code-review-graph update --repo /home/chehejia/cov-evalution-qwen3_6-eval-0521 || code-review-graph build --repo /home/chehejia/cov-evalution-qwen3_6-eval-0521'
c250-exec -C /home/chehejia/code-complete 'code-review-graph update --repo /home/chehejia/code-complete || code-review-graph build --repo /home/chehejia/code-complete'
c250-exec -C /home/chehejia/cov-evalution 'command -v graphify || uv tool install graphifyy; graphify update /home/chehejia/cov-evalution'
c250-exec -C /home/chehejia/cov-evalution-qwen3_6-eval-0521 'command -v graphify || uv tool install graphifyy; graphify update /home/chehejia/cov-evalution-qwen3_6-eval-0521'
c250-exec -C /home/chehejia/code-complete 'command -v graphify || uv tool install graphifyy; graphify update /home/chehejia/code-complete'
c250-exec -C /home/chehejia/cov-evalution 'gitnexus analyze --index-only --name cov-evalution /home/chehejia/cov-evalution'
c250-exec -C /home/chehejia/cov-evalution-qwen3_6-eval-0521 'gitnexus analyze --index-only --name cov-evalution-qwen3_6 /home/chehejia/cov-evalution-qwen3_6-eval-0521'
c250-exec -C /home/chehejia/code-complete 'gitnexus analyze --index-only --name code-complete-c250 /home/chehejia/code-complete'
```

For lpai-dev target repos, run through SSH and keep artifacts inside each repo:

```bash
ssh lpai-zyy-dev 'export PATH=/root/.local/bin:$PATH; code-review-graph build --repo /lpai/code/rllm; code-review-graph build --repo /lpai/code/code-complete'
ssh lpai-zyy-dev 'export PATH=/root/.local/bin:$PATH; graphify update /lpai/code/rllm; graphify update /lpai/code/code-complete'
ssh lpai-zyy-dev 'gitnexus analyze --index-only --name rllm-lpai-dev /lpai/code/rllm; gitnexus analyze --index-only --name code-complete-lpai-dev /lpai/code/code-complete'
```

After `graphify update`, create or refresh the Understand-Anything-compatible graph from `graphify-out/graph.json` when the real `/understand` plugin command is not available in Codex. The compatible output paths are:

```text
<repo>/.understand-anything/knowledge-graph.json
<repo>/.understand-anything/meta.json
```

lpai-dev graph tool installation should prefer isolated tool environments. If `uv` is available, use company indexes in the same style as code-complete. If only pip is available, keep it outside project virtualenvs and record dependency risks:

```bash
ssh lpai-zyy-dev 'python3 -m pip install --user -i https://artifactory.ep.chehejia.com/artifactory/api/pypi/liauto-pypi-l5/simple code-review-graph==2.3.1 graphifyy'
```

Do not add `/lpai/code/cov-evalution`, `/lpai/code/tmp/code-complete`, or `/lpai/code/cov-evalution-qwen3_6-eval-0521` as lpai-dev targets unless the requirement file is updated again. Those paths are not part of the current `远端lpai-zyy-dev` scope.

c250 GitNexus coverage is available through the user-level wrapper at `/home/chehejia/.local/bin/gitnexus`. It uses Node `v22.22.3` and Linuxbrew glibc/libstdc++ to satisfy GitNexus native dependencies on the older Ubuntu/glibc runtime. FTS extension install is disabled on c250, so use GitNexus there for graph/flow/context/impact coverage, not FTS completeness.

## Markdown Document Layer

Markdown is first-class context for `kg-code` because it captures architecture, runbooks, task records, eval reports, and repository summaries that AST graphs usually do not cover.

Use this default scan shape:

```bash
rg --files /Users/zhengyuyu/programs/lixiang/rllm \
  /Users/zhengyuyu/programs/lixiang/code-complete \
  /Users/zhengyuyu/programs/lixiang/agent_create_code \
  -g '*.md'
rg -n "<keyword>" <repo> --glob '*.md' --glob '*.sh' --glob '*.py'
c250-exec -C /home/chehejia/cov-evalution 'find . -name "*.md" -o -name "*.sh"'
```

Route document hits by layer:

- User-level cross-repo knowledge: `$CODEX_HOME/memories/index-code-graph.md`.
- Requirement phase state: `{requirement}.plan.md`, `{requirement}.research.md`, `{requirement}.task.md`.
- Repo-level durable understanding: `<repo>/docs/总结/*.md`.
- c250 eval/runbook documents: `/home/chehejia/cov-evalution/**/docs`, `/home/chehejia/cov-evalution-qwen3_6-eval-0521/docs`, and `parallel_eval_monitor/*.md`.

## Maintenance Commands

Local registry:

```bash
code-review-graph repos
code-review-graph register /Users/zhengyuyu/programs/lixiang/rllm --alias rllm
code-review-graph register /Users/zhengyuyu/programs/lixiang/code-complete --alias code-complete
```

Local graph refresh:

```bash
code-review-graph update --repo /Users/zhengyuyu/programs/lixiang/rllm
code-review-graph build --repo /Users/zhengyuyu/programs/lixiang/code-complete
```

c250 graph check:

```bash
c250-exec -C /home/chehejia/cov-evalution 'code-review-graph status --repo /home/chehejia/cov-evalution'
c250-exec -C /home/chehejia/cov-evalution-qwen3_6-eval-0521 'find agent/shells docs -maxdepth 3 -type f | sort | head'
c250-exec -C /home/chehejia/code-complete 'code-review-graph status --repo /home/chehejia/code-complete'
c250-exec -C /home/chehejia/cov-evalution 'jq -r "\"graphify nodes=\\(.nodes|length) links=\\(.links|length)\"" graphify-out/graph.json'
c250-exec -C /home/chehejia/cov-evalution 'jq -r "\"understand nodes=\\(.nodes|length) edges=\\(.edges|length)\"" .understand-anything/knowledge-graph.json'
```

## Output Rules

- Store durable cross-repo architecture knowledge in `$CODEX_HOME/memories/index-code-graph.md` or a focused sibling memory file. Keep repo-specific knowledge in that repo's `docs/总结/`.
- Keep transient command logs out of durable docs; record only command names, key results, dates, and residual risks.
- Do not promote repo-specific rules into user-level AGENTS unless the user explicitly asks.
