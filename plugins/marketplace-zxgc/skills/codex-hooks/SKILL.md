---
name: codex-hooks
description: Use this skill when the user asks to create, modify, validate, or troubleshoot Codex hooks, including SessionStart, UserPromptSubmit, PreToolUse, PermissionRequest, PostToolUse, and Stop hooks. Also use it when migrating Claude Code hook guidance to Codex hook files. This skill wraps the Claude hook-development reference while adapting paths and event names for Codex.
---

# Codex Hooks

Use this skill to work on Codex hook configuration and hook scripts.

## Codex Files

Codex hook configuration:

```text
$HOME/.codex/hooks.json
```

Codex hook scripts:

```text
$HOME/.codex/hooks/
```

Current local learning hook:

```text
$HOME/.codex/hooks/codex_learning_hook.py
```

## Source Reference

This skill is adapted from Claude's `hook-development` skill. When detailed hook patterns, examples, schema checks, or migration notes are needed, read the source reference:

```text
$HOME/.claude/plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/skills/hook-development/SKILL.md
```

Related reference folders:

```text
$HOME/.claude/plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/skills/hook-development/references/
$HOME/.claude/plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/skills/hook-development/examples/
$HOME/.claude/plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/skills/hook-development/scripts/
```

## Codex Hook Events

The active Codex config on this machine uses:

- `SessionStart`
- `UserPromptSubmit`
- `PreToolUse`
- `PermissionRequest`
- `PostToolUse`
- `Stop`

Use the exact event names already present in `$HOME/.codex/hooks.json`.

## Workflow

1. Read `$HOME/.codex/hooks.json`.
2. Read the relevant existing script under `$HOME/.codex/hooks/`.
3. If the requested behavior already fits `codex_learning_hook.py`, extend that script narrowly.
4. If the behavior is independent, add a small dedicated hook script under `$HOME/.codex/hooks/`.
5. Update `$HOME/.codex/hooks.json` with the minimal new command entry.
6. Validate JSON syntax and run the hook script with representative stdin where practical.
7. Do not print secrets from hook payloads. Redact keys matching token, secret, password, authorization, credential, or auth.

## Adaptation Rules

- Translate Claude paths like `~/.claude/settings.json` or `.claude/hooks` to Codex paths only when appropriate.
- Prefer `$HOME/.codex/hooks.json` over Claude settings files.
- Preserve existing hook entries; append or edit narrowly.
- Do not replace the existing learning hook unless explicitly requested.
- Use `apply_patch` for manual file edits.
