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

- Add `scripts/install-macos` to install the Brewfile without routine upgrades
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

## Keeping the fork current

Keep the original repository as `upstream` and the personal fork as `origin`.
Commit local changes before integrating upstream work. Fetch upstream, review
its changes, merge the desired changes, and run `tests/validate-desktop` before
pushing. Review `chezmoi diff` before applying changes on each machine.
