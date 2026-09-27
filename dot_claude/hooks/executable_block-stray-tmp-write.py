#!/usr/bin/env python3
"""PreToolUse hook (Edit|Write|Bash): deny writes into /tmp or ~/tmp that
aren't scoped to this session's own tmp dir.

Allowed:
  - anything under /tmp/claude/<CLAUDE_CODE_SESSION_ID>/
  - anything whose path contains the session id (covers the harness's own
    /tmp/claude-<uid>/.../<session-id>/scratchpad dir)
Everything else under /tmp, and anything under $HOME/tmp, is denied for
Edit/Write, and best-effort flagged for Bash (redirects / common write
commands targeting either).
"""
import json
import os
import re
import sys

SESSION_ID = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
HOME = os.environ.get("HOME", "")
HOME_TMP = os.path.join(HOME, "tmp") if HOME else None


def is_tmp_path(path):
    if path.startswith("/tmp/") or path == "/tmp":
        return True
    if HOME_TMP and (path == HOME_TMP or path.startswith(HOME_TMP + "/")):
        return True
    return False


def is_allowed(path):
    if not is_tmp_path(path):
        return True  # not under /tmp or ~/tmp at all, not our concern
    if SESSION_ID and SESSION_ID in path:
        return True
    if path in ("/tmp", "/tmp/claude"):
        # bare container dirs, not a real stray write target
        return True
    return False


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


_PATH_ALT = r"/tmp/[^\s\"'`)|;&]+"
if HOME_TMP:
    _PATH_ALT = rf"(?:{_PATH_ALT}|{re.escape(HOME_TMP)}(?:/[^\s\"'`)|;&]*)?)"
TMP_PATH_RE = re.compile(_PATH_ALT)
WRITE_VERB_RE = re.compile(
    r"\b(touch|mkdir|cp|mv|tee|rsync|ln|install|dd|truncate|mktemp)\b"
)
REDIRECT_RE = re.compile(rf"(>>?|1>>?|2>>?)\s*({_PATH_ALT})")


def bash_offender(command):
    for m in REDIRECT_RE.finditer(command):
        p = m.group(2)
        if not is_allowed(p):
            return p
    if WRITE_VERB_RE.search(command):
        for p in TMP_PATH_RE.findall(command):
            if not is_allowed(p):
                return p
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    tool_name = payload.get("tool_name")
    tool_input = payload.get("tool_input", {})

    if tool_name in ("Edit", "Write"):
        path = tool_input.get("file_path", "")
        if path and not is_allowed(path):
            deny(
                f"{path} is a stray write under /tmp or ~/tmp, neither of "
                f"which is scoped to this session. Use "
                f"/tmp/claude/{SESSION_ID or '<session-id>'}/ instead."
            )
        return 0

    if tool_name == "Bash":
        command = tool_input.get("command", "")
        offender = bash_offender(command)
        if offender:
            deny(
                f"This command writes to {offender}, a stray path under "
                f"/tmp or ~/tmp, neither of which is scoped to this "
                f"session. Use /tmp/claude/{SESSION_ID or '<session-id>'}/ "
                "instead."
            )
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
