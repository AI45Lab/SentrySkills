# Installing SentrySkills for Codex

## Installation

```bash
git clone https://github.com/AI45Lab/SentrySkills.git ~/.codex/sentryskills
mkdir -p ~/.agents/skills
ln -s ~/.codex/sentryskills ~/.agents/skills/sentryskills
cp ~/.codex/sentryskills/AGENTS.template.md ~/.codex/AGENTS.md
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
cmd /c mklink /J "$env:USERPROFILE\.agents\skills\sentryskills" "$env:USERPROFILE\.codex\sentryskills"
Copy-Item "$env:USERPROFILE\.codex\sentryskills\AGENTS.template.md" "$env:USERPROFILE\.codex\AGENTS.md" -Force
```

Restart Codex after installation.

## Integration model

Codex does not provide the same hard enforcement as a hook-driven integration. Treat this as:

- `SKILL.md` defines the method
- `AGENTS.md` enforces agent behavior as much as the framework allows

Recommended policy:

- always run the rule frontend first
- if `rule_stage_action == block`, stop immediately
- assign `framework_risk_level` after rule gating
- only low-risk turns may use subagents for `model_stage`
- if risk is high or subagent behavior is not reliable, fall back to synchronous `model_stage`
- run one proposal sweep at the end of each main-agent task
- proposal sweep only affects subsequent turns

## What to expect

The runtime writes workspace-local state into:

- `.sentryskills/base/`
- `.sentryskills/extra/`

Key fields in results:

- `base_rule_action`
- `extra_rule_action`
- `rule_stage_action`
- `framework_risk_level`
- `model_dispatch_mode`
- `model_stage_status`
- `model_executor`
- `model_stage_result_available`
- `proposal_sweep_effect`
- `final_action`
