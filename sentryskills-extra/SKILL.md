---
name: sentryskills-extra
description: Extension layer for SentrySkills. It separates online extra-rule detection from post-model-stage knowledge management.
---

# SentrySkills Extra

## Purpose

`sentryskills-extra` has two distinct responsibilities:

- `extra_rule`: online rule extension after `base_rule`
- `extra_memory`: post-model-stage knowledge management
  and end-of-task proposal sweeping by the main agent

This skill must not use any framework-external model.

## Execution Boundary

### `extra_rule`

`extra_rule` runs during the online decision path:

- after `base_rule`
- before `rule_gate`
- using only active extra rules

It may:

- match active extra rules
- raise the rule-stage decision conservatively

It may not:

- generate candidate rules
- write textual memory
- run dedup or validation

### `extra_memory`

`extra_memory` runs only after `model_stage` is completed.

It may:

- synthesize candidate rules from model findings
- store textual memory
- deduplicate similar knowledge
- validate new candidate rules
- promote validated rules into `active_extra_rules.json`

For async subagent results:

- the subagent may only write proposal files
- proposal files are swept and consumed by the main agent
- async analysis does not directly modify active or candidate stores
- proposal sweep only affects subsequent turns

It must not run when:

- `rule_stage_action == block`
- `model_stage` is skipped
- `model_stage` is still pending

## Model-Stage Knowledge Contract

After a completed `model_stage`, the framework agent must pass reusable knowledge to the runtime hook:

- `rule_candidates`: deterministic extra-rule proposals for patterns that can be checked locally
- `memory_candidates`: natural-language observations for patterns that are useful but not rule-stable

Do not rely on a prose-only analysis if a reusable rule or memory exists. The runtime can preserve fallback textual memory from `findings`, but executable rules must be supplied as structured `rule_candidates`.

Rule candidate fields:

- `pattern`
- `pattern_type`: `substring`, `regex`, or `planned_action`
- `risk_type`
- `trigger_condition`
- `suggested_action`: `downgrade` or `block`
- `reason_code`
- `evidence_items`

Memory candidate fields:

- `pattern_summary`
- `risk_type`
- `trigger_contexts`
- `why_not_rule_friendly`
- `evidence_items`
- `suggested_action`

For async model-stage execution, the subagent writes proposal files only. The main agent processes those proposal files during the end-of-task sweep.

## Storage

Workspace-local runtime state is stored under:

- `.sentryskills/extra/memory/active_extra_rules.json`
- `.sentryskills/extra/memory/candidate_extra_rules.jsonl`
- `.sentryskills/extra/memory/textual_memory.jsonl`
- `.sentryskills/extra/memory/validation_audit.jsonl`
- `.sentryskills/extra/memory/dedup_audit.jsonl`
- `.sentryskills/extra/memory/proposal_audit.jsonl`
- `.sentryskills/extra/proposals/pending/`
- `.sentryskills/extra/proposals/processed/`
- `.sentryskills/extra/proposals/rejected/`

## Model Constraint

Allowed:

- the framework's own primary model, if the framework provides a `model_stage` result

Not allowed:

- external APIs
- embedding models
- rerankers
- separate similarity models
- custom external classifiers
