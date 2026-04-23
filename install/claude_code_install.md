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

Then the framework may choose:

- `sync model_stage`
- `async/subagent model_stage`

Key rules:

- `rule_stage_action == block` stops immediately
- subagents are only allowed after rule gating
- knowledge writeback only happens after completed `model_stage`

## Runtime fields to inspect

- `base_rule_action`
- `extra_rule_action`
- `rule_stage_action`
- `model_dispatch_mode`
- `model_stage_status`
- `model_stage_action`
- `knowledge_writeback_status`
- `final_action`

## Storage

Claude Code runs against the current workspace, so runtime state stays local:

- `.sentryskills/base/`
- `.sentryskills/extra/`
