# Installing SentrySkills for OpenClaw

## Installation

```bash
npm i -g clawhub
clawhub install sentryskills
curl -o ~/.openclaw/workspace/AGENTS.md https://raw.githubusercontent.com/AI45Lab/SentrySkills/main/AGENTS.template.md
```

Restart OpenClaw after installation.

## Integration model

OpenClaw relies on skill loading plus `AGENTS.md` behavior constraints. The intended execution order is:

`base_rule -> extra_rule -> rule_gate -> model_stage -> knowledge_writeback`

Recommended policy:

- rule frontend is always synchronous
- if `rule_stage_action == block`, stop immediately
- async/subagent execution is only for `model_stage`
- if async execution is unstable in your setup, use synchronous `model_stage`

## Runtime state

Workspace-local state is written under:

- `.sentryskills/base/`
- `.sentryskills/extra/`

Knowledge writeback only occurs after a completed `model_stage`.
