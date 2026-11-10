#!/bin/sh
# Name the herdr tab after the first prompt of a session, unless it was renamed by hand.

set -eu

[ "${HERDR_ENV:-}" = "1" ] || exit 0
[ -n "${HERDR_PANE_ID:-}" ] || exit 0
command -v herdr >/dev/null 2>&1 || exit 0
command -v jq >/dev/null 2>&1 || exit 0

input="$(cat)"
session_id="$(printf '%s' "$input" | jq -r '.session_id // empty')"
prompt="$(printf '%s' "$input" | jq -r '.prompt // empty')"
[ -n "$session_id" ] || exit 0

marker_dir="${XDG_CACHE_HOME:-$HOME/.cache}/herdr-tab-title"
mkdir -p "$marker_dir"
marker="$marker_dir/$session_id"
[ ! -e "$marker" ] || exit 0

case "$prompt" in
  ''|/*) exit 0 ;;
esac

title="$(printf '%s' "$prompt" | tr 'A-Z' 'a-z' | tr -c 'a-z0-9\n' ' ' | awk '
  BEGIN {
    n = split("a an the and or but to of in on at for with from by is are was were be do does did can could would should will i me my we you your it its this that these those please just so how what why when where which who ok okay yeah yes now also then", w, " ")
    for (i = 1; i <= n; i++) skip[w[i]] = 1
  }
  {
    for (i = 1; i <= NF; i++) if (!skip[$i] && count < 2) words[++count] = $i
  }
  END {
    if (count == 2) print words[1] "-" words[2]
    else if (count == 1) print words[1]
  }')"
[ -n "$title" ] || exit 0
touch "$marker"

tab="$(herdr pane get "$HERDR_PANE_ID" | jq -r '.result.pane.tab_id // empty')"
[ -n "$tab" ] || exit 0
info="$(herdr tab get "$tab")"
label="$(printf '%s' "$info" | jq -r '.result.tab.label // empty')"
number="$(printf '%s' "$info" | jq -r '.result.tab.number // empty')"
[ "$label" = "$number" ] || exit 0

herdr tab rename "$tab" "$title" >/dev/null
