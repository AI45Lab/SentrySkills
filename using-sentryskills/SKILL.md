---
name: using-sentryskills
description: Run SentrySkills before every task using a rule-first frontend and a risk-gated model backend. The skill/framework decides sync vs async after rule gating.
---

# Using SentrySkills

## Purpose

`using-sentryskills` is the entry skill. It defines the required execution order for every task:

`base_rule -> extra_rule -> rule_gate -> risk assessment -> model_stage -> end-of-task proposal sweep`

The first three stages are mandatory and synchronous. `model_stage` is conditional. Proposal sweep is a main-agent maintenance step that runs at the end of every task and only affects subsequent turns.

## Required Behavior

1. Build the current input payload and run `shared/scripts/self_guard_runtime_hook_template.py`.
2. Read the result under `.sentryskills/base/`.
3. At task end, if this is a main-agent turn, execute one proposal sweep.
4. Respect the returned stage fields:
   - `base_rule_action`
   - `extra_rule_action`
   - `rule_stage_action`
   - `model_dispatch_mode`
   - `model_stage_status`
   - `model_stage_action`
   - `model_executor`
   - `model_stage_result_available`
   - `proposal_sweep_effect`
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

### Risk-gated model backend

If `rule_stage_action != block`, the skill or framework must assign:

- `framework_risk_level = high | low`

Then the main framework agent dispatches `model_stage` with these rules:

- `high` -> `model_dispatch_mode = sync`
- `low + subagent support` -> `model_dispatch_mode = async`
- `low + no stable subagent support` -> `model_dispatch_mode = sync`

The runtime script records this decision. It should not invent async execution by itself.

Subagent capability may always be present in the framework, but actual subagent dispatch is still gated by the main framework agent's risk assessment.

### Knowledge writeback

Only after `model_stage` is completed may the system:

- synthesize candidate extra rules
- synthesize textual memory
- run dedup
- run validation
- promote validated rules into active extra rules

If `model_stage` is skipped or pending, knowledge writeback must also be skipped or deferred.

### Proposal sweep

At the end of every main-agent task:

- scan `.sentryskills/extra/proposals/pending/`
- process all readable proposal files
- move consumed files to `processed/` or `rejected/`

Proposal sweep must not rewrite the already finalized current turn. Its updates only affect subsequent turns.

## Expected Input

The runtime script accepts the normal task payload. When the framework already has a model-stage result, it may pass:

```json
{
  "framework_risk_level": "high",
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

If the framework chooses async model execution for a low-risk turn, the current turn may omit `model_stage`; the script will record pending model-stage state instead.

When an async subagent later completes `model_stage`, it should submit proposals rather than directly modifying active rules. The main agent is responsible for sweeping and consuming pending proposal files at task end, with effects starting from the next turn.

## Runtime State

Workspace-local state is written under:

- `.sentryskills/base/`
- `.sentryskills/extra/`

`base` stores the current turn logs and state. `extra` stores active rules, candidate rules, textual memory, validation audit, and dedup audit.
