---
name: pr
description: Create a pull request with a Conventional Commits title and a short, plain-language body (a 2-sentence purpose plus a short list of the broad changes). Picks gh or fj automatically based on the repo's remotes. Use whenever the user asks to open, create, or send a PR.
---

# PR creation

Fixed order, every activation.

## 1. Pick the tool and remote

```bash
git remote -v
```

- A remote pointing at `mpluta.dev` → use `fj`, targeting that remote with `-R <remote-name>`.
- Else a remote pointing at `github.com` → use `gh` (auto-detects from `origin`; pass `--repo owner/repo` if there's more than one GitHub remote and it's ambiguous which one).
- Else: ask the user which remote/tool to use via `AskUserQuestion` — don't guess.

## 2. Determine the base branch

`git symbolic-ref --short refs/remotes/origin/HEAD`, else `main`, else `master`, else whatever the current branch tracks.

## 3. Draft the title — Conventional Commits

`type(scope): description`, following the `commit-style` skill's normal-repo rules (imperative, no trailing period, scope discovered from `git log` rather than invented). Base it on the PR as a whole, not any single commit in it.

## 4. Draft the body — two parts only

1. **Purpose** — max 2 sentences, plain language. No jargon, no AI-isms: banned words/phrases include "leverage", "seamless", "robust", "comprehensive", "ensure", "delve", "this PR introduces/enhances", and no emoji or em dashes used for dramatic effect. Just say what it's for.
2. **Changes** — a short bullet list of only the broad, significant changes. Use `git log <base>..HEAD --oneline` as a starting point, then condense and filter: skip tiny things (formatting, typo fixes, minor renames). Usually 2-5 bullets, not one per commit.

Nothing else goes in the body — no "Testing" section, no checklists, no generated boilerplate.

## 5. Show the draft, then create it

Print the title and body in chat before running anything — better to catch a mistake by reading plain content than by reading a raw shell command in a permission prompt. (The `ask-public-forge-action` hook will also gate the actual command as a second check.)

```bash
fj pr create --title "<title>" --body "<body>" --base <base> -R <remote>
# or
gh pr create --title "<title>" --body "<body>" --base <base>
```

## 6. Report back

Give the user the PR URL (both tools print it on success).
