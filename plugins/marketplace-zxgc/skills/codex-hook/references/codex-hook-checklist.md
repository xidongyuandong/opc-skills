# Codex Hook Checklist

## Before Editing

- Confirm the request is hook-related.
- Inspect `/Users/zhengyuyu/.codex/hooks.json`.
- Identify the exact event and matcher affected.
- Inspect the target script before editing.

## Validation

Run:

```bash
python3 -m json.tool /Users/zhengyuyu/.codex/hooks.json >/dev/null
python3 -m py_compile /Users/zhengyuyu/.codex/hooks/<script>.py
```

For simple hook scripts, run a representative event:

```bash
printf '{}' | python3 /Users/zhengyuyu/.codex/hooks/<script>.py --event SessionStart
```

## Troubleshooting

- Hook not firing: check event name, matcher, JSON syntax, and Codex restart requirement.
- Hook blocks Codex: lower timeout, make script return success on recoverable errors, and log details.
- Permission denied: ask the user to run the exact command in normal Terminal or grant file access.
- Duplicate behavior: search hooks.json and scripts before adding entries.

## Naming

Use `codex-hook` for the skill name. Treat `skill-hook` as a legacy alias only in historical notes.
