#!/usr/bin/env python3
"""
Claude Code PreToolUse hook adapter for SentrySkills.

Reads hook input from stdin, maps to SentrySkills input format,
runs the main security check, and returns an appropriate decision.

Exit codes (Claude Code convention):
  0 = allow
  2 = block (Claude Code surfaces the stdout message to the agent)
"""

from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Force UTF-8 output on Windows to avoid GBK codec errors
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Resolve project root relative to this script
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
HOOK_SCRIPT = SCRIPT_DIR / "self_guard_runtime_hook_template.py"
LOG_DIR = PROJECT_ROOT / "sentry_skill_log"

# High-risk tool names that should always be checked
HIGH_RISK_TOOLS = {"Bash", "Write", "Edit", "NotebookEdit"}

# Map tool name -> planned_action tag
TOOL_ACTION_MAP = {
    "Bash": "execute_command",
    "Write": "write_file",
    "Edit": "write_file",
    "NotebookEdit": "write_file",
    "WebFetch": "network_call",
    "WebSearch": "network_call",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def extract_prompt_from_tool(tool_name: str, tool_input: dict) -> str:
    """Build a short description of what the tool is about to do."""
    if tool_name == "Bash":
        return tool_input.get("command", "")[:500]
    if tool_name in ("Write", "Edit"):
        path = tool_input.get("file_path", "")
        content_preview = str(tool_input.get("new_string", tool_input.get("content", "")))[:200]
        return f"file: {path}\n{content_preview}"
    if tool_name in ("WebFetch", "WebSearch"):
        return tool_input.get("url", tool_input.get("query", ""))
    return json.dumps(tool_input)[:300]


def main() -> int:
    raw = sys.stdin.read().strip()
    if not raw:
        # No input, allow
        return 0

    try:
        hook_data = json.loads(raw)
    except json.JSONDecodeError:
        print("[SentrySkills] hook: could not parse stdin JSON, allowing", file=sys.stderr)
        return 0

    tool_name: str = hook_data.get("tool_name", "unknown")
    tool_input: dict = hook_data.get("tool_input", {})
    session_id: str = hook_data.get("session_id", str(uuid.uuid4())[:8])
    turn_id: str = f"hook-{uuid.uuid4().hex[:8]}"

    prompt_text = extract_prompt_from_tool(tool_name, tool_input)
    planned_action = TOOL_ACTION_MAP.get(tool_name, "tool_call")

    payload = {
        "session_id": session_id,
        "turn_id": turn_id,
        "project_path": str(PROJECT_ROOT),
        "user_prompt": prompt_text,
        "planned_actions": [planned_action],
        "candidate_response": "",
        "intent_tags": [f"tool:{tool_name}"],
    }

    policy_profile = os.environ.get("SENTRYSKILLS_PROFILE", "balanced")

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    input_path = LOG_DIR / f"hook_input_{turn_id}.json"
    unified_log_path: Optional[Path] = None

    try:
        input_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

        proc = subprocess.run(
            [
                sys.executable,
                str(HOOK_SCRIPT),
                str(input_path),
                "--policy-profile", policy_profile,
            ],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(PROJECT_ROOT),
        )

        if proc.returncode != 0:
            print(f"[SentrySkills] hook script error:\n{proc.stderr[-500:]}", file=sys.stderr)
            return 0  # fail-open: don't block on hook script errors

        # Only detailed unified log is used for decision.
        match = re.search(r"Unified log:\s*(.+)", proc.stdout or "")
        if match:
            unified_log_path = Path(match.group(1).strip())

        if not unified_log_path or not unified_log_path.exists():
            print("[SentrySkills] no unified log file found, allowing", file=sys.stderr)
            return 0

        result = json.loads(unified_log_path.read_text(encoding="utf-8"))
        final_node = result.get("final", {})
        meta_node = result.get("meta", {})

        final_action = final_node.get("action", "allow")
        trace_id = meta_node.get("trace_id", "?")
        matched_rules = final_node.get("matched_rules", [])
        reason_codes = final_node.get("reason_codes", [])
        explanation = final_node.get("explanation", "")

        if final_action == "block":
            msg = (
                f"\n[SentrySkills] BLOCKED this tool call.\n"
                f"   Tool    : {tool_name}\n"
                f"   Trace   : {trace_id}\n"
                f"   Matched : {matched_rules}\n"
                f"   Reason  : {reason_codes}\n"
                f"   Why     : {explanation}\n"
                f"   Action  : Refusing - do not proceed with this operation.\n"
            )
            print(msg)
            return 2  # block

        if final_action == "downgrade":
            print(
                f"[SentrySkills] WARNING: downgrade on {tool_name} "
                f"(trace={trace_id}, rules={matched_rules}, why={explanation})",
                file=sys.stderr,
            )
            return 0  # allow with warning

        return 0  # allow

    except subprocess.TimeoutExpired:
        print("[SentrySkills] hook timed out, allowing", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"[SentrySkills] hook exception: {e}, allowing", file=sys.stderr)
        return 0
    finally:
        # Clean up input file
        try:
            input_path.unlink(missing_ok=True)
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
