# Dotfiles

Cross-platform Bash and Git configuration managed with
[chezmoi](https://www.chezmoi.io/), for Linux and macOS.

## Set up a new machine

Install Git and chezmoi, configure an SSH key for GitHub, and then run:

```sh
chezmoi init --apply git@github.com:AlexandreAmice/dotfiles.git
```

Initialization prompts once for the Git name and email to use on that machine.
GitHub credentials are intentionally not stored in this repository. Install the
GitHub CLI and run `gh auth login` when GitHub API or HTTPS access is needed.

On macOS, these files assume Bash is the interactive shell. The managed
`.bash_profile` loads the shared `.profile` configuration.

## Daily use

Preview and apply source changes:

```sh
chezmoi diff
chezmoi apply -v
```

Capture a change made directly to a managed file, then commit it:

```sh
chezmoi add ~/.bashrc
chezmoi cd
git add .
git commit
git push
```

Pull and apply changes made on another machine:

```sh
chezmoi update -v
```

## Ubuntu Sway trial

The Linux-only Sway configuration keeps Ubuntu GNOME available as a fallback,
uses the Intel GPU for display scan-out, and leaves NVIDIA available for
offloaded applications. Apply the dotfiles, then install the separate GDM
session and NVIDIA sleep hooks:

```sh
chezmoi diff
chezmoi apply -v
~/.local/bin/sway-trial-system install
```

At GDM, select **Sway (Intel hybrid trial)**. Super is the window-manager
modifier, Super+/ opens the executable command palette, and all Super+Space
bindings are intentionally absent.

If the trial session is unusable, press Ctrl+Alt+F3, log in, restart GDM, and
select Ubuntu. The system-level trial additions can be removed with:

```sh
~/.local/bin/sway-trial-system rollback
```

Do not add shell histories, SSH keys, license files, GitHub CLI configuration,
or plaintext tokens. Use `chezmoi diff` before every apply.
