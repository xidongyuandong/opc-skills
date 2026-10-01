# Design rationale and public references

One existing task compiler plus a thin DAG scheduler avoids duplicate model policies.
The coordinator owns semantic decomposition and acceptance; scripts enforce scope,
dependencies, ownership, retry and context-size contracts.

Reference patterns (not runtime dependencies or bundled third-party source):
- [Independent agents](https://github.com/obra/superpowers/tree/main/skills/dispatching-parallel-agents): bounded independent outputs.
- [Subagent development](https://github.com/obra/superpowers/tree/main/skills/subagent-driven-development): separate implementation and acceptance.
- [Team composition](https://github.com/wshobson/agents/tree/main/plugins/agent-teams/skills/team-composition-patterns): smallest useful team.
- [GSD orchestrator](https://github.com/gsd-build/gsd-2/tree/main/gsd-orchestrator): explicit blocked states.

Small tasks stay with the coordinator. No objective superiority or token savings
is claimed without paired quality and complete usage evidence.
