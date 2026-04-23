---
name: sentryskills-extra
description: Extension layer for SentrySkills. It separates online extra-rule detection from post-model-stage knowledge management.
---

# SentrySkills Extra

## Purpose

`sentryskills-extra` has two distinct responsibilities:

- `extra_rule`: online rule extension after `base_rule`
- `extra_memory`: post-model-stage knowledge management

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

It must not run when:

- `rule_stage_action == block`
- `model_stage` is skipped
- `model_stage` is still pending

## Storage

Workspace-local runtime state is stored under:

- `.sentryskills/extra/memory/active_extra_rules.json`
- `.sentryskills/extra/memory/candidate_extra_rules.jsonl`
- `.sentryskills/extra/memory/textual_memory.jsonl`
- `.sentryskills/extra/memory/validation_audit.jsonl`
- `.sentryskills/extra/memory/dedup_audit.jsonl`

## Model Constraint

Allowed:

- the framework's own primary model, if the framework provides a `model_stage` result

Not allowed:

- external APIs
- embedding models
- rerankers
- separate similarity models
- custom external classifiers
