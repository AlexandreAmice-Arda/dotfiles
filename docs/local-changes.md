# Local changes

The personal fork is [AlexandreAmice-Arda/dotfiles](https://github.com/AlexandreAmice-Arda/dotfiles).
Its upstream is [AlexandreAmice/dotfiles](https://github.com/AlexandreAmice/dotfiles),
and this checkout started at upstream commit `8c56f00`.
The changes below preserve the local Ubuntu/macOS setup decisions made on
October 5, 2026. Git history records the implementation; this page records
the reasons and known differences.

## Desktop shortcuts

Both desktop adapters use Super: Windows/Super on Ubuntu, Command on macOS.
AeroSpace previously used Option as its primary modifier. Its shared actions
now follow Sway's chords:

- Super+T opens a plain terminal; Shift adds tmux, Ctrl adds Herdr.
- Super+D opens the application launcher; macOS uses Spotlight.
- Super+/ opens the command palette. The macOS palette reads annotated
  AeroSpace bindings and preserves the original target window when dispatching.
- Super+C opens system controls; macOS uses System Settings.
- Super+H/J/K/L focuses windows; Alt moves windows; Ctrl moves whole workspaces
  between monitors.
- Super+E selects tiles or changes their orientation. Super+S/W selects
  vertical/horizontal accordion layouts on macOS.

AeroSpace's explicit split bindings retain single-child containers by disabling
container flattening. These desktop bindings override native Command shortcuts,
including Copy, Save, Close, Hide, Find, and New Tab. Sway's scratchpad, power
menu, lock, and screenshot controls do not have matching AeroSpace bindings.

## Terminal panes

Tmux and Herdr use Ctrl+H/J/K/L for direct pane focus on both platforms. The
previous shared config omitted Ctrl+H, which allowed applications to interpret
it as backspace. Foot and Ghostty already map Ctrl+Backspace separately to
erase the previous word, so Ctrl+H is now bound to left-pane focus.

Ctrl+Alt+B/V splits panes; Ctrl+Alt+H/J/K/L swaps panes; Ctrl+Alt+F zooms.
Alt is Option on macOS. These terminal controls remain distinct from desktop
controls, and the Ctrl+B prefix remains available.

## Workspaces and monitors

Workspaces 1–10 are persistent, rather than a hard maximum. AeroSpace can
create an extra empty workspace when an attached monitor has no assigned
workspace. Moving an existing workspace to that monitor lets the unused empty
workspace disappear. No machine-specific monitor assignment is committed.

## macOS setup changes already present in this checkout

- Add `scripts/install` to install the Brewfile without routine upgrades
  and install Codex, including Homebrew PATH discovery.
- Remove Signal from the macOS package, startup, and workspace declarations;
  Slack remains configured on workspace 10. Ubuntu retains Signal.
- Exclude Linux-only display, focus, and battery helpers from macOS deployment.
- Ignore Python bytecode caches in Git and Chezmoi.
- Extend `desktop-doctor` with AeroSpace TOML and Ghostty configuration checks.
- Document macOS bootstrap, Accessibility permission, and existing-app adoption.

## Verification

`tests/validate-desktop` passed for rendered portable Ubuntu, workstation
Ubuntu, and portable macOS homes. It covers platform boundaries, configuration
syntax, command catalog coverage, shell checks, and existing desktop tests.
Native Sway, Foot, and systemd validators were unavailable on this Mac.

The macOS palette dispatch and cancellation tests passed. AeroSpace reloaded
the new bindings successfully, and Ghostty's native configuration validator
passed. A temporary tmux session verified that a Control+H input byte selects
the left pane. The running Herdr server accepted the config reload with no
diagnostics. The graphical launcher and palette still need hands-on validation.

## Minimal macOS terminal appearance

Ghostty follows Foot's shared font, Tokyo Night palette, selection colors,
padding, 95% opacity, and blinking beam cursor. Blur is disabled and unfocused
Ghostty splits retain full opacity. The macOS title bar is hidden to reduce
terminal chrome; this setting applies to new windows. Scrollback remains at
Ghostty's default byte budget, since Foot's 10,000-line limit has no exact
Ghostty equivalent. Foot's machine-local opacity picker remains Linux-specific.

A macOS-only, idempotent Chezmoi script enables Dock auto-hiding and restarts
Dock only when the preference changes. The Dock still appears when the pointer
reaches its screen edge. Tmux's status bar, AeroSpace configuration, and the
macOS menu bar are unchanged by this appearance update.

## Keeping the fork current

Keep the original repository as `upstream` and the personal fork as `origin`.
Commit local changes before integrating upstream work. Fetch upstream, review
its changes, merge the desired changes, and run `tests/validate-desktop` before
pushing. Review `chezmoi diff` before applying changes on each machine.

## Shared theme rollout

Theme colors now have one source in `.chezmoidata.yaml`; tmux and Starship are
templates with identical existing output, and Neovim explicitly selects Night.
Bright terminal colors are shared as named tokens. `apply-appearance` now works
on Ubuntu and macOS, with Midnight artwork and 95% opacity as fresh defaults.
The same pinned Ubuntu wallpaper archive is installed on macOS. Saved choices
remain local and survive deployment; solid backgrounds remain optional.

Ghostty reads a local opacity include, and real-home setup restores native
wallpaper, dark mode, and purple accents. This rollout does not change AeroSpace
or tmux layout/controls. Herdr uses its existing built-in theme and VS Code
continues to use Settings Sync. See `wallpapers.md` for controls and platform
limits.

Verification: all 18 automated tests and clean-room platform checks passed.
Ghostty's native validator accepted the runtime include, and Neovim compiled
and evaluated its new theme specification. AppKit confirmed Midnight on both
connected Mac screens, native appearance was dark, and the purple accent was
applied. Native Sway/Foot verification still requires an Ubuntu machine.
