# Send Editor to Sway Workspace

Moves the active text editor among the VS Code floating windows assigned to
Sway workspaces 1-4.

## Commands

| Shortcut | Command |
| --- | --- |
| `Ctrl+Shift+1` | Send Active Editor to Workspace 1 |
| `Ctrl+Shift+2` | Send Active Editor to Workspace 2 |
| `Ctrl+Shift+3` | Send Active Editor to Workspace 3 |
| `Ctrl+Shift+4` | Send Active Editor to Workspace 4 |
| `Ctrl+Shift+Q` | Close the active editor or integrated terminal |

The commands are also available from the Command Palette under the `Sway`
category.

The extension supports ordinary text editors. It opens the document in the
destination window and verifies it before closing the source tab. Notebooks,
diff editors, custom editors, and non-editor pages are intentionally left
untouched.
