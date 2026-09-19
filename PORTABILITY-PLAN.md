# Portable Sway and AeroSpace plan

## Goal

Maintain one version-controlled desktop system that installs safely on Ubuntu
and macOS while preserving the same workspace, direction, terminal, and visual
language. Portability means shared intent with native platform adapters—not an
attempt to run Linux desktop components on macOS.

## Architecture

Chezmoi owns deployment. `.chezmoidata.yaml` is the declarative source for
shared Tokyo Night colors, H/J/K/L directions, workspaces, fonts, and idle
power policy. Templates render that intent into:

- Sway and Foot on Ubuntu.
- AeroSpace and Ghostty on macOS.
- tmux on both platforms for portable pane controls and structural restore
  across terminal restarts and reboots.

Platform-only features remain native: Waybar, SwayNC, Wofi, wlogout, GTKLock,
brightness, and Linux session integration stay on Ubuntu; macOS retains its
native system controls.

Sway is intentionally a small entry point plus topic-oriented files under
`sway/conf.d/`. Long-running session components are systemd user services.
Small action scripts connect components without putting procedural logic into
the compositor config. This layout is part of the portability contract: a
human should be able to find one concern without editing a monolithic generated
file.

## Profiles

`portable` is the default for a new host. It must not depend on a username,
monitor serial, connector name, GPU PCI address, project path, or optional
personal application.

`amice-workstation` preserves the original machine's Intel/NVIDIA session,
known monitor placement, automatic cloud and messaging applications, and an
explicit launcher for the heavier project-window arrangement. Those details
must remain gated behind this profile.

## Installation contract

Ubuntu dependencies are declared in `packages/ubuntu.txt` and installed by
`packages/install-ubuntu`. macOS dependencies are declared in `Brewfile`.
Downloaded package trees, credentials, histories, caches, and machine-local
databases are never committed.

A new host should follow this sequence:

1. Install Git and chezmoi.
2. Run `chezmoi init --apply` against this repository.
3. Select `portable` unless deliberately restoring the original workstation.
4. Install the platform package manifest.
5. Run `packages/validate-desktop` from the source repository.
6. Run `desktop-doctor` after deployment.

The generation baseline is Ubuntu 24.04+ and macOS 13+. Ubuntu's installer
enforces its lower bound; the deployed doctor enforces the macOS lower bound.
Qualification is separately recorded under `desktop.support`: Ubuntu 24.04 is
qualified on the current workstation and macOS remains unqualified until a
real Mac completes the checklist. Newer versions may render, but are not
silently claimed as hardware-qualified.

## Degradation rules

- Unknown outputs use Sway's automatic placement.
- Missing batteries or temperature sensors leave the corresponding bar item
  empty instead of breaking Waybar.
- Rotated outputs use a portrait wallpaper; all others use landscape.
- Missing optional personal applications do not affect the portable session.
- The hardware-specific Intel/NVIDIA launcher is absent from portable hosts.
- Native package-manager binaries take precedence over current-machine
  compatibility wrappers.
- Idle locking and display power-off apply everywhere on Ubuntu. Automatic
  idle suspend applies only when a system `BAT*` device reports `Discharging`.
- Linux session services restart after isolated failures and stop as one target
  when the compositor exits.
- Privileged graphical actions use MATE's standalone polkit agent instead of a
  GNOME-session agent.
- The graphical Sway control center launches standalone tools: NetworkManager
  for connections, Blueman for Bluetooth, pavucontrol for audio, wdisplays for
  outputs, and a small power-profiles-daemon menu. It does not impersonate a
  GNOME session or depend on GNOME Settings panels.
- Ctrl-Backspace is encoded as readline's previous-word erase on Foot and
  Ghostty; tmux deliberately does not capture the ambiguous Ctrl-H byte.
- Chezmoi installs pinned, checksummed tmux-resurrect and tmux-continuum
  archives on both platforms. They periodically save and restore tmux
  structure, but never replay processes or persist pane text. Application
  state resumes explicitly through the application's own interface.
- Each native terminal window resumes one detached numbered tmux session or
  creates a new one, so persistence does not make separate windows mirror one
  another. The legacy `main` session remains an explicit shared option.

## Validation gates

`packages/validate-desktop` must materialize fresh homes for portable Ubuntu,
workstation Ubuntu, and portable macOS. It validates platform/profile absence
rules as well as Sway, Foot, systemd units, TOML, JSON, shell scripts, known
personal-data leaks, and Git whitespace. This avoids passing validation merely
because the current machine already has a required runtime file.

Before calling the setup broadly portable, complete these hardware tests:

- A second Ubuntu laptop using the `portable` profile.
- An Ubuntu system with only external displays.
- Apple Silicon macOS with AeroSpace Accessibility permission granted.
- Intel macOS if Intel support remains a requirement.
- Full-screen GTKLock and one supervised suspend/resume cycle on each Ubuntu
  hardware class.

## Current status — 2026-09-16

The generator, both profiles, package manifests, three wallpaper moods,
landscape/portrait variants, appearance controls, hardware keys, power-aware
idle suspend, automatic battery/temperature discovery, terminal adapters,
reboot-safe tmux structure restore, explicit workstation launch, supervised
session services, clean-room validation, and host doctor are implemented. The
dense status bar is intentionally retained. Cross-machine hardware
qualification remains outstanding; it is the remaining evidence needed before
claiming broad portability rather than generator-level portability.
