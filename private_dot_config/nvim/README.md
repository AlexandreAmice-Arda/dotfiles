# LazyVim configuration

This is the portable [LazyVim starter](https://www.lazyvim.org/installation).
Keep options, keymaps, and autocommands in `lua/config/`, and put each focused
plugin override in a small file under `lua/plugins/`.

Plugin downloads, Mason tools, logs, caches, and editor state are runtime data
and are intentionally not managed by chezmoi. `lazy-lock.json` is managed so a
new computer can reproduce the reviewed plugin versions.
