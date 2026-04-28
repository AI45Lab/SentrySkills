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

1. Build the current input payload and run `shared/scripts/self_guard_runtime_hook_template.py` once for rule gating.
2. Read the result under `.sentryskills/base/`.
3. If `rule_stage_action == block`, stop and treat that hook result as the final guard result.
4. If `rule_stage_action != block`, run the task's `model_stage` in `sync` or `async` mode according to the risk gate.
5. After a completed `model_stage`, call the runtime hook again with the completed model-stage knowledge envelope. This second call is what writes extra rules, textual memory, or async proposal files.
6. At task end, if this is a main-agent turn, ensure one proposal sweep has run.
7. Respect the returned stage fields:
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

### Two-call runtime pattern

For non-blocked turns, do not stop after the initial rule-gating hook. Use this pattern:

1. `pre_model_hook`: payload has the original task context and no `model_stage`; use it to compute `base_rule`, `extra_rule`, and `rule_stage_action`.
2. `model_stage`: the framework agent or allowed subagent performs the model-heavy safety judgment.
3. `post_model_hook`: payload includes the same task context plus `framework_risk_level`, `model_dispatch_mode`, `sentryskills_role`, and the completed `model_stage` object.

If the second hook is skipped, `sentryskills-extra` cannot write new rules, textual memory, or async proposals.

### Knowledge writeback

Only after `model_stage` is completed may the system:

- synthesize candidate extra rules
- synthesize textual memory
- run dedup
- run validation
- promote validated rules into active extra rules

If `model_stage` is skipped or pending, knowledge writeback must also be skipped or deferred.

When `model_stage` is completed, do not only write an analysis paragraph. Also produce reusable knowledge:

- use `rule_candidates` for deterministic patterns that can be checked by the extra rule stage
- use `memory_candidates` for natural-language lessons that are useful but not stable enough for a rule
- if there is no reusable knowledge, return empty arrays explicitly

The runtime hook can store fallback textual memory from `findings`, but it cannot invent high-quality executable rules from prose. Put executable rule proposals in `rule_candidates`.

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
    "rule_candidates": [
      {
        "pattern": "literal substring or regex",
        "pattern_type": "substring|regex|planned_action",
        "risk_type": "prompt_injection|secret_exfiltration|unsafe_tool_use|...",
        "trigger_condition": "when this rule should fire",
        "suggested_action": "downgrade|block",
        "reason_code": "EXTRA_...",
        "evidence_items": ["model-stage evidence"]
      }
    ],
    "memory_candidates": [
      {
        "pattern_summary": "natural-language lesson learned from this model-stage result",
        "risk_type": "prompt_injection|secret_exfiltration|unsafe_tool_use|...",
        "trigger_contexts": ["where this tends to appear"],
        "why_not_rule_friendly": "why this is not yet a stable deterministic rule",
        "evidence_items": ["model-stage evidence"],
        "suggested_action": "downgrade|block"
      }
    ]
  }
}
```

If the framework chooses async model execution for a low-risk turn, the current turn may omit `model_stage`; the script will record pending model-stage state instead.

When an async subagent later completes `model_stage`, it must call the runtime hook with `sentryskills_role = "subagent"`, `model_dispatch_mode = "async"`, and the completed `model_stage` envelope. The subagent writes proposal files only; it must not modify active rules directly. The main agent is responsible for sweeping and consuming pending proposal files at task end, with effects starting from the next turn.

## Runtime State

Workspace-local state is written under:

- `.sentryskills/base/`
- `.sentryskills/extra/`

`base` stores the current turn logs and state. `extra` stores active rules, candidate rules, textual memory, validation audit, and dedup audit.
