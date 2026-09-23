# Keybinding conventions

This page is intentionally not an exhaustive shortcut list. Annotated `#@`
entries in `private_dot_config/sway/conf.d/50-keybindings.conf.tmpl` are the
source of truth. On a running Sway session, `Super+/` renders those annotations
as the complete searchable reference and can execute entries that carry a
Sway command.

Sway uses Super and AeroSpace uses Option/Alt as the window-manager modifier.
Directional operations follow H/J/K/L. A plain direction focuses, adding Alt
on Sway moves a window, and adding left Ctrl moves the whole workspace to an
output. Number keys select workspaces; Shift routes the focused window.

Important chords:

- `Super+T` / `Option+T`: plain terminal, suitable for transparent SSH use.
- Add `Shift`: independent persistent local tmux terminal.
- `Super+/`: exhaustive Sway command palette and shortcut reference.
- `Super+D`: application launcher.
- `Super+C`: graphical Sway system controls.
- `Super+P`: lock and power menu.
- `Super+Shift+X`: lock immediately.
- `Super+R`: enter Sway resize mode; use arrows or H/J/K/L and Escape to exit.

The Kinesis Advantage2 places Super, Space, and Enter in one thumb cluster, so
Sway deliberately defines no Super+Space or Super+Return chord. Tmux uses its
existing prefix-free pane controls plus the ordinary `Ctrl+B` prefix for
window and persistence operations; its configuration is authoritative for
those bindings.
