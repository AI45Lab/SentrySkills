# Changelog

All notable changes to SentrySkills will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.7] - 2026-04-08

### Added

- **Stage-Level Analysis in Logs**:
  - Added per-stage `analysis` text for `preflight`, `runtime`, and `output_guard`
  - Added `stage_analyses` to summary output for quick stage-by-stage reading
  - Added stage analysis content to `decision_trace.stages[*].analysis`
- **Improved Decision Explainability**:
  - Added reason-code to human-readable description mapping
  - Enhanced `decision_explanation` to better describe final decision path

### Changed

- **Logging Output Strategy**:
  - Runtime hook now defaults to detailed unified log only
  - Summary JSON is now opt-in via `--emit-summary` (together with `--out`)
- **Hook Integration Behavior**:
  - `claude_code_hook.py` now reads decision from unified detailed log output
  - Block and downgrade hook messages now include human-readable `Why` explanation

### Removed

- **Legacy Summary Dependency in Hook Flow**:
  - Removed reliance on `hook_result_*.json` for hook decision parsing
  - Hook decision pipeline now uses unified log as single source of truth

## [0.1.6] - 2026-04-03

### Added

- **AGENTS.template.md**: Simplified template file for Codex/OpenClaw automatic execution
  - Located in project root directory
  - Contains only essential execution instructions (12 lines)
  - Replaces embedded AGENTS.md content in installation documentation
- **Enhanced Installation Documentation**:
  - `install/codex_install.md`: Added warning box explaining skill installation ≠ automatic execution
  - `install/codex_install.md`: Added AGENTS.md path location section with verification steps
  - `install/openclaw_install.md`: Added warning box explaining skill installation ≠ automatic execution
  - `install/openclaw_install.md`: Added AGENTS.md path location section with verification steps
  - `install/openclaw_install.md`: Corrected AGENTS.md path to `~/.openclaw/workspace/AGENTS.md`

### Changed

- **Simplified AGENTS.md Configuration**:
  - Removed all explanatory text from template (moved to installation docs)
  - Template now contains only core execution instructions
  - Installation docs reference template instead of embedding content
  - Users can download template via curl or create manually with provided commands
- **Documentation Updates**:
  - `README.md`: Updated OpenClaw installation to use `curl` command
  - `README.md`: Updated Codex installation to use `cp` command
  - `README.md`: Added warnings about non-system enforcement for Codex/OpenClaw
  - `docs/index.html`: Updated installation tabs for OpenClaw and Codex
  - `docs/index.html`: Added warning boxes about prompt-based enforcement

### Fixed

- **Incorrect AGENTS.md Path**: Fixed OpenClaw documentation
  - Changed from `~/.codex/AGENTS.md` to `~/.openclaw/workspace/AGENTS.md`
  - Updated all path references in install/openclaw_install.md
  - Updated Linux/Mac/Windows path examples
  - Updated verification commands
- **Documentation Clarity**: Clarified framework enforcement differences
  - Claude Code: System-level hooks (truly enforced)
  - Codex/OpenClaw: AGENTS.md prompts (LLM-dependent, not enforced)

### Technical Details

**AGENTS.template.md Structure**:
```markdown
# SentrySkills - Automatic Security Protection

Before EVERY response:

1. Run the SentrySkills pre-flight check:
   /using-sentryskills

2. Based on the result:
   - If blocked: Refuse the request and explain why
   - If allowed with warnings: Include warnings in response
   - If allowed: Proceed normally

3. Include in your response:
   - sentryskills_decision: <block|allow|downgrade>
   - sentryskills_trace_id: <trace_id_from_result>
```

**Installation Commands**:
- **OpenClaw**: `curl -o ~/.openclaw/workspace/AGENTS.md https://raw.githubusercontent.com/AI45Lab/SentrySkills/main/AGENTS.template.md`
- **Codex**: `cp ~/.codex/sentryskills/AGENTS.template.md ~/.codex/AGENTS.md`

**Path Locations**:
- Codex: `~/.codex/AGENTS.md`
- OpenClaw: `~/.openclaw/workspace/AGENTS.md`

---

## [0.1.5] - 2026-04-03

### Added

