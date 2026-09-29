#!/usr/bin/env bash
# PreToolUse hook (Bash): ask before any gh/fj command that publishes
# something publicly visible (PR, issue, comment, review, release).
set -euo pipefail

input="$(cat)"
command="$(printf '%s' "$input" | jq -r '.tool_input.command // empty')"
[ -z "$command" ] && exit 0

# Strip quoted strings first, so a quoted argument value (e.g. a PR body
# mentioning "pr create") can't trigger a false match.
scan="$(printf '%s' "$command" | sed -E "s/'[^']*'//g; s/\"[^\"]*\"//g")"

printf '%s' "$scan" | grep -qE '\b(gh|fj)\b[^;&|]*\b(pr|pull|issue|release)\b[^;&|]*\b(create|comment|review|merge|close|reopen|edit)\b' || exit 0

reason='This command creates or edits something public-facing on a forge (PR, issue, comment, review, or release). Confirm this is intentional before it runs.'
jq -n --arg reason "$reason" \
  '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "ask", permissionDecisionReason: $reason}}'
