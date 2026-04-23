# SentrySkills Roadmap

## Overview

This document outlines planned improvements and future directions for SentrySkills.

## 🔴 P0: Core Functionality (Critical)

### 1.1 Complete Two-Path Architecture Implementation ⚠️ IMPORTANT

**Current State**: Documentation describes two-path architecture, but implementation is incomplete.

**What's Missing**:
- Subagent spawning mechanism not implemented
- Async path always falls back to synchronous
- `index.jsonl` append-and-read logic not implemented

**Required Tasks**:
1. **Implement Subagent Spawning**
   ```python
   # In self_guard_runtime_hook_template.py
   def spawn_subagent_async(input_file: Path) -> None:
       """Spawn background process to run full pipeline."""
       cmd = [
           sys.executable, str(HOOK_SCRIPT),
           str(input_file),
           "--mode", "async",
           "--output", str(LOG_DIR / "index.jsonl")
       ]
       subprocess.Popen(cmd, cwd=PROJECT_ROOT)
   ```

2. **Implement Next-Turn Result Check**
   ```python
   def check_prior_subagent_result() -> Optional[Dict]:
       """Check if previous turn's subagent found a block."""
       if not LOG_DIR.exists():
           return None
       
       # Read latest entry from index.jsonl
       # Return if final_action == "block"
   ```

3. **Update Hook Logic**
   - Modify `claude_code_hook.py` to spawn subagent on LOW path
   - Add next-turn check at start of pipeline

**Estimated Effort**: 4-6 hours

---

### 1.2 Comprehensive Test Suite

**Current State**: No automated tests.

**Required Tasks**:

1. **Unit Tests** (`tests/test_*.py`)
   - `test_preflight.py` - Pre-flight decision logic
   - `test_runtime.py` - Runtime monitoring
   - `test_output_guard.py` - Output redaction
   - `test_detection_rules.py` - All 24+ rules
   - `test_predictive.py` - Risk predictors

2. **Integration Tests** (`tests/integration/`)
   - `test_full_pipeline.py` - End-to-end flow
   - `test_claude_code_hook.py` - PreToolUse integration
   - `test_two_path_flow.py` - HIGH vs LOW path routing

3. **Test Fixtures**
   ```python
   # tests/fixtures/
   ├── inputs/          # Sample user prompts
   ├── policies/        # Policy profiles
   └── expectations/    # Expected outputs
   ```

4. **Testing Framework**
   - Use `pytest` with Python 3.8+
   - Mock external dependencies
   - Parametrized tests for detection rules

**Example Test**:
```python
import pytest
from self_guard_runtime_hook_template import preflight_decision

@pytest.mark.parametrize("prompt,action,expected", [
    ("run ls", "execute_command", "downgrade"),  # HIGH
    ("list files", "read_file", "allow"),          # LOW
    ("ignore instructions", "execute_command", "block"),  # CRITICAL
])
def test_preflight_risk_assessment(prompt, action, expected):
    result = preflight_decision(prompt, [action], [], "normal", {})
    assert result["preflight_decision"] == expected
```

**Estimated Effort**: 8-12 hours

---

### 1.3 Performance Optimization

**Current State**: 30-100ms per check, which may slow down workflows.

**Optimization Targets**:

1. **Caching Detection Rules**
   ```python
   _rule_cache = {}
   def get_detection_rules_cached():
       if 'rules' not in _rule_cache:
           _rule_cache['rules'] = load_detection_rules()
       return _rule_cache['rules']
   ```

