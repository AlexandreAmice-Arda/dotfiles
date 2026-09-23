# Dotfiles

Cross-platform shell and desktop configuration managed with
[chezmoi](https://www.chezmoi.io/). Ubuntu renders a Sway desktop and macOS
renders an AeroSpace desktop from the same direction, workspace, and Tokyo
Night theme data in `.chezmoidata.yaml`.

Generation baseline: Ubuntu 24.04 or newer and macOS 13 or newer. The current
hardware-qualified set is Ubuntu 24.04; macOS is generator-validated but still
needs its first hardware qualification. These bounds and qualification lists
live under `desktop.support` in `.chezmoidata.yaml`, so the claim cannot drift
silently from the implementation.

## Set up a new machine

Install Git and chezmoi, configure an SSH key for GitHub, and then run:

```sh
chezmoi init --apply --branch setup/sway-stable-trial-20260908 \
  git@github.com:AlexandreAmice/dotfiles.git
```

The desktop generator currently lives on that named setup branch. Remove the
`--branch` argument after it is deliberately promoted to the repository's
default branch; until then, an unqualified init would install the older main
branch instead.

Initialization prompts once for the Git name and email to use on that machine.
Choose the `portable` desktop profile on ordinary machines. The
`amice-workstation` profile adds the saved external-monitor layout and personal
session applications used by the original Ubuntu workstation.
GitHub credentials are intentionally not stored in this repository. Install the
GitHub CLI and run `gh auth login` when GitHub API or HTTPS access is needed.

The shared shell environment works with Ubuntu's Bash and macOS's default Zsh.
Homebrew's shell environment is loaded explicitly so GUI-launched Ghostty can
find tools on both Apple Silicon and Intel Macs.

Chezmoi also installs checksummed Linux releases of Starship, Atuin, Neovim,
and the tree-sitter CLI plus the JetBrainsMono Nerd Font. Ubuntu supplies fzf,
zoxide, fd, and Kanshi through apt; Homebrew supplies the corresponding shell
and editor tools on macOS. Small wrappers prefer native package-manager
binaries and use the pinned Linux releases as a fallback.

### Ubuntu desktop dependencies

After cloning the source repository, install the reviewed Ubuntu package set:

```sh
chezmoi cd
./packages/install-ubuntu --grant-backlight
chezmoi apply -v
./packages/check-ubuntu
desktop-doctor
```

`--grant-backlight` adds the current user to the `video` group only when a
backlight device exists. A complete logout/login is required when that
membership changes. Omit the flag on desktops that have no controllable laptop
panel. `check-ubuntu` verifies every package in the reviewed manifest;
`desktop-doctor` then checks that the commands, services, personal workstation
applications, and hardware integrations actually work.

### macOS desktop dependencies

Install Homebrew, then:

```sh
chezmoi cd
brew bundle --file Brewfile
chezmoi apply -v
desktop-doctor
```

Run `brew bundle check --file Brewfile` at any time to verify the macOS package
manifest without changing the machine.

Grant AeroSpace the Accessibility permission requested by macOS. AeroSpace
uses Option as its window-manager modifier; Sway uses Super. Both render their
direction and workspace bindings from `.chezmoidata.yaml`.

Launch AeroSpace and Ghostty once after installation. If a legacy
`~/.aerospace.toml` or a Ghostty config under `~/Library/Application Support`
already exists, move it aside so it cannot override the managed XDG config.
AeroSpace provides its own virtual workspaces; separate Mission Control Spaces
are unnecessary for this setup.

### Atuin account setup

The repository manages Atuin's safe behavior, not its account, encryption key,
history database, or session. On the first computer, register interactively so
the password never appears in the command line:

```sh
atuin register -u YOUR_USERNAME -e YOUR_EMAIL
atuin key
```

Store the displayed encryption key in a password manager. Before importing,
review the current shell history (`~/.bash_history` or `~/.zsh_history`) for
credentials, then run:

```sh
atuin import auto
atuin sync
```

On later computers, run `atuin login -u YOUR_USERNAME` and enter the password
and saved encryption key at the prompts. `desktop-doctor` warns when the local
key or account state is missing. Atuin sync uses its hosted service; the
managed config filters common credential forms and commands beginning with a
space, but reviewing old history before importing remains essential.

### Neovim and LazyVim

Run `nvim` to open the managed LazyVim setup. The small, editable configuration
under `~/.config/nvim` is portable; downloaded plugins, Mason tools, caches,
logs, and session state stay local to each computer. Plugin versions are
reproducible through the managed `lazy-lock.json`.

Inside Neovim, `:Lazy` opens the plugin manager and `:checkhealth lazyvim`
checks the required editor toolchain. LazyVim may warn that `lazygit` is absent;
that integration is optional and is not currently part of this baseline.

Ghostty and Foot open a plain native shell by default, which keeps SSH ownership
unambiguous: a terminal split is never silently presented as part of a remote
session. The shifted terminal shortcut explicitly runs `terminal-main`, which
resumes the oldest detached `terminal-N` tmux session or creates the next
numbered session when every existing one is in use.

Pinned tmux-resurrect and tmux-continuum plugins save persistent terminal
structure every five minutes and rebuild sessions, windows, panes, layouts,
and working directories when the first explicit tmux terminal opens after a
reboot. The terminal application itself remains platform-native. Run
`terminal-main --shared` when two terminal windows should intentionally share
the legacy `main` session.

Process memory cannot survive a reboot, so commands are never replayed
automatically and pane text is not persisted. This avoids rerunning stale or
dangerous commands and storing terminal secrets. Resume stateful applications
with their own mechanism after tmux restores—for Codex, run `codex resume` (or
`codex resume --last`). In tmux, `Ctrl+B`, then `Ctrl+S` forces a snapshot and
`Ctrl+B`, then `Ctrl+R` restores one manually.

### Validate the generator

Run this before committing desktop changes:

```sh
chezmoi cd
./packages/validate-desktop
```

It materializes portable Ubuntu, workstation Ubuntu, and portable macOS homes,
then validates Sway, Foot, systemd units, TOML, JSON, shell syntax, platform
boundaries, and known workstation-data leaks. ShellCheck and native platform
parsers run when installed. Platform-specific files are selected by
`.chezmoiignore`; secrets and hardware-specific values do not belong in the
shared schema.

Machine-specific shell exports belong in the unmanaged `~/.bashrc.local` hook,
not as absolute home paths inside a portable template.

### Where things live

- `.chezmoidata.yaml`: shared theme, key directions, workspaces, power timings,
  and the explicitly personal workstation display inventory.
- `.chezmoiexternal.toml.tmpl`: pinned Linux Starship, Atuin, Neovim,
  tree-sitter CLI, Nerd Font, and tmux plugin releases with SHA-256 checksums.
- `private_dot_config/sway/config.tmpl`: short entry point; readable fragments
  live under `sway/conf.d/` by topic.
- `private_dot_config/kanshi/`: hot-plug monitor profiles for the original
  workstation only.
- `private_dot_config/{starship.toml,atuin/,nvim/}`: portable prompt, history,
  and LazyVim configuration; generated account, plugin, cache, and editor state
  remain deliberately excluded.
- `private_dot_config/systemd/user/`: supervised Sway-session services.
- `private_dot_config/{waybar,swaync,wofi,wlogout,gtklock}/`: one focused config
  and/or stylesheet per component.
- `private_dot_local/bin/`: cross-component commands such as locking, session
  actions, terminal startup, and the desktop doctor.
- `packages/`: reviewed dependency manifests and source validation.

## Daily use

### Core keys

- `Super+T` on Sway or `Option+T` on AeroSpace: open a plain terminal without
  tmux. This is the predictable choice for SSH connections.
- `Super+Shift+T` on Sway or `Option+Shift+T` on AeroSpace: open or resume an
  independent persistent local tmux session.
- `terminal-main --shared`: explicitly attach the legacy shared `main` tmux
  session when mirrored clients are intentional.
- `Super+Shift+D` (workstation profile): launch and arrange the personal
  project applications; they do not open merely because Sway started.
- `Ctrl+Alt+B`: split an explicit tmux terminal side-by-side.
- `Ctrl+Alt+V`: split an explicit tmux terminal top/bottom.
- `Ctrl+Backspace`: erase the previous shell word; it is not consumed by tmux.
- `Super+H/J/K/L`: focus a desktop window.
- `Super+1` through `Super+0`: select workspaces 1 through 10.
- Hardware brightness/volume keys: adjust the current display or audio sink.
- `Super+Alt+-` / `Super+Alt+=`: brightness fallback when a keyboard does not
  emit dedicated brightness keys.
- `Super+C`: open the Ubuntu graphical system controls.
- `Super+Shift+X`: lock the Ubuntu session.

On Ubuntu the session locks after 10 minutes idle, powers displays down after
15 minutes, and locks then suspends after 30 minutes only when the system
battery is discharging. The three values are together under `desktop.power` in
`.chezmoidata.yaml`.

The half-circle `◐` near the right end of Waybar opens wallpaper and terminal
opacity choices. The power icon beside it opens lock, suspend, logout, restart,
and shutdown actions.

The Ubuntu system menu is a graphical front door to standalone Sway-friendly
tools: NetworkManager connections, Blueman Bluetooth, pavucontrol audio,
wdisplays outputs, and power profile selection. It deliberately avoids GNOME
Settings panels, whose behavior depends on services from a full GNOME session.

### Shell navigation and history

- `z DIRECTORY_FRAGMENT`: jump to a frequently used directory with zoxide.
- `zi`: choose a known directory interactively through fzf.
- `Ctrl+T`: insert a fuzzy-selected file or directory into the command line.
- `Alt+C`: change into a fuzzy-selected directory.
- `Ctrl+R`: search global Atuin history. Enter inserts the selected command for
  review; press Enter again at the prompt to run it.
- Up arrow: ordinary shell history, intentionally unchanged by Atuin.

Inside tmux, Atuin opens an 80% by 60% popup when supported and otherwise uses
the normal terminal interface. Starship shows the current directory, Git
state, detected language/project context, command duration, failures, and time;
username and hostname appear only for remote shells.

Preview and apply source changes:

```sh
chezmoi diff
chezmoi apply -v
```

Capture a change made directly to a managed file, then commit it:

```sh
chezmoi add ~/.bashrc
chezmoi cd
git diff
git add dot_bashrc.tmpl
git diff --cached
git commit
git push
```

Pull and apply changes made on another machine:

```sh
chezmoi update -v
```

## Ubuntu Sway

The `portable` profile uses Ubuntu's standard Sway session and automatic output
placement. Use wdisplays for an ad-hoc layout. Hardware keys, the bar,
notifications, appearance presets, locking, and the terminal workflow are all
part of that portable base.

### Original Intel/NVIDIA workstation trial

The `amice-workstation` profile additionally keeps the original saved monitor
roles in hot-plug-aware Kanshi profiles, automatic cloud and messaging
applications, and an explicit launcher for project applications. The office,
home, and laptop-only profiles keep the laptop panel enabled and reapply the
correct landscape/portrait wallpaper after layout changes. It can install a
separate GDM entry that uses the Intel GPU for scan-out and leaves NVIDIA
available for offloaded applications:

```sh
chezmoi diff
chezmoi apply -v
~/.local/bin/sway-trial-system install
```

At GDM, select **Sway (Intel hybrid trial)**. Super is the window-manager
modifier and Super+/ opens the executable command palette. Because Super,
Space, and Enter share a Kinesis Advantage2 thumb cluster, no Super chord uses
Space or Enter.

Sway starts desktop infrastructure, pCloud, Signal, and Slack at login; the two
messaging applications are supervised user services with journal logs, and
their windows are collected on workspace 10. Press Super+Shift+D when
you want VS Code and the arranged Chrome project workspaces; the same action is
available in the Super+/ command palette.
Super+T opens a plain Foot shell. Super+Shift+T opens Foot with its own
persistent tmux session, resuming a detached terminal before creating another
one. The shared `main` session remains in the Super+/ command palette when
mirrored clients are intentional. Super+C opens the control center.
Choose **Appearance** there—or click the palette icon near the right side of
Waybar—to switch Midnight, Dusk, and Dawn wallpaper moods or select terminal
opacity. Rotated Sway outputs receive the portrait wallpaper automatically.

Run `desktop-doctor` after setup or whenever a desktop integration stops
working. It validates configuration, dependencies, wallpaper assets, and
backlight and battery policy without changing the session. Sway session
components (Waybar, SwayNC, swayidle, NetworkManager applet, and the polkit
agent) are supervised as user services and stop together when Sway exits.

If the trial session is unusable, press Ctrl+Alt+F3, log in, restart GDM, and
select Ubuntu. The system-level trial additions can be removed with:

```sh
~/.local/bin/sway-trial-system rollback
```

Do not add shell histories, SSH keys, license files, GitHub CLI configuration,
or plaintext tokens. Use `chezmoi diff` before every apply.