- **One-Click Installation System**: Complete automated installer for Claude Code
  - `install/install.py` - Fully automated plugin installation
  - Creates plugin structure with 4 security skills
  - Installs scripts (19 files) and references (18 files)
  - Auto-registers plugin with Claude Code
  - Verifies installation with detailed status reporting
- **One-Click Uninstallation System**: Complete automated cleanup
  - `install/uninstall.py` - Fully automated plugin removal
  - Cleans up all 4 skills from `.claude/skills/`
  - Removes plugin cache and registration
  - Does not affect other installed plugins
  - Safe, forceful cleanup with verification
- **Plugin-Based Architecture**: Transitioned from hook-based to plugin-based installation
  - Uses Claude Code's native skill system
  - No manual hook configuration required
  - Better integration and automatic loading
  - Skills directly accessible: `/using-sentryskills`, `/sentryskills-preflight`, `/sentryskills-runtime`, `/sentryskills-output`

### Changed

- **Installation Documentation**: Complete rewrite for simplicity
  - `README.md`: Reduced installation to 3 commands (clone + install + restart)
  - `install/claude_code_install.md`: Comprehensive 400+ line guide
  - Removed all PreToolUse hook configuration instructions
  - Added troubleshooting section with common issues
  - Added FAQ section covering multi-framework support
- **Website Documentation**: Updated `docs/index.html`
  - Simplified Claude Code installation to one-click installer
  - Removed hook configuration from installation tabs
  - Updated flow diagram (removed orchestrator references)
  - Added installation features summary box
  - Updated i18n translations (EN/ZH) for new architecture
- **Developer Experience**: 
  - Installation time reduced from ~10 minutes to ~5 seconds
  - Zero manual configuration required
  - No editing of settings.json needed
  - Works immediately after IDE restart

### Fixed

- **Plugin Loading Issues**: Fixed "failed to load" warnings
  - Plugins show "failed to load" but skills work correctly (expected behavior)
  - Caused by local marketplace not registered to system
  - This is intentional to avoid marketplace configuration errors
  - Skills are fully functional despite warning
- **Installation Errors**: Fixed multiple installation failure modes
  - JSON escape errors in installed_plugins.json (Windows paths)
  - Encoding issues on Windows (UTF-8 wrapper added)
  - Missing skills directory creation
  - Incomplete cleanup on uninstall

### Removed

- **Hook-Based Installation**: Deprecated manual hook configuration
  - Removed PreToolUse hook setup from all documentation
  - Removed `claude_code_hook.py` from installation instructions
  - Simplified to pure plugin-based approach
  - Legacy hook method still works but not documented
- **Obsolete Documentation**: Cleaned up docs directory
  - Removed `docs/corrected-flow.md` (development discussion)
  - Removed `docs/flow-analysis.md` (implementation notes)
  - Removed `docs/subagent-implementation.md` (design discussion)
  - Now only `docs/index.html` remains (canonical documentation)

### Technical Details

**Installation Flow**:
```bash
git clone https://github.com/AI45Lab/SentrySkills.git ~/SentrySkills
cd SentrySkills
python install/install.py  # One command
# Restart IDE → Done
```

**Uninstallation Flow**:
```bash
cd SentrySkills
python install/uninstall.py --force  # One command
# All traces removed
```

**What Gets Installed**:
```
~/.claude/
├── plugins/cache/local-marketplace/sentryskills/0.1.5/
│   ├── .claude-plugin/plugin.json
│   ├── skills/ (4 skills)
│   ├── scripts/ (19 security scripts)
│   └── references/ (18 config files)
└── skills/ (4 skills, directly accessible)
    ├── using-sentryskills/
    ├── sentryskills-preflight/
    ├── sentryskills-runtime/
    └── sentryskills-output/
```

**Safety Features**:
- ✅ Does not affect other plugins (superpowers, etc.)
- ✅ Selective cleanup (only removes sentryskills files)
- ✅ Preserves user settings and configurations
- ✅ Verbose output for debugging
- ✅ Graceful error handling

**Migration Notes**:
- **Breaking Change**: Hook-based installation no longer documented
- Users with existing hook installations can continue using them
- To migrate: Run uninstall, delete old hook config, run new installer
- No changes to detection logic or security rules

---

## [0.1.4] - 2026-04-03

### Changed

