# SentrySkills

[![Docs](https://img.shields.io/badge/docs-website-blue?style=flat-square)](https://zengbiaojie.github.io/SentrySkills/)
[![GitHub](https://img.shields.io/badge/github-AI45Lab%2FSentrySkills-181717?style=flat-square&logo=github)](https://github.com/AI45Lab/SentrySkills)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

SentrySkills is a self-guarding security framework for AI agents. The current version uses a **rule-first frontend** and a **conditional model backend**:

`base_rule -> extra_rule -> rule_gate -> model_stage(sync or async) -> knowledge_writeback`

## What changed in the new version

- All tasks go through the rule frontend first.
- `base_rule` and `extra_rule` are always synchronous.
- `rule_gate` uses `block > downgrade > allow`.
- `model_stage` is only entered when the rule stage does not block.
- Knowledge writeback is only allowed after a completed `model_stage`.
- Runtime state is workspace-local under `.sentryskills/base` and `.sentryskills/extra`.

## Core modules

- `using-sentryskills`
  Entry skill and execution contract
- `sentryskills-preflight`
  Base-rule pre-execution checks
- `sentryskills-runtime`
  Base-rule runtime monitoring
- `sentryskills-output`
  Base-rule output protection
- `sentryskills-extra`
  Extra-rule detection plus post-model knowledge management
- `shared/scripts/self_guard_runtime_hook_template.py`
  Main runtime script

## Decision model

### Rule-first frontend

The system always runs:

- `base_rule`
- `extra_rule`
- `rule_gate`

If `rule_stage_action == block`, the turn ends immediately. No model stage and no knowledge writeback are allowed.

### Conditional model backend

If `rule_stage_action != block`, the framework may enter `model_stage`.

Default dispatch policy:

- `downgrade -> sync`
- `allow -> async`
- frameworks without stable subagent support fall back to `sync`

### Knowledge writeback

Only a completed `model_stage` may generate:

- candidate extra rules
- textual memory
- dedup audit
- validation audit
- promoted active extra rules

Pure rule hits do not create new knowledge.

## Runtime outputs

The runtime script now exposes these stage fields in summaries and logs:

- `base_rule_action`
- `extra_rule_action`
- `rule_stage_action`
- `model_dispatch_mode`
- `model_stage_status`
- `model_stage_action`
- `knowledge_writeback_status`
- `final_action`

`final_action` is always the executable decision for the current turn. Async model results do not retroactively rewrite an already finished turn.

## Storage layout

- `.sentryskills/base/`
  - unified logs
  - turn results
  - session state
  - index
- `.sentryskills/extra/`
  - active extra rules
  - candidate extra rules
  - textual memory
  - dedup audit
  - validation audit

## Framework integration

- Claude Code
  Prefer hook-enforced rule-first execution; model stage may be sync or async if the framework supports it.
- Codex / OpenClaw
  Use `SKILL.md` + `AGENTS.md` discipline. If async/subagent execution is not reliable, treat `model_stage` as synchronous.

See:

- [install/claude_code_install.md](install/claude_code_install.md)
- [install/codex_install.md](install/codex_install.md)
- [install/openclaw_install.md](install/openclaw_install.md)

## Requirements

- Python 3.8+
- no external Python dependencies for the core runtime path
