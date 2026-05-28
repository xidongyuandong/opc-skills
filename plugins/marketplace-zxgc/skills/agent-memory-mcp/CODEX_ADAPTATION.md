# Codex Adaptation

This skill is installed for Codex and backed by a local MCP server.

## Installed Paths

- Skill: `$CODEX_HOME/skills/agent-memory-mcp`
- MCP server source: `$CODEX_HOME/tools/agentMemory`
- Memory data root: `$AGENT_MEMORY_WORKSPACE/.agentMemory`
- Codex MCP config: `$CODEX_HOME/config.toml`

When installed from `marketplace-zxgc`, use:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}" \
AGENT_MEMORY_PROJECT_ID="${AGENT_MEMORY_PROJECT_ID:-$(whoami)-agent-memory}" \
AGENT_MEMORY_WORKSPACE="${AGENT_MEMORY_WORKSPACE:-$HOME}" \
"$MARKETPLACE_ZXGC_HOME/plugins/marketplace-zxgc/scripts/install-agent-memory-mcp.sh" --apply
```

For c250 Codex, use the remote Codex home and jenkins workspace:

```bash
CODEX_HOME=/data/jenkins/.codex/home \
AGENT_MEMORY_PROJECT_ID=c250-jenkins-home \
AGENT_MEMORY_WORKSPACE=/data/jenkins \
/data/jenkins/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-agent-memory-mcp.sh --apply
```

## Codex MCP Registration

The server is registered as `agentMemory`:

```toml
[mcp_servers.agentMemory]
command = "node"
args = ["$CODEX_HOME/tools/agentMemory/out/mcp-server/server.js", "$AGENT_MEMORY_PROJECT_ID", "$AGENT_MEMORY_WORKSPACE"]
```

Restart Codex after installation or config edits so the MCP tools are loaded.

## Available Tools

Codex should see these MCP tools after restart:

- `memory_write`
- `memory_read`
- `memory_search`
- `memory_list`
- `memory_update`
- `project_init`
- `memory_stats`

The Codex adapter injects the project id automatically. Do not ask the user for `projectId` unless they explicitly want a different memory namespace.

## Local Changes Applied

The upstream server was adapted locally for Codex:

- Supports standard MCP stdio `Content-Length` framing, while preserving newline JSON-RPC compatibility.
- Does not start the dashboard by default. Set `AGENT_MEMORY_DASHBOARD=1` if a dashboard is needed.
- Does not start the Unix socket bridge by default. Set `AGENT_MEMORY_SOCKET_BRIDGE=1` for KiloCode/RooCode-style socket clients.
- Tool schemas no longer require `projectId`; the server injects it.
