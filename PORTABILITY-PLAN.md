# Portable Sway and AeroSpace plan

## Goal

Maintain one version-controlled desktop system that installs safely on Ubuntu
and macOS while preserving the same workspace, direction, terminal, and visual
language. Portability means shared intent with native platform adapters—not an
attempt to run Linux desktop components on macOS.

## Architecture

Chezmoi owns deployment. `.chezmoidata.yaml` is the declarative source for
shared Tokyo Night colors, H/J/K/L directions, and workspaces. Templates render
that intent into:

- Sway and Foot on Ubuntu.
- AeroSpace and Ghostty on macOS.
- tmux on both platforms for persistent sessions and portable pane controls.

Platform-only features remain native: Waybar, SwayNC, Wofi, wlogout, GTKLock,
brightness, and Linux session integration stay on Ubuntu; macOS retains its
native system controls.

## Profiles

`portable` is the default for a new host. It must not depend on a username,
monitor serial, connector name, GPU PCI address, project path, or optional
personal application.

`amice-workstation` preserves the original machine's Intel/NVIDIA session,
known monitor placement, application startup, and project-window arrangement.
Those details must remain gated behind this profile.

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

## Degradation rules

- Unknown outputs use Sway's automatic placement.
- Missing batteries or temperature sensors leave the corresponding bar item
  empty instead of breaking Waybar.
- Rotated outputs use a portrait wallpaper; all others use landscape.
- Missing optional personal applications do not affect the portable session.
- The hardware-specific Intel/NVIDIA launcher is absent from portable hosts.
- Native package-manager binaries take precedence over current-machine
  compatibility wrappers.

## Validation gates

`packages/validate-desktop` must render both Sway profiles, AeroSpace, Foot,
Ghostty, and both Waybar launch profiles. It then runs every available syntax
checker for Sway, Foot, TOML, JSON, shell scripts, and Git whitespace.

Before calling the setup broadly portable, complete these hardware tests:

- A second Ubuntu laptop using the `portable` profile.
- An Ubuntu system with only external displays.
- Apple Silicon macOS with AeroSpace Accessibility permission granted.
- Intel macOS if Intel support remains a requirement.
- Full-screen GTKLock and suspend/resume before enabling automatic idle lock.

## Current status — 2026-09-15

The generator, both profiles, package manifests, three wallpaper moods,
landscape/portrait variants, appearance controls, hardware keys, automatic
battery/temperature discovery, terminal adapters, validation command, and host
doctor are implemented. The current Ubuntu workstation passes source and live
configuration checks. Cross-machine hardware qualification remains outstanding.
