#!/usr/bin/env python3
"""PreToolUse hook (Edit|Write): ask before introducing a multi-line comment.

Reads the hook JSON on stdin. If the edited/written text introduces a
multi-line comment block, emits a permissionDecision "ask" so the user is
prompted instead of the edit silently going through. A single-line comment,
however long, is never flagged.
"""
import json
import re
import sys

CODE_EXTS = {
    "c", "h", "cc", "cpp", "cxx", "hpp", "hh", "hxx",
    "rs", "go", "java", "kt", "swift",
    "js", "jsx", "ts", "tsx", "mjs", "cjs",
    "sh", "bash", "zsh",
    "css", "scss", "less",
    "html", "htm", "xml",
}

BLOCK_COMMENT_RE = re.compile(r"/\*.*?\n.*?\*/", re.S)
HTML_COMMENT_RE = re.compile(r"<!--.*?\n.*?-->", re.S)
STANDALONE_TRIPLE_RE = re.compile(
    r'^[ \t]*(\'\'\'|""").*?\n.*?^[ \t]*\1', re.S | re.M
)


def consecutive_line_comment_block(text, markers, min_lines=3):
    lines = text.split("\n")
    run = 0
    for line in lines:
        stripped = line.strip()
        is_comment = any(
            stripped.startswith(m) and not stripped.startswith("#!")
            for m in markers
        )
        if is_comment and stripped:
            run += 1
            if run >= min_lines:
                return True
        else:
            run = 0
    return False


def has_multiline_comment(text):
    if BLOCK_COMMENT_RE.search(text):
        return True
    if HTML_COMMENT_RE.search(text):
        return True
    if STANDALONE_TRIPLE_RE.search(text):
        return True
    if consecutive_line_comment_block(text, ("//", "#")):
        return True
    return False


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    tool_name = payload.get("tool_name")
    tool_input = payload.get("tool_input", {})

    if tool_name == "Edit":
        text = tool_input.get("new_string", "")
    elif tool_name == "Write":
        text = tool_input.get("content", "")
    else:
        return 0

    file_path = tool_input.get("file_path", "")
    ext = file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""
    if ext and ext not in CODE_EXTS:
        return 0

    if not text or not has_multiline_comment(text):
        return 0

    reason = (
        "This edit introduces a multi-line comment. House rule: prefer a "
        "single-line comment. Multi-line is fine when it's a genuinely "
        "longer explanation, ASCII/diagram art, something that relies on "
        "multi-line formatting, or a linter requires it — if that's the "
        "case, explain why in the chat before this is approved."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
