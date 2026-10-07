"""Exercise installer failure handling without downloads or system changes."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SOURCE_ROOT = Path(__file__).resolve().parents[1]


class InstallerTests(unittest.TestCase):
    def run_installer(self, failures, component=None, platform="Linux", rust_available=True, arguments=()):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scripts = root / "scripts"
            scripts.mkdir()
            shutil.copy2(SOURCE_ROOT / "scripts/install", scripts)
            # The simulated Linux installer must not read the test host's OS.
            os_release = root / "os-release"
            os_release.write_text('ID=ubuntu\nVERSION_ID="24.04"\nVERSION_CODENAME=noble\n')
            installer = scripts / "install"
            installer.write_text(installer.read_text().replace("/etc/os-release", str(os_release)))
            shutil.copytree(SOURCE_ROOT / "packages", root / "packages")
            shutil.copy2(SOURCE_ROOT / ".chezmoidata.yaml", root)
            mock_bin = root / "bin"
            mock_bin.mkdir()
            log = root / "commands.log"
            mock = mock_bin / "mock"
            mock.write_text(f"#!{sys.executable}\n" + '''
import fnmatch
import os
from pathlib import Path
import sys
name = Path(sys.argv[0]).name
args = sys.argv[1:]
if name == "sh" and args[:3] == ["-eu", "-s", "--"]:
    name = "install-" + args[3]
    args = []
command = " ".join([name, *args])
with open(os.environ["INSTALL_TEST_LOG"], "a") as log:
    log.write(command + "\\n")
if any(fnmatch.fnmatchcase(command, pattern)
       for pattern in os.environ["INSTALL_TEST_FAILURES"].split("\\n")):
    sys.exit(7)
if name in ("cargo", "rustc") and args == ["--version"]:
    ready = Path(os.environ["HOME"]) / ".rust-ready"
    if os.environ["INSTALL_TEST_RUST_AVAILABLE"] != "1" and not ready.exists():
        sys.exit(1)
    print(name + " 1.90.0")
elif name == "sh" and "--no-modify-path" in args:
    (Path(os.environ["HOME"]) / ".rust-ready").touch()
elif name == "cargo" and args[0] == "install":
    binary = Path(os.environ["HOME"]) / ".cargo/bin/automatic-timezoned"
    binary.parent.mkdir(parents=True, exist_ok=True)
    binary.symlink_to(Path(sys.argv[0]).resolve())
elif name == "automatic-timezoned":
    print("automatic-timezoned 2.0.160")
elif name == "uname":
    print(os.environ["INSTALL_TEST_PLATFORM"])
elif name == "dpkg" and args == ["--print-architecture"]:
    print("amd64")
elif name == "dpkg-query":
    print("ii ")
elif name == "getent":
    print("video:x:44:")
elif name == "snap":
    sys.exit(1)
''')
            mock.chmod(0o755)
            for name in ("uname", "dpkg", "sudo", "wget", "gpg", "curl",
                         "sha256sum", "install", "snap", "find", "getent", "sh", "dpkg-query", "brew", "cargo", "rustc"):
                (mock_bin / name).symlink_to(mock)
            for name in ("check-ubuntu",):
                (scripts / name).symlink_to(mock)
            env = os.environ.copy()
            # Keep host-installed Rust and nwg-displays out of component tests.
            env.update(PATH=f"{mock_bin}:/usr/bin:/bin", HOME=str(root), USER="installer-test",
                       INSTALL_TEST_LOG=str(log), INSTALL_TEST_FAILURES="\n".join(failures),
                       INSTALL_TEST_PLATFORM=platform, CARGO_HOME=str(root / ".cargo"),
                       RUSTUP_HOME=str(root / ".rustup"),
                       INSTALL_TEST_RUST_AVAILABLE="1" if rust_available else "0")
            if component is None:
                result = subprocess.run(["/bin/sh", str(scripts / "install"), *arguments],
                                        env=env, capture_output=True, text=True)
            else:
                marker = component.upper().replace("-", "_") + "_INSTALL"
                body = (scripts / "install").read_text().split(
                    f"<<'{marker}'\n", 1)[1].split(f"\n{marker}\n", 1)[0]
                result = subprocess.run(["/bin/sh", "-eu", "-s"], input=body,
                                        env=env, capture_output=True, text=True)
            return result, log.read_text().splitlines()

    def test_success(self):
        result, commands = self.run_installer([])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Software installation complete.", result.stdout)
        self.assertEqual(commands[-1], "check-ubuntu")

    def test_retired_apps_are_not_installed(self):
        result, commands = self.run_installer([])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(any("signal-desktop" in command or "pcloud" in command
                             for command in commands))

    def test_failed_child_and_check_are_reported_after_later_steps(self):
        result, commands = self.run_installer(["install-foot", "install-nwg-displays", "check-ubuntu"])
        self.assertEqual(result.returncode, 1)
        self.assertIn("install-codex", commands)
        self.assertEqual(commands[-1], "check-ubuntu")
        self.assertIn("3 failed step(s)", result.stderr)
        self.assertIn("Install nwg-displays (exit 7)", result.stderr)
        self.assertNotIn("Software installation complete.", result.stdout)

    def test_failed_package_update_continues(self):
        result, commands = self.run_installer(["sudo apt-get update"])
        self.assertEqual(result.returncode, 1)
        self.assertIn("install-nwg-displays", commands)
        self.assertEqual(commands[-1], "check-ubuntu")
        self.assertIn("2 failed step(s)", result.stderr)

    def test_sway_session_is_registered_by_normal_install(self):
        result, commands = self.run_installer([])
        self.assertEqual(result.returncode, 0, result.stderr)
        launcher = next(i for i, command in enumerate(commands)
                        if command.endswith(" /usr/local/bin/start-sway"))
        session = next(i for i, command in enumerate(commands)
                       if command.endswith(" /usr/share/wayland-sessions/sway.desktop"))
        self.assertLess(launcher, session)

    def test_session_only_updates_sway_and_removes_duplicates(self):
        result, commands = self.run_installer([], arguments=('--sway-session',))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(any(command.endswith(' /usr/share/wayland-sessions/sway.desktop')
                            for command in commands))
        self.assertIn('sudo rm -f -- /usr/share/wayland-sessions/sway-dotfiles.desktop '
                      '/usr/share/wayland-sessions/sway-intel.desktop', commands)
        self.assertFalse(any('apt-get' in command or command.startswith('install-')
                             for command in commands))

    def test_failed_sway_launcher_install_skips_session_entry(self):
        result, commands = self.run_installer(["sudo install */usr/local/bin/start-sway"])
        self.assertEqual(result.returncode, 1)
        self.assertFalse(any(command.endswith(" /usr/share/wayland-sessions/sway.desktop")
                             for command in commands))
        self.assertIn("Register Sway login session (exit 7)", result.stderr)
        self.assertEqual(commands[-1], "check-ubuntu")

    def test_failed_repository_download_skips_dependent_commands(self):
        result, commands = self.run_installer(["wget *microsoft.asc *"])
        self.assertEqual(result.returncode, 1)
        self.assertFalse(any("microsoft.gpg" in command for command in commands))
        self.assertFalse(any("vscode.sources" in command for command in commands))
        self.assertTrue(any("cloudflare-warp.sources" in command for command in commands))
        self.assertIn("install-nwg-displays", commands)
        self.assertIn("Configure VS Code repository (exit 7)", result.stderr)

    def test_nwg_component_download_failure_stops_before_install(self):
        result, commands = self.run_installer(["curl *"], component="nwg-displays")
        self.assertEqual(result.returncode, 7)
        self.assertTrue(any(command.startswith("curl ") for command in commands))
        self.assertFalse(any(command.startswith("sudo ") for command in commands))

    def test_cloudflare_one_repository_precedes_manifest_install(self):
        result, commands = self.run_installer([])
        self.assertEqual(result.returncode, 0, result.stderr)
        repository = next(i for i, command in enumerate(commands)
                          if command.endswith(" /etc/apt/sources.list.d/cloudflare-warp.sources"))
        refresh = commands.index("sudo apt-get update", repository)
        packages = next(i for i, command in enumerate(commands)
                        if command.startswith("sudo apt-get install -y sway "))
        self.assertLess(repository, refresh)
        self.assertLess(refresh, packages)
        self.assertIn("cloudflare-warp", commands[packages].split())

    def test_cloudflare_one_key_failure_skips_repository_install(self):
        for failure in ("wget *cloudflare-warp.asc *", "gpg *cloudflare-warp.asc"):
            with self.subTest(failure=failure):
                result, commands = self.run_installer([failure])
                self.assertEqual(result.returncode, 1)
                self.assertFalse(any(command.startswith("sudo install ") and "cloudflare-warp" in command
                                     for command in commands))
                self.assertIn("install-codex", commands)
                self.assertIn("Configure Cloudflare One repository (exit 7)", result.stderr)

    def test_foot_component_checksum_failure_stops_before_build(self):
        result, commands = self.run_installer(["sha256sum *"], component="foot")
        self.assertEqual(result.returncode, 7)
        self.assertFalse(any(command.startswith("sudo ") for command in commands))

    def test_macos_installs_homebrew_and_codex_without_ubuntu_packages(self):
        result, commands = self.run_installer([], platform="Darwin")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(any(command.startswith("brew bundle install ") for command in commands))
        self.assertIn("install-codex", commands)
        self.assertNotIn("install-foot", commands)
        self.assertFalse(any(command.startswith("sudo apt-get ") for command in commands))

    def test_macos_brew_failure_still_attempts_codex(self):
        result, commands = self.run_installer(["brew bundle install *"], platform="Darwin")
        self.assertEqual(result.returncode, 1)
        self.assertIn("install-codex", commands)
        self.assertIn("Install Homebrew dependencies (exit 7)", result.stderr)

    def test_existing_working_rust_is_reused(self):
        result, commands = self.run_installer([], component="rust")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("cargo --version", commands)
        self.assertIn("rustc --version", commands)
        self.assertFalse(any(command.startswith("curl ") for command in commands))

    def test_missing_rust_installs_toolchain_without_editing_shell_files(self):
        result, commands = self.run_installer([], component="rust", rust_available=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(any("https://sh.rustup.rs" in command for command in commands))
        self.assertTrue(any("--no-modify-path" in command for command in commands))
        self.assertEqual(commands[-2:], ["cargo --version", "rustc --version"])

    def test_failed_rust_download_never_runs_installer(self):
        result, commands = self.run_installer(["curl *"], component="rust", rust_available=False)
        self.assertEqual(result.returncode, 7)
        self.assertFalse(any("--no-modify-path" in command for command in commands))

    def test_timezone_daemon_is_installed_at_service_path(self):
        result, commands = self.run_installer([], component="automatic-timezoned")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(any(command.startswith("cargo install --locked --version 2.0.160 --root ")
                            and command.endswith(" automatic-timezoned") for command in commands))
        self.assertEqual(commands[-1], "automatic-timezoned --version")

    def test_failed_rust_steps_do_not_stop_other_installations(self):
        result, commands = self.run_installer(["install-rust", "install-automatic-timezoned"])
        self.assertEqual(result.returncode, 1)
        self.assertIn("install-nwg-displays", commands)
        self.assertEqual(commands[-1], "check-ubuntu")
        self.assertIn("2 failed step(s)", result.stderr)


if __name__ == "__main__":
    unittest.main()
