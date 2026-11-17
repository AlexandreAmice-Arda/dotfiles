"""Check session setup with synthetic sysfs and a recording compositor."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SOURCE_ROOT = Path(__file__).resolve().parents[1]


class SwaySessionTests(unittest.TestCase):
    def launch(self, drivers, override=None, connected=(), stack_ready=None, profile=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            if profile is not None:
                (root / '.profile').write_text(profile)
            drm = root / "drm"
            drm.mkdir()
            for card, driver in drivers.items():
                device = drm / card / "device"
                device.mkdir(parents=True)
                target = root / "drivers" / driver
                target.mkdir(parents=True, exist_ok=True)
                (device / "driver").symlink_to(target)
            for card in connected:
                connector = drm / (card + '-DP-1')
                connector.mkdir()
                (connector / 'status').write_text('connected\n')
            # A connector must never become a DRM device in the selected list.
            (drm / "card0-HDMI-A-1").mkdir()
            compositor = root / "sway"
            compositor.write_text(
                "#!/usr/bin/python3\nimport json, os, sys\n"
                "print(json.dumps({'args': sys.argv[1:], "
                "'devices': os.environ.get('WLR_DRM_DEVICES'), "
                "'software_cursor': os.environ.get('WLR_NO_HARDWARE_CURSORS'), "
                "'path': os.environ['PATH'].replace(os.environ['HOME'], '~'), "
                "'desktop': os.environ.get('XDG_CURRENT_DESKTOP')}))\n")
            compositor.chmod(0o755)
            if stack_ready is not None:
                stack = root / '.local/lib/sway-stack/current'
                (stack / 'bin').mkdir(parents=True)
                stack_sway = stack / 'bin/sway'
                stack_sway.write_text(compositor.read_text().replace(
                    'sys.argv[1:]', "['--private-stack', *sys.argv[1:]]"))
                stack_sway.chmod(0o755)
                if stack_ready != 'missing-locker':
                    (stack / 'bin/gtklock').symlink_to(compositor)
                if stack_ready:
                    (stack / 'ready').write_text('verified\n')
            launcher = root / "start-sway"
            source = (SOURCE_ROOT / "private_dot_local/bin/executable_start-sway").read_text()
            launcher.write_text(source.replace('/sys/class/drm', str(drm))
                               .replace('/usr/bin/sway', str(compositor)))
            env = os.environ.copy()
            env.pop('WLR_DRM_DEVICES', None)
            env.pop('WLR_NO_HARDWARE_CURSORS', None)
            env['HOME'] = str(root)
            env['PATH'] = '/usr/bin:/bin'
            env['XDG_STATE_HOME'] = str(root / 'state')
            if override is not None:
                env['WLR_DRM_DEVICES'] = override
            result = subprocess.run(['/bin/sh', str(launcher), '--test'],
                                    env=env, capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout, '')
            return json.loads((root / 'state/sway/session.log').read_text())

    def test_non_nvidia_and_nouveau_keep_default_gpu_selection(self):
        for drivers in ({}, {'card3': 'i915'}, {'card2': 'amdgpu'}, {'card0': 'nouveau'}):
            with self.subTest(drivers=drivers):
                self.assertEqual(self.launch(drivers),
                                 {'args': ['--debug', '--test'], 'devices': None, 'software_cursor': None,
                                  'desktop': 'sway', 'path': '/usr/bin:/bin'})

    def test_graphical_login_loads_user_paths_before_strict_mode(self):
        result = self.launch({}, profile=(
            '# Profiles may contain optional checks that return false.\n'
            '[ -d "$HOME/missing" ]\n'
            'export PATH="$HOME/.local/bin:$HOME/bin:$PATH"\n'))
        self.assertEqual(result['path'], '~/.local/bin:~/bin:/usr/bin:/bin')

    def test_hybrid_gpu_selection_does_not_depend_on_pci_or_card_number(self):
        result = self.launch({'card7': 'nvidia', 'card4': 'i915', 'card9': 'amdgpu'}, connected=('card4', 'card9'))
        self.assertEqual(result['args'], ['--debug', '--unsupported-gpu', '--test'])
        self.assertEqual(result['devices'], '/dev/dri/card4:/dev/dri/card9:/dev/dri/card7')

    def test_nvidia_only_keeps_its_device(self):
        result = self.launch({'card2': 'nvidia'})
        self.assertEqual(result['args'], ['--debug', '--unsupported-gpu', '--test'])
        self.assertEqual(result['devices'], '/dev/dri/card2')
        self.assertEqual(result['software_cursor'], '1')

    def test_monitor_on_nvidia_with_disconnected_intel(self):
        result = self.launch({'card1': 'i915', 'card2': 'nvidia'}, connected=('card2',))
        self.assertEqual(result['devices'], '/dev/dri/card2:/dev/dri/card1')

    def test_monitors_on_both_gpus_keep_both_available(self):
        result = self.launch({'card1': 'i915', 'card2': 'nvidia'}, connected=('card1', 'card2'))
        self.assertEqual(result['devices'], '/dev/dri/card1:/dev/dri/card2')

    def test_explicit_device_selection_is_preserved(self):
        result = self.launch({'card2': 'nvidia', 'card1': 'i915'}, '/dev/dri/card2')
        self.assertEqual(result['devices'], '/dev/dri/card2')
        self.assertIn('--unsupported-gpu', result['args'])

    def test_completed_stack_is_used_for_login(self):
        self.assertEqual(self.launch({}, stack_ready=True)['args'],
                         ['--private-stack', '--debug', '--test'])

    def test_incomplete_stack_keeps_system_compositor(self):
        for ready in (False, 'missing-locker'):
            with self.subTest(ready=ready):
                self.assertEqual(self.launch({}, stack_ready=ready)['args'],
                                 ['--debug', '--test'])


if __name__ == '__main__':
    unittest.main()