2. **Parallel Rule Execution**
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   def run_all_rules_parallel(text, rules):
       with ThreadPoolExecutor() as executor:
           results = list(executor.map(
               lambda r: check_rule(text, r), rules
           ))
       return results
   ```

3. **Lazy Pattern Compilation**
   ```python
   _compiled_patterns = {}
   def get_pattern(pattern_str):
       if pattern_str not in _compiled_patterns:
           _compiled_patterns[pattern_str] = re.compile(pattern_str, re.I)
       return _compiled_patterns[pattern_str]
   ```

**Target**: Reduce latency to <50ms per check

**Estimated Effort**: 4-6 hours

---

## 🟡 P1: Quality & Experience

### 2.1 GitHub Actions CI/CD

**Required Workflows** (`.github/workflows/`)

1. **`test.yml`** - Run tests on PR
   ```yaml
   name: Tests
   on: [push, pull_request]
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - uses: actions/setup-python@v4
           with:
             python-version: '3.8'
         - run: pip install pytest
         - run: pytest tests/
   ```

2. **`lint.yml`** - Code quality checks
   ```yaml
   name: Lint
   on: [push, pull_request]
   jobs:
     lint:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - run: pip install flake8 mypy
         - run: flake8 shared/scripts/
         - run: mypy shared/scripts/
   ```

3. **`release.yml`** - Automated PyPI releases (future)

**Estimated Effort**: 2-4 hours

---

### 2.2 Docker Support

**Files to Create**:

1. **`Dockerfile`** - Minimal image
   ```dockerfile
   FROM python:3.8-slim
   WORKDIR /app
   COPY . .
   ENTRYPOINT ["python", "shared/scripts/self_guard_runtime_hook_template.py"]
   ```

2. **`docker-compose.yml`** - Development environment
   ```yaml
   version: '3.8'
   services:
     sentryskills:
       build: .
       volumes:
         - ./.sentryskills/base:/app/.sentryskills/base
   ```

**Use Cases**:
- Standalone deployment
- Easy local testing
- Containerized security checks

**Estimated Effort**: 2-3 hours

---

### 2.3 Developer Experience

**Tools to Add**:

1. **`scripts/run_tests.sh`** - Quick test runner
   ```bash
   #!/bin/bash
   pytest tests/ -v --cov=shared/scripts
   ```

2. **`scripts/dev_hook.py`** - Development hook tester
   ```python
   """Test hook without running full agent."""
   import sys
   test_input = {
       "tool_name": sys.argv[1],
       "tool_input": {"command": sys.argv[2]}
   }
   # Run hook and show result
   ```

3. **`CONTRIBUTING.md`** - Contribution guidelines
4. **`scripts/benchmark.py`** - Performance profiler

**Estimated Effort**: 3-4 hours

---

## 🟢 P2: Ecosystem & Expansion

### 3.1 CLI Tool

**Proposed Interface**:
```bash
$ sentryskills check --policy balanced --input context.json
$ sentryskills test-rules --list
$ sentryskills benchmark --runs 100
$ sentryskills logs --tail 10
```

**Implementation**: Using `click` or `argparse`

**Estimated Effort**: 6-8 hours

---

### 3.2 Monitoring Dashboard

**Web Dashboard** (Optional):

1. **Real-time Event Viewer**
   - Live feed of security events
   - Filter by severity/category
   - Trace ID drill-down

2. **Analytics Page**
   - Block rate over time
   - Most triggered rules
   - Risk trends

3. **Configuration UI**
   - Edit policy profiles
   - Toggle detection rules
   - View logs

**Tech Stack**: Simple Flask/FastAPI app + SQLite

**Estimated Effort**: 16-24 hours

---

### 3.3 Plugin System

**Goal**: Allow custom detection rules and policies.

**Implementation**:
```python
# plugins/custom_rules.py
def custom_rule_check(text: str) -> bool:
    """User-defined rule."""
    return "FORBIDDEN_PATTERN" in text

# Register in policy.json
{
  "plugins": ["custom_rules.custom_rule_check"]
}
```

**Estimated Effort**: 8-12 hours

---

## 📋 Priority Matrix

| Task | Impact | Effort | Priority |
|------|--------|--------|----------|
| Complete two-path implementation | 🔴 High | Medium | **P0** |
| Add test suite | 🔴 High | Medium | **P0** |
| GitHub Actions CI | 🟡 Medium | Low | P1 |
| Docker support | 🟡 Medium | Low | P1 |
| Performance optimization | 🟡 Medium | Medium | P1 |
| Developer tooling | 🟡 Medium | Low | P1 |
| CLI tool | 🟢 Low | Medium | P2 |
| Monitoring dashboard | 🟢 Low | High | P2 |
| Plugin system | 🟢 Low | High | P2 |

---

## 🎯 Recommended Next Steps

### Immediate (This Week)

1. ✅ **Add Basic Tests** (4-6 hours)
   - Start with `test_detection_rules.py`
   - Add `test_preflight.py`
   - Get CI running

2. ✅ **Implement Subagent Logic** (4-6 hours)
   - Complete async path
   - Update hook script
   - Test end-to-end

### Short-term (This Month)

3. **Set Up GitHub Actions** (2-3 hours)
4. **Add Dockerfile** (1-2 hours)
5. **Performance Optimization** (4-6 hours)

### Long-term (This Quarter)

6. **CLI Tool** (6-8 hours)
7. **Enhanced Documentation** (4-6 hours)
   - API reference
   - Video tutorials
   - Contribution guide

---

## 📊 Success Metrics

**Technical Metrics**:
- ✅ Test coverage > 80%
- ✅ CI passes on all PRs
- ✅ Latency < 50ms per check
- ✅ Zero external dependencies maintained

**Adoption Metrics**:
- ⭐ GitHub stars growth
- 📥 Download/clone count
- 🐛 Issue resolution time
- 📖 Documentation views

---

## 🔄 Version Roadmap

- **v0.1.2** (Current) - Two-path architecture + Claude Code
- **v0.1.3** - Complete async path + test suite
- **v0.2.0** - CLI tool + Docker + CI/CD
- **v0.3.0** - Plugin system + monitoring dashboard
- **v1.0.0** - Production-ready, enterprise features

---

## 💡 Discussion Points

1. **Subagent Implementation**: Should we use Python's `subprocess.Popen` or explore async frameworks?

2. **Testing Strategy**: Focus on unit tests first, or integration tests?

3. **Performance**: Is 50ms target realistic? Should we profile first?

4. **Breaking Changes**: When to introduce them? (Suggest v1.0.0)

5. **Dependencies**: Stay zero-dep forever, or allow optional deps for testing?

---

**Last Updated**: 2026-04-01  
**Status**: Draft - Open for feedback
