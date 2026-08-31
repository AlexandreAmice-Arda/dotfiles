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

Do not add shell histories, SSH keys, license files, GitHub CLI configuration,
or plaintext tokens. Use `chezmoi diff` before every apply.
