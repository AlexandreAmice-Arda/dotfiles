# Dotfiles

Cross-platform shell and desktop configuration managed by
[chezmoi](https://www.chezmoi.io/). Ubuntu renders a Sway desktop and macOS
renders an AeroSpace desktop from shared Tokyo Night theme, direction, and
workspace data. Supported generation baselines are Ubuntu 24.04+ and macOS
13+.

## Quick start

Install Git and chezmoi, configure access to GitHub, then run:

```sh
chezmoi init --apply --branch setup/sway-stable-trial-20260908 \
  git@github.com:AlexandreAmice/dotfiles.git
```

Choose `portable` for an ordinary machine. Choose `amice-workstation` only on
the original Ubuntu workstation. The branch flag remains necessary until this
desktop work is promoted to the repository's default branch.

Existing checkouts upgrading to this layout must run `chezmoi init` once to
regenerate the derived `isAmiceWorkstation` config value before applying.

Review changes before every real apply:

```sh
chezmoi diff
chezmoi apply --dry-run --verbose
chezmoi apply --verbose
desktop-doctor
```

## Dependencies

Ubuntu packages are declared in `packages/ubuntu.txt`:

```sh
chezmoi cd
./scripts/install-ubuntu --grant-backlight
./scripts/check-ubuntu
```

Omit `--grant-backlight` on systems without a laptop panel. If group
membership changes, log out completely before testing brightness.

macOS packages are declared in `Brewfile`:

```sh
chezmoi cd
brew bundle --file Brewfile
brew bundle check --file Brewfile
```

Grant AeroSpace Accessibility permission when macOS requests it. GitHub and
Atuin credentials, encryption keys, histories, and caches are deliberately
machine-local.

## Validation

Run the clean-room integration validator before committing:

```sh
chezmoi cd
./tests/validate-desktop
```

It materializes portable Linux, workstation Linux, and portable macOS homes;
checks profile and platform boundaries; parses rendered configuration; and
runs native validators and ShellCheck when available.

## Daily controls

- `Super+T` on Sway or `Option+T` on AeroSpace opens a plain terminal.
- Add `Shift` to open or resume an independent persistent tmux terminal.
- `Super+H/J/K/L` focuses Sway windows; `Super+1` through `Super+0` selects a
  workspace.
- `Super+/` is the exhaustive searchable Sway command and key reference.
- `Super+C` opens Sway system controls; `Super+Shift+X` locks the session.
- `Ctrl+R` searches Atuin history and inserts the result for review.

Starship gives the full untruncated directory its own line, Git state and
command duration the next, and a clean `❯` input marker the final line. SSH
sessions add a separate `user@hostname` line above the directory.

## Documentation

- [Architecture](docs/architecture.md)
- [Profiles and portability](docs/profiles.md)
- [Keybinding conventions](docs/keybindings.md)
- [Wallpaper assets and provenance](docs/wallpapers.md)
- [Roadmap and hardware qualification](docs/roadmap.md)
