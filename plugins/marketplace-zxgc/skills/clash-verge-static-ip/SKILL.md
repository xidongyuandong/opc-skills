---
name: clash-verge-static-ip
description: Safely build, migrate, and verify a Clash Verge Rev/Mihomo static-IP exit that uses subscription nodes as dialer upstreams. Use for durable remote-profile sidecars, Auto-Best groups, cross-computer migration, refresh/restart persistence, direct YAML builds, or diagnosing static-route selection without exposing credentials.
---

# Clash Verge Static IP

Build the route `traffic group -> static exit group -> static SOCKS5 proxy -> dialer-proxy -> subscription node`, with sidecar persistence, dry-run output, backups, redacted logs, and layered verification.

## Choose a mode

- For a remote subscription that users will refresh in Clash Verge, use the durable
  sidecar workflow in [references/portable-sidecar.md](references/portable-sidecar.md).
  This is the default and the portable cross-computer path.
- For a standalone local YAML that will not be replaced by a subscription refresh,
  use [references/workflow.md](references/workflow.md) and the legacy YAML builder.
- Do not overwrite a remote profile YAML or copy an entire `profiles.yaml` merely to
  migrate this feature. A remote YAML is replaceable data; the profile-bound sidecar
  is the durable customization source.

## Workflow

1. Determine whether the target is a refreshable remote profile or a standalone YAML.
2. Generate only a candidate sidecar or YAML and inspect it before binding/applying.
3. Run the matching verifier. Use Mihomo syntax validation on the final composition
   when its binary is available.
4. Ask for explicit confirmation before editing a live profile binding or applying
   to a live YAML.
5. Reload Clash Verge, select the intended runtime group, and perform external-IP
   and restart/update checks.

When diagnosing a failure, start with the "错误尝试与正确第一步" table in the
relevant reference. Do not inspect or print a whole live profile merely to
understand a parser error.

## Sidecar commands (recommended)

Generate a candidate from a provider/reference YAML. The selected output is the
only new file that may contain the static proxy credentials:

```bash
ruby scripts/build_static_ip_sidecar.rb \
  --reference /path/provider-reference.yaml \
  --proxy-name cliproxy-static \
  --output /tmp/static-ip-sidecar.js
```

Use optional `--exclude-regex` to exclude unsuitable upstream nodes from
Auto-Best. Never put credentials on the command line.

Verify the final composed YAML after Clash Verge has run the sidecar:

```bash
ruby scripts/verify_sidecar_profile.rb \
  --profile /path/final-composed.yaml \
  --static-proxy-name cliproxy-static
```

## Direct YAML commands (standalone profiles only)

Create a candidate only:

```bash
ruby scripts/build_static_ip_profile.rb \
  --reference /path/reference.yaml \
  --target /path/subscription.yaml \
  --output /tmp/static-ip-candidate.yaml
```

Verify structure:

```bash
ruby scripts/verify_static_ip_profile.rb --profile /tmp/static-ip-candidate.yaml
```

Run the self-contained regression suite before changing the workflow scripts:

```bash
ruby scripts/test_static_ip_workflow.rb
ruby scripts/test_sidecar_workflow.rb
```

Apply only after the user explicitly approves modification of the live profile:

```bash
ruby scripts/build_static_ip_profile.rb \
  --reference /path/reference.yaml \
  --target /path/live-profile.yaml \
  --apply
```

## Safety Rules

- Never print or persist proxy credentials outside the selected YAML/sidecar output
  and an explicitly created local backup.
- A generated sidecar necessarily contains the static proxy credential. Treat it
  as sensitive, do not commit it, and do not copy it through chat or public storage.
- Keep the reusable asset template free of real server addresses, credentials,
  subscription URLs, profile UIDs, and machine-specific paths.
- Never infer that a country-matching node is equivalent to the provider's static proxy.
- Never claim all device traffic is covered unless TUN or equivalent system-wide routing is verified. With system proxy only, say "traffic entering Mihomo".
- Treat subscription refresh as destructive to manual remote-YAML edits. A bound
  sidecar must be re-run and verified after both normal update and update-via-proxy.
- Configuration presence does not prove activation. In Global mode verify
  `GLOBAL -> static group`; in Rule mode verify the traffic group (normally
  `Proxy`) selects the static group.
- A successful config parse does not prove the provider IP is fixed long term.
- If YAML parsing fails, stop before writing and report only the file and parser line, not nearby secrets.
- Keep scripts compatible with the macOS system Ruby 2.6 unless the skill explicitly checks for a newer runtime.
- Invoke scripts with the interpreter matching their shebang or extension; `quick_validate.py` must run with Python, not Ruby.
