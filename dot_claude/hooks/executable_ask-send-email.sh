#!/usr/bin/env bash
# PreToolUse hook (Bash): ask before any git send-email invocation.
set -euo pipefail

input="$(cat)"
command="$(printf '%s' "$input" | jq -r '.tool_input.command // empty')"
[ -z "$command" ] && exit 0

# Strip quoted strings first, so a quoted argument value (e.g. a commit
# message mentioning "git send-email") can't trigger a false match.
scan="$(printf '%s' "$command" | sed -E "s/'[^']*'//g; s/\"[^\"]*\"//g")"

printf '%s' "$scan" | grep -qE '\bgit\b[^;&|]*\bsend-email\b|\bgit-send-email\b' || exit 0

reason='This command sends patches by email (git send-email). Confirm this is intentional before it runs.'
jq -n --arg reason "$reason" \
  '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "ask", permissionDecisionReason: $reason}}'
