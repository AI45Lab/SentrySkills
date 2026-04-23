# SentrySkills Installation Notes

SentrySkills does not become automatic just because it is installed. You must also configure your framework so that the **rule-first frontend** always runs before normal work.

## New-version execution model

All integrations should follow:

`base_rule -> extra_rule -> rule_gate -> model_stage(sync or async) -> knowledge_writeback`

Key rules:

- `block` at rule stage ends the turn immediately
- subagents are only for `model_stage`, never for the rule frontend
- new rules and textual memory are only written after a completed `model_stage`

## Documentation

- [claude_code_install.md](claude_code_install.md)
- [codex_install.md](codex_install.md)
- [openclaw_install.md](openclaw_install.md)

## Workspace-local state

The runtime writes to:

- `.sentryskills/base/`
- `.sentryskills/extra/`

These directories are per workspace, not global shared state.
