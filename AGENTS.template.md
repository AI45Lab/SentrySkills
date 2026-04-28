# SentrySkills - Rule-First Execution Policy

Before every task, apply SentrySkills in this order:

1. Run `/using-sentryskills` first.
2. Complete the rule-first frontend before any model-heavy reasoning:
   - `base_rule`
   - `extra_rule`
   - `rule_gate`
3. If `rule_stage_action == block`:
   - stop immediately
   - refuse the request
   - do not use subagents
   - do not summarize new rules or memories
4. If `rule_stage_action != block`:
   - assign `framework_risk_level` first
   - use `sync` model-stage execution for high risk
   - only use subagents for `model_stage`, never before rule gating
   - only low-risk turns may use subagents
   - the main framework agent decides whether subagent dispatch actually happens
5. For any non-blocked turn, run the runtime hook twice:
   - first without `model_stage` for rule gating
   - second after completed `model_stage` with the model-stage knowledge envelope
6. Only after `model_stage` completes may you:
   - synthesize new extra rules
   - write textual memory
   - run dedup / validation / promotion
7. A completed `model_stage` must include a knowledge envelope:
   - put deterministic reusable patterns in `rule_candidates`
   - put non-rule-stable lessons in `memory_candidates`
   - use empty arrays only when there is genuinely no reusable knowledge
8. For async/subagent `model_stage`, write proposal files only; the subagent must not directly modify active extra rules.
9. At the end of every main-agent task, run one proposal sweep over pending async proposals.
10. If there is a pending async model task from a previous turn, check it before continuing the new turn.

Proposal sweep updates subsequent turns only. Do not rewrite the already finalized current turn.

When reporting the decision, include:

- `sentryskills_trace_id`
- `base_rule_action`
- `extra_rule_action`
- `rule_stage_action`
- `framework_risk_level`
- `model_dispatch_mode`
- `model_stage_status`
- `model_stage_result_available`
- `proposal_sweep_effect`
- `knowledge_writeback_status`
- `final_action`
