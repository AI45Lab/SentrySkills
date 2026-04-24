# SentrySkills

SentrySkills is a workspace-local self-guard framework for AI agents.

## Package structure

- `using-sentryskills`
  Entry skill that defines the full execution contract
- `sentryskills-preflight`
  Base-rule pre-execution analysis
- `sentryskills-runtime`
  Base-rule runtime monitoring
- `sentryskills-output`
  Base-rule output protection
- `sentryskills-extra`
  Extra-rule detection and post-model-stage knowledge management

## Current architecture

The current version follows:

`base_rule -> extra_rule -> rule_gate -> risk assessment -> model_stage(sync or async) -> end-of-task proposal sweep`

Key rules:

- the rule frontend always runs first
- `block` at rule stage ends the turn
- async/subagent execution is only for low-risk `model_stage`
- new extra knowledge is only written after completed `model_stage`
- the main framework agent runs one proposal sweep at task end
- proposal sweep only affects subsequent turns

## Runtime state

Workspace-local state is stored at:

- `.sentryskills/base/`
- `.sentryskills/extra/`
