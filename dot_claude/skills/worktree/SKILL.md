---
name: worktree
description: Create a new git worktree for a task, with a guided prompt/name/branch/repo flow, then open it in a new zellij tab with a Claude session on the left and a plain terminal on the right. Use whenever the user asks to create, start, or spin up a new worktree, or whenever a task is substantial or isolated enough that Claude thinks offering a fresh worktree is worth suggesting.
---

# Worktree creation

Fixed order, every activation. Repos live under `~/dev` (search depth 3, to tolerate e.g. `~/dev/homelab/<repo>`). Worktrees go in `<repo>/.worktrees/<name>`.

## 0. Confirm first

If the user explicitly asked for a worktree, that's confirmation — go to step 1.

If Claude is the one suggesting it, stop and use `AskUserQuestion` with a Yes/No question ("Want me to set up a new worktree for this?") before running anything else — no commands, no git. A "No" ends the skill here.

## 1. Get the task prompt

Ask in plain chat what they want done (skip if already stated clearly). Keep it verbatim — used for name/branch suggestions and, with the suffix from step 5, as the new session's opening prompt.

## 2. One `AskUserQuestion` call: repo, worktree name, branch name

```bash
find ~/dev -maxdepth 3 -type d -name .git 2>/dev/null | sed 's|/\.git$||' | grep -v '/\.worktrees/'
```

(Exclude `.worktrees` — a worktree is itself a `.git` checkout and would show up as a fake repo.) Default to the current repo if cwd is inside one of these; otherwise list up to 4, current/most-recent first.

Generate 2-3 kebab-case suggestions each for name and branch from the task prompt (independent fields, can share a top suggestion). Ask one `AskUserQuestion` with three questions: Repo / Worktree name / Branch name (options as above; "Other" is automatic).

## 3. Branch + base ref

```bash
git -C <repo> rev-parse --verify --quiet "refs/heads/<branch>"
```

If it exists, ask whether to reuse it (drop `-b` below) or rename. Base ref — don't ask, just pick: `git -C <repo> symbolic-ref --short refs/remotes/origin/HEAD`, else `main`, else `master`, else the repo's currently checked-out branch.

## 4. Create the worktree

Ensure `<repo>/.gitignore` has a `.worktrees/` line (add if missing), then:

```bash
git -C <repo> worktree add -b <branch> <repo>/.worktrees/<name> <base-ref>
```

(Drop `-b <branch>` and pass `<branch>` as the commit-ish if reusing an existing branch.)

## 5. Build the opening prompt

Append this fixed suffix to the step-1 prompt, verbatim, every time:

```
<task prompt>

Before doing any work, explain in plain terms your understanding of the problem and what you plan to do to fix it. Do not start implementing until you've given that explanation.
```

## 6. Open the zellij tab

```bash
[ -n "$ZELLIJ" ] && echo IN_ZELLIJ
```

Not in zellij: skip to step 7, nothing to open.

In zellij: use one atomic KDL layout file (verified — chained `new-tab`/`new-pane` CLI calls are unreliable: `new-pane --cwd` silently ignored, new tab didn't reliably get focus):

```kdl
layout {
    tab name="<worktree-name>" {
        pane split_direction="vertical" {
            pane command="claude" cwd="<worktree-path>" focus=true {
                args "<prompt from step 5, KDL-escaped>"
            }
            pane cwd="<worktree-path>"
        }
        pane size=1 borderless=true {
            plugin location="zellij:compact-bar"
        }
    }
}
```

Both panes same `cwd` (the worktree path). The `compact-bar` pane is required — omit it and the tab loses its status bar, since a custom layout fully replaces the default rather than extending it.

KDL-escape the prompt for `args`, in order: `\` → `\\`, `"` → `\"`, newline → literal `\n`.

Write to `/tmp/claude/$CLAUDE_CODE_SESSION_ID/<worktree-name>-layout.kdl`, then:

```bash
zellij action new-tab --layout /tmp/claude/$CLAUDE_CODE_SESSION_ID/<worktree-name>-layout.kdl
```

## 7. Report back

Repo, worktree path, branch (new or reused), and whether/why a tab was opened.
