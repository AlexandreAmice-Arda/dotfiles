# Architecture

## Deployment model

Chezmoi owns deployment. This repository remains destination-shaped: source
names such as `private_dot_config` map directly into the target home. Shared
data in `.chezmoidata.yaml` renders native adapters rather than attempting to
make both platforms run the same desktop stack:

- Ubuntu uses Sway, Foot, Waybar, SwayNC, Wofi, wlogout, and GTKLock.
- macOS uses AeroSpace, Ghostty, and native macOS facilities.
- Shell configuration, Tokyo Night colors, H/J/K/L directions, workspaces,
  tmux, Herdr, Starship, Atuin, fzf, and zoxide are shared where their behavior
  truly aligns.

Sway's entry point stays short. Ordered fragments under
`~/.config/sway/conf.d` separate theme, session, inputs, workspaces, bindings,
and rules. The numeric order is intentional and must remain stable.

Package declarations are separate from repository tooling. The root
`Brewfile` is the macOS manifest and `packages/ubuntu.txt` is the Ubuntu
manifest. The Ubuntu installer also configures vendor repositories for VS Code
and Signal, installs Slack through its supported Snap, and installs pCloud
Drive from its checksum-pinned official AppImage. Installers live in `scripts/`,
integration checks in `tests/`, and durable explanations in `docs/`; chezmoi
ignores all three tooling/document trees so they never appear in a rendered
home.

## Executable ownership

Use the narrowest stable interface:

- `~/.local/bin` contains commands a person may call and commands shared by
  multiple components, such as `desktop-doctor`, `terminal-main`, and session
  actions.
- `~/.local/libexec` contains private implementations owned by one component.
  Waybar's temperature probe is therefore
  `~/.local/libexec/waybar/desktop-temperature`.
- `~/.config/sway/scripts` contains Sway session integration. `start-waybar`
  remains here because it chooses a live output and builds session-specific
  Waybar configuration.

Do not move scripts broadly merely for symmetry; ownership and call surface
decide the location.

## External assets and runtime state

Pinned release archives in `.chezmoiexternal.toml.tmpl` fill Linux package
gaps and carry large binary assets. Every archive uses a versioned URL and a
SHA-256 checksum. Wallpaper PNGs are installed from the public assets release,
not Git history; see [wallpapers.md](wallpapers.md).

Runtime state is not source state. Atuin accounts and history, editor caches,
terminal session data, pCloud credentials, selected wallpaper mood, and
terminal opacity remain local. VS Code settings and ordinary extensions belong
to VS Code and Settings Sync. The retired unpublished Sway extension is removed
only by its exact installed directory through `.chezmoiremove.tmpl`.

Long-running Sway components are supervised by systemd user units and tied to
the Sway session target. Small scripts connect components without embedding
procedural behavior in compositor configuration.

## Prompt and terminal decisions

Native terminal windows begin with a plain shell so an SSH session is never
silently nested inside local tmux. The shifted terminal shortcut explicitly
resumes a detached numbered session or creates the next one; `terminal-main
--shared` is the deliberate shared-session escape hatch.

Herdr is a separate, explicit agent-workspace layer rather than a replacement
for general tmux sessions. The Ctrl-modified terminal shortcut starts its
background server/client, while tmux remains on Shift. `terminal-agents`
rejects launches from inside either multiplexer so their shared Ctrl+B prefix
and overlapping pane ownership never become ambiguous. Only Herdr's
`config.toml` is source state; agent sessions, logs, sockets, and pane contents
remain local runtime state.

Starship stays on both platforms with a compact multiline prompt. The full,
untruncated directory has its own line, Git branch/status and command duration
share the next, and the final line is the clean `❯` character. SSH sessions
conditionally add a separate `user@hostname` line above the directory. Time
and project-language modules are intentionally omitted.
