# dotfiles

Pull and apply on a new machine:

```
chezmoi init --apply ssh://forgejo@git.mpluta.dev/mikey/dotfiles.git
```

Or, from the GitHub mirror:

```
chezmoi init --apply https://github.com/m-pluta/dotfiles.git
```

Already initialized elsewhere? Pull and apply updates:

```
chezmoi update
```

## What's tracked

Bash config (`.bashrc`, `.bash_aliases`, `.bash_functions`), `.gitconfig`, SSH/git/helix/kitty/alacritty/zellij/starship config under `.config`, and Claude Code config (`.claude`: settings, hooks, skills).
