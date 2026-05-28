# C250 Remote Script Execution

## Rule

Do not put complex programs directly inside `c250-exec '...'`.

Use a bundled script when the remote logic:

- is more than 10 shell lines,
- contains Python, awk, sed programs, JSON, regex, here-docs, or nested quotes,
- needs to be reused,
- generates durable reports,
- or must be verified with `py_compile`, shellcheck-style checks, or deterministic tests.

## Preferred Pattern: Skill Bundled Script

1. Put the script under a skill:

```text
~/.codex/skills/<skill-name>/scripts/<tool>.py
```

2. Validate locally:

```bash
python3 -m py_compile ~/.codex/skills/<skill-name>/scripts/<tool>.py
```

3. Sync only the needed skills:

```bash
c250-sync-codex --skills <skill-name>
```

4. Validate remotely:

```bash
c250-exec 'python3 -m py_compile /data/jenkins/.codex/home/skills/<skill-name>/scripts/<tool>.py'
```

5. Run remotely with simple arguments:

```bash
c250-exec -C /home/chehejia/cov-evalution-qwen3_6-eval-0521 \
'python3 /data/jenkins/.codex/home/skills/<skill-name>/scripts/<tool>.py --arg value'
```

## Acceptable Fallback: Base64 Transfer

Use base64 only for one-off emergency scripts when sync/scp is unavailable.

```bash
SCRIPT_B64="$(base64 -i /path/to/script.py | tr -d '\n')"
c250-exec "printf '%s' '$SCRIPT_B64' | base64 -d > /tmp/script.py && python3 /tmp/script.py"
```

After the task, move reusable logic into a skill `scripts/` directory.

## Acceptable for Small Commands

Inline `c250-exec` is fine for short inspections:

```bash
c250-exec 'hostname; whoami; pwd'
c250-exec -C /home/chehejia/cov-evalution 'find docs -maxdepth 2 -type f | sort | head -100'
```

## Avoid

- Multi-layer quoted here-docs inside `c250-exec`.
- Large inline `python3 - <<'PY' ... PY` blocks through local shell + wrapper + remote shell.
- Escaping-heavy awk or sed programs in remote command strings.
- Printing secrets while debugging quoting.

## Reason

Nested local shell, wrapper, Docker exec, and remote shell interpretation makes quote removal, command substitution, globbing, word splitting, and here-doc parsing fragile. File-based scripts reduce the number of interpreters touching program text and allow local/remote validation before execution.
