#!/usr/bin/env bash
# PreToolUse hook (Bash, Write, Edit): deny any call whose text has a Claude or
# Anthropic attribution line. It covers commit messages and PR bodies written
# by a command or saved to a file first.
set -euo pipefail

input="$(cat)"

case "$(printf '%s' "$input" | jq -r '.tool_name // empty')" in
  Bash) text="$(printf '%s' "$input" | jq -r '.tool_input.command // empty')" ;;
  Write) text="$(printf '%s' "$input" | jq -r '.tool_input.content // empty')" ;;
  Edit) text="$(printf '%s' "$input" | jq -r '.tool_input.new_string // empty')" ;;
  *) exit 0 ;;
esac

# The hook scripts hold the patterns, so editing them is allowed.
file="$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')"
case "$file" in
  */.claude/hooks/* | */chezmoi/dot_claude/hooks/*) exit 0 ;;
esac

printf '%s' "$text" | grep -qiE 'generated with \[?claude code\]?|claude\.com/claude-code|co-authored-by:[[:space:]]*claude|noreply@anthropic\.com' || exit 0

reason='This text has a Claude or Anthropic attribution line (Generated with Claude Code, Co-Authored-By: Claude). Remove it and try again.'
jq -n --arg reason "$reason" \
  '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $reason}}'
