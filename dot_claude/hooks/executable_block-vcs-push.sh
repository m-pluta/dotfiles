#!/usr/bin/env bash
# PreToolUse hook (Bash): ask before any git/jj push to a remote.
set -euo pipefail

input="$(cat)"
command="$(printf '%s' "$input" | jq -r '.tool_input.command // empty')"
[ -z "$command" ] && exit 0

# Strip quoted strings first, so a quoted argument value (e.g. a commit
# message containing the word "push") can't trigger a false match.
scan="$(printf '%s' "$command" | sed -E "s/'[^']*'//g; s/\"[^\"]*\"//g")"

# Strip git send-email invocations before matching, so send-email (which
# mails patches rather than pushing to a remote) never trips this hook.
scan="$(printf '%s' "$scan" | sed -E 's/\bgit([^;&|]*)\bsend-email\b[^;&|]*//g')"

matched=0
if printf '%s' "$scan" | grep -qE '\bgit\b[^;&|]*\bpush\b'; then
  matched=1
elif printf '%s' "$scan" | grep -qE '\bgit-push\b'; then
  matched=1
elif printf '%s' "$scan" | grep -qE '\bjj\b[^;&|]*\b(git[[:space:]]+push|push|git[[:space:]]+submit|submit)\b'; then
  matched=1
elif printf '%s' "$scan" | grep -qE '\breceive-pack\b'; then
  matched=1
fi

[ "$matched" -eq 0 ] && exit 0

reason='This command looks like it pushes to a remote (git push / jj git push / jj submit / receive-pack). Confirm this is intentional before it runs.'
jq -n --arg reason "$reason" \
  '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "ask", permissionDecisionReason: $reason}}'
