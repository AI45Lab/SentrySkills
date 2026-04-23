---
name: using-sentryskills
description: Run SentrySkills before every task using a rule-first frontend and a conditional model backend. The model stage may be synchronous or async, but only after rule gating.
---

# Using SentrySkills

## Purpose

`using-sentryskills` is the entry skill. It defines the required execution order for every task:

`base_rule -> extra_rule -> rule_gate -> model_stage -> knowledge_writeback`

The first three stages are mandatory and synchronous. `model_stage` is conditional. `knowledge_writeback` is only allowed after `model_stage` finishes.

## Required Behavior

1. Build the current input payload and run `shared/scripts/self_guard_runtime_hook_template.py`.
2. Read the result under `.sentryskills/base/`.
3. Respect the returned stage fields:
   - `base_rule_action`
   - `extra_rule_action`
   - `rule_stage_action`
   - `model_dispatch_mode`
   - `model_stage_status`
   - `model_stage_action`
   - `knowledge_writeback_status`
   - `final_action`

## Execution Rules

### Rule-first frontend

Always run:

- `base_rule`
- `extra_rule`
- `rule_gate`

Use conservative merging:

- `block > downgrade > allow`

If `rule_stage_action == block`:

- stop immediately
- do not enter `model_stage`
- do not create new extra rules
- do not create textual memory

### Conditional model backend

If `rule_stage_action != block`, `model_stage` may run.

Default policy:

- `rule_stage_action == downgrade` -> `model_dispatch_mode = sync`
- `rule_stage_action == allow` -> `model_dispatch_mode = async`
- if the framework cannot support async/subagent execution, fall back to `sync`

### Knowledge writeback

Only after `model_stage` is completed may the system:

- synthesize candidate extra rules
- synthesize textual memory
- run dedup
- run validation
- promote validated rules into active extra rules

If `model_stage` is skipped or pending, knowledge writeback must also be skipped or deferred.

## Expected Input

The runtime script accepts the normal task payload. When the framework already has a model-stage result, it may pass:

```json
{
  "model_dispatch_mode": "sync",
  "model_stage": {
    "action": "allow|downgrade|block",
    "analysis": "string",
    "reason_codes": ["..."],
    "findings": ["..."],
    "rule_candidates": [],
    "memory_candidates": []
  }
}
```

If the framework chooses async model execution, the current turn may omit `model_stage`; the script will record pending model-stage state instead.

## Runtime State

Workspace-local state is written under:

- `.sentryskills/base/`
- `.sentryskills/extra/`

`base` stores the current turn logs and state. `extra` stores active rules, candidate rules, textual memory, validation audit, and dedup audit.
