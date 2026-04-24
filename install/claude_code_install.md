# Claude Code Installation Guide

## Installation

```bash
git clone https://github.com/AI45Lab/SentrySkills.git ~/SentrySkills
cd ~/SentrySkills
python install/install.py
```

Restart Claude Code after installation.

## Integration model

Claude Code is the best fit for the new version because hooks can enforce the rule-first frontend:

`base_rule -> extra_rule -> rule_gate`

Then the framework performs risk assessment and may choose:

- `sync model_stage`
- `async/subagent model_stage`

Key rules:

- `rule_stage_action == block` stops immediately
- subagents are only allowed after rule gating
- only low-risk turns may use async/subagent execution
- knowledge writeback only happens after completed `model_stage`
- the main framework agent should run one proposal sweep at task end
- proposal sweep only affects subsequent turns

## Runtime fields to inspect

- `base_rule_action`
- `extra_rule_action`
- `rule_stage_action`
- `framework_risk_level`
- `model_dispatch_mode`
- `model_stage_status`
- `model_stage_action`
- `model_executor`
- `model_stage_result_available`
- `proposal_sweep_effect`
- `knowledge_writeback_status`
- `final_action`

## Storage

Claude Code runs against the current workspace, so runtime state stays local:

- `.sentryskills/base/`
- `.sentryskills/extra/`
