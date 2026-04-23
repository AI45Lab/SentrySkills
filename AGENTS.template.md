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
   - model-stage work is allowed
   - subagents may only be used for `model_stage`, never before rule gating
5. Only after `model_stage` completes may you:
   - synthesize new extra rules
   - write textual memory
   - run dedup / validation / promotion
6. If there is a pending async model task from a previous turn, check it before continuing the new turn.

When reporting the decision, include:

- `sentryskills_trace_id`
- `base_rule_action`
- `extra_rule_action`
- `rule_stage_action`
- `model_dispatch_mode`
- `model_stage_status`
- `final_action`
