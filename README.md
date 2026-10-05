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
   chezmoi init AlexandreAmice-Arda/dotfiles
   ```

4. Navigate to the chezmoi source, install software, and apply chezmoi.

   ```sh
   cd "$(chezmoi source-path)"
   ./scripts/install
   chezmoi diff
   chezmoi apply --verbose
   ```

   Use `./scripts/install --grant-backlight` instead on a laptop with
   a real backlight; omit the flag in a VM or on a desktop.
   Failed installation steps are reported while the remaining steps continue.
   The installer lists failures at the end and exits with a nonzero status if any
   step failed; resolve them and rerun it to finish installation.
   `chezmoi apply` deploys Atuin, `desktop-doctor`, and the managed configuration;
   open a new shell afterward so the commands and Atuin shell integration load.

5. Optionally log into Atuin. This requires the Atuin encryption key.

   ```sh
   atuin login
   ```

6. Check the installation.

   ```sh
   desktop-doctor
   ./tests/validate-desktop
   ```

7. Log out completely and select **Sway** at the login screen.

Atuin credentials, encryption keys, and history are deliberately not deployed.

Choose `portable` for an ordinary machine. Choose `amice-workstation` only on
the original Ubuntu workstation.

The Ubuntu installer updates the existing **Sway** login entry to use the
portable launcher and removes the older Intel trial and dotfiles entries.
Its launcher detects GPU drivers and connected monitors at each login. With
proprietary NVIDIA loaded, it passes `--unsupported-gpu` and orders DRM devices
so a GPU with a connected monitor comes first, while retaining the other GPUs
for additional displays. It prefers Intel/AMD only when a monitor is connected
to them. An explicit `WLR_DRM_DEVICES` setting takes precedence. Other machines
use Sway's normal GPU selection. No workstation profile is needed.

For an existing install, `./scripts/install --sway-session` updates only the
launcher and login entry, without reinstalling software. It needs sudo for the
system files. Startup diagnostics are saved to
`~/.local/state/sway/session.log` (or `$XDG_STATE_HOME/sway/session.log`), with
the previous attempt retained as `session.previous.log`. NVIDIA support remains
experimental; configuration validation does not verify real display startup.

Existing checkouts upgrading to this layout must run `chezmoi init` once to
regenerate the derived `isAmiceWorkstation` config value before applying.

### macOS

Install [Homebrew](https://brew.sh) first. If this is a new checkout, bootstrap
chezmoi and GitHub access before initializing the portable profile:

```sh
brew install git gh chezmoi
gh auth login
chezmoi init AlexandreAmice-Arda/dotfiles
```

Install the dependencies, apply, and verify:

```sh
cd "$(chezmoi source-path)"
./scripts/install
chezmoi diff
chezmoi apply --verbose
open -a AeroSpace
desktop-doctor
```

Grant AeroSpace permission in System Settings → Privacy & Security →
Accessibility when macOS requests it. Quit and reopen AeroSpace after enabling
permission if its CLI cannot connect. Open a fresh Ghostty window to load the
managed shell setup.

The installer adopts identical applications already in `/Applications` and
installs missing dependencies without routine package upgrades. An existing
application with different contents needs to be reconciled manually with
Homebrew before rerunning the installer.

If adopting an existing app requests an administrator password, run the
installer in an interactive terminal. For Slack specifically, run
`brew install --cask --adopt slack`, then rerun the installer.

GitHub credentials, application histories, and caches are deliberately
machine-local.

Cloudflare One Client (WARP) is installed by `scripts/install` through
[Cloudflare's official apt repository](https://pkg.cloudflareclient.com/) on
Ubuntu and the `cloudflare-warp` Homebrew cask on macOS. After installation,
[enroll the device in your Zero Trust organization](https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/cloudflare-one-client/deployment/manual-deployment/).
On Linux, run `warp-cli registration new <team-name>`, complete the browser
login, then run `warp-cli connect`. On macOS, open Cloudflare WARP and use
Preferences → Account → Login with Cloudflare Zero Trust. Enrollment and
credentials remain machine-local.

Codex is installed automatically during the software-install step. Run
`codex` once to sign in and create `~/.codex`; credentials and session state
remain machine-local. Herdr is installed as a pinned external on Linux and
through Homebrew on macOS. After that first Codex launch, install Herdr's
session hook while preserving other Codex hooks:

```sh
cd "$(chezmoi source-path)"
./scripts/install --agent-integrations
```

The installer installs Rust and Cargo through rustup if a working toolchain is
missing. On Ubuntu it also installs pinned `automatic-timezoned` with Cargo for
the Sway timezone service. Cargo commands are available in a new shell after
applying the managed shell configuration.

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

- `Super+T` on Sway or `Command+T` on AeroSpace opens a plain terminal.
- Add `Shift` to open or resume an independent persistent tmux terminal.
- Add left Ctrl instead to open the agent-aware Herdr workspace. Herdr and
  tmux are separate terminal modes and must not be nested.
- `Super+H/J/K/L` focuses Sway windows; `Super+1` through `Super+0` selects a
  workspace.
- `Super+/` on Sway or `Command+/` on AeroSpace opens the searchable desktop command reference.
- `Super+C` opens Sway system controls; `Super+Shift+X` locks the session.
- `Ctrl+R` searches Atuin history and inserts the result for review.

Starship gives the full untruncated directory its own line, Git state and
command duration the next, and a clean `❯` input marker the final line. SSH
sessions add a separate `user@hostname` line above the directory.

## Appearance

Ubuntu and macOS use the same Tokyo Night palette and pinned wallpaper artwork.
Midnight and 95% terminal opacity are the defaults; saved selections remain
machine-local. Use `apply-appearance --mood midnight` (or `dusk`, `dawn`, `solid`)
and `apply-appearance --opacity 1.00` (or `0.95`, `0.89`). Use `--restore` after
attaching another screen. See [wallpapers.md](docs/wallpapers.md) for native
appearance permissions and reload requirements.

## Documentation

- [Local changes and upstream workflow](docs/local-changes.md)
- [Architecture](docs/architecture.md)
- [Profiles and portability](docs/profiles.md)
- [Keybinding conventions](docs/keybindings.md)
- [Herdr agent workspaces](docs/herdr.md)
- [Wallpaper assets and provenance](docs/wallpapers.md)
- [Roadmap and hardware qualification](docs/roadmap.md)