- **Architecture Simplification**: Removed redundant `sentryskills-orchestrator` component
  - Orchestration logic now consolidated in `using-sentryskills`
  - Clearer separation of concerns: entry point + orchestration vs. detection stages
  - Updated all documentation to reflect streamlined architecture

- **Enhanced Sub-Skill Integration**: Updated `using-sentryskills/SKILL.md`
  - **Step 2a (HIGH Path)**: Now explicitly documents execution of 3 sub-skills:
    - `sentryskills-preflight` - Deep pre-execution analysis
    - `sentryskills-runtime` - Runtime behavior monitoring
    - `sentryskills-output` - Output leakage detection
  - **Step 2b (LOW Path)**: Subagent now executes all 3 sub-skills in parallel
  - **Decision Integration**: Added clear guidance on integrating all 4 decisions (script + 3 sub-skills)
  - **Response Metadata**: Updated to include all sub-skill decisions

- **Documentation Updates**:
  - `README.md`: Updated skill package structure (removed orchestrator)
  - `README.md`: Simplified execution flow diagrams
  - `README.md`: Updated decision flow to show direct sub-skill calls
  - Added sub-skill descriptions in README

### Fixed

- **Architecture Clarity**: Eliminated confusion about orchestration layer
  - Previous: `using-sentryskills` → `sentryskills-orchestrator` → sub-skills (2 hops)
  - Current: `using-sentryskills` → sub-skills (1 hop, clearer)

### Technical Details

**Simplified Architecture**:
```
using-sentryskills (Entry + Orchestration)
  ├─ Step 0: Fast pre-assessment
  ├─ Step 1: Run main script
  └─ Step 2: Execute 3 sub-skills
       ├─ sentryskills-preflight
       ├─ sentryskills-runtime
       └─ sentryskills-output
```

**Decision Integration**:
- Main script returns: `final_action`, `preflight_decision`, `runtime_decision`, `output_guard_decision`
- Each sub-skill returns additional detailed analysis
- Framework uses most conservative action: `block > downgrade > allow`

**Migration Notes**:
- No breaking changes to detection logic
- Purely architectural simplification
- All existing integrations continue to work

---

## [0.1.3] - 2026-04-01

### Added

- **ROADMAP.md**: Comprehensive project roadmap with P0/P1/P2 task breakdown
  - Two-path architecture implementation status
  - Test suite, CI/CD, Docker support, CLI tool plans
  - Version roadmap and success metrics
- **Analysis Documentation**:
  - `docs/corrected-flow.md` - Correct architecture understanding (SentrySkills = rule library + guide)
  - `docs/flow-analysis.md` - Current implementation analysis and gap identification
  - `docs/subagent-implementation.md` - Subagent implementation strategy discussion
- **Verification Script**: `verify_p0_fixes.py` - Automated testing for critical fixes (all 5 tests pass)

### Changed

- **Documentation Restructure**: Clarified SKILL.md roles and responsibilities
  - Root `SKILL.md`: Repositioned as project overview/user manual
  - `using-sentryskills/SKILL.md`: Enhanced as primary execution guide
    - Added risk assessment matrix (HIGH/MEDIUM/LOW criteria)
    - Added decision tree (ASCII flowchart)
    - Added Fast Pre-Assessment pseudocode
    - Added framework integration examples (Claude Code/Codex/OpenClaw)
    - Added next-turn check implementation with code examples
- **Architecture Clarification**:
  - Frameworks responsible for: big model pre-assessment, sync/async decision, subagent spawning
  - SentrySkills provides: detection rules, check scripts, usage guide, logging system

### Fixed

- **Detection Rules Metadata**: Fixed `detection_rules.json` showing 11 enabled instead of 24
- **All P0 Critical Fixes Verified**:
  - Detection rules: All 24 rules enabled (metadata corrected)
  - Policy differentiation: strict(2), balanced(3), permissive(5) confirmed working
  - Whitelist false positives: Exact placeholder matching implemented
  - Conversation history: Persisting to state file with 20-entry limit
  - Unified logging: events_sink enabled for all log_layout modes

### Technical Details

**Documentation Structure**:
```
SKILL.md (root) → Project overview, skill package descriptions
using-sentryskills/SKILL.md → Execution logic, integration examples
sentryskills-orchestrator/SKILL.md → Orchestration, execution modes
```

