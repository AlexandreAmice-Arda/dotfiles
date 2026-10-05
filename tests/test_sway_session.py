"""Check GPU selection with synthetic sysfs and a recording compositor."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SOURCE_ROOT = Path(__file__).resolve().parents[1]


class SwaySessionTests(unittest.TestCase):
    def launch(self, drivers, override=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            drm = root / "drm"
            drm.mkdir()
            for card, driver in drivers.items():
                device = drm / card / "device"
                device.mkdir(parents=True)
                target = root / "drivers" / driver
                target.mkdir(parents=True, exist_ok=True)
                (device / "driver").symlink_to(target)
            # A connector must never become a DRM device in the selected list.
            (drm / "card0-HDMI-A-1").mkdir()
            compositor = root / "sway"
            compositor.write_text(
                "#!/usr/bin/python3\nimport json, os, sys\n"
                "print(json.dumps({'args': sys.argv[1:], "
                "'devices': os.environ.get('WLR_DRM_DEVICES'), "
                "'desktop': os.environ.get('XDG_CURRENT_DESKTOP')}))\n")
            compositor.chmod(0o755)
            launcher = root / "start-sway"
            source = (SOURCE_ROOT / "private_dot_local/bin/executable_start-sway").read_text()
            launcher.write_text(source.replace('/sys/class/drm', str(drm))
                               .replace('/usr/bin/sway', str(compositor)))
            env = os.environ.copy()
            env.pop('WLR_DRM_DEVICES', None)
            if override is not None:
                env['WLR_DRM_DEVICES'] = override
            result = subprocess.run(['/bin/sh', str(launcher), '--debug'],
                                    env=env, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)

    def test_non_nvidia_and_nouveau_keep_default_gpu_selection(self):
        for drivers in ({}, {'card3': 'i915'}, {'card2': 'amdgpu'}, {'card0': 'nouveau'}):
            with self.subTest(drivers=drivers):
                self.assertEqual(self.launch(drivers),
                                 {'args': ['--debug'], 'devices': None, 'desktop': 'sway'})

    def test_hybrid_gpu_selection_does_not_depend_on_pci_or_card_number(self):
        result = self.launch({'card7': 'nvidia', 'card4': 'i915', 'card9': 'amdgpu'})
        self.assertEqual(result['args'], ['--unsupported-gpu', '--debug'])
        self.assertEqual(result['devices'], '/dev/dri/card4:/dev/dri/card9')

    def test_nvidia_only_uses_default_device_selection(self):
        result = self.launch({'card2': 'nvidia'})
        self.assertEqual(result['args'], ['--unsupported-gpu', '--debug'])
        self.assertIsNone(result['devices'])

    def test_explicit_device_selection_is_preserved(self):
        result = self.launch({'card2': 'nvidia', 'card1': 'i915'}, '/dev/dri/card2')
        self.assertEqual(result['devices'], '/dev/dri/card2')
        self.assertIn('--unsupported-gpu', result['args'])


if __name__ == '__main__':
    unittest.main()
