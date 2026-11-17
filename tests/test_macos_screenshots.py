"""Exercise rendered macOS screenshot setup without touching host preferences."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SOURCE_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SOURCE_ROOT / 'run_onchange_after_26_macos_screenshots.sh.tmpl'


class ScreenshotShortcutTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.state = self.root / 'preferences.json'
        self.original = {'79': {'enabled': False}, 'custom': {'value': 'keep'}}
        self.state.write_text(json.dumps(self.original))
        self.refresh = self.root / 'refresh'
        self.env = dict(os.environ, HOME=str(self.root), CHEZMOI_DEST_DIR=str(self.root),
                        PATH=f'{self.root}:/usr/bin:/bin',
                        SCREENSHOT_TEST_STATE=str(self.state),
                        SCREENSHOT_TEST_REFRESH=str(self.refresh))
        self.env.pop('SCREENSHOT_TEST_REFRESH_FAIL', None)
        self.env.pop('SCREENSHOT_TEST_WRITE_FAIL', None)
        self.mock('uname', '#!/bin/sh\nprintf "%s\\n" Darwin\n')
        self.mock('defaults', f'#!{sys.executable}\n' + '''
import json, os, pathlib, plistlib, sys
assert sys.argv[1:5] == ['write', 'com.apple.symbolichotkeys',
                         'AppleSymbolicHotKeys', '-dict-add']
if os.environ.get('SCREENSHOT_TEST_WRITE_FAIL'):
    sys.exit(1)
path = pathlib.Path(os.environ['SCREENSHOT_TEST_STATE'])
state = json.loads(path.read_text())
state[sys.argv[5]] = plistlib.loads(
    ('<plist version="1.0">' + sys.argv[6] + '</plist>').encode())
path.write_text(json.dumps(state))
''')
        self.mock('activateSettings', '''#!/bin/sh
[ "$1" = -u ] || exit 2
printf refreshed > "$SCREENSHOT_TEST_REFRESH"
[ "${SCREENSHOT_TEST_REFRESH_FAIL:-}" != 1 ]
''')

    def mock(self, name, content):
        path = self.root / name
        path.write_text(content)
        path.chmod(0o755)

    def run_script(self, os_name='darwin'):
        rendered = subprocess.run(
            ['chezmoi', '--source', str(SOURCE_ROOT), '--override-data',
             json.dumps({'chezmoi': {'os': os_name}}),
             'execute-template', '--file', str(SCRIPT)],
            check=True, capture_output=True, text=True).stdout
        return subprocess.run(['/bin/sh'], input=rendered, env=self.env,
                              capture_output=True, text=True)

    def test_mappings_preserve_other_preferences_and_repeat_safely(self):
        for _ in range(2):
            result = self.run_script()
            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads(self.state.read_text())
            expected = dict(self.original)
            for shortcut_id, keycode, modifiers in (
                    ('28', 99, 1179648), ('29', 99, 1441792),
                    ('30', 118, 1179648), ('31', 118, 1441792),
                    ('184', 96, 1179648)):
                expected[shortcut_id] = {
                    'enabled': True,
                    'value': {'parameters': [65535, keycode, modifiers],
                              'type': 'standard'}}
            self.assertEqual(state, expected)
            self.assertEqual(self.refresh.read_text(), 'refreshed')

    def test_platform_and_destination_guards(self):
        for scenario in ('linux_template', 'linux_host', 'temporary_home'):
            with self.subTest(scenario=scenario):
                self.mock('uname', '#!/bin/sh\nprintf "%s\\n" ' +
                          ('Linux' if scenario == 'linux_host' else 'Darwin') + '\n')
                self.env['CHEZMOI_DEST_DIR'] = str(
                    self.root / 'target' if scenario == 'temporary_home' else self.root)
                result = self.run_script('linux' if scenario == 'linux_template' else 'darwin')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(self.state.read_text()), self.original)
                self.assertFalse(self.refresh.exists())

    def test_refresh_failure_reports_logout(self):
        self.env['SCREENSHOT_TEST_REFRESH_FAIL'] = '1'
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('log out and back in', result.stderr)

    def test_preference_write_failure_stops_before_refresh(self):
        self.env['SCREENSHOT_TEST_WRITE_FAIL'] = '1'
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(self.state.read_text()), self.original)
        self.assertFalse(self.refresh.exists())


if __name__ == '__main__':
    unittest.main()
