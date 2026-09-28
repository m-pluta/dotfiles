## Scratch/temp files

Use `/tmp/claude/$CLAUDE_CODE_SESSION_ID/` for scratch files, not a bare `/tmp` or `~/tmp` path — a hook denies those.

## Config management

My dotfiles and config in `~` (including `~/.claude`) are managed by chezmoi (source: `~/.local/share/chezmoi`). After changing any of them, run `chezmoi status` and sync it (`chezmoi add` new files, `chezmoi forget` deleted/renamed ones).
