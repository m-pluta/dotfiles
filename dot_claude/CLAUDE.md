## Commit messages

Always use the `commit-style` skill when writing any git commit message, in any repo.

## Kernel patch series

For kernel patch work (infer the tree from the task, ask if unsure), use one worktree per series and one branch per version:

- Ask me for the worktree name (`<name>` below), then use `<repo>/.worktrees/<name>`. All work happens there. The main checkout stays a clean copy of upstream: never edit, commit or build in it.
- Branches are `<name>/v1`, `<name>/v2`... (`<n>` below is the version number), each new one cut from the last. This replaces the worktree skill's branch-name question.
- Before creating, check `git branch --list '<name>/*'` is empty and no branch is named exactly `<name>` (it would block `<name>/v1`).
- Once a version has been emailed to the mailing list as patches, tag it `sent-<name>-v<n>` and never rewrite that branch.

## Config management

My dotfiles and config in `~` (including `~/.claude`) are managed by chezmoi (source: `~/.local/share/chezmoi`). After changing any of them, run `chezmoi status` and sync it (`chezmoi add` new files, `chezmoi forget` deleted/renamed ones). Commit and push the chezmoi source repo after each independent change, rather than batching unrelated changes into one commit.
