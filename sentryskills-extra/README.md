# sentryskills-extra

`sentryskills-extra` is the extension layer for the new SentrySkills architecture.

It is split into:

- `extra_rule`
  online rule evaluation after `base_rule`
- `extra_memory`
  post-model-stage knowledge management

Runtime storage lives under `.sentryskills/extra/memory/`.

The initial tracked state is empty by design:

- `active_extra_rules.json`
- `candidate_extra_rules.jsonl`
- `textual_memory.jsonl`
- `validation_audit.jsonl`
- `dedup_audit.jsonl`
