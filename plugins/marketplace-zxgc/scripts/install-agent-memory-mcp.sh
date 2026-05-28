#!/usr/bin/env bash
set -euo pipefail

MODE="dry-run"
NPM_INSTALL="auto"
SMOKE_TEST="auto"

usage() {
  cat <<'EOF'
Usage:
  scripts/install-agent-memory-mcp.sh [--dry-run|--apply] [--npm-install|--no-npm-install] [--smoke-test|--no-smoke-test]

Environment:
  CODEX_HOME                    Codex home. Defaults to $HOME/.codex.
  AGENT_MEMORY_PROJECT_ID       MCP project id. Defaults to "$(whoami)-agent-memory".
  AGENT_MEMORY_WORKSPACE        Workspace/memory root. Defaults to $HOME.
  NODE_BIN                      Node executable. Defaults to node.
  NPM_BIN                       npm executable. Defaults to npm.

This installs the packaged agentMemory MCP server and writes a target-local
Codex MCP config block. It does not copy secrets or auth files.
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)
      MODE="dry-run"
      shift
      ;;
    --apply)
      MODE="apply"
      shift
      ;;
    --npm-install)
      NPM_INSTALL="yes"
      shift
      ;;
    --no-npm-install)
      NPM_INSTALL="no"
      shift
      ;;
    --smoke-test)
      SMOKE_TEST="yes"
      shift
      ;;
    --no-smoke-test)
      SMOKE_TEST="no"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [ "$MODE" != "dry-run" ] && [ "$MODE" != "apply" ]; then
  echo "Invalid mode: $MODE" >&2
  exit 2
fi

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
NODE_BIN="${NODE_BIN:-node}"
NPM_BIN="${NPM_BIN:-npm}"
AGENT_MEMORY_PROJECT_ID="${AGENT_MEMORY_PROJECT_ID:-$(whoami)-agent-memory}"
AGENT_MEMORY_WORKSPACE="${AGENT_MEMORY_WORKSPACE:-$HOME}"

SOURCE_SKILL="$PLUGIN_ROOT/skills/agent-memory-mcp"
TARGET_SKILL="$CODEX_HOME/skills/agent-memory-mcp"
SOURCE_TOOL="$PLUGIN_ROOT/tools/agentMemory"
TARGET_TOOL="$CODEX_HOME/tools/agentMemory"
CONFIG_FILE="$CODEX_HOME/config.toml"
BACKUP_ROOT="$CODEX_HOME/backups/agent-memory-mcp/$(date +%Y%m%d%H%M%S)"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

toml_escape() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

copy_dir() {
  src="$1"
  dst="$2"
  label="$3"
  if [ ! -d "$src" ]; then
    echo "Missing packaged $label: $src" >&2
    exit 1
  fi
  if [ "$MODE" = "dry-run" ]; then
    if [ -e "$dst" ]; then
      echo "Would back up $dst -> $BACKUP_ROOT/$(basename "$dst")"
    fi
    echo "Would install $label: $src -> $dst"
    return
  fi
  mkdir -p "$(dirname "$dst")"
  if [ -e "$dst" ]; then
    mkdir -p "$BACKUP_ROOT"
    mv "$dst" "$BACKUP_ROOT/$(basename "$dst")"
  fi
  cp -R "$src" "$dst"
}

install_dependencies() {
  if [ "$NPM_INSTALL" = "no" ]; then
    return
  fi
  if [ "$MODE" = "dry-run" ]; then
    echo "Would run npm install in $TARGET_TOOL"
    return
  fi
  require_command "$NPM_BIN"
  if [ -f "$TARGET_TOOL/package-lock.json" ]; then
    (cd "$TARGET_TOOL" && "$NPM_BIN" ci)
  else
    (cd "$TARGET_TOOL" && "$NPM_BIN" install)
  fi
  if [ ! -f "$TARGET_TOOL/out/mcp-server/server.js" ] && [ -f "$TARGET_TOOL/package.json" ]; then
    (cd "$TARGET_TOOL" && "$NPM_BIN" run compile)
  fi
}

write_config() {
  server_path="$TARGET_TOOL/out/mcp-server/server.js"
  escaped_server_path="$(toml_escape "$server_path")"
  escaped_project_id="$(toml_escape "$AGENT_MEMORY_PROJECT_ID")"
  escaped_workspace="$(toml_escape "$AGENT_MEMORY_WORKSPACE")"

  if [ "$MODE" = "dry-run" ]; then
    echo "Would update $CONFIG_FILE with mcp_servers.agentMemory"
    echo "  server: $server_path"
    echo "  project: $AGENT_MEMORY_PROJECT_ID"
    echo "  workspace: $AGENT_MEMORY_WORKSPACE"
    return
  fi

  mkdir -p "$(dirname "$CONFIG_FILE")"
  tmp="$CONFIG_FILE.tmp.$$"
  if [ -f "$CONFIG_FILE" ]; then
    awk '
      /^\[mcp_servers\."agentMemory"\]/ { skip=1; next }
      /^\[mcp_servers\."agentMemory"\.tools\./ { skip=1; next }
      /^\[/ { skip=0 }
      skip == 0 { print }
    ' "$CONFIG_FILE" > "$tmp"
  else
    : > "$tmp"
  fi
  cat >> "$tmp" <<EOF

[mcp_servers."agentMemory"]
command = "node"
args = ["$escaped_server_path", "$escaped_project_id", "$escaped_workspace"]

[mcp_servers."agentMemory".tools.memory_write]
approval_mode = "approve"
EOF
  chmod 644 "$tmp"
  mv -f "$tmp" "$CONFIG_FILE"
}

run_smoke_test() {
  if [ "$SMOKE_TEST" = "no" ]; then
    return
  fi
  if [ "$MODE" = "dry-run" ]; then
    echo "Would smoke test agentMemory tools/list"
    return
  fi
  require_command "$NODE_BIN"
  if command -v timeout >/dev/null 2>&1; then
    smoke_cmd=(timeout 10 "$NODE_BIN" "$TARGET_TOOL/out/mcp-server/server.js" "$AGENT_MEMORY_PROJECT_ID" "$AGENT_MEMORY_WORKSPACE")
  else
    smoke_cmd=("$NODE_BIN" "$TARGET_TOOL/out/mcp-server/server.js" "$AGENT_MEMORY_PROJECT_ID" "$AGENT_MEMORY_WORKSPACE")
  fi
  if "${smoke_cmd[@]}" <<'EOF' | grep -q '"memory_write"'
{"jsonrpc":"2.0","id":1,"method":"tools/list"}
EOF
  then
    echo "agentMemory MCP smoke test passed"
    return 0
  fi
  if [ "$SMOKE_TEST" = "auto" ]; then
    echo "agentMemory MCP smoke test failed in auto mode; check Node dependencies before using MCP." >&2
    return 0
  fi
  echo "agentMemory MCP smoke test failed" >&2
  return 1
}

echo "Mode: $MODE"
echo "CODEX_HOME: $CODEX_HOME"
echo "Skill: $SOURCE_SKILL -> $TARGET_SKILL"
echo "Tool: $SOURCE_TOOL -> $TARGET_TOOL"
echo "Config: $CONFIG_FILE"

require_command "$NODE_BIN"
copy_dir "$SOURCE_SKILL" "$TARGET_SKILL" "skill"
copy_dir "$SOURCE_TOOL" "$TARGET_TOOL" "MCP server"
install_dependencies
write_config
run_smoke_test

echo "agentMemory MCP installation completed"
