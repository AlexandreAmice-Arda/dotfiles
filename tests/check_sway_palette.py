"""Check rendered binding coverage and palette dispatch without a live desktop."""

import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


def check(home):
    config = home / ".config/sway/config"
    script = home / ".config/sway/scripts/keybindings"
    files = [config, *sorted((config.parent / "conf.d").glob("*.conf"))]
    variables = {}
    bindings = []
    entries = []
    for path in files:
        for number, line in enumerate(path.read_text().splitlines(), 1):
            line = line.strip()
            if line.startswith("set $"):
                _, name, value = line.split(maxsplit=2)
                variables[name] = value.strip('"')
            if line.startswith("#@ "):
                fields = line[3:].split(" :: ", 2)
                assert len(fields) >= 2, (path, number, "invalid palette entry")
                entries.append(fields)
            if line.startswith(("bindsym ", "bindcode ")):
                match = re.match(r"bind\w+\s+(?:--\S+\s+)*\S+\s+(.+)", line)
                assert match, (path, number, "unrecognized binding")
                bindings.append((path, number, match[1]))

    def expand(command):
        return re.sub(r"\$[A-Za-z_][A-Za-z_0-9]*",
                      lambda match: variables.get(match[0], match[0]), command)

    commands = {expand(fields[2]) for fields in entries if len(fields) == 3}
    for path, number, command in bindings:
        assert expand(command) in commands, (
            f"{path}:{number}: bound action missing from palette: {command}"
        )

    env = dict(os.environ, SWAY_CONFIG_PATH=str(config))
    labels = subprocess.check_output(["bash", str(script), "--print"], env=env,
                                     text=True).splitlines()
    assert len(labels) == len(set(labels)), "ambiguous duplicate palette labels"
    assert len(labels) == len(entries), "palette dropped annotations"
    for fields, label in zip(entries, labels):
        assert label.startswith(fields[1] + " — "), "action must precede shortcut"
        assert ("[reference only]" in label) == (len(fields) == 2)

    # Exercise real selection/dispatch, including shell pipelines and quoted
    # geometry. Fake programs record arguments without executing desktop actions.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for name, body in {
            "wofi": 'printf "%s\\n" "$@" > "$WOFI_ARGS"\ncat >/dev/null\n[ "$CANCEL" = 0 ] || exit 1\nprintf "%s\\n" "$SELECTION"',
            "swaymsg": 'printf "%s\\n" "$@" > "$DISPATCH"',
        }.items():
            target = root / name
            target.write_text("#!/bin/sh\n" + body + "\n")
            target.chmod(0o755)
        dispatch = root / "dispatch"
        wofi_args = root / "wofi_args"
        env.update(PATH=f"{root}:{env['PATH']}", DISPATCH=str(dispatch), CANCEL="0",
                   WOFI_ARGS=str(wofi_args))
        for fields, label in zip(entries, labels):
            dispatch.unlink(missing_ok=True)
            subprocess.run(["bash", str(script)], env=dict(env, SELECTION=label),
                           check=True)
            if len(fields) == 3:
                assert dispatch.read_text() == "--\n" + fields[2] + "\n", label
            else:
                assert not dispatch.exists(), "reference entry executed a command"
        arguments = wofi_args.read_text().splitlines()
        assert arguments[arguments.index("--matching") + 1] == "multi-contains"
        assert "--insensitive" in arguments
        for selection, cancel in [("", "0"), ("not a listed action", "0"), (labels[0], "1")]:
            dispatch.unlink(missing_ok=True)
            subprocess.run(["bash", str(script)],
                           env=dict(env, SELECTION=selection, CANCEL=cancel), check=True)
            assert not dispatch.exists(), "dismissed/unknown selection executed a command"


if __name__ == "__main__":
    for argument in sys.argv[1:]:
        check(Path(argument))
    print("Sway palette coverage and command dispatch passed")
