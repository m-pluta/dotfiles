#!/usr/bin/env python3
"""Prompt cache countdown for the ccstatusline custom-command widget.

Reads the statusline JSON on stdin, finds the last cache-touching assistant
message in the transcript, and prints the time left on the cache coloured by
how much remains. Mirrors the logic of ccstatusline's built-in cache-timer.
"""
import json
import sys
import time
import unicodedata
from datetime import datetime

TTL = 3600
SAFETY_MARGIN = 5
TAIL_BYTES = 32768

# (minimum seconds remaining, 256-colour code), checked in order
COLOURS = [(20 * 60, 208), (5 * 60, 220), (0, 134)]
# (minimum seconds remaining, icon), a draining circle in quarters of the TTL
ICONS = [(TTL * 3 // 4, "\u25cf"), (TTL // 2, "\u25d5"), (TTL // 4, "\u25d1"), (0, "\u25d4")]
HOT = (203, "\U0001F525HOT")
BLINK_BELOW = 5 * 60
BLINK_OFF = 244
COLD = (33, "❄ COLD")


WIDTH = 7


def cells(text):
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)


def paint(code, text):
    # Pad inside the colour codes, the widget trims whitespace around the output
    text += " " * (WIDTH - cells(text))
    return f"\x1b[38;5;{code}m{text}\x1b[39m"


def read_tail(path, size):
    with open(path, "rb") as f:
        f.seek(0, 2)
        end = f.tell()
        n = min(size, end)
        f.seek(end - n)
        return f.read(n).decode("utf-8", "replace"), n == end


def has_cache_activity(entry):
    usage = (entry.get("message") or {}).get("usage")
    if not usage:
        return True
    return (usage.get("cache_read_input_tokens") or 0) + (usage.get("cache_creation_input_tokens") or 0) > 0


def scan(text):
    """Return ('working', None), ('assistant', epoch) or None if undecided."""
    finished = False
    for line in reversed(text.split("\n")):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if entry.get("isSidechain") is True:
            continue
        kind = entry.get("type")
        if kind == "assistant":
            finished = True
            ts = entry.get("timestamp")
            if entry.get("isApiErrorMessage") is not True and has_cache_activity(entry) and ts:
                try:
                    return "assistant", datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
                except ValueError:
                    pass
        elif kind == "user" and not finished:
            return "working", None
    return None


def state(path):
    size = TAIL_BYTES
    while True:
        text, complete = read_tail(path, size)
        if not text:
            return None
        found = scan(text)
        if found:
            return found
        if complete:
            return None
        size *= 2


def main():
    try:
        path = json.load(sys.stdin).get("transcript_path")
        found = state(path) if path else None
    except (OSError, ValueError):
        return
    if not found:
        return
    kind, ts = found
    if kind == "working":
        print(paint(*HOT))
        return
    remaining = TTL - SAFETY_MARGIN - (time.time() - ts)
    if remaining <= 0:
        print(paint(*COLD))
        return
    code = next(c for floor, c in COLOURS if remaining > floor or floor == 0)
    if remaining <= BLINK_BELOW and int(time.time()) % 2:
        code = BLINK_OFF
    icon = next(i for floor, i in ICONS if remaining > floor or floor == 0)
    print(paint(code, f"{icon} {int(remaining // 60):>2}:{int(remaining % 60):02d}"))


main()
