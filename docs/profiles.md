# Profiles and portability

## Profile contract

`portable` is the default. It must not depend on a username, absolute home
path, GPU address, or project path. Shared applications and workspace
conventions remain consistent across machines. Saved display profiles are
data, not a portability requirement: unmatched monitor identities are ignored
and unknown display sets retain Sway's automatic placement until saved through
the Displays GUI.

`amice-workstation` preserves the original Ubuntu workstation's Intel/NVIDIA
session and conditional environment discovery for its locally installed solver
and CUDA toolchains. The existing profile name and the
`.desktop.profiles.amice_workstation` schema are stable interfaces.

The config initializer derives `isAmiceWorkstation`. It is true only when the
operating system is Linux and the selected profile is `amice-workstation`.
Templates and `.chezmoiignore` gate workstation behavior with that boolean so
the platform requirement cannot be forgotten in individual comparisons.
Validation overrides calculate the same boolean from their simulated OS and
profile. Existing checkouts must run `chezmoi init` once after adopting this
schema so the generated config gains the derived value before the next apply.

## Degradation rules

- `display-layouts.json` may contain monitor serials from any Linux host. A
  host applies only an exact connected-monitor match, and unknown sets use
  automatic placement until explicitly saved.
- Missing battery or temperature sensors leave the corresponding bar item
  empty rather than breaking Waybar.
- Portrait transforms receive portrait artwork; other outputs use landscape.
- The Intel/NVIDIA launcher and saved output identities are absent from
  portable homes and all macOS homes.
- Idle locking and display power-off apply on Ubuntu. Automatic idle suspend
  occurs only while a system battery reports `Discharging`.
- Native package-manager binaries take priority over pinned fallback binaries.

## Support and qualification

The generation baseline is Ubuntu 24.04+ and macOS 13+. Ubuntu 24.04 on the
original workstation is currently hardware-qualified. macOS is
generator-validated but remains unqualified until tested on real hardware.
The authoritative bounds and qualification lists live under
`.desktop.support` in `.chezmoidata.yaml`.

Machine- or employer-specific shell additions belong in the unmanaged
`~/.bashrc.local` hook. Credentials, license files, SSH keys, shell histories,
and tokens never belong in profile data.
