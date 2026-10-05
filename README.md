# Dotfiles

Cross-platform shell and desktop configuration managed by
[chezmoi](https://www.chezmoi.io/). Ubuntu renders a Sway desktop and macOS
renders an AeroSpace desktop from shared Tokyo Night theme, direction, and
workspace data. Supported generation baselines are Ubuntu 24.04+ and macOS
13+.

## Quick Start

1. Install Git, gh, and chezmoi.

   ```sh
   sudo apt install git gh
   sudo snap install chezmoi --classic
   ```

2. Log into GitHub.

   ```sh
   gh auth login
   ```

3. Get the dotfiles and follow the system prompts.

   ```sh
   chezmoi init AlexandreAmice/dotfiles
   ```

4. Navigate to the chezmoi source, install software, and apply chezmoi.

   ```sh
   cd "$(chezmoi source-path)"
   ./scripts/install-ubuntu
   chezmoi diff
   chezmoi apply --verbose
   ```

   Use `./scripts/install-ubuntu --grant-backlight` instead on a laptop with
   a real backlight; omit the flag in a VM or on a desktop.

5. Optionally log into Atuin. This requires the Atuin encryption key.

   ```sh
   atuin login
   ```

6. Check the installation.

   ```sh
   desktop-doctor
   ./tests/validate-desktop
   ```

7. Log out completely and log back into Sway.

Atuin credentials, encryption keys, and history are deliberately not deployed.

Choose `portable` for an ordinary machine. Choose `amice-workstation` only on
the original Ubuntu workstation.

Existing checkouts upgrading to this layout must run `chezmoi init` once to
regenerate the derived `isAmiceWorkstation` config value before applying.

### macOS

Install the Homebrew dependencies, apply, and verify:

```sh
cd "$(chezmoi source-path)"
brew bundle --file Brewfile
./scripts/install-codex
chezmoi diff
chezmoi apply --verbose
desktop-doctor
```

Grant AeroSpace Accessibility permission when macOS requests it. GitHub
credentials, application histories, and caches are deliberately machine-local.

Codex is installed automatically during the software-install step. Run
`codex` once to sign in and create `~/.codex`; credentials and session state
remain machine-local. Herdr is installed as a pinned external on Linux and
through Homebrew on macOS. After that first Codex launch, install Herdr's
session hook while preserving other Codex hooks:

```sh
cd "$(chezmoi source-path)"
./scripts/install-agent-integrations
```

On Ubuntu, the installer builds pinned Foot 1.28 and fcft 3.3.1 source releases
and installs Foot under `/usr/local`. Ubuntu 24.04's Foot 1.16 duplicates Enter
and Backspace release events when Herdr enables Kitty keyboard reporting. The
apt package remains installed as a system fallback, while the normal
`/usr/local/bin` path selects the fixed version.

The Ubuntu installer also installs pinned nwg-displays 0.4.4. Open Displays
from `Super+C` to arrange screens and assign workspaces. Closing the GUI saves
the connected-monitor profile locally and updates the Chezmoi source; later
workspace moves are recorded automatically by the Sway layout service.

## Validation

Run the clean-room integration validator before committing:

```sh
cd "$(chezmoi source-path)"
./tests/validate-desktop
```

It materializes portable Linux, workstation Linux, and portable macOS homes;
checks profile and platform boundaries; parses rendered configuration; and
runs native validators and ShellCheck when available.

## Daily controls

- `Super+T` on Sway or `Option+T` on AeroSpace opens a plain terminal.
- Add `Shift` to open or resume an independent persistent tmux terminal.
- Add left Ctrl instead to open the agent-aware Herdr workspace. Herdr and
  tmux are separate terminal modes and must not be nested.
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
- [Herdr agent workspaces](docs/herdr.md)
- [Wallpaper assets and provenance](docs/wallpapers.md)
- [Roadmap and hardware qualification](docs/roadmap.md)
