# Keybinding conventions

This page is intentionally not an exhaustive shortcut list. Annotated `#@`
entries in `private_dot_config/sway/conf.d/50-keybindings.conf.tmpl` are the
source of truth. On a running Sway session, `Super+/` renders those annotations
as the complete searchable reference and can execute entries that carry a
Sway command. Rows show the category and action first, followed by the shortcut.
Search for familiar terms such as `screenshot`, `snip`, `monitor`, `workspace`,
`volume`, or `brightness`; monitor actions also include `screen` and `output`.
The palette matches each space-separated search term as a substring, ignoring
case and word order: `snip` finds the region screenshot, and `workspace right`
finds workspace movement to the right monitor. Shortcuts are searchable too.
Entries marked `[reference only]` describe terminal shortcuts and do not run
when selected. `Palette only` means the action runs from the palette but has
no dedicated shortcut. Enter selects an entry; Escape closes the palette.

Every bound Sway action must have an executable annotation. Alternate keys for
the same action can share an entry. `tests/validate-desktop` checks coverage
and verifies command dispatch against the rendered Linux configurations.

Both desktops use Super as the window-manager modifier: the Windows/Super key
on Ubuntu and Command on macOS. Desktop bindings take precedence over native
macOS app shortcuts, including Command+C, Command+H, and Command+T.
Directional operations follow H/J/K/L. A plain direction focuses, adding Alt
moves a window, and adding left Ctrl moves the whole workspace to an
adjacent monitor. Number keys select workspaces; Shift routes the focused window.

Important chords:

- `Super+T` / `Command+T`: plain terminal, suitable for transparent SSH use.
- Add `Shift`: independent persistent local tmux terminal.
- Add left Ctrl instead: agent-aware Herdr workspace.
- `Super+/`: searchable desktop command palette and shortcut reference.
- `Super+D`: application launcher (Spotlight on macOS).
- `Super+C`: system controls (System Settings on macOS).
- `Super+P`: lock and power menu.
- `Super+Shift+X`: lock immediately.
- `Super+R`: enter resize mode; use H/J/K/L and Escape to exit.
- `Print Screen`: copy a screenshot of all screens to the clipboard.
- `Shift+Print Screen`: select a region and copy its screenshot to the clipboard.

Screenshot actions copy an image for pasting; they do not save a file. Volume,
microphone mute, media playback, brightness, and individual resize actions
are also available directly from the palette.

The Displays entry under `Super+C` opens nwg-displays for both monitor geometry
and workspace placement. Close the GUI after applying changes to save the
active monitor-set profile; subsequent whole-workspace moves are saved
automatically.

The Kinesis Advantage2 places Super, Space, and Enter in one thumb cluster, so
Sway deliberately defines no Super+Space or Super+Return chord. Tmux uses its
existing prefix-free pane controls plus the ordinary `Ctrl+B` prefix for
window and persistence operations. Herdr also uses `Ctrl+B`, but only in its
own terminal windows; do not nest either multiplexer inside the other. Each
tool's own configuration is authoritative for its internal bindings.

Tmux and Herdr share these direct pane controls:

- `Ctrl+H/J/K/L`: focus left/down/up/right. Foot and Ghostty map
  Ctrl+Backspace separately to erase the previous word.
- `Ctrl+Alt+H/J/K/L` or `Ctrl+Alt+Arrow`: swap with the neighboring pane.
- `Ctrl+Alt+B/V`: split side-by-side / top-to-bottom. Herdr calls these
  operations `split_vertical` / `split_horizontal`, respectively.
- `Ctrl+Alt+Shift+Arrow`: resize in that direction.
- `Ctrl+Alt+F`: toggle pane zoom.
- `Ctrl+Alt+Q`: close the pane.

The close shortcut is not perfectly equivalent: tmux confirms before killing
the pane, while Herdr 0.9.1 closes it immediately. Herdr's safer prefix form
(`Ctrl+B`, then `x`) remains available alongside the direct shortcut.

On macOS, `Super+/` opens an fzf command palette in a temporary Ghostty window.
Its actions and shortcut labels come directly from the annotated AeroSpace
bindings, and window actions target the window that was focused before the
palette opened. `Super+E` selects tiles or toggles their orientation; `Super+S`
and `Super+W` select vertical and horizontal accordion layouts. AeroSpace has
no direct Sway scratchpad equivalent. Lock/power and screenshot shortcuts above
remain Sway-specific; macOS uses its native controls for those actions.
