# Roadmap

The repository is generator-validated, but portability claims still require
real hardware evidence:

- Run the `portable` profile on a second Ubuntu laptop.
- Qualify an Ubuntu system with external displays only.
- Test Apple Silicon macOS with AeroSpace Accessibility permission.
- Test Intel macOS if Intel support remains a requirement.
- Exercise full-screen GTKLock and a supervised suspend/resume cycle on each
  Ubuntu hardware class.

After normal daily use, review whether the simplified multiline Starship prompt
continues to provide the right information density. Its current deliberate
baseline is a full path line, a Git + command-duration line, an SSH-only
identity line, no time, and `❯` alone on the final line.

Record qualification evidence under `.desktop.support` in
`.chezmoidata.yaml`; do not broaden the support claim based only on successful
template rendering.
