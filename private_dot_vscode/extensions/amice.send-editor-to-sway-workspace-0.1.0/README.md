# Send Editor to Sway Workspace

Moves the active text editor among the VS Code floating windows assigned to
Sway workspaces 1-4.

## Commands

| Shortcut | Command |
| --- | --- |
| `Ctrl+Alt+1` | Send Active Editor to Workspace 1 |
| `Ctrl+Alt+2` | Send Active Editor to Workspace 2 |
| `Ctrl+Alt+3` | Send Active Editor to Workspace 3 |
| `Ctrl+Alt+4` | Send Active Editor to Workspace 4 |

The commands are also available from the Command Palette under the `Sway`
category.

The extension supports ordinary text editors. It opens the document in the
destination window and verifies it before closing the source tab. Notebooks,
diff editors, custom editors, and non-editor pages are intentionally left
untouched.
