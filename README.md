# Dotfiles

Cross-platform shell and desktop configuration managed with
[chezmoi](https://www.chezmoi.io/). Ubuntu renders a Sway desktop and macOS
renders an AeroSpace desktop from the same direction, workspace, and Tokyo
Night theme data in `.chezmoidata.yaml`.

## Set up a new machine

Install Git and chezmoi, configure an SSH key for GitHub, and then run:

```sh
chezmoi init --apply git@github.com:AlexandreAmice/dotfiles.git
```

Initialization prompts once for the Git name and email to use on that machine.
Choose the `portable` desktop profile on ordinary machines. The
`amice-workstation` profile adds the saved external-monitor layout and personal
session applications used by the original Ubuntu workstation.
GitHub credentials are intentionally not stored in this repository. Install the
GitHub CLI and run `gh auth login` when GitHub API or HTTPS access is needed.

On macOS, these files assume Bash is the interactive shell. The managed
`.bash_profile` loads the shared `.profile` configuration.

### Ubuntu desktop dependencies

After cloning the source repository, install the reviewed Ubuntu package set:

```sh
chezmoi cd
./packages/install-ubuntu
chezmoi apply -v
desktop-doctor
```

The installer may add the current user to the `video` group for backlight
access. A complete logout/login is required when that membership changes.

### macOS desktop dependencies

Install Homebrew, then:

```sh
chezmoi cd
brew bundle --file Brewfile
chezmoi apply -v
desktop-doctor
```

Grant AeroSpace the Accessibility permission requested by macOS. AeroSpace
uses Option as its window-manager modifier; Sway uses Super. Both render their
direction and workspace bindings from `.chezmoidata.yaml`.

Ghostty and Foot both open the same persistent tmux session, so terminal state
survives terminal-window restarts and the interaction model is consistent on
both platforms. The terminal application itself remains platform-native.

### Validate the generator

Run this before committing desktop changes:

```sh
chezmoi cd
./packages/validate-desktop
```

It renders both platform targets from the shared data and validates every
checker available on the current machine. Platform-specific files are selected
by `.chezmoiignore`; secrets and hardware-specific values do not belong in the
shared schema.

## Daily use

### Core keys

- `Super+Enter`: open the platform terminal and attach tmux session `main`.
- `Ctrl+Alt+B`: split the terminal side-by-side.
- `Ctrl+Alt+V`: split the terminal top/bottom.
- `Ctrl+H/J/K/L`: focus a tmux pane.
- `Super+H/J/K/L`: focus a desktop window.
- `Super+1` through `Super+0`: select workspaces 1 through 10.
- Hardware brightness/volume keys: adjust the current display or audio sink.
- `Super+Alt+-` / `Super+Alt+=`: brightness fallback when a keyboard does not
  emit dedicated brightness keys.
- `Super+Alt+Space`: open the Ubuntu system menu.
- `Super+Shift+X`: lock the Ubuntu session.

The half-circle `◐` near the right end of Waybar opens wallpaper and terminal
opacity choices. The power icon beside it opens lock, suspend, logout, restart,
and shutdown actions.

Preview and apply source changes:

```sh
chezmoi diff
chezmoi apply -v
```

Capture a change made directly to a managed file, then commit it:

```sh
chezmoi add ~/.bashrc
chezmoi cd
git add .
git commit
git push
```

Pull and apply changes made on another machine:

```sh
chezmoi update -v
```

## Ubuntu Sway

The `portable` profile uses Ubuntu's standard Sway session and automatic output
placement. Hardware keys, the bar, notifications, appearance presets, locking,
and the terminal workflow are all part of that portable base.

### Original Intel/NVIDIA workstation trial

The `amice-workstation` profile additionally keeps the original saved monitor
roles and startup applications. It can install a separate GDM entry that uses
the Intel GPU for scan-out and leaves NVIDIA available for offloaded
applications:

```sh
chezmoi diff
chezmoi apply -v
~/.local/bin/sway-trial-system install
```

At GDM, select **Sway (Intel hybrid trial)**. Super is the window-manager
modifier, Super+/ opens the executable command palette, and all Super+Space
bindings are intentionally absent.

Super+Enter opens Foot attached to the persistent tmux session named `main`.
Super+Alt+Space opens the control center. Choose **Appearance** there—or click
the palette icon near the right side of Waybar—to switch Midnight, Dusk, and
Dawn wallpaper moods or select terminal opacity. Rotated Sway outputs receive
the portrait wallpaper automatically.

Run `desktop-doctor` after setup or whenever a desktop integration stops
working. It validates configuration, dependencies, wallpaper assets, and
backlight permission without changing the session.

If the trial session is unusable, press Ctrl+Alt+F3, log in, restart GDM, and
select Ubuntu. The system-level trial additions can be removed with:

```sh
~/.local/bin/sway-trial-system rollback
```

Do not add shell histories, SSH keys, license files, GitHub CLI configuration,
or plaintext tokens. Use `chezmoi diff` before every apply.