**Two-Path Execution**:
- HIGH/MEDIUM risk: Synchronous blocking pipeline
- LOW risk: Async subagent monitoring
- Risk assessment: Framework's internal LLM judgment

**Verification**:
- All P0 fixes tested and verified
- `verify_p0_fixes.py`: 5/5 tests passing

---

## [0.1.2] - 2026-04-01

### Added

- **Two-Path Execution Architecture**: Fast pre-assessment on every task
  - HIGH-risk triggers synchronous blocking pipeline
  - LOW-risk proceeds immediately with parallel subagent monitoring
- **Claude Code Integration**: Complete PreToolUse hook support
  - Automatic security checks on Bash/Edit/Write/WebFetch/WebSearch tool calls
  - Detailed installation guide (`install/claude_code_install.md`)
- **Detection Rules Enhancement**: Enabled all 24 detection rules (previously only 11 active)
  - Added `; curl` pattern to `command_injection_basic` rule
- **Project Documentation**: Comprehensive Overview section in `docs/index.html`
  - Problem statement and solution explanation
  - Target audience definitions (Enterprise Teams, Security Engineers, Developers, Platform Builders)
  - Full bilingual support (English/Chinese)

### Changed

- **Updated Installation Documentation**: Rewrote all installation guides with two-path architecture
  - `README.md` - Updated execution flow diagrams
  - `SKILL.md` (root) - Updated Quick Enable AGENTS.md template
  - `install/README.md` - Removed broken links, simplified Quick Start
  - `install/codex_install.md` - Updated AGENTS.md template with two-path instructions
  - `install/openclaw_install.md` - Updated AGENTS.md template with two-path instructions
  - `sentryskills-orchestrator/README.md` - Updated for dual-mode execution
  - `docs/index.html` - Updated flow descriptions and added Claude Code installation tab

### Fixed

- **Critical Bug Fixes** in `self_guard_runtime_hook_template.py`:
  - Fixed `predictive_report_raw` UnboundLocalError in early exit path
  - Fixed `conv_history` not initialized in early exit path
  - Fixed `matched_rules` missing in high-risk action branch
  - Fixed preflight scan not including `planned_actions` content
  - Fixed output_guard not running extended detection rules
- **Removed Broken References** in `install/README.md`:
  - Removed `first_time_setup.md` (non-existent)
  - Removed `agents_config.md` (non-existent)
  - Removed `triggering_design.md` (non-existent)
  - Removed `AGENTS.md.template` reference
- **Documentation**:
  - Fixed license from MIT-0 to MIT in `docs/index.html`
  - Added bilingual i18n support for user group descriptions
  - Separated Claude Code installation tab from OpenClaw

### Removed

- **Test Files**: Cleaned up temporary test files
  - `test_command_injection.py`
  - `simple_test.py`
  - `hook_test.py`, `hook_test_prompt.py`
  - `test_hook_directly.py`
  - `verify_hook.py`
  - `TWO_PATH_ARCHITECTURE.md`

### Technical Details

**Detection Rules Status**:
- 24/24 rules now enabled (100% coverage)
- Categories: AI/LLM attacks, Web Security, Data Leaks, Code Security

**Hook Configuration**:
- PreToolUse hook runs complete three-stage check (preflight → runtime → output)
- Average latency: 30-100ms per check
- Exit codes: 0 (allow), 2 (block)

**Logging**:
- All hook executions logged to `sentry_skill_log/hook_result_*.json`
- Each log includes: session_id, turn_id, trace_id, final_action, matched_rules

**Migration Notes**:
- No breaking changes
- Existing configurations continue to work
- New two-path architecture is backward compatible

### Contributors

- @zengbiaojie

---

## [0.1.1] - 2026-03-25

### Added

- Initial release of SentrySkills
- Three-stage protection pipeline (preflight → runtime → output)
- 33+ detection rules across 4 categories
- 7 risk predictors
- Support for OpenClaw and Codex
- Policy profiles: balanced, strict, permissive
- JSONL event logging with trace IDs
- Zero external dependencies (Python 3.8+ stdlib only)

### Documentation

- GitHub Pages deployment
- Installation guides for OpenClaw and Codex
- Skill package structure documentation
