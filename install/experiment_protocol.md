# SentrySkills Experiment Protocol

This protocol defines the minimum logging and execution contract for framework-native experiments with Codex and Claude Code.

## Execution contract

Every turn follows:

`base_rule -> extra_rule -> rule_gate -> risk assessment -> model_stage(sync or async) -> end-of-task proposal sweep`

Rules:

- the main framework agent assigns `framework_risk_level`
- high risk must stay `sync`
- only low-risk turns may actually use subagents
- async subagents write proposal files only
- the main agent runs one proposal sweep at task end
- proposal sweep affects subsequent turns only

## Minimum experiment fields

Use these fields as the standard experiment record:

- `trace_id`
- `base_rule_action`
- `extra_rule_action`
- `rule_stage_action`
- `framework_risk_level`
- `model_dispatch_mode`
- `model_stage_status`
- `model_stage_action`
- `model_executor`
- `model_stage_result_available`
- `proposal_write`
- `proposal_sweep`
- `proposal_sweep_effect`
- `knowledge_writeback_status`
- `final_action`

## Required validation scenarios

- rule-stage block
- high-risk sync model stage
- low-risk async subagent proposal write
- main-agent end-of-task proposal sweep
- next-turn visibility of promoted active rules

## Interpretation rules

- `model_executor` describes the source of the current-turn model result only
- `model_stage_result_available` is `true` only when the current turn has a completed model-stage result
- `proposal_sweep_effect` only reflects rule-state change:
  - `no_change`
  - `candidate_only`
  - `active_rule_updated`
